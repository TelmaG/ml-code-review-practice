#!/usr/bin/env python3
"""Score your review notes against a case's answer key.

Usage:
    python tools/score_review.py --case cases/case-01-model-loading --notes notes/case-01.md

Matching is deliberately fuzzy: each expected issue has keyword groups; an issue
counts as "caught" if your notes mention enough of its keywords. Severity is
compared by finding P1/P2/P3 mentions near the keywords (best effort).
"""
import argparse
import re
import sys

# Per-case issue keywords: (issue_id, severity, [keyword groups — ANY group match = caught])
CASES = {
    "case-01-model-loading": [
        ("model-in-predict", "P1", [["predict"], ["load", "joblib", "startup", "lifespan"]]),
        ("no-validation", "P1", [["valid", "schema", "pydantic"], ["payload", "request", "input"]]),
        ("feature-order", "P1", [["feature order", "column order", "order drift", "positional"]]),
        ("unpinned-deps", "P1", [["pin", "lockfile", "unpinned", "requirements"]]),
        ("batch-loop", "P2", [["batch"], ["loop", "vectoriz", "per row"]]),
        ("hardcoded-path", "P2", [["hardcod", "/models", "path", "env"]]),
        ("print-logging", "P2", [["print", "logging"], ["pii", "payload", "log"]]),
    ],
    "case-02-data-pipeline": [
        ("oom-risk", "P1", [["oom", "memory", "dtype", "read_csv", "chunk"]]),
        ("silent-stale-output", "P1", [["stale", "success", "marker", "versioned", "atomic"]]),
        ("iterrows", "P2", [["iterrows"], ["vectoriz", "np.where"]]),
        ("merge-explosion", "P2", [["merge"], ["duplicat", "cartesian", "row", "validate"]]),
        ("chain-inplace", "P2", [["chain", "inplace", "settingwithcopy"]]),
        ("nan-self-check", "P2", [["nan"], ["values", "to_numpy", "isfinite", "self"]]),
        ("normalizer-leakage", "P2", [["max", "normaliz", "scal"], ["serve", "inference", "leak", "persist"]]),
    ],
    "case-03-llm-batch-job": [
        ("no-timeout", "P1", [["timeout"]]),
        ("swallowed-exceptions", "P1", [["except", "swallow", "silent", "drop"], ["continue", "failur"]]),
        ("no-retry", "P1", [["retry", "backoff", "429", "tenacity"]]),
        ("hardcoded-key", "P1", [["api key", "secret", "sk-vendor", "leak", "rotate"]]),
        ("sequential-runtime", "P2", [["sequential", "concurren", "async", "1s", "14h", "window"]]),
        ("no-resume", "P2", [["resume", "checkpoint", "idempoten", "incremental"]]),
        ("rate-limit", "P2", [["rate limit", "req/s", "semaphore", "pacing"]]),
        ("no-response-validation", "P2", [["raise_for_status", "validate", "schema", "label"]]),
    ],
    "case-04-training-script": [
        ("scaler-leakage", "P1", [["leak", "scaler", "fit_transform"], ["split", "valid"]]),
        ("accuracy-imbalanced", "P1", [["accuracy"], ["imbalanc", "1%", "majority", "positive rate"]]),
        ("no-seeds", "P1", [["seed", "random_state", "reproducib", "deterministic"]]),
        ("prod-overwrite", "P1", [["overwrit", "model.pt", "version", "registry", "promot"]]),
        ("no-zero-grad", "P1", [["zero_grad", "gradient"], ["accumulat"]]),
        ("full-batch-cpu", "P2", [["batch", "dataloader", "gpu", "device", "forward"]]),
        ("no-scaler-persistence", "P2", [["scaler"], ["persist", "save", "serve", "skew"]]),
        ("no-eval-checkpoint", "P2", [["eval", "early stopping", "checkpoint", "best"]]),
    ],
    "case-05-feature-serving": [
        ("blocking-in-async", "P1", [["blocking", "sync", "async", "event loop", "requests"]]),
        ("no-timeout", "P1", [["timeout"]]),
        ("silent-defaults", "P1", [["default", "0.5", "fabricat", "silent", "fallback"]]),
        ("no-caching", "P2", [["cache", "caching", "ttl", "lru"]]),
        ("no-pooling", "P2", [["pool", "session", "keep-alive", "connection"]]),
        ("no-retry-breaker", "P2", [["retry", "circuit breaker", "breaker"]]),
        ("degraded-mode-missing", "P2", [["degraded", "stale", "incident", "5 min", "policy"]]),
    ],
    "case-06-project-hygiene": [
        ("data-in-git", "P1", [["data"], ["git", "dvc", "commit", "history"]]),
        ("no-deps", "P1", [["requirements", "pin", "dependenc", "lockfile"]]),
        ("notebook-dump", "P2", [["notebook", "magic number", "top-level", "hardcod"]]),
        ("no-tests", "P2", [["test"]]),
        ("no-ci", "P2", [["ci", "github action", "workflow"]]),
        ("artifact-provenance", "P2", [["pkl", "pickle", "artifact"], ["provenance", "metadata", "version"]]),
    ],
    "case-07-sklearn-preprocessing": [
        ("refit-train-serve-skew", "P1", [["fit", "refit", "refits"], ["train", "training"], ["serve", "serving", "pipeline", "transform"]]),
        ("unseen-categories", "P1", [["onehot", "one-hot", "labelencoder"], ["unknown", "unseen", "handle_unknown"]]),
        ("division-by-zero", "P1", [["division", "divide", "inf"], ["tenure", "zero", "0"]]),
        ("dropna-silent", "P2", [["dropna", "imput"], ["silent", "shrink", "empty"]]),
        ("ordinal-encoding", "P2", [["labelencoder", "ordinal"], ["categor", "nominal", "order"]]),
        ("schema-contract", "P2", [["schema", "column"], ["contract", "missing", "validate"]]),
    ],
    "case-08-pandas-indexing": [
        ("o-n-lookup", "P1", [["scan", "o(n)", "linear", "full scan", "index"], ["lookup", "online", "request"]]),
        ("missing-user-semantics", "P1", [["missing", "unknown"], ["user"], ["silent", "inconsistent", "policy"]]),
        ("label-leak-shift", "P1", [["shift"], ["leak", "boundary", "next", "label"]]),
        ("merge-no-validate", "P2", [["merge"], ["validate", "duplicat", "multipl"]]),
        ("drop-duplicates-mask", "P2", [["drop_duplicates"], ["mask", "root cause", "expensive"]]),
        ("groupby-apply", "P2", [["groupby", "apply"], ["vectoriz", "head"]]),
    ],
    "case-09-numpy-broadcasting": [
        ("swapped-normalization", "P1", [["mean", "std"], ["swap", "invert", "multiply", "divide", "formula", "normaliz"]]),
        ("eye-matrix-oom", "P1", [["eye", "diagonal", "matrix"], ["19gb", "memory", "oom", "materializ", "01"]]),
        ("dtype-ladder", "P2", [["float64", "float32", "fp16", "dtype"], ["memory", "copy", "cast"]]),
        ("unbounded-batch", "P2", [["batch", "chunk"], ["all", "2m", "unbound", "limit"]]),
        ("intermediate-copies", "P2", [["copy", "contiguous", "swapaxes", "transpose"], ["memory", "materializ"]]),
    ],
    "case-10-seaborn-monitoring": [
        ("wrong-baseline", "P1", [["last_week", "baseline", "window"], ["wrong", "same", "7", "week"]]),
        ("print-alert", "P1", [["print"], ["alert", "page", "oncall", "metric"]]),
        ("scatter-15m", "P1", [["scatter"], ["15m", "million", "aggregate", "bin", "oom", "slow"]]),
        ("corr-annot", "P1", [["corr", "correlation", "heatmap"], ["annot", "numeric", "illegible", "slow"]]),
        ("kde-scale", "P2", [["kde", "kdeplot"], ["n2", "sample", "histogram"]]),
        ("mean-only-drift", "P2", [["mean"], ["drift"], ["psi", "ks", "variance", "shape"]]),
        ("overwrite-artifacts", "P2", [["overwrite", "fixed name", "date"], ["artifact", "png", "history"]]),
    ],
    "case-11-batch-inference-queue": [
        ("model-per-message", "P1", [["model", "load"], ["message", "startup", "deserialize"]]),
        ("ack-loss", "P1", [["ack"], ["exception", "fail", "lost", "dead-letter"]]),
        ("publish-ack-idempotency", "P1", [["publish", "ack"], ["duplicate", "idempot", "transaction"]]),
        ("unbounded-payload", "P2", [["payload", "dataframe"], ["unbound", "limit", "chunk", "memory"]]),
        ("backpressure", "P2", [["sleep", "backpressure", "concurren", "visibility"]]),
        ("schema-validation", "P2", [["schema", "validate"], ["count", "misalign", "input"]]),
    ],
    "case-12-feature-freshness": [
        ("refresh-timeout-stampede", "P1", [["timeout", "hang"], ["thread", "stampede", "single-flight"]]),
        ("stale-contract", "P1", [["stale", "expired", "freshness"], ["ten minute", "timestamp", "fail"]]),
        ("atomic-cache-swap", "P1", [["lock", "atomic", "snapshot"], ["partial", "race"]]),
        ("refresh-per-caller", "P2", [["thread"], ["every", "caller", "single-flight", "backoff"]]),
        ("silent-missing", "P2", [["missing", "default", "unknown"], ["metric", "fallback"]]),
        ("warmup-memory", "P2", [["parquet", "records", "dictionary"], ["memory", "replica"]]),
    ],
    "case-13-data-contract-drift": [
        ("global-fillna", "P1", [["fillna"], ["contract", "categorical", "semantic", "silent"]]),
        ("coerce-zero", "P1", [["coerce", "zero", "amount"], ["malformed", "corrupt", "reject"]]),
        ("schema-quality-gates", "P1", [["schema", "row count", "distribution", "validate"], ["drift", "fail"]]),
        ("ingest-memory", "P2", [["in-memory", "read_json", "chunk", "column"]]),
        ("small-data-fail", "P2", [["small", "print"], ["fail", "page", "save"]]),
        ("artifact-lineage", "P2", [["overwrite", "current"], ["version", "lineage", "rollback"]]),
    ],
    "case-14-distributed-training": [
        ("distributed-sampler", "P1", [["sampler", "set_epoch"], ["rank", "duplicate", "overlap"]]),
        ("checkpoint-race", "P1", [["checkpoint", "write"], ["rank", "corrupt", "concurrent"]]),
        ("distributed-seeds", "P1", [["seed", "reproduc", "rng"], ["worker", "cuda", "loader"]]),
        ("checkpoint-io", "P2", [["checkpoint", "save"], ["synchronous", "storage", "barrier"]]),
        ("checkpoint-state", "P2", [["optimizer", "rng", "sampler", "scaler"], ["restart", "resume"]]),
        ("rank-zero-metrics", "P2", [["rank zero", "logging", "barrier"], ["metric", "inconsistent"]]),
    ],
    "case-15-workflow-idempotency": [
        ("external-timeout", "P1", [["timeout"], ["warehouse", "registry", "deploy"]]),
        ("nonidempotent-retry", "P1", [["retry"], ["idempot", "deploy", "duplicate", "promotion"]]),
        ("durable-resume", "P1", [["resume", "done", "state"], ["durable", "partial", "manifest"]]),
        ("run-scoped-artifact", "P2", [["tmp", "model.pkl", "path"], ["concurrent", "overwrite", "run"]]),
        ("swallowed-workflow", "P2", [["exception", "swallow", "attempt"], ["failure", "reason"]]),
        ("promotion-gate", "P2", [["validation", "metric", "threshold", "approval"], ["deploy", "promot"]]),
    ],
    "case-16-canary-deployment": [
        ("durable-canary", "P1", [["sleep", "durable", "state", "restart"], ["canary", "watchdog"]]),
        ("statistical-test", "P1", [["sample", "confidence", "statistic", "significance"], ["conversion", "noise"]]),
        ("operational-guardrails", "P1", [["latency", "error"], ["promot", "rollback"]]),
        ("canary-timeouts", "P2", [["timeout", "retry"], ["metrics", "router"]]),
        ("state-race", "P2", [["race", "compare-and-swap", "state machine", "concurr"]]),
        ("rollback-watchdog", "P2", [["watchdog", "heartbeat"], ["rollback", "controller"]]),
    ],
    "case-17-streaming-inference": [
        ("auto-commit-loss", "P1", [["auto commit", "offset"], ["durable", "lose", "crash"]]),
        ("producer-flush", "P1", [["producer", "send", "flush", "ack"], ["durable", "error"]]),
        ("stream-idempotency-order", "P1", [["replay", "duplicate", "idempot"], ["order", "partition", "event"]]),
        ("microbatch", "P2", [["one event", "microbatch", "batch"], ["50k", "lag", "backpressure"]]),
        ("dead-letter-schema", "P2", [["schema", "dead-letter", "poison", "validate"], ["retry"]]),
        ("partition-key", "P2", [["partition", "user"], ["ordering", "hot"]]),
    ],
    "case-18-pii-observability": [
        ("raw-pii-logs", "P1", [["payload", "raw"], ["pii", "financial", "redact", "privacy"]]),
        ("structured-model-telemetry", "P1", [["model version", "request id", "structured"], ["error", "metric", "observ"]]),
        ("prediction-errors", "P1", [["exception", "error"], ["telemetry", "structured", "stack"]]),
        ("monotonic-latency", "P2", [["time.time", "monotonic", "latency"], ["clock"]]),
        ("logger-controls", "P2", [["root logger", "logging"], ["sampling", "access", "field"]]),
        ("log-rate-limit", "P2", [["rate", "sampling"], ["qps", "latency", "cost"]]),
    ],
    "case-19-hyperparameter-search": [
        ("validation-overfit", "P1", [["500", "search", "configuration"], ["validation", "nested", "test", "overfit"]]),
        ("search-reproducibility", "P1", [["seed", "reproduc"], ["split", "audit"]]),
        ("search-overwrite", "P1", [["current.pkl", "overwrite", "production"], ["version", "promotion", "artifact"]]),
        ("model-memory", "P2", [["model", "memory", "resident", "release"], ["non-winner", "gpu"]]),
        ("search-parallelism", "P2", [["gpu", "parallel", "sequential", "scheduler"], ["trial"]]),
        ("trial-isolation", "P2", [["failed", "trial", "experiment", "budget"], ["isolation", "cost"]]),
    ],
    "case-20-gpu-serving": [
        ("gpu-queue", "P1", [["synchronous", "queue", "microbatch", "batch"], ["1500", "gpu", "worker"]]),
        ("cuda-sync", "P1", [["synchronize", "overlap", "p99", "latency"], ["gpu"]]),
        ("input-overload", "P1", [["size", "queue", "overload", "timeout", "32"]],),
        ("eval-mixed-precision", "P2", [["eval", "mixed precision", "fp16", "memory"]]),
        ("serving-lifecycle", "P2", [["startup", "readiness", "import", "load"], ["model"]]),
        ("stage-metrics", "P2", [["queue wait", "preprocess", "serialization", "metric"], ["latency"]]),
    ],
    "case-21-point-in-time-features": [
        ("future-profile-leak", "P1", [["profile", "as-of", "point-in-time", "future"], ["updated_at", "event_ts"]]),
        ("rolling-time-leak", "P1", [["rolling", "window"], ["current", "future", "closed-left", "timestamp"]]),
        ("temporal-split", "P1", [["temporal", "time split", "future month", "validation"], ["leak"]]),
        ("rolling-sort", "P2", [["rolling", "sort"], ["unsorted", "event time"]]),
        ("large-join", "P2", [["2b", "2 billion", "in-memory", "partition", "column"]]),
        ("timestamp-quality", "P2", [["duplicate", "timestamp", "quality", "key"]]),
    ],
    "case-22-llm-gateway": [
        ("gateway-reliability", "P1", [["timeout", "retry", "breaker"], ["vendor", "worker", "storm"]]),
        ("tenant-auth", "P1", [["tenant"], ["auth", "authorize", "imperson", "identity"]]),
        ("tenant-limits", "P1", [["rate", "budget", "concurr", "limit"], ["tenant", "noisy"]]),
        ("malformed-response", "P1", [["empty", "malformed", "schema"], ["failure", "status", "validate"]]),
        ("gateway-pooling", "P2", [["sync", "async", "pool", "connection", "stream"]]),
        ("prompt-retention", "P2", [["prompt", "response"], ["redact", "retention", "cross-tenant"]]),
        ("gateway-idempotency", "P2", [["request id", "idempot", "usage"], ["reconcile"]]),
    ],
    "case-23-retraining-orchestrator": [
        ("shared-artifact", "P1", [["shared", "model.pkl", "artifact"], ["overwrite", "concurrent", "immutable"]]),
        ("promotion-race", "P1", [["promotion", "promote"], ["lock", "race", "compare-and-swap", "last writer"]]),
        ("run-lineage", "P1", [["uuid", "run id"], ["path", "manifest", "reproduc"]]),
        ("subprocess-check", "P2", [["subprocess", "return code", "check", "timeout"], ["failed"]]),
        ("durable-state", "P2", [["state", "atomic", "structured", "json"], ["durable"]]),
        ("symlink-rollback", "P2", [["symlink", "rollback", "health"], ["current"]]),
    ],
    "case-24-statistical-rollback": [
        ("statistical-validity", "P1", [["confidence", "sample", "statistic", "cluster", "season"], ["mean", "conversion", "noise"]]),
        ("tail-latency", "P1", [["latency"], ["p99", "p95", "tail", "mean"]]),
        ("evaluator-reliability", "P1", [["timeout", "metrics"], ["fail closed", "idempot", "durable"]]),
        ("population-balance", "P2", [["population", "window", "missing", "imbalance"], ["candidate", "baseline"]]),
        ("hysteresis", "P2", [["cooldown", "hysteresis", "flap", "observation"]]),
        ("decision-audit", "P2", [["audit", "version", "threshold"], ["decision", "input"]]),
    ],
    "case-25-distributed-join": [
        ("driver-collect", "P1", [["collect"], ["driver", "oom", "terabyte", "distributed"]]),
        ("join-skew", "P1", [["skew", "partition", "broadcast", "hot key"], ["straggler", "2 hour"]]),
        ("rdd-regression", "P1", [["rdd", "map"], ["optimizer", "vector", "pass"]]),
        ("atomic-output", "P2", [["overwrite", "atomic", "version", "success marker"], ["partial"]]),
        ("join-quality", "P2", [["row count", "duplicate", "null", "schema"], ["quality"]]),
        ("adaptive-query", "P2", [["aqe", "adaptive", "resource", "partition"]]),
    ],
    "case-26-model-supply-chain": [
        ("untrusted-url", "P1", [["url", "allowlist", "ssrf", "auth"], ["attacker", "object store"]]),
        ("pickle-rce", "P1", [["pickle", "deserialize"], ["code execution", "untrusted", "signature"]]),
        ("artifact-integrity", "P1", [["checksum", "signature", "digest", "version"], ["tamper", "atomic", "current"]]),
        ("download-timeout", "P2", [["timeout", "size", "stream", "content-length"], ["large", "hang"]]),
        ("atomic-artifact", "P2", [["atomic", "temporary", "permissions", "rollback"], ["write"]]),
        ("artifact-provenance", "P2", [["provenance", "framework", "schema", "metadata"], ["compatibility"]]),
    ],
    "case-27-event-time-streaming": [
        ("processing-vs-event-time", "P1", [["processing time", "time.time"], ["event time", "late", "out-of-order"]]),
        ("unbounded-state", "P1", [["state", "unbound", "watermark", "high-cardinality"], ["memory"]]),
        ("state-recovery", "P1", [["restart", "checkpoint", "process-local", "dedup"], ["replay", "double"]]),
        ("future-event", "P2", [["future", "timestamp"], ["event"]]),
        ("state-hotspot", "P2", [["partition", "hot user", "hotspot", "concurr"]]),
        ("watermark-metrics", "P2", [["watermark", "lag", "dropped", "state bytes"], ["metric"]]),
    ],
    "case-28-fairness-calibration": [
        ("arbitrary-threshold", "P1", [["threshold", ".5", "cost", "calibrat"], ["fairness", "criterion"]]),
        ("missing-group", "P1", [["missing", "group"], ["drop", "coverage", "unknown", "fairness"]]),
        ("fairness-metrics", "P1", [["selection", "tpr", "fpr", "equalized", "confidence"], ["metric", "group"]]),
        ("monitoring", "P2", [["print", "monitor", "alert", "versioned"], ["metric"]]),
        ("holdout-stability", "P2", [["holdout", "threshold", "overfit", "stability"]]),
        ("intersectional-policy", "P2", [["intersection", "proxy", "privacy", "sensitive"], ["group"]]),
    ],
    "case-29-ensemble-hedging": [
        ("hedge-timeout", "P1", [["timeout", "deadline", "future"], ["slow", "120ms", "cancel"]]),
        ("executor-per-request", "P1", [["executor", "thread", "connection"], ["per request", "pool", "qps"]]),
        ("partial-ensemble", "P1", [["failure", "partial", "fallback", "schema"], ["model"]]),
        ("ensemble-pooling", "P2", [["connection", "pool", "session", "breaker"], ["reuse"]]),
        ("cancel-futures", "P2", [["cancel", "future", "timeout"], ["work"]]),
        ("ensemble-calibration", "P2", [["mean", "weight", "calibrat", "correlat"], ["ensemble"]]),
    ],
    "case-30-artifact-hot-reload": [
        ("reload-timeout", "P1", [["registry", "request", "timeout", "retry"], ["hang", "watcher"]]),
        ("partial-snapshot", "P1", [["partial", "atomic", "snapshot", "swap"], ["mixed", "generation"]]),
        ("old-model-memory", "P1", [["old", "models", "reference", "release", "memory"], ["del", "generation"]]),
        ("artifact-validation", "P1", [["integrity", "version", "schema", "validate"], ["rollback", "bad"]]),
        ("watcher-exception", "P2", [["exception", "watcher", "health", "metric"], ["silent"]]),
        ("reload-lock", "P2", [["lock", "consistent", "generation"], ["request"]]),
        ("readiness-budget", "P2", [["readiness", "memory", "budget", "startup"], ["reload"]]),
    ],
}


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9%/. ]+", " ", text.lower())


