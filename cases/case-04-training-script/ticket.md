# PR #77: Fraud model v2 — PyTorch retrain script

**Author:** ml-eng · **Reviewers:** you · **Target:** `main`

## Context

Ticket: FRAUD-15 — retrain the fraud classifier on Q2 data (binary
classification, ~1% positive rate), promote if AUC beats current prod (0.91).

- 800k transactions, parquet input, PyTorch MLP, single GPU.
- Runs ad-hoc on the shared training box; artifacts go to the model store at
  `/models/fraud/model.pt` (the serving container pulls that path on restart).
- The promotion decision is made off this script's printed metrics.

Author's note: "AUC 0.97 on validation, big lift over prod. Ready to promote —
can I get a quick stamp?"
