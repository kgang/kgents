# ASHC Consumer Integration: Master Plan

> *"Derivation isn't something you pass. It's something you see."*
>
> *"The file is a lie. There is only the Constitutional Graph."*

**Created**: 2025-01-10
**Status**: Ready for Execution
**Philosophy**: "Daring, bold, creative, opinionated but not gaudy"
**Grounding**: Integrates with 10-week roadmap, extends trail-to-crystal pilot

---

## Vision Statement

**Constitutional grounding is not a gate developers pass—it's a surface consumers navigate.**

Traditional CI systems treat verification as binary: pass or fail. Code either derives from principles or it doesn't. You wait for the verdict. This is backwards. It treats Constitutional grounding as a chore to endure rather than a landscape to explore.

The ASHC Consumer Integration inverts this relationship completely.

Every K-Block is born knowing its derivation story. Every file lives in a Constitutional Graph, not a directory tree. When you open a project, you don't see a folder structure—you see derivation paths radiating from principles to implementation. Orphan K-Blocks aren't shameful gaps to hide; they're visible invitations to connection.

**The radical insight**: If derivation is visible, it becomes navigable. If navigable, it becomes understandable. If understandable, it becomes natural. The consumer doesn't need to understand Galois Loss or categorical laws. They see: "This file derives from COMPOSABLE with 0.92 confidence, through spec/protocols/witness.md." That's enough. That's everything.

The hypergraph editor becomes the primary surface for this experience. Not because it's the fanciest UI, but because it already thinks in graphs. The transition from "files in folders" to "nodes in derivation paths" is natural. The Trail becomes not just navigation history, but Constitutional lineage.

**What we're building**: An editor where Constitutional position is as ambient as syntax highlighting. Where derivation is something you SEE, not something you VERIFY.

---

## The Five Key Concepts

### 1. Born With Derivation Context

Every K-Block enters existence with metadata that tells its Constitutional story:

```typescript
interface KBlockDerivation {
  source_principle: string | null;     // Which principle this derives from
  galois_loss: number;                 // Distance from principle (0.0 = perfect)
  grounding_status: 'grounded' | 'derived' | 'orphan' | 'contested';
  derivation_path: DerivationEdge[];   // Full lineage to principle
  confidence: number;                  // How certain is this derivation
}
```

**Grounding statuses**:
- `grounded`: Directly instantiates a Constitutional principle (L < 0.05)
- `derived`: Derives through intermediate specs (0.05 <= L < 0.30)
- `orphan`: No derivation path found (awaiting connection)
- `contested`: Multiple conflicting derivation paths exist

This isn't computed on demand—it's part of the K-Block's identity from birth.

### 2. The Constitutional Graph

Files don't live in directories. They live in a graph where edges are derivation relationships:

```
CONSTITUTIONAL PRINCIPLES
        │
        ├── COMPOSABLE ────────────────────────────────────────┐
        │       │                                              │
        │       ├── derives ──→ spec/protocols/witness.md      │
        │       │                   │                          │
        │       │                   ├── derives ──→ services/witness/mark.py
        │       │                   │                   │
        │       │                   │                   └── derives ──→ tests/test_mark.py
        │       │                   │
        │       │                   └── derives ──→ services/witness/trace.py
        │       │
        │       └── derives ──→ spec/protocols/operad.md
        │                           │
        │                           └── derives ──→ agents/operad/core.py
        │
        ├── TASTEFUL ──────────────────────────────────────────┐
        │       │                                              │
        │       └── derives ──→ spec/surfaces/hypergraph-editor.md
        │                           │
        │                           └── derives ──→ web/src/components/Editor.tsx
        │
        └── ETHICAL ───────────────────────────────────────────┐
                │                                              │
                └── derives ──→ spec/governance/constitution.md
                                    │
                                    └── derives ──→ services/constitution/floor.py

ORPHAN ZONE (visible, not hidden)
        │
        ├── impl/claude/utils/helpers.py  [awaiting derivation]
        └── scripts/dev-server.sh         [awaiting derivation]
```

