---
path: plans/crown-jewels-genesis-phase2-continuation
status: active
progress: 0
last_touched: 2025-12-18
touched_by: claude-opus-4-5
blocking: []
enables:
  - crown-jewels-genesis-phase2
parent: crown-jewels-genesis-phase2
session_notes: |
  2025-12-18: Continuation prompt created after Week 3 core completion.
  - FishbowlCanvas + SpectatorOverlay shipped (47 tests)
  - useAtelierStream enhanced with session subscription
  - Ready for integration + Week 4 BidQueue
phase_ledger:
  PLAN: complete
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.0
  returned: 0.0
---

# Crown Jewels Genesis Phase 2 — Continuation

> *"The workshop breathes. Now make it dance."*

## Context

Week 3 core deliverables complete:
- ✅ FishbowlCanvas.tsx (breathing border, content fade-in)
- ✅ SpectatorOverlay.tsx (eigenvector colors, stale cleanup)
- ✅ Spectator contracts (7 new types)
- ✅ useAtelierStream (session subscription, cursor updates)
- ✅ 47 tests passing

Remaining: Integration, BidQueue, Town connection, polish.

---

## Chunk 1: AtelierVisualization Integration (2-3 hours)

### Goal
Wire FishbowlCanvas into the existing AtelierVisualization so users can toggle between Gallery view and Live Fishbowl view.

### Steps

1. **Add view state for fishbowl**
```typescript
// AtelierVisualization.tsx
type View = 'commission' | 'collaborate' | 'gallery' | 'piece' | 'lineage' | 'fishbowl';
```

2. **Add Fishbowl tab to navigation**
```tsx
const tabs = [
  { key: 'gallery', label: 'Gallery' },
  { key: 'fishbowl', label: 'Live' },  // NEW
  { key: 'commission', label: 'Commission' },
  { key: 'collaborate', label: 'Collaborate' },
];
```

3. **Fishbowl view section**
```tsx
{view === 'fishbowl' && (
  <FishbowlCanvas
    sessionId={activeSessionId || 'demo'}
    artisan={activeArtisan}
    isLive={stream.isSessionLive}
    content={stream.sessionState?.content || ''}
    contentType={stream.sessionState?.contentType || 'text'}
    spectatorCount={stream.sessionState?.spectatorCount || 0}
    spectatorCursors={stream.spectatorCursors}
    showCursors={showSpectatorCursors}
    onCanvasClick={handleCanvasClick}
  />
)}
```

4. **Session selector component** (if multiple live sessions)
```tsx
function SessionSelector({ sessions, onSelect }: SessionSelectorProps) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2">
      {sessions.map(session => (
        <button
          key={session.id}
          onClick={() => onSelect(session.id)}
          className={cn(
            'px-3 py-1.5 rounded-full text-sm whitespace-nowrap',
            session.isLive ? 'bg-green-500/20 text-green-300' : 'bg-stone-700'
          )}
        >
          {session.artisanName} {session.isLive && '● LIVE'}
        </button>
      ))}
    </div>
  );
}
```

### Exit Criteria
- [ ] Fishbowl tab appears in Atelier navigation
- [ ] FishbowlCanvas renders when viewing live session
- [ ] Session selector allows switching between active sessions
- [ ] Spectator cursor toggle works
- [ ] 5+ integration tests

---

## Chunk 2: BidQueue Core (Week 4, Part 1) — 4 hours

### Goal
Let spectators submit bids to influence creation. The BidQueue shows pending bids; the artisan can accept/reject.

### Components

**BidQueuePanel.tsx**
```typescript
interface BidQueuePanelProps {
  bids: Bid[];
  isCreator: boolean;  // Can accept/reject
  onAccept?: (bidId: string) => void;
  onReject?: (bidId: string) => void;
  tokenBalance: number;
}

interface Bid {
  id: string;
  spectatorId: string;
  spectatorName?: string;
  bidType: 'suggestion' | 'direction' | 'constraint';
  content: string;
  tokenCost: number;
  submittedAt: string;
  status: 'pending' | 'accepted' | 'rejected';
}
```

**Visual Design**
- Vertical queue with newest at top
- Each bid card shows: spectator name, bid type icon, content preview, token cost
- Accepted bids glow green briefly, rejected fade out
- Use `useUnfurling` for entrance animation
- Creator sees accept/reject buttons; spectators see status

**BidSubmitModal.tsx**
```typescript
interface BidSubmitModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (bid: NewBid) => Promise<void>;
  tokenBalance: number;
  bidCosts: Record<BidType, number>;
}

interface NewBid {
  bidType: BidType;
  content: string;
}
```

### Hook: useTokenBalance
```typescript
function useTokenBalance(userId: string) {
  const [balance, setBalance] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  // Fetch initial balance
  // Subscribe to balance updates via SSE
  // Return { balance, spend, earn, isLoading }
}
```

### Backend Contracts (add to contracts.py)
```python
@dataclass(frozen=True)
class Bid:
    id: str
    session_id: str
    spectator_id: str
    spectator_name: str | None
    bid_type: str  # suggestion, direction, constraint
    content: str
    token_cost: int
    submitted_at: str
    status: str  # pending, accepted, rejected

@dataclass(frozen=True)
class BidListResponse:
    session_id: str
    bids: list[Bid]

@dataclass(frozen=True)
class BidAcceptRequest:
    session_id: str
    bid_id: str

@dataclass(frozen=True)
class BidRejectRequest:
    session_id: str
    bid_id: str
    reason: str | None = None
```

### Exit Criteria
- [ ] BidQueuePanel renders bid list with animations
- [ ] BidSubmitModal validates token balance before submit
- [ ] useTokenBalance tracks balance in real-time
- [ ] Creator can accept/reject bids
- [ ] 15+ tests for BidQueue components

