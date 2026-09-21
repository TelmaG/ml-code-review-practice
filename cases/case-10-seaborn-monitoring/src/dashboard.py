"""Weekly model-monitoring dashboard charts."""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_theme()


def build_dashboard(predictions_path: str, out_dir: str = "reports") -> None:
    df = pd.read_parquet(predictions_path)  # ~15M rows

    # 1. score distribution, this week vs last week
    last_week = df[df["ts"] < df["ts"].max()]
    sns.kdeplot(data=last_week, x="score", label="last_week")
    sns.kdeplot(data=df, x="score", label="this_week")
    plt.legend()
    plt.savefig(f"{out_dir}/score_dist.png")
    plt.close()

    # 2. per-segment calibration
    for seg in df["segment"].unique():
        sub = df[df["segment"] == seg]
        plt.scatter(sub["score"], sub["label"], alpha=0.6)
        plt.title(seg)
        plt.savefig(f"{out_dir}/calib_{seg}.png")
        plt.close()

    # 3. correlation heatmap of all numeric columns
    corr = df.corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm")
    plt.savefig(f"{out_dir}/corr.png")
    plt.close()

    # 4. drift alert: if the score mean moved, page oncall
    if abs(df["score"].mean() - last_week["score"].mean()) > 0.01:
        print("DRIFT ALERT: score mean moved")
