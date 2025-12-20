"""
AGENTESE Phase 8: Natural Language → AGENTESE Adapter

This module provides the final piece of the AGENTESE architecture:
translation from natural language queries to AGENTESE paths.

┌─────────────────────────────────────────────────────────────────────────────┐
│                         ADAPTER ARCHITECTURE                                 │
│                                                                              │
│   User Input: "Show me the house"                                           │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │  PatternTranslator  │  ← Rule-based patterns (fast, no LLM)             │
│   │   (Fast Path)       │    "show me" → manifest, "what happened" → witness │
│   └─────────────────────┘                                                    │
│          │ (if no match)                                                     │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │   LLMTranslator     │  ← LLM-based translation (slow, fallback)         │
│   │    (Slow Path)      │    Few-shot prompting with examples               │
│   └─────────────────────┘                                                    │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │  GgentIntegration   │  ← Validates output is valid AGENTESE             │
│   │    (Validation)     │                                                    │
│   └─────────────────────┘                                                    │
│          │                                                                   │
│          ▼                                                                   │
│   ┌─────────────────────┐                                                    │
│   │      WiredLogos     │  ← Execute the translated path                    │
│   │     (Execution)     │                                                    │
│   └─────────────────────┘                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

Key Design Principle: Fast path first, LLM only when needed.
The pattern translator handles common queries instantly, while the
LLM translator provides flexibility for complex natural language.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from .exceptions import (
    AgentesError,
)
from .integration import GgentIntegration

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Translation Result Types
# =============================================================================


@dataclass(frozen=True)
class TranslationResult:
    """
    Result of translating natural language to AGENTESE.

    Captures the translation path for debugging and learning.
    """

    path: str
    """The translated AGENTESE path."""

    confidence: float
    """Confidence in the translation (0.0 to 1.0)."""

    source: str
    """How the translation was performed: 'pattern', 'llm', or 'fallback'."""

    original_input: str
    """The original natural language input."""

    matched_pattern: str | None = None
    """If pattern-based, which pattern matched."""

    extracted_entities: dict[str, str] = field(default_factory=dict)
    """Entities extracted from input (e.g., holon name)."""


@dataclass
class TranslationError(AgentesError):
    """
    Raised when translation fails.

    Sympathetic error that suggests alternatives.
    """

    input: str
    """The input that couldn't be translated."""

    reason: str
    """Why translation failed."""

    suggestions: list[str] = field(default_factory=list)
    """Suggested rephrasing or direct AGENTESE paths."""

    def __str__(self) -> str:
        msg = f"Could not translate: '{self.input}'\n\n"
        msg += f"  Reason: {self.reason}\n"
        if self.suggestions:
            msg += "\n  Try one of these:\n"
            for suggestion in self.suggestions[:5]:
                msg += f"    - {suggestion}\n"
        msg += "\n  (You can also use AGENTESE directly: world.house.manifest)"
        return msg


# =============================================================================
# Translation Patterns
# =============================================================================


