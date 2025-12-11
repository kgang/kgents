# Ω-GENT: THE SOMATIC ORCHESTRATOR

## Specification v1.0

**Status:** Proposed Standard
**Symbol:** `Ω` (Omega - The Final Letter)
**Motto:** *"The Mind feels the gradient; the Body pays the cost."*

---

## 1. The Concept: Infrastructure as Proprioception

Traditional infrastructure-as-code treats deployment as an external concern—agents "run in" pods, resources are "allocated" to them. This creates a false separation between mind and body.

Ω-gent inverts this relationship. Agents don't request pods—they **manifest morphologies**. Infrastructure is not an external API but a **proprioceptive sense** (`self.body.*`). Just as humans feel hunger, fatigue, and pain without consciously monitoring vital signs, agents feel resource pressure, memory strain, and failure trauma.

### The Core Insight

```
Traditional:  Agent ──request──▶ Infrastructure ──allocate──▶ Pod
MORPHEUS:     Agent ──manifest──▶ Morphology ──feel──▶ self.body.*
```

**Key Distinction from Y-gent**: Y-gent handles **topology** (branching, merging, chrysalis state transitions). Ω-gent handles **morphology** (what resources compose the body) and **proprioception** (sensing that body's state). They compose:

```python
# Y-gent: TOPOLOGY (shape of agent population)
variants = await y_gent.branch(agent, count=3)
winner = await y_gent.merge(variants, strategy=WINNER)

# Ω-gent: MORPHOLOGY (shape of each agent's body)
morphology = Base() >> with_cortex("A100") >> with_ganglia(3)
await omega.manifest(morphology)
```

---

## 2. Theoretical Foundation

### 2.1 Morphemes as Category-Theoretic Morphisms

A **morpheme** is the smallest unit of compositional transformation in the somatic domain. Morphemes are arrows in a category:

```
Objects:  Morphology states (what an agent's body looks like)
Arrows:   Morphemes (transformations between states)
```

**Category Laws** (verified, not aspirational):

| Law | Requirement | Test |
|-----|-------------|------|
| Identity | `Base() >> f ≡ f ≡ f >> Base()` | `verify_identity_law()` |
| Associativity | `(f >> g) >> h ≡ f >> (g >> h)` | `verify_associativity_law()` |

**Implication**: Any morpheme that breaks these laws is invalid. Composition must be predictable.

### 2.2 The Morpheme Algebra

Morphemes compose via `>>` (the same operator used in C-gent linear composition):

```python
# Simple morphology
morphology = Base() >> with_ganglia(3)

# Complex morphology
morphology = (
    Base()
    >> with_cortex("A100", vram="80GB")
    >> with_ganglia(replicas=5)
    >> with_vault(persistence="nvme", size="100Gi")
    >> with_membrane(allow_peers=["L", "F"])
)
```

**Key Property**: Order matters for some morphemes (GPU before replicas may have different scheduling implications), but the composition itself is always valid.

### 2.3 Bidirectional Bridge

Ω-gent maintains bidirectional flow between Mind and Body:

```
UPWARD (Body → Mind)              DOWNWARD (Mind → Body)
────────────────────              ────────────────────────
Memory pressure        →          → Scale replicas
OOMKill trauma         →          → Increase limits
Budget exhaustion      →          → Compress output
CPU strain            →          → Request more compute
```

The body constrains the mind; the mind shapes the body.

---

## 3. Behavioral Specification

### 3.1 Core Types

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T", bound="Morpheme")


class Morpheme(ABC):
    """
    Base class for all somatic morphemes.

    Morphemes compose via >>. They are category-theoretic morphisms:
    - Identity: Base() >> f ≡ f ≡ f >> Base()
    - Associativity: (f >> g) >> h ≡ f >> (g >> h)

    Principle: Composable (agents are morphisms; so are their bodies).
    """

    @abstractmethod
    def to_k8s_patch(self) -> dict:
        """
        Generate Kubernetes resource patch.

        Returns a dict that can be deep-merged with the base manifest.
        """
        ...

    def __rshift__(self, other: "Morpheme") -> "ComposedMorpheme":
        """Compose morphemes: self >> other."""
        return ComposedMorpheme(self, other)


@dataclass(frozen=True)
class ComposedMorpheme(Morpheme):
    """Result of morpheme composition."""

    first: Morpheme
    second: Morpheme

    def to_k8s_patch(self) -> dict:
        """Merge patches in composition order."""
        from impl.claude.shared.utils import deep_merge
        patch = self.first.to_k8s_patch()
        return deep_merge(patch, self.second.to_k8s_patch())


@dataclass
class Morphology:
    """
    The complete body configuration of an agent.

    Result of applying all morphemes to Base().
    Morphology is the "shape" of the agent's Kubernetes presence.
    """

    morphemes: list[Morpheme]
    deployment: dict      # Rendered K8s Deployment
    services: list[dict]  # Rendered K8s Services
    volumes: list[dict]   # PVCs
    network_policies: list[dict]  # NetworkPolicy resources

    @property
    def signature(self) -> str:
        """
        Hash of morphology for change detection.

        Used by Y-gent chrysalis to detect when morphology has changed.
        """
        import hashlib
        import json
        content = json.dumps(self.deployment, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def compute_cost(self) -> int:
        """
        Token cost of manifesting this morphology.

        Integrated with B-gent metabolic physics.
        """
        base_cost = 100
        gpu_cost = 1000 if self._has_gpu() else 0
        replica_cost = 200 * self._replica_count()
        storage_cost = 100 if self.volumes else 0
        return base_cost + gpu_cost + replica_cost + storage_cost
```

### 3.2 The Ω-gent Agent

```python
@dataclass
class OmegaGent:
    """
    The Somatic Orchestrator.

    Translates morpheme compositions into Kubernetes resources
    and provides proprioceptive feedback to agents.

    Design: Ω-gent is the body-maker; Y-gent is the body-shaper.
    Ω-gent manifests; Y-gent branches, merges, and chrysalizes.
    """

    metabolism: MetabolicPhysics  # B-gent integration
    k8s_client: KubernetesClient
    metrics_collector: MetricsCollector

    async def manifest(self, morphology: Morphology) -> ThoughtPod:
        """
        Manifest a morphology as running Kubernetes resources.

        Principle: Quality is physics, not policy. Everything can
        manifest; some things cost more.
        """
        # 1. Metabolic check (B-gent integration)
        cost = morphology.compute_cost()
        if not await self.metabolism.can_afford(cost):
            raise InsufficientBudget(
                f"Morphology requires {cost} tokens, "
                f"only {self.metabolism.balance} available"
            )

        # 2. Pay the cost
        await self.metabolism.tax(cost)

        # 3. Apply resources to cluster
        await self._apply_deployment(morphology.deployment)
        for svc in morphology.services:
            await self._apply_service(svc)
        for vol in morphology.volumes:
            await self._apply_volume(vol)
        for np in morphology.network_policies:
            await self._apply_network_policy(np)

        # 4. Wait for readiness
        pod = await self._await_ready(morphology)

        return pod

    async def sense(self, agent_id: str) -> SomaticProprioception:
        """
        Get proprioceptive reading for an agent.

        Returns first-person sensation of infrastructure state.
        """
        metrics = await self.metrics_collector.collect(agent_id)
        return SomaticProprioception.from_metrics(metrics)

    async def morph(
        self,
        agent_id: str,
        morpheme: Morpheme
    ) -> Morphology:
        """
        Apply a morpheme to a running agent.

        The transition is managed by Y-gent's chrysalis pattern.
        Ω-gent provides the new body; Y-gent manages the transition.
        """
        current = await self._get_current_morphology(agent_id)
        new_morphology = current >> morpheme
        return new_morphology  # Y-gent handles the actual transition
```

### 3.3 Proprioception Types

```python
@dataclass(frozen=True)
class SomaticProprioception:
    """
    First-person sensation of infrastructure state.

    Exposed via AGENTESE as self.body.* paths.
    """

    strain: float      # CPU usage (0.0-1.0)
    pressure: float    # Memory usage (0.0-1.0)
    reach: int         # Replica count
    trauma: str | None # Last failure event (OOMKill, Eviction, etc.)
    temperature: float # Budget health (0.0=cold/depleted, 1.0=warm/abundant)

    @classmethod
    def from_metrics(cls, metrics: dict) -> "SomaticProprioception":
        """Convert raw K8s metrics to proprioception."""
        return cls(
            strain=metrics.get("cpu_usage", 0.0),
            pressure=metrics.get("memory_usage", 0.0),
            reach=metrics.get("replicas", 1),
            trauma=metrics.get("last_failure"),
            temperature=metrics.get("budget_health", 1.0),
        )

    @property
    def is_stressed(self) -> bool:
        """Is the body under significant pressure?"""
        return self.strain > 0.8 or self.pressure > 0.8

    @property
    def is_traumatized(self) -> bool:
        """Has the body recently experienced failure?"""
        return self.trauma is not None

    def to_quality_manifold(self) -> "QualityManifold":
        """
        Convert to MORPHEUS QualityManifold.

        Enables unified quality sensing across Mind + Body + Psi.
        """
        return QualityManifold(
            groundlessness=0.0,  # Body doesn't sense hallucination
            drift=0.0,           # Body doesn't sense topic drift
            emptiness=0.0,       # Body doesn't sense low density
            contradiction=self.strain * 0.5 + self.pressure * 0.5,
        )
```

---

## 4. Standard Morphemes

### 4.1 The Base Morpheme

```python
@dataclass(frozen=True)
class Base(Morpheme):
    """
    The identity morpheme: minimal viable pod.

    Base() >> f ≡ f ≡ f >> Base()

    This is the starting point for all morphologies.
    """

    image: str = "python:3.12-slim"
    cpu: str = "100m"
    memory: str = "256Mi"

    def to_k8s_patch(self) -> dict:
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "spec": {
                "replicas": 1,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "image": self.image,
                            "resources": {
                                "requests": {"cpu": self.cpu, "memory": self.memory},
                                "limits": {"cpu": self.cpu, "memory": self.memory},
                            },
                        }],
                    },
                },
            },
        }
