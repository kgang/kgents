# LIVING CANVAS UNIFIED ARCHITECTURE

## Document Director Absorbs Living Spec Ledger

**Status**: Implementation In Progress
**Created**: 2025-12-24
**Voice Anchor**: *"Daring, bold, creative, opinionated but not gaudy"*

---

## Executive Summary

The Living Spec Ledger and Document Director represent two paradigms:

| Old (Ledger) | New (Director) |
|--------------|----------------|
| Batch "Scan Corpus" | Per-document lifecycle |
| ProxyHandleStore | SovereignStore overlays |
| LedgerReport cache | AnalysisCrystal persistence |
| Accounting metaphor | Living document metaphor |

**The Decision**: Document Director absorbs Ledger. No batch scan. Auto-analyze on upload.

---

## What Gets Deleted

### Backend
- `services/living_spec/ledger_node.py` - Replaced by DocumentDirector
- `protocols/api/spec_ledger.py` - Replaced by director.py
- `SourceType.SPEC_CORPUS` - No corpus-level caching

### Frontend
- `components/LedgerDashboard.tsx` - Replaced by DirectorDashboard
- `components/SpecTable.tsx` - Replaced by DocumentGrid in DirectorDashboard
- `api/specLedger.ts` - Replaced by director.ts

---

## What Stays

### Backend (Enhanced)
- `services/director/director.py` - Core orchestrator
- `services/director/types.py` - AnalysisCrystal, DocumentStatus
- `protocols/api/director.py` - All endpoints
- `services/sovereign/store.py` - Entity storage + overlays
- `services/living_spec/analyzer.py` - Claim extraction (reused)

### Frontend (Enhanced)
- `api/director.ts` - Unified API client
- `components/director/*` - Status badges, detail views

---

## The New Data Flow

```
UPLOAD → ANALYZE (auto) → DISPLAY (immediate)

[User uploads] ──▶ [POST /upload] ──▶ [Ingest to sovereign]
                         │
                         ▼
                  [Set status: PROCESSING]
                         │
                         ▼ (background task)
                  [director.analyze_deep()]
                         │
                         ├──▶ [SSE: document.analysis.started]
                         │
                         ▼
                  [Store AnalysisCrystal in overlay]
                         │
                         ├──▶ [SSE: document.analysis.complete]
                         │
                         ▼
                  [Set status: READY]
                         │
                         ▼
                  [Frontend receives SSE ──▶ Updates grid immediately]
```

---

## Endpoint Migration

| Old (Ledger) | New (Director) |
|--------------|----------------|
| `POST /api/spec/scan` | DELETED (auto on upload) |
| `GET /api/spec/ledger` | `GET /api/director/documents` |
| `GET /api/spec/orphans` | `GET /api/director/documents?needs_evidence=true` |
| `GET /api/spec/harmonies` | In AnalysisCrystal (per-doc) |
| `POST /api/spec/evidence/*` | `POST /api/director/documents/{path}/evidence` |

---

## New Director Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/director/summary` | Aggregate stats by status |
| `POST /api/director/documents/{path}/deprecate` | Mark deprecated |
| Query params: `needs_evidence`, `has_placeholders`, `min_claims` | Filter documents |

---

## Frontend Components

| Old | New |
|-----|-----|
| `LedgerDashboard` | `DirectorDashboard` |
| "Scan Corpus" button | DELETED (auto-analyze) |
| `SpecTable` | DocumentGrid in DirectorDashboard |
| Status: active/orphan/deprecated | Status: uploaded/processing/ready/executed/stale |

---

## SSE Real-Time Updates

```typescript
// useDirectorStream.ts
const { events, connected } = useWitnessStream();

useEffect(() => {
  const directorEvents = events.filter(e =>
    e.topic?.startsWith('document.')
  );

  for (const event of directorEvents) {
    switch (event.topic) {
      case 'document.analysis.complete':
        // Update document status in grid
        break;
      case 'document.uploaded':
        // Add new document to grid
        break;
    }
  }
}, [events]);
```

---

## Critical Design Decisions

### 1. No More Batch Scan
- **Old**: Click "Scan Corpus" → wait → see results
- **New**: Upload → auto-analyze → see immediately
- **Why**: Batch is opaque. Per-document is traceable.

### 2. AnalysisCrystal is Single Source
- **Old**: LedgerReport cached in ProxyHandle
- **New**: AnalysisCrystal in document overlay
- **Why**: Overlays are persistent. ProxyHandles are ephemeral.

### 3. Summary Computed from Documents
- **Old**: Pre-computed LedgerSummary
- **New**: Aggregate on query
- **Why**: Documents ARE the truth. No separate cache.

### 4. SSE for Real-Time
- **Old**: Manual refresh
- **New**: SSE stream → instant updates
- **Why**: WitnessBus already streams. Frontend subscribes.

---

## Philosophy

> *"This is not accounting. This is gardening."*

Documents have lifecycles:
- **Born** (uploaded)
- **Mature** (analyzed → ready)
- **Act** (executed → code generated)
- **Decay** (stale → needs re-analysis)

The canvas breathes. No more batch. The proof IS the document.

---

**Filed**: 2025-12-24
