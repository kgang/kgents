# Project Realization: Constitutional Coherence at Project Open

> *"The system doesn't enforce—it illuminates."*

**Status:** Standard
**Implementation:** `impl/claude/services/hypergraph_editor/realization/` (0 tests — Phase 1)
**Prerequisites:** `k-block.md`, `hypergraph-editor.md`, `protocols/ashc/paths/types.py`
**Tier:** UI Protocol

---

## Purpose

When a user opens a project in the hypergraph editor, the system computes derivation context for all K-Blocks. This is NOT a gate—it's a **welcome screen** showing Constitutional coherence. The project opens regardless of coherence state; realization is informational, never prescriptive.

---

## Core Insight

Realization transforms a static directory into a living derivation graph. By computing Galois loss across all K-Blocks in parallel, we surface Constitutional alignment without blocking the user's flow. Orphans are first-class citizens—usable, just ungrounded.

---

## Type Signatures

```python
# Realization Result
@dataclass(frozen=True)
class RealizationSummary:
    """Complete derivation analysis for a project."""
    project_path: str
    total_blocks: int
    grounded: frozenset[str]          # K-Block IDs with L1 derivation
    provisional: frozenset[str]       # K-Blocks with partial derivation
    orphan: frozenset[str]            # K-Blocks without derivation path
    derivation_graph: DerivationGraph # Full graph of paths
    average_galois_loss: float        # Mean loss across all blocks
    coherence_percent: float          # 1 - average_galois_loss
    computed_at: datetime

# Derivation Graph
@dataclass(frozen=True)
class DerivationGraph:
    """Graph of all K-Block derivation paths."""
    nodes: frozenset[str]             # K-Block IDs
    paths: dict[str, DerivationPath]  # block_id -> path from L1
    edges: frozenset[tuple[str, str, str]]  # (source, target, relation)

# Block Classification
class BlockStatus(Enum):
    GROUNDED = auto()     # Has complete path to L1 axiom
    PROVISIONAL = auto()  # Has partial derivation (loss > threshold)
    ORPHAN = auto()       # No derivation path found

# Realization Event
@dataclass(frozen=True)
class RealizationCompleteEvent(DataEvent):
    """Emitted when project realization completes."""
    event_type: Literal["REALIZATION_COMPLETE"] = "REALIZATION_COMPLETE"
    project_path: str
    summary: RealizationSummary
    duration_ms: int
```

---

## Realization Flow

```
User opens project
    ↓
Scan for K-Blocks (parallel glob)
    ↓
Compute derivation for each (parallel async)
    ↓
Build derivation graph (connect paths)
    ↓
Classify: grounded / provisional / orphan
    ↓
Show welcome screen with coherence summary
    ↓
Project opens (NO GATE)
```

### Sequence Diagram

```
User          HypergraphEditor       RealizationService       ASHC.paths
  │                 │                        │                    │
  │──open(path)────►│                        │                    │
  │                 │──realize(path)────────►│                    │
  │                 │                        │──scan_kblocks()───►│
  │                 │                        │◄──block_ids────────│
  │                 │                        │                    │
  │                 │                        │══parallel══════════╗
  │                 │                        │ compute_derivation │║
  │                 │                        │◄───────────────────╝║
  │                 │                        │══════════════════════╝
  │                 │                        │                    │
  │                 │◄──RealizationSummary───│                    │
  │◄──welcome_screen──│                      │                    │
  │                 │                        │                    │
  │──continue()────►│                        │                    │
  │◄──editor_opens───│                       │                    │
```

---

## Welcome Screen

