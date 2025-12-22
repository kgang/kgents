# Repository Archaeology: Priors for the Self-Hosting Compiler

**Status:** Active (Phase 2-3 Complete, Phase 4: Integration pending)
**Heritage:** ASHC (Agentic Self-Hosting Compiler), M-gent (self.memory), Causal Graph Learning
**AGENTESE Context:** `self.memory.archaeology.*`
**Priority:** HUGE (feeds all three goals)

> *"The past is not dead. It is not even past."* — Faulkner
>
> *"If you grow the tree a thousand times, the pattern of growth IS the proof."* — ASHC Spec

---

## Purpose

This project mines the kgents git history and codebase to extract **priors**—patterns of what worked, what didn't, and what Kent actually cares about.

**Three Interlocking Goals:**

| Goal | Output | Consumer |
|------|--------|----------|
| **Kent's Brain** | `self.memory` crystals of project history | Brain Crown Jewel |
| **Repo Cleanup** | Curated list of dead/languishing code | Session focus work |
| **ASHC Priors** | Causal graph of nudge → outcome patterns | ASHC metacompiler |

**Why this matters:**
- ASHC needs priors: "What kinds of specs succeed? What nudges correlate with pass rates?"
- Kent's brain needs history: "What did I try? What worked? What did I abandon?"
- The repo needs curation: "What can be safely deleted? What needs love?"

---

## The Core Insight

The git history is a **trace monoid of Kent's development choices**. Each commit is a nudge. Each merge is a composition. The pattern of commits IS the prior.

```
Git History
    │
    ▼
┌────────────────────────────────────────────────────────────┐
│                  ARCHAEOLOGY ENGINE                         │
│                                                             │
│  1. Parse git log → Trace[Commit]                          │
│  2. Cluster by feature/area → FeatureTrajectory            │
│  3. Classify: succeeded | abandoned | over-engineered       │
│  4. Extract causal patterns: context → commit_type → fate  │
│  5. Build CausalGraph[SpecPattern, Outcome]                │
│                                                             │
└────────────────────────────────────────────────────────────┘
    │
    ├──► self.memory crystals (Brain)
    ├──► cleanup recommendations (Session work)
    └──► ASHC priors (Causal Graph)
```

---

## Type Signatures

### Archaeological Artifacts

```python
@dataclass(frozen=True)
class Commit:
    """A single git commit as archaeological evidence."""
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: tuple[str, ...]
    insertions: int
    deletions: int

    @property
    def is_refactor(self) -> bool:
        """Refactors touch many files with low net change."""
        return len(self.files_changed) > 5 and abs(self.insertions - self.deletions) < 50

    @property
    def is_feature(self) -> bool:
        """Features add more than they remove."""
        return self.insertions > self.deletions * 2 and len(self.files_changed) > 1

    @property
    def is_fix(self) -> bool:
        """Fixes are small, targeted changes."""
        return len(self.files_changed) <= 3 and self.insertions < 50

@dataclass(frozen=True)
class FeatureTrajectory:
    """The lifecycle of a feature from inception to current state."""
    name: str                           # e.g., "AGENTESE", "K-gent", "Flux"
    first_commit: Commit
    commits: tuple[Commit, ...]
    current_status: FeatureStatus       # THRIVING | STABLE | LANGUISHING | ABANDONED | OVER_ENGINEERED
    path_pattern: str                   # e.g., "spec/agents/k-gent/*", "impl/claude/protocols/agentese/*"

    @property
    def velocity(self) -> float:
        """Recent activity relative to total activity."""
        recent = sum(1 for c in self.commits if c.timestamp > datetime.now() - timedelta(days=30))
        return recent / max(len(self.commits), 1)

    @property
    def churn(self) -> float:
        """Total insertions + deletions / commit count."""
        return sum(c.insertions + c.deletions for c in self.commits) / max(len(self.commits), 1)

class FeatureStatus(Enum):
    THRIVING = "thriving"           # Active development, tests passing, docs current
    STABLE = "stable"               # Mature, little change needed, solid tests
    LANGUISHING = "languishing"     # Started strong, activity dropped off
    ABANDONED = "abandoned"         # No commits in months, may have broken tests
    OVER_ENGINEERED = "over_engineered"  # Lots of code, few users, high complexity
```

