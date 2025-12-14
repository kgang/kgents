# Reactive Substrate Unification - Implementation Prompt

## Context

You are implementing the **Reactive Substrate Unification** - a Crown Jewel extension that creates a unified widget abstraction layer enabling the same widget definition to render across CLI, TUI (Textual), marimo notebooks, and JSON API responses.

**Plan**: `plans/reactive-substrate-unification.md`
**Research**: `plans/meta/v0-ui-learnings-synthesis.md` (critical reading!)
**Synergy**: Ties directly into `plans/agentese-universal-protocol.md`

## Key Insights from V0-UI Research

The v0-ui-mock React codebase revealed six critical patterns we must adopt:

### 1. Pure Entropy Algebra
```python
# NO random.random() in render paths!
distortion = entropy_to_distortion(entropy, seed, t)  # Pure function
personality = generate_personality(seed)  # Deterministic from seed
```

### 2. Time Flows Downward
```python
# Parent provides t to children - ensures deterministic tree rendering
def render(self, t: float):
    for child in self.children:
        child.render(t=t)
```

### 3. Projections Are Manifest
```python
# project() IS logos.invoke("manifest", observer)
# Same state, different targets
widget.project(RenderTarget.CLI)     # → ASCII
widget.project(RenderTarget.TUI)     # → Textual widget
widget.project(RenderTarget.MARIMO)  # → anywidget
widget.project(RenderTarget.JSON)    # → dict (for API)
```

### 4. Glyph as Atomic Unit
Everything renders to glyphs. Glyphs compose into Bars, Bars into Cards, Cards into Screens.

### 5. Deterministic Joy
```python
# Same seed → same personality, forever
personality = generate_personality(hash_string(agent_id))
```

### 6. Slots/Fillers Composition
Widgets define slots; any compatible widget can fill a slot. This is operad-like.

## Current Phase: IMPLEMENT (Wave 1: Core Primitives)

### Your Mission

Build the foundational reactive primitives and the Glyph widget as the atomic unit.

### Files to Create

```
impl/claude/agents/i/reactive/
├── __init__.py
├── signal.py           # Signal[T], Computed[T], Effect
├── entropy.py          # Pure entropy algebra (from v0 learnings)
├── joy.py              # Deterministic personality generation
├── widget.py           # KgentsWidget[S] base class
├── projectors.py       # RenderTarget enum + projector protocol
├── primitives/
│   ├── __init__.py
│   └── glyph.py        # The atomic visual unit
└── _tests/
    ├── __init__.py
    ├── test_signal.py
    ├── test_entropy.py
    ├── test_joy.py
    └── test_glyph.py
```

### Implementation Details

#### 1. Signal[T] - The Reactive Primitive

```python
# signal.py
from typing import TypeVar, Generic, Callable
from dataclasses import dataclass, field

T = TypeVar("T")

@dataclass
class Signal(Generic[T]):
    """
    Observable state primitive.

    Equivalent to:
    - Textual: reactive() attribute
    - Marimo: Cell variable
    - React: useState()
    - Solid: createSignal()

    Key: Pure, no side effects in the primitive itself.
    """

    _value: T
    _subscribers: list[Callable[[T], None]] = field(default_factory=list)

    @classmethod
    def of(cls, value: T) -> "Signal[T]":
        """Create a signal with initial value."""
        return cls(_value=value)

    @property
    def value(self) -> T:
        return self._value

    def set(self, new_value: T) -> None:
        if new_value != self._value:
            self._value = new_value
            for sub in self._subscribers:
                sub(new_value)

    def update(self, fn: Callable[[T], T]) -> None:
        self.set(fn(self._value))

    def subscribe(self, callback: Callable[[T], None]) -> Callable[[], None]:
        self._subscribers.append(callback)
        return lambda: self._subscribers.remove(callback)

    def map(self, fn: Callable[[T], "U"]) -> "Computed[U]":
        """Functor map - create derived signal."""
        return Computed(compute=lambda: fn(self._value), sources=[self])
```

#### 2. Entropy Algebra (Pure Functions)

