# Analysis Operad: Four Modes of Rigorous Inquiry

> *"Analysis is not one thing but four: verification of laws, grounding of claims, resolution of tensions, and regeneration from axioms."*

**Version**: 2.0
**Status**: Production
**Date**: 2025-12-24
**Principles**: Composable, Generative, Heterarchical, Tasteful

---

## Purpose

The kgents system contains **self-referential specifications** that must validate themselves. Traditional analysis fails for recursive structures. We need an **operad of analysis modes** that can:

1. Verify laws categorically (does it satisfy composition laws?)
2. Ground claims epistemically (what layer IS this? bootstrapping paradox?)
3. Resolve contradictions dialectically (what tensions exist?)
4. Regenerate from axioms generatively (can this be rebuilt from principles?)

**Core Tension Resolved**: Analysis that handles self-reference without paradox, by recognizing different modes compose—and composition itself can be analyzed.

---

## The Core Insight

**Analysis is a four-colored operad where each mode illuminates what others cannot see.**

| Mode | Lens | Core Question | Structure |
|------|------|---------------|-----------|
| **Categorical** | Laws | Does X satisfy composition laws? | Lawvere fixed-point |
| **Epistemic** | Grounding | What layer IS X? How justified? | Foundational/Coherentist |
| **Dialectical** | Contradictions | What tensions? How resolved? | Paraconsistent synthesis |
| **Generative** | Regeneration | Can X regenerate from axioms? | Grammar compression |

These modes are **composable operations**, not alternatives. Complete analysis applies all four.

---

## Part I: The Four Modes

### 1.1 Categorical Analysis

**Question**: Does this spec satisfy its own composition laws?

