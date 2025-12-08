"""Session type handlers - route input to appropriate kgents agents.

This module implements the routing layer between zen-agents sessions and
kgents LLM-backed agents. Each session type has a dedicated handler that
interprets user input and invokes the appropriate agent.

Session Types and Their Agents:
    ROBIN       -> RobinAgent (scientific companion)
    CREATIVITY  -> CreativityCoach (idea expansion)
    HYPOTHESIS  -> HypothesisEngine (Popperian hypothesis generation)
    KGENT       -> KgentAgent (personalized dialogue)

Command Prefixes (for KGENT mode switching):
    /challenge <msg>  -> CHALLENGE mode (pushback)
    /advise <msg>     -> ADVISE mode (actionable)
    /explore <msg>    -> EXPLORE mode (open-ended)
    (no prefix)       -> REFLECT mode (introspective)

Usage:
    handler = SessionTypeHandler(orchestrator)
    response = await handler.handle_input(session, "Why do neurons spike?")
"""

from typing import Optional, Callable, Awaitable
from dataclasses import dataclass

from ..models.session import Session, SessionType, session_requires_llm
from .agent_orchestrator import (
    AgentOrchestrator,
    AnalysisResult,
    ExpansionResult,
    DialogueResult,
    ScientificResult,
)
from ..kgents_bridge import DialogueMode, CreativityMode


@dataclass
class HandlerResult:
    """Result from a session handler."""
    formatted_output: str
    raw_result: object  # The underlying result type
    success: bool = True
    error: Optional[str] = None


