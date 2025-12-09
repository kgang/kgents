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
