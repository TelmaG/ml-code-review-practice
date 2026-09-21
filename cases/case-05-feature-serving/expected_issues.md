# Answer key — case 05

## P1

1. **Blocking sync HTTP call inside an async handler** — `requests.get` in the
   event-loop coroutine. One 2s feature-service spike blocks the loop → *all*
   concurrent requests stall → p99 detonates exactly when the dependency is
   degraded. → `httpx.AsyncClient` (or run sync in a threadpool deliberately).
2. **No timeout** — vendor degradation = worker threads/coroutines pile up
   until the container is wedged; "died slowly at peak" incident. → explicit
   connect/read timeouts.
3. **Silent default fallbacks** — `data.get("risk_score", 0.5)` / `1.0` turn a
   schema change or partial outage into *plausible fabricated features* — the
   worst silent failure class for a model input. → fail fast or explicit,
   telemetry-visible fallback; never an invisible constant. If fallback cached
   values are the policy (per ticket), they must be *fresh* cached values with
   an age metric.

## P2

4. **No caching despite 80% hot-account traffic** — 500 QPS × 1 HTTP each =
   500 QPS onto the feature service for mostly identical lookups; also burns
   the p99 budget on repeat work. → TTL cache (e.g. 30–60s) or in-process LRU;
   staleness limits per the incident policy.
5. **No connection pooling / session reuse** — new TCP+TLS (or at least new
   connection) per request; at 500 QPS ephemeral-port/FD exhaustion is a real
   failure mode. → one shared `httpx.AsyncClient` with limits, created at
   startup.
6. **No retry/backoff, no circuit breaker** — every transient feature-service
   blip becomes an error at the caller; a multi-minute degradation wedges
   everything (see #1) with no isolation. → small retry on transient status,
   breaker that opens during degradation and serves the cached/policy fallback.
7. **`resp.json()` without `raise_for_status`** — a 500 HTML error page becomes
   a JSONDecodeError; a 200-with-new-shape becomes silent defaults (#3).
8. **No stale-cache degradation path at all** — the ticket *requires* a defined
   degraded mode (≤5 min last-known, then fail fast); the code has none — it
   will just error or fabricate.

## P3

9. No validation on `payload` (KeyError 500s), hardcoded URL, no request id
   propagation, no metrics (cache hit rate, feature-service latency,
   fallback-activated count), no tests for the degraded mode.

## The headline

"Sync is simpler and works in staging" — staging has no concurrency and a
healthy feature service. Under production p99 spikes this design turns a
dependency's bad minute into **our** outage, plus silent fabricated features.
Both are structural, not "optimize later".
