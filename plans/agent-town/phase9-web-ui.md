---
path: plans/agent-town/phase9-web-ui
status: active
progress: 10
last_touched: 2025-12-15
touched_by: claude-opus-4-5
blocking: []
enables:
  - monetization/stripe-integration
  - deployment/public-demo
session_notes: |
  PHASE 9: Web UI MVP - Public-facing interface for Agent Town.
  Enables monetization through browser-based access.
  React + Canvas/Pixi.js for visualization.

  Dependencies RESOLVED (2025-12-15):
  - Phase 8 INHABIT: COMPLETE (88 tests)
    - InhabitSession with consent tracking
    - process_input_async, force_action_async
    - LLM alignment checking with heuristic fallback
  - Web scaffold: EXISTS (impl/claude/web/)
    - Routes: Landing, Town, Inhabit, Dashboard, CheckoutSuccess
    - Stores: townStore, userStore
    - Types: Full API types including INHABIT
  - Backend APIs: READY
    - protocols/api/town.py
    - protocols/api/payments.py
    - protocols/api/action_metrics.py

  Kickoff prompt: prompts/phase9-web-ui-kickoff.md
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: in_progress
  STRATEGIZE: complete
  CROSS-SYNERGIZE: touched
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.03
  remaining: 0.07
---

# Phase 9: Web UI MVP

> *"The interface is not a window to the system. The interface IS the system, made visible."*

---

## Scope Statement

Phase 9 delivers the **browser-based Agent Town interface**—the public-facing product that enables monetization. This is where free users discover the product and paying users engage with their towns.

**Core Screens**:
1. **Landing Page**: Marketing + demo town preview
2. **Town Mesa**: 2D grid view with citizen positions
3. **Citizen Panel**: Inspectable citizen details (LOD-gated)
4. **Event Feed**: Real-time activity stream
5. **INHABIT Interface**: Browser-based INHABIT mode
6. **Dashboard**: User's towns, credits, subscription

---

## Exit Criteria

- [ ] Landing page with demo town preview
- [ ] Town Mesa renders citizens on 2D grid
- [ ] Click citizen → Citizen Panel opens
- [ ] LOD 0-2 visible to all; LOD 3-5 gated by subscription/credits
- [ ] SSE event stream shows real-time activity
- [ ] INHABIT mode works in browser
- [ ] Auth flow with Stripe checkout
- [ ] Mobile responsive (basic)
- [ ] 95+ Lighthouse performance score

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Framework** | React 18 + TypeScript | Industry standard, good ecosystem |
| **Rendering** | Pixi.js | Fast 2D WebGL for Mesa |
| **State** | Zustand | Lightweight, works with SSE |
| **Styling** | Tailwind CSS | Rapid prototyping |
| **Streaming** | EventSource (SSE) | Native browser support |
| **Auth** | Clerk/Auth0 | Quick setup, Stripe integration |
| **Payments** | Stripe | Industry standard |
| **Hosting** | Vercel/Fly.io | Edge deployment, WebSocket support |

---

## Screen Designs

