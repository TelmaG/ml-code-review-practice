# Answer key

## P1
1. Uses processing time (`time.time`) instead of event time; late/out-of-order events are assigned to the wrong windows.
2. Unbounded state for high-cardinality users and no watermark/late-event policy; memory grows without bound.
3. State is process-local and lost on restart; replay can double-count because no event id/version deduplication.

## P2
4. No clock/event timestamp validation or future-event guard.
5. No partitioning/concurrency strategy; a hot user can become a state hotspot.
6. No metrics for watermark lag, dropped late events, state size, or recovery.
