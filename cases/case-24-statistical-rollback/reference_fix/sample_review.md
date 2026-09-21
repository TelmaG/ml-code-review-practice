> **[P1] evaluator.py:9 — mean conversion difference is not a statistical decision.** Repeated users, seasonality, and sample size make noise look like a regression. Use a predeclared experiment window, confidence bounds/clustered analysis, minimum sample size, and guardrails.

> **[P1] mean latency >200 is not the SLA signal.** Tail latency and error rate matter; use p95/p99 with units and a minimum sample count.

> **[P2] metrics calls lack timeouts and decisions lack durable audit/idempotency.** A metrics outage must fail closed, and rollback transitions need a state machine, cooldown, and recorded inputs.
