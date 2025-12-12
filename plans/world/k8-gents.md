# K8-gents: world.cluster.* Implementation

> *"The cluster is not a computer; it is a body. The K8-gent is not a script; it is a cell."*

**AGENTESE Context**: `world.cluster.*`
**Status**: Phase 0-1 Complete, Phase 2+ Planned
**Principles**: Tasteful, Spec-Driven Infrastructure, Graceful Degradation

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Reject Dapr** | K8s Operator IS the actor runtime. Keep stack hollow. |
| **Five separate CRDs** | Agent, Pheromone, Memory, Umwelt, Proposal—independent lifecycles |
| **kopf for operators** | Python-native, production-ready |
| **Three-layer fallback** | gRPC → Ghost → kubectl. Never blind. |
| **Cognitive Probes** | LLM health ≠ HTTP 200. Check semantic output. |
| **Half-life decay** | Pheromones decay exponentially, not linearly |

---

## The Bi-Cameral Architecture

### Left Brain: K8s Control Plane
- Deterministic, fast, rule-based
- API Server, etcd, Controllers, Webhooks
- Go/Rust/Python (`kopf`)
- Keeps the "Body" alive

### Right Brain: The Symbionts
- Probabilistic, creative, slow
- LLM Agents, Vector Stores, Pheromones
- Python (L-gents, K-gents)
- Solves problems, dreams

### The Bridge: Cortex Daemon
- Translates Left Brain constraints → Right Brain prompts
- Translates Right Brain desires → Left Brain specs

---

## CRDs (✅ DONE)

All five CRDs are implemented:

| CRD | Path | Size | Purpose |
|-----|------|------|---------|
| Agent | `infra/k8s/crds/agent-crd.yaml` | 11KB | Agent lifecycle |
| Pheromone | `infra/k8s/crds/pheromone-crd.yaml` | 4.6KB | Stigmergic signals |
| Memory | `infra/k8s/crds/memory-crd.yaml` | 5KB | D-gent state |
| Umwelt | `infra/k8s/crds/umwelt-crd.yaml` | 6.3KB | Observer context |
| Proposal | `infra/k8s/crds/proposal-crd.yaml` | 13.7KB | Safe autopoiesis |

---

## Operators (📋 PLANNED)

### AgentOperator

```yaml
apiVersion: kgents.io/v1
kind: Agent
metadata:
  name: b-gent
spec:
  genus: B
  reconciliation:
    sequential: true      # Controller ensures one-at-a-time
    idempotent: true      # Safe to retry
```

**Deliverables**:
- `infra/k8s/operators/agent_operator.py`
- Auto-inject D-gent/K-gent sidecars
- Cognitive probe health checks

### ProposalOperator

**Risk Calculation**:
- Base risk = change magnitude
- Velocity penalty = proposals per hour
- Cumulative penalty = 24h change volume

**T-gent Integration**:
- Medium risk → Emit `REVIEW_REQUEST` pheromone
- High risk → T-gent webhook blocks
- Low risk → Auto-merge

---

## Ghost Protocol (✅ DONE)

Three-layer fallback for CLI resilience:

```
Layer 1: gRPC (500ms timeout)
    ↓ (fail)
Layer 2: Ghost cache (~/.kgents/ghost/)
    ↓ (miss)
Layer 3: Direct kubectl
    ↓ (fail)
Show helpful "kgents infra init" message
```

Ghost cache structure:
```
~/.kgents/ghost/
├── agents/
│   └── _index.json
├── pheromones/
│   ├── active.json
│   └── by_type/
├── proposals/
│   ├── pending.json
│   └── rejected.json
├── cluster/
│   └── status.json
└── _meta/
    └── stability_score.json
```

---

## T-gent Webhook (📋 PLANNED)

ValidatingAdmissionWebhook for proposals:

```
kubectl apply / Proposal CR
       ↓
   K8s API Server
       ↓ (calls webhook)
┌─────────────────────────────────┐
│ T-GENT WEBHOOK                  │
│  ┌──────────┐  ┌──────────────┐ │
│  │FAST PATH │  │ SLOW PATH    │ │
│  │ CEL/Rego │  │ LLM Query    │ │
│  └────┬─────┘  └──────┬───────┘ │
│       ↓               ↓         │
│    ALLOW/DENY    ALLOW/DENY     │
└─────────────────────────────────┘
```

