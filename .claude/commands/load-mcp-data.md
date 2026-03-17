Pre-load all Datadog data into a local snapshot so skills can run without hitting the MCP API.

---

# Phase 0 — Resolve Service Identifiers

Read `k8s/configmap.yaml` and `k8s/deployment.yaml`.
- From configmap: extract every unique `DD_SERVICE` value
- From deployment: extract every `metadata.name` and `namespace`
- Deduplicate and build:
  - `$SERVICE_QUERY` — e.g. `service:(demo-api OR demo-api-v1 OR demo-api-v2)`
  - `$NAMESPACE` — the k8s namespace (e.g. `demo-mcp`)
  - `$DEPLOYMENTS` — list of deployment names (e.g. `demo-api-v1`, `demo-api-v2`)
  - `$VERSIONS` — list of DD_VERSION values per configmap (e.g. `1.0.0`, `2.0.0`)

Use these variables in all subagent prompts below.

---

# Phase 1 — Collect All Data in Parallel

Launch all four subagents **in a single message** using the Agent tool (general-purpose type).
Do not wait between launches — fire all four at once.

## Subagent 1 — logs
Prompt:
> You are collecting log data from Datadog. The target query is `$SERVICE_QUERY`.
> Run these two calls in parallel, both from `now-5m` to `now`:
> 1. `search_datadog_logs` — all logs for `$SERVICE_QUERY`
> 2. `search_datadog_logs` — same query with `status:error` appended, use `use_log_patterns: true`
>
> Return a structured block containing:
> - total log count
> - first 5 log sample lines (skip raw HTTP access log lines like `INFO: x.x.x.x - "GET /..."` — only include application-level log messages)
> - error log count
> - for each distinct error: message, version, file:line, first seen timestamp, count
>
> Important: ignore raw uvicorn/gunicorn HTTP access log lines (format: `INFO: <ip> - "<METHOD> <path> HTTP/..."`) — these are not application errors and must not be treated as endpoint names or errors.

## Subagent 2 — spans and services
Prompt:
> You are collecting APM trace and service data from Datadog. The target query is `$SERVICE_QUERY`.
> Run these three calls in parallel, spans from `now-5m` to `now`:
> 1. `search_datadog_spans` — all spans for the service query
> 2. `search_datadog_spans` — same query with `status:error`, request `error.type`, `error.message`, `error.stack` attributes
> 3. `search_datadog_services` — registered service list
>
> Return a structured block containing:
> - total span count
> - error span count
> - registered services list
> - for each error span: endpoint, HTTP status, error type, error message, full stack trace, first seen timestamp

## Subagent 3 — metrics
Prompt:
> You are collecting container resource metrics from Datadog for namespace `$NAMESPACE`.
> Run all five of these in parallel:
> 1. `get_datadog_metric` — `avg:container.cpu.usage{kube_namespace:$NAMESPACE} by {kube_deployment}`, from `now-30m`
> 2. `get_datadog_metric` — `avg:container.cpu.throttled{kube_namespace:$NAMESPACE} by {kube_deployment}`, from `now-30m`
> 3. `get_datadog_metric` — `avg:container.memory.usage{kube_namespace:$NAMESPACE} by {kube_deployment}`, from `now-30m`
> 4. `get_datadog_metric` — `avg:container.memory.rss{kube_namespace:$NAMESPACE} by {kube_deployment}`, from `now-3h`
> 5. `get_datadog_metric` — `avg:container.memory.oom_events{kube_namespace:$NAMESPACE} by {kube_deployment}`, from `now-30m`
>
> Return a structured block containing per deployment:
> - cpu_usage_avg_mcores (divide raw values by 1e6)
> - cpu_throttled yes/no
> - memory_usage_avg_mb (divide raw bytes by 1e6)
> - memory_rss_start_mb, memory_rss_end_mb, memory_rss_growth_mb (first and last values from the 3h window)
> - oom_event_count

## Subagent 4 — version comparison
Prompt:
> You are collecting version comparison data from Datadog. Services are `$DEPLOYMENTS` with versions `$VERSIONS`.
> Run all three of these in parallel over the last 10 minutes:
> 1. `analyze_datadog_logs` — SQL: `SELECT version, status, count(*) as count FROM logs WHERE $SERVICE_QUERY GROUP BY version, status`
> 2. `analyze_datadog_logs` — SQL: `SELECT version, DATE_TRUNC('minute', timestamp) as minute, count(*) as requests FROM logs WHERE $SERVICE_QUERY GROUP BY version, DATE_TRUNC('minute', timestamp) ORDER BY minute DESC`
> 3. `search_datadog_spans` — for each deployment in `$DEPLOYMENTS` separately, collect unique `resourcename` values and span durations to estimate p50/p95 latency
>
> Return a structured block containing:
> - error count and rate per version
> - throughput (requests/min) per version
> - p50 and p95 latency per version
> - endpoint list per version (for diffing — derive endpoint names exclusively from span `resourcename` values, never from log message text)

---

# Phase 2 — Write Snapshot

Collect all four subagent results. Write the following file using the Write tool to `.claude/snapshot.md`.
Use the current ISO timestamp. **Preserve full detail from every subagent — do not summarize or truncate. Include all counts, all per-deployment rows, all per-endpoint latency splits, all observations and anomalies noted by subagents.**

```
<datadog-snapshot timestamp="[ISO timestamp]">

[LOGS]
total_count: <n>
sample: <first 5 log lines>

[ERROR_LOGS]
total_count: <n>
distinct_errors: <list each unique error message + count + version + file:line>
first_seen: <earliest timestamp per error>
patterns: <log patterns from use_log_patterns if any>

[SERVICES]
registered: <comma-separated list>

[SPANS]
total_count: <n>
error_count: <n>

[ERROR_SPANS]
<for each error span:>
  endpoint: <value>
  http_status: <value>
  error_type: <value>
  error_message: <value>
  first_seen: <timestamp>
  stack:
    <full stack trace>

[METRICS]
cpu_usage_avg_mcores:
  <one entry per $DEPLOYMENTS>
cpu_throttled:
  <one entry per $DEPLOYMENTS: yes/no>
memory_usage_avg_mb:
  <one entry per $DEPLOYMENTS>
memory_rss_start_mb / end_mb / growth_mb:
  <one entry per $DEPLOYMENTS>
oom_events:
  <one entry per $DEPLOYMENTS>

[VERSION_COMPARISON]
error_rate:
  <one entry per $VERSIONS: count + rate%>
throughput:
  <one entry per $VERSIONS: ~n rps>
latency:
  <one entry per $VERSIONS: p50=ms p95=ms>
endpoints:
  <one entry per $DEPLOYMENTS: comma-separated endpoint list>

</datadog-snapshot>
```

---

# Phase 3 — Confirm

Print:
```
Snapshot saved to .claude/snapshot.md
Timestamp: [ISO timestamp]
Coverage: logs, error logs, spans, error spans, metrics, version comparison
Run /health-check, /triage, or /compare-versions — they will use this snapshot.
```
