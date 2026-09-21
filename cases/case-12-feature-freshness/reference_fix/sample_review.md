> **[P1] cache.py:10 — warehouse request has no timeout and refresh is per caller.** A slow warehouse can create thousands of threads. Use one scheduled/single-flight refresh with connect/read timeouts and backoff.

> **[P1] cache.py:21 — expired values are returned while refresh is pending.** This violates the ten-minute contract and hides degradation. Store timestamps per entry, fail fast after the limit, and emit freshness metrics.

> **[P1] global dictionary replacement is unsynchronized.** Build an immutable snapshot, validate it, then atomically swap the reference.
