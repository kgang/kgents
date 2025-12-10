"""
The Oracle: Metamorphic Judge for Generative Outputs.

Philosophy: Since we cannot know the exact correct output for generative AI,
we validate RELATIONSHIPS between inputs and outputs instead.

Research Basis: Chen et al., "Metamorphic Testing: A Review of Challenges and Opportunities"

Phase 8.1 - Foundation:
- MetamorphicRelation protocol
- SubsetRelation, IdempotencyRelation, PermutationInvarianceRelation
- Oracle for fuzzy truth judgments
- Agent validation via metamorphic relations
"""

from dataclasses import dataclass, field
from typing import Any, Protocol, Callable
import math
import random

# Try relative import first, fall back to absolute
try:
    from ..agents.l.semantic import Embedder, SimpleEmbedder
except ImportError:
    try:
        from agents.l.semantic import Embedder, SimpleEmbedder
    except ImportError:
        # Fallback: define minimal Embedder protocol locally
        class Embedder(Protocol):
            """Protocol for embedding text into vector space."""

            async def embed(self, text: str) -> list[float]: ...

            @property
            def dimension(self) -> int: ...

        class SimpleEmbedder:
            """Minimal TF-IDF embedder fallback."""

            def __init__(self, dimension: int = 128):
                self._dimension = dimension
                self._vocabulary: dict[str, int] = {}

            @property
            def dimension(self) -> int:
                return self._dimension

            async def embed(self, text: str) -> list[float]:
                """Simple hash-based embedding."""
                tokens = text.lower().split()
                vec = [0.0] * self._dimension
                for token in tokens:
                    idx = hash(token) % self._dimension
                    vec[idx] += 1.0
                # Normalize
                norm = math.sqrt(sum(v * v for v in vec))
                if norm > 0:
                    vec = [v / norm for v in vec]
                return vec


# =============================================================================
# Core Types
# =============================================================================


@dataclass
class RelationResult:
    """Result of checking a metamorphic relation."""

    relation: str
    holds: bool
    evidence: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def __repr__(self) -> str:
        status = "HOLDS" if self.holds else "VIOLATED"
        return f"RelationResult({self.relation}={status}, conf={self.confidence:.2f})"


@dataclass
class MetamorphicTest:
    """A test case with two related input/output pairs."""

    relation: str
    input_a: Any
    output_a: Any
    input_b: Any
    output_b: Any


@dataclass
class OracleValidation:
    """Full validation report for an agent."""

    agent_name: str
    tests_run: int
    passed: int
    failed: int
    results: list[RelationResult]
    validity_score: float

    def __repr__(self) -> str:
        return f"OracleValidation({self.agent_name}: {self.passed}/{self.tests_run}, score={self.validity_score:.2%})"


# =============================================================================
# Metamorphic Relations
# =============================================================================


class MetamorphicRelation(Protocol):
    """A relation that must hold between input/output pairs."""

    async def check(
        self,
        input_a: Any,
        output_a: Any,
        input_b: Any,
        output_b: Any,
    ) -> RelationResult:
        """Check if the relation holds."""
        ...


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


@dataclass
class SubsetRelation:
    """Output A should be semantically present in Output AB.

    When we extend input A to A+B, the information from A
    should still be present in the combined output.
    """

    embedder: Embedder
    similarity_threshold: float = 0.7

    async def check(
        self,
        input_a: Any,
        output_a: Any,
        input_ab: Any,
        output_ab: Any,
    ) -> RelationResult:
        """Check if A's output is contained in AB's output."""
        # Embed both outputs
        emb_a = await self.embedder.embed(str(output_a))
        emb_ab = await self.embedder.embed(str(output_ab))

        # Check semantic similarity
        similarity = cosine_similarity(emb_a, emb_ab)

        # Also check lexical overlap
        tokens_a = set(str(output_a).lower().split())
        tokens_ab = set(str(output_ab).lower().split())
        overlap = len(tokens_a & tokens_ab) / len(tokens_a) if tokens_a else 1.0

        holds = similarity > self.similarity_threshold and overlap > 0.5

        return RelationResult(
            relation="subset",
            holds=holds,
            evidence={
                "semantic_similarity": similarity,
                "lexical_overlap": overlap,
            },
            confidence=min(similarity, overlap),
        )


