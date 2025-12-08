"""Orchestrates kgents agents for zen-agents TUI.

This service provides a high-level interface for executing LLM-backed agents
from the kgents ecosystem within the zen-agents TUI. It uses ClaudeCLIRuntime
which authenticates via OAuth (no API key needed).

Usage:
    orchestrator = AgentOrchestrator()

    # Check availability
    if await orchestrator.check_available():
        # Analyze session output
        result = await orchestrator.analyze_log(log_content)

        # Expand ideas
        ideas = await orchestrator.expand_idea("distributed systems")

        # Scientific dialogue with Robin
        synthesis = await orchestrator.scientific_dialogue(
            query="Why do neurons form sparse codes?",
            domain="neuroscience"
        )
"""

from typing import Optional
from dataclasses import dataclass, field

from ..kgents_bridge import (
    ClaudeCLIRuntime,
    # A-gents: Creativity
    CreativityCoach,
    CreativityInput,
    CreativityMode,
    creativity_coach,
    # B-gents: Scientific discovery
    HypothesisEngine,
    HypothesisInput,
    hypothesis_engine,
    RobinAgent,
    RobinInput,
    robin,
    # H-gents: Dialectics
    HegelAgent,
    DialecticInput,
    hegel,
    # K-gent: Personalization
    KgentAgent,
    DialogueMode,
    DialogueInput,
    kgent,
    PersonaQuery,
    query_persona,
)


@dataclass
class AnalysisResult:
    """Result of log analysis via HypothesisEngine."""
    hypotheses: list[str]
    suggested_tests: list[str]
    reasoning: str


@dataclass
class ExpansionResult:
    """Result of idea expansion via CreativityCoach."""
    ideas: list[str]
    follow_ups: list[str]


@dataclass
class DialogueResult:
    """Result of K-gent dialogue."""
    response: str
    mode: DialogueMode


@dataclass
class DialecticResult:
    """Result of Hegelian dialectic analysis."""
    synthesis: str
    notes: str
    productive_tension: bool
    next_thesis: Optional[str]


@dataclass
class ScientificResult:
    """Result of Robin scientific dialogue."""
    synthesis: str
    hypotheses: list[str]
    dialectic: Optional[dict]
    next_questions: list[str]
    personalization: Optional[dict]


