# Answer key

## P1
1. Warehouse call has no timeout and runs in an unbounded thread per request after expiry; a slow warehouse creates a refresh stampede and thread exhaustion.
2. Expired cache is still served while refresh runs, violating the ten-minute freshness contract; stale values are indistinguishable from fresh values.
3. Refresh swaps the global dictionary without a lock and mutates it during warmup; readers can observe partial state.

## P2
4. Every caller starts a refresh thread during expiry; use single-flight refresh and backoff.
5. Missing users receive a silent constant instead of an explicit fallback/metric.
6. Warmup loads the full parquet and converts all records to Python dictionaries, causing high memory use at 3,000 QPS replicas.
