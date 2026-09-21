# PR: Low-latency ensemble service

Context: Three models provide complementary scores. Requests have a 120ms p99 budget. A slow dependency may be hedged, but total downstream load must remain bounded.