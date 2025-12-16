# Crown Jewels Wave 4 - Continuation Prompt

## Context: The Seven Jewel Crown

The Crown is 7 jewels forming ONE unified experience engine:

| Tier | Jewels | Status |
|------|--------|--------|
| **1 (Hero)** | Brain, Gestalt, Gardener | CLI complete, Web 80% |
| **2 (Extension)** | Atelier, Coalition | Synergies complete, Web exists |
| **3 (Full)** | Park, Domain | CLI complete, **Web just shipped** |

### What's Complete (as of 2025-12-16)

**Infrastructure:**
- [x] Wave 0: All 5 foundations (Path visibility, Observer switching, Polynomial diagram, Synergy bus, Animations)
- [x] 607+ tests passing across all jewels
- [x] AGENTESE path display on all CLI commands
- [x] SynergyEventBus with auto-capture hooks

**Per-Jewel:**
- [x] Brain: Capture, topology 3D, crystals ✓
- [x] Gestalt: Analysis, health grading, drift, 3D topology, Web page ✓
- [x] Gestalt Live: Real-time streaming infrastructure visualization ✓
- [x] Gardener: N-Phase sessions, tending calculus, Garden state ✓
- [x] Atelier: Bidding, eigenvector personality, Brain synergy ✓
- [x] Coalition: Formation, Brain context enrichment, Gardener bridge ✓
- [x] Park: Crisis practice, masks, timers, **Web UI just shipped** ✓
- [x] Domain: Compliance drills, timer infrastructure, Brain synergy ✓

**Web Routes Now Available:**
- `/town/:townId` - Agent Town simulation
- `/atelier` - Artisan collaboration
- `/gallery` - Component gallery
- `/brain` - Holographic memory 3D
- `/gestalt` - Code architecture analysis
- `/gestalt/live` - Real-time infrastructure
- `/gardener` - Development sessions
- `/garden` - Garden state visualization
- `/park` - **NEW: Crisis practice scenarios**
- `/emergence` - Emergence demo

## What's Missing: The Unified Crown

The jewels exist but don't feel like ONE system. The Mirror Test fails:

```
- [ ] Tasteful: Does the Hero Path feel curated, not sprawling?
- [ ] Joy-inducing: Do the animations and feedback spark delight?
- [ ] Composable: Can I chain AGENTESE paths?
- [ ] Observer-dependent: Do I see different things from different perspectives?
- [ ] Autopoietic: Does the Gardener help me evolve kgents itself?
- [ ] Categorical: Is the math visible, not just infrastructure?
```

### Specific Gaps

1. **No Unified Navigation** - Each page feels separate, not part of one crown
2. **No Cross-Jewel Context** - Brain crystals don't surface in other jewels
3. **Observer Switching UI** - Exists in CLI, not prominent in Web
4. **Polynomial Visualization** - Gardener has it, others don't show their state machines
5. **Hero Path Not Guided** - No onboarding flow through Brain → Gestalt → Gardener
6. **Synergy Notifications** - Work in CLI, silent in Web

## Recommended Next Steps

### Option A: Hero Path Onboarding (High Impact)
Create a guided first-experience that proves AGENTESE:

```
1. Welcome → "Let's explore your codebase with the Crown"
2. Gestalt scan → See health grade, architecture
3. Brain auto-capture → "Architecture snapshot saved"
4. Gardener session → "Ready to improve it?"
5. Synergy visible → Show connections between jewels
```

### Option B: Cross-Jewel Context Panel (Medium Impact)
Add a collapsible "Crown Context" panel to every page showing:
- Recent Brain crystals relevant to current view
- Current Gardener session state (if any)
- Synergy events from other jewels
- AGENTESE path for current page

### Option C: Unified Crown Dashboard (High Effort)
Create `/crown` as the true home showing all 7 jewels:
- Real-time status of each jewel
- Recent activity across all
- Polynomial state machines visible
- Quick-launch to any jewel

### Option D: Web Synergy Notifications (Quick Win)
Add toast notifications when synergies fire:
```tsx
// When Gestalt completes analysis
toast.success("✓ Architecture captured to Brain", {
  description: "Crystal: impl/claude/ architecture",
  action: { label: "View", onClick: () => navigate('/brain') }
});
```

## Key Files

**Plan:** `plans/crown-jewels-enlightened.md` (master strategy)
**API:** `protocols/api/app.py` (all routers)
**Layout:** `web/src/components/layout/Layout.tsx` (nav bar)
**Pages:** `web/src/pages/*.tsx`
**Synergy:** `protocols/synergy/` (event bus, handlers)

## Success Criteria

> **Can a new user experience the "wow moment" in under 5 minutes?**

The wow moment = seeing that 7 jewels are actually ONE engine:
1. Action in one jewel affects another
2. AGENTESE paths are visible and learnable
3. Observer-dependent perception is demonstrable
4. Polynomial state machines are navigable
5. Joy in every interaction

## Session Prompt

```
CROWN JEWEL UNIFIER: Read this file and crown-jewels-enlightened.md.

The jewels are built. Now make them feel like ONE crown.

Priority:
1. Choose one option (A-D) or propose alternative
2. Implement cross-jewel awareness
3. Make synergies visible in Web
4. Add guided hero path
5. Pass the Mirror Test

The target: "wow moment" in < 5 minutes for new user.
```

---

*Created: 2025-12-16*
*Context: Park Web UI just shipped, all 7 jewels have basic Web presence*
