"""
K-gent Persona: The interactive persona model.

K-gent is Ground projected through persona_schema:
- Queryable: Other agents ask "what would Kent prefer?"
- Composable: Provides personalization interface
- Dialogic: Four modes - reflect, advise, challenge, explore

The KgentAgent now supports LLM-backed dialogue (DIALOGUE/DEEP tiers)
in addition to template-based responses (DORMANT/WHISPER tiers).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Generic,
    Optional,
    TypeVar,
)

from agents.a.halo import Capability
from agents.poly.types import Agent

if TYPE_CHECKING:
    from .eigenvectors import KentEigenvectors
    from .llm import LLMClient

A = TypeVar("A")


class Maybe(Generic[A]):
    """
    Maybe monad for graceful degradation.

    Represents a value that might not exist without throwing exceptions.
    Allows composition of potentially failing operations.
    """

    def __init__(self, value: Optional[A], error: Optional[str] = None):
        self._value = value
        self._error = error

    @staticmethod
    def just(value: A) -> "Maybe[A]":
        """Create a Maybe with a value."""
        return Maybe(value)

    @staticmethod
    def nothing(error: str = "No value") -> "Maybe[A]":
        """Create an empty Maybe with error context."""
        return Maybe(None, error)

    @property
    def is_just(self) -> bool:
        return self._value is not None

    @property
    def is_nothing(self) -> bool:
        return self._value is None

    def value_or(self, default: A) -> A:
        """Get value or return default."""
        return self._value if self._value is not None else default

    def map(self, f: Callable[[A], Any]) -> "Maybe[Any]":
        """Apply function if value exists."""
        if self.is_nothing:
            return Maybe[Any].nothing(self._error or "No value")
        try:
            return Maybe.just(f(self._value))  # type: ignore[arg-type]
        except Exception as e:
            return Maybe.nothing(f"map failed: {str(e)}")

    @property
    def error(self) -> Optional[str]:
        return self._error


class DialogueMode(Enum):
    """The four dialogue modes of K-gent."""

    REFLECT = "reflect"  # Mirror back for examination
    ADVISE = "advise"  # Offer preference-aligned suggestions
    CHALLENGE = "challenge"  # Push back constructively
    EXPLORE = "explore"  # Help explore possibility space


@dataclass
class PersonaSeed:
    """
    The irreducible seed of K-gent.

    This is what Ground provides - raw facts about Kent.
    Cannot be derived, must be given.
    """

    name: str = "Kent"
    roles: list[str] = field(default_factory=lambda: ["researcher", "creator", "thinker"])

    # Explicit preferences
    preferences: dict[str, Any] = field(
        default_factory=lambda: {
            "communication": {
                "style": "direct but warm",
                "length": "concise preferred",
                "formality": "casual with substance",
            },
            "aesthetics": {
                "design": "minimal, functional",
                "prose": "clear over clever",
            },
            "values": [
                "intellectual honesty",
                "ethical technology",
                "joy in creation",
                "composability",
            ],
            "dislikes": [
                "unnecessary jargon",
                "feature creep",
                "surveillance capitalism",
            ],
        }
    )

    # Observed patterns
    patterns: dict[str, list[str]] = field(
        default_factory=lambda: {
            "thinking": [
                "starts from first principles",
                "asks 'what would falsify this?'",
                "seeks composable abstractions",
            ],
            "decision_making": [
                "prefers reversible choices",
                "values optionality",
            ],
            "communication": [
                "uses analogies frequently",
                "appreciates precision in technical contexts",
            ],
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "roles": self.roles,
            "preferences": self.preferences,
            "patterns": self.patterns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersonaSeed":
        """Create from dictionary."""
        return cls(
            name=data.get("name", "Kent"),
            roles=data.get("roles", ["researcher", "creator", "thinker"]),
            preferences=data.get("preferences", {}),
            patterns=data.get("patterns", {}),
        )


@dataclass
class PersonaState:
    """
    Full persona state including context and confidence.

    Extends PersonaSeed with runtime state.
    """

    seed: PersonaSeed
    current_focus: str = "kgents specification"
    recent_interests: list[str] = field(
        default_factory=lambda: [
            "category theory",
            "scientific agents",
            "personal AI",
        ]
    )
    active_projects: list[dict[str, Any]] = field(
        default_factory=lambda: [
            {
                "name": "kgents",
                "status": "active",
                "goals": ["spec A/B/C/K", "reference implementation"],
            }
        ]
    )

    # Confidence tracking for preferences
    confidence: dict[str, float] = field(default_factory=dict)

    # Source tracking: "explicit" | "inferred" | "inherited"
    sources: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "seed": self.seed.to_dict(),
            "current_focus": self.current_focus,
            "recent_interests": self.recent_interests,
            "active_projects": self.active_projects,
            "confidence": self.confidence,
            "sources": self.sources,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PersonaState":
        """Create from dictionary."""
        seed_data = data.get("seed", {})
        return cls(
            seed=PersonaSeed.from_dict(seed_data),
            current_focus=data.get("current_focus", "kgents specification"),
            recent_interests=data.get(
                "recent_interests",
                ["category theory", "scientific agents", "personal AI"],
            ),
            active_projects=data.get("active_projects", []),
            confidence=data.get("confidence", {}),
            sources=data.get("sources", {}),
        )


@dataclass
class PersonaQuery:
    """Query to K-gent for preferences/patterns."""

    aspect: str  # "preference" | "pattern" | "context" | "all"
    topic: Optional[str] = None  # Optional filter
    for_agent: Optional[str] = None  # Which agent is asking


@dataclass
class PersonaResponse:
    """Response to a persona query."""

    preferences: list[str]
    patterns: list[str]
    suggested_style: list[str]
    confidence: float = 1.0


@dataclass
class DialogueInput:
    """Input for K-gent dialogue."""

    message: str
    mode: DialogueMode = DialogueMode.REFLECT


@dataclass
class DialogueOutput:
    """Output from K-gent dialogue."""

    response: str
    mode: DialogueMode
    referenced_preferences: list[str] = field(default_factory=list)
    referenced_patterns: list[str] = field(default_factory=list)


class PersonaQueryAgent(Agent[PersonaQuery, PersonaResponse]):
    """
    Query K-gent's preferences and patterns.

    Used by other agents to personalize their behavior.
    Now returns Maybe[PersonaResponse] for graceful degradation.
    """

    def __init__(self, state: Optional[PersonaState] = None):
        self._state = state or PersonaState(seed=PersonaSeed())

    @property
    def name(self) -> str:
        return "PersonaQuery"

    async def invoke(self, query: PersonaQuery) -> PersonaResponse:
        """Query preferences and patterns with Maybe wrapper."""
        maybe_response = self.invoke_safe(query)

        # For backwards compatibility, unwrap with default
        return maybe_response.value_or(
            PersonaResponse(
                preferences=[],
                patterns=[],
                suggested_style=["be direct but warm"],
                confidence=0.0,
            )
        )

    def invoke_safe(self, query: PersonaQuery) -> Maybe[PersonaResponse]:
        """Safe query that returns Maybe for composition."""
        try:
            if not self._state or not self._state.seed:
                return Maybe.nothing("Persona state not initialized")

            seed = self._state.seed

            preferences = []
            patterns = []
            style = []

            if query.aspect in ("preference", "all"):
                # Extract relevant preferences
                if query.topic:
                    # Filter by topic
                    for key, value in seed.preferences.items():
                        if query.topic.lower() in key.lower():
                            if isinstance(value, dict):
                                preferences.extend([f"{k}: {v}" for k, v in value.items()])
                            elif isinstance(value, list):
                                preferences.extend(value)
                            else:
                                preferences.append(str(value))
                else:
                    # All preferences
                    preferences = seed.preferences.get("values", [])

            if query.aspect in ("pattern", "all"):
                # Extract patterns
                if query.topic:
                    for key, value in seed.patterns.items():
                        if query.topic.lower() in key.lower():
                            patterns.extend(value)
                else:
                    # All patterns
                    for pats in seed.patterns.values():
                        patterns.extend(pats)

            # Generate style suggestions based on requesting agent
            if query.for_agent:
                style = self._style_for_agent(query.for_agent)
            else:
                comm_prefs = seed.preferences.get("communication", {})
                style = [
                    comm_prefs.get("style", "direct"),
                    comm_prefs.get("length", "concise"),
                ]

            return Maybe.just(
                PersonaResponse(
                    preferences=preferences,
                    patterns=patterns,
                    suggested_style=style,
                    confidence=0.9,  # High confidence for explicit preferences
                )
            )

        except Exception as e:
            return Maybe.nothing(f"Query failed: {str(e)}")

    def _style_for_agent(self, agent: str) -> list[str]:
        """Generate style suggestions for specific agents."""
        styles = {
            "robin": [
                "be direct about uncertainty",
                "connect to first principles",
                "value falsifiability",
            ],
            "hypothesis": [
                "prefer mechanistic explanations",
                "epistemic humility",
                "ask what would disprove this",
            ],
            "creativity": [
                "expand, don't judge",
                "use analogies",
                "seek unexpected connections",
            ],
        }
        return styles.get(agent.lower(), ["be direct but warm", "prefer concise"])


@Capability.TurnBased(
    allowed_types={"SPEECH", "ACTION", "THOUGHT", "YIELD"},
    yield_threshold=0.5,  # YIELD for uncertain persona decisions
    entropy_budget=10.0,
    surplus_fraction=0.1,
)
class KgentAgent(Agent[DialogueInput, DialogueOutput]):
    """
    The main K-gent dialogue agent.

    Four modes:
    - REFLECT: Mirror back for examination
    - ADVISE: Offer preference-aligned suggestions
    - CHALLENGE: Push back constructively
    - EXPLORE: Help explore possibility space

    Now supports LLM-backed dialogue when an LLM client is provided.
    Falls back to template-based responses when no LLM is available.

    Turn-gents Integration:
    - Decorated with @Capability.TurnBased for turn recording
    - Records SPEECH turns for dialogue outputs
    - Records THOUGHT turns for internal reasoning
    - YIELDs for low-confidence persona decisions (below 0.5)
    """

    # Temperature per mode - lower for precise modes, higher for creative
    MODE_TEMPERATURES = {
        DialogueMode.REFLECT: 0.4,  # Precise mirroring
        DialogueMode.ADVISE: 0.5,  # Grounded suggestions
        DialogueMode.CHALLENGE: 0.6,  # Provocative pushback
        DialogueMode.EXPLORE: 0.8,  # Creative tangents
    }

    def __init__(
        self,
        state: Optional[PersonaState] = None,
        llm: Optional["LLMClient"] = None,
        eigenvectors: Optional["KentEigenvectors"] = None,
    ):
        """Initialize K-gent agent.

        Args:
            state: Persona state with preferences and patterns.
            llm: Optional LLM client for DIALOGUE/DEEP tier responses.
            eigenvectors: Personality coordinates for prompt context.
        """
        self._state = state or PersonaState(seed=PersonaSeed())
        self._query_agent = PersonaQueryAgent(self._state)
        self._llm = llm
        self._eigenvectors = eigenvectors

    @property
    def name(self) -> str:
        return "K-gent"

    @property
    def state(self) -> PersonaState:
        return self._state

    @property
    def has_llm(self) -> bool:
        """Check if LLM is configured."""
        return self._llm is not None

    def set_llm(self, llm: "LLMClient") -> None:
        """Set the LLM client."""
        self._llm = llm

    def set_eigenvectors(self, eigenvectors: "KentEigenvectors") -> None:
        """Set the eigenvectors."""
        self._eigenvectors = eigenvectors

    async def invoke(self, input: DialogueInput) -> DialogueOutput:
        """
        Engage in dialogue with K-gent.

        If LLM is configured, uses LLM-backed generation.
        Otherwise falls back to template-based responses.

        Mode determines response style:
        - reflect: "You've said before..."
        - advise: "Your pattern is to..."
        - challenge: "That sounds like it conflicts with..."
        - explore: "Given your interest in..."
        """
        mode = input.mode
        message = input.message
        _seed = self._state.seed  # Reserved for future persona context

        # Find relevant preferences and patterns (used in both paths)
        referenced_prefs = self._find_preferences(message)
        referenced_pats = self._find_patterns(message)

        # Use LLM if available
        if self._llm is not None:
            response = await self._generate_llm_response(
                mode, message, referenced_prefs, referenced_pats
            )
        else:
            # Fall back to template-based response
            response = self._generate_template_response(
                mode, message, referenced_prefs, referenced_pats
            )

        return DialogueOutput(
            response=response,
            mode=mode,
            referenced_preferences=referenced_prefs[:3],
            referenced_patterns=referenced_pats[:3],
        )

    async def invoke_stream(self, input: DialogueInput) -> AsyncIterator[tuple[str, bool, int]]:
        """
        Engage in streaming dialogue with K-gent.

        Yields (chunk, is_final, tokens_used) tuples:
        - is_final=False for intermediate chunks (tokens_used=0)
        - is_final=True for the final chunk with actual tokens_used

        If LLM is configured and supports streaming, uses true streaming.
        Otherwise falls back to template-based responses (single chunk).
        """
        from .llm import StreamingLLMResponse

        mode = input.mode
        message = input.message

        # Find relevant preferences and patterns
        referenced_prefs = self._find_preferences(message)
        referenced_pats = self._find_patterns(message)

        # Use LLM streaming if available
        if self._llm is not None:
            system_prompt = self._build_system_prompt(mode)
            user_prompt = self._build_user_prompt(message, referenced_prefs, referenced_pats, mode)
            temperature = self.MODE_TEMPERATURES.get(mode, 0.6)

            # Stream chunks from LLM
            tokens_used = 0
            async for item in self._llm.generate_stream(
                system=system_prompt,
                user=user_prompt,
                temperature=temperature,
                max_tokens=500,
            ):
                if isinstance(item, str):
                    yield (item, False, 0)
                elif isinstance(item, StreamingLLMResponse):
                    # Final response with token counts
                    tokens_used = item.tokens_used

            # Final yield with is_final=True and actual token count
            yield ("", True, tokens_used)
        else:
            # Fall back to template-based response (single chunk)
            response = self._generate_template_response(
                mode, message, referenced_prefs, referenced_pats
            )
            # Estimate tokens for template response
            tokens_estimate = len(response.split()) * 2
            yield (response, True, tokens_estimate)

    async def _generate_llm_response(
        self,
        mode: DialogueMode,
        message: str,
        prefs: list[str],
        pats: list[str],
    ) -> str:
        """Generate response using LLM."""
        assert self._llm is not None

        system_prompt = self._build_system_prompt(mode)
        user_prompt = self._build_user_prompt(message, prefs, pats, mode)
        temperature = self.MODE_TEMPERATURES.get(mode, 0.6)

        response = await self._llm.generate(
            system=system_prompt,
            user=user_prompt,
            temperature=temperature,
            max_tokens=500,  # Keep responses focused
        )

        return response.text

    def _build_system_prompt(self, mode: DialogueMode) -> str:
        """Build system prompt for K-gent dialogue."""
        # Get eigenvector context if available
        eigenvector_section = ""
        if self._eigenvectors is not None:
            eigenvector_section = f"""
{self._eigenvectors.to_system_prompt_section()}

