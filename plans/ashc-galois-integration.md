# ASHC Galois Integration Plan

> *"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof."*

**Status**: ✅ IMPLEMENTED (Phase 1-2, 2025-01-10)
**Date**: 2025-01-10
**Priority**: P1 (High Value)
**Scope**: Evidence scoring, self-hosting, chaos testing
**Related**: `coherence-synthesis-master.md`, `zero-seed-integration.md`

---

## Executive Summary

ASHC (Agentic Self-Hosting Compiler) correctly identifies that **evidence, not generation** is the hard problem. The implementation has 276 passing tests across 4 phases. This plan integrates Galois loss into the evidence scoring system, validates self-hosting, and completes the missing chaos testing phase.

### Current State

| Phase | Tests | Status |
|-------|-------|--------|
| Phase 1: L0 Kernel | 47 | Complete |
| Phase 2: Evidence Engine | 103 | Complete |
| Phase 2.5: Adaptive Bayesian | 32 | Complete |
| Phase 2.75: Economy | ~94 | Complete |
| **Phase 3: Chaos Testing** | 0 | **NOT IMPLEMENTED** |
| **Phase 4: Causal Learning** | 0 | **NOT IMPLEMENTED** |

### The Gap

```python
# CURRENT (evidence.py)
def equivalence_score(self) -> float:
    pass_rate = sum(r.test_results.passed for r in self.runs) / len(self.runs)
    chaos_score = self.chaos_report.stability_score
    nudge_stability = self.causal_graph.stability_score
    return (pass_rate * 0.4 + chaos_score * 0.3 + nudge_stability * 0.3)

# NEEDED
def equivalence_score(self) -> float:
    # Galois loss IS the equivalence measure
    spec_loss = await galois_loss(self.spec, self.executable)
    evidence_coherence = 1.0 - spec_loss  # R = 1 - L

    # Weight by empirical confidence
    empirical_weight = self._empirical_confidence()

    return evidence_coherence * empirical_weight
```

---

## Part I: The Core Insight

From the ASHC spec:

> **The compiler is a trace accumulator, not a code generator.**
>
> LLMs are "good enough" at: idea → prompt → implementation. That pipeline works. What's missing is **evidence that the implementation matches the spec**.

### The ETHICAL Gate

All ASHC outputs must pass the ETHICAL floor constraint (Amendment A):

```python
# ETHICAL is a GATE, not a weight
ETHICAL_FLOOR_THRESHOLD = 0.6

# If generated code violates ethical constraints → REJECT
# Examples:
# - Code that hoards data without disclosure
# - Code that manipulates rather than assists
# - Code that claims certainty it doesn't have
```

**Implication**: An implementation with high pass rate but ETHICAL < 0.6 is REJECTED.

### The Failure of Prompt Engineering

The spec notes that Evergreen Prompt System has 216 tests but "solved the wrong problem":

> **Writing prompts is not hard.** A competent developer can write a good system prompt in one sitting.
>
> **What IS hard:**
> - How do I know my agent will behave correctly in edge cases?
> - How do I verify that my spec matches what the agent actually does?
> - How do I build confidence that changes won't break things?
>
> These are verification problems, not generation problems.

### Galois Loss as Verification

The connection to Zero Seed is clear:

```
ASHC Evidence = Galois Loss Applied to Spec↔Impl

Specifically:
  L(spec, impl) = d(spec, C(R(impl)))

Where:
  R = Restructure impl back to modular form
  C = Canonicalize to spec-like format
  d = Semantic distance

If L < threshold, spec and impl are equivalent.
```

---

## Part II: Evidence Galois Integration

### 2.1 Updated Evidence Types

