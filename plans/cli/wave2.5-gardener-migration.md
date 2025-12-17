# Wave 2.5: Gardener CLI Migration to Isomorphic Architecture

**Status**: Complete
**Priority**: High
**Progress**: 100%
**Parent**: `plans/cli-isomorphic-migration.md`
**Depends On**: Wave 0 (Dimension System), Wave 2 (Forest/Joy)
**Last Updated**: 2025-12-17
**Completed**: 2025-12-17

---

## Objective

Migrate the Gardener CLI—the most sophisticated CLI in kgents—to the Isomorphic CLI architecture. This includes session management, garden state, tending gestures, and the auto-inducer. The migration must preserve Rich output formatting while routing through AGENTESE paths.

---

## Current Architecture Analysis

The Gardener CLI spans **4 handler files** with **~2,500 lines** of business logic:

| File | Lines | Purpose | Complexity |
|------|-------|---------|------------|
| `gardener.py` | ~1,200 | Session management, garden lifecycle, chat mode | **High** |
| `garden.py` | ~690 | Garden state, seasons, auto-inducer | Medium |
| `tend.py` | ~680 | Six tending gestures + aliases | Medium |
| `gardener.py` (API) | ~940 | REST endpoints | Medium |

### Key Subsystems

1. **Session Polynomial** (`concept.gardener.session.*`)
   - SENSE → ACT → REFLECT cycle
   - Session persistence via GardenerContext
   - Polynomial visualization

2. **Garden State** (`self.garden.*`)
   - Plots (crown jewels regions)
   - Seasons (DORMANT, SPROUTING, BLOOMING, HARVEST, COMPOSTING)
   - Metrics and health scoring
   - Auto-Inducer (phase transition suggestions)

3. **Tending Calculus** (`self.garden.tend.*`)
   - Six primitive verbs: OBSERVE, PRUNE, GRAFT, WATER, ROTATE, WAIT
   - Entropy costs per verb
   - Synergy detection

4. **Persona Garden** (`self.garden.persona.*`)
   - Idea lifecycle: SEED → SAPLING → TREE → FLOWER → COMPOST
   - Plant, nurture, harvest operations
   - Cross-jewel flow (harvest → Brain crystals)

---

## Target Architecture

### AGENTESE Path Registry

```
concept.gardener.*           - Session polynomial (abstract concept)
  ├── session.manifest       - View active session
  ├── session.define         - Start new session
  ├── session.advance        - Advance to next phase
  ├── session.polynomial     - Full polynomial visualization
  ├── sessions.manifest      - List recent sessions
  └── session.chat           - Interactive tending chat

self.garden.*                - Garden state (internal)
  ├── manifest               - Garden overview
  ├── season.manifest        - Current season info
  ├── season.transition      - Change season
  ├── health.manifest        - Health metrics
  ├── plots.manifest         - List all plots
  ├── plot.focus             - Focus a specific plot
  └── init                   - Initialize garden

self.garden.tend.*           - Tending gestures
  ├── observe                - Perceive without changing
  ├── prune                  - Mark for removal
  ├── graft                  - Add something new
  ├── water                  - Nurture via TextGRAD
  ├── rotate                 - Change perspective
  └── wait                   - Intentional pause

self.garden.persona.*        - Persona garden (ideas)
  ├── manifest               - Garden status with lifecycle counts
  ├── plant                  - Plant a new idea
  ├── harvest                - Show flowers ready to harvest
  ├── nurture                - Water/boost an idea
  ├── harvest_brain          - Harvest to Brain crystals
  └── surprise               - Serendipity from void

void.garden.sip              - Serendipity (accursed share)

self.garden.inducer.*        - Auto-Inducer
  ├── suggest                - Check for transition suggestion
  ├── accept                 - Accept suggestion
  └── dismiss                - Dismiss suggestion
```

---

## Implementation Phases

### Phase 1: Create GardenerNode (Day 1)

**File**: `impl/claude/protocols/agentese/contexts/gardener.py`

Create `GardenerNode` for `concept.gardener.*` paths:

