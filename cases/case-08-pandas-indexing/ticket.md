# PR #610: Online A/B scoring — pandas feature joiner

**Author:** experimentation-eng · **Reviewers:** you · **Target:** `main`

## Context

Ticket: EXP-55 — join live request rows against user features at scoring time.

- Online: ~800 QPS bursts; each request has a user_id; features table has 10M
  users (loaded once at startup — already good).
- Offline: nightly job joins 50M-row logs against the same table to build
  training sets.
- Author's note: "Passes unit test with the 200-user fixture. Quick review?"
