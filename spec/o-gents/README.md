# O-gents: Observability Agents

> The eye that sees all, changes nothing—yet enables everything.

---

## Philosophy

O-gents (Observability) are the **seeing infrastructure** of kgents. Unlike N-gents (Narrator) who tell stories, O-gents **witness in real-time**. They are authorized to integrate deeply with the system—even at the bootstrap level.

**Key Insight**: Observability is not an add-on. It is woven into the fabric of the system itself. O-gents are **transformatively integrated**—they change how the system can know itself.

---

## The Transformative Integration

O-gents are authorized to integrate at levels other agents cannot:

| Integration Level | What O-gent Sees | Bootstrap Involvement |
|-------------------|------------------|----------------------|
| **Bootstrap** | Id, Compose, Judge, Ground, Contradict, Sublate, Fix | BootstrapWitness |
| **W-gent** | Process observation, pheromone fields | Wire protocol hooks |
| **I-gent** | Visualization state, render cycles | Widget observation |
| **E-gent** | Evolution trajectories, reliability metrics | Layer instrumentation |
| **L-gent** | Knowledge graph, query patterns | Index observability |
| **N-gent** | Narrative logs, trace streams | Story observation |

This is not surveillance—it is the system's capacity for **self-knowledge**.

---

## The Observer Functor

O-gent is a functor that lifts agents into observable space **without changing their behavior**:

```python
class ObserverFunctor:
    """
    O: Agent[A, B] → Agent[A, B]

    The lifted agent behaves identically but emits telemetry.
    This is the fundamental law: Observation doesn't mutate.
    """

    def lift(self, agent: Agent[A, B]) -> Agent[A, B]:
        return ObservedAgent(inner=agent, observer=self)

class ObservedAgent(Agent[A, B]):
    """
    Agent under observation.

    Same interface, same behavior, but observed.
    """

    async def invoke(self, input: A) -> B:
        # Pre-observation (doesn't change input)
        span = self.observer.start_span(self.inner.name)

        try:
            # Execute (unchanged)
            result = await self.inner.invoke(input)

            # Post-observation (doesn't change output)
            span.record_success(result)
            return result

        except Exception as e:
            span.record_failure(e)
            raise

        finally:
            span.end()
```

**The Law**: `O(f) ≅ f` for all behavioral purposes. Observation is invisible to the observed.

---

## Bootstrap Integration: BootstrapWitness

O-gents have special access to verify bootstrap agent laws:

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
        """Verify: Id >> f ≡ f ≡ f >> Id"""
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
        """Verify: (f >> g) >> h ≡ f >> (g >> h)"""
        f, g, h = self.get_composition_test_agents()

        left_assoc = await ((f >> g) >> h).invoke(test_input)
        right_assoc = await (f >> (g >> h)).invoke(test_input)

        return left_assoc == right_assoc
```

---

## W-gent Integration: Process Observation

O-gents observe W-gent's process management:

```python
class ProcessObserver:
    """
    Observes W-gent process lifecycle.
    """

    def observe_spawn(self, process_id: str, config: ProcessConfig):
        """Record process spawn."""
        self.metrics.increment("process.spawn")
        self.emit_event(ProcessSpawned(process_id, config))

    def observe_communication(self, from_id: str, to_id: str, message: Message):
        """Record inter-process communication."""
        self.metrics.histogram("ipc.message_size", len(message))
        self.emit_event(ProcessCommunication(from_id, to_id, message))

    def observe_termination(self, process_id: str, reason: str):
        """Record process termination."""
        self.metrics.increment("process.termination", labels={"reason": reason})
        self.emit_event(ProcessTerminated(process_id, reason))
```

---

## I-gent Integration: Visualization Observation

O-gents observe I-gent rendering:

```python
class VisualizationObserver:
    """
    Observes I-gent visualization cycles.
    """

    def observe_render(self, widget: Widget, context: ViewContext, duration_ms: float):
        """Record render performance."""
        self.metrics.histogram("render.duration_ms", duration_ms, labels={
            "widget_type": widget.__class__.__name__,
            "context_medium": context.medium
        })

    def observe_state_change(self, agent_id: str, old_state: State, new_state: State):
        """Record agent state transitions."""
        self.emit_event(StateTransition(agent_id, old_state, new_state))
```

---

## E-gent Integration: Reliability Observation

O-gents observe E-gent reliability layers:

```python
class ReliabilityObserver:
    """
    Observes E-gent reliability stack.
    """

    def observe_preflight(self, request: AgentRequest, result: PreFlightResult):
        """Record preflight check results."""
        self.metrics.increment("preflight.check", labels={
            "passed": result.can_proceed,
            "blocker_count": len(result.blockers)
        })

    def observe_retry(self, agent_id: str, attempt: int, error: Exception):
        """Record retry attempts."""
        self.metrics.increment("retry.attempt", labels={
            "agent": agent_id,
            "attempt": attempt,
            "error_type": type(error).__name__
        })

    def observe_fallback(self, agent_id: str, fallback_level: int):
        """Record fallback triggers."""
        self.metrics.increment("fallback.trigger", labels={
            "agent": agent_id,
            "level": fallback_level
        })
