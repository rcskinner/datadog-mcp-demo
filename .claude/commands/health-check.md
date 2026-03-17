Check the health of the service by querying Datadog.

---

# Phase 1 — Resolve Service Identifiers

Read `k8s/configmap.yaml` and `k8s/deployment.yaml` directly (no subagent needed).
- Extract every unique `DD_SERVICE` value from the configmap
- Extract every deployment `metadata.name` from the deployment manifest
- Extract the `namespace` from the deployment manifest
- Deduplicate and build:
  - `$SERVICE_QUERY` — combined Datadog query string
  - `$NAMESPACE` — k8s namespace
  - `$DEPLOYMENTS` — list of deployment names

Print:
```
Services targeted: <all unique DD_SERVICE values and deployment names>
Namespace:         <namespace>
Combined query:    <$SERVICE_QUERY>
```

---

# Phase 2 — Parallel Data Collection

Launch all three subagents **in a single message** using the Agent tool (general-purpose type).
Do not wait between launches — fire all three at once.

## Subagent 1 — logs
Prompt:
> You are collecting log health data from Datadog. The target query is `$SERVICE_QUERY`.
> Run these two calls in parallel, both from `now-5m` to `now`:
> 1. `search_datadog_logs` — all logs for `$SERVICE_QUERY`
> 2. `search_datadog_logs` — same query with `status:error` appended
>
> Return a structured block containing:
> - total log count
> - first 5 application-level log sample lines (skip raw HTTP access log lines like `INFO: x.x.x.x - "GET /..."`)
> - error log count
> - for each distinct error: message, version, file:line, first seen timestamp, count
>
> Important: ignore raw uvicorn/gunicorn HTTP access log lines (format: `INFO: <ip> - "<METHOD> <path> HTTP/..."`) — these are not application errors.

## Subagent 2 — spans
Prompt:
> You are collecting APM trace health data from Datadog. The target query is `$SERVICE_QUERY`.
> Run these two calls in parallel, spans from `now-5m` to `now`:
> 1. `search_datadog_spans` — all spans for `$SERVICE_QUERY`
> 2. `search_datadog_services` — registered service list for `$SERVICE_QUERY`
>
> Return a structured block containing:
> - total span count
> - count of spans with status:error
> - registered services list
> - one full error span traceback if any errors were found (include endpoint, HTTP status, error type, stack)

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

---

# Phase 3 — Consolidate and Analyze

Collect the three subagent results. Build the snapshot, then produce the reports below. 
**No further MCP calls after this point.**

```
<datadog-snapshot timestamp="[ISO timestamp]">

[LOGS]
total_count: <n>
sample: <first 5 log lines>

[ERROR_LOGS]
total_count: <n>
distinct_errors: <list each unique error message + count + version + file:line>
first_seen: <earliest timestamp per error>

[SERVICES]
registered: <comma-separated list>

[SPANS]
total_count: <n>
error_spans: <count of spans with status:error>
sample_error: <one full error span traceback if present>

[METRICS]
cpu_usage_avg_mcores:
  demo-api-v1: <value>
  demo-api-v2: <value>
cpu_throttled: <yes/no per deployment>
memory_usage_avg_mb:
  demo-api-v1: <value>
  demo-api-v2: <value>
memory_rss_start_mb / end_mb / growth_mb:
  demo-api-v1: <start> / <end> / <growth>
  demo-api-v2: <start> / <end> / <growth>
oom_events:
  demo-api-v1: <count>
  demo-api-v2: <count>

</datadog-snapshot>
```

## Health Report

| Check | Status | Detail |
|---|---|---|
| Logs flowing | PASS/FAIL | total log count in last 5m |
| APM service registered | PASS/FAIL | which services found |
| Traces visible | PASS/FAIL | span count in last 5m |
| Errors detected | PASS/FAIL | error count + one-line summary |
| CPU normal | PASS/FAIL | avg mCPU, throttled yes/no |
| Memory stable | PASS/FAIL | RSS growth over 3h |
| OOM events | PASS/FAIL | count |

One-sentence overall verdict.

## Error Report

For each distinct error found in the snapshot:
- Error type and message
- Endpoint and HTTP status
- Version it affects
- File and line number
- First seen timestamp
- Approximate frequency (errors/min)

## Infrastructure Summary

- Summarize the related kubernetes infrastructure in a table 
- CPU usage per deployment (mCPU)
- Memory usage per deployment (MB current, MB growth)
- RSS growth flag if >5 MB/hour
- OOM risk assessment
- Resource limits configured: yes/no


## Summarize 
Give a concise summary about the state of the deployment and make a recommendation if the deployment is a viable candidate for promotion from staging to production