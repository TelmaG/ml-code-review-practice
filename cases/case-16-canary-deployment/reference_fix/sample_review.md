> **[P1] controller.py:20 — `sleep(3600)` is not durable orchestration.** A restart loses the canary state while routing can remain at 5%. Persist a state machine and schedule evaluation checkpoints.

> **[P1] conversion lift alone is not a promotion test.** Without sample size/confidence bounds, latency, and errors, random noise can promote a bad model. Require statistical and operational guardrails.

> **[P2] concurrent controllers can race.** Use a versioned state transition or compare-and-swap and an independent rollback watchdog.