# Pattern → (context, aspect_hint, confidence)
# These patterns handle common natural language queries
# NOTE: More specific patterns MUST come before more general ones
TRANSLATION_PATTERNS: list[tuple[re.Pattern[str], str, str, float]] = [
    # History/logs patterns - MUST BE BEFORE generic "show me X" patterns
    (
        re.compile(r"^show\s+me\s+(?:the\s+)?logs?$", re.I),
        "time.trace.witness",
        "witness",
        0.95,
    ),
    (
        re.compile(r"^show\s+(?:the\s+)?logs?$", re.I),
        "time.trace.witness",
        "witness",
        0.9,
    ),
    (
        re.compile(r"^what\s+happened\s+(?:to\s+)?(?:the\s+)?(\w+)\??$", re.I),
        "world.{entity}.witness",
        "witness",
        0.9,
    ),
    (
        re.compile(r"^history\s+(?:of\s+)?(?:the\s+)?(\w+)$", re.I),
        "world.{entity}.witness",
        "witness",
        0.85,
    ),
    (
        re.compile(r"^trace\s+(?:the\s+)?(\w+)$", re.I),
        "time.trace.witness",
        "witness",
        0.9,
    ),
    (
        re.compile(r"^what\s+happened\s+yesterday\??$", re.I),
        "time.past.project",
        "project",
        0.85,
    ),
    # Perception verbs → manifest (generic patterns after specific ones)
    (
        re.compile(r"^show\s+me\s+(?:the\s+)?(\w+)$", re.I),
        "world.{entity}.manifest",
        "manifest",
        0.9,
    ),
    (
        re.compile(r"^show\s+(?:the\s+)?(\w+)$", re.I),
        "world.{entity}.manifest",
        "manifest",
        0.85,
    ),
    (
        re.compile(r"^get\s+(?:the\s+)?(\w+)$", re.I),
        "world.{entity}.manifest",
        "manifest",
        0.85,
    ),
    (
        re.compile(r"^view\s+(?:the\s+)?(\w+)$", re.I),
        "world.{entity}.manifest",
        "manifest",
        0.85,
    ),
    (
        re.compile(r"^display\s+(?:the\s+)?(\w+)$", re.I),
        "world.{entity}.manifest",
        "manifest",
        0.85,
    ),
    (
        re.compile(r"^what\s+is\s+(?:the\s+)?(\w+)\??$", re.I),
        "world.{entity}.manifest",
        "manifest",
        0.8,
    ),
    (
        re.compile(r"^describe\s+(?:the\s+)?(\w+)$", re.I),
        "world.{entity}.manifest",
        "manifest",
        0.85,
    ),
    # Memory verbs → self.*
    (
        re.compile(r"^(?:show\s+)?(?:my\s+)?memory$", re.I),
        "self.memory.manifest",
        "manifest",
        0.9,
    ),
    (re.compile(r"^recall\s+(.+)$", re.I), "self.memory.manifest", "manifest", 0.8),
    (
        re.compile(r"^consolidate\s+(?:my\s+)?(?:thoughts?|memory)$", re.I),
        "self.memory.consolidate",
        "consolidate",
        0.9,
    ),
    (
        re.compile(r"^sort\s+(?:my\s+)?thoughts?$", re.I),
        "self.memory.consolidate",
        "consolidate",
        0.85,
    ),
    (re.compile(r"^dream$", re.I), "self.memory.consolidate", "consolidate", 0.9),
    (
        re.compile(r"^what\s+can\s+i\s+do\??$", re.I),
        "self.capabilities.affordances",
        "affordances",
        0.9,
    ),
    (
        re.compile(r"^my\s+capabilities$", re.I),
        "self.capabilities.affordances",
        "affordances",
        0.85,
    ),
    # Concept verbs → concept.*
    (
        re.compile(r"^think\s+(?:about|harder\s+about)\s+(\w+)$", re.I),
        "concept.{entity}.refine",
        "refine",
        0.9,
    ),
    (
        re.compile(r"^refine\s+(?:the\s+)?(?:concept\s+(?:of\s+)?)?(\w+)$", re.I),
        "concept.{entity}.refine",
        "refine",
        0.9,
    ),
    (
        re.compile(r"^challenge\s+(?:the\s+)?(?:idea\s+(?:of\s+)?)?(\w+)$", re.I),
        "concept.{entity}.refine",
        "refine",
        0.85,
    ),
    (re.compile(r"^define\s+(\w+)$", re.I), "concept.{entity}.define", "define", 0.85),
    (
        re.compile(r"^what\s+is\s+(?:the\s+)?(?:concept\s+(?:of\s+)?)?(\w+)\??$", re.I),
        "concept.{entity}.manifest",
        "manifest",
        0.75,
    ),
    # Entropy verbs → void.*
    (
        re.compile(r"^give\s+me\s+(?:some(?:thing)?\s+)?random(?:ness)?$", re.I),
        "void.entropy.sip",
        "sip",
        0.9,
    ),
    (
        re.compile(r"^(?:some\s+)?random(?:ness)?$", re.I),
        "void.entropy.sip",
        "sip",
        0.85,
    ),
    (
        re.compile(r"^sip\s+(?:from\s+)?(?:the\s+)?(?:void|entropy)$", re.I),
        "void.entropy.sip",
        "sip",
        0.95,
    ),
    (re.compile(r"^surprise\s+me$", re.I), "void.serendipity.sip", "sip", 0.85),
    (re.compile(r"^tithe$", re.I), "void.gratitude.tithe", "tithe", 0.95),
    (re.compile(r"^thank(?:s|\s+you)?$", re.I), "void.gratitude.thank", "thank", 0.9),
    (re.compile(r"^express\s+gratitude$", re.I), "void.gratitude.thank", "thank", 0.9),
    # Temporal verbs → time.*
    (
        re.compile(r"^(?:show\s+)?(?:the\s+)?past\s+(?:state\s+(?:of\s+)?)?(\w+)?$", re.I),
        "time.past.project",
        "project",
        0.85,
    ),
    (
        re.compile(r"^forecast\s+(?:the\s+)?(\w+)?$", re.I),
        "time.future.forecast",
        "forecast",
        0.85,
    ),
    (
        re.compile(r"^predict\s+(?:the\s+)?(?:future\s+(?:of\s+)?)?(\w+)?$", re.I),
        "time.future.forecast",
        "forecast",
        0.8,
    ),
    (re.compile(r"^schedule\s+(.+)$", re.I), "time.schedule.defer", "defer", 0.85),
    # Server/system status (common IT patterns)
    (
        re.compile(r"^(?:get\s+)?server\s+status$", re.I),
        "world.server.manifest",
        "manifest",
        0.9,
    ),
    (
        re.compile(r"^(?:check\s+)?system\s+(?:health|status)$", re.I),
        "world.system.manifest",
        "manifest",
        0.9,
    ),
    (
        re.compile(r"^(?:show\s+)?(?:the\s+)?status$", re.I),
        "world.project.manifest",
        "manifest",
        0.8,
    ),
    # Creation verbs
    (
        re.compile(r"^create\s+(?:a\s+)?(?:new\s+)?(\w+)$", re.I),
        "world.{entity}.define",
        "define",
        0.85,
    ),
    (
        re.compile(r"^add\s+(?:a\s+)?(?:new\s+)?(\w+)$", re.I),
        "world.{entity}.define",
        "define",
        0.8,
    ),
]


