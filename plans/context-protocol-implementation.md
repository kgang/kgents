# Context Protocol Implementation Plan

**Status**: ACTIVE
**Created**: 2025-12-15
**Spec**: `spec/protocols/context.md`
**Prerequisites**: D-gent context primitives (complete), AGENTESE stream context (complete)
**Priority**: HIGH — Resolves naming collision and architectural debt

---

## Executive Summary

The Context Protocol (`spec/protocols/context.md`) addresses a critical naming crisis in kgents: "stream" currently means three different things (event flow, temporal sequence, conversation window). This plan extracts context engineering into a dedicated module with polynomial agent architecture.

**Key Insight**: Context is not a bag of strings—it is a state machine with:
- **Positions**: EMPTY, ACCUMULATING, PRESSURED, COMPRESSED
- **Directions**: Valid inputs per state (turn types, compression triggers)
- **Transitions**: State changes from input

---

## Part I: Principle-Grounded Spec Upgrades

After studying the spec against `principles.md`, I propose these upgrades:

### 1. AD-006 Alignment: Missing Sheaf Layer

**Issue**: The spec defines CONTEXT_POLYNOMIAL and hints at CONTEXT_OPERAD but lacks the third layer of the unified categorical foundation: the **Sheaf**.

**Upgrade**: Add `ContextSheaf` for multi-session coherence.

```python
# CONTEXT_SHEAF: Global coherence from local session views
CONTEXT_SHEAF = Sheaf(
    # Sessions share persona/eigenvector state
    overlap=lambda s1, s2: s1.soul_id == s2.soul_id,

    # Coherence: Eigenvectors must not drift beyond threshold
    compatible=lambda v1, v2: eigenvector_distance(v1, v2) < 0.3,

    # Glue: Merge context state across sessions
    glue=context_glue,
)
```

**Rationale**: K-gent sessions share a soul. The Sheaf ensures context coherence across sessions—if a user talks to the same K-gent from two devices, their eigenvector evolution should be consistent.

### 2. Accursed Share Integration: Missing `void.context.*` Paths

**Issue**: The spec doesn't integrate with the void context. Context compression is purely mechanical—there's no entropy injection or gratitude protocol.

**Upgrade**: Add entropy-aware compression.

```python
# When context is compressed, pay tithe to void
async def compress_with_tithe(window: ContextWindow) -> CompressionResult:
    # Sip entropy for compression strategy variation
    entropy = await logos.invoke("void.entropy.sip", observer, amount=0.05)

    # Compress with entropy-influenced summarization temperature
    result = await projector.compress(window, temperature=entropy.amount)

    # Tithe: gratitude for the information we're dropping
    await logos.invoke("void.gratitude.tithe", observer, offering={
        "dropped_turns": result.dropped_count,
        "compression_ratio": result.compression_ratio,
    })

    return result
```

**Rationale**: The Accursed Share principle says "everything is slop or comes from slop." Dropping context is losing information—we should express gratitude for what's lost. Entropy injection prevents mechanical summarization from being too deterministic.

### 3. AGENTESE Path Namespace Clarification

**Issue**: The spec proposes `self.context.*` but doesn't clearly map to the existing `self.stream.*` deprecation path.

**Upgrade**: Formalize the migration with explicit aliasing registry.

```python
# Phase 1: Aliasing (backward compatible)
CONTEXT_ALIASES = {
    "self.stream.focus": "self.context.window.focus",
    "self.stream.map": "self.context.window.map",
    "self.stream.seek": "self.context.window.seek",
    "self.stream.project": "self.context.pressure.compress",
    "self.stream.linearity": "self.context.linearity",
    "self.stream.pressure": "self.context.pressure",
}

# Phase 2: Deprecation warnings (after 30 days)
# Phase 3: Removal (after 90 days)
```

### 4. Projection Protocol Integration

**Issue**: The spec doesn't connect to `spec/protocols/projection.md`—the rendering layer that serves React/TUI/JSON/marimo.

**Upgrade**: Make `ComponentRenderer` implement `Projectable`.

