from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class WeatherRecord:
    """Viens laikapstākļu ieraksts."""

    city: str
    date_time: datetime
    temperature: float
    wind_speed: float

    def value_for(self, metric: str) -> float:
        """Atgriež vērtību pēc metrikas nosaukuma."""
        return float(getattr(self, metric))


class WeatherAnalyzer:
    """Filtrē un apkopo laikapstākļu ierakstus."""

    def __init__(self, records: List[WeatherRecord]):
        self.records = records

    def available_cities(self) -> List[str]:
        """Return sorted list of unique cities."""
        return sorted({record.city for record in self.records})

    def filter_by_city(self, city_name: str) -> List[WeatherRecord]:
        """Filter records by city name (case-insensitive)."""
        filtered = [record for record in self.records if record.city.lower() == city_name.lower()]
        return sorted(filtered, key=lambda record: record.date_time)

    def average_for(self, records: List[WeatherRecord], metric: str) -> float:
        """Calculate average value for metric across records."""
        if not records:
            return 0.0
        return sum(record.value_for(metric) for record in records) / len(records)
