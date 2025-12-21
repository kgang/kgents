# Crown Jewel Cleanup: Pre-Planning Audit

> **Purpose**: Audit frontend crown jewel apps and their AGENTESE nodes for cleanup before ashc work.
> **Scope**: Remove development scaffolding while preserving production primitives.
> **Date**: 2025-12-21

---

## Executive Summary

The kgents frontend has accumulated 15+ crown jewel apps during development. With the ashc pivot, we're cleaning house: **keep Brain, Galleries, OS-Shell, and auto-magic AGENTESE rendering**; remove the rest.

### What We're Keeping

| Category | Items | Rationale |
|----------|-------|-----------|
| **Brain** | `self.memory` node, Brain page, Brain components | Core memory system |
| **Galleries** | `/_/gallery/*` routes, gallery components | Developer showcase |
| **OS-Shell** | Shell, NavigationTree, Terminal, projections | Universal AGENTESE rendering |
| **Primitives** | elastic/, joy/, genesis/, projection/, categorical/, polynomial/, synergy/, servo/ | Reusable UI components |
| **Auto-magic** | UniversalProjection, ConceptHomeProjection, GenericProjection | AGENTESE → React pipeline |
| **Living Docs** | `concept.docs`, `self.docs`, `self.document` nodes | Documentation & interactive text |
| **Liminal** | `time.coffee` node | Morning ritual personality |
| **Infrastructure** | morpheus/, verification/, metabolism/, conductor/, ashc/, foundry/, principles/ | ashc work & core infra |
| **Witness** | services/witness/, self.witness.*, time.witness.* | Trust-gated agency, trace store, voice gate |

### What We're Removing

| Category | Items | Files to Delete |
|----------|-------|-----------------|
| **Town** | world.town.*, TownProjection, Town pages, Town components | 15+ files |
| **Park** | world.park.*, ParkProjection, Park page, Park components | 12+ files |
| **Forge** | world.forge.*, ForgeProjection, Forge page, Forge components | 18+ files |
| **Gestalt** | world.codebase.*, GestaltProjection, Gestalt page, Gestalt components | 14+ files |
| **Muse** | self.muse.*, Muse components | 8+ files |
| **Differance** | time.differance.*, DifferanceProjection, Differance page, Differance components | 11+ files |
| **Chat** | self.chat.*, ChatProjection, Chat page, Chat components | 12+ files |
| **Soul** | self.soul.*, SoulProjection, Soul page | 5+ files |
| **Cockpit** | self.cockpit.*, CockpitProjection, Cockpit page | 4+ files |
| **Workshop** | world.town.workshop.*, WorkshopProjection, Workshop page | 6+ files |
| **Emergence** | world.emergence.*, EmergenceProjection, Emergence page | 4+ files |
| **Design System** | concept.design.*, DesignSystemProjection, DesignSystem page | 5+ files |
| **Miscellaneous** | Inhabit, Canvas, various experimental pages | 8+ files |

---

## Detailed Audit

### 1. Frontend Pages (`impl/claude/web/src/pages/`)

**23 page files found:**

```
KEEP:
├── Brain.tsx                 # Core memory UI
├── GalleryPage.tsx          # Projection gallery
├── LayoutGallery.tsx        # Layout showcase
├── InteractiveTextGallery.tsx # Text rendering gallery
├── AgenteseDocs.tsx         # AGENTESE explorer
├── NotFound.tsx             # Error handling

REMOVE:
├── Canvas.tsx               # Collaborative canvas experiment
├── ChatPage.tsx             # Chat interface
├── Cockpit.tsx              # Developer portal (replaced by galleries)
├── DesignSystem.tsx         # Categorical design language
├── Differance.tsx           # Ghost/trace visualization
├── Emergence.tsx            # Cymatics experiment
├── Forge.tsx                # Agent workshop
├── Gestalt.tsx              # Codebase visualizer
├── Inhabit.tsx              # Citizen inhabitation
├── ParkScenario.tsx         # Westworld simulation
├── Soul.tsx                 # K-gent personality
├── Town.tsx                 # Town simulation
├── TownCitizensPage.tsx     # Citizen registry
├── TownCoalitionsPage.tsx   # Coalition management
├── TownOverviewPage.tsx     # Town overview
├── Witness.tsx              # Trust-gated agency
└── Workshop.tsx             # Event-driven builder
```

### 2. Frontend Components (`impl/claude/web/src/components/`)

**32 component directories found:**

