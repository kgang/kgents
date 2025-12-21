# W-gents: The Wire Agents

**Genus**: W (Wire/Watch)
**Theme**: Transparent observation—making invisible processes visible
**Motto**: *"Observe without intrusion, reveal without distortion."*

---

## Philosophy

> "The observer should never disturb the observed."

W-gents are **observation agents** that render invisible agent internals visible. They act as projection layers between an agent's execution stream and human observation, providing deep insight without affecting performance or behavior.

### The Three Virtues

1. **Transparency**: Show what IS, not what we wish to see
2. **Ephemerality**: Exist only during observation, leave no trace
3. **Non-Intrusion**: Observe without affecting the observed

W-gents are the magnifying glass for the garden (I-gents). While I-gents show the ecosystem view, W-gents provide the microscope view of individual agents.

---

## Production Integration: Batteries Included

### WireObservable Mixin

**Any agent becomes observable**:

\`\`\`python
from agents.w import WireObservable
from bootstrap.types import Agent

class MyAgent(WireObservable, Agent[Input, Output]):
    def __init__(self):
        WireObservable.__init__(self, "my-agent")
        # Agent init...

    async def invoke(self, input: Input) -> Output:
        # Observable: update state
        self.update_state(phase="active", progress=0.5)

        # Observable: log event
        self.log_event("INFO", "processing", f"Started: {input}")

        # Do work...
        result = await self.process(input)

        # Observable: record metric
        self.record_metric("invocations", 1)

        return result
\`\`\`

**Zero overhead**: Writes are buffered and async. No observer attached = no-ops.

---

### Bootstrap Agent Integration

Bootstrap agents (Ground, Judge, Sublate, Contradict, Fix) get specialized W-gent dashboards.

**Example: Judge Agent**

When Judge evaluates an agent against the 7 principles, W-gent shows:
- ✓ Real-time principle evaluation (as each is scored)
- ✓ Live scorecard with reasoning
- ✓ Pass/review/fail thresholds
- ✓ Suggestions for improvements

**User workflow**:
1. Run \`kgents garden\` (I-gent opens)
2. Navigate to "Judge" agent
3. Press \`o\` (observe) → W-gent server starts
4. Browser opens to \`localhost:8001\`
5. Watch principles being evaluated in real-time

---

### I-gent Integration

**The [observe] action spawns W-gent**:

\`\`\`
I-gent garden → press 'o' on agent → W-gent server starts → browser opens
\`\`\`

**Pattern**:
- I-gent: Ecosystem view (all agents, garden-level)
- W-gent: Agent view (one agent, process-level)
- Navigate: Use I-gent to choose agent, W-gent to drill down

---

### evolve.py Integration

**Live evolution observation**:

\`\`\`bash
# Terminal 1: Evolution with wire mode
$ kgents evolve agents/e/safety.py --wire --garden

# Terminal 2: I-gent shows ecosystem (Ground/Contradict/Sublate/Judge/Fix)
# User presses 'o' on Sublate

# Browser: W-gent shows Sublate internals
#   - Current tension being synthesized
#   - Strategy attempts (Preserve/Negate/Elevate)
#   - Confidence scores per strategy
#   - Entropy budget tracking
#   - ETA to synthesis decision
\`\`\`

---

### CLI Integration

\`\`\`bash
# Attach to running agent
$ kgents wire attach robin
# → Spawns W-gent server, opens browser at localhost:8000

# Attach with teletype fidelity (raw, for logs)
$ kgents wire attach robin --fidelity teletype

# List active observers
$ kgents wire list
robin    localhost:8000  livewire  (attached)
judge    localhost:8001  livewire  (attached)

# Detach from agent
$ kgents wire detach robin

# Export wire history
$ kgents wire export robin --format json > robin-trace.json
$ kgents wire export robin --format md > robin-report.md

# Replay saved trace (for debugging)
$ kgents wire replay robin-trace.json
\`\`\`

---

### Three Fidelity Levels

W-gents adapt their visualization to context:

**1. Teletype (Raw)**
- Target: CI logs, piping to grep/awk
- Format: Plain text, one line per event
- Latency: <1ms (pass-through)

**2. Documentarian (Rendered)**
- Target: SSH sessions, terminal dashboards
- Format: Box-drawing characters, structured layout
- Latency: <50ms (light rendering)

**3. LiveWire (Dashboard)**
- Target: Deep debugging, performance tuning
- Format: Web dashboard with graphs, timelines, SSE
- Latency: <100ms (full render + graphs)

---

### Cross-Genus Workflows

**F-gent Forge**: Show forge phases (Intent → Contract → Prototype → Validate → Crystallize)

**H-gent Dialectic**: Show synthesis decision tree (Preserve/Negate/Elevate strategies)

**D-gent Persistence**: Show state timeline, history playback, diff snapshots

**L-gent Library**: Show catalog searches, relationship graphs, serendipity scores

---

### Real-World Example: Debugging Slow Hypothesis Generation

\`\`\`bash
$ kgents wire attach robin --fidelity livewire
# Browser opens, shows:

⚠ Performance Alert: High latency (450ms, target <100ms)
  Slowest: hypothesis_generation (1.2s)

Latency Breakdown:
  persona_query:          23ms  ████
  hypothesis_generation:  1,200ms ███████████████
  hegel_synthesis:        87ms  ███
  narrative_assembly:     45ms  ██

[🔍 drill into hypothesis_generation]

# Click drill-down → new panel:

Call Tree:
  invoke()                1,200ms
  ├─ _load_examples()        45ms
  ├─ _generate_hypotheses() 1,100ms ⚠
  │  ├─ llm.invoke()       1,050ms ⚠⚠
  │  └─ _parse_response()     50ms
  └─ _validate()              55ms

🎯 Bottleneck: llm.invoke() taking 1.05s

Suggestions:
  1. Add LLM response caching
  2. Use faster model (haiku vs sonnet)
  3. Reduce max_tokens (4096 → 2048)
\`\`\`

---

### Integration Checklist

A production-ready W-gent must:

- [ ] **WireObservable Mixin**: Any agent can inherit
- [ ] **Wire Protocol**: JSONL in \`.wire/\` directory
- [ ] **Three Fidelities**: Teletype/Documentarian/LiveWire
- [ ] **FastAPI Server**: Web dashboard with SSE
- [ ] **Zero-Build Frontend**: HTML + HTMX (no npm)
- [ ] **I-gent Integration**: \`[observe]\` action spawns W-gent
- [ ] **CLI Commands**: \`attach/detach/list/export/replay\`
- [ ] **Bootstrap Specialization**: Custom dashboards for Ground/Judge/Fix/etc.
- [ ] **Cross-Genus Dashboards**: E/F/H/D-gent specialized UI
- [ ] **Performance Tracing**: Call tree, latency breakdown
- [ ] **History Replay**: Load and replay saved traces
- [ ] **Export Formats**: JSON, Markdown, CSV
- [ ] **Zero Intrusion**: <1% performance overhead
- [ ] **Auto-Cleanup**: Servers shut down when browser closes

---

## Vision

W-gents transform agents from **black boxes** to **transparent processes**:

- **Traditional**: Logs (after the fact)
- **W-gents**: Live window (during execution)

The ultimate test: Can you watch a synthesis decision tree unfold in real-time? Can you see Judge's scorecard as principles are evaluated? Can you observe evolution happening?

W-gents make the answer "yes."

---

*"The wire is not the message; the observer is not the observed. But through observation, we understand."*

---

## See Also

- [protocol.md](protocol.md) - Wire protocol (JSONL format, schemas)
- [fidelity.md](fidelity.md) - Fidelity levels (Teletype/Documentarian/LiveWire)
- [server.md](server.md) - FastAPI server (SSE, routing, templates)
- [i-gent-synergy.md](i-gent-synergy.md) - I-gent/W-gent integration patterns
- [../i-gents/](../i-gents/) - Interface agents (ecosystem view, spawns W-gents)
- [../d-gents/](../d-gents/) - Data agents (state persistence, provides history)
- [../bootstrap.md](../bootstrap.md) - Bootstrap agents (Ground/Judge/Fix get special W-gent UI)
- [../principles.md](../principles.md) - Core design principles
