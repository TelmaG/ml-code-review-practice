# PR: Nightly retraining workflow

Context: An orchestrator retries failed tasks automatically. The workflow downloads data, trains, registers, and deploys a model. A run may be resumed after a worker crash; deployment must never happen twice for one run.