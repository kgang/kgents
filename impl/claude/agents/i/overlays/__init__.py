"""Overlay modules for kgents dashboard."""

from .chat import AgentChatPanel, ChatMessage, ExplanationContext, MessageRole
from .fever import (
    EntropyGauge,
    EntropyState,
    FeverOverlay,
    ObliqueDisplay,
    create_fever_overlay,
    should_show_fever_overlay,
)

__all__ = [
    # Chat
    "AgentChatPanel",
    "ChatMessage",
    "ExplanationContext",
    "MessageRole",
    # Fever
    "EntropyGauge",
    "EntropyState",
    "FeverOverlay",
    "ObliqueDisplay",
    "create_fever_overlay",
    "should_show_fever_overlay",
]