```
KEEP (Primitives & Reusable):
├── elastic/                 # ElasticContainer, ElasticCard, FloatingActions (13 files)
├── joy/                     # PageTransition, PersonalityLoading, animations (14 files)
├── genesis/                 # BreathingContainer, GrowingContainer, OrganicToast (8 files)
├── projection/              # Widgets: Graph, Table, Select, Progress (13 files)
├── categorical/             # StateIndicator, TeachingCallout, TracePanel (7 files)
├── polynomial/              # PolynomialDiagram, MiniPolynomial (7 files)
├── synergy/                 # SynergyToaster, cross-jewel notifications (6 files)
├── servo/                   # Servo components (9 files)
├── error/                   # ErrorBoundary, error handling (4 files)
├── layout/                  # Layout primitives (3 files)
├── path/                    # Path utilities (3 files)
├── dev/                     # Development tools (3 files)
├── AgentLink.tsx            # Single-file utility

KEEP (Brain):
├── brain/                   # MemoryBrowser, CrystalTimeline, etc. (7 files)

REMOVE (Crown Jewel-specific):
├── town/                    # TownGrid, CitizenCard, etc. (12 files)
├── park/                    # ParkCanvas, ScenarioPanel, etc. (13 files)
├── forge/                   # ForgeWorkspace, ArtisanPanel, etc. (19 files)
├── gestalt/                 # GestaltTree, ArchitectureGraph, etc. (14 files)
├── muse/                    # MuseWhisper, PatternPanel (3 files)
├── witness/                 # WitnessPanel, TrustMeter (3 files)
├── differance/              # GhostHeritageDAG, TraceTimeline (11 files)
├── chat/                    # ChatWindow, MessageList (5 files)
├── cockpit/                 # CockpitDashboard, QuickActions (3 files)
├── docs/                    # UmweltDocs, RequestBuilder (10 files)
├── canvas/                  # CollaborativeCanvas, CanvasTools (6 files)
├── scene/                   # SceneRenderer, 3D components (4 files)
├── eigenvector/             # Eigenvector visualizations (4 files)
├── terrace/                 # Terrace layout (3 files)
├── terrarium/               # Terrarium experiment (5 files)
├── voice/                   # Voice components (3 files)
└── layout-sheaf/            # LayoutSheaf experiment (7 files)
```

### 3. Shell Components (`impl/claude/web/src/shell/`)

**KEEP (OS-Shell infrastructure):**
```
├── Shell.tsx                # Main shell layout
├── ShellProvider.tsx        # Shell context
├── ShellErrorBoundary.tsx   # Error handling
├── NavigationTree.tsx       # AGENTESE tree nav
├── PathSearch.tsx           # Path search
├── PathProjection.tsx       # Path rendering
├── StreamPathProjection.tsx # Streaming rendering
├── Terminal.tsx             # Terminal emulator
├── CommandPalette.tsx       # Cmd+K
├── KeyboardHints.tsx        # Keyboard shortcuts
├── GhostPanel.tsx           # Ghost context
├── ObserverDrawer.tsx       # Observer context
├── ContextBadge.tsx         # Context indicator
├── ReferencePanel.tsx       # Reference viewer
├── ExamplesPanel.tsx        # Examples
├── GeneratedPlayground.tsx  # Code playground
├── ExplorationBreadcrumb.tsx # Breadcrumbs
├── hooks/                   # Shell hooks
├── components/              # Shell sub-components
│   ├── TreeNodeItem.tsx     # KEEP
│   ├── CrownJewelsSection.tsx # MODIFY (remove non-Brain jewels)
│   ├── ToolsSection.tsx     # MODIFY (remove differance)
│   └── GallerySection.tsx   # KEEP
└── projections/             # Projection system
    ├── registry.tsx         # MODIFY (remove non-Brain projections)
    ├── UniversalProjection.tsx # KEEP (auto-magic)
    ├── ConceptHomeProjection.tsx # KEEP (fallback)
    ├── GenericProjection.tsx # KEEP (JSON viewer)
    ├── ContextOverviewProjection.tsx # KEEP
    ├── ProjectionLoading.tsx # KEEP
    └── ProjectionError.tsx  # KEEP
```

### 4. Backend AGENTESE Nodes (`impl/claude/services/`)

**29 services found, 20+ @node registrations:**

