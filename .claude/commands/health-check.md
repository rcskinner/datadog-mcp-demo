Check the health of the service by querying Datadog.

First, read the k8s files to build the full list of service identifiers:
- Read `k8s/configmap.yaml` and extract every unique `DD_SERVICE` value
- Read `k8s/deployment.yaml` and extract every deployment `metadata.name`
- Combine them into a deduplicated list and construct a Datadog OR query, e.g. `service:(demo-api OR demo-api-v1 OR demo-api-v2)`


# Summarize the Datadog Searches 
Provide the user with a concise list of datadog services that the skill is looking for. Enumerate them clearly and separately in a list that is human readable. This is for auding purposes thaNo t allows the user to understand if the skill is targeting the correct services. 

Use this combined query for all checks below.

Run all four checks in parallel:
- Search logs: combined service query, from `now-5m`
- Search services: combined service query
- Search spans: combined service query, from `now-5m`
- Search error logs: combined service query + `status:error`, from `now-5m`

Print a health report with a clear pass/fail for each check:
- Logs flowing
- APM service registered
- Traces visible
- Errors detected (include count and a brief summary if any)

One line per check plus a one-sentence overall verdict.


## Error Report

Print a detailed report of the different errors detected in the deployment, when they're first detected and what version they are associated with