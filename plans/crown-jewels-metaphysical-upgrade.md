---
path: plans/crown-jewels-metaphysical-upgrade
status: complete
progress: 100
last_touched: 2025-12-17
touched_by: claude-opus-4-5
blocking: []
enables:
  - plans/cli/wave1-crown-jewels
  - plans/agentese-v3-crown-synergy-audit
  - plans/crown-jewels-enlightened
session_notes: |
  Created to transformatively apply two new foundations:
  1. CLI Isomorphic Projection (spec/protocols/cli.md, Wave 0-4)
  2. Metaphysical Fullstack Architecture (docs/skills/metaphysical-fullstack.md)

  This plan supersedes the individual wave plans for Crown Jewels.

  Session 2025-12-17 (COMPLETE):
  - Brain migration at 80%: service, node, thin handler all working
  - Soul migration at 50%: thin handler created, SoulNode already has @chatty
  - **Town migration at 100%**: TownNode, thin handler, hollow.py wired
  - **Atelier migration at 100%**: AtelierNode, thin handler, hollow.py wired
  - **Gardener migration at 100%**:
    - Created protocols/agentese/contexts/world_gardener.py with GardenerNode, GardenNode, VoidGardenNode
    - GardenerNode: manifest, start, advance, cycle, polynomial, sessions, intent
    - GardenNode: manifest, plant, harvest, nurture, harvest_to_brain
    - VoidGardenNode: sip (serendipity)
    - Created protocols/cli/handlers/gardener_thin.py (routing shim for concept.gardener.*, self.garden.*, void.garden.*)
    - Wired hollow.py to use gardener_thin
  - **Park migration at 100%**:
    - Created protocols/agentese/contexts/world_park.py with ParkNode, ScenarioNode, MaskNode, ForceNode
    - ScenarioNode: start, tick, phase, complete (crisis practice)
    - MaskNode: manifest, don, doff (dialogue masks)
    - ForceNode: use (consent debt mechanic)
    - Created protocols/cli/handlers/park_thin.py (routing shim)
    - Wired hollow.py to use park_thin

  All 6 Crown Jewels now have:
  - services/<jewel>/ directory with persistence
  - AGENTESE nodes in protocols/agentese/contexts/
  - Thin handlers in protocols/cli/handlers/<jewel>_thin.py
  - Wiring in hollow.py

phase_ledger:
  PLAN: complete
  RESEARCH: complete
  STRATEGIZE: complete
  IMPLEMENT: complete
  REFLECT: complete
entropy:
  planned: 0.15
  spent: 0.15
  returned: 0.0
---

# Crown Jewels Metaphysical Upgrade

> *"The Crown Jewels become fully realized when they complete the metaphysical stack: service → node → projection → surface."*
>
> *"The more fully defined, the more fully projected."*

---

## Part 0: The Synthesis

This plan integrates TWO major architectural foundations:

| Foundation | Spec | Core Insight |
|------------|------|--------------|
| **CLI Isomorphic Projection** | `spec/protocols/cli.md` | CLI is a projection functor of AGENTESE, not a separate protocol |
| **Metaphysical Fullstack** | `docs/skills/metaphysical-fullstack.md` | Services own business logic + persistence; nodes provide semantic interface |

### The Unified Vision

