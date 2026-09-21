# Python & ML-engineering concept map

Single source of truth for `python-mastery-coach`. Each `##` heading is a
concept id referenced by `tools/gap_analysis.py`'s pattern classifier. Keep ids
in sync between the two files.

---

## variable-scope-and-closures

### The mental model
Assigning to a name anywhere inside a function makes Python treat it as local
for the *entire* function body — even on lines before the assignment. Reading
it before that point raises `UnboundLocalError`, not "falls through to the
outer scope." To reassign a module-level name from inside a function, you must
declare `global name` (or `nonlocal` for enclosing-function scope) first.

### Why it bites in production
A "let's cache this at module level" fix is one of the most common
production-adjacent bugs juniors write: it looks like caching, passes a quick
local test where the exception is swallowed, and silently degrades into
"never actually caches, always hits the fallback path."

### Worked example (do this correctly)
```python
_cached_model = None

def get_model():
    global _cached_model
    if _cached_model is None:
        _cached_model = load_model()
    return _cached_model
```
Better yet, avoid the footgun entirely with a class or `functools.lru_cache`:
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_model():
    return load_model()
```

### Self-check
```python
counter = 0

def increment():
    counter = counter + 1
    return counter

print(increment())
```
What happens when you run this? Why, specifically — what does Python do
differently here versus a plain `print(counter)` with no assignment in the
function?

### Go deeper
- Python docs: [Naming and binding](https://docs.python.org/3/reference/executionmodel.html#naming-and-binding)
- Python docs: [`global` statement](https://docs.python.org/3/reference/simple_stmts.html#the-global-statement)

---

## exception-handling-and-silent-failure

### The mental model
`except Exception:` (or bare `except:`) catches everything, including bugs you
didn't anticipate. Returning a plausible-looking default from that block turns
a loud crash into a silent lie: the caller can't tell "the model said 0.5"
from "something broke and we made up 0.5."

### Why it bites in production
This is the #1 silent-failure anti-pattern across the whole case set (P1 in
nearly every case involving external calls or model inference). At scale, a
swallowed exception isn't one bad response — it's every response from the
moment the exception starts firing, with no alert.

### Worked example (do this correctly)
```python
try:
    result = risky_call()
except SpecificExpectedError as e:
    logger.warning("expected failure, falling back", exc_info=e)
    return fallback_value  # documented, monitored fallback
# let anything else propagate — an unexpected exception should be loud
```
Rule of thumb: catch the narrowest exception type you can name, and if you
must have a fallback, log it and count it as a metric so someone notices the
fallback rate climbing.

### Self-check
```python
def parse_amount(raw):
    try:
        return float(raw)
    except Exception:
        return 0.0

amounts = [parse_amount(x) for x in ["12.50", "N/A", "8.00", ""]]
total = sum(amounts)
```
What does `total` silently include that it shouldn't? What's the difference
between this failing loudly vs. this specific implementation?

### Go deeper
- Python docs: [Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html)
- PEP 3134: [Exception Chaining and Embedded Tracebacks](https://peps.python.org/pep-3134/)

---

## data-contracts-and-schema-validation

### The mental model
Untyped dicts and positional lists have no enforced shape. The moment the
producer (a training notebook, an upstream service) changes field order or
adds/removes a field, every consumer silently gets garbage instead of an error.

### Why it bites in production
Feature-order drift between train and serve is a recurring P1: the model
still runs, still returns a number, and that number is meaningless.

### Worked example (do this correctly)
```python
from pydantic import BaseModel

class ScoreRequest(BaseModel):
    tenure_months: float
    monthly_spend: float
    plan_type: int
    # ... explicit, named, typed

FEATURES = list(ScoreRequest.model_fields)  # single source of truth for order

def to_vector(req: ScoreRequest):
    return [getattr(req, f) for f in FEATURES]
```
The vector is built from names, not from a hand-typed positional list that can
silently drift out of sync with the training schema.

### Self-check
Two files define the "same" record shape independently:
```python
# training.py
COLUMNS = ["age", "income", "region"]

