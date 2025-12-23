# Validation Framework Implementation Plan

**Spec:** `spec/validation/schema.md`
**Status:** ✅ Complete (Sessions 1+2 Fused)
**Tests:** 92 passing

---

## Overview

Generalize `plans/categorical-validation-framework.md` into a project-wide validation system with Witness integration.

---

## Session 1: Core Engine (~3 hours)

### Files to Create

```
impl/claude/services/validation/
├── __init__.py
├── schema.py           # Proposition, Gate, Initiative, Phase dataclasses
├── engine.py           # ValidationEngine core logic
├── runner.py           # ValidationRunner (threshold checking)
├── store.py            # Persistence for validation runs
└── _tests/
    ├── __init__.py
    ├── test_schema.py
    ├── test_engine.py
    └── test_runner.py
```

### Implementation Order

1. **schema.py** — Type definitions (frozen dataclasses)
   - `MetricType`, `Direction` enums
   - `Proposition`, `Gate`, `Phase`, `Initiative`
   - `PropositionResult`, `GateResult`, `ValidationRun`

2. **runner.py** — Threshold validation logic
   - `check_proposition(prop, value) -> PropositionResult`
   - `check_gate(gate, results) -> GateResult`
   - No side effects, pure functions

3. **store.py** — Validation run persistence
   - `ValidationStore` using `StorageProvider`
   - `save_run()`, `get_latest()`, `get_history()`

4. **engine.py** — Orchestration
   - `ValidationEngine.register_initiative()`
   - `ValidationEngine.validate()`
   - `ValidationEngine.get_status()`
   - `ValidationEngine.get_blockers()`

### Session 1 Exit Criteria

- [x] `pytest services/validation/` passes (92 tests)
- [x] Basic validation works (measurements → results)
- [x] Persistence works (runs survive restart)

---

## Session 2: Witness Integration (FUSED INTO SESSION 1)

> **Bold Decision**: Session 2 was fused into Session 1 because "validation IS witnessed measurement."
> Witnessing is intrinsic to `ValidationEngine.validate()`, not a separate layer.

### What Was Done

1. **`ValidationEngine` now has intrinsic witness integration**:
   - `_mark_store` field for injected MarkStore
   - `emit_marks: bool = True` to enable/disable
   - `_emit_proposition_mark()` helper for measurements
   - `_emit_gate_decision_mark()` helper with `Proof.empirical()`
   - `_validate_propositions_witnessed()` for witnessed validation

2. **No `integration.py` needed** — witnessing is built into the engine

3. **Mark tags** follow spec:
   - `("validation", initiative_id, proposition_id)` for measurements
   - `("validation", "gate", initiative_id, gate_id)` for decisions

### Session 2 Exit Criteria

- [x] Every validation run produces Marks (7 new tests verify this)
- [x] Gate decisions include `Proof.empirical()` with Toulmin structure
- [x] `PropositionResult.mark_id` and `GateResult.decision_id` populated
- [x] `emit_marks=False` disables witnessing (for pure validation)
- [x] 92 tests passing, mypy clean

---

## Session 3: CLI & AGENTESE (~2 hours)

### CLI Extension

Add to existing `kg` CLI (or create new commands):

```python
# impl/claude/cli/commands/validate.py

@click.group()
def validate():
    """Validation commands."""
    pass

@validate.command()
@click.argument('initiative')
@click.argument('phase', required=False)
def run(initiative: str, phase: str | None):
    """Run validation for an initiative."""
    ...

@validate.command()
def status():
    """Show status of all initiatives."""
    ...

@validate.command()
def blockers():
    """Show what's blocking progress."""
    ...

@validate.command()
@click.argument('initiative')
def history(initiative: str):
    """Show validation history."""
    ...
```

### AGENTESE Nodes

```python
# impl/claude/protocols/agentese/contexts/validation.py

@node("concept.validation.status")
class ValidationStatusNode:
    ...

@node("concept.validation.run")
class ValidationRunNode:
    ...

@node("concept.validation.blockers")
class ValidationBlockersNode:
    ...
```

