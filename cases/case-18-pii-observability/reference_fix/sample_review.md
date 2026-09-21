> **[P1] api.py:13 — raw payload and result enter retained logs.** For financial applications this risks exposing applicant data to every log consumer. Redact/allowlist fields, hash a request id, and never log raw features.

> **[P1] missing model version and structured error telemetry.** We cannot correlate a regression to an artifact or distinguish validation, dependency, and model failures. Emit bounded structured events.

> **[P2] `time.time()` and unbounded logging.** Use monotonic latency and sampling/rate limits so observability does not become the bottleneck.
