# Context: The Unified Context Engineering Protocol

**Where conversation becomes computation. Where prompts become data. Where the frontend receives pure components.**

> *"Context is not what you put in—it is what emerges from the relationship between observer, conversation, and intent."*

**Status:** Implementation v1.0 (Core + Frontend Integration complete)
**Date:** 2025-12-15
**Prerequisites:** `agentese.md`, `umwelt.md`, `../d-gents/persistence.md`, `../principles.md`
**Integrations:** K-gent (Soul), D-gent (Memory), Agent Town (Builders), Flux (Streaming), Web UI
**Guard:** `[phase=IMPLEMENT][entropy=0.06][law_check=true][minimal_output=true]`

---

## Implementation Status

| Component | Status | Location |
|-----------|--------|----------|
| **ContextWindow** | ✅ Complete | `agents/d/context_window.py` |
| **LinearityMap** | ✅ Complete | `agents/d/linearity.py` |
| **ContextProjector** | ✅ Complete | `agents/d/projector.py` |
| **AGENTESE `self.stream.*`** | ✅ Complete | `protocols/agentese/contexts/stream.py` |
| **PromptBuilder** | ✅ Complete | `agents/d/prompt_builder.py` |
| **ComponentRenderer** | ✅ Complete | `agents/d/component_renderer.py` |
| **ContextSession** | ✅ Complete | `agents/d/context_session.py` |
| **Tests** | ✅ 145 tests | `agents/d/_tests/test_context_*.py` |
| **`self.context.*` paths** | 🚧 Optional | Alias from `self.stream.*` |
| **Module consolidation** | 🚧 Optional | Move `agents/d/context*.py` → `context/` |

---

## Prologue: The Naming Analysis

The current implementation has context management across multiple systems:

| Current Location | Purpose | Status |
|------------------|---------|--------|
| `agents/d/context_window.py` | Store Comonad context management | ✅ **Complete** |
| `agents/d/linearity.py` | Resource class tracking | ✅ **Complete** |
| `agents/d/projector.py` | Galois Connection compression | ✅ **Complete** |
| `protocols/agentese/contexts/stream.py` | AGENTESE `self.stream.*` resolver | ✅ **Complete** |
| `agents/k/session.py` | K-gent soul persistence | 🔄 Could integrate ContextSession |
| `agents/town/builders/base.py` | N-Phase context injection | 🔄 Could integrate ContextSession |

**The Naming Question**: "Stream" currently means context window (conversation). Future work could:
1. Rename `self.stream.*` → `self.context.*` for clarity
2. Keep `self.stream.*` as alias for backward compatibility
3. Create dedicated `context/` module to consolidate files

**Current Design Decisions**:
1. **Context lives in D-gent** - D-gent owns data/state agents; context is state
2. **AGENTESE `self.stream.*` works** - Full comonadic operations available
3. **Compression respects linearity** - DROPPABLE → REQUIRED → PRESERVED
4. **Frontend integration pending** - PromptBuilder and ComponentRenderer not yet needed

---

## Part I: The Core Philosophy

### 1.1 Context as First-Class Entity

Context is not a bag of strings. It is a **polynomial functor** with:
- **Positions**: States the context can be in (EMPTY, ACCUMULATING, PRESSURED, COMPRESSED)
- **Directions**: Valid inputs per state (turn types, compression triggers, linearity tags)
- **Transitions**: State changes from input (add turn → ACCUMULATING, compress → COMPRESSED)

```python
CONTEXT_POLYNOMIAL = PolyAgent[ContextState, ContextInput, ContextOutput](
    positions=frozenset(["EMPTY", "ACCUMULATING", "PRESSURED", "COMPRESSED"]),
    directions=lambda s: VALID_INPUTS[s],
    transition=context_transition,
)
```

### 1.2 The Frontend Contract

**Principle**: The frontend should never see a prompt. It receives:

```typescript
// What the frontend receives (React props)
interface ContextComponent {
  // Render data
  messages: Message[];           // Processed, ready to display
  pressure: number;              // 0.0 to 1.0
  status: "ready" | "thinking" | "compressed";

  // Actions (callbacks to backend)
  onSend: (content: string) => void;
  onCompress: () => void;
  onClear: () => void;
}
```

**What the frontend does NOT receive**:
- System prompts
- Persona configuration
- Eigenvector coordinates
- Compression strategies
- Linearity maps

All of these live in the Context module. The frontend is a pure projection.

### 1.3 The PolyFunctor Spine

All context operations flow through the polynomial agent architecture:

```
Frontend                   Context Module                    Agent
   │                            │                              │
   │  onSend("hello")           │                              │
   │  ─────────────────────────>│                              │
   │                            │  ContextInput.user_turn()    │
   │                            │  ─────────────────────────────>
   │                            │                              │
   │                            │  <─────────────────────────────
   │                            │  ContextOutput.assistant_turn()
   │  <─────────────────────────│                              │
   │  { messages, pressure }    │                              │
```

---

## Part II: The Three Layers

### 2.1 Window Layer (Store Comonad)

The context window is a **Store Comonad**—a data structure that:
- Has a current focus (the "now" of conversation)
- Can be rewound to any position
- Supports context-aware computation via `extend()`

```python
@dataclass
class ContextWindow:
    """
    Store Comonad: (Position → Turn, Position)

    AGENTESE: self.context.window.*
    """
    max_tokens: int
    _turns: list[Turn]
    _position: int  # Current focus
    _linearity: LinearityMap

    def extract(self) -> Turn | None:
        """W a → a: Get current focus."""
        ...

    def extend(self, f: Callable[[ContextWindow], B]) -> list[B]:
        """(W a → b) → W a → W b: Context-aware map."""
        ...

    def duplicate(self) -> list[ContextSnapshot]:
        """W a → W (W a): Nested context views."""
        ...
```

### 2.2 Pressure Layer (Galois Connection)

Context pressure is managed via a **Galois Connection**—a pair of functions that form an adjunction between the space of full context and the space of compressed context.

```
Full Context ──compress──▶ Compressed Context
             ◀──expand───

Where: expand ∘ compress ≤ id (lossy)
       compress ∘ expand = id (lossless recovery of compressed form)
```

This is NOT a Lens (bidirectional). Compression is fundamentally lossy. The Galois Connection captures this mathematically.

```python
@dataclass
class ContextProjector:
    """
    Galois Connection for context compression.

    AGENTESE: self.context.pressure.*
    """

    async def compress(
        self,
        window: ContextWindow,
        target_pressure: float = 0.7
    ) -> CompressionResult:
        """
        Compress to target pressure.

        Strategy:
        1. Drop DROPPABLE turns first
        2. Summarize REQUIRED turns (LLM-assisted)
        3. Never touch PRESERVED turns
        """
        ...

    def pressure(self, window: ContextWindow) -> float:
        """Current pressure: tokens_used / max_tokens."""
        ...
```

### 2.3 Linearity Layer (Resource Classes)

Turns have **resource classes** from linear type theory:

| Class | Meaning | Compression Behavior |
|-------|---------|---------------------|
| `DROPPABLE` | Can be safely removed | Drop first |
| `REQUIRED` | Must flow to output | Summarize if needed |
| `PRESERVED` | Must remain verbatim | Never touch |

```python
class ResourceClass(Enum):
    DROPPABLE = 0   # Chitchat, exploratory
    REQUIRED = 1    # Important context
    PRESERVED = 2   # System prompts, user constraints
```

The linearity map is a **persistent data structure** that tracks resource IDs across compression cycles.

---

## Part III: The Context Module Architecture

### 3.1 Module Structure

