IMAGE = demo-api:latest

.PHONY: deploy load stop-load teardown

deploy:
	docker build -t $(IMAGE) demo-api/
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/
	kubectl apply -f k8s/load-generator.yaml
	kubectl rollout restart deployment -n demo-mcp

load:
	kubectl apply -f k8s/load-generator.yaml

stop-load:
	kubectl delete -f k8s/load-generator.yaml --ignore-not-found

teardown:
	kubectl delete namespace demo-mcp --ignore-not-found
