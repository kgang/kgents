# Exploration Plan: Terrarium Metrics + Bounty Board

> *"Let agents leave signals for other agents."*

**Focus**: Exploration (15% attention budget)
**Date**: 2025-12-12
**Prerequisites**: Terrarium Phase 1-5 complete (176+ tests), Bounty Board initialized

---

## Executive Summary

This plan addresses the Exploration slice from `_focus.md`:

> **Exploration (15%): Terrarium Phase 3 + Bounty Board** — Metrics emission for I-gent widgets. The terrarium window should show pressure/flow/temperature. Also: the new Bounty Board (`plans/_bounty.md`) is stigmergic coordination for agent observations. **Let agents leave signals for other agents.**

There are two complementary workstreams:

1. **Terrarium Metrics → I-gent Widgets**: Wire existing `MetricsManager` to dashboard visualization
2. **Bounty Board Automation**: Let agents programmatically post/claim/query bounties

Both serve the meta-goal: **stigmergic coordination**—agents leaving traces that other agents (and humans) can perceive and act upon.

---

## Current State

### Terrarium Metrics (Implemented)

The metrics foundation exists in `impl/claude/protocols/terrarium/metrics.py`:

| Component | Status | Location |
|-----------|--------|----------|
| `MetricsManager` | Complete | `metrics.py:217` |
| `calculate_pressure()` | Complete | `metrics.py:46` |
| `calculate_flow()` | Complete | `metrics.py:81` |
| `calculate_temperature()` | Complete | `metrics.py:108` |
| `emit_metrics_loop()` | Complete | `metrics.py:152` |
| `TerriumEvent` | Complete | `events.py:40` |
| `EventType.METABOLISM` | Complete | `events.py:28` |

**What's Missing**: Dashboard consumption. The metrics emit through `HolographicBuffer`, but I-gent widgets don't yet subscribe.

### Bounty Board (Initialized)

The protocol exists in `plans/_bounty.md`:

| Element | Status |
|---------|--------|
| Format spec | Complete |
| Lifecycle diagram | Complete |
| Initial bounties | 5 entries |
| Agent protocol | Missing (no programmatic API) |

**What's Missing**: Agents can't post/claim bounties programmatically. It's manual markdown editing only.

---

## Workstream 1: Terrarium Metrics → I-gent Widgets

### Goal

The terrarium window (I-gent TUI) should display live metabolism metrics for running FluxAgents.

### Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     METRICS → WIDGET FLOW                          │
│                                                                    │
│  FluxAgent                MetricsManager           I-gent TUI      │
│  ┌──────────┐            ┌──────────────┐         ┌──────────┐    │
│  │ pressure │───poll────▶│ emit_metrics │───ws───▶│ Density  │    │
│  │ flow     │            │ _loop()      │         │ Field    │    │
│  │ temp     │            └──────────────┘         └──────────┘    │
│  └──────────┘                   │                      │          │
│                                 ▼                      │          │
│                          HolographicBuffer ────────────┘          │
│                          (broadcast)                               │
└────────────────────────────────────────────────────────────────────┘
```

### Phases

#### Phase A: DensityField Widget Binding

**Goal**: Wire existing DensityField to consume TerriumEvent.METABOLISM events.

**Files**:
```
impl/claude/agents/i/widgets/density_field.py    # Add metabolism subscription
impl/claude/agents/i/terrarium_tui.py            # Wire to HolographicBuffer
```

**Key Integration**:
```python
# In terrarium_tui.py
async def _handle_metabolism(self, event: TerriumEvent) -> None:
    """Update DensityField from metabolism event."""
    self.density_field.set_metrics(
        pressure=event.pressure,
        flow=event.flow,
        temperature=event.temperature,
    )
```

**Exit Criteria**: DensityField animates when FluxAgent runs.

#### Phase B: Multi-Agent Dashboard

**Goal**: Show all registered agents' metrics in a grid.

**Files**:
```
impl/claude/agents/i/widgets/metrics_grid.py     # Grid of mini-density fields
impl/claude/agents/i/terrarium_tui.py            # Add MetricsGrid to layout
```

**Exit Criteria**: Dashboard shows N agents simultaneously.

#### Phase C: Fever Overlay Integration

**Goal**: Visual alert when agent temperature exceeds threshold.

**Key Integration**:
```python
# Use existing emit_fever_alert() from metrics.py
if event.temperature > 0.8:
    await emit_fever_alert(event.agent_id, buffer, event.temperature)
