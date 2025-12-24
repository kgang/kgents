# Analysis Service: LLM-Backed Four-Mode Spec Analysis

> *"Analysis that can analyze itself is the only analysis worth having."*

The Analysis Service provides production-ready, LLM-backed implementations of the four analysis modes from the Analysis Operad.

## Overview

### Four Analysis Modes

1. **Categorical**: Extract laws, verify composition, find fixed points
2. **Epistemic**: Determine layer, build Toulmin structure, trace grounding
3. **Dialectical**: Find tensions, classify contradictions, synthesize
4. **Generative**: Extract grammar, measure compression, test regeneration

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    AnalysisService                           │
│  Orchestrates four-mode analysis with optimal composition   │
└──────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │               │
           ▼               ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Cat      │    │ Epi      │    │ Dia      │    │ Gen      │
    │ Analyzer │    │ Analyzer │    │ Analyzer │    │ Analyzer │
    └──────────┘    └──────────┘    └──────────┘    └──────────┘
           │               │               │               │
           └───────────────┴───────────────┴───────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │   LLMClient      │
                  │  (Claude Opus)   │
                  └──────────────────┘
```

### Key Features

- **Production-Ready**: Full async/await, error handling, structured reports
- **Compositional**: Follows Analysis Operad completeness law
- **Typed**: Returns strongly-typed dataclasses, not dicts
- **Graceful Degradation**: Parse errors return error reports, don't crash
- **Self-Analyzing**: Can analyze the Analysis Operad itself

## Installation

No additional dependencies beyond kgents core:

```bash
cd impl/claude
uv sync
```

## Quick Start

### Basic Usage

```python
from agents.k.soul import create_llm_client
from services.analysis import AnalysisService

# Initialize
llm = create_llm_client()
service = AnalysisService(llm)

# Full four-mode analysis
report = await service.analyze_full("spec/theory/zero-seed.md")

# Check validity
if report.is_valid:
    print("✅ Spec is valid!")
else:
    print("⚠️ Issues found:")
    print(report.synthesis)
```

### Single Mode Analysis

```python
# Just categorical
cat_report = await service.analyze_categorical("spec/protocols/witness.md")
print(f"Laws: {cat_report.laws_passed}/{cat_report.laws_total}")

# Just epistemic
epi_report = await service.analyze_epistemic("spec/agents/operad.md")
print(f"Layer: L{epi_report.layer}, Grounded: {epi_report.is_grounded}")

# Just dialectical
dia_report = await service.analyze_dialectical("spec/principles/CONSTITUTION.md")
print(f"Tensions: {len(dia_report.tensions)}, Problematic: {dia_report.problematic_count}")

# Just generative
gen_report = await service.analyze_generative("spec/theory/dp-native-kgents.md")
print(f"Compression: {gen_report.compression_ratio:.2f}, Regenerable: {gen_report.is_regenerable}")
```

### Demo Script

```bash
cd impl/claude
uv run python scripts/demo_analysis_service.py
```

This performs self-analysis: the Analysis Operad analyzes its own specification.

## Module Structure

```
services/analysis/
├── __init__.py         # Public exports
├── service.py          # Main AnalysisService orchestrator
├── llm_agents.py       # LLM agent wrappers per mode
├── prompts.py          # LLM prompt templates
├── parsers.py          # JSON response → typed reports
├── README.md           # This file
└── _tests/
    ├── __init__.py
    └── test_parsers.py # Parser tests
```

## API Reference

### AnalysisService

Main service class that orchestrates four-mode analysis.

#### Methods

**`async analyze_categorical(spec_path: str) -> CategoricalReport`**

Perform categorical analysis (laws and fixed points).

```python
report = await service.analyze_categorical("spec/theory/analysis-operad.md")
print(f"Fixed point: {report.fixed_point.description}")
```

**`async analyze_epistemic(spec_path: str) -> EpistemicReport`**

Perform epistemic analysis (grounding and justification).

```python
report = await service.analyze_epistemic("spec/protocols/zero-seed.md")
print(f"Layer: L{report.layer}")
print(f"Claim: {report.toulmin.claim}")
```

**`async analyze_dialectical(spec_path: str, categorical: CategoricalReport | None = None) -> DialecticalReport`**

Perform dialectical analysis (tensions and contradictions).

```python
report = await service.analyze_dialectical("spec/agents/operad.md")
for tension in report.tensions:
    print(f"{tension.thesis} ↔ {tension.antithesis}")
    if tension.synthesis:
        print(f"  → {tension.synthesis}")
