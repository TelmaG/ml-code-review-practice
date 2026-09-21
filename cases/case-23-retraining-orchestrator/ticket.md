# PR: Concurrent retraining controller

Context: Three model families retrain concurrently from shared data. A run must be reproducible, artifacts immutable, and only one promotion may win. Jobs can be interrupted and resumed.