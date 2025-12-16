# Tiny Atelier: Phases 5-8 Continuation

## Context

You are continuing implementation of **Tiny Atelier**, a demo app showcasing the full kgents ecosystem. Phases 1-4 are complete and working.

Theme: Orisinal.com aesthetic—whimsical, minimal, melancholic but hopeful.

## What Already Exists (Phases 1-4)

### Directory Structure
```
impl/claude/agents/atelier/
├── __init__.py
├── artisan.py                    # Base class, Commission, Piece, Provenance
├── artisans/
│   ├── __init__.py               # ARTISAN_REGISTRY
│   ├── calligrapher.py           # Words artisan (streaming LLM)
│   ├── cartographer.py           # Maps artisan
│   └── archivist.py              # Synthesis artisan
├── gallery/
│   ├── __init__.py
│   ├── store.py                  # JSON file persistence
│   └── lineage.py                # Inspiration graph
├── workshop/
│   ├── __init__.py
│   ├── operad.py                 # ATELIER_OPERAD (solo/duet/ensemble/refinement/chain)
│   ├── collaboration.py          # Multi-artisan streaming composition
│   ├── commission.py             # Async queue with persistence
│   └── orchestrator.py           # Workshop + WorkshopFlux (EventBus)
└── _tests/                       # 47 passing tests

protocols/cli/handlers/atelier.py # Full CLI (10 commands)
```

### Working CLI Commands
```bash
kg atelier artisans               # List artisans
kg atelier commission <name> <request>  # Create piece (streaming)
kg atelier gallery                # View gallery
kg atelier view <id>              # View piece + provenance
kg atelier lineage <id>           # View inspiration graph
kg atelier collaborate <names...> -r <request>  # Multi-artisan
kg atelier queue <name> <request> # Queue for background
kg atelier pending                # View queue
kg atelier process [--all]        # Process queue
kg atelier search <query>         # Search gallery
```

### Key Abstractions
- **AtelierEvent**: Streaming events (COMMISSION_RECEIVED, CONTEMPLATING, WORKING, FRAGMENT, PIECE_COMPLETE, ERROR)
- **EventBus[AtelierEvent]**: Fan-out to subscribers
- **ATELIER_OPERAD**: Composition grammar (CompositionLaw.SEQUENTIAL/PARALLEL_MERGE/ITERATIVE)
- **WorkshopFlux**: Central streaming orchestrator

### Patterns Established
```python
# Streaming artisan work
async for event in artisan.stream(commission):
    if event.event_type == AtelierEventType.PIECE_COMPLETE:
        piece = Piece.from_dict(event.data["piece"])

# Collaboration streaming
async for event in collaboration.execute(commission):
    await event_bus.publish(event)

# CLI with live updates
with Live(spinner, console=console) as live:
    async for event in workshop.flux.commission(...):
        live.update(Spinner("dots2", text=event.message))
```

## Your Mission: Phases 5-8

### Phase 5: API Integration

Create REST API for Atelier matching existing patterns in `protocols/api/`.

**File: `protocols/api/atelier.py`**

```python
# Endpoints to implement:
# POST /api/atelier/commission     - Create commission (returns SSE stream)
# GET  /api/atelier/gallery        - List pieces
# GET  /api/atelier/gallery/{id}   - Get piece with provenance
# GET  /api/atelier/gallery/{id}/lineage - Get inspiration graph
# POST /api/atelier/collaborate    - Multi-artisan collaboration (SSE stream)
# POST /api/atelier/queue          - Queue commission
# GET  /api/atelier/queue/pending  - Get pending queue
# POST /api/atelier/queue/process  - Process one/all

# SSE streaming pattern (follow town.py):
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/atelier", tags=["atelier"])

@router.post("/commission")
async def commission(request: CommissionRequest) -> StreamingResponse:
    """Stream artisan work as SSE events."""
    async def generate():
        async for event in workshop.flux.commission(...):
            yield f"data: {json.dumps(event.to_dict())}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**Register in `protocols/api/app.py`**

### Phase 6: Web UI Components

Create React components in `impl/claude/web/src/components/atelier/`.

**Components to build:**
```
web/src/components/atelier/
├── ArtisanCard.tsx        # Individual artisan display
├── ArtisanGrid.tsx        # Grid of available artisans
├── CommissionForm.tsx     # Request input + artisan selection
├── PieceCard.tsx          # Piece preview with provenance teaser
├── PieceDetail.tsx        # Full piece view with provenance
├── GalleryGrid.tsx        # Masonry grid of pieces
├── LineageTree.tsx        # D3/SVG lineage visualization
├── StreamingProgress.tsx  # Real-time work progress
├── CollaborationBuilder.tsx # Select artisans + mode
└── index.ts               # Exports
```

**Streaming hook pattern (follow useTownStreamWidget.ts):**
```typescript
// web/src/hooks/useAtelierStream.ts
export function useAtelierStream(commissionId: string | null) {
  const [events, setEvents] = useState<AtelierEvent[]>([]);
  const [piece, setPiece] = useState<Piece | null>(null);
  const [status, setStatus] = useState<'idle' | 'streaming' | 'complete'>('idle');

  useEffect(() => {
    if (!commissionId) return;

    const eventSource = new EventSource(`/api/atelier/commission/${commissionId}/stream`);
    eventSource.onmessage = (e) => {
      const event = JSON.parse(e.data);
      setEvents(prev => [...prev, event]);
      if (event.event_type === 'piece_complete') {
        setPiece(event.data.piece);
        setStatus('complete');
      }
    };
    return () => eventSource.close();
  }, [commissionId]);

  return { events, piece, status };
}
```

### Phase 7: Reactive Widgets

Create reactive widgets following `agents/i/reactive/` patterns.

**Files to create:**
```
agents/atelier/ui/
├── __init__.py
├── widgets.py             # AtelierWidget, PieceWidget, GalleryWidget
├── projections.py         # CLI/JSON/marimo projections
└── _tests/
    └── test_widgets.py
