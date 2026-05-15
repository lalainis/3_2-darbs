import unittest
from datetime import datetime
from unittest.mock import patch

from app import parse_args
from app import resolve_city
from app import resolve_plotter
from api_client import CITY_COORDINATES
from api_client import WeatherDataClient
from api_client import WeatherDataLoader
from chart_strategy import TemperaturePlotter
from chart_strategy import WindSpeedPlotter
from models import WeatherAnalyzer
from models import WeatherRecord


class TestWeatherAnalysis(unittest.TestCase):
    def test_parse_args_reads_city_and_metric(self):
        args = parse_args(["--city", "Rīga", "--metric", "temperature"])

        self.assertEqual(args.city, "Rīga")
        self.assertEqual(args.metric, "temperature")

    def test_resolve_city_case_insensitive(self):
        city = resolve_city(["Rīga", "Liepāja"], "RĪGa")

        self.assertEqual(city, "Rīga")

    def test_resolve_city_invalid_raises(self):
        with self.assertRaises(ValueError):
            resolve_city(["Rīga", "Liepāja"], "Tallinn")

    def test_resolve_plotter_temperature(self):
        plotter = resolve_plotter("temperature")

        self.assertIsInstance(plotter, TemperaturePlotter)

    def test_resolve_plotter_wind_speed(self):
        plotter = resolve_plotter("wind_speed")

        self.assertIsInstance(plotter, WindSpeedPlotter)

    def test_resolve_plotter_invalid_raises(self):
        with self.assertRaises(ValueError):
            resolve_plotter("humidity")

    def test_object_creation(self):
        record = WeatherRecord("Riga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0)
        self.assertEqual(record.city, "Riga")
        self.assertEqual(record.date_time, datetime(2026, 5, 14, 9, 0))
        self.assertEqual(record.temperature, 4.0)
        self.assertEqual(record.wind_speed, 12.0)

    @patch.object(WeatherDataClient, "fetch_weather")
    def test_api_loading(self, mock_fetch_weather):
        mock_fetch_weather.return_value = {
            "hourly": {
                "time": ["2026-05-14T09:00", "2026-05-14T10:00"],
                "temperature_2m": [4, 5],
                "wind_speed_10m": [12, 10],
            }
        }

        loader = WeatherDataLoader({"Riga": CITY_COORDINATES["Rīga"]})
        records = loader.load_records()

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].city, "Riga")
        self.assertEqual(records[1].temperature, 5.0)

    @patch.object(WeatherDataClient, "fetch_weather")
    def test_api_loading_error_propagates(self, mock_fetch_weather):
        mock_fetch_weather.side_effect = TimeoutError("Open-Meteo request timed out")

        loader = WeatherDataLoader({"Riga": CITY_COORDINATES["Rīga"]})

        with self.assertRaises(TimeoutError):
            loader.load_records()

    def test_filter_by_city(self):
        records = [
            WeatherRecord("Riga", datetime(2026, 5, 14, 10, 0), 5.0, 15.0),
            WeatherRecord("Rome", datetime(2026, 5, 14, 9, 0), 18.0, 5.0),
            WeatherRecord("Riga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
        ]
        analyzer = WeatherAnalyzer(records)

        filtered = analyzer.filter_by_city("Riga")

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].date_time, datetime(2026, 5, 14, 9, 0))
        self.assertEqual(filtered[1].date_time, datetime(2026, 5, 14, 10, 0))

    def test_average_calculation(self):
        records = [
            WeatherRecord("Riga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
            WeatherRecord("Riga", datetime(2026, 5, 14, 10, 0), 6.0, 10.0),
        ]
        analyzer = WeatherAnalyzer(records)

        average_temperature = analyzer.average_for(records, "temperature")

        self.assertAlmostEqual(average_temperature, 5.0)

    def test_empty_data_list(self):
        analyzer = WeatherAnalyzer([])

        average = analyzer.average_for([], "temperature")

        self.assertEqual(average, 0.0)

    def test_nonexistent_city_and_data_type(self):
        records = [
            WeatherRecord("Riga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
            WeatherRecord("Rome", datetime(2026, 5, 14, 10, 0), 20.0, 7.0),
        ]
        analyzer = WeatherAnalyzer(records)

        no_city_records = analyzer.filter_by_city("Tallinn")
        self.assertEqual(no_city_records, [])

        with self.assertRaises(AttributeError):
            analyzer.average_for(records, "pressure")

    def test_oslo_filter_and_average(self):
        records = [
            WeatherRecord("Oslo", datetime(2026, 5, 14, 9, 0), -3.0, 9.0),
            WeatherRecord("Riga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
            WeatherRecord("Oslo", datetime(2026, 5, 14, 10, 0), -1.0, 11.0),
        ]
        analyzer = WeatherAnalyzer(records)

        oslo_records = analyzer.filter_by_city("Oslo")
        self.assertEqual(len(oslo_records), 2)
        self.assertEqual(
            [record.date_time for record in oslo_records],
            [datetime(2026, 5, 14, 9, 0), datetime(2026, 5, 14, 10, 0)],
        )

        average_oslo_temperature = analyzer.average_for(oslo_records, "temperature")
        self.assertAlmostEqual(average_oslo_temperature, -2.0)


if __name__ == "__main__":
    unittest.main()
