# Skill: Analysis Operad

> *"Analysis is not one thing but four: verification of laws, grounding of claims, resolution of tensions, and regeneration from axioms."*

## Overview

The Analysis Operad provides four composable modes for rigorous inquiry into specifications. Use this skill when you need to validate specs, diagnose issues, or ensure a spec passes the Generative Test.

**Key Insight**: Each mode illuminates what others cannot see. Full analysis requires all four.

**Related**: `spec/theory/analysis-operad.md`, `docs/skills/spec-hygiene.md`, `docs/skills/spec-template.md`

---

## The Four Modes

| Mode | Lens | Core Question | When to Use |
|------|------|---------------|-------------|
| **Categorical** | Laws | Does X satisfy its own composition laws? | After adding operads, laws, or composition |
| **Epistemic** | Grounding | What layer IS X? How is it justified? | After adding new specs, checking derivation |
| **Dialectical** | Contradictions | What tensions exist? How are they resolved? | When spec has trade-offs or conflicts |
| **Generative** | Regeneration | Can X be regenerated from its axioms? | Before finalizing a spec, checking quality |

---

## Quick Reference

### CLI Commands

```bash
# Full analysis (all four modes)
kg analyze spec/protocols/zero-seed.md

# Single mode
kg analyze <path> --mode categorical
kg analyze <path> --mode cat  # Shorthand

# Multiple modes
kg analyze <path> --mode cat,epi,dia

# Self-analysis (meta-applicability test)
kg analyze --self

# JSON output for pipelines
kg analyze <path> --json

# Structural analysis (no LLM, fast)
kg analyze <path> --structural
```

### AGENTESE Paths

```
concept.analysis.categorical.{target}    # Categorical analysis
concept.analysis.epistemic.{target}      # Epistemic analysis
concept.analysis.dialectical.{target}    # Dialectical analysis
concept.analysis.generative.{target}     # Generative analysis
concept.analysis.full.{target}           # Full four-mode
concept.analysis.meta.self               # Self-analysis
```

---

## Mode Details

### 1. Categorical Analysis (Laws)

**Question**: Does the spec satisfy its own composition laws?

**What it checks**:
- Explicit law declarations in operads
- Implicit category laws (identity, associativity)
- Fixed-point analysis for self-referential specs

**Output**:
```python
CategoricalReport:
    laws_extracted: tuple[LawExtraction, ...]
    law_verifications: tuple[LawVerification, ...]
    fixed_point: FixedPointAnalysis | None

# Law statuses:
PASSED      # Verified with concrete evidence
STRUCTURAL  # Verified by construction/type
FAILED      # Violation detected
UNDECIDABLE # Cannot be verified (Gödel limit)
```

**When laws fail**:
```bash
# Check which law failed
kg analyze <path> --mode cat --json | jq '.law_verifications'

# Common fixes:
# - Identity: Ensure Id >> f = f = f >> Id
# - Associativity: Check nested compositions
# - Fixed-point: Make self-reference explicit
```

---

### 2. Epistemic Analysis (Grounding)

**Question**: What layer IS this spec? How is it justified?

**What it checks**:
- Layer classification (L1-L7 in Zero Seed taxonomy)
- Toulmin argument structure (data, warrant, claim, backing, qualifier, rebuttals)
- Grounding chain (does it terminate at axioms?)
- Bootstrap validity (for self-referential specs)

**Output**:
```python
EpistemicReport:
    layer: int                     # 1-7
    toulmin: ToulminStructure      # Defeasible reasoning
    grounding: GroundingChain      # Derivation path
    bootstrap: BootstrapAnalysis | None

# Evidence tiers:
SOMATIC     # Felt truth (axioms)
AESTHETIC   # Beauty/taste judgment
EMPIRICAL   # Observed evidence
CATEGORICAL # Formal proof
DERIVED     # From other tiers
```

**Layer Reference**:
| Layer | Domain | AGENTESE Context |
|-------|--------|------------------|
| L1 | Assumptions (axioms) | `void.*` |
| L2 | Values (principles) | `void.*` |
| L3 | Goals (dreams, plans) | `concept.*` |
| L4 | Specifications | `concept.*` |
| L5 | Execution | `world.*` |
| L6 | Reflection | `self.*` |
| L7 | Representation | `time.*` |

---

### 3. Dialectical Analysis (Contradictions)

**Question**: What internal tensions exist? How are they resolved?

**What it checks**:
- Thesis/antithesis pairs (implicit and explicit)
- Classification of each tension
- Synthesis attempts and their success
- Paraconsistent tolerance (is contradiction deliberate?)

**Output**:
```python
DialecticalReport:
    tensions: tuple[Tension, ...]

# Tension types:
APPARENT       # Seems contradictory, different scopes
PRODUCTIVE     # Real tension driving design decisions
PROBLEMATIC    # Unresolved, needs fixing
PARACONSISTENT # Deliberately tolerated
```

**Healthy tension counts**:
- `PROBLEMATIC = 0` (required for valid spec)
- `PRODUCTIVE > 0` (good specs have design tensions)
- `PARACONSISTENT >= 0` (acceptable if justified)

