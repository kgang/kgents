"""
Soulful Advisor: Agents with Personality.

The @Soulful capability connects your agent to K-gent (Kent simulacra).
This enables persona-aware responses that feel consistent and human.

Key insight:
    K-gent is NOT a chatbot. It's a Governance Functor that ensures
    responses align with declared eigenvectors (personality dimensions).

Run:
    python -m agents.examples.soulful_advisor
"""

import asyncio
from dataclasses import dataclass

from agents.a import Capability, Kappa, get_halo
from bootstrap.types import Agent


@dataclass
class Advice:
    """Advice with reasoning."""

    suggestion: str
    reasoning: str
    confidence: float


@Capability.Soulful(persona="Kent")
class AdvisorAgent(Agent[str, Advice]):
    """
    An advisor that gives persona-aligned advice.

    Type: Agent[str, Advice]
    Input: A question or situation
    Output: Advice with reasoning

    The @Soulful decorator declares that this agent should
    consult K-gent for persona consistency.

    Note: Full persona integration happens when compiled through
    LocalProjector with an active K-gent instance.
    """

    @property
    def name(self) -> str:
        return "advisor"

    async def invoke(self, input: str) -> Advice:
        """Give advice aligned with persona."""
        # In production, this would consult K-gent for eigenvector alignment
        # Here we demonstrate the pattern

        # Simple keyword-based advice (placeholder for LLM integration)
        if "code" in input.lower():
            return Advice(
                suggestion="Start with the simplest thing that could work.",
                reasoning="Complexity is debt. Simplicity compounds.",
                confidence=0.9,
            )
        elif "career" in input.lower():
            return Advice(
                suggestion="Follow your curiosity, not the crowd.",
                reasoning="Joy-inducing > merely functional. This applies to careers too.",
                confidence=0.85,
            )
        else:
            return Advice(
                suggestion="What would make you smile when you look back?",
                reasoning="The mirror test: does this feel like you on your best day?",
                confidence=0.7,
            )


class FullStackAdvisor(Kappa[str, Advice]):
    """
    Alternative: Using the Kappa archetype.

    Kappa = Stateful + Soulful + Observable + Streamable (full stack).
    The "batteries included" archetype for production agents.
    """

    @property
    def name(self) -> str:
        return "kappa-advisor"

    async def invoke(self, input: str) -> Advice:
        return Advice(
            suggestion="Trust the process.",
            reasoning="Kappa agents have all capabilities. Use them wisely.",
            confidence=0.95,
        )


async def main() -> None:
    """Demonstrate soulful agents."""
    advisor = AdvisorAgent()

    # Get advice on different topics
    code_advice = await advisor.invoke("How should I approach this code review?")
    career_advice = await advisor.invoke("Should I change my career?")
    general_advice = await advisor.invoke("I feel stuck.")

    print("Code advice:", code_advice.suggestion)
    print("Career advice:", career_advice.suggestion)
    print("General advice:", general_advice.suggestion)

    # Inspect Halos
    print("\n--- Halos ---")
    advisor_halo = get_halo(AdvisorAgent)
    kappa_halo = get_halo(FullStackAdvisor)

    print(f"Advisor caps: {[type(c).__name__ for c in advisor_halo]}")
    print(f"Kappa caps: {[type(c).__name__ for c in kappa_halo]}")


if __name__ == "__main__":
    asyncio.run(main())
