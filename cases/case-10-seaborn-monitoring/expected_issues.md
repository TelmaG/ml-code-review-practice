# Answer key — case 10

## P1

1. **"This week" vs "last week" is wrong** — `last_week = df[df.ts < max(df.ts)]`
   means "everything before the newest timestamp" — for a 15M-row weekly
   extract that's ~all rows of this week, not the previous week; and `df`
   includes last week's rows too. Both curves show nearly the same thing → the
   drift chart lies *while looking plausible*, and the drift alert below
   inherits the same false reference.
   → filter on a 7-day window against `now`/max-date explicitly; persist last
   week's aggregates for a true comparison.
2. **Drift "alert" is a `print`** — pages nobody; the text goes to cron logs
   nobody reads. Silent-failure class. → emit a metric (Prometheus/statsd) +
   alertmanager route, or call the incident API; print as secondary.
3. **Per-point scatter of 15M rows** — `plt.scatter(sub.score, sub.label)` per
   segment sends the full rowset through matplotlib's renderer → minutes-to-
   hours and multi-GB RAM; on 8GB BI container: OOM or blown 15-min budget, and
   again a stale dashboard that looks "up to date". → aggregate first
   (`groupby(score_bin).label.mean()` then plot ~50 points), or sns.lineplot
   on binned means.
4. **`df.corr()` with `annot=True` over all numeric columns** — computes a
   full numeric×numeric matrix on 15M rows and annotates every cell (illegible
   for >15 cols anyway; seaborn heatmap with 15M rows upstream is slow).
   → select the relevant columns, compute Pearson on binned/sampled aggregates.

## P2

5. **kdeplot on 15M rows ×2** — KDE fitting is O(n²)-ish in bandwidth
   estimation for the default scipy backend → runtime explodes. → histograms or
   sample (fixed seed!) to ~100k rows for the visual.
6. **Comparing distributions by mean only** — mean-shift >0.01 misses
   variance/shape/tail drift; the "drift alert" trips or misses depending on
   noise, no threshold provenance, no segment slicing. → PSI/KS per segment,
   documented thresholds.
7. **No sampling seed anywhere** — any future `sample()` added under time
   pressure will produce non-comparable week-over-week charts; make the seed a
   constant now (also: seaborn's `kdeplot` Monte-Carlo path where applicable).
8. **Wrong file/deliverable hygiene** — writes PNGs into `reports/` with fixed
   names (each week silently overwrites last week's artifacts; no way to "see
   what the dashboard said when the alert fired"). → date-stamped outputs.

## P3

9. `print` for status, no logging; matplotlib backend not set (`Agg`) → flaky
   in headless containers (crashes if $DISPLAY leaks in); repetitious
   savefig/close; no figsize control; `palette`/style set globally affecting
   other jobs importing this module (side effects on import via
   `sns.set_theme()` at module level).

## The headline

Dashboards are model-adjacent production surfaces: a wrong-but-rendered chart
is worse than a failed job because **the business acts on it**. Two lies here:
the baseline comparison and the silent print-alert. Chart bugs don't page —
that's why the review has to.
