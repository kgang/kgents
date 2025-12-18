---
path: plans/crown-jewels-genesis-phase2
status: active
progress: 35
last_touched: 2025-12-18
touched_by: claude-opus-4-5
blocking: []
enables:
  - core-apps/atelier-experience
  - monetization/token-economy
session_notes: |
  2025-12-18: Plan created after Phase 1 Foundation completion.
  - Phase 1 COMPLETE: useGrowing (31 tests), useUnfurling (38 tests), useFlowing (28 tests)
  - Living Earth colors, OrganicToast, BreathingContainer, UnfurlPanel all shipped
  - 213 hook tests passing

  2025-12-18 PM: Week 3 Chunk 1-2 COMPLETE
  - FishbowlCanvas.tsx: Breathing border with LIVING_EARTH.amber, spectator count badge
  - SpectatorOverlay.tsx: Eigenvector-based coloring, stale cursor cleanup
  - Spectator contracts added to services/atelier/contracts.py
  - useAtelierStream enhanced with session subscription + cursor updates
  - 35+ tests for FishbowlCanvas and SpectatorOverlay
  Next: Integration into AtelierVisualization, then Week 4 BidQueue
phase_ledger:
  PLAN: complete
  RESEARCH: complete
  DEVELOP: in_progress
  STRATEGIZE: touched
  CROSS-SYNERGIZE: pending
  IMPLEMENT: in_progress
  QA: pending
  TEST: in_progress
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.05
  returned: 0.0
---

# Crown Jewels Genesis: Phase 2 — Atelier Rebuild

> *"The workshop breathes. Spectators gather around the fishbowl, watching creation unfold."*

**Parent Plan**: `plans/crown-jewels-genesis.md` (Phase 2 of 5)
**Duration**: Weeks 3-5
**Foundation**: Phase 1 complete (97 animation tests, 3 hooks, 3 components)

---

## Overview

Phase 2 rebuilds the Atelier Crown Jewel frontend with:
- **FishbowlCanvas** — Live creation stream with breathing border
- **BidQueue** — Token-based spectator influence
- **Exquisite Cadaver** — Fog/reveal handoff visualization

All components use Phase 1 animation primitives (`useGrowing`, `useUnfurling`, `useFlowing`).

---

## Completed Foundation (Phase 1)

| Deliverable | Location | Tests |
|-------------|----------|-------|
| `useGrowing` | `web/src/hooks/useGrowing.ts` | 31 |
| `useUnfurling` | `web/src/hooks/useUnfurling.ts` | 38 |
| `useFlowing` | `web/src/hooks/useFlowing.ts` | 28 |
| `LIVING_EARTH` palette | `web/src/constants/colors.ts` | — |
| `OrganicToast` | `web/src/components/joy/OrganicToast.tsx` | — |
| `BreathingContainer` | `web/src/components/joy/BreathingContainer.tsx` | — |
| `UnfurlPanel` | `web/src/components/joy/UnfurlPanel.tsx` | — |

---

## Week 3: FishbowlCanvas Core

### Goal
Live creation stream with organic breathing border and spectator presence.

### Deliverables

| File | Description |
|------|-------------|
| `web/src/components/atelier/FishbowlCanvas.tsx` | Main canvas with breathing border |
| `web/src/components/atelier/SpectatorOverlay.tsx` | Opt-in cursor visibility |
| `web/src/hooks/useAtelierStream.ts` | SSE subscription for live updates |
| `web/src/components/atelier/AtelierVisualization.tsx` | Integration point |

### FishbowlCanvas Specification

```typescript
interface FishbowlCanvasProps {
  sessionId: string;
  artisan: ArtisanSummary | null;
  stream: UseAtelierStreamResult;
  spectatorCount: number;
  content: string;
  contentType: 'image' | 'text' | 'code';
  isLive: boolean;
  onCanvasClick?: (position: { x: number; y: number }) => void;
}

interface FishbowlCanvasState {
  // Breathing animation (3-4s cycle)
  breathPhase: number;
  borderGlow: number;

  // Content display
  contentOpacity: number;
  scale: number;

  // Spectator presence
  spectatorCursors: Map<string, CursorPosition>;
}
```

### Visual Design