```python
# File: impl/claude/protocols/ashc/evidence.py (modifications)

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Sequence

from services.galois.service import GaloisLossService
from services.galois.types import GaloisLoss


@dataclass(frozen=True)
class Run:
    """A single execution of spec → implementation."""

    spec_hash: str
    prompt_used: str
    implementation: str
    test_results: TestReport
    type_results: TypeReport
    lint_results: LintReport
    timestamp: datetime
    duration_ms: int
    nudges: tuple[Nudge, ...]

    # NEW: Galois loss for this run
    galois_loss: float | None = None


@dataclass(frozen=True)
class Evidence:
    """
    Accumulated evidence for spec↔impl equivalence.

    UPDATED: Now includes Galois loss as primary equivalence measure.
    """

    runs: tuple[Run, ...]
    chaos_report: ChaosReport | None
    causal_graph: CausalGraph | None
    confidence: float

    # NEW: Galois-based fields
    spec_content: str = ""
    best_impl_content: str = ""
    galois_loss: float | None = None  # L(spec, best_impl)

    def equivalence_score(self) -> float:
        """
        How confident are we that spec matches impl?

        UPDATED: Now uses Galois loss as primary signal.

        The equation:
            score = (1 - L) * empirical_weight

        Where:
            L = galois_loss (structure preservation)
            empirical_weight = confidence from run count and pass rate
        """
        if self.galois_loss is None:
            # Fallback to old method if Galois not computed
            return self._legacy_equivalence_score()

        # Galois coherence: R = 1 - L
        galois_coherence = 1.0 - self.galois_loss

        # Empirical weight: more runs + higher pass rate = more confidence
        empirical_weight = self._compute_empirical_weight()

        return galois_coherence * empirical_weight

    def _compute_empirical_weight(self) -> float:
        """
        Compute weight from empirical evidence.

        More runs with higher pass rate = higher weight.
        """
        if not self.runs:
            return 0.0

        # Pass rate
        pass_rate = sum(
            1 for r in self.runs if r.test_results.passed
        ) / len(self.runs)

        # Volume factor (saturates at 100 runs)
        volume = min(1.0, len(self.runs) / 100)

        # Chaos factor (if available)
        chaos_factor = 1.0
        if self.chaos_report:
            chaos_factor = self.chaos_report.stability_score

        return pass_rate * 0.5 + volume * 0.3 + chaos_factor * 0.2

    def _legacy_equivalence_score(self) -> float:
        """Original equivalence score for backward compatibility."""
        if not self.runs:
            return 0.0

        pass_rate = sum(
            1 for r in self.runs if r.test_results.passed
        ) / len(self.runs)

        chaos_score = 1.0
        if self.chaos_report:
            chaos_score = self.chaos_report.stability_score

        nudge_stability = 1.0
        if self.causal_graph:
            nudge_stability = self.causal_graph.stability_score

        return (
            pass_rate * 0.4 +
            chaos_score * 0.3 +
            nudge_stability * 0.3
        )

    @property
    def galois_coherence(self) -> float:
        """Coherence from Galois loss: 1 - L."""
        if self.galois_loss is None:
            return 0.0
        return 1.0 - self.galois_loss


@dataclass(frozen=True)
class ASHCOutput:
    """
    The compiler's output: executable + evidence.

    UPDATED: is_verified now uses Galois loss.
    """

    executable: AgentExecutable
    evidence: Evidence
    spec_hash: str

    @property
    def is_verified(self) -> bool:
        """
        Is there sufficient evidence for this executable?

        UPDATED: Now requires Galois coherence.
        """
        # Must have Galois loss computed
        if self.evidence.galois_loss is None:
            return False

        # Galois coherence must be high
        if self.evidence.galois_coherence < 0.85:
            return False

        # Must have enough runs
        if len(self.evidence.runs) < 10:
            return False

        # Equivalence score must be high
        if self.evidence.equivalence_score() < 0.8:
            return False

        # Chaos stability must be high (if available)
        if self.evidence.chaos_report:
            if self.evidence.chaos_report.pass_rate < 0.95:
                return False

        return True
```

### 2.2 Galois-Enhanced Compiler

