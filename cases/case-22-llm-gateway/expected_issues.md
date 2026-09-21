# Answer key

## P1
1. No timeout/retry classification/circuit breaker; 5k/sec can exhaust workers and retry storms can amplify vendor outages.
2. Tenant is accepted but not authenticated/authorized; one tenant can impersonate another and consume their budget.
3. No tenant rate limit, concurrency limit, or budget enforcement; noisy tenants starve others and costs are unbounded.
4. Default empty text turns malformed/vendor failures into successful-looking responses; validate status/schema and make failure explicit.

## P2
5. Sync requests in async-capable high-throughput gateway; no connection pooling or streaming.
6. Prompt and response retention/redaction policy is absent; cross-tenant logging risk.
7. No request id/idempotency or usage reconciliation.
