> **[P1] features.py:10 — profile join is not point-in-time.** Current profile values can include changes after the transaction, so the model learns future information and the evaluation is invalid. Use an as-of join constrained to `updated_at <= event_ts`.

> **[P1] rolling feature includes future/current information.** Sort by event time and use a closed-left window ending before the prediction timestamp. Add a temporal leakage test with a future profile update.

> **[P1] no temporal split/validation.** A high metric is not evidence until a future-month holdout and PIT invariants pass.
