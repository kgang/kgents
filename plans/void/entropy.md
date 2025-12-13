---
path: void/entropy
status: dormant
progress: 85
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [self/stream]
session_notes: |
  Core metabolism + Flux integration complete (36 + 21 = 57 tests).
  CLI tithe command complete (12 tests).
  Total: 69 tests. Only TUI FeverOverlay remaining.
---

# Metabolism: void.entropy.* Implementation

> *"Without the Accursed Share, your agents are just scripts."*

**AGENTESE Context**: `void.entropy.*`
**Status**: Flux Integration Complete, TUI/CLI Remaining
**Principles**: Accursed Share, Joy-Inducing
**Research**: See `entropy-research-report.md` for detailed analysis

---

## Current State

**Already Implemented** (in `protocols/agentese/contexts/void.py`):

| Component | Path | Status |
|-----------|------|--------|
| EntropyPool | `void.entropy.sip/pour/status` | ✅ Complete |
| SerendipityNode | `void.serendipity.sip/inspire` | ✅ Complete |
| GratitudeNode | `void.gratitude.tithe/thank` | ✅ Complete |
| CapitalNode | `void.capital.*` | ✅ Complete |
| PataphysicsNode | `void.pataphysics.solve` | ✅ Complete |

**Core Metabolism** (in `protocols/agentese/metabolism/`):

| Component | Path | Status |
|-----------|------|--------|
| MetabolicEngine | `void.entropy.pressure/fever` | ✅ Complete (36 tests) |
| FeverStream | `void.entropy.oblique/dream` | ✅ Complete |
| FluxMetabolism | `agents/flux/metabolism.py` | ✅ Complete (21 tests) |
| FluxAgent integration | `agents/flux/agent.py` | ✅ Complete |

**Remaining** (TUI/CLI polish):

| Component | Path | Status |
|-----------|------|--------|
| TitheHandler | `kgents tithe` | 📋 Planned |
| FeverOverlay | TUI widget | 📋 Planned |

---

## Key Insight: Two Pressures

The system has **two distinct pressures** that should not be conflated:

| Pressure Type | Source | Response | Location |
|---------------|--------|----------|----------|
| **Context Pressure** | Token accumulation in ContextWindow | Compression (drop/summarize) | `self.stream.pressure` |
| **Metabolic Pressure** | Activity accumulation (LLM calls) | Fever (creative expenditure) | `void.entropy.pressure` |

**Context pressure** is about **scarcity** (running out of room).
**Metabolic pressure** is about **surplus** (the Accursed Share that must be spent).

The MetabolicEngine uses context pressure as a **temperature signal** but tracks its own pressure separately.

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Separate pressures** | Context and metabolic pressure serve different purposes |
| **Token Thermometer** | Input/output ratio indicates system "temperature" |
| **Oblique Strategies** | Cheap (no LLM), deterministic given seed |
| **Fever Dreams** | Expensive (LLM), optional enhancement |
| **Global Engine** | One MetabolicEngine for whole system, not per-agent |
| **Non-blocking Fever** | Fever is a state that colors output, not a blocking mode |

---

## The Accursed Share

Every system accumulates surplus. The Accursed Share principle says this excess must be **spent, not suppressed**.

In kgents:
- **Pressure accumulates** from agent activity (LLM calls)
- **Fever triggers** when pressure exceeds threshold
- **Oblique Strategies** provide cheap creative output
- **Fever Dreams** provide expensive creative output (optional)
- **Tithe** allows voluntary discharge

---

## Metabolic Engine

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

    # Token thermometer
    input_tokens: int = 0
    output_tokens: int = 0

    # Fever state
    in_fever: bool = False
    fever_start: float | None = None

    # Integration
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
        self.input_tokens += input_count
        self.output_tokens += output_count

        # Pressure accumulates based on activity
        activity = (input_count + output_count) * 0.001
        self.pressure += activity

        # Natural decay
        self.pressure *= (1.0 - self.decay_rate)

        # Check fever state
        if self.pressure > self.critical_threshold and not self.in_fever:
            return self._trigger_fever()

        if self.in_fever and self.pressure < self.critical_threshold * 0.5:
            self._end_fever()

        return None

    def _trigger_fever(self) -> FeverEvent:
        """Forced creative expenditure."""
        self.in_fever = True
        self.fever_start = time.time()

        intensity = self.pressure - self.critical_threshold

        # Draw from entropy pool if available
        seed = random.random()
        if self._entropy_pool:
            try:
                grant = self._entropy_pool.sip(intensity * 0.5)
                seed = grant.get("seed", seed)
            except BudgetExhaustedError:
                pass

        # Discharge pressure
        self.pressure *= 0.5

        return FeverEvent(
            intensity=intensity,
            timestamp=time.time(),
            trigger="pressure_overflow",
            seed=seed,
        )

    def _end_fever(self) -> None:
        """End fever state."""
        self.in_fever = False
        self.fever_start = None

    def tithe(self, amount: float = 0.1) -> dict[str, Any]:
        """Voluntary pressure discharge."""
        self.pressure = max(0.0, self.pressure - amount)

        if self._entropy_pool:
            self._entropy_pool.tithe()

        return {
            "discharged": amount,
            "remaining_pressure": self.pressure,
            "gratitude": "The river flows.",
        }