# serving.py
def build_row(payload):
    return [payload["age"], payload["region"], payload["income"]]  # bug: order
```
Nothing here raises an exception. How would you design this so the bug becomes
a loud error instead of a silent one?

### Go deeper
- Pydantic docs: [Models](https://docs.pydantic.dev/latest/concepts/models/)

---

## concurrency-and-shared-state

### The mental model
Mutable module-level state read/written by multiple requests or threads
without synchronization can be observed mid-update. "It worked in my manual
test" doesn't prove thread safety — it proves you got lucky with timing once.

### Why it bites in production
Cache-refresh and hot-reload code paths (feature caches, model registries)
are exactly where this recurs: one goroutine/thread is replacing a dict while
another reads it, and readers can see a half-updated state.

### Worked example (do this correctly)
```python
import threading

_lock = threading.Lock()
_state = {}

def refresh(new_data: dict):
    global _state
    with _lock:
        _state = new_data  # atomic pointer swap, not a mutation of the old dict

def read(key):
    return _state.get(key)  # safe: dict reference read is atomic in CPython
```
Prefer building a whole new immutable snapshot and swapping the reference,
over mutating an existing shared structure in place.

### Self-check
```python
cache = {}

def refresh():
    for k, v in fetch_all().items():
        cache[k] = v  # mutates in place, one key at a time
```
A reader calling `cache.get(k)` mid-refresh — what could it see that's
inconsistent, and why does building a new dict first and swapping avoid that?

### Go deeper
- Python docs: [`threading` — Lock objects](https://docs.python.org/3/library/threading.html#lock-objects)
- Python docs: [GIL and atomicity of built-in types](https://docs.python.org/3/glossary.html#term-global-interpreter-lock)

---

## reproducibility-and-randomness

### The mental model
Every source of randomness (`random`, `numpy.random`, framework RNGs, dataset
shuffling, weight initialization) needs an explicit seed, or two runs of
"the same" code produce different models and different metrics — with no way
to tell whether a change in a metric came from your code change or from RNG.

### Why it bites in production
Unseeded training makes promotion decisions untrustworthy: you can't tell if
0.97 AUC is real progress or noise from an unseeded split.

### Worked example (do this correctly)
```python
import random
import numpy as np
import torch

def set_seeds(seed: int = 42) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
```
Call this once at the top of every training entrypoint, and pass
`random_state=seed` to every sklearn split/estimator.

### Self-check
```python
from sklearn.model_selection import train_test_split

X_train, X_test = train_test_split(X, test_size=0.2)
model = train(X_train)
print(evaluate(model, X_test))
```
Run this twice. Why do you get two different numbers, and which specific line
is responsible?

### Go deeper
- scikit-learn docs: [Controlling randomness](https://scikit-learn.org/stable/common_pitfalls.html#controlling-randomness)

---

## data-leakage-and-train-serve-skew

### The mental model
Any statistic (mean, scaler, encoder) must be *fit* on training data only and
*applied* (not refit) everywhere else, including at serve time. Fitting on
data that includes validation/test/future rows leaks information the model
wouldn't have in production and inflates offline metrics.

### Why it bites in production
`StandardScaler().fit_transform(X)` before the split is the single most common
"secretly high offline metric" bug. Point-in-time joins have the same root
cause: joining "current" state instead of "state as of the prediction time."

### Worked example (do this correctly)
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X_train, X_valid, y_train, y_valid = train_test_split(X, y, random_state=42)
scaler = StandardScaler().fit(X_train)          # fit on train ONLY
X_train = scaler.transform(X_train)
X_valid = scaler.transform(X_valid)             # transform, never refit
# persist `scaler` alongside the model artifact; serving loads and transforms only
```

### Self-check
```python
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # fit on the WHOLE dataset
X_train, X_valid = train_test_split(X_scaled, test_size=0.2)
```
What information from the validation rows has leaked into the training
features here, and why does that inflate the validation metric specifically?

