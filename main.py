from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
import requests
from datetime import datetime, timedelta

app = FastAPI(title="Weather Service", version="0.1.0")

class ForecastResponse(BaseModel):
    date: str
    time: str
    temperature: float

@app.get("/ping")
def ping():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html>
        <head>
            <title>Weather Service</title>
        </head>
        <body style="font-family: sans-serif; max-width: 600px; margin: auto; line-height: 1.6;">
            <h1>🌦 Weather Service (yr.no)</h1>
            <p>
                Get temperature forecasts for any location using the
                <a href="https://api.met.no" target="_blank">yr.no API</a>.
            </p>

            <h2>Usage</h2>
            <ul>
                <li><code>/ping</code> → Health check</li>
                <li><code>/forecast</code> → Get forecast</li>
            </ul>

            <h2>Example</h2>
            <pre style="background:#f4f4f4; padding:1em; border-radius:6px;">
Input:
<code>/forecast?days=2&amp;latitude=44.8176&amp;longitude=20.4569&amp;time_of_day=14</code>

Output:
[
  {"date": "2025-08-21", "time": "14:00:00", "temperature": 27.5},
  {"date": "2025-08-22", "time": "14:00:00", "temperature": 26.8}
]
            </pre>

            <h2>Docs</h2>
            <p>
                Interactive API docs available at
                <a href="/docs">/docs</a>.
            </p>
        </body>
    </html>
    """

@app.get("/forecast", response_model=List[ForecastResponse])
def get_forecast(
    days: int = 100,
    altitude: int = Query(120, ge=0),
    latitude: float = Query(44.8176, ge=-90, le=90),
    longitude: float = Query(20.4569, ge=-180, le=180),
    time_of_day: int = Query(14, ge=0, le=23),
):
    """
    Get temperature forecast for the next N days
    Default location is Belgrade, specify latitude and longitude
    for other locations
    Default time is 14:00
    """
    # construct payload
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    params = {"lat": latitude, "lon": longitude, "altitude": altitude}
    headers = {"User-Agent": "weather-service/0.1 licomail256@gmail.com"}

    # get data
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch weather data: {e}")
    except ValueError:
        raise HTTPException(status_code=502, detail="Invalid response format from weather API")

    # group forecasts by date
    grouped: dict[str, list[dict]] = {}
    for entry in data["properties"]["timeseries"]:
        dt = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
        date_str = dt.date().isoformat()
        grouped.setdefault(date_str, []).append(entry)

    forecasts: List[ForecastResponse] = []

    # for each date, pick the entry closest to time_of_day
    for date_str, entries in grouped.items():
        if not entries:
            continue
        # calculate the closest entry to specified time
        closest = min(
            entries,
            key=lambda e: abs(
                datetime.fromisoformat(e["time"].replace("Z", "+00:00")).hour - time_of_day
            )
        )

        dt = datetime.fromisoformat(closest["time"].replace("Z", "+00:00"))
        temp = closest["data"]["instant"]["details"]["air_temperature"]
        forecasts.append(ForecastResponse(
                date=date_str,
                time=dt.time().isoformat(timespec="minutes"),
                temperature=temp,
            )
        )

    # sort forecasts by date and return up to requested days
    forecasts.sort(key=lambda f: f.date)
    return forecasts[:days]