```

**`async analyze_generative(spec_path: str) -> GenerativeReport`**

Perform generative analysis (compression and regeneration).

```python
report = await service.analyze_generative("spec/theory/dp-native-kgents.md")
print(f"Primitives: {report.grammar.primitives}")
print(f"Compression: {report.compression_ratio:.2f}")
```

**`async analyze_full(spec_path: str) -> FullAnalysisReport`**

Perform complete four-mode analysis.

Implements the completeness law:
```
full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)
```

Phase 1: Categorical + Epistemic in parallel
Phase 2: Dialectical + Generative in parallel (informed by phase 1)
Phase 3: Synthesize all results

```python
report = await service.analyze_full("spec/theory/analysis-operad.md")

# Access individual mode results
print(report.categorical.summary)
print(report.epistemic.summary)
print(report.dialectical.summary)
print(report.generative.summary)

# Overall synthesis
print(report.synthesis)

# Validity check
if report.is_valid:
    print("✅ All modes passed")
```

## Report Types

All reports are immutable dataclasses from `agents.operad.domains.analysis`.

### CategoricalReport

```python
@dataclass(frozen=True)
class CategoricalReport:
    target: str                              # Spec path
    laws_extracted: tuple[LawExtraction, ...] # Extracted laws
    law_verifications: tuple[LawVerification, ...] # Verification results
    fixed_point: FixedPointAnalysis | None   # Fixed point analysis
    summary: str                             # Summary text

    @property
    def laws_passed(self) -> int:           # Number of laws verified

    @property
    def laws_total(self) -> int:            # Total laws checked

    @property
    def has_violations(self) -> bool:       # Any FAILED laws?
```

### EpistemicReport

```python
@dataclass(frozen=True)
class EpistemicReport:
    target: str                              # Spec path
    layer: int                               # Zero Seed layer (1-7)
    toulmin: ToulminStructure                # Toulmin argument
    grounding: GroundingChain                # Grounding chain
    bootstrap: BootstrapAnalysis | None      # Bootstrap analysis
    summary: str                             # Summary text

    @property
    def is_grounded(self) -> bool:           # Terminates at axiom?

    @property
    def has_valid_bootstrap(self) -> bool:   # Valid bootstrap?
```

### DialecticalReport

```python
@dataclass(frozen=True)
class DialecticalReport:
    target: str                              # Spec path
    tensions: tuple[Tension, ...]            # Identified tensions
    summary: str                             # Summary text

    @property
    def resolved_count(self) -> int:         # Resolved tensions

    @property
    def problematic_count(self) -> int:      # Problematic tensions

    @property
    def paraconsistent_count(self) -> int:   # Tolerated contradictions
```

### GenerativeReport

```python
@dataclass(frozen=True)
class GenerativeReport:
    target: str                              # Spec path
    grammar: OperadGrammar                   # Extracted grammar
    compression_ratio: float                 # Spec size / impl size
    regeneration: RegenerationTest           # Regeneration test
    minimal_kernel: tuple[str, ...]          # Minimal axioms
    summary: str                             # Summary text

    @property
    def is_compressed(self) -> bool:         # Ratio < 1.0?

    @property
    def is_regenerable(self) -> bool:        # Passed regeneration?
```

### FullAnalysisReport

```python
@dataclass(frozen=True)
class FullAnalysisReport:
    target: str                              # Spec path
    categorical: CategoricalReport           # Categorical results
    epistemic: EpistemicReport               # Epistemic results
    dialectical: DialecticalReport           # Dialectical results
    generative: GenerativeReport             # Generative results
    synthesis: str                           # Overall synthesis

    @property
    def is_valid(self) -> bool:              # All modes pass?
