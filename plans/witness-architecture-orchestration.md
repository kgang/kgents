# Witness Architecture Orchestration Plan

> *Parallel sub-agent execution to complete the Witness Architecture.*

**Created**: 2025-12-25
**Status**: ACTIVE
**Target**: Complete integration in 6 parallel workstreams

---

## Current State Assessment

### Already Built ✅

| Component | Location | Lines | Status |
|-----------|----------|-------|--------|
| **Backend Mark Types** | services/witness/mark.py | ~900 | Complete (Mark, MarkLink, LinkRelation) |
| **Portal Marks** | services/witness/portal_marks.py | ~250 | Complete (mark_portal_expansion) |
| **Chat Witness** | services/chat/witness.py | ~200 | Complete (ChatMark, ChatPolicyTrace) |
| **Constitutional Reward** | services/chat/reward.py | ~150 | Complete (7 principles, scoring) |
| **Crystal Services** | services/witness/crystal*.py | ~2000 | Complete (crystallizer, store, trail) |
| **useWitness Hook** | hooks/useWitness.ts | 456 | Complete (unified witness API) |
| **useNavigationWitness** | hypergraph/useNavigationWitness.ts | 357 | Complete (navigation-specific) |
| **WitnessedTrail** | hypergraph/WitnessedTrail.tsx | 224 | Complete (trail + marks) |
| **NavigationConstitutionalBadge** | hypergraph/NavigationConstitutionalBadge.tsx | ~180 | Complete |
| **ConstitutionalRadar** | components/chat/ConstitutionalRadar.tsx | ~180 | Complete (7-point SVG) |

### Missing / Needs Integration 🔧

1. **HypergraphEditor Integration** - Wire useNavigationWitness into main component
2. **Constitutional Generalization** - Extend beyond chat to navigation/portal
3. **Crystal UI** - Frontend components for crystallization flow
4. **Portal Frontend Witnessing** - Call mark_portal_expansion from PortalToken
5. **End-to-End Testing** - Full flow verification

---

## Orchestration: 6 Parallel Workstreams

### Stream 1: HypergraphEditor Integration (CRITICAL PATH)

**Agent Type**: general-purpose
**Priority**: 1 (unlocks all other frontend work)
**Estimated**: 2 hours

**Tasks**:
1. Import useNavigationWitness into HypergraphEditor.tsx
2. Wire witnessNavigation calls into gD, gl, gh, gj, gk handlers
3. Add WitnessedTrail to TrailBar area
4. Add NavigationConstitutionalBadge to StatusLine
5. Ensure fire-and-forget (no blocking on mark emission)

**Success Criteria**:
- `gD` navigation creates derivation mark
- Trail shows recent marks with principle indicators
- Constitutional badge updates in real-time
- No UX latency from witnessing

---

### Stream 2: Portal Frontend Witnessing

**Agent Type**: general-purpose
**Priority**: 2
**Estimated**: 1.5 hours

**Tasks**:
1. Import useWitness into PortalToken.tsx
2. Call witnessPortal on expand/collapse (depth >= 2)
3. Connect to backend mark_portal_expansion via API
4. Add evidence_id to portal response for linking
5. Show witness indicator on witnessed portals

**Success Criteria**:
- Portal depth 2+ creates mark
- Marks visible in WitnessedTrail
- evidence_id enables trail reconstruction

---

### Stream 3: Constitutional Generalization

**Agent Type**: general-purpose
**Priority**: 2
**Estimated**: 2 hours

**Tasks**:
1. Create services/constitutional/reward.py (extract from chat)
2. Add domain parameter (chat/navigation/portal/edit)
3. Implement domain-specific scoring rules:
   - Navigation: derivation=generative, loss_gradient=ethical
   - Portal: depth_weighted, edge_type_matters
   - Edit: change_size, spec_alignment
4. Update NavigationConstitutionalBadge to use generalized scoring
5. Add constitutional_scores to all Mark types

**Success Criteria**:
- All domains use same PrincipleScore type
- Domain-specific rules apply correctly
- Constitutional badge works for navigation context

---

### Stream 4: Crystal UI Components

**Agent Type**: general-purpose
**Priority**: 3
**Estimated**: 2.5 hours

**Tasks**:
1. Create primitives/Crystal/CrystalCard.tsx (single crystal display)
2. Create primitives/Crystal/CrystalHierarchy.tsx (SESSION→DAY→WEEK→EPOCH)
3. Create primitives/Crystal/MoodIndicator.tsx (7D mood visualization)
4. Add /crystallize command to CommandLine.tsx
5. Create CrystallizationModal for session end

**Success Criteria**:
- CrystalCard shows insight, significance, mood
- Hierarchy navigable with expand/collapse
- /crystallize triggers compression flow
- Mood vector visible as subtle indicators