### Priors for ASHC

```python
@dataclass(frozen=True)
class SpecPattern:
    """A pattern extracted from successful specs."""
    pattern_type: str               # e.g., "polynomial_definition", "operad_operations", "integration_paths"
    example_specs: tuple[str, ...]  # Paths to specs that use this pattern
    success_correlation: float      # How often specs with this pattern succeeded

@dataclass(frozen=True)
class EvolutionTrace:
    """How a spec/impl pair evolved over time."""
    spec_path: str
    impl_path: str
    evolution_commits: tuple[Commit, ...]
    phases: tuple[EvolutionPhase, ...]
    final_status: FeatureStatus

    @property
    def spec_first(self) -> bool:
        """Was the spec written before implementation?"""
        spec_commits = [c for c in self.evolution_commits if self.spec_path in c.files_changed]
        impl_commits = [c for c in self.evolution_commits if self.impl_path in c.files_changed]
        return spec_commits[0].timestamp < impl_commits[0].timestamp if spec_commits and impl_commits else False

class EvolutionPhase(Enum):
    SPEC_DRAFT = "spec_draft"           # Initial spec written
    INITIAL_IMPL = "initial_impl"       # First implementation
    ITERATION = "iteration"             # Spec-impl back-and-forth
    STABILIZATION = "stabilization"     # Tests passing, bugs fixed
    POLISH = "polish"                   # Docs, cleanup, refinement
    ABANDONMENT = "abandonment"         # Activity stops
```

### Kent's Memory Crystals

```python
@dataclass(frozen=True)
class HistoryCrystal:
    """A crystallized memory of a feature's journey."""
    feature_name: str
    summary: str                        # 2-3 sentence summary
    key_insights: tuple[str, ...]       # What worked, what didn't
    emotional_valence: float            # -1.0 (frustration) to 1.0 (joy)
    lessons: tuple[str, ...]            # Extractable wisdom
    related_principles: tuple[str, ...] # Which design principles were at play

    def to_brain_crystal(self) -> dict:
        """Format for Brain Crown Jewel storage."""
        return {
            "content": self.summary + "\n\nInsights:\n" + "\n".join(f"- {i}" for i in self.key_insights),
            "tags": ["archaeology", "history", self.feature_name],
            "metadata": {
                "type": "history_crystal",
                "feature": self.feature_name,
                "valence": self.emotional_valence,
            }
        }
```

---

## Architecture

### Phase 1: Mining (This Session)

Extract raw data from git history:

```bash
# Generate commit data
git log --all --format="%H|%s|%ae|%ad|%cd" --date=iso --numstat > commits.csv

# File activity patterns
git log --all --format="" --name-only | sort | uniq -c | sort -rn > file_activity.txt

# Author patterns (mostly Kent)
git shortlog -sn --all
```

### Phase 2: Classification

Classify features by trajectory:

```python
KNOWN_FEATURES = {
    # Crown Jewels (expected: THRIVING or STABLE)
    "Brain": ["impl/claude/services/brain/*", "spec/m-gents/*"],
    "Town": ["impl/claude/services/town/*", "spec/town/*"],

    # Infrastructure (expected: STABLE)
    "PolyAgent": ["impl/claude/agents/poly/*", "spec/architecture/polyfunctor.md"],
    "AGENTESE": ["impl/claude/protocols/agentese/*", "spec/protocols/agentese*.md"],
    "Flux": ["impl/claude/agents/flux/*", "spec/agents/flux.md"],

    # Question marks (to be classified)
    "K8-gents": ["spec/k8-gents/*", "impl/claude/k8/*"],
    "Psi-gents": ["spec/psi-gents/*"],
    "Omega-gents": ["spec/omega-gents/*"],
    "Evergreen": ["spec/protocols/evergreen*.md", "impl/claude/protocols/evergreen/*"],
}

async def classify_feature(name: str, paths: list[str], commits: list[Commit]) -> FeatureTrajectory:
    """Classify a feature's current status based on commit patterns."""
    feature_commits = [c for c in commits if any(p in c.files_changed for p in paths)]

    if not feature_commits:
        return FeatureTrajectory(name=name, status=FeatureStatus.ABANDONED, ...)

    # Calculate velocity, churn, test presence
    velocity = calculate_velocity(feature_commits)
    has_tests = any("test" in c.files_changed for c in feature_commits)
    recent_activity = any(c.timestamp > datetime.now() - timedelta(days=14) for c in feature_commits)

    # Classify
    if velocity > 0.3 and recent_activity:
        status = FeatureStatus.THRIVING
    elif has_tests and velocity > 0.1:
        status = FeatureStatus.STABLE
    elif velocity < 0.05 and not recent_activity:
        status = FeatureStatus.ABANDONED if not has_tests else FeatureStatus.LANGUISHING
    else:
        status = FeatureStatus.LANGUISHING

    return FeatureTrajectory(name=name, status=status, commits=tuple(feature_commits), ...)
```

### Phase 3: Prior Extraction

Build causal graph for ASHC:

```python
class ArchaeologyPriorExtractor:
    """Extract priors from archaeological analysis."""

    async def extract_spec_patterns(self, trajectories: list[FeatureTrajectory]) -> list[SpecPattern]:
        """What patterns appear in successful specs?"""
        successful = [t for t in trajectories if t.current_status in (FeatureStatus.THRIVING, FeatureStatus.STABLE)]

        patterns = []

        # Pattern: Polynomial definition present?
        poly_specs = [t for t in successful if "polynomial" in t.spec_content.lower()]
        if poly_specs:
            patterns.append(SpecPattern(
                pattern_type="polynomial_definition",
                example_specs=tuple(t.spec_path for t in poly_specs),
                success_correlation=len(poly_specs) / len(successful)
            ))

        # Pattern: AGENTESE paths defined?
        agentese_specs = [t for t in successful if "agentese" in t.spec_content.lower()]
        if agentese_specs:
            patterns.append(SpecPattern(
                pattern_type="agentese_integration",
                example_specs=tuple(t.spec_path for t in agentese_specs),
                success_correlation=len(agentese_specs) / len(successful)
            ))

        # Pattern: Spec written before impl?
        spec_first = [t for t in successful if t.spec_first]
        if spec_first:
            patterns.append(SpecPattern(
                pattern_type="spec_first_development",
                example_specs=tuple(t.spec_path for t in spec_first),
                success_correlation=len(spec_first) / len(successful)
            ))

        return patterns

    async def build_causal_graph(self, trajectories: list[FeatureTrajectory]) -> CausalGraph:
        """Build causal graph: nudge patterns → outcomes."""
        edges = []

        for t in trajectories:
            # Each commit message is a "nudge"
            for commit in t.commits:
                nudge = Nudge(
                    location=t.name,
                    before="",  # N/A for archaeological analysis
                    after=commit.message,
                    reason=f"Commit to {t.name}"
                )

                # Outcome is the feature's final status
                outcome = 1.0 if t.current_status in (FeatureStatus.THRIVING, FeatureStatus.STABLE) else 0.0

                edges.append(CausalEdge(
                    nudge=nudge,
                    outcome_delta=outcome,
                    confidence=0.5,  # Low confidence for historical data
                    runs_observed=1
                ))

        return CausalGraph(edges=tuple(edges))
```

### Phase 4: Crystal Generation

Generate memories for Kent's brain:

```python
async def generate_history_crystals(trajectories: list[FeatureTrajectory]) -> list[HistoryCrystal]:
    """Generate memory crystals from feature trajectories."""
    crystals = []

    for t in trajectories:
        # Use LLM to summarize the feature's journey
        summary = await summarize_trajectory(t)
        insights = await extract_insights(t)
        lessons = await extract_lessons(t, principles=DESIGN_PRINCIPLES)

        crystal = HistoryCrystal(
            feature_name=t.name,
            summary=summary,
            key_insights=tuple(insights),
            emotional_valence=calculate_valence(t),
            lessons=tuple(lessons),
            related_principles=tuple(identify_principles(t))
        )

        crystals.append(crystal)

    return crystals
```

