# K8-gents Implementation Plan v2.1

> *"The cluster is not a computer; it is a body. The K8-gent is not a script; it is a cell."*

**Status**: Active Implementation Plan (Refined)
**Date**: 2025-12-11
**Spec Source**: `spec/k8-gents/` (v4.0 First Principles Consolidation)
**Refinements**: Dapr rejection, Trust Gate with Capital Ledger, K8s-native actor model

---

## Critical Refinement (v2.1)

### Dapr Integration: REJECTED

**The original proposal** (plan-upgrade-proposal.md §5.1) suggested adopting Dapr sidecars for actor semantics.

**The critique identified**: Adding Dapr introduces a massive dependency (sidecar injection, separate control plane) for a problem K8s can solve natively with a simple CRD controller loop.

**The decision**: **REJECT Dapr.** The K8s Operator IS the actor runtime. We do not need an actor runtime *on top of* our container orchestrator. Keep the stack hollow.

```yaml
# REJECTED pattern (Dapr integration):
# apiVersion: kgents.io/v1
# kind: Agent
# spec:
#   actor:
#     model: dapr  # NO - introduces bloat
#     stateStore: redis  # NO - we have D-gent

# APPROVED pattern (K8s-native):
apiVersion: kgents.io/v1
kind: Agent
metadata:
  name: b-gent
spec:
  genus: B
  reconciliation:
    sequential: true      # Controller ensures one-at-a-time
    idempotent: true      # Safe to retry
  # Durable execution via CRD state machine, not Dapr
```

**Principle violated by Dapr**: **Tasteful** (avoid kitchen-sink/bloat) & **Spec-Driven Infra**.

See `plans/lattice-refinement.md` for full rationale.

---

## The Core Pivot: From Category Theory to Durable Biology

**The Hard Truth**: You cannot guarantee `(f >> g) >> h ≡ f >> (g >> h)` over a network using standard RPC/REST. Network partitions, zombie processes, and side effects break associativity.

**The Enlightened Fix**: **Durable Execution** (workflow-as-code).

Instead of piping live agents (`A >> B`), we pipe **Promises of Completion**.

- **The Log is the Truth**: If Agent A finishes and Agent B dies, the system must know A *already happened*.
- **Reification**: The "Category" is not the agents themselves, but the **Workflow History**.

**Solution**: A **Durable Execution Engine** (Temporal or lightweight CRD-based state machine) inside the Cortex.

```python
# AGENTESE path for durable workflows
await logos.invoke("world.cluster.workflow.define", workflow=A >> B)
```

This guarantees exactly-once semantics, making Category Laws valid *eventually*.

---

## Part 0: The Bi-Cameral Architecture

We split the system into two hemispheres to resolve the tension between mathematical purity and biological substrate.

### Left Brain: The Rigid Structure (K8s Control Plane)

| Aspect | Description |
|--------|-------------|
| **Role** | Deterministic, fast, rule-based |
| **Components** | API Server, etcd, Controllers, Webhooks |
| **Language** | Go / Rust / Python (`kopf`) |
| **Responsibility** | Keeping the "Body" alive (Pod scheduling, Networking, PVCs) |

### Right Brain: The Fluid Cognition (The Symbionts)

| Aspect | Description |
|--------|-------------|
| **Role** | Probabilistic, creative, slow |
| **Components** | LLM Agents, Vector Stores, Pheromones |
| **Language** | Python (L-gents, K-gents) |
| **Responsibility** | Solving problems, autopoiesis, "Dreaming" |

### The Bridge: The Cortex Daemon (Logos)

The Cortex translates:
- Left Brain structural constraints → Right Brain prompts
- Right Brain desires (Proposals) → Left Brain specs

---

## Part I: Critical Analysis

### The Isomorphism Claim: Stress-Tested

| Agent Concept | K8s Primitive | Strength | Resolution |
|---------------|---------------|----------|------------|
| Reconciliation Loop | Controller | **Strong** | Both are perception-action cycles |
| Eventual Consistency | etcd | **Strong** | Both reject SSOT |
| Domain Object | CRD | **Strong** | Declarative, watchable |
| Composition | Service Mesh | **Weak** | **→ Durable Execution Engine** |
| Agent Memory | PVC | **Medium** | Add query semantics via D-gent |
| Agent Identity | SPIFFE | **Strong** | Cryptographic, attestable |

