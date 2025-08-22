# Weather Service (FastAPI + yr.no API)

Simple FastAPI service that fetches daily temperature forecasts using the yr.no API.

## Endpoints
- /ping → Health check
- /forecast → Returns temperature forecasts for up to N days
  - Params: days, latitude, longitude, altitude, time_of_day (hours)

## Run locally
python -m venv venv
.\venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --reload

view on http://127.0.0.1:8000

Docs: http://127.0.0.1:8000/docs

## Run with Docker
docker build -t weather-service .
docker run -d -p 8000:8000 weather-service

## Example Curl Request

### Linux / macOS
curl "http://127.0.0.1:8000/forecast?days=2&latitude=44.8176&longitude=20.4569&time_of_day=14"

### Windows PowerShell
curl.exe "http://127.0.0.1:8000/forecast?days=2&latitude=44.8176&longitude=20.4569&time_of_day=14"

### Example Response
[
  {"date": "2025-08-21", "time": "14:00:00", "temperature": 27.5},
  {"date": "2025-08-22", "time": "14:00:00", "temperature": 26.8}
]


## Example
curl "http://127.0.0.1:8000/forecast?days=2&latitude=44.8176&longitude=20.4569&time_of_day=14"

Response:
[
    {
      "date": "2025-08-22",
      "time": "14:00",
      "temperature": 25.4
    },
    {
      "date": "2025-08-23",
      "time": "14:00",
      "temperature": 25.6
    }
  ]
