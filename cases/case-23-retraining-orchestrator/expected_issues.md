# Answer key

## P1
1. All concurrent jobs write `/shared/model.pkl`; artifacts overwrite and each result may point to another model.
2. Promotion loop has no lock/compare-and-swap; last writer wins regardless of quality or intended ordering.
3. UUID is generated but not used in artifact path/manifest; retries create ambiguous, non-reproducible runs.

## P2
4. `subprocess.run` ignores return code and timeout; failed/long jobs can be promoted.
5. State writes are non-atomic and stringified Python objects, not durable structured state.
6. Symlink creation can fail if current exists and no rollback/health check exists.
