---
path: ideas/impl/metrics-reflection
status: active
progress: 0
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Metrics measurement and reflection framework.
  Covers usage metrics, quality metrics, value metrics.
  Re-metabolization process for continuous improvement.
---

# Metrics and Reflection Framework

> *"What gets measured gets improved. What gets reflected upon gets transformed."*

**Purpose**: Track, measure, and learn from implementation
**Phases**: Measure → Analyze → Reflect → Re-Metabolize
**Cadence**: Per-sprint metrics, monthly reflection

---

## Part 1: Measurement Framework

### Usage Metrics

#### Command Invocation Tracking

```python
# Automatic CLI telemetry (opt-in)
@track_usage
async def handle_soul_vibe(args: Namespace) -> int:
    """Track invocation of 'kg soul vibe'."""
    # Implementation
    pass

# Telemetry data structure
class CommandTelemetry(TypedDict):
    command: str           # e.g., "soul.vibe"
    timestamp: datetime
    duration_ms: int
    success: bool
    error_type: str | None
    user_context: str      # "cli" | "script" | "api"
```

#### Metric Categories

| Category | Metrics | Collection Method |
|----------|---------|-------------------|
| **Volume** | Invocations per day/week/month | CLI telemetry |
| **Performance** | P50/P95/P99 latency | Timing middleware |
| **Reliability** | Success rate, error distribution | Error logging |
| **Adoption** | New commands used, command diversity | Usage patterns |

#### Dashboard Specification

```
┌─ USAGE METRICS DASHBOARD ─────────────────────────────────────────┐
│                                                                    │
│  Top Commands (7 days)          Response Times (P95)               │
│  ─────────────────────          ──────────────────                 │
│  1. kg soul vibe      (142)     kg parse:      120ms              │
│  2. kg oblique        (98)      kg soul vibe:   85ms              │
│  3. kg parse          (76)      kg dialectic:  340ms              │
│  4. kg dialectic      (45)      kg compose:     45ms              │
│                                                                    │
│  Success Rate: 97.2%            Error Breakdown                    │
│  ████████████████████░░ 97%     ─────────────────                  │
│                                 Timeout:    12 (1.2%)              │
│  Daily Trend                    ParseError:  8 (0.8%)              │
│  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁               Other:       7 (0.7%)              │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

### Quality Metrics

#### Test Coverage Tracking

| Metric | Target | Measurement |
|--------|--------|-------------|
| Line Coverage | >= 94% | `pytest --cov` |
| Branch Coverage | >= 90% | `pytest --cov-branch` |
| Type Coverage | 100% | `mypy --strict` |
| Mutation Score | >= 80% | `mutmut run` |

#### Code Quality Scores

```python
# Quality score calculation
def calculate_quality_score(module: str) -> QualityScore:
    return QualityScore(
        test_coverage=get_test_coverage(module),
        type_coverage=get_type_coverage(module),
        lint_score=get_lint_score(module),
        complexity=get_cyclomatic_complexity(module),
        doc_coverage=get_doc_coverage(module)
    )

# Composite score
composite = (
    test_coverage * 0.3 +
    type_coverage * 0.2 +
    lint_score * 0.2 +
    (1 - complexity_normalized) * 0.15 +
    doc_coverage * 0.15
)
```

#### Bug Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Bug Escape Rate | Bugs found in prod / total bugs | < 5% |
| Mean Time to Detect | Time from introduction to discovery | < 24 hours |
| Mean Time to Fix | Time from detection to fix | < 4 hours |
| Regression Rate | Fixed bugs that reappear | < 2% |

---

### Value Metrics

#### Developer Experience (DX) Score

```
DX Score = (Ease × 0.3) + (Speed × 0.3) + (Joy × 0.2) + (Power × 0.2)

Where:
- Ease: How easy to use (1-10 self-rating)
- Speed: Time saved vs alternative (estimated hours)
- Joy: How enjoyable to use (1-10 self-rating)
- Power: Capability unlocked (1-10 self-rating)
```

#### Time Savings Estimation

| Task | Without kgents | With kgents | Savings |
|------|----------------|-------------|---------|
| Soul check | 10 min (manual reflection) | 5 sec | 9.9 min |
| Parse analysis | 5 min (manual inspection) | 2 sec | 4.97 min |
| Dialectical synthesis | 30 min (thinking) | 10 sec | 29.8 min |
| Code review ethics | 15 min (checklist) | 30 sec | 14.5 min |

#### Feature Request Tracking

```python
class FeatureRequest(TypedDict):
    id: str
    title: str
    description: str
    requested_by: str
    requested_at: datetime
    priority: int  # User-assigned 1-10
    implemented: bool
    implementation_date: datetime | None
