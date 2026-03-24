-include .env

.PHONY: deploy-local deploy-remote load stop-load teardown

# Build and deploy using the local Docker image (no registry required)
deploy-local:
	docker build -t demo-api:latest demo-api/
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/
	kubectl rollout restart deployment -n demo-mcp

# Build, push to registry, and patch deployments to pull from the registry
# Requires REGISTRY to be set in .env or via CLI: make deploy-remote REGISTRY=<your-dockerhub-username>
deploy-remote:
ifndef REGISTRY
	$(error REGISTRY is not set. Set it in .env or via: make deploy-remote REGISTRY=<your-dockerhub-username>)
endif
	docker build -t $(REGISTRY)/demo-api:latest demo-api/
	docker push $(REGISTRY)/demo-api:latest
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/
	kubectl set image deployment/demo-api-v1 demo-api=$(REGISTRY)/demo-api:latest -n demo-mcp
	kubectl set image deployment/demo-api-v2 demo-api=$(REGISTRY)/demo-api:latest -n demo-mcp
	kubectl rollout restart deployment -n demo-mcp

load:
	kubectl apply -f k8s/load-generator.yaml

stop-load:
	kubectl delete -f k8s/load-generator.yaml --ignore-not-found

teardown:
	kubectl delete namespace demo-mcp --ignore-not-found