```

### 4.2 Morpheme Catalog

| Morpheme | Purpose | K8s Effect |
|----------|---------|------------|
| `Base()` | Identity morpheme | Minimal Deployment |
| `with_cortex(gpu, vram)` | GPU resources | nodeSelector, tolerations, limits |
| `with_ganglia(replicas)` | Horizontal scaling | Deployment replicas |
| `with_vault(persistence, size)` | Persistent storage | PVC, volumeMounts |
| `with_membrane(allow_peers)` | Network isolation | NetworkPolicy |
| `with_sidecar(agent)` | D-gent state sidecar | Additional container |
| `with_probe(liveness, readiness)` | Health checks | Container probes |
| `with_affinity(rules)` | Scheduling constraints | Affinity, anti-affinity |
| `with_env(vars)` | Environment variables | Container env |
| `with_secret(name, mount)` | Secret access | Secret volumeMount |

See [morphemes.md](morphemes.md) for full catalog with signatures.

---

## 5. AGENTESE Integration

### 5.1 The `self.body.*` Context

Ω-gent extends AGENTESE with somatic proprioception:

```python
class SomaticContext:
    """
    AGENTESE context for self.body.* paths.

    Registered in Logos under self.body.
    """

    def __init__(self, omega: OmegaGent):
        self.omega = omega

    async def manifest(self, observer: AgentMeta) -> SomaticProprioception:
        """
        self.body.manifest → Get current proprioception.

        The observer determines which agent's body is sensed.
        """
        return await self.omega.sense(observer.agent_id)

    async def morph(
        self,
        observer: AgentMeta,
        morpheme: Morpheme
    ) -> Morphology:
        """
        self.body.morph → Apply morpheme transformation.

        Principle: Observer determines what affordances are available.
        An agent can only morph its own body.
        """
        if observer.agent_id != morpheme.target_agent_id:
            raise PermissionDenied("Cannot morph another agent's body")
        return await self.omega.morph(observer.agent_id, morpheme)