**Navigation changes**:
- `gh` (parent) now means "what does this derive from?"
- `gl` (child) now means "what derives from this?"
- `gd` (definition) goes to the grounding principle
- Directory browsing becomes principle browsing

### 3. Project Realization (Not Project Opening)

When you open a project, derivation is computed immediately—but as a WELCOME SCREEN, not a GATE.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    PROJECT REALIZATION                               │
│                                                                      │
│  kgents/impl/claude                                                  │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │  Constitutional Coverage: 87%                                   │ │
│  │  ████████████████████░░░                                        │ │
│  │                                                                 │ │
│  │  Principle Alignment:                                           │ │
│  │    COMPOSABLE   ████████████████████ 0.95                       │ │
│  │    TASTEFUL     █████████████████░░░ 0.85                       │ │
│  │    ETHICAL      ████████████████████ 0.98                       │ │
│  │    JOY_INDUCING ████████████░░░░░░░░ 0.62                       │ │
│  │    CURATED      ████████████████░░░░ 0.78                       │ │
│  │    HETERARCHICAL████████████████████ 0.91                       │ │
│  │    GENERATIVE   █████████████░░░░░░░ 0.67                       │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Recent Derivation Activity:                                         │
│    + services/witness/crystal.py grounded via COMPOSABLE (2 hrs ago) │
│    ~ spec/surfaces/elastic-ui.md drift detected, L: 0.12 → 0.24      │
│    ? impl/claude/utils/temp.py remains orphan (3 days)               │
│                                                                      │
│  [Enter to continue]  [g to browse by principle]  [o for orphans]    │
└──────────────────────────────────────────────────────────────────────┘
```

**This is not a gate**. You can press Enter and start working immediately. But now you KNOW where you stand Constitutionally. The project has realized its derivation structure.

### 4. Orphan K-Blocks: Visible and Inviting

Orphan files are not errors to fix. They're opportunities to connect. The system makes them visible without shaming:

```
┌──────────────────────────────────────────────────────────────────────┐
│  ORPHAN ZONE                                                         │
│                                                                      │
│  These K-Blocks have no derivation path to Constitutional principles.│
│  They work fine. They might always be orphans. Or they might be      │
│  waiting for connection.                                             │
│                                                                      │
│  impl/claude/utils/helpers.py                                        │
│  ├── Lines: 234                                                      │
│  ├── Age: 15 days                                                    │
│  ├── Suggested principle: COMPOSABLE (similarity: 0.67)              │
│  └── [c] Connect  [i] Ignore permanently  [?] Explain                │
│                                                                      │
│  scripts/dev-server.sh                                               │
│  ├── Lines: 45                                                       │
│  ├── Age: 30 days                                                    │
│  ├── Suggested principle: None (utility script)                      │
│  └── [i] Ignore permanently  [?] Explain                             │
│                                                                      │
│  Total orphans: 12 / 847 K-Blocks (1.4%)                             │
└──────────────────────────────────────────────────────────────────────┘
```

**The philosophy**: Utility scripts SHOULD be orphans. Not everything needs Constitutional justification. But the system should know what it knows and show what it shows. Orphans are visible facts, not hidden shame.

### 5. Derivation Trail Bar: Ambient Awareness

The Trail Bar (already in hypergraph-editor.md) evolves to show Constitutional position:

```
┌──────────────────────────────────────────────────────────────────────┐
│ COMPOSABLE(0.95) → witness.md(0.12) → mark.py(0.08) → [CURRENT]     │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  # Mark Implementation                                               │
│                                                                      │
│  class Mark:                                                         │
│      """A witnessed action with justification."""                    │
│      ...                                                             │
```

The Trail Bar shows:
- The grounding principle (with its loss from axiom)
- The derivation chain (each step with cumulative loss)
- Current position (highlighted)

**One glance tells you**: "I'm editing mark.py, which derives from witness.md, which derives from COMPOSABLE. Total Constitutional distance: 0.15. I'm well-grounded."

---

## The Five Workstreams

### Workstream Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ASHC CONSUMER INTEGRATION                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  WORKSTREAM 1              WORKSTREAM 2              WORKSTREAM 3               │
│  ═════════════            ═════════════             ═════════════              │
│  K-Block Derivation       Constitutional Graph       Project Realization        │
│  Context                  Navigation                 Experience                 │
│  (Week 1-2)               (Week 2-3)                 (Week 3-4)                 │
│                                                                                 │
│  ┌───────────┐            ┌───────────┐             ┌───────────┐              │
│  │ Derivation │            │ Graph     │             │ Welcome   │              │
│  │ Metadata   │────────────│ Store     │─────────────│ Screen    │              │
│  └───────────┘            └───────────┘             └───────────┘              │
│       │                        │                          │                     │
│       │                        │                          │                     │
│       ▼                        ▼                          ▼                     │
│  ┌───────────┐            ┌───────────┐             ┌───────────┐              │
│  │ Birth     │            │ Principle │             │ Coverage  │              │
│  │ Protocol  │────────────│ Browser   │─────────────│ Metrics   │              │
│  └───────────┘            └───────────┘             └───────────┘              │
│       │                        │                          │                     │
│       └────────────────────────┼──────────────────────────┘                     │
│                                │                                                │
│                                ▼                                                │
│                     ╔═════════════════════╗                                     │
│                     ║  INTEGRATION POINT  ║                                     │
│                     ║   (Week 4 Gate)     ║                                     │
│                     ╚═════════════════════╝                                     │
│                                │                                                │
│           ┌────────────────────┼────────────────────┐                           │
│           │                    │                    │                           │
│           ▼                    ▼                    ▼                           │
│  WORKSTREAM 4              WORKSTREAM 5                                         │
│  ═════════════            ═════════════                                        │
│  Orphan Experience         Trail Bar Evolution                                  │
│  (Week 4-5)                (Week 5-6)                                          │
│                                                                                 │
│  ┌───────────┐            ┌───────────┐                                        │
│  │ Orphan    │            │ Derivation │                                        │
│  │ Browser   │────────────│ Display    │                                        │
│  └───────────┘            └───────────┘                                        │
│       │                        │                                                │
│       ▼                        ▼                                                │
│  ┌───────────┐            ┌───────────┐                                        │
│  │ Connect   │            │ Principle  │                                        │
│  │ Workflow  │────────────│ Navigation │                                        │
│  └───────────┘            └───────────┘                                        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Workstream 1: K-Block Derivation Context (Week 1-2)

**Goal**: Every K-Block knows its Constitutional story from birth.

**Dependencies**: ASHC Path-Aware Execution (Workstream A types)

**Deliverables**:
- [ ] `KBlockDerivation` type with source_principle, galois_loss, grounding_status
- [ ] Birth protocol: compute derivation on K-Block creation
- [ ] Derivation update protocol: recompute on edit (lazy, async)
- [ ] Integration with existing K-Block monad

**Files to Create/Modify**:
```
impl/claude/services/k_block/
├── derivation.py      # KBlockDerivation, DerivationEdge
├── birth.py           # Birth protocol (modify existing)
└── _tests/
    └── test_derivation_context.py
