## 🎯 Practice review assignment

**Case:** `__CASE__`

### How to complete this practice round

1. **Read the ticket:** `cases/__CASE__/ticket.md` — absorb the production
   context (QPS, data size, SLA) before reviewing.
2. **Review the code** in `cases/__CASE__/src/` as if it were a real PR.
   Leave **review comments** on the diff for each issue — use coaching format:
   > If we deploy this as-is, we risk X under Y. I suggest Z.
3. **Raise issues as comments.** At minimum, one P1 must be identified in a
   review comment or in the PR body checklist below.
4. **(Optional but encouraged) commit your fix** to `cases/__CASE__/src/`
   on this branch — the grader evaluates both the review and the fix.
5. Push → the **practice-review-grade** status check evaluates and may block
   merge until your score meets the bar.

### Self-review checklist (filled by you, graded by the bot)

<!-- Check what you found; the bot compares against the answer key -->
- [ ] Model loading / startup lifecycle issues
- [ ] Data/OOM (pandas ops, memory) issues
- [ ] External call reliability (timeout/retry/backoff)
- [ ] Reproducibility (seeds, determinism)
- [ ] Silent failure / data-leakage
- [ ] Latency in serving hot path
- [ ] Project/dependency hygiene
