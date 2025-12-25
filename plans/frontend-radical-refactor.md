# Frontend Radical Refactor: The Telescope Doctrine

> *"Complexity is the disease. The focal distance is the cure."*
>
> *"Daring, bold, creative, opinionated but not gaudy"*

**Date**: 2025-12-24
**Target**: 71% code reduction (51,000 → 14,700 LOC)
**Duration**: 4 weeks

---

## Executive Summary

The kgents frontend has grown to 51,000 lines across 350+ files. This refactor proposes:

1. **6 Primitives** to replace 137+ components
2. **4 Constructions** for composed experiences
3. **Unified Design System** (kill 3 competing philosophies)
4. **Theory-First UI** (DP, ASHC, Value Agents visible in every view)

**The Keeper Code** (~30%):
- Hypergraph Editor (5,200 LOC) - excellent, minimal changes
- Chat Core (2,100 LOC of 8,000) - keep branching + crystallization
- STARK Design Biome - 90% steel, 10% earned glow

**The Death List** (~70%):
- Zero-Seed/Telescope (4,582 → 600 LOC)
- Chat bloat (5,900 LOC deleted)
- Duplicate components (OrganicToast, BreathingContainer)
- Example files, mock data generators
- 3 design systems → 1

---

## Part I: The Current State

### Metrics

| Area | Files | LOC | Status |
|------|-------|-----|--------|
| components/ | 137 | 30,000 | Overengineered |
| hypergraph/ | 31 | 5,200 | **Keeper** |
| hooks/ | 24 | 7,000 | Consolidate |
| api/ | 6 | 8,500 | Keep |
| pages/ | 8 | 2,400 | Simplify |
| **Total** | **350+** | **51,000** | **Refactor** |

### Critical Issues Found

1. **Zero-Seed Over-Engineering**: 4,582 LOC for what should be ~600
   - 4 content modes that should be 1
   - 300 LOC mock data generator
   - 11 state action types that should be 3
   - 15 components for 1 telescope metaphor

2. **Chat Bloat**: 8,000 LOC with 2,000 core + 5,900 bloat
   - Duplicate stores (store.ts + chatStore.ts)
   - 4 example files (700 LOC)
   - Redundant components (ToolPanel, TransparencySelector)
   - MentionPicker at 600 LOC (heavy dependency)

3. **Design System Fragmentation**:
   - STARK BIOME (good) vs Brutalist (conflict) vs Elastic (merge)
   - Token duplication (--elastic-gap-* vs --space-*)
   - No single source of truth

4. **Structural Debt**:
   - Root-level components (DirectorDashboard.tsx at top level)
   - Scattered type definitions
   - 0 test files for 51K LOC
   - Duplicate components (OrganicToast appears twice)

---

## Part II: The New Architecture

### The Telescope Principle

Every UI is a telescope with three controls:

```
1. FOCAL DISTANCE (zoom: near ↔ far)
2. APERTURE (detail: compressed ↔ expanded)
3. FILTER (aspect: data/proof/gradient/personality)
```

Not 15 components. Not 4 modes. **ONE COMPONENT** that responds to three dimensions.

### The 6 Primitives

| Primitive | LOC | Replaces | Theory Integration |
|-----------|-----|----------|-------------------|
| **Telescope** | 400 | GaloisTelescope, TelescopeNavigator, AnalysisQuadrant (4,582 LOC) | DP gradients, focal layers |
| **Trail** | 250 | DerivationTrail, FocalDistanceRuler, BranchTree partial (1,200 LOC) | PolicyTrace compression |
| **Conversation** | 1,800 | ChatPanel + 30 components (8,000 LOC) | Turn-level evidence |
| **Graph** | 5,200 | Keep existing | K-Block isolation |
| **Witness** | 300 | ASHCEvidence, ConfidenceIndicator, ContextIndicator (800 LOC) | EvidenceCorpus tiers |
| **ValueCompass** | 350 | NEW | Constitution scores, PersonalityAttractor |

