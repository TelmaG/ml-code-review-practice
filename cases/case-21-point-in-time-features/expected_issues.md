# Answer key

## P1
1. Profiles are joined on current customer state without an as-of timestamp; future profile updates leak into historical examples.
2. Rolling window includes the current transaction and potentially events after the label/prediction timestamp; temporal leakage inflates evaluation.
3. No train/evaluation time boundary or point-in-time join validation; the 2B-row job can produce a high-scoring but invalid model.

## P2
4. `groupby(...).rolling` is not explicitly sorted and may behave incorrectly on unsorted event partitions.
5. Full in-memory joins at 2B rows are unsafe; use partitioned/as-of engine and column pruning.
6. No duplicate-key or timestamp quality checks.
