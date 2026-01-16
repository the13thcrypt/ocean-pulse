from global_land_mask import globe

def near_coast(lat, lon):
    return globe.is_land(lat + 0.05, lon)