```

**Key Implementation**:
```python
@dataclass(frozen=True)
class KBlockDerivation:
    """Constitutional context for a K-Block."""
    source_principle: str | None
    galois_loss: float
    grounding_status: Literal['grounded', 'derived', 'orphan', 'contested']
    derivation_path: tuple[DerivationEdge, ...]
    confidence: float
    computed_at: datetime

    @classmethod
    async def compute(cls, kblock: KBlock, graph: ConstitutionalGraph) -> "KBlockDerivation":
        """Compute derivation context for a K-Block."""
        paths = await graph.find_paths_to_principles(kblock.path)

        if not paths:
            return cls(
                source_principle=None,
                galois_loss=1.0,
                grounding_status='orphan',
                derivation_path=(),
                confidence=0.0,
                computed_at=datetime.utcnow(),
            )

        # Take shortest path (minimal loss)
        best_path = min(paths, key=lambda p: p.total_loss)

        status = (
            'grounded' if best_path.total_loss < 0.05
            else 'derived' if best_path.total_loss < 0.30
            else 'contested' if len(paths) > 1 and paths[0].total_loss != paths[1].total_loss
            else 'orphan'
        )

        return cls(
            source_principle=best_path.principle,
            galois_loss=best_path.total_loss,
            grounding_status=status,
            derivation_path=tuple(best_path.edges),
            confidence=1.0 - best_path.total_loss,
            computed_at=datetime.utcnow(),
        )
