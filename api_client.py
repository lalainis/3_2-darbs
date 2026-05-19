import json
import logging
from datetime import datetime
from typing import Any, Dict, List
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from models import WeatherRecord

logger = logging.getLogger(__name__)

# Load config
try:
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = json.load(f)
        CITY_COORDINATES = {city: (data["latitude"], data["longitude"]) 
                           for city, data in CONFIG["cities"].items()}
        BASE_URL = CONFIG["api"]["base_url"]
        API_TIMEOUT = CONFIG["api"]["timeout_seconds"]
        FORECAST_DAYS = CONFIG["api"]["forecast_days"]
except FileNotFoundError as e:
    logger.error(f"config.json not found: {e}")
    raise SystemExit("Kļūda: config.json nav atrodams. Lūdzu atkopējiet failu.") from e
except (json.JSONDecodeError, KeyError) as e:
    logger.error(f"Invalid config.json format: {e}")
    raise SystemExit(f"Kļūda: config.json formāts ir nepareizs: {e}") from e


class WeatherDataClient:
    """Atbildīgs tikai par datu saņemšanu no Open-Meteo."""

    def fetch_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Fetch weather data from Open-Meteo API with error handling."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,wind_speed_10m",
            "timezone": "auto",
            "forecast_days": FORECAST_DAYS,
        }
        url = f"{BASE_URL}?{urlencode(params)}"

        try:
            with urlopen(url, timeout=API_TIMEOUT) as response:
                raw_data = response.read().decode("utf-8")
                logger.debug(f"API response received for ({latitude}, {longitude})")
                return json.loads(raw_data)
        except URLError as e:
            error_msg = f"API savienojuma kļūda ({latitude}, {longitude}): {e}"
            logger.error(error_msg)
            raise URLError(error_msg) from e
        except json.JSONDecodeError as e:
            error_msg = f"Nepareizs JSON atbildē: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        except Exception as e:
            error_msg = f"Neparedzēta kļūda API izsaukumā: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e


class WeatherDataLoader:
    """Ielādē laikapstākļu datus no Open-Meteo API."""

    def __init__(self, city_coordinates: Dict[str, tuple], data_client: WeatherDataClient | None = None):
        self.city_coordinates = city_coordinates
        self.data_client = data_client or WeatherDataClient()

    def load_records(self) -> List[WeatherRecord]:
        """Load weather records with graceful error handling."""
        records = []

        for city, (latitude, longitude) in self.city_coordinates.items():
            try:
                logger.info(f"Ielādēju datus pilsētai: {city}")
                payload = self.data_client.fetch_weather(latitude, longitude)
                hourly = payload.get("hourly", {})
                times = hourly.get("time", [])
                temperatures = hourly.get("temperature_2m", [])
                wind_speeds = hourly.get("wind_speed_10m", [])

                if not times:
                    logger.warning(f"Nav datu pilsētai {city}")
                    continue

                for stamp, temperature, wind_speed in zip(times, temperatures, wind_speeds):
                    try:
                        records.append(
                            WeatherRecord(
                                city=city,
                                date_time=datetime.fromisoformat(stamp),
                                temperature=float(temperature),
                                wind_speed=float(wind_speed),
                            )
                        )
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Nevarēju parsēt ierakstu {city} - {stamp}: {e}")
                        continue
                        
            except (URLError, ValueError, RuntimeError) as e:
                logger.error(f"Nevarēju ielādēt datus {city}: {e}")
                continue

        if not records:
            raise RuntimeError("Nevarēju ielādēt datus no API jebkurai pilsētai.")
            
        logger.info(f"Veiksmīgi ielādēti {len(records)} ieraksti")
        return records
