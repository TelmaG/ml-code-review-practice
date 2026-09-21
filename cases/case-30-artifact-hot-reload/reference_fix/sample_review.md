> **[P1] registry.py:10 — models are installed one at a time into the live map.** During reload, requests can see a partial or mixed version set. Build a complete immutable candidate snapshot, validate every artifact/schema, then atomically swap the reference.

> **[P1] old snapshot is never replaced.** `models = models` is a no-op, so model objects remain referenced across reloads and can exceed the 16GB budget. Track generations and release the previous snapshot only after in-flight requests drain.

> **[P1] watcher has no timeout or exception boundary.** A registry hang blocks refresh; one malformed artifact kills the thread silently. Add bounded requests, retry/backoff, failure metrics, and a readiness signal.
