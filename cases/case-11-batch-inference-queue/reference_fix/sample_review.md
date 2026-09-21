> **[P1] worker.py:10 — model load per message.** If deployed as-is, each 400MB deserialize consumes the SLA and causes disk/memory pressure. Load once during startup and expose readiness.

> **[P1] worker.py:22 — failed messages are acknowledged.** A transient model or publish error becomes permanent data loss. Retry boundedly, then dead-letter and alert.

> **[P1] worker.py:16 — publish/ack has no idempotency contract.** A worker crash can duplicate output. Use message IDs as idempotency keys and make output writes deduplicating.
