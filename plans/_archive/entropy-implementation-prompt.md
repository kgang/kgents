# void/entropy Implementation Prompt

> Use this prompt to guide AI agents implementing the Metabolism system.

---

## Context

You are implementing the **Metabolic Engine** for kgents—the thermodynamic heart that tracks activity pressure and triggers creative "fever" events when the system runs hot. This implements the **Accursed Share** principle: surplus must be spent, not suppressed.

**Key Insight**: There are TWO distinct pressures in kgents:
- **Context Pressure** (`self.stream.pressure`): Token accumulation in ContextWindow → triggers compression
- **Metabolic Pressure** (`void.entropy.pressure`): Activity accumulation from LLM calls → triggers fever

You are implementing metabolic pressure. Do NOT confuse it with context pressure.

---

## What Already Exists

Before writing any code, read these existing files:

### Core void.* Implementation
**File**: `impl/claude/protocols/agentese/contexts/void.py` (999 lines)

This file already implements:
- `EntropyPool` (lines 42-163): Budget tracking for entropy draws
- `RandomnessGrant` (lines 169-199): Grants from the pool
- `EntropyNode` (lines 204-267): `void.entropy.sip/pour/sample/status`
- `SerendipityNode` (lines 269-428): `void.serendipity.sip/inspire/tangent`
- `GratitudeNode` (lines 431-517): `void.gratitude.tithe/thank/acknowledge`
- `CapitalNode` (lines 519-645): `void.capital.*` social capital ledger
- `PataphysicsNode` (lines 650-864): `void.pataphysics.solve/melt/verify/imagine`
- `VoidContextResolver` (lines 869-924): Routes void.* paths

**DO NOT** duplicate this functionality. You are ADDING to it.

### Glitch System (TUI Integration Point)
**File**: `impl/claude/agents/i/widgets/glitch.py` (500 lines)

This file implements visual entropy manifestation:
- `GlitchController`: Coordinates glitch effects across UI
- `GlitchEvent`: Record of a glitch trigger
- `trigger_global_glitch()`: Screen-wide effects
- `on_void_phase()`: Agent-specific glitches
- `GlitchIndicator`: Widget showing glitch state

Wire your `FeverEvent` to trigger `GlitchController.trigger_global_glitch()`.

### Context Window (Temperature Signal)
**File**: `impl/claude/agents/d/context_window.py`

Relevant properties:
- `pressure`: Token ratio (0.0-1.0)
- `total_tokens`: Current token count
- `max_tokens`: Budget limit
- `needs_compression`: True if pressure > 0.7

Use `ContextWindow.pressure` as a temperature signal, but track metabolic pressure separately.

### AGENTESE Logos Resolver
**File**: `impl/claude/protocols/agentese/logos.py`

The Logos resolves AGENTESE paths like `void.entropy.pressure`. Your new paths must be wired through `VoidContextResolver.resolve()`.

### CLI Framework
**File**: `impl/claude/protocols/cli/hollow.py`

CLI commands use the `@expose` decorator. See existing handlers in `protocols/cli/handlers/` for patterns.

---

## What You Must Implement

### 1. MetabolicEngine (`protocols/agentese/metabolism/engine.py`)

```python
@dataclass
class MetabolicEngine:
    """
    The thermodynamic heart of the system.

    Tracks activity-based pressure (not token budget).
    Triggers fever when surplus accumulates beyond threshold.
    """

    # Pressure state
    pressure: float = 0.0
    critical_threshold: float = 1.0
    decay_rate: float = 0.01  # Natural decay per tick

    # Token thermometer (temperature signal)
    input_tokens: int = 0
    output_tokens: int = 0

    # Fever state
    in_fever: bool = False
    fever_start: float | None = None

    # Integration (injected)
    _entropy_pool: EntropyPool | None = None
    _glitch_controller: GlitchController | None = None

    @property
    def temperature(self) -> float:
        """
        Token-based temperature.

        High input:output = cold (receiving more than giving)
        Low input:output = hot (giving more than receiving)
        """
        if self.output_tokens == 0:
            return 0.0
        return min(2.0, self.input_tokens / self.output_tokens)

    def tick(self, input_count: int, output_count: int) -> FeverEvent | None:
        """
        Called per LLM invocation (not static resolutions).

        Returns FeverEvent if pressure exceeds threshold.
        """
        # Implement: accumulate pressure, apply decay, check threshold
        pass

    def _trigger_fever(self) -> FeverEvent:
        """Forced creative expenditure."""
        # Implement: set fever state, draw from entropy pool, discharge pressure
        pass

    def _end_fever(self) -> None:
        """End fever state when pressure drops below 50% of threshold."""
        pass

    def tithe(self, amount: float = 0.1) -> dict[str, Any]:
        """Voluntary pressure discharge."""
        # Implement: reduce pressure, call entropy_pool.tithe() if available
        pass
```

### 2. FeverEvent and FeverStream (`protocols/agentese/metabolism/fever.py`)

