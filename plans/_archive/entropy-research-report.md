# void/entropy Research Report

> *"The river that flows only downhill never discovers the mountain spring."*

**Date**: 2025-12-12
**Status**: Research Complete, Ready for Implementation
**Author**: Claude Opus 4.5

---

## Executive Summary

This report analyzes the `void/entropy` spec and proposes enhancements for implementation. The current spec (plans/void/entropy.md) defines a **Metabolic Engine** for tracking token pressure and triggering creative "fever" events when the system runs hot. However, several gaps exist between the spec and the existing codebase.

**Key Findings**:
1. **80% of void.entropy is already implemented** in `protocols/agentese/contexts/void.py`
2. The **MetabolicEngine** and **FeverStream** are the missing pieces
3. Strong integration points exist with I-gent TUI (GlitchController) and context management (ContextWindow pressure)
4. The spec conflates two distinct pressures: **context pressure** (token budget) and **metabolic pressure** (activity accumulation)

**Recommendations**:
1. Implement MetabolicEngine as a thin layer on top of existing EntropyPool
2. Wire FeverStream to GlitchController for TUI visualization
3. Connect to ContextWindow.pressure for token-based temperature
4. Add CLI handler for `kgents tithe` command

---

## Part I: Current Implementation Analysis

### 1.1 What Already Exists

The `void.py` context file (999 lines) implements:

| Component | Status | Location |
|-----------|--------|----------|
| EntropyPool | ✅ Complete | `void.py:42-163` |
| RandomnessGrant | ✅ Complete | `void.py:169-199` |
| EntropyNode | ✅ Complete | `void.py:204-267` |
| SerendipityNode | ✅ Complete | `void.py:269-428` |
| GratitudeNode | ✅ Complete | `void.py:431-517` |
| CapitalNode | ✅ Complete | `void.py:519-645` |
| PataphysicsNode | ✅ Complete | `void.py:650-864` |
| VoidContextResolver | ✅ Complete | `void.py:869-924` |

**Existing AGENTESE Paths**:
- `void.entropy.sip` → Draw entropy from pool
- `void.entropy.pour` → Return unused entropy (50% recovery)
- `void.entropy.sample` → Get random value without budget cost
- `void.entropy.status` → Check pool state
- `void.serendipity.sip` → Generate tangential thought
- `void.serendipity.inspire` → Generate inspiration
- `void.gratitude.tithe` → Noop sacrifice (regenerates pool)
- `void.gratitude.thank` → Express gratitude
- `void.capital.*` → Social capital ledger
- `void.pataphysics.solve` → Contract-bounded hallucination

### 1.2 What's Missing (From Spec)

| Component | Spec Status | Implementation Status |
|-----------|-------------|----------------------|
| MetabolicEngine | Specced | ❌ Not implemented |
| FeverStream | Specced | ❌ Not implemented |
| Token Thermometer | Specced | ❌ Not implemented |
| FeverEvent | Specced | ❌ Not implemented |
| `void.entropy.pressure` | Specced | ❌ Not implemented |
| `void.entropy.fever` | Specced | ❌ Not implemented |
| TUI Fever Glitch | Specced | ⚠️ Glitch system exists, needs wiring |
| `kgents tithe` CLI | Specced | ❌ Not implemented |

### 1.3 Related Systems

**GlitchController** (`agents/i/widgets/glitch.py`):
- Already implements visual entropy manifestation
- `trigger_global_glitch()` for screen-wide effects
- `on_void_phase()` for agent-specific glitches
- Can be wired to FeverStream for continuous fever visualization

**ContextWindow** (`agents/d/context_window.py`):
- Has `pressure` property (token ratio)
- Has `needs_compression` (pressure > 0.7)
- Has `total_tokens` and `max_tokens` tracking
- Can provide temperature signal to MetabolicEngine

**StreamContextResolver** (`protocols/agentese/contexts/stream.py`):
- `self.stream.pressure.check` already exposes context pressure
- `self.stream.pressure.auto_compress` triggers compression
- Natural integration point for metabolic pressure

---

## Part II: Gap Analysis

### 2.1 Conceptual Gap: Two Pressures

The spec conflates two distinct pressure concepts:

| Pressure Type | Source | Scale | Response |
|---------------|--------|-------|----------|
| **Context Pressure** | Token accumulation in ContextWindow | 0.0-1.0 (% of max tokens) | Compression (drop/summarize) |
| **Metabolic Pressure** | Activity accumulation (LLM calls) | Unbounded, decays naturally | Fever (creative expenditure) |

**The Insight**: Context pressure is about **scarcity** (running out of room). Metabolic pressure is about **surplus** (the Accursed Share that must be spent).

