# Answer key

## P1
1. Synchronous endpoint and CPU preprocessing block request workers; no batching or queue means 1,500 QPS cannot use the GPU efficiently.
2. Every request allocates/copies tensors and synchronizes the GPU before returning; `cuda.synchronize()` destroys overlap and inflates p99.
3. No input size limit, timeout, or overload behavior; a 32-image request can monopolize the GPU and cause queue collapse.

## P2
4. No model eval mode or mixed precision policy; unnecessary memory/latency.
5. Model loading at import is not lifecycle-managed and startup/readiness is absent.
6. No metrics for queue wait, preprocessing, GPU, and serialization latency.
