# D-gent Memory: self.memory.* Implementation

> *"Memory is not storage. Memory is selection."*

**AGENTESE Context**: `self.memory.*`
**Status**: Ghost Cache Done, Comonadic Memory Planned
**Principles**: Graceful Degradation, Accursed Share

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Ghost cache** | Local file-based cache for CLI resilience |
| **StateCrystal** | Checkpoint with linearity-aware compression |
| **TTL-based composting** | Unpinned crystals auto-expire (Accursed Share) |
| **Focus fragments** | PRESERVED regions survive compression verbatim |
| **Parent chain** | Crystals track parent for `duplicate()` lineage |

---

## Ghost Cache (✅ DONE)

The Ghost cache provides offline CLI capability:

```
~/.kgents/ghost/
├── status.json         # Last known cortex status
├── map.json            # Last known holoMap
├── agents/             # Per-agent state snapshots
│   └── _index.json
├── pheromones/
│   ├── active.json
│   └── by_type/
│       ├── WARNING.json
│       └── DREAM.json
├── proposals/
│   ├── pending.json
│   └── rejected.json
├── cluster/
│   └── status.json
└── _meta/
    ├── last_sync.txt
    └── stability_score.json
```

**Staleness levels**:
| Level | Age | Behavior |
|-------|-----|----------|
| FRESH | < threshold | Show live |
| STALE | < 2x threshold | Show with `[GHOST]` |
| REFUSE | > 2x threshold | Don't show (misleading) |

**Adaptive staleness** based on cluster stability:
```python
threshold = BASE_THRESHOLD * (1 + stability_score)
```

---

## State Crystals (📋 PLANNED)

```python
@dataclass
class StateCrystal:
    """
    Checkpoint with linearity-aware compression.

    AGENTESE: self.memory.crystallize
    """

    crystal_id: str
    agent: str
    timestamp: datetime

    # Core state (REQUIRED)
    task_state: TaskState
    working_memory: dict[str, Any]

    # Compressed history (DROPPABLE masked)
    history_summary: str
    summary_tokens: int

    # Focus fragments (PRESERVED: verbatim)
    focus_fragments: list[FocusFragment]
    focus_tokens: int

    # Comonadic structure
    parent_crystal: str | None
    branch_reason: str | None
    branch_depth: int = 0

    # Accursed Share lifecycle
    ttl: timedelta = timedelta(hours=24)
    pinned: bool = False

    def is_expired(self) -> bool:
        return not self.pinned and (datetime.now() - self.timestamp > self.ttl)

    def total_tokens(self) -> int:
        return self.summary_tokens + self.focus_tokens
```

---

## Focus Fragments

```python
@dataclass
class FocusFragment:
    """
    A preserved fragment with PRESERVED linearity.

    Focus fragments survive compression verbatim.
    They are marked via focus hints during crystallization.
    """

    hint: str                   # What triggered preservation
    content: str                # Verbatim content
    position: int               # Original position in history
    linearity: Linearity = Linearity.PRESERVED
```

**Focus hints examples**:
- `[FOCUS:decision]` → Preserve decision rationale
- `[FOCUS:error]` → Preserve error context
- User-injected focus → Preserve verbatim

---

## Crystallization Engine (📋 PLANNED)

```python
class CrystallizationEngine:
    """
    Creates State Crystals with linearity-aware compression.

    AGENTESE: self.memory.crystallize
    """

    async def crystallize(
        self,
        context: ContextWindow,
        focus_hints: list[str] | None = None,
        ttl: timedelta = timedelta(hours=24),
    ) -> StateCrystal:
        """
        Create a crystal from current context.

        Process:
        1. Mark linearity classes based on focus hints
        2. Extract PRESERVED fragments verbatim
        3. Compress DROPPABLE+REQUIRED via masking + summary
        4. Store with comonadic metadata
        """
        ...
```

---

## Crystal Reaper (📋 PLANNED)

```python
class CrystalReaper:
    """
    TTL-based crystal composting.

    AGENTESE: void.entropy.pour

    Unpinned crystals are composted after TTL.
    Pinned crystals (`cherished`) survive indefinitely.
    """

    async def reap(self) -> list[str]:
        """Compost expired crystals, return IDs."""
        expired = [c for c in self.crystals if c.is_expired()]
        for crystal in expired:
            await self.d_gent.delete_crystal(crystal.crystal_id)
        return [c.crystal_id for c in expired]
```

**Cherish operation**:
```python
# AGENTESE: self.memory.cherish
await logos.invoke("self.memory.cherish", crystal_id="abc123")
# → Sets pinned=True, survives reaping
```

---

## AGENTESE Path Registry

| Path | Operation | Description |
|------|-----------|-------------|
| `self.memory.crystallize` | Create checkpoint | Context → Crystal |
| `self.memory.resume` | Restore checkpoint | Crystal → Context |
| `self.memory.cherish` | Pin from reaping | Set pinned=True |
| `self.memory.manifest` | Get cached state | Ghost cache read |
| `self.memory.engram` | Persist state | Ghost cache write |
| `self.memory.compost` | Force expiration | Delete crystal |

---

## Integration with Ghost

The Ghost cache IS `self.memory` from the CLI perspective:

| Ghost Operation | AGENTESE Path | Description |
|-----------------|---------------|-------------|
| Write cache | `self.memory.engram` | Persist on successful invoke |
| Read cache | `self.memory.manifest` | Graceful degradation fallback |
| Cache miss | Transparent error | Clear messaging |
| Stale data | `[GHOST]` prefix | User knows data is old |

---

## Memory Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│ Hot Memory (ContextWindow)                              │
│   • Current session                                     │
│   • In-memory, fast                                     │
│   • Compressed via ContextProjector                     │
└───────────────────────────┬─────────────────────────────┘
                            │ crystallize
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Warm Memory (StateCrystals)                             │
│   • Recent checkpoints                                  │
│   • D-gent persistence (etcd/PVC)                       │
│   • TTL-based expiration                                │
└───────────────────────────┬─────────────────────────────┘
                            │ expire (unpinned)
                            ▼
┌─────────────────────────────────────────────────────────┐
│ Cold Memory (Ghost Cache)                               │
│   • CLI-local fallback                                  │
│   • ~/.kgents/ghost/                                    │
│   • Staleness-aware                                     │
└─────────────────────────────────────────────────────────┘
```

---

## Cross-References

- **Plans**: `self/stream.md` (ContextWindow), `void/entropy.md` (Composting)
- **Impl**: `protocols/cli/glass.py` (Ghost), `agents/d/` (D-gent)
- **Spec**: `spec/protocols/agentese.md`

---

*"What you forget defines you as much as what you remember."*
