# Backend Integration Plan for Evergreen Frontend

> *"The frontend is an anti-sloppification machine. The backend is its evidence source."*

**Status:** Planning
**Created:** 2026-01-17
**Grounded In:** 10-evergreen-vision.md, Backend Services Survey

---

## Executive Summary

The kgents backend is **95% ready** to support the Evergreen Frontend vision. Core infrastructure for witness marks, constitutional scoring, Galois loss, garden lifecycle, and fusion tracking already exists. Only 4 small extensions are needed.

### What Already Exists (Production-Ready)

| Frontend Need | Backend Service | API Endpoint | Status |
|---------------|-----------------|--------------|--------|
| Provenance tracking | `Mark.origin` + `author` field | `POST /api/witness/marks` | ✅ Ready |
| Constitutional scoring | `ConstitutionalAlignment` | `GET /api/witness/constitutional/{id}` | ✅ Ready |
| Galois loss | `services/zero_seed/galois/` | `GET /api/witness/galois/{artifact}` | ✅ Ready |
| Garden lifecycle | `services/witness/garden_service.py` | Needs endpoint | ⚠️ 90% |
| Fusion (Kent vs Claude) | `services/fusion/service.py` | `POST /api/witness/dialectic-decisions` | ✅ Ready |
| K-Block persistence | `services/k_block/` | `GET /api/kblocks/*` | ✅ Ready |
| Trust levels | `ConstitutionalTrustComputer` | `GET /api/witness/constitutional/{id}` | ✅ Ready |
| Crystal compression | `services/witness/crystal.py` | Via marks API | ✅ Ready |

### What Needs Creation (4 Small Extensions)

1. **Garden API Endpoint** — Expose GardenScene to frontend
2. **K-Block Authorship** — Add `author` field to K-Block lifecycle
3. **Fusion → K-Block Link** — Connect dialectic decisions to resulting K-Blocks
4. **Unified Provenance Timeline** — API for authorship history

---

## Part 1: Frontend → Backend Mapping

### 1.1 Three Containers (Human/Collaboration/AI)

**Frontend Need:** Display content with provenance intensity based on author.

**Backend Support:**

```typescript
// Frontend types
type Author = 'kent' | 'claude' | 'fusion';

// Maps to existing Mark.origin + CreateMarkRequest.author
```

**Existing API:**
```python
# protocols/api/witness.py
class CreateMarkRequest(BaseModel):
    author: str = Field(default="kent", description="kent | claude | system")
```

**Integration:**
- When creating marks, frontend passes `author` field
- When displaying marks, use `mark.origin` or `mark.stimulus.author` for intensity
- Fusion container uses `mark.fusion_id` when available

**No changes needed** — existing API sufficient.

---

### 1.2 Collapsing Functions Panel

**Frontend Need:** Display TypeScript, Tests, Constitution, Galois status.

**Backend Support:**

| Function | Backend Service | Existing? |
|----------|-----------------|-----------|
| TypeScript | N/A (frontend build) | N/A |
| Tests | N/A (CI/pytest) | N/A |
| Constitution | `ConstitutionalAlignment` | ✅ |
| Galois | `galois_loss.py` | ✅ |

**Existing API for Constitutional:**
```python
# GET /api/witness/constitutional/{agent_id}
class ConstitutionalHealthResponse(BaseModel):
    agent_id: str
    trust_level: TrustLevel
    principle_averages: dict[str, float]
    dominant_principles: list[str]
    weakest_principles: list[str]
    total_marks_evaluated: int
    recommendations: list[str]
```

**Existing API for Galois:**
```python
# GET /api/witness/galois/{artifact}
# Returns: galois_loss: float, tier: str, evidence: list
```

**Frontend TypeScript/Tests:**
- These are build-time concerns, not backend
- Frontend can poll webpack/vite build status
- Tests run via CI, results stored as marks