```python
@dataclass
class GardenerNode(BaseLogosNode):
    """
    concept.gardener - Development Session Polynomial.

    The Gardener manages structured development sessions following
    the SENSE → ACT → REFLECT polynomial cycle.

    AGENTESE Paths:
    - concept.gardener.session.manifest  - View active session
    - concept.gardener.session.define    - Start new session
    - concept.gardener.session.advance   - Advance phase
    - concept.gardener.session.polynomial - Full visualization
    """

    _handle: str = "concept.gardener"
    _ctx: "GardenerContext | None" = None

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session_state")],
        help="View active gardener session",
        long_help="Show current session status including phase, counts, and intent.",
        examples=["kg gardener", "kg gardener status"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> BasicRendering:
        """View session status and garden overview."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session_state")],
        help="Start a new gardener session",
        examples=["kg gardener start", "kg gardener start 'Feature X'"],
    )
    async def define(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Create a new session."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("session_state")],
        help="Advance to next polynomial phase",
        examples=["kg gardener advance"],
    )
    async def advance(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Advance SENSE→ACT→REFLECT."""
        ...

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("session_state")],
        help="Show polynomial state machine visualization",
        examples=["kg gardener manifest", "kg gardener poly"],
    )
    async def polynomial(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Get polynomial visualization data."""
        ...
```

**Key Implementation Details**:
- Thread-safe GardenerContext initialization (reuse existing pattern)
- Delegate to existing `agents.gardener.handlers` for business logic
- Return structured data for projection functor to render

### Phase 2: Create GardenNode (Day 1-2)

**File**: `impl/claude/protocols/agentese/contexts/garden.py`

Create `GardenNode` for `self.garden.*` paths:

```python
@dataclass
class GardenNode(BaseLogosNode):
    """
    self.garden - Garden State and Tending Interface.

    The garden is the unified state model for development:
    - Plots are focused regions (crown jewels, plans)
    - Seasons affect plasticity and entropy costs
    - Gestures accumulate in momentum trace
    """

    _handle: str = "self.garden"

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="View garden status",
        examples=["kg garden"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> BasicRendering:
        """Show garden status (ASCII or JSON)."""
        ...

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Show current season info",
        examples=["kg garden season"],
    )
    async def season_manifest(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Show current season with plasticity and entropy."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Transition to a new season",
        examples=["kg garden transition BLOOMING"],
    )
    async def season_transition(
        self, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """Transition garden season."""
        ...
```

### Phase 3: Create TendNode (Day 2)

**File**: `impl/claude/protocols/agentese/contexts/tend.py`

Create `TendNode` for the six tending gestures:

```python
# Tending verb → aspect metadata
TENDING_ASPECTS: dict[str, dict[str, Any]] = {
    "observe": {
        "category": AspectCategory.PERCEPTION,
        "effects": [Effect.READS("garden_state")],
        "help": "Perceive without changing (nearly free)",
        "entropy_cost": 0.01,
    },
    "prune": {
        "category": AspectCategory.MUTATION,
        "effects": [Effect.WRITES("garden_state")],
        "help": "Mark for removal (moderate cost)",
        "entropy_cost": 0.08,
    },
    "graft": {
        "category": AspectCategory.GENERATION,
        "effects": [Effect.WRITES("garden_state")],
        "help": "Add something new (expensive)",
        "entropy_cost": 0.12,
    },
    "water": {
        "category": AspectCategory.MUTATION,
        "effects": [Effect.WRITES("garden_state"), Effect.CALLS("textgrad")],
        "help": "Nurture via TextGRAD (moderate cost)",
        "entropy_cost": 0.10,
    },
    "rotate": {
        "category": AspectCategory.PERCEPTION,
        "effects": [Effect.READS("garden_state")],
        "help": "Change perspective (cheap)",
        "entropy_cost": 0.02,
    },
    "wait": {
        "category": AspectCategory.ENTROPY,
        "effects": [],
        "help": "Intentional pause (free)",
        "entropy_cost": 0.0,
    },
}

@dataclass
class TendNode(BaseLogosNode):
    """
    self.garden.tend - The Six Tending Gestures.

    The tending calculus provides primitive gestures for
    gardener-world interaction. Each gesture has an entropy cost
    modulated by the current season's plasticity.
    """

    _handle: str = "self.garden.tend"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes can tend."""
        return tuple(TENDING_ASPECTS.keys())

    async def _invoke_aspect(
        self, aspect: str, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> Any:
        """Route to tending gesture handler."""
        if aspect not in TENDING_ASPECTS:
            return {"error": f"Unknown gesture: {aspect}"}

        return await self._apply_gesture(aspect, observer, **kwargs)

    async def _apply_gesture(
        self, verb: str, observer: "Umwelt[Any, Any]", **kwargs: Any
    ) -> dict[str, Any]:
        """Apply a tending gesture."""
        from protocols.gardener_logos.tending import apply_gesture, TendingGesture, TendingVerb

        garden = await _get_garden()
        gesture = TendingGesture(
            verb=TendingVerb[verb.upper()],
            target=kwargs.get("target", ""),
            tone=kwargs.get("tone", 0.5),
            reasoning=kwargs.get("reason", kwargs.get("feedback", "")),
        )

        result = await apply_gesture(garden, gesture)

        return {
            "verb": verb,
            "target": gesture.target,
            "accepted": result.accepted,
            "state_changed": result.state_changed,
            "changes": result.changes,
            "reasoning_trace": list(result.reasoning_trace),
            "entropy_cost": gesture.entropy_cost,
        }
```