def issue_caught(issue_keywords, notes: str) -> bool:
    return all(
        any(kw in notes for kw in group) for group in issue_keywords
    )


def severity_mentioned(sev: str, notes: str) -> bool:
    return sev.lower() in notes or sev in notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, help="case directory path")
    parser.add_argument("--notes", required=True, help="your review notes markdown")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON (used by the grading workflow)")
    args = parser.parse_args()

    case_name = args.case.rstrip("/").split("/")[-1]
    if case_name not in CASES:
        print(f"unknown case: {case_name}. known: {', '.join(CASES)}")
        return 2

    try:
        with open(args.notes) as f:
            notes = normalize(f.read())
    except FileNotFoundError:
        print(f"notes file not found: {args.notes}")
        print("write your review first — see docs/practice_protocol.md step 3")
        return 2

    issues = CASES[case_name]
    caught, missed, sev_mismatch = [], [], []

    for issue_id, sev, kw_groups in issues:
        if issue_caught(kw_groups, notes):
            caught.append((issue_id, sev))
            if not severity_mentioned(sev, notes):
                sev_mismatch.append(issue_id)
        else:
            missed.append((issue_id, sev))

    p1_total = [i for i in issues if i[1] == "P1"]
    p1_caught = [i for i in p1_total if any(c[0] == i[0] for c in caught)]
    p2_total = [i for i in issues if i[1] == "P2"]
    p2_caught = [i for i in p2_total if any(c[0] == i[0] for c in caught)]

    if args.json:
        import json
        print(json.dumps({
            "case": case_name,
            "total": len(issues),
            "caught": len(caught),
            "p1_score": len(p1_caught) / max(len(p1_total), 1),
            "p2_score": len(p2_caught) / max(len(p2_total), 1),
            "overall_score": len(caught) / max(len(issues), 1),
            "missed": [i[0] for i in missed],
        }, indent=2))
        return 0

    print(f"\n=== {case_name} ===")
    print(f"caught {len(caught)}/{len(issues)} issues")
    print(f"P1 recall: {len(p1_caught)}/{len(p1_total)}")
    if caught:
        print("\n✔ caught:")
        for issue_id, sev in caught:
            flag = " (severity not mentioned)" if issue_id in sev_mismatch else ""
            print(f"  [{sev}] {issue_id}{flag}")
    if missed:
        print("\n✘ missed:")
        for issue_id, sev in missed:
            print(f"  [{sev}] {issue_id}")
    print("\nNow compare against the answer key: " + args.case + "/expected_issues.md")
    return 0


