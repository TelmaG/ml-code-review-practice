# PR #201: Nightly feature pipeline for the recommendation model

**Author:** growth-analytics · **Reviewers:** you · **Target:** `main`

## Context

Ticket: REC-88 — build the nightly preprocessing job that produces training
features for the recommender.

- Input: `events.csv` — raw clickstream export, currently **~2 GB / ~20M rows
  per night**, growing ~15% month over month. `users.csv` (~500k rows).
- Scheduled on a **16GB RAM** worker at 02:00; must finish before the 06:00
  training job.
- Output: `features.parquet` on the shared volume.

Author's note: "Runs in ~40 min on last week's extract. I sampled a few hundred
rows of output and the joins look right."
