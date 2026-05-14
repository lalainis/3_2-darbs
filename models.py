from dataclasses import dataclass
from datetime import datetime


@dataclass
class WeatherRecord:
    """One weather row object."""

    city: str
    date_time: datetime
    temperature: float
    wind_speed: float

    def value_for(self, metric: str):
        """Return metric value by metric name."""
        return getattr(self, metric)


class WeatherAnalyzer:
    """Filters and aggregates weather records."""

    def __init__(self, records):
        self.records = records

    def available_cities(self):
        return sorted({record.city for record in self.records})

    def filter_by_city(self, city_name):
        filtered = [record for record in self.records if record.city.lower() == city_name.lower()]
        return sorted(filtered, key=lambda record: record.date_time)

    def average_for(self, records, metric):
        if not records:
            return 0.0
        return sum(record.value_for(metric) for record in records) / len(records)
