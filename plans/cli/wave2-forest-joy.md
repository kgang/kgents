# Wave 2: Forest Protocol + Joy Commands Migration

**Status**: Complete
**Priority**: Medium
**Progress**: 100%
**Parent**: `plans/cli-isomorphic-migration.md`
**Depends On**: Wave 0 (Dimension System)
**Last Updated**: 2025-12-17
**Completed**: 2025-12-17

---

## Objective

Migrate the Forest Protocol commands and Joy commands to the Isomorphic CLI architecture. These commands are already partially AGENTESE-aware, making them good candidates for migration after the Crown Jewels establish the pattern.

---

## Commands Overview

### Forest Protocol (self.forest.*)

| Handler | Current State | AGENTESE Path | Notes |
|---------|---------------|---------------|-------|
| `forest.py` | ✅ Uses ForestNode | `self.forest.*` | Most migrated |
| `grow.py` | Thin wrapper | `self.grow.*` | Links to self.forest |
| `tend.py` | Thin wrapper | `self.forest.tend` | Same as grow |
| `garden.py` | Some AGENTESE | `self.forest.garden` | Hypnagogia |
| `gardener.py` | Logos integration | `self.gardener.*` | Advanced |

### Joy Commands (void.*)

| Handler | Purpose | AGENTESE Path | Complexity |
|---------|---------|---------------|------------|
| `challenge.py` | Oblique Strategies | `void.oblique.sip` | Simple |
| `oblique.py` | Same as challenge | `void.oblique.*` | Simple |
| `surprise.py` | Random serendipity | `void.surprise.sip` | Simple |

### Soul Extensions

| Handler | Purpose | AGENTESE Path | Complexity |
|---------|---------|---------------|------------|
| `why.py` | Recursive Why | `self.soul.why` | Medium |
| `tension.py` | Tension detection | `self.soul.tension` | Medium |
| `flinch.py` | Flinch detection | `self.soul.flinch` | Simple |

---

## Phase 1: Forest Protocol Completion (Day 1)

### Step 1.1: Verify ForestNode Completeness

The ForestNode already exists at `protocols/agentese/contexts/forest.py`. Verify it has all required aspects:

```python
# Expected aspects with @aspect decorators
class ForestNode:
    @aspect(category=PERCEPTION, help="Show canopy view of forest health")
    async def manifest(self, observer: Observer) -> ForestManifest: ...

    @aspect(category=PERCEPTION, help="Show drift report for stale plans")
    async def witness(self, observer: Observer) -> DriftReport: ...

    @aspect(category=MUTATION, effects=[WRITES("plans_archive")], help="Archive stale plans")
    async def tithe(self, observer: Observer, execute: bool = False) -> TitheResult: ...

    @aspect(category=MUTATION, effects=[WRITES("forest_meta")], help="Full reconciliation")
    async def reconcile(self, observer: Observer, commit: bool = False) -> ReconcileResult: ...

    @aspect(category=PERCEPTION, help="Show implementation status matrix")
    async def status(self, observer: Observer) -> StatusMatrix: ...
```

### Step 1.2: Add Missing @aspect Metadata

**File**: `impl/claude/protocols/agentese/contexts/forest.py`

Add missing decorators:
- `help` text for each aspect
- `examples` for CLI usage
- `effects` declarations

### Step 1.3: Simplify forest.py Handler

**File**: `impl/claude/protocols/cli/handlers/forest.py`

The handler is already routing to ForestNode. Simplify further:

```python
def cmd_forest(args: list[str], ctx: ...) -> int:
    """Route forest commands through AGENTESE projection."""
    from protocols.cli.projection import project_command

    SUBCOMMAND_TO_PATH = {
        "manifest": "self.forest.manifest",
        "status": "self.forest.status",
        "witness": "self.forest.witness",
        "tithe": "self.forest.tithe",
        "reconcile": "self.forest.reconcile",
    }

    subcommand = _parse_subcommand(args) or "manifest"
    path = SUBCOMMAND_TO_PATH.get(subcommand, "self.forest.manifest")

    return project_command(path, args, ctx)
```