```python
# File: impl/claude/protocols/ashc/compiler.py (modifications)

from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncIterator

from protocols.ashc.evidence import ASHCOutput, Evidence, Run
from services.galois.service import GaloisLossService


@dataclass
class GaloisEvidenceCompiler:
    """
    ASHC compiler with Galois loss integration.

    Compiles spec to executable while accumulating Galois-grounded evidence.
    """

    galois: GaloisLossService
    generator: ImplementationGenerator
    verifier: ImplementationVerifier

    async def compile(
        self,
        spec: str,
        n_variations: int = 10,
        compute_chaos: bool = False,
    ) -> ASHCOutput:
        """
        Compile spec to executable with Galois evidence.

        Flow:
        1. Generate N implementation variations
        2. Verify each with tests/types/lint
        3. Compute Galois loss for each
        4. Select best implementation
        5. Optionally run chaos tests
        6. Return output with full evidence

        Args:
            spec: The specification to compile
            n_variations: Number of variations to generate
            compute_chaos: Whether to run chaos testing

        Returns:
            ASHCOutput with executable and Galois-grounded evidence
        """
        runs = []

        # Generate and verify N variations
        async for run in self._generate_variations(spec, n_variations):
            runs.append(run)

        # Find best implementation (lowest Galois loss)
        best_run = min(runs, key=lambda r: r.galois_loss or 1.0)

        # Compute overall spec↔impl Galois loss
        overall_loss = await self.galois.compute(
            f"SPEC:\n{spec}\n\nIMPL:\n{best_run.implementation}"
        )

        # Build evidence
        evidence = Evidence(
            runs=tuple(runs),
            chaos_report=None,  # TODO: Phase 3
            causal_graph=None,  # TODO: Phase 4
            confidence=len(runs) / n_variations,
            spec_content=spec,
            best_impl_content=best_run.implementation,
            galois_loss=overall_loss.total,
        )

        # Optionally run chaos tests
        if compute_chaos:
            chaos_report = await self._run_chaos_tests(runs)
            evidence = evidence._replace(chaos_report=chaos_report)

        return ASHCOutput(
            executable=AgentExecutable(code=best_run.implementation),
            evidence=evidence,
            spec_hash=hash_content(spec),
        )

    async def _generate_variations(
        self,
        spec: str,
        n: int,
    ) -> AsyncIterator[Run]:
        """Generate N implementation variations with Galois loss."""
        for i in range(n):
            # Generate implementation
            impl = await self.generator.generate(spec, variation=i)

            # Verify
            test_results = await self.verifier.run_tests(impl)
            type_results = await self.verifier.run_types(impl)
            lint_results = await self.verifier.run_lint(impl)

            # Compute Galois loss for this run
            run_loss = await self.galois.compute(
                f"SPEC:\n{spec}\n\nIMPL:\n{impl.code}"
            )

            yield Run(
                spec_hash=hash_content(spec),
                prompt_used=impl.prompt,
                implementation=impl.code,
                test_results=test_results,
                type_results=type_results,
                lint_results=lint_results,
                timestamp=datetime.now(timezone.utc),
                duration_ms=impl.duration_ms,
                nudges=(),
                galois_loss=run_loss.total,
            )

    async def _run_chaos_tests(self, runs: list[Run]) -> ChaosReport:
        """Run chaos tests on implementations."""
        # TODO: Implement in Phase 3
        raise NotImplementedError("Phase 3: Chaos Testing")
```

---

## Part III: Self-Hosting Verification

### 3.1 The Self-Hosting Test

ASHC must be able to compile its own kernel:

```python
# File: impl/claude/protocols/ashc/_tests/test_self_hosting.py

import pytest
from pathlib import Path

from protocols.ashc.compiler import GaloisEvidenceCompiler
from protocols.ashc.evidence import ASHCOutput
from services.galois.service import GaloisLossService

BOOTSTRAP_SPECS = [
    ("zero-seed", Path("spec/protocols/zero-seed.md")),
    ("constitution", Path("spec/principles/CONSTITUTION.md")),
    ("witness-primitives", Path("spec/protocols/witness-primitives.md")),
    ("agentese", Path("spec/protocols/agentese.md")),
]


@pytest.fixture
def galois_compiler():
    galois = GaloisLossService()
    return GaloisEvidenceCompiler(galois=galois)


class TestSelfHosting:
    """
    ASHC must be able to compile its own foundation.

    This is the self-hosting test: can the compiler regenerate
    the specs that define it?
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name,path", BOOTSTRAP_SPECS)
    async def test_can_compile_bootstrap_spec(
        self,
        galois_compiler,
        name: str,
        path: Path,
    ):
        """Each bootstrap spec should compile with high evidence."""
        if not path.exists():
            pytest.skip(f"Spec not found: {path}")

        spec = path.read_text()
        output = await galois_compiler.compile(
            spec,
            n_variations=10,  # Reduced for test speed
        )

        # Must be verified
        assert output.is_verified, (
            f"{name} failed verification: "
            f"equivalence={output.evidence.equivalence_score():.2f}, "
            f"galois_loss={output.evidence.galois_loss:.3f}"
        )

        # Galois coherence must be high
        assert output.evidence.galois_coherence >= 0.85, (
            f"{name} Galois coherence too low: {output.evidence.galois_coherence:.2f}"
        )

    @pytest.mark.asyncio
    async def test_zero_seed_regeneration(self, galois_compiler):
        """
        Zero Seed must regenerate from itself.

        This is the ultimate self-hosting test:
        1. Compile Zero Seed spec
        2. Extract spec from generated executable
        3. Compare regenerated spec to original
        4. Galois loss must be < 0.15 (85% regenerability)
        """
        zero_seed_path = Path("spec/protocols/zero-seed.md")
        if not zero_seed_path.exists():
            pytest.skip("Zero Seed spec not found")

        original_spec = zero_seed_path.read_text()

        # Compile
        output = await galois_compiler.compile(original_spec, n_variations=20)

        # Extract regenerated spec (assuming executable has render_spec method)
        if hasattr(output.executable, "render_spec"):
            regenerated_spec = output.executable.render_spec()
        else:
            # Fallback: use best impl as spec
            regenerated_spec = output.evidence.best_impl_content

        # Compute regeneration loss
        galois = galois_compiler.galois
        regen_loss = await galois.compute(
            f"ORIGINAL:\n{original_spec}\n\nREGENERATED:\n{regenerated_spec}"
        )

        # Must be a fixed point
        assert regen_loss.total < 0.15, (
            f"Zero Seed regeneration failed: L={regen_loss.total:.3f} "
            f"(target < 0.15)"
        )

    @pytest.mark.asyncio
    async def test_constitution_regeneration(self, galois_compiler):
        """Constitution should have even stricter regenerability."""
        constitution_path = Path("spec/principles/CONSTITUTION.md")
        if not constitution_path.exists():
            pytest.skip("Constitution not found")

        spec = constitution_path.read_text()
        output = await galois_compiler.compile(spec, n_variations=20)

        # Constitution is axiomatic: stricter threshold
        assert output.evidence.galois_loss < 0.10, (
            f"Constitution Galois loss too high: {output.evidence.galois_loss:.3f}"
        )
```

### 3.2 Evidence Sufficiency Law

From the ASHC spec:

```
∀ ASHCOutput O:
  O.is_verified ⟹ len(O.evidence.runs) ≥ 10
                ∧ O.evidence.equivalence_score() ≥ 0.8
                ∧ O.evidence.chaos_report.pass_rate ≥ 0.95  [if chaos run]
                ∧ O.evidence.galois_loss < 0.15  [NEW]
```

---

## Part IV: Chaos Testing (Phase 3)

### 4.1 Chaos Testing Theory

From the ASHC spec:

> If we have N passes that can compose, complexity is O(N!).
> Chaos testing samples this exponential space.

The goal is to verify that implementations remain stable under:
- Combinatorial composition
- Mutation
- Principled variation

