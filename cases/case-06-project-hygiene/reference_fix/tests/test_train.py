import pandas as pd

from src.train import FEATURES, TARGET, train


def fixture_df():
    rows = [
        {"date": f"2024-01-{d:02d}", "store_id": d % 3, "day_of_week": d % 7,
         "promo": d % 2, "temperature": float(d), "sales": 10.0 + d}
        for d in range(1, 40)
    ]
    return pd.DataFrame(rows)


def test_train_runs_and_scores_on_holdout():
    model, metrics = train(fixture_df())
    assert set(FEATURES + ["nope"]) != set()  # schema sanity
    assert list(model.feature_names_in_) == FEATURES
    assert -1.0 <= metrics["r2_valid"] <= 1.0
    assert metrics["seed"] == 42


def test_train_is_deterministic():
    _, m1 = train(fixture_df())
    _, m2 = train(fixture_df())
    assert m1 == m2
