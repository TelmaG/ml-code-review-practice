# Answer key — case 04

## P1

1. **Data leakage: `StandardScaler.fit_transform` before the split** —
   `train.py:34`. Validation statistics contaminate training → the 0.97 AUC is
   inflated and the promotion decision is based on a lie. → Split first, fit
   scaler on train only, transform valid; better, a sklearn `Pipeline`.
   *Detector: yes — data leakage smell*
2. **Accuracy printed on a 1%-positive dataset** — predicting "not fraud" for
   everything scores ~99% accuracy. Printing it invites the wrong conclusion;
   at least it's secondary to AUC, but per-class PR/ROC and a threshold
   analysis are missing. Auto-promotion off these printed numbers is unsafe.
   *Detector: yes — overreliance on accuracy / imbalanced handling*
3. **No reproducibility** — no seeds anywhere (`numpy` permutation, torch weight
   init, dropout/shuffle RNG, cuDNN nondeterminism). The "0.97" cannot be
   re-run; if prod regresses we can't attribute it to data vs RNG vs code.
   *Detector: yes — missing seeds (NumPy/Torch), DataLoader determinism*
4. **Overwrites the prod artifact unconditionally** —
   `torch.save(..., "/models/fraud/model.pt")` at the end of *every* run,
   successful or not, validated or not. A fat-fingered re-run silently swaps the
   production model; no rollback, no lineage. → versioned path + registry +
   explicit promotion step, save scaler + feature list + metrics alongside.

## P2

5. **`model.forward(X_train)` called directly + full-batch training** — skips
   hooks/wrappers, and 640k×… full-batch every epoch is slow and unstable; no
   DataLoader, no shuffled mini-batches, no GPU `.to(device)` at all (model and
   tensors stay on CPU — "runs on the GPU box" doesn't mean it *uses* the GPU).
   *Detector: yes — direct forward call, DataLoader reproducibility*
6. **No `opt.zero_grad()`** — gradients accumulate across epochs ("loss"
   decreases oddly; the printed curve misleads — another silent wrongness).
   This is arguably P1 for model quality. *Detector: yes — missing gradient zeroing*
7. **No `model.eval()`/toggle around eval, no early stopping, no checkpointing
   of best-valid weights** — last-epoch weights saved regardless of overfit.
   *Detector: yes — eval mode, early stopping, scheduler smells*
8. **No held-out test set / no cross-validation** — one 80/20 split and a
   promotion decision on it. Also `np.random.permutation` every run → different
   split per run (ties to #3).
9. **No scaler persistence** — the serving path rebuilds scaling how? Train/serve
   skew in the preprocessing is a classic silent prod failure.

## P3

10. Magic hyperparams inline, `print` logging, no experiment tracking
    (mlflow/wandb), no feature-list versioning, hardcoded paths.

## The headline

The author wants a "quick stamp" on 0.97 AUC. The reviewer's headline:
**this number is not trustworthy** — leakage (scaler), accumulated gradients,
unfixed seeds, and a different split per run. Fix the pipeline first, then
re-measure before any promotion decision.
