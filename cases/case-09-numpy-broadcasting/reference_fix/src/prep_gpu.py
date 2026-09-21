"""Batch image preprocessing — reference fix."""
import numpy as np

IMAGENET_MEAN = np.float32([0.485, 0.456, 0.406])[None, None, None, :]
IMAGENET_STD = np.float32([0.229, 0.224, 0.225])[None, None, None, :]
WHITEN_SCALE = np.float32(0.01)
MAX_BATCH = 8192  # memory-budget cap: 8192 x 224 x 224 x 3 x 4 bytes ≈ 4.9GB float32


def preprocess_batch(images):
    """images: iterable of (224, 224, 3) uint8 arrays, len <= MAX_BATCH."""
    n = len(images)
    if n > MAX_BATCH:
        raise ValueError(f"batch of {n} exceeds MAX_BATCH={MAX_BATCH}; chunk upstream")

    batch = np.stack(images).astype(np.float32)  # float32 early: half the memory of float64
    batch = batch / 255.0
    batch = (batch - IMAGENET_MEAN) / IMAGENET_STD  # normalize: subtract mean, divide std
    batch *= WHITEN_SCALE  # scalar scale — never materialize a diagonal matrix
    return np.ascontiguousarray(batch.transpose(0, 3, 1, 2))  # NCHW, one explicit copy


if __name__ == "__main__":
    import time
    rng = np.random.default_rng(42)  # seeded demo data
    demo = [rng.integers(0, 256, (224, 224, 3), dtype=np.uint8) for _ in range(512)]
    t = time.time()
    out = preprocess_batch(demo)
    print(f"preprocessed {out.shape} {out.dtype} in {time.time() - t:.2f}s; "
          f"mean={out.mean():.3f} std={out.std():.3f}")
