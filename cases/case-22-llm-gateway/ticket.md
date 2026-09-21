# PR: Multi-tenant LLM gateway

Context: 200 tenants call a shared gateway at 5k requests/sec. Each tenant has a budget, data-retention policy, and latency tier. Vendor calls can return 429, 5xx, malformed JSON, or hang.