### 4.2 Chaos Testing Implementation

```python
# File: impl/claude/protocols/ashc/chaos.py

from __future__ import annotations

import asyncio
import itertools
import random
from dataclasses import dataclass
from typing import Callable, Sequence

from protocols.ashc.evidence import Run
from services.galois.service import GaloisLossService


@dataclass(frozen=True)
class ChaosConfig:
    """Configuration for chaos testing."""

    n_variations: int = 100
    composition_depth: int = 3
    mutation_rate: float = 0.1
    sample_rate: float = 0.01  # Sample 1% of composition space
    timeout_per_test_ms: int = 5000
    principles_to_vary: tuple[str, ...] = ()


@dataclass(frozen=True)
class FailureMode:
    """A discovered failure mode."""

    description: str
    inputs: tuple[str, ...]
    expected: str
    actual: str
    galois_loss: float


@dataclass(frozen=True)
class ChaosReport:
    """Results of chaos testing."""

    variations_tested: int
    compositions_tested: int
    pass_rate: float
    failure_modes: tuple[FailureMode, ...]
    stability_score: float

    @property
    def categorical_complexity(self) -> int:
        """
        Degrees of freedom from composition.

        If we have N passes that can compose, complexity is O(N!).
        """
        from math import factorial
        return factorial(min(self.compositions_tested, 10))  # Cap at 10!


@dataclass
class ChaosEngine:
    """
    Chaos testing engine for ASHC.

    Tests implementations under combinatorial stress.
    """

    galois: GaloisLossService
    verifier: ImplementationVerifier

    async def run_chaos_tests(
        self,
        runs: Sequence[Run],
        config: ChaosConfig,
    ) -> ChaosReport:
        """
        Run chaos tests on implementations.

        Tests:
        1. Composition: Can impls compose correctly?
        2. Mutation: Are impls stable under small changes?
        3. Variation: Do impls handle principle variations?

        Args:
            runs: Passing runs to chaos test
            config: Chaos configuration

        Returns:
            ChaosReport with results
        """
        passing_runs = [r for r in runs if r.test_results.passed]

        if len(passing_runs) < 2:
            return ChaosReport(
                variations_tested=0,
                compositions_tested=0,
                pass_rate=1.0,
                failure_modes=(),
                stability_score=1.0,
            )

        # Run all chaos tests
        composition_results = await self._test_compositions(passing_runs, config)
        mutation_results = await self._test_mutations(passing_runs, config)
        variation_results = await self._test_variations(passing_runs, config)

        # Aggregate results
        all_results = composition_results + mutation_results + variation_results
        passes = sum(1 for r in all_results if r.passed)
        failures = [r for r in all_results if not r.passed]

        # Compute stability score
        stability = self._compute_stability(all_results)

        return ChaosReport(
            variations_tested=len(mutation_results) + len(variation_results),
            compositions_tested=len(composition_results),
            pass_rate=passes / len(all_results) if all_results else 1.0,
            failure_modes=tuple(self._extract_failure_modes(failures)),
            stability_score=stability,
        )

    async def _test_compositions(
        self,
        runs: Sequence[Run],
        config: ChaosConfig,
    ) -> list[ChaosResult]:
        """Test pairwise and higher-order compositions."""
        results = []

        # Sample composition space
        pairs = list(itertools.combinations(runs, 2))
        sample_size = max(1, int(len(pairs) * config.sample_rate))
        sampled_pairs = random.sample(pairs, min(sample_size, len(pairs)))

        for run_a, run_b in sampled_pairs:
            # Compose implementations
            composed = self._compose_impls(run_a.implementation, run_b.implementation)

            # Verify composition
            test_result = await self.verifier.run_tests(composed)

            # Compute composition Galois loss
            loss = await self.galois.compute(composed)

            results.append(ChaosResult(
                kind="composition",
                passed=test_result.passed and loss.total < 0.5,
                galois_loss=loss.total,
                details=f"{run_a.spec_hash[:8]} >> {run_b.spec_hash[:8]}",
            ))

        return results

    async def _test_mutations(
        self,
        runs: Sequence[Run],
        config: ChaosConfig,
    ) -> list[ChaosResult]:
        """Test stability under small mutations."""
        results = []

        for run in runs[:config.n_variations]:
            # Apply random mutation
            mutated = self._mutate_impl(run.implementation, config.mutation_rate)

            # Verify mutated version
            test_result = await self.verifier.run_tests(mutated)

            # Compute mutation stability
            loss = await self.galois.compute(
                f"ORIGINAL:\n{run.implementation}\n\nMUTATED:\n{mutated}"
            )

            # Small mutations should have small loss
            results.append(ChaosResult(
                kind="mutation",
                passed=loss.total < 0.3,  # Mutations shouldn't diverge too much
                galois_loss=loss.total,
                details=f"mutation_rate={config.mutation_rate}",
            ))

        return results

    async def _test_variations(
        self,
        runs: Sequence[Run],
        config: ChaosConfig,
    ) -> list[ChaosResult]:
        """Test behavior under principle variations."""
        results = []

        for principle in config.principles_to_vary:
            for run in runs[:10]:  # Sample
                # Vary implementation by principle
                varied = self._vary_by_principle(run.implementation, principle)

                # Verify
                test_result = await self.verifier.run_tests(varied)

                # Check principle preservation
                loss = await self.galois.compute(varied)

                results.append(ChaosResult(
                    kind="variation",
                    passed=test_result.passed,
                    galois_loss=loss.total,
                    details=f"principle={principle}",
                ))

        return results

    def _compose_impls(self, impl_a: str, impl_b: str) -> str:
        """Compose two implementations."""
        # Simple composition: concatenate with composition marker
        return f"{impl_a}\n\n# COMPOSED WITH\n\n{impl_b}"

    def _mutate_impl(self, impl: str, rate: float) -> str:
        """Apply random mutations to implementation."""
        lines = impl.split("\n")
        mutated = []

        for line in lines:
            if random.random() < rate:
                # Random mutation: swap two characters, add space, etc.
                if len(line) > 2:
                    i = random.randint(0, len(line) - 2)
                    line = line[:i] + line[i+1] + line[i] + line[i+2:]
            mutated.append(line)

        return "\n".join(mutated)

    def _vary_by_principle(self, impl: str, principle: str) -> str:
        """Vary implementation by principle."""
        # Principle-specific variations
        variations = {
            "COMPOSABLE": lambda s: s.replace("def ", "async def "),
            "TASTEFUL": lambda s: s.replace("    ", "  "),  # Indent change
            "JOY_INDUCING": lambda s: s.replace('"""', '"""# Joy! '),
        }

        vary_fn = variations.get(principle, lambda s: s)
        return vary_fn(impl)

    def _compute_stability(self, results: list[ChaosResult]) -> float:
        """Compute overall stability score."""
        if not results:
            return 1.0

        # Stability = 1 / (1 + variance of galois losses)
        losses = [r.galois_loss for r in results]
        mean = sum(losses) / len(losses)
        variance = sum((l - mean) ** 2 for l in losses) / len(losses)

        return 1.0 / (1.0 + variance * 10)

    def _extract_failure_modes(
        self,
        failures: list[ChaosResult],
    ) -> list[FailureMode]:
        """Extract failure modes from failed tests."""
        modes = []

        for failure in failures[:10]:  # Limit to 10
            modes.append(FailureMode(
                description=f"Chaos {failure.kind} failure",
                inputs=(failure.details,),
                expected="pass",
                actual=f"fail (L={failure.galois_loss:.3f})",
                galois_loss=failure.galois_loss,
            ))

        return modes


@dataclass
class ChaosResult:
    """Result of a single chaos test."""

    kind: str  # "composition", "mutation", "variation"
    passed: bool
    galois_loss: float
    details: str
```

