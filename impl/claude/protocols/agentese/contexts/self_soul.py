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
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node
from .chat_resolver import ChatNode, create_chat_node
from .soul_contracts import (
    ChallengeRequest,
    ChallengeResponse,
    DialogueRequest,
    DialogueResponse,
    EigenvectorsResponse,
    GovernanceRequest,
    GovernanceResponse,
    ModeRequest,
    ModeResponse,
    ReflectRequest,
    ReflectResponse,
    SoulManifestResponse,
    StartersRequest,
    StartersResponse,
    TensionRequest,
    TensionResponse,
    WhyRequest,
    WhyResponse,
)

if TYPE_CHECKING:
    from agents.k.soul import KgentSoul
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Renderable Classes for Soul Aspects
# Following BrainNode pattern: proper Renderable objects with to_dict/to_text
# =============================================================================


@dataclass(frozen=True)
class SoulDialogueRendering:
    """Rendering for dialogue response."""

    response: str
    mode: str
    tokens_used: int
    was_template: bool = False
    budget_tier: str = "dialogue"

    def to_dict(self) -> dict[str, Any]:
        return {
            "response": self.response,
            "mode": self.mode,
            "tokens_used": self.tokens_used,
            "was_template": self.was_template,
            "budget_tier": self.budget_tier,
        }

    def to_text(self) -> str:
        return f"[{self.mode}] {self.response}\n({self.tokens_used} tokens)"


@dataclass(frozen=True)
class SoulEigenvectorsRendering:
    """Rendering for eigenvector coordinates."""

    aesthetic: float
    categorical: float
    gratitude: float
    heterarchy: float
    generativity: float
    joy: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "aesthetic": self.aesthetic,
            "categorical": self.categorical,
            "gratitude": self.gratitude,
            "heterarchy": self.heterarchy,
            "generativity": self.generativity,
            "joy": self.joy,
        }

    def to_text(self) -> str:
        lines = [
            "Personality Eigenvectors",
            "========================",
            f"Aesthetic:    {self.aesthetic:.2f} (Minimalist ← → Baroque)",
            f"Categorical:  {self.categorical:.2f} (Concrete ← → Abstract)",
            f"Gratitude:    {self.gratitude:.2f} (Utilitarian ← → Sacred)",
            f"Heterarchy:   {self.heterarchy:.2f} (Hierarchical ← → Peer-to-Peer)",
            f"Generativity: {self.generativity:.2f} (Documentation ← → Generation)",
            f"Joy:          {self.joy:.2f} (Austere ← → Playful)",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class SoulStartersRendering:
    """Rendering for dialogue starters."""

    mode: str | None
    starters: list[str] | dict[str, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "starters": self.starters,
        }

    def to_text(self) -> str:
        if isinstance(self.starters, dict):
            lines = ["Dialogue Starters by Mode", "========================="]
            for mode_name, mode_starters in self.starters.items():
                lines.append(f"\n{mode_name}:")
                for s in mode_starters[:3]:
                    lines.append(f"  - {s}")
            return "\n".join(lines)
        else:
            lines = [f"Starters for {self.mode or 'all modes'}:", ""]
            for s in self.starters:
                lines.append(f"  - {s}")
            return "\n".join(lines)


@dataclass(frozen=True)
class SoulGovernanceRendering:
    """Rendering for governance decision."""

    approved: bool
    reasoning: str
    alternatives: list[str]
    confidence: float
    tokens_used: int
    recommendation: str
    principles: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "reasoning": self.reasoning,
            "alternatives": self.alternatives,
            "confidence": self.confidence,
            "tokens_used": self.tokens_used,
            "recommendation": self.recommendation,
            "principles": self.principles,
        }

    def to_text(self) -> str:
        status = "APPROVED" if self.approved else "REJECTED"
        lines = [
            f"Governance Decision: {status}",
            f"Confidence: {self.confidence:.0%}",
            f"Recommendation: {self.recommendation}",
            "",
            "Reasoning:",
            f"  {self.reasoning}",
        ]
        if self.alternatives:
            lines.append("")
            lines.append("Alternatives:")
            for alt in self.alternatives:
                lines.append(f"  - {alt}")
        if self.principles:
            lines.append("")
            lines.append("Principles Applied:")
            for p in self.principles:
                lines.append(f"  - {p}")
        return "\n".join(lines)


@dataclass(frozen=True)
class SoulModeRendering:
    """Rendering for mode get/set."""

    mode: str
    status: str = "current"

    def to_dict(self) -> dict[str, Any]:
        return {"mode": self.mode, "status": self.status}

    def to_text(self) -> str:
        if self.status == "changed":
            return f"Mode changed to: {self.mode}"
        return f"Current mode: {self.mode}"


# Soul affordances
SOUL_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "dialogue",
    "governance",  # Semantic gatekeeper for operations
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


