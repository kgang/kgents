# Validation Framework

**Status:** Implemented
**Implementation:** `impl/claude/services/validation/`
**Tests:** 92 passing

> *"If you can't measure it, you can't claim it."*

---

## Purpose

A project-wide system for defining success criteria, running experiments, and making evidence-based go/no-go decisions. Validation transforms aspirational claims into witnessed propositions.

---

## Core Insight

**Validation is witnessed measurement.** Every check emits a Mark. Every gate decision is a decision with Toulmin proof. The validation framework is the first-class citizen that makes "this works" provable.

---

## The Three Primitives

### 1. Proposition

The atomic unit of validation. A claim that can be measured.

```python
@dataclass(frozen=True)
class Proposition:
    """A measurable claim."""
    id: str                    # Unique within initiative
    description: str           # Human-readable claim
    metric: MetricType         # How to measure
    threshold: float           # Success boundary
    direction: Direction       # ">", "<", ">=", "<=", "="
    required: bool = True      # Does this block gates?

    # For qualitative propositions
    judgment_required: bool = False  # Needs human judgment?
    judgment_criteria: str = ""      # What should human assess?
```

### 2. Gate

A decision point. Aggregates propositions into a go/no-go moment.

```python
@dataclass(frozen=True)
class Gate:
    """A decision checkpoint."""
    id: str
    name: str
    condition: GateCondition   # How to aggregate
    propositions: tuple[str, ...]  # Proposition IDs

class GateCondition(Enum):
    ALL_REQUIRED = "all_required"  # All required props pass
    ANY = "any"                    # Any prop passes
    QUORUM = "quorum"              # N of M pass
    CUSTOM = "custom"              # Custom aggregation function
```

### 3. Initiative

A body of work that needs validation. May have phases (linear) or be flat.

```python
@dataclass
class Initiative:
    """A validatable body of work."""
    id: str
    name: str
    description: str

    # Structure (one of these)
    phases: tuple[Phase, ...] = ()       # Phased work (linear DAG)
    propositions: tuple[Proposition, ...] = ()  # Flat work (single gate)

    # Witness integration
    witness_tags: tuple[str, ...] = ("validation",)

@dataclass
class Phase:
    """A stage within a phased initiative."""
    id: str
    name: str
    gate: Gate
    depends_on: tuple[str, ...] = ()  # Phase IDs that must pass first
```

---

## Type Signatures

### Metric Types

```python
class MetricType(Enum):
    """Kinds of measurements."""
    # Quantitative
    ACCURACY = "accuracy"        # 0.0 - 1.0
    RECALL = "recall"            # 0.0 - 1.0
    PRECISION = "precision"      # 0.0 - 1.0
    F1 = "f1"                    # 0.0 - 1.0
    AUC = "auc"                  # 0.0 - 1.0
    PEARSON_R = "pearson_r"      # -1.0 - 1.0
    COUNT = "count"              # Integer
    PERCENT = "percent"          # 0 - 100
    DURATION_MS = "duration_ms"  # Milliseconds

    # Qualitative
    BINARY = "binary"            # 0 or 1
    ORDINAL = "ordinal"          # 1-5 rating
    JUDGMENT = "judgment"        # Human assessment

class Direction(Enum):
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    EQ = "="
```

### Validation Results

```python
@dataclass(frozen=True)
class PropositionResult:
    """Result of validating a single proposition."""
    proposition_id: str
    value: float | None         # None if not measured
    passed: bool
    timestamp: datetime

    # Witness integration
    mark_id: MarkId | None = None  # The Mark that recorded this

@dataclass(frozen=True)
class GateResult:
    """Result of evaluating a gate."""
    gate_id: str
    proposition_results: tuple[PropositionResult, ...]
    passed: bool
    timestamp: datetime

    # Witness integration (decision)
    decision_id: str | None = None  # kg decide result

@dataclass(frozen=True)
class ValidationRun:
    """Complete validation run for an initiative."""
    initiative_id: str
    phase_id: str | None        # None for flat initiatives
    gate_result: GateResult
    measurements: dict[str, float]
    timestamp: datetime
```

---

## Laws

### Law 1: Witness Integration

Every validation run produces exactly one Mark per proposition measured, plus one decision Mark for the gate.

```
len(marks) == len(propositions_measured) + 1
```

### Law 2: Gate Monotonicity

Once a gate passes, it can only be invalidated by explicit re-run, not by time or external state.

```
passed_at(t1) ∧ ¬re_run → passed_at(t2)  ∀t2 > t1
```

### Law 3: Dependency Ordering

A phase cannot be validated until all its dependencies have passed.

```
validate(phase) → all(passed(dep) for dep in phase.depends_on)
```

### Law 4: Blocker Visibility

Any proposition that blocks a gate MUST be surfaced in blocker queries.

