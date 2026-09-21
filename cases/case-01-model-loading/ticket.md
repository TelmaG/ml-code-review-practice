# PR #137: Churn scoring service v1

**Author:** junior-ds · **Reviewers:** you · **Target:** `main`

## Context

Ticket: CHURN-42 — expose the churn model as a REST endpoint.

The data science team trained a churn model (`churn_model_v3.pkl`, ~180MB
joblib artifact) and wrapped it in FastAPI. The service will be deployed behind
the internal gateway:

- Expected traffic: **~200 QPS** at peak (billing batch calls + dashboard).
- SLA: **p99 < 300ms**.
- Input: JSON rows with the 14 features listed in `schema.md` (not shown here).
- Deployed on 2 vCPU / 4GB containers behind a load balancer.

Author's note: "Tested locally with curl, predictions look right. PTAL — would
love to merge this week so we can start the billing integration."

## Files changed

- `api.py` (new)
- `predictor.py` (new)
- `requirements.txt` (new)