```python
# entropy.py
import math
from dataclasses import dataclass

PHI = 1.618033988749  # Golden ratio

@dataclass(frozen=True)
class VisualDistortion:
    blur: float
    skew: float
    jitter_x: float
    jitter_y: float
    pulse: float

def entropy_to_distortion(
    entropy: float,
    seed: int,
    t: float = 0.0,
) -> VisualDistortion:
    """
    Pure function: (entropy, seed, t) → VisualDistortion

    NO RANDOMNESS! Same inputs → same output, always.
    This is critical for deterministic rendering.
    """
    e = max(0.0, min(1.0, entropy))

    def hash_fn(n: float) -> float:
        return (n * PHI) % 1.0

    intensity = e * e  # Non-linear for drama

    wave = math.sin(t * 0.001 + seed)
    wave2 = math.cos(t * 0.0013 + seed * PHI)

    return VisualDistortion(
        blur=intensity * 2 * (1 + wave * 0.3),
        skew=intensity * 8 * wave2,
        jitter_x=intensity * 4 * hash_fn(seed) * wave,
        jitter_y=intensity * 4 * hash_fn(seed + 1) * wave2,
        pulse=1 + intensity * 0.15 * math.sin(t * 0.002 + seed),
    )

# ASCII density characters
DENSITY_RUNES = " ·∴∵◦○◎●◉█"
SPARK_CHARS = "▁▂▃▄▅▆▇█"

PHASE_GLYPHS = {
    "idle": "○",
    "active": "◉",
    "waiting": "◐",
    "error": "◈",
    "yielding": "◇",
}
```

#### 3. Glyph Widget (Atomic Unit)

```python
# primitives/glyph.py
from dataclasses import dataclass
from typing import Literal
from ..widget import KgentsWidget, RenderTarget
from ..signal import Signal
from ..entropy import entropy_to_distortion, PHASE_GLYPHS

Phase = Literal["idle", "active", "waiting", "error", "yielding"]

@dataclass(frozen=True)
class GlyphState:
    """Immutable glyph state."""
    char: str = "·"
    fg: str | None = None
    bg: str | None = None
    phase: Phase | None = None
    entropy: float = 0.0
    seed: int = 0
    t: float = 0.0
    animate: Literal["none", "pulse", "blink", "breathe", "wiggle"] = "none"

class GlyphWidget(KgentsWidget[GlyphState]):
    """
    The atomic visual unit. Everything composes from Glyphs.

    A Glyph:
    - Has deterministic visual state (no randomness)
    - Responds to entropy with graceful distortion
    - Carries semantic meaning through phase
    - Time (t) is passed from parent, not managed internally
    """

    def __init__(self, initial: GlyphState | None = None):
        self.state = Signal.of(initial or GlyphState())

    def with_time(self, t: float) -> "GlyphWidget":
        """Return new glyph with updated time. Immutable pattern."""
        current = self.state.value
        new_state = GlyphState(
            char=current.char,
            fg=current.fg,
            bg=current.bg,
            phase=current.phase,
            entropy=current.entropy,
            seed=current.seed,
            t=t,  # Updated
            animate=current.animate,
        )
        widget = GlyphWidget(new_state)
        return widget

    def project(self, target: RenderTarget) -> str | dict | object:
        state = self.state.value

        # Compute distortion if entropy > threshold
        distortion = None
        if state.entropy > 0.1:
            distortion = entropy_to_distortion(state.entropy, state.seed, state.t)

        # Resolve character
        char = state.char
        if state.phase and state.char == "·":
            char = PHASE_GLYPHS.get(state.phase, state.char)

        match target:
            case RenderTarget.CLI:
                return char  # Just the character
            case RenderTarget.TUI:
                return self._to_rich_text(char, state, distortion)
            case RenderTarget.MARIMO:
                return self._to_html_span(char, state, distortion)
            case RenderTarget.JSON:
                return {
                    "type": "glyph",
                    "char": char,
                    "phase": state.phase,
                    "entropy": state.entropy,
                    "distortion": distortion.__dict__ if distortion else None,
                }

    def _to_rich_text(self, char: str, state: GlyphState, distortion) -> "Text":
        """Convert to Rich Text for Textual."""
        from rich.text import Text
        style = f"[{state.fg or 'default'}]"
        if state.bg:
            style = f"[{state.fg or 'default'} on {state.bg}]"
        return Text(char, style=style)

    def _to_html_span(self, char: str, state: GlyphState, distortion) -> str:
        """Convert to HTML span for anywidget/marimo."""
        style_parts = []
        if state.fg:
            style_parts.append(f"color: {state.fg}")
        if distortion:
            style_parts.append(f"filter: blur({distortion.blur}px)")
            style_parts.append(f"transform: skewX({distortion.skew}deg)")
        style = "; ".join(style_parts)
        return f'<span style="{style}">{char}</span>'
```