# Hint templates per case+issue: what area to check, no solution given.
HINTS = {
    "model-in-predict": "look at the serving lifecycle: where does heavy initialization happen relative to request handling?",
    "no-validation": "trace the request body from the API surface to the feature vector — what assumptions are made?",
    "feature-order": "compare how features are assembled at serve time vs. how they were ordered at training time",
    "unpinned-deps": "check dependency management files for version guarantees",
    "batch-loop": "look at how the batch endpoint processes multiple rows",
    "hardcoded-path": "scan for absolute paths and environment assumptions",
    "print-logging": "check what gets logged, at what level, and what's in it",
    "oom-risk": "estimate peak memory: input size × inflation from dtypes × copies from merges",
    "silent-stale-output": "what does the *consumer* see when this job fails halfway?",
    "iterrows": "check for per-row Python iteration over large frames",
    "merge-explosion": "check merge keys for uniqueness guarantees and validate= flags",
    "chain-inplace": "look for inplace mutations and chained indexing",
    "nan-self-check": "test conditions that compare a Series to itself",
    "normalizer-leakage": "is the normalizing statistic persisted for serve time, or recomputed per batch?",
    "no-timeout": "find every external call and check for a deadline",
    "swallowed-exceptions": "find except blocks and ask what data lands downstream when they fire",
    "no-retry": "look for transient-failure handling: backoff, jitter, retry budgets",
    "hardcoded-key": "scan for secrets in source",
    "sequential-runtime": "compute calls/sec × total calls against the time budget",
    "no-resume": "what happens if the job is killed at 90%? where's the checkpoint?",
    "rate-limit": "check client pacing against the documented rate limit",
    "no-response-validation": "what happens when the dependency returns an unexpected body or status?",
    "scaler-leakage": "check what state is fitted before vs. after the train/valid split",
    "accuracy-imbalanced": "check the metric against the positive-rate in the ticket",
    "no-seeds": "list every RNG source in the pipeline and check each is seeded",
    "prod-overwrite": "check the artifact output path — versioned and gated, or shared?",
    "no-zero-grad": "verify gradient accumulation boundaries in the training loop",
    "full-batch-cpu": "check device placement and batch construction",
    "no-scaler-persistence": "is preprocessing state saved with the artifact?",
    "no-eval-checkpoint": "is the *best* epoch saved, or the last?",
}


def build_gap_hints(case_name: str, missed_ids: list) -> str:
    """Produce a hints-only gap report for a failed practice round."""
    lines = []
    case_title = case_name.replace("case-", "").replace("-", " ").strip()
    for issue_id in missed_ids:
        sev = next((s for i, s, _ in CASES[case_name] if i == issue_id), "?")
        hint = HINTS.get(issue_id, "re-scan the code with this category in mind")
        readable = issue_id.replace("-", " ")
        lines.append(f"- **[{sev}] {readable}** — {hint}")
    return "\n".join(lines)


def main_gap_hints(case_dir: str) -> None:
    """CLI: print gap hints for a case (used by the issue-creation workflow)."""
    case_name = case_dir.rstrip("/").split("/")[-1]
    issues = CASES.get(case_name, [])
    missed = [i[0] for i in issues]  # all if used standalone
    print(build_gap_hints(case_name, missed))
