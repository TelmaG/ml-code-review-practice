# Sample review — case 05

> **[P1] sidecar.py:18 — blocking `requests.get` inside an async handler**
> **Risk:** Staging has no concurrency and a healthy dependency, so "sync is
> simpler" survives there. In prod, when the feature service hits its
> documented 2s p99, this blocks the event loop and *every* in-flight request
> stalls — a dependency's bad minute becomes our 250ms-SLA outage.
> **Suggestion:** `httpx.AsyncClient` (or an explicit `run_in_threadpool`),
> one shared client created at startup.

> **[P1] sidecar.py:11 — no timeout**
> **Risk:** No connect/read timeout means degradation piles up coroutines
> until the container wedges — no backpressure, no clean error, just a slow
> death at peak.
> **Suggestion:** explicit `httpx.Timeout(connect=1, read=2)` tuned to the SLA
> budget.

> **[P1] sidecar.py:14–15 — silent default values (`0.5`, `1.0`)**
> **Risk:** If the feature service changes its payload or returns a partial
> body, we fabricate plausible-looking features — the model scores garbage and
> nobody gets paged. For model inputs this is the worst silent-failure class.
> **Suggestion:** Validate keys explicitly and fail fast; if fallback is needed,
> the ticket's policy is last-known-good (≤5 min) from cache, marked + metered
> — never a baked-in constant.

> **[P2] no caching despite 80% hot-account repeat traffic**
> **Risk:** 500 QPS downstream for mostly identical lookups, paying full
> dependency p99 on every one. A 30–60s TTL cache absorbs most of it and buys
> the degraded mode for free.
> **Suggestion:** in-process TTL/LRU cache + cache-hit metric.

> **[P2] no session reuse / retry / breaker**
> **Risk:** New connection per request at 500 QPS (FD/ephemeral-port pressure),
> every transient 5xx surfaced to our caller, no isolation during multi-minute
> degradations.
> **Suggestion:** pooled keep-alive client, 1–2 retries on 5xx/timeouts, and a
> breaker that opens during degradation and routes to the cached fallback.

The requirement to have an explicit degraded mode is already in the ticket —
let's implement it (cache + stale window + 503 after) rather than discovering
the behavior during the next feature-service incident.
