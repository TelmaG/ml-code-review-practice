#!/usr/bin/env python3
"""LLM-backed PR review agent for practice PRs.

Reads the PR diff plus per-case context (ticket, rubric hints, detector output)
and produces a coaching-style review comment using Anthropic's native Messages API.

Required environment variable:
    ANTHROPIC_API_KEY — API key for Claude

Optional environment variables:
    ANTHROPIC_MODEL — default: claude-sonnet-4-5-20250929
    ANTHROPIC_BASE_URL — default: https://api.anthropic.com

Usage:
    ANTHROPIC_API_KEY=... python tools/agent_review.py \
        --base origin/main --head HEAD --context-dir eval_context --out review_comment.md
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

SYSTEM_PROMPT = """You are an experienced production ML code reviewer coaching a trainee.

You receive:
1. A PR diff (the trainee's attempt to fix a deliberately bad ML case).
2. The trainee's written review (PR body + review comments).
3. The case ticket (production context: QPS, data size, SLA).
4. Rubric hints — the severity classes an expert reviewer checks.
5. Output from an automated static-analysis tool, and a rule-based keyword score.

Your job — grade the SUBMISSION (fix + written review), not the original bad code:
- For each rubric hint, state: FIXED (code changed correctly) / IDENTIFIED
  (mentioned in review, no fix) / MISSED, with a line reference.
- Scoring: FIXED = 1.0, IDENTIFIED = 0.5, MISSED = 0.0 per rubric item.
- Judge failure semantics: does the fix eliminate the silent failure / latency
  bottleneck under the ticket's stated load? Do the arithmetic (QPS x size).
- Be strict on P1s: papering over a failure mode (try/except pass, silent
  constant fallback) counts as MISSED.
- Frame feedback coaching-style: "With this change, we still risk X under Y;
  I'd suggest Z." Never "this is bad".

You MUST end your reply with these XML tags, computing scores from your own
assessments (and improving on the keyword score where it's clearly wrong):

<grade>{"case": "<slug>", "p1_score": 0.0-1.0, "p2_score": 0.0-1.0,
"overall_score": 0.0-1.0, "headline": "<one line>",
"missed_hints": ["<short area to recheck, no solution, one per MISSED item>"]}</grade>"""


def gather_diff(base: str, head: str) -> str:
    result = subprocess.run(
        ["git", "diff", f"{base}...{head}", "--", "cases/"],
        capture_output=True, text=True, check=True,
    )
    diff = result.stdout
    return diff[:120_000]  # keep within context limits


def gather_context(context_dir: str) -> str:
    parts = []
    for fname in sorted(os.listdir(context_dir)):
        with open(os.path.join(context_dir, fname)) as f:
            parts.append(f.read())
    return "\n\n---\n\n".join(parts)[:60_000]


def call_model(system: str, user: str) -> str:
    """Call Claude through Anthropic's native Messages API."""
    # os.environ.get(key, default) only falls back when the key is absent, not
    # when a CI variable is set-but-empty — guard both cases explicitly.
    base_url = os.environ.get("ANTHROPIC_BASE_URL") or "https://api.anthropic.com"
    model = os.environ.get("ANTHROPIC_MODEL") or "claude-sonnet-4-5-20250929"
    payload = json.dumps({
        "model": model,
        "max_tokens": 4000,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "temperature": 0.2,
    }).encode()
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise RuntimeError(f"Anthropic API HTTP {exc.code}: {detail}") from None
    return "".join(
        block["text"] for block in body["content"] if block.get("type") == "text"
    )


def split_grade(raw: str) -> tuple:
    """Split the raw model output into review text and grade data."""
    import re
    m = re.search(r"<grade>(.*?)</grade>", raw, re.DOTALL)
    grade_data = {"case": "unknown", "p1_score": 0.0, "p2_score": 0.0,
                  "overall_score": 0.0, "headline": "no grade parsed", "missed_hints": []}
    if m:
        try:
            grade_data.update(json.loads(m.group(1)))
        except json.JSONDecodeError:
            pass
        review = raw[: m.start()].rstrip()
    else:
        review = raw
    return review, grade_data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--context-dir", required=True)
    parser.add_argument("--review-notes", default=None,
                        help="markdown file with the trainee's written review (PR body + comments)")
    parser.add_argument("--out", required=True)
    parser.add_argument("--json-out", default=None,
                        help="write machine-readable grade JSON for the status check")
    args = parser.parse_args()

    diff = gather_diff(args.base, args.head)
    context = gather_context(args.context_dir)
    case_names = sorted(f[:-3] for f in os.listdir(args.context_dir) if f.endswith(".md"))
    case_slug = case_names[0] if len(case_names) == 1 else ",".join(case_names) or "unknown"

    review_notes = ""
    if args.review_notes and os.path.exists(args.review_notes):
        with open(args.review_notes) as f:
            review_notes = f.read()

    if not diff.strip() and not review_notes.strip():
        review = "No changes under `cases/` and no review text found — nothing to evaluate."
        grade_data = {"case": case_slug, "p1_score": 0.0, "p2_score": 0.0, "overall_score": 0.0,
                      "headline": "empty submission", "missed_hints": []}
    else:
        user_msg = (
            "## Case context\n\n" + context +
            "\n\n## Trainee's written review\n\n" + (review_notes or "(none)") +
            "\n\n## PR diff to evaluate\n\n```diff\n" + diff + "\n```"
        )
        header = (
            "## \U0001F916 Practice review — graded\n\n"
            "_Coaching format: risk first, suggestion second. "
            "Merge stays blocked until the grade meets the bar._\n\n"
        )
        try:
            raw = call_model(SYSTEM_PROMPT, user_msg)
            review, grade_data = split_grade(raw)
        except Exception as exc:
            # A judge/API failure must not crash the pipeline uninterpretably —
            # fail the grade cleanly (0 score) so merge stays blocked with a
            # clear, actionable reason instead of an unhandled workflow error.
            review = f"Grading agent error: {exc}"
            grade_data = {"case": case_slug, "p1_score": 0.0, "p2_score": 0.0,
                          "overall_score": 0.0, "headline": f"agent error: {exc}", "missed_hints": []}
        review = header + review

    with open(args.out, "w") as f:
        f.write(review)
    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(grade_data, f, indent=2)
    print(review[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