```

**Exit Criteria**:
- Every new K-Block has derivation context
- Derivation recomputes on significant edit (debounced)
- Integration tests pass with existing K-Block infrastructure

### Workstream 2: Constitutional Graph Navigation (Week 2-3)

**Goal**: Transform file navigation into principle navigation.

**Dependencies**: Workstream 1 (derivation context), hypergraph-editor infrastructure

**Deliverables**:
- [ ] `ConstitutionalGraph` store with principle→file edges
- [ ] Principle browser (navigate by Constitutional principle)
- [ ] Modified navigation keybindings (gh/gl/gd semantics)
- [ ] Graph visualization component

**Files to Create/Modify**:
```
impl/claude/services/constitutional_graph/
├── __init__.py
├── store.py           # ConstitutionalGraph persistence
├── navigation.py      # Navigation primitives
└── visualization.py   # Graph rendering

impl/claude/web/src/components/
└── ConstitutionalGraph/
    ├── index.tsx
    ├── PrincipleBrowser.tsx
    └── DerivationTree.tsx
```

**Key Implementation**:
```typescript
// Navigation semantics evolve
const constitutionalNavigation = {
  // gh: What does this derive from?
  gh: async () => {
    const current = await getCurrentKBlock();
    if (current.derivation.source_principle) {
      const parent = current.derivation.derivation_path[0]?.target;
      if (parent) await focusNode(parent);
    }
  },

  // gl: What derives from this?
  gl: async () => {
    const current = await getCurrentKBlock();
    const children = await graph.findDerivedFrom(current.path);
    if (children.length === 1) await focusNode(children[0]);
    else await showDerivationPicker(children);
  },

  // gd: Go to grounding principle
  gd: async () => {
    const current = await getCurrentKBlock();
    if (current.derivation.source_principle) {
      await showPrincipleDefinition(current.derivation.source_principle);
    }
  },

  // gp: Browse by principle (new)
  gp: async () => {
    await showPrincipleBrowser();
  },
};
```

**Exit Criteria**:
- Can navigate from any file to its grounding principle
- Can browse all files derived from a principle
- Graph visualization renders derivation structure

### Workstream 3: Project Realization Experience (Week 3-4)

**Goal**: Transform project opening into Constitutional awareness.

**Dependencies**: Workstream 1 + 2

**Deliverables**:
- [ ] Project realization computation (on open)
- [ ] Welcome screen with Constitutional coverage
- [ ] Principle alignment radar chart
- [ ] Recent derivation activity feed

**Files to Create/Modify**:
```
impl/claude/services/project_realization/
├── __init__.py
├── realization.py     # Compute Constitutional coverage
├── metrics.py         # Alignment metrics
└── activity.py        # Recent derivation changes

impl/claude/web/src/components/
└── ProjectRealization/
    ├── index.tsx
    ├── WelcomeScreen.tsx
    ├── CoverageBar.tsx
    ├── PrincipleRadar.tsx
    └── ActivityFeed.tsx
```

**Key Implementation**:
```python
@dataclass
class ProjectRealization:
    """Constitutional awareness of a project."""
    coverage: float  # Percentage of K-Blocks with derivation
    principle_alignment: dict[str, float]  # Per-principle scores
    orphan_count: int
    total_kblocks: int
    recent_activity: list[DerivationEvent]
    computed_at: datetime

    @classmethod
    async def compute(cls, project_path: Path) -> "ProjectRealization":
        """Realize a project's Constitutional structure."""
        graph = await ConstitutionalGraph.load(project_path)
        kblocks = await graph.all_kblocks()

        # Compute coverage
        grounded = [k for k in kblocks if k.derivation.grounding_status != 'orphan']
        coverage = len(grounded) / len(kblocks) if kblocks else 0.0

        # Compute per-principle alignment
        principles = ['COMPOSABLE', 'TASTEFUL', 'ETHICAL', 'JOY_INDUCING',
                     'CURATED', 'HETERARCHICAL', 'GENERATIVE']
        alignment = {}
        for principle in principles:
            derived = [k for k in grounded if k.derivation.source_principle == principle]
            if derived:
                alignment[principle] = 1.0 - statistics.mean(
                    k.derivation.galois_loss for k in derived
                )
            else:
                alignment[principle] = 0.0

        return cls(
            coverage=coverage,
            principle_alignment=alignment,
            orphan_count=len(kblocks) - len(grounded),
            total_kblocks=len(kblocks),
            recent_activity=await graph.recent_activity(limit=10),
            computed_at=datetime.utcnow(),
        )