# LLM few-shot examples for translation
LLM_TRANSLATION_EXAMPLES: list[tuple[str, str]] = [
    # Perception
    ("show me the house", "world.house.manifest"),
    ("get server status", "world.server.manifest"),
    ("what is the project", "world.project.manifest"),
    ("describe the library", "world.library.manifest"),
    # History
    ("what happened to the house", "world.house.witness"),
    ("show me the logs", "time.trace.witness"),
    ("trace authentication", "time.trace.witness"),
    ("what happened yesterday", "time.past.project"),
    # Memory
    ("show my memory", "self.memory.manifest"),
    ("dream", "self.memory.consolidate"),
    ("sort my thoughts", "self.memory.consolidate"),
    ("what can I do", "self.capabilities.affordances"),
    # Concepts
    ("think harder about justice", "concept.justice.refine"),
    ("refine the concept of fairness", "concept.fairness.refine"),
    ("define love", "concept.love.define"),
    # Entropy
    ("give me something random", "void.entropy.sip"),
    ("surprise me", "void.serendipity.sip"),
    ("tithe", "void.gratitude.tithe"),
    ("thanks", "void.gratitude.thank"),
    # Temporal
    ("forecast the weather", "time.future.forecast"),
    ("schedule a meeting", "time.schedule.defer"),
    ("show the past state", "time.past.project"),
    # Creation
    ("create a new garden", "world.garden.define"),
    ("add a user", "world.user.define"),
]


