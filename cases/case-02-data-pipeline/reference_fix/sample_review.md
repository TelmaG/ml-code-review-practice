# Sample review — case 02

> **[P1] pipeline.py:6 — unbounded `read_csv`, no dtype spec, 2GB → 16GB worker**
> **Risk:** This works this week. At 15%/mo growth plus the object-dtype
> inflation (no `dtype=`), we're 2–3 months from a mid-night OOM kill — and the
> failure mode is the *trainer silently consuming yesterday's parquet*. Nobody
> pages on "job died but old file still there".
> **Suggestion:** `dtype=`/`usecols=` today, `chunksize=` or DuckDB/Polars as the
> follow-up. And emit to a versioned path + `_SUCCESS` marker so a failed run
> can't masquerade as fresh data.

> **[P2] pipeline.py:15 — `iterrows` over ~20M rows**
> **Risk:** The per-row Python loop plus the `.apply` below puts python overhead
> on the critical path of a 4h window; profile before merge, but expect this to
> dominate the runtime.
> **Suggestion:** `np.where(...)` for the discount, `.str.upper()` for the
> category — both single vectorized ops.

> **[P2] pipeline.py:23–25 — region merge multiplies rows**
> **Risk:** `regions` joins `users` onto an already-event-level frame and merges
> back on `user_id` without a uniqueness guarantee — if `id` duplicates once, we
> silently duplicate every event for that user, training on inflated weights.
> **Suggestion:** Aggregate to one row per user first and use
> `merge(..., validate="m:1")` so violations raise instead of passing silently.

> **[P2] pipeline.py:29 — NaN self-comparison + `.values`**
> **Risk:** `df["score"] == df["score"]` is elementwise — as an `if` condition it
> raises (or, in a future refactor, silently always-true/alway-false). This is
> exactly the silent-skip class of bug a sampled glance won't find.
> **Suggestion:** Drop the check and guard the division (`np.isfinite` on the
> max, or `fillna`). Use `.to_numpy()` if you truly need the array.

> **[P2] full-table normalizer (`score.max()`)**
> **Risk:** Fine for this nightly batch, but if serving recomputes this per
> request-batch, distributions drift between train and serve.
> **Suggestion:** Persist `score_max` alongside the artifact and reuse it at
> inference time.
