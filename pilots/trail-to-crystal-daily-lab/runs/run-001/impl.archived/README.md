# kgents Pilots Web

> Universal container for kgents pilots - standalone experiments that test kgents principles.

*"The day is the proof. Honest gaps are signal. Compression is memory."*

## Quick Start

```bash
# From impl/claude (monorepo root)
cd impl/claude

# Install all workspace dependencies
pnpm install

# Start the pilots webapp (port 3001)
pnpm dev:pilots

# Visit http://localhost:3001
```

The backend API must also be running:

```bash
# Terminal 2: Start the backend (port 8000)
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

## Architecture

### Monorepo Workspace Structure

```
impl/claude/
├── package.json              # Workspace root (@kgents/monorepo)
├── web/                      # Agent Town (main app, DO NOT MODIFY for pilots)
├── pilots-web/               # Pilots container shell (@kgents/pilots-web)
│   ├── package.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── router/           # Pilot routing
│   │   ├── shell/            # Container chrome (Shell, PilotSelector, Theme)
│   │   ├── pilots/           # Pilot-specific pages
│   │   │   ├── daily-lab/    # Trail to Crystal pilot
│   │   │   └── zero-seed/    # Zero Seed Governance pilot
│   │   ├── api/              # API clients (witness, galois, pilots)
│   │   ├── hooks/            # Shared hooks
│   │   └── utils/            # Utilities (download, gap messages)
│   └── tailwind.config.js
└── shared-primitives/        # Shared component library (@kgents/shared-primitives)
    └── src/
        ├── witness/          # MarkCaptureInput, TrailTimeline, CrystalCard, etc.
        ├── hooks/            # useLayoutContext
        ├── constants/        # LIVING_EARTH palette, TIMING
        └── joy/              # GrowingContainer animation primitive
```

### Dependency Direction

```
pilots-web ──depends on──> shared-primitives
                                   ▲
                                   │
web (Agent Town) ──depends on──────┘

NEVER: shared-primitives → pilots-web
NEVER: shared-primitives → web
```

The dependency arrow points ONE way: pilots consume primitives, never the reverse.

## Available Pilots

### Daily Lab (Trail to Crystal)

**Status**: Active
**Route**: `/daily-lab`
**Joy Dimension**: WARMTH

Turn your day into proof of intention. The Daily Lab transforms ordinary actions into a visible trace and compresses them into a crystal - a memory artifact that honors honest gaps instead of concealing them.

#### Features

| Feature | Description |
|---------|-------------|
| **Mark Capture** | Quick action entry (< 5 seconds) with intent and tags |
| **Trail Timeline** | Visual trace of the day with neutral gap indicators |
| **Crystal Generation** | Compress the day into a shareable memory artifact |
| **Day Closure** | Ritual prompt after 6 PM to crystallize the day |
| **Gap Honesty** | Untracked time is data, not failure |

#### The 5 Laws

| Law | Description |
|-----|-------------|
| **L1 Day Closure** | A day is complete only when a crystal is produced |
| **L2 Intent First** | Actions without declared intent are marked provisional |
| **L3 Noise Quarantine** | High-loss marks cannot define the day narrative |
| **L4 Compression Honesty** | All crystals disclose what was dropped |
| **L5 Provenance** | Every crystal statement links to at least one mark |

#### The 4 Quality Attributes

| QA | Description |
|----|-------------|
| **QA-1** | The ritual feels lighter than a to-do list |
| **QA-2** | Honest gaps are rewarded, not concealed |
| **QA-3** | Users feel witnessed, not surveilled |
| **QA-4** | The crystal is a memory artifact, not a summary |

### Zero Seed Governance

**Status**: Experimental
**Route**: `/zero-seed`
**Joy Dimension**: FLOW

Build your personal constitution from axioms. Zero Seed applies Galois loss analysis to detect semantic fixed points - statements that survive the restructure-reconstitute cycle.

#### Features

| Feature | Description |
|---------|-------------|
| **Constitution View** | Visualize epistemic layers (L1 Axiom to L7 Representation) |
| **Axiom Detection** | Identify fixed points via R/C iteration analysis |
| **Layer Assignment** | Classify statements by Galois loss thresholds |
| **Amendment History** | Track how your constitution evolves (coming soon) |

#### Layer Structure

| Layer | Name | Loss Range | Description |
|-------|------|------------|-------------|
| L1 | Axiom | < 1% | Self-evident truths surviving R/C cycles |
| L2 | Value | 1-5% | Core values derived from axioms |
| L3 | Goal | 5-12% | Desired outcomes from values |
| L4 | Strategy | 12-25% | Approaches to achieve goals |
| L5 | Tactic | 25-40% | Specific methods |
| L6 | Action | 40-60% | Concrete steps |
| L7 | Representation | > 60% | Surface expressions |

## Development

### Prerequisites

- Node.js 18+
- pnpm (v9.0.0 specified in packageManager)
- Python 3.12+ with uv (for backend)

### Commands

```bash
# Development
pnpm dev:pilots          # Start pilots-web dev server (port 3001)
pnpm dev:web             # Start main web dev server (port 3000)

