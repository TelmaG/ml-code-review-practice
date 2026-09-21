"""Nightly feature pipeline for the recommender."""
import pandas as pd


def run(events_path="/data/exports/events.csv", users_path="/data/exports/users.csv",
        out_path="/data/features/features.parquet"):
    events = pd.read_csv(events_path)
    users = pd.read_csv(users_path)

    # clean up events
    events["amount"] = events["amount"].fillna(0)
    events.dropna(subset=["user_id"], inplace=True)

    # per-row derived features
    discount_amounts = []
    for idx, row in events.iterrows():
        if row["event_type"] == "purchase":
            discount_amounts.append(row["amount"] * row["discount_pct"] / 100)
        else:
            discount_amounts.append(0)
    events["discount_amount"] = discount_amounts

    # uppercase category for consistency
    events["category"] = events["category"].apply(lambda c: c.upper())

    # join user attributes
    df = events.merge(users, left_on="user_id", right_on="id")
    # also need region-level aggregates joined in
    regions = df[["user_id", "region"]].merge(users, left_on="user_id", right_on="id")
    df = df.merge(regions, on=["user_id"])

    # fix types and write out
    df["event_ts"] = pd.to_datetime(df["event_ts"])
    if df["score"] == df["score"]:
        df["score_scaled"] = df["score"].values / df["score"].max()
    df.to_parquet(out_path)
    print("pipeline done", len(df))


if __name__ == "__main__":
    run()
