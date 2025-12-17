# Wave 1: Crown Jewels Migration

**Status**: Active
**Priority**: High
**Progress**: 0%
**Parent**: `plans/cli-isomorphic-migration.md`
**Depends On**: Wave 0 (Dimension System)
**Last Updated**: 2025-12-17

---

## Objective

Migrate the four Crown Jewel CLI handlers (Brain, Soul, Town, Atelier) to the Isomorphic CLI architecture. These are the most visible, most used commands and serve as the model for all subsequent migrations.

---

## Crown Jewels Overview

| Jewel | Handler | Current Lines | AGENTESE Path | Complexity |
|-------|---------|---------------|---------------|------------|
| Brain | `handlers/brain.py` | 738 | `self.memory.*` | High |
| Soul | `handlers/soul.py` | 306 | `self.soul.*` | Medium |
| Town | `handlers/town.py` | ~300 | `world.town.*` | High |
| Atelier | `handlers/atelier.py` | ~200 | `world.atelier.*` | Medium |

---

## Migration Pattern

Each handler follows the same migration pattern:

### Before (Current)
```python
def cmd_brain(args: list[str], ctx: ...) -> int:
    if "--help" in args:
        print_help()
        return 0

    # Scattered async handling
    return _run_async(_async_route(subcommand, args, json_output))

async def _async_route(...):
    # Handler-specific logic
    brain = await _get_brain()
    result = await brain.capture(content)
    # Manual output formatting
```

### After (Isomorphic)
```python
@logos.node("self.memory")
class MemoryNode:
    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("memory_crystals"), Effect.CALLS("llm")],
        help="Capture content to holographic memory",
        budget_estimate="low",
        streaming=False,
    )
    async def capture(self, observer: Observer, content: str) -> CaptureResult:
        """Capture content to memory with semantic embedding."""
        brain = await self._get_brain()
        return await brain.capture(content)

# CLI invocation routes through projection
# kg brain capture "content" → logos.invoke("self.memory.capture", observer, content="content")
```

---

## Phase 1: Brain Migration (Day 1)

The Brain handler is the most complex but also the best documented. It serves as the template.

### Step 1.1: Create MemoryNode

**File**: `impl/claude/protocols/agentese/contexts/self_memory.py`

```python
@dataclass
class MemoryNode:
    """
    AGENTESE node for self.memory.* paths.

    Crown Jewel Brain provides high-level memory operations:
    - capture: Store content to holographic memory
    - search: Semantic search for similar memories
    - surface: Serendipity from the void
    - status: Brain health statistics
    """

    _brain: Any = field(default=None)

    async def _get_brain(self) -> Any:
        if self._brain is None:
            from agents.brain import get_brain_crystal
            self._brain = await get_brain_crystal()
        return self._brain

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("brain_status")],
        help="Display brain status and health metrics",
        examples=["kg brain", "kg brain status"],
    )
    async def manifest(self, observer: Observer) -> BrainStatus:
        """Show the current brain state."""
        brain = await self._get_brain()
        return await brain.status()

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("memory_crystals"),
            Effect.CALLS("llm"),
        ],
        help="Capture content to holographic memory",
        examples=["kg brain capture 'Python is great'"],
        budget_estimate="low",
    )
    async def capture(self, observer: Observer, content: str) -> CaptureResult:
        """Store content with semantic embedding."""
        brain = await self._get_brain()
        return await brain.capture(content)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("memory_crystals"), Effect.CALLS("llm")],
        help="Semantic search for similar memories",
        examples=["kg brain search 'category theory'"],
        budget_estimate="low",
    )
    async def search(
        self,
        observer: Observer,
        query: str,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search brain for similar content."""
        brain = await self._get_brain()
        return await brain.search(query, limit=limit)

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[Effect.READS("memory_crystals")],
        help="Surface a serendipitous memory",
        examples=["kg brain surface", "kg brain surface 'agents'"],
    )
    async def surface(
        self,
        observer: Observer,
        context: str | None = None,
        entropy: float = 0.7,
    ) -> SearchResult | None:
        """Draw a memory from the void."""
        brain = await self._get_brain()
        return await brain.surface(context=context, entropy=entropy)
```

### Step 1.2: Register MemoryNode in Logos

**File**: `impl/claude/protocols/agentese/contexts/__init__.py`

Add MemoryNode to context resolvers:
```python
def create_context_resolvers(...):
    resolvers["self"] = SelfContextResolver(
        memory=MemoryNode(),  # Crown Jewel Brain
        ...
    )
```