---

## Expected Outputs

### 1. Feature Trajectory Report

```markdown
# kgents Feature Archaeology Report

## THRIVING (Recent high activity, tests passing)
| Feature | Commits | Velocity | Last Active |
|---------|---------|----------|-------------|
| Brain | 87 | 0.42 | 2025-12-20 |
| AGENTESE | 156 | 0.38 | 2025-12-21 |
| Witness | 61 | 0.67 | 2025-12-21 |

## STABLE (Mature, low activity, solid tests)
| Feature | Commits | Velocity | Last Active |
|---------|---------|----------|-------------|
| PolyAgent | 34 | 0.08 | 2025-12-15 |
| Operad | 28 | 0.05 | 2025-12-14 |

## LANGUISHING (Started strong, activity dropped)
| Feature | Commits | Velocity | Last Active |
|---------|---------|----------|-------------|
| K8-gents | 45 | 0.02 | 2025-11-20 |
| Psi-gents | 12 | 0.00 | 2025-10-15 |

## OVER-ENGINEERED (High complexity, low usage)
| Feature | Commits | Test Coverage | Diagnosis |
|---------|---------|---------------|-----------|
| Evergreen | 89 | 92% | 216 tests for problem that doesn't exist |

## ABANDONED (No recent activity, broken/missing tests)
| Feature | Commits | Last Active | Fate Recommendation |
|---------|---------|-------------|---------------------|
| Omega-gents | 8 | 2025-09-01 | Archive or revive? |
```

### 2. ASHC Prior Summary

```markdown
# Extracted Priors for ASHC Metacompiler

## Spec Patterns Correlated with Success
| Pattern | Success Rate | Example |
|---------|--------------|---------|
| polynomial_definition | 0.85 | K-gent SOUL_POLYNOMIAL |
| agentese_integration | 0.78 | Brain integration |
| spec_first_development | 0.72 | Brain Crown Jewel |
| operad_operations | 0.68 | Town TOWN_OPERAD |

## Commit Message Patterns
| Pattern | Correlation with Success |
|---------|-------------------------|
| "feat(X): " prefix | +15% completion rate |
| References spec in message | +12% stability |
| "WIP" or "temp" | -20% completion rate |

## Lessons Learned (Feed to ASHC CausalGraph)
1. Specs with explicit AGENTESE paths succeed 78% of the time
2. Features without tests within 10 commits have 60% abandonment rate
3. Kent prefers polynomial models—adoption correlates with completion
```

### 3. Brain Crystals

```python
# Example crystals to store in self.memory
crystals = [
    {
        "content": """AGENTESE: The Universal Protocol

Started as just paths, evolved into the API itself. Key insight:
'The protocol IS the API—no explicit routes needed.'

What worked: Observer-dependent projection, five contexts only.
What didn't: Early attempts at too many contexts (sprawl).
Lesson: Constraint enables creativity.""",
        "tags": ["archaeology", "agentese", "success"],
        "metadata": {"type": "history_crystal", "valence": 0.9}
    },
    {
        "content": """Evergreen Prompt System: The Beautiful Mistake

216 tests for a system that solved the wrong problem.
Writing prompts is easy—verification is hard.

Became the foundation for ASHC's insight: 'We don't prove
equivalence. We observe it.'

Lesson: Over-engineering teaches what matters.""",
        "tags": ["archaeology", "evergreen", "over-engineered", "learning"],
        "metadata": {"type": "history_crystal", "valence": 0.3}
    }
]
```

---

## Laws / Invariants

### Archaeological Completeness
```
∀ Feature F with ≥10 commits:
  F ∈ FeatureTrajectory.all()
```

Every significant feature must be classified.

### Prior Validity
```
∀ SpecPattern P:
  P.success_correlation ∈ [0.0, 1.0]
  len(P.example_specs) ≥ 2
```