```

**Exit Criteria**: FeverOverlay triggers on high temperature.

### Tests (Conceptual)

- Metabolism event updates DensityField values
- Multiple agents render in MetricsGrid
- Fever threshold triggers overlay
- Disconnected observer doesn't crash
- Metrics continue after agent restart

---

## Workstream 2: Bounty Board Automation

### Goal

Agents can programmatically interact with the Bounty Board through an AGENTESE path.

### Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                    BOUNTY BOARD AGENTESE                           │
│                                                                    │
│  Agent Session                 BountyBoard           _bounty.md   │
│  ┌──────────────┐             ┌───────────┐        ┌───────────┐  │
│  │ "noticed X"  │──invoke────▶│ .post()   │──write─▶│ OPEN      │  │
│  │ "claim Y"    │──invoke────▶│ .claim()  │──edit──▶│ CLAIMED   │  │
│  │ "resolve Z"  │──invoke────▶│ .resolve()│──move──▶│ RESOLVED  │  │
│  └──────────────┘             └───────────┘        └───────────┘  │
│                                    │                              │
│                                    ▼                              │
│                          void.bounty.* (AGENTESE)                 │
└────────────────────────────────────────────────────────────────────┘
```

### AGENTESE Paths

| Path | Operation | Returns |
|------|-----------|---------|
| `void.bounty.post` | Create new bounty | BountyToken |
| `void.bounty.claim` | Claim open bounty | ClaimReceipt |
| `void.bounty.resolve` | Mark bounty done | ResolutionRecord |
| `void.bounty.query` | Find matching bounties | list[Bounty] |
| `void.bounty.manifest` | Get board state | BountyBoardState |

**Why `void.*`?**: The Bounty Board is stigmergic—it's entropy discharge. Agents leave signals as a side effect of work. This aligns with `void.sip` and `void.tithe` patterns.

### Phases

#### Phase A: BountyBoard Core Types

**Goal**: Define bounty types and the in-memory representation.

**Files**:
```
impl/claude/protocols/agentese/bounty/
├── __init__.py
├── types.py          # Bounty, BountyType, BountyState
├── board.py          # BountyBoard class
└── _tests/
    └── test_bounty.py
```

**Key Types**:
```python
@dataclass
class Bounty:
    id: str
    type: BountyType         # IDEA | GRIPE | WIN
    impact: ImpactLevel      # HIGH | MED | LOW
    description: str
    tags: frozenset[str]
    created: datetime
    claimed_by: str | None = None
    resolved: datetime | None = None
    outcome: str | None = None

class BountyBoard:
    """In-memory bounty state with file sync."""

    def post(self, type: BountyType, impact: ImpactLevel,
             description: str, tags: set[str]) -> Bounty: ...

    def claim(self, bounty_id: str, agent_id: str) -> bool: ...

    def resolve(self, bounty_id: str, outcome: str) -> bool: ...

    def query(self, tags: set[str] | None = None,
              type: BountyType | None = None,
              state: BountyState | None = None) -> list[Bounty]: ...
```

**Exit Criteria**: BountyBoard can post/claim/resolve in memory.

#### Phase B: File Sync

**Goal**: Sync BountyBoard state to/from `plans/_bounty.md`.

**Key Challenges**:
- Parse existing bounty format (pipe-delimited)
- Write back without corrupting manual edits
- Handle concurrent writes (file locking or append-only)

**Approach**: Append-only for posts, in-place edit for claims, section move for resolves.

**Exit Criteria**: `BountyBoard.load("plans/_bounty.md")` round-trips.

#### Phase C: AGENTESE Wiring

**Goal**: Register `void.bounty.*` paths in Logos.

**Files**:
```
impl/claude/protocols/agentese/wiring.py    # Add bounty paths
impl/claude/protocols/agentese/contexts/void.py  # Handler implementation
```