**Grounded In**: [Categorical Proof-Theoretic Semantics](https://arxiv.org/abs/2302.09031), [Lawvere Fixed-Point](https://plato.stanford.edu/entries/self-reference/)

```python
@dataclass
class CategoricalReport:
    """Verify composition laws and fixed points."""
    target: str
    laws_extracted: tuple[LawExtraction, ...]
    law_verifications: tuple[LawVerification, ...]
    fixed_point: FixedPointAnalysis | None
    summary: str
```

**Operations**:
- `extract_laws()` - Find explicit and implicit laws
- `verify_laws()` - Verify each law (PASSED/STRUCTURAL/FAILED/UNDECIDABLE)
- `fixed_point_analysis()` - Apply Lawvere's theorem

---

### 1.2 Epistemic Analysis

**Question**: What layer IS this? How is it justified?

**Grounded In**: [Foundationalism](https://plato.stanford.edu/entries/justep-foundational/), [Coherentism](https://plato.stanford.edu/entries/justep-coherence/), [Base-Extension Semantics](https://link.springer.com/article/10.1007/s11225-024-10163-9)

```python
@dataclass
class EpistemicReport:
    """Analyze justification structure and grounding."""
    target: str
    layer: int  # 1-7 in Zero Seed
    toulmin: ToulminStructure
    grounding: GroundingChain
    bootstrap: BootstrapAnalysis | None
    summary: str
```

**Operations**:
- `classify_layer()` - Determine Zero Seed layer (L1-L7)
- `justify()` - Build Toulmin structure (Claim/Grounds/Warrant/Backing/Qualifier/Rebuttals)
- `check_grounding()` - Verify traceable to L1-L2 axioms
- `bootstrap_analysis()` - Validate self-referential specs

---

### 1.3 Dialectical Analysis

**Question**: What tensions exist? How does paraconsistency help?

**Grounded In**: [Paraconsistent Logic](https://plato.stanford.edu/entries/logic-paraconsistent/), [Dialogical Logic](https://en.wikipedia.org/wiki/Dialogical_logic)

```python
@dataclass
class DialecticalReport:
    """Identify tensions and synthesize resolutions."""
    target: str
    tensions: tuple[Tension, ...]
    summary: str
```

**Operations**:
- `extract_tensions()` - Find thesis/antithesis pairs
- `classify_contradiction()` - APPARENT/PRODUCTIVE/PROBLEMATIC/PARACONSISTENT
- `synthesize()` - Attempt dialectical resolution
- `paraconsistent_tolerance()` - Determine if contradiction can be tolerated

---

### 1.4 Generative Analysis

**Question**: Can this spec be regenerated from its own axioms?

**Grounded In**: [Generative Grammar](https://en.wikipedia.org/wiki/Generative_grammar), [Operads as Grammars](https://math.libretexts.org/)

```python
@dataclass
class GenerativeReport:
    """Test regenerability from axioms."""
    target: str
    grammar: OperadGrammar  # Primitives/Operations/Laws
    compression_ratio: float  # spec_size / impl_size
    regeneration: RegenerationTest
    minimal_kernel: tuple[str, ...]
    summary: str
```

**Operations**:
- `extract_grammar()` - Find primitives, operations, laws
- `compute_compression()` - Measure spec_size / impl_size (good specs < 1.0)
- `test_regeneration()` - Attempt to rebuild spec from axioms
- `find_minimal_kernel()` - Smallest axiom set that generates spec

---

## Part II: The Analysis Operad

### 2.1 Formal Definition

```python
ANALYSIS_OPERAD = Operad(
    name="AnalysisOperad",
    operations={
        "categorical": Operation(
            arity=1, signature="Spec → CategoricalReport",
            compose=categorical_analysis,
        ),
        "epistemic": Operation(
            arity=1, signature="Spec → EpistemicReport",
            compose=epistemic_analysis,
        ),
        "dialectical": Operation(
            arity=1, signature="Spec → DialecticalReport",
            compose=dialectical_analysis,
        ),
        "generative": Operation(
            arity=1, signature="Spec → GenerativeReport",
            compose=generative_analysis,
        ),
        "full": Operation(
            arity=1, signature="Spec → FullAnalysisReport",
            compose=lambda spec: full_analysis(spec),
        ),
    },
    laws=[
        Law(
            name="completeness",
            equation="full(X) = seq(par(categorical, epistemic), par(dialectical, generative))(X)",
            description="Full analysis = all four modes composed",
        ),
        Law(
            name="idempotence",
            equation="mode(mode(X)) ≡ mode(X)",
            description="Repeated analysis doesn't change results",
        ),
        Law(
            name="meta_applicability",
            equation="ANALYSIS_OPERAD.full(ANALYSIS_OPERAD.spec) = valid",
            description="The Analysis Operad can analyze itself",
        ),
    ],
)
```

### 2.2 Composition Laws

| Law | Equation | Meaning |
|-----|----------|---------|
| **Completeness** | `full = (categorical ‖ epistemic) >> (dialectical ‖ generative)` | Full analysis covers all modes |
| **Idempotence** | `mode(mode(X)) ≡ mode(X)` | Analysis is stable |
| **Commutativity** | `mode_a ‖ mode_b = mode_b ‖ mode_a` | Parallel order irrelevant |
| **Meta-Applicability** | `full(ANALYSIS_OPERAD) = valid` | Can analyze itself |

### 2.3 AGENTESE Integration

```python
# Analysis paths
concept.analysis.categorical.{target}    # Categorical analysis
concept.analysis.epistemic.{target}      # Epistemic analysis
concept.analysis.dialectical.{target}    # Dialectical analysis
concept.analysis.generative.{target}     # Generative analysis
concept.analysis.full.{target}           # Full four-mode analysis
concept.analysis.meta.{analysis_id}      # Analyze a previous analysis
```

### 2.4 DP-Native Integration

Each analysis mode is a **DP problem formulation**:

```python
class AnalysisFormulation(ProblemFormulation):
    """Analysis as Dynamic Programming."""

    def reward(self, s: AnalysisState, a: AnalysisAction, s_: AnalysisState) -> float:
        ethical = s_.tensions_identified / s.potential_tensions
        generative = 1.0 - s_.compression_ratio if s_.compression_ratio < 1 else 0.0
        composable = s_.laws_verified / s_.laws_total
        return 0.4 * ethical + 0.3 * generative + 0.3 * composable
```

---

## Part III: Supporting Types

### Report Types

```python
@dataclass(frozen=True)
class LawExtraction:
    name: str
    equation: str
    source: str
    tier: EvidenceTier = EvidenceTier.CATEGORICAL

@dataclass(frozen=True)
class FixedPointAnalysis:
    is_self_referential: bool
    fixed_point_description: str
    is_valid: bool
    implications: tuple[str, ...]

@dataclass(frozen=True)
class ToulminStructure:
    claim: str
    grounds: tuple[str, ...]
    warrant: str
    backing: str
    qualifier: str
    rebuttals: tuple[str, ...]
    tier: EvidenceTier

@dataclass(frozen=True)
class GroundingChain:
    steps: tuple[tuple[int, str, str], ...]  # (layer, node, edge_type)
    terminates_at_axiom: bool

@dataclass(frozen=True)
class BootstrapAnalysis:
    is_self_describing: bool
    layer_described: int
    layer_occupied: int
    is_valid: bool
    explanation: str

@dataclass(frozen=True)
class Tension:
    thesis: str
    antithesis: str
    classification: ContradictionType
    synthesis: str | None
    is_resolved: bool

@dataclass(frozen=True)
class OperadGrammar:
    primitives: FrozenSet[str]
    operations: FrozenSet[str]
    laws: FrozenSet[str]

@dataclass(frozen=True)
class RegenerationTest:
    axioms_used: tuple[str, ...]
    structures_regenerated: tuple[str, ...]
    missing_elements: tuple[str, ...]
    passed: bool

@dataclass(frozen=True)
class FullAnalysisReport:
    target: str
    categorical: CategoricalReport
    epistemic: EpistemicReport
    dialectical: DialecticalReport
    generative: GenerativeReport
    synthesis: str

    @property
    def is_valid(self) -> bool:
        return (
            not self.categorical.has_violations
            and self.epistemic.is_grounded
            and self.dialectical.problematic_count == 0
            and self.generative.is_regenerable
        )
```

### Enums

```python
class ContradictionType(Enum):
    APPARENT = auto()       # Different scopes
    PRODUCTIVE = auto()     # Drives design
    PROBLEMATIC = auto()    # Needs resolution
    PARACONSISTENT = auto() # Tolerated deliberately

class EvidenceTier(Enum):
    SOMATIC = auto()        # Felt truth (axioms)
    AESTHETIC = auto()      # Beauty/taste
    EMPIRICAL = auto()      # Observations
    CATEGORICAL = auto()    # Formal proof
    DERIVED = auto()        # From other tiers
```

---

## Part IV: Self-Analysis

The Analysis Operad **analyzes itself** via the `meta_applicability` law. This is a valid Lawvere fixed-point, not a paradox.

**Meta-Application Test**:
```bash
kg analyze spec/theory/analysis-operad.md --full
```

Expected outcome:
- **Categorical**: All composition laws verified (completeness, idempotence, meta-applicability)
- **Epistemic**: L4 (Specification), grounded in L1-L2 axioms ("Rigor", "Composable modes")
- **Dialectical**: Productive tensions resolved (Completeness vs Minimality, Rigor vs Usability)
- **Generative**: Compression < 1.0, regenerable from minimal kernel

See `docs/examples/analysis-operad-self-analysis.md` for detailed walkthrough.

---

## Part V: Implementation

### Directory Structure

```
impl/claude/agents/operad/domains/analysis.py    # Analysis Operad
impl/claude/services/analysis/                    # Analysis service (LLM-backed)
  ├── categorical.py
  ├── epistemic.py
  ├── dialectical.py
  ├── generative.py
  └── reports.py
```

### CLI Integration

```bash
kg analyze <path> --full                     # Full four-mode analysis
kg analyze <path> --mode categorical         # Specific mode
kg analyze <path> --llm                      # Use LLM-backed analysis
kg analyze --self                            # Analyze Analysis Operad itself
kg analyze <path> --json                     # JSON output for pipelines
```

### AGENTESE Nodes

```python
@node("concept.analysis.categorical", description="Categorical spec analysis")
class CategoricalAnalysisNode(BaseLogosNode):
    async def invoke(self, observer: Observer, target: str) -> CategoricalReport:
        return await categorical_analysis(target)
```

### Anti-Patterns

| Anti-Pattern | Detection |
|--------------|-----------|
| **Law Inflation** | Categorical: many SKIPPED |
| **Groundless Specs** | Epistemic: empty grounding chain |
| **Hidden Contradictions** | Dialectical: 0 tensions (suspicious) |
| **Documentation Masquerading** | Generative: compression > 1.0 |
| **Regressive Bootstrap** | Epistemic: infinite regress detected |

---

*"Analysis that can analyze itself is the only analysis worth having."*

---

**Related Specs**:
- `spec/theory/dp-native-kgents.md` — DP foundation
- `spec/protocols/zero-seed.md` — Seven-layer holarchy
- `spec/principles/CONSTITUTION.md` — 7+7 principles
- `spec/agents/operad.md` — Operad foundation
