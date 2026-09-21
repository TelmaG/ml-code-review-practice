> **[P1] search.py:8–12 — the search overfits its validation set.** Selecting the best of 500 on one split and promoting on the same score makes 0.92 optimistic. Use nested CV or reserve a final untouched test set and require a separate promotion evaluation.

> **[P1] no seed and direct overwrite of `current.pkl`.** Results cannot be reproduced and an experiment can replace production. Version artifacts, persist configs/metrics/seeds, and separate registration from promotion.

> **[P2] all models remain resident.** Release non-winners and schedule trials across GPUs with a budget and failure isolation.
