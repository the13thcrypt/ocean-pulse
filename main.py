from fastapi import FastAPI
from fastapi.responses import FileResponse
from gee_ship_detection import detect_ships
from predictor import predict_drift
from weather_service import fetch_weather
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Serve frontend
@app.get("/")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

# ✅ Ships + waste prediction API
@app.get("/ships")
def get_ships():
    ships = detect_ships()
    results = []

    for ship in ships:
        lat = ship["lat"]
        lon = ship["lon"]

        weather = fetch_weather(lat, lon)
        path, beaching = predict_drift(lat, lon, weather)

        results.append({
            "ship": ship,
            "path": path,
            "beaching": beaching
        })

    return results