**Integration:**
```typescript
// Frontend fetches collapse state
async function fetchCollapseState(kblockId: string): Promise<CollapseState> {
  const [constitutional, galois] = await Promise.all([
    fetch(`/api/witness/constitutional/${kblockId}`),
    fetch(`/api/witness/galois/${kblockId}`)
  ]);

  return {
    typescript: { status: 'pending' }, // From build
    tests: { status: 'pending' },       // From CI
    constitution: constitutional.json(),
    galois: galois.json(),
    overallSlop: computeSlop(constitutional, galois)
  };
}
```

**Minor enhancement needed:** Add K-Block ID support to constitutional endpoint.

---

### 1.3 Garden Lifecycle

**Frontend Need:** Display SEED → SPROUT → BLOOM → WITHER → COMPOST states.

**Backend Support:**

The `WitnessGarden` service exists with full lifecycle tracking:

```python
# services/witness/garden.py
class PlantHealth(Enum):
    BLOOMING = "blooming"   # ≥ 0.9
    HEALTHY = "healthy"     # 0.6-0.9
    WILTING = "wilting"     # 0.3-0.6
    DEAD = "dead"           # < 0.3
    SEEDLING = "seedling"   # New

class SpecLifecycle(Enum):
    UNWITNESSED = "unwitnessed"   # SEED equivalent
    IN_PROGRESS = "in_progress"   # SPROUT equivalent
    WITNESSED = "witnessed"       # BLOOM equivalent
    CONTESTED = "contested"       # WITHER equivalent
    SUPERSEDED = "superseded"     # COMPOST equivalent
```

**NEW ENDPOINT NEEDED:**

```python
# protocols/api/garden.py (NEW)
from fastapi import APIRouter
from services.witness.garden_service import WitnessGarden

router = APIRouter(prefix="/api/garden", tags=["garden"])

class GardenStateResponse(BaseModel):
    seeds: int
    sprouts: int
    blooms: int
    withering: int
    composted_today: int
    health: float
    attention: list[GardenItemResponse]

class GardenItemResponse(BaseModel):
    path: str
    stage: str  # seed | sprout | bloom | wither | compost
    health: float
    days_since_activity: int
    dependents: list[str]

@router.get("/state", response_model=GardenStateResponse)
async def get_garden_state():
    garden = WitnessGarden()
    scene = await garden.build_scene()
    return transform_to_response(scene)

@router.get("/attention", response_model=list[GardenItemResponse])
async def get_attention_items(limit: int = 10):
    garden = WitnessGarden()
    return await garden.get_attention_items(limit)
```

**Mapping:**

| Frontend Stage | Backend SpecLifecycle | Backend PlantHealth |
|----------------|----------------------|---------------------|
| `seed` | UNWITNESSED | SEEDLING |
| `sprout` | IN_PROGRESS | HEALTHY |
| `bloom` | WITNESSED | BLOOMING |
| `wither` | CONTESTED | WILTING |
| `compost` | SUPERSEDED | DEAD |

---

### 1.4 Provenance System (Sloppification Visibility)

**Frontend Need:** Per-line authorship tracking with review status.

**Backend Support:**

Currently, provenance is at the **mark level**, not per-line. This is by design — the witness system tracks decisions, not keystrokes.

**Proposed Approach:**

1. **K-Block Level Provenance** (Existing)
   - Track who created the K-Block
   - Track fusion synthesis provenance
   - This is sufficient for the "container" concept

2. **Mark-Based Evidence** (Existing)
   - When Claude suggests edits, emit a mark
   - When Kent approves, emit a confirmation mark
   - Provenance chain: suggestion → review → acceptance

3. **Per-Line Attribution** (Not Needed?)
   - Git blame provides this
   - Adding per-line tracking adds complexity
   - **Recommendation:** Use K-Block + Mark provenance, not per-line

**K-Block Author Extension:**

```python
# services/k_block/core/kblock.py (EXTENSION)
@dataclass
class KBlockProvenance:
    created_by: str  # 'kent' | 'claude' | 'fusion'
    created_at: datetime
    last_edited_by: str
    last_edited_at: datetime
    fusion_result_of: Optional[str]  # FusionId if from dialectic
    review_status: str  # 'unreviewed' | 'reviewed' | 'confirmed'
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
```