# =============================================================================
# Translator Protocols
# =============================================================================


@runtime_checkable
class Translator(Protocol):
    """Protocol for translation strategies."""

    def translate(
        self, input: str, context: dict[str, Any] | None = None
    ) -> TranslationResult | None:
        """
        Translate natural language to AGENTESE.

        Args:
            input: Natural language input
            context: Optional context (previous paths, observer info)

        Returns:
            TranslationResult if successful, None if cannot translate
        """
        ...


@runtime_checkable
class AsyncTranslator(Protocol):
    """Protocol for async translation strategies (LLM)."""

    async def translate(
        self, input: str, context: dict[str, Any] | None = None
    ) -> TranslationResult | None:
        """Async translation (for LLM calls)."""
        ...


# =============================================================================
# Pattern-Based Translator (Fast Path)
# =============================================================================


@dataclass
class PatternTranslator:
    """
    Rule-based pattern translator.

    The fast path for common queries. No LLM needed.

    Example:
        >>> translator = PatternTranslator()
        >>> result = translator.translate("show me the house")
        >>> result.path
        'world.house.manifest'
        >>> result.confidence
        0.9
    """

    patterns: list[tuple[re.Pattern[str], str, str, float]] = field(
        default_factory=lambda: TRANSLATION_PATTERNS.copy()
    )

    def translate(
        self, input: str, context: dict[str, Any] | None = None
    ) -> TranslationResult | None:
        """
        Translate using pattern matching.

        Args:
            input: Natural language input (normalized)
            context: Optional context (unused in pattern matching)

        Returns:
            TranslationResult if a pattern matches, None otherwise
        """
        normalized = input.strip()

        for pattern, template, aspect, confidence in self.patterns:
            match = pattern.match(normalized)
            if match:
                # Extract entity from capture groups
                groups = match.groups()
                entity = None
                extracted = {}

                for group in groups:
                    if group and group.lower() not in ("me", "the", "a", "an"):
                        entity = group.lower()
                        extracted["entity"] = entity
                        break

                # Build path from template
                if "{entity}" in template:
                    if entity:
                        path = template.replace("{entity}", entity)
                    else:
                        # No entity captured, can't complete the path
                        continue
                else:
                    path = template

                return TranslationResult(
                    path=path,
                    confidence=confidence,
                    source="pattern",
                    original_input=input,
                    matched_pattern=pattern.pattern,
                    extracted_entities=extracted,
                )

        return None

    def add_pattern(
        self,
        pattern: str,
        template: str,
        aspect: str = "manifest",
        confidence: float = 0.8,
    ) -> None:
        """
        Add a custom translation pattern.

        Args:
            pattern: Regex pattern (with optional capture group for entity)
            template: AGENTESE template (use {entity} for captured entity)
            aspect: The aspect being invoked
            confidence: Confidence score for this pattern
        """
        self.patterns.append((re.compile(pattern, re.I), template, aspect, confidence))


# =============================================================================
# LLM-Based Translator (Slow Path)
# =============================================================================


@runtime_checkable
class LLMProtocol(Protocol):
    """Protocol for LLM invocation."""

    async def complete(self, prompt: str) -> str:
        """Complete a prompt and return the response."""
        ...


def build_translation_prompt(
    input: str,
    examples: list[tuple[str, str]] | None = None,
    context: dict[str, Any] | None = None,
) -> str:
    """
    Build the few-shot prompt for LLM translation.

    Args:
        input: The natural language input to translate
        examples: Few-shot examples (defaults to LLM_TRANSLATION_EXAMPLES)
        context: Optional context to include

    Returns:
        Formatted prompt string
    """
    examples = examples or LLM_TRANSLATION_EXAMPLES

    prompt = """You are an AGENTESE translator. Convert natural language to AGENTESE paths.

AGENTESE paths follow this format: <context>.<holon>.<aspect>

Valid contexts:
- world.*  : External entities, environments, resources
- self.*   : Internal: memory, capability, state
- concept.*: Abstract: platonics, definitions, logic
- void.*   : Accursed Share: entropy, serendipity, gratitude
- time.*   : Temporal: traces, forecasts, schedules

Common aspects:
- manifest : Perceive/view something
- witness  : View history/traces
- refine   : Think harder/challenge
- define   : Create new
- sip      : Draw from entropy
- tithe    : Express gratitude

Examples:
"""

    for nl, agentese in examples[:15]:  # Limit examples
        prompt += f"Input: {nl}\nOutput: {agentese}\n\n"

    if context:
        prompt += f"\nContext: {context}\n"

    prompt += f"""
Input: {input}
Output:"""

    return prompt


