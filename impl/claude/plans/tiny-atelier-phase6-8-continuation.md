# Tiny Atelier: Phases 6-8 Continuation

## Context

You are continuing implementation of **Tiny Atelier**, a demo app showcasing the full kgents ecosystem. Phases 1-5 are complete and Phase 6 is partially complete.

Theme: Orisinal.com aesthetic—whimsical, minimal, melancholic but hopeful.

## What Was Completed This Session

### Phase 5: API Integration (COMPLETE)

**Files created:**
- `protocols/api/atelier.py` - Full REST API with SSE streaming (478 lines)
- `protocols/api/_tests/test_atelier.py` - 17 passing tests

**Endpoints implemented:**
```
GET  /api/atelier/artisans              - List available artisans
POST /api/atelier/commission            - Commission artisan (SSE stream)
POST /api/atelier/collaborate           - Multi-artisan collaboration (SSE stream)
GET  /api/atelier/gallery               - List gallery pieces
GET  /api/atelier/gallery/search        - Search gallery
GET  /api/atelier/gallery/{id}          - Get piece with provenance
GET  /api/atelier/gallery/{id}/lineage  - Get inspiration graph
DELETE /api/atelier/gallery/{id}        - Delete piece
POST /api/atelier/queue                 - Queue commission
GET  /api/atelier/queue/pending         - Get pending queue
POST /api/atelier/queue/process         - Process queue (SSE stream)
GET  /api/atelier/status                - Workshop status
```

**Router registered in:** `protocols/api/app.py`

### Phase 6: Web UI Components (PARTIAL)

**Files created:**
- `web/src/api/atelier.ts` - TypeScript API client and types
- `web/src/hooks/useAtelierStream.ts` - SSE streaming hook for commissions
- `web/src/components/atelier/ArtisanCard.tsx` - Individual artisan display
- `web/src/components/atelier/ArtisanGrid.tsx` - Grid of artisans with selection
- `web/src/components/atelier/CommissionForm.tsx` - Commission request form
- `web/src/components/atelier/StreamingProgress.tsx` - Real-time progress display
- `web/src/components/atelier/PieceCard.tsx` - Gallery piece preview

## What Remains

### Phase 6: Remaining Components

Create these components in `web/src/components/atelier/`:

```
PieceDetail.tsx       - Full piece view with provenance
GalleryGrid.tsx       - Masonry grid of pieces (use existing PieceCard)
LineageTree.tsx       - D3/SVG visualization of inspiration graph
CollaborationBuilder.tsx - Enhanced collaboration UI
index.ts              - Exports
```

Add an Atelier page:
```
web/src/pages/Atelier.tsx - Main page combining components
```

### Phase 7: Reactive Widgets

Create reactive widgets in `agents/atelier/ui/`:

```python
# agents/atelier/ui/__init__.py
# agents/atelier/ui/widgets.py - AtelierWidget, PieceWidget, GalleryWidget
# agents/atelier/ui/projections.py - CLI/JSON/marimo projections
# agents/atelier/ui/_tests/test_widgets.py
```

Follow patterns from `agents/i/reactive/`:
- Use Signal/Computed/Effect
- Implement KgentsWidget protocol
- Support `.to_cli()`, `.to_marimo()`, `.to_json()`

### Phase 8: Advanced Features

Implement at least ONE of:

**Option A: Patron Profiles**
```python
# agents/atelier/patron.py
@dataclass
class Patron:
    id: str
    name: str
    preferences: dict[str, float]  # artisan -> affinity
    history: list[str]  # commission IDs

class PatronRegistry:
    async def get_or_create(self, name: str) -> Patron
    async def update_preferences(self, patron: Patron, piece: Piece)
    async def recommend_artisan(self, patron: Patron, request: str) -> str
```

**Option B: Exhibition Mode**
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
    async def curate(self, theme: str, gallery: Gallery) -> Exhibition
```

## Key Files to Reference

- `protocols/api/atelier.py` - API patterns established
- `web/src/hooks/useTownStreamWidget.ts` - Reference SSE hook pattern
- `agents/i/reactive/` - Widget patterns (Signal/Computed/Effect)
- `agents/atelier/artisan.py` - Core types (Piece, Commission, Provenance)
- `agents/atelier/workshop/` - WorkshopFlux streaming patterns

## Testing Commands

```bash
# Run existing tests
cd impl/claude && uv run pytest protocols/api/_tests/test_atelier.py -v

# Run all atelier tests
uv run pytest agents/atelier/_tests/ -v

# Start backend
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Start frontend
cd web && npm run dev
```

## Success Criteria

1. **Phase 6**: Gallery browsable, piece detail view works, lineage visualization renders
2. **Phase 7**: Widget tests pass, projections work for CLI and JSON
3. **Phase 8**: One advanced feature (patron OR exhibition) is functional

## Aesthetic Guidelines

- Soft amber/stone color palette
- Gentle animations (200-300ms transitions)
- Understated UI - content is primary
- Typography: serif for content, sans for UI
- Border-radius: 0.5rem (rounded-lg)
- Shadows: subtle (shadow-sm on hover only)

Barrel through. Ship it.
