# Memory-First Documentation: Execution Plan

> *"Teaching moments don't die; they become ancestors."*

**Status:** 🟡 Phase 2A Complete (2-3 sessions remaining)
**Spec:** `spec/protocols/memory-first-docs.md`
**Parent Plan:** `plans/_archive/.../memory-first-docs-rollout.md`
**Priority:** HIGH (institutional memory at risk)
**Filed:** 2025-12-22

---

## 🎯 GROUNDING IN KENT'S INTENT

> *"Don't waste good work, like you wouldn't waste food."*
> *"The persona is a garden, not a museum."*

This plan ensures wisdom survives code deletion. The 2025-12-21 Crown Jewel Cleanup deleted ~52K lines—Town, Park, Gestalt, Forge, Coalition, Muse, Gardener. Their gotchas would normally be lost. Memory-First makes them **ancestors** that haunt future hydrations.

---

## Current State (What Already Exists)

| Component | Status | Location |
|-----------|--------|----------|
| `TeachingCrystal` model | ✅ Complete | `models/brain.py` |
| `ExtinctionEvent` model | ✅ Complete | `models/brain.py` |
| `ExtinctionTeaching` join | ✅ Complete | `models/brain.py` |
| `crystallize_teaching()` | ✅ Complete | `services/brain/persistence.py` |
| `get_alive_teaching()` | ✅ Complete | `services/brain/persistence.py` |
| `get_teaching_by_module()` | ✅ Complete | `services/brain/persistence.py` |
| Crystallization tests | ✅ 10 passing | `services/brain/_tests/test_crystallization.py` |
| `prepare_extinction()` | 🔴 Not Started | — |
| Bootstrap script | 🔴 Not Started | — |
| `kg docs extract --crystallize` | 🔴 Not Started | — |
| `void.extinct.*` AGENTESE nodes | 🔴 Not Started | — |
| `hydrate_with_ghosts()` | 🔴 Not Started | — |

---

## Remaining Phases

### Phase 2B: Bootstrap & CLI Wiring (1 session)

**Goal:** Crystallize all ~165 existing teaching moments and wire CLI.

#### Task 2B.1: Bootstrap Script

**File:** `impl/claude/scripts/bootstrap_teaching_crystals.py`

```python
"""
Bootstrap all teaching moments from Living Docs into Brain.

Usage:
    uv run python scripts/bootstrap_teaching_crystals.py [--dry-run]

Teaching:
    gotcha: Run with --dry-run first to preview without persistence.
            (Evidence: this script)
"""

import asyncio
from services.brain import BrainPersistence
from services.living_docs import TeachingCollector

async def main(dry_run: bool = False) -> None:
    collector = TeachingCollector()
    teachings = collector.collect_all()

    print(f"Found {len(teachings)} teaching moments")

    if dry_run:
        for t in teachings[:10]:
            print(f"  [{t.severity}] {t.source_module}::{t.source_symbol}")
            print(f"     {t.insight[:60]}...")
        print(f"  ... and {len(teachings) - 10} more")
        return

    brain = await BrainPersistence.create()
    new_count = 0
    dup_count = 0

    for t in teachings:
        result = await brain.crystallize_teaching(
            insight=t.insight,
            severity=t.severity,
            source_module=t.source_module,
            source_symbol=t.source_symbol,
            evidence=t.evidence,
        )
        if result.is_new:
            new_count += 1
        else:
            dup_count += 1

    print(f"✅ Crystallized {new_count} new, {dup_count} already existed")
```

**Exit Criteria:**
- [ ] Script runs without error
- [ ] `--dry-run` shows preview
- [ ] All ~165 teaching moments crystallized
- [ ] Idempotent: re-run creates no duplicates

#### Task 2B.2: CLI Command `kg docs extract --crystallize`

**File:** `impl/claude/protocols/cli/handlers/docs.py` (modify)

Add `--crystallize` flag to `_handle_extract()`:

```python
async def _handle_extract(args: Namespace) -> None:
    """Extract teaching moments from codebase."""
    collector = TeachingCollector()
    teachings = collector.collect_all()

    if args.crystallize:
        brain = await _get_brain()
        new_count = 0
        for t in teachings:
            result = await brain.crystallize_teaching(
                insight=t.insight,
                severity=t.severity,
                source_module=t.source_module,
                source_symbol=t.source_symbol,
                evidence=t.evidence,
            )
            if result.is_new:
                new_count += 1
        print(f"✅ Crystallized {new_count} new teaching moments to Brain")
    else:
        # Existing behavior: print to stdout
        for t in teachings:
            print(f"[{t.severity}] {t.source_module}::{t.source_symbol}")
            print(f"  {t.insight}")
```

