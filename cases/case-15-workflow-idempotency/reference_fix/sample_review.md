> **[P1] workflow.py:6–8 — retries wrap non-idempotent calls.** A deployment timeout can mean the deploy succeeded; retrying may promote twice or race another run. Give every operation a run-scoped idempotency key and make registry/deploy APIs idempotent.

> **[P1] no timeouts on external calls.** One hung dependency can hold an orchestrator slot forever. Use connect/read timeouts and classify retryable statuses.

> **[P1] local `/tmp/done` is not a resume protocol.** Concurrent workers and crashes can reuse partial artifacts. Use durable run state, immutable artifact paths, and a manifest of completed stages.