**The Weak Link Resolved**: Composition over network is handled by Durable Execution—not raw RPC. The workflow log becomes the source of truth for composition.

### The Five CRDs: Decision

Keep five separate CRDs (Agent, Pheromone, Memory, Umwelt, Proposal):
- Independent lifecycle (Umwelt can be shared across agents)
- Fine-grained RBAC (different permissions for Memory vs Agent)
- Looser coupling (agent restart doesn't affect memory)

### The Bootstrap Paradox: Three-Layer Fallback

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE GHOST PROTOCOL (ENHANCED)                             │
│                                                                              │
│   CLI invocation                                                            │
│        │                                                                     │
│        ▼                                                                     │
│   ┌─────────────────────────────────────┐                                   │
│   │ 1. Try gRPC (500ms timeout)         │                                   │
│   └──────────────┬──────────────────────┘                                   │
│                  │                                                           │
│         ┌───────┴───────┐                                                   │
│         │               │                                                    │
│         ▼               ▼                                                    │
│   ┌──────────┐   ┌──────────────────┐                                       │
│   │ SUCCESS  │   │ FAILURE          │                                       │
│   │ Update   │   │                  │                                       │
│   │ ghost +  │   │ 2. Read Ghost    │                                       │
│   │ return   │   │    cache         │                                       │
│   └──────────┘   └────────┬─────────┘                                       │
│                           │                                                  │
│                  ┌────────┴────────┐                                        │
│                  │                 │                                         │
│                  ▼                 ▼                                         │
│           ┌──────────┐     ┌──────────────┐                                 │
│           │ GHOST    │     │ NO GHOST     │                                 │
│           │ EXISTS   │     │              │                                 │
│           │          │     │ 3. kubectl   │                                 │
│           │ Show     │     │    fallback  │                                 │
│           │ [GHOST]  │     │    (direct)  │                                 │
│           └──────────┘     └──────┬───────┘                                 │
│                                   │                                          │
│                          ┌────────┴────────┐                                │
│                          │                 │                                 │
│                          ▼                 ▼                                 │
│                   ┌──────────┐     ┌──────────────┐                         │
│                   │ KUBECTL  │     │ NO CLUSTER   │                         │
│                   │ WORKS    │     │              │                         │
│                   │          │     │ Show helpful │                         │
│                   │ Seed     │     │ "kgents      │                         │
│                   │ ghost    │     │ infra init"  │                         │
│                   └──────────┘     └──────────────┘                         │
│                                                                              │
│   "Three fallback layers. Never blind."                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part II: Resolved Design Decisions

### 1. T-Gent: The Immune System as ValidatingAdmissionWebhook

**The Fix**: Make T-gent a **K8s Webhook** so it's part of the physics of the cluster—unbyppassable.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         T-GENT ADMISSION WEBHOOK                              │
│                                                                              │
│   kubectl apply / Proposal CR                                               │
│        │                                                                     │
│        ▼                                                                     │
│   K8s API Server                                                            │
│        │                                                                     │
│        ▼ (calls webhook)                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ T-GENT WEBHOOK                                                       │   │
│   │                                                                      │   │
│   │  ┌──────────────────┐    ┌──────────────────────────────────────┐   │   │
│   │  │ FAST PATH        │    │ SLOW PATH                            │   │   │
│   │  │ (Left Brain)     │    │ (Right Brain)                        │   │   │
│   │  │                  │    │                                      │   │   │
│   │  │ Rego/CEL Rules:  │    │ LLM Query:                           │   │   │
│   │  │ • No root access │    │ "Does this change violate the        │   │   │
│   │  │ • Resource limits│    │  Constitution?"                      │   │   │
│   │  │ • Namespace check│    │                                      │   │   │
│   │  └────────┬─────────┘    └─────────────┬────────────────────────┘   │   │
│   │           │                            │                             │   │
│   │           ▼                            ▼                             │   │
│   │       ALLOW/DENY                 ALLOW/DENY/ESCALATE                │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Result: Immune system cannot be bypassed. It's the law.                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**T-gent Decision Protocol** (from spec):
- Rules generated by agents themselves (see `impl/claude/bootstrap`)
- Appeal process deferred to v-gent (judge infrastructure)
- Multiple T-gent instances: consensus via y-gents spec

### 2. LLM Health: Cognitive Probes

An LLM is "unhealthy" if it returns HTTP 200 but outputs garbage.

```python
class CognitiveProbe:
    """
    Standard Cognitive Unit (SCU) - the basic health check.

    Zeroth-order approximation. Higher-order semantic checks
    delegated to H-gents and Psi-gents.
    """

    async def probe(self, agent: Agent) -> HealthStatus:
        # Simple structured output test
        prompt = "Output exactly: {'status': 'alive'}"
        response = await agent.invoke(prompt, timeout=5.0)

        try:
            data = json.loads(response)
            if data.get("status") == "alive":
                return HealthStatus.HEALTHY
        except (json.JSONDecodeError, KeyError):
            pass

        return HealthStatus.COGNITIVE_DEGRADATION

    def remediate(self, status: HealthStatus) -> Action:
        """
        Restarting won't fix a bad prompt.
        Degrade to Safemode rather than crash-loop.
        """
        if status == HealthStatus.COGNITIVE_DEGRADATION:
            return Action.DEGRADE_TO_SAFEMODE
        return Action.RESTART
```

**Graceful Heterarchies**: Higher-order semantic health checks handled by:
- L-gent: Coherence drift detection
- R-gent: Refinery quality checks
- T-gent: Alignment verification
- B-gent: "Busy thinking" vs "unhealthy" distinction

### 3. Pheromone Decay: Half-Life Model

Biology follows exponential decay, not linear.

```python
class PheromoneDecay:
    """
    The Half-Life Model (Radioactive Decay)

    Formula: Intensity(t) = Initial * (0.5)^(t / HalfLife)

    Why: High-signal warnings stay urgent, then drop off fast.
         Low-level dreams linger longer.
    """

    def decay(self, pheromone: Pheromone, elapsed: timedelta) -> float:
        half_life = self.get_half_life(pheromone.type)
        decay_factor = 0.5 ** (elapsed.total_seconds() / half_life.total_seconds())
        return pheromone.intensity * decay_factor

    def get_half_life(self, ptype: PheromoneType) -> timedelta:
        """Different types decay differently."""
        return {
            PheromoneType.WARNING: timedelta(minutes=5),    # Urgent, fast decay
            PheromoneType.SCARCITY: timedelta(minutes=15),  # Economic signals
            PheromoneType.DREAM: timedelta(hours=2),        # Dreams linger
            PheromoneType.REVIEW_REQUEST: timedelta(hours=1),
        }.get(ptype, timedelta(minutes=30))


class StigmergicMetabolism:
    """
    Agents don't just read pheromones—they metabolize them.

    Reading a "Task" pheromone slightly reduces its intensity,
    implementing distributed locking via biology.
    """

    def sense_and_metabolize(
        self,
        agent: Agent,
        pheromone: Pheromone,
        metabolism_rate: float = 0.05
    ) -> Pheromone:
        # Agent "claims" part of the pheromone
        pheromone.intensity *= (1 - metabolism_rate)
        return pheromone
```

### 4. Ghost Staleness: Adaptive Thresholds

```python
class AdaptiveStaleness:
    """
    Staleness adapts to cluster stability.
    Follow 80/20 principle: simple rules, big impact.
    """

    BASE_THRESHOLDS = {
        "agents": timedelta(minutes=1),
        "pheromones": timedelta(seconds=30),
        "proposals": timedelta(minutes=5),
        "cluster": timedelta(minutes=2),
    }

    def check(self, category: str, age: timedelta, stability: float) -> StalenessLevel:
        # Stable clusters can tolerate older data
        threshold = self.BASE_THRESHOLDS[category] * (1 + stability)

        if age < threshold:
            return StalenessLevel.FRESH
        elif age < threshold * 2:
            return StalenessLevel.STALE  # Show [GHOST] prefix
        else:
            return StalenessLevel.REFUSE  # Do not show misleading data
```

**UX Decision**: "Very stale" data is **refused**, not shown with warnings.

### 5. Cortex Daemon Lifecycle: Local Cluster First

```bash
# Daemon starts automatically on first CLI use (like Docker)
kgents status  # → Checks for daemon, starts if missing

# Or explicit control
kgents daemon start    # Hot-reload capable
kgents daemon stop
kgents daemon status
```

**Platform**: Mac-focused development. Uses launchd for persistence.
**Hot Reload**: Daemon supports hot reload with fallback/failover.

### 6. MCP Security: Track Human Users

```python
@server.tool("kgents_propose")
async def propose(target: str, patch: dict, reason: str, ctx: MCPContext) -> ProposalResult:
    proposal = Proposal(
        target=target,
        patch=patch,
        reason=reason,
        proposer=f"claude-code:{ctx.user_identity}",  # Track human, not just tool
    )
    return await proposal_service.create(proposal)
```

Human identity tracked via K-gent integration.

### 7. AGENTESE Path Ambiguity: Embrace It

Path collisions (e.g., agent named `manifest`) are disambiguated contextually:
- J-gent: JSON-based contextual disambiguation
- Z-gent: Surface ambiguity to user (see spec)
- Ghost Protocol: CLI-level resolution

**Philosophy**: Ambiguity should be **embraced and leveraged**, not eliminated.

---

## Part III: The Foundation (CRDs + Operators)

### 3.1 Agent CRD + AgentOperator

**Goal**: Agent CR → Deployment + Service + NetworkPolicy + Memory CR

```yaml
apiVersion: kgents.io/v1
kind: Agent
metadata:
  name: b-gent
spec:
  genus: B
  image: kgents/b-gent:latest
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi

  symbiont:
    memory:
      enabled: true
      type: BICAMERAL
      size: 256Mi
      retentionPolicy: COMPOST
    identity:
      enabled: true
      spiffeId: spiffe://kgents.io/agents/b-gent

  health:
    type: COGNITIVE_PROBE  # Uses SCU, not HTTP liveness
    probeInterval: 30s
    unhealthyThreshold: 3
    degradeToSafemode: true

  networkPolicy:
    allowedPeers: [L, F]
    allowEgress: false

  umwelt: b-gent-umwelt
```

**Files**:
```
impl/claude/infra/k8s/crds/agent-crd.yaml
impl/claude/infra/k8s/operators/agent_operator.py  # Use kopf
impl/claude/infra/k8s/operators/_tests/test_agent_operator.py
```

### 3.2 Proposal CRD + ProposalOperator (Safe Autopoiesis)

**Cumulative Risk Tracking**:

```python
class ProposalRiskCalculator:
    """
    Risk = change magnitude + velocity penalty + cumulative penalty.

    An agent making 10 small changes/hour is suspicious.
    """

    def calculate_risk(
        self,
        current: Resource,
        proposed: Resource,
        history: list[Proposal],
    ) -> float:
        base_risk = self._change_magnitude_risk(current, proposed)

        # Velocity: how many proposals in last hour?
        recent_count = len([p for p in history if p.age < timedelta(hours=1)])
        velocity_penalty = min(recent_count * 0.1, 0.5)

        # Cumulative change in last 24h
        cumulative_change = self._cumulative_change(history)
        cumulative_penalty = min(cumulative_change * 0.05, 0.3)

        return min(base_risk + velocity_penalty + cumulative_penalty, 1.0)
```

**T-gent Integration via Stigmergy**:

```yaml
# When ProposalOperator detects medium risk:
apiVersion: kgents.io/v1
kind: Pheromone
metadata:
  name: proposal-review-needed
spec:
  type: REVIEW_REQUEST
  intensity: 0.8
  source: proposal-operator
  payload: |
    proposal: b-gent-scale-up
    risk_score: 0.45
  half_life_seconds: 3600
```

**Files**:
```
impl/claude/infra/k8s/crds/proposal-crd.yaml
impl/claude/infra/k8s/operators/proposal_operator.py
impl/claude/infra/k8s/operators/_tests/test_proposal_operator.py
```

### 3.3 CRD Installation

```bash
kgents infra crd --apply          # Install all CRDs
kgents infra crd --apply agent    # Install specific CRD
kgents infra crd --list           # List installed CRDs
kgents infra crd --diff           # Show pending changes
kgents infra crd --delete         # Remove all (requires --confirm)
```

---

## Part IV: The Interface (Ghost, Tether, Terrarium)

### 4.1 Enhanced Ghost Structure

```
.kgents/ghost/
├── agents/
│   ├── b-gent/
│   │   ├── current.json       # Latest CR state
│   │   ├── history.jsonl      # Recent changes (append-only, N-gent witness)
│   │   └── metrics.json       # Resource usage
│   └── _index.json            # Quick lookup
├── pheromones/
│   ├── active.json            # Currently active
│   ├── by_type/
│   │   ├── WARNING.json
│   │   └── DREAM.json
│   └── decay_log.jsonl        # Half-life decay tracking
├── proposals/
│   ├── pending.json
│   ├── merged.json
│   └── rejected.json          # Why rejected? (for learning)
├── cluster/
│   ├── status.json            # Overall health
│   ├── events.jsonl           # Recent K8s events
│   └── connectivity.json      # Last successful connection
└── _meta/
    ├── last_sync.txt
    ├── sync_errors.jsonl
    └── stability_score.json   # For adaptive staleness
```

### 4.2 Terrarium TUI (Built with Textual)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TERRARIUM                                          [Live] 12:34:56 UTC       │
├───────────────────────────────────┬─────────────────────────────────────────┤
│ AGENTS (sorted by activity)       │ PHEROMONE HEATMAP                       │
│                                   │                                         │
│ ▶ B-gent  ████████░░ 80% [busy]  │     ░░▒▒▓▓███ WARNING ███▓▓▒▒░░        │
│   L-gent  ██████████ 100% [idle] │           ▒▒ SCARCITY ▒▒               │
│   M-gent  ██░░░░░░░░ 20% [dream] │    ░░░░░░░░░ DREAM ░░░░░░░░░          │
│                                   │                                         │
│ [↑↓] select  [t]ether  [d]etails │ Visual stigmergy: see hot spots         │
├───────────────────────────────────┴─────────────────────────────────────────┤
│ PROPOSALS                                                                    │
│                                                                              │
│ PENDING   b-gent-scale    Risk: ▒▒░░ 0.25  "High load detected"            │
│ APPROVED  l-gent-memory   Risk: ░░░░ 0.10  "Cache expansion" (auto)        │
│ REJECTED  x-gent-image    Risk: ████ 0.75  "Blocked by T-gent"             │
│                                                                              │
│ [a]pprove  [r]eject  [v]iew diff                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ THOUGHT STREAM (N-gent witness)                                              │
│                                                                              │
│ 12:34:52 [B-gent] Processing invoice batch (47 items)                       │
│ 12:34:54 [M-gent] Attractor forming around protocols/cli/ (surprise: 0.3)   │
│ 12:34:56 [L-gent] Query: "budget allocation" → B-gent (score: 0.91)        │
│                                                                              │
│ [f]ilter by agent  [p]ause stream  [c]lear                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ [q]uit [r]efresh [g]host mode [h]elp                         Pressure: 32%  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Visual Stigmergy**: Pheromones rendered as a **heatmap**, not a list. You physically see "hot spots" of activity.

**Split-Pane Tether**: Built with tmux + Textual integration. Mac-focused.

### 4.3 The "Seance" Mode (Time-Travel Debugging)

```bash
# Since we have Ghost (cache) and Identity (history):
kgents seance b-gent --time "1 hour ago"
```

Spins up a local container with the *exact state and memory* the agent had 1 hour ago.

### 4.4 The "Dream" State (Self-Optimization)

When cluster load is low (CPU < 20%), the Operator spawns a **Dream Cycle**:

```python
class DreamCycleOperator:
    """
    When the body rests, the mind dreams.

    Agents access void.dream (dropped tasks, random thoughts)
    and generate new Proposal CRs for self-optimization.
    """

    async def check_dream_conditions(self, cluster: ClusterState) -> bool:
        return (
            cluster.cpu_usage < 0.20 and
            cluster.active_proposals < 3 and
            datetime.now().hour in range(2, 6)  # Night hours
        )

    async def spawn_dream_cycle(self, agents: list[Agent]):
        for agent in agents:
            if agent.spec.symbiont.dream_enabled:
                await agent.invoke(
                    "void.dream.access",
                    umwelt=agent.umwelt,
                    mode="generative"
                )
```

**Result**: Your cluster optimizes itself while you sleep.

---

## Part V: The Synergy (CLI Hollowing + AGENTESE)

### 5.1 The Layered Isomorphism

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE LAYERED ISOMORPHISM                                   │
│                                                                              │
│   LAYER 3: CLI Shell (Hollow)                                               │
│   ├── Parse args                                                            │
│   ├── Invoke GlassClient                                                    │
│   └── Format output                                                         │
│                                                                              │
│   LAYER 2: Logos Resolver (Cortex Daemon)                                   │
│   ├── AGENTESE path → Operation                                             │
│   ├── Observer threading (Umwelt)                                           │
│   ├── Lens application (Optics)                                             │
│   └── Durable Execution coordination                                        │
│                                                                              │
│   LAYER 1: K8s Backend                                                       │
│   ├── CRD operations (Agent, Pheromone, Proposal)                          │
│   ├── Controller reconciliation                                             │
│   └── etcd persistence                                                      │
│                                                                              │
│   The isomorphism:                                                           │
│   CLI command ≅ AGENTESE path ≅ K8s operation ≅ Durable Workflow            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 AGENTESE Path Registry

| CLI Command | AGENTESE Path | K8s Operation |
|-------------|---------------|---------------|
| `kgents status` | `world.cluster.agents.manifest` | `kubectl get agents -o json` |
| `kgents status --agent b-gent` | `world.cluster.agents.b-gent.manifest` | `kubectl get agent b-gent` |
| `kgents observe` | `void.pheromone.sense` | Watch Pheromone CRs |
| `kgents propose <target> <patch>` | `self.deployment.define` | Create Proposal CR |
| `kgents ghost` | `self.memory.manifest` | Read Ghost cache |
| `kgents tether <agent>` | `world.cluster.agents.<agent>.tether` | Port-forward + signal |
| `kgents signal emit <type>` | `void.pheromone.emit` | Create Pheromone CR |
| `kgents signal sense` | `void.pheromone.sense` | List Pheromone CRs |
| `kgents seance <agent>` | `time.witness.<agent>.replay` | Reconstruct historical state |
| `kgents workflow define` | `world.cluster.workflow.define` | Create Durable Workflow |

### 5.3 GlassClient: The Resilient Boundary

```python
class GlassClient:
    """
    Three fallback layers: gRPC → Ghost → kubectl

    "Online Brain, Offline Reflexes"
    """

    async def invoke(
        self,
        path: str,
        observer: Umwelt | None = None,
        lens: str = "optics.identity",
        ghost_key: str | None = None,
        **kwargs,
    ) -> GlassResponse:
        # Layer 1: Cortex daemon (gRPC)
        # Layer 2: Ghost cache
        # Layer 3: Direct kubectl
        # → See impl/claude/protocols/cli/glass.py
```

---

## Part VI: Implementation Order

### Phase 0: The "Hollow" Body

*Don't build the fancy CLI yet. Build the organs.*

| # | Task | Deliverable | Notes |
|---|------|-------------|-------|
| 0.1 | Base CRDs | `Agent`, `Pheromone` CRDs | Use `kopf` (Python, production-ready) |
| 0.2 | The Operator | `agent_operator.py` | Basic reconciliation |
| 0.3 | The Cortex | Python daemon, gRPC socket | Just wraps kubectl initially |
| 0.4 | Terrarium TUI | Basic Textual app | Split-pane capable |

### Phase 1: The Nervous System

*Connect the organs.*

| # | Task | Deliverable | Depends On |
|---|------|-------------|------------|
| 1.1 | Ghost Protocol | `~/.kgents/ghost/` local file cache | 0.3 |
| 1.2 | Symbiont Injector | Auto-inject D-gent/K-gent sidecars | 0.1, 0.2 |
| 1.3 | Logos Resolver | `world.cluster` → cache reads (fast) or K8s calls (slow) | 0.3, 1.1 |
| 1.4 | Cognitive Probes | Health checks that understand LLM semantics | 1.2 |

### Phase 2: The Mind

*Turn on the consciousness.*

| # | Task | Deliverable | Depends On |
|---|------|-------------|------------|
| 2.1 | Proposal Operator | Autopoiesis enabled | 1.3 |
| 2.2 | T-Gent Webhook | ValidatingAdmissionWebhook | 2.1 |
| 2.3 | Durable Workflow | Lightweight CRD-based state machine | 2.1 |
| 2.4 | Dream Cycle | Low-load self-optimization | 2.3 |

### Phase 3: The Interface

*The viewport into the hive mind.*

| # | Task | Deliverable | Depends On |
|---|------|-------------|------------|
| 3.1 | Visual Stigmergy | Pheromone heatmap in Terrarium | 0.4, 1.3 |
| 3.2 | Seance Mode | Time-travel debugging | 1.1 |
| 3.3 | MCP Server | Claude Code integration | 1.3 |
| 3.4 | `kgents workflow` | CLI for Durable Execution | 2.3 |

---

## Part VII: Success Criteria

### Phase 0 Complete When:

- [ ] `kubectl apply -f infra/k8s/crds/` installs Agent + Pheromone CRDs
- [ ] Creating Agent CR spawns Deployment
- [ ] Terrarium TUI launches and shows placeholder data
- [ ] Cortex daemon starts and responds to health check

### Phase 1 Complete When:

- [ ] Ghost cache created on first successful connection
- [ ] `kgents status` shows `[GHOST]` when cluster unavailable
- [ ] Agents have D-gent memory sidecar auto-injected
- [ ] Cognitive probes detect "garbage output" as unhealthy

### Phase 2 Complete When:

- [ ] Creating Proposal CR triggers dry-run validation
- [ ] Low-risk proposals auto-merge
- [ ] T-gent webhook blocks high-risk changes
- [ ] Durable workflows preserve composition laws

### Phase 3 Complete When:

- [ ] Terrarium shows pheromone heatmap
- [ ] `kgents seance b-gent --time "1h ago"` reconstructs past state
- [ ] Claude Code can `<resource>kgents://agents</resource>`
- [ ] Dream cycle runs during low-load periods

---

## Part VIII: Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Composition breaks over network** | High | Durable Execution Engine (Temporal patterns) |
| **Ghost cache corruption** | Medium | Checksum validation, auto-rebuild from kubectl |
| **Operator complexity explosion** | High | Kopf framework, rigorous testing |
| **T-gent webhook latency** | Medium | Fast path (CEL/Rego) for common cases |
| **Dream cycle runaway** | High | Start with "Deny All" for LLM proposals |

---

## Part IX: What We're NOT Doing (Yet)

| Feature | Why Deferred | Revisit When |
|---------|--------------|--------------|
| Agent Mesh (sidecar proxy) | Overkill for <10 agents | >10 agents deployed |
| SpinKube/Wasm | Immature | Production scale needs |
| Federated Discovery | Single-cluster first | Multi-cluster requirement |
| Full Active Inference | Research needed | Phase 3 complete |
| Custom K8s Scheduler | Pod Priority sufficient | >100 agents/cluster |
| Windows support | Mac-focused development | User demand |

---

## Cross-References

- **Spec**: `spec/k8-gents/README.md`, `02_evolution.md`, `03_interface.md`
- **Plans**: `plans/cli-hollowing-plan.md`, `plans/agentese-synthesis.md`
- **Principles**: `spec/principles.md`
- **Existing Impl**: `infra/k8s/operators/pheromone_operator.py`, `infra/k8s/tether.py`
- **Glass Terminal**: `protocols/cli/glass.py`, `infra/cortex/service.py`

---

*"Do not over-engineer the network layer. Focus on the interface. The Terrarium is not just a tool; it is the viewport into the hive mind. Make it beautiful."*

*"Relax. The body knows how to heal. You are just building the skeleton."*
