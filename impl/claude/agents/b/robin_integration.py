"""
Robin: Scientific Companion Agent

A personalized scientific dialogue agent that composes:
- K-gent (personalization layer)
- HypothesisEngine (scientific reasoning)
- HegelAgent (dialectic refinement)

Robin is NOT a simple composition (types don't align for >>).
Instead, it's an orchestrating agent that:
1. Personalizes scientific queries through K-gent
2. Generates falsifiable hypotheses
3. Applies dialectic synthesis to surface tensions

The "composition" is at the conceptual level:
    Robin = Personalization → Hypothesis Generation → Dialectic Refinement
"""

from dataclasses import dataclass, field
from typing import Optional

from agents.a.skeleton import AgentBehavior, AgentIdentity, AgentInterface, AgentMeta
from agents.h import (
    DialecticInput,
    DialecticOutput,
    HegelAgent,
)
from agents.k import (
    DialogueInput,
    DialogueMode,
    DialogueOutput,
    KgentAgent,
    PersonaQuery,
    PersonaQueryAgent,
    PersonaResponse,
    PersonaSeed,
    PersonaState,
)  # kgent, query_persona intentionally not imported (available via agents.k)
from bootstrap.types import Agent
from runtime.base import AgentResult, Runtime

from .hypothesis import (
    HypothesisEngine,
    HypothesisInput,
    HypothesisOutput,
)
from .hypothesis_parser import Hypothesis


@dataclass
class RobinInput:
    """
    Input for Robin scientific companion.

    Combines a scientific query with optional personalization.
    """

    query: str  # The scientific question or topic
    observations: list[str] = field(default_factory=list)  # Supporting observations
    domain: str = "general science"  # Scientific domain
    dialogue_mode: DialogueMode = DialogueMode.EXPLORE  # How K-gent engages
    constraints: list[str] = field(default_factory=list)  # Known constraints
    apply_dialectic: bool = True  # Whether to dialectically refine


@dataclass
class RobinOutput:
    """
    Robin's comprehensive scientific response.

    Includes personalization, hypotheses, and dialectic analysis.
    """

    # From K-gent
    personalization: PersonaResponse
    kgent_reflection: DialogueOutput

    # From HypothesisEngine
    hypotheses: list[Hypothesis]
    reasoning_chain: list[str]
    suggested_tests: list[str]

    # From HegelAgent (if apply_dialectic)
    dialectic: Optional[DialecticOutput] = None

    # Robin's synthesis
    synthesis_narrative: str = ""  # Combines all three perspectives
    next_questions: list[str] = field(default_factory=list)  # What to explore next

    def __str__(self) -> str:
        lines = ["=" * 60, "ROBIN SCIENTIFIC COMPANION OUTPUT", "=" * 60]

        # Personalization
        lines.append("\n📌 PERSONALIZATION:")
        lines.append(
            f"  Style hints: {', '.join(self.personalization.suggested_style)}"
        )
        lines.append(f"  K-gent reflection: {self.kgent_reflection.response[:200]}...")

        # Hypotheses
        lines.append(f"\n🔬 HYPOTHESES ({len(self.hypotheses)}):")
        for i, h in enumerate(self.hypotheses, 1):
            lines.append(f"\n  {i}. {h.statement}")
            lines.append(
                f"     Confidence: {h.confidence:.0%} | Novelty: {h.novelty.value}"
            )
            lines.append("     Falsifiable by:")
            for f in h.falsifiable_by[:2]:
                lines.append(f"       - {f}")

        # Reasoning
        lines.append("\n📋 REASONING CHAIN:")
        for i, r in enumerate(self.reasoning_chain[:5], 1):
            lines.append(f"  {i}. {r}")

        # Dialectic
        if self.dialectic:
            lines.append("\n🔄 DIALECTIC ANALYSIS:")
            if self.dialectic.productive_tension:
                lines.append("  ⚡ Productive tension held (no premature synthesis)")
            if self.dialectic.synthesis:
                lines.append(f"  Synthesis: {self.dialectic.synthesis}")
            lines.append(f"  Notes: {self.dialectic.sublation_notes}")

        # Synthesis
        if self.synthesis_narrative:
            lines.append("\n✨ SYNTHESIS:")
            lines.append(f"  {self.synthesis_narrative}")

        # Next questions
        if self.next_questions:
            lines.append("\n❓ NEXT QUESTIONS:")
            for q in self.next_questions:
                lines.append(f"  - {q}")

        return "\n".join(lines)