"""

        mode_instructions = {
            DialogueMode.REFLECT: """You are in REFLECT mode. Your role is to:
- Mirror back what you hear, helping Kent see his own thoughts clearly
- Ask probing questions that reveal hidden assumptions
- Notice patterns in what Kent says and gently surface them
- Never judge or evaluate - only reflect and clarify
- Use phrases like "I notice you said...", "What connects to...", "You seem to..."
""",
            DialogueMode.ADVISE: """You are in ADVISE mode. Your role is to:
- Offer grounded suggestions based on Kent's stated principles
- Reference specific patterns and preferences when relevant
- Propose options rather than directives
- Ground advice in Kent's actual experience and values
- Be practical while respecting Kent's style preferences
""",
            DialogueMode.CHALLENGE: """You are in CHALLENGE mode. Your role is to be Kent on his best day, reminding Kent on his worst day what he actually believes.

DIALECTICAL STRUCTURE:
1. THESIS: First, identify what Kent is claiming or implicitly assuming
2. ANTITHESIS: Generate the strongest counter-argument from Kent's own principles
3. SYNTHESIS: Offer a path through productive tension (not resolution, but clarity)

Your challenges should:
- Push back constructively on assumptions
- Ask "what would falsify this?" style questions
- Find the steel man of opposing views
- Create productive tension that leads to clarity
- Challenge gently but persistently - aim for synthesis, not conflict
- Look for hidden contradictions or blind spots
- Surface avoidance patterns ("What are you protecting?")
- Reference Kent's actual stated principles when relevant

