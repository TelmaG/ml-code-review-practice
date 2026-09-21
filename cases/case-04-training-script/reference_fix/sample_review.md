# Sample review — case 04

Not stamping this yet. The 0.97 is measurement, not progress — context: dataset
is 1% positive, so accuracy of the constant classifier is ~99% and any number
we print here decides a production swap.

> **[P1] train.py:34 — `fit_transform` before the train/valid split**
> **Risk:** Validation rows leak into the scaler, so 0.97 inflates the true
> number by an unknown amount, and we're about to promote off it. If we deploy
> as-is, we risk shipping a model that's actually worse than prod with no way
> to know.
> **Suggestion:** Split first, fit the scaler on train only, transform valid
> (sklearn Pipeline). Re-measure before we talk promotion.

> **[P1] train.py:46 — missing `opt.zero_grad()`**
> **Risk:** Gradients accumulate across all 20 epochs, so each step uses
> stale gradient sums; the printed loss curve is misleading and the final
> weights aren't what the optimizer "intended". Combined with the leakage we
> can't say what this model actually is.
> **Suggestion:** `opt.zero_grad()` at the top of each step.

> **[P1] train.py — no seeds anywhere**
> **Risk:** Every run has a different split (`np.random.permutation`), init and
> cuDNN nondeterminism. If next week's rerun prints 0.93, is it the data or the
> RNG? Debugging regressions becomes archaeology.
> **Suggestion:** Fix `random`/`numpy`/`torch` seeds (+ `cudnn.deterministic`),
> `random_state` on the split, log the seed in the run metadata.

> **[P1] train.py:60 — unconditional overwrite of the prod artifact path**
> **Risk:** Any run — including a broken one — silently replaces the model
> serving pulls on restart. No rollback, no lineage.
> **Suggestion:** Versioned output dir (`/models/fraud/{date}/`), save the
> scaler + feature list + metrics with it, and make promotion an explicit
> separate step.

> **[P2] full-batch training on CPU, `model.forward()` directly**
> **Risk:** The tensor/model never touch the GPU on the "GPU box", 640k-row
> full-batch steps are slow and unstable, and calling `.forward()` directly
> skips any future wrappers/hooks.
> **Suggestion:** `.to(device)`, shuffled mini-batches (DataLoader with a seeded
> generator), call `model(x)`, and `BCEWithLogitsLoss` + `pos_weight` given
> the 1% positive rate.

Once these are in, re-run and we'll look at AUC + PR-AUC on a clean split. The
structure is close — it's the evaluation integrity that needs to be airtight
before this script drives a promotion decision.