```

**Exit Criteria**:
- Project opens with Constitutional awareness
- Coverage and alignment visible at a glance
- Welcome screen is informative, not blocking

### Workstream 4: Orphan Experience (Week 4-5)

**Goal**: Make orphans visible without shame, connectable without friction.

**Dependencies**: Workstream 3 (project realization)

**Deliverables**:
- [ ] Orphan browser with suggested connections
- [ ] Connect workflow (guided derivation creation)
- [ ] "Ignore permanently" workflow (utility scripts)
- [ ] Orphan metrics in project realization

**Files to Create/Modify**:
```
impl/claude/services/orphan/
├── __init__.py
├── browser.py         # Orphan enumeration and suggestions
├── connect.py         # Connection workflow
└── ignore.py          # Permanent ignore list

impl/claude/web/src/components/
└── OrphanZone/
    ├── index.tsx
    ├── OrphanList.tsx
    ├── ConnectionWizard.tsx
    └── IgnoreConfirmation.tsx
```

**Key Implementation**:
```python
@dataclass
class OrphanSuggestion:
    """Suggested connection for an orphan K-Block."""
    kblock_path: str
    suggested_principle: str | None
    similarity_score: float
    reasoning: str

async def suggest_connections(orphan: KBlock) -> list[OrphanSuggestion]:
    """Suggest Constitutional connections for an orphan."""
    # Compute semantic similarity to principle definitions
    similarities = []
    for principle in CONSTITUTIONAL_PRINCIPLES:
        definition = await get_principle_definition(principle)
        similarity = await compute_semantic_similarity(orphan.content, definition)
        if similarity > SUGGESTION_THRESHOLD:  # 0.5
            similarities.append(OrphanSuggestion(
                kblock_path=orphan.path,
                suggested_principle=principle,
                similarity_score=similarity,
                reasoning=f"Content semantically similar to {principle} definition",
            ))

    # Also check for derivation through intermediate specs
    specs = await find_similar_specs(orphan)
    for spec in specs:
        similarities.append(OrphanSuggestion(
            kblock_path=orphan.path,
            suggested_principle=spec.derivation.source_principle,
            similarity_score=spec.similarity,
            reasoning=f"Similar to {spec.path} which derives from {spec.derivation.source_principle}",
        ))

    return sorted(similarities, key=lambda s: -s.similarity_score)
```

**Exit Criteria**:
- Can browse all orphans with suggestions
- Can connect orphan to principle with guided workflow
- Can permanently ignore utility files

### Workstream 5: Trail Bar Evolution (Week 5-6)

**Goal**: Ambient Constitutional awareness in every editing session.

**Dependencies**: Workstream 1 + 2 (derivation context, navigation)

**Deliverables**:
- [ ] Derivation Trail Bar component
- [ ] Principle navigation from Trail Bar
- [ ] Loss visualization (color-coded)
- [ ] Integration with existing Trail primitive

**Files to Create/Modify**:
```
impl/claude/web/src/components/
└── TrailBar/
    ├── index.tsx
    ├── DerivationPath.tsx     # The chain display
    ├── LossIndicator.tsx      # Color-coded loss
    └── PrincipleChip.tsx      # Clickable principle
```

**Key Implementation**:
```typescript
interface DerivationTrailBarProps {
  currentPath: string;
  derivation: KBlockDerivation;
}

