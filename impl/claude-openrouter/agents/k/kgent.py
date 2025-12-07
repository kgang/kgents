"""
K-gent: Kent Simulacra

An interactive persona that embodies Kent's preferences, values, and thinking
patterns—evolving through use.

K-gent IS:
- A mirror for self-dialogue
- A preference repository
- An evolving representation
- A personalization layer for other agents

K-gent is NOT:
- A chatbot pretending to be Kent
- A replacement for Kent's judgment
- A static snapshot

Bootstrap dependency: Ground (persona data)
"""

from dataclasses import dataclass, field
from typing import Any

from bootstrap import Agent, Ground, ground_agent, GroundState, PersonaState
from ..types import (
    KgentInput,
    KgentOutput,
    PersonaQuery,
    PersonaUpdate,
    Dialogue,
    DialogueMode,
    QueryAspect,
    UpdateOperation,
    QueryResponse,
    UpdateConfirmation,
    DialogueResponse,
)


class Kgent(Agent[KgentInput, KgentOutput]):
    """
    Kent Simulacra - Interactive persona agent.

    Modes:
    - Query: Ask about preferences, patterns, context
    - Update: Modify persona state (with owner permission)
    - Dialogue: Engage in reflect/advise/challenge/explore modes

    Type signature: Kgent: (Query | Update | Dialogue) → Response
    """

    def __init__(self, ground: Ground | None = None):
        self._ground = ground or ground_agent
        self._updates: list[PersonaUpdate] = []  # Track updates for evolution

    @property
    def name(self) -> str:
        return "K-gent"

    @property
    def genus(self) -> str:
        return "k"

    @property
    def purpose(self) -> str:
        return "Interactive persona embodying Kent's preferences and patterns"

    async def invoke(self, input: KgentInput) -> KgentOutput:
        """
        Process input based on type.

        Dispatches to appropriate handler:
        - PersonaQuery → QueryResponse
        - PersonaUpdate → UpdateConfirmation
        - Dialogue → DialogueResponse
        """
        match input:
            case PersonaQuery():
                return await self._handle_query(input)
            case PersonaUpdate():
                return await self._handle_update(input)
            case Dialogue():
                return await self._handle_dialogue(input)

    async def _handle_query(self, query: PersonaQuery) -> QueryResponse:
        """Handle persona queries"""
        ground_state = await self._ground.invoke(None)
        persona = ground_state.persona

        preferences: list[str] = []
        patterns: list[str] = []
        suggested_style: list[str] = []

        match query.aspect:
            case QueryAspect.PREFERENCE:
                preferences = self._extract_preferences(persona, query.topic)
            case QueryAspect.PATTERN:
                patterns = self._extract_patterns(persona, query.topic)
            case QueryAspect.CONTEXT:
                preferences = [f"Current focus: {persona.context.current_focus}"]
                patterns = persona.context.recent_interests
            case QueryAspect.ALL:
                preferences = self._extract_preferences(persona, query.topic)
                patterns = self._extract_patterns(persona, query.topic)

        # Tailor style suggestions for requesting agent
        if query.for_agent:
            suggested_style = self._suggest_style_for_agent(persona, query.for_agent)

        return QueryResponse(
            preferences=preferences,
            patterns=patterns,
            suggested_style=suggested_style
        )

    async def _handle_update(self, update: PersonaUpdate) -> UpdateConfirmation:
        """
        Handle persona updates.

        Note: In production, this would persist changes and require authentication.
        Current implementation tracks updates in memory for evolution tracking.
        """
        # Track the update for evolution
        self._updates.append(update)

        # Would persist here in production
        return UpdateConfirmation(
            success=True,
            aspect_updated=update.aspect.value,
            new_value=update.content
        )

    async def _handle_dialogue(self, dialogue: Dialogue) -> DialogueResponse:
        """
        Handle dialogue in various modes.

        Modes:
        - REFLECT: Mirror back thinking for examination
        - ADVISE: Offer suggestions aligned with preferences
        - CHALLENGE: Push back constructively
        - EXPLORE: Help explore possibility space
        """
        ground_state = await self._ground.invoke(None)
        persona = ground_state.persona

        response = ""
        follow_ups: list[str] = []

        match dialogue.mode:
            case DialogueMode.REFLECT:
                response, follow_ups = self._reflect(dialogue.message, persona)
            case DialogueMode.ADVISE:
                response, follow_ups = self._advise(dialogue.message, persona)
            case DialogueMode.CHALLENGE:
                response, follow_ups = self._challenge(dialogue.message, persona)
            case DialogueMode.EXPLORE:
                response, follow_ups = self._explore(dialogue.message, persona)

        return DialogueResponse(
            response=response,
            mode_used=dialogue.mode,
            follow_ups=follow_ups
        )

    def _extract_preferences(self, persona: PersonaState, topic: str | None) -> list[str]:
        """Extract relevant preferences from persona"""
        prefs = persona.preferences
        results = []

        # Add communication preferences
        results.append(f"Communication: {prefs.communication.style}")
        results.append(f"Length: {prefs.communication.length}")
        results.append(f"Formality: {prefs.communication.formality}")

        # Add aesthetics
        results.append(f"Design: {prefs.aesthetics.design}")
        results.append(f"Prose: {prefs.aesthetics.prose}")

        # Add values
        for value in prefs.values:
            results.append(f"Values: {value}")

        # Filter by topic if provided
        if topic:
            topic_lower = topic.lower()
            results = [r for r in results if topic_lower in r.lower()]

        return results

    def _extract_patterns(self, persona: PersonaState, topic: str | None) -> list[str]:
        """Extract relevant patterns from persona"""
        patterns = persona.patterns
        results = []

        for p in patterns.thinking:
            results.append(f"Thinking: {p}")
        for p in patterns.decision_making:
            results.append(f"Decision: {p}")
        for p in patterns.communication:
            results.append(f"Communication: {p}")

        # Filter by topic if provided
        if topic:
            topic_lower = topic.lower()
            results = [r for r in results if topic_lower in r.lower()]

        return results

    def _suggest_style_for_agent(self, persona: PersonaState, agent_name: str) -> list[str]:
        """Suggest communication style based on requesting agent"""
        # Base suggestions from preferences
        suggestions = [
            f"Be {persona.preferences.communication.style}",
            f"Keep it {persona.preferences.communication.length}",
        ]

        # Agent-specific suggestions
        agent_lower = agent_name.lower()
        if "scientific" in agent_lower or "hypothesis" in agent_lower or "robin" in agent_lower:
            suggestions.append("Emphasize falsifiability")
            suggestions.append("Connect to first principles")
            suggestions.append("Be direct about uncertainty")
        elif "creative" in agent_lower or "art" in agent_lower:
            suggestions.append("Encourage exploration")
            suggestions.append("Use analogies")
        elif "hegel" in agent_lower or "dialectic" in agent_lower:
            suggestions.append("Surface tensions explicitly")
            suggestions.append("Avoid premature synthesis")

        return suggestions

    def _reflect(self, message: str, persona: PersonaState) -> tuple[str, list[str]]:
        """Reflect mode: Mirror back thinking for examination"""
        # Find relevant patterns
        relevant_patterns = []
        for p in persona.patterns.thinking:
            relevant_patterns.append(p)

        response = f"You mentioned: '{message}'. "

        if "not sure" in message.lower() or "uncertain" in message.lower():
            response += f"You've noted you '{persona.patterns.decision_making[0] if persona.patterns.decision_making else 'prefer reversible choices'}'. "
            response += "What about this feels uncertain? Is it the approach, the outcome, or something else?"
        else:
            response += f"Given your pattern of '{relevant_patterns[0] if relevant_patterns else 'starting from first principles'}', "
            response += "what assumptions are you making here?"

        follow_ups = [
            "What would falsify this thinking?",
            "Is this a reversible decision?",
            "What's the core tension here?"
        ]

        return response, follow_ups

    def _advise(self, message: str, persona: PersonaState) -> tuple[str, list[str]]:
        """Advise mode: Offer suggestions aligned with preferences"""
        response = ""

        # Check against dislikes
        for dislike in persona.preferences.dislikes:
            if dislike.lower().replace(" ", "") in message.lower().replace(" ", ""):
                response = f"Careful—this touches on '{dislike}', which you've flagged as a dislike. "
                break

        if not response:
            response = f"Given your value of '{persona.preferences.values[0] if persona.preferences.values else 'intellectual honesty'}', "

        # Add pattern-based advice
        if persona.patterns.decision_making:
            response += f"and your tendency to '{persona.patterns.decision_making[0]}', "

        response += "consider: does this align with your core principles?"

        follow_ups = [
            "Does this serve your current focus?",
            "What's the simplest version of this?",
            "Who else has solved this well?"
        ]

        return response, follow_ups

    def _challenge(self, message: str, persona: PersonaState) -> tuple[str, list[str]]:
        """Challenge mode: Push back constructively"""
        response = f"Let me push back on '{message[:50]}...': "

        # Use falsifiability pattern
        response += "What would prove this wrong? "

        # Check against values
        if persona.preferences.values:
            response += f"Does this truly serve '{persona.preferences.values[0]}'? "

        response += "Sometimes the obvious path isn't the composed one."

        follow_ups = [
            "What's the strongest argument against this?",
            "Is this feature creep in disguise?",
            "What would you advise someone else in this situation?"
        ]

        return response, follow_ups

    def _explore(self, message: str, persona: PersonaState) -> tuple[str, list[str]]:
        """Explore mode: Help explore possibility space"""
        response = f"Exploring '{message[:50]}...': "

        # Use current context
        response += f"Given your focus on '{persona.context.current_focus}' "
        response += f"and interest in {', '.join(persona.context.recent_interests[:2]) if persona.context.recent_interests else 'composable abstractions'}, "
        response += "what connections emerge?"

        follow_ups = [
            "How does this relate to category theory?",
            "What's the opposite of this idea?",
            "Who would disagree with this, and why?",
            "What would this look like in 10 years?"
        ]

        return response, follow_ups


# Singleton instance
kgent = Kgent()


async def query_persona(
    aspect: QueryAspect,
    topic: str | None = None,
    for_agent: str | None = None
) -> QueryResponse:
    """Convenience function to query K-gent's persona"""
    result = await kgent.invoke(PersonaQuery(
        aspect=aspect,
        topic=topic,
        for_agent=for_agent
    ))
    assert isinstance(result, QueryResponse)
    return result


async def dialogue(message: str, mode: DialogueMode) -> DialogueResponse:
    """Convenience function to engage in dialogue with K-gent"""
    result = await kgent.invoke(Dialogue(message=message, mode=mode))
    assert isinstance(result, DialogueResponse)
    return result
