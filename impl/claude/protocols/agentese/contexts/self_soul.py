"""
AGENTESE Self Soul Context: K-gent Soul Integration

The self.soul context provides access to K-gent Soul, including:
- self.soul.manifest - View soul state
- self.soul.dialogue - Direct dialogue (legacy)
- self.soul.chat.* - Chat protocol affordances (NEW)
- self.soul.challenge - Challenge assumptions
- self.soul.reflect - Reflective dialogue

The chat affordances are the primary interface for conversation
with K-gent, integrating with the Chat Protocol for:
- Turn management
- Context window management
- Session persistence
- Budget tracking

AGENTESE: self.soul.*

Principle Alignment:
- Ethical: K-gent augments human judgment
- Joy-Inducing: Personality eigenvectors
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..affordances import (
    CHAT_AFFORDANCES,
    AspectCategory,
    Effect,
    aspect,
    chatty,
)
from ..node import BaseLogosNode, BasicRendering, Renderable
from .chat_resolver import ChatNode, create_chat_node

if TYPE_CHECKING:
    from agents.k.soul import KgentSoul
    from bootstrap.umwelt import Umwelt


# Soul affordances
SOUL_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "dialogue",
    "challenge",
    "reflect",
    "why",
    "tension",
    "starters",
    "eigenvectors",
    "mode",
    # Chat affordances are accessed via self.soul.chat.*
)

# Soul + chat combined (for introspection)
SOUL_CHAT_AFFORDANCES: tuple[str, ...] = SOUL_AFFORDANCES + ("chat",)


@chatty(
    context_window=16000,
    context_strategy="summarize",
    persist_history=True,
    inject_memories=True,
    memory_recall_limit=5,
    entropy_budget=1.0,
    entropy_decay_per_turn=0.02,
)
@dataclass
class SoulNode(BaseLogosNode):
    """
    self.soul - K-gent Soul interface.

    The soul node provides access to K-gent Soul for:
    - Dialogue (legacy and chat protocol)
    - Challenge (assumption challenging)
    - Reflection (introspection)
    - Personality eigenvectors

    Chat is the primary interface, accessed via self.soul.chat.*
    """

    _handle: str = "self.soul"

    # K-gent Soul instance (injected)
    _soul: "KgentSoul | None" = None

    # Chat node (lazy-initialized)
    _chat_node: ChatNode | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Soul affordances available to all archetypes."""
        return SOUL_CHAT_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View soul state."""
        if self._soul is None:
            return BasicRendering(
                summary="K-gent Soul",
                content="Soul not initialized. Use `kg soul init` first.",
                metadata={"status": "uninitialized"},
            )

        # Get eigenvectors
        eigenvectors = self._soul.eigenvectors

        return BasicRendering(
            summary="K-gent Soul",
            content=(
                f"Mode: {self._soul.active_mode.value}\n"
                f"Has LLM: {self._soul.has_llm}\n"
                f"Aesthetic: {eigenvectors.aesthetic.value:.2f}\n"
                f"Categorical: {eigenvectors.categorical.value:.2f}\n"
                f"Gratitude: {eigenvectors.gratitude.value:.2f}"
            ),
            metadata={
                "mode": self._soul.active_mode.value,
                "has_llm": self._soul.has_llm,
                "eigenvectors": {
                    "aesthetic": eigenvectors.aesthetic.value,
                    "categorical": eigenvectors.categorical.value,
                    "gratitude": eigenvectors.gratitude.value,
                    "heterarchy": eigenvectors.heterarchy.value,
                    "generativity": eigenvectors.generativity.value,
                    "joy": eigenvectors.joy.value,
                },
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle soul-specific aspects."""
        match aspect:
            case "dialogue":
                return await self._dialogue(observer, **kwargs)
            case "challenge":
                return await self._challenge(observer, **kwargs)
            case "reflect":
                return await self._reflect(observer, **kwargs)
            case "why":
                return await self._why(observer, **kwargs)
            case "tension":
                return await self._tension(observer, **kwargs)
            case "starters":
                return await self._get_starters(observer, **kwargs)
            case "eigenvectors":
                return await self._get_eigenvectors(observer, **kwargs)
            case "mode":
                return await self._get_or_set_mode(observer, **kwargs)
            case "chat":
                # Return the chat node for sub-resolution
                return self._get_chat_node()
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    def _get_chat_node(self) -> ChatNode:
        """Get or create the chat node for this soul."""
        if self._chat_node is None:
            self._chat_node = create_chat_node(
                parent_path="self.soul",
                parent_node=self,
            )
        return self._chat_node

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
        help="Direct dialogue with K-gent (legacy, prefer chat.*)",
        examples=["self.soul.dialogue[message='Hello']"],
        budget_estimate="~500 tokens",
    )
    async def _dialogue(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Direct dialogue with K-gent Soul.

        This is the legacy interface. Prefer self.soul.chat.send for
        turn-based conversation with context management.

        Args:
            message: The message to send
            mode: Optional dialogue mode (challenge, reflect, etc.)

        Returns:
            Dict with response and metadata
        """
        message = kwargs.get("message")
        if not message:
            return {"error": "message required"}

        if self._soul is None:
            return {"error": "Soul not initialized", "note": "Use kg soul init"}

        mode_str = kwargs.get("mode")
        mode = None
        if mode_str:
            from agents.k.persona import DialogueMode

            try:
                mode = DialogueMode(mode_str)
            except ValueError:
                pass

        output = await self._soul.dialogue(message, mode=mode)

        return {
            "response": output.response,
            "mode": output.mode.value,
            "tokens_used": output.tokens_used,
            "was_template": output.was_template,
            "budget_tier": output.budget_tier.value,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
        help="Challenge assumptions with K-gent",
        examples=["self.soul.challenge[message='What am I avoiding?']"],
        budget_estimate="~800 tokens",
    )
    async def _challenge(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Challenge assumptions with K-gent."""
        message = kwargs.get("message")
        if not message:
            return {"error": "message required"}

        if self._soul is None:
            return {"error": "Soul not initialized"}

        from agents.k.persona import DialogueMode

        output = await self._soul.dialogue(message, mode=DialogueMode.CHALLENGE)

        return {
            "response": output.response,
            "mode": "challenge",
            "tokens_used": output.tokens_used,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
        help="Reflective dialogue with K-gent",
        examples=["self.soul.reflect[message='How am I doing?']"],
        budget_estimate="~600 tokens",
    )
    async def _reflect(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Reflective dialogue with K-gent."""
        message = kwargs.get("message")
        if not message:
            return {"error": "message required"}

        if self._soul is None:
            return {"error": "Soul not initialized"}

        from agents.k.persona import DialogueMode

        output = await self._soul.dialogue(message, mode=DialogueMode.REFLECT)

        return {
            "response": output.response,
            "mode": "reflect",
            "tokens_used": output.tokens_used,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
        help="Explore the deeper purpose behind something",
        long_help="Keep asking 'why' until you reach core values or first principles.",
        examples=["self.soul.why[message='Why am I working on this?']"],
        budget_estimate="~600 tokens",
    )
    async def _why(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Explore purpose and meaning through iterative 'why' questioning.

        AGENTESE: self.soul.why

        The 'why' aspect helps surface deeper motivations and values.
        Each response probes one level deeper into purpose.
        """
        message = kwargs.get("message") or kwargs.get("topic")
        if not message:
            return {
                "error": "message or topic required",
                "hint": "What would you like to understand the purpose of?",
            }

        if self._soul is None:
            return {"error": "Soul not initialized"}

        from agents.k.persona import DialogueMode

        # Use reflect mode with a why-focused prompt
        why_prompt = f"Help me explore the deeper 'why' behind this: {message}\n\nKeep probing until we reach something meaningful."
        output = await self._soul.dialogue(why_prompt, mode=DialogueMode.REFLECT)

        return {
            "response": output.response,
            "mode": "why",
            "depth": "exploring purpose",
            "tokens_used": output.tokens_used,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
        help="Surface and hold creative tension",
        long_help="Name the opposing forces at play without rushing to resolve them.",
        examples=["self.soul.tension[message='What tensions am I holding?']"],
        budget_estimate="~600 tokens",
    )
    async def _tension(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Surface the creative tensions in a situation.

        AGENTESE: self.soul.tension

        The 'tension' aspect helps name opposing forces at play.
        It doesn't resolve - it holds space for productive friction.
        """
        message = kwargs.get("message") or kwargs.get("topic")
        if not message:
            return {
                "error": "message or topic required",
                "hint": "What situation's tensions would you like to explore?",
            }

        if self._soul is None:
            return {"error": "Soul not initialized"}

        from agents.k.persona import DialogueMode

        # Use challenge mode with tension-focused prompt
        tension_prompt = f"Help me name the creative tensions at play here: {message}\n\nDon't resolve them - just name them clearly so I can hold them."
        output = await self._soul.dialogue(tension_prompt, mode=DialogueMode.CHALLENGE)

        return {
            "response": output.response,
            "mode": "tension",
            "holding_space": True,
            "tokens_used": output.tokens_used,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("soul_state")],
        help="Get mode-specific conversation starters",
        examples=["self.soul.starters", "self.soul.starters[mode=challenge]"],
    )
    async def _get_starters(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get conversation starters for a mode."""
        mode_str = kwargs.get("mode")

        from agents.k.starters import get_starters

        if mode_str:
            from agents.k.persona import DialogueMode

            try:
                mode = DialogueMode(mode_str)
                starters = get_starters(mode)
                return {"mode": mode.value, "starters": starters}
            except ValueError:
                return {"error": f"Invalid mode: {mode_str}"}

        # Return all starters by mode
        from agents.k.persona import DialogueMode

        all_starters = {}
        for mode in DialogueMode:
            all_starters[mode.value] = get_starters(mode)

        return {"starters": all_starters}

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("soul_state")],
        help="Get personality eigenvectors",
        examples=["self.soul.eigenvectors"],
    )
    async def _get_eigenvectors(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get personality eigenvectors."""
        if self._soul is None:
            from agents.k.eigenvectors import KENT_EIGENVECTORS

            ev = KENT_EIGENVECTORS
        else:
            ev = self._soul.eigenvectors

        return {
            "aesthetic": ev.aesthetic.value,
            "categorical": ev.categorical.value,
            "gratitude": ev.gratitude.value,
            "heterarchy": ev.heterarchy.value,
            "generativity": ev.generativity.value,
            "joy": ev.joy.value,
        }

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("soul_state")],
        help="Get or set dialogue mode",
        examples=["self.soul.mode", "self.soul.mode[set=challenge]"],
    )
    async def _get_or_set_mode(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Get or set the current dialogue mode."""
        set_mode = kwargs.get("set")

        if self._soul is None:
            return {"error": "Soul not initialized"}

        if set_mode:
            from agents.k.persona import DialogueMode

            try:
                mode = DialogueMode(set_mode)
                self._soul.active_mode = mode
                return {"mode": mode.value, "status": "set"}
            except ValueError:
                return {"error": f"Invalid mode: {set_mode}"}

        return {"mode": self._soul.active_mode.value}


# Factory function
def create_soul_node(
    soul: "KgentSoul | None" = None,
) -> SoulNode:
    """
    Create a SoulNode with optional K-gent Soul injection.

    Args:
        soul: K-gent Soul instance (optional)

    Returns:
        Configured SoulNode
    """
    return SoulNode(_soul=soul)


__all__ = [
    "SoulNode",
    "SOUL_AFFORDANCES",
    "SOUL_CHAT_AFFORDANCES",
    "create_soul_node",
]
