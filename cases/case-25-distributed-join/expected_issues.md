# Answer key

## P1
1. `collect()` moves the distributed join result to the driver; 8TB/40TB scale causes driver OOM.
2. Join has no column pruning, partition strategy, skew handling, or broadcast decision; hot product keys can create stragglers and miss the 2-hour SLA.
3. RDD map after join loses optimizer/vectorization and creates a second expensive pass; output semantics are unclear.

## P2
4. Overwrite is not atomic/versioned; partial output can be consumed as complete.
5. No data-quality row counts, duplicate key, null, or schema checks.
6. No adaptive query execution or resource/partition configuration.
