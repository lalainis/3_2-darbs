import logging
from typing import List

import matplotlib.pyplot as plt

from models import WeatherRecord

logger = logging.getLogger(__name__)


class MetricPlotter:
    """Pamata klase vienas metrikas attēlošanai."""

    metric_name: str = ""
    metric_label: str = ""

    def values(self, records: List[WeatherRecord]) -> List[float]:
        """Izgūst metrikas vērtības no ierakstiem."""
        return [record.value_for(self.metric_name) for record in records]

    def plot(self, city_name: str, records: List[WeatherRecord]) -> None:
        """Attēlo metrikas datus pilsētai."""
        labels = [record.date_time.strftime("%Y-%m-%d %H:%M") for record in records]
        values = self.values(records)

        plt.figure(figsize=(9, 5))
        plt.plot(labels, values, marker="o", linewidth=2)
        plt.title(f"{city_name} - {self.metric_label} pēc datuma/laika")
        plt.xlabel("Datums/Laiks")
        plt.ylabel(self.metric_label)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        logger.info(f"Rāda grafiku par {city_name} ({self.metric_name})")
        plt.show()


class TemperaturePlotter(MetricPlotter):
    metric_name = "temperature"
    metric_label = "Temperatūra (°C)"


class WindSpeedPlotter(MetricPlotter):
    metric_name = "wind_speed"
    metric_label = "Vēja ātrums (m/s)"