### 1. Landing Page

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║              A G E N T   T O W N                                       ║  │
│  ║              Civilizations that dream                                  ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                             │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │                                                                 │     │
│     │              [LIVE DEMO TOWN PREVIEW]                          │     │
│     │                                                                 │     │
│     │         A  ·  ·  B  ·  ·  ·  ·  C                              │     │
│     │         ·  ·  ·  ·  ·  ·  D  ·  ·                              │     │
│     │         ·  E  ·  ·  ·  ·  ·  ·  ·                              │     │
│     │         ·  ·  ·  F  ·  ·  ·  G  ·                              │     │
│     │                                                                 │     │
│     │    "Alice just greeted Bob warmly..."  ← live event feed       │     │
│     │                                                                 │     │
│     └─────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│     [Watch the Demo]                    [Start Your Town - $9.99/mo]        │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                  │
│     │   OBSERVE    │   │   INHABIT    │   │   BRANCH     │                  │
│     │              │   │              │   │              │                  │
│     │ Watch lives  │   │ Become them  │   │ Fork reality │                  │
│     │ unfold       │   │              │   │              │                  │
│     └──────────────┘   └──────────────┘   └──────────────┘                  │
│                                                                             │
│  ───────────────────────────────────────────────────────────────────────── │
│                                                                             │
│     PRICING                                                                 │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│     │ TOURIST  │  │ RESIDENT │  │ CITIZEN  │  │ FOUNDER  │                 │
│     │   FREE   │  │$9.99/mo  │  │$29.99/mo │  │$99.99/mo │                 │
│     │ [Demo]   │  │ [Start]  │  │ [Start]  │  │ [Start]  │                 │
│     └──────────┘  └──────────┘  └──────────┘  └──────────┘                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Town Mesa (Main View)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Agent Town > Demo Town                     [Credits: 150] [Kent ▾] [⚙]   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Day 7, MORNING                                    [⏸ Pause] [⏩ Speed]   │
│                                                                             │
│   ┌───────────────────────────────────────────────────────────────────┐     │
│   │                                                                   │     │
│   │      [A]  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·         │     │
│   │        │                                                          │     │
│   │        ↓ approaching                                              │     │
│   │      ·  ·  [B]  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  ·         │     │
│   │                    \                                              │     │
│   │      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  [C]  ·  ·  ·  ·  ·  ·         │     │
│   │                                      │                            │     │
│   │      ·  ·  ·  ·  ·  ·  [D]  ·  ·  ·  │  ·  ·  ·  ·  ·  ·         │     │
│   │                          \           │                            │     │
│   │      ·  ·  ·  ·  ·  ·  ·  \  ·  ·  ·  ↓  ·  ·  ·  ·  ·  ·         │     │
│   │                            [E]  ·  ·  ·  ·  ·  ·  ·  ·  ·         │     │
│   │                                                                   │     │
│   │      ·  ·  ·  ·  ·  ·  ·  ·  ·  ·  [F]  ·  ·  ·  ·  [G]          │     │
│   │                                                                   │     │
│   └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│   Legend: A=Alice B=Bob C=Clara D=David E=Eve F=Frank G=Grace              │
│                                                                             │
├────────────────────────────────────┬────────────────────────────────────────┤
│  EVENT FEED                        │  CITIZEN PANEL                         │
│  ───────────────────────────────   │  (Click a citizen to inspect)         │
│  10:32 Alice greeted Bob warmly    │                                        │
│  10:31 Clara wrote in her journal  │  ┌────────────────────────────────┐   │
│  10:30 David examined the well     │  │  Selected: None                │   │
│  10:28 Eve watched silently        │  │                                │   │
│  10:25 Coalition formed: [A,B,D]   │  │  Click a citizen on the map   │   │
│  ...                               │  │  to see their details          │   │
│  [See more...]                     │  └────────────────────────────────┘   │
│                                    │                                        │
└────────────────────────────────────┴────────────────────────────────────────┘
```

### 3. Citizen Panel (LOD-Gated)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  CITIZEN PANEL: Alice (Innkeeper)                                [×]       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   [LOD 0: Silhouette] ✓                                                    │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │  Name: Alice                                                     │      │
│   │  Archetype: Innkeeper (Builder)                                  │      │
│   │  Location: Inn                                                   │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   [LOD 1: Posture] ✓                                                       │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │  Action: SOCIALIZING                                             │      │
│   │  Mood: 😊 Content                                                │      │
│   │  Facing: Bob                                                     │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   [LOD 2: Dialogue] ✓                                                      │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │  Recent speech:                                                  │      │
│   │  "Good morning, Bob! You look tired. Sit, I'll bring tea."      │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   [LOD 3: Memory] 🔒 10 credits                                            │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │      │
│   │  Unlock to see Alice's active memories and current goals         │      │
│   │                                        [Unlock - 10 credits]     │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   [LOD 4: Psyche] 🔒 50 credits                                            │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │      │
│   │  Unlock to see Alice's personality eigenvectors and tensions     │      │
│   │                                        [Unlock - 50 credits]     │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   [LOD 5: Abyss] 🔒 200 credits                                            │
│   ┌─────────────────────────────────────────────────────────────────┐      │
│   │  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │      │
│   │  Unlock to peer into the irreducible mystery of Alice's being    │      │
│   │                                       [Unlock - 200 credits]     │      │
│   └─────────────────────────────────────────────────────────────────┘      │
│                                                                             │
│   ─────────────────────────────────────────────────────────────────────   │
│   [INHABIT Alice - 50 credits/10min]    [WHISPER to Alice - 20 credits]   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. INHABIT Mode (Browser)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  INHABIT: Alice (Innkeeper)                    [Credits: 100] [Exit ×]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        ALICE'S VIEW                                  │   │
│   │                                                                       │   │
│   │   You stand behind the counter of your inn. The fire crackles.       │   │
│   │   Bob sits at a table, stirring tea you just brought him.            │   │
│   │   Clara is in the corner, scribbling.                                │   │
│   │                                                                       │   │
│   │   Through the window, you see David walking toward the old well.     │   │
│   │   Something about that well... you remember Eve's warning.           │   │
│   │                                                                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  [Alice's Inner Voice]                                               │   │
│   │                                                                       │   │
│   │  "The inn is quiet this morning. But there's tension in the air.     │   │
│   │   Bob seems troubled. Clara keeps looking up from her notes.          │   │
│   │   And David... why is he going to the well again?"                    │   │
│   │                                                                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   What do you do?                                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                                                                       │   │
│   │  > ask bob what's troubling him_                                     │   │
│   │                                                                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Session: 3:42 remaining                    [Memory] [Relationships] [?]  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

```
src/
├── app/
│   ├── layout.tsx           # Root layout with auth
│   ├── page.tsx             # Landing page
│   ├── town/
│   │   ├── [id]/
│   │   │   ├── page.tsx     # Town Mesa
│   │   │   └── inhabit/
│   │   │       └── [citizen]/
│   │   │           └── page.tsx  # INHABIT mode
│   └── dashboard/
│       └── page.tsx         # User dashboard
├── components/
│   ├── town/
│   │   ├── Mesa.tsx         # Pixi.js 2D grid
│   │   ├── CitizenSprite.tsx
│   │   ├── CitizenPanel.tsx
│   │   ├── EventFeed.tsx
│   │   └── TimeControls.tsx
│   ├── inhabit/
│   │   ├── InhabitView.tsx
│   │   ├── InnerVoice.tsx
│   │   └── ActionInput.tsx
│   ├── paywall/
│   │   ├── LODGate.tsx
│   │   └── UpgradeModal.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Modal.tsx
│       └── ...
├── hooks/
│   ├── useTownStream.ts     # SSE connection
│   ├── useCredits.ts        # Credit management
│   └── useInhabit.ts        # INHABIT session
├── stores/
│   ├── townStore.ts         # Zustand store
│   └── userStore.ts
└── lib/
    ├── api.ts               # Backend API client
    └── sse.ts               # SSE utilities
