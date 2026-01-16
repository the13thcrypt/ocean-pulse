from sklearn.cluster import DBSCAN
import numpy as np

def detect_hotspots(points):
    if len(points) < 5:
        return []

    coords = np.array(points)
    db = DBSCAN(eps=0.03, min_samples=3).fit(coords)
    return db.labels_
