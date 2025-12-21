# Repository Archaeology Implementation Plan

**Spec**: `spec/protocols/repo-archaeology.md`
**Phase**: IMPLEMENT (Session 1 Complete)
**Priority**: HUGE (feeds Brain, Cleanup, and ASHC)
**Session**: 2025-12-21

---

## Session 1 Results (2025-12-21)

### Completed
- [x] Brain stability verified (46 tests passing)
- [x] Created `services/archaeology/` module (32 tests passing)
- [x] Implemented `Commit` dataclass with git log parser
- [x] Implemented `FeaturePattern` registry (30 features)
- [x] Implemented `FeatureTrajectory` and classification logic
- [x] Initial archaeology analysis run (500 commits)

### Key Findings (Preliminary - 500 most recent commits)

| Status | Count | Notable |
|--------|-------|---------|
| THRIVING | 21 | CLI (111), AGENTESE (105), I-gents (82) |
| STABLE | 8 | Psi-gents, Omega-gents, Conductor |
| LANGUISHING | 0 | None in recent window |
| ABANDONED | 1 | H-gents (no tests) |
| OVER_ENGINEERED | 0 | Need full history for Evergreen analysis |

### Tests Added
- `test_mining.py` — 15 tests for Commit parsing
- `test_classifier.py` — 17 tests for classification logic

### Next Session Focus
1. Full history analysis (all 805+ commits)
2. Prior extraction for ASHC
3. HistoryCrystal generation for top features

> *"The past is not dead. It is not even past."*

---

## Vision Grounding

🎯 **GROUNDING IN KENT'S INTENT:**

*"Daring, bold, creative, opinionated but not gaudy"*
*"The Mirror Test: Does K-gent feel like me on my best day?"*
*"Depth over breadth"*

This project is **daring**—we're mining our own git history to build priors for the metacompiler. It's **opinionated**—we'll classify features as OVER_ENGINEERED when they are (hello, Evergreen). It's **deep**—we want causal patterns, not just statistics.

---

## The Three Outputs

| Output | Consumer | Value |
|--------|----------|-------|
| **History Crystals** | Brain Crown Jewel | Kent's memory of project evolution |
| **Cleanup Recommendations** | Session work | Dead code, languishing features |
| **ASHC Priors** | Metacompiler | Causal graph of nudge → outcome |

---

## Quick Facts (Pre-Research)

From initial exploration:
- **~805 total commits** in repo
- **~740 commits in 2025** (this year)
- **Oldest commit**: `766aec7e Initial commit`
- **8 Crown Jewels** in various states (Brain 100%, Witness 75%, Park 60%, etc.)
- **Known over-engineered**: Evergreen Prompt System (216 tests, wrong problem)
- **Known successes**: AGENTESE, PolyAgent, Brain, Gardener

---

## Phase 1: Git Mining (This Session)

### 1.1 Raw Data Extraction

```bash
# Run these to generate raw data

# Full commit log with stats
git log --all --format="%H|%s|%ae|%ad" --date=iso --numstat > /tmp/kgents-commits.txt

# File activity (most touched files)
git log --all --format="" --name-only | sort | uniq -c | sort -rn > /tmp/kgents-file-activity.txt

# Commit messages for pattern analysis
git log --all --oneline > /tmp/kgents-messages.txt

# Authors
git shortlog -sn --all
```

### 1.2 Known Feature Patterns

Map features to file patterns for classification:

```python
FEATURE_PATTERNS = {
    # Crown Jewels
    "Brain": ["impl/claude/services/brain/", "spec/m-gents/"],
    "Gardener": ["impl/claude/services/gardener/", "spec/protocols/gardener"],
    "Town": ["impl/claude/services/town/", "spec/town/"],
    "Park": ["impl/claude/services/park/"],
    "Forge": ["impl/claude/services/forge/"],
    "Gestalt": ["impl/claude/services/gestalt/"],
    "Witness": ["impl/claude/services/witness/"],

    # Infrastructure
    "AGENTESE": ["impl/claude/protocols/agentese/", "spec/protocols/agentese"],
    "PolyAgent": ["impl/claude/agents/poly/", "spec/architecture/polyfunctor"],
    "Operad": ["impl/claude/agents/operad/", "spec/c-gents/"],
    "Flux": ["impl/claude/agents/flux/"],
    "D-gent": ["impl/claude/agents/d/", "spec/d-gents/"],

    # Protocols
    "CLI": ["impl/claude/protocols/cli/", "spec/protocols/cli"],
    "ASHC": ["impl/claude/protocols/ashc/", "spec/protocols/agentic-self-hosting"],
    "Evergreen": ["impl/claude/protocols/evergreen/", "spec/protocols/evergreen"],

    # Speculative (check if abandoned)
    "K8-gents": ["spec/k8-gents/"],
    "Psi-gents": ["spec/psi-gents/"],
    "Omega-gents": ["spec/omega-gents/"],
    "H-gents": ["spec/h-gents/"],
    "G-gents": ["spec/g-gents/"],
    "L-gents": ["spec/l-gents/"],
}
```

