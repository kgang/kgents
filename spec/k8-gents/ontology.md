# K8-Gents Ontology Specification

**AGENTESE Handle**: `world.cluster.logos`

## Overview

The K8-Gents ontology maps Kubernetes nouns to AGENTESE verbs. This is the heart of the K8-Terrarium architecture: instead of querying resources directly, agents grasp **handles** that yield **affordances** based on who is grasping.

```
Traditional: kubectl get pods → JSON object
AGENTESE:    world.cluster.workload.manifest → Handle[Observer, Interaction]
```

## The Five Contexts

| Context | K8s Domain | Purpose |
|---------|------------|---------|
| `world.*` | External resources | Pods, Deployments, Services |
| `self.*` | Agent-owned resources | Secrets, ConfigMaps, Memory CRs |
| `concept.*` | Abstract definitions | (Not K8s - pure AGENTESE) |
| `void.*` | Entropy, pheromones | Chaos injection, stigmergy |
| `time.*` | Events, traces | History, logs, auditing |

## Ontology Map

### world.cluster.* (External)

| AGENTESE Path | K8s Kind | Affordances |
|---------------|----------|-------------|
| `world.cluster.workload` | Pod | manifest, witness, terminate |
| `world.cluster.deployment` | Deployment | manifest, scale, rollback |
| `world.cluster.agent` | Agent CR | manifest, scale, terminate, tether |

### void.* (Entropy)

| AGENTESE Path | K8s Kind | Affordances |
|---------------|----------|-------------|
| `void.pheromone` | Pheromone CR | sense, emit, witness |

### self.* (Agent-Owned)

| AGENTESE Path | K8s Kind | Affordances |
|---------------|----------|-------------|
| `self.memory.store` | Memory CR | manifest, define, compost |
| `self.governance.proposal` | Proposal CR | define, approve, reject, witness |
| `self.umwelt` | Umwelt CR | manifest, refine |
| `self.memory.secret` | Secret | manifest, define |
| `self.memory.config` | ConfigMap | manifest, define, refine |

### time.* (Temporal)

| AGENTESE Path | K8s Kind | Affordances |
|---------------|----------|-------------|
| `time.trace.witness` | Event | witness |

## Affordances

Affordances are verbs that a handle permits based on observer identity:

| Affordance | Meaning | Example |
|------------|---------|---------|
| `manifest` | Observe current state | Get pod spec |
| `witness` | Observe history | Get pod logs, events |
| `terminate` | End lifecycle | Delete pod |
| `scale` | Change replicas | Scale deployment |
| `rollback` | Revert changes | Rollback deployment |
| `sense` | Perceive pheromones | List active signals |
| `emit` | Create pheromone | Broadcast signal |
| `define` | Create new entity | Create Memory CR |
| `refine` | Modify entity | Update ConfigMap |
| `compost` | Archive/delete | Delete old memories |
| `approve` | Approve proposal | Governance workflow |
| `reject` | Reject proposal | Governance workflow |
| `tether` | Bind agent | Connect to resource |

## Observer Filtering

Different observers get different affordances for the same handle:

```python
# Architect observer - full access
architect_umwelt = Umwelt(affordance_patterns=["*"])
handle = await resolver.resolve("world.cluster.agent.my-agent", architect_umwelt)
# handle.can("terminate") → True

# Reader observer - limited access
reader_umwelt = Umwelt(affordance_patterns=["manifest", "witness"])
handle = await resolver.resolve("world.cluster.agent.my-agent", reader_umwelt)
# handle.can("terminate") → False
```

## Path Syntax

AGENTESE paths follow the pattern:

```
<context>.<entity>[.<name>][.<aspect>]
```

Examples:
- `world.cluster.agent` → Handle to all agents
- `world.cluster.agent.my-agent` → Handle to specific agent
- `world.cluster.agent.my-agent.manifest` → Invoke manifest aspect
- `void.pheromone.sense` → Sense all pheromones

## Implementation Trace

| Spec Section | Implementation File | Status |
|--------------|---------------------|--------|
| Ontology Map | `impl/claude/infra/cortex/logos_resolver.py:ONTOLOGY_MAP` | Aligned |
| Path Parsing | `impl/claude/infra/cortex/logos_resolver.py:parse_path` | Aligned |
| Affordance Filtering | `impl/claude/infra/cortex/logos_resolver.py:_filter_affordances` | Aligned |
