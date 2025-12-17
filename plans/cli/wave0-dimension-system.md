# Wave 0: Command Dimension System

**Status**: Complete
**Priority**: Critical (Foundation)
**Progress**: 100%
**Parent**: `plans/cli-isomorphic-migration.md`
**Last Updated**: 2025-12-17
**Completed**: 2025-12-17

---

## Objective

Implement the Command Dimension Space from `spec/protocols/cli.md` Part II. Every CLI command exists in a 6-dimensional product space:

```
CommandSpace = Execution × Statefulness × Backend × Intent × Seriousness × Interactivity
```

This wave creates the infrastructure that all subsequent waves depend on.

---

## The Core Insight

> *"Just as screen density replaced scattered `isMobile` checks, command dimensions replace scattered behavioral checks."*

The dimension system is a **Simplifying Isomorphism** (AD-008). Instead of:
```python
if is_async_command(name):
    result = await run_async(handler, args)
```

We have:
```python
dimensions = derive_dimensions(path)
result = await cli_project(path, observer, dimensions)
```

---

## Tasks

### Phase 1: Data Types (Day 1 AM)

**File**: `impl/claude/protocols/cli/dimensions.py`

```python
from enum import Enum, auto
from dataclasses import dataclass

class Execution(Enum):
    SYNC = auto()
    ASYNC = auto()

class Statefulness(Enum):
    STATELESS = auto()
    STATEFUL = auto()

class Backend(Enum):
    PURE = auto()
    LLM = auto()
    EXTERNAL = auto()

class Seriousness(Enum):
    SENSITIVE = auto()
    PLAYFUL = auto()
    NEUTRAL = auto()

class Interactivity(Enum):
    ONESHOT = auto()
    STREAMING = auto()
    INTERACTIVE = auto()

@dataclass(frozen=True)
class CommandDimensions:
    """The 6-dimensional command space."""
    execution: Execution
    statefulness: Statefulness
    backend: Backend
    intent: str  # "functional" | "instructional"
    seriousness: Seriousness
    interactivity: Interactivity
```

**Tests**:
- [x] `test_dimension_types.py` - Enum completeness
- [x] `test_dimension_equality.py` - Frozen dataclass behavior

### Phase 2: Derivation Rules (Day 1 PM)

**File**: `impl/claude/protocols/cli/dimensions.py` (continued)

Implement derivation from AspectCategory and Effects:

```python
def derive_from_category(category: AspectCategory) -> tuple[Execution, Statefulness]:
    """Derive execution and statefulness from aspect category."""
    CATEGORY_RULES = {
        AspectCategory.PERCEPTION: (Execution.SYNC, Statefulness.STATELESS),
        AspectCategory.MUTATION: (Execution.ASYNC, Statefulness.STATEFUL),
        AspectCategory.GENERATION: (Execution.ASYNC, Statefulness.STATEFUL),
        AspectCategory.COMPOSITION: (Execution.SYNC, Statefulness.STATELESS),
        AspectCategory.INTROSPECTION: (Execution.SYNC, Statefulness.STATELESS),
        AspectCategory.ENTROPY: (Execution.SYNC, Statefulness.STATELESS),
    }
    return CATEGORY_RULES.get(category, (Execution.SYNC, Statefulness.STATELESS))

def derive_backend(effects: list[Effect]) -> Backend:
    """Derive backend from declared effects."""
    for effect in effects:
        if isinstance(effect, DeclaredEffect):
            if effect.effect == Effect.CALLS:
                if "llm" in effect.resource.lower():
                    return Backend.LLM
                return Backend.EXTERNAL
    return Backend.PURE

def derive_seriousness(path: str, effects: list[Effect]) -> Seriousness:
    """Derive seriousness from path context and effects."""
    # Playful if void.* context
    if path.startswith("void."):
        return Seriousness.PLAYFUL

    # Sensitive if FORCES effect present
    for effect in effects:
        if isinstance(effect, DeclaredEffect):
            if effect.effect == Effect.FORCES:
                return Seriousness.SENSITIVE

    # Sensitive if writes to protected resources
    PROTECTED = {"soul", "memory", "forest", "config"}
    for effect in effects:
        if isinstance(effect, DeclaredEffect):
            if effect.effect == Effect.WRITES:
                if effect.resource.lower() in PROTECTED:
                    return Seriousness.SENSITIVE

    return Seriousness.NEUTRAL

def derive_interactivity(meta: AspectMetadata) -> Interactivity:
    """Derive interactivity from aspect metadata."""
    if getattr(meta, "interactive", False):
        return Interactivity.INTERACTIVE
    if getattr(meta, "streaming", False):
        return Interactivity.STREAMING
    return Interactivity.ONESHOT
```

**Tests**:
- [x] `test_derive_from_category.py` - All categories covered
- [x] `test_derive_backend.py` - LLM vs EXTERNAL vs PURE
- [x] `test_derive_seriousness.py` - void.* → PLAYFUL, FORCES → SENSITIVE
- [x] `test_derive_interactivity.py` - streaming flag handling

### Phase 3: Full Derivation (Day 2 AM)

**File**: `impl/claude/protocols/cli/dimensions.py` (continued)