---

## Part V: Causal Learning (Phase 4)

### 5.1 Causal Graph Theory

From the ASHC spec:

> Over time, the causal graph becomes a **learned prior** about which nudges matter and how.

The causal graph tracks:
- Which prompt changes (nudges) affect outcomes
- How much each nudge contributes to pass rate
- Stability under different nudges

### 5.2 Causal Learning Implementation

```python
# File: impl/claude/protocols/ashc/causal.py

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class Nudge:
    """A single adjustment to the prompt/spec."""

    location: str
    before: str
    after: str
    reason: str


@dataclass(frozen=True)
class CausalEdge:
    """A tracked relationship between nudge and outcome."""

    nudge: Nudge
    outcome_delta: float  # Change in pass rate
    confidence: float
    runs_observed: int


@dataclass(frozen=True)
class CausalGraph:
    """Graph of nudge → outcome relationships."""

    edges: tuple[CausalEdge, ...]

    def predict_outcome(self, proposed_nudge: Nudge) -> float:
        """
        Predict outcome of a new nudge based on history.

        Uses similarity to past nudges weighted by confidence.
        """
        similar = [
            e for e in self.edges
            if self._similar_nudge(e.nudge, proposed_nudge)
        ]

        if not similar:
            return 0.5  # No data, uncertain

        # Weighted average by confidence
        total_weight = sum(e.confidence for e in similar)
        weighted_sum = sum(e.outcome_delta * e.confidence for e in similar)

        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def _similar_nudge(self, a: Nudge, b: Nudge) -> bool:
        """Check if two nudges are similar."""
        # Same location
        if a.location == b.location:
            return True

        # Similar reason
        a_words = set(a.reason.lower().split())
        b_words = set(b.reason.lower().split())
        overlap = len(a_words & b_words) / max(len(a_words | b_words), 1)
        return overlap > 0.5

    @property
    def stability_score(self) -> float:
        """How stable are outcomes under small nudges?"""
        small_nudges = [
            e for e in self.edges
            if len(e.nudge.after) < 100  # Small changes
        ]

        if not small_nudges:
            return 1.0

        deltas = [e.outcome_delta for e in small_nudges]
        variance = statistics.variance(deltas) if len(deltas) > 1 else 0.0

        return 1.0 / (1.0 + variance)

    @property
    def high_impact_nudges(self) -> list[CausalEdge]:
        """Get nudges with highest positive impact."""
        return sorted(
            [e for e in self.edges if e.outcome_delta > 0.1],
            key=lambda e: e.outcome_delta,
            reverse=True,
        )


@dataclass
class CausalLearner:
    """Learn causal relationships between nudges and outcomes."""

    def learn(
        self,
        runs_without_nudge: Sequence[Run],
        runs_with_nudge: Sequence[Run],
        nudge: Nudge,
    ) -> CausalEdge:
        """
        Learn the causal effect of a nudge.

        Compares outcomes with and without the nudge.
        """
        # Pass rates
        rate_without = self._pass_rate(runs_without_nudge)
        rate_with = self._pass_rate(runs_with_nudge)

        # Delta
        delta = rate_with - rate_without

        # Confidence based on sample size
        n = min(len(runs_without_nudge), len(runs_with_nudge))
        confidence = min(1.0, n / 10)

        return CausalEdge(
            nudge=nudge,
            outcome_delta=delta,
            confidence=confidence,
            runs_observed=n,
        )

    def _pass_rate(self, runs: Sequence[Run]) -> float:
        """Compute pass rate for runs."""
        if not runs:
            return 0.0
        return sum(1 for r in runs if r.test_results.passed) / len(runs)

    def build_graph(
        self,
        run_history: list[tuple[Nudge, list[Run]]],
    ) -> CausalGraph:
        """Build causal graph from run history."""
        edges = []

        # Compare each nudged run set against baseline
        baseline_runs = run_history[0][1] if run_history else []

        for nudge, runs in run_history[1:]:
            edge = self.learn(baseline_runs, runs, nudge)
            edges.append(edge)

        return CausalGraph(edges=tuple(edges))
```