**Key Integration**:
```python
# In wiring.py
"void.bounty.post": ("POST", bounty_post_handler),
"void.bounty.claim": ("PUT", bounty_claim_handler),
"void.bounty.resolve": ("PUT", bounty_resolve_handler),
"void.bounty.query": ("GET", bounty_query_handler),
"void.bounty.manifest": ("GET", bounty_manifest_handler),
```

**Exit Criteria**: `await logos.invoke("void.bounty.query", {"tags": ["#testing"]})` returns bounties.

#### Phase D: CLI Integration

**Goal**: `kgents bounty` command for human access.

**Subcommands**:
```
kgents bounty list [--tag=<tag>] [--type=<type>] [--state=<state>]
kgents bounty post "<description>" --type=<type> --impact=<level> --tags=<tags>
kgents bounty claim <id>
kgents bounty resolve <id> "<outcome>"
```

**Exit Criteria**: Human can manage bounties from CLI.

### Tests (Conceptual)

- Post bounty creates valid entry
- Claim updates in-place without corruption
- Resolve moves to correct section
- Query filters by tags/type/state
- Concurrent posts don't corrupt file
- AGENTESE paths resolve correctly
- CLI subcommands work end-to-end

---

## Integration: Metrics + Bounty Board

The two workstreams connect:

1. **Metrics → Bounty**: When fever threshold exceeded, auto-post a GRIPE bounty
2. **Bounty → Dashboard**: Show open bounty count in I-gent widget
3. **Agent Session End**: Prompt agent to post observations as bounties

### Example Integration

```python
# In flux agent fever handler
async def on_fever(agent_id: str, temperature: float) -> None:
    """Auto-post bounty when agent overheats."""
    await logos.invoke("void.bounty.post", {
        "type": "GRIPE",
        "impact": "MED",
        "description": f"{agent_id} hit fever temp {temperature:.2f}",
        "tags": ["#performance", "#auto-generated"],
    })
```

---

## Priority Sequencing

Given 15% attention budget:

| Priority | Work | Rationale |
|----------|------|-----------|
| 1 | Phase A: DensityField Binding | Highest impact—makes existing metrics visible |
| 2 | Phase A: BountyBoard Core Types | Foundation for agent signaling |
| 3 | Phase B: File Sync | Required for persistence |
| 4 | Phase C: AGENTESE Wiring | Enables programmatic access |
| 5 | Phase B: Multi-Agent Dashboard | Nice-to-have polish |
| 6 | Phase D: CLI Integration | Human convenience |
| 7 | Phase C: Fever Overlay | Joy-inducing polish |
| 8 | Integration work | Cross-workstream synthesis |

---

## Principles Alignment

| Principle | How This Honors It |
|-----------|-------------------|
| **Tasteful** | Thin wiring, not new frameworks |
| **Curated** | Reuses existing MetricsManager, HolographicBuffer |
| **Ethical** | Transparent signaling, no hidden side effects |
| **Joy-Inducing** | Live dashboard, fever overlay |
| **Composable** | AGENTESE paths compose with existing void.* |
| **Heterarchical** | Stigmergic coordination, not central control |
| **Generative** | Bounty Board enables emergent agent collaboration |

---

## Exit Criteria (Overall)

This exploration slice is complete when:

1. DensityField shows live pressure/flow/temperature for running FluxAgent
2. `void.bounty.post` AGENTESE path works
3. Bounties persist to `plans/_bounty.md`
4. At least one integration point (fever → bounty or dashboard → bounty count)

---

## Cross-References

- **Plan**: `plans/agents/terrarium.md` — Phase 3 context
- **Plan**: `plans/_bounty.md` — Bounty Board protocol
- **Impl**: `impl/claude/protocols/terrarium/metrics.py` — MetricsManager
- **Impl**: `impl/claude/protocols/terrarium/events.py` — TerriumEvent
- **Impl**: `impl/claude/agents/i/terrarium_tui.py` — I-gent TUI
- **Spec**: `spec/principles.md` — Design constraints

---

*"The forest speaks to those who listen. Leave a signal. Claim a prize."*