```
KEEP:
├── brain/node.py            # @node("self.memory") - Core memory
├── interactive_text/        # @node("self.document") - Interactive text for galleries
├── living_docs/node.py      # @node("concept.docs"), @node("self.docs") - Living docs
├── liminal/coffee/node.py   # @node("time.coffee") - Morning ritual personality
├── morpheus/node.py         # @node("world.morpheus") - LLM gateway infrastructure
├── verification/            # Proof generation (ashc work)
├── metabolism/              # Session metabolism (ashc work)
├── conductor/               # File guard, session management
├── ashc/                    # New ashc work
├── foundry/                 # Foundry infrastructure
├── principles/              # Principles

REMOVE:
├── town/node.py             # @node("world.town")
├── town/citizen_node.py     # @node("world.town.citizen")
├── town/coalition_node.py   # @node("world.town.coalition")
├── town/collective_node.py  # @node("world.town.collective")
├── town/inhabit_node.py     # @node("world.town.inhabit")
├── town/workshop_node.py    # @node("world.town.workshop")
├── park/node.py             # @node("world.park")
├── forge/node.py            # @node("world.forge")
├── forge/soul_node.py       # @node("world.forge.soul")
├── gestalt/node.py          # @node("world.codebase")
├── muse/node.py             # @node("self.muse")
├── witness/node.py          # @node("self.witness")
├── witness/crystallization_node.py # @node("time.witness")
├── chat/node.py             # @node("self.chat")
├── f/node.py                # @node("self.flow")
├── coalition/               # Coalition service
├── gardener/                # Gardener (Brain has its own)
├── archaeology/             # Code archaeology
```

### 5. App Router Configuration (`impl/claude/web/src/App.tsx`)

**Current routes:**

```tsx
KEEP:
<Route path="/_/gallery" element={<GalleryPage />} />
<Route path="/_/gallery/layout" element={<LayoutGallery />} />
<Route path="/_/gallery/interactive-text" element={<InteractiveTextGallery />} />
<Route path="/_/docs/agentese" element={<AgenteseDocs />} />
<Route path="/*" element={<UniversalProjection />} />  // Auto-magic

REMOVE:
<Route path="/_/canvas" element={<Canvas />} />
```

### 6. Projection Registry (`impl/claude/web/src/shell/projections/registry.tsx`)

**TYPE_REGISTRY entries to remove:**
```
MemoryCrystal, CrystalCartography, BrainManifest → KEEP (Brain)
ForgeCommission, ForgeArtisan → REMOVE
DifferanceTrace, GhostHeritageDAG → REMOVE
CitizenManifest, CitizenList, CoalitionManifest, TownManifest → REMOVE
GestaltTopology, GestaltLayer → REMOVE
SoulManifestResponse, EigenvectorsResponse, DialogueResponse, StartersResponse → REMOVE
LayoutOperadManifest, ContentOperadManifest, MotionOperadManifest, DesignOperadManifest → REMOVE
EmergenceManifest, EmergenceQualia, EmergenceCircadian → REMOVE
```

**PATH_REGISTRY entries to remove:**
```
self.memory.*, self.memory → KEEP (Brain)
world.forge.*, world.forge → REMOVE
time.differance.*, time.differance → REMOVE
world.codebase.*, world.codebase → REMOVE
world.town.*, world.town → REMOVE
world.park.*, world.park → REMOVE
self.differance.*, self.differance → REMOVE
world.gallery.*, world.gallery → EVALUATE (galleries)
world.workshop.*, world.workshop → REMOVE
self.chat.*, self.chat → REMOVE
self.soul.*, self.soul → REMOVE
concept.design.*, concept.design → REMOVE
world.emergence.*, world.emergence → REMOVE
self.cockpit → REMOVE
```

### 7. Navigation Components

**CrownJewelsSection.tsx** - Update `CROWN_JEWELS` array:
```tsx
// KEEP only:
{ name: 'brain', label: 'Brain', path: 'self.memory', icon: Brain }

// REMOVE:
{ name: 'gestalt', ... }
{ name: 'forge', ... }
{ name: 'coalition', ... }
{ name: 'park', ... }
```

**ToolsSection.tsx** - Update `TOOLS` array:
```tsx
// REMOVE:
{ path: 'time.differance', label: 'Différance', icon: GitBranch }
```

---

## Implementation Plan

### Phase 1: Backend Cleanup (AGENTESE Nodes)

1. **Remove service directories** (with tests):
   - `services/town/` (entire directory)
   - `services/park/` (entire directory)
   - `services/forge/` (entire directory)
   - `services/gestalt/` (entire directory)
   - `services/muse/` (entire directory)
   - `services/witness/` (entire directory)
   - `services/chat/` (entire directory)
   - `services/f/` (entire directory)
   - `services/coalition/` (entire directory)
   - `services/gardener/` (entire directory - Brain has its own)
   - `services/archaeology/` (entire directory)

2. **Keep service directories**:
   - `services/brain/` - Core memory
   - `services/interactive_text/` - Gallery text rendering
   - `services/living_docs/` - concept.docs, self.docs
   - `services/liminal/` - time.coffee ritual
   - `services/morpheus/` - LLM gateway
   - `services/verification/` - ashc proof generation
   - `services/metabolism/` - ashc session metabolism
   - `services/conductor/` - File guard, sessions
   - `services/ashc/` - New ashc work
   - `services/foundry/` - Foundry infrastructure
   - `services/principles/` - Principles

