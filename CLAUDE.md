# General Rules: 

1. Never store any secrets as plaintext
2. Be as concise as you can with any documentation (ReadMe specifically). They should only contain the absolute bare minimum. 
3. Never use any emojis ever 
4. Keep any code written or artifact created as simple as possible. If there's an easy way to do something take that first and we'll deal with any scaling later 
5. Import as little dependencies as you can. If there's a small utility that an import brings in that could be handled as a helper functions please just do that. 
6. Guiding principals - keep it simple, get something working fast, but consider best practices. Try and balance the complexity and getting running quick

### Claude: 
1. Uses the cheapest model when applicable this is a sandbox (claude-haiku)


### Kubernetes: 
1. Always create a new isolated namespace for this work. All resources that are applicable are to be stored in this namespace
2. This is a sandbox. Always keep replicas = 1 when applicable 
3. Always store secrets as kubernetes secrets 
4. Always pull from the local registry
5. Always pull a new image with a deployment this is a sandbox
6. Externalize all configuration changes to a ConfigMap. Environment variables, mounts, anything that's applicable


### Docker
1. If possible lets bake in multi-architecture images from the start so we can run on ARM and Intel Chips 
2. Mulitstage builds to compress image changes would be nice 

### Python: 
1. Always use UV for dependency mapping 
2. Always separate API layer from the business logic. For example the app.py should handle routes that import functions that do the heavy lifting. 
3. Find instances to consolidate functions and helper functions into different modules to be organized by function or use-case to organize them into modules


### Java 
1. As little boilerplate as humanly possible please 
2. Keep it simple as possible


### Git: 
1. Always ask for a review prior to a Git push


### Testing:
Not super important here it's just a demo sandbox

### Datadog:
1. Before making any Datadog MCP calls, check if `.claude/snapshot.md` exists and read it. If it does, use the cached data from that file instead of querying the MCP API.
2. Only call the Datadog MCP tools if the snapshot does not exist or the user explicitly asks to refresh with `--refresh`.