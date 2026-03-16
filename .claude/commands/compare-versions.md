Compare the two running versions of the API (v1 and v2) using Datadog data to produce a rollout readiness report.

First, read the k8s files to identify the two versions:
- Read `k8s/configmap.yaml` to get DD_SERVICE and DD_VERSION values per version
- The two versions are v1 (version:1.0.0, service:demo-api-v1) and v2 (version:2.0.0, service:demo-api-v2)

Run all of the following in parallel over the last 10 minutes:

1. **Error rate per version** — use `analyze_datadog_logs` SQL:
   `SELECT version, status, count(*) as count FROM logs WHERE service = 'demo-api-v1' OR service = 'demo-api-v2' GROUP BY version, status`

2. **Latency per version** — use `search_datadog_spans` for each version, look at span durations to estimate p50/p95

3. **Throughput per version** — use `analyze_datadog_logs` SQL:
   `SELECT version, DATE_TRUNC('minute', timestamp) as minute, count(*) as requests FROM logs GROUP BY version, DATE_TRUNC('minute', timestamp) ORDER BY minute DESC`

4. **Endpoint inventory per version** — use `search_datadog_spans` for each version, collect unique `resourcename` values to diff what endpoints exist in v2 vs v1

5. **Error details for any failing endpoints** — use `search_datadog_spans` with `status:error` for v2, collect error type, message, stack, and first seen time

## Output Format

Print a version comparison table:

```
VERSION COMPARISON  v1.0.0 vs v2.0.0  (last 10m)
──────────────────────────────────────────────────
Error rate     v1: X%       v2: X%
Throughput     v1: ~X rps   v2: ~X rps
p95 latency    v1: Xms      v2: Xms
Endpoints      v1: X        v2: X
```

Then print an endpoint diff:
- List endpoints present in both versions
- List endpoints NEW in v2, with their health status (healthy / error rate %)

Then print an **Error Breakdown** for any failing endpoints:
- Endpoint, error type, error message, first seen, error rate

Finally print a **Rollout Recommendation** — one clear sentence: is v2 safe to promote, and why or why not?
