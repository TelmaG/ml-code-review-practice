# PR: Kafka online classifier

Context: Events arrive at 50k/sec, sometimes out of order. The consumer must preserve per-user ordering, tolerate replay, and commit offsets only after predictions are durably written.