### Step 1.4: Merge grow.py, tend.py, garden.py

These are thin wrappers. Consolidate into aliases:

**File**: `impl/claude/protocols/cli/legacy.py`

```python
LEGACY_COMMANDS.update({
    "grow": "self.forest.grow",
    "tend": "self.forest.tend",
    "garden": "self.forest.garden",
})
```

Remove individual handler files after adding to legacy registry.

---

## Phase 2: Joy Commands (Day 1)

Joy commands embody the Accursed Share principle - playful entropy.

### Step 2.1: Create VoidNode

**File**: `impl/claude/protocols/agentese/contexts/void_joy.py`

```python
@dataclass
class JoyNode:
    """
    AGENTESE node for void.joy.* paths.

    The Joy commands embody the Accursed Share - structured serendipity
    that prevents system ossification.
    """

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[],  # Pure computation, no side effects
        help="Draw an Oblique Strategy for lateral thinking",
        examples=["kg oblique", "kg challenge"],
        see_also=["void.surprise.sip"],
    )
    async def oblique(self, observer: Observer) -> str:
        """Draw from the Oblique Strategies deck."""
        from agents.joy import get_oblique_strategy
        return get_oblique_strategy()

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[],
        help="Get a random surprise prompt",
        examples=["kg surprise"],
    )
    async def surprise(self, observer: Observer) -> str:
        """Generate serendipitous inspiration."""
        from agents.joy import get_surprise
        return get_surprise()
```

### Step 2.2: Register Joy Shortcuts

**File**: `impl/claude/protocols/cli/shortcuts.py`

```python
SHORTCUTS.update({
    "/oblique": "void.joy.oblique",
    "/surprise": "void.joy.surprise",
    "/serendipity": "void.joy.surprise",  # alias
})
```

### Step 2.3: Joy Dimensions

These commands should derive:
- `Execution.SYNC` - No async needed
- `Statefulness.STATELESS` - Pure functions
- `Backend.PURE` - No external calls
- `Seriousness.PLAYFUL` - void.* context
- `Interactivity.ONESHOT` - Single response

---

## Phase 3: Soul Extensions (Day 2)

### Step 3.1: Add Why Aspect to SoulNode

**File**: `impl/claude/protocols/agentese/contexts/self_soul.py`

```python
@aspect(
    category=AspectCategory.GENERATION,
    effects=[Effect.CALLS("llm")],
    help="Recursive Why - drill to root causes",
    examples=["kg why 'We need more tests'", "kg soul why 'I feel stuck'"],
    budget_estimate="medium",  # Multiple LLM calls possible
)
async def why(self, observer: Observer, statement: str, depth: int = 5) -> WhyChain:
    """
    Recursive Why questioning to find root causes.

    Keeps asking "Why?" up to `depth` times, revealing
    underlying assumptions and beliefs.
    """
    from agents.k.recursive_why import run_why_chain
    return await run_why_chain(statement, depth)
```

### Step 3.2: Add Tension Aspect

```python
@aspect(
    category=AspectCategory.PERCEPTION,
    effects=[Effect.READS("conversation_context")],
    help="Detect tensions in recent conversation",
    examples=["kg tension"],
)
async def tension(self, observer: Observer) -> TensionReport:
    """
    Detect unresolved tensions in recent dialogue.

    Scans conversation history for:
    - Contradictory statements
    - Unacknowledged emotions
    - Implicit disagreements
    """
    from agents.k.tension import detect_tensions
    return await detect_tensions()
```

### Step 3.3: Add Flinch Aspect

```python
@aspect(
    category=AspectCategory.ENTROPY,
    effects=[],
    help="Detect flinching - what are you avoiding?",
    examples=["kg flinch"],
)
async def flinch(self, observer: Observer, topic: str | None = None) -> FlinchDetection:
    """
    Notice what you're flinching from.

    Often the thing we avoid is the thing most worth doing.
    """
    from agents.k.flinch import detect_flinch
    return detect_flinch(topic)
```

