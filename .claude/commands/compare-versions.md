Compare the two running versions of the API using Datadog data to produce a rollout readiness report.

First, read `k8s/configmap.yaml` and `k8s/deployment.yaml`:
- Extract `DD_SERVICE` and `DD_VERSION` per configmap entry
- Extract `metadata.name` per deployment
- Build `$SERVICE_QUERY`, `$DEPLOYMENTS`, and `$VERSIONS`

Run all of the following in parallel over the last 10 minutes:

1. **Error rate per version** — use `analyze_datadog_logs` SQL:
   `SELECT version, status, count(*) as count FROM logs WHERE $SERVICE_QUERY GROUP BY version, status`

2. **Latency per version** — use `search_datadog_spans` for each deployment in `$DEPLOYMENTS`, look at span durations to estimate p50/p95

3. **Throughput per version** — use `analyze_datadog_logs` SQL:
   `SELECT version, DATE_TRUNC('minute', timestamp) as minute, count(*) as requests FROM logs WHERE $SERVICE_QUERY GROUP BY version, DATE_TRUNC('minute', timestamp) ORDER BY minute DESC`

4. **Endpoint inventory per version** — use `search_datadog_spans` for each deployment in `$DEPLOYMENTS`, collect unique `resourcename` values to diff endpoints across versions

5. **Error details for any failing endpoints** — use `search_datadog_spans` with `$SERVICE_QUERY status:error`, collect error type, message, stack, and first seen time

## Output Format

Print a version comparison table:

```
⏺ VERSION COMPARISON  v1.0.0 vs v2.0.0  (snapshot: 2026-03-17T15:23Z)
  ─────────────────────────────────────────────────────────────────────
                                  v1.0.0          v2.0.0
  ─────────────────────────────────────────────────────────────────────
  Error rate                      0%              0%
  Throughput                      ~225 req/min    ~401 req/min
  p50/p95  GET /items             42ms / 48ms     9.6ms / 9.6ms
  p50/p95  POST /items            2.6ms / 3.0ms   1.6ms / 1.6ms
  p50/p95  GET /items/{id}        —               0.78ms / 0.82ms
  p50/p95  GET /items/stats       —               0.97ms / 0.97ms
  Endpoints                       2               4
  Span count                      1,114           2,816
  CPU (mcores)                    45.25           17.53
  Memory (MB)                     107.36          96.74
  RSS growth (3h)                 +1.62 MB        +0.03 MB
  OOM events                      0               0
  ─────────────────────────────────────────────────────────────────────
```

Then print an endpoint diff:
- List endpoints present in both versions
- List endpoints NEW in v2, with their health status (healthy / error rate %)

Then print an **Error Breakdown** for any failing endpoints:
- Endpoint, error type, error message, first seen, error rate

Finally print a **Rollout Recommendation** — one clear sentence: is v2 safe to promote, and why or why not?
