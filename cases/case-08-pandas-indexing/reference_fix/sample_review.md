# Sample review — case 08

> **[P1] joiner.py:11 — full-table scan per online lookup**
> **Risk:** `features[features.user_id == user_id]` scans 10M rows per request.
> At 800 QPS that's ~8 × 10⁹ row-comparisons/sec — latency collapses the moment
> traffic ramps. The 200-user fixture can't see this; the arithmetic can.
> **Suggestion:** index once at construction (`set_index`/dict) for O(1)
> `lookup`; if 10M rows stops fitting, this becomes a Redis/feature-store
> lookup — same interface.

> **[P1] joiner.py:21 — `shift(-1)` leaks labels across users, `fillna(0)`
> fabricates labels**
> **Risk:** After the merge, row N−1 of user A sees user B's conversion as its
> label, and every genuine tail becomes "no conversion". We trained last
> quarter's model on similarly-built labels — part of the persistent
> offline/online AUC gap may be this.
> **Suggestion:** `groupby("uid")["converted"].shift(-1)` and drop tails; never
> fill unknown outcomes with a class value — that's silent label fraud.

> **[P2] merge without `validate`**
> Duplicate `user_id` in a bad features rebuild multiplies log rows silently;
> and `drop_duplicates()` right after is both expensive and masks the root
> cause. Add `validate="m:1"` — duplicates become a build-time error instead of
> a training-data mystery.

> **[P2] `groupby.apply(lambda sort+head)`**
> Python-level apply over 50M rows → nightly window risk. Vectorize:
> `sort_values(...).groupby("uid").head(50)` — same semantics, orders of
> magnitude faster, no per-group interpreter overhead.

> **[P2] inconsistent unknown-user semantics**: online `{}` vs offline
> inner-drop. One policy, both paths: left-join + missing-rate metric, raise
> above a threshold — new-user spikes during a signup push currently vanish
> from training without a trace.

Quick review granted on shape — this is the right abstraction boundary. The
label construction and lookup complexity need to land before merge.
