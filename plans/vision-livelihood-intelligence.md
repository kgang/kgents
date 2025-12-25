# Vision: Livelihood Intelligence System

> *"kgents becomes Kent's livelihood. Not through selling to users, but through making Kent radically more capable."*

**Status**: VISION
**Created**: 2025-12-24
**Arc**: Evidence Mining → Livelihood Intelligence

---

## The Core Insight

> *"The intelligence of our data is also data."*

The original ROI model assumed generic users paying for witness marks. But kgents has only one user: Kent. The value isn't "saved $800/month vs. hypothetical non-witnessed development." The value is:

**kgents makes Kent's output worth more.**

This isn't ROI—it's **Livelihood Intelligence**: the systematic amplification of Kent's capability, decisions, and creative output into economic value.

**But here's the deeper insight**: The intelligence we compute (scores, trajectories, causality) must itself be data in the same system. Not a separate dashboard—**K-blocks, HyperEdges, and Crystals**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  THE RECURSIVE LOOP                                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│     Kent's Work  ────────────→  Witness Marks  ────────────→  Intelligence  │
│          ↑                                                          │        │
│          │                                                          │        │
│          └──────────────────────────────────────────────────────────┘        │
│                                                                              │
│     Intelligence IS data. It feeds back. Kent edits it. It improves.        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Livelihood Equation

```
Kent's Value = f(
    Decision Quality,      # Better decisions → better outcomes
    Execution Velocity,    # Faster implementation → more done
    Knowledge Retention,   # Never re-learn the same lesson
    Creative Leverage,     # One insight → many applications
    Credibility Capital    # Track record of good judgment
)
```

Each factor is **measurable** and **improvable** through kgents systems:

| Factor | kgents System | Metric |
|--------|---------------|--------|
| Decision Quality | Witness + ASHC betting | Calibration score, bullshit rate |
| Execution Velocity | ASHC compilation | Time-to-working-code |
| Knowledge Retention | Crystal hierarchy | Gotcha reuse rate |
| Creative Leverage | Derivation DAG | Reuse distance (how far ideas travel) |
| Credibility Capital | Economic accountability | Prediction accuracy over time |

---

## Intelligence as Document: The K-Block Model

Every piece of livelihood intelligence is a **document in the cosmos**:

```
.kgents/intelligence/
├── scores/
│   ├── 2025-12-24.md          # Daily livelihood score
│   ├── week-51.md             # Weekly rollup
│   └── current.md             # Live score (frequently updated)
├── trajectories/
│   ├── decision-quality.md    # Time-series data as markdown
│   ├── execution-velocity.md
│   ├── knowledge-retention.md
│   └── creative-leverage.md
├── causality/
│   ├── effective-practices.md # What works for Kent
│   ├── causal-graph.md        # Full learned causality
│   └── recommendations.md     # Current recommendations
└── digests/
    ├── 2025-W51.md            # Weekly digest (crystallized)
    └── 2025-12.md             # Monthly digest
```

### Why Documents?

1. **Editable**: Kent can open any intelligence file in a K-block, edit it, challenge it
2. **Versioned**: Cosmos append-only log tracks every intelligence update
3. **Witnessed**: Every intelligence update creates a mark
4. **Graph-linked**: HyperEdges connect intelligence to evidence
5. **Crystallizable**: Intelligence compresses through the crystal hierarchy

### Intelligence Document Structure

```markdown
<!-- .kgents/intelligence/scores/2025-12-24.md -->
# Livelihood Score: 2025-12-24

## Current Score: 0.847

### Factor Breakdown

| Factor | Score | Δ 7-day | Evidence |
|--------|-------|---------|----------|
| Decision Quality | 0.91 | +0.03 | [47 decisions](witness://decisions/2025-12-24) |
| Execution Velocity | 0.82 | +0.05 | [time-to-impl analysis](self://livelihood/trajectories/execution-velocity) |
| Knowledge Retention | 0.78 | -0.02 | [gotcha reuse](witness://gotchas/reuse) |
| Creative Leverage | 0.89 | +0.08 | [derivation depth](concept://derivation/depth) |

### Causal Attribution

This score derives from:
- 12 witness marks tagged `decision:*`
- 5 ASHC compilations with 94% success rate
- 3 crystals created (compression ratio 12:1)

<!-- @evidence witness:mark-abc123, witness:mark-def456 -->
<!-- @confidence 0.92 -->
```