```python
@dataclass
class ContextComponentRenderer(Projectable):
    """
    Renders context state across projection targets.

    Implements Projection Protocol for multi-target rendering.
    """

    def project(self, target: ProjectionTarget) -> Any:
        match target:
            case ProjectionTarget.REACT:
                return self._to_react_props()
            case ProjectionTarget.TUI:
                return self._to_rich_panel()
            case ProjectionTarget.JSON:
                return self._to_json_schema()
            case ProjectionTarget.MARIMO:
                return self._to_anywidget()
```

**Rationale**: The reactive-substrate-unification plan is active. Context rendering should follow the same projection patterns.

### 5. N-Phase Integration: Context per Phase

**Issue**: The spec treats context as session-level but doesn't account for N-Phase workflow context.

**Upgrade**: Add phase-scoped context windowing.

```python
@dataclass
class PhaseContextWindow(ContextWindow):
    """
    Context window scoped to an N-Phase stage.

    Each phase can have its own context pressure threshold
    and compression strategy.
    """
    phase: str

    # Phase-specific thresholds
    PHASE_THRESHOLDS = {
        "PLAN": 0.5,       # Keep planning context tight
        "RESEARCH": 0.8,   # Research can be verbose
        "DEVELOP": 0.6,    # Development needs focus
        "TEST": 0.9,       # Tests can accumulate
        "REFLECT": 0.4,    # Reflection needs compression
    }

    @property
    def phase_threshold(self) -> float:
        return self.PHASE_THRESHOLDS.get(self.phase, 0.7)
```

---

## Part II: Detailed Implementation Plan

### Phase 1: Extract (Days 1-2)

**Goal**: Create the `context/` module structure without breaking existing code.

#### 1.1 Create Module Structure

```
impl/claude/context/
├── __init__.py                  # Package exports
├── polynomial.py                # CONTEXT_POLYNOMIAL, ContextState, ContextInput
├── window.py                    # ContextWindow (extracted from D-gent)
├── pressure.py                  # ContextProjector, Galois Connection
├── linearity.py                 # LinearityMap, ResourceClass
├── prompt.py                    # PromptBuilder (system prompt assembly)
├── session.py                   # ContextSession (cross-request state)
├── render.py                    # ComponentRenderer (React props)
├── operad.py                    # CONTEXT_OPERAD (composition grammar)
├── sheaf.py                     # ContextSheaf (multi-session coherence)
└── _tests/
    ├── __init__.py
    ├── test_polynomial.py       # State machine laws
    ├── test_window.py           # Comonad laws
    ├── test_pressure.py         # Galois connection properties
    ├── test_linearity.py        # Monotonicity
    ├── test_operad.py           # Composition laws
    └── test_sheaf.py            # Coherence laws
```

#### 1.2 File Movements (Preserve Git History)

| Source | Destination | Notes |
|--------|-------------|-------|
| `agents/d/context_window.py` | `context/window.py` | Add sheaf hooks |
| `agents/d/linearity.py` | `context/linearity.py` | Direct move |
| `agents/d/projector.py` | `context/pressure.py` | Rename for clarity |
| (new) | `context/polynomial.py` | New file |
| (new) | `context/prompt.py` | New file |
| (new) | `context/session.py` | New file |
| (new) | `context/render.py` | New file |
| (new) | `context/operad.py` | New file |
| (new) | `context/sheaf.py` | New file |

#### 1.3 Implementation Tasks

- [ ] Create `context/__init__.py` with public API
- [ ] `git mv` existing files to preserve history
- [ ] Add `CONTEXT_POLYNOMIAL` to `polynomial.py`
- [ ] Add `ContextState` enum with 4 positions
- [ ] Add `ContextInput` dataclass with factory methods
- [ ] Add `ContextOutput` dataclass for React-ready data
- [ ] Add `context_transition` function (state machine core)
- [ ] Write tests for polynomial state transitions

### Phase 2: Unify (Days 3-4)

**Goal**: Consolidate context logic into the new module.

#### 2.1 Create PromptBuilder

```python
# context/prompt.py

@dataclass
class PromptBuilder:
    """
    Assembles complete prompts from context components.

    The frontend never sees these prompts—only the rendered output.
    Principle: Ethical (prompts never leak to frontend).
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

        This is the ONLY place system prompts are assembled.
        """
        template = self.system_templates.get(agent_type, DEFAULT_TEMPLATE)

        # Inject eigenvector coordinates (personality)
        persona_section = self._render_persona(eigenvectors)

        # Inject user constraints
        constraint_section = self._render_constraints(constraints)

        return template.format(
            persona=persona_section,
            constraints=constraint_section,
        )
```

