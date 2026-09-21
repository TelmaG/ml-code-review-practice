# Answer key

## P1
1. External calls have no timeouts; a hung warehouse/registry/deploy task occupies a worker indefinitely.
2. Retry repeats non-idempotent registry and deployment calls; a timeout after deployment can trigger multiple promotions.
3. `/tmp/done` is written only at the end, locally, and is not used to resume. A retry repeats downloads/training/deployment and can use a partial artifact.

## P2
4. No run-scoped artifact paths or manifest; concurrent dates can overwrite `/tmp/model.pkl`.
5. Exceptions are swallowed after three attempts; orchestrator receives success/None semantics poorly and has no failure reason.
6. No validation gate between training and deployment; no model version, metric threshold, or approval state.
