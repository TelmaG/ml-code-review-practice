# PR: Automated rollback evaluator

Context: A canary compares models on conversion and latency. Traffic is seasonal, users are repeated, and the system must roll back within 10 minutes for a real regression without reacting to noise.