### K-Block Operations on Intelligence

```python
# Intelligence is editable like any document
kblock = await kblock_service.create(".kgents/intelligence/causality/recommendations.md")

# Kent disagrees with a recommendation
await kblock.update_content("""
# Recommendations

## Effective (Validated)
- Crystallize within 2 hours of insight ✓

## Disputed (Kent Override)
~~- Reduce context-switching to < 5 topics/day~~
Kent: "Context-switching IS my creative process. Remove this."

## Pending Validation
- Morning witness review correlates with decision quality
""")

# Save creates witness mark + HyperEdge
await kblock.save(reasoning="Kent disputes context-switching recommendation")
```

---

## Intelligence as Graph: The HyperEdge Model

Livelihood intelligence creates **HyperEdges** in the WitnessedGraph:

### Edge Types for Intelligence

```python
class IntelligenceEdgeKind(Enum):
    # Score edges
    CONTRIBUTES_TO = "contributes_to"      # Mark → Score factor
    DERIVED_FROM = "derived_from"          # Score → Evidence

    # Causality edges
    CAUSES = "causes"                       # Practice → Outcome
    CORRELATES_WITH = "correlates_with"    # Weak causation
    CONTRADICTS = "contradicts"            # Kent override

    # Trajectory edges
    IMPROVES = "improves"                  # Time-series trend
    DEGRADES = "degrades"                  # Negative trend
    STABILIZES = "stabilizes"              # Flat trend
```

### Intelligence HyperEdges

```python
@dataclass(frozen=True)
class IntelligenceEdge(HyperEdge):
    """
    An edge encoding livelihood intelligence.

    These edges connect:
    - Witness marks → Score factors (evidence)
    - Practices → Outcomes (causality)
    - Time points → Trends (trajectory)
    """

    # Standard HyperEdge fields
    kind: IntelligenceEdgeKind
    source_path: str  # e.g., "witness://mark-abc123"
    target_path: str  # e.g., ".kgents/intelligence/scores/current.md#decision-quality"
    origin: str = "livelihood"  # New origin type

    # Intelligence-specific fields
    contribution: float = 0.0  # How much this edge contributes to target
    learned_at: datetime | None = None  # When causality was learned
    sample_size: int = 0  # How many observations support this edge

    @property
    def is_causal(self) -> bool:
        return self.kind in (IntelligenceEdgeKind.CAUSES, IntelligenceEdgeKind.CONTRADICTS)

    @property
    def is_disputed(self) -> bool:
        return self.kind == IntelligenceEdgeKind.CONTRADICTS
```

### Graph Queries for Intelligence

```python
# Find all evidence for current score
async for edge in graph.edges_to(".kgents/intelligence/scores/current.md"):
    if edge.origin == "livelihood":
        print(f"{edge.source_path} contributes {edge.contribution}")

# Find disputed causality (Kent overrides)
disputed = [e for e in graph.all_edges()
            if e.kind == IntelligenceEdgeKind.CONTRADICTS]

# Navigate from mark to its impact on livelihood
async for edge in graph.edges_from("witness://mark-abc123"):
    if edge.target_path.startswith(".kgents/intelligence/"):
        print(f"This mark affects: {edge.target_path}")
```

---

## Intelligence as Memory: The Crystal Model

Intelligence crystallizes through the same hierarchy as witness marks:

```
Level 0: Daily Intelligence (SESSION)
   └─ Today's scores, today's causality updates

Level 1: Weekly Intelligence (DAY)
   └─ Week's trajectory, effective practices this week

Level 2: Monthly Intelligence (WEEK)
   └─ Month's trend, validated causality

Level 3: Epoch Intelligence (EPOCH)
   └─ Long-term patterns, stable practices
```

### Intelligence Crystal Structure

