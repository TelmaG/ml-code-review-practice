# Practice protocol

How to use this repo for deliberate practice, 30–45 minutes per session.

## Session structure (one case per session)

### 1. Set the stage (2 min)
Read the case's `ticket.md`. Note the production context: expected QPS, data size,
SLA, team seniority. Your review should be **calibrated to that context** — a
latency concern matters differently at 2 QPS than at 2,000 QPS.

### 2. First pass — hunt for smells (10–15 min)
Scan `src/` without running anything. Speak out loud (this is the training!):

- Where can this **fail silently**? (swallowed exceptions, wrong-but-valid outputs,
  non-determinism, leakage)
- Where does this **waste time or memory** under load? (per-request I/O, per-row ops,
  loading whole datasets, sequential network calls)

Mark line numbers as you go. Do not look at `expected_issues.md`.

### 3. Write your review (5–10 min)
Write review comments to `notes/case-XX.md` using the coaching format:

```
[severity] file:line — <what is wrong>
Risk: If we deploy this as-is, <what happens under load / in prod>.
Suggestion: <concrete fix>, e.g. <pattern/library>.
```

Prioritize: max 3 P1s, then P2s. A real reviewer doesn't dump 20 nits.

### 4. Score yourself (2 min)

```bash
make score CASE=case-01-model-loading NOTES=notes/case-01.md
```

The scorer fuzzy-matches your notes against the answer key. Treat results as:

- **Caught + correct severity** → solid.
- **Caught, wrong severity** → you saw it but misjudged impact. Re-read the ticket.
- **Missed** → add the anti-pattern to your personal checklist (`docs/review_rubric.md`).

### 5. Run the linters (2 min)

```bash
make lint CASE=case-01-model-loading
```

Compare what the tool found vs what you found vs the answer key. Three buckets:

| Tool found, you found | You found, tool missed | Tool found, you missed |
|---|---|---|
| Automatable — let CI catch it | Your human value-add | Study this gap |

### 6. Read the answer key (5 min)
`expected_issues.md`, then `reference_fix/sample_review.md` for phrasing,
then skim `reference_fix/src/` to see the fix shape.

### 7. Log it
Append one line to `notes/progress.md`: case, P1 recall, P2 recall, one lesson.

## Spaced repetition

Re-run each case blind after 3 days, 1 week, 3 weeks. You "own" a case when you
catch 100% of P1s and ≥80% of P2s twice in a row. Then generate new cases with the
LLM workflow in `skills/generate-case/SKILL.md`.

## Mock-interview mode

With a partner or an LLM playing the PR author: they defend the code ("it works on
my machine", "we'll fix it later"). You practice pushing back with risk statements
instead of taste statements. See `docs/feedback_templates.md` → "Handling pushback".
