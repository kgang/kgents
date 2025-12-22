# PLAN: Agent-as-Witness Phase 0

> *"Every action leaves a mark. The mark is the proof."*

**Status:** Ready for Execution
**Parallelizes with:** `PLAN-symmetric-supersession-phase0.md`
**Estimated effort:** 1-2 sessions
**Output:** Minimal witness infrastructure that records traces

---

## Goal

Build the **minimal kernel** of Agent-as-Witness: the ability to leave marks (traces) and retrieve them. Nothing fancy—just enough to prove the concept works.

---

## Success Criteria

```python
# After Phase 0, this works:

# 1. Create a mark
mark = await witness.mark(
    action="Refactored DI container",
    reasoning="Enable Crown Jewel pattern",
    principles=["composable", "generative"],
)

# 2. Mark is persisted
assert await witness.get(mark.id) == mark

# 3. Marks can be queried
recent = await witness.recent(limit=10)
assert mark in recent

# 4. AGENTESE path works
result = await logos.invoke("time.witness.mark", observer, action="Did a thing")
assert result.mark_id is not None
```

---

## Scope: What's IN

| Component | Description | Priority |
|-----------|-------------|----------|
| `Mark` dataclass | Immutable record of action + reasoning | P0 |
| `MarkStore` | D-gent persistence for marks | P0 |
| `time.witness.mark` | AGENTESE node for creating marks | P0 |
| `time.witness.recent` | Query recent marks | P0 |
| `time.witness.get` | Retrieve specific mark | P0 |
| Basic tests | Verify marks persist and retrieve | P0 |

## Scope: What's OUT (Future Phases)

| Component | Why Deferred |
|-----------|--------------|
| Walk (session streams) | Phase 1 |
| Playbook (orchestration) | Phase 2 |
| Stigmergic memory | Phase 2 |
| Causal graphs | Phase 3 |
| Proof generation | Phase 3 |
| LLM narrative synthesis | Phase 3 |

---

## Implementation Plan

### Step 1: Define Mark Dataclass

**File:** `impl/claude/services/witness/mark.py`

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import NewType
import uuid

MarkId = NewType("MarkId", str)

def new_mark_id() -> MarkId:
    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    short = uuid.uuid4().hex[:8]
    return MarkId(f"mark-{ts}-{short}")

@dataclass(frozen=True)
class Mark:
    """
    Atomic unit of witness. Every action leaves a mark.

    Marks are:
    - Immutable (frozen)
    - Minimal (only essential fields)
    - Self-describing (action + reasoning)
    """
    id: MarkId
    timestamp: datetime

    # What
    action: str                           # What was done

    # Why (optional but encouraged)
    reasoning: str | None = None          # Why this action
    principles: tuple[str, ...] = ()      # Which principles honored

    # Context (optional)
    session_id: str | None = None
    parent_id: MarkId | None = None       # For nested marks

    # Authorship
    author: str = "unknown"               # "kent", "claude", "k-gent"

def create_mark(
    action: str,
    *,
    reasoning: str | None = None,
    principles: list[str] | None = None,
    session_id: str | None = None,
    parent_id: MarkId | None = None,
    author: str = "unknown",
) -> Mark:
    """Factory for creating marks."""
    return Mark(
        id=new_mark_id(),
        timestamp=datetime.utcnow(),
        action=action,
        reasoning=reasoning,
        principles=tuple(principles or []),
        session_id=session_id,
        parent_id=parent_id,
        author=author,
    )
```

### Step 2: Create MarkStore (D-gent Persistence)

**File:** `impl/claude/services/witness/store.py`

```python
from dataclasses import dataclass
from typing import Protocol
from .mark import Mark, MarkId

class MarkStore(Protocol):
    """Protocol for mark persistence."""

    async def save(self, mark: Mark) -> None:
        """Persist a mark."""
        ...

    async def get(self, mark_id: MarkId) -> Mark | None:
        """Retrieve a mark by ID."""
        ...

    async def recent(self, limit: int = 10) -> list[Mark]:
        """Get recent marks, newest first."""
        ...

    async def by_session(self, session_id: str) -> list[Mark]:
        """Get all marks for a session."""
        ...