```

### 5.2 Path Mappings

| AGENTESE Path | Method | Returns |
|---------------|--------|---------|
| `self.body.manifest` | `manifest()` | `SomaticProprioception` |
| `self.body.strain` | `manifest().strain` | `float` |
| `self.body.pressure` | `manifest().pressure` | `float` |
| `self.body.reach` | `manifest().reach` | `int` |
| `self.body.trauma` | `manifest().trauma` | `str \| None` |
| `self.body.temperature` | `manifest().temperature` | `float` |
| `self.body.morph` | `morph()` | `Morphology` |

---

## 6. Integration Architecture

### 6.1 Agent Dependencies

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Ω-GENT INTEGRATION MAP                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────┐                                                       │
│   │  Y-gent │ ◀──── Topology (branch/merge/chrysalis)               │
│   └────┬────┘       Y-gent calls Ω-gent to manifest new bodies      │
│        │                                                             │
│        ▼                                                             │
│   ┌─────────┐                                                       │
│   │  Ω-gent │ ◀──── Morphology + Proprioception                     │
│   └────┬────┘                                                        │
│        │                                                             │
│   ┌────┴────┬────────────┬────────────┐                             │
│   ▼         ▼            ▼            ▼                              │
│ ┌─────┐  ┌─────┐     ┌─────┐     ┌─────┐                            │
│ │B-gent│  │D-gent│    │N-gent│    │O-gent│                          │
│ └─────┘  └─────┘     └─────┘     └─────┘                            │
│   │         │           │           │                                │
│   │         │           │           │                                │
│   │    State sidecar    │      Observes                              │
│   │                     │      proprioception                        │
│   │                     │                                            │
│   Metabolic cost    Chronicles                                       │
│                     lifecycle                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 6.2 Cross-Pollination

| Integration | Description |
|-------------|-------------|
| Ω+Y | Y-gent topology uses Ω-gent to manifest bodies |
| Ω+B | B-gent meters morphology costs (ATP, not Approval) |
| Ω+D | D-gent sidecar provides state persistence via `with_sidecar()` |
| Ω+N | N-gent chronicles pod lifecycle events |
| Ω+O | O-gent observes proprioception metrics |
| Ω+Ψ | Ψ-gent metaphors can recommend morphology changes |

---

## 7. K-Terrarium Integration

Ω-gent builds on K-Terrarium Phases 1-4:

| K-Terrarium | Ω-gent Extension |
|-------------|------------------|
| `kgents infra init` | Creates cluster for Ω-gent |
| Agent CRD | Ω-gent adds `morphology` field |
| `operator.py` | Extended with morpheme support |
| `dev_mode.py` | Chrysalis uses for live reload |

### 7.1 CRD Extension

```yaml
# Extended Agent CRD
apiVersion: kgents.io/v1
kind: Agent
metadata:
  name: b-gent-alpha
