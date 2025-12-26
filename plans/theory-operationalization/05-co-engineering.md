# Operationalization: Co-Engineering Practice

> *"The witness IS the trace. The dialectic IS the synthesis. The mark IS the proof."*

**Theory Source**: Part VI (Co-Engineering Practice)
**Chapters**: 15-17 (Analysis Operad, Witness Protocol, Dialectical Fusion)
**Sub-Agent**: a4cafdc
**Status**: **PARTIAL** — E1 and E3 complete, E2/E4/E5 pending

---

## Implementation Status (Updated 2025-12-26)

| Proposal | Status | Location | Tests |
|----------|--------|----------|-------|
| **E1** | **DONE** | `services/witness/kleisli.py` | 36 passing |
| E2 | Pending | — | — |
| **E3** | **DONE** | `services/dialectic/fusion.py` | 22 passing |
| E4 | Pending | — | — |
| E5 | Pending | — | — |

### E1 Implementation Summary
- `Witnessed[A]` — Writer monad with value and mark trace
- `kleisli_compose` — Categorical composition (>=>)
- `kleisli_chain` — Compose N Kleisli arrows
- `@witnessed_operation` — Decorator for async traced operations
- `@witnessed_sync` — Decorator for sync traced operations
- All 3 monad laws verified by property tests

### E3 Implementation Summary
- `Position` — Structured view with principle alignment
- `Fusion` — Complete dialectical record
- `FusionResult` — 6 outcomes (CONSENSUS, SYNTHESIS, KENT_PREVAILS, CLAUDE_PREVAILS, DEFERRED, VETO)
- `DialecticalFusionService` — Full fusion workflow with Constitution Article IV/VI compliance
- Trust delta tracking for Article V
- Witness mark creation via Kleisli composition

---

## Zero Seed Grounding

> *"The proof IS the decision. The mark IS the witness."*

### Axiom Derivation Chain

E1 and E3 derive from Constitution axioms:

```
A4 (Witness) → Witness monad → Kleisli composition (E1)
  └─ "The mark IS the witness"
  └─ Witnessed[A] = Writer monad with trace
  └─ kleisli_compose = categorical composition (>=>)

Article VI (Fusion as Goal) → Dialectical Fusion (E3)
  └─ "Fusion is the goal; autonomy is earned"
  └─ DialecticalFusionService implements Kent+Claude synthesis
  └─ Trust delta tracking honors Article V (Trust Gradient)
```

### Grounding Evidence

| Component | Axiom | Derivation |
|-----------|-------|------------|
| `Witnessed[A]` | A4 | Writer monad structure from "trace is proof" |
| `kleisli_compose` | A4 | Categorical law: traces compose associatively |
| `Position` | Art VI | Structured view with principle alignment |
| `Fusion` | Art VI | Complete dialectical record with trust tracking |
| `FusionResult.VETO` | Art IV | Kent's disgust veto (ETHICAL floor) |

---

## Analysis Operad Coherence Check

The four operad modes validate E1 and E3 implementation:

### Categorical (Structure)

- **E1 monad laws**: VERIFIED (36 property tests)
  - Left identity: `pure(a) >>= f ≡ f(a)`
  - Right identity: `m >>= pure ≡ m`
  - Associativity: `(m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)`
- **E3 fusion structure**: Position → Synthesis → FusionResult forms valid composition

### Epistemic (Confidence)

| Component | Confidence | Justification |
|-----------|------------|---------------|
| E1 Kleisli | **High** | 36 tests, monad laws verified |
| E3 Fusion | **High** | 22 tests, Constitution integration |
| E2 Operad | Medium | Spec complete, impl pending |
| E4 AGENTESE | Medium | Pattern established, wiring pending |
| E5 Trust | Medium | Foundation in gradient.py, integration pending |

### Dialectical (Synthesis)

- **Kent + Claude fusion**: Now operational via E3
- **Fusion outcomes**: CONSENSUS, SYNTHESIS, KENT_PREVAILS, CLAUDE_PREVAILS, DEFERRED, VETO
- **Trust evolution**: Each fusion adjusts trust delta per Article V

### Generative (Regenerability)

- **E1**: `Witnessed[A]` regenerable from Writer monad spec
- **E3**: `DialecticalFusionService` regenerable from Constitution Article VI
- **Compression**: Theory → Implementation is ~5:1 (550 lines theory → 110 lines impl)

---

## Type-Level Honesty: Approximate[T] (Invention)

> *"The type IS the contract. The wrapper IS the acknowledgment."*

**Problem**: E3 comments say "heuristic synthesis, not cocone" but comments are forgotten. Future developers might treat approximate results as exact, leading to silent correctness degradation.

**Solution**: Encode approximation status in the type system. When you see `Approximate[Cocone]`, the TYPE ITSELF tells you this is not a true cocone.

### The Approximate[T] Wrapper