```python
@dataclass(frozen=True)
class IntelligenceCrystal(Crystal):
    """
    Compressed intelligence over a time period.

    Unlike regular crystals (which compress marks),
    intelligence crystals compress scores, trajectories, and causality.
    """

    # Crystal fields
    level: int  # 0=daily, 1=weekly, 2=monthly, 3=epoch
    time_span: tuple[datetime, datetime]

    # Intelligence-specific compression
    score_summary: ScoreSummary  # Min/max/mean/trend
    trajectory_deltas: dict[str, float]  # Factor → change over period
    validated_causality: list[CausalEdge]  # High-confidence edges
    disputed_causality: list[CausalEdge]  # Kent overrides

    # Natural language summary (LLM-generated)
    insight: str  # "This week: Decision quality improved 12%..."
    recommendations: list[str]  # "Continue crystallizing within 2 hours..."

    # Provenance
    source_crystals: tuple[CrystalId, ...]  # Lower-level crystals
    source_scores: tuple[str, ...]  # Score document paths

@dataclass(frozen=True)
class ScoreSummary:
    min_score: float
    max_score: float
    mean_score: float
    trend: Literal["improving", "stable", "declining"]
    volatility: float  # Standard deviation
```

### Crystal Compression Example

```python
# End of week: Crystallize daily intelligence
weekly_crystal = await crystallizer.crystallize_intelligence(
    sources=[
        ".kgents/intelligence/scores/2025-12-18.md",
        ".kgents/intelligence/scores/2025-12-19.md",
        # ... through 2025-12-24
    ],
    level=1,  # Weekly
)

# Result:
IntelligenceCrystal(
    level=1,
    time_span=(datetime(2025, 12, 18), datetime(2025, 12, 24)),
    score_summary=ScoreSummary(
        min_score=0.72,
        max_score=0.85,
        mean_score=0.79,
        trend="improving",
        volatility=0.04
    ),
    trajectory_deltas={
        "decision_quality": +0.08,
        "execution_velocity": +0.05,
        "knowledge_retention": -0.02,
        "creative_leverage": +0.12,
    },
    validated_causality=[
        CausalEdge("crystallize_within_2hrs", "knowledge_retention", strength=0.73),
    ],
    disputed_causality=[
        CausalEdge("reduce_context_switching", "decision_quality",
                   disputed_by="Kent", reason="Context-switching IS my creative process"),
    ],
    insight="Week 51: Livelihood score improved 9% (0.72→0.85). "
            "Creative leverage drove growth (+0.12). "
            "Knowledge retention dipped slightly; consider more gotcha capture.",
    recommendations=[
        "Continue crystallizing within 2 hours of insight (validated)",
        "Increase gotcha capture rate (retention dipped)",
    ],
)
```

---

## Integration with ASHC

ASHC already has the right foundation:

### 1. **ASHCCredibility → Kent's Credibility**

```python
@dataclass
class LivelihoodCredibility:
    """
    Kent's credibility as measured by kgents.

    Every decision Kent makes (via ASHC, via Witness, via Derivation)
    accumulates into a credibility score that reflects his judgment quality.

    This is the "skin in the game" that makes kgents meaningful:
    - Confident predictions that work → credibility rises
    - Bullshit (high confidence + wrong) → credibility falls
    - Well-calibrated uncertainty → credibility stable

    The score is Kent's track record, made legible.
    """

    # Core metrics (mirroring ASHCCredibility)
    credibility: float = 1.0
    total_decisions: int = 0
    successful_predictions: int = 0
    bullshit_count: int = 0
    calibration_sum: float = 0.0

    # Livelihood-specific metrics
    creative_leverage: float = 1.0  # How many downstream uses per insight
    knowledge_velocity: float = 1.0  # How fast Kent learns (gotcha → no-repeat)
    decision_velocity: float = 1.0   # Time from question → action

    @property
    def livelihood_score(self) -> float:
        """
        Composite score representing Kent's economic capability.

        This is what kgents optimizes.
        """
        return (
            self.credibility * 0.4 +
            self.creative_leverage * 0.2 +
            self.knowledge_velocity * 0.2 +
            self.decision_velocity * 0.2
        )
```

### 2. **Evidence Mining → Livelihood Evidence**

The current evidence system mines git history to validate "witness marks help." Refactored:

```python
@dataclass(frozen=True)
class LivelihoodEvidence:
    """
    Evidence of Kent's capability amplification over time.

    Not "ROI vs. hypothetical user" but "Kent today vs. Kent yesterday."
    """

    # Decision quality trajectory
    decision_success_rate: TimeSeriesMetric
    calibration_improvement: TimeSeriesMetric
    bullshit_rate_reduction: TimeSeriesMetric

    # Execution velocity trajectory
    time_to_implementation: TimeSeriesMetric  # Hours from decision → code
    rework_ratio_reduction: TimeSeriesMetric  # Less backtracking over time

    # Knowledge retention trajectory
    gotcha_reuse_rate: TimeSeriesMetric  # How often captured lessons prevent bugs
    pattern_propagation: TimeSeriesMetric  # How far insights travel (reuse distance)

    # Creative leverage trajectory
    derivation_depth: TimeSeriesMetric  # How much derives from Kent's axioms
    idea_to_implementation: TimeSeriesMetric  # Compression of creative cycle

    def trend(self) -> Literal["improving", "stable", "declining"]:
        """Are things getting better?"""
        ...

    def weekly_digest(self) -> str:
        """Human-readable summary of livelihood health."""
        ...
```

### 3. **Causal Graph → Livelihood Causality**

ASHC's `CausalGraph` learns nudge → outcome relationships. Extended:

```python
@dataclass
class LivelihoodCausality:
    """
    What actually improves Kent's output?

    Learned through observation:
    - Which witness patterns correlate with better decisions?
    - Which crystallization habits correlate with knowledge retention?
    - Which derivation structures correlate with creative leverage?

    This is the "what works for Kent" model—his personal effectiveness graph.
    """

    # Edges learned from correlation
    witness_to_quality: CausalEdge  # More witnessing → better quality?
    crystallization_to_retention: CausalEdge  # More compression → better memory?
    derivation_to_leverage: CausalEdge  # More structure → more reuse?

    # Nudge effectiveness (what to do more/less of)
    effective_practices: list[Practice]  # Ranked by causal impact
    ineffective_practices: list[Practice]  # Things that don't help

    def recommend(self) -> Practice:
        """What should Kent do more of?"""
        ...
```

---

## The Unified Architecture: Intelligence IS the Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  THE COSMOS (append-only, witnessed)                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  CONTENT LAYER (Kent's Work)                                         │   │
│  │                                                                       │   │
│  │  spec/        impl/        docs/        plans/                       │   │
│  │    │            │            │            │                          │   │
│  │    └────────────┴────────────┴────────────┘                          │   │
│  │                      │                                                │   │
│  │              HyperEdges (implements, tests, derives_from...)         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                      │                                                      │
│                      │ CONTRIBUTES_TO edges                                 │
│                      ↓                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  INTELLIGENCE LAYER (.kgents/intelligence/)                          │   │
│  │                                                                       │   │
│  │  scores/          trajectories/      causality/       digests/       │   │
│  │    │                   │                 │               │           │   │
│  │    │                   │                 │               │           │   │
│  │    └───────────────────┴─────────────────┴───────────────┘           │   │
│  │                      │                                                │   │
│  │              IntelligenceEdges (causes, improves, contradicts...)    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                      │                                                      │
│                      │ SOURCE edges                                         │
│                      ↓                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  WITNESS LAYER (marks + crystals)                                    │   │
│  │                                                                       │   │
│  │  witness://marks/     witness://crystals/     witness://decisions/   │   │
│  │                                                                       │   │
│  │  Every action leaves a mark. Marks crystallize. Crystals inform.     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

All three layers are:
  ✓ K-Block editable (transactional isolation)
  ✓ HyperEdge connected (graph-navigable)
  ✓ Crystal compressible (memory-efficient)
  ✓ Witness traced (full audit trail)
```

### The Fourth Edge Source: LivelihoodSource

The WitnessedGraph currently has three sources:
- `sovereign` (code structure)
- `witness` (mark-based evidence)
- `spec_ledger` (spec relations)

We add a fourth:

```python
class LivelihoodSource(EdgeSourceProtocol):
    """
    Edge source for livelihood intelligence.

    Produces edges that connect:
    - Content → Score factors (contribution)
    - Practices → Outcomes (causality)
    - Time series → Trends (trajectory)
    - Kent overrides → Disputed causality
    """

    origin = "livelihood"

    async def edges_from(self, path: str) -> AsyncIterator[HyperEdge]:
        """Edges originating from this path affecting livelihood."""
        # If path is a witness mark, find its score contributions
        if path.startswith("witness://"):
            for factor in self._factors_affected_by(path):
                yield IntelligenceEdge(
                    kind=IntelligenceEdgeKind.CONTRIBUTES_TO,
                    source_path=path,
                    target_path=f".kgents/intelligence/scores/current.md#{factor}",
                    contribution=self._compute_contribution(path, factor),
                    origin="livelihood",
                )

        # If path is an intelligence doc, yield its evidence edges
        if path.startswith(".kgents/intelligence/"):
            async for edge in self._edges_from_intelligence_doc(path):
                yield edge

    async def edges_to(self, path: str) -> AsyncIterator[HyperEdge]:
        """Edges pointing to this path from livelihood system."""
        if path.startswith(".kgents/intelligence/scores/"):
            # All marks that contribute to this score
            async for mark in self._marks_contributing_to(path):
                yield IntelligenceEdge(
                    kind=IntelligenceEdgeKind.CONTRIBUTES_TO,
                    source_path=f"witness://{mark.id}",
                    target_path=path,
                    contribution=mark.contribution,
                    origin="livelihood",
                )

