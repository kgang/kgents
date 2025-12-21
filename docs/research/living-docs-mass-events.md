# Living Docs: Handling Mass Cleanup Events

> *Brainstorming how Living Docs could surface, track, and learn from mass architectural events like the Crown Jewel Cleanup of 2025-12-21*

---

## The Problem

We just deleted 450+ files across 18 Crown Jewels (Town, Park, Gestalt, Forge, Chat, Archaeology, etc.). The current Living Docs system:

1. **CATEGORIES hardcoded** — `generator.py` lists paths like `services/town/`, `services/gestalt/` that no longer exist
2. **No event awareness** — It extracts from what exists now, with no concept of "what just happened"
3. **Teaching moments orphaned** — Gotchas embedded in deleted files are gone forever
4. **No cleanup cascade** — The reference docs will silently emit empty sections or fail

---

## Brainstormed Solutions

### 1. **Extinction Events as First-Class Primitives**

```python
@dataclass
class ExtinctionEvent:
    """A mass deletion event with provenance."""
    timestamp: datetime
    reason: str  # "Crown Jewel Cleanup - AD-009 Collapse to Metabolic Foundation"
    deleted_paths: list[str]  # ["services/town/", "services/forge/", ...]
    preserved_teaching: list[TeachingMoment]  # Salvaged gotchas
    commit: str  # Git SHA
    decision_doc: str | None  # Link to spec/decision-XXX.md
```

**How it works:**
- Before deletion, run `kg docs extinct services/town/ --reason "..." --preserve-gotchas`
- This extracts all teaching moments, bundles them into an `ExtinctionEvent`
- Events are stored in `membrane.db` or a manifest file
- Generator can display "Deprecated" sections with salvaged wisdom

**Teaching moments don't die; they become archaeological artifacts.**

---

### 2. **Living Docs as Git Archaeology**

Current: Extract from working tree only.

Proposed: Living Docs has a "temporal mode" that understands git history.

```python
class TemporalHydrator:
    """Hydrate context from any point in history."""

    async def hydrate_from_commit(self, task: str, commit: str) -> HydrationContext:
        """Get context as of a specific commit."""
        # Check out that commit's docs in memory
        # Extract teaching moments that existed then
        # Diff against now to show what was lost/gained
```

**Use case:** When you're debugging why something broke, hydrate context from before/after the change to see what gotchas existed.

---

### 3. **Category Registry (Dynamic Discovery)**

Current: Hardcoded `CATEGORIES` list.

Proposed: Categories discovered from filesystem + registry.

```python
# In services/<jewel>/__init__.py
LIVING_DOCS_CATEGORY = CategoryConfig(
    name="Brain",
    description="Memory crystallization and vector storage.",
    deprecated=False,
)

# Or use AGENTESE node registration pattern
@node(
    "concept.docs.category",
    aspects=("living_docs",),
)
def brain_category():
    return CategoryConfig(...)
```

**On mass deletion:** Missing categories are automatically detected and handled gracefully, rather than silent failures.

---

### 4. **Pre-Deletion Hooks (Teaching Salvage)**

A hook that runs before `git rm` to preserve institutional memory:

```bash
# In .git/hooks/pre-commit or custom script
kg docs salvage services/town/ services/forge/ ...

# Output:
# 🏛️ Salvaged 47 teaching moments from 6 deleted jewels
# 📦 Archive: .extinct/2025-12-21-crown-jewel-cleanup.json
```

**Archive structure:**
```json
{
  "event": "crown-jewel-cleanup",
  "date": "2025-12-21",
  "teaching_moments": [
    {
      "symbol": "DialogueService.turn",
      "module": "services.town.dialogue_service",
      "insight": "Turns must complete within budget or they're forcibly truncated",
      "severity": "warning",
      "evidence": "test_dialogue_service.py::test_budget_enforcement"
    }
  ],
  "decision_link": "spec/decisions/AD-009.md"
}
```

---

### 5. **Hydration with Extinction Awareness**

When you ask "how does town work?", the hydrator should know Town is extinct and redirect:

```python
def hydrate(self, task: str) -> HydrationContext:
    # Check if task mentions extinct modules
    extinct_refs = self._find_extinct_references(task)

    if extinct_refs:
        # Return context explaining the extinction
        return HydrationContext(
            task=task,
            relevant_teaching=[],  # None from current codebase
            extinct_modules=extinct_refs,  # ["services.town"]
            successor_modules=["services.brain"],  # What replaced it
            archived_teaching=self._load_archived_teaching(extinct_refs),
        )
```

**Output in markdown:**
```markdown
## Extinct Modules Referenced

You mentioned `town` which was removed in the Crown Jewel Cleanup (2025-12-21).

### What Happened
Town, Park, and Gestalt were consolidated into Brain as part of AD-009.

### Archived Wisdom (Still Relevant)
- ⚠️ **DialogueService.turn**: Turns must complete within budget
- ℹ️ **CoalitionNode**: Agents can form temporary coalitions for shared goals

### Successor Patterns
See `services/brain/` for the metabolic foundation that replaced these.
```

---

### 6. **Continuous Integration Gate**

Add CI check that fails when docs reference non-existent modules:

```python
# In CI pipeline
def test_living_docs_coherence():
    generator = ReferenceGenerator()

    for category in CATEGORIES:
        for path in category.paths:
            full_path = BASE_PATH / path
            assert full_path.exists(), f"Category path missing: {path}"

    # Also check that generated docs don't have empty sections
    docs = generator.generate_all()
    assert "0 symbols" not in docs
```

---

### 7. **Deprecation as a First-Class State**

Instead of binary exists/deleted, modules can be deprecated:

```python
class ModuleStatus(Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"  # Still exists, but discouraged
    EXTINCT = "extinct"  # Deleted, but archived wisdom exists
    EXPERIMENTAL = "experimental"  # May not survive

@dataclass
class CategoryConfig:
    name: str
    paths: list[str]
    status: ModuleStatus = ModuleStatus.ACTIVE
    deprecated_at: datetime | None = None
    successor: str | None = None  # What to use instead
```

---

### 8. **Mass Event Notification Bus**

Living Docs subscribes to architectural events:

```python
class ArchitecturalEventBus:
    """Broadcast significant codebase events."""

    async def emit(self, event: ArchitecturalEvent):
        # Notify all subscribers
        for subscriber in self._subscribers:
            await subscriber.on_event(event)

class LivingDocsSubscriber:
    async def on_event(self, event: ArchitecturalEvent):
        if isinstance(event, MassDeletionEvent):
            # 1. Salvage teaching moments
            # 2. Update category registry
            # 3. Generate deprecation notices
            # 4. Update hydration redirects
```

---

## Recommended First Steps

1. **Quick Fix:** Update `CATEGORIES` to remove deleted paths (5 min)
2. **Short Term:** Add extinction manifest format + salvage script (1 day)
3. **Medium Term:** Dynamic category discovery from filesystem (1 week)
4. **Long Term:** Full temporal hydration with git archaeology (future)

---

## The Meta-Learning

*"This mass deletion event itself is a teaching moment that should be captured."*

The Living Docs system should be self-aware enough to recognize when it's been affected by a mass event and surface that to future developers. Otherwise, they'll wonder why references to Town exist in old commits but nothing documents what Town was.

**The wisdom:**
> gotcha: Mass deletions orphan teaching moments. Always run salvage before `git rm -r`.
> (Evidence: 2025-12-21-crown-jewel-cleanup where 450+ files were deleted without salvage)

---

*Brainstormed: 2025-12-21 | Post-Cleanup Reflection*
