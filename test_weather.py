import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from weather_analysis import WeatherAnalyzer
from weather_analysis import WeatherDataLoader
from weather_analysis import WeatherRecord


class TestWeatherAnalysis(unittest.TestCase):
	def test_object_creation(self):
		record = WeatherRecord("Riga", 1, 4.0, 82.0, 12.0)
		self.assertEqual(record.city, "Riga")
		self.assertEqual(record.day, 1)
		self.assertEqual(record.temperature, 4.0)
		self.assertEqual(record.humidity, 82.0)
		self.assertEqual(record.wind_speed, 12.0)

	def test_csv_loading(self):
		csv_content = (
			"city,day,temperature,humidity,wind_speed\n"
			"Riga,1,4,82,12\n"
			"Rome,2,20,58,7\n"
		)
		with TemporaryDirectory() as tmp_dir:
			csv_path = Path(tmp_dir) / "weather_data.csv"
			csv_path.write_text(csv_content, encoding="utf-8")

			loader = WeatherDataLoader(csv_path)
			records = loader.load_records()

		self.assertEqual(len(records), 2)
		self.assertEqual(records[0].city, "Riga")
		self.assertEqual(records[1].temperature, 20.0)

	def test_filter_by_city(self):
		records = [
			WeatherRecord("Riga", 2, 5.0, 80.0, 15.0),
			WeatherRecord("Rome", 1, 18.0, 60.0, 5.0),
			WeatherRecord("Riga", 1, 4.0, 82.0, 12.0),
		]
		analyzer = WeatherAnalyzer(records)

		filtered = analyzer.filter_by_city("Riga")

		self.assertEqual(len(filtered), 2)
		self.assertEqual(filtered[0].day, 1)
		self.assertEqual(filtered[1].day, 2)

	def test_average_calculation(self):
		records = [
			WeatherRecord("Riga", 1, 4.0, 82.0, 12.0),
			WeatherRecord("Riga", 2, 6.0, 80.0, 10.0),
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
			WeatherRecord("Riga", 1, 4.0, 82.0, 12.0),
			WeatherRecord("Rome", 2, 20.0, 58.0, 7.0),
		]
		analyzer = WeatherAnalyzer(records)

		no_city_records = analyzer.filter_by_city("Tallinn")
		self.assertEqual(no_city_records, [])

		with self.assertRaises(AttributeError):
			analyzer.average_for(records, "pressure")

	def test_oslo_filter_and_average(self):
		records = [
			WeatherRecord("Oslo", 1, -3.0, 75.0, 9.0),
			WeatherRecord("Riga", 1, 4.0, 82.0, 12.0),
			WeatherRecord("Oslo", 2, -1.0, 73.0, 11.0),
		]
		analyzer = WeatherAnalyzer(records)

		oslo_records = analyzer.filter_by_city("Oslo")
		self.assertEqual(len(oslo_records), 2)
		self.assertEqual([record.day for record in oslo_records], [1, 2])

		average_oslo_temperature = analyzer.average_for(oslo_records, "temperature")
		self.assertAlmostEqual(average_oslo_temperature, -2.0)


if __name__ == "__main__":
	unittest.main()