# Compose into unified graph
graph = sovereign >> witness >> spec_ledger >> livelihood
```

### Navigating Intelligence in Hypergraph Editor

```
NORMAL MODE (graph navigation):
  gL → Go to livelihood score for current file
  gC → Go to causality for current practice
  gT → Go to trajectory for current factor

WITNESS MODE (capturing):
  mL → Quick livelihood mark (how this affects my capability)
  mD → Dispute causality (Kent override)

COMMAND MODE:
  :livelihood → Open current score in K-Block
  :causality <practice> → View/edit causality for practice
  :trajectory <factor> → View factor trajectory
```

---

## Refactoring the Evidence Service

### FROM: ROI Model (Generic Users)

```python
# OLD: Assumes multiple users, computes dollar value
class ROICalculator:
    def calculate_monthly_value(self) -> MonthlyValue:
        # Hours saved × hourly rate
        # Bugs prevented × bug cost
        # Decisions accelerated × decision cost
        return MonthlyValue(dollar_value=800.0)  # Meaningless for Kent
```

### TO: Livelihood Model (Kent Only)

```python
# NEW: Kent's capability trajectory
class LivelihoodIntelligence:
    """
    The Crown Jewel for Kent's capability amplification.

    Integrates:
    - Witness (every action leaves a mark)
    - ASHC (empirical proof through observation)
    - Derivation (confidence-weighted structure)
    - Crystal (memory compression)

    Produces:
    - LivelihoodEvidence (trajectories over time)
    - LivelihoodCausality (what works for Kent)
    - LivelihoodScore (the optimization target)
    """

    def __init__(
        self,
        witness: WitnessPersistence,
        ashc_credibility: ASHCCredibility,
        derivation_dag: DerivationGraph,
        crystal_store: CrystalStore,
    ):
        self.witness = witness
        self.ashc = ashc_credibility
        self.derivation = derivation_dag
        self.crystals = crystal_store

    async def compute_evidence(
        self,
        since: datetime | None = None
    ) -> LivelihoodEvidence:
        """
        Compute evidence of Kent's capability trajectory.

        Uses:
        - Witness marks for decision quality
        - ASHC bets for calibration
        - Git history for execution velocity
        - Crystals for knowledge retention
        - Derivation depth for creative leverage
        """
        ...

    async def learn_causality(self) -> LivelihoodCausality:
        """
        Learn what practices improve Kent's output.

        Correlates:
        - Witness patterns with outcome quality
        - Crystal habits with knowledge retention
        - Derivation structure with reuse
        """
        ...

    async def current_score(self) -> float:
        """
        Kent's current livelihood score.

        The number kgents optimizes.
        """
        credibility = self.ashc.credibility
        evidence = await self.compute_evidence()
        return (
            credibility * 0.4 +
            evidence.decision_success_rate.latest * 0.2 +
            evidence.knowledge_velocity.latest * 0.2 +
            evidence.creative_leverage.latest * 0.2
        )
```

---

## AGENTESE Paths (Document-Centric)

Intelligence documents are navigable via AGENTESE just like any cosmos content:

```python
# SELF CONTEXT — Kent's current state
self.livelihood.manifest       # → .kgents/intelligence/scores/current.md
self.livelihood.score          # → Current score value (extracted from doc)
self.livelihood.trajectory     # → .kgents/intelligence/trajectories/
self.livelihood.causality      # → .kgents/intelligence/causality/
self.livelihood.recommend      # → .kgents/intelligence/causality/recommendations.md

# CONCEPT CONTEXT — Definitions and models
concept.livelihood.factors     # → Explain the five factors
concept.livelihood.model       # → How the score is computed
concept.livelihood.edges       # → IntelligenceEdge types