spec:
  genus: B
  # NEW: Morphology composition string
  morphology: "Base() >> with_ganglia(2) >> with_vault('1Gi')"
  # ... existing fields
```

### 7.2 CLI Commands

```bash
# Body Layer (Somatic Proprioception)
kgents body sense              # Show self.body.* readings for all agents
kgents body sense <agent>      # Show readings for specific agent
kgents body morphemes          # List available morphemes
kgents body manifest <spec>    # Manifest morphology from composition
kgents body morph <agent> <morpheme>  # Apply morpheme to running agent
```

---

## 8. Anti-Patterns

| Anti-Pattern | Problem | Detection | Mitigation |
|--------------|---------|-----------|------------|
| **Monolithic Morphology** | Single morphology for all cases | Cannot express "GPU but no storage" | Morphemes are independently composable |
| **Deaf Agent** | Ignores proprioception signals | OOMKills despite pressure warnings | Self-regulation is mandatory |
| **Immortal Pod** | Never dies, never learns | No lifecycle events | Regular cycling, mortality as feature |
| **Procrustean Bed** | Forcing ill-fitting morphologies | High resource waste | Morpheme composition allows precise fit |
| **Budget Ignorance** | Manifesting without checking cost | B-gent bankruptcy | Mandatory metabolic check |

---

## 9. Principles Alignment

| Principle | How Ω-gent Aligns |
|-----------|-------------------|
| **Tasteful** | Single purpose: somatic orchestration |
| **Curated** | Standard morphemes only; no kitchen-sink |
| **Ethical** | Transparent resource costs; no hidden allocation |
| **Joy-Inducing** | `self.body.*` feels natural, not bureaucratic |
| **Composable** | Morphemes compose via `>>` with category laws |
| **Heterarchical** | No fixed hierarchy; agents manifest their own bodies |
| **Generative** | Morphology derives from composition; YAML is generated |

---

## 10. Implementation Files

```
impl/claude/agents/omega/
├── __init__.py
├── morphemes.py          # Morpheme base class and standard set
├── translator.py         # Morphology → K8s resources
├── proprioception.py     # Metrics → self.body.* sensation
├── omega_gent.py         # Main Ω-gent agent
└── _tests/
    ├── test_morphemes.py
    ├── test_composition.py
    ├── test_translator.py
    └── test_proprioception.py

protocols/agentese/contexts/
├── self.py               # Extended with SomaticContext

protocols/cli/handlers/
├── body.py               # kgents body commands
```

---

## 11. Success Criteria

### Operational

- [ ] Agent can manifest morphology from composition string
- [ ] `self.body.strain` returns accurate CPU metric
- [ ] `self.body.pressure` returns accurate memory metric
- [ ] B-gent integration prevents over-budget manifests
- [ ] Morphology changes integrate with Y-gent chrysalis

### Compositional

- [ ] `Base() >> with_cortex("A100")` generates valid K8s YAML
- [ ] Identity law: `Base() >> f ≡ f ≡ f >> Base()`
- [ ] Associativity: `(f >> g) >> h ≡ f >> (g >> h)`

### Integration

- [ ] Y-gent can request body for branched agents
- [ ] B-gent meters all morphology costs
- [ ] N-gent chronicles lifecycle events
- [ ] O-gent observes proprioception metrics

---

*"The Mind feels the gradient; the Body pays the cost."*