**Total Primitives**: 8,300 LOC (vs 14,600 replaced)

### New Folder Structure

```
src/
├── primitives/          # The 6 core components (8,300 LOC)
│   ├── Telescope/
│   │   ├── Telescope.tsx        (400)
│   │   ├── useFocalState.ts     (150)
│   │   └── filters/             (200)
│   ├── Trail/
│   │   └── Trail.tsx            (250)
│   ├── Conversation/
│   │   ├── Conversation.tsx     (300 - orchestrator)
│   │   ├── Message.tsx          (400 - unified)
│   │   ├── InputArea.tsx        (350 - keep)
│   │   ├── BranchTree.tsx       (450 - keep)
│   │   └── SafetyGate.tsx       (250 - merge)
│   ├── Graph/
│   │   └── [existing 5,200 - minimal changes]
│   ├── Witness/
│   │   └── Witness.tsx          (300)
│   └── ValueCompass/
│       └── ValueCompass.tsx     (350)
│
├── constructions/       # Composed experiences (2,500 LOC)
│   ├── DirectorView/    (500)
│   ├── ZeroSeedExplorer/(430)
│   ├── ChatSession/     (620)
│   └── HypergraphStudio/(750)
│
├── pages/               # Routes (1,200 LOC)
│   ├── WelcomePage.tsx  (250)
│   ├── ChatPage.tsx     (200)
│   ├── DirectorPage.tsx (200)
│   ├── ZeroSeedPage.tsx (200)
│   ├── HypergraphEditorPage.tsx (200)
│   └── NotFound.tsx     (150)
│
├── design/              # Unified design system (1,500 LOC)
│   ├── tokens.css       (300 - ONE file)
│   ├── stark.css        (200)
│   ├── animations.css   (150)
│   ├── elastic.css      (250)
│   └── typography.css   (600)
│
├── hooks/               # Consolidated (2,000 LOC)
├── api/                 # Keep (2,500 LOC)
├── stores/              # Deduplicated (800 LOC)
└── types/               # Consolidated (600 LOC)

TOTAL: ~14,700 LOC
```

---

## Part III: Theory-UI Mapping

### How Each Theory Concept Becomes Visible

| Theory Primitive | UI Primitive | Visibility |
|-----------------|--------------|------------|
| **ValueAgent[S,A,B]** | ValueCompass | 7-principle radar + decision trajectory |
| **PolicyTrace** | Trail | Breadcrumb with compression ratios |
| **Constitution** | ValueCompass | Principle thresholds + current scores |
| **EvidenceCorpus** | Witness | Confidence tiers + causal graph |
| **PersonalityAttractor** | ValueCompass | 7D coordinate in principle space |
| **DP Gradients** | Telescope (filter="gradient") | Loss landscape at focal distance |
| **ASHC Decisions** | Trail + Witness | Decision → evidence chains |

### Example: Zero-Seed with Theory

```tsx
<ZeroSeedExplorer>
  <Telescope
    data={zeroSeedCorpus}
    focalDistance={0.5}     // L2-L3 visible
    aperture={0.7}          // Mostly expanded
    filter="gradient"       // Show DP loss landscape
    onNavigate={(path) => setTrail([...trail, path])}
  />

  <Trail
    path={trail}
    compressionRatio={policyTrace.ratio}
    showPrinciples={true}   // Show principle scores at each step
  />

  <ValueCompass
    scores={constitution.scores}
    trajectory={policyTrace.decisions}
    attractor={personality.coordinates}
  />
</ZeroSeedExplorer>
```

---

## Part IV: The Death List

### Phase 1: Immediate Deletions (Safe, Low-Risk)

```bash
# Example files (700 LOC)
rm src/components/chat/ChatInputExample.tsx
rm src/components/chat/CrystallizationExample.tsx
rm src/components/chat/INTEGRATION_EXAMPLE.tsx
rm src/components/chat/ToolTransparencyExample.tsx
rm src/router/MIGRATION_EXAMPLE.tsx

# Duplicate store
rm src/components/chat/store.ts  # Keep stores/chatStore.ts

# Documentation in wrong place
mv src/components/chat/*.md docs/
```

