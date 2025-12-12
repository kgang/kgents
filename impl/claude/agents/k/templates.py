"""
K-gent Templates: Zero-token responses for cost-conscious operation.

Many common patterns can be handled without LLM calls.
This provides the DORMANT and WHISPER level responses.

Philosophy:
    "Always-on" doesn't mean "always-burning-tokens."
    Template responses handle 30% of interactions at zero cost.

Usage:
    result = try_template_response("hello", mode=DialogueMode.REFLECT)
    if result is not None:
        return result  # No LLM needed
    # Fall back to LLM
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .persona import DialogueMode


# --- Mode Transition Templates ---

MODE_TRANSITIONS = {
    "reflect": "Entering REFLECT mode. What pattern are you noticing?",
    "advise": "Entering ADVISE mode. What decision are you facing?",
    "challenge": "Entering CHALLENGE mode. State your thesis.",
    "explore": "Entering EXPLORE mode. Where does your curiosity pull?",
}


# --- Greeting Templates ---

GREETINGS = [
    "What's on your mind?",
    "Ready when you are.",
    "Hello. What shall we examine?",
    "I'm here. What are you working through?",
]

MORNING_GREETINGS = [
    "Good morning. What's the focus today?",
    "Morning. Ready to think?",
    "Good morning. What pattern is emerging?",
]

EVENING_GREETINGS = [
    "Good evening. Reflecting on the day?",
    "Evening. What did you learn today?",
    "Good evening. Time to process?",
]


# --- Session Management Templates ---

SESSION_TEMPLATES = {
    "save": "Session saved to ghost cache. We can pick up here.",
    "saved": "Session saved to ghost cache. We can pick up here.",
    "done": "Session complete. Insights captured.",
    "bye": "Until next time. The patterns will be here.",
    "goodbye": "Until next time. The patterns will be here.",
    "thanks": "Thank you for thinking with me.",
    "thank you": "Thank you for thinking with me.",
}


# --- Reflection Acknowledgments ---

REFLECT_ACKS = [
    "I hear you. What else is there?",
    "Go on. What connects to that?",
    "Interesting. What's underneath that?",
    "Noted. What would you add?",
]


# --- Challenge Prompts ---
# These are Kent-specific: interrupt avoidance, surface contradictions

CHALLENGE_PROMPTS = [
    # Dialectical - surface the thesis/antithesis
    "State your thesis clearly. Now, what's the strongest case against it?",
    "What would falsify that? (You've asked this of others before.)",
    "You prefer reversible decisions. What makes this one feel irreversible?",
    # Eigenvector-informed challenges
    "You value minimalism. What's the simplest version that would still work?",
    "Your pattern is to seek composable abstractions. Is this actually composable?",
    "You've said 'say no more than yes.' What are you saying yes to by default here?",
    # Avoidance detection
    "What are you protecting that doesn't need protection?",
    "What would you tell someone else in this position?",
    "You're good at spotting others' blind spots. What's yours here?",
    # Productive tension
    "Where's the tension between what you believe and what you're doing?",
    "What assumption would Kent-on-his-best-day question?",
    "If you weren't afraid of being wrong, what would you try?",
]


# --- Exploration Prompts ---

EXPLORE_PROMPTS = [
    "What's adjacent to that idea?",
    "And then what?",
    "What would that look like?",
    "Who else has explored this?",
]


# --- Pattern Detection Keywords ---

GREETING_KEYWORDS = frozenset(
    [
        "hello",
        "hi",
        "hey",
        "morning",
        "evening",
        "afternoon",
        "good morning",
        "good evening",
        "good afternoon",
    ]
)

MODE_KEYWORDS = frozenset(
    [
        "reflect",
        "advise",
        "challenge",
        "explore",
        "let's reflect",
        "let's advise",
        "let's challenge",
        "let's explore",
        "challenge me",
        "advise me",
        "help me reflect",
        "help me explore",
    ]
)

SESSION_KEYWORDS = frozenset(
    [
        "save",
        "saved",
        "done",
        "bye",
        "goodbye",
        "thanks",
        "thank you",
        "save this",
        "that's all",
        "all done",
    ]
)


def try_template_response(
    input_text: str,
    mode: Optional["DialogueMode"] = None,
) -> Optional[str]:
    """
    Attempt to respond without LLM call.

    Returns None if LLM is needed, otherwise returns template response.

    This is the DORMANT level of K-gent—zero tokens until triggered.
    """
    normalized = input_text.lower().strip()

    # Check for greetings
    if _is_greeting(normalized):
        return _greeting_response(normalized)

    # Check for mode transitions
    mode_response = _check_mode_transition(normalized)
    if mode_response:
        return mode_response

    # Check for session management
    session_response = _check_session_keywords(normalized)
    if session_response:
        return session_response

    # Check for short acknowledgment prompts
    if len(normalized) < 20 and mode is not None:
        from .persona import DialogueMode

        if mode == DialogueMode.REFLECT:
            return random.choice(REFLECT_ACKS)
        elif mode == DialogueMode.CHALLENGE:
            return random.choice(CHALLENGE_PROMPTS)
        elif mode == DialogueMode.EXPLORE:
            return random.choice(EXPLORE_PROMPTS)

    # No template match—LLM needed
    return None


def _is_greeting(text: str) -> bool:
    """Check if text is a greeting."""
    words = set(text.split())
    return bool(words & GREETING_KEYWORDS) or text in GREETING_KEYWORDS


def _greeting_response(text: str) -> str:
    """Generate greeting response."""
    if "morning" in text:
        return random.choice(MORNING_GREETINGS)
    elif "evening" in text:
        return random.choice(EVENING_GREETINGS)
    return random.choice(GREETINGS)


def _check_mode_transition(text: str) -> Optional[str]:
    """Check for mode transition keywords."""
    for mode_key, response in MODE_TRANSITIONS.items():
        if mode_key in text:
            return response
    return None


def _check_session_keywords(text: str) -> Optional[str]:
    """Check for session management keywords."""
    for keyword, response in SESSION_TEMPLATES.items():
        if keyword in text:
            return response
    return None


# --- Budget-Aware Response Selection ---


def get_whisper_response(input_text: str) -> str:
    """
    Generate a WHISPER-level response (~100 tokens).

    Used for quick check-ins that don't need deep LLM reasoning.
    """
    # Try template first
    template = try_template_response(input_text)
    if template:
        return template

    # Generate minimal acknowledgment
    return "I hear you. Tell me more—or shall we go deeper?"


def should_use_template(input_text: str) -> bool:
    """
    Check if input can be handled by template (no LLM needed).
    """
    return try_template_response(input_text) is not None
