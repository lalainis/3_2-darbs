---
name: city-forecast-checklist
description: "Use when a user asks for weather forecast output for a specific city in this repository. Follow a short checklist: validate inputs, run the CLI, capture summary values, and report any blockers."
---

# City Forecast Checklist

Use this skill when the user wants a forecast summary for one city from this project.

## Outcome

Produce a concise forecast result for one city, including:
- selected city
- selected metric
- average value for the selected metric
- any blockers (invalid city, invalid metric, runtime issues)

## Required Inputs

- city name (for example: Rīga, Liepāja, Daugavpils)
- metric (temperature or wind_speed). If missing, default to temperature.

## Checklist

1. Confirm inputs.
- If city is missing, ask for city.
- If metric is missing, set metric=temperature.

2. Validate allowed values.
- Allowed metrics: temperature, wind_speed.
- Allowed cities are based on CITY_COORDINATES in api_client.py.

3. Run non-interactive command.
- Run: python app.py --city "<city>" --metric <metric>

4. Capture forecast summary from stdout.
- Selected city: ...
- Selected metric: ...
- Average ...: ...

5. Report result clearly.
- Include city, metric, average value.
- If command fails, include exact reason and next fix.

6. Run tests after forecast run.
- Run: python -m unittest -v tests.py
- Report pass/fail status.

## Decision Points

- If city is not found: list available cities and ask user to choose one.
- If metric is invalid: switch to temperature or wind_speed and rerun.
- If chart display is unavailable (headless session): report that completion is blocked, because chart is required.

## Completion Checks

A run is complete only if all are true:
- command exits without traceback
- selected city and selected metric are shown in output
- average value is present and numeric
- chart window is displayed successfully
- tests.py is executed and status is reported
- any fallback or correction is documented