### Integration Points

#### With Existing Marimo Bridge

The marimo integration in `impl/claude/agents/i/marimo/` already has `LogosCell`. The new reactive substrate should integrate:

```python
# In marimo notebook
from impl.claude.agents.i.reactive.primitives.glyph import GlyphWidget, GlyphState

@app.cell
def glyph_demo():
    glyph = GlyphWidget(GlyphState(
        char="◉",
        phase="active",
        entropy=0.3,
        seed=42,
        t=time.time(),
    ))
    # Project to marimo-compatible output
    return mo.Html(glyph.project(RenderTarget.MARIMO))
```

#### With AGENTESE Universal Protocol

The JSON projection IS the API response:

```python
# In AgenteseBridge
async def invoke(self, handle: str, observer: ObserverContext, **kwargs):
    result = await self.logos.invoke(handle, umwelt, **kwargs)

    if isinstance(result, KgentsWidget):
        return AgenteseResponse(
            handle=handle,
            result=result.project(RenderTarget.JSON),  # Uses JSON projector
            meta=ResponseMeta(...),
        )
```

### Test Requirements

#### test_signal.py
- `test_signal_of` - Creation works
- `test_signal_set_notifies` - Subscribers called on change
- `test_signal_no_notify_same_value` - No notification if value unchanged
- `test_signal_map_creates_computed` - Functor map works
- `test_unsubscribe` - Cleanup works

#### test_entropy.py
- `test_entropy_to_distortion_pure` - Same inputs → same output
- `test_entropy_to_distortion_bounds` - Handles edge cases (0, 1, negative)
- `test_high_entropy_more_distortion` - Non-linear scaling
- `test_time_affects_distortion` - Time parameter works

#### test_joy.py
- `test_generate_personality_deterministic` - Same seed → same personality
- `test_seeded_random_sequence` - Reproducible sequence

#### test_glyph.py
- `test_glyph_project_cli` - Returns string
- `test_glyph_project_json` - Returns dict
- `test_glyph_with_time_immutable` - Returns new widget
- `test_glyph_phase_resolves_char` - Phase → glyph character

### Success Criteria for Wave 1

1. `Signal[T]` works with subscribe/notify pattern
2. `entropy_to_distortion()` is pure (deterministic tests pass)
3. `GlyphWidget` projects to all 4 targets
4. Time flows from parent (not managed internally)
5. All tests pass, mypy clean

### Next Waves (Don't Implement Yet)

- Wave 2: Bar, Sparkline, DensityField primitives
- Wave 3: AgentCard, YieldCard composed widgets
- Wave 4: Screen widgets + shell integration

## Commands

```bash
# Run tests
cd impl/claude && uv run pytest agents/i/reactive/_tests/ -v

# Type check
cd impl/claude && uv run mypy agents/i/reactive/

# Quick manual test
cd impl/claude && uv run python -c "
from agents.i.reactive.primitives.glyph import GlyphWidget, GlyphState
from agents.i.reactive.widget import RenderTarget

g = GlyphWidget(GlyphState(char='◉', phase='active', entropy=0.5, seed=42))
print('CLI:', g.project(RenderTarget.CLI))
print('JSON:', g.project(RenderTarget.JSON))
"
```

## Constraints

- No `random.random()` in any render path - all deterministic
- Time (`t`) passed from parent, never managed internally
- All state classes are frozen dataclasses (immutable)
- Projectors are pure functions
- Follow patterns from `plans/meta/v0-ui-learnings-synthesis.md`

## Epilogue Template

When complete, write epilogue to:
`impl/claude/plans/_epilogues/2025-12-14-reactive-substrate-wave1.md`

Include:
- Files created
- Test counts
- Key implementation decisions
- How this connects to AUP and marimo integration
- Learnings from v0-ui study applied

---

*"The glyph is the atom. The widget is the molecule. The screen is the organism. All breathe with the same entropy."*
