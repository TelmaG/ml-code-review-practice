# PR: Batch inference worker

Context: 2M records/day arrive through a queue. Workers have 4 vCPU and 8GB RAM; p95 completion must stay below 5 minutes per batch. The model is 400MB and downstream retries messages when the process exits.

Review the worker and its queue adapter. Focus on backpressure, duplicate processing, model lifecycle, and failure recovery.