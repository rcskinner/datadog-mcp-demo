Triage the current health of the deployment and recommend fixes for any errors found.

First, read the source code to understand the codebase:
- Read `demo-api/src/app.py` for all routes
- Read `demo-api/src/items.py` for the data model

Then run the following Datadog queries in parallel over the last 10 minutes:

1. **Error spans with full detail** — `search_datadog_spans` with `service:(demo-api OR demo-api-v1 OR demo-api-v2) status:error`, request `error.type`, `error.message`, `error.stack` custom attributes
2. **Error log patterns** — `search_datadog_logs` with `use_log_patterns: true` on `service:(demo-api OR demo-api-v1 OR demo-api-v2) status:error`
3. **Error rate by endpoint** — `analyze_datadog_logs` SQL grouping by version, message, and count

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