@node(
    "self.soul",
    description="K-gent Soul - personality, dialogue, governance",
    singleton=True,
    contracts={
        # Perception aspects (Response only)
        "manifest": Response(SoulManifestResponse),
        "eigenvectors": Response(EigenvectorsResponse),
        "starters": Contract(StartersRequest, StartersResponse),
        # Mode (get/set)
        "mode": Contract(ModeRequest, ModeResponse),
        # Dialogue aspects (Contract with request + response)
        "dialogue": Contract(DialogueRequest, DialogueResponse),
        "challenge": Contract(ChallengeRequest, ChallengeResponse),
        "reflect": Contract(ReflectRequest, ReflectResponse),
        "why": Contract(WhyRequest, WhyResponse),
        "tension": Contract(TensionRequest, TensionResponse),
        # Governance (semantic gatekeeper)
        "governance": Contract(GovernanceRequest, GovernanceResponse),
    },
    examples=[
        # Quick exploration of soul state
        ("manifest", {}, "View soul state"),
        ("eigenvectors", {}, "See personality coordinates"),
        # Dialogue examples per mode
        ("starters", {"mode": "challenge"}, "Challenge starters"),
        ("starters", {"mode": "reflect"}, "Reflection starters"),
        # Actual dialogue
        (
            "dialogue",
            {"message": "What pattern am I seeing?", "mode": "reflect"},
            "Quick reflection",
        ),
        ("challenge", {"message": "Am I avoiding something?"}, "Challenge assumptions"),
        ("why", {"message": "Why am I working on this?"}, "Explore purpose"),
        # Governance
        (
            "governance",
            {"action": "delete old_backups", "context": {"reason": "disk space"}},
            "Check governance",
        ),
    ],
)
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
        """
        Soul affordances vary by archetype.

        Phase 8 Observer Consistency:
        - developer/architect: Full access including eigenvector inspection
        - operator: Dialogue, governance, mode (no eigenvector adjustment)
        - reviewer/newcomer: Basic dialogue only
        - guest: Manifest only (read-only soul state)

        Observer gradation: Observer (minimal) → Umwelt (full)
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: all soul + chat affordances
        if archetype_lower in ("developer", "architect", "admin", "system"):
            return SOUL_CHAT_AFFORDANCES

        # Operators: governance, dialogue, mode - no eigenvector deep-dive
        if archetype_lower == "operator":
            return (
                "manifest",
                "dialogue",
                "governance",
                "challenge",
                "reflect",
                "mode",
                "starters",
                "chat",
            )

        # Reviewers/security: dialogue and challenge, no mutation
        if archetype_lower in ("reviewer", "security"):
            return (
                "manifest",
                "dialogue",
                "challenge",
                "starters",
            )

        # Newcomers/casual: basic dialogue only
        if archetype_lower in ("newcomer", "casual", "reflective"):
            return (
                "manifest",
                "dialogue",
                "starters",
                "chat",
            )

        # Creative/strategic: dialogue modes for exploration
        if archetype_lower in ("creative", "strategic", "tactical"):
            return (
                "manifest",
                "dialogue",
                "challenge",
                "reflect",
                "why",
                "tension",
                "starters",
                "chat",
            )

        # Technical: similar to architect (full dialogue access)
        if archetype_lower == "technical":
            return SOUL_CHAT_AFFORDANCES

        # Guest (default): read-only soul state
        return ("manifest", "starters")

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
            case "governance":
                return await self._governance(observer, **kwargs)
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

        # Return Renderable for consistent CLI/TUI/JSON projection
        return SoulDialogueRendering(
            response=output.response,
            mode=output.mode.value,
            tokens_used=output.tokens_used,
            was_template=output.was_template,
            budget_tier=output.budget_tier.value,
        ).to_dict()

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.CALLS("llm"), Effect.CHARGES("tokens")],
        help="Semantic gatekeeper - evaluate operations against K-gent's principles",
        examples=[
            "self.soul.governance[action='delete user_data table', context={'environment': 'production'}]"
        ],
        budget_estimate="~500 tokens",
    )
    async def _governance(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Evaluate an operation against K-gent's principles.

        Uses the Semantic Gatekeeper pattern to reason about operations
        and provide approve/reject/escalate recommendations.

        Args:
            action: The action to evaluate (e.g., "delete user_data table")
            context: Additional context dict (environment, reason, severity)
            budget: Budget tier for evaluation ("dialogue" or "deep")

        Returns:
            Dict with approved, reasoning, alternatives, confidence, recommendation
        """
        action = kwargs.get("action")
        if not action:
            return {"error": "action required", "hint": "Describe the operation to evaluate"}

        if self._soul is None:
            return {"error": "Soul not initialized", "note": "Use kg soul init"}

        context = kwargs.get("context", {})
        budget_str = kwargs.get("budget", "dialogue")

        # Create a mock semaphore token from the request
        class _MockToken:
            def __init__(self, prompt: str, reason: str, severity: float, token_id: str) -> None:
                self.prompt = prompt
                self.reason = reason
                self.severity = severity
                self.id = token_id

        token = _MockToken(
            prompt=action,
            reason=context.get("reason", ""),
            severity=context.get("severity", 0.5),
            token_id=f"agentese_{action[:20]}",
        )

        # Use deep intercept for governance evaluation
        result = await self._soul.intercept_deep(token)

        # Build alternatives if rejected
        alternatives: list[str] = []
        if result.recommendation == "reject":
            alternatives = [
                "Consider using soft delete instead",
                "Archive the data before removing",
                "Add additional confirmation step",
            ]
        elif result.recommendation == "escalate":
            alternatives = [
                "Get explicit confirmation from stakeholders",
                "Review in team meeting",
                "Defer until more context available",
            ]

        # Estimate tokens used
        estimated_tokens = 500 if budget_str == "deep" else 150

        # Return Renderable for consistent CLI/TUI/JSON projection
        return SoulGovernanceRendering(
            approved=result.handled,
            reasoning=result.reasoning or result.annotation or "No reasoning provided",
            alternatives=alternatives,
            confidence=result.confidence,
            tokens_used=estimated_tokens,
            recommendation=result.recommendation or "escalate",
            principles=result.matching_principles,
        ).to_dict()

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

        # Return Renderable for consistent CLI/TUI/JSON projection
        return SoulDialogueRendering(
            response=output.response,
            mode="challenge",
            tokens_used=output.tokens_used,
        ).to_dict()

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

        # Return Renderable for consistent CLI/TUI/JSON projection
        return SoulDialogueRendering(
            response=output.response,
            mode="reflect",
            tokens_used=output.tokens_used,
        ).to_dict()

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
                # Return Renderable for consistent CLI/TUI/JSON projection
                return SoulStartersRendering(
                    mode=mode.value,
                    starters=starters,
                ).to_dict()
            except ValueError:
                return {"error": f"Invalid mode: {mode_str}"}

        # Return all starters by mode
        from agents.k.persona import DialogueMode

        all_starters = {}
        for mode in DialogueMode:
            all_starters[mode.value] = get_starters(mode)

        # Return Renderable for consistent CLI/TUI/JSON projection
        return SoulStartersRendering(
            mode=None,
            starters=all_starters,
        ).to_dict()

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

        # Return Renderable for consistent CLI/TUI/JSON projection
        return SoulEigenvectorsRendering(
            aesthetic=ev.aesthetic.value,
            categorical=ev.categorical.value,
            gratitude=ev.gratitude.value,
            heterarchy=ev.heterarchy.value,
            generativity=ev.generativity.value,
            joy=ev.joy.value,
        ).to_dict()

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
                # Return Renderable for consistent CLI/TUI/JSON projection
                return SoulModeRendering(
                    mode=mode.value,
                    status="changed",
                ).to_dict()
            except ValueError:
                return {"error": f"Invalid mode: {set_mode}"}

        # Return Renderable for consistent CLI/TUI/JSON projection
        return SoulModeRendering(
            mode=self._soul.active_mode.value,
            status="current",
        ).to_dict()


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