**Exit Criteria:**
- [ ] `kg docs extract` works (no regression)
- [ ] `kg docs extract --crystallize` persists to Brain
- [ ] Test coverage for crystallize path

---

### Phase 3: Extinction Protocol (1 session)

**Goal:** Enable graceful code deletion with wisdom preservation.

#### Task 3.1: `prepare_extinction()` Method

**File:** `impl/claude/services/brain/persistence.py` (extend)

```python
async def prepare_extinction(
    self,
    reason: str,
    commit: str,
    deleted_paths: list[str],
    decision_doc: str | None = None,
    successor_map: dict[str, str | None] | None = None,
) -> ExtinctionResult:
    """
    Prepare wisdom preservation before mass deletion.

    AGENTESE: self.memory.extinction.prepare

    The Extinction Law: Before deleting code, crystallize
    its teaching and mark as extinct.

    Args:
        reason: Why the deletion happened (e.g., "Crown Jewel Cleanup - AD-009")
        commit: Git SHA of the deletion commit
        deleted_paths: Paths being deleted (e.g., ["services/town/", "services/park/"])
        decision_doc: Reference to decision doc (optional)
        successor_map: Mapping of old → new paths (optional)

    Returns:
        ExtinctionResult with event_id, affected_count, preserved_count

    Teaching:
        gotcha: deleted_paths uses filesystem paths but source_module uses dots.
                Convert "services/town/" → "services.town" for matching.
                (Evidence: this implementation)
    """
    async with self.table.session_factory() as session:
        # Create ExtinctionEvent
        event_id = f"ext-{commit[:8]}-{int(datetime.now().timestamp())}"
        event = ExtinctionEvent(
            id=event_id,
            reason=reason,
            decision_doc=decision_doc,
            commit=commit,
            deleted_paths=deleted_paths,
            successor_map=successor_map or {},
        )
        session.add(event)

        # Convert paths to module prefixes
        module_prefixes = [
            p.rstrip("/").replace("/", ".") for p in deleted_paths
        ]

        # Find affected teaching crystals
        affected_crystals = []
        for prefix in module_prefixes:
            crystals = await self.get_teaching_by_module(prefix, include_extinct=False)
            affected_crystals.extend(crystals)

        # Mark as extinct and link to event
        preserved_count = 0
        for crystal in affected_crystals:
            crystal.died_at = datetime.now()
            # Set successor if provided
            if successor_map:
                for old_path, new_path in successor_map.items():
                    if crystal.source_module.startswith(old_path.replace("/", ".")):
                        crystal.successor_module = new_path

            # Create join record
            link = ExtinctionTeaching(
                extinction_id=event_id,
                teaching_id=crystal.id,
            )
            session.add(link)
            preserved_count += 1

        await session.commit()

        return ExtinctionResult(
            event_id=event_id,
            reason=reason,
            affected_count=len(affected_crystals),
            preserved_count=preserved_count,
        )
```

**Exit Criteria:**
- [ ] Method implemented with full docstring
- [ ] Path → module conversion works
- [ ] Teaching crystals marked with `died_at`
- [ ] `ExtinctionTeaching` links created
- [ ] Tests for happy path, edge cases

#### Task 3.2: Record 2025-12-21 Crown Jewel Cleanup

**File:** `impl/claude/scripts/record_crown_jewel_extinction.py`

One-time script to capture the cleanup that already happened:

```python
"""
Record the 2025-12-21 Crown Jewel Cleanup as an ExtinctionEvent.

Run once:
    uv run python scripts/record_crown_jewel_extinction.py
"""

CROWN_JEWEL_CLEANUP = {
    "reason": "Crown Jewel Cleanup - AD-009 Metaphysical Fullstack",
    "commit": "12209627",  # refactor: Remove world.emergence route, node, and frontend
    "decision_doc": "spec/principles/decisions/AD-009-metaphysical-fullstack.md",
    "deleted_paths": [
        "services/town/",
        "services/park/",
        "services/gestalt/",
        "services/forge/",
        "services/chat/",
        "services/archaeology/",
        "services/coalition/",
        "services/muse/",
        "services/gardener/",
    ],
    "successor_map": {
        "services/town": None,           # Concept removed
        "services/park": None,           # Concept removed
        "services/gestalt": None,        # Concept removed
        "services/forge": None,          # Concept removed
        "services/chat": "services.brain.conversation",
        "services/archaeology": "services.living_docs.temporal",
        "services/coalition": None,      # Concept removed
        "services/muse": None,           # Concept removed
        "services/gardener": "protocols.ashc",
    },
}
```

**Exit Criteria:**
- [ ] Script runs successfully
- [ ] ExtinctionEvent created with correct metadata
- [ ] All affected teaching crystals marked extinct
- [ ] `kg witness` can query the extinction event

