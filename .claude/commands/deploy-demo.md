Deploy the demo-api service to Kubernetes and verify it is healthy using Datadog.

Follow these steps in order:

1. Apply all Kubernetes manifests:
   ```
   kubectl apply -f k8s/
   ```

2. Wait for the pod to reach Running status. Poll every 5 seconds:
   ```
   kubectl get pods -n demo-mcp
   ```
   Keep polling until the demo-api pod shows STATUS=Running (timeout after 90 seconds).

3. Port-forward the service in the background:
   ```
   kubectl port-forward svc/demo-api 18080:8000 -n demo-mcp &
   ```
   Wait 2 seconds for the tunnel to open.

4. Generate load against all endpoints (no extra deps, just curl):
   ```
   for i in 1 2 3 4 5; do curl -s -X POST http://localhost:18080/items -H "Content-Type: application/json" -d "{\"name\": \"item-$i\"}" > /dev/null; done
   curl -s http://localhost:18080/items > /dev/null
   for i in 1 2 3; do curl -s http://localhost:18080/items/fail > /dev/null; done
   curl -s http://localhost:18080/items/999 > /dev/null
   ```

5. Kill the port-forward:
   ```
   kill %1 2>/dev/null || true
   ```

6. Wait 30 seconds for telemetry to flow into Datadog.

7. Run all four Datadog MCP checks (do these in parallel if possible):
   - Search logs: query `service:demo-api`, from `now-5m`
   - Search services: look for `demo-api`
   - Search spans: query `service:demo-api`, from `now-5m`
   - Search error logs: query `service:demo-api status:error`, from `now-5m`

8. Print a deployment health report with a clear pass/fail for each check:
   - Logs flowing
   - APM service registered
   - Traces visible
   - Errors detected (include count and a brief summary if any)

Keep the report concise — one line per check plus a one-sentence overall verdict.