---

## Part VI: Implementation Roadmap

### Phase 1: Evidence Galois (Days 1-2)

| Task | File | Status |
|------|------|--------|
| Update Evidence types | `evidence.py` | Modify |
| Update equivalence_score | `evidence.py` | Modify |
| Galois-enhanced compiler | `compiler.py` | Modify |
| Unit tests | `_tests/test_evidence_galois.py` | New |

### Phase 2: Self-Hosting (Days 3-4)

| Task | File | Status |
|------|------|--------|
| Self-hosting tests | `_tests/test_self_hosting.py` | New |
| Zero Seed regeneration | `_tests/test_self_hosting.py` | New |
| Constitution regeneration | `_tests/test_self_hosting.py` | New |

### Phase 3: Chaos Testing (Days 5-7)

| Task | File | Status |
|------|------|--------|
| ChaosConfig, ChaosReport | `chaos.py` | New |
| ChaosEngine | `chaos.py` | New |
| Chaos tests | `_tests/test_chaos.py` | New |

### Phase 4: Causal Learning (Days 8-10)

| Task | File | Status |
|------|------|--------|
| Nudge, CausalEdge, CausalGraph | `causal.py` | New |
| CausalLearner | `causal.py` | New |
| Causal tests | `_tests/test_causal.py` | New |