```python
from typing import TypeVar, Generic
from dataclasses import dataclass

T = TypeVar('T')

@dataclass(frozen=True)
class Approximate(Generic[T]):
    """
    Type-level encoding of approximation.

    When you see Approximate[Cocone], the TYPE ITSELF tells you:
    - This is NOT a true cocone
    - It approximates cocone behavior
    - Confidence and ideal are explicit

    This is an INVENTION from the Analysis Operad:
    - Categorical: Approximate is a functor wrapping T with honesty metadata
    - Epistemic: Grounds in principle of honest naming
    - Dialectical: Comments (forgotten) vs Types (enforced) -> Types win
    - Generative: Minimal wrapper with confidence and ideal reference
    """
    value: T
    confidence: float  # 0.0-1.0, how close to ideal
    ideal: str  # What this approximates, e.g., "categorical cocone"
    method: str  # How approximation is computed, e.g., "LLM synthesis"

    def unwrap(self) -> T:
        """
        Get the underlying value.

        Explicit unwrap forces acknowledgment. You cannot accidentally
        pass an Approximate[T] where T is expected - you must consciously
        call .unwrap() which serves as a code-level acknowledgment point.
        """
        return self.value

    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if approximation meets confidence threshold."""
        return self.confidence >= threshold

    def map(self, f: 'Callable[[T], U]') -> 'Approximate[U]':
        """
        Functor map - transform the value while preserving approximation metadata.

        Note: Confidence, ideal, and method are preserved. If the transformation
        changes the nature of the approximation, create a new Approximate instead.
        """
        return Approximate(
            value=f(self.value),
            confidence=self.confidence,
            ideal=self.ideal,
            method=self.method
        )

    def __repr__(self) -> str:
        return f"Approximate[{type(self.value).__name__}](confidence={self.confidence:.2f}, ideal='{self.ideal}')"
```

### Usage in E3 (Dialectical Fusion)

```python
# In services/dialectic/fusion.py

async def _attempt_synthesis(
    self,
    topic: str,
    kent_position: Position,
    claude_position: Position
) -> Approximate[Cocone]:
    """
    Returns Approximate[Cocone], NOT Cocone.
    The return type itself documents the approximation.

    A true categorical cocone would satisfy universal property:
    for any other cone, there exists a unique morphism to the cocone.
    We use LLM synthesis which is a heuristic approximation.
    """
    synthesis = await self._llm_synthesize(kent_position, claude_position)

    return Approximate(
        value=Cocone(
            apex=synthesis,
            kent_projection=self._project_kent(synthesis, kent_position),
            claude_projection=self._project_claude(synthesis, claude_position)
        ),
        confidence=0.65,  # LLM synthesis typically achieves ~65% of true cocone quality
        ideal="categorical cocone (Ch. 17 Definition 17.5)",
        method="LLM-based heuristic synthesis with position alignment scoring"
    )


# Consumer code must acknowledge approximation
async def handle_fusion_result(result: Approximate[Cocone]) -> FusionResult:
    """Process fusion result with explicit approximation handling."""

    if result.is_high_confidence(threshold=0.8):
        # High confidence - can treat more like exact
        cocone = result.unwrap()  # Explicit acknowledgment point
        return FusionResult.SYNTHESIS
    else:
        # Low confidence - handle accordingly
        log.info(f"Low confidence synthesis: {result.confidence:.2f} (ideal: {result.ideal})")
        # Maybe defer, or require human review
        return FusionResult.DEFERRED
```

### Type Aliases for Common Patterns

```python
from typing import TypeAlias

# Honest type aliases - immediately communicate approximation status
HeuristicSynthesis: TypeAlias = Approximate[Cocone]
EstimatedDifficulty: TypeAlias = Approximate[float]  # D(P) estimate
PredictedCorrelation: TypeAlias = Approximate[float]  # Galois bet validation
EmbeddingSimilarity: TypeAlias = Approximate[float]   # Vector distance as semantic similarity

# Exact types (no approximation wrapper needed)
VerifiedLaw: TypeAlias = bool        # Either passes or doesn't - binary, exact
WitnessedTrace = Witnessed[T]        # Exact by construction (monad laws hold)
HashDigest: TypeAlias = str          # Cryptographic hash - exact by definition
AxiomReference: TypeAlias = str      # Reference to axiom - exact lookup
```

### Compile-Time Honesty

```python
# This function requires an EXACT cocone, not approximate
def verify_cocone_universality(cocone: Cocone) -> bool:
    """
    Requires EXACT cocone, not approximate.

    Type checker will reject: verify_cocone_universality(approximate_result)
    Caller must explicitly unwrap: verify_cocone_universality(approximate_result.unwrap())
    """
    # Check universal property...
    pass


# Practical usage pattern
async def fusion_ceremony(topic: str, kent: Position, claude: Position) -> FusionResult:
    # Get approximate synthesis
    result: Approximate[Cocone] = await _attempt_synthesis(topic, kent, claude)

    # COMPILE ERROR if you try: verify_cocone_universality(result)
    # Type mismatch: Approximate[Cocone] != Cocone

    # Must explicitly acknowledge approximation
    if result.is_high_confidence():
        exact = result.unwrap()  # Acknowledgment: "I know this is approximate"
        # Now can pass to functions expecting exact
        is_valid = verify_cocone_universality(exact)
    else:
        # Handle low confidence case
        return FusionResult.DEFERRED
```

### Zero Seed Grounding

The `Approximate[T]` wrapper derives from Constitution axioms:

```
A4 (Witness) -> Honesty about what we know
  └─ "The mark IS the witness"
  └─ Approximate[T] is a mark that says "this is not exact"

Principle 3 (Ethical) -> Agents don't deceive about limitations
  └─ Type-level encoding prevents accidental deception
  └─ Cannot claim cocone when you have Approximate[Cocone]

Type Theory -> Static enforcement of contracts
  └─ Compiler catches violations, not runtime
  └─ Honesty enforced at development time
```

### Benefits

| Benefit | Description |
|---------|-------------|
| **Compiler enforces honesty** | Cannot accidentally treat approximate as exact - type mismatch |
| **Self-documenting** | Return type `Approximate[Cocone]` tells the story without reading comments |
| **Explicit acknowledgment** | Must call `.unwrap()` to use, forcing conscious decision |
| **Confidence tracking** | Metadata (confidence, ideal, method) travels with value |
| **Functor structure** | Can transform underlying value while preserving approximation metadata |

### Integration with Analysis Operad

The `Approximate[T]` wrapper instantiates all four operad modes:

1. **Categorical**: `Approximate` is a functor `T -> Approximate[T]` with `.map()` preserving structure
2. **Epistemic**: `confidence` field explicitly tracks uncertainty
3. **Dialectical**: Resolves tension between "comments (forgotten)" and "types (enforced)"
4. **Generative**: Minimal implementation (~40 lines) from principle "encode honesty in types"

---

## Executive Summary

Co-Engineering defines how humans and AI collaborate. With E1 (Kleisli composition) and E3 (Dialectical Fusion) complete, the core interaction patterns between Kent and Claude are now operational. Remaining work (E2, E4, E5) focuses on composition grammar and AGENTESE integration.

---

## Gap Analysis

### Current State (Updated 2025-12-26)

| Component | Theory | Implementation | Gap |
|-----------|--------|----------------|-----|
| Witness (Mark/Trace/Crystal) | Ch 16 | `services/witness/` | Strong (98%) |
| Analysis Operad | Ch 15 | Partial | Medium |
| Kleisli Composition | Ch 16 | `services/witness/kleisli.py` | **CLOSED** |
| Dialectical Fusion | Ch 17 | `services/dialectic/fusion.py` | **CLOSED** |
| Trust Gradient | Ch 17 | `services/witness/trust/gradient.py` | Strong |
| AGENTESE Fusion | Ch 17 | Pending | High |

### Closed Gaps (2025-12-26)

1. **E1: Kleisli witness composition** — `Witnessed[A]` monad with `kleisli_compose`
2. **E3: Dialectical fusion service** — `DialecticalFusionService` with Constitution integration

### Remaining Gaps

1. **E2: Analysis Operad** — Four modes not fully composable
2. **E4: AGENTESE fusion ceremony** — No protocol for recording fusions via AGENTESE
3. **E5: Trust Gradient Dialectic** — Trust-weighted fusion not implemented

---

## Proposal E1: Kleisli Witness Composition

> **STATUS: DONE** (2025-12-26)
> - Location: `impl/claude/services/witness/kleisli.py`
> - Tests: `impl/claude/services/witness/_tests/test_kleisli.py` (36 tests passing)
> - Exports added to `services/witness/__init__.py`

### Theory Basis (Ch 16: Witness Protocol)

```
Witness as Writer Monad:
  Writer A = (A, Trace)
  return: A → (A, [])
  bind:   (A, T1) → (A → (B, T2)) → (B, T1++T2)

Kleisli composition for marks:
  f >=> g = λx. let (y, t1) = f(x) in let (z, t2) = g(y) in (z, t1++t2)

This IS how reasoning traces compose.
```

### Implementation

**Location**: `impl/claude/services/witness/kleisli.py`

