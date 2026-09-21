# Answer key

## P1
1. Model is loaded for every message: 400MB disk reads and deserialization destroy the 5-minute SLA. Load once at startup and fail readiness if unavailable.
2. Exception path acknowledges the message, silently losing predictions. Retry transient failures and route poison messages to a dead-letter queue with metrics.
3. Publish then ack is not transactional; a crash after publish causes duplicates, while a crash before publish causes redelivery. Use an idempotency key and an outbox/transactional queue pattern.

## P2
4. Whole message payload becomes an unbounded DataFrame; enforce message size and batch limits, use streaming/chunking.
5. Fixed sleep reduces throughput and does not implement backpressure; use bounded concurrency and visibility timeout renewal.
6. No schema or output count validation; wrong input can produce misaligned predictions.
