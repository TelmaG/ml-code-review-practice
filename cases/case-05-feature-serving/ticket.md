# PR #455: Real-time feature enrichment sidecar

**Author:** backend-eng · **Reviewers:** you · **Target:** `main`

## Context

Ticket: FEAT-201 — the scoring service needs two live features
(`account_risk_score`, `region_price_index`) from the internal feature service
before it can score.

- The calling service runs at **~500 QPS** (async FastAPI), SLA p99 < 250ms
  end-to-end. Feature service typical latency 20–40ms, p99 spikes to ~2s,
  occasional multi-minute degradation (documented last month).
- ~80% of requests hit one of ~2,000 hot accounts — same features repeatedly.
- Behavior required when the feature service is down: **serve with the last
  known features for ≤5 min, then fail requests fast** (per the incident policy).

Author's note: "Sync is simpler than async here and works fine in staging.
Let's ship and optimize later if needed."