### Step 1.3: Update brain.py as Thin Shim

**File**: `impl/claude/protocols/cli/handlers/brain.py`

```python
"""
Brain Handler: Shim routing to self.memory.* AGENTESE paths.

This file is now a thin routing layer. All logic lives in MemoryNode.
"""

def cmd_brain(args: list[str], ctx: ...) -> int:
    """Route brain commands through AGENTESE projection."""
    from protocols.cli.projection import project_command

    # Map subcommands to paths
    SUBCOMMAND_TO_PATH = {
        "capture": "self.memory.capture",
        "search": "self.memory.search",
        "ghost": "self.memory.search",  # alias
        "surface": "self.memory.surface",
        "list": "self.memory.list",
        "status": "self.memory.manifest",
        "chat": "self.memory.chat",
        "import": "self.memory.import",
    }

    subcommand = _parse_subcommand(args) or "manifest"
    path = SUBCOMMAND_TO_PATH.get(subcommand, "self.memory.manifest")

    return project_command(path, args, ctx)
```

### Step 1.4: Create projection.py

**File**: `impl/claude/protocols/cli/projection.py`

```python
"""
CLI Projection Functor

The bridge between CLI invocation and AGENTESE execution.

CLIProject : (Path, Observer) → Renderable[Terminal]
"""

@dataclass
class CLIProjection:
    """The CLI projection functor."""

    logos: Logos

    async def project(
        self,
        path: str,
        observer: Observer,
        dimensions: CommandDimensions,
        kwargs: dict[str, Any],
    ) -> TerminalOutput:
        """
        Project an AGENTESE path to terminal output.

        Handles:
        1. Async wrapping (if dimensions.execution == ASYNC)
        2. State loading (if dimensions.statefulness == STATEFUL)
        3. Budget display (if dimensions.backend == LLM)
        4. Confirmation (if dimensions.seriousness == SENSITIVE)
        5. Streaming (if dimensions.interactivity == STREAMING)
        """
        # Pre-UX: Confirmation, budget warning
        await self._pre_ux(dimensions, path)

        # Invoke through Logos
        result = await self.logos.invoke(path, observer, **kwargs)

        # Post-UX: Format output
        return self._post_ux(result, dimensions)

    async def _pre_ux(self, dimensions: CommandDimensions, path: str) -> None:
        """Pre-invocation UX: confirmations, warnings."""
        if dimensions.seriousness == Seriousness.SENSITIVE:
            # Show confirmation dialog
            ...

        if dimensions.backend == Backend.LLM:
            # Show budget indicator
            ...

    def _post_ux(self, result: Any, dimensions: CommandDimensions) -> TerminalOutput:
        """Post-invocation UX: formatting."""
        # Dimension-aware formatting
        ...


def project_command(path: str, args: list[str], ctx: Any) -> int:
    """
    Main entry point for CLI → AGENTESE projection.

    This is what handlers call instead of direct business logic.
    """
    import asyncio
    from protocols.agentese import create_logos, Observer
    from protocols.cli.dimensions import derive_dimensions

    logos = create_logos()
    observer = Observer.from_archetype("cli")

    # Get aspect metadata and derive dimensions
    meta = logos.get_aspect_meta(path)
    dimensions = derive_dimensions(path, meta)

    # Parse kwargs from args
    kwargs = _parse_kwargs_from_args(args, path)

    # Project
    projection = CLIProjection(logos)

    try:
        result = asyncio.run(projection.project(path, observer, dimensions, kwargs))
        _render_output(result, ctx)
        return 0
    except Exception as e:
        _render_error(e, dimensions, ctx)
        return 1
```

### Step 1.5: Tests

**File**: `impl/claude/protocols/cli/_tests/test_brain_migration.py`

```python
"""Tests for Brain handler migration to Isomorphic CLI."""

async def test_brain_capture_dimensions():
    """self.memory.capture should derive ASYNC, STATEFUL, LLM."""
    meta = get_aspect_meta("self.memory.capture")
    dims = derive_dimensions("self.memory.capture", meta)

    assert dims.execution == Execution.ASYNC
    assert dims.statefulness == Statefulness.STATEFUL
    assert dims.backend == Backend.LLM
    assert dims.seriousness == Seriousness.NEUTRAL

async def test_brain_surface_dimensions():
    """self.memory.surface should derive ENTROPY characteristics."""
    meta = get_aspect_meta("self.memory.surface")
    dims = derive_dimensions("self.memory.surface", meta)

    # Surface is read-only perception
    assert dims.execution == Execution.SYNC or dims.backend == Backend.PURE
    # But it's from void.* conceptually, so playful
    assert dims.seriousness == Seriousness.NEUTRAL  # Not from void.* path

async def test_kg_brain_capture_end_to_end():
    """kg brain capture routes through projection."""
    result = cmd_brain(["capture", "test content"])
    assert result == 0
```

