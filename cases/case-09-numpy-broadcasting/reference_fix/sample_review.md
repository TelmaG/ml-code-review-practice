# Sample review — case 09

Blocking — this silently changes model inputs and can OOM the worker.

> **[P1] prep_gpu.py:15 — normalization formula is inverted**
> `batch * MEAN + STD` should be `(batch − MEAN) / STD`. Shapes broadcast fine,
> so nothing errors; the model receives systematically-shifted inputs and keeps
> emitting plausible tensors. This is a silent quality regression at 2M images/
> night. Fix the line, and add the test that would have caught it: preprocess a
> constant image, assert the output equals the analytically-computed value.

> **[P1] prep_gpu.py:22 — `np.eye(50176)*0.01` materializes ~19GB**
> On a 16GB worker this is a MemoryError at best, swap-death at worst (6h → days
> under swap thrash). Semantically it's just `* 0.01` — compute it as a scalar
> multiply. If real whitening is intended later, store the vector, never the
> diagonal matrix.

> **[P2] memory profile: float64 intermediates + unbounded batch**
> `/ 255.0` promotes uint8 → float64, `np.array(list_of_arrays)` copies, and
> nothing stops a caller passing all 2M at once. Cast to float32 first
> (`np.stack(...).astype(np.float32)`), cap with MAX_BATCH + chunk upstream,
> and make the NCHW transpose one explicit contiguous copy.

> **[P3] fp16 output + unseeded demo**
> fp16 is fine for the GPU side, but cast at the boundary with a range check,
> and seed the demo (`default_rng(42)`) so perf numbers are comparable run to
> run.

The good news: the vectorization direction is right. Once the formula, the
19GB eye, and the dtype ladder are fixed, this should sit comfortably in the
90-minute window.
