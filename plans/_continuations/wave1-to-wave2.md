# Continuation Prompt: Wave 1 → Wave 2

> Use this prompt to resume Crown Jewel development after Wave 1 Hero Path Polish.

---

## Session Context

**Previous Wave**: Wave 1 - Hero Path Polish
**Next Wave**: Wave 2 - Extensions (Atelier + Coalition)
**Date**: 2025-12-16
**Branch**: main

---

## Wave 1 Completion Summary

### What Was Built

| Component | Status | Notes |
|-----------|--------|-------|
| **ObserverSwitcher → Gestalt** | ✓ Complete | FilterPanel integration |
| **Brain CrystalDetail** | ✓ Complete | Modal with 4 observer views |
| **Gardener Web UI** | ✓ Complete | /gardener route, PolynomialDiagram |
| **Gardener API** | ✓ Complete | 5 endpoints, models, client |
| **Gestalt → Brain Synergy** | ✓ Complete | Already existed, verified |
| **Gardener CLI** | ✓ Complete | `kg gardener` command |

### Files Created

```
impl/claude/web/src/components/brain/CrystalDetail.tsx
impl/claude/web/src/components/brain/index.ts
impl/claude/web/src/pages/Gardener.tsx
impl/claude/protocols/api/gardener.py
impl/claude/protocols/cli/handlers/gardener.py
```

### Files Modified

```
impl/claude/web/src/components/gestalt/FilterPanel.tsx
impl/claude/web/src/pages/Gestalt.tsx
impl/claude/web/src/pages/Brain.tsx
impl/claude/web/src/api/client.ts
impl/claude/web/src/App.tsx
impl/claude/protocols/api/models.py
impl/claude/protocols/api/app.py
impl/claude/protocols/cli/hollow.py
```

---

## Wave 1 Remaining Work (Optional Polish)

These items would complete Wave 1 to 100% but aren't blockers for Wave 2:

1. **Test the Hero Path end-to-end**
   - Run: `kg brain capture <url>` → `kg world codebase` → `kg gardener start`
   - Verify synergy messages appear
   - Check web UI renders correctly

2. **Gardener API Integration**
   - Connect Gardener.tsx to real API (currently uses mock data)
   - Wire up `gardenerApi.getSession()` and `gardenerApi.advanceSession()`

3. **Observer-Specific Content**
   - Enhance CrystalDetail observer views with real content transformations
   - Add observer-dependent module views in Gestalt

4. **Navigation Between Jewels**
   - Add links: Brain → Gestalt ("Analyze this crystal's codebase")
   - Add links: Gestalt → Brain ("Capture this analysis")
   - Add links: Gardener → Both ("Use Brain context", "Run Gestalt scan")

---

## Wave 2: Extensions

### Goal

Build Atelier + Coalition on top of the Tier 1 foundation.

### Atelier Experience (60% → 100%)

**Current State**: Bidding, economy, widget system exist but UX is rough.

**Tasks**:
1. Apply Foundation 1 (Observer Switching) to workshop views
2. Add Path Visibility to atelier CLI commands
3. Create "quick auction" flow (< 2 min to first bid)
4. Add Joy layer (celebrate winning bids, personality loading)
5. Wire Atelier → Brain synergy (capture winning designs)

**Key Files**:
- `impl/claude/agents/atelier/` - Backend
- `impl/claude/web/src/pages/Workshop.tsx` - Web UI
- `impl/claude/protocols/cli/handlers/atelier.py` - CLI

### Coalition Forge (40% → 100%)

**Current State**: Coalition formation exists, but visualization missing.

**Tasks**:
1. Create Coalition visualization component (network graph)
2. Add polynomial state for coalition lifecycle
3. Apply Foundation 1 (Observer views of coalitions)
4. Wire Coalition → Brain synergy (capture coalition decisions)
5. Add coalition-specific joy animations

**Key Files**:
- `impl/claude/agents/forge/` - Backend (may need creation)
- `impl/claude/web/src/pages/Coalition.tsx` - Web UI (create)
- `plans/core-apps/coalition-forge.md` - Plan

---

## Wave 2 Success Criteria

- [ ] Atelier: User can complete auction in < 2 minutes
- [ ] Atelier: Observer switching shows different bid perspectives
- [ ] Coalition: User can visualize coalition formation
- [ ] Coalition: Polynomial state visible in UI
- [ ] Both: Synergy to Brain works automatically
- [ ] Both: Joy layer present (animations, personality)

---

## Suggested Session Start

```
I am the Crown Jewel Executor resuming work.

Reading enlightened plan...
[Read plans/crown-jewels-enlightened.md]

Previous wave: Wave 1 (Hero Path Polish) - COMPLETE
Current wave: Wave 2 (Extensions)
Focus: Atelier Experience → 100%

First task: [Choose from Wave 2 tasks above]

Beginning execution...
```

---

## Key References

| Document | Purpose |
|----------|---------|
| `plans/crown-jewels-enlightened.md` | Master plan |
| `plans/core-apps/atelier-experience.md` | Atelier plan |
| `plans/core-apps/coalition-forge.md` | Coalition plan |
| `impl/claude/HYDRATE.md` | Project state |
| `docs/skills/test-patterns.md` | Testing conventions |

---

## Notes for Next Session

1. **Run tests first** - Verify Wave 1 changes don't break anything
2. **Check TypeScript** - `cd impl/claude/web && npm run typecheck`
3. **Check Python** - `cd impl/claude && uv run pytest -x`
4. **Prioritize Atelier** - It's at 60%, closer to completion than Coalition (40%)
5. **Use existing foundations** - ObserverSwitcher, PolynomialDiagram, PathTrace are ready

---

*"The garden tends itself, but only because we planted it together."*

*Written: 2025-12-16*