class AgentOrchestrator:
    """
    Central orchestrator for LLM-backed agents.

    Uses ClaudeCLIRuntime (OAuth via Claude CLI) by default.
    All methods are async and designed to work within Textual's event loop.

    Attributes:
        runtime: The underlying ClaudeCLIRuntime instance (lazily initialized)
    """

    def __init__(self, runtime: Optional[ClaudeCLIRuntime] = None):
        """
        Initialize the orchestrator.

        Args:
            runtime: Optional pre-configured runtime. If None, creates one lazily.
        """
        self._runtime = runtime
        self._available: Optional[bool] = None

    @property
    def runtime(self) -> ClaudeCLIRuntime:
        """Lazy initialization of runtime."""
        if self._runtime is None:
            self._runtime = ClaudeCLIRuntime()
        return self._runtime

    async def check_available(self) -> bool:
        """
        Check if Claude CLI is available for LLM calls.

        Returns:
            True if claude CLI is installed and accessible, False otherwise.
        """
        if self._available is not None:
            return self._available

        try:
            import subprocess
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                timeout=5
            )
            self._available = result.returncode == 0
        except Exception:
            self._available = False
        return self._available

    # -------------------------------------------------------------------------
    # Analysis (HypothesisEngine)
    # -------------------------------------------------------------------------

    async def analyze_log(
        self,
        log_content: str,
        domain: str = "software engineering",
        question: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze session log using HypothesisEngine.

        Generates falsifiable hypotheses about what's happening in the output,
        following Popperian epistemology.

        Args:
            log_content: Raw log/output text to analyze
            domain: Domain context (e.g., "networking", "database", "memory")
            question: Specific question to answer (optional)

        Returns:
            AnalysisResult with hypotheses, suggested tests, and reasoning chain
        """
        engine = hypothesis_engine()
        result = await self.runtime.execute(
            engine,
            HypothesisInput(
                observations=[log_content],
                domain=domain,
                question=question or "What is happening in this output?"
            )
        )
        return AnalysisResult(
            hypotheses=[h.statement for h in result.output.hypotheses],
            suggested_tests=result.output.suggested_tests,
            reasoning="\n".join(result.output.reasoning_chain)
        )

    # -------------------------------------------------------------------------
    # Creativity (CreativityCoach)
    # -------------------------------------------------------------------------

    async def expand_idea(
        self,
        seed: str,
        mode: CreativityMode = CreativityMode.EXPAND,
        context: Optional[str] = None
    ) -> ExpansionResult:
        """
        Expand an idea using CreativityCoach.

        Args:
            seed: The seed idea to expand
            mode: Expansion mode - EXPAND (variations), CONNECT (associations),
                  CONSTRAIN (limitations), or QUESTION (challenges)
            context: Optional additional context

        Returns:
            ExpansionResult with generated ideas and suggested follow-ups
        """
        coach = creativity_coach()
        result = await self.runtime.execute(
            coach,
            CreativityInput(seed=seed, mode=mode, context=context)
        )
        return ExpansionResult(
            ideas=result.output.responses,
            follow_ups=result.output.follow_ups
        )

    # -------------------------------------------------------------------------
    # Scientific Dialogue (Robin)
    # -------------------------------------------------------------------------

    async def scientific_dialogue(
        self,
        query: str,
        domain: str,
        observations: Optional[list[str]] = None,
        mode: DialogueMode = DialogueMode.EXPLORE
    ) -> ScientificResult:
        """
        Scientific dialogue using Robin.

        Robin = K-gent (personalization) + HypothesisEngine + HegelAgent
        Provides personalized scientific exploration with dialectic refinement.

        Args:
            query: The scientific question to explore
            domain: Domain (e.g., "neuroscience", "biochemistry", "physics")
            observations: Optional observations to base hypotheses on
            mode: Dialogue mode (EXPLORE, CHALLENGE, REFLECT, ADVISE)

        Returns:
            ScientificResult with synthesis, hypotheses, dialectic, and next questions
        """
        robin_agent = robin(runtime=self.runtime)
        result = await robin_agent.invoke(RobinInput(
            query=query,
            domain=domain,
            observations=observations or [],
            dialogue_mode=mode,
            apply_dialectic=True
        ))
        return ScientificResult(
            synthesis=result.synthesis_narrative,
            hypotheses=[h.statement for h in result.hypotheses],
            dialectic=result.dialectic,
            next_questions=result.next_questions,
            personalization=result.personalization
        )

    # -------------------------------------------------------------------------
    # Personalization (K-gent)
    # -------------------------------------------------------------------------

    async def kgent_dialogue(
        self,
        message: str,
        mode: DialogueMode = DialogueMode.REFLECT
    ) -> DialogueResult:
        """
        Dialogue with K-gent for personalized responses.

        K-gent adapts responses based on Kent's persona schema and preferences.

        Args:
            message: The message/query to reflect on
            mode: REFLECT (introspective), ADVISE (actionable),
                  CHALLENGE (pushback), or EXPLORE (open-ended)

        Returns:
            DialogueResult with personalized response and mode used
        """
        k = kgent()
        result = await self.runtime.execute(
            k,
            DialogueInput(message=message, mode=mode)
        )
        return DialogueResult(
            response=result.output.response,
            mode=mode
        )

    async def query_preferences(
        self,
        aspect: str = "all",
        topic: Optional[str] = None,
        for_agent: Optional[str] = None
    ) -> dict:
        """
        Query K-gent preferences for adapting agent behavior.

        Args:
            aspect: "preference", "pattern", "value", or "all"
            topic: Specific topic to query about
            for_agent: Agent name this is for (influences style suggestions)

        Returns:
            Dict with preferences, patterns, and suggested_style lists
        """
        query = query_persona()
        result = await self.runtime.execute(
            query,
            PersonaQuery(aspect=aspect, topic=topic, for_agent=for_agent)
        )
        return {
            "preferences": result.output.preferences,
            "patterns": result.output.patterns,
            "suggested_style": result.output.suggested_style
        }

    # -------------------------------------------------------------------------
    # Dialectics (Hegel)
    # -------------------------------------------------------------------------

    async def dialectic_analysis(
        self,
        thesis: str,
        antithesis: str
    ) -> DialecticResult:
        """
        Dialectic analysis using HegelAgent.

        Synthesizes opposing positions through sublation.

        Args:
            thesis: First position
            antithesis: Opposing position

        Returns:
            DialecticResult with synthesis, notes, and indication of productive tension
        """
        h = hegel()
        result = await self.runtime.execute(
            h,
            DialecticInput(thesis=thesis, antithesis=antithesis)
        )
        return DialecticResult(
            synthesis=result.output.synthesis,
            notes=result.output.sublation_notes,
            productive_tension=result.output.productive_tension,
            next_thesis=result.output.next_thesis
        )

    # -------------------------------------------------------------------------
    # Convenience: Session Name Suggestions
    # -------------------------------------------------------------------------

    async def suggest_session_name(
        self,
        working_dir: str,
        session_type: str,
        context: Optional[str] = None
    ) -> str:
        """
        Use K-gent to suggest a personalized session name.

        Args:
            working_dir: Working directory path
            session_type: Type of session (e.g., "shell", "robin", "hypothesis")
            context: Optional additional context about the session

        Returns:
            Short (1-2 word) memorable session name
        """
        message = (
            f"Suggest a short (1-2 word) memorable session name for a "
            f"{session_type} session in {working_dir}"
        )
        if context:
            message += f". Context: {context}"

        result = await self.kgent_dialogue(message, DialogueMode.ADVISE)

        # Extract first word/phrase as name, clean up quotes
        name = result.response.split()[0].lower()
        name = name.replace('"', '').replace("'", '').replace(":", "")
        return name[:20]  # Cap at 20 chars for tmux compatibility