---

### 1.5 Witness Integration

**Frontend Need:** Real-time marks, trails, crystals.

**Backend Support:** Fully implemented.

**Existing API:**
```python
# SSE endpoint for real-time marks
@router.get("/stream")
async def witness_stream():
    """Stream witness events via SSE"""
    # Returns: mark_created, crystal_formed, trail_updated events

# List marks with filters
@router.get("/marks")
async def list_marks(
    limit: int = 50,
    offset: int = 0,
    author: Optional[str] = None,
    origin: Optional[str] = None,
    since: Optional[datetime] = None
):
    ...

# Create mark
@router.post("/marks")
async def create_mark(request: CreateMarkRequest):
    ...
```

**Frontend Integration:**
```typescript
// Real-time witness stream
const eventSource = new EventSource('/api/witness/stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  switch(data.type) {
    case 'mark_created':
      addMarkToDisplay(data.mark);
      if (isGlowWorthy(data.mark)) triggerEarnedGlow();
      break;
    case 'crystal_formed':
      updateCrystalDisplay(data.crystal);
      triggerEarnedGlow(); // Crystal formation is glow-worthy
      break;
  }
};
```

---

## Part 2: New API Endpoints Needed

### 2.1 Garden State Endpoint

```python
# protocols/api/garden.py (NEW FILE)

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from services.witness.garden_service import WitnessGarden, get_witness_garden

router = APIRouter(prefix="/api/garden", tags=["garden"])

class GardenItemResponse(BaseModel):
    path: str
    title: str
    stage: str  # seed | sprout | bloom | wither | compost
    health: float
    days_since_activity: int
    dependents: list[str]
    evidence_count: int
    last_tended: Optional[datetime]

class GardenStateResponse(BaseModel):
    seeds: int
    sprouts: int
    blooms: int
    withering: int
    composted_today: int
    health: float  # Overall garden health 0-1
    attention: list[GardenItemResponse]

class GardenStatsResponse(BaseModel):
    total_plants: int
    healthy_ratio: float
    attention_needed: int
    recently_composted: int

@router.get("/state", response_model=GardenStateResponse)
async def get_garden_state(
    garden: WitnessGarden = Depends(get_witness_garden)
) -> GardenStateResponse:
    """Get current garden state for dashboard."""
    scene = await garden.build_scene()

    # Map lifecycle stages
    seeds = [p for p in scene.plants if p.lifecycle == 'unwitnessed']
    sprouts = [p for p in scene.plants if p.lifecycle == 'in_progress']
    blooms = [p for p in scene.plants if p.lifecycle == 'witnessed']
    withering = [p for p in scene.plants if p.lifecycle == 'contested']

    # Compute attention items (prioritized)
    attention = sorted(
        [p for p in scene.plants if p.health.value in ['wilting', 'dead', 'seedling']],
        key=lambda p: (p.health.value == 'dead', p.days_inactive),
        reverse=True
    )[:10]

    return GardenStateResponse(
        seeds=len(seeds),
        sprouts=len(sprouts),
        blooms=len(blooms),
        withering=len(withering),
        composted_today=scene.composted_today,
        health=scene.overall_health,
        attention=[_to_item(p) for p in attention]
    )

@router.get("/items", response_model=list[GardenItemResponse])
async def list_garden_items(
    stage: Optional[str] = None,
    limit: int = 50,
    garden: WitnessGarden = Depends(get_witness_garden)
) -> list[GardenItemResponse]:
    """List garden items with optional stage filter."""
    scene = await garden.build_scene()
    items = scene.plants

    if stage:
        stage_map = {
            'seed': 'unwitnessed',
            'sprout': 'in_progress',
            'bloom': 'witnessed',
            'wither': 'contested',
            'compost': 'superseded'
        }
        items = [p for p in items if p.lifecycle == stage_map.get(stage, stage)]

    return [_to_item(p) for p in items[:limit]]

@router.post("/items/{path:path}/tend")
async def tend_item(
    path: str,
    garden: WitnessGarden = Depends(get_witness_garden)
):
    """Mark an item as tended (updates last_tended)."""
    await garden.tend(path)
    return {"status": "tended", "path": path}

@router.post("/items/{path:path}/compost")
async def compost_item(
    path: str,
    garden: WitnessGarden = Depends(get_witness_garden)
):
    """Mark an item for composting."""
    await garden.compost(path)
    return {"status": "composted", "path": path}

def _to_item(plant) -> GardenItemResponse:
    """Transform SpecPlant to API response."""
    stage_map = {
        'unwitnessed': 'seed',
        'in_progress': 'sprout',
        'witnessed': 'bloom',
        'contested': 'wither',
        'superseded': 'compost'
    }
    return GardenItemResponse(
        path=plant.path,
        title=plant.title,
        stage=stage_map.get(plant.lifecycle, 'seed'),
        health=plant.health.value,
        days_since_activity=plant.days_inactive,
        dependents=plant.dependents,
        evidence_count=len(plant.evidence_ladder),
        last_tended=plant.last_tended
    )
```

