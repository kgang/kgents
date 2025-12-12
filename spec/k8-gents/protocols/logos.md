# Logos Protocol Specification

**AGENTESE Handle**: `world.cluster.logos`

## Overview

The Logos Protocol defines how AGENTESE paths are resolved to Kubernetes API operations. It is a **stateless translation layer** that maps semantic paths to concrete K8s calls while respecting observer permissions.

## Architecture

K8-Terrarium v2.0 Architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CortexServicer                           │
│  ┌─────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │ GetStatus   │    │    Invoke    │    │ StreamDreams     │   │
│  └─────────────┘    └──────┬───────┘    └──────────────────┘   │
│                            │                                    │
│                   ┌────────┴────────┐                          │
│                   │ is K8s path?    │                          │
│                   └────────┬────────┘                          │
│                     yes    │    no                             │
│                   ┌────────┴────────┐                          │
│                   ▼                 ▼                          │
│           ┌──────────────┐   ┌─────────────┐                   │
│           │ LogosResolver│   │ Logos       │                   │
│           │ (stateless)  │   │ (AGENTESE)  │                   │
│           └──────┬───────┘   └─────────────┘                   │
│                  │                                              │
└──────────────────┼──────────────────────────────────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │  kubectl CLI   │
          │  (K8s API)     │
          └────────────────┘
```

The **LogosResolver** is a thin (~200 line) translation layer, not a God Object. It:
1. Parses AGENTESE paths
2. Looks up K8s resource mapping
3. Filters affordances by observer
4. Translates aspect to K8s operation
5. Returns result

## Path Resolution

AGENTESE paths resolve to K8s operations via the ontology map:

```
world.cluster.agent.my-agent.manifest
  │       │       │        │       │
  │       │       │        │       └── Aspect: kubectl get
  │       │       │        └── Name: filter by name
  │       │       └── Entity: agents.kgents.io
  │       └── Context prefix
  └── Context: world (external)
```

### Resolution Algorithm

```python
def resolve(path: str, observer: Umwelt) -> Handle:
    # 1. Parse path
    context, entity, name, aspect = parse_path(path)

    # 2. Lookup in ontology
    resource = ONTOLOGY_MAP[(context, entity)]

    # 3. Filter affordances by observer
    affordances = filter_by_observer(resource.affordances, observer)

    # 4. Return handle
    return Handle(resource, affordances, name)
```

## Handle and Invocation

A **Handle** is not the resource itself - it's a morphism that maps Observer → Interaction:

```python
# Different observers, different capabilities
handle = await resolver.resolve("world.cluster.agent.my-agent", admin)
# handle.affordances = ["manifest", "scale", "terminate", "tether"]

handle = await resolver.resolve("world.cluster.agent.my-agent", reader)
# handle.affordances = ["manifest", "witness"]
```

Invocation translates aspects to K8s operations:

| Aspect | K8s Operation |
|--------|---------------|
| `manifest` | `kubectl get <resource> -o json` |
| `witness` | `kubectl logs` or `kubectl get events` |
| `terminate` | `kubectl delete` |
| `scale` | `kubectl scale --replicas=N` |
| `sense` | `kubectl get pheromones` + calculate intensity |
| `emit` | `kubectl apply -f pheromone.yaml` |

## K8s Path Detection

Paths delegated to LogosResolver:

```python
K8S_PREFIXES = (
    "world.cluster.",      # Pods, Deployments, Agents
    "void.pheromone",      # Pheromone CRDs
    "self.memory.secret",  # K8s Secrets
    "self.memory.config",  # K8s ConfigMaps
    "time.trace.",         # K8s Events
)
```

All other paths use the standard AGENTESE Logos resolver.

## Pheromone Sensing

Pheromone `sense` aspect implements Passive Stigmergy:

```python
async def _invoke_sense(self, handle: Handle) -> dict:
    # 1. Get pheromone CRs
    manifest = await kubectl_get_pheromones()

    # 2. Calculate intensity on read (Passive Stigmergy)
    for item in manifest["items"]:
        spec = item["spec"]
        item["calculated_intensity"] = calculate_intensity(spec)

    return manifest
```

## Error Handling

| Error | Response |
|-------|----------|
| Unknown path | `{"error": "Unknown AGENTESE entity: ..."}` |
| Permission denied | `{"error": "Handle does not afford 'terminate'"}` |
| K8s error | `{"error": "<kubectl stderr>"}` |

## Security

The LogosResolver respects observer permissions through:

1. **SPIFFE ID**: Observer identity from Umwelt
2. **Affordance Patterns**: Glob patterns like `["manifest", "witness.*"]`
3. **K8s RBAC**: Underlying kubectl respects K8s permissions

## Implementation Trace

| Spec Section | Implementation File | Status |
|--------------|---------------------|--------|
| LogosResolver | `impl/claude/infra/cortex/logos_resolver.py` | Aligned |
| K8s Path Detection | `impl/claude/infra/cortex/service.py:_is_k8s_path` | Aligned |
| CortexServicer Integration | `impl/claude/infra/cortex/service.py:_invoke_k8s_path` | Aligned |
