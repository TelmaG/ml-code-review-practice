# Feedback phrasing templates (coaching style)

Core pattern: risk first, suggestion second. The goal is to de-risk a deployment,
not grade homework.

## The canonical format

> **[severity] file:line — observation**
> **Risk:** If we deploy this as-is, `<failure mode>` under `<load/scale condition>`.
> **Suggestion:** Refactor to `<pattern>` — e.g. `<library/mechanism>`. Happy to pair on it.

## Worked examples per anti-pattern class

### Model loading in the predict path
> **[P1] api.py:23 — model loaded from disk inside `/predict`**
> Risk: If we deploy this as-is, every request pays a disk read + deserialize
> (100–500ms for this model size). At 200 QPS the disk queue and GC pressure
> will push p99 past the 300ms SLA, and a concurrent load during a hot reload
> can serve a half-written artifact.
> Suggestion: Load once at application startup (FastAPI lifespan handler),
> fail fast if the artifact is missing/corrupt, and add a `/healthz` that
> reports model-loaded state.

### Pandas OOM
> **[P2] pipeline.py:41 — full `pd.read_csv` with no dtypes or chunking**
> Risk: This silently works today at 2GB; when the feed grows ~4× (already on
> the roadmap), the worker gets OOM-killed mid-job and the nightly table is
> stale with no error propagating.
> Suggestion: Specify `dtype=` + `usecols=` for immediate wins, switch to
> chunked processing (`chunksize=`) or move the heavy join to DuckDB/Polars/BigQuery.

### External call without timeout/retry
> **[P1] enrich.py:12 — `requests.get` with no timeout**
> Risk: One hung connection from the vendor API will hold a worker thread
> forever; under load this cascades into full thread-pool exhaustion — the
> service dies slowly and mysteriously at peak traffic.
> Suggestion: Always set `timeout=(connect, read)`, wrap in a retry policy with
> exponential backoff + jitter (e.g. `tenacity`), and cap concurrency. Decide
> now what the fallback is when the dependency is down: cached features, or
> fail the request fast?

### Missing seed / non-reproducibility
> **[P2] train.py — no `random_state` / seeds anywhere**
> Risk: If the run we promote can't be reproduced, debugging a prod regression
> becomes archaeology; we also can't trust A/B comparisons of two training runs
> because part of the delta is just RNG variance.
> Suggestion: Fix seeds (`numpy`, `random`, framework-specific) and pass
> `random_state` to every sklearn estimator/split; log the seed with the run.

### Swallowed exception (silent failure)
> **[P1] classify.py:57 — `except Exception: continue` around the LLM call**
> Risk: Rate limits and 5xx become empty labels mixed into good data. The job
> "succeeds", the report looks fine, and we ship a silently degraded dataset.
> Suggestion: Fail loud by default; if partial results are truly acceptable,
> count and log failures and abort the job above a threshold (e.g. >1%).

## Weakest → strongest phrasing

| Avoid | Prefer |
|---|---|
| "This is bad practice." | "If the vendor API hangs, this blocks a worker indefinitely." |
| "Use vectorization." | "This loop is O(rows × python overhead); the vectorized op is ~100× faster at 1M rows." |
| "Add retries." | "Add a retry with backoff+jitter on 429/5xx and a hard timeout; otherwise a rate-limit storm stalls the batch for hours." |
| "Don't hardcode." | "If this path differs between your laptop and the container, the job fails silently with an empty output." |

## Handling pushback (mock-interview mode)

- **"It works on my machine."** → "Sure — the failure mode I'm describing only
  appears under N× current load / when dependency X degrades. Here's the cheapest
  way to guard it."
- **"We'll fix it later."** → "Let's ticket it with an owner and a trigger
  (what metric tells us it became urgent?). Otherwise merge is blocked on this one."
- **"Performance doesn't matter here."** → "Agree if this stays at demo scale.
  If we expect it in the serving path within a quarter, the refactor is 10×
  cheaper now than after it's load-bearing."
- **"The linter passed."** → "The linter can't see failure semantics — it won't
  catch a swallowed exception or a missing timeout. Those are the ones that page us."
