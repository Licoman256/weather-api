from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Weather Service", version="0.1.0")

class ForecastResponse(BaseModel):
    date: str
    temperature: float

@app.get("/ping")
def ping():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/forecast", response_model=List[ForecastResponse])
def get_forecast(days: int = 3):
    """
    Get forecast for the next N days
    Example: /forecast?days=3
    """
    dummy_data = [
        {"date": "2025-08-20", "temperature": 27.5},
        {"date": "2025-08-21", "temperature": 28.0},
        {"date": "2025-08-22", "temperature": 26.7},
    ]
    return dummy_data[:days]