3. **Update `services/providers.py`**:
   - Remove registrations for deleted services
   - Keep brain, living_docs, interactive_text, liminal, morpheus, verification, metabolism, conductor, ashc, foundry, principles

4. **Update `services/__init__.py`**:
   - Remove exports for deleted services

5. **Verify AGENTESE gateway still works**:
   - `pytest impl/claude/protocols/agentese/`
   - Should discover only remaining nodes

### Phase 2: Frontend Pages Cleanup

1. **Delete page files** (`impl/claude/web/src/pages/`):
   ```bash
   rm Canvas.tsx ChatPage.tsx Cockpit.tsx DesignSystem.tsx \
      Differance.tsx Emergence.tsx Forge.tsx Gestalt.tsx \
      Inhabit.tsx ParkScenario.tsx Soul.tsx Town.tsx \
      TownCitizensPage.tsx TownCoalitionsPage.tsx TownOverviewPage.tsx \
      Witness.tsx Workshop.tsx
   ```

2. **Update `App.tsx`**:
   - Remove lazy imports for deleted pages
   - Remove Canvas route

### Phase 3: Frontend Components Cleanup

1. **Delete component directories**:
   ```bash
   rm -rf components/town components/park components/forge \
          components/gestalt components/muse components/witness \
          components/differance components/chat components/cockpit \
          components/docs components/canvas components/scene \
          components/eigenvector components/terrace components/terrarium \
          components/voice components/layout-sheaf
   ```

2. **Keep directories**:
   - `brain/` - Core memory UI
   - `elastic/` - Elastic layouts
   - `joy/` - Animations and delight
   - `genesis/` - Organic containers
   - `projection/` - Widgets
   - `categorical/` - State indicators
   - `polynomial/` - Polynomial diagrams
   - `synergy/` - Toasts
   - `servo/` - Servo components
   - `error/` - Error handling
   - `layout/` - Layout primitives
   - `path/` - Path utilities
   - `dev/` - Dev tools

### Phase 4: Shell Updates

1. **Update `projections/registry.tsx`**:
   - Remove all projection imports except Brain
   - Simplify TYPE_REGISTRY to Brain types only
   - Simplify PATH_REGISTRY to Brain paths only
   - Keep ConceptHomeProjection as fallback

2. **Update `components/CrownJewelsSection.tsx`**:
   - Remove all jewels except Brain
   - Update CROWN_JEWELS array

3. **Update `components/ToolsSection.tsx`**:
   - Remove Différance tool
   - Consider removing entire section or adding Brain-related tools

4. **Keep intact**:
   - `GallerySection.tsx` - Gallery shortcuts
   - `TreeNodeItem.tsx` - Tree rendering
   - All shell infrastructure

### Phase 5: Cleanup & Verification

1. **Run type checking**:
   ```bash
   cd impl/claude/web && npm run typecheck
   ```

2. **Run linting**:
   ```bash
   cd impl/claude/web && npm run lint
   ```

3. **Run backend tests**:
   ```bash
   cd impl/claude && uv run pytest -q
   ```

4. **Manual verification**:
   - Visit `http://localhost:3000/self.memory` - Brain should work
   - Visit `http://localhost:3000/_/gallery` - Galleries should work
   - Visit `http://localhost:3000/unknown.path` - ConceptHome fallback
   - Navigate via tree - Only Brain in Crown Jewels

---

## File Count Summary

| Action | Frontend Files | Backend Files | Total |
|--------|----------------|---------------|-------|
| **DELETE** | ~120 files | ~80 files | ~200 files |
| **MODIFY** | ~5 files | ~3 files | ~8 files |
| **KEEP** | ~100 files | ~50 files | ~150 files |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Breaking imports | TypeScript will catch missing imports |
| Orphaned dependencies | Run `npm run typecheck` after each phase |
| Missing AGENTESE nodes | Gateway discovery will show what's registered |
| Regression in Brain | Keep Brain tests, run after each phase |

---

## Decisions Made

| Question | Decision |
|----------|----------|
| Keep `time.coffee`? | ✅ YES - Morning ritual personality |
| Keep `concept.docs` / `self.docs`? | ✅ YES - Living docs |
| Keep `self.document`? | ✅ YES - Interactive text for galleries |
| Keep `verification/`, `metabolism/`, `morpheus/`? | ✅ YES - ashc infrastructure |
| Keep polynomial diagrams? | ✅ YES - State machine visualization |

---

## Next Steps

1. ✅ Review this plan
2. ✅ Decisions made (see above)
3. Execute phases in order
4. Commit after each phase (atomic commits)
5. Update NOW.md with cleanup status

*"Tasteful > feature-complete. Time to prune the garden."*