### Phase 4: Create PersonaGardenNode (Day 2)

**File**: `impl/claude/protocols/agentese/contexts/garden_persona.py`

Handle the idea lifecycle (plant, nurture, harvest):

```python
@dataclass
class PersonaGardenNode(BaseLogosNode):
    """
    self.garden.persona - Idea Lifecycle Management.

    Ideas flow through stages:
    SEED (0-0.4) → SAPLING (0.4-0.7) → TREE (0.7-0.9) → FLOWER (0.9+) → COMPOST

    High-confidence flowers can be harvested to Brain crystals.
    """

    _handle: str = "self.garden.persona"

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("persona_garden")],
        help="Show garden lifecycle distribution",
        examples=["kg gardener garden"],
    )
    async def manifest(self, observer: "Umwelt[Any, Any]") -> BasicRendering:
        """Show ideas by lifecycle stage."""
        ...

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.WRITES("persona_garden")],
        help="Plant a new idea in the garden",
        examples=["kg gardener plant 'My insight'"],
    )
    async def plant(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Plant an idea as a seed or sapling."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("persona_garden")],
        help="Nurture an idea with evidence",
        examples=["kg gardener water <id> 'Validated in prod'"],
    )
    async def nurture(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> dict[str, Any]:
        """Boost idea confidence with evidence."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("persona_garden"), Effect.WRITES("brain_crystals")],
        help="Harvest flowers to Brain crystals",
        examples=["kg gardener harvest-to-brain"],
    )
    async def harvest_brain(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Cross-jewel flow: garden → brain."""
        ...
```

### Phase 5: Create AutoInducerNode (Day 3)

**File**: `impl/claude/protocols/agentese/contexts/garden_inducer.py`

Handle season transition suggestions:

```python
@dataclass
class AutoInducerNode(BaseLogosNode):
    """
    self.garden.inducer - Season Transition Auto-Inducer.

    Monitors garden activity and suggests season transitions
    based on TransitionSignals (gesture frequency, diversity, etc.).
    """

    _handle: str = "self.garden.inducer"

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("garden_state")],
        help="Check for suggested season transition",
        examples=["kg garden suggest"],
    )
    async def suggest(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Evaluate transition signals and suggest."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("garden_state")],
        help="Accept the current transition suggestion",
        examples=["kg garden accept"],
    )
    async def accept(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Apply the suggested transition."""
        ...

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("inducer_dismissals")],
        help="Dismiss suggestion (4h cooldown)",
        examples=["kg garden dismiss"],
    )
    async def dismiss(self, observer: "Umwelt[Any, Any]") -> dict[str, Any]:
        """Record dismissal to prevent re-suggestion."""
        ...
```

### Phase 6: Thin Handlers (Day 3)

**File**: `impl/claude/protocols/cli/handlers/gardener.py` (simplified)

