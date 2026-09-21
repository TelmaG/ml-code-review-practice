# PR #310: LLM auto-labeler for support tickets

**Author:** intern ML · **Reviewers:** you · **Target:** `main`

## Context

Ticket: SUP-19 — classify 50k backlog support tickets with the vendor LLM API.

- One-off job now, but the team wants to run it **weekly** as traffic grows.
- ~50k tickets/run; vendor API: ~1s/response, **rate limit 20 req/s**, occasional
  5xx and 429s, occasional hangs (vendor status page shows 3 incidents last month).
- Runs on a tiny cron container (must finish within the 6h maintenance window).
- Output feeds a training set — label quality matters, **missing labels are NOT
  acceptable as normal data** (the trainer treats empty string as a real class).

Author's note: "I ran it on 200 tickets and it worked. Lint passes. Can we run
the full 50k tonight?"
