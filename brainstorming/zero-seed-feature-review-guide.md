# Zero Seed Genesis — Feature Review Guide

> *A walkthrough for Kent to explore and review the implementation*

**Prepared by**: Claude
**Date**: 2025-12-25
**Duration**: ~90 minutes (can split across sessions)

---

## How to Use This Guide

This is a **guided tour** through the Zero Seed Genesis implementation. For each phase:

1. **Context** — What problem this solves
2. **Key Files** — Where to look
3. **Demo** — How to see it in action
4. **Discussion Points** — Questions for refinement
5. **Joy Check** — Does this feel like you on your best day?

---

## Pre-Flight Checklist

Before we start, verify the environment:

```bash
# Terminal 1: Start backend
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Start frontend
cd impl/claude/web
npm run dev
# Visit http://localhost:3000

# Terminal 3: TypeScript verification
cd impl/claude/web && npm run typecheck  # Should pass clean
```

---

## Phase 0: Bootstrap Infrastructure

### Context
*"From nothing, the seed."*

The Zero Seed is the minimal generative kernel that spawns the entire system. Three axioms (A1: Entity, A2: Morphism, G: Galois Ground) derive the 7 layers.

### Key Files to Review

| File | Lines | What to Look For |
|------|-------|------------------|
| `reset-world.sh` | 308 | Does the reset feel complete? Any missing cleanup? |
| `services/zero_seed/seed.py` | 468 | Do the 3 axioms feel right? Is the derivation clear? |
| `protocols/api/genesis.py` | 370 | Are the endpoints intuitive? |

### Demo Commands

```bash
# Reset the world (DESTRUCTIVE - use with care)
./reset-world.sh

# Verify axioms were seeded
curl http://localhost:8000/api/genesis/status

# Check design laws
curl http://localhost:8000/api/genesis/design-laws
```

### Discussion Points

1. **Reset ceremony**: Should `reset-world.sh` require confirmation? A password? A haiku?
2. **Axiom content**: Do the actual texts of A1, A2, G feel right? Or too abstract?
3. **Visibility**: Should users see the seeding happen (animation), or is it instant?

### Joy Check
- [ ] Does this feel *daring, bold, creative*?
- [ ] Is the Zero Seed something you'd want to watch spawn?

---

## Phase 1: Feed Primitive

### Context
*"The feed is not a view of data. The feed IS the primary interface."*

The infinite chronological feed is the universal truth stream. Everything surfaces here.

### Key Files to Review

| File | Lines | What to Look For |
|------|-------|------------------|
| `services/feed/ranking.py` | 285 | Is the 4-factor scoring intuitive? |
| `services/feed/defaults.py` | 181 | Do the 5 default feeds make sense? |
| `web/src/primitives/Feed/Feed.tsx` | 335 | Does the UX feel like a feed you'd use? |
| `web/src/primitives/Feed/FeedItem.tsx` | 244 | Is the K-Block card readable? |

### Demo

1. Navigate to the Feed in the web UI
2. Try filtering by layer (L1 Axiom, L3 Goal, etc.)
3. Notice the loss color gradient (green → red)
4. Try scrolling (infinite scroll kicks in)

### Discussion Points

1. **Ranking weights**: Currently attention=0.4, principles=0.3, recency=0.2, coherence=0.1. Feel right?
2. **Default feeds**:
   - `cosmos` (everything)
   - `coherent` (loss < 0.3)
   - `contradictions` (super-additive loss)
   - `axioms` (L1 only)
   - `handwavy` (loss > 0.5)

   Missing any? Too many?
3. **Visual hierarchy**: Is layer vs loss distinction clear enough?

### Joy Check
- [ ] Would you scroll this feed for pleasure?
- [ ] Does it feel like a *chronological truth stream*?

---

## Phase 2: File Explorer + Sovereign Uploads

### Context
*"Sovereignty before integration. The staging area is sacred."*

Files enter through `uploads/` as sovereign entities, then deliberately integrate.

### Key Files to Review

| File | Lines | What to Look For |
|------|-------|------------------|
| `web/src/components/FileExplorer/FileExplorer.tsx` | 569 | Does the tree feel navigable? |
| `web/src/components/FileExplorer/UploadZone.tsx` | 296 | Is drag-drop obvious? |
| `web/src/components/FileExplorer/IntegrationDialog.tsx` | 228 | Is the integration preview clear? |
| `services/sovereign/integration.py` | ~21KB | Do the 9 steps make sense? |

### Demo

1. Navigate to File Explorer
2. Drag a file into the `uploads/` zone
3. Then drag that file to `spec/` or `impl/`
4. Watch the Integration Dialog appear
5. Review: layer assignment, proposed edges, contradictions

### Discussion Points

1. **Integration dialog**: Currently shows layer + edges + contradictions. Too much? Too little?
2. **Keyboard nav**: j/k, Enter, h/l for navigation. Vim enough?
3. **Missing steps**: Steps 4-6, 9 return TODO. Priority to complete?

### Joy Check
- [ ] Does dragging a file feel like *sovereignty before integration*?
- [ ] Is the staging area *sacred* enough?

---

## Phase 3: First Time User Experience

### Context
*"The act of declaring is itself a radical act of self-transformation."*

The FTUE walks a new user from nothing to their first K-Block declaration.

### Key Files to Review

