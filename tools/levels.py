#!/usr/bin/env python3
"""Levels helper: print the level of a case, or the full level map.

Usage:
    python tools/levels.py --level-of case-17-streaming-inference
    python tools/levels.py --map
"""
import argparse
import re
import sys
from pathlib import Path

LEVELS_FILE = Path(__file__).parent.parent / "cases" / "levels.yaml"


def parse_levels() -> dict:
    """Parse cases/levels.yaml without pyyaml dependency."""
    levels, current = {}, None
    for line in LEVELS_FILE.read_text().splitlines():
        head = re.match(r"^(easy|medium|difficult):\s*$", line)
        item = re.match(r"^\s+-\s+(case-\d+[\w-]*)\s*$", line)
        if head:
            current = head.group(1)
            levels[current] = []
        elif item and current:
            levels[current].append(item.group(1))
    return levels


def level_of(case: str) -> str:
    for level, cases in parse_levels().items():
        if case in cases:
            return level
    return "unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--level-of", metavar="CASE")
    parser.add_argument("--map", action="store_true")
    args = parser.parse_args()

    if args.level_of:
        print(level_of(args.level_of))
    elif args.map:
        for level, cases in parse_levels().items():
            for case in cases:
                print(f"{level}\t{case}")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