# === Singleton Management ===

_soul_node: SoulNode | None = None


def get_soul_node() -> SoulNode:
    """
    Get the singleton SoulNode.

    Creates a new instance if one doesn't exist.
    Use set_soul() to inject KgentSoul after bootstrap.

    Returns:
        The singleton SoulNode instance
    """
    global _soul_node
    if _soul_node is None:
        _soul_node = SoulNode()
    return _soul_node


def set_soul_node(node: SoulNode | None) -> None:
    """
    Set or clear the singleton SoulNode.

    Used for testing and reset scenarios.

    Args:
        node: SoulNode instance or None to clear
    """
    global _soul_node
    _soul_node = node


def set_soul(soul: "KgentSoul") -> None:
    """
    Wire a KgentSoul to the singleton SoulNode.

    This is the bootstrap pattern for connecting the KgentSoul service
    (from agents.k.soul) to the AGENTESE node. Call this in setup_providers()
    after bootstrapping the service registry.

    Args:
        soul: KgentSoul instance from bootstrap

    Example:
        # In setup_providers():
        soul = await get_service("kgent_soul")
        set_soul(soul)
    """
    node = get_soul_node()
    node._soul = soul


__all__ = [
    "SoulNode",
    "SOUL_AFFORDANCES",
    "SOUL_CHAT_AFFORDANCES",
    "create_soul_node",
    "get_soul_node",
    "set_soul_node",
    "set_soul",
]
