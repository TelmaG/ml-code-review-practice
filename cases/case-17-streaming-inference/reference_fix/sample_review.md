> **[P1] consumer.py:5 — auto-commit is incompatible with durable output.** The offset can commit before the prediction is persisted, so a crash loses events. Disable auto-commit and commit only after checked producer acknowledgement.

> **[P1] no idempotency/order contract.** Replays duplicate predictions and out-of-order events can corrupt per-user state. Key partitions by user and deduplicate by event id/version.

> **[P2] one model call per event at 50k/sec.** Add bounded micro-batching and lag/backpressure metrics; otherwise the consumer falls behind silently.
