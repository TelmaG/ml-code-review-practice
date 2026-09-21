> **[P1] controller.py:11 — concurrent jobs share one output path.** Models overwrite each other and the returned run id does not identify the bytes served. Give each run an immutable directory and write a manifest with code/data/config hashes.

> **[P1] promote has no concurrency control.** Two successful runs can race and last-writer wins. Use a registry transaction/compare-and-swap with an explicit promotion policy.

> **[P2] subprocess failures are ignored.** Require `check=True`, a timeout, durable state transitions, and promote only after evaluation and health checks.
