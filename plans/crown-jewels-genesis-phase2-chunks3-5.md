---
path: plans/crown-jewels-genesis-phase2-chunks3-5
status: ready
progress: 0
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
- [ ] Token balance visible in Atelier header
- [ ] Balance updates animate smoothly
- [ ] Spend history accessible
- [ ] 8+ tests

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
- [ ] Spectator can link to Town citizen
- [ ] Cursor color reflects citizen eigenvector
- [ ] Bid type suggestions based on archetype
- [ ] 6+ integration tests

---

## Chunk 5: Polish & Joy (4 hours)

### Performance
- [ ] Cursor updates batched (max 10/sec)
- [ ] Memoize eigenvector→color calculations
- [ ] Virtual scroll for bid queue (>20 bids)
- [ ] Lazy load SpectatorOverlay

### Accessibility
- [ ] Keyboard navigation for bid queue
- [ ] Screen reader announcements for bid status
- [ ] Focus management in BidSubmitModal
- [ ] Color contrast check for LIVING_EARTH colors

### Animation Refinements
- [ ] Breathing border intensity responds to activity level
- [ ] Bid acceptance triggers celebratory particle burst
- [ ] Stale cursor fadeout uses `useFlowing`

### Error States
- [ ] SSE disconnect shows reconnecting indicator
- [ ] Bid submit failure shows inline error
- [ ] Token balance fetch failure shows stale indicator

### Exit Criteria
- [ ] 60fps on scroll with 50 cursors
- [ ] Lighthouse accessibility ≥95
- [ ] 10+ polish-focused tests

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

*Run: `npm run test -- --run tests/unit/components/atelier` (currently 111 passing)*
