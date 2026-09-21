# ML platform code review rubric

The checklist to internalize. Severity scale:

- **P1** — silent failure, data corruption, or outage under realistic load. Blocks merge.
- **P2** — significant latency/cost/reproducibility problem. Fix before merge or ticketed with owner.
- **P3** — nit / maintainability. Optional.

## 1. Silent failures (highest priority)

| # | Check | P1 example |
|---|---|---|
| 1.1 | Exceptions swallowed (`except: pass`, bare `except Exception`) | LLM/API failures return empty predictions scored as normal |
| 1.2 | Wrong-but-valid outputs: no validation of model input/output schema | Feature order drift between train and serve → plausible garbage |
| 1.3 | Data leakage: transforms/state fitted before train/valid split, or on full data | `StandardScaler().fit(X)` before split → inflated offline metrics |
| 1.4 | Reproducibility: seeds not fixed (numpy / torch / TF / `random_state`), non-deterministic algorithms | Model retrains differ run-to-run; debugging impossible |
| 1.5 | Fallbacks that mask outages: cached default predictions, silent stale features | Feature service down → model silently serves last week's features |
| 1.6 | Metrics that hide failure: accuracy on imbalanced data, no per-class/error slicing | 99% accuracy predicting the majority class |
| 1.7 | Missing model/data versioning on save/load paths | `model.pkl` overwritten; can't roll back or audit |

## 2. Latency & resource bottlenecks

| # | Check | P1/P2 example |
|---|---|---|
| 2.1 | **Model loaded inside the predict path** instead of app startup | `joblib.load` per request → disk I/O + GC pressure per call |
| 2.2 | Per-row operations on dataframes: `iterrows`, `apply` where vectorized ops exist, row-wise HTTP/DB calls | 1M-row pipeline takes hours; per-request feature fetch adds 200ms p99 |
| 2.3 | Unbounded memory: `read_csv` of huge files without dtype spec/chunking,full-cartesian merges, copied datasets per worker | OOM kill at 2am when input grows 3× |
| 2.4 | Sequential network where batching/async is safe | 10k LLM calls × 1s = 3h instead of minutes |
| 2.5 | Blocking I/O in async/event-loop handlers | One slow dependency stalls the whole service |
| 2.6 | No connection/session reuse (`requests.get` per call instead of `Session`) | TLS handshake per request; FD exhaustion |
| 2.7 | Repeated expensive computation with no caching (same features fetched per request) | 99% of feature lookups are duplicates |

## 3. Reliability of external calls (API / LLM)

| # | Check |
|---|---|
| 3.1 | **No timeout** on any HTTP/LLM call |
| 3.2 | **No retry with backoff + jitter** around transient failures |
| 3.3 | No circuit breaker / fallback policy for a down dependency |
| 3.4 | No idempotency / resume state on long batch jobs (crash at 90% = restart from 0) |
| 3.5 | No rate-limit awareness (429 handling) |
| 3.6 | Secrets hardcoded or logged |

## 4. Serving hygiene

| # | Check |
|---|---|
| 4.1 | Heavy init (model load, tokenizer download, warmup) at startup, not first request |
| 4.2 | Pydantic/JSON-schema validation on request bodies |
| 4.3 | Structured logging (`logging`, levels), never `print` |
| 4.4 | Config via env/params, no hardcoded absolute paths |
| 4.5 | `model.eval()` / `torch.no_grad()` in PyTorch inference |
| 4.6 | Batch prediction endpoint used where traffic is batched |
| 4.7 | Model loading failures crash the app at startup (fail fast), not the first request |

## 5. Project hygiene

| # | Check |
|---|---|
| 5.1 | Dependencies pinned; lockfile present |
| 5.2 | Data/model artifacts not committed to git (use DVC/object store) |
| 5.3 | Tests exist and exercise the ML-specific risks (leakage, determinism, schema) |
| 5.4 | CI runs tests + linters |
| 5.5 | Notebooks cleaned of large outputs if committed |

## 6. Library-specific traps (cases 07–10)

| # | Check |
|---|---|
| 6.1 | sklearn: anything `.fit` at serve time? Encoders/scalers must be fitted once in training, persisted, loaded |
| 6.2 | sklearn: unseen-category handling (`handle_unknown`), and no ordinal encoding of nominal columns |
| 6.3 | pandas: is any per-request lookup a full-frame scan? Index/dict for O(1) |
| 6.4 | pandas: `shift`/`rolling` without `groupby` — leaks across entity boundaries |
| 6.5 | numpy: verify the math *direction* of normalization (subtract-then-divide), not just broadcastability |
| 6.6 | numpy: every intermediate allocation sized — `np.eye(n²)`, implicit float64 promotion, list-of-arrays stacking |
| 6.7 | seaborn/matplotlib: aggregate/sample before plotting; per-point rendering of millions of rows is a silent budget-killer |
| 6.8 | dashboards: comparisons against a real persisted baseline; alerts through a real channel, never `print` |

## Interview answer shape

For each finding: **what → risk under load/prod → concrete suggestion → severity**.
Never "this is bad style". Always "if we deploy this as-is, we risk X; I suggest Y".
