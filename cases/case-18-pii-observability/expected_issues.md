# Answer key

## P1
1. Entire payload and result are logged, likely including financial/identity data, into 90-day searchable logs. This is a privacy and compliance incident.
2. No request correlation, model version, outcome/error metrics, or redaction policy; incidents cannot be investigated safely or reliably.
3. Prediction exceptions are not observed with a structured failure event and may leak stack traces through framework defaults.

## P2
4. Uses wall-clock `time.time()` for latency; clock changes can create negative values. Use monotonic timing.
5. Global root logger and raw string formatting make retention, sampling, and field-level access control difficult.
6. No rate limiting or log sampling under high QPS; logging can become a latency and cost bottleneck.