@dataclass
class InMemoryMarkStore:
    """Simple in-memory store for development/testing."""

    _marks: dict[MarkId, Mark] = field(default_factory=dict)

    async def save(self, mark: Mark) -> None:
        self._marks[mark.id] = mark

    async def get(self, mark_id: MarkId) -> Mark | None:
        return self._marks.get(mark_id)

    async def recent(self, limit: int = 10) -> list[Mark]:
        sorted_marks = sorted(
            self._marks.values(),
            key=lambda m: m.timestamp,
            reverse=True,
        )
        return sorted_marks[:limit]

    async def by_session(self, session_id: str) -> list[Mark]:
        return [
            m for m in self._marks.values()
            if m.session_id == session_id
        ]
```

### Step 3: Create PostgreSQL Adapter

**File:** `impl/claude/services/witness/persistence.py`

```python
from sqlalchemy import Column, String, DateTime, JSON
from agents.d import TableAdapter
from .mark import Mark, MarkId

class MarkAdapter(TableAdapter[Mark]):
    """D-gent persistence for marks."""

    __tablename__ = "witness_marks"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    action = Column(String, nullable=False)
    reasoning = Column(String, nullable=True)
    principles = Column(JSON, default=list)
    session_id = Column(String, nullable=True, index=True)
    parent_id = Column(String, nullable=True, index=True)
    author = Column(String, default="unknown")

    def to_domain(self) -> Mark:
        return Mark(
            id=MarkId(self.id),
            timestamp=self.timestamp,
            action=self.action,
            reasoning=self.reasoning,
            principles=tuple(self.principles or []),
            session_id=self.session_id,
            parent_id=MarkId(self.parent_id) if self.parent_id else None,
            author=self.author,
        )

    @classmethod
    def from_domain(cls, mark: Mark) -> "MarkAdapter":
        return cls(
            id=mark.id,
            timestamp=mark.timestamp,
            action=mark.action,
            reasoning=mark.reasoning,
            principles=list(mark.principles),
            session_id=mark.session_id,
            parent_id=mark.parent_id,
            author=mark.author,
        )
```

### Step 4: Create WitnessService

**File:** `impl/claude/services/witness/service.py`

```python
from dataclasses import dataclass
from .mark import Mark, MarkId, create_mark
from .store import MarkStore

@dataclass
class WitnessService:
    """
    The Witness service: records and retrieves marks.

    Phase 0: Just marks. No walks, playbooks, or proofs yet.
    """

    store: MarkStore
    default_author: str = "unknown"
    current_session_id: str | None = None

    async def mark(
        self,
        action: str,
        *,
        reasoning: str | None = None,
        principles: list[str] | None = None,
        parent_id: MarkId | None = None,
        author: str | None = None,
    ) -> Mark:
        """
        Leave a mark. Every action leaves a mark.

        This is the primary API for Phase 0.
        """
        mark = create_mark(
            action=action,
            reasoning=reasoning,
            principles=principles,
            session_id=self.current_session_id,
            parent_id=parent_id,
            author=author or self.default_author,
        )
        await self.store.save(mark)
        return mark

    async def get(self, mark_id: MarkId) -> Mark | None:
        """Retrieve a specific mark."""
        return await self.store.get(mark_id)

    async def recent(self, limit: int = 10) -> list[Mark]:
        """Get recent marks."""
        return await self.store.recent(limit)

    async def session_marks(self) -> list[Mark]:
        """Get marks for current session."""
        if self.current_session_id is None:
            return []
        return await self.store.by_session(self.current_session_id)
```

### Step 5: Register AGENTESE Node

**File:** `impl/claude/services/witness/node.py`

```python
from protocols.agentese import node, Response, Contract
from pydantic import BaseModel
from .service import WitnessService
from .mark import Mark, MarkId

class MarkRequest(BaseModel):
    action: str
    reasoning: str | None = None
    principles: list[str] = []

class MarkResponse(BaseModel):
    mark_id: str
    timestamp: str
    action: str

class RecentResponse(BaseModel):
    marks: list[MarkResponse]