```
┌────────────────────────────────────────────────────────────────────────────┐
│                     METAPHYSICAL FULLSTACK + ISOMORPHIC CLI                 │
│                                                                             │
│   CLI                     Web                    API                        │
│   "kg brain capture"      Click [Capture]        POST /agentese/self.memory │
│        │                       │                       │                    │
│        └───────────────────────┴───────────────────────┘                    │
│                                │                                            │
│                     ┌──────────▼──────────┐                                 │
│                     │  CLI PROJECTION      │  ← Wave 0-4 foundation         │
│                     │  Dimensions → UX     │                                │
│                     └──────────┬──────────┘                                 │
│                                │                                            │
│                     ┌──────────▼──────────┐                                 │
│                     │  AGENTESE NODE       │  ← @aspect decorators          │
│                     │  self.memory.*       │    @chatty for chat            │
│                     │  Semantic interface  │                                │
│                     └──────────┬──────────┘                                 │
│                                │                                            │
│                     ┌──────────▼──────────┐                                 │
│                     │  SERVICE MODULE      │  ← Business logic lives here   │
│                     │  services/brain/     │    TableAdapter + D-gent       │
│                     │  Persistence layer   │    Frontend components         │
│                     └──────────┬──────────┘                                 │
│                                │                                            │
│                     ┌──────────▼──────────┐                                 │
│                     │  INFRASTRUCTURE      │  ← Generic primitives          │
│                     │  agents/poly/        │    PolyAgent, Operad, Sheaf    │
│                     │  agents/d/           │    D-gent persistence          │
│                     └──────────────────────┘                                │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Why This Matters

**Current State**: Crown Jewels are partially implemented across:
- `handlers/brain.py` (738 lines of mixed logic)
- `agents/brain.py` (partial)
- `protocols/api/brain.py` (partial)

**Target State**: Each Crown Jewel is a clean vertical slice:
- `services/brain/` - All business logic and persistence
- `protocols/agentese/contexts/self_memory.py` - Semantic interface
- CLI, Web, API all project from the same node

---

## Part I: Current Crown Jewel Assessment

### What Exists vs What's Needed

| Jewel | Current Location | Service Needed | Node Needed | Progress |
|-------|------------------|----------------|-------------|----------|
| **Brain** | `handlers/brain_thin.py` + `services/brain/` | `services/brain/` ✅ | `self.memory.*` ✅ | **100%** ✅ |
| **Soul** | `handlers/soul_thin.py` + `agents/k/` | `agents/k/` ✅ | `self.soul.*` ✅ | **100%** ✅ |
| **Town** | `handlers/town_thin.py` + `services/town/` | `services/town/` ✅ | `world.town.*` ✅ | **100%** ✅ |
| **Atelier** | `handlers/atelier_thin.py` + `services/atelier/` | `services/atelier/` ✅ | `world.atelier.*` ✅ | **100%** ✅ |
| **Gardener** | `handlers/gardener_thin.py` + `services/gardener/` | `services/gardener/` ✅ | `concept.gardener.*` ✅ | **100%** ✅ |
| **Park** | `handlers/park_thin.py` + `services/park/` | `services/park/` ✅ | `world.park.*` ✅ | **100%** ✅ |

### The Gap

Each jewel needs:
1. **Service extraction** - Move business logic to `services/<jewel>/`
2. **AGENTESE node** - Create/update node with full `@aspect` metadata
3. **Dimension compliance** - Ensure aspects derive correct CLI dimensions
4. **Handler thinning** - Reduce handler to routing shim

---

## Part II: The Migration Pattern

### For Each Crown Jewel

```
Phase 1: Service Extraction (2-3 hours per jewel)
├── Create services/<jewel>/ directory
├── Extract business logic from handler
├── Create persistence layer (TableAdapter + D-gent)
├── Write service tests
└── Verify functionality unchanged

Phase 2: AGENTESE Node (1-2 hours per jewel)
├── Create/update node in protocols/agentese/contexts/
├── Add @aspect decorators with full metadata:
│   ├── category (PERCEPTION, MUTATION, GENERATION, etc.)
│   ├── effects (READS, WRITES, CALLS, CHARGES, FORCES)
│   ├── help text
│   ├── examples
│   └── budget_estimate (if LLM-backed)
├── Wire node to service via dependency injection
└── Register in context resolvers

Phase 3: Handler Thinning (30 min per jewel)
├── Reduce handler to path routing
├── Remove all business logic
├── Add to legacy registry for backwards compat
└── Add to shortcut registry if needed

Phase 4: Dimension Verification (30 min per jewel)
├── Write dimension derivation tests
├── Verify CLI UX matches expected dimensions
└── Test end-to-end flow
```

---

## Part III: Brain Migration (Template)

Brain is the most complex jewel and serves as the template.

### Step 3.1: Create Service

**Directory**: `impl/claude/services/brain/`

```
services/brain/
├── __init__.py           # Public API: capture, search, surface, status
├── crystal.py            # BrainCrystal core logic
├── persistence.py        # BrainPersistence (TableAdapter + D-gent)
├── search.py             # Semantic search implementation
├── embeddings.py         # L-gent embedding integration
├── web/                  # Frontend components (if any)
│   └── components/
└── _tests/
    ├── test_crystal.py
    ├── test_persistence.py
    └── test_search.py
