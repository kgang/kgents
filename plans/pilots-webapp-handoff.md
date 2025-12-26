# Pilots Webapp Handoff

**Status**: ✅ COMPLETE
**Created**: 2025-12-26
**Completed**: 2025-12-26
**Context Agent**: af8b2da (can resume for clarification)

---

## Executive Summary

This document handed off the execution of a **separate pilots webapp** that serves as a universal container for kgents pilots. **All phases are now complete.**

**Key Constraint**: Pilots do NOT affect the core kgents project. The dependency arrow points ONE way: `pilots → primitives` (never reverse).

### Completion Summary

| Phase | Status | Key Deliverables |
|-------|--------|------------------|
| Phase 1: Foundation | ✅ Complete | Workspace root, shared-primitives, pilots-web shell, pilot registry API |
| Phase 2: Daily Lab | ✅ Complete | Mark capture, Trail timeline, Crystal generation, Day closure, Gap honesty, ShareModal |
| Phase 3: Polish | ✅ Complete | Keyboard shortcuts, README, 29/29 integration tests passing |
| Phase 4: Zero Seed | ✅ Complete | Layer pyramid, Axiom detection, Constitution view (stub) |

### Key Files Created

- `impl/claude/pilots-web/` - Full pilots webapp
- `impl/claude/shared-primitives/` - Reusable component library
- `impl/claude/pilots-web/LAWS.md` - Synthesized pilot laws
- `impl/claude/pilots-web/README.md` - Developer documentation

---

## Part 1: What Was Decided

### Architectural Decision: Monorepo Workspace (Option C)

Create `impl/claude/pilots-web/` as a **separate Vite workspace** alongside the existing `impl/claude/web/`.

**Why this option over alternatives**:
- **Option A** (repo root `pilots-webapp/`): Too distant from backend, duplicates deps
- **Option B** (impl subdir without workspace): Duplicates node_modules
- **Option C** (workspace): Shares deps, maintains isolation, standard monorepo pattern ✓

### Target Structure

```
impl/claude/
├── web/                      # Existing Agent Town (DO NOT MODIFY)
├── pilots-web/               # NEW: Pilots container shell
│   ├── package.json          # Workspace member: "@kgents/pilots-web"
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx           # Shell with pilot selector
│   │   ├── router/
│   │   │   └── index.tsx     # Pilot routing
│   │   ├── shell/            # Container chrome
│   │   │   ├── PilotSelector.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── ThemeProvider.tsx
│   │   ├── pilots/           # Pilot-specific pages
│   │   │   ├── daily-lab/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── MarkCapturePage.tsx
│   │   │   │   ├── TrailPage.tsx
│   │   │   │   └── CrystalPage.tsx
│   │   │   ├── zero-seed/
│   │   │   │   └── index.tsx
│   │   │   └── index.ts      # Pilot registry
│   │   ├── api/              # API client
│   │   │   ├── client.ts
│   │   │   ├── witness.ts
│   │   │   └── pilots.ts
│   │   └── primitives/       # Re-exported from shared
│   │       └── index.ts
│   └── public/
├── shared-primitives/        # NEW: Shared component package
│   ├── package.json          # "@kgents/shared-primitives"
│   ├── tsconfig.json
│   ├── src/
│   │   ├── witness/          # Extract from web/src/components/witness/
│   │   │   ├── MarkCaptureInput.tsx
│   │   │   ├── TrailTimeline.tsx
│   │   │   ├── CrystalCard.tsx
│   │   │   ├── ValueCompassRadar.tsx
│   │   │   ├── GapIndicator.tsx
│   │   │   └── index.ts
│   │   ├── hooks/            # Extract shared hooks
│   │   │   └── useLayoutContext.ts
│   │   ├── constants/        # Extract LIVING_EARTH, TIMING
│   │   │   └── index.ts
│   │   └── index.ts          # Barrel export
│   └── vite.config.ts        # Library build config
└── package.json              # NEW: Workspace root
```

