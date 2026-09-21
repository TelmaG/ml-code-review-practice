# Answer key

## P1
1. No timeouts; `f.result()` waits forever and one dependency can hold the request beyond 120ms.
2. Creates a new thread pool and three connections per request; at high QPS this exhausts threads/FDs and multiplies downstream load.
3. No partial/hedged policy: a failed model fails the whole ensemble; no model-version/schema validation or score range checks.

## P2
4. No connection pooling/session reuse or circuit breakers.
5. No cancellation of slow futures after deadline; work continues after caller timeout.
6. Simple mean has no weighting/calibration and may be invalid if models are correlated.
