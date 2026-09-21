"""Shared feature preprocessing for churn model (train + serve)."""
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

CATEGORICAL = ["plan_type", "region", "acquisition_channel"]
NUMERIC = ["monthly_spend", "tenure_months", "usage_gb"]


def build_features(df: pd.DataFrame, fit: bool = True):
    """Return a feature matrix ready for the model."""
    out = df.copy()

    # encode categoricals
    for col in CATEGORICAL:
        le = LabelEncoder()
        out[col] = le.fit_transform(out[col])

    # scale numerics to [0, 1]
    scaler = MinMaxScaler()
    out[NUMERIC] = scaler.fit_transform(out[NUMERIC])

    # drop rows with any nulls to keep the model simple
    out = out.dropna()

    # engineer a couple of ratios we discussed in the ticket
    out["spend_per_month"] = out["monthly_spend"] / out["tenure_months"]
    out["usage_per_tenure"] = out["usage_gb"] / out["tenure_months"]

    return out[CATEGORICAL + NUMERIC + ["spend_per_month", "usage_per_tenure"]].values