---

## Terrarium TUI (🚧 IN PROGRESS)

Visual interface for the hive mind:

```
┌──────────────────────────────────────────────────────────┐
│ TERRARIUM                                   [Live] 12:34 │
├──────────────────────────┬───────────────────────────────┤
│ AGENTS (by activity)     │ PHEROMONE HEATMAP             │
│ ▶ B-gent  ████░░ [busy]  │     ██▓▒░ WARNING ░▒▓██      │
│   L-gent  ██████ [idle]  │        ▒▒ DREAM ▒▒           │
├──────────────────────────┴───────────────────────────────┤
│ PROPOSALS                                                │
│ PENDING   b-gent-scale    Risk: ▒░ 0.25  "High load"    │
├──────────────────────────────────────────────────────────┤
│ THOUGHT STREAM (N-gent)                                  │
│ 12:34:52 [B-gent] Processing invoice batch (47 items)   │
└──────────────────────────────────────────────────────────┘
```

---

## AGENTESE Path Registry

| CLI Command | AGENTESE Path | K8s Operation |
|-------------|---------------|---------------|
| `kgents status` | `world.cluster.agents.manifest` | `kubectl get agents` |
| `kgents observe` | `void.pheromone.sense` | Watch Pheromone CRs |
| `kgents propose` | `self.deployment.define` | Create Proposal CR |
| `kgents tether` | `world.cluster.agents.<agent>.tether` | Port-forward |
| `kgents seance` | `time.witness.<agent>.replay` | Reconstruct history |
| `kgents workflow` | `world.cluster.workflow.define` | Durable Workflow |

---

## Implementation Phases

### Phase 0: The "Hollow" Body (✅ DONE)
- [x] Base CRDs
- [x] Cortex daemon + gRPC
- [x] Basic Terrarium TUI structure

### Phase 1: The Nervous System (🚧 IN PROGRESS)
- [x] Ghost Protocol
- [ ] Symbiont Injector (D-gent/K-gent sidecars)
- [ ] Logos Resolver enhancement
- [ ] Cognitive Probes

### Phase 2: The Mind (📋 PLANNED)
- [ ] Proposal Operator
- [ ] T-gent Webhook
- [ ] Durable Workflow (CRD state machine)
- [ ] Dream Cycle Operator

### Phase 3: The Interface (📋 PLANNED)
- [ ] Visual Stigmergy (pheromone heatmap)
- [ ] Seance Mode (time-travel debugging)
- [ ] MCP Server integration
- [ ] `kgents workflow` CLI

---

## Operationalization Phases (2025-12-11)

> *K8s infrastructure first, LLM integration second.*

### Phase A: Cluster Setup (✅ DONE)

| Deliverable | Path | Status |
|-------------|------|--------|
| Setup script | `infra/k8s/scripts/setup-cluster.sh` | ✅ |
| Verify script | `infra/k8s/scripts/verify-cluster.sh` | ✅ |
| Teardown script | `infra/k8s/scripts/teardown-cluster.sh` | ✅ |

**Commands**:
```bash
./impl/claude/infra/k8s/scripts/setup-cluster.sh
./impl/claude/infra/k8s/scripts/verify-cluster.sh
```

### Phase B: Operator Deployment (✅ DONE)

Single pod with all 3 operators (kopf handles multiplexing).

| Deliverable | Path | Status |
|-------------|------|--------|
| Dockerfile | `infra/k8s/operators/Dockerfile` | ✅ |
| Deployment manifest | `infra/k8s/manifests/operators-deployment.yaml` | ✅ |
| Deploy script | `infra/k8s/scripts/deploy-operators.sh` | ✅ |

**Operators** (already implemented):
- `agent_operator.py` (700 lines) - Reconciles Agent → Deployment + Service
- `pheromone_operator.py` (348 lines) - Decay loop (60s interval)
- `proposal_operator.py` (795 lines) - Risk calculation + T-gent pheromone

