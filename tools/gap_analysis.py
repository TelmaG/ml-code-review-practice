#!/usr/bin/env python3
"""Aggregate practice-tracking issues into weak-concept frequency counts.

Reads GitHub issues labeled `practice-tracking` (opened by pr_evaluation.yml
whenever a practice PR fails its grade), extracts the "Gaps to recheck" hint
lines the grading agent wrote, and buckets each hint into a Python/ML-engineering
concept id. Concept ids must have a matching "## <concept-id>" section in
skills/python-mastery-coach/concept-map.md — that's where the actual study
content lives; this script only tells you which sections to read first.

Usage:
    python tools/gap_analysis.py                  # human-readable report
    python tools/gap_analysis.py --json            # machine-readable
    python tools/gap_analysis.py --top 5           # only the N weakest concepts
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict

# (pattern matched against a hint line, case-insensitive) -> concept id.
# Keep concept ids in sync with skills/python-mastery-coach/concept-map.md.
PATTERNS = [
    (r"\bglobal\b|\bclosure\b|cache.*not|not.*cach", "variable-scope-and-closures"),
    (r"except|silent|swallow|fallback|constant.*(0\.5|default)", "exception-handling-and-silent-failure"),
    (r"feature order|schema|column order|positional|contract|validat", "data-contracts-and-schema-validation"),
    (r"thread.?unsafe|race|concurren|\block\b|atomic|global state", "concurrency-and-shared-state"),
    (r"seed|reproducib|determinis|random_state", "reproducibility-and-randomness"),
    (r"leak(age)?|split|fit_transform|point-in-time|as-of", "data-leakage-and-train-serve-skew"),
    (r"timeout|retry|backoff|circuit breaker|idempot", "resilient-external-calls"),
    (r"iterrows|vectoriz|dataframe|groupby|merge", "pandas-vectorization"),
    (r"broadcast|dtype|float64|float32|numpy|allocation|memory", "numpy-memory-and-broadcasting"),
    (r"async|event loop|blocking|sync.*(handler|request)", "asyncio-and-blocking-io"),
    (r"pickle|deserializ|ssrf|untrusted|signature|secret|leaked.*key", "security-and-untrusted-input"),
    (r"statistic|confidence|sample size|p-value|significance|\bpsi\b|ks test", "statistics-for-ml-systems"),
    (r"watermark|event time|window|late event", "event-time-and-windowing"),
    (r"depend|\bpin\b|lockfile|requirements", "dependency-and-environment-management"),
    (r"\blog\b|\bprint\b|observab|telemetry|redact|\bpii\b", "structured-logging-and-observability"),
    (r"hardcod|config.*env|absolute path|model version|artifact.*version|versioned", "configuration-and-artifact-versioning"),
]


def load_issues() -> list:
    try:
        raw = subprocess.run(
            ["gh", "issue", "list", "--label", "practice-tracking", "--state", "all",
             "--json", "number,title,body,labels,createdAt,state", "--limit", "300"],
            capture_output=True, text=True, check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"could not read GitHub issues via gh CLI: {exc}", file=sys.stderr)
        print("is `gh` installed and authenticated for this repo?", file=sys.stderr)
        return []
    return json.loads(raw)


def level_of(issue: dict) -> str:
    for label in issue.get("labels", []):
        name = label.get("name") if isinstance(label, dict) else label
        if name in ("easy", "medium", "difficult"):
            return name
    return "unknown"


def hint_lines(body: str) -> list:
    section = re.search(r"### Gaps to recheck.*?\n\n(.*?)\n\n###", body or "", re.DOTALL)
    if not section:
        return []
    return [
        line.strip().lstrip("-").strip()
        for line in section.group(1).splitlines()
        if line.strip().startswith("-")
    ]


def classify(line: str) -> str:
    for pattern, concept in PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return concept
    return "uncategorized"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--top", type=int, default=None, help="only show the N weakest concepts")
    args = parser.parse_args()

    issues = load_issues()
    counts: Counter = Counter()
    evidence = defaultdict(list)

    for issue in issues:
        level = level_of(issue)
        for line in hint_lines(issue.get("body", "")):
            concept = classify(line)
            counts[concept] += 1
            evidence[concept].append({
                "issue": issue["number"], "title": issue["title"],
                "level": level, "hint": line, "state": issue.get("state"),
            })

    ranked = counts.most_common(args.top)

    if args.json:
        print(json.dumps(
            {"ranked_concepts": [{"concept": c, "count": n, "evidence": evidence[c]} for c, n in ranked]},
            indent=2,
        ))
        return 0

    if not ranked:
        print("No practice-tracking issues found (or `gh` unavailable). "
              "Nothing to aggregate yet — complete a few practice PRs first, "
              "or tell the coach directly which categories you keep missing.")
        return 0

    print("Weakest concepts (by frequency across practice-tracking issues):\n")
    for concept, count in ranked:
        case_refs = sorted({e["issue"] for e in evidence[concept]})
        print(f"  {count:>2}x  {concept}   (issues: {', '.join(f'#{n}' for n in case_refs)})")

    print("\nLook up each concept id as a `## <concept-id>` heading in "
          "skills/python-mastery-coach/concept-map.md for the study guide.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