### Phase 2: Component Deletions (After Primitives Built)

```bash
# Zero-Seed (4,582 LOC → Telescope 400)
rm -rf src/components/zero-seed/
# Replaced by: primitives/Telescope/

# Analysis (1,000 LOC → filters in Telescope)
rm src/components/analysis/AnalysisQuadrant.tsx
rm src/components/analysis/DialecticalPanel.tsx
# Replaced by: Telescope with filter="dialectic"

# Layout redundancies (1,300 LOC → Trail + AppShell)
rm src/components/layout/TelescopeShell.tsx
rm src/components/layout/FocalDistanceRuler.tsx
rm src/components/layout/DerivationTrail.tsx
# Replaced by: primitives/Trail/

# Chat redundancies (1,800 LOC)
rm src/components/chat/ToolPanel.tsx
rm src/components/chat/TransparencySelector.tsx
rm src/components/chat/ConfidenceBar.tsx
rm src/components/chat/ChatMutationManager.tsx
rm src/components/chat/CrystallizationTrigger.tsx

# Director redundancies (1,850 LOC → DirectorView)
rm src/components/DirectorDashboard.tsx  # Root-level, wrong place
rm src/components/director/DocumentStatus.tsx
rm src/components/director/GhostDetailPanel.tsx
rm src/components/director/GhostDocumentSection.tsx
```

### Phase 3: Design System Consolidation

```bash
# Kill competing philosophies
rm src/styles/brutalist.css
# Merge useful patterns into design/stark.css

# Consolidate tokens
# FROM: globals.css + design-system.css + scattered files
# TO: design/tokens.css (ONE file)

# Consolidate animations
# FROM: animations.css + joy/ + genesis/
# TO: design/animations.css
```

---

## Part V: Implementation Plan

### Week 1: Foundation

**Goals**:
- Build primitives/ValueCompass (simplest, validates theory integration)
- Build primitives/Witness (consolidate existing evidence display)
- Build primitives/Trail (replace DerivationTrail + FocalRuler)
- Consolidate design/tokens.css

**Deliverables**:
- [ ] ValueCompass.tsx (350 LOC)
- [ ] Witness.tsx (300 LOC)
- [ ] Trail.tsx (250 LOC)
- [ ] design/tokens.css (unified)
- [ ] Storybook/demo for each

### Week 2: Telescope + Conversation

**Goals**:
- Build primitives/Telescope (the big one)
- Refactor Chat into primitives/Conversation
- Build 4 constructions

**Deliverables**:
- [ ] Telescope.tsx (400 LOC)
- [ ] Conversation/ folder (1,800 LOC total)
- [ ] constructions/DirectorView
- [ ] constructions/ZeroSeedExplorer
- [ ] constructions/ChatSession
- [ ] constructions/HypergraphStudio

### Week 3: Theory Integration

**Goals**:
- Wire backend endpoints to theory primitives
- Ensure ValueCompass shows real data
- Ensure Witness shows real evidence

**Deliverables**:
- [ ] API endpoints for theory data
- [ ] Types in types/theory.ts
- [ ] All constructions showing theory data

### Week 4: Extinction + Polish

**Goals**:
- Execute death list (36,300 LOC deleted)
- Verify all pages functional
- Performance audit (bundle size, build time)

**Deliverables**:
- [ ] All old components deleted
- [ ] npm run typecheck passes
- [ ] npm run build succeeds
- [ ] Bundle size < 40% of original

---

## Part VI: Success Metrics

### Quantitative

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| LOC | 51,000 | 14,700 | 71% reduction |
| Files | 350+ | ~80 | 77% reduction |
| Components | 137 | 6 primitives + 4 constructions | 93% reduction |
| Bundle Size | 100% | TBD | 60% reduction |
| Build Time | 100% | TBD | 50% reduction |

