# Git Archaeology Backfill Strategy

> *"The past is not dead. It is not even past."* — Faulkner
>
> *"Teaching moments don't die; they become ancestors."* — Memory-First Docs

**Status:** Proposed
**Priority:** HIGH (feeds ASHC priors, Brain crystals, and Ghost Hydration)
**Heritage:** spec/protocols/repo-archaeology.md (Phases 1-3 complete, code deleted)

---

## Context

The archaeology infrastructure (76 tests, 4 modules) was built and then deleted in the Crown Jewel Cleanup (2025-12-21). The spec remains at `spec/protocols/repo-archaeology.md`. This is a perfect case for the Memory-First Docs pattern:

1. **The code exists in git history** at commit `fdd10657`
2. **The spec documents the design** with complete type signatures
3. **The wisdom should be crystallized** before we rebuild/adapt

This strategy recovers value from git history and feeds it into:
- **TeachingCrystals** (gotchas, patterns from commit messages)
- **HistoryCrystals** (feature trajectories, what worked/failed)
- **Witness Marks** (decision traces from significant commits)
- **ASHC Priors** (spec patterns that correlate with success)

---

## The Meta-Insight

We use git archaeology to:
1. Recover the archaeology code itself
2. Crystallize wisdom FROM the archaeology code
3. Run archaeology ON the repo to extract more wisdom
4. Feed everything into the unified crystal system

**The archaeology of archaeology.**

---

## Phase 1: Recovery & Assessment

### 1.1 Extract Deleted Archaeology Code

```bash
# Extract the archaeology service from before deletion
git show fdd10657:impl/claude/services/archaeology/mining.py > /tmp/mining.py
git show fdd10657:impl/claude/services/archaeology/classifier.py > /tmp/classifier.py
git show fdd10657:impl/claude/services/archaeology/priors.py > /tmp/priors.py
git show fdd10657:impl/claude/services/archaeology/crystals.py > /tmp/crystals.py
```

**Decision Point:** Do we restore to `services/archaeology/` or adapt into `services/living_docs/temporal.py`?

Recommendation: **Adapt into living_docs** (successor was designated in extinction event)

### 1.2 Assess What Still Works

| Component | Status | Location |
|-----------|--------|----------|
| `Commit` dataclass | Recoverable | Was in mining.py |
| `FeatureTrajectory` | Recoverable | Was in classifier.py |
| `HistoryCrystal` | Recoverable | Was in crystals.py |
| `SpecPattern` | Recoverable | Was in priors.py |
| 76 tests | Recoverable | Was in _tests/ |

### 1.3 Create Minimal Recovery Script

```python
# scripts/recover_archaeology.py
"""
Recover the archaeology code from git history and adapt for living_docs.
"""
import subprocess
from pathlib import Path

COMMIT = "fdd10657"
FILES = [
    "impl/claude/services/archaeology/mining.py",
    "impl/claude/services/archaeology/classifier.py",
    "impl/claude/services/archaeology/priors.py",
    "impl/claude/services/archaeology/crystals.py",
]

def recover_file(commit: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        capture_output=True, text=True
    )
    return result.stdout
```

---

## Phase 2: Git Mining Pipeline

### 2.1 Commit Parsing

Re-implement minimal git mining in `services/living_docs/temporal.py`:

```python
@dataclass(frozen=True)
class Commit:
    """A git commit as archaeological evidence."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: tuple[str, ...]
    insertions: int
    deletions: int

    @property
    def commit_type(self) -> str:
        """Extract type from conventional commit message."""
        if ": " in self.message:
            prefix = self.message.split(": ")[0]
            if "(" in prefix:
                prefix = prefix.split("(")[0]
            return prefix.lower()
        return "other"

    @property
    def scope(self) -> str | None:
        """Extract scope from conventional commit message."""
        if "(" in self.message and ")" in self.message:
            return self.message[self.message.index("(")+1:self.message.index(")")]
        return None


async def parse_git_log(max_commits: int = 1000) -> list[Commit]:
    """Parse git log into structured commits."""
    ...
```

