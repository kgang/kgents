# K8-gents: Kubernetes as Agent Substrate

> *"The cluster is not a computer; it is a body. The K8-gent is not a script; it is a cell."*

**Version**: 4.0 (First Principles Consolidation)

K8-gents recognizes that Kubernetes primitives ARE agent primitives. This is not "agents on K8s" but "K8s IS agents"—a structural isomorphism at the category-theoretic level.

---

## Core Thesis: The Puppet Swap

Kubernetes is an **isomorphic puppet** (see `spec/principles.md`) that makes agent lifecycle tractable:

| Agent Concept | K8s Primitive | Why It Works |
|---------------|---------------|--------------|
| Reconciliation Loop | Controller | Both are perception-action cycles |
| Eventual Consistency | etcd | Both reject single source of truth |
| Domain Object | CRD | Watchable, validatable, declarative |
| Composition | Service Mesh | Network calls preserve morphism laws |

**Ontological Fit** (not convenience):
1. Controllers = Agent perception-action cycles
2. Eventual Consistency = Heterarchical coordination
3. CRDs = First-class domain objects (Pheromones, Memories)
4. Namespaces = Agent umwelts (bounded perception)
5. etcd = Distributed memory

---

## The Five CRDs

**Tasteful Constraint**: Exactly five CRDs. No sprawl.

| CRD | Purpose | Maps To |
|-----|---------|---------|
| **Agent** | Agent definition | Deployment + Service + NetworkPolicy |
| **Pheromone** | Stigmergic signal | Decaying CRD (watched, ephemeral) |
| **Memory** | Persistent state | PVC + retention policy |
| **Umwelt** | Observer context | ConfigMap + Secret + affordances |
| **Proposal** | Safe self-modification | Dry-run patch + trust gates |

---

## Agent Anatomy: The Symbiont Pod

```
┌─────────────────────────────────────────────────────────────────┐
│                       AGENT POD                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │     Logic       │  │     Memory      │  │    Identity     │  │
│  │   (Container)   │  │   (Sidecar)     │  │   (Sidecar)     │  │
│  │                 │  │                 │  │                 │  │
│  │  Python + LLM   │  │  D-gent         │  │  SPIFFE         │  │
│  │  Agent logic    │  │  PVC mount      │  │  SVID           │  │
│  │  Stateless      │  │  State          │  │  mTLS           │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Spec (ConfigMap)                          ││
│  │           Agent reads its own spec to know what it is        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

**Symbiont Pattern**: Logic is stateless, D-gent holds state. Logic can crash and restart; memory persists.

---

## Categorical Foundation

Agents must satisfy composition laws (verified by BootstrapWitness):

```
Identity:      Id >> f ≡ f ≡ f >> Id
Associativity: (f >> g) >> h ≡ f >> (g >> h)
```

### Distributed Composition

Network composition is associative **if operations are idempotent**.

```python
@dataclass
class DistributedResult(Generic[T]):
    value: T | None
    error: DistributedError | None
    trace_id: str  # Correlation across network boundary

class DistributedAgent(Generic[A, B]):
    async def invoke(self, input: A) -> DistributedResult[B]: ...
    def __rshift__(self, other: DistributedAgent[B, C]) -> DistributedAgent[A, C]: ...
```

**Requirement**: Distributed agents MUST be idempotent. The `@idempotent` decorator tracks invocation hashes and returns cached results for repeat calls.

---

## CRD Specifications

### Agent CRD

```yaml
apiVersion: kgents.io/v1
kind: Agent
metadata:
  name: b-gent
spec:
  genus: B
  image: kgents/b-gent:latest
  resources:
    cpu: 100m
    memory: 256Mi
  sidecar: true              # Include D-gent memory sidecar
  networkPolicy:
    allowedPeers: [L, F]     # Permission graph
  umwelt: b-gent-umwelt      # Reference to Umwelt CR
```

### Pheromone CRD

Stigmergic coordination via decaying signals.

```yaml
apiVersion: kgents.io/v1
kind: Pheromone
metadata:
  name: high-load-warning
spec:
  type: WARNING              # WARNING, MEMORY, INTENT, DREAM, etc.
  intensity: 0.8             # 0.0-1.0
  decay_rate: 0.1            # Per minute
  source: b-gent
  payload: "Request queue depth: 47"
  ttl_seconds: 600           # Hard TTL
```

**Key Behaviors**:
- Intensity decays over time (PheromoneOperator)
- DREAM pheromones decay at 50% rate (Accursed Share)
- Deleted when intensity ≤ 0 or TTL expires
- Agents sense pheromones via Umwelt filtering

### Memory CRD

```yaml
apiVersion: kgents.io/v1
kind: Memory
metadata:
  name: b-gent-memory
spec:
  owner: b-gent
  type: BICAMERAL            # Relational + vector
  size: 256Mi
  retention_policy: COMPOST  # Feed to Lethe on delete
```

### Umwelt CRD

Observer context—what the agent can perceive and do.

```yaml
apiVersion: kgents.io/v1
kind: Umwelt
metadata:
  name: b-gent-umwelt
