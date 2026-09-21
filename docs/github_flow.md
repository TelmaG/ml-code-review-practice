# GitHub Flow setup — the merge gate

This repo treats practice like real work: a case is "assigned" as a PR, you
review/fix inside the PR, a grading action scores you, and **merge is blocked
until your score meets the bar**.

## One-time repo setup (5 min)

0. **Difficulty registry**: every case is classified in `cases/levels.yaml`
   (`python tools/levels.py --level-of case-17-…` prints its level). The grading
   workflow uses this to tag the issue it opens on failure with
   `practice-tracking` + the level.

1. **Push this repo to GitHub** (private is fine).

2. **Add the Claude secret** for the grading agent:
   - Repo → Settings → Secrets and variables → Actions → New repository secret:
     `ANTHROPIC_API_KEY` — your Anthropic API key.
   - Optionally add repository variables `ANTHROPIC_MODEL` and
     `ANTHROPIC_BASE_URL`. The default model is `claude-3-5-haiku-latest` and
     the default endpoint is `https://api.anthropic.com`.
   - The workflow does not use OpenAI-compatible configuration.

3. **Protect `main`** — this is what makes merge actually blocked:
   - Repo → Settings → Branches → Add branch ruleset (or classic branch
     protection rule) for `main`:
     - ☑ Require a pull request before merging
     - ☑ Require status checks to pass → add **`practice-review-grade`**
       (it appears in the picker after it has run once — open your first
       practice PR, let the workflow run, then come back and add the check)
     - ☑ (optional, realistic) Require conversation resolution before merging
     - ☑ Do not allow bypassing the above settings
4. **Tune the bar** in `.github/workflows/pr_evaluation.yml` env block:
   `P1_REQUIRED: 0.85`, `OVERALL_REQUIRED: 0.70` are sane starting points.
   Raise them once you consistently pass.

## The practice loop (GitHub Flow)

```
Actions tab → "dispense practice case" → pick a case → Run workflow
      │
      ▼   opens PR  practice/case-07-sklearn-preprocessing-<stamp> → main
      │
You:  read ticket.md (linked in the PR body)
      leave REVIEW COMMENTS on the diff — coaching format:
        "if we deploy this as-is, we risk X under Y; I suggest Z"
      optionally commit your FIX to cases/<case>/src/ on this branch
      tick the checklist items in the PR body
      │
      ▼   every push re-triggers "practice PR grading"
Bot:  comments FIXED / IDENTIFIED / MISSED per issue + score line
      sets status check  practice-review-grade = success | failure
      │
      ▼   merge blocked while below the bar
You:  improve fix / sharpen review → push → re-grade → meets bar → merge
```

## How the grade is computed

| Signal | Source | Role |
|---|---|---|
| Keyword score on your written review | `tools/score_review.py --json` (PR body + review comments + inline comments) | advisory input to the judge |
| Detector findings on your *fixed* code | `ml_smell_detector` in the workflow | "still broken" signals given to the judge |
| Holistic judgement of fix + review | `tools/agent_review.py` (LLM) | emits `<grade>{p1_score, p2_score, overall_score}</grade>` |
| Gate | workflow compares scores to env thresholds → commit status `practice-review-grade` | blocks merge via branch protection |

## How a failed grade creates a tracking issue

When `practice-review-grade` fails:

1. The bot comments the full grade on the PR (FIXED / IDENTIFIED / MISSED).
2. It opens a **GitHub Issue** titled `practice gap: <case> (<level>)` containing:
   - the score line and the grades per issue,
   - a **hints-only** gap list — just the area to recheck, never the fix,
   - instructions for closing (pass the gate, note what you learned).
3. You push your improved fix/review → automatic re-grade → gate passes →
   close the issue with a one-line reflection.

Use the `practice-tracking` label filter on the Issues tab to see your gap
trend per level over time.

## Keeping `main` pristine

`cases_ci.yml` (push to main) still enforces that no case has been fixed on
`main` — every case's `src/` must keep producing detector findings. Practice
merges should go to `practice`-scoped history, or stay unmerged: completing a
practice PR means *meeting the grade bar*, not necessarily merging the fixed
case into `main`. If you prefer merged attempts to accumulate, change the
practice PR base to a `practice-log` branch (never protected).

## Anti-cheat

The PR diff is graded, and `cases/*/expected_issues.md` lives on `main` — treat
it as out of bounds during practice. `cases_ci.yml` will fail loudly if an
answer key or case source is modified on `main`.