#### Task 3.3: CLI Command `kg brain extinct`

**File:** `impl/claude/protocols/cli/handlers/brain.py` (modify or create)

```bash
kg brain extinct prepare \
    --reason "Removing X module" \
    --commit abc123 \
    --paths services/x/,services/y/ \
    --successor-map "x:z,y:null"

kg brain extinct list                  # List extinction events
kg brain extinct show ext-abc123       # Show details
```

**Exit Criteria:**
- [ ] `prepare` command creates extinction event
- [ ] `list` shows all extinction events
- [ ] `show` displays details including affected teaching

---

### Phase 4: Ghost Hydration (1-2 sessions)

**Goal:** Surface ancestral wisdom during hydration.

#### Task 4.1: `get_extinct_wisdom()` Method

**File:** `impl/claude/services/brain/persistence.py` (extend)

```python
async def get_extinct_wisdom(
    self,
    keywords: list[str] | None = None,
    module_prefix: str | None = None,
) -> list[GhostWisdom]:
    """
    Get wisdom from deleted code (ancestral teaching).

    AGENTESE: void.extinct.wisdom

    Args:
        keywords: Search for keywords in insights
        module_prefix: Filter by former module location

    Returns:
        List of GhostWisdom with teaching + extinction context
    """
    async with self.table.session_factory() as session:
        stmt = (
            select(TeachingCrystal, ExtinctionEvent)
            .join(ExtinctionTeaching)
            .join(ExtinctionEvent)
            .where(TeachingCrystal.died_at.isnot(None))
        )

        if module_prefix:
            stmt = stmt.where(
                TeachingCrystal.source_module.startswith(module_prefix)
            )

        result = await session.execute(stmt)

        ghosts = []
        for teaching, event in result:
            # Keyword filtering (if specified)
            if keywords:
                if not any(kw.lower() in teaching.insight.lower() for kw in keywords):
                    continue

            ghosts.append(GhostWisdom(
                teaching=teaching,
                extinction_event=event,
                successor=teaching.successor_module,
            ))

        return ghosts
```

**Exit Criteria:**
- [ ] Keyword search works
- [ ] Module prefix filtering works
- [ ] Returns extinction context with teaching

#### Task 4.2: `hydrate_with_ghosts()` in Living Docs

**File:** `impl/claude/services/living_docs/hydrator.py` (extend)

```python
async def hydrate_with_ghosts(
    self,
    task: str,
    brain: BrainPersistence,
) -> HydrationContext:
    """
    Hydrate context including ancestral wisdom.

    When a task mentions extinct modules, surface their
    preserved teaching as "ghosts."
    """
    # Regular hydration
    context = await self.hydrate(task)

    # Extract keywords from task
    keywords = self._extract_keywords(task)

    # Check for ghost matches
    ghosts = await brain.get_extinct_wisdom(keywords=keywords)

    if ghosts:
        context.ancestral_wisdom = ghosts
        context.extinct_modules = list(set(
            g.teaching.source_module for g in ghosts
        ))

    return context
```

**Markdown Output:**
```markdown
## ⚰️ Ancestral Wisdom (From Deleted Code)

These modules no longer exist but their lessons persist:

### services.town.dialogue_service
**Reason for deletion:** Crown Jewel Cleanup - AD-009
**Replaced by:** None (concept removed)

- **DialogueService.process_turn** [warning]:
  Always validate turn order before processing. Out-of-order turns
  cause state corruption that's hard to debug.
  (Evidence: test_dialogue.py::test_turn_order_validation)
```

**Exit Criteria:**
- [ ] Ghost section appears when relevant
- [ ] Keywords from task trigger ghost lookup
- [ ] Successor mapping shown when available

#### Task 4.3: AGENTESE Nodes

**File:** `impl/claude/protocols/agentese/contexts/void_extinct.py` (new)

```python
@node(
    path="void.extinct",
    category="void",
    summary="Ancestral wisdom from deleted code",
)
class ExtinctNode:
    """
    Access wisdom preserved from deleted code.

    void.* = The Accursed Share (entropy, deletion, gratitude)
    Extinction events live here because deletion is
    part of the codebase lifecycle.
    """

    def __init__(self, brain: BrainPersistence):
        self.brain = brain

    @command
    async def list(self) -> list[ExtinctionSummary]:
        """List all extinction events."""
        ...

    @command
    async def wisdom(self, path: str) -> list[GhostWisdom]:
        """Get preserved teaching from a deleted module."""
        return await self.brain.get_extinct_wisdom(module_prefix=path)

    @command
    async def show(self, event_id: str) -> ExtinctionEvent:
        """Show details of an extinction event."""
        ...
```