export const DerivationTrailBar: React.FC<DerivationTrailBarProps> = ({
  currentPath,
  derivation,
}) => {
  const lossColor = (loss: number) => {
    if (loss < 0.05) return 'green';      // Grounded
    if (loss < 0.15) return 'blue';       // Well-derived
    if (loss < 0.30) return 'yellow';     // Acceptable
    return 'orange';                       // Drifting
  };

  return (
    <div className="derivation-trail-bar">
      {derivation.source_principle && (
        <PrincipleChip
          principle={derivation.source_principle}
          loss={derivation.galois_loss}
          onClick={() => navigateToPrinciple(derivation.source_principle)}
        />
      )}

      {derivation.derivation_path.map((edge, i) => (
        <React.Fragment key={i}>
          <Arrow color={lossColor(edge.loss)} />
          <PathNode
            path={edge.target}
            loss={edge.loss}
            onClick={() => navigateToPath(edge.target)}
          />
        </React.Fragment>
      ))}

      <Arrow color={lossColor(derivation.galois_loss)} />
      <CurrentNode path={currentPath} />
    </div>
  );
};
```

**Exit Criteria**:
- Trail Bar shows derivation chain
- One-click navigation to any point in derivation
- Loss visually indicated through color

---

## Integration Points

### Integration with trail-to-crystal Pilot

The trail-to-crystal pilot (Weeks 1-6 of main roadmap) provides the foundation:

| trail-to-crystal Primitive | ASHC Consumer Use |
|---------------------------|-------------------|
| Mark | Derivation events marked when K-Blocks connect |
| Trace | Derivation history becomes traceable |
| Crystal | Project Constitutional summary crystallized |
| Trail | Derivation Trail Bar extends Trail primitive |

**Synchronization**: ASHC Consumer work begins Week 2, parallel to Galois integration. Workstreams 1-3 should complete by end of Week 4 (main roadmap), enabling integration into trail-to-crystal pilot.

### Integration with ASHC Path-Aware Execution

ASHC Consumer Integration is the UX layer on top of ASHC Path-Aware Execution:

| ASHC Path-Aware | ASHC Consumer |
|-----------------|---------------|
| DerivationPath types | KBlockDerivation wraps DerivationPath |
| Witness Bridge | Derivation events emit marks |
| Self-Awareness queries | Project Realization uses am_i_grounded() |
| Bootstrap | Project Realization shows Constitutional coverage |

**Dependency**: Workstream A (Core Types) from ASHC Path-Aware must complete before Workstream 1 here begins.

### Integration with Hypergraph Editor

The hypergraph editor (from docs/skills/hypergraph-editor.md) provides the surface:

| Hypergraph Editor Mode | ASHC Consumer Enhancement |
|-----------------------|---------------------------|
| NORMAL | Constitutional navigation (gh/gl/gd) |
| EDGE | Derivation edge creation |
| WITNESS | Derivation marks |
| Trail | Derivation Trail Bar |
| Layout | Constitutional Graph visualization |

**Extension, not replacement**: All six modes remain. Constitutional awareness is added as a layer, not a new mode.

---

## Success Criteria

### Consumer Experience Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to understand file's Constitutional position | < 3 seconds | User study: "Where does this derive from?" |
| Orphan awareness | 100% visible | All orphans surfaced in browser |
| Derivation navigation success | 90% | Can reach principle in < 5 clicks |
| Project realization time | < 5 seconds | Benchmark on 1000-file project |
| Principle alignment understandable | 4/5 users | "What does 0.85 COMPOSABLE mean?" |

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Derivation computation latency | < 100ms per K-Block | Benchmark |
| Graph query latency | < 50ms | Benchmark |
| Project realization latency | < 5s for 1000 files | Benchmark |
| Memory overhead | < 50MB for graph | Profiling |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | > 90% | pytest-cov |
| Type coverage | 100% | mypy strict |
| Integration tests | All pass | CI |
| Kent's somatic response | No disgust | Mirror Test |

---

## Timeline

### Aligned with 10-Week Roadmap

```
Main Roadmap Week 1:  Core Pipeline (trail-to-crystal primitives)
ASHC Consumer:        [Preparation - types from ASHC Path-Aware]

Main Roadmap Week 2:  Galois Integration (wasm-survivors)
ASHC Consumer:        Workstream 1: K-Block Derivation Context ████████

