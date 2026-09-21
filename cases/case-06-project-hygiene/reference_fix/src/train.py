"""Demand forecast training — reference fix (seeded, split, versioned artifacts)."""
import argparse
import json
import os
import pickle
from datetime import date

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

SEED = 42
FEATURES = ["store_id", "day_of_week", "promo", "temperature"]
TARGET = "sales"


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df.dropna()


def train(df: pd.DataFrame) -> tuple[RandomForestRegressor, dict]:
    X, y = df[FEATURES], df[TARGET]
    X_train, X_valid, y_train, y_valid = train_test_split(
        X, y, test_size=0.2, random_state=SEED
    )
    model = RandomForestRegressor(random_state=SEED, n_estimators=200)
    model.fit(X_train, y_train)
    return model, {"r2_valid": model.score(X_valid, y_valid), "seed": SEED}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=os.environ.get("TRAIN_CSV", "data/sales.csv"))
    parser.add_argument("--out", default=os.environ.get("MODEL_DIR", "models"))
    args = parser.parse_args()

    model, metrics = train(load_data(args.data))

    version = date.today().isoformat()
    out_dir = os.path.join(args.out, version)
    os.makedirs(out_dir, exist_ok=True)
    joblib.dump(model, os.path.join(out_dir, "model.joblib"))
    with open(os.path.join(out_dir, "metadata.json"), "w") as f:
        json.dump({**metrics, "features": FEATURES}, f, indent=2)
    print(json.dumps(metrics))


if __name__ == "__main__":
    main()
