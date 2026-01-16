import numpy as np
from global_land_mask import globe

def predict_drift(lat, lon, weather):
    if not weather:
        return [], False

    rad = np.deg2rad(weather["dir"])
    dx = float(np.sin(rad) * weather["speed"] * 0.15)
    dy = float(np.cos(rad) * weather["speed"] * 0.15)

    new_lat = float(lat + dy)
    new_lon = float(lon + dx)

    path = [
        (float(lat), float(lon)),
        (new_lat, new_lon)
    ]

    # 🔥 CRITICAL FIX: convert numpy.bool_ → bool
    beaching = bool(globe.is_land(new_lat, new_lon))

    return path, beaching

