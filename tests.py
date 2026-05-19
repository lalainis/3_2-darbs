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

    def test_parse_args_no_plot_flag(self):
        args = parse_args(["--city", "Rīga", "--no-plot"])
        self.assertTrue(args.no_plot)

    def test_parse_args_log_level(self):
        args = parse_args(["--log-level", "DEBUG"])
        self.assertEqual(args.log_level, "DEBUG")

    def test_resolve_city_case_insensitive(self):
        city = resolve_city(["Rīga", "Liepāja"], "RĪGa")
        self.assertEqual(city, "Rīga")

    def test_resolve_city_invalid_raises_detailed_message(self):
        with self.assertRaises(ValueError) as context:
            resolve_city(["Rīga", "Liepāja"], "Tallinn")
        self.assertIn("Tallinn", str(context.exception))
        self.assertIn("Rīga", str(context.exception))

    def test_resolve_plotter_temperature(self):
        plotter = resolve_plotter("temperature")
        self.assertIsInstance(plotter, TemperaturePlotter)

    def test_resolve_plotter_wind_speed(self):
        plotter = resolve_plotter("wind_speed")
        self.assertIsInstance(plotter, WindSpeedPlotter)

    def test_resolve_plotter_invalid_raises_detailed_message(self):
        with self.assertRaises(ValueError) as context:
            resolve_plotter("humidity")
        self.assertIn("humidity", str(context.exception))
        self.assertIn("temperature", str(context.exception))

    def test_object_creation(self):
        record = WeatherRecord("Rīga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0)
        self.assertEqual(record.city, "Rīga")
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

        loader = WeatherDataLoader({"Rīga": CITY_COORDINATES["Rīga"]})
        records = loader.load_records()

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].city, "Rīga")
        self.assertEqual(records[1].temperature, 5.0)

    def test_filter_by_city(self):
        records = [
            WeatherRecord("Rīga", datetime(2026, 5, 14, 10, 0), 5.0, 15.0),
            WeatherRecord("Liepāja", datetime(2026, 5, 14, 9, 0), 18.0, 5.0),
            WeatherRecord("Rīga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
        ]
        analyzer = WeatherAnalyzer(records)

        filtered = analyzer.filter_by_city("Rīga")

        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].date_time, datetime(2026, 5, 14, 9, 0))
        self.assertEqual(filtered[1].date_time, datetime(2026, 5, 14, 10, 0))

    def test_average_calculation(self):
        records = [
            WeatherRecord("Rīga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
            WeatherRecord("Rīga", datetime(2026, 5, 14, 10, 0), 6.0, 10.0),
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
            WeatherRecord("Rīga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
            WeatherRecord("Liepāja", datetime(2026, 5, 14, 10, 0), 20.0, 7.0),
        ]
        analyzer = WeatherAnalyzer(records)

        no_city_records = analyzer.filter_by_city("Tallinn")
        self.assertEqual(no_city_records, [])

        with self.assertRaises(AttributeError):
            analyzer.average_for(records, "pressure")

    def test_liepaja_filter_and_average(self):
        records = [
            WeatherRecord("Liepāja", datetime(2026, 5, 14, 9, 0), 3.0, 9.0),
            WeatherRecord("Rīga", datetime(2026, 5, 14, 9, 0), 4.0, 12.0),
            WeatherRecord("Liepāja", datetime(2026, 5, 14, 10, 0), 5.0, 11.0),
        ]
        analyzer = WeatherAnalyzer(records)

        liepaja_records = analyzer.filter_by_city("Liepāja")
        self.assertEqual(len(liepaja_records), 2)
        self.assertEqual(
            [record.date_time for record in liepaja_records],
            [datetime(2026, 5, 14, 9, 0), datetime(2026, 5, 14, 10, 0)],
        )

        average_liepaja_temperature = analyzer.average_for(liepaja_records, "temperature")
        self.assertAlmostEqual(average_liepaja_temperature, 4.0)


if __name__ == "__main__":
    unittest.main()