```

**Location**: `protocols/agentese/metabolism/engine.py`

---

## Fever Events and Stream

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
    - oblique: Quick, no LLM (Oblique Strategies)
    - dream: Slow, uses LLM (optional)
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
        """
        Return an Oblique Strategy.

        Cost: FREE (no LLM)
        Deterministic: Same seed -> same strategy
        """
        if seed is None:
            seed = random.random()
        idx = int(seed * len(self._oblique_strategies))
        return self._oblique_strategies[idx % len(self._oblique_strategies)]

    async def dream(
        self,
        context: dict,
        llm_client: Any = None,
    ) -> str:
        """
        Generate a fever dream from current context.

        Cost: HIGH (uses LLM with temperature=1.4)
        Falls back to oblique() if no LLM client.
        """
        if llm_client is None:
            return self.oblique()

        prompt = f"""
        The system is running hot. Context (truncated):
        {json.dumps(context, indent=2, default=str)[:1000]}

        Generate an oblique strategy—a sideways thought that might
        illuminate the problem from an unexpected angle.

        Be brief, enigmatic, potentially useful.
        """

        return await llm_client.generate(
            prompt,
            temperature=1.4,
            max_tokens=100,
        )
```

**Location**: `protocols/agentese/metabolism/fever.py`

---

## Tithe Command

```python
# protocols/cli/handlers/tithe.py

@expose(help="Voluntarily discharge entropy pressure")
async def tithe(self, ctx: CommandContext, amount: float = 0.1) -> dict:
    """
    kgents tithe - Pay for order, discharge metabolic pressure.

    The Accursed Share: surplus must be spent. Use this command
    to voluntarily discharge pressure before fever triggers.
    """
    metabolism = ctx.get_service("metabolism")
    if metabolism is None:
        return {"error": "Metabolism not initialized"}

    result = metabolism.tithe(amount)

    ctx.output(f"Discharged: {result['discharged']:.2f}")
    ctx.output(f"Remaining: {result['remaining_pressure']:.2f}")
    ctx.output(f"{result['gratitude']}")

    return result
```

**Usage**:
```bash
kgents tithe             # Discharge default amount
kgents tithe --amount 0.3  # Discharge more
```

---

## TUI Integration

When pressure exceeds threshold, the FluxApp TUI shows:
- Pressure gauge in status bar
- Fever overlay with oblique strategy
- Glitch effects via GlitchController

```
+-------------------------------------------------------------+
| FLUX                            [Pressure: ||||||||.. 82%]  |
|                                 ~~~ FEVER ~~~                |
+-------------------------------------------------------------+
|                                                              |
|  [OBLIQUE] "Honor thy error as a hidden intention."         |
|                                                              |
|  ...rest of TUI with subtle visual distortions...           |
+-------------------------------------------------------------+
```

Wire to existing GlitchController:
- `trigger_global_glitch()` on FeverEvent
- `on_void_phase()` for agent-specific effects
- Intensity scales with fever intensity

---

## AGENTESE Path Registry

| Path | Operation | Description | Cost |
|------|-----------|-------------|------|
| `void.entropy.sip` | Draw | Branch via duplicate() | Low |
| `void.entropy.pour` | Return | Recover 50% of unused | Free |
| `void.entropy.tithe` | Discharge | Voluntary pressure release | Free |
| `void.entropy.pressure` | Query | Current metabolic pressure | Free |
| `void.entropy.fever` | Check | Is system in fever? | Free |
| `void.entropy.oblique` | Generate | Return Oblique Strategy | Free |
| `void.entropy.dream` | Generate | Fever dream (LLM) | High |

---

## Pressure Dynamics

