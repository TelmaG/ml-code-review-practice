# Sample review — case 03

Blocking merge / the run tonight. The code "works" for 200 tickets and fails
exactly in the ways that only appear at 50k.

> **[P1] labeler.py — no timeout, no retry, no backoff on the vendor call**
> **Risk:** The vendor's status page shows hangs and 5xx/429s. Without a
> timeout, one hung socket stalls the whole run indefinitely inside a 6h window;
> without retries, guaranteed transient 429s at this call volume all become
> dropped tickets.
> **Suggestion:** `timeout=(5, 30)`, exponential backoff with jitter on
> 429/5xx (tenacity), and respect `Retry-After`. Fail 4xx (non-429) fast —
> retrying an auth error just burns quota.

> **[P1] labeler.py:34 — `except Exception: continue`**
> **Risk:** This is the silent-failure pattern at its worst: the job "succeeds",
> the CSV loads fine, and the trainer silently ingests a dataset with holes —
> the ticket explicitly says missing labels are treated as a real class.
> **Suggestion:** Never drop silently. Persist failed ids, log counts, and abort
> the run if failures exceed ~1%.

> **[P1] labeler.py:7 — API key committed to source**
> **Risk:** This key is now in git history. Treat as leaked: rotate before merge,
> scrub history, move to env/vault.
> **Suggestion:** `os.environ["VENDOR_API_KEY"]` + add a pre-commit secret scan.

> **[P2] The runtime math doesn't close**
> 50k × ~1s sequential ≈ **14h > 6h window**. The 200-ticket smoke test hides
> this. Refactor to bounded concurrency (asyncio semaphore at ~12–15 req/s,
> under the 20 req/s limit) — expect ~50–70 min wall clock.

> **[P2] No resume/checkpoint**
> A crash at hour 5 loses everything and double-pays the vendor. Append + flush
> per result, skip labeled ids on restart.

Summary: the shape is right (single-purpose script, clear IO). What changes
this from demo to production is failure semantics: timeouts, retries, loud
failures, resume, and concurrency. Also — please rotate that key now.