---

### 4. Generative Analysis (Regeneration)

**Question**: Can the spec be regenerated from its axioms?

**What it checks**:
- Grammar extraction (primitives, operations, laws)
- Compression ratio (spec_size / impl_size)
- Regeneration test (can you rebuild from axioms?)
- Minimal kernel (smallest sufficient axiom set)

**Output**:
```python
GenerativeReport:
    grammar: OperadGrammar
    compression_ratio: float       # < 1.0 is good
    regeneration: RegenerationTest
    minimal_kernel: tuple[str, ...]
```

**Quality thresholds**:
| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Compression ratio | < 0.3 | < 0.7 | > 1.0 |
| Regeneration | PASSED | N/A | FAILED |
| Minimal kernel | 3-5 axioms | 6-10 | > 10 |

---

## Composition Laws

The Analysis Operad satisfies these laws:

| Law | Equation | Meaning |
|-----|----------|---------|
| **Completeness** | `full = (cat ∥ epi) >> (dia ∥ gen)` | Full analysis covers all modes |
| **Idempotence** | `mode(mode(X)) ≡ mode(X)` | Repeated analysis is stable |
| **Commutativity** | `mode_a ∥ mode_b = mode_b ∥ mode_a` | Parallel order doesn't matter |
| **Meta-Applicability** | `full(ANALYSIS_OPERAD) = valid` | Can analyze itself |

---

## Usage Patterns

### Pattern 1: Pre-Commit Spec Validation

```bash
# Before committing a new or modified spec
kg analyze spec/protocols/my-new-spec.md --mode gen
# Check: compression_ratio < 0.7, regeneration: PASSED
```

### Pattern 2: Debugging Spec Issues

```bash
# Spec seems inconsistent
kg analyze <path> --mode dia
# Look for: PROBLEMATIC tensions

# Spec seems ungrounded
kg analyze <path> --mode epi
# Look for: terminates_at_axiom: false
```

### Pattern 3: Full Quality Gate

```bash
# Before merging major spec changes
kg analyze <path> --json > analysis.json

# Check all pass criteria:
cat analysis.json | jq '
  .categorical.has_violations == false and
  .epistemic.is_grounded == true and
  .dialectical.problematic_count == 0 and
  .generative.is_regenerable == true
'
```

### Pattern 4: Agent Integration

```python
from services.analysis import AnalysisService
from agents.k.soul import create_llm_client

# Create service
llm = create_llm_client()
service = AnalysisService(llm)

# Full analysis
report = await service.analyze_full("spec/protocols/witness.md")
print(f"Valid: {report.is_valid}")
print(f"Synthesis: {report.synthesis}")

# Individual modes
cat = await service.analyze_categorical("spec/agents/operad.md")
print(f"Laws: {cat.laws_passed}/{cat.laws_total}")
```

---

## Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| **Skipping modes** | Only running categorical | Run full analysis for important specs |
| **Ignoring tensions** | 0 tensions found | Real specs have trade-offs; look harder |
| **Floating specs** | Not grounded at axioms | Trace derivation to L1-L2 |
| **Over-compression** | Ratio < 0.1 | May be too abstract; ensure regenerable |
| **Law washing** | All laws STRUCTURAL | Add concrete test cases |

---

## Integration with Other Skills

### With spec-hygiene.md

```bash
# After distillation, verify generativity preserved
kg analyze <distilled-spec> --mode gen
```

### With spec-template.md

The template structure aligns with epistemic analysis:
- Purpose → L3 (Goals)
- Core Insight → L2 (Values)
- Laws → Categorical verification targets
- Anti-patterns → Dialectical tensions

### With witness-for-agents.md

```bash
# Analysis creates marks
km "Analyzed spec/protocols/witness.md" --json
# Tags: analysis, categorical, epistemic, dialectical, generative
```

---

## Implementation Reference

| Component | Location |
|-----------|----------|
| Operad definition | `agents/operad/domains/analysis.py` |
| Report types | `agents/operad/domains/analysis.py` |
| LLM agents | `services/analysis/llm_agents.py` |
| Orchestration | `services/analysis/service.py` |
| Prompts | `services/analysis/prompts.py` |
| Parsers | `services/analysis/parsers.py` |
| CLI handler | `protocols/cli/handlers/analyze.py` |
| Spec | `spec/theory/analysis-operad.md` |

---

## Quick Diagnosis Table

| Problem | Mode | Signal | Action |
|---------|------|--------|--------|
| Laws not verified | Categorical | `has_violations: true` | Fix composition, add tests |
| Spec seems floating | Epistemic | `terminates_at_axiom: false` | Add grounding chain |
| Conflicting claims | Dialectical | `problematic_count > 0` | Synthesize or scope |
| Can't regenerate | Generative | `regeneration.passed: false` | Extract minimal kernel |
| Spec too large | Generative | `compression_ratio > 1.0` | Apply spec-hygiene patterns |

---

*"Analysis that can analyze itself is the only analysis worth having."*