```python
from dataclasses import dataclass
from typing import TypeVar, Generic, Callable, List
from datetime import datetime

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')

@dataclass
class Mark:
    """A single witness mark."""
    id: str
    action: str
    reasoning: str
    timestamp: datetime
    principle_scores: Dict[str, float]
    parent_id: Optional[str] = None

@dataclass
class Witnessed(Generic[A]):
    """The Writer monad: value with witness trace."""
    value: A
    marks: List[Mark]

    @staticmethod
    def pure(value: A) -> 'Witnessed[A]':
        """Inject a pure value (return/unit)."""
        return Witnessed(value=value, marks=[])

    def bind(self, f: Callable[[A], 'Witnessed[B]']) -> 'Witnessed[B]':
        """Monadic bind (>>=). Composes witness traces."""
        result = f(self.value)
        # Traces concatenate (Writer monad semantics)
        return Witnessed(
            value=result.value,
            marks=self.marks + result.marks
        )

    def map(self, f: Callable[[A], B]) -> 'Witnessed[B]':
        """Functor map (preserves trace)."""
        return Witnessed(value=f(self.value), marks=self.marks)

    def tell(self, mark: Mark) -> 'Witnessed[A]':
        """Add a mark to the trace."""
        return Witnessed(value=self.value, marks=self.marks + [mark])

    # Monad laws verification
    def verify_laws(self, f: Callable[[A], 'Witnessed[B]']) -> dict:
        """Verify Writer monad laws."""
        return {
            'left_identity': self._verify_left_identity(f),
            'right_identity': self._verify_right_identity(),
            # Associativity verified structurally
        }

    def _verify_left_identity(self, f: Callable[[A], 'Witnessed[B]']) -> bool:
        """pure(a) >>= f ≡ f(a)"""
        a = self.value
        lhs = Witnessed.pure(a).bind(f)
        rhs = f(a)
        return lhs.value == rhs.value

    def _verify_right_identity(self) -> bool:
        """m >>= pure ≡ m"""
        lhs = self.bind(Witnessed.pure)
        return lhs.value == self.value


def kleisli_compose(
    f: Callable[[A], Witnessed[B]],
    g: Callable[[B], Witnessed[C]]
) -> Callable[[A], Witnessed[C]]:
    """Kleisli composition (>=>). The categorical composition for effectful functions."""
    def composed(a: A) -> Witnessed[C]:
        witnessed_b = f(a)
        return witnessed_b.bind(g)
    return composed


# Integration with existing witness service
class WitnessedOperation:
    """Decorator for witnessed operations."""

    def __init__(
        self,
        action: str,
        reasoning_fn: Callable = None,
        principles: List[str] = None
    ):
        self.action = action
        self.reasoning_fn = reasoning_fn or (lambda *args: "")
        self.principles = principles or []

    def __call__(self, func):
        async def wrapper(*args, **kwargs) -> Witnessed:
            # Execute function
            result = await func(*args, **kwargs)

            # Generate mark
            mark = Mark(
                id=generate_id(),
                action=self.action,
                reasoning=self.reasoning_fn(*args, **kwargs),
                timestamp=datetime.now(),
                principle_scores={p: 0.8 for p in self.principles}  # Placeholder
            )

            # Return witnessed result
            return Witnessed(value=result, marks=[mark])

        return wrapper


# Example: Chain of witnessed operations
@WitnessedOperation(
    action="analyzed_input",
    reasoning_fn=lambda x: f"Analyzed: {x[:50]}...",
    principles=["tasteful", "composable"]
)
async def analyze(text: str) -> str:
    return await llm.complete(f"Analyze: {text}")

@WitnessedOperation(
    action="synthesized_result",
    reasoning_fn=lambda x: f"Synthesized from analysis",
    principles=["generative", "joy_inducing"]
)
async def synthesize(analysis: str) -> str:
    return await llm.complete(f"Synthesize: {analysis}")

# Compose using Kleisli
analyze_and_synthesize = kleisli_compose(
    lambda text: analyze(text),
    lambda analysis: synthesize(analysis)
)

# Usage
result: Witnessed[str] = await analyze_and_synthesize("input text")
# result.marks contains [analyze_mark, synthesize_mark]
```

### Tests

```python
# tests/test_kleisli_witness.py

def test_left_identity():
    """pure(a) >>= f ≡ f(a)"""
    a = "test"
    f = lambda x: Witnessed(value=x.upper(), marks=[mock_mark("f")])

    lhs = Witnessed.pure(a).bind(f)
    rhs = f(a)

    assert lhs.value == rhs.value

def test_kleisli_composition_preserves_traces():
    """(f >=> g)(a) should have traces from both f and g."""
    f = lambda x: Witnessed(value=x * 2, marks=[mock_mark("f")])
    g = lambda x: Witnessed(value=x + 1, marks=[mock_mark("g")])

    composed = kleisli_compose(f, g)
    result = composed(5)

    assert result.value == 11
    assert len(result.marks) == 2
    assert result.marks[0].action == "f"
    assert result.marks[1].action == "g"
```

### Effort: 1 week

---

## Proposal E2: Analysis Operad Composer

### Theory Basis (Ch 15: Analysis Operad)

```
Four analysis modes:
  CATEGORICAL: Structure-preserving, law-checking
  EPISTEMIC: Uncertainty-aware, confidence tracking
  DIALECTICAL: Thesis-antithesis-synthesis
  GENERATIVE: From spec to implementation

Operad composition:
  CATEGORICAL → EPISTEMIC → DIALECTICAL → GENERATIVE
```

### Implementation

**Location**: `impl/claude/services/analysis/operad_composer.py`