```

**Widget pattern:**
```python
from agents.i.reactive import Signal, Computed, KgentsWidget

@dataclass
class AtelierWidgetState:
    artisan: str
    status: str  # idle/contemplating/working/ready
    progress: float
    current_fragment: str
    piece: Piece | None

class AtelierWidget(KgentsWidget[AtelierWidgetState]):
    """Reactive widget for artisan work progress."""

    def to_cli(self) -> str:
        state = self.state.value
        if state.status == "working":
            return f"[{state.artisan}] ⟳ {state.progress:.0%} {state.current_fragment[:30]}..."
        elif state.status == "ready":
            return f"[{state.artisan}] ✓ Complete"
        return f"[{state.artisan}] ○ {state.status}"

    def to_marimo(self) -> Any:
        # Return marimo-compatible widget
        pass
```

### Phase 8: Advanced Features

#### 8.1 Patron Profiles
Track who commissions what for personalized recommendations.

```python
# agents/atelier/patron.py
@dataclass
class Patron:
    id: str
    name: str
    preferences: dict[str, float]  # artisan -> affinity
    history: list[str]  # commission IDs

class PatronRegistry:
    async def get_or_create(self, name: str) -> Patron: ...
    async def update_preferences(self, patron: Patron, piece: Piece): ...
    async def recommend_artisan(self, patron: Patron, request: str) -> str: ...
```

#### 8.2 Exhibition Mode
Curated collections with themes.

```python
# agents/atelier/exhibition.py
@dataclass
class Exhibition:
    id: str
    title: str
    theme: str
    curator_note: str
    piece_ids: list[str]
    created_at: datetime

class ExhibitionCurator:
    """Use LLM to curate exhibitions from gallery."""
    async def curate(self, theme: str, gallery: Gallery) -> Exhibition: ...
```

#### 8.3 Refinement Loops
Iterative improvement with feedback.

```python
# Extend collaboration.py
async def refine_until_satisfied(
    artisan: Artisan,
    commission: Commission,
    max_iterations: int = 3,
    satisfaction_check: Callable[[Piece], bool] | None = None,
) -> AsyncIterator[AtelierEvent]:
    """Keep refining until satisfied or max iterations."""
    ...
```

#### 8.4 AGENTESE Integration
Wire atelier paths into AGENTESE.

```python
# protocols/agentese/resolvers/atelier.py
# Paths:
#   world.atelier.commission(artisan, request)
#   world.atelier.gallery.manifest
#   world.atelier.collaborate(artisans, mode, request)
```

## Testing Commands

After implementing each phase:

```bash
# Phase 5: API
curl -X POST http://localhost:8000/api/atelier/commission \
  -H "Content-Type: application/json" \
  -d '{"artisan": "calligrapher", "request": "a haiku about APIs"}'

# Phase 6: Web (run dev server)
cd impl/claude/web && npm run dev
# Visit http://localhost:3000/atelier

# Phase 7: Widgets
uv run pytest agents/atelier/ui/_tests/ -v

# Phase 8: Advanced
kg atelier exhibition create "winter themes"
kg atelier refine <piece_id> "make it more melancholic"
```

## Success Criteria

1. **Phase 5**: SSE streaming works for commission and collaboration endpoints
2. **Phase 6**: Web UI shows real-time streaming progress, gallery is browsable
3. **Phase 7**: Widgets project correctly to CLI, JSON, and marimo
4. **Phase 8**: At least one advanced feature (patron profiles OR exhibitions) is functional

## Architecture Notes

- **Streaming is primary**: Everything emits events, never blocks
- **EventBus for fan-out**: Single event → multiple subscribers
- **Provenance always**: Every piece tracks its creative history
- **Orisinal aesthetic**: Gentle, minimal, warm in all UI output

## Files to Reference

- `protocols/api/town.py` - SSE streaming patterns
- `agents/town/flux.py` - Event streaming architecture
- `agents/i/reactive/` - Widget patterns
- `web/src/hooks/useTownStreamWidget.ts` - Frontend streaming hooks
- `protocols/agentese/resolvers/` - AGENTESE wiring

Barrel through. Ship it.
