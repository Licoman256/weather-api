from fastapi import FastAPI, HTTPException, Query
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