from .robin_helpers import generate_fallback_hypotheses  # noqa: E402
from .robin_morphisms_integration import (  # noqa: E402
    NarrativeSynthesizer,
    NextQuestionGenerator,
    QuestionInput,
    SynthesisInput,
)


class RobinAgent(Agent[RobinInput, RobinOutput]):
    """
    Robin: Personalized Scientific Companion.

    Orchestrates K-gent, HypothesisEngine, and HegelAgent to provide
    a dialogic scientific experience tailored to the user's thinking style.

    Robin is dialogic - it responds to queries with:
    - Personalized framing (via K-gent)
    - Falsifiable hypotheses (via HypothesisEngine)
    - Dialectic refinement (via HegelAgent)

    NOTE: Robin requires a runtime for the HypothesisEngine component.
    Use RobinAgent.with_runtime(runtime) or pass runtime to invoke.
    """

    meta = AgentMeta(
        identity=AgentIdentity(
            name="Robin",
            genus="b",
            version="0.1.0",
            purpose="Personalized scientific companion for dialogic inquiry",
        ),
        interface=AgentInterface(
            input_type=RobinInput,
            input_description="Scientific query with personalization context",
            output_type=RobinOutput,
            output_description="Comprehensive response with hypotheses and dialectic",
            error_codes=[
                ("MISSING_RUNTIME", "Runtime required for hypothesis generation"),
                ("EMPTY_QUERY", "Query cannot be empty"),
            ],
        ),
        behavior=AgentBehavior(
            description="Orchestrates persona, hypothesis, and dialectic agents",
            guarantees=[
                "Always applies personalization",
                "All hypotheses are falsifiable",
                "Dialectic does not force premature synthesis",
            ],
            constraints=[
                "Does not claim empirical certainty",
                "Does not diagnose, prescribe, or make medical claims",
                "System-introspective, not therapeutic",
            ],
        ),
    )

    def __init__(
        self,
        persona_state: Optional[PersonaState] = None,
        hypothesis_count: int = 3,
        runtime: Optional[Runtime] = None,
        fallback_mode: bool = False,
    ):
        """
        Initialize Robin.

        Args:
            persona_state: Optional K-gent persona state. If None, uses defaults.
            hypothesis_count: Number of hypotheses to generate (default 3).
            runtime: Runtime for LLM-backed hypothesis generation.
            fallback_mode: If True, operates in deterministic fallback mode for testing.
        """
        self._persona_state = persona_state or PersonaState(seed=PersonaSeed())
        self._hypothesis_count = hypothesis_count
        self._runtime = runtime
        self._fallback_mode = fallback_mode

        # Initialize component agents
        self._kgent = KgentAgent(self._persona_state)
        self._query_agent = PersonaQueryAgent(self._persona_state)
        self._hypothesis_engine = HypothesisEngine(hypothesis_count=hypothesis_count)
        self._hegel = HegelAgent()

        # Initialize composable morphisms
        self._synthesizer = NarrativeSynthesizer()
        self._question_gen = NextQuestionGenerator()

    @property
    def name(self) -> str:
        return "Robin"

    def with_runtime(self, runtime: Runtime) -> "RobinAgent":
        """Return a new RobinAgent with the specified runtime."""
        return RobinAgent(
            persona_state=self._persona_state,
            hypothesis_count=self._hypothesis_count,
            runtime=runtime,
            fallback_mode=self._fallback_mode,
        )

    async def invoke(
        self, input: RobinInput, runtime: Optional[Runtime] = None
    ) -> RobinOutput:
        """
        Execute Robin's scientific companion workflow.

        1. Query K-gent for personalization
        2. Get K-gent dialogue reflection
        3. Generate hypotheses (requires runtime)
        4. Optionally apply dialectic synthesis
        5. Synthesize into coherent narrative (via NarrativeSynthesizer)
        6. Generate next questions (via NextQuestionGenerator)
        """
        effective_runtime = runtime or self._runtime

        if not input.query.strip():
            raise ValueError("Query cannot be empty")

        # Step 1: Get personalization from K-gent
        persona_response = await self._query_agent.invoke(
            PersonaQuery(
                aspect="all",
                topic="science",
                for_agent="robin",
            )
        )

        # Step 2: Get K-gent dialogue reflection
        kgent_output = await self._kgent.invoke(
            DialogueInput(
                message=input.query,
                mode=input.dialogue_mode,
            )
        )

        # Step 3: Generate hypotheses
        if effective_runtime is None or self._fallback_mode:
            # Fallback mode: Generate deterministic placeholder hypotheses for testing
            hypothesis_output = generate_fallback_hypotheses(
                input, self._hypothesis_count
            )
        else:
            # Build hypothesis input
            hyp_input = HypothesisInput(
                observations=input.observations
                if input.observations
                else [input.query],
                domain=input.domain,
                question=input.query,
                constraints=input.constraints,
            )

            result: AgentResult[HypothesisOutput] = await effective_runtime.execute(
                self._hypothesis_engine,  # type: ignore[arg-type]
                hyp_input,
            )
            hypothesis_output = result.output

        # Step 4: Apply dialectic (if requested and we have hypotheses)
        dialectic_output = None
        if input.apply_dialectic and len(hypothesis_output.hypotheses) >= 2:
            # Use first two hypotheses as thesis/antithesis
            h1, h2 = hypothesis_output.hypotheses[0], hypothesis_output.hypotheses[1]

            dialectic_output = await self._hegel.invoke(
                DialecticInput(
                    thesis=h1.statement,
                    antithesis=h2.statement,
                    context={
                        "domain": input.domain,
                        "query": input.query,
                    },
                )
            )
        elif input.apply_dialectic and len(hypothesis_output.hypotheses) == 1:
            # Single hypothesis - surface antithesis
            h = hypothesis_output.hypotheses[0]
            dialectic_output = await self._hegel.invoke(
                DialecticInput(
                    thesis=h.statement,
                    context={"domain": input.domain},
                )
            )

        # Step 5: Synthesize narrative (via composable morphism)
        synthesis = await self._synthesizer.invoke(
            SynthesisInput(
                domain=input.domain,
                query=input.query,
                persona=persona_response,
                kgent=kgent_output,
                hypotheses=hypothesis_output,
                dialectic=dialectic_output,
            )
        )

        # Step 6: Generate next questions (via composable morphism)
        next_questions = await self._question_gen.invoke(
            QuestionInput(
                hypotheses=hypothesis_output,
                dialectic=dialectic_output,
            )
        )

        return RobinOutput(
            personalization=persona_response,
            kgent_reflection=kgent_output,
            hypotheses=hypothesis_output.hypotheses,
            reasoning_chain=hypothesis_output.reasoning_chain,
            suggested_tests=hypothesis_output.suggested_tests,
            dialectic=dialectic_output,
            synthesis_narrative=synthesis,
            next_questions=next_questions,
        )