### 2.2 K-Block Provenance Extension

```python
# services/k_block/core/provenance.py (NEW FILE)

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class ReviewStatus(str, Enum):
    UNREVIEWED = "unreviewed"
    REVIEWED = "reviewed"
    CONFIRMED = "confirmed"

@dataclass(frozen=True)
class KBlockProvenance:
    """Provenance tracking for K-Blocks (anti-sloppification)."""

    # Creation
    created_by: str  # 'kent' | 'claude' | 'fusion'
    created_at: datetime

    # Editing
    last_edited_by: str
    last_edited_at: datetime
    edit_count: int = 0

    # Fusion origin (if from dialectic)
    fusion_result_of: Optional[str] = None  # FusionId

    # Review status (for AI-generated content)
    review_status: ReviewStatus = ReviewStatus.UNREVIEWED
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None

    @property
    def is_human_authored(self) -> bool:
        return self.created_by == 'kent'

    @property
    def is_ai_generated(self) -> bool:
        return self.created_by == 'claude'

    @property
    def is_fusion(self) -> bool:
        return self.created_by == 'fusion' or self.fusion_result_of is not None

    @property
    def needs_review(self) -> bool:
        return self.is_ai_generated and self.review_status == ReviewStatus.UNREVIEWED

    def with_edit(self, editor: str) -> 'KBlockProvenance':
        """Create new provenance with edit recorded."""
        return KBlockProvenance(
            created_by=self.created_by,
            created_at=self.created_at,
            last_edited_by=editor,
            last_edited_at=datetime.utcnow(),
            edit_count=self.edit_count + 1,
            fusion_result_of=self.fusion_result_of,
            review_status=self.review_status,
            reviewed_at=self.reviewed_at,
            reviewed_by=self.reviewed_by
        )

    def with_review(self, reviewer: str, confirmed: bool = False) -> 'KBlockProvenance':
        """Create new provenance with review recorded."""
        return KBlockProvenance(
            created_by=self.created_by,
            created_at=self.created_at,
            last_edited_by=self.last_edited_by,
            last_edited_at=self.last_edited_at,
            edit_count=self.edit_count,
            fusion_result_of=self.fusion_result_of,
            review_status=ReviewStatus.CONFIRMED if confirmed else ReviewStatus.REVIEWED,
            reviewed_at=datetime.utcnow(),
            reviewed_by=reviewer
        )
```

### 2.3 Collapse State Endpoint

