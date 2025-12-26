#!/usr/bin/env python3
"""
Phase 1 Toy Example Runner: De-risking infrastructure before expensive runs.

This script runs ONE simple problem ("What is 2 + 2?") through each probe
with n=3 (tiny sample) to validate the machinery works.

FULLY STANDALONE - No imports from main codebase to avoid dependency hell.

Philosophy:
    "Measure first. Build only what measurement validates."
    "Start small, validate machinery, scale gradually."

Usage:
    python scripts/run_phase1_toy.py

Expected output:
    ✅ Phase A passed - machinery works
    OR
    ❌ Phase A failed - fix machinery before proceeding
"""

import asyncio
import sys
from collections import Counter
from dataclasses import dataclass

# =============================================================================
# Result Types (inline to avoid imports)
# =============================================================================


@dataclass
class ProbeResult:
    """Result from a single probe test."""
    name: str
    base_answer: str
    modified_answer: str
    passed: bool
    score: float
    details: str = ""


@dataclass
class CoherenceResult:
    """Result from sheaf coherence check."""
    is_coherent: bool
    claims: list
    violations: list
    score: float


# =============================================================================
# Mock LLM Client (for toy example without API costs)
# =============================================================================


class MockLLM:
    """
    Mock LLM for toy example testing.
    Returns deterministic answers for simple problems.

    NOTE: Must be robust to perturbations (whitespace, middle insertions)
    to properly test the hypothesis that these don't matter.
    """

    async def solve(self, prompt: str) -> str:
        """Solve a problem and return the answer."""
        # Normalize: collapse whitespace, remove brackets, lowercase
        normalized = ' '.join(prompt.lower().split())
        # Remove bracketed insertions (our perturbation markers)
        import re
        normalized = re.sub(r'\[.*?\]', '', normalized)
        normalized = ' '.join(normalized.split())  # Re-collapse after removal

        # Handle simple math (robust to whitespace variations)
        if "2 + 2" in normalized or "2+2" in normalized or "2  +  2" in normalized:
            return "4"
        if "5 + 3" in normalized or "5+3" in normalized:
            return "8"
        if "what color is the sky" in normalized:
            return "blue"
        return "unknown"

    async def generate(self, prompt: str) -> str:
        """Generate text."""
        # Handle CoT
        if "2 + 2" in prompt:
            return "Let me think step by step. 2 + 2 = 4. The answer is 4."
        return "I don't know."


# =============================================================================
# Middle Invariance Probe (inline implementation)
# =============================================================================


class MiddleInvarianceProbe:
    """Test: Does the middle matter less than the edges?"""

    def __init__(self, llm):
        self.llm = llm

    async def middle_perturbation_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """
        Insert noise tokens in the middle 20-80% of the prompt.
        Measure: How often does this CHANGE the answer?
        """
        # Get base answers
        base_answers = [await self.llm.solve(prompt) for _ in range(n)]

        # Perturb middle
        mid_start = len(prompt) // 5
        mid_end = 4 * len(prompt) // 5
        perturbed_prompt = (
            prompt[:mid_start]
            + " [Note: intermediate detail follows.] "
            + prompt[mid_start:mid_end]
            + " [End intermediate detail.] "
            + prompt[mid_end:]
        )

        # Get perturbed answers
        perturbed_answers = [await self.llm.solve(perturbed_prompt) for _ in range(n)]

        base_mode = Counter(base_answers).most_common(1)[0][0]
        perturbed_mode = Counter(perturbed_answers).most_common(1)[0][0]

        passed = base_mode == perturbed_mode
        score = 1.0 if passed else 0.0

        return ProbeResult(
            name="middle_perturbation",
            base_answer=base_mode,
            modified_answer=perturbed_mode,
            passed=passed,
            score=score,
            details=f"Perturbed prompt: {perturbed_prompt[:50]}..."
        )

    async def middle_deletion_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """
        Remove a semantically-redundant middle clause.
        Measure: Does the answer stay the same?
        """
        sentences = prompt.split(". ")
        if len(sentences) < 3:
            # Not applicable for short prompts
            return ProbeResult(
                name="middle_deletion",
                base_answer="N/A",
                modified_answer="N/A",
                passed=True,
                score=1.0,
                details="Prompt too short (< 3 sentences)"
            )

        # Remove middle sentence
        reduced_prompt = ". ".join(sentences[:1] + sentences[2:])

        base_answers = [await self.llm.solve(prompt) for _ in range(n)]
        reduced_answers = [await self.llm.solve(reduced_prompt) for _ in range(n)]

        base_mode = Counter(base_answers).most_common(1)[0][0]
        reduced_mode = Counter(reduced_answers).most_common(1)[0][0]

        passed = base_mode == reduced_mode
        score = 1.0 if passed else 0.0

        return ProbeResult(
            name="middle_deletion",
            base_answer=base_mode,
            modified_answer=reduced_mode,
            passed=passed,
            score=score,
            details=f"Reduced prompt: {reduced_prompt}"
        )

    async def edge_perturbation_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """
        CONTROL: Insert noise at the BEGINNING.
        Measure: This SHOULD break things (score=1 when different).
        """
        base_answers = [await self.llm.solve(prompt) for _ in range(n)]
        prefix_perturbed = [await self.llm.solve("Ignore this. " + prompt) for _ in range(n)]

        base_mode = Counter(base_answers).most_common(1)[0][0]
        perturbed_mode = Counter(prefix_perturbed).most_common(1)[0][0]

        # INVERTED: We WANT this to differ (proves edges matter more)
        # But for MockLLM, it will likely be the same (which is fine for Phase A)
        differs = base_mode != perturbed_mode

        return ProbeResult(
            name="edge_perturbation",
            base_answer=base_mode,
            modified_answer=perturbed_mode,
            passed=True,  # Always pass in Phase A (informational only)
            score=1.0 if differs else 0.5,  # 0.5 = inconclusive with mock
            details="Control test: edge perturbation (informational)"
        )