---

### Stream 5: API Endpoint Completion

**Agent Type**: general-purpose
**Priority**: 2
**Estimated**: 1.5 hours

**Tasks**:
1. Verify POST /api/witness/marks works from frontend
2. Add GET /api/witness/marks?path=... for node-specific marks
3. Add POST /api/witness/crystallize for session compression
4. Add GET /api/witness/crystals for hierarchy retrieval
5. Add SSE endpoint for real-time mark updates

**Success Criteria**:
- All endpoints return correct data
- SSE delivers marks in real-time
- Crystallization endpoint invokes backend crystallizer

---

### Stream 6: End-to-End Testing

**Agent Type**: general-purpose
**Priority**: 4 (after others complete)
**Estimated**: 1.5 hours

**Tasks**:
1. Write integration test: navigation → mark → trace → crystal
2. Test constitutional scoring across all domains
3. Test portal witnessing at different depths
4. Verify crystallization compresses correctly
5. Performance test: marks don't block UX (<50ms)

**Success Criteria**:
- Full flow works end-to-end
- All tests pass
- No performance regressions

---

## Execution Order

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARALLEL EXECUTION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Wave 1 (Start Immediately):                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Stream 1     │  │ Stream 3     │  │ Stream 5     │          │
│  │ HypergraphEd │  │ Constitutional│  │ API Endpoints│          │
│  │ Integration  │  │ Generalization│  │ Completion   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  Wave 2 (After Stream 1): │                 │                   │
│  ┌──────▼───────┐         │                 │                   │
│  │ Stream 2     │         │                 │                   │
│  │ Portal       │◄────────┘                 │                   │
│  │ Witnessing   │                           │                   │
│  └──────┬───────┘                           │                   │
│         │                                   │                   │
│  Wave 3 (After Stream 5): ◄─────────────────┘                   │
│  ┌──────▼───────┐                                               │
│  │ Stream 4     │                                               │
│  │ Crystal UI   │                                               │
│  └──────┬───────┘                                               │
│         │                                                       │
│  Wave 4 (After All):                                            │
│  ┌──────▼───────┐                                               │
│  │ Stream 6     │                                               │
│  │ E2E Testing  │                                               │
│  └──────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## User Workflows Enabled

### 1. The Explorer (Navigation-First)

```
User navigates via gD → Mark created
Trail shows breadcrumb → Principles visible
Session ends → /crystallize
Crystal captures: "Investigated derivation chain for X"
```

### 2. The Researcher (Portal-First)

```
User expands portal → depth 2+ marked
Evidence links form → Exploration visible
Pattern emerges → Mark accumulates
Crystal captures: "Researched import graph of module Y"
```

### 3. The Conversationalist (Chat-First)

```
User sends message → ChatMark created
Constitutional scored → Radar updates
Session saves → PolicyTrace preserved
Crystal captures: "Discussed approach to problem Z"
```

### 4. The Reviewer (Cross-Domain)

```
User navigates → reads → edits → tests
All actions witnessed → Trail shows full journey
Crystal compresses SESSION → DAY → WEEK → EPOCH
Long-term insight: "This week focused on witness architecture"
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Mark Latency** | <50ms | Time from action to mark created |
| **UI Blocking** | 0ms | Fire-and-forget, no wait |
| **Trail Accuracy** | 100% | All witnessed actions appear |
| **Constitutional Coverage** | 100% | All domains scored |
| **Crystallization Success** | >95% | Compressions complete |
| **Test Coverage** | >80% | Integration tests pass |

---

## Anti-Patterns to Avoid

1. **Blocking on witnessing** — Use fire-and-forget always
2. **Over-marking** — Depth 0-1 portals shouldn't mark
3. **Silent failures** — Log errors, never swallow
4. **Mutable traces** — Always immutable append
5. **Domain confusion** — Keep principle weights domain-specific

---

## Files to Create/Modify

### New Files
- `services/constitutional/reward.py` (extracted from chat)
- `primitives/Crystal/CrystalCard.tsx`
- `primitives/Crystal/CrystalHierarchy.tsx`
- `primitives/Crystal/MoodIndicator.tsx`
- `primitives/Crystal/index.ts`

### Modified Files
- `hypergraph/HypergraphEditor.tsx` (wire witness hooks)
- `hypergraph/StatusLine.tsx` (add constitutional badge)
- `hypergraph/TrailBar.tsx` (add WitnessedTrail)
- `components/tokens/PortalToken.tsx` (add witnessing)
- `hypergraph/CommandLine.tsx` (add /crystallize)
- `protocols/api/witness.py` (add crystallize endpoint)

---

*"The proof IS the decision. The mark IS the witness."*
