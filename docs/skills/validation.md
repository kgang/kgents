# Skill: Validation Framework

> *"If you can't measure it, you can't claim it."*
> *"Validation IS witnessed measurement."*

**92 tests** | **Intrinsic Witness Integration**

## When to Use This Skill

- Defining success criteria for any initiative
- Running experiments that measure progress
- Making evidence-based go/no-go decisions
- Adding validation to new features

---

## The Three Primitives

### 1. Proposition — A Measurable Claim

```yaml
- id: tests_pass
  description: All tests pass
  metric: binary
  threshold: 1
  direction: "="
  required: true
```

**Key fields:**
- `metric`: How to measure (see MetricType below)
- `threshold`: The success boundary
- `direction`: How to compare (`>`, `>=`, `<`, `<=`, `=`)
- `required`: Does this block gates?

### 2. Gate — A Decision Point

```yaml
gate:
  id: my_gate
  name: Feature Complete
  condition: all_required  # or: any, quorum, custom
```

### 3. Initiative — A Body of Work

**Flat (single gate):**
```yaml
id: my_feature
name: My Feature
propositions: [...]
gate: {...}
```

**Phased (linear DAG):**
```yaml
id: my_research
name: My Research
phases:
  - id: phase1
    depends_on: []
    propositions: [...]
    gate: {...}
  - id: phase2
    depends_on: [phase1]
    propositions: [...]
    gate: {...}
```

---

## Metric Types

| Type | Range | Use Case |
|------|-------|----------|
| `binary` | 0 or 1 | Pass/fail checks |
| `count` | Integer | Test counts, item counts |
| `accuracy` | 0.0 - 1.0 | Classification accuracy |
| `recall` | 0.0 - 1.0 | Detection coverage |
| `precision` | 0.0 - 1.0 | Prediction precision |
| `f1` | 0.0 - 1.0 | Balanced metric |
| `auc` | 0.0 - 1.0 | ROC AUC |
| `pearson_r` | -1.0 - 1.0 | Correlation |
| `percent` | 0 - 100 | Percentage values |
| `duration_ms` | Milliseconds | Performance timing |
| `judgment` | Human input | Qualitative assessment |

---

## CLI Commands

```bash
# Run validation
kg validate <initiative> [phase]

# Show status of all initiatives
kg validate status

# Show what's blocking progress
kg validate blockers

# Show history for an initiative
kg validate history <initiative>
```

**Example output:**
```
$ kg validate brain

============================================================
Initiative: brain — Brain Crown Jewel
============================================================

✅ tests_pass
   1 = 1 [REQUIRED]

✅ test_count
   247 >= 200 [REQUIRED]

✅ spatial_navigable
   1 = 1 [REQUIRED]

✅ teaching_crystal_crystallizes
   1 = 1 [REQUIRED]

→ Gate PASSED: brain_complete
```

---

## AGENTESE Paths

```python
# Get status of all initiatives
await logos.invoke("concept.validation.status", umwelt)

# Run validation
await logos.invoke("concept.validation.run", umwelt,
                   initiative="brain")

# Get blockers
await logos.invoke("concept.validation.blockers", umwelt)
```

---

## Adding Validation to Your Feature

### Step 1: Create Initiative Config

```yaml
# impl/claude/services/validation/initiatives/<category>/<name>.yaml

id: my_feature
name: My Feature
description: |
  What this feature does and why validation matters.

propositions:
  - id: tests_pass
    description: All tests pass
    metric: binary
    threshold: 1
    direction: "="
    required: true

  - id: my_metric
    description: Custom metric exceeds threshold
    metric: accuracy
    threshold: 0.9
    direction: ">="
    required: true

gate:
  id: my_feature_complete
  name: My Feature Complete
  condition: all_required

witness_tags:
  - validation
  - my_feature
```

### Step 2: Run Validation

```bash
# Automatic measurement (if runners exist)
kg validate my_feature

# Manual measurement
kg validate my_feature --measurements '{"tests_pass": 1, "my_metric": 0.95}'
```

### Step 3: Check Results

All validation runs are witnessed:

```bash
kg witness show --tag validation --tag my_feature
```

---

## Witness Integration (Intrinsic)

**Validation IS witnessed measurement** — witnessing is not a bolt-on, it's intrinsic.

Every `engine.validate()` call automatically produces:

1. **One Mark per proposition** — Recording the measurement with `mark_id` populated
2. **One Mark with Proof.empirical() per gate** — Recording the decision with `decision_id` populated

```python
# All validation runs emit marks automatically
run = engine.validate("brain", {"tests_pass": 1, "test_count": 250})

# Results have mark IDs
for result in run.gate_result.proposition_results:
    print(result.mark_id)  # e.g., "mark-abc123..."

# Gate decision has decision ID with Toulmin proof
print(run.gate_result.decision_id)  # e.g., "mark-def456..."

# To disable marks (pure validation)
engine = ValidationEngine(emit_marks=False)
```

**Proof Structure** (Toulmin model):
- `data`: "3/4 propositions passed"
- `warrant`: "All required propositions satisfied" or "Blocked by: test_count"
- `claim`: "Gate brain_gate: PASS" or "Gate brain_gate: BLOCKED"
- `backing`: "Initiative: brain"

---

## Qualitative Propositions

For things that need human judgment:

```yaml
- id: feels_right
  description: The UI feels right
  metric: judgment
  threshold: 1
  direction: "="
  required: false
  judgment_required: true
  judgment_criteria: |
    The Mirror Test: Does this feel like Kent on his best day?
```

When validated, the system prompts for human input.

---

## Gate Conditions

| Condition | Meaning |
|-----------|---------|
| `all_required` | All required propositions must pass |
| `any` | Any proposition passing is sufficient |
| `quorum` | N of M propositions must pass (requires `quorum_n` field) |
| `custom` | Custom aggregation function (requires `custom_fn` field) |

---

## Anti-Patterns

- **Untraceable validation**: Running checks without Witness integration
- **Floating gates**: Gates with no propositions
- **Required-less initiatives**: All propositions optional
- **Magic thresholds**: Thresholds without justification
- **Circular dependencies**: Phase A depends on B depends on A

---

## Example: Crown Jewel Validation

See the built-in initiative configs:

```
impl/claude/services/validation/initiatives/
├── crown_jewels/
│   ├── brain.yaml      # Spatial cathedral validation
│   └── witness.yaml    # Mark/crystal validation
├── infrastructure/
│   └── agentese.yaml   # Protocol validation
└── research/
    └── categorical_reasoning.yaml  # Phased research validation
```

---

## Spec Reference

See: `spec/validation/schema.md`

## Implementation Reference

See: `impl/claude/services/validation/`

| File | Purpose |
|------|---------|
| `schema.py` | Type definitions (Proposition, Gate, Initiative, etc.) |
| `runner.py` | Pure validation functions (no side effects) |
| `store.py` | JSONL persistence for validation runs |
| `engine.py` | Orchestration with intrinsic witness integration |
| `initiatives/` | YAML configs for built-in initiatives |

---

*"The proof IS the decision. The validation IS the witness."*