```

### Key Components

```typescript
// components/town/Mesa.tsx
import { Stage, Container, Sprite } from '@pixi/react';
import { useTownStore } from '@/stores/townStore';

export function Mesa({ townId }: { townId: string }) {
  const { citizens, selectedCitizen, selectCitizen } = useTownStore();

  return (
    <Stage width={800} height={600}>
      <Container>
        {citizens.map(citizen => (
          <CitizenSprite
            key={citizen.id}
            citizen={citizen}
            selected={selectedCitizen?.id === citizen.id}
            onClick={() => selectCitizen(citizen)}
          />
        ))}
      </Container>
    </Stage>
  );
}


// components/town/CitizenPanel.tsx
import { LODGate } from '@/components/paywall/LODGate';
import { useCredits } from '@/hooks/useCredits';

export function CitizenPanel({ citizen }: { citizen: Citizen }) {
  const { credits, spend } = useCredits();

  return (
    <div className="citizen-panel">
      {/* LOD 0-2: Always visible */}
      <LODLevel level={0} citizen={citizen} />
      <LODLevel level={1} citizen={citizen} />
      <LODLevel level={2} citizen={citizen} />

      {/* LOD 3+: Gated */}
      <LODGate
        level={3}
        cost={10}
        credits={credits}
        onUnlock={() => spend(10, 'lod3')}
      >
        <LODLevel level={3} citizen={citizen} />
      </LODGate>

      <LODGate
        level={4}
        cost={50}
        credits={credits}
        onUnlock={() => spend(50, 'lod4')}
      >
        <LODLevel level={4} citizen={citizen} />
      </LODGate>

      <LODGate
        level={5}
        cost={200}
        credits={credits}
        onUnlock={() => spend(200, 'lod5')}
      >
        <LODLevel level={5} citizen={citizen} />
      </LODGate>
    </div>
  );
}


