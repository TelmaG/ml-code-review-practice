> **[P1] ingest.py:8 — global fillna hides contract violations.** A missing category and missing amount are not the same event. The job can retrain on changed semantics without failing. Validate a versioned schema and apply field-specific policies.

> **[P1] ingest.py:10 — malformed amounts are coerced to zero.** If a producer sends currency text, the model sees legitimate zeros. Reject or quarantine rows and fail above a documented bad-row threshold.

> **[P1] train_job.py:8 — small data only prints.** The job still saves a model. Make data-quality gates fail before training and write a versioned artifact only after evaluation.
