# Answer key

## P1
1. Means are compared without confidence intervals, sample size, randomization, repeated-user clustering, or seasonality; false rollback/promote decisions are likely.
2. Latency threshold uses mean and unit is unclear; p99/tail latency is the operational risk.
3. Network calls have no timeout and the function has no durable action/idempotency; a metrics outage can produce an unsafe decision.

## P2
4. No guard against candidate/baseline population imbalance or missing windows.
5. No multiple-observation policy, hysteresis, or cooldown; alert flapping possible.
6. No audit record of decision inputs, model versions, and threshold configuration.
