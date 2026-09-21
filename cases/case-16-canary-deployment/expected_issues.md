# Answer key

## P1
1. Controller sleeps for an hour in a process with no durable state; restart loses the canary window and may leave traffic at 5% forever.
2. Uses conversion lift without sample size, confidence interval, traffic parity, or segment checks; noise can promote a regression.
3. Promotes to 100% based only on conversion, ignoring latency/error metrics required by the ticket.

## P2
4. Metrics calls and router writes have no timeout/retry/idempotency.
5. No monotonic state machine or compare-and-swap; two controller instances can promote and roll back out of order.
6. No explicit rollback watchdog/heartbeat if the controller dies during the canary.
