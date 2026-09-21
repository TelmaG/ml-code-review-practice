# Answer key

## P1
1. Registry request has no timeout/retry/authentication; the watcher can hang forever and silently stop refreshing.
2. Models are loaded into the live global dictionary one by one. Requests can observe a partial model set or a mixture of versions during reload.
3. `old = models; models = models; del old` never creates a new snapshot, so old models are not released. Repeated reloads accumulate references/allocations and can exceed 16GB.
4. No artifact integrity/version/schema validation and no rollback if one model fails; a bad model can leave the service partially refreshed.

## P2
5. Background thread has no exception boundary or health metric; one exception can kill the watcher silently.
6. No locking/atomic swap or request consistency policy; one ensemble request may use mixed model versions.
7. No startup readiness, reload timeout, or memory budget before installing a new version.
