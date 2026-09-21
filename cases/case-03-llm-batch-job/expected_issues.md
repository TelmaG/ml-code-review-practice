# Answer key — case 03

## P1

1. **No timeout on the LLM call** — `classify()` has no `timeout=`. Vendor hangs
   (documented: 3 incidents last month) block a worker thread forever; the job
   stalls past the 6h window and looks "in progress". → `timeout=(connect, read)`.
2. **Swallowed exceptions → silent data corruption** — `except Exception: continue`
   turns 429s/5xx/hangs into *dropped* tickets. The trainer treats missing as a
   class (ticket says labels must be complete) — we ship a silently degraded
   dataset and the job reports success. → retry transient errors; abort above a
   failure threshold (e.g. >1%); persist failures for replay.
3. **No retry/backoff** — transient 429/5xx is guaranteed at 50k calls against a
   20 req/s API. → exponential backoff + jitter (tenacity), respect
   `Retry-After`, classify 429 vs 4xx (don't retry auth failures).
4. **Hardcoded API key in source** — committed secret; must rotate NOW, not
   "later", and history scrubbed. → env var / vault, and note in review that
   rotation is a prerequisite to merge.

## P2

5. **Sequential calls → runtime blowup** — 50k × ~1s ≈ 14h > 6h window. The
   author's 200-ticket test (~3min) extrapolates linearly — review arithmetic!
   → bounded concurrency (e.g. `asyncio` + semaphore or `ThreadPoolExecutor`)
   capped under 20 req/s with a rate limiter.
6. **No resume/checkpoint** — crash or timeout at 90% = restart from zero and
   double-pay the vendor. → write results incrementally (append + flush), skip
   already-labeled ids on restart (idempotency).
7. **No rate-limit awareness** — bursty loop will sit in 429 purgatory; no
   client-side pacing. → token bucket / semaphore at e.g. 15 req/s headroom.
8. **`resp.json()["label"]` without `raise_for_status` or schema check** —
   a 200 with an unexpected body (vendor deploys a change) yields cryptic
   KeyError mid-run, or worse a wrong field read. → `raise_for_status()` +
   validate the label is in `LABELS`.

## P3

9. `print` progress instead of logging; whole input read into memory (fine at
   50k, note for growth); no cost accounting (50k calls × price — worth one
   line in the review!); no dry-run flag; filename paths hardcoded.
10. Progress print at `i % 100` is fine, but combined with sequential calls the
    ETA math (i/elapsed) is missing — operationally nice.

## The headline

The author asked "can we run the full 50k tonight?" The reviewer's job is the
arithmetic: **no — 50k × 1s sequential ≈ 14h > 6h window, and the first hung
socket would stall it indefinitely with no record of what was missed.**