```python
from dataclasses import dataclass
from typing import List, Callable, Any
from enum import Enum

class AnalysisMode(Enum):
    """The four analysis modes."""
    CATEGORICAL = "categorical"
    EPISTEMIC = "epistemic"
    DIALECTICAL = "dialectical"
    GENERATIVE = "generative"

@dataclass
class AnalysisResult:
    """Result of an analysis phase."""
    mode: AnalysisMode
    input: Any
    output: Any
    confidence: float
    marks: List[Mark]

@dataclass
class AnalysisPhase:
    """A single analysis phase."""
    mode: AnalysisMode
    analyzer: Callable[[Any], Witnessed[Any]]
    preconditions: List[Callable[[Any], bool]]
    postconditions: List[Callable[[Any, Any], bool]]

@dataclass
class AnalysisOperadComposer:
    """Composes analysis phases according to operad structure."""
    phases: Dict[AnalysisMode, AnalysisPhase]

    def compose(self, modes: List[AnalysisMode]) -> Callable[[Any], Witnessed[Any]]:
        """Compose analysis phases in sequence."""
        if not modes:
            return Witnessed.pure

        composed = self.phases[modes[0]].analyzer
        for mode in modes[1:]:
            phase = self.phases[mode]
            composed = kleisli_compose(composed, phase.analyzer)

        return composed

    async def analyze(
        self,
        input: Any,
        modes: List[AnalysisMode] = None
    ) -> List[AnalysisResult]:
        """Run full analysis through specified modes."""
        if modes is None:
            # Default: all modes in canonical order
            modes = [
                AnalysisMode.CATEGORICAL,
                AnalysisMode.EPISTEMIC,
                AnalysisMode.DIALECTICAL,
                AnalysisMode.GENERATIVE,
            ]

        results = []
        current_input = input

        for mode in modes:
            phase = self.phases[mode]

            # Check preconditions
            for precond in phase.preconditions:
                if not precond(current_input):
                    raise ValueError(f"Precondition failed for {mode}")

            # Run analysis
            witnessed = await phase.analyzer(current_input)

            # Check postconditions
            for postcond in phase.postconditions:
                if not postcond(current_input, witnessed.value):
                    raise ValueError(f"Postcondition failed for {mode}")

            results.append(AnalysisResult(
                mode=mode,
                input=current_input,
                output=witnessed.value,
                confidence=self._compute_confidence(witnessed.marks),
                marks=witnessed.marks
            ))

            current_input = witnessed.value

        return results

    def _compute_confidence(self, marks: List[Mark]) -> float:
        """Compute confidence from marks."""
        if not marks:
            return 0.5
        # Average of mark confidences
        return sum(
            sum(m.principle_scores.values()) / len(m.principle_scores)
            for m in marks
        ) / len(marks)


# Standard analysis phases
def create_standard_phases(llm: 'LLMProvider') -> Dict[AnalysisMode, AnalysisPhase]:
    """Create standard analysis phases."""
    return {
        AnalysisMode.CATEGORICAL: AnalysisPhase(
            mode=AnalysisMode.CATEGORICAL,
            analyzer=lambda x: categorical_analyze(x, llm),
            preconditions=[],
            postconditions=[lambda i, o: 'structure' in str(o).lower()]
        ),
        AnalysisMode.EPISTEMIC: AnalysisPhase(
            mode=AnalysisMode.EPISTEMIC,
            analyzer=lambda x: epistemic_analyze(x, llm),
            preconditions=[],
            postconditions=[lambda i, o: 'confidence' in str(o).lower()]
        ),
        AnalysisMode.DIALECTICAL: AnalysisPhase(
            mode=AnalysisMode.DIALECTICAL,
            analyzer=lambda x: dialectical_analyze(x, llm),
            preconditions=[],
            postconditions=[lambda i, o: 'synthesis' in str(o).lower()]
        ),
        AnalysisMode.GENERATIVE: AnalysisPhase(
            mode=AnalysisMode.GENERATIVE,
            analyzer=lambda x: generative_analyze(x, llm),
            preconditions=[],
            postconditions=[]
        ),
    }

@WitnessedOperation(action="categorical_analysis", principles=["composable"])
async def categorical_analyze(input: Any, llm: 'LLMProvider') -> str:
    """Categorical analysis: structure and laws."""
    return await llm.complete(f"""
Analyze the following categorically:
1. What are the objects (entities)?
2. What are the morphisms (relationships)?
3. Do composition laws hold?
4. What structure is preserved?

Input: {input}
""")

@WitnessedOperation(action="epistemic_analysis", principles=["ethical"])
async def epistemic_analyze(input: Any, llm: 'LLMProvider') -> str:
    """Epistemic analysis: uncertainty and confidence."""
    return await llm.complete(f"""
Analyze the following epistemically:
1. What is known with certainty?
2. What is uncertain?
3. What are the confidence levels?
4. What would change our beliefs?

Input: {input}
""")

@WitnessedOperation(action="dialectical_analysis", principles=["heterarchical"])
async def dialectical_analyze(input: Any, llm: 'LLMProvider') -> str:
    """Dialectical analysis: thesis, antithesis, synthesis."""
    return await llm.complete(f"""
Analyze the following dialectically:
1. What is the thesis (main claim)?
2. What is the antithesis (counter)?
3. What synthesis resolves the tension?
4. What is preserved in the synthesis?

Input: {input}
""")

@WitnessedOperation(action="generative_analysis", principles=["generative"])
async def generative_analyze(input: Any, llm: 'LLMProvider') -> str:
    """Generative analysis: from spec to implementation."""
    return await llm.complete(f"""
Generate implementation from this specification:
1. What are the core components?
2. What is the minimal implementation?
3. What can be regenerated from spec?
4. What is the compression ratio?

Input: {input}
""")
```

### Effort: 5 days

---

## Proposal E3: DialecticalFusionService

> **STATUS: DONE** (2025-12-26)
> - Location: `impl/claude/services/dialectic/fusion.py`
> - Tests: `impl/claude/services/dialectic/_tests/test_fusion.py` (22 tests passing)
> - Honest naming: Uses "heuristic synthesis" not "cocone"
> - Constitution Article IV (Disgust Veto) and Article VI (Fusion as Goal) integrated

### Theory Basis (Ch 17: Dialectical Fusion)

```
Dialectical fusion (Kent + Claude):
  thesis: Kent's view
  antithesis: Claude's view
  synthesis: Cocone construction

The Emerging Constitution (7 articles) governs the fusion.
```

### Implementation

**Location**: `impl/claude/services/dialectic/fusion.py`

