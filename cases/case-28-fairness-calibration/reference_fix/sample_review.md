> **[P1] calibrate.py:7 — `.5` is an arbitrary threshold.** It is not tied to lending costs or a measured fairness criterion. Evaluate a holdout across thresholds, report calibration plus TPR/FPR/selection-rate intervals, and get the policy decision recorded.

> **[P1] missing group values are excluded from the fairness story.** The overall system still serves them, so dropping them can conceal disparate behavior. Define an explicit unknown-group policy and report coverage.

> **[P2] print-only group output is not monitoring.** Persist versioned metrics and alert on confidence-aware regressions, including intersectional slices where sample size permits.