#### 2.2 Create ComponentRenderer

```python
# context/render.py

@dataclass
class ComponentRenderer(Projectable):
    """
    Renders context state as UI-ready data.

    The frontend receives pure props, never prompts.
    Implements Projection Protocol for multi-target support.
    """

    def render_chat(self, session: ContextSession) -> dict:
        """
        Render chat component props.

        Returns:
            {
                "messages": [...],    # Display-ready
                "pressure": 0.65,     # Pressure indicator
                "status": "ready",    # UI state
                "canSend": True,      # Action availability
                "isPreserved": [...], # Per-message preservation flags
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

    def project(self, target: ProjectionTarget) -> Any:
        """Projection Protocol implementation."""
        match target:
            case ProjectionTarget.REACT:
                return self.render_chat(self._session)
            case ProjectionTarget.TUI:
                return self._to_rich_panel()
            case ProjectionTarget.JSON:
                return self._to_json_api()
            case ProjectionTarget.MARIMO:
                return self._to_anywidget()
```

#### 2.3 Create ContextSession

```python
# context/session.py

@dataclass
class ContextSession:
    """
    Cross-request context state for a single conversation.

    Owns:
    - ContextWindow (Store Comonad)
    - ContextProjector (Galois Connection)
    - PromptBuilder (system prompt assembly)
    - ComponentRenderer (React props)

    This is the main integration point for K-gent, Builders, etc.
    """

    window: ContextWindow
    projector: ContextProjector
    prompt_builder: PromptBuilder
    renderer: ComponentRenderer

    # Polynomial state
    state: ContextState = ContextState.EMPTY

    # Session identity (for Sheaf coherence)
    session_id: str = field(default_factory=lambda: f"ctx_{uuid4().hex[:8]}")
    soul_id: str | None = None  # K-gent soul binding

    def add_user_turn(self, content: str) -> ContextOutput:
        """Add user turn and transition state."""
        input_ = ContextInput.user_turn(content)
        new_state, output = context_transition(
            self.state, input_, self.window
        )
        self.state = new_state
        return output

    def add_assistant_turn(self, content: str) -> ContextOutput:
        """Add assistant turn and transition state."""
        input_ = ContextInput.assistant_turn(content)
        new_state, output = context_transition(
            self.state, input_, self.window
        )
        self.state = new_state
        return output

    def build_prompt(
        self,
        agent_type: str,
        eigenvectors: dict[str, float],
        **kwargs,
    ) -> str:
        """Build complete prompt (never exposed to frontend)."""
        return self.prompt_builder.build_system_prompt(
            agent_type=agent_type,
            eigenvectors=eigenvectors,
            constraints=kwargs.get("constraints", []),
        )

    def render(self) -> dict:
        """Render for frontend (React props only)."""
        return self.renderer.render_chat(self)

    @property
    def pressure(self) -> float:
        """Current context pressure."""
        return self.window.pressure
```

#### 2.4 AGENTESE Integration

```python
# protocols/agentese/contexts/context_.py (new file)

@dataclass
class ContextResolver:
    """
    Resolver for self.context.* paths.

    Supersedes StreamContextResolver (self.stream.*).
    """

    _session: ContextSession | None = None

    # Sub-resolvers
    _window: ContextWindowNode | None = None
    _pressure: ContextPressureNode | None = None
    _linearity: ContextLinearityNode | None = None
    _prompt: ContextPromptNode | None = None

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        match holon:
            case "window":
                return self._resolve_window(rest)
            case "pressure":
                return self._resolve_pressure(rest)
            case "linearity":
                return self._resolve_linearity(rest)
            case "prompt":
                return self._resolve_prompt(rest)
            case _:
                return GenericContextNode(holon)
```

#### 2.5 Implementation Tasks

