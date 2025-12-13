---
path: ideas/impl/developer-education
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Developer education guide for the kgents implementation.
  Quick starts, CLI reference, architecture overview, extension guides.
  Designed for Kent to quickly understand and extend the system.
---

# Developer Education Guide

> *"The best documentation is the one you don't have to read."*

**Audience**: Kent (primary developer)
**Goal**: Enable rapid understanding and extension of the system
**Format**: Progressive disclosure (quick start → deep dive)

---

## 60-Second Quick Start

```bash
# Install (if not already)
uv sync

# Check your soul
kg soul vibe

# Parse something
kg parse "analyze this text for meaning"

# Get a dialectical synthesis
kg dialectic "move fast" "don't break things"

# See agent composition
kg compose Ground >> Judge >> Sublate

# Get creative inspiration
kg oblique
```

That's it. You're using kgents.

---

## 5-Minute Overview

### What is kgents?

A specification and implementation for tasteful, ethical, joy-inducing AI agents.

### Key Concepts

| Concept | One-Liner |
|---------|-----------|
| **Agent Genus** | Letter-coded agent families (K, H, U, P, J, I...) |
| **AGENTESE** | Verb-first protocol for agent-world interaction |
| **Eigenvectors** | Six dimensions of Kent's cognitive personality |
| **Bootstrap Agents** | 7 core agents (Id, Compose, Judge, Ground, Contradict, Sublate, Fix) |
| **Flux** | Event streaming for agent coordination |

### The Agent Alphabet

```
A - Art/Creativity coaches
B - Economics/Distillation
C - Category Theory (composition)
D - Data/State
E - Evolution
H - Thinking (Hegel, Jung, Lacan)
I - Visualization
J - JIT Reality Classifier
K - Kent simulacra (soul)
M - Memory
N - Narrative
P - Parsing
T - Testing
U - Tools/MCP
```

### The Six Eigenvectors

```
Aesthetic:    0.15  (taste, beauty, craft)
Categorical:  0.20  (structure, types, composition)
Gratitude:    0.15  (appreciation, acknowledgment)
Heterarchy:   0.15  (non-hierarchical, network thinking)
Generativity: 0.20  (creation, emergence)
Joy:          0.15  (delight, play, humor)
```

---

## CLI Reference

### Soul Commands (K-gent)

```bash
# Get current soul vibe
kg soul vibe
# Output: { dominant: "categorical", confidence: 0.92, mood: "contemplative" }

# Detect eigenvector drift
kg soul drift
# Output: Drift detected in 'aesthetic' (+0.05 over 7 days)

# Find soul tensions
kg soul tense
# Output: Tension: categorical (0.20) vs joy (0.15)

# Query from Kent's perspective
kg soul ask "Should I refactor this?"
# Output: { perspective: "Kent would consider...", confidence: 0.85 }
```

### Parsing Commands (P-gent)

```bash
# Parse with confidence
kg parse "analyze this"
# Output: { intent: "analysis", confidence: 0.87, domain: "general" }

# Repair and parse broken input
kg repair "{ incomplete json"
# Output: { repaired: true, result: { ... }, confidence: 0.72 }
```

### Reality Classification (J-gent)

```bash
# Classify reality type
kg reality "The system crashed after deploy"
# Output: { reality: Reality.EMPIRICAL, evidence: ["crash", "deploy"] }

# Full analysis pipeline
kg analyze "optimize database queries"
# Output: Ground → Judge → Verdict pipeline result
```

### Thinking Commands (H-gent)

```bash
# Jungian shadow analysis
kg shadow "I hate legacy code"
# Output: { shadow: "perfectionism", projection: true, integration: "..." }

# Dialectical synthesis
kg dialectic "move fast" "don't break things"
# Output: { synthesis: "Move fast on reversible, careful on irreversible" }

# Lacanian gaps
kg gaps "I want to refactor everything"
# Output: { desire: "control", lack: "certainty", objet_a: "perfect code" }
```

### Visualization Commands (I-gent)

```bash
# Sparkline of metrics
kg sparkline --metric cpu --window 1h

# Weather report (system health)
kg weather

# Full dashboard
kg dash

# Living garden view
kg garden
```

### Composition Commands (A-gent)

```bash
# Compose agents
kg compose Ground >> Judge >> Sublate

# What-if exploration
kg whatif "merge these PRs together"

# Oblique strategy
kg oblique
# Output: "Honor thy error as a hidden intention"
```

### Cross-Pollination Commands

```bash
# Would Kent Approve?
kg approve "this code change"

# Full introspection (K + H pipeline)
kg introspect

# Memory as story
kg remember --as-story --days 7

# Ethical code review
kg review --ethical path/to/diff
```

---

## Architecture Overview

### Directory Structure