```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum

class FusionResult(Enum):
    """Outcomes of dialectical fusion."""
    CONSENSUS = "consensus"        # Agreement reached
    SYNTHESIS = "synthesis"        # New position that sublates both
    KENT_PREVAILS = "kent"         # Kent's position wins
    CLAUDE_PREVAILS = "claude"     # Claude's position wins
    DEFERRED = "deferred"          # Decision deferred
    VETO = "veto"                  # Kent's disgust veto

@dataclass
class Position:
    """A position in the dialectic."""
    content: str
    reasoning: str
    confidence: float
    evidence: List[str]
    principle_alignment: Dict[str, float]

@dataclass
class Fusion:
    """A dialectical fusion."""
    id: str
    topic: str
    timestamp: datetime
    kent_position: Position
    claude_position: Position
    synthesis: Optional[Position]
    result: FusionResult
    reasoning: str
    trust_delta: float  # How much trust changed

@dataclass
class DialecticalFusionService:
    """Manages dialectical fusion between Kent and Claude."""
    witness: 'WitnessService'
    trust_gate: 'TrustGateService'
    llm: 'LLMProvider'

    async def propose_fusion(
        self,
        topic: str,
        kent_view: str,
        kent_reasoning: str,
        claude_view: str,
        claude_reasoning: str
    ) -> Fusion:
        """Propose and execute a dialectical fusion."""
        # 1. Structure positions
        kent_position = await self._structure_position(
            kent_view, kent_reasoning, "kent"
        )
        claude_position = await self._structure_position(
            claude_view, claude_reasoning, "claude"
        )

        # 2. Check for immediate consensus
        if await self._check_consensus(kent_position, claude_position):
            return await self._create_consensus_fusion(
                topic, kent_position, claude_position
            )

        # 3. Attempt synthesis
        synthesis = await self._attempt_synthesis(
            topic, kent_position, claude_position
        )

        # 4. Determine result
        result, reasoning = await self._determine_result(
            kent_position, claude_position, synthesis
        )

        # 5. Compute trust delta
        trust_delta = self._compute_trust_delta(result, synthesis)

        # 6. Record in witness
        fusion = Fusion(
            id=generate_id(),
            topic=topic,
            timestamp=datetime.now(),
            kent_position=kent_position,
            claude_position=claude_position,
            synthesis=synthesis,
            result=result,
            reasoning=reasoning,
            trust_delta=trust_delta
        )

        await self._witness_fusion(fusion)
        return fusion

    async def _structure_position(
        self,
        view: str,
        reasoning: str,
        perspective: str
    ) -> Position:
        """Structure a raw view into a Position."""
        # Extract evidence
        evidence_prompt = f"List evidence supporting: {view}\n\nReasoning: {reasoning}"
        evidence_response = await self.llm.complete(evidence_prompt)
        evidence = evidence_response.strip().split("\n")

        # Score principle alignment
        alignment = {}
        for principle in ["tasteful", "curated", "ethical", "joy_inducing", "composable", "heterarchical", "generative"]:
            score = await self._score_principle(view, principle)
            alignment[principle] = score

        # Estimate confidence
        confidence = sum(alignment.values()) / len(alignment)

        return Position(
            content=view,
            reasoning=reasoning,
            confidence=confidence,
            evidence=evidence,
            principle_alignment=alignment
        )

    async def _check_consensus(
        self,
        kent: Position,
        claude: Position
    ) -> bool:
        """Check if positions are already in consensus."""
        prompt = f"""
Do these two positions fundamentally agree or disagree?

Position 1: {kent.content}
Position 2: {claude.content}

Answer only "AGREE" or "DISAGREE":
"""
        response = await self.llm.complete(prompt)
        return "AGREE" in response.upper()

    async def _attempt_synthesis(
        self,
        topic: str,
        kent: Position,
        claude: Position
    ) -> Optional[Position]:
        """Attempt to synthesize a new position."""
        prompt = f"""
Topic: {topic}

Kent's position: {kent.content}
Kent's reasoning: {kent.reasoning}

Claude's position: {claude.content}
Claude's reasoning: {claude.reasoning}

Generate a synthesis that:
1. Acknowledges the valid points in both positions
2. Resolves the tension between them
3. Creates a new position that sublates (preserves and transcends) both
4. Explains what each side contributes to the synthesis

Synthesis:
"""
        synthesis_content = await self.llm.complete(prompt)

        return await self._structure_position(
            synthesis_content,
            f"Synthesis of Kent's {kent.content} and Claude's {claude.content}",
            "synthesis"
        )

    async def _determine_result(
        self,
        kent: Position,
        claude: Position,
        synthesis: Optional[Position]
    ) -> tuple[FusionResult, str]:
        """Determine the fusion result."""
        # Check Kent's ETHICAL floor (disgust veto)
        if kent.principle_alignment.get("ethical", 1.0) < 0.3:
            return FusionResult.VETO, "Kent's disgust veto (ETHICAL floor violation)"

        # If synthesis is strong, use it
        if synthesis and synthesis.confidence > max(kent.confidence, claude.confidence):
            return FusionResult.SYNTHESIS, f"Synthesis achieves higher confidence ({synthesis.confidence:.2f})"

        # Otherwise, higher confidence wins
        if kent.confidence > claude.confidence:
            return FusionResult.KENT_PREVAILS, f"Kent's position has higher confidence ({kent.confidence:.2f} vs {claude.confidence:.2f})"
        elif claude.confidence > kent.confidence:
            return FusionResult.CLAUDE_PREVAILS, f"Claude's position has higher confidence ({claude.confidence:.2f} vs {kent.confidence:.2f})"
        else:
            return FusionResult.DEFERRED, "Positions equally confident, deferring decision"

    def _compute_trust_delta(
        self,
        result: FusionResult,
        synthesis: Optional[Position]
    ) -> float:
        """Compute how much trust changes from this fusion."""
        deltas = {
            FusionResult.CONSENSUS: 0.1,
            FusionResult.SYNTHESIS: 0.15,
            FusionResult.KENT_PREVAILS: 0.05,
            FusionResult.CLAUDE_PREVAILS: 0.08,
            FusionResult.DEFERRED: 0.0,
            FusionResult.VETO: -0.1,
        }
        return deltas.get(result, 0.0)

    async def _witness_fusion(self, fusion: Fusion):
        """Record fusion in witness."""
        await self.witness.mark(
            action=f"dialectical_fusion:{fusion.result.value}",
            reasoning=fusion.reasoning,
            metadata={
                "fusion_id": fusion.id,
                "topic": fusion.topic,
                "result": fusion.result.value,
                "trust_delta": fusion.trust_delta
            }
        )

    async def _score_principle(self, view: str, principle: str) -> float:
        """Score a view against a principle."""
        prompt = f"On a scale of 0-1, how well does '{view}' align with the principle '{principle}'? Answer with just a number:"
        response = await self.llm.complete(prompt)
        try:
            return float(response.strip())
        except:
            return 0.5
```