### Session 3 Exit Criteria

- [ ] `kg validate status` works
- [ ] `kg validate brain` validates Brain initiative
- [ ] AGENTESE paths respond correctly

---

## Initiative Configs

Create YAML configs for built-in initiatives:

```
impl/claude/services/validation/initiatives/
├── crown_jewels/
│   ├── brain.yaml
│   ├── witness.yaml
│   ├── atelier.yaml
│   └── liminal.yaml
├── infrastructure/
│   ├── agentese.yaml
│   ├── storage.yaml
│   └── web_ui.yaml
└── research/
    └── categorical_reasoning.yaml
```

### Brain Initiative (example)

```yaml
# brain.yaml
id: brain
name: Brain Crown Jewel
description: Spatial cathedral of memory with TeachingCrystal crystallization

propositions:
  - id: tests_pass
    description: All Brain tests pass
    metric: binary
    threshold: 1
    direction: "="
    required: true

  - id: test_count
    description: At least 200 tests
    metric: count
    threshold: 200
    direction: ">="
    required: true

  - id: spatial_navigable
    description: Spatial cathedral is navigable
    metric: binary
    threshold: 1
    direction: "="
    required: true

  - id: teaching_crystal
    description: TeachingCrystal crystallizes correctly
    metric: binary
    threshold: 1
    direction: "="
    required: true

gate:
  id: brain_complete
  name: Brain Complete
  condition: all_required

witness_tags:
  - validation
  - crown_jewel
  - brain
```

### Categorical Reasoning Initiative (migrated)

```yaml
# categorical_reasoning.yaml
id: categorical_reasoning
name: Categorical Machine Reasoning
description: Validate LLM categorical reasoning capabilities

phases:
  - id: foundations
    name: "Phase 1: Foundations"
    gate:
      id: foundations_gate
      condition: all_required
    propositions:
      - id: monad_identity_correlation
        metric: pearson_r
        threshold: 0.3
        direction: ">"
        required: true
      - id: sheaf_coherence_correlation
        metric: pearson_r
        threshold: 0.4
        direction: ">"
        required: true
      - id: combined_prediction_auc
        metric: auc
        threshold: 0.7
        direction: ">"
        required: true

  - id: integration
    name: "Phase 2: Integration"
    depends_on: [foundations]
    # ... additional propositions

  - id: architecture
    name: "Phase 3: Architecture"
    depends_on: [integration]
    # ...

  - id: synthesis
    name: "Phase 4: Synthesis"
    depends_on: [architecture]
    # ...
```

---

## Migration Path

The existing `plans/categorical-validation-framework.md` contains:
1. ✅ Validation schema → migrates to `spec/validation/schema.md`
2. ✅ Runner logic → migrates to `services/validation/runner.py`
3. 📋 Experiment runners (phase1.py, phase2.py) → stay in place, called by engine
4. 📋 Thresholds YAML → migrates to `initiatives/research/categorical_reasoning.yaml`

After migration:
- Archive `plans/categorical-validation-framework.md` to `plans/_archive/`
- Or keep as reference doc with "Migrated" status

---

## Success Criteria

From `prompts/generalize-validation-framework.md`:

1. ✅ Categorical validation framework migrates cleanly
2. ⏳ At least 3 other initiatives have validation defined
   - Brain, Witness, AGENTESE (infrastructure)
3. ⏳ `kg validate status` shows useful overview
4. ⏳ Documentation enables new contributors

---

## Non-Goals (Preserved from Prompt)

- Don't build full CI/CD system
- Don't automate all measurements (some are manual)
- Don't over-engineer schema (start simple)

---

## Dependencies

- `services/witness/` — For Marks and decisions
- `protocols/agentese/` — For AGENTESE nodes
- `cli/` — For kg commands

No new external dependencies required.

---

*"Plans have teeth when they have validation."*
