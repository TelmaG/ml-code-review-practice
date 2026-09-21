# PR #730: Model quality dashboards — plotting utilities

**Author:** analytics-eng · **Reviewers:** you · **Target:** `main`

## Context

Ticket: DASH-14 — weekly model-monitoring dashboard.

- Input: weekly predictions parquet — **~15M rows** (user_id, score, label,
  segment, ts).
- Output: 4 PNG charts for the weekly business review + a "drift alert" if
  distributions moved.
- Runtime budget: 15 min on the BI container (8GB RAM). The dashboard feeds a
  distribution-shift alarm that pages the oncall.
- Author's note: "Charts render on the sample data and look correct."
