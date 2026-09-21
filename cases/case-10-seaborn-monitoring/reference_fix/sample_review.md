# Sample review — case 10

> **[P1] dashboard.py:13 — "last week" is computed as `ts < max(ts)`**
> For a weekly extract that's ~the whole current week, so both curves render
> nearly identical distributions — and they *look* fine, which is the danger.
> The drift alert below compares the same wrong populations. If we deploy this
> as-is, the first real drift will show a flat overlay and the weekly review
> will draw wrong conclusions with full confidence.
> **Suggestion:** explicit 7-day window, and persist last week's aggregates so
> the baseline is real and auditable.

> **[P1] dashboard.py:32 — drift alert is a `print`**
> Pages nobody; goes to a cron log nobody reads. Silent-failure class — an
> alerting surface that can never alert. Emit a metric + alertmanager route,
> or call the incident API; keep the print as secondary logging.

> **[P2] per-point scatter over 15M rows**
> 15M points through matplotlib's renderer = minutes-to-hours + multi-GB RAM on
> an 8GB container; the 15-min budget goes with it, and we get a stale
> dashboard that looks current. Aggregate first — bin scores to 20 points per
> segment and plot the means.

> **[P2] kdeplot ×2 + `corr(annot=True)` on the full frame**
> KDE's default density estimation doesn't scale to 15M rows; the heatmap
> annotates every cell of a full numeric×numeric matrix — slow to build,
> illegible to read. Histograms on a seeded 200k sample for the visual; narrow
> the correlation to the columns the review actually uses.

> **[P2] fixed output filenames** — every week silently overwrites last week's
> charts, and when an alert fires there's no artifact to look back at.
> Date-stamp outputs and persist the comparison aggregates.

> **[P2] mean-only drift** — misses variance/tail movement. PSI or KS with a
> documented threshold, per segment. Happy to pair on the PSI helper.

The dashboard UI itself is solid — colors, layout, churn is readable. What's
needed is statistical correctness on the baseline, a real alert channel, and
pre-aggregation before rendering.