```

## Implementation Details

### Prompt Engineering

Each mode has a specialized prompt in `prompts.py`:

- **CATEGORICAL_PROMPT**: Category theory framing, law extraction
- **EPISTEMIC_PROMPT**: Zero Seed layers, Toulmin structure
- **DIALECTICAL_PROMPT**: Hegelian dialectic, paraconsistent logic
- **GENERATIVE_PROMPT**: Grammar extraction, compression analysis

Prompts request JSON output for reliable parsing.

### Parsing Strategy

LLMs often wrap JSON in markdown:

```
```json
{"key": "value"}
```
```

The `extract_json_from_response()` function handles this automatically.

### Error Handling

The service never raises on analysis errors. Instead, it returns error reports:

```python
# File not found
report = await service.analyze_categorical("missing.md")
assert "Error" in report.summary  # Error reported in summary

# LLM timeout
report = await service.analyze_epistemic("huge-spec.md")
assert report.layer == 4  # Defaults to L4, summary has error
```

### Completeness Law

Full analysis follows the operad completeness law:

```
full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)
```

This means:

1. Phase 1: Run `categorical` and `epistemic` **in parallel**
2. Phase 2: Run `dialectical` and `generative` **in parallel**, informed by phase 1
3. Phase 3: Synthesize all four results

**NOT** simple parallel execution of all four!

## Testing

Run parser tests:

```bash
cd impl/claude
uv run pytest services/analysis/_tests/test_parsers.py -v
```

Run with coverage:

```bash
uv run pytest services/analysis/_tests/ --cov=services.analysis --cov-report=term-missing
```

## Integration Points

### With ASHC (Future)

```python
# TODO: ASHC bridge for confidence tracking
from services.analysis.ashc_bridge import analyze_with_evidence

result = await analyze_with_evidence(
    target="spec/theory/zero-seed.md",
    mode="categorical",
    confidence=0.8,
    stake=Decimal("0.05"),
)

print(f"Confidence: {result.confidence}")
print(f"Mark ID: {result.mark_id}")
```

### With Witness (Future)

```python
# TODO: Emit witness marks on analysis
from services.witness import get_mark_store

service = AnalysisService(llm, witness=get_mark_store())
report = await service.analyze_full("spec.md")

# Analysis emits mark
mark = await get_mark_store().get_mark(report.mark_id)
print(f"Witnessed: {mark.action}")
```

### With CLI (Future)

```bash
# TODO: CLI integration
kg analyze spec/theory/zero-seed.md --full
kg analyze spec/protocols/witness.md --mode categorical
kg analyze spec/agents/operad.md --json
```

## Performance

Approximate timings (Claude Opus 4.5):

| Mode | Tokens | Time |
|------|--------|------|
| Categorical | ~3000 | 8-12s |
| Epistemic | ~3000 | 8-12s |
| Dialectical | ~3000 | 8-12s |
| Generative | ~3000 | 8-12s |
| **Full (all 4)** | ~12000 | **30-45s** |

Full analysis runs cat+epi in parallel (15s), then dia+gen in parallel (15s), then synthesizes.

## Philosophical Notes

### Meta-Applicability

The Analysis Operad **can analyze itself**:

```python
report = await service.analyze_full("spec/theory/analysis-operad.md")
```

This is a valid Lawvere fixed point, not a paradox. The spec:

1. Describes L4 specifications
2. **Is** an L4 specification
3. Grounds at L1-L2 axioms (no infinite regress)

### Self-Analysis Results

When the Analysis Operad analyzes itself, expected results:

- **Categorical**: 3 laws (completeness, idempotence, meta-applicability) verified
- **Epistemic**: L4 specification, grounded at L1 ("rigor" axiom)
- **Dialectical**: 2 productive tensions (rigor vs usability, completeness vs minimality)
- **Generative**: Compression ~0.25, regenerable from 3 axioms

## Contributing

When adding features:

1. Keep agents thin (prompt + invoke + parse)
2. Keep parsers pure (JSON → dataclass)
3. Keep service orchestration-focused
4. Return error reports, don't raise on LLM errors
5. Add tests to `_tests/`
6. Update this README

## See Also

- **Spec**: `spec/theory/analysis-operad.md` (conceptual foundation)
- **Structural Impl**: `agents/operad/domains/analysis.py` (report types)
- **Demo**: `scripts/demo_analysis_service.py` (self-analysis)
- **Tests**: `services/analysis/_tests/` (parser tests)

---

*"The proof IS the decision. The mark IS the witness."*