# Type checking (run before committing!)
pnpm typecheck:all       # Check all workspaces
cd pilots-web && pnpm typecheck  # Check pilots-web only

# Building
pnpm build:all           # Build all workspaces

# Individual package commands
cd pilots-web && pnpm dev        # Dev server
cd pilots-web && pnpm build      # Production build
cd pilots-web && pnpm lint       # ESLint
```

### Adding a New Pilot

1. **Create the pilot directory**:
   ```bash
   mkdir -p src/pilots/my-pilot
   ```

2. **Create the layout component** (`src/pilots/my-pilot/index.tsx`):
   ```tsx
   import { Routes, Route, Navigate, NavLink } from 'react-router-dom';

   export function MyPilotLayout() {
     return (
       <div className="space-y-6">
         <div className="text-center">
           <h1 className="text-2xl font-bold text-lantern mb-2">My Pilot</h1>
           <p className="text-sand">Description of my pilot</p>
         </div>

         <nav className="flex justify-center gap-4 border-b border-sage/20 pb-4">
           <TabLink to="/my-pilot" label="Tab 1" end />
           <TabLink to="/my-pilot/tab2" label="Tab 2" />
         </nav>

         <Routes>
           <Route index element={<Tab1Page />} />
           <Route path="tab2" element={<Tab2Page />} />
           <Route path="*" element={<Navigate to="." replace />} />
         </Routes>
       </div>
     );
   }
   ```

3. **Register in the router** (`src/router/index.tsx`):
   ```tsx
   import { MyPilotLayout } from '../pilots/my-pilot';

   // Add to router children:
   {
     path: 'my-pilot/*',
     element: <MyPilotLayout />,
   },
   ```

4. **Add to backend pilot registry** (`protocols/api/pilots.py`):
   ```python
   PilotManifest(
       id="my-pilot",
       name="My Pilot Name",
       description="What my pilot does",
       status="experimental",  # or "active" | "coming_soon"
       route="/my-pilot",
       primitives=["list", "of", "primitives"],
       joy_dimension="FLOW",  # or "WARMTH" | "SURPRISE"
   ),
   ```

5. **Create API client if needed** (`src/api/my-pilot.ts`)

### Testing Strategy

Backend integration tests validate pilot behavior:

```bash
cd impl/claude
uv run pytest services/witness/_tests/integ/test_daily_pilot.py -v
```

Frontend type checking catches component contract violations:

```bash
cd impl/claude/pilots-web
pnpm typecheck
```

## Design System

### Living Earth Palette

The pilots use the Living Earth color palette, designed for warmth and readability:

| Token | Hex | Usage |
|-------|-----|-------|
| `bark` | #1C1917 | Background (dark mode) |
| `lantern` | #FAFAF9 | Primary text |
| `sand` | #A8A29E | Secondary text |
| `clay` | #78716C | Muted text, borders |
| `sage` | #A3E635 | Accent, active states |
| `amber` | #FBBF24 | CTAs, highlights |
| `rust` | #C2410C | Errors, warnings |

### WARMTH Principles

The pilots embody the WARMTH design philosophy:

1. **No shame mechanics** - The system never judges. Gaps are data, not failure. There are no streaks to break, no scores to disappoint.

2. **Gaps are data, not failure** - Untracked time is honestly acknowledged: "2h untracked. This is noted, not judged." The UI treats gaps as neutral information.

3. **Compression is memory, not loss** - When the day crystallizes, what's dropped is disclosed. The crystal is a memory artifact that deserves to be re-read, not a summary to be filed.

4. **Witnessed, not surveilled** - The system is a collaborator, not a panopticon. Users should feel their choices are honored, not monitored.

5. **Lighter than a to-do list** - If the ritual feels like friction, it's failing. Mark capture is < 5 seconds. The crystal should feel like closure, not obligation.

### Anti-Patterns (What NOT to Build)

- Productivity metrics or scores
- Streak counters or gamification
- Comparisons to benchmarks
- Pressure to track more
- Judgment of time allocation

## API Integration

### Backend Endpoints

Pilots connect to the FastAPI backend running on port 8000:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/pilots` | GET | List available pilots |
| `/api/pilots/{id}` | GET | Get pilot manifest |
| `/api/witness/marks/capture` | POST | Capture a mark |
| `/api/witness/trail/today` | GET | Get today's trail |
| `/api/witness/crystallize` | POST | Generate crystal |
| `/api/witness/crystals` | GET | Get crystals |
| `/api/galois/fixed_point` | POST | Detect semantic fixed point |
| `/api/galois/layer` | POST | Assign epistemic layer |

