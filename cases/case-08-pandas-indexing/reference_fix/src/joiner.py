"""Feature lookup — reference fix (O(1) online lookup, validated offline joins)."""
import pandas as pd


class FeatureJoiner:
    def __init__(self, features_path: str):
        features = pd.read_parquet(features_path)
        if features["user_id"].duplicated().any():
            raise ValueError("features table has duplicate user_id — rebuild upstream")
        self._by_user = (
            features.set_index("user_id").to_dict(orient="index")  # O(1) dict lookup
        )

    # ---------- online path (per request) ----------
    def lookup(self, user_id: int) -> dict | None:
        return self._by_user.get(user_id)  # None = unknown user; caller decides explicitly

    # ---------- offline path (50M-row nightly logs) ----------
    def join_logs(self, logs: pd.DataFrame) -> pd.DataFrame:
        features = pd.Series(self._by_user, name="_f").reset_index(names="user_id")
        features = pd.json_normalize(features["_f"]).assign(
            user_id=features["user_id"].values
        )
        merged = logs.merge(
            features, left_on="uid", right_on="user_id",
            how="left", validate="m:1", indicator=True,
        )
        n_missing = (merged["_merge"] != "both").sum()
        if n_missing / max(len(merged), 1) > 0.005:
            raise ValueError(f"{n_missing} log rows with unknown users (>0.5%)")
        merged = merged.drop(columns="_merge").sort_values(["uid", "ts"])
        # per-user next-outcome label; unknown tail rows are DROPPED, not zero-filled
        merged["label"] = merged.groupby("uid")["converted"].shift(-1)
        merged = merged.dropna(subset=["label"])
        return merged.sort_values(["uid", "ts"]).groupby("uid", observed=True).head(50)
