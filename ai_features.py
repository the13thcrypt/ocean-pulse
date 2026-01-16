import time

ship_features = {}

def update_features(mmsi, speed, confidence, distance_to_coast):
    if mmsi not in ship_features:
        ship_features[mmsi] = {
            "speed": [],
            "confidence": [],
            "distance": [],
            "last_seen": time.time()
        }

    ship_features[mmsi]["speed"].append(speed)
    ship_features[mmsi]["confidence"].append(confidence)
    ship_features[mmsi]["distance"].append(distance_to_coast)
    ship_features[mmsi]["last_seen"] = time.time()

def get_feature_matrix():
    matrix = []
    mmsi_list = []

    for mmsi, f in ship_features.items():
        vector = [
            sum(f["speed"]) / len(f["speed"]),
            max(f["confidence"]),
            min(f["distance"])
        ]
        matrix.append(vector)
        mmsi_list.append(mmsi)

    return matrix, mmsi_list