### 1.3 Classification Criteria

| Status | Criteria |
|--------|----------|
| **THRIVING** | ≥5 commits in last 14 days, tests exist and passing |
| **STABLE** | Tests exist, <5 commits in 14 days but recent activity |
| **LANGUISHING** | Tests exist but <2 commits in 30 days |
| **ABANDONED** | No commits in 60 days OR no tests |
| **OVER_ENGINEERED** | High test count but low actual usage in codebase |

---

## Phase 2: Analysis Scripts

### 2.1 Commit Parser

```python
# impl/claude/services/archaeology/parser.py

from dataclasses import dataclass
from datetime import datetime
import subprocess

@dataclass(frozen=True)
class Commit:
    sha: str
    message: str
    author: str
    timestamp: datetime
    files_changed: tuple[str, ...]
    insertions: int
    deletions: int

def parse_git_log() -> list[Commit]:
    """Parse git log into structured commits."""
    result = subprocess.run(
        ["git", "log", "--all", "--format=%H|%s|%ae|%ad", "--date=iso", "--numstat"],
        capture_output=True, text=True
    )
    # Parse and return commits
    ...
```

### 2.2 Feature Classifier

```python
# impl/claude/services/archaeology/classifier.py

from enum import Enum
from datetime import datetime, timedelta

class FeatureStatus(Enum):
    THRIVING = "thriving"
    STABLE = "stable"
    LANGUISHING = "languishing"
    ABANDONED = "abandoned"
    OVER_ENGINEERED = "over_engineered"

def classify_feature(
    name: str,
    commits: list[Commit],
    file_patterns: list[str],
    now: datetime = datetime.now()
) -> FeatureStatus:
    """Classify a feature based on commit patterns."""
    feature_commits = [c for c in commits
                       if any(p in f for p in file_patterns for f in c.files_changed)]

    if not feature_commits:
        return FeatureStatus.ABANDONED

    recent = [c for c in feature_commits if c.timestamp > now - timedelta(days=14)]
    month_old = [c for c in feature_commits if c.timestamp > now - timedelta(days=30)]

    if len(recent) >= 5:
        return FeatureStatus.THRIVING
    elif len(month_old) >= 2:
        return FeatureStatus.STABLE
    elif len(month_old) >= 1:
        return FeatureStatus.LANGUISHING
    else:
        return FeatureStatus.ABANDONED
```

### 2.3 Prior Extractor

```python
# impl/claude/services/archaeology/priors.py

from dataclasses import dataclass

@dataclass(frozen=True)
class SpecPattern:
    pattern_type: str
    success_correlation: float
    example_specs: tuple[str, ...]

def extract_patterns(trajectories: list[FeatureTrajectory]) -> list[SpecPattern]:
    """Extract patterns from successful features."""
    successful = [t for t in trajectories
                  if t.status in (FeatureStatus.THRIVING, FeatureStatus.STABLE)]

    patterns = []

    # Check for polynomial definitions
    for t in successful:
        spec_content = read_spec(t.spec_path)
        if "polynomial" in spec_content.lower():
            patterns.append(...)

    return patterns
```

---

## Phase 3: Report Generation

### 3.1 Trajectory Report

Generate a human-readable report of all features:

```markdown
# kgents Repository Archaeology Report
Generated: 2025-12-21

## Executive Summary
- 805 total commits (740 in 2025)
- 24 features analyzed
- 5 THRIVING, 6 STABLE, 8 LANGUISHING, 5 ABANDONED

## THRIVING (Active development, ship-ready)
...

## Recommendations
1. Archive Omega-gents (no activity since September)
2. Consider Evergreen → ASHC migration complete
3. Park needs attention (60% complete, slowing)
```