// hooks/useTownStream.ts
import { useEffect } from 'react';
import { useTownStore } from '@/stores/townStore';

export function useTownStream(townId: string) {
  const { addEvent, updateCitizen } = useTownStore();

  useEffect(() => {
    const eventSource = new EventSource(`/api/town/${townId}/stream`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      switch (data.type) {
        case 'dialogue':
          addEvent(data);
          break;
        case 'movement':
          updateCitizen(data.citizen_id, { position: data.position });
          break;
        case 'phase':
          useTownStore.setState({ phase: data.phase });
          break;
      }
    };

    return () => eventSource.close();
  }, [townId]);
}
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/town/{id}/state` | Full town state |
| GET | `/api/town/{id}/stream` | SSE event stream |
| GET | `/api/town/{id}/citizen/{id}` | Citizen details |
| GET | `/api/town/{id}/citizen/{id}/lod/{level}` | LOD-gated data |
| POST | `/api/town/{id}/inhabit/{citizen_id}` | Start INHABIT |
| POST | `/api/town/{id}/inhabit/{citizen_id}/action` | Submit INHABIT action |
| DELETE | `/api/town/{id}/inhabit/{citizen_id}` | End INHABIT |
| POST | `/api/town/{id}/branch` | Create branch |
| GET | `/api/user/credits` | User credit balance |
| POST | `/api/user/credits/spend` | Spend credits |
| POST | `/api/checkout/subscription` | Stripe checkout |
| POST | `/api/checkout/credits` | Credit purchase |

---

## Implementation Phases

### Phase W1: Foundation (Week 1-2)

| Task | Description |
|------|-------------|
| Project setup | Next.js + TypeScript + Tailwind |
| Auth | Clerk integration |
| API client | Fetch wrapper with auth |
| Basic routing | Landing, town, dashboard pages |

### Phase W2: Mesa (Week 3-4)

| Task | Description |
|------|-------------|
| Pixi.js setup | Canvas rendering |
| Citizen sprites | Position, selection, animation |
| SSE integration | Real-time updates |
| Event feed | Activity stream |

### Phase W3: Citizen Panel (Week 5)

| Task | Description |
|------|-------------|
| Panel component | Expandable details |
| LOD levels | Progressive disclosure |
| Paywall gates | Credit check, unlock flow |

### Phase W4: INHABIT (Week 6-7)

| Task | Description |
|------|-------------|
| INHABIT view | Scene description, inner voice |
| Action input | Text input with suggestions |
| Resistance UI | Force/rephrase flow |
| Session timer | Credit consumption |

### Phase W5: Monetization (Week 8)

| Task | Description |
|------|-------------|
| Stripe checkout | Subscription + credits |
| Dashboard | Usage, balance, subscription |
| Upgrade modals | Paywall UX |

---

## Mobile Considerations

Responsive design for core features:

| Screen | Mobile Adaptation |
|--------|-------------------|
| Mesa | Touch to select, pinch to zoom |
| Citizen Panel | Bottom sheet instead of sidebar |
| INHABIT | Full screen, swipe gestures |
| Event Feed | Collapsible |

**MVP**: Desktop-first, mobile responsive. Native app post-MVP.

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP | <2.5s | Lighthouse |
| FID | <100ms | Lighthouse |
| CLS | <0.1 | Lighthouse |
| TTI | <3s | Lighthouse |
| Overall score | >95 | Lighthouse |
| Bundle size | <200KB | webpack-bundle-analyzer |
| SSE latency | <500ms | Custom metric |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Pixi.js complexity | Medium | Medium | Start with simple sprites, add effects later |
| SSE reliability | Medium | High | Reconnection logic, offline state |
| Mobile performance | Medium | Medium | Lazy loading, virtualization |
| Auth complexity | Low | Medium | Use Clerk, proven solution |

---

## Continuation

```
⟿[IMPLEMENT]
/hydrate plans/agent-town/phase9-web-ui.md
handles:
  phase8: Requires INHABIT backend from Phase 8
  api: protocols/api/town.py endpoints
  streaming: protocols/api/sse.py
mission: Build React web UI for Agent Town
exit: Web UI deployed; demo town accessible; ledger.IMPLEMENT=touched
```

---

*"The interface is not a window to the system. The interface IS the system, made visible."*