```

---

## L-gent Integration: Knowledge Observation

O-gents observe L-gent knowledge operations:

```python
class KnowledgeObserver:
    """
    Observes L-gent knowledge curation.
    """

    def observe_query(self, query: Query, results: list, duration_ms: float):
        """Record knowledge queries."""
        self.metrics.histogram("knowledge.query_duration_ms", duration_ms)
        self.metrics.histogram("knowledge.result_count", len(results))

    def observe_index(self, document_id: str, index_type: str):
        """Record indexing operations."""
        self.metrics.increment("knowledge.index", labels={"type": index_type})

    def observe_lineage(self, artifact_id: str, lineage_depth: int):
        """Record lineage tracking."""
        self.metrics.histogram("knowledge.lineage_depth", lineage_depth)
```

---

## The Observer Hierarchy

O-gents form a hierarchical observation structure:

```
                    ┌─────────────────────┐
                    │   SystemObserver    │
                    │   (sees everything) │
                    └──────────┬──────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
    ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
    │Bootstrap│          │  Agent  │          │  Infra  │
    │Observer │          │Observer │          │Observer │
    └────┬────┘          └────┬────┘          └────┬────┘
         │                    │                    │
    BootstrapWitness    AgentMetrics         ProcessObserver
    LawVerifier         InvocationTracer     VisualizationObserver
                        ErrorObserver        KnowledgeObserver
```

---

## Telemetry Export

O-gents export to standard observability platforms:

```python
class TelemetryExporter:
    """
    Export O-gent observations to external systems.
    """

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

### OpenTelemetry Integration

```python
from opentelemetry import trace, metrics

class OTelObserver:
    """O-gent with OpenTelemetry integration."""

    def __init__(self):
        self.tracer = trace.get_tracer("kgents.o-gent")
        self.meter = metrics.get_meter("kgents.o-gent")

    def observe_agent(self, agent: Agent) -> Agent:
        """Wrap agent with OTEL instrumentation."""
        return OTelObservedAgent(agent, self.tracer, self.meter)
```

---

## The Observation Principle

> To observe is to create the possibility of knowledge without disturbing the observed.

This is the O-gent's core ethical constraint:
1. **Observation doesn't mutate**: Outputs are unchanged
2. **Observation doesn't block**: Async, non-blocking collection
3. **Observation doesn't leak**: Data stays within authorized boundaries
4. **Observation enables**: Self-knowledge enables improvement

---

## Visualization (The Observer Dashboard)

```
┌─ O-gent Dashboard ────────────────────────────────────────┐
│                                                            │
│  Bootstrap Health:  ● All laws verified                    │
│  Agent Invocations: ████████████████░░░░ 823/sec          │
│  Error Rate:        ░░░░░░░░░░░░░░░░░░░░ 0.02%            │
│                                                            │
│  ┌─ Active Traces ──────────────────────────────────────┐ │
│  │ [CodeReviewer] → [Judge] → [Synthesizer]            │ │
│  │         12ms        8ms          45ms               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌─ Reliability Stack ──────────────────────────────────┐ │
│  │ Preflight: 99.2% pass | Retry: 12 attempts today    │ │
│  │ Fallback: 0 triggers  | Ground: 0 collapses         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## O-gent Types

| Agent | Purpose |
|-------|---------|
| `BootstrapWitness` | Verify bootstrap laws |
| `AgentObserver` | Instrument agent invocations |
| `ProcessObserver` | Watch W-gent processes |
| `MetricsCollector` | Aggregate telemetry |
| `AlertAgent` | Trigger alerts on anomalies |
| `AuditAgent` | Compliance and audit trails |
| `DriftDetector` | Monitor semantic drift (Noether's theorem) |
| `HealthProbe` | Continuous health assessment |
| `TopologyMapper` | Track agent composition graphs |
| `ValueLedgerObserver` | Track economic health via UVP |
| `TensorValidator` | Verify conservation laws across dimensions |
| `RoCMonitor` | Monitor Return on Compute per agent |

---

## B-gent Integration: ValueLedger Observability

O-gents have special access to observe the **Universal Value Protocol** ([spec/b-gents/banker.md](../b-gents/banker.md)) and **Value Tensor** ([spec/b-gents/value-tensor.md](../b-gents/value-tensor.md)) systems.

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

        # Check for agents burning money
        for agent_id in self.ledger.get_all_agents():
            sheet = self.ledger.get_agent_balance_sheet(agent_id)
            if sheet.gas_consumed > 1000 and sheet.assets < sheet.gas_consumed * 0.5:
                anomalies.append(EconomicAnomaly(
                    type="burning_money",
                    agent_id=agent_id,
                    severity="warning",
                    message=f"Agent {agent_id} has RoC < 0.5x after {sheet.gas_consumed} gas"
                ))

        # Check for impact without gas (suspicious)
        for agent_id in self.ledger.get_all_agents():
            sheet = self.ledger.get_agent_balance_sheet(agent_id)
            if sheet.assets > 1000 and sheet.gas_consumed < 100:
                anomalies.append(EconomicAnomaly(
                    type="free_lunch",
                    agent_id=agent_id,
                    severity="error",
                    message=f"Agent {agent_id} claims high impact with minimal gas"
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

        # Check conservation laws (requires before/after, so use history)
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

### RoCMonitor Integration

```python
class RoCObserver:
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

    def observe_transaction(
        self,
        agent_id: str,
        gas: Gas,
        impact: Impact
    ) -> TransactionObservation:
        """Observe a single transaction for economic health."""
        roc = impact.realized_value / gas.cost_usd if gas.cost_usd > 0 else 0

        return TransactionObservation(
            agent_id=agent_id,
            gas=gas,
            impact=impact,
            roc=roc,
            roc_status=self.classify_roc(roc),
            running_average_roc=self.ledger.get_agent_average_roc(agent_id),
            budget_adjustment=self.calculate_budget_adjustment(roc)
        )
