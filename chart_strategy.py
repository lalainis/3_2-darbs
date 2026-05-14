import matplotlib.pyplot as plt


class MetricPlotter:
    """Pamata klase vienas metrikas attēlošanai."""

    metric_name = ""
    metric_label = ""

    def values(self, records):
        return [record.value_for(self.metric_name) for record in records]

    def plot(self, city_name, records):
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
        plt.show()


class TemperaturePlotter(MetricPlotter):
    metric_name = "temperature"
    metric_label = "Temperature (C)"


class WindSpeedPlotter(MetricPlotter):
    metric_name = "wind_speed"
    metric_label = "Wind speed (m/s)"