### 3.2 ASHC Priors Export

Export priors in format ASHC expects:

```python
def export_priors_for_ashc(patterns: list[SpecPattern]) -> dict:
    """Export in ASHC CausalGraph format."""
    return {
        "spec_patterns": [
            {
                "type": p.pattern_type,
                "correlation": p.success_correlation,
                "examples": list(p.example_specs)
            }
            for p in patterns
        ],
        "commit_patterns": [
            {"pattern": "feat(X):", "correlation": 0.85},
            {"pattern": "references_spec", "correlation": 0.78},
        ]
    }
```

---

## Phase 4: Brain Integration

### 4.1 Crystal Generation

Use LLM to generate crystals from trajectories:

```python
async def generate_crystal(trajectory: FeatureTrajectory, llm: LLM) -> HistoryCrystal:
    """Generate a history crystal for a feature."""
    prompt = f"""
    Analyze this feature's journey and create a memory crystal.

    Feature: {trajectory.name}
    Status: {trajectory.status}
    Commits: {len(trajectory.commits)}
    First commit: {trajectory.first_commit.message}
    Recent commits: {[c.message for c in trajectory.commits[-5:]]}

    Create:
    1. A 2-3 sentence summary
    2. 2-3 key insights (what worked, what didn't)
    3. 1-2 lessons learned
    4. Emotional valence (-1 to 1)
    """

    response = await llm.generate(prompt)
    return parse_crystal(response)
```

### 4.2 Storage

Store crystals via Brain:

```python
async def crystallize_history(crystals: list[HistoryCrystal], brain: BrainPersistence):
    """Store history crystals in Brain."""
    for crystal in crystals:
        await brain.capture(
            content=crystal.to_brain_crystal()["content"],
            tags=crystal.to_brain_crystal()["tags"],
            metadata=crystal.to_brain_crystal()["metadata"]
        )
```

---

## Implementation Tasks

### Session 1: Git Mining
- [ ] Create `impl/claude/services/archaeology/` module
- [ ] Implement `parser.py` (Commit dataclass, git log parsing)
- [ ] Run initial analysis, export raw data
- [ ] Identify all 24+ features for classification

### Session 2: Classification
- [ ] Implement `classifier.py` (FeatureStatus, trajectory building)
- [ ] Build FeatureTrajectory for each feature
- [ ] Generate first trajectory report
- [ ] Validate classifications with manual review

### Session 3: Prior Extraction
- [ ] Implement `priors.py` (SpecPattern extraction)
- [ ] Build CausalGraph edges from commit patterns
- [ ] Export priors for ASHC
- [ ] Wire into `concept.compiler.priors`

### Session 4: Crystallization
- [ ] Implement crystal generation (LLM-assisted)
- [ ] Store crystals in Brain
- [ ] Create cleanup recommendations list
- [ ] Final report generation

---

## Success Metrics

| Metric | Target | Verification |
|--------|--------|--------------|
| Features classified | ≥24 | `len(trajectories) >= 24` |
| Priors extracted | ≥10 | `len(spec_patterns) >= 10` |
| Crystals generated | ≥15 | `brain.count(tag="archaeology") >= 15` |
| ASHC edges | ≥50 | `len(causal_graph.edges) >= 50` |
| Cleanup items | ≥5 | Manual review |

---

## Questions to Answer

Through this research:

1. **What features succeeded?** → Feed to ASHC as positive priors
2. **What features failed?** → Learn why (spec issues? no tests? premature?)
3. **What's over-engineered?** → Candidates for simplification or archival
4. **What patterns predict success?** → Spec-first? Tests early? Polynomial models?
5. **What does Kent's intuition favor?** → Features Kent returns to vs. abandons

---

## Dependencies

- ASHC Phase 3 (Causal Graph) ✅ — Can receive priors
- Brain Crown Jewel ✅ — Can store crystals
- Git repository — Obviously

---

## Anti-Patterns to Avoid

- **Analysis paralysis**: Get to 80% accuracy, not 100%
- **Over-automation**: Some classifications need Kent's judgment
- **Ignoring context**: "Abandoned" doesn't mean "bad"—some features were experiments
- **Cherry-picking**: Include failures, not just successes

---

*"If you grow the tree a thousand times, the pattern of growth IS the proof."* — ASHC

*"The artifact remembers so the agent can forget."* — M-gent Stigmergy