spec:
  agent: b-gent
  affordances:
    - "world.token.budget.*"
    - "self.memory.*"
  constraints:
    token_budget: 10000
  pheromone_sensitivity:
    sense: [SCARCITY, WARNING]
    emit: [SCARCITY]
  slop_budget: 0.10          # 10% for exploration (Accursed Share)
  workload: routine          # routine | exploration | urgent
```

**Workload Classification** (simplified from Active Inference):
- `routine`: Normal priority, standard token budget
- `exploration`: Lower priority, higher token budget, more tangents allowed
- `urgent`: Higher priority, focused execution

### Proposal CRD

Safe autopoiesis via dry-run validation.

```yaml
apiVersion: kgents.io/v1
kind: Proposal
metadata:
  name: b-gent-scale-up
spec:
  target: Deployment/b-gent
  patch: |
    spec:
      replicas: 3
  reason: "High load detected. Request queue depth: 47"
  proposer: b-gent
  urgency: MEDIUM
status:
  phase: PASSED              # PENDING → VALIDATING → PASSED/FAILED → APPROVED/REJECTED → MERGED
  risk_score: 0.25
  validation_result: "Dry-run successful"
```

**Trust Gates**:
- risk < 0.3: Auto-merge
- risk 0.3-0.6: T-gent review (immune system)
- risk > 0.6: Human review required

---

## Operators

### PheromoneOperator

Decays intensity, garbage collects expired pheromones.

```python
@kopf.timer("pheromones.kgents.io", interval=60.0)
async def decay_pheromones(spec, status, patch, **_):
    new_intensity = status.current_intensity * (1 - spec.decay_rate)
    if spec.type == "DREAM":
        new_intensity = status.current_intensity * (1 - spec.decay_rate * 0.5)
    if new_intensity <= 0:
        await delete_pheromone(...)
    else:
        patch.status["current_intensity"] = new_intensity
```

### AgentOperator

Agent CR → Deployment + Service + NetworkPolicy + Memory CR (if sidecar=true)

### ProposalOperator

1. Validate via K8s dry-run
2. Calculate risk score
3. Auto-merge if low risk, queue for review otherwise

---

## Communication

### Telepathy (gRPC)

Agents communicate via gRPC. NetworkPolicy enforces the permission graph.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: b-gent-policy
spec:
  podSelector:
    matchLabels:
      agent: b-gent
  egress:
  - to:
    - podSelector:
        matchLabels:
          agent: l-gent
```

### Explicit Routing (Phase 1)

In Phase 1, routing is explicit:
```bash
kgents call b-gent --payload '{"action": "check_balance"}'
```

**Deferred**: Semantic routing (L-gent resolves "Who handles budgets?") deferred until >10 agents exist.

---

## AGENTESE Paths

K8-gent paths follow AGENTESE:
```
world.cluster.agents.manifest    # List running agents
self.pod.memory.load             # D-gent in-cluster operation
void.pheromone.sip               # Sense the field
time.trace.witness               # N-gent narrative
```

---

## Lifecycle: Spec → Running

**Generative Principle**: YAML is generated, not written.

```
spec/agents/*.md  →  spec_to_crd.py  →  Agent CR  →  Operator  →  Running Pod
```

```bash
kgents infra crd --apply          # Install CRDs
kgents infra apply b-gent         # Deploy from spec
kgents infra apply --all          # Deploy all agents
```

---

## Graceful Degradation

When cluster is unavailable:
- CLI shows cached state from `.kgents/ghost/`
- Commands that require cluster show actionable error
- Never silent failure

---

## Principle Alignment

| Principle | K8-gent Manifestation |
|-----------|----------------------|
| **Tasteful** | Five CRDs only. No sprawl. |
| **Curated** | NetworkPolicy enforces relationships. No free-for-all. |
| **Ethical** | SPIFFE identity cannot be spoofed. Proposals require validation. |
| **Joy-Inducing** | DREAM pheromones. Slop budget. Terrarium TUI. |
| **Composable** | DistributedAgent preserves composition laws. |
| **Heterarchical** | No orchestrator. Any agent can propose. |
| **Generative** | YAML derived from spec. Can delete and regenerate. |
| **Graceful Degradation** | CLI works (degraded) when cluster down. |

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Hand-written YAML | Spec rot inevitable |
| Pheromones without decay | Breaks thermodynamics |
| Direct Deployment edits | Bypasses Proposal safety |
| Fixed orchestrator | Violates Heterarchical |
| CLI with business logic | Hollow CLI contract |

---

## Spec Structure

| Document | Focus |
|----------|-------|
| `README.md` | Core thesis, CRDs, anatomy (this document) |
| `02_evolution.md` | Self-modification (Proposal CRD, trust gates) |
| `03_interface.md` | Developer surface (Ghost, Tether, MCP) |

**Moved to research/**: 10-month horizon roadmap (speculative, not spec)

---

*"The well-designed system feels inevitable. The over-designed system feels fragile."*
