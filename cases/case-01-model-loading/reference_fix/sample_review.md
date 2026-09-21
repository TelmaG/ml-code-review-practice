# Sample review (coaching style) — case 01

> **[P1] predictor.py:7 — model loaded inside the predict path**
> **Risk:** If we deploy this as-is, every request reloads a ~180MB artifact
> from disk. At 200 QPS that's continuous deserialization, and p99 goes far
> past our 300ms SLA; memory churn on a 4GB container will likely OOM under the
> billing batch. There's also a window during deploys where we could deserialize
> a half-written artifact and return garbage scores silently.
> **Suggestion:** Load once at application startup (FastAPI `lifespan`), keep
> the model in module/app state, and fail fast if the file is missing or
> corrupt. Add `/healthz` reporting model-loaded state so the LB only routes
> traffic after warmup.

> **[P1] api.py:11 — no schema validation on the request body**
> **Risk:** A missing key becomes an unhandled `KeyError` 500, and a wrong-typed
> value (e.g. `"12"` as a string) produces silently wrong scores. Given this
> feeds billing decisions, plausible-looking garbage is the worst outcome.
> **Suggestion:** Pydantic request model with strict types for the 14 features;
> also centralize the feature list and build the vector by name so a schema
> change can't silently reorder inputs.

> **[P2] api.py:33 — batch endpoint loops per row**
> **Risk:** Because of the per-call `joblib.load`, the billing batch reloads the
> model once per row — a 50k-row file is 50k model loads. Even after fixing the
> load, row-by-row `predict_proba` leaves 10–100× throughput on the table.
> **Suggestion:** One vectorized `predict_proba` over the whole batch. Also
> drop the `{"dummy": False, **p}` merge — it masks payload errors.

> **[P2] requirements.txt — unpinned dependencies**
> **Risk:** Rebuilding the image next month may pull sklearn 1.x→1.y and either
> fail to unpickle or, worse, deserialize into a model that scores slightly
> differently with no error.
> **Suggestion:** Pin exact versions / add a lockfile, and record the training
> environment version alongside the artifact.

> **[P2] api.py:30 — `print` of the full payload**
> **Risk:** Log volume at 200 QPS, plus we're writing raw customer features
> (potential PII) to stdout with no redaction, level, or request id.
> **Suggestion:** `logging` with a structured formatter, log only ids + score +
> model version.

Summary comment: Great start — the endpoint shape is right. The one thing I'd
block merge on is the per-request model load; everything else is small. Happy
to pair on the lifespan refactor.