---

## Phase 2: Soul Migration (Day 2)

Soul has complex routing with multiple modes. The key insight: each mode becomes an aspect.

### Step 2.1: Create SoulNode

**File**: `impl/claude/protocols/agentese/contexts/self_soul.py`

```python
@dataclass
class SoulNode:
    """
    AGENTESE node for self.soul.* paths.

    K-gent Soul is the Middleware of Consciousness.
    """

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.CALLS("llm"), Effect.WRITES("soul_state")],
        help="Engage in self-reflection dialogue",
        examples=["kg soul reflect 'What am I uncertain about?'"],
        budget_estimate="medium",
        streaming=True,  # Soul dialogues stream
    )
    async def reflect(self, observer: Observer, prompt: str | None = None) -> DialogueResult:
        ...

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.CALLS("llm")],
        help="Challenge an idea through dialectics",
        examples=["kg soul challenge 'AI will replace programmers'"],
        budget_estimate="medium",
    )
    async def challenge(self, observer: Observer, idea: str) -> ChallengeResult:
        ...

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("soul_state")],
        help="Show current soul state and eigenvectors",
        examples=["kg soul manifest"],
    )
    async def manifest(self, observer: Observer) -> SoulManifest:
        ...
```

### Step 2.2: Update soul.py as Thin Shim

Similar pattern to brain.py - route modes to paths.

---

## Phase 3: Town Migration (Day 2-3)

Town is simulation-heavy. Key aspects: `populate`, `step`, `gossip`, `manifest`.

---

## Phase 4: Atelier Migration (Day 3)

Atelier manages collaborative workshops. Key aspects: `create`, `list`, `join`.

---

## Acceptance Criteria

For each Crown Jewel:

1. [ ] AGENTESE node created with full aspect metadata
2. [ ] All effects declared
3. [ ] Help text and examples provided
4. [ ] Handler reduced to thin routing shim
5. [ ] Dimensions derive correctly
6. [ ] End-to-end tests pass
7. [ ] No regression in existing functionality

---

## Migration Checklist Template

Copy this for each handler migration:

```markdown
## [Handler Name] Migration

- [ ] Create AGENTESE node at `protocols/agentese/contexts/`
- [ ] Add @aspect decorators with:
  - [ ] category (required)
  - [ ] effects (required for MUTATION/GENERATION)
  - [ ] help (required)
  - [ ] examples (recommended)
  - [ ] budget_estimate (if CALLS effect)
  - [ ] streaming (if applicable)
- [ ] Register node in context resolvers
- [ ] Update handler to thin routing shim
- [ ] Remove handler-specific async wrappers
- [ ] Remove handler-specific state loading
- [ ] Remove handler-specific confirmation dialogs
- [ ] Add to shortcut registry if warranted
- [ ] Add to legacy registry for backwards compatibility
- [ ] Write dimension derivation tests
- [ ] Write end-to-end tests
- [ ] Verify: kg <path> --dry-run
```

---

## Files Created/Modified

| File | Action | Lines Est. |
|------|--------|------------|
| `protocols/agentese/contexts/self_memory.py` | Create | ~200 |
| `protocols/agentese/contexts/self_soul.py` | Create | ~150 |
| `protocols/agentese/contexts/world_town.py` | Create | ~150 |
| `protocols/agentese/contexts/world_atelier.py` | Create | ~100 |
| `protocols/cli/projection.py` | Create | ~150 |
| `protocols/cli/handlers/brain.py` | Modify | -500 |
| `protocols/cli/handlers/soul.py` | Modify | -200 |
| `protocols/cli/handlers/town.py` | Modify | -200 |
| `protocols/cli/handlers/atelier.py` | Modify | -100 |
| `protocols/cli/_tests/test_crown_jewel_migration.py` | Create | ~300 |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking kg brain functionality | Feature flag: `KGENTS_ISOMORPHIC_CLI` |
| Complex soul routing breaks | Mode-by-mode migration, test each |
| Town simulation timing changes | Benchmark before/after |

---

*Next: Wave 2 - Forest + Joy Commands*