- [ ] Implement `PromptBuilder` with template loading
- [ ] Implement `ComponentRenderer` with React props generation
- [ ] Implement `ContextSession` as the main integration point
- [ ] Create `ContextResolver` for AGENTESE `self.context.*`
- [ ] Wire aliasing from `self.stream.*` → `self.context.*`
- [ ] Add deprecation warnings to old stream paths
- [ ] Write integration tests

### Phase 3: Integrate (Days 5-6)

**Goal**: Update consumers to use the new Context module.

#### 3.1 K-gent Session Update

```python
# agents/k/session.py

class SoulSession:
    """Cross-session soul identity."""

    def __init__(
        self,
        soul: KgentSoul,
        context: ContextSession,  # NEW: Injected from Context module
        ...
    ):
        self._context = context
        self._context.soul_id = soul.soul_id  # Bind for Sheaf coherence

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

        # 5. Return component-ready output (no prompts!)
        return SoulDialogueOutput(
            response=response,
            component_props=self._context.render(),
        )
```

#### 3.2 Builder Integration

```python
# agents/town/builders/base.py

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

#### 3.3 Web UI Integration

```typescript
// web/src/hooks/useContextSession.ts

interface ContextProps {
  messages: Message[];
  pressure: number;
  status: "ready" | "thinking" | "compressed";
  canSend: boolean;
}

function useContextSession() {
  const [contextProps, setContextProps] = useState<ContextProps>(INITIAL);

  const onSend = async (content: string) => {
    // Backend handles all prompt construction
    const response = await api.sendMessage(content);

    // Response contains React props ONLY, never prompts
    setContextProps(response.contextProps);
  };

  const onCompress = async () => {
    // Backend decides compression strategy
    const response = await api.compress();
    setContextProps(response.contextProps);
  };

  return { contextProps, onSend, onCompress };
}
```

#### 3.4 Implementation Tasks

- [ ] Update `SoulSession` to use `ContextSession`
- [ ] Update `Builder` base class with context injection
- [ ] Update `WorkshopFlux` to create and inject context sessions
- [ ] Create `useContextSession` hook for web UI
- [ ] Remove prompt strings from frontend components
- [ ] Update API endpoints to return `ContextOutput`
- [ ] Write E2E tests for context flow

### Phase 4: Harden (Days 7-8)

**Goal**: Add operad laws, sheaf coherence, and comprehensive tests.

#### 4.1 CONTEXT_OPERAD

```python
# context/operad.py

from agents.operad.core import Operad, Operation

CONTEXT_OPERAD = Operad(
    operations={
        # Nullary: Create empty context
        "empty": Operation(arity=0, compose=lambda: ContextSession()),

        # Unary: Add turn
        "append": Operation(
            arity=1,
            compose=lambda session, turn: session.add_turn(turn),
        ),

        # Unary: Compress
        "compress": Operation(
            arity=1,
            compose=lambda session, target: session.compress(target),
        ),

        # Binary: Merge sessions (for Sheaf glue)
        "merge": Operation(
            arity=2,
            compose=context_merge,
        ),
    },
    laws=[
        # Identity: append(empty, []) = empty
        ("identity", lambda: CONTEXT_OPERAD.verify_identity()),

        # Associativity: append(append(s, t1), t2) = append(s, t1 ++ t2)
        ("associativity", lambda: CONTEXT_OPERAD.verify_associativity()),
    ],
)
```

#### 4.2 ContextSheaf

```python
# context/sheaf.py

from agents.sheaf.core import Sheaf