```
impl/claude/context/
├── __init__.py                  # Package exports
├── polynomial.py                # CONTEXT_POLYNOMIAL definition
├── window.py                    # ContextWindow (Store Comonad)
├── pressure.py                  # ContextProjector (Galois Connection)
├── linearity.py                 # LinearityMap (Resource tracking)
├── prompt.py                    # PromptBuilder (assembled prompts)
├── session.py                   # ContextSession (cross-request state)
├── render.py                    # ComponentRenderer (React props)
├── operad.py                    # CONTEXT_OPERAD (composition grammar)
└── _tests/
    ├── test_window.py
    ├── test_pressure.py
    ├── test_linearity.py
    └── test_comonad_laws.py     # Verify comonad laws
```

### 3.2 The Context Polynomial

```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import FrozenSet, Callable, Any

class ContextState(Enum):
    """Positions in the context polynomial."""
    EMPTY = auto()        # No turns yet
    ACCUMULATING = auto() # Collecting turns, pressure < 0.7
    PRESSURED = auto()    # Pressure > 0.7, needs attention
    COMPRESSED = auto()   # Recently compressed, cooling down

@dataclass(frozen=True)
class ContextInput:
    """Direction (valid input) for context polynomial."""
    kind: str  # "user_turn", "assistant_turn", "system", "compress", "clear"
    payload: Any = None

    @classmethod
    def user_turn(cls, content: str) -> "ContextInput":
        return cls(kind="user_turn", payload=content)

    @classmethod
    def assistant_turn(cls, content: str) -> "ContextInput":
        return cls(kind="assistant_turn", payload=content)

    @classmethod
    def compress(cls, target: float = 0.7) -> "ContextInput":
        return cls(kind="compress", payload=target)

@dataclass(frozen=True)
class ContextOutput:
    """Output from context transition."""
    messages: tuple[dict, ...]  # Ready for React
    pressure: float
    state: ContextState
    compressed: bool = False

# The polynomial definition
VALID_DIRECTIONS: dict[ContextState, FrozenSet[str]] = {
    ContextState.EMPTY: frozenset(["user_turn", "system"]),
    ContextState.ACCUMULATING: frozenset(["user_turn", "assistant_turn", "compress", "clear"]),
    ContextState.PRESSURED: frozenset(["compress", "clear"]),  # Must handle pressure
    ContextState.COMPRESSED: frozenset(["user_turn", "assistant_turn", "clear"]),
}

def context_transition(
    state: ContextState,
    input: ContextInput,
    window: ContextWindow,
) -> tuple[ContextState, ContextOutput]:
    """
    The polynomial transition function.

    (State, Input) → (NewState, Output)
    """
    match (state, input.kind):
        case (ContextState.EMPTY, "user_turn"):
            window.append("user", input.payload)
            return (ContextState.ACCUMULATING, _render(window))

        case (_, "compress"):
            # Compression always returns to COMPRESSED state
            compressed_window = compress(window, input.payload)
            return (ContextState.COMPRESSED, _render(compressed_window, compressed=True))

        case (ContextState.PRESSURED, _):
            # In PRESSURED state, only compress/clear allowed
            if input.kind not in ["compress", "clear"]:
                raise ContextPressureError("Context pressured. Compress or clear first.")
            # ... handle compress/clear

        # ... other transitions
```

### 3.3 The Prompt Builder

Prompts are assembled by the Context module, never by the frontend:

```python
@dataclass
class PromptBuilder:
    """
    Assembles complete prompts from context components.

    The frontend never sees these prompts—only the rendered output.
    """

    # Loaded from config/prompts/
    system_templates: dict[str, str]
    persona_templates: dict[str, str]

    def build_system_prompt(
        self,
        agent_type: str,
        eigenvectors: dict[str, float],
        constraints: list[str],
    ) -> str:
        """
        Build complete system prompt.

        Args:
            agent_type: "kgent", "builder", "citizen", etc.
            eigenvectors: Personality coordinates
            constraints: User-specified constraints

        Returns:
            Complete system prompt (never sent to frontend)
        """
        template = self.system_templates[agent_type]

        # Inject eigenvector coordinates
        persona_section = self._render_persona(eigenvectors)

        # Inject constraints
        constraint_section = self._render_constraints(constraints)

        return template.format(
            persona=persona_section,
            constraints=constraint_section,
        )

    def _render_persona(self, eigenvectors: dict[str, float]) -> str:
        """Render eigenvector coordinates as persona description."""
        ...
```