```
┌─────────────────────────────────────────────────────┐
│ ╭───────────────────────────────────────────────╮   │
│ │                                               │   │
│ │        [LIVE CREATION CANVAS]                │   │ ← Breathing border
│ │                                               │   │   (LIVING_EARTH.amber)
│ │    Content renders here with organic         │   │
│ │    fade-in using useGrowing                  │   │
│ │                                               │   │
│ │           👁 47 watching                      │   │ ← Spectator count
│ ╰───────────────────────────────────────────────╯   │
│                                                     │
│  [BID]  [FOLLOW]  [SHARE]                          │ ← Action buttons
└─────────────────────────────────────────────────────┘
```

### Breathing Border Implementation

```typescript
// Use existing useBreathing hook pattern
const { phase, intensity } = useBreathing({
  duration: 4000,  // 4s full cycle
  baseIntensity: 0.3,
  maxIntensity: 0.6
});

// Border style with Living Earth colors
const borderStyle = {
  boxShadow: `
    0 0 ${20 * intensity}px ${LIVING_EARTH.amber}40,
    inset 0 0 ${10 * intensity}px ${LIVING_EARTH.honey}20
  `,
  borderColor: `rgba(212, 165, 116, ${0.3 + intensity * 0.4})`,
  transition: 'box-shadow 100ms ease-out'
};
```

### SpectatorOverlay Specification

```typescript
interface SpectatorOverlayProps {
  spectators: SpectatorCursor[];
  showCursors: boolean;
  eigenvectorColors: boolean; // Color by citizen eigenvector
}

interface SpectatorCursor {
  id: string;
  position: { x: number; y: number };
  citizenId?: string; // If linked to Town citizen
  eigenvector?: number[]; // For color mapping
  lastUpdate: number;
}
```

### Exit Criteria
- [x] FishbowlCanvas renders with breathing border animation
- [x] SpectatorOverlay shows cursor positions when enabled
- [x] useAtelierStream connects to SSE endpoint
- [x] Content fades in using useGrowing on update
- [x] 15+ new tests for FishbowlCanvas (35+ delivered)
- [ ] Integration into AtelierVisualization (pending)

---

## Week 4: BidQueue & Token Economy

### Goal
Enable spectators to influence creation through token-based bidding.

### Deliverables

| File | Description |
|------|-------------|
| `web/src/components/atelier/BidQueue.tsx` | Token-based influence panel |
| `web/src/components/atelier/BidCard.tsx` | Individual bid display |
| `web/src/hooks/useTokenAnimation.ts` | Arc trajectory for token spend |
| `web/src/components/atelier/TokenBalance.tsx` | Wallet display with animation |
| `services/atelier/contracts.py` | SpectatorJoinRequest/Response, BidQueueResponse |

### BidQueue Specification

```typescript
interface BidQueueProps {
  sessionId: string;
  spectatorId: string;
  tokenBalance: number;
  activeBids: Bid[];
  onBid: (bid: BidRequest) => void;
}

interface Bid {
  id: string;
  type: 'color' | 'direction' | 'challenge' | 'boost';
  content: string;
  tokens: number;
  spectatorId: string;
  spectatorName: string;
  status: 'pending' | 'accepted' | 'acknowledged' | 'ignored';
  createdAt: number;
}

// Token costs (from plan)
const BID_COSTS = {
  color: 1,      // "Suggest a color"
  direction: 1,  // "Suggest a direction"
  challenge: 5,  // "Challenge the builder"
  boost: 2,      // "Boost current path"
} as const;
```

### Token Animation

```typescript
// Arc trajectory from wallet to bid queue
export function useTokenAnimation(options: TokenAnimationOptions) {
  const { from, to, tokenCount, onComplete } = options;

  // Use bezier path from useFlowing
  const path = createCurvedPath(from, to, 0.4);

  const { particles, start } = useFlowing(path, {
    particleCount: Math.min(tokenCount, 5),
    duration: 800,
    particleSize: 6,
    loop: false,
    onParticleComplete: (id) => {
      if (id === 'particle-0') onComplete?.();
    }
  });

  return { particles, triggerSpend: start };
}
```

### Visual Design

```
┌─────────────────────────────────┐
│  BID QUEUE            💰 47    │ ← Token balance
├─────────────────────────────────┤
│ ┌─────────────────────────────┐ │
│ │ 🎨 Suggest Color      [1T] │ │ ← Bid type buttons
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 🧭 Suggest Direction  [1T] │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ 🔥 Challenge          [5T] │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ ⚡ Boost Current Path [2T] │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│  PENDING BIDS                   │
│ ┌─────────────────────────────┐ │
│ │ 👤 alice: "More blue" (1T) │ │ ← Growing entrance
│ │ 🕐 Waiting...              │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### AGENTESE Extensions

```python
# services/atelier/node.py additions