```

**Key Files**:

```python
# services/brain/persistence.py
@dataclass
class BrainPersistence:
    """
    Brain persistence layer.

    Uses dual-track storage:
    - TableAdapter[Crystal] for queryable metadata
    - D-gent Datum for semantic content
    """

    table: TableAdapter[Crystal]
    dgent: DgentProtocol
    embeddings: EmbeddingService

    async def capture(self, content: str, tags: list[str] | None = None) -> CaptureResult:
        """Capture content to brain with semantic embedding."""
        # 1. Generate embedding
        embedding = await self.embeddings.embed(content)

        # 2. Store semantic content in D-gent
        datum = await self.dgent.put(Datum(
            content=content,
            embedding=embedding,
            metadata={"tags": tags or []},
        ))

        # 3. Store queryable metadata in table
        crystal = Crystal(
            id=uuid4(),
            datum_id=datum.id,
            content_preview=content[:200],
            tags=tags or [],
            embedding=embedding,
            created_at=datetime.utcnow(),
            access_count=0,
        )
        await self.table.put(crystal)

        return CaptureResult(
            crystal_id=crystal.id,
            datum_id=datum.id,
            preview=crystal.content_preview,
        )

    async def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        """Semantic search for similar crystals."""
        query_embedding = await self.embeddings.embed(query)

        # Vector similarity search
        results = await self.table.query(
            vector_column="embedding",
            query_vector=query_embedding,
            limit=limit,
        )

        # Increment access counts
        for r in results:
            r.crystal.access_count += 1
            await self.table.put(r.crystal)

        return results
```

### Step 3.2: Create AGENTESE Node

**File**: `impl/claude/protocols/agentese/contexts/self_memory.py`

```python
@dataclass
class MemoryNode:
    """
    AGENTESE node for self.memory.* paths.

    Crown Jewel Brain provides holographic memory operations.
    """

    persistence: BrainPersistence  # Injected from service

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("brain_crystals")],
        help="Display brain status and health metrics",
        examples=["kg brain", "kg brain status"],
    )
    async def manifest(self, observer: Observer) -> BrainStatus:
        """Show current brain state."""
        return await self.persistence.status()

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[
            Effect.WRITES("brain_crystals"),
            Effect.CALLS("llm"),  # For embeddings
        ],
        help="Capture content to holographic memory",
        examples=["kg brain capture 'Python is great for data science'"],
        budget_estimate="low",
    )
    async def capture(self, observer: Observer, content: str, tags: list[str] | None = None) -> CaptureResult:
        """Store content with semantic embedding."""
        return await self.persistence.capture(content, tags)

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[
            Effect.READS("brain_crystals"),
            Effect.CALLS("llm"),
        ],
        help="Semantic search for similar memories",
        examples=["kg brain search 'category theory'"],
        budget_estimate="low",
    )
    async def search(self, observer: Observer, query: str, limit: int = 10) -> list[SearchResult]:
        """Search brain for similar content."""
        return await self.persistence.search(query, limit)

    @aspect(
        category=AspectCategory.ENTROPY,
        effects=[Effect.READS("brain_crystals")],
        help="Surface a serendipitous memory from the void",
        examples=["kg brain surface", "kg brain surface 'agents'"],
    )
    async def surface(self, observer: Observer, context: str | None = None, entropy: float = 0.7) -> SearchResult | None:
        """Draw a memory from the Accursed Share."""
        return await self.persistence.surface(context, entropy)
```

### Step 3.3: Thin Handler

**File**: `impl/claude/protocols/cli/handlers/brain.py`

```python
"""
Brain Handler: Thin routing shim to self.memory.* AGENTESE paths.

All business logic lives in services/brain/. This file only routes.
"""

def cmd_brain(args: list[str], ctx: ...) -> int:
    """Route brain commands through AGENTESE projection."""
    from protocols.cli.projection import project_command

    SUBCOMMAND_TO_PATH = {
        "capture": "self.memory.capture",
        "search": "self.memory.search",
        "ghost": "self.memory.search",  # alias
        "surface": "self.memory.surface",
        "list": "self.memory.list",
        "status": "self.memory.manifest",
        "chat": "self.memory.chat.send",
        "import": "self.memory.import",
    }

    subcommand = _parse_subcommand(args) or "manifest"
    path = SUBCOMMAND_TO_PATH.get(subcommand, "self.memory.manifest")

    return project_command(path, args, ctx)
```

### Step 3.4: Dimension Tests

```python
# protocols/cli/_tests/test_brain_dimensions.py