```

---

### Sprint Metrics Summary

| Sprint | Commands Shipped | Test Coverage | Bugs Found | DX Score |
|--------|-----------------|---------------|------------|----------|
| 1 | 10 | 95% | 3 | - |
| 2 | 15 | 94% | 5 | - |
| 3 | 12 | 96% | 2 | - |
| 4 | 20 | 94% | 4 | - |
| 5 | 8 | 95% | 6 | - |
| 6 | - | 94% | - | 8.5 |

---

## Part 2: Analysis Framework

### Weekly Analysis

**Schedule**: Every Friday
**Duration**: 30 minutes
**Output**: `plans/metrics/week-YYYY-WW.md`

**Template**:
```markdown
# Week [NUMBER] Metrics Analysis

## Usage Summary
- Total invocations: [N]
- Most used: [command] ([N] times)
- Least used: [command] ([N] times)
- New commands tried: [list]

## Quality Summary
- Test coverage: [X]%
- Bugs introduced: [N]
- Bugs fixed: [N]
- Outstanding issues: [N]

## Observations
- [Observation 1]
- [Observation 2]

## Actions
- [ ] [Action 1]
- [ ] [Action 2]
```

### Monthly Analysis

**Schedule**: First Monday of month
**Duration**: 1 hour
**Output**: `plans/metrics/month-YYYY-MM.md`

**Sections**:
1. Usage trends (growth, decline)
2. Quality trajectory (improving, stable, declining)
3. Value delivered (time saved, problems solved)
4. Pain points identified
5. Opportunities spotted

---

## Part 3: Reflection Framework

### The Five Reflection Questions

After each major milestone, answer:

1. **What worked?**
   - Which implementations exceeded expectations?
   - Which patterns proved valuable?
   - Which decisions were good?

2. **What didn't work?**
   - Which implementations underperformed?
   - Which patterns failed?
   - Which decisions were poor?

3. **What surprised us?**
   - Unexpected successes
   - Unexpected failures
   - Emergent behaviors

4. **What did we learn?**
   - New insights about agents
   - New insights about composition
   - New insights about the problem space

5. **What would we do differently?**
   - Process changes
   - Technical changes
   - Priority changes

### Reflection Template

```markdown
# [Milestone] Reflection

## Context
- Sprint: [N]
- Date: [YYYY-MM-DD]
- Features shipped: [list]

## The Five Questions

### What Worked?
- [Item 1]: [Why it worked]
- [Item 2]: [Why it worked]

### What Didn't Work?
- [Item 1]: [Why it failed]
- [Item 2]: [Why it failed]

### What Surprised Us?
- [Surprise 1]: [Implications]
- [Surprise 2]: [Implications]

### What Did We Learn?
- [Learning 1]: [How to apply]
- [Learning 2]: [How to apply]

### What Would We Do Differently?
- [Change 1]: [Rationale]
- [Change 2]: [Rationale]

## Action Items
- [ ] [Immediate action]
- [ ] [Near-term action]
- [ ] [Long-term action]
```

---

## Part 4: Re-Metabolization Process

### Pattern Extraction

When a pattern proves valuable:

1. **Document in skills/**:
```markdown
# plans/skills/[pattern-name].md

## Pattern: [Name]

### When to Use
[Circumstances]

### Implementation
[Code/steps]

### Examples
[Real examples from codebase]

### Pitfalls
[Common mistakes]
```

2. **Add to CLAUDE.md**:
```markdown
## Skills Directory

| Skill | Description |
|-------|-------------|
| [new-pattern] | [One-liner] |
```

### Anti-Pattern Documentation

When a pattern proves harmful:

1. **Document in plans/meta.md**:
```markdown
## Anti-Patterns