```
             pressure
                ^
                |
    threshold --|-------------- fever trigger
                |      /\
                |     /  \   /\
                |    /    \_/  \
                |   /           \
                |  /             \_____  <- recovery at 50%
                | /                    \___
                |/                          \____
                +---------------------------------> time
                     ^        ^          ^
                     |        |          |
                   tick()   fever()    tithe()
```

- **tick()**: Adds pressure per LLM call
- **decay**: Natural 1% decay per tick
- **fever()**: Forced discharge at threshold (50% reduction)
- **tithe()**: Voluntary discharge
- **recovery**: Fever ends when pressure < 50% of threshold

---

## Implementation Dependencies

```
1. MetabolicEngine
   ├── depends: EntropyPool (exists)
   └── enables: FeverStream, CLI handler

2. FeverStream
   ├── depends: MetabolicEngine
   └── enables: TUI integration

3. CLI Handler
   ├── depends: MetabolicEngine
   ├── depends: CLI framework (exists)
   └── enables: User interaction

4. TUI Integration
   ├── depends: FeverStream
   ├── depends: GlitchController (exists)
   └── enables: Visual feedback
```

---

## Implementation Checklist

### Core Engine ✅ COMPLETE
- [x] `MetabolicEngine` dataclass
- [x] `FeverEvent` dataclass
- [x] `tick()` with pressure accumulation and decay
- [x] `_trigger_fever()` with entropy draw
- [x] `tithe()` for voluntary discharge
- [x] Integration with EntropyPool

### FeverStream ✅ COMPLETE
- [x] `FeverStream` class
- [x] Oblique Strategies collection (~20 strategies)
- [x] `oblique()` deterministic selection
- [x] `dream()` LLM generation (optional)

### Flux Integration ✅ COMPLETE (2025-12-12)
- [x] `FluxMetabolism` adapter class
- [x] `attach_metabolism()` / `detach_metabolism()` methods
- [x] Wire to `FluxAgent._process_flux()`
- [x] Fever callback integration
- [x] 21 tests in `agents/flux/_tests/test_metabolism.py`

### AGENTESE Wiring (Partial)
- [ ] `MetabolicNode` for pressure/fever/oblique paths
- [ ] Update `VoidContextResolver`
- [x] Wire `tick()` to FluxAgent event processing

### CLI Handler ✅ COMPLETE
- [x] `tithe.py` handler
- [x] Wire to `hollow.py`
- [x] Reflector output
- [x] 12 tests in `protocols/cli/handlers/_tests/test_tithe.py`

### TUI Integration
- [ ] `FeverOverlay` widget
- [ ] Pressure gauge in status bar
- [ ] Wire to GlitchController

### Tests ✅ COMPLETE
- [x] `test_engine.py`: Pressure dynamics (36 tests)
- [x] `test_fever.py`: FeverStream behavior
- [x] `test_metabolism.py`: Flux integration (21 tests)
- [x] `test_tithe.py`: Command execution (12 tests)

---

## Success Criteria

### Functional
- [ ] `void.entropy.pressure` returns float
- [ ] `void.entropy.fever` returns bool
- [ ] `void.entropy.oblique` returns strategy (no LLM cost)
- [ ] `kgents tithe` discharges pressure
- [ ] Fever triggers at threshold
- [ ] Fever ends at 50% of threshold

### Integration
- [ ] MetabolicEngine.tick() called on LLM invocations
- [ ] GlitchController triggers on FeverEvent
- [ ] FeverOverlay appears in TUI

### Quality
- [ ] All tests pass
- [ ] mypy strict passes
- [ ] No regressions in void.* tests

---

## Cross-References

- **Plans**: `self/stream.md` (Phase 2.2 ModalScope), `concept/creativity.md`
- **Impl**: `protocols/agentese/contexts/void.py` (existing), `protocols/agentese/metabolism/` (new)
- **Spec**: `spec/principles.md` (Accursed Share), `spec/protocols/agentese.md`
- **TUI**: `agents/i/widgets/glitch.py` (existing)
- **Research**: `entropy-research-report.md`

---

## Appendix: Oblique Strategies Source

The Oblique Strategies are inspired by Brian Eno and Peter Schmidt's 1975 card deck for breaking creative blocks. Our implementation curates strategies appropriate for agent-world interaction.

Original deck: ~100 cards. Our curation: ~20 strategies focusing on:
- Process reframing ("Turn it upside down")
- Perspective shifts ("What would your closest friend do?")
- Temporal advice ("Work at a different speed")
- Metaphorical guidance ("Gardening, not architecture")

Full list in `metabolism/fever.py`.

---

*"The river that flows only downhill never discovers the mountain spring."*