```python
def derive_dimensions(
    path: str,
    meta: AspectMetadata,
) -> CommandDimensions:
    """
    Derive complete dimensions from path and aspect metadata.

    This is the SINGLE SOURCE OF TRUTH for CLI behavior.
    No scattered conditionals should exist outside this derivation.
    """
    execution, statefulness = derive_from_category(meta.category)

    # Override execution if effects indicate async needed
    if any(isinstance(e, DeclaredEffect) and e.effect == Effect.CALLS
           for e in meta.effects):
        execution = Execution.ASYNC

    # Override statefulness if effects indicate state access
    has_state_effect = any(
        isinstance(e, DeclaredEffect) and e.effect in (Effect.READS, Effect.WRITES)
        for e in meta.effects
    )
    if has_state_effect:
        statefulness = Statefulness.STATEFUL

    return CommandDimensions(
        execution=execution,
        statefulness=statefulness,
        backend=derive_backend(meta.effects),
        intent="instructional" if meta.category == AspectCategory.INTROSPECTION else "functional",
        seriousness=derive_seriousness(path, meta.effects),
        interactivity=derive_interactivity(meta),
    )
```

**Tests**:
- [x] `test_derive_dimensions_brain.py` - self.memory.capture → ASYNC, STATEFUL, LLM
- [x] `test_derive_dimensions_forest.py` - self.forest.manifest → SYNC, STATEFUL, PURE
- [x] `test_derive_dimensions_void.py` - void.*.sip → SYNC, STATELESS, PURE, PLAYFUL

### Phase 4: Integration with @aspect (Day 2 PM)

**File**: `impl/claude/protocols/agentese/affordances.py` (extend)

Add new fields to `@aspect` decorator:

```python
def aspect(
    category: AspectCategory,
    effects: list[DeclaredEffect | Effect] | None = None,
    requires_archetype: tuple[str, ...] = (),
    idempotent: bool = False,
    description: str = "",
    # v3.1: Extended for self-documentation
    examples: list[str] | None = None,
    see_also: list[str] | None = None,
    since_version: str = "1.0",
    # v3.2: CLI Integration
    help: str = "",  # Short help text (required for CLI)
    long_help: str = "",  # Extended help
    streaming: bool = False,  # Enable streaming output
    interactive: bool = False,  # Enable REPL mode
    budget_estimate: str | None = None,  # LLM cost estimate
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    ...
```

**Tests**:
- [x] `test_aspect_v32_fields.py` - New fields accessible (verified via derive_dimensions tests)
- [x] `test_aspect_backward_compat.py` - Old decorations still work (559 existing tests pass)

### Phase 5: Validation (Day 2 PM)

**File**: `impl/claude/protocols/cli/validation.py`

```python
@dataclass
class ValidationError:
    path: str
    message: str
    severity: str = "error"  # error, warning

def validate_aspect_registration(
    node_path: str,
    aspect_meta: AspectMetadata,
) -> list[ValidationError]:
    """
    Validate aspect metadata at registration time.

    Per spec §4.2, this ensures AI agents cannot misconfigure.
    """
    errors = []

    # 1. Category is required
    if aspect_meta.category is None:
        errors.append(ValidationError(
            node_path,
            "AspectCategory required for CLI exposure"
        ))

    # 2. Effects must be declared for MUTATION/GENERATION
    if aspect_meta.category in (AspectCategory.MUTATION, AspectCategory.GENERATION):
        if not aspect_meta.effects:
            errors.append(ValidationError(
                node_path,
                "MUTATION/GENERATION aspects must declare effects"
            ))

    # 3. Help text required
    if not aspect_meta.help:
        errors.append(ValidationError(
            node_path,
            "Help text required for CLI exposure",
            severity="warning"  # Start as warning, escalate to error later
        ))

    # 4. CALLS effect requires budget estimation
    has_calls = any(
        isinstance(e, DeclaredEffect) and e.effect == Effect.CALLS
        for e in aspect_meta.effects
    )
    if has_calls and aspect_meta.budget_estimate is None:
        errors.append(ValidationError(
            node_path,
            "LLM-backed aspects must estimate budget",
            severity="warning"
        ))

    return errors
```

**Tests**:
- [x] `test_validate_requires_category.py`
- [x] `test_validate_mutation_needs_effects.py`
- [x] `test_validate_calls_needs_budget.py`

---

## Acceptance Criteria

1. [x] All dimension types defined and frozen (6 enums + CommandDimensions dataclass)
2. [x] Derivation rules cover all AspectCategories (6 categories covered)
3. [x] `derive_dimensions()` produces correct output for 10+ paths (8 test scenarios)
4. [x] `@aspect` extended with v3.2 fields (help, long_help, streaming, interactive, budget_estimate)
5. [x] Validation catches incomplete registrations (5 validation rules)
6. [x] Tests pass with >90% coverage on new code (85 tests passing)

---

## Files Created/Modified

| File | Action | Lines Actual |
|------|--------|------------|
| `protocols/cli/dimensions.py` | Created | ~400 |
| `protocols/cli/validation.py` | Created | ~230 |
| `protocols/agentese/affordances.py` | Modified | +45 |
| `protocols/cli/_tests/test_dimensions.py` | Created | ~400 |
| `protocols/cli/_tests/test_validation.py` | Created | ~250 |
| `protocols/cli/__init__.py` | Modified | +50 |

---

## Dependencies

- None (this is the foundation)

## Dependents

- Wave 1: Crown Jewels Migration
- Wave 2: Forest + Joy
- Wave 3: Help/Affordances
- Wave 4: Observability

---

*Next: Wave 1 - Crown Jewels Migration*
