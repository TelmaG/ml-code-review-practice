# Curriculum

The exercises progress through three levels. The first ten are short, focused
reviews. The medium and difficult cases are intentionally more extensive and
combine multiple modules and failure modes. Each case contains `ticket.md`,
`src/`, `expected_issues.md`, and a reference sample review. The CI structure
check ensures all cases retain these files.

## Easy: cases 01–10

One dominant anti-pattern per case, with a small amount of surrounding code.
Focus on spotting the failure, explaining the production impact, and proposing
one concrete fix.

## Medium: cases 11–20

Several modules and interacting issues. Review the contract between components,
calculate operational impact, and distinguish a local fix from a system fix.

| Case | Theme |
|---|---|
| 11 | batch inference queue and backpressure |
| 12 | feature-store freshness and cache stampede |
| 13 | data contracts and distribution drift |
| 14 | distributed training reproducibility |
| 15 | workflow orchestration and idempotency |
| 16 | model registry and canary deployment |
| 17 | Kafka streaming inference |
| 18 | PII-safe observability |
| 19 | hyperparameter search integrity |
| 20 | GPU serving and micro-batching |

## Hard: cases 21–30

Multiple services, adversarial edge cases, and trade-offs. Reviewers must reason
about time, ordering, statistical validity, failure recovery, security, and cost.

| Case | Theme |
|---|---|
| 21 | point-in-time feature correctness |
| 22 | multi-tenant LLM gateway |
| 23 | concurrent retraining orchestrator |
| 24 | statistically valid canary rollback |
| 25 | distributed join and data skew |
| 26 | model supply-chain security |
| 27 | event-time streaming and watermarks |
| 28 | fairness and threshold calibration |
| 29 | ensemble latency and hedged requests |
| 30 | multi-model artifact cache and hot reload |

For every case: read `ticket.md`, review `src/`, write review comments without
opening `expected_issues.md`, then compare after scoring. Revisit a level until
P1 recall is at least 90% twice before advancing.