@node(
    path="world.atelier.session.spectator.join",
    aspect=Aspect.DEFINE,
    effects=[Effect.GRANT_ACCESS],
)
async def spectator_join(request: SpectatorJoinRequest) -> SpectatorJoinResponse:
    """Join session as spectator, receive initial token allocation."""
    ...

@node(
    path="world.atelier.session.bid.queue",
    aspect=Aspect.MANIFEST,
)
async def get_bid_queue(session_id: str) -> BidQueueResponse:
    """Get current bid queue for session."""
    ...

@node(
    path="world.atelier.session.bid.submit",
    aspect=Aspect.DEFINE,
    effects=[Effect.TRANSFER_TOKENS, Effect.NOTIFY_BUILDER],
)
async def submit_bid(request: BidSubmitRequest) -> BidSubmitResponse:
    """Submit a bid using tokens."""
    ...
```

### Exit Criteria
- [ ] BidQueue displays bid options with token costs
- [ ] Token animation plays on bid submission
- [ ] Pending bids appear with growing entrance
- [ ] TokenBalance updates in real-time
- [ ] AGENTESE nodes registered and functional
- [ ] 20+ new tests for BidQueue

---

## Week 5: Exquisite Cadaver Mode

### Goal
Fog/reveal handoff visualization with dramatic reveal moment.

### Deliverables

| File | Description |
|------|-------------|
| `web/src/components/atelier/HandoffVisualization.tsx` | Fog/reveal with edge-only visibility |
| `web/src/components/atelier/FogOverlay.tsx` | CSS clip-path fog effect |
| `web/src/hooks/useExquisiteCadaver.ts` | Round-based session state |
| `web/src/components/atelier/RevealMoment.tsx` | Dramatic fog lift animation |
| `web/src/components/atelier/MemoryTheatre.tsx` | Stub for M-gent crystal playback |

### HandoffVisualization Specification

```typescript
interface HandoffVisualizationProps {
  sessionId: string;
  currentRound: number;
  totalRounds: number;
  currentBuilder: ArtisanSummary;
  visibilityPercent: number; // Default 10% - edge only
  isRevealing: boolean;
  onRoundComplete: () => void;
}

interface ExquisiteCadaverState {
  rounds: Round[];
  currentRound: number;
  phase: 'waiting' | 'creating' | 'handoff' | 'revealing' | 'complete';
  revealProgress: number; // 0-1 during reveal animation
}

interface Round {
  builderId: string;
  builderName: string;
  startTime: number;
  endTime?: number;
  canvasSnapshot?: string; // Base64 or URL
}
```

### Fog Effect Implementation

```typescript
// FogOverlay uses CSS clip-path for performant masking
interface FogOverlayProps {
  visibilityPercent: number; // 0.1 = 10% visible (right edge)
  direction: 'left' | 'right' | 'top' | 'bottom';
  isRevealing: boolean;
}

// Fog lifts using useUnfurling for dramatic effect
const FogOverlay: React.FC<FogOverlayProps> = ({
  visibilityPercent,
  direction,
  isRevealing
}) => {
  const { progress, unfurl, style } = useUnfurling({
    direction: direction === 'right' ? 'left' : 'right',
    duration: 2000, // Slow, dramatic reveal
    initialOpen: false,
  });

  useEffect(() => {
    if (isRevealing) unfurl();
  }, [isRevealing]);

  // When not revealing, show only edge
  const visiblePercent = isRevealing
    ? visibilityPercent + (1 - visibilityPercent) * progress
    : visibilityPercent;

  return (
    <div
      className="absolute inset-0 pointer-events-none"
      style={{
        clipPath: `inset(0 0 0 ${(1 - visiblePercent) * 100}%)`,
        background: `linear-gradient(
          to right,
          ${LIVING_EARTH.soil}ee 0%,
          ${LIVING_EARTH.soil}88 70%,
          transparent 100%
        )`,
        ...style
      }}
    />
  );
};
```

### Visual Design: Handoff Flow

```
ROUND 1: Builder A                    ROUND 2: Builder B
┌─────────────────────────────┐       ┌─────────────────────────────┐
│                             │       │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│░░░░│
│    [FULL CANVAS VISIBLE]    │  ──►  │▓▓▓▓▓▓▓ FOG ▓▓▓▓▓▓▓▓│edge│
│    Builder A creates        │       │▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│vis │
│                             │       │                     │    │
└─────────────────────────────┘       └─────────────────────────────┘

