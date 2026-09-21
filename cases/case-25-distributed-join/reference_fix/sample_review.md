> **[P1] join.py:8 — `collect()` makes a driver-sized lookup from a multi-terabyte join.** The driver will OOM. Keep the join distributed and select only required columns; use a broadcast only if the measured dimension fits.

> **[P1] no skew/partition plan.** A few hot product keys can make one executor the 2-hour straggler. Profile key distribution, enable AQE/skew handling, and measure stage-level tails.

> **[P2] overwrite of final output is not an atomic publish.** Write a run-versioned path, validate counts/schema, then commit a success marker or metadata pointer.
