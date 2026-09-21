# Answer key — case 08

## P1

1. **O(n) scan per request in the online path** — `features[features.user_id ==
   user_id]` does a full 10M-row scan per lookup at 800 QPS → the service melts.
   → set the index once (`features.set_index("user_id")` / a dict or dedicated
   store) for O(1) lookups. The 200-user unit test hides this completely —
   review must extrapolate to 10M.
2. **Silent missing-user semantics differ between paths** — online returns `{}`
   (caller must guess), offline merge drops unknown users (`inner` by default).
   If the caller does `**lookup()` or forwards empty dicts as "not found", two
   codepaths disagree silently about new users. → explicit policy: raise /
   default-with-flag, identical in both paths, plus a missing-rate metric.
3. **Label construction leaks across users + invents labels** —
   `shift(-1)` on the merged frame crosses user boundaries (last row of user A
   predicts with user B's outcome) and `.fillna(0)` fabricates "didn't convert"
   labels for genuinely-unknown tails. Training set is corrupt *silently*.
   → `groupby("uid")["converted"].shift(-1)` and drop (not fill) missing tails.

## P2

4. **Unvalidated merge keys** — no uniqueness check: if `user_id` duplicates in
   features (a bad rebuild), the merge multiplies log rows silently.
   → `validate="m:1"`.
5. **`drop_duplicates()` on the full merged frame** — expensive no-op guard that
   also *hides* the duplication root cause (#4). 50M×40 cols dedup = minutes of
   nightly time and a mask for data bugs.
6. **`groupby().apply(lambda sort+head)`** — python-level apply per group over
   50M rows → the nightly window blows. → vectorized
   `sort_values(...).groupby("uid").head(50)`.
7. **Memory**: 10M×40 float64 in memory per worker replica — fine on one box,
   but the class holds the raw parquet frame rather than a typed/indexed
   representation; per-replica RAM multiplies under replication.

## P3

8. No dtype tightening for `user_id` (int64 vs string mismatches between parquet
   and logs → silent merge miss), no logging/metrics, no tests at realistic
   scale or for the boundary-leak case.

## The headline

Two separate bugs are "correct-looking": O(n) lookups (works at 200 users) and
`shift(-1)` (works in a single-user notebook). **Scale and boundaries are where
pandas eats people** — state the arithmetic in the review: 800 QPS × 10M-row
scan ≈ 8 billion row-comparisons/sec.