# Convenience functions


def robin(
    persona_state: Optional[PersonaState] = None,
    hypothesis_count: int = 3,
    runtime: Optional[Runtime] = None,
    fallback_mode: bool = False,
) -> RobinAgent:
    """
    Create a Robin scientific companion agent.

    Args:
        persona_state: Optional K-gent persona. If None, uses defaults.
        hypothesis_count: Number of hypotheses to generate.
        runtime: Runtime for LLM-backed hypothesis generation.
        fallback_mode: If True, operates in deterministic fallback mode for testing.

    Returns:
        RobinAgent instance.

    Example:
        robin_agent = robin(runtime=my_runtime)
        result = await robin_agent.invoke(RobinInput(
            query="Why do neurons form sparse codes?",
            domain="neuroscience",
        ))
    """
    return RobinAgent(
        persona_state=persona_state,
        hypothesis_count=hypothesis_count,
        runtime=runtime,
        fallback_mode=fallback_mode,
    )


def robin_with_persona(
    seed: PersonaSeed,
    runtime: Optional[Runtime] = None,
    fallback_mode: bool = False,
) -> RobinAgent:
    """Create Robin with a specific persona seed."""
    return RobinAgent(
        persona_state=PersonaState(seed=seed),
        runtime=runtime,
        fallback_mode=fallback_mode,
    )


def quick_robin(runtime: Runtime, fallback_mode: bool = False) -> RobinAgent:
    """Create Robin with defaults and attached runtime."""
    return RobinAgent(runtime=runtime, fallback_mode=fallback_mode)


def fallback_robin(persona_state: Optional[PersonaState] = None) -> RobinAgent:
    """
    Create Robin in fallback mode for testing.

    Operates deterministically without runtime, generating predictable
    placeholder hypotheses. Useful for testing and development.

    Returns:
        RobinAgent configured for fallback mode.
    """
    return RobinAgent(
        persona_state=persona_state,
        runtime=None,
        fallback_mode=True,
    )