```python
# protocols/api/collapse.py (NEW FILE)

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from enum import Enum

router = APIRouter(prefix="/api/collapse", tags=["collapse"])

class CollapseStatus(str, Enum):
    PASS = "pass"
    PARTIAL = "partial"
    FAIL = "fail"
    PENDING = "pending"

class CollapseResultResponse(BaseModel):
    status: CollapseStatus
    score: Optional[float] = None
    total: Optional[float] = None
    message: Optional[str] = None

class ConstitutionalCollapseResponse(BaseModel):
    score: float  # 0-7
    principles: dict[str, float]

class GaloisCollapseResponse(BaseModel):
    loss: float  # 0-1
    tier: str  # CATEGORICAL | EMPIRICAL | AESTHETIC | SOMATIC | CHAOTIC

class CollapseStateResponse(BaseModel):
    typescript: CollapseResultResponse
    tests: CollapseResultResponse
    constitution: ConstitutionalCollapseResponse
    galois: GaloisCollapseResponse
    overall_slop: str  # low | medium | high

@router.get("/{kblock_id}", response_model=CollapseStateResponse)
async def get_collapse_state(kblock_id: str) -> CollapseStateResponse:
    """Get collapse state for a K-Block."""

    # Fetch constitutional alignment
    constitutional = await get_constitutional_score(kblock_id)

    # Fetch Galois loss
    galois = await get_galois_loss(kblock_id)

    # Compute overall sloppification
    slop = compute_slop(constitutional, galois)

    return CollapseStateResponse(
        typescript=CollapseResultResponse(status=CollapseStatus.PENDING),
        tests=CollapseResultResponse(status=CollapseStatus.PENDING),
        constitution=ConstitutionalCollapseResponse(
            score=constitutional.weighted_total * 7,
            principles=constitutional.scores
        ),
        galois=GaloisCollapseResponse(
            loss=galois.loss,
            tier=galois.tier
        ),
        overall_slop=slop
    )

def compute_slop(constitutional, galois) -> str:
    """Compute overall sloppification level."""
    # High slop if: low constitutional score OR high Galois loss
    if constitutional.weighted_total < 0.6 or galois.loss > 0.5:
        return "high"
    elif constitutional.weighted_total < 0.8 or galois.loss > 0.3:
        return "medium"
    return "low"
```

---

## Part 3: SSE Real-Time Integration

### 3.1 Unified Event Stream

The frontend needs a single SSE stream for all real-time updates:

```python
# protocols/api/realtime.py (NEW FILE)

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import asyncio
import json

router = APIRouter(prefix="/api/realtime", tags=["realtime"])

@router.get("/stream")
async def unified_stream():
    """Unified SSE stream for all frontend updates."""

    async def event_generator():
        # Subscribe to all relevant channels
        witness_sub = subscribe_witness_events()
        garden_sub = subscribe_garden_events()
        kblock_sub = subscribe_kblock_events()

        while True:
            # Check each subscription
            for sub, event_type in [
                (witness_sub, 'witness'),
                (garden_sub, 'garden'),
                (kblock_sub, 'kblock')
            ]:
                event = await sub.get_nowait()
                if event:
                    yield f"event: {event_type}\ndata: {json.dumps(event)}\n\n"

            await asyncio.sleep(0.1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 3.2 Frontend SSE Client

```typescript
// src/hooks/useRealtimeStream.ts

import { useEffect, useCallback } from 'react';

type EventType = 'witness' | 'garden' | 'kblock' | 'collapse';

interface RealtimeEvent {
  type: EventType;
  data: unknown;
}

export function useRealtimeStream(handlers: Partial<Record<EventType, (data: unknown) => void>>) {
  useEffect(() => {
    const eventSource = new EventSource('/api/realtime/stream');

    eventSource.onmessage = (event) => {
      const parsed: RealtimeEvent = JSON.parse(event.data);
      const handler = handlers[parsed.type];
      if (handler) {
        handler(parsed.data);
      }
    };

    eventSource.onerror = () => {
      // Reconnect after 5 seconds
      setTimeout(() => eventSource.close(), 5000);
    };

    return () => eventSource.close();
  }, [handlers]);
}

