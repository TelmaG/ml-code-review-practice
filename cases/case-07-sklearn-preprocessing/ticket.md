# PR #502: Churn prep library — reusable preprocessing module

**Author:** ds-team · **Reviewers:** you · **Target:** `main`

## Context

Ticket: CHURN-88 — factor out the feature prep we copy-paste everywhere.

- Consumed by **both** the nightly training job and the FastAPI serving service.
- Categorical features: `plan_type` (12 values), `region` (~400 values),
  `acquisition_channel` (8). Numeric: spend, tenure, usage counters.
- Serving receives single rows as JSON; training sends 5M-row dataframes.
- Author's note: "Tests pass on the sample. Ready to merge so serving can use it."
