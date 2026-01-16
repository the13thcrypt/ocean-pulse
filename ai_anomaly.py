from sklearn.ensemble import IsolationForest
import numpy as np

model = IsolationForest(
    n_estimators=100,
    contamination=0.05,
    random_state=42
)

trained = False

def train(features):
    global trained
    if len(features) >= 10:
        model.fit(features)
        trained = True

def score(feature_vector):
    if not trained:
        return 0.0
    return model.decision_function([feature_vector])[0]
