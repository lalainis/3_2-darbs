# Weather Analysis

Programma iegust laika datus no Open-Meteo API, apreikina videjo vertibu izveletajai metrikai un parada grafiku.

## Projekta struktura

- app.py - lietotaja saskarne un programmas palaisana
- models.py - datu klases un analize
- api_client.py - datu ieguve no Open-Meteo
- chart_strategy.py - grafiku sagatavosana
- tests.py - vienibu testi

## Prasibas

- Python 3.10+

Instalesana:

```bash
pip install -r requirements.txt
```

## Programmas palaisana

Interaktivs rezims:

```bash
python app.py
```

Ar komandrindas argumentiem:

```bash
python app.py --city "Rīga" --metric temperature
```

Piemeri:

```bash
python app.py --city "Liepāja" --metric wind_speed
python app.py --city "Daugavpils" --metric temperature
```

Pieejamas metrikas:

- temperature
- wind_speed

## Testu palaisana

```bash
python -m unittest -v tests.py
```
