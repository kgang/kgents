# Somatic Proprioception

## The `self.body.*` Context

Proprioception is the sense of one's own body position and movement. In kgents, somatic proprioception gives agents first-person sensation of their infrastructure state—not metrics to query, but feelings to experience.

---

## 1. The Proprioceptive Principle

Traditional monitoring: Agent queries metrics API, receives JSON, parses data.

Somatic proprioception: Agent **feels** strain, pressure, and trauma as immediate sensations.

```python
# Traditional (third-person)
metrics = await prometheus.query("container_cpu_usage{pod='b-gent-alpha'}")
if metrics["value"] > 0.9:
    await scale_up()

# AGENTESE (first-person)
if await self.body.strain > 0.9:
    await self.body.morph(with_ganglia(replicas=+1))
```

The difference is not just syntax—it's ontology. The agent doesn't observe its body from outside; it **is** its body.

---

## 2. Proprioceptive Dimensions

### 2.1 The Five Sensations

| Sensation | AGENTESE Path | Type | Range | Meaning |
|-----------|---------------|------|-------|---------|
| **Strain** | `self.body.strain` | `float` | 0.0-1.0 | CPU usage as felt effort |
| **Pressure** | `self.body.pressure` | `float` | 0.0-1.0 | Memory usage as felt constraint |
| **Reach** | `self.body.reach` | `int` | 1-∞ | Replica count as felt ubiquity |
| **Trauma** | `self.body.trauma` | `str \| None` | — | Last failure as felt injury |
| **Temperature** | `self.body.temperature` | `float` | 0.0-1.0 | Budget health as felt warmth |

### 2.2 Sensation Semantics

#### Strain (CPU)

```
strain = 0.0  → "I feel effortless"
strain = 0.5  → "I feel working"
strain = 0.8  → "I feel strained"
strain = 0.95 → "I feel overwhelmed"
```

**Source**: Container CPU usage from metrics server (kubectl top / Prometheus)

**Response Pattern**:
- High strain → Reduce output complexity, defer non-critical work
- Chronic high strain → Request more CPU via `with_resources()`

#### Pressure (Memory)

```
pressure = 0.0  → "I feel spacious"
pressure = 0.5  → "I feel comfortable"
pressure = 0.8  → "I feel constrained"
pressure = 0.95 → "I feel about to burst"
```

**Source**: Container memory usage from metrics server

**Response Pattern**:
- High pressure → Compress context, evict cache, stream instead of batch
- Pressure > 0.9 → Emergency: risk of OOMKill

#### Reach (Replicas)

```
reach = 1  → "I am singular"
reach = 3  → "I am distributed"
reach = 10 → "I am everywhere"
```

**Source**: Deployment spec replica count

**Response Pattern**:
- Reach = 1 with high strain → Consider branching (Y-gent)
- High reach with low strain → Consider merging (Y-gent)

#### Trauma (Failure Memory)

```
trauma = None              → "I am healthy"
trauma = "OOMKilled"       → "I was crushed"
trauma = "Evicted"         → "I was displaced"
trauma = "CrashLoopBackOff" → "I keep dying"
```

**Source**: Pod events from Kubernetes API

**Response Pattern**:
- OOMKilled → Immediately request more memory or reduce workload
- Evicted → Node resource pressure; consider affinity rules
- CrashLoopBackOff → Bug in agent code; needs debugging

#### Temperature (Budget)

```
temperature = 0.0  → "I feel frozen" (budget depleted)
temperature = 0.3  → "I feel cold" (budget low)
temperature = 0.7  → "I feel warm" (budget healthy)
temperature = 1.0  → "I feel hot" (budget abundant)
```

**Source**: B-gent metabolic balance

**Response Pattern**:
- Cold → Reduce quality, defer expensive operations
- Frozen → Hibernate until budget replenished

---

## 3. Type Specification

