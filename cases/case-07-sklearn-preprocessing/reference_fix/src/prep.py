"""Shared feature preprocessing — reference fix (fit-once Pipeline, persisted)."""
import numpy as np
import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

CATEGORICAL = ["plan_type", "region", "acquisition_channel"]
NUMERIC = ["monthly_spend", "tenure_months", "usage_gb"]
EPS = 1e-6

PREPROCESSOR_PATH = "artifacts/preprocessor.joblib"


def build_preprocessor() -> Pipeline:
    """Fit me ONCE during training. At serve time: load, never refit."""
    return Pipeline(steps=[
        ("cols", ColumnTransformer(transformers=[
            ("cat", Pipeline([
                ("impute", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore",
                                         min_frequency=10)),  # rare cats grouped
            ]), CATEGORICAL),
            ("num", Pipeline([
                ("impute", SimpleImputer(strategy="median")),
                ("scale", MinMaxScaler()),
            ]), NUMERIC),
        ]))
    ])


def engineer(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["spend_per_month"] = out["monthly_spend"] / out["tenure_months"].clip(lower=1)
    out["usage_per_tenure"] = out["usage_gb"] / (out["tenure_months"] + EPS)
    n_inf = np.isinf(out[["spend_per_month", "usage_per_tenure"]]).sum().sum()
    if n_inf:
        raise ValueError(f"{n_inf} infinite values after feature engineering")
    return out


def transform(df: pd.DataFrame, preprocessor: Pipeline) -> pd.DataFrame:
    missing = set(CATEGORICAL + NUMERIC) - set(df.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")
    features = preprocessor.transform(engineer(df))
    return pd.DataFrame(features, columns=preprocessor.get_feature_names_out())
