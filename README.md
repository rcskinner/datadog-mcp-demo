# datadog-mcp-demo

Demo sandbox for Datadog MCP.

## Prerequisites

- Local k8s cluster (minikube, kind, orbstack, etc.) with the Datadog Agent running
- An LLM client configured with the Datadog MCP server
- Docker

## Usage

```bash
make deploy   # build image and apply k8s manifests
make load     # start load generators
make stop-load # stop load generators
make teardown # delete the demo-mcp namespace
```

## Claude Skills

- `/load-mcp-data` — pre-loads all Datadog data into `.claude/snapshot.md`; run this first so other skills use the cache instead of hitting the MCP API on every call
- `/health-check` — checks deployment health against the configured Datadog instance
- `/triage` — queries error spans and logs, cross-references source code, and recommends fixes
- `/compare-versions` — compares v1 and v2 error rates, latency, and throughput to produce a rollout readiness report

> Skills read from the snapshot by default. Pass `--refresh` or re-run `/load-mcp-data` to pull fresh data.
