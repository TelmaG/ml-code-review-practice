# Answer key

## P1
1. Auto-commit can advance offsets before prediction output is flushed; a crash loses events.
2. Producer send is asynchronous and never flushed/checked; output durability and errors are unknown.
3. No event-time/order handling or idempotency. Replays and out-of-order events can produce wrong state and duplicate predictions.

## P2
4. One event per model call under 50k/sec; no micro-batching/backpressure, likely falling behind.
5. No schema validation, dead-letter topic, retry policy, or poison-message handling.
6. No partition/key assertion for per-user ordering.