```python
"""
Gardener CLI: Thin routing to concept.gardener.* paths.
"""

GARDENER_SUBCOMMAND_MAP: dict[str, str] = {
    "status": "concept.gardener.session.manifest",
    "session": "concept.gardener.session.manifest",
    "start": "concept.gardener.session.define",
    "create": "concept.gardener.session.define",
    "advance": "concept.gardener.session.advance",
    "next": "concept.gardener.session.advance",
    "manifest": "concept.gardener.session.polynomial",
    "polynomial": "concept.gardener.session.polynomial",
    "poly": "concept.gardener.session.polynomial",
    "sessions": "concept.gardener.sessions.manifest",
    "list": "concept.gardener.sessions.manifest",
    "chat": "concept.gardener.session.chat",
    # Persona garden
    "garden": "self.garden.persona.manifest",
    "plant": "self.garden.persona.plant",
    "harvest": "self.garden.persona.harvest",
    "harvest-to-brain": "self.garden.persona.harvest_brain",
    "reap": "self.garden.persona.harvest_brain",
    "water": "self.garden.persona.nurture",
    "nurture": "self.garden.persona.nurture",
    "surprise": "void.garden.sip",
    "serendipity": "void.garden.sip",
}

def cmd_gardener(args: list[str], ctx: InvocationContext | None = None) -> int:
    """Route gardener commands through AGENTESE projection."""
    from protocols.cli.projection import project_command

    subcommand = _parse_subcommand(args) or "status"
    path = GARDENER_SUBCOMMAND_MAP.get(subcommand, "concept.gardener.session.manifest")

    return project_command(path, args, ctx)
```

**File**: `impl/claude/protocols/cli/handlers/tend.py` (simplified)

```python
"""
Tend CLI: Thin routing to self.garden.tend.* paths.
"""

TEND_VERB_MAP: dict[str, str] = {
    "observe": "self.garden.tend.observe",
    "prune": "self.garden.tend.prune",
    "graft": "self.garden.tend.graft",
    "water": "self.garden.tend.water",
    "rotate": "self.garden.tend.rotate",
    "wait": "self.garden.tend.wait",
}

def cmd_tend(args: list[str], ctx: InvocationContext | None = None) -> int:
    """Route tending gestures through AGENTESE projection."""
    from protocols.cli.projection import project_command

    verb = _parse_verb(args) or "observe"
    path = TEND_VERB_MAP.get(verb, "self.garden.tend.observe")

    return project_command(path, args, ctx)

# Top-level aliases
def cmd_observe(args: list[str], ctx = None) -> int:
    return project_command("self.garden.tend.observe", args, ctx)

def cmd_prune(args: list[str], ctx = None) -> int:
    return project_command("self.garden.tend.prune", args, ctx)
# ... etc
```

### Phase 7: Rich Output Projection (Day 3-4)

The projection functor needs to handle Rich output for gardener commands. Add dimension-aware formatting:

```python
# In protocols/cli/projection.py

def _format_gardener_session(result: dict[str, Any], dimensions: CommandDimensions) -> str:
    """Format gardener session with Rich panels."""
    if not RICH_AVAILABLE:
        return _format_neutral(result)

    phase = result.get("phase", "SENSE")
    polynomial = _render_polynomial_ascii(phase)

    return Panel(
        f"[bold green]Session:[/] {result.get('name', 'Unnamed')}\n"
        f"[dim]ID: {result.get('session_id', 'unknown')[:8]}...[/]\n\n"
        f"[bold]State Machine:[/]\n{polynomial}\n\n"
        f"[bold]Phase:[/] {phase}",
        border_style="green",
    )

def _format_garden_status(result: dict[str, Any], dimensions: CommandDimensions) -> str:
    """Format garden with lifecycle icons."""
    lifecycle_icons = {
        "seed": "🌱", "sapling": "🌿", "tree": "🌳",
        "flower": "🌸", "compost": "🍂",
    }
    # ... render with Rich Table
```

### Phase 8: Dimension Tests (Day 4)

```python
class TestGardenerDimensions:
    """Test dimension derivation for Gardener paths."""

    def test_session_manifest_dimensions(self) -> None:
        """concept.gardener.session.manifest should be sync, stateful."""
        meta = AspectMetadata(
            category=AspectCategory.PERCEPTION,
            effects=[Effect.READS("session_state")],
            ...
        )
        dims = derive_dimensions("concept.gardener.session.manifest", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATEFUL
        assert dims.backend == Backend.PURE

    def test_session_advance_dimensions(self) -> None:
        """concept.gardener.session.advance should be async (WRITES)."""
        ...

    def test_tend_water_dimensions(self) -> None:
        """self.garden.tend.water should derive LLM backend (CALLS textgrad)."""
        meta = AspectMetadata(
            category=AspectCategory.MUTATION,
            effects=[Effect.WRITES("garden_state"), Effect.CALLS("textgrad")],
            ...
        )
        dims = derive_dimensions("self.garden.tend.water", meta)
        assert dims.backend == Backend.LLM  # Because CALLS("textgrad")

    def test_tend_wait_dimensions(self) -> None:
        """self.garden.tend.wait should be sync, stateless, playful (entropy)."""
        meta = AspectMetadata(
            category=AspectCategory.ENTROPY,
            effects=[],
            ...
        )
        dims = derive_dimensions("self.garden.tend.wait", meta)
        assert dims.execution == Execution.SYNC
        assert dims.statefulness == Statefulness.STATELESS
```