### Phase C: L-gent Containerization (📋 PLANNED)

L-gent is pure Python library. Needs HTTP server wrapper.

| Deliverable | Path | Status |
|-------------|------|--------|
| HTTP server | `agents/l/server.py` | 📋 |
| Dockerfile | `agents/l/Dockerfile` | 📋 |
| Build script | `agents/l/scripts/build.sh` | 📋 |

**Endpoints**:
- `GET /health` - Liveness
- `GET /ready` - Readiness
- `POST /search` - Semantic search
- `POST /register` - Register artifact

### Phase D: L-gent Cluster Deploy (📋 PLANNED)

| Deliverable | Path | Status |
|-------------|------|--------|
| PostgreSQL | `infra/k8s/manifests/l-gent-postgres.yaml` | ✅ (exists) |
| L-gent deployment | `infra/k8s/manifests/l-gent-deployment.yaml` | 🚧 (placeholder) |
| Agent CR | `infra/k8s/manifests/l-gent-agent-cr.yaml` | 📋 |
| Deploy script | `infra/k8s/scripts/deploy-lgent.sh` | 📋 |
| Verify script | `infra/k8s/scripts/verify-lgent.sh` | 📋 |

### Phase E: MCP Resources (✅ COMPLETE)

Expose K8s as MCP resources:
```
kgents://agents           -> List Agent CRs
kgents://agents/{name}    -> Agent status
kgents://pheromones       -> Active pheromones
kgents://cluster/status   -> Cluster health
```

| Deliverable | Path | Status |
|-------------|------|--------|
| Resource provider | `protocols/cli/mcp/resources.py` | ✅ |
| MCP server update | `protocols/cli/mcp/server.py` | ✅ |
| Tests | `protocols/cli/mcp/_tests/test_resources.py` | ✅ (16 tests) |

### Phase F: LLM Integration (✅ COMPLETE)

Wire `ClaudeCLIRuntime` into Cortex for LLM-backed AGENTESE paths.

| Deliverable | Path | Status |
|-------------|------|--------|
| Cognitive probes | `infra/cortex/probes.py` | ✅ |
| Cortex LLM wire | `infra/cortex/service.py` | ✅ |
| Path agents | `infra/cortex/agents/` | ✅ |
| Tests | `infra/cortex/_tests/test_probes.py` | ✅ (19 tests) |

**Components implemented**:
- `CognitiveProbe` - Basic LLM health check (echo test)
- `ReasoningProbe` - Deeper cognitive validation (arithmetic)
- `PathProbe` - AGENTESE path resolution validation
- `DefineAgent` - concept.define path handler
- `BlendAgent` - concept.blend.forge path handler
- `CriticAgent` - concept.refine path handler

**Usage**:
```python
# Create servicer with LLM runtime
servicer = create_cortex_servicer(use_cli_runtime=True)

# Run cognitive probe
result = await servicer._run_cognitive_probe()

# Invoke LLM-backed path
result = await servicer.Invoke(request)  # path="concept.define"
```

**Existing runtime** (`impl/claude/runtime/`):
- `ClaudeCLIRuntime` - Uses `claude -p` (OAuth, no API key)
- `ClaudeRuntime` - Direct Anthropic API
- `OpenRouterRuntime` - Multi-model gateway

---

## NOT Doing (Yet)

| Feature | Why Deferred | Revisit When |
|---------|--------------|--------------|
| Agent Mesh (sidecar proxy) | Overkill for <10 agents | >10 agents |
| SpinKube/Wasm | Immature | Production scale |
| Federated Discovery | Single-cluster first | Multi-cluster |
| Custom K8s Scheduler | Pod Priority sufficient | >100 agents |

---

## Cross-References

- **Spec**: `spec/k8-gents/README.md`
- **Plans**: `self/cli.md` (Ghost Protocol), `void/capital.md` (Trust Gate)
- **Impl**: `infra/k8s/crds/`, `infra/k8s/tether.py`, `infra/cortex/`

---

*"Do not over-engineer the network layer. Focus on the interface. Make it beautiful."*