def test_brain_capture_dimensions():
    """self.memory.capture derives ASYNC, STATEFUL, LLM."""
    meta = get_aspect_meta("self.memory.capture")
    dims = derive_dimensions("self.memory.capture", meta)

    assert dims.execution == Execution.ASYNC
    assert dims.statefulness == Statefulness.STATEFUL
    assert dims.backend == Backend.LLM
    assert dims.seriousness == Seriousness.NEUTRAL

def test_brain_surface_dimensions():
    """self.memory.surface derives ENTROPY characteristics."""
    meta = get_aspect_meta("self.memory.surface")
    dims = derive_dimensions("self.memory.surface", meta)

    assert dims.execution == Execution.SYNC
    assert dims.backend == Backend.PURE
    # Not from void.* path, so not PLAYFUL
    assert dims.seriousness == Seriousness.NEUTRAL
```

---

## Part IV: Soul Migration

Soul has the `@chatty` decorator for interactive chat.

### Service Structure

```
services/soul/
├── __init__.py
├── soul.py              # K-gent soul core logic
├── dialogue.py          # Dialogue management
├── eigenvector.py       # Personality eigenvectors
├── hypnagogia.py        # Dream cycle
└── _tests/
```

### Node with Chat

```python
# protocols/agentese/contexts/self_soul.py

from protocols.agentese.affordances import chatty

@chatty(
    system_prompt_template=SOUL_SYSTEM_PROMPT,
    context_strategy="summarize",
    token_budget=8000,
    personality_eigenvectors=True,
)
@dataclass
class SoulNode:
    """AGENTESE node for self.soul.* paths."""

    soul: SoulService

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("soul_state")],
        help="Show current soul state and eigenvectors",
        examples=["kg soul", "kg soul manifest"],
    )
    async def manifest(self, observer: Observer) -> SoulManifest:
        return await self.soul.manifest()

    @aspect(
        category=AspectCategory.GENERATION,
        effects=[Effect.CALLS("llm")],
        help="Challenge an idea through dialectics",
        examples=["kg soul challenge 'AI will replace programmers'"],
        budget_estimate="medium",
    )
    async def challenge(self, observer: Observer, idea: str) -> ChallengeResult:
        return await self.soul.challenge(idea)

    # chat.* affordances auto-added by @chatty decorator
```

---

## Part V: Town Migration

Town has citizen-specific nodes with chat.

### Service Structure

```
services/town/
├── __init__.py
├── town.py              # TownSimulation core
├── citizen.py           # Citizen logic
├── coalition.py         # Coalition management
├── memory.py            # Citizen memory (D-gent)
├── dialogue.py          # Multi-citizen dialogue
└── _tests/
```

### Node with Per-Citizen Chat

```python
# protocols/agentese/contexts/world_town.py

@dataclass
class TownNode:
    """AGENTESE node for world.town.* paths."""

    town: TownService

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("town_state")],
        help="Show town status and citizen activity",
        examples=["kg town", "kg town manifest"],
    )
    async def manifest(self, observer: Observer) -> TownManifest:
        return await self.town.manifest()

