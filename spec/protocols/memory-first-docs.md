# Memory-First Documentation

**Status:** Emerging Standard
**Implementation:** `impl/claude/services/living_docs/` + `impl/claude/services/brain/`

> *"Teaching moments don't die; they become ancestors."*

---

## Purpose

Documentation systems suffer from amnesia—they know only the present. When code is deleted, its wisdom dies. Memory-First Documentation treats the codebase as a living organism with institutional memory.

**Heritage**: This spec synthesizes insights from:
- [Institutional Memory](https://en.wikipedia.org/wiki/Institutional_memory): Organizations lose knowledge when people leave—codebases lose knowledge when code is deleted
- [Architecture Decision Records](https://adr.github.io/): ADRs are marked "superseded" not deleted—teaching moments deserve the same
- [Temporal Knowledge Graphs](https://arxiv.org/abs/2501.13956) (Zep/Graphiti): Knowledge graphs with explicit timestamps for when relationships started, evolved, or ended
- [Code Archaeology](https://jfire.io/blog/2012/03/07/code-archaeology-with-git/): Git history preserves *what* changed, but not *why* it mattered

---

## Core Insight

Brain is already the ground truth for memory (crystals, semantic search, healing). Living Docs should become a **projection of Brain's memory**, not a separate extraction system. Documentation emerges from Brain's understanding, including understanding of what no longer exists.

```
LivingDocs = Brain.project(teaching_crystals)

hydrate(task) =
  Brain.semantic_search(task)
  >> filter_teaching
  >> check_extinctions
  >> annotate_successors
  >> project(observer)
```

---

## Type Signatures

### TeachingCrystal (The Persistent Wisdom)

```python
class TeachingCrystal(TimestampMixin, Base):
    """
    A teaching moment crystallized in Brain.

    Persists beyond the death of source code.
    Links to successors when source is deleted.
    """
    __tablename__ = "brain_teaching_crystals"

    id: Mapped[str]  # Primary key

    # The teaching
    insight: Mapped[str]  # The gotcha
    severity: Mapped[str]  # "info" | "warning" | "critical"
    evidence: Mapped[str | None]  # test_file.py::test_name

    # Provenance
    source_module: Mapped[str]  # "services.town.dialogue_service"
    source_symbol: Mapped[str]  # "DialogueService.process_turn"
    source_commit: Mapped[str | None]  # Git SHA where learned

    # Temporal
    born_at: Mapped[datetime]  # When first captured
    died_at: Mapped[datetime | None]  # When source was deleted

    # Lineage (Successor Chain)
    successor_module: Mapped[str | None]  # What replaced the source
    successor_symbol: Mapped[str | None]  # Symbol in successor
    applies_to: Mapped[list[str]]  # AGENTESE paths still relevant

    # Link to full crystal content
    crystal_id: Mapped[str | None]  # FK to brain_crystals
```

### ExtinctionEvent (The Planned Departure)

```python
class ExtinctionEvent(TimestampMixin, Base):
    """
    A mass deletion event with salvaged wisdom.

    Records architectural decisions that removed code
    while preserving the teaching moments learned.
    """
    __tablename__ = "brain_extinction_events"

    id: Mapped[str]  # Primary key

    # What happened
    reason: Mapped[str]  # "Crown Jewel Cleanup - AD-009"
    decision_doc: Mapped[str | None]  # "spec/decisions/AD-009.md"
    commit: Mapped[str]  # Git SHA of deletion

    # What was deleted
    deleted_paths: Mapped[list[str]]  # ["services/town/", ...]

    # Successor mapping (DAG)
    successor_map: Mapped[dict[str, str]]  # {"town": "brain", ...}
```

### HydrationContext (The Ghost-Aware Query)

```python
@dataclass
class HydrationContext:
    """Context blob with extinction awareness."""

    task: str
    relevant_teaching: list[TeachingResult]
    related_modules: list[str]
    voice_anchors: list[str]

    # Semantic (from Brain vectors)
    semantic_teaching: list[ScoredTeachingResult]
    has_semantic: bool

    # Extinction awareness (Memory-First)
    extinct_modules: list[str]  # Modules referenced that no longer exist
    ancestral_wisdom: list[TeachingCrystal]  # Teaching from extinct code
    successor_map: dict[str, str]  # What replaced what
```

---

## Laws

### The Persistence Law

```
For all teaching moments T in source code:
  crystallize(T) → TeachingCrystal in Brain

Teaching moments extracted from code MUST be crystallized in Brain.
```

### The Extinction Law

```
For all mass deletions D affecting paths P:
  prepare_extinction(P) → ExtinctionEvent

Mass deletions MUST be preceded by extinction preparation.
Teaching moments from deleted code are marked died_at but NOT deleted.
```

### The Ghost Hydration Law

```
For all tasks T referencing extinct module M:
  hydrate(T) → context with M's ancestral wisdom

Hydration MUST surface wisdom from extinct code when relevant.
```

### The Successor Chain Law

```
Successor mappings form a directed acyclic graph:
  ∀ M: Module, successor_chain(M) is finite ∧ acyclic

If M₁ → M₂ → M₃, then:
  wisdom(M₁) applies_to wisdom(M₂) applies_to wisdom(M₃)
```

---

## AGENTESE Integration

```
# Extinction archaeology
void.extinct.list                    → list[ExtinctionEvent]
void.extinct.show(path)              → ExtinctionDetail
void.extinct.wisdom(path)            → list[TeachingCrystal]
void.extinct.successors(path)        → dict[str, str]

# Temporal documentation
time.docs.at(commit)                 → HydrationContext
time.docs.lineage(module)            → EvolutionHistory
time.docs.diff(before, after)        → DocsDiff

# Ancestral wisdom
concept.docs.ancestors               → list[TeachingCrystal]

# Crystal persistence
self.memory.crystallize_teaching     → CrystallizeResponse
self.memory.prepare_extinction       → ExtinctionEvent
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| **Deletion without extinction protocol** | Deleting code without running `prepare_extinction()`. Teaching moments lost forever. |
| **Hardcoded categories** | Listing paths in code instead of discovering from Brain topology. Categories should emerge, not be declared. |
| **Present-tense only hydration** | Ignoring extinction archive when hydrating context. Users get "module not found" instead of ancestral wisdom. |
| **Orphaned successors** | Successor mappings pointing to non-existent modules. Chains must be valid. |
| **Teaching without crystal** | Extracting teaching moments but not persisting to Brain. If Brain doesn't know it, we don't know it. |

---

## Connection to Temporal Knowledge Graphs

Memory-First Documentation implements the temporal knowledge graph pattern:

| TKG Concept | Memory-First Equivalent |
|-------------|------------------------|
| Time-stamped edges | `born_at`, `died_at` on TeachingCrystal |
| Event-driven updates | ExtinctionEvent captures deletion events |
| Decay policies | `died_at` marks inactive but preserved wisdom |
| Provenance tracking | `source_commit`, `evidence` fields |
| Successor relationships | `successor_module`, `successor_map` |

The key insight from Zep/Graphiti: *"A TKG doesn't just tell you that knowledge exists. It tells you when it was valid, and what superseded it."*

---

## Connection to ADRs

Architecture Decision Records handle decisions; Memory-First handles code:

| ADR Pattern | Memory-First Pattern |
|-------------|---------------------|
| ADR marked "superseded" | TeachingCrystal.died_at + successor_module |
| ADR immutability | TeachingCrystals never deleted, only marked |
| ADR links to successors | ExtinctionEvent.successor_map |
| ADR preserves context | TeachingCrystal.insight preserves the *why* |

*"Reading code will only describe the way the world is now, not what it was in the past."* — ADR rationale that applies equally to teaching moments.

---

## The Soil Remembers

The final insight: **the soil remembers what the garden forgets**.

When we prune the garden (delete code), the wisdom learned from that code doesn't disappear. It becomes compost—ancestral knowledge that enriches the soil for future growth.

```
Current Hydration:
  context = find_relevant_teaching(task)

Memory-First Hydration:
  context = find_relevant_teaching(task)
           + find_ancestral_wisdom(task)
           + find_successor_mapping(task)
```

The code dies. The wisdom lives.

---

*"The persona is a garden, not a museum. But the soil remembers."*

*Specified: 2025-12-21 | Memory-First Crystallization*