---

## Part VII: Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Zero Seed regeneration | L < 0.15 | Self-hosting test |
| Constitution regeneration | L < 0.10 | Self-hosting test |
| Evidence ↔ Galois correlation | ρ > 0.90 | Regression test |
| Chaos stability | > 0.95 | Chaos testing |
| Test count | +100 | Phase 3-4 complete |

---

## Appendix: ASHC Laws Reference

From the ASHC spec:

### Evidence Sufficiency

```
∀ ASHCOutput O:
  O.is_verified ⟹ len(O.evidence.runs) ≥ 10
                ∧ O.evidence.equivalence_score() ≥ 0.8
                ∧ O.evidence.galois_loss < 0.15
```

### Verification Consistency

```
∀ Run R:
  R.test_results = pytest(R.implementation)
  R.type_results = mypy(R.implementation)
  R.lint_results = ruff(R.implementation)
```

### Causal Monotonicity

```
∀ CausalGraph G, Nudge n₁, n₂:
  similarity(n₁, n₂) > 0.9 ⟹ |G.predict(n₁) - G.predict(n₂)| < 0.1
```

---

---

## Appendix: Terminology & Methodology

### "Galois Loss" in ASHC Context

The term "Galois loss" here means **semantic preservation loss under restructuring**:

```
L(spec, impl) = d(spec, C(R(impl)))

Where:
  R = Restructure implementation back to modular form
  C = Canonicalize to spec-like format
  d = Semantic distance metric
```

This is **not** classical Galois theory (adjoint functors between posets). The name honors the inspiration from abstract interpretation's Galois connections.

See: `coherence-synthesis-master.md` Appendix B for full glossary.

### R = 1 - L as Design Axiom

The equation `R_constitutional = 1 - L_galois` is a **design axiom**, not a theorem:
- Both R and L are normalized to [0, 1]
- They are defined as complements by construction
- Empirical validation shows ρ = 0.8346 (Spearman) correlation

### Constitutional Principles in ASHC

| Principle | Type | Role in ASHC |
|-----------|------|--------------|
| **ETHICAL** | **GATE** | Code must pass ≥0.6 floor |
| **COMPOSABLE** | Weight | Code must compose (category laws) |
| **GENERATIVE** | Weight | Spec must regenerate from impl |
| **JOY_INDUCING** | Weight | Code should be elegant |
| **CURATED** | Weight | Avoid bloat in generated code |

---

*"If you grow the tree a thousand times, the pattern of growth IS the proof."*