# TIME CONTEXT — Historical intelligence
time.livelihood.history        # → All score documents
time.livelihood.crystals       # → Intelligence crystals by level
time.livelihood.compare        # → Diff two time periods

# WORLD CONTEXT — External evidence
world.git.contribution         # → How current work affects score
world.ashc.credibility         # → ASHC betting outcomes
```

### Document as Node

Every intelligence document is an AGENTESE node:

```python
@node(".kgents/intelligence/scores/current",
    aspects=["score", "trajectory", "evidence"],
    effects=["witness"],  # Updates create marks
    affordances=["edit", "dispute", "crystallize"],
)
class CurrentScoreNode(BaseLogosNode):
    """
    The current livelihood score document.

    Editable in K-Block. Edits create CONTRADICTS edges when Kent disputes.
    """

    async def manifest(self) -> ScoreManifest:
        """Return current score with factor breakdown."""
        doc = await self.cosmos.read(".kgents/intelligence/scores/current.md")
        return self._parse_score_document(doc)

    async def trajectory(self, factor: str) -> TrajectoryResponse:
        """Return time-series for a specific factor."""
        doc = await self.cosmos.read(f".kgents/intelligence/trajectories/{factor}.md")
        return self._parse_trajectory(doc)

    async def dispute(self, section: str, reason: str) -> DisputeResult:
        """Kent disputes a causality claim."""
        kblock = await self.kblock_service.create(
            ".kgents/intelligence/causality/effective-practices.md"
        )
        # Add dispute annotation
        await kblock.annotate(section, f"DISPUTED: {reason}")
        await kblock.save(reasoning=f"Kent disputes: {reason}")

        # Creates CONTRADICTS edge in graph
        return DisputeResult(mark_id=kblock.mark_id)
```

---

## CLI Commands (Document-Centric)

Since intelligence is documents, CLI commands open and manipulate them:

```bash
# Core document access
kg livelihood                 # Open .kgents/intelligence/scores/current.md in K-Block
kg livelihood score           # Print current score value (quick read)
kg livelihood edit            # Open score doc in $EDITOR via K-Block
kg livelihood trajectory      # Open trajectories/ index
kg livelihood causality       # Open causality/effective-practices.md

# K-Block operations on intelligence
kg livelihood dispute "crystallize within 2hrs" --reason "Doesn't work for me"
# → Opens causality doc, adds dispute annotation, creates CONTRADICTS edge

kg livelihood validate "morning review"
# → Promotes causality from "pending" to "validated", creates CAUSES edge

# Crystal operations
kg livelihood crystallize     # Compress today's intelligence to daily crystal
kg livelihood digest          # Generate weekly digest from crystals

# Graph navigation
kg livelihood graph           # Show intelligence subgraph (scores → evidence → marks)
kg livelihood edges           # List all IntelligenceEdges for current work
kg livelihood trace <mark>    # Trace from mark → score impact

# Integration with existing commands
kg witness show --contribution    # Show each mark's contribution to score
kg decide --impact                # Show decision's effect on factors
kg morning --livelihood           # Include livelihood digest in morning coffee
```

### Example Session

```bash
$ kg livelihood score
Livelihood Score: 0.847 (↑ 0.03 from yesterday)

Factor Breakdown:
  Decision Quality:    0.91 ↑
  Execution Velocity:  0.82 ↑
  Knowledge Retention: 0.78 ↓  ← Consider more gotcha capture
  Creative Leverage:   0.89 ↑

$ kg livelihood causality
# Opens K-Block with causality doc

$ kg livelihood dispute "reduce context-switching" \
    --reason "Context-switching IS my creative process"
✓ Disputed: reduce context-switching
  Mark: mark-abc123
  Edge: CONTRADICTS → .kgents/intelligence/causality/effective-practices.md
  Reason recorded in cosmos history

$ kg livelihood crystallize
✓ Daily crystal created: intelligence-crystal-2025-12-24
  Compressed: 47 marks → 1 crystal
  Score summary: 0.72-0.85 (mean: 0.79, trend: improving)