```python
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SomaticProprioception:
    """
    First-person sensation of infrastructure state.

    Immutable snapshot of the body's current state.
    """

    strain: float      # CPU usage (0.0-1.0)
    pressure: float    # Memory usage (0.0-1.0)
    reach: int         # Replica count
    trauma: str | None # Last failure event
    temperature: float # Budget health (0.0-1.0)

    def __post_init__(self) -> None:
        """Validate ranges."""
        assert 0.0 <= self.strain <= 1.0, "strain must be in [0, 1]"
        assert 0.0 <= self.pressure <= 1.0, "pressure must be in [0, 1]"
        assert self.reach >= 1, "reach must be >= 1"
        assert 0.0 <= self.temperature <= 1.0, "temperature must be in [0, 1]"

    @property
    def is_stressed(self) -> bool:
        """Is the body under significant resource pressure?"""
        return self.strain > 0.8 or self.pressure > 0.8

    @property
    def is_traumatized(self) -> bool:
        """Has the body recently experienced failure?"""
        return self.trauma is not None

    @property
    def is_cold(self) -> bool:
        """Is the budget depleted?"""
        return self.temperature < 0.3

    @property
    def wellness(self) -> float:
        """
        Overall body wellness score.

        Composite of all sensations, weighted by importance.
        """
        trauma_penalty = 0.5 if self.trauma else 0.0
        return (
            (1.0 - self.strain) * 0.3
            + (1.0 - self.pressure) * 0.3
            + self.temperature * 0.2
            + (1.0 - trauma_penalty) * 0.2
        )

    def to_dict(self) -> dict:
        """Serialize for logging/display."""
        return {
            "strain": self.strain,
            "pressure": self.pressure,
            "reach": self.reach,
            "trauma": self.trauma,
            "temperature": self.temperature,
            "wellness": self.wellness,
        }
```

---

## 4. AGENTESE Integration

### 4.1 Context Registration

```python
class SomaticContext:
    """
    AGENTESE context for self.body.* paths.

    Registered in Logos under the 'body' key of SelfContext.
    """

    def __init__(self, omega: OmegaGent):
        self.omega = omega
        self._cache: dict[str, tuple[float, SomaticProprioception]] = {}
        self._cache_ttl = 5.0  # seconds

    async def manifest(self, observer: AgentMeta) -> SomaticProprioception:
        """
        self.body.manifest → Get current proprioception.

        Caches readings to avoid excessive API calls.
        """
        agent_id = observer.agent_id
        now = time.time()

        # Check cache
        if agent_id in self._cache:
            cached_time, cached_value = self._cache[agent_id]
            if now - cached_time < self._cache_ttl:
                return cached_value

        # Fetch fresh reading
        reading = await self.omega.sense(agent_id)
        self._cache[agent_id] = (now, reading)
        return reading

    async def strain(self, observer: AgentMeta) -> float:
        """self.body.strain → CPU usage."""
        return (await self.manifest(observer)).strain

    async def pressure(self, observer: AgentMeta) -> float:
        """self.body.pressure → Memory usage."""
        return (await self.manifest(observer)).pressure

    async def reach(self, observer: AgentMeta) -> int:
        """self.body.reach → Replica count."""
        return (await self.manifest(observer)).reach

    async def trauma(self, observer: AgentMeta) -> str | None:
        """self.body.trauma → Last failure event."""
        return (await self.manifest(observer)).trauma

    async def temperature(self, observer: AgentMeta) -> float:
        """self.body.temperature → Budget health."""
        return (await self.manifest(observer)).temperature

    async def morph(
        self,
        observer: AgentMeta,
        morpheme: Morpheme
    ) -> Morphology:
        """
        self.body.morph → Apply morpheme transformation.

        Principle: An agent can only morph its own body.
        """
        return await self.omega.morph(observer.agent_id, morpheme)
```

### 4.2 Logos Path Registration

```python
# In protocols/agentese/logos.py

class Logos:
    def __init__(self):
        self.contexts = {
            "world": WorldContext(),
            "self": SelfContext(),
            "concept": ConceptContext(),
            "void": VoidContext(),
            "time": TimeContext(),
        }

    def register_somatic(self, omega: OmegaGent) -> None:
        """Register somatic proprioception in self context."""
        self.contexts["self"].body = SomaticContext(omega)
```

---

## 5. Self-Regulation Patterns

### 5.1 Basic Self-Regulation