Patterns must have supporting evidence.

### Crystal Richness
```
∀ HistoryCrystal C:
  len(C.key_insights) ≥ 2
  len(C.lessons) ≥ 1
```

Crystals must contain actionable wisdom.

---

## Integration

### AGENTESE Paths

```
self.memory.archaeology.*
  .trajectories        # List all feature trajectories
  .classify            # Classify a specific feature
  .priors              # Get extracted priors for ASHC
  .crystals            # Get history crystals for Brain
  .cleanup             # Get cleanup recommendations

concept.compiler.priors.*
  .from_archaeology    # Load priors from archaeological analysis
  .merge               # Merge with existing causal graph
```

### CLI

```bash
# Run full archaeological analysis
kg archaeology mine

# Get feature status report
kg archaeology report

# Extract priors for ASHC
kg archaeology priors --output ashc-priors.json

# Store crystals in brain
kg archaeology crystallize
```

---

## Implementation Phases

### Phase 1: Git Mining ✅ COMPLETE
- [x] Parse git log into structured Commit objects
- [x] Identify file patterns for known features
- [x] Calculate velocity, churn, test coverage per feature

**Location:** `impl/claude/services/archaeology/mining.py`, `patterns.py`, `classifier.py`
**Tests:** 32 passing

### Phase 2: Classification & Prior Extraction ✅ COMPLETE (Session 2)
- [x] Build FeatureTrajectory for each known feature
- [x] Classify status: THRIVING | STABLE | LANGUISHING | ABANDONED | OVER_ENGINEERED
- [x] Generate human-readable report
- [x] Extract SpecPattern from successful features (4 patterns found)
- [x] Build EvolutionTrace for feature lifecycles (30 traces)
- [x] Extract CausalPrior for ASHC (5 priors)

**Location:** `impl/claude/services/archaeology/priors.py`
**Tests:** 76 passing total

**Results (805 commits):**
- 22 THRIVING features (CLI, AGENTESE, I-gents leading)
- 7 STABLE features
- 1 ABANDONED (H-gents)

### Phase 3: Crystallization ✅ COMPLETE (Session 2)
- [x] Generate HistoryCrystal for each significant feature (23 crystals)
- [x] Include emotional valence (-1.0 to 1.0)
- [x] Extract lessons and related principles
- [x] Format for Brain storage via `to_brain_crystal()`

**Location:** `impl/claude/services/archaeology/crystals.py`

### Phase 4: Integration (Next Session)
- [ ] Wire into ASHC's `concept.compiler.priors`
- [ ] Store crystals in Brain via `self.memory.capture`
- [ ] Add AGENTESE nodes for `self.memory.archaeology.*`
- [ ] Create CLI commands (`kg archaeology mine/report/crystallize`)

---

## Anti-Patterns

- **Treating history as truth**: History is evidence, not gospel. Patterns may not generalize.
- **Ignoring failures**: Abandoned features teach as much as successes.
- **Over-automation**: Some judgment calls require Kent's taste.
- **Completionism**: Not every commit needs analysis—sample the important ones.

---

## Connection to Kent's Intent

From `_focus.md`:

> *"Daring, bold, creative, opinionated but not gaudy"*
> *"The Mirror Test: Does K-gent feel like me on my best day?"*
> *"Depth over breadth"*

This project embodies these by:
1. **Daring**: Mining our own history for causal patterns
2. **Bold**: Using archaeology to seed the metacompiler
3. **Opinionated**: Classifying features as OVER_ENGINEERED when warranted
4. **Depth over breadth**: Understanding few features deeply vs. cataloging everything

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Features classified | ≥30 |
| Priors extracted | ≥10 patterns |
| Crystals generated | ≥20 |
| ASHC CausalGraph edges | ≥100 |
| Cleanup recommendations | ≥5 actionable items |

---

*"The past is not dead. It is not even past."* — Faulkner

*"To remember is to reduce surprise."* — Active Inference (M-gent pillar)

*"The artifact remembers so the agent can forget."* — Stigmergy (M-gent pillar)