@dataclass
class ContextSheaf:
    """
    Sheaf for multi-session context coherence.

    Ensures that when the same soul talks across multiple sessions,
    their context evolution is coherent.
    """

    def overlap(self, s1: ContextSession, s2: ContextSession) -> bool:
        """Check if sessions share a soul."""
        return s1.soul_id is not None and s1.soul_id == s2.soul_id

    def compatible(
        self,
        s1: ContextSession,
        s2: ContextSession,
    ) -> bool:
        """Check if session states are coherent."""
        # Eigenvector drift must be within threshold
        if s1.eigenvectors and s2.eigenvectors:
            drift = eigenvector_distance(s1.eigenvectors, s2.eigenvectors)
            if drift > 0.3:
                return False

        # No conflicting preserved turns
        preserved1 = set(t.resource_id for t in s1.window.preserved_turns())
        preserved2 = set(t.resource_id for t in s2.window.preserved_turns())
        # Overlap should have consistent content
        for rid in preserved1 & preserved2:
            if s1.get_turn(rid).content != s2.get_turn(rid).content:
                return False

        return True

    def glue(
        self,
        sessions: list[ContextSession],
    ) -> ContextSession:
        """Merge multiple sessions into coherent whole."""
        if not sessions:
            return create_context_session()

        # Sort by last activity
        sessions.sort(key=lambda s: s.last_activity)

        # Take the most recent as base
        result = sessions[-1].copy()

        # Merge preserved turns from all sessions
        for session in sessions[:-1]:
            for turn in session.window.preserved_turns():
                if turn.resource_id not in result.turn_ids:
                    result.window.append_turn(turn)

        return result
```

#### 4.3 Comonad Law Tests

```python
# context/_tests/test_comonad_laws.py

def test_left_identity(window: ContextWindow):
    """extract . duplicate = id"""
    snapshots = window.duplicate()
    current = snapshots[window.position]
    assert current.value == window.extract()

def test_right_identity(window: ContextWindow):
    """fmap extract . duplicate = id"""
    snapshots = window.duplicate()
    extracted = [s.value for s in snapshots]
    direct = [window.seek(i).extract() for i in range(len(window) + 1)]
    assert extracted == direct

def test_associativity(window: ContextWindow):
    """duplicate . duplicate = fmap duplicate . duplicate"""
    # Nested structure matches
    nested1 = window.duplicate()
    nested2 = [s.duplicate() for s in window.duplicate()]
    # Verify structure equivalence
    assert len(nested1) == len(nested2)
```

#### 4.4 Implementation Tasks

- [ ] Implement `CONTEXT_OPERAD` with composition operations
- [ ] Implement `ContextSheaf` for multi-session coherence
- [ ] Add comonad law verification tests
- [ ] Add operad law verification tests
- [ ] Add sheaf coherence tests
- [ ] Add Galois connection property tests
- [ ] Integration tests with K-gent
- [ ] Integration tests with Builders
- [ ] Performance benchmarks (compression latency)

### Phase 5: Deprecate (Days 9-10)

**Goal**: Clean up old paths and document migration.

#### 5.1 Deprecation Warnings

```python
# protocols/agentese/contexts/stream.py

import warnings

