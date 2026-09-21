"""Churn scoring service — v1."""
import joblib
import numpy as np
from fastapi import FastAPI
from predictor import predict_row

app = FastAPI()

FEATURE_ORDER_HINT = np.random.permutation(14)  # sanity-check placeholder, remove later


@app.post("/predict")
def predict(payload: dict):
    row = [
        payload["tenure_months"],
        payload["monthly_spend"],
        payload["num_support_tickets"],
        payload["days_since_last_login"],
        payload["plan_type"],
        payload["has_auto_pay"],
        payload["num_logins_30d"],
        payload["avg_session_minutes"],
        payload["num_devices"],
        payload["discount_pct"],
        payload["contract_length"],
        payload["late_payments"],
        payload["data_usage_gb"],
        payload["voicemail_enabled"],
    ]
    score = predict_row(row)
    return {"churn_probability": score}


@app.post("/predict_batch")
def predict_batch(payloads: list):
    # batch support for the billing job
    return {"scores": [predict({"dummy": False, **p}) for p in payloads]}