### Go deeper
- scikit-learn docs: [Data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage)

---

## resilient-external-calls

### The mental model
Every network call needs three things: a timeout (bounded wait), a retry
policy for transient failures (backoff + jitter, not infinite retries), and a
defined behavior for when the dependency is down (fail fast vs. degraded
fallback) — decided in advance, not improvised in a `try/except`.

### Why it bites in production
No-timeout is the most common P1 across LLM/API cases: one hung connection
holds a worker forever, and under load that becomes total thread-pool
exhaustion.

### Worked example (do this correctly)
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential

@retry(wait=wait_random_exponential(multiplier=1, max=30), stop=stop_after_attempt(3))
async def call_dependency(client: httpx.AsyncClient, payload: dict):
    resp = await client.post(URL, json=payload, timeout=httpx.Timeout(connect=1, read=3))
    resp.raise_for_status()
    return resp.json()
```

### Self-check
```python
import requests

def get_features(user_id):
    resp = requests.get(f"{URL}/{user_id}")
    return resp.json()
```
Name two independent ways this function can hang or misbehave under a slow or
degraded dependency, and what's the minimal change to guard against each?

### Go deeper
- `httpx` docs: [Timeouts](https://www.python-httpx.org/advanced/timeouts/)
- `tenacity` docs: [Retrying](https://tenacity.readthedocs.io/en/latest/)

---

## pandas-vectorization

### The mental model
`DataFrame.iterrows()` and row-wise Python loops pay per-row interpreter
overhead; vectorized operations (`np.where`, `.str.*`, boolean masks) run the
loop in C once over the whole column. The performance gap grows linearly (or
worse) with row count.

### Why it bites in production
Fine on a 200-row unit test, catastrophic on the 20M-row nightly job it will
actually run against.

### Worked example (do this correctly)
```python
import numpy as np

df["discount_amount"] = np.where(
    df["event_type"] == "purchase", df["amount"] * df["discount_pct"] / 100, 0.0
)
```
instead of looping row by row and appending to a list.

### Self-check
```python
results = []
for _, row in df.iterrows():
    results.append(row["price"] * 1.2 if row["taxable"] else row["price"])
df["total"] = results
```
Rewrite this as a single vectorized expression. What's the rough speedup you'd
expect at 1M rows, and why?

### Go deeper
- pandas docs: [Enhancing performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)

---

## numpy-memory-and-broadcasting

### The mental model
Broadcasting only checks that shapes are *compatible* — it says nothing about
whether the operation is mathematically correct (e.g., subtract-then-divide
vs. multiply-then-add both "work" shape-wise). Separately, every intermediate
array has a real memory cost: `np.eye(n)` on a large `n` allocates `n²`
elements even if you only wanted a scalar multiply.

### Why it bites in production
A silently-inverted normalization formula produces plausible-looking numbers
that are just wrong — the worst kind of bug because nothing crashes.

### Worked example (do this correctly)
```python
mean = np.array([0.485, 0.456, 0.406])[None, None, None, :]
std = np.array([0.229, 0.224, 0.225])[None, None, None, :]
normalized = (batch.astype(np.float32) / 255.0 - mean) / std
```
Always sanity-check normalization with a known input: mean should land near 0,
std near 1, on real data.

### Self-check
```python
scale = np.eye(50176) * 0.01
result = batch @ scale
```
What is this code actually trying to compute, and what's the memory cost of
computing it this way versus the direct equivalent?

### Go deeper
- NumPy docs: [Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)

---

## asyncio-and-blocking-io

### The mental model
An `async def` function only yields control at `await` points. Calling a
synchronous, blocking library (`requests`, blocking file I/O) inside it still
blocks the *entire event loop* — every other concurrent request on that
worker stalls too, not just the one making the call.

### Why it bites in production
"Sync is simpler" works fine locally with no concurrency; in production a
single slow dependency call inside an `async def` handler can stall hundreds
of concurrent requests at once.

### Worked example (do this correctly)
```python
import httpx

