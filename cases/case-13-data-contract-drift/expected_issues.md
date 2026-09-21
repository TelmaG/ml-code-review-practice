# Answer key

## P1
1. `fillna(0)` globally turns missing categorical, numeric, and label values into valid-looking data. Contract violations become silently changed training semantics.
2. `errors='coerce'` plus fillna converts malformed amounts into zero; the job succeeds with corrupted features and no rejection threshold.
3. No schema/version validation, row-count, duplicate, range, or distribution checks before training. Producer drift can silently retrain and overwrite the model.

## P2
4. All files are loaded into memory at once; use typed columns, selected fields, and chunked/columnar processing.
5. Small-data condition only prints and still trains/saves; fail the job and page.
6. Artifact overwrites a shared current path without lineage, validation gate, or rollback metadata.