---

## Chunk 3: Token Economy Visualization (Week 4, Part 2) — 3 hours

### Goal
Make token flow visible. Spectators see their balance, spending, earning. Creators see incoming tokens.

### Components

**TokenBalanceWidget.tsx**
```typescript
interface TokenBalanceWidgetProps {
  balance: number;
  recentChange?: { amount: number; direction: 'in' | 'out' };
  className?: string;
}
```
- Shows current balance with animated counter
- Flash green on earn, red on spend
- Use `useFlowing` for number transitions

**TokenFlowIndicator.tsx**
- Positioned on FishbowlCanvas edge
- Shows token particles flowing from spectators to canvas when bids accepted
- Uses LIVING_EARTH.honey for particles

**SpendHistoryPanel.tsx**
- Collapsible panel showing recent token activity
- Each row: timestamp, action, amount, balance after

### Exit Criteria
- [ ] Token balance visible in Atelier header
- [ ] Balance updates animate smoothly
- [ ] Spend history accessible
- [ ] 8+ tests

---

## Chunk 4: Town Integration (Week 5) — 4 hours

### Goal
Connect Atelier spectators to Town citizens. A citizen's eigenvector determines their cursor color in the Fishbowl.

### Steps

1. **Fetch citizen data for spectator**
```typescript
// When spectator joins, optionally link to their Town citizen
const citizenData = await townApi.getCitizen(citizenId);
const eigenvector = citizenData.eigenvector;
```

2. **Pass eigenvector to SpectatorOverlay**
Already supported! SpectatorCursor has `eigenvector?: number[]` and `eigenvectorToColor()` converts it.

3. **Add "Watch as Citizen" option**
```tsx
function WatchAsCitizenToggle({ citizens, onSelect }: WatchAsCitizenToggleProps) {
  // Dropdown to select which citizen persona to watch as
  // Changes cursor color and potentially bid preferences
}
```

4. **Citizen personality affects bid suggestions**
- Builders prefer structural bids
- Traders prefer value-oriented bids
- Scholars prefer conceptual bids
- Use archetype to pre-fill bid type selector

### Exit Criteria
- [ ] Spectator can link to Town citizen
- [ ] Cursor color reflects citizen eigenvector
- [ ] Bid type suggestions based on archetype
- [ ] 6+ integration tests

---

## Chunk 5: Polish & Joy (Week 6) — 4 hours

### Quality Enhancements

**Performance**
- [ ] Cursor position updates batched (max 10/sec)
- [ ] Memoize expensive eigenvector→color calculations
- [ ] Virtual scroll for bid queue (>20 bids)
- [ ] Lazy load SpectatorOverlay (only when showCursors=true)

**Accessibility**
- [ ] Keyboard navigation for bid queue
- [ ] Screen reader announcements for bid status changes
- [ ] Focus management in BidSubmitModal
- [ ] Color contrast check for all LIVING_EARTH colors

**Animation Refinements**
- [ ] Breathing border intensity responds to activity level (more spectators = faster breathing)
- [ ] Bid acceptance triggers celebratory particle burst
- [ ] Stale cursor fadeout uses `useFlowing` for smooth opacity
- [ ] Add subtle parallax to FishbowlCanvas on mouse move

**Error States**
- [ ] SSE disconnect shows reconnecting indicator
- [ ] Bid submit failure shows inline error (not toast)
- [ ] Token balance fetch failure shows stale indicator

**Teaching Mode Integration**
- [ ] Add TeachingCallout explaining eigenvector coloring
- [ ] Add TeachingCallout for token economy flow
- [ ] First-visit overlay for Fishbowl view

### Exit Criteria
- [ ] Performance: 60fps on scroll with 50 cursors
- [ ] Lighthouse accessibility score ≥95
- [ ] All error states have recovery paths
- [ ] 10+ polish-focused tests

---

## Quality Gates

Before marking Phase 2 complete:

1. **Test Coverage**
   - [ ] 100+ tests total for Phase 2 components
   - [ ] Property-based tests for eigenvector→color mapping
   - [ ] Chaos tests for SSE disconnect/reconnect

2. **Visual Regression**
   - [ ] Playwright visual snapshots for FishbowlCanvas states
   - [ ] Mobile/tablet/desktop variants captured

3. **Performance Baselines**
   - [ ] FishbowlCanvas render <16ms
   - [ ] Cursor update propagation <50ms
   - [ ] Bid queue reorder <100ms

4. **Documentation**
   - [ ] Update docs/systems-reference.md with Atelier spectator system
   - [ ] Add Atelier to docs/skills/crown-jewel-patterns.md examples

---

## Anti-Sausage Reminders

Before each chunk, ground in:

> *"Daring, bold, creative, opinionated but not gaudy"*

Ask:
- Is this token economy genuinely novel or just gamification?
- Does the eigenvector coloring add meaning or just visual noise?
- Would Kent use this feature or find it gimmicky?

Keep:
- The fishbowl metaphor (spectators watching creation)
- Eigenvector personality colors (connects Town to Atelier)
- Breathing animation (Ghibli-inspired life)

Kill if needed:
- Excessive particle effects
- Too many token types
- Unnecessary notifications

---

## Success Definition

Phase 2 is complete when:

1. **Functional**: Spectators can watch live creation, submit bids, see tokens flow
2. **Connected**: Town citizens bring their personality to Atelier
3. **Joyful**: The breathing canvas feels alive, not mechanical
4. **Tested**: 100+ tests, visual regression, performance baselines
5. **Documented**: Systems reference updated, patterns extracted

---

*"The persona is a garden, not a museum."*
— This phase makes Atelier a living space where creation happens visibly.