```
kgents/
├── spec/                    # Language specification
│   ├── protocols/
│   │   └── agentese.md      # AGENTESE spec
│   └── principles.md        # Core principles
│
├── impl/                    # Reference implementation
│   └── claude/
│       ├── agents/          # Agent implementations
│       │   ├── a/           # Art/Creativity
│       │   ├── h/           # Thinking (Hegel, Jung, Lacan)
│       │   ├── i/           # Visualization
│       │   ├── k/           # Kent simulacra
│       │   ├── p/           # Parsing
│       │   ├── t/           # Testing
│       │   └── u/           # Tools
│       │
│       ├── protocols/
│       │   ├── agentese/    # AGENTESE impl (559 tests)
│       │   │   ├── contexts/
│       │   │   │   ├── world.py
│       │   │   │   ├── self_.py
│       │   │   │   ├── concept.py
│       │   │   │   ├── void.py
│       │   │   │   └── time_.py
│       │   │   └── logos.py  # Central dispatch
│       │   │
│       │   └── cli/
│       │       └── handlers/ # CLI command handlers
│       │
│       └── flux/            # Event streaming
│
├── plans/                   # Planning documents
│   ├── skills/              # Reusable patterns
│   ├── ideas/               # Creative exploration
│   │   └── impl/            # Implementation plans
│   └── _forest.md           # Forest Protocol index
│
└── tests/                   # Test suites
    ├── unit/
    ├── property/
    ├── integration/
    ├── adversarial/
    └── dialectic/
```

### Data Flow

```
User Input
    ↓
CLI Handler (protocols/cli/handlers/*.py)
    ↓
AGENTESE Dispatch (protocols/agentese/logos.py)
    ↓
Context Resolution (world.*, self.*, concept.*, void.*, time.*)
    ↓
Agent Execution (agents/*/)
    ↓
Flux Event Stream (optional)
    ↓
Response Synthesis
    ↓
Output Formatting
```

### Key Files

| File | Purpose |
|------|---------|
| `logos.py` | Central AGENTESE dispatch |
| `handlers/soul.py` | Soul CLI commands |
| `agents/k/eigenvectors.py` | Eigenvector calculations |
| `agents/k/garden.py` | Memory garden |
| `agents/h/thinking.py` | Dialectical pipeline |
| `agents/i/widgets/` | TUI widget components |

---

## Extension Guide

### Adding a New CLI Command

1. **Create handler file**:
```python
# impl/claude/protocols/cli/handlers/mycommand.py
from impl.claude.protocols.cli.handlers.base import BaseHandler

class MyCommandHandler(BaseHandler):
    """Handle the mycommand CLI command."""

    async def handle(self, args: Namespace) -> int:
        # Implementation here
        result = await self.do_work(args)
        self.output(result)
        return 0
```

2. **Register in CLI**:
```python
# impl/claude/protocols/cli/__init__.py
from .handlers.mycommand import MyCommandHandler

HANDLERS = {
    # ... existing handlers
    "mycommand": MyCommandHandler,
}
```

3. **Add tests**:
```python
# tests/unit/test_mycommand.py
async def test_mycommand_basic():
    handler = MyCommandHandler()
    result = await handler.handle(args)
    assert result == 0
```

### Adding a New Agent

1. **Create agent directory**:
```
impl/claude/agents/x/
├── __init__.py
├── agent.py       # Main agent class
├── types.py       # Type definitions
└── _tests/
    └── test_x.py
```

2. **Implement agent class**:
```python
# impl/claude/agents/x/agent.py
from impl.claude.agents.base import BaseAgent

class XAgent(BaseAgent):
    """X-gent: Description of what it does."""

    async def invoke(self, input: XInput) -> XOutput:
        # Agent logic here
        return XOutput(...)
```

3. **Register with AGENTESE** (if needed):
```python
# impl/claude/protocols/agentese/contexts/self_.py
async def handle_self_x(path: str, umwelt: Umwelt) -> Any:
    """Handle self.x.* paths."""
    agent = XAgent()
    return await agent.invoke(...)
```

### Adding a New Widget

1. **Create widget file**:
```python
# impl/claude/agents/i/widgets/mywidget.py
from textual.widget import Widget

class MyWidget(Widget):
    """Description of widget."""

    def compose(self) -> ComposeResult:
        yield Static("Content")

    def on_mount(self) -> None:
        # Setup code
        pass
```

2. **Add to widget exports**:
```python
# impl/claude/agents/i/widgets/__init__.py
from .mywidget import MyWidget

__all__ = [..., "MyWidget"]
```

3. **Use in screen**:
```python
# impl/claude/agents/i/screens/myscreen.py
from impl.claude.agents.i.widgets import MyWidget

class MyScreen(Screen):
    def compose(self) -> ComposeResult:
        yield MyWidget()
```

### Adding an AGENTESE Path

1. **Choose context** (world, self, concept, void, time)

