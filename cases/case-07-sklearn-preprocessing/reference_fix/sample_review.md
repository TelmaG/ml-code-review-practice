# Sample review — case 07

Blocking. This module is the train/serve seam, and right now it's the most
dangerous kind of bug: everything errors never, scores always.

> **[P1] prep.py:14–19 — encoders/scalers are refit on every call**
> **Risk:** The `fit` parameter is accepted and ignored. Every serving request
> fits a fresh `LabelEncoder` on *that batch*, so `plan_type="pro"` encodes as
> 0 at 09:01 and 5 at 09:02. The model outputs plausible scores for scrambled
> inputs — the worst silent-failure class in this rubric. If we deploy this
> as-is, churn scores for the highest-value cohort are meaningless and nobody
> gets paged.
> **Suggestion:** Fit one sklearn `Pipeline` (ColumnTransformer +
> `OneHotEncoder(handle_unknown="ignore")` + `MinMaxScaler`) at training,
> `joblib.dump` it with the model artifact, and have serving call
> `.transform` only. Contract: fitting happens exactly once, owned by the
> training job.

> **[P1] prep.py:25 — division by zero for new customers**
> **Risk:** Every tenure-0 account yields `inf` in `spend_per_month`. Inf
> inputs give undefined model outputs for exactly the newest customers — the
> segment churn models most affect. No error surfaces.
> **Suggestion:** floor the denominator (`clip(lower=1)` / epsilon) and assert
> finiteness after engineering.

> **[P2] prep.py:22 — `dropna` in shared prep**
> **Risk:** Training silently loses biased-deletion rows; serving turns an
> all-null request into an empty matrix — indistinguishable from "no input".
> **Suggestion:** `SimpleImputer` inside the Pipeline for train, explicit
> validation error at serve.

> **[P2] unseen categories / ordinal encoding of `region`**
> ~400 regions guarantee unseen values at serve time (crash, or silent
> relabeling under the refit bug). And ordinal codes impose fake ordering on a
> nominal column. One-hot with `handle_unknown="ignore"` + `min_frequency`
> solves both.

> **[P3] `.values` return**
> Feature names are dropped — drift debugging becomes column-guessing. Return a
> named DataFrame.

Suggested test (adds real value): transform the same row through the training
path and the serving path and assert identical output — that's the regression
guard for the whole contract.