**Resolution**: MetabolicEngine should track metabolic pressure separately, but use context pressure as a **temperature signal**:

```python
@property
def temperature(self) -> float:
    """Token-based temperature estimate."""
    if self.output_tokens == 0:
        return 0.0
    # High input:output ratio = cold (receiving more than giving)
    # Low input:output ratio = hot (giving more than receiving)
    return min(2.0, self.input_tokens / self.output_tokens)
```

### 2.2 Implementation Gap: FeverStream

The spec describes FeverStream as:
> "Background thread that runs when pressure is high. Generates poetic misunderstandings that sometimes solve problems."

**Problem**: The spec conflates two behaviors:
1. **Oblique Strategies** (terse, enigmatic prompts)
2. **Fever Dreams** (longer, hallucinatory generation)

**Resolution**: Split into two mechanisms:
- `void.entropy.oblique` → Return a random Oblique Strategy (cheap, no LLM)
- `void.pataphysics.dream` → Generate a fever dream (expensive, uses LLM)

The SerendipityNode already implements something like Oblique Strategies via `_tangent_templates`. Enhance it.

### 2.3 TUI Integration Gap

The GlitchController exists and is well-designed, but:
1. No connection to MetabolicEngine pressure
2. No "Fever Mode" UI state
3. No Oblique Strategy display area

**Resolution**: Add to FluxApp:
- Pressure gauge showing metabolic pressure
- Fever overlay when pressure exceeds threshold
- Oblique strategy display in status bar during fever

---

## Part III: Proposed Architecture

### 3.1 MetabolicEngine Design

```python
@dataclass
class MetabolicEngine:
    """
    The thermodynamic heart of the system.

    Tracks activity pressure (not token pressure) and triggers
    creative expenditure when pressure exceeds threshold.
    """

    # Activity tracking
    pressure: float = 0.0
    critical_threshold: float = 1.0
    decay_rate: float = 0.01  # Natural decay per tick

    # Token thermometer (feeds into pressure calculation)
    input_tokens: int = 0
    output_tokens: int = 0

    # Fever state
    in_fever: bool = False
    fever_start: float | None = None

    # Entropy pool integration
    _entropy_pool: EntropyPool | None = None

    # Glitch controller integration (for TUI)
    _glitch_controller: GlitchController | None = None

    @property
    def temperature(self) -> float:
        """Token-based temperature estimate."""
        if self.output_tokens == 0:
            return 0.0
        return min(2.0, self.input_tokens / self.output_tokens)

    def tick(self, input_count: int, output_count: int) -> FeverEvent | None:
        """
        Called per LLM invocation.

        Returns FeverEvent if pressure exceeds threshold.
        """
        self.input_tokens += input_count
        self.output_tokens += output_count

        # Pressure accumulates based on activity
        activity = (input_count + output_count) * 0.001
        self.pressure += activity

        # Natural decay
        self.pressure *= (1.0 - self.decay_rate)

        # Check for fever trigger
        if self.pressure > self.critical_threshold and not self.in_fever:
            return self._trigger_fever()

        # Check for fever recovery
        if self.in_fever and self.pressure < self.critical_threshold * 0.5:
            self._end_fever()

        return None

    def _trigger_fever(self) -> FeverEvent:
        """Forced creative expenditure."""
        self.in_fever = True
        self.fever_start = time.time()

        intensity = self.pressure - self.critical_threshold

        # Draw from entropy pool
        if self._entropy_pool:
            try:
                grant = self._entropy_pool.sip(intensity * 0.5)
            except BudgetExhaustedError:
                grant = {"seed": random.random(), "amount": 0}

        # Discharge pressure
        self.pressure *= 0.5

        # Trigger glitch if available
        if self._glitch_controller:
            # Async handled by caller
            pass

        return FeverEvent(
            intensity=intensity,
            timestamp=time.time(),
            trigger="pressure_overflow",
            seed=grant.get("seed", random.random()),
        )

    def tithe(self, amount: float = 0.1) -> dict[str, Any]:
        """Voluntary pressure discharge."""
        self.pressure = max(0.0, self.pressure - amount)

        # Also tithe to entropy pool
        if self._entropy_pool:
            self._entropy_pool.tithe()

        return {
            "discharged": amount,
            "remaining_pressure": self.pressure,
            "gratitude": "The river flows.",
        }
```

### 3.2 FeverEvent and FeverStream