```python
@dataclass
class FeverEvent:
    """Record of a fever trigger."""
    intensity: float          # How far above threshold
    timestamp: float          # When triggered
    trigger: str              # "pressure_overflow", "manual", "error"
    seed: float               # For deterministic oblique selection
    oblique_strategy: str = ""  # Populated by FeverStream


@dataclass
class FeverStream:
    """
    Generates creative output during fever state.

    Two modes:
    - oblique: Quick, no LLM (Oblique Strategies) - FREE
    - dream: Slow, uses LLM - EXPENSIVE
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
        "Consider the opposite.",
        "What if you're already at the destination?",
        "The path is made by walking.",
        "Remove ambiguities and convert to specifics.",
        "Change instrument roles.",
    )

    def oblique(self, seed: float | None = None) -> str:
        """Return an Oblique Strategy. Cost: FREE. Deterministic given seed."""
        pass

    async def dream(self, context: dict, llm_client: Any = None) -> str:
        """Generate fever dream via LLM. Falls back to oblique() if no client."""
        pass
```

### 3. MetabolicNode (`protocols/agentese/contexts/void.py` - MODIFY)

Add a new node class to handle the new paths:

```python
@dataclass
class MetabolicNode(BaseLogosNode):
    """
    void.entropy.pressure/fever/oblique/dream

    Metabolic pressure tracking and fever generation.
    """

    _handle: str = "void.metabolism"  # or extend EntropyNode
    _engine: MetabolicEngine
    _fever_stream: FeverStream

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        return ("pressure", "fever", "oblique", "dream", "tithe")

    async def _invoke_aspect(self, aspect: str, observer: Umwelt, **kwargs) -> Any:
        match aspect:
            case "pressure":
                return {"pressure": self._engine.pressure, "in_fever": self._engine.in_fever}
            case "fever":
                return {"in_fever": self._engine.in_fever, "fever_start": self._engine.fever_start}
            case "oblique":
                seed = kwargs.get("seed")
                return {"strategy": self._fever_stream.oblique(seed)}
            case "dream":
                context = kwargs.get("context", {})
                llm = kwargs.get("llm_client")
                dream = await self._fever_stream.dream(context, llm)
                return {"dream": dream}
            case "tithe":
                amount = kwargs.get("amount", 0.1)
                return self._engine.tithe(amount)
```

Update `VoidContextResolver` to include MetabolicNode.

### 4. CLI Handler (`protocols/cli/handlers/tithe.py` - NEW)

```python
from ..handler import CommandContext, expose

@expose(help="Voluntarily discharge entropy pressure")
async def tithe(ctx: CommandContext, amount: float = 0.1) -> dict:
    """
    kgents tithe - Pay for order, discharge metabolic pressure.

    The Accursed Share: surplus must be spent.
    """
    metabolism = ctx.get_service("metabolism")
    if metabolism is None:
        ctx.output("[yellow]Metabolism not initialized[/yellow]")
        return {"error": "Metabolism not initialized"}

    result = metabolism.tithe(amount)

    ctx.output(f"Discharged: {result['discharged']:.2f}")
    ctx.output(f"Remaining: {result['remaining_pressure']:.2f}")
    ctx.output(result['gratitude'])

    return result
```

Wire this in `hollow.py` following the pattern of other handlers.

### 5. Tests (`protocols/agentese/metabolism/_tests/`)

Create comprehensive tests:

```python
# test_engine.py
class TestMetabolicEngine:
    def test_pressure_accumulates(self):
        """Activity increases pressure."""
        engine = MetabolicEngine()
        engine.tick(100, 100)
        assert engine.pressure > 0

    def test_pressure_decays(self):
        """Natural decay reduces pressure over time."""
        engine = MetabolicEngine(pressure=1.0)
        engine.tick(0, 0)  # No activity, just decay
        assert engine.pressure < 1.0

    def test_fever_triggers_at_threshold(self):
        """Pressure exceeding threshold triggers fever."""
        engine = MetabolicEngine(critical_threshold=0.5)
        # Pump up pressure
        for _ in range(100):
            event = engine.tick(1000, 1000)
            if event is not None:
                break
        assert engine.in_fever
        assert event is not None
        assert event.trigger == "pressure_overflow"

    def test_fever_ends_at_recovery(self):
        """Fever ends when pressure drops below 50% of threshold."""
        engine = MetabolicEngine(critical_threshold=1.0, in_fever=True, pressure=0.4)
        engine.tick(0, 0)  # Trigger recovery check
        assert not engine.in_fever

    def test_tithe_discharges_pressure(self):
        """Voluntary tithe reduces pressure."""
        engine = MetabolicEngine(pressure=0.5)
        result = engine.tithe(0.2)
        assert engine.pressure == 0.3
        assert result["discharged"] == 0.2

# test_fever.py
class TestFeverStream:
    def test_oblique_is_deterministic(self):
        """Same seed produces same strategy."""
        stream = FeverStream()
        s1 = stream.oblique(0.5)
        s2 = stream.oblique(0.5)
        assert s1 == s2

    def test_oblique_varies_with_seed(self):
        """Different seeds produce different strategies."""
        stream = FeverStream()
        s1 = stream.oblique(0.1)
        s2 = stream.oblique(0.9)
        assert s1 != s2

    async def test_dream_falls_back_to_oblique(self):
        """Without LLM client, dream() returns oblique strategy."""
        stream = FeverStream()
        result = await stream.dream({}, llm_client=None)
        assert result in stream._oblique_strategies
```

