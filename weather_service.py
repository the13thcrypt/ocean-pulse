import requests

def fetch_weather(lat, lon):
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current_weather=true"
        )
        r = requests.get(url, timeout=5)
        data = r.json().get("current_weather")

        if not data:
            return None

        return {
            "speed": float(data["windspeed"]),
            "dir": float(data["winddirection"])
        }
    except Exception:
        return None
