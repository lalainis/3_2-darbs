import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

from models import WeatherRecord


CITY_COORDINATES = {
    "Rīga": (56.9496, 24.1052),
    "Liepāja": (56.5047, 21.0108),
    "Daugavpils": (55.8747, 26.5362),
}

BASE_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherDataClient:
    """Atbildīgs tikai par datu saņemšanu no Open-Meteo."""

    def fetch_weather(self, latitude, longitude):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,wind_speed_10m",
            "timezone": "auto",
            "forecast_days": 2,   #šo varētu likt kā mainīgo pie interaktīvās ievades.
        }
        url = f"{BASE_URL}?{urlencode(params)}"

        with urlopen(url, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))


class WeatherDataLoader:
    """Ielādē laikapstākļu datus no Open-Meteo API."""

    def __init__(self, city_coordinates, data_client=None):
        self.city_coordinates = city_coordinates
        self.data_client = data_client or WeatherDataClient()

    def load_records(self):
        records = []

        for city, (latitude, longitude) in self.city_coordinates.items():
            payload = self.data_client.fetch_weather(latitude, longitude)
            hourly = payload.get("hourly", {})
            times = hourly.get("time", [])
            temperatures = hourly.get("temperature_2m", [])
            wind_speeds = hourly.get("wind_speed_10m", [])

            for stamp, temperature, wind_speed in zip(times, temperatures, wind_speeds):
                records.append(
                    WeatherRecord(
                        city=city,
                        date_time=datetime.fromisoformat(stamp),
                        temperature=float(temperature),
                        wind_speed=float(wind_speed),
                    )
                )

        return records