### Step 3.4: Remove Individual Handlers

Once added to SoulNode, remove:
- `handlers/why.py`
- `handlers/tension.py`
- `handlers/flinch.py`

Add to legacy registry for backwards compatibility.

---

## Phase 4: Dimension Verification (Day 2)

### Forest Dimensions

```python
def test_forest_dimensions():
    """Forest commands should derive appropriate dimensions."""

    # self.forest.manifest - read-only perception
    dims = derive_dimensions("self.forest.manifest", meta)
    assert dims.execution == Execution.SYNC
    assert dims.statefulness == Statefulness.STATEFUL  # Reads plans
    assert dims.backend == Backend.PURE

    # self.forest.tithe - mutation with confirmation
    dims = derive_dimensions("self.forest.tithe", meta)
    assert dims.statefulness == Statefulness.STATEFUL
    assert dims.seriousness == Seriousness.SENSITIVE  # FORCES archival
```

### Joy Dimensions

```python
def test_joy_dimensions():
    """Joy commands from void.* should be playful."""

    dims = derive_dimensions("void.joy.oblique", meta)
    assert dims.execution == Execution.SYNC
    assert dims.statefulness == Statefulness.STATELESS
    assert dims.backend == Backend.PURE
    assert dims.seriousness == Seriousness.PLAYFUL  # void.* context
```

### Soul Extension Dimensions

```python
def test_why_dimensions():
    """Why should derive as LLM-backed generation."""

    dims = derive_dimensions("self.soul.why", meta)
    assert dims.execution == Execution.ASYNC
    assert dims.backend == Backend.LLM
    assert dims.seriousness == Seriousness.NEUTRAL
```

---

## Acceptance Criteria

### Forest Protocol
- [x] ForestNode has complete @aspect metadata
- [x] All forest aspects have help text and examples
- [x] Handler reduced to thin routing
- [ ] grow/tend/garden merged into aliases (deferred - lower priority)
- [x] Dimensions derive correctly

### Joy Commands
- [x] VoidNode (JoyNode) created (added to void.py)
- [x] Oblique, Surprise, Challenge, Flinch aspects implemented
- [x] Thin handler created (joy.py)
- [x] Playful seriousness derives from void.* context
- [x] Dimension tests added

### Soul Extensions
- [x] Why, Tension added to SoulNode
- [x] Effects properly declared
- [x] Budget estimates for LLM aspects
- [ ] Individual handlers removed (deferred - may keep as shortcuts)
- [ ] Legacy aliases maintained (deferred - lower priority)

---

## Files Created/Modified

| File | Action | Lines Est. |
|------|--------|------------|
| `protocols/agentese/contexts/forest.py` | Modify | +50 |
| `protocols/agentese/contexts/void_joy.py` | Create | ~80 |
| `protocols/agentese/contexts/self_soul.py` | Modify | +100 |
| `protocols/cli/handlers/forest.py` | Modify | -100 |
| `protocols/cli/handlers/grow.py` | Delete | -60 |
| `protocols/cli/handlers/tend.py` | Delete | -40 |
| `protocols/cli/handlers/why.py` | Delete | -100 |
| `protocols/cli/handlers/tension.py` | Delete | -80 |
| `protocols/cli/handlers/flinch.py` | Delete | -50 |
| `protocols/cli/legacy.py` | Modify | +20 |
| `protocols/cli/shortcuts.py` | Modify | +10 |
| `protocols/cli/_tests/test_forest_joy_migration.py` | Create | ~200 |

---

## Consolidation Benefit

This wave removes approximately **10 handler files** and consolidates their logic into **2 AGENTESE nodes**. This demonstrates the power of the Isomorphic CLI architecture:

- **Before**: 10 files, ~500 lines, scattered logic
- **After**: 2 nodes + 50 lines of aliases, centralized logic

---

*Next: Wave 3 - Help/Affordances Projection*
