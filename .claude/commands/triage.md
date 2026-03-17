Triage the current health of the deployment and recommend fixes for any errors found.

First, read these files:
- `k8s/configmap.yaml` — extract unique `DD_SERVICE` values and `DD_VERSION` per configmap → build `$SERVICE_QUERY`
- `k8s/deployment.yaml` — extract `metadata.name` values → `$DEPLOYMENTS`
- `demo-api/src/app.py` — all routes
- `demo-api/src/items.py` — data model

Then run the following Datadog queries in parallel over the last 10 minutes:

1. **Error spans with full detail** — `search_datadog_spans` with `$SERVICE_QUERY status:error`, request `error.type`, `error.message`, `error.stack` custom attributes. Endpoint names must come from span `resourcename` only — never from log message text.
2. **Error log patterns** — `search_datadog_logs` with `use_log_patterns: true` on `$SERVICE_QUERY status:error`. Ignore raw uvicorn/gunicorn HTTP access log lines (format: `INFO: <ip> - "<METHOD> <path> HTTP/..."`) — these are not application errors.
3. **Error rate by endpoint** — `analyze_datadog_logs` SQL grouping by version, message, and count. Exclude access log lines from the message grouping.

## Triage Report

For each distinct error found, produce a section:

**Error: `<error.type>`**
- Endpoint:
- Version:
- First seen:
- Rate: errors/min
- Stack trace:
  ```
  <stack>
  ```

**Root Cause**
Cross-reference the stack trace against the source code you read. Identify the exact line, what it's trying to do, and why it fails.

**Recommended Fix**
Provide a concrete, specific code change that would fix the issue. Show the before/after diff inline.

---

At the end, print a one-line **Overall Verdict**: which version is healthy, which isn't, and what needs to happen before v2 is production-ready.