---

## Part 2: What Exists Already

### Backend (Complete - No Changes Needed)

| Service | Location | Status |
|---------|----------|--------|
| DailyLab | `services/witness/daily_lab.py` | 1,432 lines, complete |
| Witness primitives | `services/witness/` | Mark, Trace, Crystal complete |
| Galois | `services/zero_seed/galois/` | Loss, layer assignment complete |
| API routes | `protocols/api/` | All endpoints exist |

### Frontend Components (Complete - Need Extraction)

Location: `impl/claude/web/src/components/witness/`

| Component | Lines | Purpose |
|-----------|-------|---------|
| `MarkCaptureInput.tsx` | 337 | Quick mark entry < 5 seconds |
| `TrailTimeline.tsx` | 455 | Visual trace with neutral gaps |
| `CrystalCard.tsx` | 475 | Memory artifact display |
| `ValueCompassRadar.tsx` | 325 | 7-principle heptagonal radar |
| `GapIndicator.tsx` | 360 | Neutral gap display |

### Shared Dependencies (Need Extraction)

From `impl/claude/web/src/`:
- `hooks/useLayoutContext.ts` - Density-aware layouts
- `constants/index.ts` - LIVING_EARTH palette, TIMING constants
- `components/joy/GrowingContainer.tsx` - Animation primitive

---

## Part 3: What Needs to Be Built

### Phase 1: Foundation (Estimate: 2-4 hours)

#### Task 1.1: Create Workspace Root

Create `impl/claude/package.json`:

```json
{
  "name": "@kgents/monorepo",
  "private": true,
  "workspaces": [
    "web",
    "pilots-web",
    "shared-primitives"
  ],
  "scripts": {
    "dev:pilots": "pnpm --filter @kgents/pilots-web dev",
    "dev:web": "pnpm --filter @kgents/web dev",
    "build:all": "pnpm -r build",
    "typecheck:all": "pnpm -r typecheck"
  }
}
```

#### Task 1.2: Create shared-primitives Package

Create `impl/claude/shared-primitives/package.json`:

```json
{
  "name": "@kgents/shared-primitives",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/index.d.ts"
    },
    "./witness": {
      "import": "./dist/witness/index.js",
      "types": "./dist/witness/index.d.ts"
    }
  },
  "scripts": {
    "build": "vite build",
    "typecheck": "tsc --noEmit"
  },
  "peerDependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "vite-plugin-dts": "^3.0.0"
  }
}
```

#### Task 1.3: Extract Components to shared-primitives

**Copy** (not move - keep originals for now) from `web/src/components/witness/`:
- All 5 witness components
- Update imports to use local paths

**Copy** shared dependencies:
- `hooks/useLayoutContext.ts`
- `constants/index.ts` (LIVING_EARTH, TIMING)
- `components/joy/GrowingContainer.tsx`

#### Task 1.4: Create pilots-web Shell

Create `impl/claude/pilots-web/package.json`:

```json
{
  "name": "@kgents/pilots-web",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --port 3001",
    "build": "vite build",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@kgents/shared-primitives": "workspace:*",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.0.0"
  }
}
```

Create minimal shell:
- `App.tsx` with router
- `PilotSelector.tsx` showing available pilots
- Route to `/daily-lab` (empty placeholder)

#### Task 1.5: Add Pilot Registry Endpoint

Create `impl/claude/protocols/api/pilots.py`:

```python
"""Pilot registry API."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/pilots", tags=["pilots"])

class PilotManifest(BaseModel):
    id: str
    name: str
    description: str
    status: str  # "active" | "coming_soon" | "experimental"
    route: str
    primitives: list[str]

PILOTS = [
    PilotManifest(
        id="daily-lab",
        name="Trail to Crystal",
        description="Turn your day into proof of intention",
        status="active",
        route="/daily-lab",
        primitives=["mark", "trace", "crystal", "compass", "trail"],
    ),
    PilotManifest(
        id="zero-seed",
        name="Zero Seed Governance",
        description="Personal constitution from axioms",
        status="coming_soon",
        route="/zero-seed",
        primitives=["galois", "constitution", "amendment"],
    ),
    # ... other pilots
]

@router.get("")
async def list_pilots() -> list[PilotManifest]:
    return PILOTS

@router.get("/{pilot_id}")
async def get_pilot(pilot_id: str) -> PilotManifest:
    for pilot in PILOTS:
        if pilot.id == pilot_id:
            return pilot
    raise HTTPException(404, f"Pilot not found: {pilot_id}")
```

Register in `app.py`:
```python
from .pilots import router as pilots_router
app.include_router(pilots_router)
```

### Phase 2: Daily Lab Integration (Estimate: 3-4 hours)

#### Task 2.1: Create Daily Lab Pages

In `pilots-web/src/pilots/daily-lab/`:

```typescript
// index.tsx - Main layout
export function DailyLabPilot() {
  return (
    <div className="daily-lab">
      <Outlet />
    </div>
  );
}

// MarkCapturePage.tsx
import { MarkCaptureInput } from '@kgents/shared-primitives/witness';

export function MarkCapturePage() {
  const handleCapture = async (req: CaptureRequest) => {
    return await api.witness.capture(req);
  };

  return <MarkCaptureInput onCapture={handleCapture} autoFocus />;
}

// TrailPage.tsx
import { TrailTimeline } from '@kgents/shared-primitives/witness';

export function TrailPage() {
  const { data: trail } = useTrail(date.today());
  return <TrailTimeline marks={trail.marks} gaps={trail.gaps} />;
}

// CrystalPage.tsx
import { CrystalCard } from '@kgents/shared-primitives/witness';

export function CrystalPage() {
  const { data: crystal } = useCrystal(date.today());
  return <CrystalCard crystal={crystal} honesty={crystal.honesty} />;
}
```

#### Task 2.2: Wire API Client

In `pilots-web/src/api/witness.ts`:

```typescript
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const witnessApi = {
  async capture(req: CaptureRequest): Promise<CaptureResponse> {
    const res = await fetch(`${BASE_URL}/api/witness/daily_lab/capture`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    });
    return res.json();
  },

  async trail(date: string): Promise<TrailResponse> {
    const res = await fetch(`${BASE_URL}/api/witness/daily_lab/trail?date=${date}`);
    return res.json();
  },

  async crystallize(date: string): Promise<CrystalResponse> {
    const res = await fetch(`${BASE_URL}/api/witness/daily_lab/crystallize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date }),
    });
    return res.json();
  },
};
```

#### Task 2.3: Add Routing

In `pilots-web/src/router/index.tsx`:

```typescript
import { createBrowserRouter } from 'react-router-dom';
import { Shell } from '../shell/Shell';
import { PilotSelector } from '../shell/PilotSelector';
import { DailyLabPilot, MarkCapturePage, TrailPage, CrystalPage } from '../pilots/daily-lab';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Shell />,
    children: [
      { index: true, element: <PilotSelector /> },
      {
        path: 'daily-lab',
        element: <DailyLabPilot />,
        children: [
          { index: true, element: <MarkCapturePage /> },
          { path: 'trail', element: <TrailPage /> },
          { path: 'crystal', element: <CrystalPage /> },
        ],
      },
    ],
  },
]);
```

---

## Part 4: Key Insights from Session

### 1. The Integration Tests Are Your Safety Net

29 integration tests exist at `services/witness/_tests/integ/test_daily_pilot.py` validating:
- **5 Laws** (L1-L5): Day closure, intent first, noise quarantine, compression honesty, provenance
- **4 QAs**: Lighter than to-do list, honest gaps, witnessed not surveilled, memory artifact

Run these after any backend changes:
```bash
cd impl/claude && uv run pytest services/witness/_tests/integ/test_daily_pilot.py -v
```

### 2. The Components Already Handle WARMTH

The witness components have WARMTH calibration built in:
- Neutral gap messages: "Untracked time is data, not failure"
- Flow optimization: Mark capture < 5 seconds
- No shame mechanics anywhere

**Do not add productivity metrics, streaks, or gamification.**

### 3. Amendment D Monad is Live

K-Block now has lineage threading via `bind()`. Every `>>` operation creates a `LineageEdge`:

```python
result = doc >> transform_a >> transform_b
# result.bind_lineage contains 2 edges tracking derivation
```

This is relevant for any pilot that needs to track content derivation.

### 4. Galois Loss Novelty Assessment

If publishing about Galois Loss, frame as **novel application** not novel formula:
- Formula `L(P) = d(P, C(R(P)))` has prior art (cycle consistency)
- Novel: Application to categorical layer assignment
- Novel: Axiom detection via fixed-point analysis
- Novel: Epistemic tier classification

### 5. Existing Backend Endpoints

These endpoints already exist and work:
- `POST /api/witness/daily_lab/capture` - Capture a mark
- `GET /api/witness/daily_lab/trail` - Get day's trail
- `POST /api/witness/daily_lab/crystallize` - Generate crystal
- `GET /api/galois/loss` - Compute Galois loss
- `POST /api/galois/fixed_point` - Fixed-point detection

---

## Part 5: Success Criteria

### Phase 1 Complete When: ✅
- [x] `pnpm install` at `impl/claude/` installs all workspaces
- [x] `pnpm dev:pilots` starts pilots-web on port 3001
- [x] Visiting `http://localhost:3001` shows pilot selector
- [x] `GET /api/pilots` returns list of pilots
- [x] `@kgents/shared-primitives` builds without errors

### Phase 2 Complete When: ✅
- [x] Daily Lab pilot loads at `/daily-lab`
- [x] Mark capture works end-to-end (UI → API → storage)
- [x] Trail displays with gaps shown neutrally
- [x] Crystal generation produces shareable artifact
- [x] All 29 integration tests still pass

### Full Success (Canary Criteria from PROTO_SPEC): ✅
- [x] User can explain their day using only the crystal and trail
- [x] System surfaces at least one honest gap without shaming (`GapDetail`, `GapSummaryCard`)
- [x] Day ends with a single, shareable artifact (`ShareModal` with clipboard/markdown/JSON)
- [x] User wants to produce the crystal (`DayClosurePrompt` with confetti celebration)

---

## Part 6: Files to Read Before Starting

1. **Pilot spec**: `pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md`
2. **Witness components**: `impl/claude/web/src/components/witness/index.ts`
3. **Backend service**: `impl/claude/services/witness/daily_lab.py`
4. **API patterns**: `impl/claude/protocols/api/app.py`
5. **Existing web config**: `impl/claude/web/vite.config.ts`
6. **Integration tests**: `impl/claude/services/witness/_tests/integ/test_daily_pilot.py`

---

## Part 7: What NOT To Do

1. **DO NOT modify `impl/claude/web/`** - Keep it untouched
2. **DO NOT add new dependencies to shared-primitives** without justification
3. **DO NOT create pilot-specific backend services** - Use existing witness/galois
4. **DO NOT add productivity metrics, streaks, or gamification** - Violates WARMTH
5. **DO NOT import directly from `web/src/`** - Always go through shared-primitives

---

## Appendix: Agent Resume Information

If you need to resume the planning agent for clarification:
- **Agent ID**: af8b2da
- **Agent Type**: Plan
- **Last Task**: Pilots webapp architecture design

To resume:
```
Resume agent af8b2da to clarify [specific question]
```

---

*"The day is the proof. Honest gaps are signal. Compression is memory."*