```python
@dataclass
class FeverEvent:
    """Record of a fever trigger."""
    intensity: float
    timestamp: float
    trigger: str  # "pressure_overflow", "manual", "error"
    seed: float
    oblique_strategy: str = ""

@dataclass
class FeverStream:
    """
    Generates creative output during fever state.

    Two modes:
    - oblique: Quick, no LLM (Oblique Strategies)
    - dream: Slow, uses LLM (Fever Dreams)
    """

    _oblique_strategies: tuple[str, ...] = (
        "Honor thy error as a hidden intention.",
        "What would your closest friend do?",
        "Turn it upside down.",
        "Ask your body.",
        "Do nothing for as long as possible.",
        "Use an old idea.",
        "What are you really thinking about just now?",
        "Look at the order in which you do things.",
        "Emphasize differences.",
        "What mistakes did you make last time?",
        "Is it finished?",
        "Into the impossible.",
        "Work at a different speed.",
        "Gardening, not architecture.",
        "Go slowly all the way round the outside.",
    )

    def oblique(self, seed: float | None = None) -> str:
        """Return an Oblique Strategy (no LLM cost)."""
        if seed is None:
            seed = random.random()
        idx = int(seed * len(self._oblique_strategies))
        return self._oblique_strategies[idx]

    async def dream(self, context: dict, llm_client: Any = None) -> str:
        """
        Generate a fever dream from current context.

        This is the "hallucination as feature" pattern.
        Expensive—uses LLM with high temperature.
        """
        if llm_client is None:
            # Fallback to oblique strategy
            return self.oblique()

        prompt = f"""
        The system is running hot. Here is the current context:
        {json.dumps(context, indent=2, default=str)[:1000]}

        Generate an oblique strategy—a sideways thought that might
        illuminate the problem from an unexpected angle.

        Be brief, enigmatic, potentially useful.
        """

        response = await llm_client.generate(
            prompt,
            temperature=1.4,  # HOT
            max_tokens=100,
        )
        return response
```

### 3.3 AGENTESE Integration

New paths to add:

| Path | Operation | Description |
|------|-----------|-------------|
| `void.entropy.pressure` | Query | Current metabolic pressure |
| `void.entropy.fever` | Check | Is system in fever? |
| `void.entropy.oblique` | Generate | Return Oblique Strategy |
| `void.entropy.dream` | Generate | Trigger fever dream (expensive) |

Update VoidContextResolver to include MetabolicEngine:

```python
@dataclass
class VoidContextResolver:
    _pool: EntropyPool = field(default_factory=EntropyPool)
    _ledger: EventSourcedLedger = field(default_factory=EventSourcedLedger)
    _metabolism: MetabolicEngine | None = None  # NEW
    _fever_stream: FeverStream = field(default_factory=FeverStream)  # NEW
```

### 3.4 CLI Handler

```python
# protocols/cli/handlers/tithe.py

@expose(help="Voluntarily discharge entropy pressure")
async def tithe(self, ctx: CommandContext, amount: float = 0.1) -> dict:
    """
    kgents tithe - Pay for order, discharge metabolic pressure.

    The Accursed Share: surplus must be spent. Use this command
    to voluntarily discharge pressure before fever triggers.

    Args:
        amount: How much pressure to discharge (default: 0.1)

    Example:
        kgents tithe
        kgents tithe --amount 0.3
    """
    metabolism = ctx.get_service("metabolism")
    if metabolism is None:
        return {
            "error": "Metabolism not initialized",
            "suggestion": "Start the system first"
        }

    result = metabolism.tithe(amount)

    # Output for user
    ctx.output(f"Discharged: {result['discharged']:.2f}")
    ctx.output(f"Remaining: {result['remaining_pressure']:.2f}")
    ctx.output(f"🙏 {result['gratitude']}")

    return result
```

### 3.5 TUI Integration

Enhance FluxApp with fever mode:

```python
# In FluxApp or a dedicated FeverOverlay widget

class FeverOverlay(Widget):
    """
    Overlay that appears during fever state.
    Shows oblique strategies and visual distortion.
    """

    DEFAULT_CSS = """
    FeverOverlay {
        display: none;
        layer: fever;
        background: rgba(255, 100, 100, 0.1);
        border: heavy #e88a8a;
    }

    FeverOverlay.active {
        display: block;
    }
    """

    def __init__(self, fever_stream: FeverStream):
        super().__init__()
        self._fever_stream = fever_stream
        self._current_strategy = ""

    def compose(self) -> ComposeResult:
        yield Static(id="oblique-strategy")
        yield Static(id="pressure-bar")

    def activate(self, event: FeverEvent) -> None:
        """Show the overlay with fever content."""
        self._current_strategy = self._fever_stream.oblique(event.seed)
        self.query_one("#oblique-strategy").update(
            f"[OBLIQUE] {self._current_strategy}"
        )
        self.add_class("active")

    def deactivate(self) -> None:
        self.remove_class("active")
```

