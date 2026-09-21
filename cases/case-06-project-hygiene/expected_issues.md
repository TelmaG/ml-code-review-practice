# Answer key — case 06 (project review)

## P1

1. **Data committed to git** — `data/sales_2023.csv` and
   `data/sales_2024_partial.csv` (placeholders here; treat as real).
   Repo bloats permanently, clones slow to a crawl, data and code versions
   entangled; if any row contains PII it's now in history forever.
   → `git rm --cached`, .gitignore `data/`, move to object storage / **DVC**
   (rubric section 5.2).
2. **No dependency pinning / no declared environment at all** — `script.py`
   imports pandas/sklearn/matplotlib but there is no `requirements.txt`,
   no lockfile. "Works on the author's laptop" is the only spec. Next hire's
   first day is a dependency-scavenger hunt; reruns aren't reproducible.
   → pinned requirements / lockfile (rubric section 5.1).

## P2

3. **Jupyter-native code as the production entrypoint** — `script.py` is a
   notebook dump: top-level execution, hardcoded absolute Windows path
   (`C:\Users\…\Desktop`), magic numbers, global state. Fails anywhere but the
   author's machine — silently or loudly.
4. **No tests at all** (rubric section 5.3) — and the ML-specific ones the
   rubric calls for: a schema/leakage/determinism test on a small fixture.
5. **Notebook hygiene** — `analysis.ipynb` has outputs with base64 images and
   execution counts committed; diff-unreviewable. → clear outputs (nbstripout)
   or export reports elsewhere.
6. **No CI** — nothing runs lint/tests on PR. → minimal CI (this very repo's
   workflow is a template).
7. **Packed artifacts/assets with no documentation** — `model_old.pkl` binary
   committed with no provenance; `README.md` is one line. UNDEAD MODEL risk:
   someone will find `model_old.pkl` in six months and wonder if it's the
   prod one.

## P3

8. One-letter/misleading names (`df2`, `script.py`), dead commented code,
   `models/` `.gitignore`d while `model_old.pkl` committed at root
   (inconsistent artifact policy), no LICENSE mention, no make/task runner for
   the standard commands.

## What automated tooling catches here

Very little — project hygiene is a human-review domain. `ml_smell_detector`
will flag the hardcoded path / missing seed inside `script.py`, but the repo-
level issues (data in git, no deps, no tests, no CI) are exactly what no
file-level linter sees.

## The headline for the author

Friendly + educational: this repo needs its **hygiene skeleton** (deps pinned,
data out of git, smoke test, CI) before any modeling discussion — those four
things are ~1 hour of work and they're the difference between "your project"
and "an org project".