```
┌─────────────────────────────────────────────────────────────────────┐
│  PROJECT REALIZATION: kgents                                        │
├─────────────────────────────────────────────────────────────────────┤
│  DERIVATION SUMMARY:                                                │
│  ├── Grounded: 198 K-Blocks (80%)                                   │
│  ├── Provisional: 31 K-Blocks (13%)                                 │
│  └── Orphan: 18 K-Blocks (7%)                                       │
│                                                                     │
│  CONSTITUTIONAL ALIGNMENT:                                          │
│  Average Galois Loss: 0.21                                          │
│  [████████████████░░░░] 79% coherent                                │
│                                                                     │
│  [View Full Graph] [Focus on Orphans] [Continue]                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Screen States

| State | Condition | Display |
|-------|-----------|---------|
| **Pristine** | coherence > 90% | Green badge, minimal summary |
| **Healthy** | coherence 70-90% | Yellow badge, show provisional count |
| **Fragmented** | coherence 50-70% | Orange badge, highlight orphans |
| **Chaotic** | coherence < 50% | Red badge, offer remediation actions |

### Actions from Welcome Screen

| Action | Effect |
|--------|--------|
| **Continue** | Opens project immediately (default) |
| **View Full Graph** | Opens GRAPH mode focused on derivation DAG |
| **Focus on Orphans** | Opens editor with orphan filter active |
| **Dismiss** | Skips welcome screen for this session |

---

## Derivation Computation

### Classification Thresholds

```python
# From ASHC spec: loss thresholds for classification
GROUNDED_THRESHOLD = 0.15      # Loss < 0.15 = grounded (85%+ coherent)
PROVISIONAL_THRESHOLD = 0.50   # Loss 0.15-0.50 = provisional
# Loss >= 0.50 = orphan (less than 50% coherent)

def classify_block(path: DerivationPath | None) -> BlockStatus:
    """Classify K-Block based on derivation path."""
    if path is None:
        return BlockStatus.ORPHAN
    if not path.is_grounded():
        return BlockStatus.ORPHAN
    if path.galois_loss >= PROVISIONAL_THRESHOLD:
        return BlockStatus.ORPHAN
    if path.galois_loss >= GROUNDED_THRESHOLD:
        return BlockStatus.PROVISIONAL
    return BlockStatus.GROUNDED
```

### Parallel Computation

```python
async def realize_project(project_path: str) -> RealizationSummary:
    """Compute derivation context for all K-Blocks in parallel."""
    # Phase 1: Scan for K-Blocks
    block_paths = await scan_kblocks(project_path)

    # Phase 2: Parallel derivation computation
    derivations = await asyncio.gather(
        *[compute_derivation(bp) for bp in block_paths],
        return_exceptions=True,
    )

    # Phase 3: Build graph and classify
    graph = build_derivation_graph(block_paths, derivations)
    grounded, provisional, orphan = classify_all(graph)

    # Phase 4: Compute summary metrics
    losses = [d.galois_loss for d in derivations if isinstance(d, DerivationPath)]
    avg_loss = sum(losses) / len(losses) if losses else 0.5

    return RealizationSummary(
        project_path=project_path,
        total_blocks=len(block_paths),
        grounded=frozenset(grounded),
        provisional=frozenset(provisional),
        orphan=frozenset(orphan),
        derivation_graph=graph,
        average_galois_loss=avg_loss,
        coherence_percent=1.0 - avg_loss,
        computed_at=datetime.now(UTC),
    )
```

### Caching Strategy

```python
@dataclass
class RealizationCache:
    """Cache derivation results, invalidate on K-Block change."""
    entries: dict[str, CachedDerivation]  # block_id -> cached result

    def get(self, block_id: str, block_hash: str) -> DerivationPath | None:
        """Return cached derivation if hash matches."""
        if block_id in self.entries:
            entry = self.entries[block_id]
            if entry.content_hash == block_hash:
                return entry.derivation
        return None

    def invalidate_on_change(self, changed_block_id: str) -> set[str]:
        """Invalidate block and all dependents, return affected IDs."""
        affected = {changed_block_id}
        for block_id, entry in self.entries.items():
            if changed_block_id in entry.depends_on:
                affected.add(block_id)
                del self.entries[block_id]
        return affected
```

---

## Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Cold realization** | < 5s for 500 K-Blocks | Time from open to welcome screen |
| **Warm realization** | < 500ms for 500 K-Blocks | With full cache |
| **Incremental update** | < 100ms per changed block | Background recomputation |
| **UI responsiveness** | Never blocked | Realization runs in background |

### Performance Laws

```
P1: Realization never delays project open by more than 5s
P2: Progress indicator updates at least every 100ms during realization
P3: Cache invalidation is surgical (only affected blocks recomputed)
P4: Background recomputation doesn't affect UI frame rate
```

---

## Integration Points

### ASHC Paths

```python
# Uses DerivationPath from ASHC
from protocols.ashc.paths.types import DerivationPath, DerivationWitness