async def get_features(client: httpx.AsyncClient, user_id: str):
    resp = await client.get(f"/accounts/{user_id}/features")
    return resp.json()
```
If you must call a genuinely sync library, run it in a thread pool explicitly:
`await asyncio.to_thread(sync_call, args)`.

### Self-check
```python
import requests
from fastapi import FastAPI

app = FastAPI()

@app.post("/enrich")
async def enrich(payload: dict):
    resp = requests.get(EXTERNAL_URL)  # sync call inside async def
    return resp.json()
```
Under 500 concurrent requests, what happens to the other 499 while one
`requests.get` call is in flight?

### Go deeper
- Python docs: [asyncio — Coroutines and Tasks](https://docs.python.org/3/library/asyncio-task.html)
- FastAPI docs: [Concurrency and async/await](https://fastapi.tiangolo.com/async/)

---

## security-and-untrusted-input

### The mental model
`pickle.load`/`pickle.loads` executes arbitrary code embedded in the byte
stream — it is not a safe format for anything you didn't produce yourself.
Any URL or path built from caller input needs an allowlist, not just a
well-formed-string check, or it becomes an SSRF/path-traversal vector.

### Why it bites in production
Loading a model artifact from an unauthenticated, caller-controlled URL and
unpickling it is a remote-code-execution primitive, not just a reliability bug.

### Worked example (do this correctly)
```python
import hashlib

def load_verified_artifact(path: str, expected_sha256: str):
    data = open(path, "rb").read()
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha256:
        raise ValueError("artifact digest mismatch — refusing to load")
    return joblib.load(path)  # only after verifying provenance
```
Prefer a signed, allowlisted artifact reference over accepting an arbitrary
URL at all.

### Self-check
```python
def load_model(url: str):
    data = requests.get(url).content
    return pickle.loads(data)
```
List two distinct ways an attacker could exploit this function if `url` comes
from a request parameter.

### Go deeper
- Python docs: [`pickle` — security warning](https://docs.python.org/3/library/pickle.html#module-pickle)
- OWASP: [Server-Side Request Forgery](https://owasp.org/www-community/attacks/Server_Side_Request_Forgery)

---

## statistics-for-ml-systems

### The mental model
A difference in means between two small or noisy samples is not evidence of a
real effect without accounting for sample size, variance, and — for
repeated-user or seasonal traffic — non-independence. "Number went down"
is not the same statement as "we are confident the model regressed."

### Why it bites in production
Canary/rollback decisions based on raw mean deltas will flap on noise or miss
real regressions depending on traffic patterns that day.

### Worked example (do this correctly)
```python
from scipy import stats

t_stat, p_value = stats.ttest_ind(candidate_scores, baseline_scores, equal_var=False)
if p_value < 0.05 and candidate_scores.mean() < baseline_scores.mean():
    # statistically significant regression, not just a lower number
    trigger_rollback()
```
Also check minimum sample size and consider clustering by user if traffic is
repeated-user.

### Self-check
```python
if candidate_conversion.mean() - baseline_conversion.mean() < -0.01:
    rollback()
```
What's missing from this decision rule that a statistics-aware version would
include?

### Go deeper
- SciPy docs: [`scipy.stats.ttest_ind`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html)

---

## event-time-and-windowing

### The mental model
"Now" (`time.time()`, wall-clock arrival) is not the same as "when the event
actually happened" (its own timestamp field). Windowing by arrival time
assigns late/out-of-order events to the wrong bucket; windowing by event time
requires an explicit policy for how late an event can arrive before it's
dropped (a watermark).

### Why it bites in production
A feature computed by processing-time window looks fine in a low-latency demo
and silently corrupts results the moment real-world network delay or
mobile-offline queuing introduces late events.

### Worked example (do this correctly)
```python
# conceptually: bucket by the event's own timestamp, not arrival time
bucket = event["event_ts"].replace(minute=0, second=0, microsecond=0)
if event["event_ts"] < watermark - LATE_TOLERANCE:
    drop_as_too_late(event)
