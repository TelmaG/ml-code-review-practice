# PR: Model artifact downloader

Context: Production workers download model artifacts during deployment from an object store. Artifacts are produced by a CI pipeline and must be integrity-checked before loading.