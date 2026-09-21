> **[P1] gateway.py:10 — tenant identity is caller-controlled.** A client can submit another tenant id and consume their budget or access their response metadata. Derive identity from authenticated claims and authorize every request.

> **[P1] vendor call has no timeout/retry policy or breaker.** At 5k/sec, a vendor incident can exhaust all workers and retries can amplify it. Use pooled async clients, bounded per-tenant concurrency, timeouts, and retry only 429/5xx with jitter.

> **[P1] `body.get('text', '')` hides malformed responses.** Return an explicit typed error and count failures; empty text must not look like a successful completion.