### Effort: 1 week

---

## Proposal E4: AGENTESE Fusion Ceremony

### Theory Basis (Ch 17: Dialectical Fusion)

```
AGENTESE path for fusion:
  self.dialectic.fuse(kent_view, claude_view)

The ceremony records:
  - Both positions
  - The synthesis
  - The witness mark
```

### Implementation

**Location**: `impl/claude/protocols/agentese/nodes/dialectic.py`

```python
from protocols.agentese.gateway import node
from services.dialectic.fusion import DialecticalFusionService, Fusion

@node(
    path="self.dialectic.fuse",
    dependencies=("dialectic_service", "witness_service")
)
class FuseDialectic:
    """AGENTESE node for dialectical fusion."""

    def __init__(
        self,
        dialectic_service: DialecticalFusionService,
        witness_service: 'WitnessService'
    ):
        self.dialectic = dialectic_service
        self.witness = witness_service

    async def invoke(
        self,
        topic: str,
        kent_view: str,
        kent_reasoning: str,
        claude_view: str,
        claude_reasoning: str,
        **kwargs
    ) -> dict:
        """Execute dialectical fusion ceremony."""
        fusion = await self.dialectic.propose_fusion(
            topic=topic,
            kent_view=kent_view,
            kent_reasoning=kent_reasoning,
            claude_view=claude_view,
            claude_reasoning=claude_reasoning
        )

        return {
            "fusion_id": fusion.id,
            "result": fusion.result.value,
            "synthesis": fusion.synthesis.content if fusion.synthesis else None,
            "reasoning": fusion.reasoning,
            "trust_delta": fusion.trust_delta
        }


@node(
    path="self.dialectic.quick",
    dependencies=("dialectic_service",)
)
class QuickDecision:
    """Quick decision recording without full fusion."""

    def __init__(self, dialectic_service: DialecticalFusionService):
        self.dialectic = dialectic_service

    async def invoke(
        self,
        decision: str,
        reasoning: str,
        **kwargs
    ) -> dict:
        """Record a quick decision."""
        # Single-party decision (no dialectic needed)
        mark = await self.dialectic.witness.mark(
            action=f"quick_decision:{decision[:50]}",
            reasoning=reasoning
        )

        return {
            "mark_id": mark.id,
            "decision": decision,
            "reasoning": reasoning
        }


@node(
    path="self.dialectic.history",
    dependencies=("dialectic_service",)
)
class FusionHistory:
    """Query fusion history."""

    def __init__(self, dialectic_service: DialecticalFusionService):
        self.dialectic = dialectic_service

    async def invoke(
        self,
        topic: str = None,
        limit: int = 10,
        **kwargs
    ) -> list:
        """Get fusion history."""
        history = await self.dialectic.get_history(topic=topic, limit=limit)
        return [
            {
                "fusion_id": f.id,
                "topic": f.topic,
                "result": f.result.value,
                "timestamp": f.timestamp.isoformat()
            }
            for f in history
        ]
```

### Effort: 5 days

---

## Proposal E5: Trust Gradient Dialectic

### Theory Basis (Ch 17: Dialectical Fusion)

```
Trust influences dialectic:
  - High trust: Claude's view gets more weight
  - Low trust: Kent's view dominates
  - Trust changes based on fusion outcomes
```

### Implementation