```
¬passed(prop) ∧ prop.required → prop ∈ blockers(gate)
```

---

## Built-in Initiatives

### Crown Jewels

Each jewel has a completion definition. Not all are phased.

```yaml
brain:
  name: "Brain Crown Jewel"
  propositions:
    - id: tests_pass
      metric: binary
      threshold: 1
      description: "All Brain tests pass"
    - id: spatial_cathedral_functional
      metric: binary
      threshold: 1
      description: "Spatial cathedral navigable"
    - id: teaching_crystal_works
      metric: binary
      threshold: 1
      description: "TeachingCrystal crystallizes correctly"
  gate:
    condition: all_required

witness:
  name: "Witness Crown Jewel"
  propositions:
    - id: tests_pass
      metric: count
      threshold: 600
      direction: ">="
      description: "At least 600 tests pass"
    - id: marks_persisted
      metric: binary
      threshold: 1
      description: "Marks persist across sessions"
    - id: crystals_promote
      metric: binary
      threshold: 1
      description: "Crystals promote through hierarchy"
```

### Categorical Machine Reasoning (Phased)

The original use case, now a registered initiative:

```yaml
categorical_reasoning:
  name: "Categorical Machine Reasoning"
  phases:
    - id: foundations
      name: "Phase 1: Foundations"
      gate:
        condition: all_required
      propositions:
        - id: monad_identity_correlation
          metric: pearson_r
          threshold: 0.3
          direction: ">"
        - id: sheaf_coherence_correlation
          metric: pearson_r
          threshold: 0.4
          direction: ">"

    - id: integration
      name: "Phase 2: Integration"
      depends_on: [foundations]
      gate:
        condition: all_required
      # ... more propositions
```

---

## Integration

### AGENTESE Paths

```
concept.validation.status         # Overview of all initiatives
concept.validation.run            # Run validation for an initiative
concept.validation.blockers       # What's blocking progress?
concept.validation.history        # Past runs for an initiative
```

### CLI Commands

```bash
kg validate <initiative> [phase]     # Run validation
kg validate status                   # All initiatives overview
kg validate blockers                 # What's blocking anywhere?
kg validate history <initiative>     # Validation history
```

### Witness Integration

```python
# Every measurement becomes a Mark
mark = Mark.from_thought(
    content=f"Measured {prop.id}: {value} {prop.direction} {prop.threshold}",
    source="validation",
    tags=("validation", initiative.id, prop.id),
)

# Every gate decision uses kg decide
decision = await kg_decide(
    fast=True,
    choice=f"Gate {gate.id}: {'PASS' if passed else 'BLOCKED'}",
    reasoning=f"{'All' if passed else 'Not all'} required propositions satisfied",
)
```

---

## Engine Interface

```python
class ValidationEngine(Protocol):
    """Core validation operations."""

    def register_initiative(self, config: Initiative) -> None:
        """Register an initiative for validation."""

    async def validate(
        self,
        initiative_id: str,
        phase_id: str | None = None,
        measurements: dict[str, float] | None = None,
    ) -> ValidationRun:
        """
        Run validation for an initiative.

        If measurements not provided, runs experiment runners to collect them.
        """

    def get_status(self, initiative_id: str) -> InitiativeStatus:
        """Get current status of an initiative."""

    def get_blockers(self) -> list[Blocker]:
        """Get all blockers across all initiatives."""

    def get_history(
        self,
        initiative_id: str,
        limit: int = 10,
    ) -> list[ValidationRun]:
        """Get past validation runs."""
```

---

## Anti-Patterns

- **Untraceable validation**: Running checks without Witness integration (violates Law 1)
- **Floating gates**: Gates with no propositions (vacuous truth)
- **Circular dependencies**: Phase A depends on B depends on A
- **Required-less initiatives**: All propositions optional (what's the point?)
- **Magic thresholds**: Thresholds without justification (should be witnessed decisions)

---

## Design Notes

### Progressive Complexity

Simple case (flat initiative):
```yaml
my_feature:
  propositions:
    - id: tests_pass
      metric: binary
      threshold: 1
```

Complex case (phased with custom gate):
```yaml
my_research:
  phases:
    - id: phase1
      gate:
        condition: custom
        custom_fn: "at_least_2_of_3_correlate"
```

### Qualitative Propositions

For things that need human judgment:

```yaml
- id: ui_feels_right
  metric: judgment
  judgment_required: true
  judgment_criteria: "Does this feel like Kent on his best day? (Mirror Test)"
```

When validated, prompts for human input.

### Measurement Collection

Two modes:
1. **Automatic**: Experiment runners collect measurements
2. **Manual**: User provides measurements dict

The engine doesn't care—it just validates measurements against thresholds.

---

## Implementation Reference

See: `impl/claude/services/validation/` (pending)

---

*"The proof IS the decision. The validation IS the witness."*
