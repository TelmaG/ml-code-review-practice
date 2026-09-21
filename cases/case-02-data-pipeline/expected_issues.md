# Answer key — case 02

## P1

1. **OOM landmine: unbounded `read_csv` with no `dtype`/`usecols`** —
   `pipeline.py:6`. 2GB today, ~15%/mo growth, 16GB worker: object-typed
   columns (no dtype spec) inflate memory 3–5×; with the merges below we're
   already near the cliff. When it tips over it's an OOM-kill mid-night and a
   *stale features table with no error* (unless the scheduler alerts).
   → `dtype=`, `usecols=`, or chunked ingest; better: DuckDB/Polars for this size.
2. **Unknowingly silent failure in output** — the job's failure modes
   (OOM-kill, missing file) leave yesterday's `features.parquet` in place; the
   06:00 training job reads it happily. → Write to a versioned path
   (`features/2026-09-21.parquet`) + a `_SUCCESS` marker; training asserts on
   freshness. Also `print` instead of logging + no error propagation.

## P2

3. **`iterrows` over 20M rows** — the discount loop is python-speed; at 20M
   rows this alone can eat most of the 4h window. → vectorized
   `np.where(events.event_type == "purchase", amount * pct / 100, 0)`.
   *Detector: yes — "Unnecessary iteration (iterrows)"*
4. **Double merge + row-explosion risk** — `regions` merges `users` onto a
   frame already containing all event rows, then merges back on `user_id`
   only → row multiplication (cartesian per user) and silently duplicated
   events + 2× memory. → aggregate to user level first, or `map` region.
5. **Chain indexing / inplace mutation** — `events["amount"].fillna(0)`
   assigned back (SettingWithCopy risk in other forms), `dropna(inplace=True)`
   mutates mid-pipeline. → P2/nit per the rubric; prefer explicit reassignment.
   *Detector: yes — chain indexing / inplace smells*
6. **Unhashable/expensive `apply(lambda c: c.upper())`** — per-row python call;
   → `.str.upper()`.
7. **`df["score_scaled"] = df["score"].values / df["score"].max()`** + the
   weird `df["score"] == df["score"]` NaN check (a Series never equals itself
   where NaN — the condition is *always* an array, so `if` on it raises; this
   branch is actually broken → silent skip or crash). Also `.values` vs
   `.to_numpy()`. And: **normalizing by a max computed on the full night's data
   is fine here, but reusing it at serve time would be leakage** — worth one
   comment. *Detector: NaN equality, `.values` smell*
8. **No dtype spec** (drives #1), no `usecols`, timestamps parsed after the
   join instead of with `parse_dates`. *Detector: dtype smells*

## P3

9. Magic paths/paths hardcoded; `print` not logging; no run manifest (row
   counts in/out, schema hash); no test on a small sample fixture.

## What's the story to tell

The headline feedback is **not** "use vectorization" — it's "this job's failure
mode is a silent stale table at 03:12, and the review artifacts in place
(sampled a few hundred rows) would never catch it."