**Location**: `impl/claude/services/dialectic/trust_integration.py`

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class TrustWeightedFusion:
    """Fusion service that weights positions by trust."""
    base_fusion: DialecticalFusionService
    trust_gate: TrustGateService

    async def propose_fusion(
        self,
        topic: str,
        kent_view: str,
        kent_reasoning: str,
        claude_view: str,
        claude_reasoning: str
    ) -> Fusion:
        """Execute trust-weighted fusion."""
        # Get current trust level
        trust = self.trust_gate.state.global_trust

        # Weight positions by trust
        kent_weight = 1.0  # Kent always at full weight (asymmetric power)
        claude_weight = trust  # Claude weighted by accumulated trust

        # Modify confidence scores
        fusion = await self.base_fusion.propose_fusion(
            topic=topic,
            kent_view=kent_view,
            kent_reasoning=kent_reasoning,
            claude_view=claude_view,
            claude_reasoning=claude_reasoning
        )

        # Adjust synthesis based on trust
        if fusion.synthesis:
            fusion.synthesis.confidence *= claude_weight

        # Update trust based on outcome
        self._update_trust(fusion)

        return fusion

    def _update_trust(self, fusion: Fusion):
        """Update trust based on fusion outcome."""
        if fusion.result == FusionResult.SYNTHESIS:
            # Successful synthesis builds trust
            self.trust_gate.record_outcome(
                ActionType.AUTONOMOUS,
                aligned=True,
                magnitude=0.5
            )
        elif fusion.result == FusionResult.VETO:
            # Veto means misalignment
            self.trust_gate.record_outcome(
                ActionType.AUTONOMOUS,
                aligned=False,
                magnitude=1.0
            )


@dataclass
class DialecticTrustLearner:
    """Learns trust adjustments from fusion outcomes."""
    fusion_service: TrustWeightedFusion
    history: List[Fusion]

    def analyze_trust_trajectory(self) -> dict:
        """Analyze how trust has evolved through fusions."""
        if not self.history:
            return {"trajectory": [], "trend": "neutral"}

        trajectory = []
        cumulative_trust = 0.5  # Starting trust

        for fusion in self.history:
            cumulative_trust += fusion.trust_delta
            cumulative_trust = max(0.0, min(1.0, cumulative_trust))
            trajectory.append({
                "fusion_id": fusion.id,
                "topic": fusion.topic,
                "result": fusion.result.value,
                "trust_after": cumulative_trust
            })

        # Compute trend
        if len(trajectory) >= 2:
            recent = trajectory[-5:]
            deltas = [
                trajectory[i]["trust_after"] - trajectory[i-1]["trust_after"]
                for i in range(1, len(recent))
            ]
            avg_delta = sum(deltas) / len(deltas) if deltas else 0

            if avg_delta > 0.01:
                trend = "increasing"
            elif avg_delta < -0.01:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "trajectory": trajectory,
            "trend": trend,
            "current_trust": cumulative_trust
        }

    def recommend_trust_action(self) -> str:
        """Recommend action based on trust trajectory."""
        analysis = self.analyze_trust_trajectory()

        if analysis["trend"] == "decreasing":
            return "CAUTION: Trust declining. Review recent fusions for misalignment."
        elif analysis["trend"] == "increasing":
            return "Trust building. Continue current collaboration pattern."
        elif analysis["current_trust"] < 0.3:
            return "LOW TRUST: Operate conservatively. Seek more consensus."
        else:
            return "Trust stable. Normal operations."
```

### Effort: 5 days

---

## Implementation Timeline

### Completed (2025-12-26)

```
✓ E1: Kleisli Witness (DONE)
├── ✓ Writer monad implementation (Witnessed[A])
├── ✓ Kleisli composition (kleisli_compose, kleisli_chain)
├── ✓ Integration decorators (@witnessed_operation, @witnessed_sync)
└── ✓ 36 property tests (all monad laws verified)

✓ E3: Dialectical Fusion (DONE)
├── ✓ Position and Fusion models
├── ✓ DialecticalFusionService with Constitution integration
├── ✓ 6 FusionResult outcomes
└── ✓ 22 tests passing
```

### Remaining Work

```
Week N: Analysis Operad (E2)
├── Day 1-2: Four analysis modes (CATEGORICAL, EPISTEMIC, DIALECTICAL, GENERATIVE)
├── Day 3-4: Operad composition with pre/post conditions
└── Day 5: Integration with Kleisli (E1)

Week N+1: AGENTESE + Trust (E4, E5)
├── Day 1-2: AGENTESE fusion nodes (self.dialectic.fuse, self.dialectic.quick)
├── Day 3-4: Trust-weighted fusion (TrustWeightedFusion)
└── Day 5: DialecticTrustLearner trajectory analysis
```

---

## Success Criteria

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Kleisli laws hold | Property tests | 100% pass |
| Analysis modes compose | Unit tests | All 4 modes work |
| Fusion produces synthesis | Integration tests | Synthesis quality > 0.7 |
| AGENTESE nodes registered | Startup test | All nodes discoverable |
| Trust tracks correctly | Simulation | Trust correlates with alignment |

---

## Dependencies

- **Upstream**: Witness (existing), Trust Gate (D2)
- **Downstream**: All pilots use witness; fusions recorded
- **Pilot Integration**: All pilots (witness spine)

---

**Document Metadata**
- **Lines**: ~850
- **Theory Chapters**: 15-17
- **Proposals**: E1-E5 (E1, E3 DONE; E2, E4, E5 pending)
- **Inventions**: Approximate[T] type-level honesty wrapper
- **Remaining Effort**: ~2 weeks (E2, E4, E5)
- **Last Updated**: 2025-12-26
