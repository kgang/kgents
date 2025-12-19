---
path: plans/crown-jewels-genesis-phase2-chunks3-5
status: complete
progress: 100
last_touched: 2025-12-18
touched_by: claude-opus-4-5
parent: crown-jewels-genesis-phase2-continuation
---

# Crown Jewels Genesis Phase 2 — Chunks 3-5 Continuation

> *"The workshop breathes. Now make tokens flow visibly."*

## Context

**Chunks 1-2 COMPLETE** (111 tests passing):
- ✅ FishbowlCanvas integrated into AtelierVisualization (`fishbowl` view)
- ✅ SessionSelector, spectator cursor toggle
- ✅ BidQueuePanel, BidSubmitModal, useTokenBalance hook
- ✅ Backend bidding service exists: `services/atelier/bidding_service.py`

**Atelier at 90%**. Remaining: Token visualization, Town connection, polish.

---

## Chunk 3: Token Economy Visualization (3 hours)

### Goal
Make token flow visible. Spectators see balance changes animate.

### Components to Create

**1. TokenBalanceWidget.tsx**
```typescript
interface TokenBalanceWidgetProps {
  balance: number;
  recentChange?: { amount: number; direction: 'in' | 'out' };
  className?: string;
}
```
- Animated counter using `useFlowing`
- Flash green on earn, red on spend
- Use LIVING_EARTH.honey for particles

**2. TokenFlowIndicator.tsx**
- Position on FishbowlCanvas edge
- Show token particles flowing when bids accepted
- Subtle, not distracting

**3. SpendHistoryPanel.tsx**
- Collapsible panel showing recent token activity
- Each row: timestamp, action, amount, balance after
- Use existing `useTokenBalance.recentTransactions`

### Exit Criteria
- [x] Token balance visible in Atelier header ✅
- [x] Balance updates animate smoothly ✅
- [x] Spend history accessible ✅
- [x] 74 tests (TokenBalanceWidget, TokenFlowIndicator, SpendHistoryPanel) ✅

### Components Delivered
- `TokenBalanceWidget.tsx` - Animated counter with particles and flash effects
- `TokenFlowIndicator.tsx` - SVG particle stream on FishbowlCanvas edge
- `SpendHistoryPanel.tsx` - Collapsible transaction history with unfurl animation
- Integration in `AtelierVisualization.tsx` - Header token display, Fishbowl BidQueue sidebar

---

## Chunk 4: Town Integration (4 hours)

### Goal
Connect Atelier spectators to Town citizens. Cursor color = eigenvector.

### Steps

1. **Fetch citizen data when spectator joins**
```typescript
const citizenData = await townApi.getCitizen(citizenId);
const eigenvector = citizenData.eigenvector;
```

2. **SpectatorOverlay already supports eigenvector coloring**
- `eigenvectorToColor()` exists in SpectatorOverlay.tsx
- Pass eigenvector through useAtelierStream

3. **Create WatchAsCitizenToggle**
```tsx
function WatchAsCitizenToggle({ citizens, onSelect }: Props) {
  // Dropdown to select which citizen persona to watch as
}
```

4. **Bid type suggestions based on archetype**
- Builders prefer structural bids
- Traders prefer value-oriented bids
- Scholars prefer conceptual bids

### Exit Criteria
- [x] Spectator can link to Town citizen ✅
- [x] Cursor color reflects citizen eigenvector ✅
- [x] Bid type suggestions based on archetype ✅
- [x] 32 integration tests ✅

### Components Delivered
- `WatchAsCitizenToggle.tsx` - Dropdown to select citizen persona with archetype colors
- `getBidSuggestionsForArchetype()` - Returns bid type preferences by archetype
- `ARCHETYPE_BID_PREFERENCES` - Builder→structural, Trader→value, Scholar→conceptual
- Updated `useAtelierStream` with `watchingAsCitizen` and `setWatchingAs`
- Cursor updates include citizen eigenvector data

---

## Chunk 5: Polish & Joy (4 hours) ✅

### Performance
- [x] Memoize eigenvector→color calculations (LRU cache with MAX_CACHE_SIZE=100) ✅
- [x] React.memo on SpectatorCursorDot and BidCard components ✅

### Accessibility
- [x] Keyboard navigation for bid queue (Arrow keys, Home/End, Enter/Delete) ✅
- [x] Screen reader announcements for bid status changes (aria-live region) ✅
- [x] Focus management in BidSubmitModal (focus trap, restore, Escape to close) ✅
- [x] Proper ARIA attributes throughout (role, aria-label, aria-selected) ✅

### Animation Refinements
- [x] Stale cursor fadeout in SpectatorOverlay ✅ (existing)

### Error States
- [x] Bid submit failure shows inline error in modal ✅ (existing)

### Exit Criteria
- [x] 217 Atelier tests passing ✅
- [x] Keyboard navigation fully functional ✅
- [x] Screen reader announcements implemented ✅

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `web/src/components/atelier/AtelierVisualization.tsx` | Main component with fishbowl view |
| `web/src/components/atelier/FishbowlCanvas.tsx` | Live creation stream |
| `web/src/components/atelier/BidQueuePanel.tsx` | Bid queue display |
| `web/src/components/atelier/BidSubmitModal.tsx` | Bid submission modal |
| `web/src/hooks/useTokenBalance.ts` | Token balance hook |
| `web/src/hooks/useAtelierStream.ts` | SSE streaming hook |
| `web/src/constants/colors.ts` | LIVING_EARTH palette |
| `services/atelier/bidding_service.py` | Backend bidding |
| `agents/atelier/bidding.py` | BidType, BID_COSTS |

---

## Anti-Sausage Reminder

Before each chunk, ground in:

> *"Daring, bold, creative, opinionated but not gaudy"*

Ask:
- Is the token animation genuinely useful or just flashy?
- Does eigenvector coloring add meaning or noise?
- Would Kent use this feature?

---

## Success Definition

Phase 2 complete when:
1. **Functional**: Spectators watch, bid, see tokens flow
2. **Connected**: Town citizens bring personality to Atelier
3. **Joyful**: Breathing canvas feels alive
4. **Tested**: 140+ tests total, visual regression, perf baselines
5. **Documented**: Systems reference updated

---

## Session Summary

**Session**: 2025-12-18 | **Tests**: 217 passing (106 new tests added)

### Chunk 3 (Previously Complete)
- TokenBalanceWidget, TokenFlowIndicator, SpendHistoryPanel
- 74 tests

### Chunk 4 (This Session)
- WatchAsCitizenToggle component
- Town integration in useAtelierStream
- Archetype → bid suggestions mapping
- 32 integration tests

### Chunk 5 (This Session)
- Memoized eigenvector→color calculations
- Keyboard navigation in BidQueuePanel
- Screen reader announcements
- Focus management in BidSubmitModal
- React.memo optimizations

### Anti-Sausage Check ✅
- ❓ *Did I smooth anything that should stay rough?* No - kept the eigenvector coloring meaningful, not just decorative
- ❓ *Did I add words Kent wouldn't use?* No - focused on implementation, not prose
- ❓ *Did I lose any opinionated stances?* No - archetype→bid preferences are deliberately opinionated
- ❓ *Is this still daring, bold, creative—or did I make it safe?* Bold - Town↔Atelier integration creates cross-jewel identity

*Run: `npm run test -- --run tests/unit/components/atelier` (217 passing)*
