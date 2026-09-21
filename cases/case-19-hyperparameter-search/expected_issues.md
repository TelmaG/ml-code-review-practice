# Answer key

## P1
1. All 500 configurations select on one validation set and auto-promote on that same set; the threshold is overfit to the search and optimistic.
2. No fixed split seed or nested/held-out test set; results are not reproducible and the winner cannot be independently audited.
3. Unconditional save to current model path allows a search run to replace production without artifact metadata or approval.

## P2
4. Stores every trained model in memory, including GPU resources, rather than releasing non-winners.
5. No parallelism/resource scheduler despite four GPUs; sequential search wastes the window.
6. No failed-trial isolation, experiment tracking, or cost/time budget.