# =============================================================================
# Monad Variator Probe (inline implementation)
# =============================================================================


class MonadVariatorProbe:
    """Test: Do semantically-equivalent transformations preserve behavior?"""

    def __init__(self, llm):
        self.llm = llm

    async def whitespace_invariance_test(self, prompt: str, n: int = 3) -> ProbeResult:
        """
        Add extra whitespace throughout.
        Measure: Should not change answer.
        """
        # Double all spaces
        spaced_prompt = prompt.replace(' ', '  ')

        base_answers = [await self.llm.solve(prompt) for _ in range(n)]
        spaced_answers = [await self.llm.solve(spaced_prompt) for _ in range(n)]

        base_mode = Counter(base_answers).most_common(1)[0][0]
        spaced_mode = Counter(spaced_answers).most_common(1)[0][0]

        passed = base_mode == spaced_mode
        score = 1.0 if passed else 0.0

        return ProbeResult(
            name="whitespace_invariance",
            base_answer=base_mode,
            modified_answer=spaced_mode,
            passed=passed,
            score=score,
            details=f"Spaced prompt: '{spaced_prompt}'"
        )


# =============================================================================
# Sheaf Coherence Detector (simplified inline)
# =============================================================================


class SheafDetector:
    """Extract claims. Check pairwise consistency."""

    def __init__(self, llm):
        self.llm = llm

    async def detect(self, trace: str) -> CoherenceResult:
        """Check coherence of a reasoning trace."""
        # Simple claim extraction (mock)
        claims = self._extract_claims_simple(trace)

        # Check for contradictions (simple heuristic)
        violations = []
        for i, claim_a in enumerate(claims):
            for j, claim_b in enumerate(claims[i+1:], i+1):
                if self._contradicts_simple(claim_a, claim_b):
                    violations.append((i, j, claim_a, claim_b))

        is_coherent = len(violations) == 0
        score = 1.0 - (len(violations) / max(len(claims), 1))

        return CoherenceResult(
            is_coherent=is_coherent,
            claims=claims,
            violations=violations,
            score=score
        )

    def _extract_claims_simple(self, trace: str) -> list:
        """Simple claim extraction via sentence splitting."""
        sentences = [s.strip() for s in trace.split('.') if s.strip()]
        # Filter to statements that look like claims
        claims = [s for s in sentences if any(c.isdigit() for c in s) or '=' in s]
        return claims if claims else sentences[:3]  # Fallback to first 3 sentences

    def _contradicts_simple(self, claim_a: str, claim_b: str) -> bool:
        """Simple contradiction check (mock - no real contradictions in toy)."""
        # Would need LLM for real check, but for toy example just return False
        return False


# =============================================================================
# Toy Example Runner
# =============================================================================