@dataclass
class LLMTranslator:
    """
    LLM-based translator for complex queries.

    The slow path when pattern matching fails. Uses few-shot
    prompting to translate natural language to AGENTESE.

    Example:
        >>> translator = LLMTranslator(llm=my_llm)
        >>> result = await translator.translate("Check if the authentication system is healthy")
        >>> result.path
        'world.authentication.manifest'
    """

    llm: LLMProtocol | None = None
    examples: list[tuple[str, str]] = field(default_factory=lambda: LLM_TRANSLATION_EXAMPLES.copy())
    validator: GgentIntegration = field(default_factory=GgentIntegration)

    async def translate(
        self, input: str, context: dict[str, Any] | None = None
    ) -> TranslationResult | None:
        """
        Translate using LLM.

        Args:
            input: Natural language input
            context: Optional context for the LLM

        Returns:
            TranslationResult if successful, None if LLM unavailable or fails
        """
        if self.llm is None:
            return None

        prompt = build_translation_prompt(input, self.examples, context)

        try:
            response = await self.llm.complete(prompt)
            path = response.strip().split("\n")[0].strip()

            # Validate the path
            is_valid, error = self.validator.validate_path(path)
            if not is_valid:
                return None

            return TranslationResult(
                path=path,
                confidence=0.7,  # LLM translations have lower confidence
                source="llm",
                original_input=input,
            )

        except Exception:
            return None

    def add_example(self, natural_language: str, agentese_path: str) -> None:
        """Add a training example."""
        self.examples.append((natural_language, agentese_path))


# =============================================================================
# Unified Adapter
# =============================================================================


