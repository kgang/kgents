# Run 001 - Archive Manifest

## Metadata

| Field | Value |
|-------|-------|
| **Timestamp** | 2025-12-26 |
| **Git SHA** | 3b49baa9e49fdc9b1d1c1e0091cc07bcecd6321b |
| **Status** | Archived for regeneration |

## Reason for Archive

Contract coherence issues between frontend and backend:

1. **API Endpoint Mismatch**: Frontend called `/api/witness/marks/capture`, backend serves `/api/witness/daily/capture`
2. **Type Drift**: `TrailResponse.gaps` expected array, got scalar
3. **Local Type Duplication**: Frontend defined local types instead of importing from shared contracts

## Files Archived

### Configuration
- `index.html`
- `package.json`
- `postcss.config.js`
- `tailwind.config.js`
- `tsconfig.json`
- `tsconfig.node.json`
- `vite.config.ts`

### Documentation
- `LAWS.md`
- `README.md`

### Source - API Layer
- `src/api/galois.ts`
- `src/api/pilots.ts`
- `src/api/witness.ts`

### Source - Components
- `src/components/index.ts`
- `src/components/KeyboardHint.tsx`

### Source - Hooks
- `src/hooks/index.ts`
- `src/hooks/useKeyboardShortcuts.ts`
- `src/hooks/usePilots.ts`

### Source - Pilots
- `src/pilots/daily-lab/index.tsx`
- `src/pilots/daily-lab/DayClosurePrompt.tsx`
- `src/pilots/daily-lab/GapDetail.tsx`
- `src/pilots/daily-lab/GapSummaryCard.tsx`
- `src/pilots/daily-lab/ShareModal.tsx`
- `src/pilots/zero-seed/index.tsx`

### Source - Router
- `src/router/index.tsx`

### Source - Shell
- `src/shell/LayoutProvider.tsx`
- `src/shell/PilotSelector.tsx`
- `src/shell/Shell.tsx`
- `src/shell/ThemeProvider.tsx`

### Source - Utils
- `src/utils/download.ts`
- `src/utils/gapMessages.ts`

### Source - Entry
- `src/main.tsx`
- `src/index.css`

### Assets
- `public/vite.svg`

## Known Issues Being Fixed

### 1. API Endpoint Mismatch
```
Frontend: POST /api/witness/marks/capture
Backend:  POST /api/witness/daily/capture
```

The frontend assumed a different route structure than what the backend actually serves. This caused 404 errors when attempting to capture marks.

### 2. Type Drift
```typescript
// Frontend expected:
interface TrailResponse {
  gaps: Gap[];  // Array
}

// Backend returned:
{
  "gaps": 0  // Scalar count
}
```

The `gaps` field was interpreted differently - frontend expected full gap objects, backend returned just a count.

### 3. Local Type Definitions
Instead of importing from `@kgents/shared-primitives`, the frontend defined local types that drifted from the canonical contracts:

```typescript
// Local (drifted)
interface Gap {
  id: string;
  // ... local definition
}

// Should use:
import { Gap } from '@kgents/shared-primitives';
```

## Contracts Snapshot

The `contracts/` directory contains a snapshot of the shared-primitives contracts at the time of archive:
- `daily-lab.ts` - Daily lab types and interfaces
- `index.ts` - Re-exports

## Regeneration Intent

Run 002 will:
1. Import types from `@kgents/shared-primitives` (no local type definitions)
2. Use correct API paths matching backend routes
3. Validate types match at build time via TypeScript
