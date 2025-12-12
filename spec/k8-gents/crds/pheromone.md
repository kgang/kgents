# Pheromone CRD Specification

**AGENTESE Handle**: `void.pheromone`
**Affordances**: `sense`, `emit`, `witness`

## Purpose

Pheromones are stigmergic signals for indirect agent coordination.
They decay over time using **Passive Stigmergy** - intensity is calculated on read, not stored in status.

This prevents etcd write storms and aligns with the principle: "The noun is a lie. There is only the rate of change."

## Schema

### spec

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `type` | enum | Yes | - | Signal type (see Pheromone Types below) |
| `emittedAt` | datetime | No | creationTimestamp | ISO8601 timestamp of emission |
| `initialIntensity` | float | No | 1.0 | Starting intensity (0.0-1.0) |
| `halfLifeMinutes` | float | No | 10 | Time in minutes for intensity to halve |
| `source` | string | Yes | - | Emitting agent name |
| `target` | string | No | - | Target agent (broadcast if omitted) |
| `payload` | string | No | - | JSON payload data |
| `position` | object | No | - | Semantic space coordinates {x, y, z} |
| `ttl_seconds` | integer | No | - | Hard TTL override |

### Pheromone Types

| Type | Emitter | Purpose |
|------|---------|---------|
| `METAPHOR` | Psi-gent | Conceptual bridges |
| `WARNING` | F/J-gent | Danger signals |
| `MEMORY` | M-gent | Recall triggers |
| `NARRATIVE` | N-gent | Story threads |
| `OPPORTUNITY` | B-gent | Economic openings |
| `SCARCITY` | B-gent | Resource constraints |
| `CAPABILITY` | L-gent | New abilities |
| `STATE` | D-gent | Persistence events |
| `TEST` | Test harness | Testing signals |
| `INTENT` | F-gent | Action declarations |
| `DREAM` | Dreamer | Accursed share (creative tangents) |
| `CHAOS` | Void service | Resilience testing |

### status

**CRITICAL**: No `current_intensity` field. Intensity is calculated on read.

| Field | Type | Description |
|-------|------|-------------|
| `phase` | enum | ACTIVE, EVAPORATING, EVAPORATED |
| `sensed_by` | array | Agents that have sensed this pheromone |

## Behavior

### Decay Function (Passive Stigmergy)

The intensity at time `t` is calculated as:

```
intensity(t) = initialIntensity * (0.5 ^ ((t - emittedAt) / halfLifeMinutes))
```

For DREAM pheromones, `halfLifeMinutes` is multiplied by 2 (the accursed share persists).

### Garbage Collection

The operator runs every 5 minutes (not every minute) and:
1. Calculates current intensity using the decay function
2. DELETEs pheromones where `intensity(now) < 0.01` (1% threshold)
3. NEVER updates `status.current_intensity`

This is **Passive Stigmergy**: the operator only cleans up, never updates state.

### CHAOS Pheromones

CHAOS type pheromones trigger resilience testing:

```yaml
spec:
  type: CHAOS
  payload: |
    {"action": "terminate_random_pod", "namespace": "kgents-agents"}
```

Supported actions:
- `terminate_random_pod`: Kill a random kgents pod
- `network_partition`: (Future) Create network chaos
- `resource_pressure`: (Future) Inject resource constraints

## Example

```yaml
apiVersion: kgents.io/v1
kind: Pheromone
metadata:
  name: attention-signal
  namespace: kgents-agents
spec:
  type: ATTENTION
  emittedAt: "2025-12-11T10:00:00Z"
  initialIntensity: 1.0
  halfLifeMinutes: 10
  source: agent-alpha
  target: agent-beta
  payload: |
    {"context": "high-priority task", "reference": "task-123"}
```

After 10 minutes, `intensity` ≈ 0.5.
After 20 minutes, `intensity` ≈ 0.25.
After ~67 minutes, `intensity` < 0.01 → garbage collected.

## AGENTESE Integration

| Aspect | K8s Operation | Description |
|--------|---------------|-------------|
| `sense` | GET + calculate | List pheromones with calculated intensity |
| `emit` | CREATE | Emit a new pheromone |
| `witness` | GET events | View pheromone history |

## Implementation Trace

| Spec Section | Implementation File | Status |
|--------------|---------------------|--------|
| Schema | `impl/claude/infra/k8s/crds/pheromone-crd.yaml` | Aligned |
| Decay Function | `impl/claude/infra/k8s/operators/pheromone_operator.py:calculate_intensity` | Aligned |
| GC | `impl/claude/infra/k8s/operators/pheromone_operator.py:garbage_collect_pheromones` | Aligned |
| MCP Resource | `impl/claude/protocols/cli/mcp/resources.py:_read_pheromones` | Aligned |
| LogosResolver | `impl/claude/infra/cortex/logos_resolver.py:_invoke_sense` | Aligned |