### [Anti-Pattern Name]
- **What it is**: [Description]
- **Why it fails**: [Explanation]
- **Better alternative**: [Suggestion]
- **Discovered**: [Date, sprint]
```

### Idea Generation

Insights feed back into creative exploration:

1. **New ideas → `plans/ideas/session-16-*.md`**
2. **Refined ideas → Update existing session files**
3. **Dead ideas → Archive with explanation**

### Knowledge Transfer

```
Lessons Learned
    ↓
skills/ (patterns)
    ↓
meta.md (anti-patterns)
    ↓
Session 16+ (new ideas)
    ↓
Next Implementation Cycle
```

---

## Metric Collection Implementation

### Telemetry Module

```python
# impl/claude/protocols/cli/telemetry.py
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import json

@dataclass
class TelemetryEvent:
    command: str
    timestamp: datetime
    duration_ms: int
    success: bool
    error_type: str | None = None

class TelemetryCollector:
    """Collect and store CLI usage telemetry."""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.events: list[TelemetryEvent] = []

    def record(self, event: TelemetryEvent) -> None:
        """Record a telemetry event."""
        self.events.append(event)
        self._persist(event)

    def _persist(self, event: TelemetryEvent) -> None:
        """Persist event to disk."""
        with open(self.data_path / "telemetry.jsonl", "a") as f:
            f.write(json.dumps(event.__dict__, default=str) + "\n")

    def get_summary(self, days: int = 7) -> dict:
        """Get usage summary for the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [e for e in self.events if e.timestamp > cutoff]

        return {
            "total_invocations": len(recent),
            "success_rate": sum(e.success for e in recent) / len(recent),
            "commands": Counter(e.command for e in recent),
            "avg_duration_ms": sum(e.duration_ms for e in recent) / len(recent)
        }
```

### Quality Tracking

```python
# impl/claude/protocols/cli/quality.py
import subprocess

def get_test_coverage(path: str = ".") -> float:
    """Get test coverage percentage."""
    result = subprocess.run(
        ["uv", "run", "pytest", "--cov=impl", "--cov-report=json", "-q"],
        capture_output=True, text=True
    )
    # Parse coverage.json
    with open("coverage.json") as f:
        data = json.load(f)
    return data["totals"]["percent_covered"]

def get_quality_report() -> dict:
    """Generate comprehensive quality report."""
    return {
        "test_coverage": get_test_coverage(),
        "type_coverage": get_type_coverage(),
        "lint_issues": get_lint_issues(),
        "complexity": get_complexity_metrics(),
        "doc_coverage": get_doc_coverage()
    }
```

---

## Reporting Schedule

| Report | Frequency | Owner | Audience |
|--------|-----------|-------|----------|
| Usage Summary | Daily | Automated | Developer |
| Quality Report | Per-PR | CI | Developer |
| Sprint Metrics | Bi-weekly | Developer | Self |
| Monthly Reflection | Monthly | Developer | Self |
| Quarterly Review | Quarterly | Developer | Self |

---

## Dashboard Commands

```bash
# View usage metrics
kg metrics usage

# View quality metrics
kg metrics quality

# Generate report
kg metrics report --period week

# Start dashboard TUI
kg dash metrics
```

---

## Success Criteria

| Timeframe | Criterion | Target |
|-----------|-----------|--------|
| Sprint 6 | Usage tracking live | 100% commands tracked |
| Sprint 6 | Quality tracking live | Automated per-PR |
| Month 3 | First monthly reflection complete | Document exists |
| Month 3 | 5+ patterns extracted to skills/ | Pattern count |
| Month 6 | Re-metabolization cycle complete | Ideas → Impl → Learn → Ideas |

---

## Metric Storage

```
~/.kgents/
├── telemetry/
│   ├── usage.jsonl           # Raw usage events
│   └── aggregates/
│       ├── daily-YYYY-MM-DD.json
│       └── weekly-YYYY-WW.json
│
├── quality/
│   ├── coverage.json         # Latest coverage
│   └── history/
│       └── coverage-YYYY-MM-DD.json
│
└── reflections/
    ├── week-YYYY-WW.md
    └── month-YYYY-MM.md
```

---

## Privacy and Data Handling

- All telemetry is local-only by default
- No external transmission without explicit opt-in
- Data can be cleared with `kg metrics clear`
- User controls retention period

---

*"The unexamined code is not worth shipping."*
