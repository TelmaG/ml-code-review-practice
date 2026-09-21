# PR: Feature cache refresh

Context: The online scorer serves 3,000 QPS. Features are refreshed from a warehouse every 5 minutes. A stale feature older than 10 minutes must never be served; the warehouse can be slow for several minutes. Review freshness, concurrency, and cache behavior.