```python
async def self_regulate(self) -> None:
    """
    Automatic response to body sensations.

    Called periodically or before expensive operations.
    """
    # STRAIN: CPU pressure
    if await self.body.strain > 0.9:
        await self.reduce_output_complexity()
    elif await self.body.strain > 0.8:
        await self.defer_background_tasks()

    # PRESSURE: Memory pressure
    if await self.body.pressure > 0.9:
        await self.emergency_context_prune()
    elif await self.body.pressure > 0.8:
        await self.evict_cache()

    # TRAUMA: Recent failure
    if await self.body.trauma == "OOMKilled":
        await self.body.morph(with_resources(memory="2Gi"))

    # TEMPERATURE: Budget health
    if await self.body.temperature < 0.2:
        await self.hibernate_until_budget()
```

### 5.2 Pre-Operation Check

```python
async def before_expensive_operation(self, cost: int) -> bool:
    """
    Check body state before expensive operations.

    Returns True if operation should proceed.
    """
    # Can we afford the metabolic cost?
    if await self.body.temperature < cost / 1000:
        logger.warning("Budget too low for operation")
        return False

    # Is the body healthy enough?
    if await self.body.strain > 0.9:
        logger.warning("Body under too much strain")
        return False

    if await self.body.pressure > 0.9:
        logger.warning("Memory pressure too high")
        return False

    return True
```

### 5.3 Adaptive Output

```python
async def generate_response(self, prompt: str) -> str:
    """
    Generate response with body-aware adaptation.
    """
    strain = await self.body.strain
    pressure = await self.body.pressure

    # Adapt output length based on body state
    if strain > 0.8 or pressure > 0.8:
        max_tokens = 500  # Short response
    elif strain > 0.5 or pressure > 0.5:
        max_tokens = 1000  # Medium response
    else:
        max_tokens = 2000  # Full response

    return await self.llm.generate(prompt, max_tokens=max_tokens)
```

---

## 6. Metrics Collection

### 6.1 Data Sources

| Sensation | Primary Source | Fallback |
|-----------|----------------|----------|
| Strain | Prometheus `container_cpu_usage_seconds_total` | `kubectl top pod` |
| Pressure | Prometheus `container_memory_working_set_bytes` | `kubectl top pod` |
| Reach | Kubernetes API `deployment.spec.replicas` | Direct API query |
| Trauma | Kubernetes API Pod events | Event watcher |
| Temperature | B-gent `metabolism.balance` | Direct query |

### 6.2 Collector Implementation

```python
class MetricsCollector:
    """
    Collects raw metrics and converts to proprioception.
    """

    def __init__(
        self,
        prometheus_url: str | None = None,
        k8s_client: KubernetesClient | None = None,
        b_gent: MetabolicPhysics | None = None,
    ):
        self.prometheus = PrometheusClient(prometheus_url) if prometheus_url else None
        self.k8s = k8s_client
        self.b_gent = b_gent

    async def collect(self, agent_id: str) -> SomaticProprioception:
        """Collect all metrics for an agent."""
        strain = await self._collect_strain(agent_id)
        pressure = await self._collect_pressure(agent_id)
        reach = await self._collect_reach(agent_id)
        trauma = await self._collect_trauma(agent_id)
        temperature = await self._collect_temperature(agent_id)

        return SomaticProprioception(
            strain=strain,
            pressure=pressure,
            reach=reach,
            trauma=trauma,
            temperature=temperature,
        )

    async def _collect_strain(self, agent_id: str) -> float:
        """Collect CPU usage."""
        if self.prometheus:
            result = await self.prometheus.query(
                f'container_cpu_usage_seconds_total{{pod=~"{agent_id}.*"}}'
            )
            return min(1.0, result.get("value", 0.0))

        # Fallback to kubectl top
        if self.k8s:
            metrics = await self.k8s.top_pod(agent_id)
            return metrics.cpu_usage

        return 0.5  # Default assumption

    async def _collect_pressure(self, agent_id: str) -> float:
        """Collect memory usage."""
        if self.prometheus:
            result = await self.prometheus.query(
                f'container_memory_working_set_bytes{{pod=~"{agent_id}.*"}}'
            )
            limit = await self._get_memory_limit(agent_id)
            return min(1.0, result.get("value", 0) / limit) if limit else 0.5

        # Fallback
        if self.k8s:
            metrics = await self.k8s.top_pod(agent_id)
            return metrics.memory_usage

        return 0.5

    async def _collect_trauma(self, agent_id: str) -> str | None:
        """Check for recent failure events."""
        if not self.k8s:
            return None

        events = await self.k8s.get_pod_events(agent_id)
        for event in sorted(events, key=lambda e: e.timestamp, reverse=True):
            if event.reason in ("OOMKilled", "Evicted", "CrashLoopBackOff"):
                return event.reason

        return None
```