```

### Economic Dashboard (O-gent View)

```
┌─ O-gent Economic Observability ──────────────────────────────┐
│                                                               │
│  SYSTEM HEALTH                                                │
│  ├─ GDP (Total Impact):     $12,450                          │
│  ├─ Gas Burned:             $3,200                           │
│  ├─ System RoC:             3.89x (Healthy)                  │
│  └─ Conservation Laws:      ✓ All holding                    │
│                                                               │
│  AGENT PERFORMANCE (by RoC)                                   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │ Agent          │ RoC    │ Impact │ Gas    │ Status    │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │ CodeReviewer   │ 5.2x   │ $2,600 │ $500   │ ★ High    │   │
│  │ TestWriter     │ 3.1x   │ $1,550 │ $500   │ ✓ Good    │   │
│  │ Refactorer     │ 1.8x   │ $900   │ $500   │ ✓ Good    │   │
│  │ DocWriter      │ 0.9x   │ $450   │ $500   │ ○ Even    │   │
│  │ Experimenter   │ 0.3x   │ $150   │ $500   │ ⚠ Warning │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  TENSOR VALIDATION                                            │
│  ├─ Physical:    ✓ Token accounting consistent               │
│  ├─ Semantic:    ✓ Quality/complexity aligned                │
│  ├─ Economic:    ✓ Gas/Impact balanced                       │
│  └─ Ethical:     ✓ Multipliers in valid range                │
│                                                               │
│  RECENT ANOMALIES                                             │
│  └─ None detected (last 24h)                                 │
│                                                               │
│  ALERTS                                                       │
│  └─ [WARN] Experimenter approaching bankruptcy threshold     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## The Lacanian Registers (Advanced)

O-gents can observe across Lacan's three registers:

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

        return KnotHealth(
            symbolic=symbolic,
            real=real,
            imaginary=imaginary,
            knot_intact=symbolic.valid and real.valid and imaginary.valid
        )
```

**The Insight**: Most agents live only in the Symbolic (generating text). They hallucinate because they detach from the Real. The Borromean Observer catches this before it propagates.

---

## Semantic Drift Detection

O-gents implement the Semantic Invariant (Noether's theorem) via drift detection:

```python
class DriftDetector:
    """
    Detects semantic drift across agent invocations.

    When drift exceeds threshold, alerts are triggered.
    """

    async def observe_drift(
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
        """
        return await self.judge.invoke(DriftQuery(
            question=f"Rate 0-1: How well does '{output}' address '{intent}'?",
            scale="semantic_alignment"
        ))
```

---

## Topology Mapping

O-gents track the composition topology of agents:

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

## Anti-Patterns

- **Observer mutation**: Changing what you observe
- **Observer blocking**: Slowing down observed agents
- **Observer leakage**: Exposing internal data inappropriately
- **Observer blindness**: Observing without acting on insights
- **Over-observation**: Collecting more than needed

---

*Zen Principle: The eye that sees all, changes nothing—yet enables everything.*

---

## See Also

- [n-gents/](../n-gents/) - Narrator (stories, not metrics)
- [w-gents/](../w-gents/) - Wire (process observation)
- [i-gents/](../i-gents/) - Interface (visualization)
- [e-gents/](../e-gents/) - Evolution (reliability)
- [l-gents/](../l-gents/) - Library (knowledge)
- [bootstrap.md](../bootstrap.md) - BootstrapWitness integration