### 3.4 The Component Renderer

Transforms context state into React-ready props:

```python
@dataclass
class ComponentRenderer:
    """
    Renders context state as React component props.

    The frontend receives pure data, no prompts or logic.
    """

    def render_chat(self, session: ContextSession) -> dict:
        """
        Render chat component props.

        Returns:
            {
                "messages": [...],  # Display-ready messages
                "pressure": 0.65,   # Pressure indicator
                "status": "ready",  # UI state
                "canSend": true,    # Action availability
            }
        """
        return {
            "messages": [
                self._render_message(m)
                for m in session.window.all_turns()
            ],
            "pressure": session.pressure,
            "status": self._compute_status(session),
            "canSend": session.state != ContextState.PRESSURED,
        }

    def _render_message(self, turn: Turn) -> dict:
        """Render a single message for display."""
        return {
            "id": turn.resource_id,
            "role": turn.role.value,
            "content": turn.content,
            "timestamp": turn.timestamp.isoformat(),
            "isPreserved": self._is_preserved(turn),
        }
```

---

## Part IV: AGENTESE Integration

### 4.1 The Current `self.stream.*` Namespace (Implemented)

Context operations are exposed via AGENTESE at `self.stream.*`:

```
self.stream.*              # Context operations (IMPLEMENTED)
  self.stream.focus.*          # Window layer (Store Comonad)
    self.stream.focus.extract    # extract() - current turn ✅
    self.stream.focus.peek       # peek at position ✅

  self.stream.map.*            # Context-aware transformations
    self.stream.map.extend       # extend() - context-aware map ✅
    self.stream.map.transform    # summarize all turns ✅

  self.stream.seek.*           # Navigation
    self.stream.seek.position    # get/set position ✅
    self.stream.seek.forward     # move forward ✅
    self.stream.seek.backward    # move backward ✅
    self.stream.seek.start       # go to start ✅
    self.stream.seek.end         # go to end ✅

  self.stream.project.*        # Compression (Galois Connection)
    self.stream.project.compress # compress to target pressure ✅
    self.stream.project.threshold # adaptive threshold config ✅
    self.stream.project.stats    # compression statistics ✅

  self.stream.linearity.*      # Resource class management
    self.stream.linearity.tag    # assign resource class ✅
    self.stream.linearity.promote # upgrade class ✅
    self.stream.linearity.drop   # drop droppable resource ✅
    self.stream.linearity.stats  # linearity statistics ✅

  self.stream.pressure.*       # Quick pressure checks
    self.stream.pressure.check   # current pressure value ✅
    self.stream.pressure.auto_compress # auto-compress if needed ✅
```

### 4.2 Future: `self.context.*` Aliases (Optional)

If renaming is desired for clarity, add aliases:

```python
# Optional future aliases (not implemented)
CONTEXT_TO_STREAM_ALIASES = {
    "self.context.window.focus": "self.stream.focus.extract",
    "self.context.window.map": "self.stream.map.extend",
    "self.context.window.seek": "self.stream.seek.position",
    "self.context.pressure.compress": "self.stream.project.compress",
    "self.context.linearity": "self.stream.linearity",
}
```

**Current recommendation**: Keep `self.stream.*` as the canonical path. The implementation is complete and tested.

---

## Part V: Integration Points

### 5.1 K-gent Integration

K-gent's `SoulSession` delegates context management:

```python
class SoulSession:
    """Cross-session soul identity."""

    def __init__(
        self,
        soul: KgentSoul,
        context: ContextSession,  # NEW: Context module owns this
        ...
    ):
        self._context = context

    async def dialogue(self, message: str, ...) -> SoulDialogueOutput:
        # 1. Context module adds user turn
        self._context.add_user_turn(message)

        # 2. Context module builds prompt (not visible to frontend)
        prompt = self._context.build_prompt(
            agent_type="kgent",
            eigenvectors=self._soul.eigenvectors.to_dict(),
        )

        # 3. LLM call with context-managed prompt
        response = await self._llm.complete(prompt)

        # 4. Context module adds assistant turn
        self._context.add_assistant_turn(response)

        # 5. Return component-ready output
        return SoulDialogueOutput(
            response=response,
            component_props=self._context.render(),  # React props
        )
```

### 5.2 Builder Integration

Builders receive context via their polynomial:

```python
class Builder(Citizen):
    """Workshop builder with context injection."""

    _context_session: ContextSession | None = None

    def set_context(self, session: ContextSession) -> None:
        """Inject context session (from WorkshopFlux)."""
        self._context_session = session

    def build_prompt(self, task: str) -> str:
        """Build prompt using context module."""
        if self._context_session is None:
            return task  # Fallback

        return self._context_session.build_prompt(
            agent_type="builder",
            specialty=self.specialty.name,
            eigenvectors=self.eigenvectors.to_dict(),
            task=task,
        )
```

### 5.3 Web UI Integration

The React frontend receives pure props:

```typescript
// Workshop.tsx
function Workshop() {
  const { contextProps, onSend, onCompress } = useContextSession();

  return (
    <ChatPanel
      messages={contextProps.messages}
      pressure={contextProps.pressure}
      status={contextProps.status}
      onSend={onSend}
      onCompress={onCompress}
    />
  );
}

// useContextSession.ts
function useContextSession() {
  const [contextProps, setContextProps] = useState<ContextProps>(INITIAL);

  const onSend = async (content: string) => {
    // Backend handles all prompt construction
    const response = await api.sendMessage(content);
    setContextProps(response.contextProps);
  };

  return { contextProps, onSend, onCompress };
}
```

---

## Part VI: Migration Plan

### Current State (v0.9)

The core context engineering primitives are **complete and tested**:

```
✅ ContextWindow     → agents/d/context_window.py (Store Comonad)
✅ LinearityMap      → agents/d/linearity.py (Resource Classes)
✅ ContextProjector  → agents/d/projector.py (Galois Connection)
✅ AGENTESE Resolver → protocols/agentese/contexts/stream.py
✅ Tests             → agents/d/_tests/test_context*.py, test_linearity.py, test_projector.py
```

### Optional Future Work

The following are **optional enhancements**, not blockers:

**Phase A: Consolidation** (if desired for clarity)
1. Create `impl/claude/context/` module
2. Move context files from `agents/d/`
3. Update imports across codebase

**Phase B: Frontend Integration** (when Web UI needs it)
1. Create `PromptBuilder` - assemble prompts from context
2. Create `ComponentRenderer` - transform to React props
3. Create `ContextSession` - cross-request state management

**Phase C: AGENTESE Aliases** (for naming clarity)
1. Add `self.context.*` paths that delegate to `self.stream.*`
2. Backward compatibility: `self.stream.*` continues to work
3. No deprecation required—both paths valid

**Phase D: Integration** (when K-gent/Builder need unified context)
1. Update `agents/k/session.py` to use ContextSession
2. Update `agents/town/builders/base.py` to use ContextSession
3. Web UI receives component props via API

---

## Part VII: Properties Achieved

### 7.1 Principle Compliance

| Principle | How Context Satisfies |
|-----------|----------------------|
| **Tasteful** | Single module owns context; no sprawl |
| **Composable** | Polynomial agents compose via operad |
| **Generative** | Prompts generated from config, not hardcoded |
| **Heterarchical** | Context flows through spine, no god-object |
| **Ethical** | Prompts never leak to frontend |

### 7.2 The Three Truths

