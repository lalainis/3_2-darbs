# Weather Analysis

Programma iegust laika datus no Open-Meteo API, aprēķina vidējo vērtību izvēlētajai metrikai un parāda grafiku.

## Projekta struktūra

- **app.py** - lietotāja saskarne un programmas palaišana
- **models.py** - datu klases un analīze
- **api_client.py** - datu ieguve no Open-Meteo API (ar kļūdu apstrādi)
- **chart_strategy.py** - grafiku sagatavošana
- **tests.py** - vienību testi
- **config.json** - konfigurācija (pilsētas, API parametri)

## Prasības

- Python 3.10+
- matplotlib>=3.8

## Instalēšana

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\Activate.ps1  # Windows PowerShell

pip install -r requirements.txt
```

## Programmas palaišana

### Interaktīvs režīms

```bash
python app.py
```

Programma lūgs izvēlēties pilsētu un metriku.

### Ar komandrindas argumentiem

```bash
python app.py --city "Rīga" --metric temperature
python app.py --city "Liepāja" --metric wind_speed --no-plot
```

### Opcijas

- `--city` - pilsētas nosaukums (Rīga, Liepāja, Daugavpils)
- `--metric` - metrika: `temperature` vai `wind_speed` (noklusējums: temperature)
- `--no-plot` - nerādīt grafiku, tikai skaitlisko rezultātu
- `--log-level` - log līmenis: DEBUG, INFO, WARNING, ERROR (noklusējums: INFO)

### Piemēri

```bash
python app.py --city "Rīga" --metric temperature
python app.py --city "Liepāja" --metric wind_speed
python app.py --city "Daugavpils" --metric temperature --no-plot
python app.py --log-level DEBUG
```

## Testa palaišana

```bash
python -m unittest -v tests.py
```

## Pieejamās metrīkas

- `temperature` - Temperatūra (°C)
- `wind_speed` - Vēja ātrums (m/s)

## Kļūdu apstrāde

Aplikācija nodrošina robusta kļūdu apstrādi:
- API savienojuma kļūdas (tīkla problēmas)
- JSON parsēšanas kļūdas
- Nevalidās pilsētas vai metrīkas
- Grafika attēlošanas problēmas (headless režīmā)

Katrai kļūdai ir informatīvs paziņojums un exit kods (1-3).
