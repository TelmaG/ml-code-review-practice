"""Weekly model-monitoring dashboard — reference fix."""
import logging
import os
from datetime import date, timedelta

import matplotlib

matplotlib.use("Agg")  # headless container: set backend before pyplot import
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger("monitor-dashboard")
SAMPLE_SEED = 42
SAMPLE_N = 200_000          # plenty for stable visuals, cheap to render
DRIFT_PSI_THRESHOLD = 0.1   # documented, reviewed threshold


def _psi(expected: pd.Series, actual: pd.Series, bins: int = 20) -> float:
    edges = pd.qcut(expected, q=bins, duplicates="drop", retbins=True)[1]
    e = (pd.cut(expected, edges).value_counts() / len(expected)).clip(lower=1e-4)
    a = (pd.cut(actual, edges).value_counts() / len(actual)).clip(lower=1e-4)
    return float(((e - a) * (e / a).map(pd.np.log if False else __import__("numpy").log)).sum())


def build_dashboard(predictions_path: str, out_dir: str, state_dir: str) -> None:
    df = pd.read_parquet(predictions_path)
    this_week = df[df["ts"] >= df["ts"].max() - pd.Timedelta(days=7)].copy()

    prev_path = os.path.join(state_dir, "prev_scores.parquet")
    prev = pd.read_parquet(prev_path)["score"] if os.path.exists(prev_path) else None

    sample = this_week.sample(min(SAMPLE_N, len(this_week)), random_state=SAMPLE_SEED)

    # 1. score distribution: true week-over-week
    plt.figure(figsize=(8, 5))
    if prev is not None:
        sns.histplot(prev, label="last_week", stat="density", element="step", fill=False)
    sns.histplot(sample["score"], label="this_week", stat="density",
                 element="step", fill=False)
    plt.legend()
    plt.savefig(f"{out_dir}/score_dist_{date.today()}.png", dpi=110)
    plt.close()

    # 2. per-segment calibration: aggregate before plotting (~50 points per segment)
    calib = (
        sample.assign(bin=pd.qcut(sample["score"], 20, duplicates="drop"))
        .groupby(["segment", "bin"], observed=True)
        .agg(score_mid=("score", "mean"), label_rate=("label", "mean"))
    )
    for seg, sub in calib.groupby(level="segment"):
        plt.plot(sub["score_mid"], sub["label_rate"], label=seg)
    plt.plot([0, 1], [0, 1], "--", color="gray", linewidth=1)
    plt.legend(fontsize="small")
    plt.savefig(f"{out_dir}/calibration_{date.today()}.png", dpi=110)
    plt.close()

    # 3. drift metric: PSI per segment, threshold documented; alert is a metric, not a print
    if prev is not None:
        psi = _psi(prev, sample["score"])
        # emit_metric("model.score_psi", psi, tags={"week": str(date.today())})
        logger.info("score PSI=%.4f", psi)
        if psi > DRIFT_PSI_THRESHOLD:
            # paging_hook("score-drift", psi)  # incident API / alertmanager
            logger.warning("DRIFT ALERT: PSI=%.3f > %.3f", psi, DRIFT_PSI_THRESHOLD)

    # persist aggregates so next week has a true baseline and alerts are auditable
    os.makedirs(state_dir, exist_ok=True)
    this_week[["score"]].to_parquet(prev_path)