2. **Add handler**:
```python
# impl/claude/protocols/agentese/contexts/self_.py
async def handle_self_mypath(path: str, umwelt: Umwelt) -> Any:
    """Handle self.mypath.* paths."""
    parts = path.split(".")

    if parts[2] == "manifest":
        return await manifest_mypath(umwelt)
    elif parts[2] == "witness":
        return await witness_mypath(umwelt)

    raise UnknownPath(path)
```

3. **Register in router**:
```python
# impl/claude/protocols/agentese/logos.py
SELF_HANDLERS = {
    # ... existing
    "mypath": handle_self_mypath,
}
```

---

## Common Patterns

### Pattern: Agent Composition

```python
# Compose multiple agents into a pipeline
pipeline = compose(Ground(), Judge(), Sublate())
result = await pipeline.invoke(input)

# Or using the >> operator
pipeline = Ground() >> Judge() >> Sublate()
```

### Pattern: Flux Event Streaming

```python
# Subscribe to events
async for event in flux.subscribe("soul.*"):
    match event.type:
        case "soul.vibe.changed":
            await handle_vibe_change(event)
        case "soul.drift.detected":
            await handle_drift(event)

# Publish events
await flux.publish(SoulEvent(type="soul.vibe.changed", data=new_vibe))
```

### Pattern: Error Handling with Reality

```python
# Use J-gent reality classification for error handling
reality = await j_gent.classify(result)

match reality:
    case Reality.NECESSARY:
        # Certain - proceed confidently
        return result.data
    case Reality.EMPIRICAL:
        # Likely - proceed with monitoring
        return result.data, {"monitor": True}
    case Reality.CHAOTIC:
        # Uncertain - fall back to ground
        return await ground.invoke(VOID)
```

### Pattern: Dialectical Resolution

```python
# Use H-gent for contradiction resolution
thesis = user_position
antithesis = await contradict.detect(thesis)
synthesis = await sublate.resolve(thesis, antithesis)

# Result includes aufheben analysis
print(f"Preserved: {synthesis.preserved}")
print(f"Negated: {synthesis.negated}")
print(f"Elevated: {synthesis.elevated}")
```

---

## Debugging Tips

### Enable Verbose Logging

```bash
# Set log level
export KGENTS_LOG_LEVEL=DEBUG

# Or per-command
kg soul vibe --verbose
```

### Trace AGENTESE Paths

```bash
# Trace path resolution
kg trace "self.soul.vibe"
# Output: self.soul.vibe → handle_self_soul → eigenvector_calculation → vibe_synthesis
```

### Inspect Agent State

```python
# In Python REPL
from impl.claude.agents.k import KgentAgent

kgent = KgentAgent.from_context(ctx)
print(kgent.state)
print(kgent.eigenvectors)
```

### Test in Isolation

```bash
# Run single test
uv run pytest tests/unit/test_soul.py::test_vibe_calculation -v

# Run with pdb on failure
uv run pytest --pdb tests/unit/test_soul.py
```

---

## Glossary

| Term | Definition |
|------|------------|
| **Agent** | Autonomous unit with specific capabilities |
| **AGENTESE** | Verb-first protocol for agent interaction |
| **Aufheben** | Dialectical operation: preserve, negate, elevate |
| **Bootstrap** | The 7 core agents that self-ground |
| **Chrysalis** | Agent in metamorphosis state |
| **Eigenvector** | Dimension of Kent's cognitive personality |
| **Flux** | Event streaming system for agent coordination |
| **Ground** | Bootstrap agent providing factual foundation |
| **Handle** | AGENTESE morphism: Observer → Interaction |
| **Holographic** | Memory model where each part contains the whole |
| **Logos** | Central AGENTESE dispatch system |
| **Stigmergic** | Indirect coordination through environment |
| **Sublate** | Bootstrap agent for dialectical synthesis |
| **Umwelt** | Observer's perceptual world |

---

## FAQ

**Q: Where do I start?**
A: Run `kg soul vibe` and `kg oblique`. Explore from there.

**Q: How do I add a new command?**
A: See Extension Guide → Adding a New CLI Command.

**Q: What's the fastest way to understand the architecture?**
A: Read `logos.py` (central dispatch) and `handlers/soul.py` (example handler).

**Q: How do tests work?**
A: Five types (Unit, Property, Integration, Adversarial, Dialectic). Run `uv run pytest`.

**Q: Where are the eigenvectors defined?**
A: `impl/claude/agents/k/eigenvectors.py`

**Q: How does AGENTESE work?**
A: Paths like `self.soul.vibe` dispatch through `logos.py` to context handlers.

---

## Resources

- `spec/protocols/agentese.md` - AGENTESE specification
- `spec/principles.md` - Core principles
- `plans/skills/` - Reusable patterns
- `plans/ideas/impl/` - Implementation plans
- `CLAUDE.md` - Project overview

---

*"Documentation is a love letter to your future self."*
