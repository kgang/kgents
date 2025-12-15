# Agent Town Web UI

React frontend for Agent Town - an interactive simulation where AI citizens form relationships, coalitions, and memories.

## Quick Start

### Prerequisites

- Node.js 18+
- Backend API running (see below)

### 1. Start the Backend API

```bash
cd /path/to/kgents/impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

### 2. Start the Frontend

```bash
cd /path/to/kgents/impl/claude/web
npm install
npm run dev
```

Visit `http://localhost:3000`

## Development

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable                      | Description     | Default                 |
| ----------------------------- | --------------- | ----------------------- |
| `VITE_API_URL`                | Backend API URL | `http://localhost:8000` |
| `VITE_WS_URL`                 | WebSocket URL   | `ws://localhost:8000`   |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe test key | -                       |
| `VITE_AUTH_PROVIDER`          | Auth provider   | `mock`                  |

### Mock Login (Development)

The app requires authentication for some features. For development, use the browser console:

```javascript
// Paste in browser console (F12) to mock login
localStorage.setItem(
  'agent-town-user',
  JSON.stringify({
    state: {
      isAuthenticated: true,
      userId: 'dev-user-001',
      apiKey: 'dev-api-key',
      tier: 'CITIZEN', // TOURIST, RESIDENT, CITIZEN, or FOUNDER
      credits: 500,
      monthlyUsage: {},
    },
    version: 0,
  })
);
location.reload();
```

### Available Scripts

| Command                 | Description                  |
| ----------------------- | ---------------------------- |
| `npm run dev`           | Start dev server (port 3000) |
| `npm run build`         | Production build             |
| `npm run typecheck`     | TypeScript type checking     |
| `npm run test`          | Run tests (watch mode)       |
| `npm run test -- --run` | Run tests once               |
| `npm run test:ui`       | Run tests with UI            |
| `npm run test:coverage` | Run tests with coverage      |
| `npm run lint`          | ESLint                       |

### Running Tests

```bash
# Run all tests
npm run test -- --run

# Run specific test file
npm run test -- tests/unit/hooks/useInhabitSession.test.ts

# Run with coverage
npm run test:coverage
```

Current test count: 160+ tests

## Architecture

### Widget-Based Rendering (New)

The Agent Town frontend uses a widget-based architecture:

1. **Backend emits widget JSON** via SSE (`live.state` events)
2. **`useTownStreamWidget` hook** consumes the JSON stream
3. **Widget components** render from JSON (type-discriminated union)

```
Backend (Python)                    Frontend (React)
     │                                    │
     │  ColonyDashboard.to_json()         │
     ├───────── SSE ──────────────────────►│ useTownStreamWidget()
     │  live.state event                  │
     │                                    ▼
     │                              ColonyDashboardJSON
     │                                    │
     │                              WidgetRenderer
     │                                    │
     │                              React Components
```

### Key Files

| File                                   | Purpose                          |
| -------------------------------------- | -------------------------------- |
| `src/hooks/useTownStreamWidget.ts`     | Widget SSE streaming hook        |
| `src/reactive/types.ts`                | Widget JSON type definitions     |
| `src/reactive/WidgetRenderer.tsx`      | Type-discriminated dispatcher    |
| `src/widgets/`                         | Widget component implementations |
| `src/pages/Town.tsx`                   | Widget-based Town page           |
| `src/components/town/Mesa.tsx`         | Props-based Mesa canvas          |
| `src/components/town/CitizenPanel.tsx` | Props-based citizen panel        |

### Directory Structure

```
src/
├── api/           # API client and types
├── components/    # Reusable UI components
│   ├── landing/   # Landing page components (DemoPreview)
│   ├── layout/    # Layout wrapper
│   ├── paywall/   # LODGate, UpgradeModal
│   └── town/      # Town visualization (Mesa, CitizenPanel)
├── hooks/         # Custom React hooks
│   ├── useInhabitSession.ts   # INHABIT session management
│   └── useTownStreamWidget.ts # Widget SSE streaming
├── lib/           # Utilities (Stripe, grid math)
├── pages/         # Route pages
│   ├── Landing.tsx
│   ├── Town.tsx            # Widget-based Town page
│   ├── Inhabit.tsx
│   ├── Dashboard.tsx
│   └── CheckoutSuccess.tsx
├── reactive/      # Widget infrastructure
│   ├── types.ts           # Widget JSON types
│   ├── WidgetRenderer.tsx # Type-safe dispatcher
│   └── useWidgetState.ts  # Widget state hook
├── widgets/       # Widget components
│   ├── primitives/  # Bar, Sparkline, Glyph
│   ├── layout/      # HStack, VStack
│   ├── cards/       # CitizenCard, EigenvectorDisplay
│   └── dashboards/  # ColonyDashboard
└── stores/        # Zustand state stores
    ├── userStore.ts   # Auth, tier, credits
    └── uiStore.ts     # Modals, notifications
```

## Features

### Subscription Tiers

| Tier     | Price     | Features                      |
| -------- | --------- | ----------------------------- |
| TOURIST  | Free      | LOD 0-1, Demo only            |
| RESIDENT | $9.99/mo  | LOD 0-3, Basic INHABIT        |
| CITIZEN  | $29.99/mo | LOD 0-4, Full INHABIT + Force |
| FOUNDER  | $99.99/yr | LOD 0-5, Unlimited everything |

### INHABIT Mode

Step into a citizen's perspective and guide their choices:

- **Suggest actions** - Propose what the citizen should do
- **Force actions** - Override citizen will (CITIZEN+ tier)
- **Apologize** - Repair consent debt after forcing
- **Consent tracking** - Monitor relationship health

## Troubleshooting

### "Demo unavailable" on Landing Page

Backend API not running. Start it with:

```bash
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

### 404 on Town Endpoints

Ensure the town router is registered in `protocols/api/app.py`. The `create_town_router()` should be included.

### Stripe Checkout Not Working

1. Add `VITE_STRIPE_PUBLISHABLE_KEY` to `.env`
2. Ensure you're logged in (use mock login above)
3. Check browser console for errors

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Town Page Blank / "Town Not Found"

1. **Check if town exists**: `curl http://localhost:8000/v1/town/{id}`
2. **Use `/town/demo`**: This creates a new town automatically
3. **Check browser console**: Look for `[Town]` log messages

### SSE Events Not Updating UI

1. **Test SSE directly**: `curl -N "http://localhost:8000/v1/town/{id}/live?speed=2&phases=1"`
2. **Check browser console**: Look for `[SSE]` messages
3. **Verify Immer plugin**: If using Map/Set in stores, ensure `enableMapSet()` is called in `main.tsx`

### Immer MapSet Error

If you see: `Error: [Immer] The plugin for 'MapSet' has not been loaded`

The fix is already in `main.tsx`, but if you're adding new stores with Map/Set:

```typescript
// main.tsx - must be called before any store usage
import { enableMapSet } from 'immer';
enableMapSet();
```

### State Updates But UI Doesn't Change

Common cause: stale closures in SSE/WebSocket event handlers.

```typescript
// BAD: handler captures stale callback
eventSource.addEventListener('event', (e) => {
  addEvent(JSON.parse(e.data)); // Stale!
});

// GOOD: use ref for fresh callbacks
const handlersRef = useRef({ addEvent });
handlersRef.current = { addEvent };

eventSource.addEventListener('event', (e) => {
  handlersRef.current.addEvent(JSON.parse(e.data)); // Fresh!
});
```

See `docs/skills/react-realtime-debugging.md` for detailed patterns.