else:
    windows[bucket].add(event)
```

### Self-check
```python
def add(event):
    bucket = int(time.time() // 3600)  # arrival-time bucket
    windows[bucket].append(event["amount"])
```
An event with `event["event_ts"]` from 40 minutes ago arrives now due to a
network retry. Which bucket does it land in here, and why is that wrong?

### Go deeper
- Apache Beam docs (concepts apply beyond Beam): [Watermarks and late data](https://beam.apache.org/documentation/programming-guide/#watermarks-and-late-data)

---

## dependency-and-environment-management

### The mental model
An unpinned dependency file is not a reproducible environment — it's a
recipe that resolves to different concrete versions depending on when it's
installed. "Works on my machine" often means "resolved a different dependency
graph than production will."

### Why it bites in production
A model deserialized under a different scikit-learn/numpy version than it was
trained with can load "successfully" and silently score differently.

### Worked example (do this correctly)
```
# requirements.txt
scikit-learn==1.6.1
numpy==2.1.3
joblib==1.4.2
```
or a lockfile-managed tool (`uv`, `poetry`, `pip-tools`) that pins the full
transitive graph, not just direct dependencies.

### Self-check
```
pandas
scikit-learn
numpy
```
What could go wrong the next time someone runs `pip install -r
requirements.txt` against this file, six months from now?

### Go deeper
- Python Packaging docs: [Requirements files](https://pip.pypa.io/en/stable/reference/requirements-file-format/)

---

## structured-logging-and-observability

### The mental model
`print()` has no level, no structured fields, no routing, and no way to
sample or redact. Production logging needs levels (so volume is controllable),
structure (so fields are queryable), and a redaction policy (so PII/secrets
never land in a retained log store).

### Why it bites in production
Logging a raw request payload "for debugging" in a service that handles
financial or personal data is a compliance incident, not a style nit.

### Worked example (do this correctly)
```python
import logging

logger = logging.getLogger("service")

logger.info("prediction served", extra={"request_id": rid, "model_version": v})
# never: logger.info(f"payload={payload} result={result}")
```

### Self-check
```python
print(f"predicted churn={score} for payload={payload}")
```
Name two problems with this line beyond "it's not `logging`" — think about
what's actually in `payload` and who can read stdout in production.

### Go deeper
- Python docs: [`logging` HOWTO](https://docs.python.org/3/howto/logging.html)

---

## configuration-and-artifact-versioning

### The mental model
Two related hygiene habits: (1) configuration (paths, URLs, credentials)
belongs in environment variables or config files, not hardcoded literals, so
the same code runs correctly in dev/CI/prod; (2) artifacts you overwrite in
place (`model.pkl`, `current.pkl`) have no history — you can't tell what's
currently serving, when it changed, or roll back.

### Why it bites in production
A hardcoded `/models/x.pkl` path works on the author's machine and crashes (or
silently serves the wrong file) the moment the deployment layout differs. An
unversioned artifact overwrite means a bad deploy has no rollback path and no
audit trail of what actually served a given prediction.

### Worked example (do this correctly)
```python
import os
from datetime import date

MODEL_PATH = os.environ["MODEL_PATH"]  # fail fast at startup if unset

def save_versioned(model, out_dir: str):
    version = date.today().isoformat()
    path = f"{out_dir}/{version}/model.pkl"
    os.makedirs(f"{out_dir}/{version}", exist_ok=True)
    joblib.dump(model, path)
    return version  # expose this in the API response / health check
```

### Self-check
```python
MODEL_PATH = "/models/churn_model_v3.pkl"

def load():
    return joblib.load(MODEL_PATH)

def save(model):
    joblib.dump(model, MODEL_PATH)  # always the same path
```
Name two independent production problems this causes — one about environments,
one about auditability/rollback.

### Go deeper
- The Twelve-Factor App: [Config](https://12factor.net/config)