### 2.2 Teaching Extraction from Commits

Certain commit patterns contain crystallizable wisdom:

| Pattern | Teaching Type | Example |
|---------|---------------|---------|
| `fix:` commits | gotcha | "fix: Null check needed before X" |
| Multi-file refactors | pattern | Architectural decisions |
| `BREAKING:` | critical | API changes, migration needs |
| Reverts | warning | Something didn't work |
| Same file, many commits | hotspot | Needs attention |

```python
class CommitTeachingExtractor:
    """Extract TeachingCrystals from commit messages."""

    def extract_from_fix(self, commit: Commit) -> TeachingMoment | None:
        """Fix commits often encode gotchas."""
        if commit.commit_type != "fix":
            return None

        # Parse the "what was wrong" from the message
        return TeachingMoment(
            insight=f"Bug fix: {commit.message}",
            severity="warning",
            source_module=self._infer_module(commit.files_changed),
            source_symbol=f"commit:{commit.sha[:8]}",
            evidence=f"Fixed in commit {commit.sha}",
        )

    def extract_from_revert(self, commit: Commit) -> TeachingMoment | None:
        """Reverts encode 'this approach failed'."""
        if not commit.message.lower().startswith("revert"):
            return None

        return TeachingMoment(
            insight=f"Approach reverted: {commit.message}",
            severity="critical",
            source_module=self._infer_module(commit.files_changed),
            source_symbol=f"commit:{commit.sha[:8]}",
            evidence=f"Reverted in commit {commit.sha}",
        )
```

### 2.3 Feature Trajectory Analysis

```python
class FeatureTrajectory:
    """The lifecycle of a feature from inception to current state."""

    name: str
    path_pattern: str
    commits: list[Commit]
    status: Literal["thriving", "stable", "languishing", "abandoned", "extinct"]

    @property
    def velocity(self) -> float:
        """Recent activity relative to total."""
        recent = sum(1 for c in self.commits
                    if c.timestamp > datetime.now() - timedelta(days=30))
        return recent / max(len(self.commits), 1)

    def to_history_crystal(self) -> HistoryCrystal:
        """Convert trajectory to a crystallized memory."""
        ...
```

---

## Phase 3: Crystallization Pipeline

### 3.1 Commit → TeachingCrystal

```python
async def crystallize_commits(commits: list[Commit]) -> CrystallizationStats:
    """
    Extract and crystallize teachings from commits.

    Pipeline:
    1. Filter commits with teaching potential
    2. Extract TeachingMoments
    3. Store as TeachingCrystals via BrainPersistence
    """
    extractor = CommitTeachingExtractor()
    brain = await get_service("brain_persistence")

    stats = CrystallizationStats()
    for commit in commits:
        # Try each extraction strategy
        teaching = (
            extractor.extract_from_fix(commit) or
            extractor.extract_from_revert(commit) or
            extractor.extract_from_breaking(commit)
        )

        if teaching:
            await brain.crystallize_teaching(teaching)
            stats.newly_crystallized += 1

    return stats
```

### 3.2 Trajectory → HistoryCrystal

```python
async def crystallize_trajectories(trajectories: list[FeatureTrajectory]) -> list[HistoryCrystal]:
    """
    Generate HistoryCrystals from feature trajectories.

    Uses LLM to:
    1. Summarize the feature's journey
    2. Extract key insights (what worked, what didn't)
    3. Identify emotional valence
    4. Extract lessons learned
    """
    crystals = []
    for trajectory in trajectories:
        if len(trajectory.commits) < 5:  # Skip trivial features
            continue

        crystal = await generate_history_crystal(trajectory)
        crystals.append(crystal)

    return crystals
```

### 3.3 Store in Brain