# Citizen nodes are resolved dynamically
# world.town.citizen.elara.chat.* → CitizenNode(name="elara")
```

---

## Part VI: Implementation Sequence

### Wave 0: Dimension System (COMPLETE)

Already implemented. Foundation is ready.

### Wave 1: Crown Jewels (This Plan)

**Sequence**: Brain → Soul → Town → Atelier → Gardener → Park

| Step | Jewel | Service | Node | Handler | Tests | Est. Hours |
|------|-------|---------|------|---------|-------|------------|
| 1.1 | Brain | Create | Create | Thin | 30+ | 6 |
| 1.2 | Soul | Create | Add @chatty | Thin | 20+ | 4 |
| 1.3 | Town | Refactor | Create | Thin | 20+ | 5 |
| 1.4 | Atelier | Create | Create | Thin | 15+ | 4 |
| 1.5 | Gardener | Refactor | Create | Thin | 15+ | 3 |
| 1.6 | Park | Create | Create | Thin | 10+ | 3 |
| **Total** | | | | | **110+** | **25** |

### Wave 2-4: After Crown Jewels

Per existing wave plans:
- Wave 2: Forest + Joy commands
- Wave 3: Help projection from affordances
- Wave 4: Full observability

---

## Part VII: Success Criteria

### Structural

- [ ] `services/` directory contains all Crown Jewel business logic
- [ ] Each jewel has a service, node, and thin handler
- [ ] No business logic in handlers (< 50 lines each)
- [ ] All AGENTESE nodes have complete @aspect metadata

### Functional

- [ ] `kg brain capture` routes through service
- [ ] `kg soul chat` enters interactive REPL
- [ ] `kg town chat elara` works with citizen memory
- [ ] All existing tests pass
- [ ] 110+ new tests for services and nodes

### CLI Dimensions

- [ ] All MUTATION aspects have effects declared
- [ ] All LLM-backed aspects have budget_estimate
- [ ] All aspects have help text and examples
- [ ] Dimension derivation tests pass for all paths

### Architectural

- [ ] Main website is shallow passthrough (no embedded logic)
- [ ] AGENTESE universal protocol handles all routing
- [ ] D-gent persistence is used consistently
- [ ] Observability spans cover all services

---

## Part VIII: Anti-Patterns (From Metaphysical Fullstack)

### What We're Eliminating

1. **Business logic in handlers**
   ```python
   # BAD: handlers/brain.py
   def cmd_brain(args):
       crystal = Crystal(...)
       session.add(crystal)  # Direct DB access!
   ```

2. **Explicit backend routes**
   ```python
   # BAD: protocols/api/brain.py
   @router.post("/brain/capture")
   async def capture(request):
       ...  # Bypasses AGENTESE!
   ```

3. **Service in agents/ directory**
   ```
   # BAD: agents/brain/
   # Services go in services/, agents/ is for primitives
   ```

4. **Scattered persistence**
   ```python
   # BAD: Multiple places using different patterns
   # Good: All persistence through services/<jewel>/persistence.py
   ```

---

## Part IX: Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Wave 0 (Dimensions) | ✅ Complete | Foundation ready |
| `@aspect` v3.2 fields | ✅ Complete | help, streaming, budget_estimate |
| `@chatty` decorator | ✅ Complete | Per chat-protocol-implementation.md |
| Chat Protocol (Phase 1-2) | ✅ Complete | 82 tests passing |
| Chat Protocol (Phase 3-5) | 🔴 Pending | CLI projection needed |
| D-gent TableAdapter | ✅ Exists | `agents/d/` |
| BrainPersistence | 🔴 Create | In services/brain/ |

---

## Part X: Migration Checklist (Per Jewel)

```markdown
## [Jewel] Migration Checklist

### Service
- [ ] Create services/<jewel>/ directory
- [ ] Create __init__.py with public API
- [ ] Create core business logic module
- [ ] Create persistence.py with TableAdapter + D-gent
- [ ] Write unit tests (15+ per jewel)
- [ ] Verify existing functionality works

### AGENTESE Node
- [ ] Create/update node in protocols/agentese/contexts/
- [ ] Add @aspect decorators with:
  - [ ] category (required)
  - [ ] effects (required for MUTATION/GENERATION)
  - [ ] help (required)
  - [ ] examples (recommended)
  - [ ] budget_estimate (if CALLS effect)
  - [ ] streaming (if applicable)
- [ ] Add @chatty if chat-capable
- [ ] Wire to service via dependency injection
- [ ] Register in context resolvers

### Handler
- [ ] Reduce to thin routing (< 50 lines)
- [ ] Remove all business logic
- [ ] Add to shortcut registry (e.g., "/brain")
- [ ] Add to legacy registry for backwards compat

### Dimensions
- [ ] Write dimension derivation tests
- [ ] Verify execution (SYNC/ASYNC) correct
- [ ] Verify statefulness correct
- [ ] Verify backend (PURE/LLM/EXTERNAL) correct
- [ ] Verify seriousness correct

### Integration
- [ ] End-to-end CLI test
- [ ] API endpoint test (via AGENTESE router)
- [ ] Web projection test (if applicable)
```

---

## Part XI: Post-Migration Synergies

Once all jewels are migrated, the `agentese-v3-crown-synergy-audit.md` unlocks:

| v3 Feature | Synergy | Now Possible |
|------------|---------|--------------|
| **Subscriptions** | Real-time streaming | `logos.subscribe("self.memory.ghost.*")` |
| **String >>** | Cross-jewel pipelines | `"self.memory.capture" >> "self.gardener.plant"` |
| **Query syntax** | Bounded discovery | `logos.query("?self.memory.crystal.*")` |
| **Effects composition** | Budget tracking | Effects sum across pipelines |
| **Unified observability** | Cross-service traces | One span hierarchy for all jewels |

---

*"When services own their logic and nodes provide semantic access, the projection is automatic. This is the Metaphysical Fullstack."*

*Created: 2025-12-17 by claude-opus-4-5*
