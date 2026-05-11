import csv
from pathlib import Path

import matplotlib.pyplot as plt


CSV_PATH = Path(__file__).with_name("weather_data.csv")

# KLASE: apraksta vienu laikapstaklu ierakstu.
class WeatherRecord:
    """One weather row object."""

    def __init__(self, city, day, temperature, humidity, wind_speed):
        self.city = city
        self.day = day
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed

    def value_for(self, metric):
        """Return metric value by metric name."""
        return getattr(self, metric)


class WeatherDataLoader:
    """Loads weather data from CSV file."""

    def __init__(self, csv_path):
        self.csv_path = csv_path

    def load_records(self):
        records = []
        with self.csv_path.open("r", encoding="utf-8", newline="") as file_obj:
            reader = csv.DictReader(file_obj)
            for row in reader:
                records.append(
                    WeatherRecord(
                        city=row["city"].strip(),
                        day=int(row["day"]),
                        temperature=float(row["temperature"]),
                        humidity=float(row["humidity"]),
                        wind_speed=float(row["wind_speed"]),
                    )
                )
        return records


class WeatherAnalyzer:
    """Filters and aggregates weather records."""

    def __init__(self, records):
        self.records = records

    def available_cities(self):
        return sorted({record.city for record in self.records})

    def filter_by_city(self, city_name):
        filtered = [record for record in self.records if record.city.lower() == city_name.lower()]
        return sorted(filtered, key=lambda record: record.day)

    def average_for(self, records, metric):
        if not records:
            return 0.0
        return sum(record.value_for(metric) for record in records) / len(records)


# KLASE: bazes klase grafika zimešanai.
class MetricPlotter:
    """Base class for plotting one metric."""

    metric_name = ""
    metric_label = ""

    def values(self, records):
        return [record.value_for(self.metric_name) for record in records]

    def plot(self, city_name, records):
        days = [record.day for record in records]
        values = self.values(records)

        plt.figure(figsize=(9, 5))
        plt.plot(days, values, marker="o", linewidth=2)
        plt.title(f"{city_name} - {self.metric_label} by Day")
        plt.xlabel("Day")
        plt.ylabel(self.metric_label)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()



# MANTOSANA: TemperaturePlotter manto no MetricPlotter.
class TemperaturePlotter(MetricPlotter):
    metric_name = "temperature"
    metric_label = "Temperature (C)"


# MANTOSANA: HumidityPlotter manto no MetricPlotter.
class HumidityPlotter(MetricPlotter):
    metric_name = "humidity"
    metric_label = "Humidity (%)"


# MANTOSANA: WindSpeedPlotter manto no MetricPlotter.
class WindSpeedPlotter(MetricPlotter):
    metric_name = "wind_speed"
    metric_label = "Wind speed"


def ask_city(cities):
    print("Available cities:", ", ".join(cities))
    while True:
        city = input("Choose city: ").strip()
        if city.lower() in {item.lower() for item in cities}:
            return city
        print("City not found. Please choose from the list.")


def ask_metric_plotter():
    print("Choose metric: temperature, humidity, wind_speed")
    plotters = {
        "temperature": TemperaturePlotter,
        "humidity": HumidityPlotter,
        "wind_speed": WindSpeedPlotter,
    }
    while True:
        metric = input("Metric: ").strip().lower()
        if metric in plotters:
            return plotters[metric]()
        print("Invalid metric. Use: temperature, humidity, or wind_speed.")


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found: {CSV_PATH}")

    # OBJEKTS: loader ir izveidots no WeatherDataLoader klases.
    loader = WeatherDataLoader(CSV_PATH)
    records = loader.load_records()

    # OBJEKTS: analyzer ir izveidots no WeatherAnalyzer klases.
    analyzer = WeatherAnalyzer(records)
    cities = analyzer.available_cities()

    selected_city = ask_city(cities)
    # OBJEKTS: selected_plotter ir viens no objektu tipiem:TemperaturePlotter, HumidityPlotter vai WindSpeedPlotter.
   
    selected_plotter = ask_metric_plotter()

    filtered_records = analyzer.filter_by_city(selected_city)
    average_value = analyzer.average_for(filtered_records, selected_plotter.metric_name)

    print(f"\nSelected city: {selected_city}")
    print(f"Selected metric: {selected_plotter.metric_name}")
    print(f"Average {selected_plotter.metric_label}: {average_value:.2f}\n")

    # POLIMORFISMS: tiek izsaukta viena un ta pati plot() metode,
    # bet reali strada dazada MetricPlotter apaksklase.
    selected_plotter.plot(selected_city, filtered_records)


if __name__ == "__main__":
    main()