```

---

## Implementation Phases

### Phase 1: Document Infrastructure (Foundation)

1. **Create intelligence document structure**
   ```bash
   .kgents/intelligence/
   ├── scores/current.md           # Live score document
   ├── trajectories/{factor}.md    # Per-factor time series
   ├── causality/                  # Causal relationships
   └── digests/                    # Crystallized summaries
   ```

2. **Define document schemas**
   - Score document: factor breakdown, evidence links, confidence
   - Trajectory document: time-series data as markdown tables
   - Causality document: practice → outcome with strength

3. **Register in cosmos**
   - Intelligence docs follow same append-only model
   - Every update creates cosmos entry with mark_id

### Phase 2: Edge Source Integration

1. **Create `LivelihoodSource`**
   - Implements `EdgeSourceProtocol`
   - Produces `IntelligenceEdge` for graph
   - Compose: `graph = sovereign >> witness >> spec_ledger >> livelihood`

2. **Define edge types**
   ```python
   class IntelligenceEdgeKind(Enum):
       CONTRIBUTES_TO = "contributes_to"
       CAUSES = "causes"
       CONTRADICTS = "contradicts"
       IMPROVES = "improves"
       DEGRADES = "degrades"
   ```

3. **Connect to WitnessedGraphService**
   - Register livelihood as fourth source
   - Enable graph queries for intelligence

### Phase 3: K-Block Integration

1. **Intelligence as editable documents**
   - `kg livelihood` opens score in K-Block
   - `kg livelihood dispute` adds CONTRADICTS annotation
   - All edits witnessed, all saves create edges

2. **Dispute mechanism**
   - Kent edits causality doc → CONTRADICTS edge created
   - Disputed causality excluded from recommendations
   - Human override preserved in graph

3. **K-Block hooks**
   ```python
   @on_kblock_save(".kgents/intelligence/causality/*")
   async def on_causality_edit(kblock: KBlock, delta: ContentDelta):
       # Detect disputes, create CONTRADICTS edges
       # Update recommendations based on new causality
   ```

### Phase 4: Crystal Hierarchy

1. **IntelligenceCrystal structure**
   - Extends base Crystal with score_summary, trajectory_deltas
   - Level 0: daily, Level 1: weekly, Level 2: monthly

2. **Crystallization triggers**
   - End of day → daily crystal
   - End of week → weekly crystal
   - Monthly digest → monthly crystal

3. **Crystal → Document**
   - Crystals rendered as markdown in digests/
   - Navigable in hypergraph editor

### Phase 5: ASHC Unification

1. **Shared credibility model**
   - `ASHCCredibility` is source of truth for prediction quality
   - Decision quality factor derives from ASHC calibration

2. **Causal graph connection**
   - ASHC's `CausalGraph` feeds into livelihood causality
   - Nudge effectiveness → practice effectiveness

3. **Betting on decisions**
   - Every `kg decide` is implicitly a bet
   - Resolution updates credibility + livelihood score

### Phase 6: Hypergraph UI

1. **Intelligence navigation**
   - `gL` → Go to livelihood for current file
   - Edge panel shows CONTRIBUTES_TO edges

2. **Score widget**
   - Always-visible current score in status line
   - Click → navigate to score document

3. **Trajectory sparklines**
   - Mini charts in graph sidebar
   - Click → open trajectory K-Block

---

## Success Criteria

| Metric | Threshold | Measurement |
|--------|-----------|-------------|
| Kent uses it daily | > 5 days/week | CLI invocation logs |
| Score improves over time | Positive 30-day trend | Time-series analysis |
| Causality feels accurate | Kent agrees with top 5 recommendations | Human judgment |
| Replaces external tracking | Kent stops using other productivity tools | Self-report |

---

## The Vision

In 6 months:

> Kent opens his terminal. `kg livelihood score` shows 0.85 (up from 0.72 a month ago). He checks `kg livelihood digest`:
>
> *"This week: 12 decisions witnessed, 94% calibrated. Your gotcha capture rate improved 20%. The causality model shows 'crystallizing within 2 hours of insight' correlates with 3x reuse rate. Recommendation: continue daily crystallization, reduce context-switching (detected 8 topic jumps yesterday)."*
>
> He makes a decision about API design. Before committing, he checks `kg decide --livelihood`:
>
> *"This decision affects derivation depth (+0.02) and aligns with your 'composability' principle (high-credibility claim based on 47 prior decisions). Estimated livelihood impact: +0.01."*
>
> The kgents system isn't a product—it's Kent's externalized judgment, learning what works for him, making his capability legible and improvable.

---

## Philosophical Grounding

From CONSTITUTION:

> **ARTICLE V: TRUST ACCUMULATION**
> Trust is earned through demonstrated alignment.
> Trust is lost through demonstrated misalignment.
> Trust level determines scope of permitted supersession.

Livelihood Intelligence is the operationalization of this article for Kent specifically:

- **Trust earned** = Livelihood score rises
- **Trust lost** = Bullshit detected, credibility falls
- **Demonstrated alignment** = Predictions match outcomes
- **Demonstrated misalignment** = High-confidence failures

The system has skin in the game because Kent's livelihood depends on it.

---

## Files to Create/Modify

### New: Intelligence Documents (Cosmos Content)

| Path | Purpose |
|------|---------|
| `.kgents/intelligence/scores/current.md` | Live livelihood score document |
| `.kgents/intelligence/scores/{date}.md` | Daily score snapshots |
| `.kgents/intelligence/trajectories/{factor}.md` | Per-factor time series |
| `.kgents/intelligence/causality/effective-practices.md` | Validated causality |
| `.kgents/intelligence/causality/recommendations.md` | Current recommendations |
| `.kgents/intelligence/digests/{period}.md` | Crystallized summaries |

### New: Services

| File | Action | Purpose |
|------|--------|---------|
| `services/livelihood/__init__.py` | CREATE | Crown Jewel exports |
| `services/livelihood/service.py` | CREATE | LivelihoodService (compute + persist) |
| `services/livelihood/source.py` | CREATE | LivelihoodSource (EdgeSourceProtocol) |
| `services/livelihood/edges.py` | CREATE | IntelligenceEdge, IntelligenceEdgeKind |
| `services/livelihood/crystal.py` | CREATE | IntelligenceCrystal, ScoreSummary |
| `services/livelihood/documents.py` | CREATE | Document schema parsing/generation |

### New: Integration

| File | Action | Purpose |
|------|--------|---------|
| `protocols/cli/handlers/livelihood.py` | CREATE | CLI handler (document operations) |
| `protocols/agentese/contexts/self_livelihood.py` | CREATE | AGENTESE node for intelligence docs |
| `services/witnessed_graph/sources/livelihood_source.py` | CREATE | Fourth edge source |

### Modify: Existing

| File | Action | Purpose |
|------|--------|---------|
| `services/witnessed_graph/service.py` | MODIFY | Add livelihood source to composition |
| `services/witness/crystallizer.py` | MODIFY | Add IntelligenceCrystal support |
| `protocols/cli/handlers/__init__.py` | MODIFY | Register livelihood handler |

### Archive: Legacy

| File | Action | Purpose |
|------|--------|---------|
| `services/evidence/roi.py` | ARCHIVE | Replaced by document-centric model |
| `services/evidence/correlation.py` | KEEP | Still useful for mark-commit linking |
| `services/evidence/mining.py` | KEEP | Still useful for git patterns |

---

## The Recursive Principle

> *"The intelligence of our data is also data."*

This principle has profound implications:

1. **No separate dashboards**: Intelligence lives in the same cosmos as content
2. **Editable intelligence**: Kent can dispute, refine, and evolve the system's understanding
3. **Graph-connected**: Intelligence edges connect to evidence edges connect to content edges
4. **Crystallizable**: Intelligence compresses through the same hierarchy as witness marks
5. **Witnessed**: Every intelligence update is itself a mark

The system observes Kent's work → produces intelligence → stores intelligence as documents → Kent edits documents → system observes edits → produces better intelligence.

**The loop closes. The intelligence improves. Kent's capability compounds.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│     Kent's Work  ─────→  Witness  ─────→  Intelligence Documents            │
│          ↑                                         │                         │
│          │                                         │ (editable K-Blocks)    │
│          │                                         ↓                         │
│     Improved     ←─────  Causality  ←─────  Kent's Feedback                 │
│     Practice              Learning                                           │
│                                                                              │
│     "The intelligence of our data is also data."                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

*"The proof IS the decision. The mark IS the witness. The trajectory IS the livelihood. The intelligence IS the data."*

---

**Filed**: 2025-12-24
**Author**: Claude (with Kent's voice anchors)
**Status**: Ready for Kent's review and refinement
**Integration Points**: K-Block, WitnessedGraph, Cosmos, Crystal hierarchy, ASHC