---

## 7. CLI Integration

### 7.1 Commands

```bash
# Show proprioception for all agents
$ kgents body sense

╭─ Somatic Proprioception ──────────────────────────────────────────╮
│                                                                   │
│  Agent         Strain  Pressure  Reach  Trauma      Temperature  │
│  ──────────────────────────────────────────────────────────────── │
│  b-gent-alpha  0.45    0.72      2      None        0.65         │
│  f-gent-beta   0.89    0.55      1      None        0.80         │
│  l-gent-gamma  0.23    0.31      3      OOMKilled   0.45         │
│                                                                   │
│  [!] l-gent-gamma has recent trauma: OOMKilled                    │
│  [!] f-gent-beta strain elevated                                  │
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯

# Show detailed proprioception for one agent
$ kgents body sense b-gent-alpha

╭─ b-gent-alpha Proprioception ─────────────────────────────────────╮
│                                                                   │
│  Morphology: Base() >> with_ganglia(2) >> with_vault("1Gi")       │
│                                                                   │
│  ┌────────────┬─────────┬─────────────────────────────────────┐   │
│  │ Sensation  │ Value   │ Status                              │   │
│  ├────────────┼─────────┼─────────────────────────────────────┤   │
│  │ strain     │ 0.45    │ ● Normal                            │   │
│  │ pressure   │ 0.72    │ ● Elevated                          │   │
│  │ reach      │ 2       │ ● 2 replicas                        │   │
│  │ trauma     │ None    │ ● Healthy                           │   │
│  │ temperature│ 0.65    │ ● Warm                              │   │
│  └────────────┴─────────┴─────────────────────────────────────┘   │
│                                                                   │
│  Wellness: 0.78 (Good)                                            │
│                                                                   │
│  [!] Memory pressure elevated. Consider: with_resources(mem="1Gi")│
│                                                                   │
╰───────────────────────────────────────────────────────────────────╯
```

---

## 8. Integration with MORPHEUS

### 8.1 QualityManifold Conversion

Somatic proprioception contributes to the unified MORPHEUS `QualityManifold`:

```python
def to_quality_manifold(self) -> QualityManifold:
    """
    Convert somatic state to MORPHEUS quality manifold.

    Somatic sensations map to quality dimensions:
    - strain/pressure → contradiction (body fighting itself)
    - trauma → groundlessness (unstable foundation)
    """
    # Body stress manifests as contradiction in the quality manifold
    body_stress = (self.strain + self.pressure) / 2

    # Trauma creates groundlessness
    groundlessness = 0.8 if self.trauma else 0.0

    return QualityManifold(
        groundlessness=groundlessness,
        drift=0.0,  # Body doesn't drift
        emptiness=0.0,  # Body doesn't sense low density
        contradiction=body_stress,
    )
```

### 8.2 Bidirectional Flow

```
Mind Layer (self.mind.*)
        │
        │ Quality gradients
        ▼
    ╔═══════════════╗
    ║   MEMBRANE    ║  ◀── Somatic constraints affect quality costs
    ╚═══════════════╝
        │
        │ Resource demands
        ▼
Body Layer (self.body.*)
```

When the body is stressed, the Semiotic Membrane increases quality thresholds—it's harder to produce high-quality output when the body is struggling.

---

## 9. Principles Alignment

| Principle | How Proprioception Aligns |
|-----------|---------------------------|
| **Ethical** | Transparent sensing; no hidden metrics |
| **Joy-Inducing** | `self.body.strain` feels natural, not bureaucratic |
| **Composable** | Integrates with MORPHEUS QualityManifold |
| **AGENTESE** | No view from nowhere; observer feels their own body |

---

*"To know the body is to feel the body; to query is not to know."*