@node(
    path="time.witness",
    description="Leave marks. Every action leaves a mark.",
    contracts={
        "mark": Contract(MarkRequest, MarkResponse),
        "recent": Response(RecentResponse),
        "get": Contract(str, MarkResponse | None),
    },
    effects=["writes:marks", "reads:marks"],
    dependencies=("witness_service",),
)
class WitnessNode:
    def __init__(self, witness_service: WitnessService):
        self.witness = witness_service

    async def mark(self, request: MarkRequest) -> MarkResponse:
        mark = await self.witness.mark(
            action=request.action,
            reasoning=request.reasoning,
            principles=request.principles,
        )
        return MarkResponse(
            mark_id=mark.id,
            timestamp=mark.timestamp.isoformat(),
            action=mark.action,
        )

    async def recent(self, limit: int = 10) -> RecentResponse:
        marks = await self.witness.recent(limit)
        return RecentResponse(
            marks=[
                MarkResponse(
                    mark_id=m.id,
                    timestamp=m.timestamp.isoformat(),
                    action=m.action,
                )
                for m in marks
            ]
        )

    async def get(self, mark_id: str) -> MarkResponse | None:
        mark = await self.witness.get(MarkId(mark_id))
        if mark is None:
            return None
        return MarkResponse(
            mark_id=mark.id,
            timestamp=mark.timestamp.isoformat(),
            action=mark.action,
        )
```

### Step 6: Register Provider

**File:** `impl/claude/services/providers.py` (add to existing)

```python
def get_witness_service() -> WitnessService:
    """Provider for WitnessService."""
    from services.witness.service import WitnessService
    from services.witness.store import InMemoryMarkStore

    # Phase 0: In-memory. Phase 1: PostgreSQL.
    store = InMemoryMarkStore()
    return WitnessService(store=store, default_author="kgents")

# Register in container
container.register("witness_service", get_witness_service, singleton=True)
```

### Step 7: Write Tests

**File:** `impl/claude/services/witness/tests/test_mark.py`

```python
import pytest
from datetime import datetime
from services.witness.mark import create_mark, Mark, MarkId

def test_create_mark_minimal():
    mark = create_mark(action="Did a thing")
    assert mark.action == "Did a thing"
    assert mark.id.startswith("mark-")
    assert mark.timestamp <= datetime.utcnow()

def test_create_mark_with_reasoning():
    mark = create_mark(
        action="Refactored DI",
        reasoning="Enable Crown Jewel pattern",
        principles=["composable", "generative"],
    )
    assert mark.reasoning == "Enable Crown Jewel pattern"
    assert mark.principles == ("composable", "generative")

def test_mark_is_immutable():
    mark = create_mark(action="Test")
    with pytest.raises(AttributeError):
        mark.action = "Modified"
```

**File:** `impl/claude/services/witness/tests/test_service.py`

```python
import pytest
from services.witness.service import WitnessService
from services.witness.store import InMemoryMarkStore

@pytest.fixture
def witness():
    store = InMemoryMarkStore()
    return WitnessService(store=store, default_author="test")

@pytest.mark.asyncio
async def test_mark_and_retrieve(witness):
    mark = await witness.mark(action="Test action")
    retrieved = await witness.get(mark.id)
    assert retrieved == mark

@pytest.mark.asyncio
async def test_recent_marks(witness):
    await witness.mark(action="First")
    await witness.mark(action="Second")
    await witness.mark(action="Third")

    recent = await witness.recent(limit=2)
    assert len(recent) == 2
    assert recent[0].action == "Third"  # Most recent first
    assert recent[1].action == "Second"
```

---

## Verification

```bash
# Run tests
cd impl/claude
uv run pytest services/witness/tests/ -v

# Type check
uv run mypy services/witness/

# Verify AGENTESE registration
uv run python -c "
from protocols.agentese import get_registry
paths = get_registry().list_paths()
assert 'time.witness' in paths, 'Witness node not registered'
print('✓ Witness node registered')
"
```

---

## Definition of Done

- [ ] `Mark` dataclass exists and is immutable
- [ ] `InMemoryMarkStore` passes all tests
- [ ] `WitnessService` can create and retrieve marks
- [ ] `time.witness` AGENTESE node is registered
- [ ] All tests pass
- [ ] Mypy passes
- [ ] Can be used by Symmetric Supersession Phase 0

---

## Integration Point

**This plan outputs:** `WitnessService` with `mark()`, `get()`, `recent()` methods.

**Consumed by:** `PLAN-symmetric-supersession-phase0.md` — the dialectical engine will use `witness.mark()` to record proposals, challenges, and syntheses.

---

*"The mark is the proof. The proof is the mark."*
