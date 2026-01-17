# Constitutional Navigation Skill

> *"The file is a lie. There is only the Constitutional Graph."*
> *"Derivation isn't something you pass. It's something you see."*

**When to use**: Implementing Constitutional awareness in editors, navigation, project visualization, or anywhere derivation context matters.

**Spec**: `plans/ashc-consumer-integration/00-master-plan.md`
**Related**: `hypergraph-editor.md`, `agentese-node-registration.md`

---

## The Paradigm Shift

Traditional navigation: `Directory -> File -> Line`
Constitutional navigation: `Principle -> Derivation Path -> Implementation`

| You don't... | You instead... |
|--------------|----------------|
| Browse directories | Navigate derivation paths |
| See files in folders | See nodes in a Constitutional Graph |
| Ask "where is this file?" | Ask "what does this derive from?" |
| Verify derivation in CI | See derivation as ambient awareness |
| Hide orphan files | Surface orphans as visible invitations |

**The radical insight**: If derivation is visible, it becomes navigable. If navigable, it becomes understandable. If understandable, it becomes natural.

---

## The Constitutional Graph

Files don't live in directories. They live in a graph where edges are derivation relationships:

```
CONSTITUTIONAL PRINCIPLES
        |
        +-- COMPOSABLE -----------------------------------------+
        |       |                                               |
        |       +-- derives --> spec/protocols/witness.md       |
        |       |                   |                           |
        |       |                   +-- derives --> services/witness/mark.py
        |       |                   |                   |
        |       |                   |                   +-- derives --> tests/test_mark.py
        |       |                   |
        |       |                   +-- derives --> services/witness/trace.py
        |       |
        |       +-- derives --> spec/protocols/operad.md
        |                           |
        |                           +-- derives --> agents/operad/core.py
        |
        +-- TASTEFUL -------------------------------------------+
        |       |                                               |
        |       +-- derives --> spec/surfaces/hypergraph-editor.md
        |                           |
        |                           +-- derives --> web/src/components/Editor.tsx
        |
        +-- ETHICAL --------------------------------------------+
                |                                               |
                +-- derives --> spec/governance/constitution.md
                                    |
                                    +-- derives --> services/constitution/floor.py

ORPHAN ZONE (visible, not hidden)
        |
        +-- impl/claude/utils/helpers.py  [awaiting derivation]
        +-- scripts/dev-server.sh         [awaiting derivation]
```

---

## Navigation Semantics Evolution

The hypergraph editor's navigation keybindings evolve to express Constitutional relationships:

### Traditional vs. Constitutional

| Key | Traditional Meaning | Constitutional Meaning |
|-----|--------------------|-----------------------|
| `gh` | Go to parent (directory) | Go to derivation source (what does this derive from?) |
| `gl` | Go to child | Go to derived file (what derives from this?) |
| `gd` | Go to definition | Go to grounding principle |
| `gp` | Go to parent spec | Browse by principle (new) |

### Implementation

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

---

## Grounding Statuses

Every K-Block has a grounding status that reflects its Constitutional position:

| Status | Meaning | Galois Loss Range |
|--------|---------|-------------------|
| `grounded` | Directly instantiates a Constitutional principle | L < 0.05 |
| `derived` | Derives through intermediate specs | 0.05 <= L < 0.30 |
| `orphan` | No derivation path found | N/A |
| `contested` | Multiple conflicting derivation paths exist | N/A |

### K-Block Derivation Type

```typescript
interface KBlockDerivation {
  source_principle: string | null;     // Which principle this derives from
  galois_loss: number;                 // Distance from principle (0.0 = perfect)
  grounding_status: 'grounded' | 'derived' | 'orphan' | 'contested';
  derivation_path: DerivationEdge[];   // Full lineage to principle
  confidence: number;                  // How certain is this derivation
}
```

### Python Implementation

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

---

## Derivation Trail Bar

The Trail Bar shows Constitutional position at a glance:

```
+----------------------------------------------------------------------+
| COMPOSABLE(0.95) -> witness.md(0.12) -> mark.py(0.08) -> [CURRENT]   |
+----------------------------------------------------------------------+
|                                                                      |
|  # Mark Implementation                                               |
|                                                                      |
|  class Mark:                                                         |
|      """A witnessed action with justification."""                    |
|      ...                                                             |
```

### What the Trail Bar Shows

| Element | Description |
|---------|-------------|
| Grounding principle | The Constitutional principle this derives from, with loss |
| Derivation chain | Each step in the path, with cumulative loss |
| Current position | The file being edited (highlighted) |

**One glance tells you**: "I'm editing mark.py, which derives from witness.md, which derives from COMPOSABLE. Total Constitutional distance: 0.15. I'm well-grounded."

### Loss Color Coding

| Loss Range | Color | Meaning |
|------------|-------|---------|
| L < 0.05 | Green | Grounded |
| 0.05 <= L < 0.15 | Blue | Well-derived |
| 0.15 <= L < 0.30 | Yellow | Acceptable |
| L >= 0.30 | Orange | Drifting |

### Trail Bar Component

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

---

## Project Realization