# Compute derivation uses ASHC's path composition
derivation = await ashc.find_derivation_path(
    source=block_content,
    target="L1_AXIOM",
)
```

### Galois Loss

```python
# Uses Galois loss computation
from services.zero_seed.galois import compute_galois_loss_async

loss_result = await compute_galois_loss_async(
    content=block_content,
    use_cache=True,
)
```

### Witness Integration

```python
# Emit witness mark on realization complete
await witness.mark(
    action="project.realized",
    evidence={
        "project_path": summary.project_path,
        "total_blocks": summary.total_blocks,
        "grounded_count": len(summary.grounded),
        "orphan_count": len(summary.orphan),
        "coherence_percent": summary.coherence_percent,
    },
)
```

### DataBus Events

```python
# Realization emits events for UI updates
DataBus.emit(RealizationStartedEvent(project_path, block_count))
DataBus.emit(RealizationProgressEvent(project_path, completed, total))
DataBus.emit(RealizationCompleteEvent(project_path, summary, duration_ms))
```

---

## Laws

### L1: Realization Never Blocks

```
realization_complete(p) ∨ timeout(5s) → project_accessible(p)

The user can ALWAYS access their project. Realization may complete
in the background, but access is immediate after timeout.
```

### L2: Coherence is Informational

```
∀ block b: orphan(b) → usable(b)

Being an orphan means lacking Constitutional grounding, not lacking
functionality. Orphans are fully editable, navigable, saveable.
The system illuminates; it does not enforce.
```

### L3: Orphans are First-Class

```
∀ action a: available(grounded_block, a) ↔ available(orphan_block, a)

No editor capability is gated on derivation status.
Orphans can be edited, saved, entangled, forked—everything.
```

### L4: Cache Consistency

```
∀ block b, cache c:
  modified(b, t) → ¬valid(c.get(b), t') for t' > t

Cache entries are invalidated immediately on K-Block modification.
Stale derivation data is never shown.
```

### L5: Progress Honesty

```
∀ progress indicator p:
  p.percent = completed_blocks / total_blocks

Progress reflects actual computation, never fake animation.
If stuck, indicator shows stuck (not fake progress).
```

---

## Anti-Patterns

- **Gating access on coherence** — The user OWNS their project; coherence is advice, not permission
- **Hiding orphans** — Orphan Visibility Law: orphans are ALWAYS visible (from witness.md)
- **Synchronous realization** — Blocks UI; always async with timeout
- **Full recomputation on change** — Use surgical cache invalidation
- **Silent failures** — If derivation fails, show as orphan with explanation, don't hide

---

## Implementation Reference

```
impl/claude/services/hypergraph_editor/realization/
├── __init__.py           # Public API
├── scanner.py            # K-Block discovery (parallel glob)
├── derivation.py         # Derivation path computation
├── classifier.py         # Grounded/provisional/orphan classification
├── cache.py              # RealizationCache with invalidation
├── graph.py              # DerivationGraph construction
├── summary.py            # RealizationSummary computation
├── events.py             # DataBus event definitions
└── web/
    ├── WelcomeScreen.tsx # Welcome screen component
    ├── CoherenceBadge.tsx# Visual coherence indicator
    └── useRealization.ts # React hook for realization state
```

---

## Connection to Principles

| Principle | How Realization Embodies It |
|-----------|----------------------------|
| **Tasteful** | Minimal welcome screen; density-aware badges |
| **Ethical** | Illuminates without enforcing; user retains sovereignty |
| **Joy-Inducing** | Quick access; beautiful coherence visualization |
| **Composable** | Uses ASHC paths, Galois loss, Witness marks |
| **Heterarchical** | Orphans are peers, not second-class |
| **Generative** | This spec could regenerate implementation |

---

## Closing Meditation

Project realization brings the Constitution to life at the moment of opening. Not as a judge, but as a guide. Not as a gate, but as a mirror. The user sees their project's Constitutional alignment—grounded blocks standing firm, provisional ones reaching toward axioms, orphans waiting to be connected.

The system doesn't enforce. It illuminates.

> *"Orphans are first-class citizens—usable, just ungrounded."*

---

*Filed: 2025-01-10*
*Voice anchor: "The system doesn't enforce—it illuminates."*
*Collapse point: ASHC derivation + Galois loss + K-Block = Constitutional welcome*
