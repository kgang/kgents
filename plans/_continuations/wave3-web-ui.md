# Wave 3 Web UI - Continuation Prompt

## Status: COMPLETE (2025-12-16)

Wave 3 CLI is COMPLETE:
- `kg park` CLI with all commands (81 tests passing)
- ParkDomainBridge, DialogueMasks, synergy integration
- Crisis practice scenarios with 5 timer types

Wave 3 Web UI is COMPLETE:
- Park API routes (`protocols/api/park.py`)
- TypeScript types and API client
- React components: TimerDisplay, PhaseTransition, MaskSelector, ConsentMeter
- ParkScenario page with full functionality
- Route added at `/park`

## Implementation Details

### Components Needed

1. **ParkScenarioView** - Main scenario page
   - Timer display with countdown and progress bar
   - Crisis phase diagram (NORMAL → INCIDENT → RESPONSE → RECOVERY)
   - Consent debt meter
   - Forces remaining indicator

2. **MaskSelector** - Mask selection UI
   - 8 mask cards with archetype icons
   - Eigenvector radar preview
   - Don/doff controls

3. **TimerDisplay** - Real-time countdown
   - Status-colored progress bar (green → yellow → red)
   - Emoji indicators ([>], [!], [X])
   - Accelerated mode indicator

4. **PhaseTransition** - Crisis phase controls
   - Visual state machine diagram
   - Valid transition buttons
   - Transition history

### API Endpoints to Add

```python
# In protocols/api/routes/park.py
GET  /api/park/scenario          # Current scenario state
POST /api/park/scenario/start    # Start new scenario
POST /api/park/scenario/tick     # Advance timers
POST /api/park/scenario/phase    # Transition phase
POST /api/park/scenario/mask     # Don/doff mask
POST /api/park/scenario/complete # End scenario
```

### Key Files

- `impl/claude/web/src/pages/ParkScenario.tsx` - Main page
- `impl/claude/web/src/components/park/` - Park-specific components
- `impl/claude/protocols/api/routes/park.py` - API routes
- `impl/claude/agents/park/domain_bridge.py` - Backend (exists)
- `impl/claude/agents/park/masks.py` - Masks (exists)

### Reference

- CLI handler: `protocols/cli/handlers/park.py` (display patterns)
- Existing pages: `web/src/pages/GestaltLive.tsx` (streaming pattern)
- Plan: `plans/crown-jewels-enlightened.md` (Wave 3 section)

### Success Criteria

- [x] Timer countdown updates in real-time (auto-tick with 1s interval)
- [x] Mask selection shows eigenvector radar (inline SVG radar chart)
- [x] Phase transitions animate smoothly (visual state machine)
- [ ] Scenario completion captures to Brain (synergy) - Backend ready, needs Brain API integration

### Files Created

**Backend:**
- `impl/claude/protocols/api/park.py` - Full REST API (scenario, masks, status)

**Frontend:**
- `impl/claude/web/src/api/types.ts` - Park types added
- `impl/claude/web/src/api/client.ts` - parkApi client added
- `impl/claude/web/src/components/park/TimerDisplay.tsx`
- `impl/claude/web/src/components/park/PhaseTransition.tsx`
- `impl/claude/web/src/components/park/MaskSelector.tsx`
- `impl/claude/web/src/components/park/ConsentMeter.tsx`
- `impl/claude/web/src/components/park/index.ts`
- `impl/claude/web/src/pages/ParkScenario.tsx`
- `impl/claude/web/src/App.tsx` - Route `/park` added

### Usage

```bash
# Start backend
cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Start frontend
cd impl/claude/web && npm run dev

# Visit http://localhost:3000/park
```