@dataclass
class IdempotencyRelation:
    """f(f(x)) == f(x) for cleaning/formatting operations.

    Running the same transformation twice should not change
    the result further.
    """

    tolerance: float = 0.95  # Allow small variations

    async def check(
        self,
        input_a: Any,
        output_a: Any,
        input_b: Any,  # This is output_a re-fed
        output_b: Any,  # This is f(f(x))
    ) -> RelationResult:
        """Check if applying f twice equals applying f once."""
        # Normalize for comparison
        if isinstance(output_a, str) and isinstance(output_b, str):
            norm_a = " ".join(output_a.split())
            norm_b = " ".join(output_b.split())

            # Check exact match first
            if norm_a == norm_b:
                return RelationResult(
                    relation="idempotency",
                    holds=True,
                    evidence={
                        "match_type": "exact",
                        "first_output": norm_a[:100],
                        "second_output": norm_b[:100],
                    },
                )

            # Check fuzzy match
            common = sum(1 for a, b in zip(norm_a, norm_b) if a == b)
            max_len = max(len(norm_a), len(norm_b))
            similarity = common / max_len if max_len > 0 else 1.0

            holds = similarity >= self.tolerance

            return RelationResult(
                relation="idempotency",
                holds=holds,
                evidence={
                    "match_type": "fuzzy",
                    "similarity": similarity,
                    "first_output": norm_a[:100],
                    "second_output": norm_b[:100],
                },
                confidence=similarity,
            )
        else:
            # Non-string: direct equality
            holds = output_a == output_b
            return RelationResult(
                relation="idempotency",
                holds=holds,
                evidence={
                    "first_output": str(output_a)[:100],
                    "second_output": str(output_b)[:100],
                },
            )


@dataclass
class PermutationInvarianceRelation:
    """Order of input elements shouldn't affect output set.

    For list inputs, changing the order should produce
    equivalent results (set equality or semantic similarity).
    """

    embedder: Embedder
    threshold: float = 0.95

    async def check(
        self,
        input_a: list,
        output_a: Any,
        input_b: list,  # Permuted input_a
        output_b: Any,
    ) -> RelationResult:
        """Check if permuting input produces equivalent output."""
        if isinstance(output_a, list) and isinstance(output_b, list):
            # Set equality for list outputs
            set_a = set(map(str, output_a))
            set_b = set(map(str, output_b))
            holds = set_a == set_b

            return RelationResult(
                relation="permutation_invariance",
                holds=holds,
                evidence={
                    "output_a": str(output_a)[:100],
                    "output_b": str(output_b)[:100],
                    "match_type": "set_equality",
                },
            )
        else:
            # Semantic comparison for non-list outputs
            emb_a = await self.embedder.embed(str(output_a))
            emb_b = await self.embedder.embed(str(output_b))
            similarity = cosine_similarity(emb_a, emb_b)
            holds = similarity > self.threshold

            return RelationResult(
                relation="permutation_invariance",
                holds=holds,
                evidence={
                    "output_a": str(output_a)[:100],
                    "output_b": str(output_b)[:100],
                    "similarity": similarity,
                },
                confidence=similarity,
            )


@dataclass
class MonotonicityRelation:
    """More input should produce proportionally more output.

    For summarizers: longer input -> longer summary (usually).
    For classifiers: less noise -> higher confidence.
    """

    direction: str = "positive"  # "positive" or "negative"
    tolerance: float = 0.8

    async def check(
        self,
        input_a: Any,
        output_a: Any,
        input_b: Any,  # Larger input
        output_b: Any,
    ) -> RelationResult:
        """Check monotonicity relationship."""
        # Get sizes
        size_in_a = len(str(input_a))
        size_in_b = len(str(input_b))
        size_out_a = len(str(output_a))
        size_out_b = len(str(output_b))

        if self.direction == "positive":
            # Larger input -> larger output (proportionally)
            ratio_in = size_in_b / size_in_a if size_in_a > 0 else 1.0
            ratio_out = size_out_b / size_out_a if size_out_a > 0 else 1.0
            holds = ratio_out >= ratio_in * self.tolerance
        else:
            # Larger input -> smaller output
            holds = size_out_b <= size_out_a * (2 - self.tolerance)

        return RelationResult(
            relation="monotonicity",
            holds=holds,
            evidence={
                "input_a_size": size_in_a,
                "input_b_size": size_in_b,
                "output_a_size": size_out_a,
                "output_b_size": size_out_b,
                "direction": self.direction,
            },
        )