### API Client Pattern

```typescript
// src/api/witness.ts
const API_BASE = '/api/witness';

export async function captureMarkApi(request: CaptureRequest): Promise<CaptureResponse> {
  const response = await fetch(`${API_BASE}/marks/capture`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to capture mark: ${response.statusText}`);
  }

  return response.json();
}
```

### Vite Proxy Configuration

The dev server proxies API requests to the backend:

```typescript
// vite.config.ts
server: {
  port: 3001,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
},
```

## Success Criteria

### What Makes a Successful Pilot

1. **Uses shared primitives correctly** - Imports from `@kgents/shared-primitives`, never duplicates
2. **Respects WARMTH principles** - No shame mechanics, gaps are data
3. **Integrates cleanly** - Works with existing backend services
4. **Feels like closure** - The ritual is satisfying, not burdensome
5. **Passes integration tests** - Backend laws are validated

### Canary Criteria (from Daily Lab PROTO_SPEC)

- User can explain their day using only the crystal and trail
- System surfaces at least one honest gap without shaming
- Day ends with a single, shareable artifact
- User wants to produce the crystal (feels like closure, not obligation)

### Failure Modes to Avoid

- **Hustle theater**: Optimizing for "productivity"
- **Gap shame**: Treating untracked time as failure
- **Surveillance drift**: Making users feel watched and judged
- **Summary flatness**: Crystals that read like bullet lists
- **Ritual burden**: End-of-day closure feels like homework

---

## Related Documentation

- **Pilot Spec**: `pilots/trail-to-crystal-daily-lab/PROTO_SPEC.md`
- **Handoff Doc**: `plans/pilots-webapp-handoff.md`
- **Backend Service**: `services/witness/daily_lab.py`
- **Integration Tests**: `services/witness/_tests/integ/test_daily_pilot.py`
- **Shared Primitives**: `shared-primitives/src/`

---

*Built with the kgents categorical framework. Every pilot is a morphism in the category of intentional action.*