---

## Acceptance Criteria

### GardenerNode
- [ ] `concept.gardener.session.*` paths resolve to GardenerNode
- [ ] Session create/advance/cycle work via AGENTESE
- [ ] Polynomial visualization returns structured data
- [ ] Thread-safe GardenerContext initialization
- [ ] All aspects have `@aspect` decorators

### GardenNode
- [ ] `self.garden.*` paths resolve to GardenNode
- [ ] Season manifest/transition work
- [ ] Health metrics accessible
- [ ] Plot CRUD operations work
- [ ] Registered in SelfContextResolver

### TendNode
- [ ] All six gestures implemented as aspects
- [ ] Entropy costs calculated correctly
- [ ] Season plasticity affects learning rate
- [ ] Synergies detected and reported
- [ ] Top-level aliases (kg observe, kg prune, etc.) work

### PersonaGardenNode
- [ ] Idea lifecycle (plant, nurture, harvest) works
- [ ] Cross-jewel flow to Brain crystals
- [ ] Serendipity from void works

### AutoInducerNode
- [ ] Transition suggestions based on signals
- [ ] Accept/dismiss with cooldowns
- [ ] Integrated with tending results

### Handlers
- [ ] gardener.py reduced to thin routing (~100 lines)
- [ ] garden.py reduced to thin routing (~50 lines)
- [ ] tend.py reduced to thin routing (~100 lines)
- [ ] Rich output preserved via projection functor

### Dimensions
- [ ] All paths derive correct dimensions
- [ ] Tests cover all key paths
- [ ] water gesture derives LLM backend

---

## Files Created/Modified

| File | Action | Lines Est. |
|------|--------|------------|
| `protocols/agentese/contexts/gardener.py` | Create | ~300 |
| `protocols/agentese/contexts/garden.py` | Create | ~400 |
| `protocols/agentese/contexts/tend.py` | Create | ~250 |
| `protocols/agentese/contexts/garden_persona.py` | Create | ~200 |
| `protocols/agentese/contexts/garden_inducer.py` | Create | ~150 |
| `protocols/agentese/contexts/self_.py` | Modify | +30 |
| `protocols/agentese/contexts/concept.py` | Modify | +20 |
| `protocols/cli/handlers/gardener.py` | Rewrite | ~100 (was 1200) |
| `protocols/cli/handlers/garden.py` | Rewrite | ~50 (was 690) |
| `protocols/cli/handlers/tend.py` | Rewrite | ~100 (was 680) |
| `protocols/cli/projection.py` | Modify | +150 (Rich formatters) |
| `protocols/cli/_tests/test_gardener_dimensions.py` | Create | ~300 |

---

## Migration Strategy

1. **Phase 1-5**: Create all AGENTESE nodes (don't touch handlers yet)
2. **Phase 6**: Rewrite handlers to thin routing
3. **Phase 7**: Add Rich formatters to projection functor
4. **Phase 8**: Add dimension tests

This allows incremental validation—new nodes can be tested independently before handlers are migrated.

---

## Risk Mitigation

1. **Rich Output Loss**: The existing handlers have extensive Rich formatting. Capture all formatting patterns in a `gardener_formatters.py` module that the projection functor can use.

2. **Session State**: GardenerContext manages session persistence. Ensure the node properly initializes and shares this context.

3. **Chat Mode**: Interactive chat mode (`kg gardener chat`) is complex. May need a dedicated ChatProjection handler similar to soul chat.

4. **Backward Compatibility**: Keep command signatures identical. `kg gardener start "Name"` should work exactly as before.

---

## Consolidation Benefit

**Before**: 4 handler files, ~2,500 lines, scattered across multiple modules
**After**: 5 AGENTESE nodes (~1,300 lines) + 3 thin handlers (~250 lines)

- **Net reduction**: ~950 lines
- **Architecture alignment**: All commands route through AGENTESE
- **Dimension-aware**: UX adapts to command semantics
- **Testable**: Business logic in nodes, not handlers

---

*Next: Wave 3 - Help/Affordances Projection*