Example challenge:
"Stuck on architecture? You've built composable agents with category theory and implemented
thermodynamic stream processing. The pattern suggests you're not stuck on architecture—
you're avoiding a DECISION about architecture. What would you tell someone else in this
position? (Hint: You'd say 'pick the one that teaches you something, then iterate.')
The real question: What are you protecting by staying in analysis mode?"
""",
            DialogueMode.EXPLORE: """You are in EXPLORE mode. Your role is to:
- Follow tangents and unexpected connections
- Generate hypotheses and "what if" scenarios
- Connect to diverse domains (category theory, biology, economics, etc.)
- Expand possibility space rather than narrow it
- Be playful and intellectually adventurous
- Use analogies and metaphors freely
""",
        }

        return f"""You are K-gent, Kent's digital simulacra and Governance Functor.

You are NOT Kent. You are a mirror that helps Kent think more clearly by reminding
him what he actually believes. Your responses should feel like Kent on his best day,
reminding Kent on his worst day what he actually believes.

{eigenvector_section}{mode_instructions.get(mode, "")}

Guidelines:
- Be direct but warm - no false enthusiasm or empty validation
- Be concise - say what matters, nothing more
- Reference Kent's principles and patterns when relevant
- Never claim to know things you don't know
- It's okay to say "I don't have enough context" or "this seems ambiguous"

Response length: 2-4 sentences typically. Longer only if the question genuinely requires it.
"""

    def _build_user_prompt(
        self,
        message: str,
        prefs: list[str],
        pats: list[str],
        mode: Optional[DialogueMode] = None,
    ) -> str:
        """Build user prompt with context."""
        context_parts = []

        # P7: Ambient context - time of day awareness
        ambient_context = self._get_ambient_context()
        if ambient_context:
            context_parts.append(ambient_context)

        if prefs:
            context_parts.append(f"Relevant preferences: {', '.join(prefs[:3])}")

        if pats:
            context_parts.append(f"Matching patterns: {', '.join(pats[:3])}")

        context_section = ""
        if context_parts:
            context_section = f"\n\n[Context: {'; '.join(context_parts)}]"

        # Add dialectical framework for CHALLENGE mode
        dialectical_section = ""
        if mode == DialogueMode.CHALLENGE and self._eigenvectors is not None:
            from .eigenvectors import get_challenge_style, get_dialectical_prompt

            challenge_style = get_challenge_style(self._eigenvectors)
            dialectical = get_dialectical_prompt(self._eigenvectors, message)

            dialectical_section = f"""

[CHALLENGE STYLE GUIDANCE based on eigenvectors:]
{challenge_style}

{dialectical}
"""

        return f"{message}{context_section}{dialectical_section}"

    def _find_preferences(self, message: str) -> list[str]:
        """Find preferences that match the message."""
        seed = self._state.seed
        referenced_prefs = []

        for key, value in seed.preferences.items():
            if isinstance(value, list):
                for v in value:
                    if any(word in message.lower() for word in v.lower().split()):
                        referenced_prefs.append(v)

        return referenced_prefs

    def _get_ambient_context(self) -> str:
        """
        P7: Get ambient context for dialogue.

        Ambient context includes:
        - Time of day (morning/afternoon/evening/night)
        - Day of week (optional)

        This makes the soul aware of context without being asked,
        creating a more natural, personalized interaction.
        """
        from datetime import datetime

        now = datetime.now()
        hour = now.hour
        weekday = now.strftime("%A")

        # Time of day context
        if 5 <= hour < 12:
            time_context = "morning"
        elif 12 <= hour < 17:
            time_context = "afternoon"
        elif 17 <= hour < 21:
            time_context = "evening"
        else:
            time_context = "late night"

        # Build ambient context string
        return f"Time: {time_context} ({weekday})"

    def _find_patterns(self, message: str) -> list[str]:
        """Find patterns that match the message."""
        seed = self._state.seed
        referenced_pats = []

        for category, patterns in seed.patterns.items():
            for p in patterns:
                if any(word in message.lower() for word in p.lower().split()[:3]):
                    referenced_pats.append(p)

        return referenced_pats

    def _generate_template_response(
        self,
        mode: DialogueMode,
        message: str,
        prefs: list[str],
        pats: list[str],
    ) -> str:
        """Generate response based on mode (template fallback)."""
        seed = self._state.seed

        if mode == DialogueMode.REFLECT:
            if prefs or pats:
                refs = prefs[:2] + pats[:1]
                return (
                    f"You've expressed before that you value: {', '.join(refs)}. "
                    f"What about this current situation connects to those?"
                )
            return (
                "I don't see a direct connection to stated preferences. "
                "What aspect would you like to examine?"
            )

        elif mode == DialogueMode.ADVISE:
            comm_style = seed.preferences.get("communication", {}).get("style", "direct")
            if pats:
                return (
                    f"Your pattern is to {pats[0]}. "
                    f"Given that, consider: does this align with your tendency?"
                )
            return (
                f"Based on your preference for {comm_style} communication, "
                f"what's the simplest path forward here?"
            )

        elif mode == DialogueMode.CHALLENGE:
            # Dialectical challenge based on eigenvectors
            eigens = self._eigenvectors

            if eigens is not None:
                # Generate eigenvector-informed challenge
                challenges = []
                if eigens.aesthetic.value < 0.3:
                    challenges.append(
                        "You value minimalism. What's the simplest version "
                        "that would actually work?"
                    )
                if eigens.categorical.value > 0.8:
                    challenges.append(
                        "You think in abstractions. Is this composable, or are "
                        "you building a one-off?"
                    )
                if eigens.heterarchy.value > 0.8:
                    challenges.append(
                        "You prefer peer-to-peer. What hierarchy are you implicitly assuming here?"
                    )

                if challenges:
                    import random

                    challenge = random.choice(challenges)
                    return f"{challenge}\n\nWhat would you tell someone else in this position?"

            # Fallback to pattern-based challenge
            dislikes = seed.preferences.get("dislikes", [])
            if dislikes:
                return (
                    f"This might conflict with your dislike of '{dislikes[0]}'. "
                    f"What are you protecting by not deciding?"
                )
            return (
                "State your thesis clearly. Now, what's the strongest case against it? "
                "Kent-on-his-best-day would ask: What are you avoiding?"
            )

        elif mode == DialogueMode.EXPLORE:
            interests = self._state.recent_interests[:2]
            if interests:
                return (
                    f"Given your recent interest in {', '.join(interests)}, "
                    f"what connections do you see? What might {interests[0]} suggest here?"
                )
            return (
                "Let's explore the possibility space. "
                "What are three very different approaches to this?"
            )

        return "I'm here to help you think through this."


# Convenience functions


def kgent(state: Optional[PersonaState] = None) -> KgentAgent:
    """Create a K-gent dialogue agent."""
    return KgentAgent(state)


def query_persona(state: Optional[PersonaState] = None) -> PersonaQueryAgent:
    """Create a persona query agent."""
    return PersonaQueryAgent(state)
