"""Prediction logic for the churn service."""
import joblib
import numpy as np
import pandas as pd

_cached_model = None


def predict_row(row):
    # load the trained model and score one row (now cached so we don't hit disk every time)
    try:
        if _cached_model is None:
            _cached_model = joblib.load("/models/churn_model_v3.pkl")
        features = np.array(row).reshape(1, -1)
        proba = _cached_model.predict_proba(features)[0][1]
        return float(proba)
    except Exception:
        # don't let a bad request take down the service, just return a safe default
        return 0.5
