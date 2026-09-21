# Answer key — case 07

## P1

1. **Refits `LabelEncoder` / `MinMaxScaler` on every call — train/serve skew** —
   `build_features` always fits fresh encoders (`fit` arg is accepted but
   ignored!). At serve time, a single row with plan `"pro"` encodes to 0, while
   training may have mapped `"pro"` → 5. The model receives per-request
   scrambled features and returns plausible garbage; nothing errors.
   → Fit once at training, persist the fitted Pipeline (ColumnTransformer +
   OneHotEncoder(handle_unknown="ignore") + scaler), `joblib.dump` it next to
   the model, and at serve time only call `.transform`.
2. **Unseen categories crash or silently mis-encode at serve time** —
   `LabelEncoder.fit_transform` on a serving batch containing a new region/
   plan_type raises (loud) or, combined with #1's refit, *relabels* existing
   categories (silent). ~400-value `region` guarantees unseen values.
   → `OneHotEncoder(handle_unknown="ignore")`.
3. **Division by zero → inf in engineered features** —
   `tenure_months == 0` for all new customers in month 0 → `spend_per_month =
   inf`. Model consumes infs silently; scores for exactly the newest customers —
   the churn cohort that matters most — are garbage.
   → clip/epsilon or define the ratio with a floor, and log a count.

## P2

4. **`dropna` inside the shared prep function** — silently shrinks training data
   (bias), and at serve time an empty input becomes an empty matrix: the caller
   can't distinguish "no rows" from "all rows dropped". Silent failure class.
   → impute deliberately (SimpleImputer in the Pipeline) or reject loudly.
5. **Ordinal encoding of high-cardinality categoricals** — LabelEncoder imposes
   a fake ordering on `region` (400 values); linear-ish models will treat region
   399 as "more" than region 3. → One-hot or target/embeddings with a decision
   note.
6. **No column-contract** — `df[FEATURES]` order depends on caller; missing
   column raises deep inside sklearn (confusing), extra columns silently
   ignored mid-refactor. → explicit schema check with a clear error (pydantic /
   pandera / manual).
7. **`fit: bool` parameter is dead/misleading** — invites the caller to think
   train/serve differ safely; they don't here. Remove the param entirely; the
   whole point is fitting must be the *training job's* artifact.
8. Mixed mutation: `out = df.copy()` then in-place assignment of scaled values —
   fine here, but the pattern `df[col] = ...` after `copy()` in a shared
   library invites SettingWithCopy bugs on future edits (mention once).

## P3

9. Returns bare `.values` ndarray — loses feature names; debugging importances/
   drift requires reverse-engineering column order. → return DataFrame (or the
   Pipeline's `get_feature_names_out`).
10. No unit test of serve-vs-train consistency: e.g. transform the same row
    through both paths, assert identical encoding (the test that would have
    caught #1 — suggest it explicitly).

## What the detector sees

`fit_transform` usage and general sklearn smells — partially flags #1. It
cannot see the *train/serve contract break*: that's the human review value.
The headline comment is: "this library is the seam between training and
serving; the contract belongs in code, not in the docstring."
