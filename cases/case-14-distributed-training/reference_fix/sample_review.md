> **[P1] train.py:11 — no distributed sampler.** Four workers can train on overlapping examples and each epoch's shuffle is not coordinated. Use a `DistributedSampler`, call `set_epoch`, and seed every worker generator.

> **[P1] checkpoint writes are concurrent and incomplete.** Any rank can corrupt the same file, and restart loses optimizer/RNG/sampler state. Rank zero should atomically write a complete checkpoint with a manifest.

> **[P2] synchronous shared-storage save every epoch.** This creates a distributed I/O barrier. Save asynchronously or at a bounded cadence after measuring checkpoint recovery objectives.
