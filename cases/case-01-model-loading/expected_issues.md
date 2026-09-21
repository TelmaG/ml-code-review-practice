# Answer key — case 01 (do not read before self-scoring)

## P1

1. **Model loaded inside the predict path** — `predictor.py:predict_row` calls
   `joblib.load(...)` on **every request**. At 200 QPS with a ~180MB artifact
   this means continuous disk reads + deserialization; p99 blows past the 300ms
   SLA and memory churn may OOM the 4GB container. Also a risk of serving a
   half-written artifact on deploy. → Load once at app startup (FastAPI
   lifespan/startup event), fail fast if the artifact is missing/corrupt.
   *Detector: partially (general smells)*
2. **No request validation** — raw `dict` payload, `KeyError` on any missing
   feature → unhandled 500, and no type/NaN checks. Wrong-but-valid input (floats
   as strings) is accepted and produces plausible garbage. → Pydantic request
   model with strict types.
3. **Feature order drift risk** — features assembled as a bare positional list in
   `predict`; nothing ties this order to the training schema. Silent wrong
   predictions if the schema changes. → Build the vector from a named feature map.
4. **Unpinned dependencies** — `requirements.txt` has no versions. Rebuilds may
   pull a different sklearn and deserialize the artifact into a subtly different
   model (silent score shift) or crash. → Pin versions + lockfile.

## P2

5. **`predict_batch` loops per row** — reloads the model N times (consequence of
   #1) and scores rows one by one instead of a single vectorized
   `predict_proba` on the batch. Also `{"dummy": False, **p}` mutates dict
   merging for no reason — a leftover hack that masks errors.
6. **Hardcoded absolute model path** — `/models/churn_model_v3.pkl` differs
   between dev/CI/prod; failure mode is a crash on first *request*, not at
   startup. → env-configured path, loaded at startup.
7. **`print` instead of structured logging** — logs full payload (potential PII)
   at info level with no request id, level, or destination control.
8. **No model version surfaced in the response/health** — can't audit which
   artifact served a prediction; rollback story unclear.

## P3

9. No `/healthz` / readiness endpoint (LB can't know if the model is loaded).
10. No error-handling boundary returning controlled 4xx/5xx bodies.

## What the linter catches vs misses (study this)

- `ml_smell_detector`: noisy environment / `print`, some general smells, magic
  patterns. It will partially flag #1/#7.
- **It cannot see**: the startup-vs-per-request lifecycle argument, the SLA
  math, feature-order semantics, PII in logs. That's the human layer.
