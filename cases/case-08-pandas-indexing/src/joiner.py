"""Feature lookup for online scoring + nightly training joins."""
import pandas as pd


class FeatureJoiner:
    def __init__(self, features_path: str):
        self.features = pd.read_parquet(features_path)  # 10M users x 40 cols

    # ---------- online path (per request) ----------
    def lookup(self, user_id: int) -> dict:
        row = self.features[self.features["user_id"] == user_id]
        if len(row) == 0:
            return {}
        return row.iloc[0].to_dict()

    # ---------- offline path (50M-row nightly logs) ----------
    def join_logs(self, logs: pd.DataFrame) -> pd.DataFrame:
        merged = logs.merge(self.features, left_on="uid", right_on="user_id")
        merged = merged.drop_duplicates()
        merged["label"] = merged["converted"].shift(-1).fillna(0)  # next-row outcome
        grouped = merged.groupby("uid").apply(lambda g: g.sort_values("ts").head(50))
        return grouped.reset_index(drop=True)
