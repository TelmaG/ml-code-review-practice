# PR #701: GPU batch-inference preprocessor

**Author:** cv-eng · **Reviewers:** you · **Target:** `main`

## Context

Ticket: IMG-23 — vectorize image preprocessing before the GPU batch inferencer.

- Nightly batch: ~2M images per run on a single GPU worker (16GB RAM + 24GB VRAM).
- Current runtime budget: 90 min; last manual run took ~6h on CPU-bound prep.
- Images decoded to `(224, 224, 3)` uint8 arrays upstream.
- Author's note: "I vectorized the loops with numpy as requested in review last
  sprint. Should be fast now."
