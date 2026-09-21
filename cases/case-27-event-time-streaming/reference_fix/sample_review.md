> **[P1] window.py:10 — window uses processing time, not event time.** A 20-minute late event lands in the wrong hour and features differ based on arrival order. Use event timestamps, watermarks, and an explicit late-event policy.

> **[P1] state is unbounded and process-local.** High-cardinality users grow memory forever and a restart loses features. Use bounded/state-store-backed windows with checkpoints and event-id deduplication.

> **[P2] no watermark/state metrics.** Instrument lag, dropped-late counts, state bytes, and restore duration before trusting the feature.
