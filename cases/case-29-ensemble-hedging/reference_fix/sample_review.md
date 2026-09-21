> **[P1] ensemble.py:9 — unbounded `f.result()` waits for the slowest model.** The 120ms p99 budget is lost when one dependency hangs. Set per-call deadlines, cancel losers, and define a bounded degraded response.

> **[P1] new executor and connections per request.** At production QPS this exhausts threads/FDs and multiplies downstream load. Reuse a bounded client/executor created at startup.

> **[P2] one failure aborts all models.** Validate response schema/ranges and define whether two healthy models can produce a calibrated fallback.
