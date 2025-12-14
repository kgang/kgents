# AGENTESE REPL: Developer Guide

> *"The interface that teaches its own structure through use is no interface at all."*

The AGENTESE REPL transforms CLI interaction into **liturgical navigation**—commands become invocations, exploration becomes discovery, and the ontology reveals itself through use.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [The Five Contexts](#the-five-contexts)
3. [Observer Archetypes](#observer-archetypes)
4. [Pipeline Composition](#pipeline-composition)
5. [Starter Pack Implementations](#starter-pack-implementations)
6. [Meta-Cognition: Evolving Your Workflow](#meta-cognition-evolving-your-workflow)
7. [Maintenance & Extension Patterns](#maintenance--extension-patterns)
8. [Ideation Garden](#ideation-garden)

---

## Getting Started

### Launching the REPL

```bash
# Standard launch
kg -i

# With verbose output (shows stack traces on errors)
kg -i --verbose

# The REPL is also available via the full command
kgents --interactive
```

### The Prompt Anatomy

```
(E) [self.soul] »
 │   │    │    └── Invocation indicator
 │   │    └─────── Current holon
 │   └──────────── Current context (colored by type)
 └──────────────── Observer archetype (E=explorer, D=developer, A=architect, *=admin)
```

### Navigation Primitives

| Command | Effect | Example |
|---------|--------|---------|
| `<context>` | Enter context | `self`, `world`, `void` |
| `<holon>` | Navigate to holon (within context) | `soul`, `agents`, `entropy` |
| `..` | Go up one level | From `self.soul` → `self` |
| `.` | Show current path | Displays `self.soul` |
| `/` | Return to root | From anywhere → `[root]` |
| `?` | Show affordances | What's available here? |
| `??` | Detailed help | Deep documentation |

### Invocation Patterns

```bash
# Navigate then invoke
self
soul
reflect "What should I focus on?"

# Direct invocation (space-separated)
self soul reflect "What should I focus on?"

# Dotted path invocation
self.soul.reflect "What should I focus on?"

# From any location, full path works
world.agents.list
```

---

## The Five Contexts

The AGENTESE ontology organizes all operations into five contexts. Each context has its own color in the REPL prompt.

### `self.*` (Green) — The Internal

Your agent's inner world: state, memory, soul, capabilities.

```
[self] » ?
  status       System health at a glance
  memory       Four Pillars memory health
  dream        LucidDreamer morning briefing
  soul         K-gent soul dialogue
  capabilities What can I do?
  dashboard    Real-time TUI dashboard
```

**Key Patterns:**
- `self status` — Quick health check before starting work
- `self soul reflect` — Mirror your current state
- `self memory` — Check memory consolidation status
- `self dashboard --demo` — Visual system overview

### `world.*` (Blue) — The External

Agents, infrastructure, resources—everything outside.

```
[world] » ?
  agents       Agent operations (list, run, inspect)
  daemon       Cortex daemon lifecycle
  infra        K8s infrastructure operations
  fixture      HotData fixtures
  exec         Q-gent execution
  dev          Live reload development
  town         Agent Town simulation
```

**Key Patterns:**
- `world agents list` — See registered agents
- `world town step` — Advance Agent Town simulation
- `world daemon status` — Check cortex health
- `world infra status` — K8s cluster overview

### `concept.*` (Magenta) — The Abstract

Laws, principles, dialectics—pure ideas.

```
[concept] » ?
  laws         Category laws (identity, associativity)
  dialectic    Challenge and refine concepts
  principle    Design principles
  operad       Composition grammar
```

**Key Patterns:**
- `concept laws verify` — Check category law compliance
- `concept dialectic "Is this approach sound?"` — Challenge ideas
- `concept principle list` — Review design principles

### `void.*` (Gray) — The Accursed Share

Entropy, shadow, serendipity—the creative unknown.

```
[void] » ?
  entropy      Draw/return randomness
  shadow       Jungian shadow analysis
  serendipity  Request tangents
  gratitude    Express thanks (tithe)
  archetype    Archetypal patterns
```

**Key Patterns:**
- `void entropy sip` — Draw from the Accursed Share
- `void shadow` — Surface unconscious patterns
- `void serendipity` — Request creative tangents
- `void gratitude tithe "Thank you for..."` — Pay for order received

### `time.*` (Yellow) — The Temporal

Traces, history, forecasts—temporal navigation.

```
[time] » ?
  trace        View temporal traces
  past         View past state
  future       Forecast (probabilistic)
  schedule     Schedule future actions
  turn         Turn management
```

**Key Patterns:**
- `time trace` — View execution history
- `time past 1h` — State one hour ago
- `time schedule "review" +24h` — Schedule future action

---

## Observer Archetypes

The REPL supports different **observer archetypes** that affect which affordances are visible and how the system responds.

### Switching Observers

```bash
/observer              # Show current archetype
/observer developer    # Switch to developer
/observers             # List all archetypes
```

### Available Archetypes

| Archetype | Prompt | Description | Affordances |
|-----------|--------|-------------|-------------|
| `explorer` | (E) | Curious newcomer | `manifest`, `witness`, `affordances` |
| `developer` | (D) | Skilled builder | Above + `define`, technical details |
| `architect` | (A) | System designer | Above + structural, composition |
| `admin` | (*) | Full access | All affordances, including dangerous |

### Why Archetypes Matter

Different observers see different things. An `explorer` sees pedagogical affordances designed for learning. A `developer` sees implementation details. An `architect` sees structural relationships.

```bash
# As explorer: see what's available for learning
(E) [concept] » ?
  laws, dialectic, principle, operad

# Switch to architect: see compositional structure
/observer architect
(A) [concept] » ?
  laws, dialectic, principle, operad
  + compose, define, refine
```

This embodies the AGENTESE principle: **there is no view from nowhere**. Every observation is situated.

---

## Pipeline Composition

The `>>` operator composes paths into pipelines that execute sequentially.

### Basic Composition

```bash
# Execute self.status, then world.agents
self status >> world agents

# Output shows each step:
# [1/2] self status
# [CORTEX] ? CRITICAL | instance:... | ...
#
# [2/2] world agents
# [A] Available Archetypes: ...
```

### Pipeline Principles

1. **Left-to-right execution** — Each path runs in order
2. **Output passing** — Results flow to next step (when supported)
3. **Graceful fallback** — Uses CLI routing when Logos unavailable
4. **Full paths work** — `world.agents.list >> concept.count`

### Common Pipelines

```bash
# Health check pipeline
self status >> world daemon status >> world infra status

# Agent Town workflow
world town step >> world town observe alice >> time trace

# Memory consolidation check
self memory >> self soul reflect "How's my memory?"
```

### Future: True Composition

When Logos integration deepens, pipelines will support true morphism composition:

```bash
# Future: output of manifest becomes input to refine
world.document.manifest >> concept.summary.refine >> self.memory.engram
```

---

## Starter Pack Implementations

### Morning Workflow

Start your day with a system check and soul reflection:

```bash
kg -i
self status                    # System health
self memory                    # Memory consolidation
self soul reflect "What should I focus on today?"
void entropy sip               # Draw creative energy
exit
```

### Agent Development Workflow

When building or debugging agents:

```bash
kg -i
/observer developer            # Switch to dev mode
world agents list              # See available agents
world agents inspect MyAgent   # Deep inspection
self soul challenge "Is this architecture right?"
world town step                # Test in simulation
time trace                     # Review execution
exit
```

### Exploration Workflow

When learning the system or onboarding:

```bash
kg -i
/observer explorer             # Pedagogical mode
?                              # What contexts exist?
self                           # Enter self
?                              # What holons here?
soul                           # Go deeper
??                             # Detailed help
..                             # Back up
world                          # Try another context
exit
```

### Debugging Workflow

When something goes wrong:

```bash
kg -i
/observer admin                # Full access
self status                    # Quick health check
time trace                     # Recent execution
self memory                    # Memory health
world daemon logs              # Check daemon
world infra status             # Infrastructure
exit
```

---

## Meta-Cognition: Evolving Your Workflow

### The REPL as Thought Partner

The REPL isn't just a command interface—it's a **cognitive scaffold**. The five contexts mirror aspects of cognition:

- **self** = Introspection, self-model
- **world** = Perception, action in environment
- **concept** = Abstract reasoning, principles
- **void** = Creativity, unconscious processing
- **time** = Memory, planning, temporal reasoning

### Workflow Evolution Stages

**Stage 1: Navigation**
Learn the contexts, use `?` liberally, build muscle memory for `.`, `..`, `/`.

**Stage 2: Invocation**
Start invoking aspects directly. Learn the difference between navigating (`soul`) and invoking (`soul reflect`).

**Stage 3: Composition**
Build pipelines. Chain operations. Think in morphisms.

**Stage 4: Observer Fluency**
Switch archetypes fluidly. Use `explorer` for learning, `developer` for building, `architect` for designing.

**Stage 5: Ambient Use**
The REPL becomes a persistent companion. You think in AGENTESE paths even outside the REPL.

### Integration Patterns

**Terminal Multiplexing:**
Keep a REPL session in a dedicated tmux/screen pane. Quick checks without leaving your editor.

**IDE Integration:**
Future: REPL as VS Code/Cursor extension. Invoke paths from editor.

**Voice Interface:**
Future: Voice-to-REPL for hands-free interaction.

### The Liturgical Mindset

Approach the REPL liturgically:
- Commands are **invocations**, not queries
- You're **grasping handles**, not accessing data
- Results are **manifestations** specific to your observer
- Composition is **ritual**, building meaning through structure

---

## Maintenance & Extension Patterns

### Adding a New Holon

To add a holon to a context:

1. **Update the context router** (`protocols/cli/contexts/<context>.py`):

```python
def _register_holons(self) -> None:
    self.register(
        "myholon",
        "Description of my holon",
        _handle_myholon,
        aspects=["manifest", "witness", "myaspect"],
    )

def _handle_myholon(args: list[str], ctx: InvocationContext | None = None) -> int:
    # Implementation
    pass
```

2. **Update REPL holon list** (`protocols/cli/repl.py`):

```python
CONTEXT_HOLONS = {
    "self": ["status", "memory", ..., "myholon"],
    ...
}
```

3. **Update context help** in `_show_detailed_help()`.

### Adding a New Aspect

Aspects are verbs that can be invoked on holons. To add one:

1. **Add to holon registration** (the `aspects` list)
2. **Handle in the holon handler** (switch on aspect name)
3. **Update Logos resolver** if using Logos routing

### Adding a New Observer Archetype

```python
# In protocols/cli/repl.py
OBSERVER_ARCHETYPES = {
    ...
    "scientist": "Hypothesis-driven, sees experimental affordances",
}
```

Consider what affordances this archetype should see and update the DNA capabilities in `ReplState.get_umwelt()`.

### Testing REPL Changes

```bash
# Quick smoke test
echo -e "?\nself\n?\nexit" | python -m protocols.cli.repl

# Full CLI test suite
uv run pytest protocols/cli/ -q

# Type checking
uv run mypy protocols/cli/repl.py --ignore-missing-imports
```

---

## Ideation Garden

These are evergreen ideas for extending the REPL. Pick one when entropy allows.

### Near-Term Extensions

| Idea | Complexity | Value | Notes |
|------|------------|-------|-------|
| **Fuzzy matching** | M | High | Typo tolerance: `slef` → "Did you mean `self`?" |
| **Session persistence** | S | Medium | Resume from last location |
| **Bookmark paths** | S | Medium | `/bookmark soul` → `/goto soul` |
| **Alias system** | S | High | `alias s="self status"` |
| **History search** | S | Medium | Ctrl+R fuzzy search through history |

### Medium-Term Extensions

| Idea | Complexity | Value | Notes |
|------|------------|-------|-------|
| **Tutorial mode** | M | High | `kg -i --tutorial` guided walkthrough |
| **LLM suggestions** | L | High | "Did you mean..." with semantic understanding |
| **Auto-complete from registry** | M | High | Dynamic completion from Logos |
| **Result caching** | M | Medium | `$_` = last result, `$1` = result 1 back |
| **Script mode** | M | High | `kg -i < script.repl` for automation |

### Long-Term Visions

| Idea | Complexity | Value | Notes |
|------|------------|-------|-------|
| **REPL-as-TUI** | L | High | Evolve into Textual app with panels |
| **Voice REPL** | L | Medium | Voice input for accessibility |
| **Web REPL** | L | Medium | Browser-based exploration |
| **Multiplayer REPL** | XL | High | Shared session, collaborative exploration |
| **REPL Notebooks** | L | High | Jupyter-style cells with AGENTESE |

### Conceptual Extensions

**Observer Algebra:**
What if observers could be composed? `explorer >> developer` = sees both pedagogical and technical.

**Temporal REPL:**
Navigate not just space (contexts) but time. `[self.soul@-1h]` = soul state one hour ago.

**Hypothetical Worlds:**
`/fork` creates a hypothetical branch. Explore "what if" without affecting real state.

**Meta-REPL:**
The REPL that operates on the REPL. `meta.repl.extend "new-holon"` adds holons at runtime.

---

## Quick Reference Card

```
NAVIGATION
  <context>     Enter context (self, world, concept, void, time)
  <holon>       Navigate to holon
  ..            Go up
  .             Show path
  /             Go to root

INTROSPECTION
  ?             Show affordances
  ??            Detailed help
  help          Full help

INVOCATION
  <path>        Invoke manifest aspect
  <path> <asp>  Invoke specific aspect
  path >> path  Compose and execute pipeline

OBSERVER
  /observer              Show current
  /observer <archetype>  Switch (explorer, developer, architect, admin)
  /observers             List all

META
  exit, quit, q  Leave REPL
  clear          Clear screen
  history        Show command history
  Ctrl+C         Interrupt (doesn't exit)
```

---

## Philosophy

The AGENTESE REPL embodies several core principles:

1. **No View From Nowhere** — Every command is situated in an observer context
2. **Verb-First Ontology** — Paths are invocations, not queries
3. **Graceful Degradation** — Works even when subsystems are offline
4. **Pedagogical Interface** — The structure teaches itself through use
5. **Compositional Thinking** — `>>` makes composition first-class
6. **Joy-Inducing** — Warmth and personality in every interaction

The REPL is not just a tool—it's a way of thinking about agent-world interaction.

---

*"The noun is a lie. There is only the rate of change."*
