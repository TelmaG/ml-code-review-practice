# Sample review — case 06 (project hygiene)

Welcome aboard! The modeling is a fine start — the feedback below is about
making this an org-grade repo before it becomes load-bearing. All of this is
about an hour of work.

> **[P1] data committed to git** (`data/sales_2023.csv`, `data/sales_2024_partial.csv`)
> **Risk:** ~440MB in git history permanently — every clone/CI run pays for it,
> and if any row contains PII it's in history forever even after deletion.
> **Suggestion:** `git rm --cached data/`, add `data/` to `.gitignore`, move the
> exports to object storage, and track them with DVC so data versions stay
> linked to code versions without living in git.

> **[P1] no dependency management**
> **Risk:** There is no `requirements.txt` at all — the only spec of this
> environment is your laptop. Next person to run this loses a day, and any
> rerun in six months silently runs on different library versions.
> **Suggestion:** pinned requirements (or a lockfile via uv/poetry/pdm);
> our project-hygiene rubric (section 5) is the checklist to satisfy.

> **[P2] `script.py` is a notebook dump used as the production entrypoint**
> **Risk:** Top-level execution, hardcoded user paths, magic numbers, and a
> score computed on training data printed as the result — if we deploy/run
> this as-is, "score: 0.9x" is a train metric masquerading as model quality.
> **Suggestion:** split into `src/` modules with a CLI entrypoint, config via
> env/args, and report metrics on a held-out split with fixed seeds.

> **[P2] no tests, no CI**
> **Risk:** First refactor breaks the pipeline invisibly; every PR review is
> manual archaeology.
> **Suggestion:** one smoke test on a small fixture (schema + train-on-sample +
> artifact written), plus a CI workflow running lint + test. The workflow in
> our training repo is a copy-paste template.

> **[P2] `model_old.pkl` + `analysis.ipynb` hygiene**
> **Risk:** A binary artifact at repo root with no provenance will be mistaken
> for the production model in six months; the notebook has committed outputs
> and execution counts, making diffs unreviewable.
> **Suggestion:** artifacts go to the model store with a metadata sidecar
> (version, metrics, feature list, seed); clear notebook outputs (nbstripout
> pre-commit).

Once the skeleton is in (deps pinned, data out of git, one test, CI), ping me
and we'll do a modeling-focused pass.