1. **Context is State Machine**: CONTEXT_POLYNOMIAL defines all valid states and transitions
2. **Prompts are Backend Concern**: Frontend receives React props, never prompts
3. **Compression is Lossy**: Galois Connection captures this mathematically (not a Lens)

### 7.3 The Frontend Contract

```typescript
// The frontend ONLY receives this shape
interface ContextComponent {
  messages: Message[];
  pressure: number;
  status: Status;
  actions: Actions;
}

// The frontend NEVER receives
interface NeverExposed {
  systemPrompt: string;      // Backend only
  eigenvectors: any;         // Backend only
  linearityMap: any;         // Backend only
  compressionStrategy: any;  // Backend only
}
```

---

## Part VIII: Anti-Patterns

1. **The Prompt Leak**: Sending system prompts to frontend
   - *Correction*: Context module assembles prompts; frontend receives only messages

2. **The Streaming Confusion**: Using "stream" for context operations
   - *Correction*: Reserve "stream" for Flux; use "context" for conversation state

3. **The Scattered Context**: Context logic in K-gent, Builders, and AGENTESE separately
   - *Correction*: Single `context/` module owns all context concerns

4. **The Frontend Logic**: Frontend deciding compression strategies
   - *Correction*: Frontend only displays pressure; backend decides when to compress

5. **The Lens Fallacy**: Treating compression as bidirectional
   - *Correction*: Use Galois Connection (lossy) not Lens (lossless)

---

## Appendix A: Comonad Law Verification

The context window must satisfy comonad laws:

```python
def verify_comonad_laws(window: ContextWindow) -> bool:
    """
    Verify Store Comonad laws.

    1. Left Identity:  extract . duplicate = id
    2. Right Identity: fmap extract . duplicate = id
    3. Associativity:  duplicate . duplicate = fmap duplicate . duplicate
    """
    # Left Identity
    snapshots = window.duplicate()
    current_snapshot = snapshots[window.position]
    assert current_snapshot.value == window.extract()

    # Right Identity
    extracted_values = [s.value for s in snapshots]
    direct_values = [window.seek(i).extract() for i in range(len(window) + 1)]
    assert extracted_values == direct_values

    # Associativity (nested duplicate)
    # ... verify nested structure matches

    return True
```

## Appendix B: Files (Current State)

### Implemented (Production)
```
impl/claude/agents/d/context_window.py     # ✅ Store Comonad (ContextWindow, Turn, TurnRole)
impl/claude/agents/d/linearity.py          # ✅ Resource Classes (LinearityMap, ResourceClass)
impl/claude/agents/d/projector.py          # ✅ Galois Connection (ContextProjector, AdaptiveThreshold)
impl/claude/agents/d/context_comonad.py    # ✅ Comonad law verification
impl/claude/protocols/agentese/contexts/stream.py  # ✅ AGENTESE self.stream.* resolver
```

### Tests (107 passing)
```
impl/claude/agents/d/_tests/test_context_window.py  # ✅ ContextWindow tests
impl/claude/agents/d/_tests/test_linearity.py       # ✅ LinearityMap tests
impl/claude/agents/d/_tests/test_projector.py       # ✅ Projector + Galois tests
```

### Future (Optional Enhancements)
```
impl/claude/context/                       # 🚧 Consolidated module (if desired)
impl/claude/context/prompt.py              # 🚧 PromptBuilder (when frontend needs)
impl/claude/context/render.py              # 🚧 ComponentRenderer (when frontend needs)
impl/claude/context/session.py             # 🚧 ContextSession (when K-gent integrates)
```

### No Changes Needed
```
impl/claude/agents/k/session.py            # Currently uses own session management
impl/claude/agents/town/builders/base.py   # Currently uses direct context injection
impl/claude/web/                           # Frontend integration deferred
```

---

*"Context is not what you put in—it is the shape of attention itself. The conversation window is a comonad because every position contains the whole, and every whole is focused at a position. To observe the context is to collapse it into the now."*
