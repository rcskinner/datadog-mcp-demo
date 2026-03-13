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

- `/health-check` — checks deployment health against the configured Datadog instance