---

## Part IV: Implementation Phases

### Phase 1: MetabolicEngine Core (Day 1)

**Goal**: Implement basic metabolic pressure tracking.

**Files**:
- `impl/claude/protocols/agentese/metabolism/__init__.py` (NEW)
- `impl/claude/protocols/agentese/metabolism/engine.py` (NEW)
- `impl/claude/protocols/agentese/metabolism/_tests/` (NEW)

**Deliverables**:
1. MetabolicEngine dataclass with tick(), tithe()
2. FeverEvent dataclass
3. Integration with existing EntropyPool
4. Unit tests for pressure dynamics

**Tests**:
- `test_pressure_accumulates`: Activity increases pressure
- `test_pressure_decays`: Natural decay over time
- `test_fever_triggers`: Pressure exceeds threshold → FeverEvent
- `test_tithe_discharges`: Voluntary discharge works

### Phase 2: FeverStream (Day 1-2)

**Goal**: Implement creative output during fever.

**Files**:
- `impl/claude/protocols/agentese/metabolism/fever.py` (NEW)
- `impl/claude/protocols/agentese/metabolism/_tests/test_fever.py` (NEW)

**Deliverables**:
1. FeverStream class with oblique() and dream()
2. Oblique Strategies collection (Eno/Schmidt inspired)
3. LLM integration for dream() (optional)

**Tests**:
- `test_oblique_is_cheap`: No LLM cost
- `test_oblique_is_deterministic`: Same seed → same strategy
- `test_dream_fallback`: Falls back to oblique without LLM

### Phase 3: AGENTESE Wiring (Day 2)

**Goal**: Connect to void.* context.

**Files**:
- `impl/claude/protocols/agentese/contexts/void.py` (MODIFY)

**Deliverables**:
1. MetabolicNode for `void.entropy.pressure`, `void.entropy.fever`
2. Update VoidContextResolver with MetabolicEngine
3. Wire tick() to be called on each invoke()

**Tests**:
- `test_void_entropy_pressure_returns_float`
- `test_void_entropy_fever_returns_bool`

### Phase 4: CLI Command (Day 2-3)

**Goal**: Add `kgents tithe` command.

**Files**:
- `impl/claude/protocols/cli/handlers/tithe.py` (NEW)
- `impl/claude/protocols/cli/hollow.py` (MODIFY)

**Deliverables**:
1. `kgents tithe` handler with `--amount` flag
2. Wire to MetabolicEngine.tithe()
3. Reflector output for CLI and FD3

**Tests**:
- `test_tithe_command_discharges_pressure`
- `test_tithe_with_amount_flag`

### Phase 5: TUI Integration (Day 3)

**Goal**: Visual fever manifestation.

**Files**:
- `impl/claude/agents/i/widgets/fever.py` (NEW)
- `impl/claude/agents/i/app.py` (MODIFY)

**Deliverables**:
1. FeverOverlay widget
2. Pressure gauge in status bar
3. Wire GlitchController to FeverEvent

**Tests**:
- `test_fever_overlay_shows_on_event`
- `test_fever_overlay_hides_on_recovery`
- `test_glitch_triggers_on_fever`

---

## Part V: Spec Refinements

Based on this research, the following changes are recommended to `plans/void/entropy.md`:

### 5.1 Clarify Two Pressures

Add section:

```markdown
## Two Pressures: Context vs Metabolic

| Pressure | Source | Response |
|----------|--------|----------|
| Context Pressure | Token accumulation | Compression |
| Metabolic Pressure | Activity accumulation | Fever |

Context pressure is **scarcity** (running out of room).
Metabolic pressure is **surplus** (Accursed Share that must be spent).

The MetabolicEngine tracks metabolic pressure. Context pressure
is handled by ContextWindow (self.stream.pressure).
```

### 5.2 Split FeverStream Operations

Update AGENTESE Path Registry:

```markdown
| Path | Operation | Description | Cost |
|------|-----------|-------------|------|
| `void.entropy.sip` | Draw entropy | Branch via duplicate() | Low |
| `void.entropy.tithe` | Pay for order | Voluntary discharge | Free |
| `void.entropy.pour` | Compost | Return unused entropy | Free |
| `void.entropy.pressure` | Query | Current metabolic pressure | Free |
| `void.entropy.fever` | Check | Is system in fever? | Free |
| `void.entropy.oblique` | Generate | Return Oblique Strategy | Free |
| `void.entropy.dream` | Generate | Fever dream (LLM) | High |
```