REVELATION: Fog Lifts
┌─────────────────────────────┐       ┌─────────────────────────────┐
│▓▓▓▓▓▓▓▓▓▓▓│░░░░░░░░░░░░░░│  ──►  │░░░░░░░░░░░░░░░░░░░░░░░░░░░│
│▓▓▓▓▓FOG▓▓▓│ [REVEALING]  │       │    [FULL PIECE VISIBLE]    │
│▓▓▓▓▓▓▓▓▓▓▓│░░░░░░░░░░░░░░│       │░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└─────────────────────────────┘       └─────────────────────────────┘
                                               ✨ CELEBRATION
```

### RevealMoment Specification

```typescript
interface RevealMomentProps {
  isActive: boolean;
  participants: ArtisanSummary[];
  onComplete: () => void;
}

// Dramatic reveal with:
// 1. Fog lifts slowly (2s)
// 2. Participants appear in corner bubbles
// 3. Confetti/celebration effect
// 4. "See the full creation" toast
```

### useExquisiteCadaver Hook

```typescript
export function useExquisiteCadaver(sessionId: string) {
  const [state, setState] = useState<ExquisiteCadaverState>({
    rounds: [],
    currentRound: 0,
    phase: 'waiting',
    revealProgress: 0,
  });

  // Subscribe to SSE for round updates
  const stream = useAtelierStream(sessionId);

  // Handle round transitions
  const advanceRound = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentRound: prev.currentRound + 1,
      phase: 'handoff',
    }));
  }, []);

  // Trigger final reveal
  const triggerReveal = useCallback(() => {
    setState(prev => ({ ...prev, phase: 'revealing' }));
  }, []);

  return {
    ...state,
    advanceRound,
    triggerReveal,
    isMyTurn: /* check against current user */,
    visibleCanvas: /* computed based on round and role */,
  };
}
```

### Exit Criteria
- [ ] HandoffVisualization shows fog with edge visibility
- [ ] Fog lifts dramatically using useUnfurling
- [ ] useExquisiteCadaver manages round state
- [ ] RevealMoment shows celebration animation
- [ ] MemoryTheatre stub exists for future M-gent integration
- [ ] 25+ new tests for Exquisite Cadaver mode

---

## Testing Strategy

### By Type (T-gent Taxonomy)

| Type | Tests | Focus |
|------|-------|-------|
| **Type I: Contracts** | 30 | Props validation, state transitions |
| **Type II: Saboteurs** | 20 | Edge cases, empty states, disconnection |
| **Type III: Spies** | 15 | Callback verification, event handlers |
| **Type IV: Properties** | 10 | Animation bounds, progress monotonicity |
| **Type V: Performance** | 5 | Render cycles, memory leaks |

### Key Test Scenarios

```typescript
// FishbowlCanvas
describe('FishbowlCanvas', () => {
  it('applies breathing animation to border');
  it('fades in content using useGrowing');
  it('shows spectator count badge');
  it('handles disconnection gracefully');
});

// BidQueue
describe('BidQueue', () => {
  it('disables bids when insufficient tokens');
  it('plays token animation on submit');
  it('shows pending bids with growing entrance');
  it('updates balance after bid accepted');
});

// HandoffVisualization
describe('HandoffVisualization', () => {
  it('shows only edge when visibilityPercent=0.1');
  it('lifts fog during reveal phase');
  it('plays celebration on complete');
});
```

### Performance Baselines

```typescript
it('FishbowlCanvas renders < 16ms', () => {
  const start = performance.now();
  render(<FishbowlCanvas {...props} />);
  expect(performance.now() - start).toBeLessThan(16);
});

it('BidQueue handles 100 pending bids', () => {
  const bids = Array.from({ length: 100 }, (_, i) => mockBid(i));
  const { container } = render(<BidQueue bids={bids} {...props} />);
  expect(container.querySelectorAll('.bid-card')).toHaveLength(100);
});
```

---

## Integration Points

### Existing AGENTESE Paths

| Path | Usage |
|------|-------|
| `world.atelier.session.manifest` | Load session data |
| `world.atelier.session.subscribe` | SSE stream |
| `world.atelier.gallery.manifest` | Completed artifacts |

### New AGENTESE Paths (Week 4)

| Path | Aspect | Description |
|------|--------|-------------|
| `world.atelier.session.spectator.join` | DEFINE | Join as spectator |
| `world.atelier.session.bid.queue` | MANIFEST | Get current bids |
| `world.atelier.session.bid.submit` | DEFINE | Submit a bid |

### Three-Bus Integration

```python
# services/atelier/bus_wiring.py
from services.town.bus_wiring import wire_data_to_synergy

