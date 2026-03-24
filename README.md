# datadog-mcp-demo

Demo sandbox for Datadog MCP.

## Prerequisites

- Local k8s cluster (minikube, kind, orbstack, etc.) with the Datadog Agent running
- An LLM client configured with the Datadog MCP server
- Docker

## Datadog Installation

```bash
helm repo add datadog https://helm.datadoghq.com
helm install datadog-operator datadog/datadog-operator
kubectl create secret generic datadog-secret --from-literal api-key=<your-api-key>

kubectl apply -f datadog-agent.yaml
```

See `datadog/values.yaml` for the full configuration.

## Usage

```bash
make deploy-local   # build image and apply k8s manifests using local Docker
make deploy-remote  # build, push to registry, and apply k8s manifests (requires REGISTRY in .env)
make load     # start load generators
make stop-load # stop load generators
make teardown # delete the demo-mcp namespace

Use `deploy-local` to deploy to your local docker for orb/kind/k3s 
Use `deploy-remote` to push an image to your target registry for use with cloud clusters or other more production oriented clusters
```

## Claude Skills

- `/load-mcp-data` — pre-loads all Datadog data into `.claude/snapshot.md`; run this first so other skills use the cache instead of hitting the MCP API on every call
- `/health-check` — checks deployment health against the configured Datadog instance
- `/triage` — queries error spans and logs, cross-references source code, and recommends fixes
- `/compare-versions` — compares v1 and v2 error rates, latency, and throughput to produce a rollout readiness report

> Skills read from the snapshot by default. Pass `--refresh` or re-run `/load-mcp-data` to pull fresh data.
