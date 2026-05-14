import argparse

from api_client import CITY_COORDINATES
from api_client import WeatherDataLoader
from chart_strategy import TemperaturePlotter
from chart_strategy import WindSpeedPlotter
from models import WeatherAnalyzer


def ask_city(cities):
    print("Available cities:", ", ".join(cities))
    while True:
        city = input("Choose city: ").strip()
        if city.lower() in {item.lower() for item in cities}:
            return city
        print("City not found. Please choose from the list.")


def ask_metric_plotter():
    print("Choose metric: temperature, wind_speed")
    plotters = _plotter_map()
    while True:
        metric = input("Metric: ").strip().lower()
        if metric in plotters:
            return plotters[metric]()
        print("Invalid metric. Use: temperature or wind_speed.")


def _plotter_map():
    return {
        "temperature": TemperaturePlotter,
        "wind_speed": WindSpeedPlotter,
    }


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Weather analyzer using Open-Meteo data")
    parser.add_argument("--city", help="City name, for example: Rīga")
    parser.add_argument("--metric", help="Metric name: temperature or wind_speed")
    return parser.parse_args(argv)


def resolve_city(cities, city_arg=None):
    if city_arg is None:
        return ask_city(cities)

    for city in cities:
        if city.lower() == city_arg.lower():
            return city

    raise ValueError("City not found. Please choose from the list.")


def resolve_plotter(metric_arg=None):
    plotters = _plotter_map()

    if metric_arg is None:
        return ask_metric_plotter()

    metric = metric_arg.strip().lower()
    if metric in plotters:
        return plotters[metric]()

    raise ValueError("Invalid metric. Use: temperature or wind_speed.")


def main(argv=None):
    args = parse_args(argv)

    loader = WeatherDataLoader(CITY_COORDINATES)
    records = loader.load_records()

    analyzer = WeatherAnalyzer(records)
    cities = analyzer.available_cities()

    try:
        selected_city = resolve_city(cities, args.city)
        selected_plotter = resolve_plotter(args.metric)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    filtered_records = analyzer.filter_by_city(selected_city)
    average_value = analyzer.average_for(filtered_records, selected_plotter.metric_name)

    print(f"\nSelected city: {selected_city}")
    print(f"Selected metric: {selected_plotter.metric_name}")
    print(f"Average {selected_plotter.metric_label}: {average_value:.2f}\n")

    selected_plotter.plot(selected_city, filtered_records)


if __name__ == "__main__":
    main()