```python
async def store_history_crystals(crystals: list[HistoryCrystal]):
    """Store HistoryCrystals as Brain memories."""
    brain = await get_service("brain_persistence")

    for crystal in crystals:
        content = crystal.to_brain_crystal()
        await brain.capture(
            content=content["content"],
            tags=content["tags"],
            metadata=content["metadata"],
        )
```

---

## Phase 4: Witness Integration

### 4.1 Decision Traces from Significant Commits

Certain commits represent decisions worth witnessing:

```python
DECISION_PATTERNS = [
    r"refactor\(.*\): ",      # Architectural decisions
    r"feat\(.*\): Add ",      # New capabilities
    r"BREAKING: ",            # Breaking changes
    r"^Merge pull request",   # Merges encode approvals
]

async def create_witness_marks_from_commits(commits: list[Commit]):
    """Create Witness marks from significant commits."""
    witness = await get_service("witness")

    for commit in commits:
        if not is_significant(commit):
            continue

        # Create a retrospective mark
        await witness.mark(
            action=f"Historical: {commit.message}",
            reasoning=f"Commit {commit.sha[:8]} on {commit.timestamp}",
            principles=infer_principles(commit),
            tags=["archaeology", "historical", commit.commit_type],
        )
```

### 4.2 Backfill Fusion Decisions

Major architectural decisions in git history can be recorded as fusions:

```bash
# Example: The AD-009 decision
kg decide --fast "Removed Town, Park, Gestalt, Forge, Coalition, Muse services" \
    --reasoning "AD-009 Metaphysical Fullstack: Focus on Brain, Witness, AGENTESE" \
    --archaeological "commit:12209627"
```

---

## Phase 5: ASHC Prior Generation

### 5.1 Spec Pattern Extraction

```python
async def extract_spec_patterns(trajectories: list[FeatureTrajectory]) -> list[SpecPattern]:
    """
    Extract patterns from successful features.

    Correlates spec characteristics with feature success.
    """
    successful = [t for t in trajectories if t.status in ("thriving", "stable")]

    patterns = []

    # Pattern: Polynomial definition present?
    poly_features = [t for t in successful if has_polynomial_spec(t)]
    if poly_features:
        patterns.append(SpecPattern(
            pattern_type="polynomial_definition",
            success_correlation=len(poly_features) / len(successful),
            example_specs=[t.spec_path for t in poly_features],
        ))

    # Pattern: AGENTESE integration?
    agentese_features = [t for t in successful if has_agentese_paths(t)]
    if agentese_features:
        patterns.append(SpecPattern(
            pattern_type="agentese_integration",
            success_correlation=len(agentese_features) / len(successful),
            example_specs=[t.spec_path for t in agentese_features],
        ))

    return patterns
```

### 5.2 Feed to CausalGraph

```python
async def build_ashc_priors(patterns: list[SpecPattern]) -> CausalGraph:
    """Build causal graph for ASHC metacompiler."""
    edges = []

    for pattern in patterns:
        edge = CausalEdge(
            nudge=Nudge(
                location="spec",
                before="",
                after=pattern.pattern_type,
                reason="Archaeological correlation",
            ),
            outcome_delta=pattern.success_correlation,
            confidence=0.6,  # Historical data has medium confidence
            runs_observed=len(pattern.example_specs),
        )
        edges.append(edge)

    return CausalGraph(edges=tuple(edges))
```

---

## Phase 6: CLI & Integration

### 6.1 New CLI Commands

```bash
# Run full archaeological analysis
kg archaeology mine [--since <date>] [--max-commits 1000]

# Generate feature trajectory report
kg archaeology report [--format markdown|json]

# Crystallize teachings from commits
kg archaeology crystallize [--dry-run]

# Extract ASHC priors
kg archaeology priors [--output priors.json]

# Backfill witness marks from significant commits
kg archaeology witness [--since <date>]
```

### 6.2 AGENTESE Paths

```
self.memory.archaeology.*
  .mine                    # Parse git history
  .trajectories            # List feature trajectories
  .classify <feature>      # Classify a specific feature
  .crystallize             # Crystallize teachings
  .priors                  # Get ASHC priors

void.extinct.archaeology   # Wisdom from deleted archaeology code itself
```

