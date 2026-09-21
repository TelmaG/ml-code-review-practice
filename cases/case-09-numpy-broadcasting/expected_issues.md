# Answer key — case 09

## P1

1. **Mean and std swapped in normalization** — `batch * MEAN + STD` instead of
   `(batch − MEAN) / STD`. Inputs are systematically wrong; the model still
   produces numeric outputs → **silent garbage at scale**, and last sprint's
   "vectorized!!!" framing makes reviewers skim. This is *the* textbook
   broadcasting-era wrong-numbnut bug: shapes line up, values don't.
   → `(x / 255.0 − MEAN[None,None,None,:]) / STD[None,None,None,:]`,
   with a test asserting output mean≈0/std≈1 on known data.
2. **`np.eye(50176) * 0.01` — ~19GB allocation for a diagonal scale** —
   `dataset_whitening` builds a full 50176² float64 matrix (~18.8GB) on a
   16GB-RAM worker; then `@` attempts batched matmul over it. Either MemoryError
   (loud) or swap-death (hours added) — and if it *does* fit somewhere with
   more RAM, it's computing `0.01 * x` the slowest way possible.
   → never materialize the matrix: `batch * 0.01` after appropriate reshape.
3. **`float16` at the end of prep** — halves GPU bandwidth later (good instinct)
   but cast *after* all compute and without range checks: intermediate float64
   blows memory (batch of 512 → ~1.2GB float64 alone); overflow in fp16 is
   possible if preprocessing drifts. Also: no fixed seed on the demo randomness
   in `__main__`.

## P2

4. **`np.array(images)` from a python list of 2M arrays** — one giant copy +
   int64-typed intermediate before the float cast; ~2× memory churn of the
   already-large uint8 payload. → `np.stack(..., dtype=...)` or preallocated
   buffer + iterator chunks.
5. **Copy-heavy axis shuffle** — `swapaxes` is a view (good) but the subsequent
   matmul forces a contiguous copy of the *whole batch* anyway; better to
   transpose into a preallocated float32 buffer. Also note: eager copies defeat
   "we vectorized it" if each op materializes intermediates.
6. **No batching/chunking control** — 2M images can't fit through this pipeline
   in one call; the caller is expected to chunk, but nothing enforces/document
   it → OOM at 3am when someone calls `preprocess_batch(all_2m)`.
   → take `batch_size` param / yield chunks; assert input length vs memory
   budget.
7. dtype consistency: input uint8 → implicit float64 after `/` — full
   float64 precision compute where float32 suffices; 2× memory and often slower
   on vectorized ops. → cast to float32 first, keep every op float32.

## P3

8. Magic stats hardcoded in two places (ImageNet + whitening scale) with no
   provenance/version; demo uses unseeded `np.random`.

## The headline

"Vectorized" is not the same as *correct* or *memory-safe* — #1 produces a
silent model-quality regression, #2 computes `0.01 * x` by way of a 19GB
eye matrix. In numpy review: **check the math direction (mult vs divide vs
subtract), and check every intermediate allocation's size arithmetic**.