# Atelier → Town synergy: Spectators become citizens
async def wire_atelier_to_town():
    await synergy_bus.subscribe(
        "atelier.spectator.joined",
        lambda evt: town_service.register_visitor(evt.spectator_id)
    )
```

---

## Dependencies

| System | Usage | Status |
|--------|-------|--------|
| `useGrowing` | Content fade-in | ✅ Ready |
| `useUnfurling` | Fog reveal | ✅ Ready |
| `useFlowing` | Token animation | ✅ Ready |
| `useBreathing` | Border animation | ✅ Exists |
| `useAtelierStream` | SSE subscription | 🔄 Enhance |
| AGENTESE gateway | Node registration | ✅ Ready |
| SynergyBus | Cross-jewel events | ✅ Ready |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| SSE connection drops | Reconnection with exponential backoff |
| Token animation performance | Limit particles, use GPU compositing |
| Fog clip-path on mobile | Fallback to opacity-based fog |
| Exquisite reveal timing | Server-authoritative countdown |

---

## Success Metrics

### Quantitative

| Metric | Target |
|--------|--------|
| New components | 8 |
| New tests | 80+ |
| Atelier test total | 400+ (from 316) |
| Animation frame rate | >55fps |
| Time to first bid | <5s from join |

### Qualitative (The Joy Test)

- [ ] Breathing border feels alive, not mechanical
- [ ] Token spend animation creates satisfaction
- [ ] Fog reveal is genuinely dramatic
- [ ] First-time spectator can bid within 30 seconds

---

## Chunks (Parallelizable Work)

### Chunk 1: FishbowlCanvas Base (4 hours)
- Create FishbowlCanvas component structure
- Implement breathing border with useBreathing
- Add spectator count badge
- **Exit criteria**: Canvas renders with animated border

### Chunk 2: SpectatorOverlay (2 hours)
- Create cursor tracking component
- Implement eigenvector color mapping
- Wire to SSE cursor events
- **Exit criteria**: Cursors appear and move

### Chunk 3: BidQueue UI (3 hours)
- Create BidQueue layout
- Implement BidCard with growing entrance
- Add TokenBalance display
- **Exit criteria**: UI renders with mock data

### Chunk 4: Token Animation (2 hours)
- Implement useTokenAnimation
- Wire to BidQueue submit
- Add balance update animation
- **Exit criteria**: Tokens fly to queue on bid

### Chunk 5: AGENTESE Nodes (3 hours)
- Add spectator.join node
- Add bid.queue and bid.submit nodes
- Wire contracts and validation
- **Exit criteria**: Nodes respond correctly

### Chunk 6: Fog System (3 hours)
- Create FogOverlay component
- Implement clip-path masking
- Wire to useUnfurling for reveal
- **Exit criteria**: Fog hides 90% of canvas

### Chunk 7: Exquisite State (2 hours)
- Implement useExquisiteCadaver hook
- Handle round transitions
- Wire to SSE events
- **Exit criteria**: State tracks rounds correctly

### Chunk 8: Reveal Moment (2 hours)
- Create RevealMoment component
- Add celebration effects
- Wire to round completion
- **Exit criteria**: Dramatic reveal plays

### Chunk 9: Integration & Tests (4 hours)
- Integrate into AtelierVisualization
- Write comprehensive tests
- Performance optimization
- **Exit criteria**: 80+ tests passing

---

## Cross-References

- **Parent Plan**: `plans/crown-jewels-genesis.md`
- **Atelier Spec**: `plans/core-apps/atelier-experience.md`
- **Animation Hooks**: `web/src/hooks/useGrowing.ts`, `useUnfurling.ts`, `useFlowing.ts`
- **Color Palette**: `web/src/constants/colors.ts` (LIVING_EARTH)
- **Joy Components**: `web/src/components/joy/`
- **Test Patterns**: `docs/skills/test-patterns.md`

---

*"The workshop breathes. Spectators gather. Creation unfolds."*

*Plan created: 2025-12-18 | Phase 1 complete | Phase 2 ready to begin*