**Exit Criteria:**
- [ ] `void.extinct.list` returns extinction events
- [ ] `void.extinct.wisdom services.town` returns teaching
- [ ] `void.extinct.show ext-abc123` shows details
- [ ] CLI projection works: `kg void.extinct.list`

#### Task 4.4: Wire to `/hydrate` Skill

**File:** `.claude/commands/hydrate.md` (modify)

Update the hydrate skill to call `hydrate_with_ghosts()` and display ghost section when relevant.

**Exit Criteria:**
- [ ] `/hydrate "town dialogue"` shows ancestral wisdom
- [ ] Ghost section only appears when matches found
- [ ] Successor mappings displayed clearly

---

## Testing Requirements

### Unit Tests (per phase)

| Phase | Tests | File |
|-------|-------|------|
| 2B | 8 | `services/brain/_tests/test_crystallization.py` (extend) |
| 3 | 12 | `services/brain/_tests/test_extinction.py` (new) |
| 4 | 15 | `services/living_docs/_tests/test_ghost_hydration.py` (new) |

### Integration Tests

```bash
# Full flow test
kg docs extract --crystallize        # Crystallize all
kg brain extinct list                # Should show Crown Jewel Cleanup
kg docs hydrate "town dialogue"      # Should show ghost section
```

---

## Verification Commands

```bash
# Phase 2B: Bootstrap
uv run python scripts/bootstrap_teaching_crystals.py --dry-run
uv run python scripts/bootstrap_teaching_crystals.py
kg docs extract --crystallize

# Phase 3: Extinction
uv run python scripts/record_crown_jewel_extinction.py
kg brain extinct list
kg brain extinct show ext-12209627-*

# Phase 4: Ghost Hydration
kg void.extinct.list
kg void.extinct.wisdom services.town
kg docs hydrate "town dialogue"

# Full test suite
cd impl/claude && uv run pytest services/brain/_tests/ -q
cd impl/claude && uv run pytest services/living_docs/_tests/ -q
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Correct Pattern |
|--------------|-----------------|
| Storing path as-is | Convert filesystem path → module path |
| Silent failures | Fail loudly if crystallization fails |
| Duplicate crystals | Use deterministic ID from (module, symbol, insight_hash) |
| Ghost noise | Only show ghosts when task keywords match |
| Lost successor | Always record successor_map, even if None |

---

## Principles Alignment

| Principle | How This Plan Aligns |
|-----------|---------------------|
| **Tasteful** | Minimal—only what's needed to preserve wisdom |
| **Curated** | Not all code is teaching; only gotchas crystallize |
| **Ethical** | Wisdom belongs to the codebase, not individuals |
| **Joy-Inducing** | Ghost hydration is delightful surprise |
| **Composable** | `void.extinct.*` composes with other AGENTESE |
| **Heterarchical** | Teaching crystals can become Brain knowledge |
| **Generative** | This plan derives from spec + principles |

---

## Files to Create

```
impl/claude/scripts/bootstrap_teaching_crystals.py
impl/claude/scripts/record_crown_jewel_extinction.py
impl/claude/services/brain/_tests/test_extinction.py
impl/claude/services/living_docs/_tests/test_ghost_hydration.py
impl/claude/protocols/agentese/contexts/void_extinct.py
```

## Files to Modify

```
impl/claude/services/brain/persistence.py       # prepare_extinction, get_extinct_wisdom
impl/claude/services/living_docs/hydrator.py   # hydrate_with_ghosts
impl/claude/protocols/cli/handlers/docs.py      # --crystallize flag
impl/claude/protocols/cli/handlers/brain.py     # extinct subcommand
.claude/commands/hydrate.md                     # Ghost section
```

---

## Session Estimates

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| 2B: Bootstrap & CLI | 1 session | None |
| 3: Extinction Protocol | 1 session | Phase 2B |
| 4: Ghost Hydration | 1-2 sessions | Phase 3 |
| **Total** | **3-4 sessions** | |

---

## Success Criteria

| Criterion | Verification |
|-----------|--------------|
| All ~165 teaching crystallized | `kg brain teaching count` ≥ 165 |
| Crown Jewel Cleanup recorded | `kg brain extinct show ext-12209627-*` |
| Ghost hydration works | `/hydrate "town"` shows ancestral wisdom |
| AGENTESE nodes functional | `kg void.extinct.list` returns events |
| No teaching lost on deletion | Deletion flow includes `prepare_extinction()` |

---

*"The ancestors speak through the ghosts. Listen."*

---

**Filed:** 2025-12-22
**Voice Anchor:** *"Don't waste good work, like you wouldn't waste food."*