When you open a project, you don't see a folder structure. You see its Constitutional reality:

```
+----------------------------------------------------------------------+
|                    PROJECT REALIZATION                               |
|                                                                      |
|  kgents/impl/claude                                                  |
|                                                                      |
|  +----------------------------------------------------------------+  |
|  |  Constitutional Coverage: 87%                                  |  |
|  |  =====================                                         |  |
|  |                                                                |  |
|  |  Principle Alignment:                                          |  |
|  |    COMPOSABLE    ==================== 0.95                     |  |
|  |    TASTEFUL      =================    0.85                     |  |
|  |    ETHICAL       ==================== 0.98                     |  |
|  |    JOY_INDUCING  ============         0.62                     |  |
|  |    CURATED       ================     0.78                     |  |
|  |    HETERARCHICAL ==================== 0.91                     |  |
|  |    GENERATIVE    =============        0.67                     |  |
|  +----------------------------------------------------------------+  |
|                                                                      |
|  Recent Derivation Activity:                                         |
|    + services/witness/crystal.py grounded via COMPOSABLE (2 hrs ago) |
|    ~ spec/surfaces/elastic-ui.md drift detected, L: 0.12 -> 0.24     |
|    ? impl/claude/utils/temp.py remains orphan (3 days)               |
|                                                                      |
|  [Enter to continue]  [g to browse by principle]  [o for orphans]    |
+----------------------------------------------------------------------+
```

### What You See

| Element | Description |
|---------|-------------|
| Constitutional coverage | Percentage of K-Blocks with derivation paths |
| Principle alignment radar | Per-principle scores (1.0 - average loss) |
| Recent derivation activity | Grounding events, drift alerts, orphan reminders |
| Orphan count | How many files lack derivation |

**This is not a gate**. You can press Enter and start working immediately. But now you KNOW where you stand Constitutionally.

### Project Realization Type

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

---

## Orphan Experience

Orphan files are not errors to fix. They're opportunities to connect. The system makes them visible without shame:

```
+----------------------------------------------------------------------+
|  ORPHAN ZONE                                                         |
|                                                                      |
|  These K-Blocks have no derivation path to Constitutional principles.|
|  They work fine. They might always be orphans. Or they might be      |
|  waiting for connection.                                             |
|                                                                      |
|  impl/claude/utils/helpers.py                                        |
|  +-- Lines: 234                                                      |
|  +-- Age: 15 days                                                    |
|  +-- Suggested principle: COMPOSABLE (similarity: 0.67)              |
|  +-- [c] Connect  [i] Ignore permanently  [?] Explain                |
|                                                                      |
|  scripts/dev-server.sh                                               |
|  +-- Lines: 45                                                       |
|  +-- Age: 30 days                                                    |
|  +-- Suggested principle: None (utility script)                      |
|  +-- [i] Ignore permanently  [?] Explain                             |
|                                                                      |
|  Total orphans: 12 / 847 K-Blocks (1.4%)                             |
+----------------------------------------------------------------------+
```

**The philosophy**: Utility scripts SHOULD be orphans. Not everything needs Constitutional justification. But the system should know what it knows and show what it shows. Orphans are visible facts, not hidden shame.

---

## Implementation Checklist

When implementing Constitutional navigation:

- [ ] K-Blocks have derivation context computed on creation
- [ ] Navigation keybindings follow Constitutional semantics (gh/gl/gd/gp)
- [ ] Trail Bar shows derivation chain with loss coloring
- [ ] Project opening computes realization (non-blocking)
- [ ] Orphans are visible and actionable
- [ ] Grounding status uses correct loss thresholds

---

## Anti-patterns

| Don't | Instead |
|-------|---------|
| Treat derivation as binary pass/fail | Show derivation as navigable landscape |
| Hide orphan files | Surface them as visible invitations |
| Compute derivation on demand | Compute at K-Block birth, cache it |
| Block project opening for verification | Show realization as welcome, not gate |
| Shame orphans | Present them neutrally (some should be orphans) |

---

## Connection to Other Skills

| Skill | Connection |
|-------|------------|
| `hypergraph-editor.md` | Constitutional navigation extends the six-mode editor |
| `agentese-node-registration.md` | Constitutional queries through AGENTESE |
| `derivation-edges.md` | Edge types include derives_from |
| `witness-for-agents.md` | Derivation events are marked |

---

## Key Metrics

| Metric | Target |
|--------|--------|
| Time to understand file's Constitutional position | < 3 seconds |
| Derivation navigation success (reach principle in clicks) | < 5 clicks |
| Project realization computation time | < 5 seconds for 1000 files |
| Orphan visibility | 100% surfaced |

---

## Critical Learnings

```
Files live in graphs, not directories: Edges are derivation relationships
Navigation is Constitutional: gh = "derives from", gl = "is derived by"
Four grounding statuses: grounded, derived, orphan, contested
Trail Bar = ambient awareness: One glance shows Constitutional lineage
Project realization = welcome, not gate: Informative, not blocking
Orphans are facts, not shame: Utility scripts should be orphans
```

---

*Skill created: 2025-01-17*
*Lines: ~350*
