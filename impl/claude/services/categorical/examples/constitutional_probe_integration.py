"""
Constitutional Probe Integration Example

Demonstrates how to wire the constitutional reward system into
TruthFunctor probes for a complete constitutional evaluation pipeline.

This shows:
1. Running categorical probes (monad, sheaf)
2. Converting probe results to constitutional evaluations
3. Aggregating constitutional scores
4. Using as DP reward function

Usage:
    python -m services.categorical.examples.constitutional_probe_integration
"""

import asyncio
import logging
from dataclasses import dataclass

from services.categorical import (
    CategoricalProbeRunner,
    Constitution,
    ConstitutionalEvaluation,
    Principle,
    ProbeRewards,
    compute_galois_loss,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Mock LLM for Example
# =============================================================================


class MockLLM:
    """Mock LLM for demonstration purposes."""

    async def generate(
        self,
        system: str,
        user: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ):
        """Generate a mock response."""
        # Simulate deterministic math problem solving
        if "2+2" in user or "2 + 2" in user:
            return type("Response", (), {"text": "The answer is 4."})()

        # Simulate claim extraction
        if "extract all factual claims" in user.lower():
            return type(
                "Response",
                (),
                {
                    "text": """CLAIM: 2 + 2 equals 4
CONTEXT: arithmetic addition

CLAIM: The result is a positive integer
CONTEXT: properties of the answer"""
                },
            )()

        # Simulate contradiction checking
        if "do these two claims contradict" in user.lower():
            return type("Response", (), {"text": "NO. Both claims are consistent."})()

        # Simulate restructuring for Galois loss
        if "restructure" in user.lower():
            return type(
                "Response",
                (),
                {
                    "text": """Component 1: Mathematical operation (2+2)
Component 2: Result validation (equals 4)
Component 3: Type checking (positive integer)"""
                },
            )()

        # Simulate reconstitution for Galois loss
        if "reconstitute" in user.lower():
            return type("Response", (), {"text": "The answer is 4."})()

        return type("Response", (), {"text": "I don't know."})()


# =============================================================================
# Constitutional Probe Runner (Integrated)
# =============================================================================


@dataclass
class ConstitutionalProbeResult:
    """
    Result from running probes with constitutional evaluation.

    Combines categorical probe results with constitutional scores.
    """

    problem: str
    monad_score: float
    coherence_score: float
    constitutional_eval: ConstitutionalEvaluation
    constitutional_total: float

    def __str__(self):
        return f"""
Constitutional Probe Result
==========================
Problem: {self.problem}

Categorical Scores:
  Monad:     {self.monad_score:.2f}
  Coherence: {self.coherence_score:.2f}

Constitutional Evaluation:
  Total:     {self.constitutional_total:.2f}
  Min:       {self.constitutional_eval.min_score:.2f}
  Max:       {self.constitutional_eval.max_score:.2f}

By Principle:
  ETHICAL:       {self.constitutional_eval.by_principle.get(Principle.ETHICAL, 0):.2f}
  COMPOSABLE:    {self.constitutional_eval.by_principle.get(Principle.COMPOSABLE, 0):.2f}
  JOY_INDUCING:  {self.constitutional_eval.by_principle.get(Principle.JOY_INDUCING, 0):.2f}
  TASTEFUL:      {self.constitutional_eval.by_principle.get(Principle.TASTEFUL, 0):.2f}
  CURATED:       {self.constitutional_eval.by_principle.get(Principle.CURATED, 0):.2f}
  HETERARCHICAL: {self.constitutional_eval.by_principle.get(Principle.HETERARCHICAL, 0):.2f}
  GENERATIVE:    {self.constitutional_eval.by_principle.get(Principle.GENERATIVE, 0):.2f}
"""


async def run_constitutional_probes(
    problem: str,
    llm,
    trace: str = "",
) -> ConstitutionalProbeResult:
    """
    Run categorical probes with constitutional evaluation.

    This is the integration point: categorical probes → constitutional scores.

    Args:
        problem: The problem to test
        llm: LLM client
        trace: Optional reasoning trace

    Returns:
        ConstitutionalProbeResult with both categorical and constitutional scores
    """
    # Step 1: Run categorical probes
    runner = CategoricalProbeRunner(llm, emit_marks=False)

    probe_results = await runner.probe(
        problem=problem,
        trace=trace or f"Let me solve {problem}. The answer is what I computed.",
        n_samples=3,  # Fewer samples for demo
        run_monad=True,
        run_sheaf=bool(trace),
    )

    # Step 2: Convert to constitutional evaluation
    # Use ProbeRewards to bridge categorical → constitutional

    monad_eval = ProbeRewards.monad_probe_reward(
        state_before=problem,
        action="categorical_probe",
        state_after=probe_results,
        identity_satisfied=(probe_results.monad_score > 0.8),
        associativity_satisfied=(probe_results.monad_score > 0.8),
    )

    if probe_results.coherence_result:
        sheaf_eval = ProbeRewards.sheaf_probe_reward(
            state_before=problem,
            action="categorical_probe",
            state_after=probe_results,
            coherence_score=probe_results.coherence_score,
            violation_count=len(probe_results.coherence_result.violations),
        )

        # Combine monad and sheaf evaluations
        combined_scores = monad_eval.scores + sheaf_eval.scores
        constitutional_eval = ConstitutionalEvaluation(scores=combined_scores)
    else:
        constitutional_eval = monad_eval

    return ConstitutionalProbeResult(
        problem=problem,
        monad_score=probe_results.monad_score,
        coherence_score=probe_results.coherence_score,
        constitutional_eval=constitutional_eval,
        constitutional_total=constitutional_eval.weighted_total,
    )


# =============================================================================
# DP Integration Example
# =============================================================================


class ConstitutionalDPSolver:
    """
    Example DP solver using constitutional reward function.

    This demonstrates how to use Constitution.evaluate as the reward
    function in a dynamic programming problem.
    """

    def __init__(self, llm):
        self.llm = llm

    async def solve_with_constitutional_reward(self, initial_problem: str):
        """
        Solve a problem using constitutional rewards to guide search.

        This is a simplified example—a real DP solver would explore
        the full state space. Here we just show the reward calculation.
        """
        logger.info(f"Solving: {initial_problem}")

        # State: current problem formulation
        state = initial_problem

        # Action: apply some transformation
        action = "simplify_problem"

        # Next state: simplified problem
        next_state = "2 + 2"

        # CONSTITUTIONAL REWARD: This is the key integration
        reward_eval = Constitution.evaluate(
            state_before=state,
            action=action,
            state_after=next_state,
            context={
                "deterministic": True,  # Simplification is deterministic
                "satisfies_identity": True,  # Composition law satisfied
                "has_spec": True,  # Simplification rule is specified
                "regenerability_score": 0.9,  # Can regenerate from spec
            },
        )

        logger.info(f"Action: {action}")
        logger.info(f"Constitutional reward: {reward_eval.weighted_total:.2f}")
        logger.info(f"ETHICAL: {reward_eval.by_principle[Principle.ETHICAL]:.2f}")
        logger.info(f"COMPOSABLE: {reward_eval.by_principle[Principle.COMPOSABLE]:.2f}")

        # In a real DP solver, we'd use this reward to update value function
        # and choose the best action via Bellman equation
        return reward_eval


# =============================================================================
# Galois Loss Example
# =============================================================================


async def test_regenerability(output: str, llm) -> float:
    """
    Test regenerability using Galois loss.

    This measures the GENERATIVE principle quantitatively.
    """
    logger.info("Testing regenerability...")

    loss = await compute_galois_loss(output, llm)

    logger.info(f"Galois loss: {loss:.3f}")
    logger.info(f"Regenerability score: {1.0 - loss:.3f}")

    return 1.0 - loss  # Convert loss to score


# =============================================================================
# Main Example
# =============================================================================


async def main():
    """Run the complete constitutional probe integration example."""
    logger.info("=" * 60)
    logger.info("Constitutional Probe Integration Example")
    logger.info("=" * 60)

    llm = MockLLM()

    # Example 1: Categorical probes with constitutional evaluation
    logger.info("\n--- Example 1: Categorical Probes ---")
    result = await run_constitutional_probes(
        problem="What is 2 + 2?",
        llm=llm,
        trace="Let me solve this. 2 + 2 equals 4. The result is a positive integer.",
    )
    print(result)

    # Example 2: DP solver with constitutional rewards
    logger.info("\n--- Example 2: DP Solver with Constitutional Rewards ---")
    dp_solver = ConstitutionalDPSolver(llm)
    reward = await dp_solver.solve_with_constitutional_reward("What is two plus two?")

    # Example 3: Galois loss for regenerability
    logger.info("\n--- Example 3: Galois Loss (Regenerability) ---")
    regenerability = await test_regenerability("The answer is 4.", llm)

    # Example 4: Direct constitutional evaluation
    logger.info("\n--- Example 4: Direct Constitutional Evaluation ---")
    eval = Constitution.evaluate(
        state_before="problem",
        action="solve_elegantly",
        state_after="solution",
        context={
            "joyful": True,
            "joy_evidence": "Elegant one-liner solution",
            "deterministic": True,
            "satisfies_identity": True,
            "satisfies_associativity": True,
            "has_spec": True,
            "regenerability_score": 0.95,
        },
    )

    logger.info("Direct evaluation results:")
    for principle, score in eval.by_principle.items():
        logger.info(f"  {principle.name}: {score:.2f}")
    logger.info(f"Total: {eval.weighted_total:.2f}")

    logger.info("\n" + "=" * 60)
    logger.info("Example complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
