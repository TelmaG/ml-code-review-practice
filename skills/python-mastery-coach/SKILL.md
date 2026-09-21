---
name: python-mastery-coach
description: Analyze practice-tracking issues and grading feedback to find recurring gaps, then produce a personalized Python/ML-engineering study guide with worked examples and self-check exercises. Use when the user says "what should I study", "give me a study guide", "I'm not solid on X", or after several failed practice PRs at the same difficulty level.
---

# python-mastery-coach

Turn repeated practice-PR gaps into a targeted study plan. This skill never
re-solves an open case and never quotes `expected_issues.md` — it works one
level up, from the *pattern* of misses, not the specific bug.

## When to use this

- The user asks what to study, or says they're "not solid" on something.
- The user has 2+ `practice-tracking` issues (open or closed) mentioning the
  same concept.
- After closing a practice-tracking issue, to reinforce the concept just learned.

## Step 1 — Aggregate the real gaps

Run:

```bash
python tools/gap_analysis.py
```

This reads every issue labeled `practice-tracking` via `gh issue list`, extracts
the "Gaps to recheck" hint lines the grading agent wrote, and buckets them into
concept ids (frequency-ranked, with issue numbers as evidence).

If `gh` isn't available or there are no issues yet, ask the user directly:
"Which 2-3 categories from the case breakdown table in README.md do you keep
missing?" and proceed with their answer instead of fabricating data.

## Step 2 — Look up each weak concept

For each concept id gap_analysis.py reports (or the user names), find the
matching `## <concept-id>` section in `skills/python-mastery-coach/concept-map.md`.
That section has: the mental model, why it bites in production, a worked
example, a self-check exercise, and reference docs.

Do not invent new concepts outside this map without also adding a section for
them — the map is the single source of truth so study guides stay consistent
across sessions.

## Step 3 — Write the personalized study guide

Create `notes/study-guide-<YYYY-MM-DD>.md` (gitignored, personal) with one
section per weak concept, ordered by frequency (weakest first). For each:

```
## <Concept name>

**Shows up in:** <case names / issue numbers from Step 1, no spoilers>
**Frequency:** <count>x across your practice attempts

### The mental model
<1-2 paragraphs from concept-map.md, adapted to plain language>

### Why it bites in production
<the concrete failure mode, tied to the rubric category>

### Worked example (do this correctly)
<the canonical correct code from concept-map.md>

### Self-check (don't look up the answer — reason it out)
<the exercise snippet + question from concept-map.md>

### Go deeper
<the reference docs from concept-map.md>
```

## Step 4 — Log it

Append one line to `notes/progress.md`:
`<date> study-guide concepts=<n> weakest=<top concept id>`

## Rules

- **Never** quote or paraphrase `expected_issues.md` content for an open case.
- **Never** solve the self-check exercises for the user — if they ask, walk
  them toward the mental model instead of giving the fixed code.
- If a concept keeps recurring across 3+ sessions, say so directly: "This is
  your third time missing `<concept>` — worth pairing on this specifically
  rather than another solo case."
- Keep the guide scoped to what's actually weak. Do not pad with concepts the
  user already demonstrates mastery of (frequency 0, or only in FIXED items).
