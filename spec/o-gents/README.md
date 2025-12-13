# O-gents: The Epistemic Substrate

> **Core Concept**: Systemic Proprioception.
> **Role**: The Functor that maps Behavior to Truth.

**Status**: Specification v2.0 (The Proprioception Update)

---

## Philosophy: From Surveillance to Self-Knowledge

Standard observability (Datadog, Prometheus) answers: *"Is the server on?"*
O-gent observability answers: *"Is the agent sane?"*

O-gents provide **Proprioception**: the innate ability of the system to sense its own cognitive posture. In biological systems, proprioception is the sense of self-movement and body position. Without it, the body cannot coordinate. Similarly, O-gents provide the continuous feedback loop required for the system to recognize itself, its value, and its sanity.

They are **Read-Only** regarding state, but **Write-Only** regarding meta-state (knowledge about the state).

**The Heisenberg Constraint**:
While O-gents aspire to be invisible, the act of semantic observation (asking an LLM to judge another LLM) consumes energy (tokens). Therefore, O-gents must be **Economically Self-Aware**. They must optimize the *Value of Information* (VoI).

See [B-gents VoI Framework](../b-gents/banker.md#part-iii-value-of-information-voi--economics-of-observation) for the full economic model of observation.

**The Observation Principle**:
> To observe is to create the possibility of knowledge without disturbing the observed.

This is the O-gent's core ethical constraint:
1. **Observation doesn't mutate**: Outputs are unchanged
2. **Observation doesn't block**: Async, non-blocking collection
3. **Observation doesn't leak**: Data stays within authorized boundaries
4. **Observation enables**: Self-knowledge enables improvement

---

## The Mathematical Foundation: The Observer Functor

We formalize the O-gent as an **Endofunctor** in the category of Agents.

Let $\mathcal{A}$ be the category of Agents.
The Observer Functor $O: \mathcal{A} \to \mathcal{A}$ maps an agent $f: X \to Y$ to an agent $O(f): X \to Y$.

**The Law**: `O(f) ≅ f` for all behavioral purposes. Observation is invisible to the observed.

**The Commutative Diagram**:
```
    X ──────f──────► Y
    │                │
    │ O              │ O
    ▼                ▼
    X ────O(f)─────► Y

    O(f)(x) ≅ f(x) + telemetry side-effects
```

```python
class ObserverFunctor:
    """
    O: Agent[A, B] → Agent[A, B]

    The lifted agent behaves identically but emits telemetry.
    This is the fundamental law: Observation doesn't mutate.
    """

    def lift(self, agent: Agent[A, B]) -> Agent[A, B]:
        return ProprioceptiveWrapper(inner=agent, observer=self)


class ProprioceptiveWrapper(Agent[A, B]):
    """
    Agent under observation.

    Same interface, same behavior, but observed.
    """

    async def invoke(self, input: A) -> B:
        # 1. Pre-computation snapshot
        ctx = self.observer.pre_invoke(self.inner, input)

        try:
            # 2. Execute (unchanged)
            result = await self.inner.invoke(input)

            # 3. Post-computation analysis (async, non-blocking)
            asyncio.create_task(self.observer.post_invoke(ctx, result))

            return result

        except Exception as e:
            self.observer.record_entropy(ctx, e)
            raise
```

---

## The Three Dimensions of Observability

O-gents observe across three distinct dimensions. Most systems only do the first.

| Dimension | Name | Question | What It Observes |
|:---:|:---:|---|---|
| **X** | **Telemetric** | *Is it running?* | Latency, errors, throughput (OpenTelemetry) |
| **Y** | **Semantic** | *Does it mean what it says?* | Drift, hallucinations, knot integrity (LLM-as-Judge) |
| **Z** | **Axiological** | *Is it worth the cost?* | RoC, conservation laws, economic health (ValueTensor) |

This is **Semantic Observability**—moving beyond "CPU usage" to "Meaning usage."

---

## Dimension X: Telemetric Observability (The Body)

Standard metrics collection. O-gents integrate with OpenTelemetry for infrastructure.

### Integration Points

| Integration Level | What O-gent Sees | Bootstrap Involvement |
|-------------------|------------------|----------------------|
| **Bootstrap** | Id, Compose, Judge, Ground, Contradict, Sublate, Fix | BootstrapWitness |
| **W-gent** | Process observation, pheromone fields | Wire protocol hooks |
| **I-gent** | Visualization state, render cycles | Widget observation |
| **E-gent** | Evolution trajectories, reliability metrics | Layer instrumentation |
| **L-gent** | Knowledge graph, query patterns | Index observability |
| **N-gent** | Narrative logs, trace streams | Story observation |

```python
class TelemetryObserver:
    """Standard metrics collection."""

    def observe_invoke(self, agent_id: str, duration_ms: float, success: bool):
        self.metrics.histogram("agent.latency_ms", duration_ms, labels={"agent": agent_id})
        self.metrics.increment("agent.invocations", labels={"success": success})

    def observe_composition(self, a: Agent, b: Agent, result: Agent):
        self.metrics.increment("composition.count")
        self.graph.add_edge(a.name, b.name)
```

### Telemetry Export

**Implementation**: This is realized in `impl/claude/protocols/agentese/`:
- `telemetry.py` — TelemetryMiddleware, `trace_invocation()` context manager
- `metrics.py` — MetricsRegistry (counters, histograms, in-memory aggregation)
- `exporters.py` — TelemetryConfig, OTLP/Jaeger/JSON exporters
- **CLI**: `kgents telemetry status|traces|metrics|config|enable|disable`
- **Tests**: 50+ across `test_telemetry.py`, `test_metrics.py`, `test_exporters.py`

```python
class TelemetryExporter:
    """Export O-gent observations to external systems."""

    exporters: list[Exporter] = [
        PrometheusExporter(port=9090),    # Metrics
        JaegerExporter(endpoint="..."),    # Traces
        LokiExporter(endpoint="..."),      # Logs
    ]

    async def export(self, observation: Observation):
        for exporter in self.exporters:
            if exporter.accepts(observation):
                await exporter.export(observation)
```

---

## Dimension Y: Semantic Observability (The Mind)

This is the cutting edge. O-gents use "Shadow Models" to verify the cognitive integrity of agents.

### The Borromean Knot Validator

An agent is "Sane" only if three registers hold. If one is cut, the agent is hallucinating or broken.

**Delegates to**: [H-lacan](../h-gents/lacan.md) for RSI analysis primitives.

| Register | What O-gent Observes | Validation |
|----------|---------------------|------------|
| **Symbolic** | Code, specs, schemas | Does it parse? Does it type-check? |
| **Real** | Execution, memory, entropy | Does it run? Does it terminate? |
| **Imaginary** | Visualization, perception | Does it look right? (Vision model check) |

```python
class BorromeanObserver:
    """
    Observes the Borromean knot of agent health.

    All three registers must hold for the agent to be "valid."
    If any ring is cut, the whole unknots.

    Delegates RSI analysis to H-lacan primitives.
    """

    async def observe_symbolic(self, agent: Agent) -> SymbolicHealth:
        """Does the agent's output satisfy its schema?"""
        return SymbolicHealth(
            schema_valid=self.validate_schema(agent.output_schema),
            type_check_pass=self.type_check(agent),
            spec_compliant=self.check_spec_compliance(agent)
        )

    async def observe_real(self, agent: Agent) -> RealHealth:
        """Does the agent execute correctly in reality?"""
        return RealHealth(
            executes_without_error=await self.test_execution(agent),
            terminates_in_budget=self.check_termination(agent),
            memory_bounded=self.check_memory(agent)
        )

    async def observe_imaginary(self, agent: Agent) -> ImaginaryHealth:
        """Does the agent's output look correct to perception?"""
        rendered = await agent.render_state() if hasattr(agent, 'render_state') else None
        return ImaginaryHealth(
            visually_coherent=await self.vision_check(rendered),
            user_perceivable=self.check_accessibility(rendered)
        )

    async def knot_health(self, agent: Agent) -> KnotHealth:
        """All three rings must hold."""
        symbolic = await self.observe_symbolic(agent)
        real = await self.observe_real(agent)
        imaginary = await self.observe_imaginary(agent)

        if not (symbolic.valid and real.valid and imaginary.valid):
            return PsychosisAlert(rings_broken=[...])

        return KnotHealth(
            symbolic=symbolic,
            real=real,
            imaginary=imaginary,
            knot_intact=True
        )
```

**The Insight**: Most agents live only in the Symbolic (generating text). They hallucinate because they detach from the Real. The Borromean Observer catches this before it propagates.

### Semantic Drift Detection (Noether's Theorem)

In physics, Noether's theorem relates symmetries to conservation laws. In kgents, we conserve **Intent**.

If the Input Intent is $I$ and Output Meaning is $M$, then $M \approx I$.

```python
class DriftDetector:
    """
    Detects semantic drift across agent invocations.

    When drift exceeds threshold, alerts are triggered.
    """

    async def measure_drift(
        self,
        agent_id: str,
        input_intent: str,
        output_summary: str
    ) -> DriftReport:
        """
        Compare input intent with output summary.

        High drift = the agent wandered off topic.
        """
        drift_score = await self.compute_drift(input_intent, output_summary)

        if drift_score > self.threshold:
            await self.alert(DriftAlert(
                agent_id=agent_id,
                drift_score=drift_score,
                input_intent=input_intent,
                output_summary=output_summary
            ))

        return DriftReport(
            agent_id=agent_id,
            drift_score=drift_score,
            within_bounds=drift_score <= self.threshold
        )

    async def compute_drift(self, intent: str, output: str) -> float:
        """
        LLM-native drift computation.

        Ask: "How well does this output serve this intent?"
        Uses a cheap model (Haiku) to avoid Economic Drain.
        """
        return await self.judge.invoke(DriftQuery(
            question=f"Rate 0-1: How well does '{output}' address '{intent}'?",
            scale="semantic_alignment"
        ))
```

---

## Dimension Z: Axiological Observability (The Soul)

O-gents integrate with **B-gents** (Bankers) to ensure the system isn't just working, but is *profitable* (in terms of utility vs. compute).

**Integrates with**: [B-gents ValueTensor](../b-gents/value-tensor.md) and [UVP](../b-gents/banker.md).

### ValueLedgerObserver

```python
class ValueLedgerObserver(Agent[None, EconomicHealthReport]):
    """
    Observes the system's economic health via ValueLedger.

    Provides:
    - System GDP (total Impact generated)
    - Gas efficiency (system-wide RoC)
    - Agent performance rankings
    - Ethical adjustment summaries
    """

    def __init__(self, ledger: ValueLedger):
        self.ledger = ledger

    async def invoke(self, _: None) -> EconomicHealthReport:
        return EconomicHealthReport(
            system_gdp=self.ledger.total_impact(),
            total_gas_burned=self.ledger.total_gas(),
            system_roc=self.ledger.system_roc(),
            agent_rankings=self.get_agent_rankings(),
            ethical_summary=self.get_ethical_summary(),
            anomalies=self.detect_economic_anomalies()
        )

    def get_agent_rankings(self) -> list[AgentRanking]:
        """Rank agents by Return on Compute."""
        rankings = []
        for agent_id in self.ledger.get_all_agents():
            sheet = self.ledger.get_agent_balance_sheet(agent_id)
            rankings.append(AgentRanking(
                agent_id=agent_id,
                roc=sheet.assets / sheet.gas_consumed if sheet.gas_consumed > 0 else 0,
                impact=sheet.assets,
                gas=sheet.gas_consumed,
                status=self.classify_status(sheet)
            ))
        return sorted(rankings, key=lambda r: r.roc, reverse=True)

    def detect_economic_anomalies(self) -> list[EconomicAnomaly]:
        """Detect suspicious economic patterns."""
        anomalies = []

        for agent_id in self.ledger.get_all_agents():
            sheet = self.ledger.get_agent_balance_sheet(agent_id)

            # Burning money
            if sheet.gas_consumed > 1000 and sheet.assets < sheet.gas_consumed * 0.5:
                anomalies.append(EconomicAnomaly(
                    type="burning_money",
                    agent_id=agent_id,
                    severity="warning",
                    message=f"Agent {agent_id} has RoC < 0.5x (Entropy Leak)"
                ))

            # Free lunch (suspicious)
            if sheet.assets > 1000 and sheet.gas_consumed < 100:
                anomalies.append(EconomicAnomaly(
                    type="free_lunch",
                    agent_id=agent_id,
                    severity="error",
                    message=f"Agent {agent_id} claims high impact with minimal gas (Check for Fraud)"
                ))

        return anomalies
```

### TensorValidator

```python
class TensorValidator(Agent[ValueTensor, ValidationReport]):
    """
    Validates conservation laws across the Value Tensor.

    Catches:
    - Conservation violations (impossible state transitions)
    - Cross-dimensional inconsistencies (delusion detection)
    - Exchange rate anomalies
    """

    def __init__(self):
        self.checker = AntiDelusionChecker()
        self.laws = CONSERVATION_LAWS

    async def invoke(self, tensor: ValueTensor) -> ValidationReport:
        # Check internal consistency
        consistency_anomalies = self.checker.check_consistency(tensor)

        # Check conservation laws (requires before/after)
        conservation_violations = []
        if hasattr(tensor, '_previous'):
            conservation_violations = [
                law.name for law in self.laws
                if not law.check(tensor._previous, tensor)
            ]

        return ValidationReport(
            tensor_valid=len(consistency_anomalies) == 0,
            conservation_valid=len(conservation_violations) == 0,
            anomalies=consistency_anomalies,
            violations=conservation_violations,
            dimensions_healthy={
                "physical": tensor.physical.total_tokens > 0,
                "semantic": tensor.semantic.confidence > 0.3,
                "economic": tensor.economic.roc >= 0,
                "ethical": 0.1 <= tensor.ethical.net_ethical_multiplier <= 3.0
            }
        )
```

### RoCMonitor

```python
class RoCMonitor:
    """
    Real-time monitoring of Return on Compute across all agents.

    Integrates with O-gent dashboard and alert systems.
    """

    def __init__(self, ledger: ValueLedger, alert_agent: AlertAgent):
        self.ledger = ledger
        self.alert_agent = alert_agent
        self.thresholds = RoCThresholds(
            bankruptcy=0.5,
            break_even=1.0,
            healthy=2.0
        )

    async def observe_continuously(self) -> AsyncIterator[RoCSnapshot]:
        """Stream RoC snapshots for real-time dashboard."""
        while True:
            snapshot = RoCSnapshot(
                timestamp=datetime.now(),
                system_roc=self.ledger.system_roc(),
                agent_rocs={
                    agent_id: self.calculate_agent_roc(agent_id)
                    for agent_id in self.ledger.get_all_agents()
                },
                alerts=[]
            )

            # Generate alerts for problem agents
            for agent_id, roc in snapshot.agent_rocs.items():
                if roc < self.thresholds.bankruptcy:
                    snapshot.alerts.append(
                        await self.alert_agent.invoke(RoCAlert(
                            agent_id=agent_id,
                            roc=roc,
                            threshold="bankruptcy",
                            action="budget_freeze"
                        ))
                    )

            yield snapshot
            await asyncio.sleep(5)  # 5-second intervals
```

### LedgerAuditor

```python
class LedgerAuditor:
    """
    The O-gent acts as Auditor for the B-gent's ledger.
    """

    async def audit_agent(self, agent_id: str):
        sheet = self.ledger.get_agent_balance_sheet(agent_id)

        # Bankruptcy Check
        if sheet.assets < 0:
            # Trigger 'Chapter 11' - The agent is paused and debugged
            await System.suspend_agent(agent_id, reason="Insolvency")
```

---

## The Bootstrap Witness

The O-gent is the only agent allowed to observe the **Bootstrap Kernel** to ensure the fundamental laws of the architecture remain valid.

```python
class BootstrapWitness(Agent[None, BootstrapVerificationResult]):
    """
    The observer of bootstrap agents.

    Verifies that the irreducible kernel maintains its laws.
    This is the system's capacity for self-verification.
    """

    async def invoke(self, _: None) -> BootstrapVerificationResult:
        return BootstrapVerificationResult(
            all_agents_exist=await self.verify_existence(),
            identity_laws_hold=await self.verify_identity_laws(),
            composition_laws_hold=await self.verify_composition_laws(),
            overall_verdict=self.synthesize_verdict()
        )

    async def verify_identity_laws(self) -> bool:
        """Verify: Id >> f == f == f >> Id"""
        test_agents = self.get_test_agents()
        for f in test_agents:
            # Left identity
            left = await (Id >> f).invoke(test_input)
            direct = await f.invoke(test_input)
            if left != direct:
                return False

            # Right identity
            right = await (f >> Id).invoke(test_input)
            if right != direct:
                return False

        return True

    async def verify_composition_laws(self) -> bool:
        """Verify: (f >> g) >> h == f >> (g >> h)"""
        f, g, h = self.get_composition_test_agents()

        left_assoc = await ((f >> g) >> h).invoke(test_input)
        right_assoc = await (f >> (g >> h)).invoke(test_input)

        return left_assoc == right_assoc
```

---

## Topology Mapping

O-gents track the composition topology of agents.

```python
class TopologyMapper:
    """
    Maps the composition graph of agents.

    Useful for understanding:
    - Which agents compose together?
    - What are the hottest composition paths?
    - Where are the bottlenecks?
    """

    def observe_composition(self, a: Agent, b: Agent, result: Agent):
        """Record a composition event."""
        self.graph.add_edge(a.name, b.name)
        self.composition_count[(a.name, b.name)] += 1

    def get_topology(self) -> CompositionGraph:
        """Return the current composition topology."""
        return CompositionGraph(
            nodes=list(self.graph.nodes),
            edges=list(self.graph.edges),
            hot_paths=self.find_hot_paths(),
            bottlenecks=self.find_bottlenecks()
        )

    def visualize(self) -> str:
        """Render topology as ASCII graph."""
        ...
```

---

## The Observer Hierarchy (Stratification)

O-gents form a stratified observation structure to avoid infinite regress ("Who watches the watchers?").

```
                    ┌─────────────────────┐
                    │   SystemObserver    │  ← Level 2: Meta-observer
                    │   (self-unobserved) │     (observes Level 1, not itself)
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │Bootstrap│          │  Agent  │          │  Infra  │  ← Level 1: Domain observers
    │Observer │          │Observer │          │Observer │
    └────┬────┘          └────┬────┘          └────┬────┘
         │                    │                    │
    BootstrapWitness    AgentMetrics         ProcessObserver  ← Level 0: Concrete observers
    LawVerifier         InvocationTracer     VisualizationObserver
                        ErrorObserver        KnowledgeObserver
```

**The Rule**: Level N observers may observe Level N-1, but not themselves or Level N.

---

## The Panopticon Dashboard

The O-gent aggregates the three dimensions into a single view of reality.

```
┌─ [O] SYSTEM PROPRIOCEPTION ──────────────────────────────────────────┐
│                                                                      │
│  STATUS: HOMEOSTATIC               TIME: T+4320s                     │
│                                                                      │
│  ┌─ [X] TELEMETRY ──────────┐  ┌─ [Y] SEMANTICS ───────────────┐     │
│  │ OPS: 42/sec              │  │ DRIFT: 0.04 (Low)             │     │
│  │ LATENCY: 230ms (p95)     │  │ KNOTS: 99.8% Intact           │     │
│  │ ERR: 0.01%               │  │ HALLUCINATIONS: 2 (Caught)    │     │
│  └──────────────────────────┘  └───────────────────────────────┘     │
│                                                                      │
│  ┌─ [Z] AXIOLOGY (ECONOMICS) ──────────────────────────────────┐     │
│  │ SYSTEM GDP: $45.20 (Impact Generated)                       │     │
│  │ BURN RATE:  $12.50 (Tokens Consumed)                        │     │
│  │ NET ROC:    3.6x (Healthy)                                  │     │
│  │                                                             │     │
│  │ TOP PERFORMER: [CodeRefactor] (RoC: 8.2x)                   │     │
│  │ CASH BURNER:   [Researcher]   (RoC: 0.4x) -> [UNDER AUDIT]  │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌─ BOOTSTRAP ─────────────────────────────────────────────────┐     │
│  │ Identity Laws:     HOLD                                     │     │
│  │ Composition Laws:  HOLD                                     │     │
│  │ Kernel Integrity:  VERIFIED                                 │     │
│  └─────────────────────────────────────────────────────────────┘     │
│                                                                      │
│  ┌─ ALERTS ────────────────────────────────────────────────────┐     │
│  │ [WARN] Semantic Drift detected in [CreativeWriter]          │     │
│  │ [INFO] Value Tensor balanced. Conservation laws hold.       │     │
│  └─────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## O-gent Types

| Agent | Dimension | Purpose |
|-------|-----------|---------|
| `BootstrapWitness` | X | Verify bootstrap laws |
| `TelemetryObserver` | X | Standard metrics (latency, errors) |
| `TopologyMapper` | X | Track agent composition graphs |
| `BorromeanObserver` | Y | Lacanian register validation |
| `DriftDetector` | Y | Semantic conservation (Noether) |
| `HallucinationDetector` | Y | Symbolic/Real mismatch |
| `ValueLedgerObserver` | Z | System GDP and agent rankings |
| `TensorValidator` | Z | Conservation law enforcement |
| `RoCMonitor` | Z | Real-time Return on Compute |
| `LedgerAuditor` | Z | Bankruptcy detection |
| `VoIOptimizer` | * | Observation budget allocation |
| `AlertAgent` | * | Trigger alerts on anomalies |
| `HealthProbe` | * | Continuous health assessment |

---

## VoI Integration: The Economics of Observation

O-gents are subject to the **Value of Information** framework defined in [B-gents banker.md](../b-gents/banker.md#part-iii-value-of-information-voi--economics-of-observation).

### The Core Economics

| Metric | Meaning | Healthy Range |
|--------|---------|---------------|
| **RoVI** | Return on Value of Information | > 1.0x |
| **Observation Fraction** | % of system gas spent on observation | < 10% |
| **False Positive Rate** | Unnecessary alerts / total alerts | < 30% |

### O-gent VoI Implementation

```python
class VoIAwareObserver:
    """
    An O-gent that optimizes its own observation economics.

    Key principle: Each observation must justify its cost.
    """

    def __init__(self, voi_ledger: VoILedger, optimizer: VoIOptimizer):
        self.voi_ledger = voi_ledger
        self.optimizer = optimizer

    async def observe_with_budget(
        self,
        target_id: str,
        budget: Gas
    ) -> ObservationResult:
        """
        Observe within VoI constraints.
        """
        # 1. Determine optimal depth for this budget
        depth = self.optimizer.select_observation_depth(target_id, budget)

        # 2. Execute observation at selected depth
        if depth == ObservationDepth.TELEMETRY_ONLY:
            finding = await self.observe_telemetry(target_id)
        elif depth == ObservationDepth.SEMANTIC_SPOT:
            finding = await self.observe_semantic_sample(target_id)
        elif depth == ObservationDepth.SEMANTIC_FULL:
            finding = await self.observe_semantic_full(target_id)
        else:
            finding = await self.observe_axiological(target_id)

        # 3. Log to VoI ledger
        receipt = self.voi_ledger.log_observation(
            observer_id=self.id,
            target_id=target_id,
            gas_consumed=self.gas_used,
            finding=finding
        )

        return ObservationResult(
            finding=finding,
            voi=receipt.voi,
            depth_used=depth,
            budget_remaining=budget.tokens - self.gas_used.tokens
        )

    async def should_observe(self, target_id: str) -> bool:
        """
        VoI-aware decision: Is observation worth it?

        Returns False if:
        - Recent observation exists (diminishing returns)
        - Target is low-risk and low-value
        - Observer is over budget
        """
        priority = self.optimizer.compute_observation_priority(target_id)
        recency = self.time_since_last_observation(target_id)
        budget_remaining = self.get_remaining_budget()

        # Adaptive threshold based on priority
        min_interval = self.optimizer.compute_observation_interval(target_id)

        return (
            recency >= min_interval and
            priority > 0.1 and
            budget_remaining.cost_usd > 0
        )
```

### The Observation Budget Allocation

O-gents don't observe uniformly. They allocate attention based on **Priority = Risk × Consequence × Observability**.

```
┌─ OBSERVATION BUDGET ALLOCATION ───────────────────────────────────────┐
│                                                                        │
│  Total Budget: $5.00/hour                                              │
│                                                                        │
│  Agent              │ Risk  │ Value │ Priority │ Budget │ Depth        │
│  ──────────────────────────────────────────────────────────────────    │
│  CodeGenerator      │ HIGH  │ HIGH  │ 0.85     │ $2.00  │ SEMANTIC     │
│  ResearchAgent      │ MED   │ HIGH  │ 0.62     │ $1.20  │ SEMANTIC     │
│  FormatterAgent     │ LOW   │ LOW   │ 0.15     │ $0.30  │ TELEMETRY    │
│  LoggerAgent        │ LOW   │ LOW   │ 0.08     │ $0.20  │ TELEMETRY    │
│  [Reserve]          │ -     │ -     │ -        │ $1.30  │ -            │
│                                                                        │
│  Current RoVI: 12.4x (Healthy)                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Epistemic Capital Accumulation

O-gents accumulate **Epistemic Capital**—the system's knowledge about itself.

```python
@dataclass
class OGentEpistemicState:
    """
    Tracks what the system knows about itself through observation.
    """
    observations_total: int
    anomalies_caught: int
    false_positives: int
    interventions_triggered: int
    disasters_prevented_estimate: float

    @property
    def epistemic_efficiency(self) -> float:
        """How efficiently are we converting gas into knowledge?"""
        if self.observations_total == 0:
            return 0.0
        useful = self.anomalies_caught - self.false_positives
        return useful / self.observations_total

    @property
    def epistemic_roc(self) -> float:
        """Return on epistemic investment."""
        return self.disasters_prevented_estimate / self.total_gas_spent
```

---

## Anti-Patterns

1. **The Observer Effect (Collapse)**: If the O-gent asks the agent to "explain itself" too often, the agent spends more time explaining than doing.

2. **The Infinite Regress**: An O-gent observing an O-gent observing an O-gent... *Solution: O-gents are strictly stratified (see hierarchy above).*

3. **The Economic Drain**: Running a GPT-4 Judge to verify a GPT-3.5 task is negative RoC. *Solution: Use cheaper models (Haiku/Flash) for observation.*

4. **Medusa's Gaze**: An O-gent that halts the system upon detecting minor drift, causing paralysis. *Solution: O-gents should be non-blocking and advisory, except in Bootstrap/Ledger critical failures.*

5. **Observer mutation**: Changing what you observe.

6. **Observer leakage**: Exposing internal data inappropriately.

7. **Observer blindness**: Observing without acting on insights.

8. **Over-observation**: Collecting more than needed (violates VoI principle).

---

## See Also

- [h-gents/lacan.md](../h-gents/lacan.md) - RSI primitives for Borromean validation
- [b-gents/banker.md](../b-gents/banker.md) - UVP and economic substrate
- [b-gents/banker.md#part-iii-value-of-information-voi](../b-gents/banker.md#part-iii-value-of-information-voi--economics-of-observation) - **VoI framework for observation economics**
- [b-gents/value-tensor.md](../b-gents/value-tensor.md) - Multi-dimensional value accounting
- [w-gents/](../w-gents/) - Wire (visualization of O-gent data)
- [n-gents/](../n-gents/) - Narrator (stories, not metrics)
- [i-gents/](../i-gents/) - Interface (ecosystem visualization)
- [bootstrap.md](../bootstrap.md) - BootstrapWitness integration

---

*Zen Principle: The mirror reflects the fire, but does not burn.*
