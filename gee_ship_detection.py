import ee

# Initialize Earth Engine
ee.Initialize()

# 🇮🇳 Arabian Sea – Mumbai shipping corridor
REGION = ee.Geometry.Rectangle([
    71.5, 18.0,   # lon_min, lat_min
    73.5, 20.5    # lon_max, lat_max
])

def detect_ships():
    # Sentinel-1 SAR collection (long-term aggregation)
    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(REGION)
        .filterDate("2023-01-01", "2023-12-31")
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(ee.Filter.listContains(
            "transmitterReceiverPolarisation", "VV"
        ))
        .select("VV")
    )

    # Median radar backscatter (persistent activity)
    median = collection.median()

    # Shipping corridor heuristic
    shipping_zones = median.gt(-14)

    # Vectorize zones safely
    vectors = shipping_zones.selfMask().reduceToVectors(
        geometry=REGION,
        scale=1000,               # coarse scale (safe)
        geometryType="centroid",
        eightConnected=False,
        bestEffort=True,
        maxPixels=1e7
    )

    features = vectors.limit(20).getInfo().get("features", [])

    results = []
    for f in features:
        lon, lat = f["geometry"]["coordinates"]
        results.append({
            "lat": float(lat),
            "lon": float(lon)
        })

    return results
