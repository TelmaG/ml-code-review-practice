"""Prediction logic for the churn service — reference fix."""
import os
import joblib
import numpy as np

MODEL_PATH = os.environ["CHURN_MODEL_PATH"]  # fail fast at startup, not per-request

FEATURES = [
    "tenure_months", "monthly_spend", "num_support_tickets",
    "days_since_last_login", "plan_type", "has_auto_pay", "num_logins_30d",
    "avg_session_minutes", "num_devices", "discount_pct", "contract_length",
    "late_payments", "data_usage_gb", "voicemail_enabled",
]


class ChurnModel:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)
        self.version = os.path.basename(MODEL_PATH)

    def predict_proba(self, rows: list[dict]) -> np.ndarray:
        # build the matrix from named fields — protects against column-order drift
        matrix = np.array([[r[f] for f in FEATURES] for r in rows])
        return self.model.predict_proba(matrix)[:, 1]