class SessionTypeHandler:
    """Routes session interactions to appropriate kgents agents.

    This class is the bridge between zen-agents' session model and kgents'
    LLM-backed agents. It interprets user input, invokes the right agent
    via AgentOrchestrator, and formats the response for display.
    """

    def __init__(self, orchestrator: AgentOrchestrator):
        """
        Initialize the handler.

        Args:
            orchestrator: The AgentOrchestrator instance for LLM calls
        """
        self.orchestrator = orchestrator
        self._handlers: dict[
            SessionType,
            Callable[[Session, str, Optional[str]], Awaitable[HandlerResult]]
        ] = {
            SessionType.ROBIN: self._handle_robin,
            SessionType.CREATIVITY: self._handle_creativity,
            SessionType.HYPOTHESIS: self._handle_hypothesis,
            SessionType.KGENT: self._handle_kgent,
        }

    def can_handle(self, session: Session) -> bool:
        """Check if this handler supports the session type."""
        return session.session_type in self._handlers

    async def handle_input(
        self,
        session: Session,
        input_text: str,
        context: Optional[str] = None
    ) -> HandlerResult:
        """
        Handle user input for a session.

        For LLM-backed session types, routes to the appropriate agent.
        For non-LLM sessions, returns input unchanged (passthrough to tmux).

        Args:
            session: The session receiving input
            input_text: User's input text
            context: Optional context (e.g., recent output, accumulated observations)

        Returns:
            HandlerResult with formatted output and metadata
        """
        handler = self._handlers.get(session.session_type)

        if handler is None:
            # Non-LLM session - passthrough
            return HandlerResult(
                formatted_output=input_text,
                raw_result=None,
                success=True
            )

        try:
            return await handler(session, input_text, context)
        except Exception as e:
            return HandlerResult(
                formatted_output=f"Error: {e}",
                raw_result=None,
                success=False,
                error=str(e)
            )

    # -------------------------------------------------------------------------
    # Robin: Scientific Companion
    # -------------------------------------------------------------------------

    async def _handle_robin(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> HandlerResult:
        """
        Handle Robin (scientific companion) session.

        Robin composes K-gent personalization + HypothesisEngine + HegelAgent
        for dialectic-refined scientific exploration.
        """
        # Get domain from session metadata, default to general
        domain = session.metadata.get("domain", "general science")

        # Parse observations from context if provided
        observations = None
        if context:
            observations = [context]

        result = await self.orchestrator.scientific_dialogue(
            query=input_text,
            domain=domain,
            observations=observations,
            mode=DialogueMode.EXPLORE
        )

        # Format output
        output_parts = [f"## Synthesis\n{result.synthesis}"]

        if result.hypotheses:
            output_parts.append("\n## Hypotheses")
            for h in result.hypotheses:
                output_parts.append(f"  * {h}")

        if result.next_questions:
            output_parts.append("\n## Next Questions")
            for q in result.next_questions:
                output_parts.append(f"  ? {q}")

        return HandlerResult(
            formatted_output="\n".join(output_parts),
            raw_result=result
        )

    # -------------------------------------------------------------------------
    # Creativity: Idea Expansion
    # -------------------------------------------------------------------------

    async def _handle_creativity(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> HandlerResult:
        """
        Handle creativity session.

        Uses CreativityCoach to expand ideas through various modes.
        Command prefixes switch modes:
            /connect <idea>    -> CONNECT mode (find associations)
            /constrain <idea>  -> CONSTRAIN mode (add limitations)
            /question <idea>   -> QUESTION mode (challenge assumptions)
            (no prefix)        -> EXPAND mode (generate variations)
        """
        # Parse mode from input prefix
        mode = CreativityMode.EXPAND
        text = input_text

        if input_text.startswith("/connect "):
            mode = CreativityMode.CONNECT
            text = input_text[9:]
        elif input_text.startswith("/constrain "):
            mode = CreativityMode.CONSTRAIN
            text = input_text[11:]
        elif input_text.startswith("/question "):
            mode = CreativityMode.QUESTION
            text = input_text[10:]

        result = await self.orchestrator.expand_idea(
            seed=text,
            mode=mode,
            context=context
        )

        # Format output
        mode_label = mode.value.upper()
        output_parts = [f"## {mode_label} Expansions"]
        for idea in result.ideas:
            output_parts.append(f"  * {idea}")

        if result.follow_ups:
            output_parts.append("\n## Follow-ups")
            for f in result.follow_ups:
                output_parts.append(f"  -> {f}")

        return HandlerResult(
            formatted_output="\n".join(output_parts),
            raw_result=result
        )

    # -------------------------------------------------------------------------
    # Hypothesis: Scientific Reasoning
    # -------------------------------------------------------------------------

    async def _handle_hypothesis(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> HandlerResult:
        """
        Handle hypothesis session.

        Uses HypothesisEngine to generate falsifiable hypotheses
        from observations, following Popperian epistemology.
        """
        domain = session.metadata.get("domain", "software engineering")

        # Input text is treated as observations
        result = await self.orchestrator.analyze_log(
            log_content=input_text,
            domain=domain,
            question=context  # Context becomes the guiding question
        )

        # Format output
        output_parts = ["## Hypotheses"]
        for h in result.hypotheses:
            output_parts.append(f"  * {h}")

        if result.suggested_tests:
            output_parts.append("\n## Falsification Tests")
            for t in result.suggested_tests:
                output_parts.append(f"  [x] {t}")

        if result.reasoning:
            output_parts.append(f"\n## Reasoning\n{result.reasoning}")

        return HandlerResult(
            formatted_output="\n".join(output_parts),
            raw_result=result
        )

    # -------------------------------------------------------------------------
    # K-gent: Personalized Dialogue
    # -------------------------------------------------------------------------

    async def _handle_kgent(
        self,
        session: Session,
        input_text: str,
        context: Optional[str]
    ) -> HandlerResult:
        """
        Handle K-gent dialogue session.

        K-gent provides personalized responses based on Kent's persona schema.
        Command prefixes switch dialogue modes:
            /challenge <msg>  -> CHALLENGE mode (pushback, devil's advocate)
            /advise <msg>     -> ADVISE mode (actionable suggestions)
            /explore <msg>    -> EXPLORE mode (open-ended exploration)
            (no prefix)       -> REFLECT mode (introspective)
        """
        # Parse mode from input prefix
        mode = DialogueMode.REFLECT
        text = input_text

        if input_text.startswith("/challenge "):
            mode = DialogueMode.CHALLENGE
            text = input_text[11:]
        elif input_text.startswith("/advise "):
            mode = DialogueMode.ADVISE
            text = input_text[8:]
        elif input_text.startswith("/explore "):
            mode = DialogueMode.EXPLORE
            text = input_text[9:]

        result = await self.orchestrator.kgent_dialogue(text, mode)

        # Format output with mode indicator
        mode_label = mode.value.upper()
        formatted = f"[{mode_label}] {result.response}"

        return HandlerResult(
            formatted_output=formatted,
            raw_result=result
        )


# Convenience function for quick handler creation
def create_handler(orchestrator: Optional[AgentOrchestrator] = None) -> SessionTypeHandler:
    """Create a SessionTypeHandler with optional orchestrator.

    Args:
        orchestrator: Optional pre-configured orchestrator.
                     If None, creates a new AgentOrchestrator.

    Returns:
        Configured SessionTypeHandler
    """
    if orchestrator is None:
        orchestrator = AgentOrchestrator()
    return SessionTypeHandler(orchestrator)