@dataclass
class SymmetryRelation:
    """Compare(A, B) = -Compare(B, A) or similar symmetric property."""

    async def check(
        self,
        input_a: tuple[Any, Any],  # (A, B)
        output_a: Any,  # Compare(A, B)
        input_b: tuple[Any, Any],  # (B, A)
        output_b: Any,  # Compare(B, A)
    ) -> RelationResult:
        """Check symmetry relationship."""
        # Try numeric comparison (e.g., distance metrics)
        try:
            val_a = float(output_a)
            val_b = float(output_b)

            # Symmetric: |a| == |b|
            if abs(abs(val_a) - abs(val_b)) < 0.01:
                holds = True
            # Antisymmetric: a == -b
            elif abs(val_a + val_b) < 0.01:
                holds = True
            else:
                holds = False

            return RelationResult(
                relation="symmetry",
                holds=holds,
                evidence={
                    "output_a": val_a,
                    "output_b": val_b,
                    "sum": val_a + val_b,
                },
            )
        except (ValueError, TypeError):
            # Non-numeric: check string equality
            holds = str(output_a) == str(output_b) or str(output_a) == f"-{output_b}"
            return RelationResult(
                relation="symmetry",
                holds=holds,
                evidence={
                    "output_a": str(output_a)[:100],
                    "output_b": str(output_b)[:100],
                },
            )


# =============================================================================
# The Oracle
# =============================================================================


class Oracle:
    """Metamorphic Oracle for judging generative outputs.

    The Oracle doesn't know the "correct" answer, but it can verify
    that outputs satisfy expected relationships.

    Philosophy: Fuzzy truth through metamorphic relations.
    """

    def __init__(self, embedder: Embedder | None = None):
        """Initialize Oracle.

        Args:
            embedder: Embedder for semantic comparisons (defaults to SimpleEmbedder)
        """
        self.embedder = embedder or SimpleEmbedder()

        self.relations: dict[str, MetamorphicRelation] = {
            "subset": SubsetRelation(self.embedder),
            "idempotency": IdempotencyRelation(),
            "permutation": PermutationInvarianceRelation(self.embedder),
            "monotonicity": MonotonicityRelation(),
            "symmetry": SymmetryRelation(),
        }

    async def semantically_equivalent(
        self,
        output_a: Any,
        output_b: Any,
        threshold: float = 0.85,
    ) -> bool:
        """Check if two outputs are semantically equivalent."""
        emb_a = await self.embedder.embed(str(output_a))
        emb_b = await self.embedder.embed(str(output_b))

        similarity = cosine_similarity(emb_a, emb_b)
        return similarity >= threshold

    async def similarity(self, output_a: Any, output_b: Any) -> float:
        """Return similarity score between outputs."""
        emb_a = await self.embedder.embed(str(output_a))
        emb_b = await self.embedder.embed(str(output_b))
        return cosine_similarity(emb_a, emb_b)

    async def check_relation(
        self,
        relation_name: str,
        input_a: Any,
        output_a: Any,
        input_b: Any,
        output_b: Any,
    ) -> RelationResult:
        """Check a specific metamorphic relation."""
        relation = self.relations.get(relation_name)
        if not relation:
            raise ValueError(f"Unknown relation: {relation_name}")

        return await relation.check(input_a, output_a, input_b, output_b)

    async def generate_metamorphic_tests(
        self,
        agent: Any,
        seed_input: Any,
    ) -> list[MetamorphicTest]:
        """Generate metamorphic test cases from a seed input.

        Args:
            agent: Agent to test (must have async invoke method)
            seed_input: Starting input

        Returns:
            List of MetamorphicTest cases
        """
        tests = []

        # Get baseline output
        output_baseline = await agent.invoke(seed_input)

        # Subset test (for string inputs)
        if isinstance(seed_input, str):
            extended_input = (
                seed_input + "\n\nAdditional context: This is extra information."
            )
            output_extended = await agent.invoke(extended_input)

            tests.append(
                MetamorphicTest(
                    relation="subset",
                    input_a=seed_input,
                    output_a=output_baseline,
                    input_b=extended_input,
                    output_b=output_extended,
                )
            )

        # Idempotency test
        output_twice = await agent.invoke(output_baseline)
        tests.append(
            MetamorphicTest(
                relation="idempotency",
                input_a=seed_input,
                output_a=output_baseline,
                input_b=output_baseline,
                output_b=output_twice,
            )
        )

        # Permutation test (if input is list-like)
        if isinstance(seed_input, list) and len(seed_input) > 1:
            permuted = seed_input.copy()
            random.shuffle(permuted)
            output_permuted = await agent.invoke(permuted)

            tests.append(
                MetamorphicTest(
                    relation="permutation",
                    input_a=seed_input,
                    output_a=output_baseline,
                    input_b=permuted,
                    output_b=output_permuted,
                )
            )

        return tests

    async def validate_agent(
        self,
        agent: Any,
        seed_inputs: list[Any],
    ) -> OracleValidation:
        """Full metamorphic validation of an agent.

        Args:
            agent: Agent to validate (must have invoke method and name attr)
            seed_inputs: List of inputs to generate tests from

        Returns:
            Validation report with scores and results
        """
        all_results = []

        for seed in seed_inputs:
            tests = await self.generate_metamorphic_tests(agent, seed)

            for test in tests:
                result = await self.check_relation(
                    test.relation,
                    test.input_a,
                    test.output_a,
                    test.input_b,
                    test.output_b,
                )
                all_results.append(result)

        passed = sum(1 for r in all_results if r.holds)
        agent_name = getattr(agent, "name", type(agent).__name__)

        return OracleValidation(
            agent_name=agent_name,
            tests_run=len(all_results),
            passed=passed,
            failed=len(all_results) - passed,
            results=all_results,
            validity_score=passed / len(all_results) if all_results else 1.0,
        )