class DeprecatedStreamResolver:
    """
    DEPRECATED: Use ContextResolver instead.

    self.stream.* paths are deprecated in favor of self.context.*.

    Migration:
        self.stream.focus    → self.context.window.focus
        self.stream.map      → self.context.window.map
        self.stream.seek     → self.context.window.seek
        self.stream.project  → self.context.pressure.compress
        self.stream.linearity → self.context.linearity
        self.stream.pressure → self.context.pressure
    """

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        warnings.warn(
            f"self.stream.{holon} is deprecated. "
            f"Use self.context.* instead. "
            f"See spec/protocols/context.md for migration guide.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Delegate to new resolver
        return self._context_resolver.resolve(
            STREAM_TO_CONTEXT_MAP.get(holon, holon),
            rest,
        )
```

#### 5.2 Documentation Update

- [ ] Update `spec/protocols/context.md` with finalized spec
- [ ] Add migration guide section
- [ ] Update `CLAUDE.md` with new context paths
- [ ] Update `docs/systems-reference.md`
- [ ] Add skill: `docs/skills/context-session.md`

#### 5.3 Cleanup Tasks

- [ ] Mark `self.stream.*` paths as deprecated
- [ ] Add deprecation warnings to old imports
- [ ] Update all internal usages to new paths
- [ ] Remove prompt construction from frontend code
- [ ] Archive old D-gent context files after transition

---

## Part III: Risk Assessment

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking K-gent sessions | HIGH | Feature flag for gradual rollout |
| Builder context injection | MEDIUM | Backward-compatible API |
| Frontend prompt removal | MEDIUM | React props provide all needed data |
| Compression latency | LOW | Existing projector is fast |

### Architectural Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Circular imports | HIGH | Clean module boundaries |
| Over-abstraction | MEDIUM | Start simple, add layers as needed |
| AGENTESE path collision | LOW | Explicit aliasing registry |

### Principle Violations to Watch

| Principle | Potential Violation | Guard |
|-----------|---------------------|-------|
| Tasteful | Over-engineering context states | Start with 4 states, add only if needed |
| Composable | Context sessions not composing | Ensure operad laws hold |
| Generative | Too much hand-written code | Derive from spec where possible |
| Ethical | Prompt leakage | Frontend NEVER receives system prompts |

---

## Part IV: Success Criteria

### Functional Criteria

- [ ] `ContextSession` manages all context for K-gent and Builders
- [ ] Frontend receives only `ContextOutput` props, never prompts
- [ ] `self.context.*` paths resolve correctly
- [ ] `self.stream.*` paths emit deprecation warnings but still work
- [ ] Compression respects linearity (PRESERVED never dropped)
- [ ] Multi-session coherence via Sheaf

### Test Criteria

- [ ] Comonad laws verified (3 tests)
- [ ] Galois connection properties verified (2 tests)
- [ ] Operad composition laws verified (2 tests)
- [ ] Sheaf coherence verified (3 tests)
- [ ] State machine transitions verified (12+ tests)
- [ ] Integration tests pass (K-gent, Builders, Web)
- [ ] No prompt leakage tests (frontend security)

### Performance Criteria

- [ ] Context compression < 100ms for 100K tokens
- [ ] State transitions < 1ms
- [ ] Rendering < 10ms

---

## Part V: Dependencies

### Required (Must Exist)

| Dependency | Status | Location |
|------------|--------|----------|
| ContextWindow | ✓ Complete | `agents/d/context_window.py` |
| LinearityMap | ✓ Complete | `agents/d/linearity.py` |
| ContextProjector | ✓ Complete | `agents/d/projector.py` |
| AGENTESE Logos | ✓ Complete | `protocols/agentese/logos.py` |
| Operad Core | ✓ Complete | `agents/operad/core.py` |
| Sheaf Core | ✓ Complete | `agents/sheaf/core.py` |

### Consumers (Will Be Updated)

| Consumer | Update Type | Priority |
|----------|-------------|----------|
| K-gent SoulSession | Inject ContextSession | HIGH |
| Builder base class | Add context injection | HIGH |
| WorkshopFlux | Create context sessions | HIGH |
| Web hooks | Use new props | MEDIUM |
| API endpoints | Return ContextOutput | MEDIUM |

---

## Part VI: Timeline

| Day | Phase | Deliverables |
|-----|-------|--------------|
| 1-2 | Extract | Module structure, polynomial implementation |
| 3-4 | Unify | PromptBuilder, ComponentRenderer, ContextSession |
| 5-6 | Integrate | K-gent, Builders, Web UI updates |
| 7-8 | Harden | Operad, Sheaf, comprehensive tests |
| 9-10 | Deprecate | Warnings, documentation, cleanup |

**Total Estimated Effort**: 5-6 focused sessions

---

## Appendix A: File Inventory

### Created (12 files)

```
impl/claude/context/
├── __init__.py
├── polynomial.py
├── window.py
├── pressure.py
├── linearity.py
├── prompt.py
├── session.py
├── render.py
├── operad.py
├── sheaf.py
└── _tests/ (6 test files)
```

### Modified (8 files)

```
impl/claude/agents/k/session.py
impl/claude/agents/town/builders/base.py
impl/claude/protocols/agentese/contexts/__init__.py
impl/claude/protocols/agentese/contexts/self_.py
impl/claude/web/src/hooks/useWorkshopStream.ts (→ useContextSession.ts)
impl/claude/web/src/pages/Workshop.tsx
impl/claude/protocols/api/routes/town.py
spec/protocols/context.md
```

### Deprecated (to remove after migration)

```
impl/claude/protocols/agentese/contexts/stream.py
impl/claude/agents/d/context_window.py (content moves)
impl/claude/agents/d/linearity.py (content moves)
impl/claude/agents/d/projector.py (content moves)
```

---

*"Context is not what you put in—it is the shape of attention itself. The polynomial captures the valid states; the operad captures valid compositions; the sheaf ensures global coherence. Together they form the unified categorical foundation for conversation."*
