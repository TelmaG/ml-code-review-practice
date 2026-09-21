# Answer key

## P1
1. A single arbitrary .5 threshold is not calibrated to costs, base rates, or the stated fairness goal; no performance/fairness trade-off is measured.
2. `dropna(group)` is omitted, so missing group rows affect overall behavior but disappear from group reporting; fairness metrics can look better than reality.
3. Group comparison uses selection rate only, not calibrated risk, TPR/FPR, equalized odds, or confidence intervals; the output is descriptive, not an enforceable guardrail.

## P2
4. `.groupby().apply` and print are not production monitoring; no versioned report, alert, or audit trail.
5. No threshold stability/holdout validation; optimizing on the same calibration data will overfit.
6. No policy for proxy/sensitive attributes, privacy, or intersectional groups.