// Usage in component
function WorkspacePage() {
  useRealtimeStream({
    witness: (data) => {
      if (data.type === 'mark_created' && isGlowWorthy(data.mark)) {
        triggerEarnedGlow();
      }
    },
    garden: (data) => {
      updateGardenState(data);
    },
    kblock: (data) => {
      updateKBlockState(data);
    }
  });
}
```

---

## Part 4: Implementation Sequence

### Phase 1: Garden API (1 hour)

1. Create `protocols/api/garden.py`
2. Register router in `protocols/api/app.py`
3. Test endpoints manually

### Phase 2: K-Block Provenance (1.5 hours)

1. Create `services/k_block/core/provenance.py`
2. Extend KBlock dataclass to include provenance
3. Update K-Block API responses to include provenance

### Phase 3: Collapse API (1 hour)

1. Create `protocols/api/collapse.py`
2. Wire to constitutional and Galois services
3. Add sloppification computation

### Phase 4: SSE Unification (1 hour)

1. Create `protocols/api/realtime.py`
2. Add event aggregation from existing streams
3. Test with frontend EventSource

### Phase 5: Frontend Hooks (2 hours)

1. Create `useGardenState` hook
2. Create `useProvenanceState` hook
3. Create `useCollapseState` hook
4. Create `useRealtimeStream` hook

---

## Part 5: API Summary

### New Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/garden/state` | Garden dashboard state |
| GET | `/api/garden/items` | List garden items with filters |
| POST | `/api/garden/items/{path}/tend` | Mark item as tended |
| POST | `/api/garden/items/{path}/compost` | Mark item for composting |
| GET | `/api/collapse/{kblock_id}` | Collapse panel state |
| GET | `/api/realtime/stream` | Unified SSE stream |

### Enhanced Endpoints

| Method | Path | Enhancement |
|--------|------|-------------|
| GET | `/api/kblocks/{id}` | Add provenance field |
| POST | `/api/kblocks` | Add created_by field |
| PATCH | `/api/kblocks/{id}` | Track edited_by |
| POST | `/api/kblocks/{id}/review` | Mark as reviewed |

### Existing Endpoints (No Changes)

| Method | Path | Purpose |
|--------|------|---------|
| GET/POST | `/api/witness/marks` | Mark CRUD |
| GET | `/api/witness/stream` | Witness SSE |
| GET | `/api/witness/constitutional/{id}` | Constitutional health |
| GET | `/api/witness/galois/{artifact}` | Galois loss |
| POST | `/api/witness/dialectic-decisions` | Fusion tracking |

---

## Part 6: Testing Strategy

### Unit Tests

```python
# tests/unit/test_garden_api.py
async def test_garden_state_returns_lifecycle_counts():
    response = await client.get("/api/garden/state")
    assert "seeds" in response.json()
    assert "sprouts" in response.json()
    assert "blooms" in response.json()

# tests/unit/test_provenance.py
def test_kblock_provenance_tracks_author():
    prov = KBlockProvenance(created_by='claude', ...)
    assert prov.is_ai_generated
    assert prov.needs_review
```

### Integration Tests

```python
# tests/integration/test_frontend_backend.py
async def test_mark_creation_triggers_sse_event():
    with EventSourceClient("/api/realtime/stream") as sse:
        await client.post("/api/witness/marks", json={...})
        event = await sse.next()
        assert event['type'] == 'witness'
```

### E2E Tests (Playwright)

```typescript
// e2e/workspace.spec.ts
test('collapse panel shows constitutional score', async ({ page }) => {
  await page.goto('/workspace');
  await expect(page.locator('[data-testid="collapse-constitution"]')).toBeVisible();
  await expect(page.locator('[data-testid="collapse-constitution"]')).toContainText(/[0-7]/);
});
```

---

## Conclusion

The backend is nearly complete. With 4 small additions (Garden API, K-Block provenance, Collapse API, unified SSE), the Evergreen Frontend will have full evidence for its anti-sloppification mission.

**Estimated Backend Work:** 5.5 hours
**Dependencies:** None (all core services exist)
**Risk:** Low (extending proven patterns)

---

*"The evidence is the interface. The interface is the evidence."*