### 6.3 Automation Hook

```python
# In /handoff skill or session end
async def archaeology_check():
    """Check if recent commits have uncrystallized teachings."""
    recent = await get_commits_since(last_crystallization)
    potential = [c for c in recent if has_teaching_potential(c)]

    if potential:
        print(f"📜 {len(potential)} commits may contain teachings")
        print("   Run: kg archaeology crystallize")
```

---

## Execution Order

| Phase | Task | Effort | Dependencies |
|-------|------|--------|--------------|
| 1.1 | Recover archaeology code from git | 30m | None |
| 1.2 | Assess and adapt for living_docs | 1h | 1.1 |
| 2.1 | Implement Commit parsing | 45m | 1.2 |
| 2.2 | Implement CommitTeachingExtractor | 1h | 2.1 |
| 2.3 | Implement FeatureTrajectory | 1h | 2.1 |
| 3.1 | Wire to TeachingCrystal storage | 45m | 2.2 |
| 3.2 | Implement HistoryCrystal generation | 1h | 2.3 |
| 3.3 | Wire to Brain storage | 30m | 3.2 |
| 4.1 | Create historical Witness marks | 1h | 3.1 |
| 4.2 | Backfill major Fusion decisions | 30m | 4.1 |
| 5.1 | Extract SpecPatterns | 1h | 3.2 |
| 5.2 | Build ASHC CausalGraph | 45m | 5.1 |
| 6.1 | CLI commands | 1h | All above |
| 6.2 | AGENTESE nodes | 45m | 6.1 |

**Total estimate:** ~12 hours across multiple sessions

---

## Success Criteria

| Metric | Target | Verification |
|--------|--------|--------------|
| Commits analyzed | ≥500 | `kg archaeology mine --json | jq '.count'` |
| TeachingCrystals extracted | ≥50 | `kg brain teaching count --source archaeology` |
| HistoryCrystals generated | ≥20 | `kg brain search --tag history_crystal --count` |
| Feature trajectories | ≥15 | `kg archaeology report --json | jq '.trajectories | length'` |
| ASHC priors | ≥5 | `kg archaeology priors --json | jq '. | length'` |
| Witness marks (historical) | ≥30 | `kg witness show --tag archaeological --count` |

---

## The Archaeology of Archaeology

**Recursive application:** Before implementing, crystallize what we learned from the DELETED archaeology code:

```python
# Record the archaeology code's own teachings
ARCHAEOLOGY_TEACHINGS = [
    TeachingMoment(
        insight="Git log is a trace monoid of development choices",
        severity="info",
        source_module="services.archaeology.mining",
        source_symbol="module_docstring",
        evidence="spec/protocols/repo-archaeology.md",
    ),
    TeachingMoment(
        insight="Feature velocity = recent commits / total commits",
        severity="info",
        source_module="services.archaeology.classifier",
        source_symbol="FeatureTrajectory.velocity",
        evidence="commit:fdd10657",
    ),
    TeachingMoment(
        insight="Spec-first development correlates with 72% success rate",
        severity="warning",
        source_module="services.archaeology.priors",
        source_symbol="extract_spec_patterns",
        evidence="spec/protocols/repo-archaeology.md (Results section)",
    ),
]
```

---

## The Transformative Vision

**Before:** Git history is a log. Lessons are forgotten. New sessions start fresh.

**After:** Git history is a teacher. Patterns crystallize. Wisdom accumulates.

Every `fix:` commit becomes a gotcha.
Every refactor becomes a decision trace.
Every abandoned feature becomes a lesson.
The repository remembers so the developer can forget.

---

*"To remember is to reduce surprise."* — Active Inference (M-gent pillar)

*"The artifact remembers so the agent can forget."* — Stigmergy

---

**Filed:** 2025-12-22
**Status:** Ready for execution