---

## File Structure

Create this structure:

```
impl/claude/protocols/agentese/metabolism/
├── __init__.py          # Export MetabolicEngine, FeverEvent, FeverStream
├── engine.py            # MetabolicEngine implementation
├── fever.py             # FeverEvent, FeverStream
└── _tests/
    ├── __init__.py
    ├── test_engine.py
    └── test_fever.py

impl/claude/protocols/cli/handlers/
└── tithe.py             # NEW: kgents tithe command
```

Modify:
- `impl/claude/protocols/agentese/contexts/void.py` - Add MetabolicNode, update VoidContextResolver
- `impl/claude/protocols/cli/hollow.py` - Wire tithe handler

---

## Integration Points

### 1. Wire tick() to LLM Invocations

Find where LLM calls happen and call `metabolism.tick(input_tokens, output_tokens)`. Look in:
- `impl/claude/runtime/` for runtime LLM calls
- `impl/claude/infra/cortex/` for Cortex service calls

### 2. Wire FeverEvent to GlitchController

When `_trigger_fever()` returns a FeverEvent:

```python
if self._glitch_controller:
    asyncio.create_task(
        self._glitch_controller.trigger_global_glitch(
            intensity=event.intensity * 0.5,
            duration_ms=int(200 + event.intensity * 100),
            source="fever",
        )
    )
```

### 3. Make MetabolicEngine a Service

The CLI handler needs `ctx.get_service("metabolism")`. Register it wherever services are initialized (likely in Cortex or CLI bootstrap).

---

## Principles to Follow

### From `spec/principles.md`:

1. **Accursed Share**: Surplus must be spent. Fever is the mechanism for spending accumulated activity surplus.

2. **Joy-Inducing**: Oblique Strategies should be delightful, not annoying. They're gifts from the void.

3. **Composable**: MetabolicEngine should work independently or integrated. Don't create hard dependencies.

4. **Graceful Degradation**: If EntropyPool or GlitchController aren't available, the engine still works.

### From `spec/protocols/agentese.md`:

1. **No View From Nowhere**: All AGENTESE invocations require an observer (Umwelt).

2. **Sympathetic Errors**: When things fail, explain why and suggest what to do.

3. **Affordances Are Permissions**: Check affordances before allowing aspects.

---

## Success Criteria

### Functional
- [ ] `void.entropy.pressure` returns `{"pressure": float, "in_fever": bool}`
- [ ] `void.entropy.fever` returns `{"in_fever": bool, "fever_start": float | None}`
- [ ] `void.entropy.oblique` returns `{"strategy": str}` with no LLM cost
- [ ] `void.entropy.dream` returns `{"dream": str}` via LLM or fallback
- [ ] `kgents tithe` discharges pressure and outputs gratitude
- [ ] Fever triggers when pressure > critical_threshold
- [ ] Fever ends when pressure < critical_threshold * 0.5

### Integration
- [ ] MetabolicEngine receives tick() calls from LLM invocations
- [ ] FeverEvent triggers GlitchController (if available)
- [ ] CLI can access metabolism service

### Quality
- [ ] All tests pass: `pytest protocols/agentese/metabolism/`
- [ ] mypy strict passes: `mypy protocols/agentese/metabolism/`
- [ ] No regressions in void.* tests: `pytest protocols/agentese/contexts/_tests/`

---

## Reference Documents

Read these before implementing:

| Document | Purpose |
|----------|---------|
| `plans/void/entropy.md` | The spec you're implementing |
| `plans/void/entropy-research-report.md` | Detailed research and rationale |
| `spec/principles.md` | Core principles (especially Accursed Share) |
| `spec/protocols/agentese.md` | AGENTESE patterns and requirements |
| `impl/claude/protocols/agentese/contexts/void.py` | Existing void.* implementation |
| `impl/claude/agents/i/widgets/glitch.py` | Glitch system for TUI integration |
| `impl/claude/agents/d/context_window.py` | Context pressure (don't confuse with metabolic) |

---

## Common Mistakes to Avoid

1. **Don't duplicate EntropyPool**: It already exists. MetabolicEngine USES it, doesn't replace it.

2. **Don't confuse pressures**: Context pressure is about tokens. Metabolic pressure is about activity.

3. **Don't make fever blocking**: Fever is a background state that colors output, not a mode that stops work.

4. **Don't require LLM for oblique()**: Oblique Strategies must be FREE. Only dream() uses LLM.

5. **Don't forget decay**: Pressure must decay naturally each tick, or it will only ever increase.

6. **Don't hard-code dependencies**: Use dependency injection for EntropyPool, GlitchController.

---

## Questions to Ask Before Starting

1. Where exactly should `metabolism.tick()` be called? (Find LLM invocation points)
2. Where are services registered? (For CLI access)
3. Should MetabolicEngine be a singleton or instantiated per-session?
4. How should fever interact with the Reflector system for FD3 output?

---

*"The river that flows only downhill never discovers the mountain spring."*