Main Roadmap Week 3:  ValueCompass (disney-portal)
ASHC Consumer:        Workstream 1 + 2: Constitutional Graph ████████████████

Main Roadmap Week 4:  Trail Primitive (rap-coach)
ASHC Consumer:        Workstream 2 + 3: Project Realization ████████████████
                      [INTEGRATION GATE]

Main Roadmap Week 5:  Crystal Compression (sprite-lab)
ASHC Consumer:        Workstream 4: Orphan Experience ████████

Main Roadmap Week 6:  FIRST PILOT (trail-to-crystal)
ASHC Consumer:        Workstream 5: Trail Bar Evolution ████████
                      [PILOT INTEGRATION: Constitutional Trail Bar in trail-to-crystal]

Main Roadmap Week 7-10: Remaining pilots
ASHC Consumer:        Hardening, iteration based on pilot feedback
```

### Parallel Execution Schedule

```
Week 2:
  WS1 (Derivation)  ████████████████████

Week 3:
  WS1 (Derivation)  ████████████
  WS2 (Graph)       ░░░░░░░░████████████

Week 4:
  WS2 (Graph)       ████████████████████
  WS3 (Realization) ░░░░░░░░████████████
  [GATE]            ▓▓▓▓▓▓▓▓▓▓

Week 5:
  WS3 (Realization) ████████████
  WS4 (Orphans)     ░░░░░░░░████████████

Week 6:
  WS4 (Orphans)     ████████████
  WS5 (Trail Bar)   ░░░░░░░░████████████
  [PILOT]           ▓▓▓▓▓▓▓▓▓▓

Legend:
  ████ Active work
  ░░░░ Blocked/waiting
  ▓▓▓▓ Gate/milestone
```

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Derivation computation too slow | Lazy computation, background workers, caching |
| Graph too large for memory | Pagination, lazy loading, SQLite backing |
| Users confused by Constitutional language | Plain English tooltips, "What's this?" links |
| Orphan stigma despite design | A/B test language, observe user behavior |
| Integration with existing K-Block breaks things | Feature flag, gradual rollout |
| Trail Bar too cluttered | Compact mode, hide on demand |

---

## The Mirror Test

> *"Does this feel like Kent on his best day?"*

| Anchor | How This Plan Honors It |
|--------|-------------------------|
| *"Daring, bold, creative, opinionated but not gaudy"* | Constitutional grounding as navigation, not gates—daring. File system as lie—bold. Orphans visible, not hidden—opinionated. No badges or achievements—not gaudy. |
| *"The Mirror Test"* | Every metric includes Kent's somatic response. Disgust = stop. |
| *"Tasteful > feature-complete"* | Five workstreams, not fifteen. Trail Bar evolution, not redesign. |
| *"The persona is a garden, not a museum"* | Derivations evolve. Orphans can connect. Project realizes anew each open. |
| *"Depth over breadth"* | One surface (hypergraph editor) deeply integrated with Constitutional awareness. |

---

## Grounding Statement

This plan derives from:
- **ASHC Path-Aware Execution** (the formal derivation infrastructure)
- **Hypergraph Editor Skill** (the surface we extend)
- **10-Week Execution Roadmap** (the timeline we align with)
- **trail-to-crystal Pilot** (the first validation point)

The key insight that grounds everything: **Derivation is something you SEE, not something you VERIFY.** This transforms Constitutional grounding from a developer CI concern into a consumer navigation experience.

The hypergraph editor becomes not just "a better file browser" but "the Constitutional Graph made navigable." Every K-Block knows its lineage. Every project knows its alignment. Every orphan knows it's seen.

---

*"The file is a lie. There is only the Constitutional Graph."*

*"Derivation isn't something you pass. It's something you see."*

---

**Document Metadata**
- **Lines**: ~400
- **Status**: Master Plan - ASHC Consumer Integration
- **Created**: 2025-01-10
- **Aligns with**: 10-week roadmap (Weeks 2-6)
- **Integrates with**: trail-to-crystal pilot, ASHC Path-Aware Execution
- **Owner**: Kent Gang + Claude