| File | Lines | What to Look For |
|------|-------|------------------|
| `web/src/pages/Genesis/GenesisWelcome.tsx` | ~100 | Does the welcome feel warm? |
| `web/src/pages/Genesis/FirstQuestion.tsx` | ~150 | Is the prompt inspiring? |
| `web/src/pages/Genesis/WelcomeToStudio.tsx` | 161 | Is the celebration joyful? |

### Demo

1. Visit `/genesis` (or `/` if fresh)
2. Click through the welcome
3. Enter your first declaration ("I want to build tasteful agents")
4. Watch the K-Block creation celebration
5. Enter the studio

### Discussion Points

1. **Welcome copy**: Is it too much? Too little? Too corporate?
2. **First question prompt**: Currently "What do you want to build?" — alternatives?
3. **Celebration**: ✨ emoji + "You've made your first declaration" — joyful enough?
4. **Loss explanation**: "A bit hand-wavy, and that's okay!" — tone right?

### Joy Check
- [ ] Would a first-time user feel *invited*?
- [ ] Does declaring feel like an *act of agency*?

---

## Phase 4: Contradiction Engine

### Context
*"Contradictions are features, not bugs. Surface. Interrogate. Transform."*

The engine detects super-additive loss when statements conflict, then helps resolve.

### Key Files to Review

| File | Lines | What to Look For |
|------|-------|------------------|
| `services/contradiction/detection.py` | 267 | Is the math intuitive? |
| `services/contradiction/classification.py` | 261 | Are the 4 types clear? |
| `services/contradiction/resolution.py` | 320 | Are the 5 strategies useful? |
| `web/src/components/Contradiction/ContradictionCard.tsx` | 176 | Is the UI readable? |

### Demo

1. Create two contradictory declarations:
   - "I value simplicity above all"
   - "I want a feature-rich complex system"
2. Watch the contradiction surface
3. Review: type, severity, options

### Discussion Points

1. **4 contradiction types**:
   - APPARENT (seems contradictory, isn't)
   - PRODUCTIVE (creative tension)
   - TENSION (genuine but livable)
   - FUNDAMENTAL (can't both be true)

   Complete? Missing any?

2. **5 resolution strategies**:
   - SYNTHESIZE (create new statement)
   - SCOPE (limit applicability)
   - CHOOSE (pick one)
   - TOLERATE (live with it)
   - IGNORE (dismiss)

   Complete? Order right?

3. **Surfacing style**: Currently neutral. Should it be more playful? More serious?

### Joy Check
- [ ] Does surfacing contradictions feel *helpful*, not *judgmental*?
- [ ] Is this *fail-fast epistemology*?

---

## Phase 5: Heterarchical Tolerance

### Context
*"The system adapts to the user. Never punish, never lecture, never block."*

Cross-layer edges are allowed. Incoherence is tolerated. The system metabolizes mess.

### Key Files to Review

| File | Lines | What to Look For |
|------|-------|------------------|
| `services/edge/policy.py` | 240 | Are the 3 levels clear? |
| `services/edge/quarantine.py` | 188 | Is 0.85 the right threshold? |
| `spec/protocols/heterarchy.md` | 673 | Is the spec complete? |

### Demo

1. Create an L3 Goal K-Block
2. Try to link it directly to an L6 Implementation
3. Notice: system allows it (OPTIONAL level) but notes the skip
4. Create something very incoherent (loss > 0.85)
5. Watch it get quarantined (gently)

### Discussion Points

1. **Policy levels**:
   - STRICT: Adjacent layers only
   - SUGGESTED: Common patterns
   - OPTIONAL: Anything goes

   Default OPTIONAL feels right?

2. **Quarantine threshold**: 0.85 means truly incoherent. Too high? Too low?

3. **Linear design**: System never blocks. Only surfaces. Feel right?

### Joy Check
- [ ] Does this feel like a *garden*, not a *museum*?
- [ ] Is incoherence *tolerated* gracefully?

---

## Overall Synthesis

After walking through all phases, consider:

### Architecture Questions
1. Is the layering (0→5) the right decomposition?
2. Are there missing phases?
3. Are there phases that should merge?

### UX Questions
1. Does the flow feel linear in the good way (adapts to you)?
2. Are there any moments that feel like *punishment* or *lecturing*?
3. What's the "one thing" that would make this 10x better?

### The Mirror Test
> *"Does K-gent feel like me on my best day?"*

After seeing all of this:
- [ ] Daring?
- [ ] Bold?
- [ ] Creative?
- [ ] Opinionated but not gaudy?

---

## Technical Notes for Demo

### Backend Commands
```bash
# Check API health
curl http://localhost:8000/health

# List all K-Blocks
curl http://localhost:8000/api/kblocks

# Get contradiction analysis
curl http://localhost:8000/api/contradictions/analyze

# Check feed
curl http://localhost:8000/api/feed/cosmos
```

### Known Gaps (Will See TODO)
- Phase 2: Integration steps 4-6, 9 return placeholder
- Phase 4: Contradiction API endpoints not exposed yet
- Real-time: No SSE/WebSocket updates yet

### Test Suite
```bash
# Run all tests
cd impl/claude && uv run pytest -q

# Run heterarchy tests (100% passing)
cd impl/claude && uv run pytest tests/test_heterarchy/ -v
```

---

## Next Steps After Review

Based on your feedback, we can:

1. **Polish** — Refine copy, colors, animations
2. **Wire** — Connect UI to backend (the main gap)
3. **Extend** — Add missing features
4. **Simplify** — Remove anything that doesn't spark joy

---

*"The seed IS the garden. The declaration IS the self."*
