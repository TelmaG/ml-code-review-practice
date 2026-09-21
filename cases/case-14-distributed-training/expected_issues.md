# Answer key

## P1
1. No DistributedSampler or `set_epoch`; every rank may process the same shuffled data, invalidating throughput and reproducibility.
2. Every rank writes the same checkpoint path concurrently; files can be corrupted or last-writer-wins with no optimizer/data-loader state.
3. Seed is rank-dependent but worker, CUDA, and data-loader generator seeds are not controlled; reruns and restarts diverge silently.

## P2
4. Checkpoint saves every epoch to shared storage synchronously, creating an I/O barrier across four workers.
5. Only model weights are saved; optimizer, epoch, scaler, RNG, and sampler position are missing, so restart is not equivalent.
6. No evaluation barrier or rank-zero logging; metrics can be duplicated or inconsistent.