# =============================================================================
# Custom Relation Builder
# =============================================================================


def custom_relation(
    name: str,
    check_fn: Callable[[Any, Any, Any, Any], tuple[bool, dict]],
) -> MetamorphicRelation:
    """Create a custom metamorphic relation.

    Args:
        name: Name of the relation
        check_fn: Function (input_a, output_a, input_b, output_b) -> (holds, evidence)

    Returns:
        MetamorphicRelation instance
    """

    class CustomRelation:
        async def check(
            self,
            input_a: Any,
            output_a: Any,
            input_b: Any,
            output_b: Any,
        ) -> RelationResult:
            holds, evidence = check_fn(input_a, output_a, input_b, output_b)
            return RelationResult(relation=name, holds=holds, evidence=evidence)

    return CustomRelation()


# =============================================================================
# Convenience Functions
# =============================================================================


async def quick_validate(
    agent: Any,
    inputs: list[Any],
    embedder: Embedder | None = None,
) -> float:
    """Quick validation returning just the validity score.

    Args:
        agent: Agent to validate
        inputs: Test inputs
        embedder: Optional embedder

    Returns:
        Validity score (0.0 to 1.0)
    """
    oracle = Oracle(embedder)
    result = await oracle.validate_agent(agent, inputs)
    return result.validity_score


def format_validation_report(validation: OracleValidation) -> str:
    """Format validation report for display.

    Returns:
        Formatted string report
    """
    lines = [
        "=" * 60,
        "              ORACLE VALIDATION REPORT                  ",
        "=" * 60,
        f" Agent: {validation.agent_name}",
        f" Tests Run: {validation.tests_run}",
        f" Passed: {validation.passed}",
        f" Failed: {validation.failed}",
        f" Validity Score: {validation.validity_score:.1%}",
        "-" * 60,
        " RESULTS BY RELATION:",
    ]

    # Group by relation
    by_relation: dict[str, list[RelationResult]] = {}
    for r in validation.results:
        by_relation.setdefault(r.relation, []).append(r)

    for relation, results in by_relation.items():
        passed = sum(1 for r in results if r.holds)
        total = len(results)
        pct = passed / total if total > 0 else 1.0
        status = "PASS" if pct >= 0.8 else "FAIL"
        lines.append(f"   {relation}: {passed}/{total} ({pct:.0%}) [{status}]")

    lines.append("=" * 60)

    return "\n".join(lines)