@dataclass
class AgentesAdapter:
    """
    Unified adapter for natural language → AGENTESE translation.

    Orchestrates pattern and LLM translators, with validation.

    Example:
        >>> adapter = create_adapter(wired_logos)
        >>> result = await adapter.execute("show me the house", observer)
        >>> # Automatically translated to world.house.manifest and invoked

    The adapter follows a priority chain:
    1. Pattern matching (fast, deterministic)
    2. LLM translation (slow, flexible)
    3. Fallback suggestions (helpful error)
    """

    logos: Any  # WiredLogos (avoid circular import)
    pattern_translator: PatternTranslator = field(default_factory=PatternTranslator)
    llm_translator: LLMTranslator = field(default_factory=LLMTranslator)
    validator: GgentIntegration = field(default_factory=GgentIntegration)

    # === Configuration ===
    min_confidence: float = 0.5
    """Minimum confidence threshold for accepting translations."""

    use_llm_fallback: bool = True
    """Whether to use LLM when pattern matching fails."""

    async def translate(
        self, input: str, context: dict[str, Any] | None = None
    ) -> TranslationResult:
        """
        Translate natural language to AGENTESE.

        Args:
            input: Natural language input
            context: Optional context

        Returns:
            TranslationResult with the translated path

        Raises:
            TranslationError: If translation fails
        """
        normalized = input.strip()

        # Check if input is already AGENTESE
        if self._is_agentese(normalized):
            return TranslationResult(
                path=normalized,
                confidence=1.0,
                source="direct",
                original_input=input,
            )

        # Try pattern matching first (fast path)
        result = self.pattern_translator.translate(normalized, context)
        if result and result.confidence >= self.min_confidence:
            return result

        # Try LLM translation (slow path)
        if self.use_llm_fallback:
            result = await self.llm_translator.translate(normalized, context)
            if result and result.confidence >= self.min_confidence:
                return result

        # Generate helpful error
        raise TranslationError(
            input=input,
            reason="No matching pattern and LLM translation failed or unavailable",
            suggestions=self._generate_suggestions(normalized),
        )

    async def execute(
        self,
        input: str,
        observer: "Umwelt[Any, Any]",
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Translate and execute in one step.

        Args:
            input: Natural language input OR AGENTESE path
            observer: Observer Umwelt
            context: Optional translation context
            **kwargs: Additional arguments for invoke

        Returns:
            Result of AGENTESE invocation
        """
        result = await self.translate(input, context)
        return await self.logos.invoke(result.path, observer, **kwargs)

    def _is_agentese(self, input: str) -> bool:
        """Check if input is already valid AGENTESE."""
        is_valid, _ = self.validator.validate_path(input)
        return is_valid

    def _generate_suggestions(self, input: str) -> list[str]:
        """Generate helpful suggestions for failed translation."""
        suggestions = []

        # Suggest based on keywords
        keywords = input.lower().split()

        if any(w in keywords for w in ("show", "get", "view", "see", "display")):
            suggestions.append("Try: 'show me the <entity>' → world.<entity>.manifest")
        if any(w in keywords for w in ("history", "happened", "trace", "log")):
            suggestions.append("Try: 'what happened to <entity>' → world.<entity>.witness")
        if any(w in keywords for w in ("memory", "recall", "remember")):
            suggestions.append("Try: 'show my memory' → self.memory.manifest")
        if any(w in keywords for w in ("think", "refine", "challenge")):
            suggestions.append("Try: 'think about <concept>' → concept.<concept>.refine")
        if any(w in keywords for w in ("random", "surprise", "entropy")):
            suggestions.append("Try: 'give me randomness' → void.entropy.sip")

        # Always suggest direct AGENTESE
        suggestions.append("Or use AGENTESE directly: world.<entity>.manifest")

        return suggestions


# =============================================================================
# Factory Functions
# =============================================================================


def create_adapter(
    logos: Any = None,
    llm: LLMProtocol | None = None,
    min_confidence: float = 0.5,
    use_llm_fallback: bool = True,
) -> AgentesAdapter:
    """
    Create an AGENTESE adapter.

    Args:
        logos: WiredLogos resolver (optional, can be set later)
        llm: LLM for fallback translation (optional)
        min_confidence: Minimum confidence threshold
        use_llm_fallback: Whether to use LLM when patterns fail

    Returns:
        Configured AgentesAdapter
    """
    return AgentesAdapter(
        logos=logos,
        pattern_translator=PatternTranslator(),
        llm_translator=LLMTranslator(llm=llm),
        min_confidence=min_confidence,
        use_llm_fallback=use_llm_fallback,
    )


def create_pattern_translator(
    extra_patterns: list[tuple[str, str, str, float]] | None = None,
) -> PatternTranslator:
    """
    Create a pattern translator with optional extra patterns.

    Args:
        extra_patterns: Additional (regex, template, aspect, confidence) tuples

    Returns:
        Configured PatternTranslator
    """
    translator = PatternTranslator()
    if extra_patterns:
        for pattern, template, aspect, confidence in extra_patterns:
            translator.add_pattern(pattern, template, aspect, confidence)
    return translator


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Result types
    "TranslationResult",
    "TranslationError",
    # Constants
    "TRANSLATION_PATTERNS",
    "LLM_TRANSLATION_EXAMPLES",
    # Protocols
    "Translator",
    "AsyncTranslator",
    "LLMProtocol",
    # Translators
    "PatternTranslator",
    "LLMTranslator",
    # Adapter
    "AgentesAdapter",
    # Factory functions
    "create_adapter",
    "create_pattern_translator",
    "build_translation_prompt",
]