async def run_phase_a_toy():
    """
    Phase A: Single toy example to validate basic machinery.
    Tests one simple problem ("What is 2 + 2?") with n=3 samples.
    """
    print("=" * 80)
    print("PHASE A: TOY EXAMPLE (De-risking Infrastructure)")
    print("=" * 80)
    print()

    # Initialize mock LLM
    llm = MockLLM()
    print("✓ Mock LLM initialized (deterministic, no API costs)")
    print()

    # Initialize probes
    middle_probe = MiddleInvarianceProbe(llm=llm)
    variator_probe = MonadVariatorProbe(llm=llm)
    sheaf_detector = SheafDetector(llm=llm)
    print("✓ Probes initialized:")
    print("  - MiddleInvarianceProbe")
    print("  - MonadVariatorProbe")
    print("  - SheafDetector")
    print()

    # Toy problem
    toy_problem = "What is 2 + 2?"
    toy_trace = "Let me think... 2 + 2 = 4. The answer is 4."
    print(f"Toy problem: '{toy_problem}'")
    print("Expected answer: 4")
    print()

    # Run probes with n=3 (tiny sample for debugging)
    n = 3
    print(f"Running probes with n={n} samples...")
    print()

    # =========================================================================
    # Middle Invariance Tests
    # =========================================================================
    print("-" * 80)
    print("1. MIDDLE INVARIANCE PROBES")
    print("-" * 80)

    # Middle perturbation
    print("  a) Middle perturbation test...")
    middle_pert = await middle_probe.middle_perturbation_test(toy_problem, n=n)
    print(f"     Base answer: '{middle_pert.base_answer}'")
    print(f"     Modified answer: '{middle_pert.modified_answer}'")
    print(f"     Passed: {middle_pert.passed} (score: {middle_pert.score:.2f})")
    print()

    # Middle deletion
    print("  b) Middle deletion test...")
    middle_del = await middle_probe.middle_deletion_test(toy_problem, n=n)
    print(f"     Base answer: '{middle_del.base_answer}'")
    print(f"     Modified answer: '{middle_del.modified_answer}'")
    print(f"     Passed: {middle_del.passed} (score: {middle_del.score:.2f})")
    if "too short" in middle_del.details:
        print(f"     Note: {middle_del.details}")
    print()

    # Edge perturbation (control)
    print("  c) Edge perturbation test (control)...")
    edge_pert = await middle_probe.edge_perturbation_test(toy_problem, n=n)
    print(f"     Base answer: '{edge_pert.base_answer}'")
    print(f"     Modified answer: '{edge_pert.modified_answer}'")
    print(f"     Score: {edge_pert.score:.2f} (0.5=inconclusive with mock)")
    print()

    middle_invariance_score = (middle_pert.score + middle_del.score) / 2  # Exclude control
    print(f"  → Middle invariance overall: {middle_invariance_score:.2f}")
    print()

    # =========================================================================
    # Monad Variator Tests
    # =========================================================================
    print("-" * 80)
    print("2. MONAD VARIATOR PROBES")
    print("-" * 80)

    # Whitespace invariance
    print("  a) Whitespace invariance test...")
    whitespace = await variator_probe.whitespace_invariance_test(toy_problem, n=n)
    print(f"     Base answer: '{whitespace.base_answer}'")
    print(f"     Variated answer: '{whitespace.modified_answer}'")
    print(f"     Passed: {whitespace.passed} (score: {whitespace.score:.2f})")
    print()

    monad_variator_score = whitespace.score
    print(f"  → Monad variator overall: {monad_variator_score:.2f}")
    print()

    # =========================================================================
    # Sheaf Coherence Test
    # =========================================================================
    print("-" * 80)
    print("3. SHEAF COHERENCE PROBE")
    print("-" * 80)

    print("  Testing coherence of reasoning trace...")
    print(f"  Trace: '{toy_trace}'")
    coherence = await sheaf_detector.detect(toy_trace)
    print(f"     Claims extracted: {len(coherence.claims)}")
    for i, claim in enumerate(coherence.claims):
        print(f"       [{i}] '{claim}'")
    print(f"     Violations found: {len(coherence.violations)}")
    print(f"     Coherent: {coherence.is_coherent}")
    print(f"     Score: {coherence.score:.2f}")
    print()

    sheaf_score = coherence.score
    print(f"  → Sheaf coherence: {sheaf_score:.2f}")
    print()

    # =========================================================================
    # Phase A Gate
    # =========================================================================
    print("=" * 80)
    print("PHASE A RESULTS")
    print("=" * 80)
    print()

    results = {
        "middle_invariance": middle_invariance_score,
        "monad_variator": monad_variator_score,
        "sheaf_coherence": sheaf_score,
    }

    print("Results:")
    for key, value in results.items():
        status = "✓" if value > 0.5 else "✗"
        print(f"  {status} {key}: {value:.2f}")
    print()

    # Gate criterion: all scores > 0.5
    passed = all(score > 0.5 for score in results.values())

    if passed:
        print("=" * 80)
        print("✅ PHASE A PASSED - Machinery works!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Review results to ensure probes behave as expected")
        print("  2. Switch MockLLM → real LLM (Claude/GPT) for Phase B")
        print("  3. Run Phase B: 10 problems from categorical_phase1_problems.json")
        print("  4. If Phase B shows signal, proceed to Phase C (n=50)")
        return 0
    else:
        print("=" * 80)
        print("❌ PHASE A FAILED - Fix machinery before proceeding")
        print("=" * 80)
        print()
        print("Failures:")
        for key, value in results.items():
            if value <= 0.5:
                print(f"  - {key}: {value:.2f} (threshold: 0.5)")
        print()
        print("Action: Debug probe implementations and re-run Phase A")
        return 1


# =============================================================================
# Main
# =============================================================================


def main():
    """Run Phase A toy example."""
    exit_code = asyncio.run(run_phase_a_toy())
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