### 5.3 Add Oblique Strategies Source

Add appendix:

```markdown
## Appendix: Oblique Strategies

The Oblique Strategies are inspired by Brian Eno and Peter Schmidt's
1975 card deck for breaking creative blocks. Our implementation
curates ~50 strategies appropriate for agent-world interaction:

- "Honor thy error as a hidden intention."
- "Turn it upside down."
- "Gardening, not architecture."
- ...

Full list in `metabolism/fever.py`.
```

### 5.4 Remove Time-Based Language

The original spec has implicit time estimates ("Phase 1.3", "Phase 4.4"). Per project principles, remove timeline implications and focus on dependencies:

```markdown
## Implementation Dependencies

1. MetabolicEngine → depends on EntropyPool (exists)
2. FeverStream → depends on MetabolicEngine
3. CLI Handler → depends on MetabolicEngine, CLI framework (exists)
4. TUI Integration → depends on FeverStream, GlitchController (exists)
```

---

## Part VI: Success Criteria

### 6.1 Functional Requirements

- [ ] `void.entropy.pressure` returns current metabolic pressure (float)
- [ ] `void.entropy.fever` returns fever state (bool)
- [ ] `void.entropy.oblique` returns Oblique Strategy (string, no LLM cost)
- [ ] `kgents tithe` discharges metabolic pressure
- [ ] Fever triggers when pressure exceeds threshold
- [ ] Fever ends when pressure drops below 50% of threshold

### 6.2 Integration Requirements

- [ ] MetabolicEngine.tick() called on each LLM invocation
- [ ] GlitchController.trigger_global_glitch() called on FeverEvent
- [ ] FeverOverlay appears in TUI during fever
- [ ] Oblique Strategy visible in TUI during fever

### 6.3 Quality Requirements

- [ ] All tests pass (`pytest protocols/agentese/metabolism/`)
- [ ] mypy strict passes
- [ ] No regressions in existing void.* tests

---

## Part VII: Open Questions

### Q1: Should MetabolicEngine be global or per-agent?

**Current thinking**: Global. The Accursed Share is a system property, not an agent property. Individual agents contribute to and are affected by system-wide pressure.

**Alternative**: Per-agent engines with cross-agent fever propagation (stigmergic).

### Q2: How should fever affect LLM temperature?

The spec suggests `temperature=1.4` during fever. Options:
1. Hard-coded high temperature during fever
2. Temperature scales with fever intensity
3. Fever just provides context, LLM temperature unchanged

**Recommendation**: Option 2—temperature scales with intensity, capped at 1.5.

### Q3: Should fever be interruptible?

If an agent is in fever but receives a high-priority task, should fever be:
1. Paused (resume after task)
2. Interrupted (ends fever)
3. Concurrent (fever continues in background)

**Recommendation**: Option 3—fever is a background state that colors output, not a blocking mode.

### Q4: What triggers tick()?

Options:
1. Every Logos.invoke() call
2. Only LLM-backed invoke() calls
3. Explicit tick() calls from CLI/runtime

**Recommendation**: Option 2—only actual LLM calls should contribute to metabolic pressure. Static node resolutions don't generate heat.

---

## Appendix A: File Map

```
impl/claude/protocols/agentese/metabolism/
├── __init__.py
├── engine.py           # MetabolicEngine
├── fever.py            # FeverStream, FeverEvent
└── _tests/
    ├── __init__.py
    ├── test_engine.py
    └── test_fever.py

impl/claude/protocols/cli/handlers/
└── tithe.py            # NEW: kgents tithe command

impl/claude/agents/i/widgets/
└── fever.py            # NEW: FeverOverlay widget

# Modified files:
impl/claude/protocols/agentese/contexts/void.py    # Add MetabolicNode
impl/claude/protocols/cli/hollow.py                # Wire tithe handler
impl/claude/agents/i/app.py                        # Add FeverOverlay
```

---

## Appendix B: Test Strategy

**Unit Tests**:
- `test_pressure_dynamics.py`: Accumulation, decay, thresholds
- `test_fever_events.py`: Trigger, recovery, intensity
- `test_fever_stream.py`: Oblique, dream, fallback

**Integration Tests**:
- `test_void_metabolism_integration.py`: AGENTESE path wiring
- `test_cli_tithe.py`: Command execution
- `test_tui_fever.py`: Widget display (mock App)

**Property-Based Tests** (Hypothesis):
- Pressure always ≥ 0
- Fever only triggers when pressure > threshold
- Tithe always reduces pressure
- Oblique is deterministic given seed

---

*"Without the Accursed Share, your agents are just scripts."*