### Qualitative

- [ ] **Mirror Test**: Does it feel like Kent on his best day?
- [ ] **Joy**: Does the Telescope metaphor delight?
- [ ] **Tasteful**: Is every line justified?
- [ ] **Theory-Visible**: Can you SEE the ValueAgent deciding?
- [ ] **Composable**: Can you build new views from primitives in <100 LOC?

---

## Part VII: Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Graph editor breaks during refactor | Low | High | Keep in primitives/Graph/, minimal changes |
| Chat branching/crystallization breaks | Medium | High | Test extensively before deleting old components |
| Theory backend not ready | High | Medium | Build with mock data, wire later |
| Design system consolidation causes visual bugs | Medium | Medium | Side-by-side comparison before/after |
| Week 4 deletions break things | Medium | High | Delete incrementally with typecheck after each |

---

## Part VIII: Immediate Next Steps

### Today

```bash
# 1. Validate the vision
kg probe health --all

# 2. Safe deletions (examples)
rm impl/claude/web/src/components/chat/*Example.tsx
rm impl/claude/web/src/router/MIGRATION_EXAMPLE.tsx

# 3. Create structure
mkdir -p impl/claude/web/src/primitives/{Telescope,Trail,Conversation,Graph,Witness,ValueCompass}
mkdir -p impl/claude/web/src/design
mkdir -p impl/claude/web/src/constructions/{DirectorView,ZeroSeedExplorer,ChatSession,HypergraphStudio}
```

### This Week

1. Build ValueCompass (simplest primitive)
2. Consolidate design/tokens.css
3. Document which design system each component uses

### Decision Points

1. **MentionPicker**: Keep (lazy-load) or delete? Audit bundle impact.
2. **D3.js in BranchTree**: Keep (if visuals essential) or replace with JSX?
3. **Chat store**: Which is canonical - stores/chatStore.ts or components/chat/store.ts?

---

## Appendix A: The Keeper Patterns

### From Hypergraph Editor

- **Declarative keybinding registry** → Extract as useKeyRegistry()
- **K-Block isolation monad** → Transaction semantics for all editors
- **Mode-based content rendering** → NORMAL (view) vs INSERT (edit)
- **Trail as semantic breadcrumb** → Conceptual journey, not file path

### From Chat

- **Branching with fork/merge** → Session tree visualization
- **Crystallization** → Trailing session compression
- **Safety gates** → Pre-execution + acknowledgment
- **Evidence display** → Confidence tiers

### From Design System

- **STARK BIOME** → 90% steel, 10% earned glow
- **Breathing animations** → 3.4s calming cycles
- **Mode-specific colors** → data-mode attributes
- **Elastic grid** → 3 density modes (compact/comfortable/spacious)

---

## Appendix B: Theory Types

```typescript
// types/theory.ts

/** Constitution: The 7 principles */
export interface ConstitutionScores {
  tasteful: number;      // 0-1
  curated: number;
  ethical: number;
  joyInducing: number;
  composable: number;
  heterarchical: number;
  generative: number;
}

/** PolicyTrace: Decision sequence with compression */
export interface PolicyTrace {
  decisions: Decision[];
  compressionRatio: number;  // 0-1
  trajectory: ConstitutionScores[];
}

/** EvidenceCorpus: ASHC evidence tiers */
export type EvidenceTier = "confident" | "uncertain" | "speculative";

export interface EvidenceCorpus {
  tier: EvidenceTier;
  items: Evidence[];
  causalGraph: CausalEdge[];
}

/** PersonalityAttractor: 7D coordinate in principle space */
export interface PersonalityAttractor {
  coordinates: ConstitutionScores;
  basin: ConstitutionScores[];
  stability: number;
}
```

---

*This is the architecture. Daring, bold, opinionated. Not gaudy. Tasteful.*

*The Telescope sees all. The Trail remembers all. The ValueCompass justifies all.*

*36,300 lines die so that 14,700 can live fully.*
