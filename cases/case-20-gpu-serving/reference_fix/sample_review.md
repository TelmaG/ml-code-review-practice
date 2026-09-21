> **[P1] server.py:10 — each request synchronously preprocesses and runs the GPU.** At 1,500 QPS the GPU sees tiny, serialized jobs and CPU workers block. Add a bounded micro-batch queue with a max wait and explicit overload response.

> **[P1] `cuda.synchronize()` per request.** This prevents CPU/GPU overlap and makes every request wait for the entire device. Time stages separately and synchronize only at the result boundary.

> **[P1] no request size/queue limits.** A maximum 32-image request can monopolize the device. Bound batch size, queue depth, and request timeout; reject quickly under overload.
