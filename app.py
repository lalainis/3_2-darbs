import argparse
import io
import logging
import sys
from typing import Dict, List, Optional, Type
from urllib.error import URLError

# Pārliecinās, ka konsoles izvade ir UTF-8 kodēta
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from api_client import CITY_COORDINATES
from api_client import WeatherDataLoader
from chart_strategy import MetricPlotter
from chart_strategy import TemperaturePlotter
from chart_strategy import WindSpeedPlotter
from models import WeatherAnalyzer

logger = logging.getLogger(__name__)


def ask_city(cities: List[str]) -> str:
    print("Pieejamās Pilsētas:", ", ".join(cities))
    while True:
        city = input("Izvēlieties pilsētu: ").strip()
        if city.lower() in {item.lower() for item in cities}:
            return city
        print("Pilsēta nav atrasta. Lūdzu, izvēlieties no saraksta.")


def ask_metric_plotter() -> MetricPlotter:
    print("Izvēlieties metriku: temperature, wind_speed")
    plotters = _plotter_map()
    while True:
        metric = input("Metrika: ").strip().lower()
        if metric in plotters:
            return plotters[metric]()
        print("Nederīga metrika. Izmantojiet: temperature vai wind_speed.")


def _plotter_map() -> Dict[str, Type[MetricPlotter]]:
    return {
        "temperature": TemperaturePlotter,
        "wind_speed": WindSpeedPlotter,
    }


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Laikapstākļu prognoze izmantojot Open-Meteo datus")
    parser.add_argument("--city", help="Pilsētas nosaukums, piemēram: Rīga")
    parser.add_argument("--metric", help="Metrikas nosaukums: temperature vai wind_speed")
    parser.add_argument("--no-plot", action="store_true", help="Nerādit grafiku, tikai skaitliska vērtība")
    parser.add_argument("--log-level", default="INFO", help="Log līmenis: DEBUG, INFO, WARNING, ERROR")
    return parser.parse_args(argv)


def resolve_city(cities: List[str], city_arg: Optional[str] = None) -> str:
    if city_arg is None:
        return ask_city(cities)

    for city in cities:
        if city.lower() == city_arg.lower():
            return city

    raise ValueError(f"Pilsēta '{city_arg}' nav atrasta. Pieejamās: {', '.join(cities)}")


def resolve_plotter(metric_arg: Optional[str] = None) -> MetricPlotter:
    plotters = _plotter_map()

    if metric_arg is None:
        return ask_metric_plotter()

    metric = metric_arg.strip().lower()
    if metric in plotters:
        return plotters[metric]()

    raise ValueError(f"Nederīga metrika '{metric_arg}'. Izmantojiet: {', '.join(plotters.keys())}")


def main(argv: Optional[List[str]] = None) -> None:
    """Galvenās programmas ieejas funkcija."""
    args = parse_args(argv)
    
    # konfigurē logging ar UTF-8 kodējumu
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        encoding='utf-8'
    )
    logger.info("Aplikācija sākas")

    try:
        loader = WeatherDataLoader(CITY_COORDINATES)
        logger.info("Ielādēju laika datus...")
        records = loader.load_records()

        analyzer = WeatherAnalyzer(records)
        cities = analyzer.available_cities()

        selected_city = resolve_city(cities, args.city)
        selected_plotter = resolve_plotter(args.metric)
        
        logger.info(f"Izvēlēta pilsēta: {selected_city}, metrika: {selected_plotter.metric_name}")

        filtered_records = analyzer.filter_by_city(selected_city)
        average_value = analyzer.average_for(filtered_records, selected_plotter.metric_name)

        print(f"\nSelected city: {selected_city}")
        print(f"Selected metric: {selected_plotter.metric_name}")
        print(f"Average {selected_plotter.metric_label}: {average_value:.2f}\n")

        if not args.no_plot:
            logger.info("Rāda grafiku...")
            selected_plotter.plot(selected_city, filtered_records)
        else:
            logger.info("Grafiks ir izslēgts (--no-plot)")
            
    except ValueError as e:
        logger.error(f"Validācijas kļūda: {e}")
        print(f"Validācijas kļūda: {e}", file=sys.stderr)
        raise SystemExit(1) from e
    except (URLError, RuntimeError) as e:
        logger.error(f"Datu ielādes kļūda: {e}")
        print(f"Datu ielādes kļūda: {e}", file=sys.stderr)
        raise SystemExit(2) from e
    except KeyboardInterrupt:
        logger.info("Lietotājs apstādināja programmu")
        print("\nProgramma apstādināta.")
        raise SystemExit(0) from None
    except Exception as e:
        logger.exception(f"Neparedzēta kļūda: {e}")
        print(f"Neparedzēta kļūda: {e}", file=sys.stderr)
        raise SystemExit(3) from e


if __name__ == "__main__":
    main()
