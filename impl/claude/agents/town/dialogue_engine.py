"""
CitizenDialogueEngine: LLM-backed dialogue generation for Agent Town citizens.

Phase 7 of Agent Town adds speech to citizens. When citizens interact
(greet, gossip, trade), they generate actual dialogue via LLM calls,
grounded in their memories and consistent with their archetype personality.

Key Features:
- Budget-aware routing: citizen tiers → model selection
- Template fallback: always produces dialogue (never fails silently)
- Memory grounding: dialogue references past interactions
- Archetype voice: personality-consistent speech

Patterns reused from:
- K-gent: LLMClient, MockLLMClient, streaming
- M-gent: Foveation pattern (focal + peripheral memories)
- Town: Archetypes, Eigenvectors, Cosmotechnics

See: plans/agent-town/phase7-llm-dialogue.md
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, AsyncIterator, Union

# DIRECT IMPORT: K-gent LLM infrastructure
from agents.k.llm import (
    LLMClient,
    LLMResponse,
    MockLLMClient,
    StreamingLLMResponse,
    create_llm_client,
    has_llm_credentials,
)

if TYPE_CHECKING:
    from agents.town.citizen import Citizen
    from agents.town.flux import TownPhase


# =============================================================================
# Track A1: Data Structures
# =============================================================================


class DialogueTier(Enum):
    """
    Citizen dialogue budget tiers.

    Adapted from K-gent BudgetTier pattern.
    Cascade: EVOLVING → LEADER → CACHED → TEMPLATE
    """

    TEMPLATE = "template"  # 0 tokens - pre-written templates only
    CACHED = "cached"  # 0 tokens - reuse recent similar dialogue
    HAIKU = "haiku"  # ~50 tokens - quick greetings
    SONNET = "sonnet"  # ~200 tokens - nuanced negotiation


@dataclass
class DialogueContext:
    """
    Memory-grounded context for dialogue generation.

    Adapted from M-gent ContextInjector's foveated view pattern:
    - focal_memories: top 3 by relevance
    - peripheral_memories: next 2
    """

    # Memory grounding
    focal_memories: list[str] = field(default_factory=list)
    peripheral_memories: list[str] = field(default_factory=list)

    # Relationship state
    relationship: float = 0.0  # [-1, 1] - speaker's view of listener
    listener_relationship: float = 0.0  # Listener's view of speaker

    # Simulation context
    phase_name: str = ""  # TownPhase.name
    region: str = ""
    day: int = 1

    # Recent events for grounding
    recent_events: list[str] = field(default_factory=list)

    # Coalition context (Phase 4)
    shared_coalition: str | None = None

    def to_context_string(self) -> str:
        """Render context for prompt injection."""
        parts = []

        if self.focal_memories:
            parts.append(f"[Memories: {'; '.join(self.focal_memories[:3])}]")

        if self.peripheral_memories:
            parts.append(f"[Also recall: {'; '.join(self.peripheral_memories[:2])}]")

        if self.recent_events:
            parts.append(f"[Just now: {'; '.join(self.recent_events[:2])}]")

        if self.shared_coalition:
            parts.append(f"[Coalition: {self.shared_coalition}]")

        return "\n".join(parts) if parts else ""


@dataclass
class DialogueResult:
    """Result from dialogue generation."""

    text: str
    tokens_used: int
    model: str
    grounded_memories: list[str] = field(default_factory=list)
    was_template: bool = False
    was_cached: bool = False
    speaker_id: str = ""
    listener_id: str = ""
    operation: str = ""


@dataclass
class CitizenBudget:
    """Per-citizen token tracking."""

    citizen_id: str
    tier: str  # "evolving", "leader", "standard"
    daily_limit: int
    tokens_used_today: int = 0
    last_reset: datetime = field(default_factory=datetime.now)

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining for today."""
        return max(0, self.daily_limit - self.tokens_used_today)

    def can_afford(self, estimated_tokens: int) -> bool:
        """Check if budget allows this operation."""
        return self.tokens_remaining >= estimated_tokens

    def spend(self, tokens: int) -> None:
        """Record token expenditure."""
        self.tokens_used_today += tokens

    def reset_if_new_day(self) -> None:
        """Reset budget if it's a new day."""
        now = datetime.now()
        if now.date() != self.last_reset.date():
            self.tokens_used_today = 0
            self.last_reset = now


# =============================================================================
# Track A2: DialogueBudgetConfig
# =============================================================================


@dataclass
class DialogueBudgetConfig:
    """Per-citizen token budget configuration."""

    # Model routing by operation
    model_routing: dict[str, str] = field(
        default_factory=lambda: {
            "greet": "haiku",
            "gossip": "haiku",
            "trade": "sonnet",
            "council": "sonnet",
            "solo_reflect": "haiku",
        }
    )

    # Daily token limits by citizen tier
    tier_budgets: dict[str, int] = field(
        default_factory=lambda: {
            "evolving": 2000,  # Full LLM access (3-5 citizens)
            "leader": 500,  # Sampled access (5 citizens)
            "standard": 100,  # Template/cached (15 citizens)
        }
    )

    # Operation token estimates
    operation_estimates: dict[str, int] = field(
        default_factory=lambda: {
            "greet": 50,
            "gossip": 100,
            "trade": 200,
            "council": 500,
            "solo_reflect": 75,
        }
    )

    def model_for_operation(self, operation: str) -> str:
        """Get model name for an operation."""
        return self.model_routing.get(operation, "haiku")

    def estimate_tokens(self, operation: str) -> int:
        """Estimate token cost for an operation."""
        return self.operation_estimates.get(operation, 100)

    def budget_for_tier(self, tier: str) -> int:
        """Get daily budget for a citizen tier."""
        return self.tier_budgets.get(tier, 100)


# =============================================================================
# Track C1-C5: CitizenDialogueEngine
# =============================================================================


class CitizenDialogueEngine:
    """
    LLM-backed dialogue generation for Agent Town citizens.

    Orchestrates:
    1. Budget checking (per-citizen daily limits)
    2. Memory retrieval (foveation pattern)
    3. Prompt building (archetype voice)
    4. Model routing (operation → haiku/sonnet)
    5. Token tracking
    6. Template fallback (when budget exhausted)
    """

    def __init__(
        self,
        llm_client: LLMClient,
        budget_config: DialogueBudgetConfig | None = None,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self._llm = llm_client
        self._config = budget_config or DialogueBudgetConfig()
        self._cache_ttl = cache_ttl_seconds

        # Per-citizen budget tracking
        self._budgets: dict[str, CitizenBudget] = {}

        # Dialogue cache (for "cached" tier)
        # Key: (speaker_archetype, listener_archetype, operation)
        # Value: (dialogue_text, timestamp)
        self._cache: dict[tuple[str, str, str], tuple[str, datetime]] = {}

    # --- Budget Management (C1) ---

    def register_citizen(
        self,
        citizen_id: str,
        tier: str,
    ) -> CitizenBudget:
        """Register a citizen for budget tracking."""
        budget = CitizenBudget(
            citizen_id=citizen_id,
            tier=tier,
            daily_limit=self._config.budget_for_tier(tier),
        )
        self._budgets[citizen_id] = budget
        return budget

    def get_budget(self, citizen_id: str) -> CitizenBudget | None:
        """Get a citizen's budget tracker."""
        budget = self._budgets.get(citizen_id)
        if budget:
            budget.reset_if_new_day()
        return budget

    def get_tier(self, citizen: "Citizen") -> DialogueTier:
        """Determine dialogue tier for a citizen based on budget."""
        budget = self.get_budget(citizen.id)
        if budget is None:
            return DialogueTier.TEMPLATE

        if budget.tier == "evolving":
            return DialogueTier.SONNET if budget.can_afford(200) else DialogueTier.HAIKU
        elif budget.tier == "leader":
            return DialogueTier.HAIKU if budget.can_afford(50) else DialogueTier.CACHED
        else:
            return (
                DialogueTier.CACHED
                if self._has_cached(citizen)
                else DialogueTier.TEMPLATE
            )

    def _has_cached(self, citizen: "Citizen") -> bool:
        """Check if citizen has usable cached dialogue."""
        now = datetime.now()
        for (arch, _, _), (_, ts) in self._cache.items():
            if arch == citizen.archetype:
                if (now - ts).total_seconds() < self._cache_ttl:
                    return True
        return False

    # --- Memory Retrieval (C2) ---

    async def _build_context(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        phase: "TownPhase",
        recent_events: list[str] | None = None,
    ) -> DialogueContext:
        """
        Build memory-grounded DialogueContext.

        Uses M-gent foveation pattern:
        - Query memories related to the listener
        - Apply effective_score = similarity × relevance
        - Foveate: top 3 focal, next 2 peripheral
        """
        focal: list[str] = []
        peripheral: list[str] = []

        # Query speaker's memory for listener
        try:
            response = await speaker.memory.query(limit=10)
            if response.state and isinstance(response.state, dict):
                # Filter memories mentioning listener
                relevant: list[tuple[float, str]] = []
                for key, value in response.state.items():
                    if isinstance(value, dict):
                        value_str = str(value)
                        # Check if memory mentions listener
                        if listener.name in value_str or listener.id in value_str:
                            # Compute effective score (simplified)
                            recency = 1.0  # Could compute from timestamp
                            relevance = 0.8 if listener.name in value_str else 0.5
                            score = recency * relevance
                            mem_summary = value.get("type", key)
                            if isinstance(mem_summary, str):
                                relevant.append((score, mem_summary))

                # Sort by score, split into focal/peripheral
                relevant.sort(key=lambda x: x[0], reverse=True)
                for i, (_, mem) in enumerate(relevant[:5]):
                    if i < 3:
                        focal.append(mem)
                    else:
                        peripheral.append(mem)
        except Exception:
            pass  # Graceful degradation

        return DialogueContext(
            focal_memories=focal,
            peripheral_memories=peripheral,
            relationship=speaker.get_relationship(listener.id),
            listener_relationship=listener.get_relationship(speaker.id),
            phase_name=phase.name if phase else "UNKNOWN",
            region=speaker.region,
            recent_events=recent_events or [],
        )

    # --- Prompt Building (C3) ---

    def _build_system_prompt(
        self,
        speaker: "Citizen",
        operation: str,
    ) -> str:
        """
        Build archetype-specific system prompt.

        Adapted from K-gent persona._build_system_prompt() pattern.
        """
        from agents.town.dialogue_voice import ARCHETYPE_SYSTEM_PROMPTS

        template = ARCHETYPE_SYSTEM_PROMPTS.get(
            speaker.archetype, ARCHETYPE_SYSTEM_PROMPTS.get("Builder", "")
        )

        ev = speaker.eigenvectors
        return template.format(
            name=speaker.name,
            warmth=ev.warmth,
            curiosity=ev.curiosity,
            trust=ev.trust,
            creativity=ev.creativity,
            patience=ev.patience,
            resilience=ev.resilience,
            ambition=ev.ambition,
            operation=operation,
        )

    def _build_user_prompt(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        context: DialogueContext,
    ) -> str:
        """
        Build user prompt for dialogue generation.

        Adapted from K-gent persona._build_user_prompt() pattern.
        """
        # Relationship descriptor
        rel = context.relationship
        rel_word = (
            "positive" if rel > 0.3 else ("negative" if rel < -0.3 else "neutral")
        )

        # Memory section
        memory_section = context.to_context_string()

        return f"""You are {operation}ing {listener.name} ({listener.archetype}).
Your relationship: {rel_word} ({rel:.2f})
Current phase: {context.phase_name}
Location: {context.region}
{memory_section}

Generate your {operation} dialogue as {speaker.name}. Speak in first person. 1-3 sentences."""

    # --- Generation (C4) ---

    async def generate(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        phase: "TownPhase",
        recent_events: list[str] | None = None,
    ) -> DialogueResult:
        """
        Generate dialogue for an interaction.

        Steps:
        1. Check budget tier for speaker
        2. If TEMPLATE/CACHED, use fallback
        3. Retrieve relevant memories
        4. Build prompt with personality (archetype voice)
        5. Route to appropriate model
        6. Generate + track tokens
        """
        tier = self.get_tier(speaker)

        # Template fallback
        if tier == DialogueTier.TEMPLATE:
            return self._generate_template(speaker, listener, operation)

        # Cached fallback
        if tier == DialogueTier.CACHED:
            cached = self._try_cache(speaker, listener, operation)
            if cached:
                return cached
            return self._generate_template(speaker, listener, operation)

        # Build context
        context = await self._build_context(
            speaker, listener, operation, phase, recent_events
        )

        # Build prompts
        system = self._build_system_prompt(speaker, operation)
        user = self._build_user_prompt(speaker, listener, operation, context)

        # Select model
        model_name = self._config.model_for_operation(operation)
        max_tokens = 100 if model_name == "haiku" else 300

        # Generate
        response = await self._llm.generate(
            system=system,
            user=user,
            temperature=self._temperature_for_archetype(speaker.archetype),
            max_tokens=max_tokens,
        )

        # Track budget
        budget = self.get_budget(speaker.id)
        if budget:
            budget.spend(response.tokens_used)

        # Cache for future use
        self._cache[(speaker.archetype, listener.archetype, operation)] = (
            response.text,
            datetime.now(),
        )

        # Emit action metric (Track B instrumentation)
        try:
            from protocols.api.action_metrics import emit_action_metric

            emit_action_metric(
                action_type="dialogue",
                user_id="system",  # System-generated dialogue
                town_id="unknown",  # Would need to be passed in
                citizen_id=speaker.id,
                tokens_in=response.tokens_in if hasattr(response, "tokens_in") else 0,
                tokens_out=response.tokens_used,
                model=model_name,
                latency_ms=0,  # Already tracked in outer scope
                credits_charged=0,  # Dialogue is part of INHABIT session
                metadata={
                    "operation": operation,
                    "speaker": speaker.name,
                    "listener": listener.name,
                    "archetype": speaker.archetype,
                },
            )
        except ImportError:
            pass  # Metrics not available

        return DialogueResult(
            text=response.text,
            tokens_used=response.tokens_used,
            model=response.model,
            grounded_memories=context.focal_memories,
            was_template=False,
            was_cached=False,
            speaker_id=speaker.id,
            listener_id=listener.id,
            operation=operation,
        )

    # --- Streaming Generation (C5) ---

    async def generate_stream(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
        phase: "TownPhase",
        recent_events: list[str] | None = None,
    ) -> AsyncIterator[Union[str, DialogueResult]]:
        """
        Generate dialogue with streaming.

        Yields text chunks as they're generated.
        Final yield is DialogueResult with token counts.
        """
        tier = self.get_tier(speaker)

        # Template/cached don't support streaming
        if tier in (DialogueTier.TEMPLATE, DialogueTier.CACHED):
            result = await self.generate(
                speaker, listener, operation, phase, recent_events
            )
            yield result.text
            yield result
            return

        context = await self._build_context(
            speaker, listener, operation, phase, recent_events
        )
        system = self._build_system_prompt(speaker, operation)
        user = self._build_user_prompt(speaker, listener, operation, context)
        model_name = self._config.model_for_operation(operation)
        max_tokens = 100 if model_name == "haiku" else 300

        accumulated_text = ""
        tokens_used = 0
        model = ""

        async for item in self._llm.generate_stream(
            system=system,
            user=user,
            temperature=self._temperature_for_archetype(speaker.archetype),
            max_tokens=max_tokens,
        ):
            if isinstance(item, str):
                accumulated_text += item
                yield item
            elif isinstance(item, StreamingLLMResponse):
                tokens_used = item.tokens_used
                model = item.model

        # Track budget
        budget = self.get_budget(speaker.id)
        if budget:
            budget.spend(tokens_used)

        # Cache for future use
        self._cache[(speaker.archetype, listener.archetype, operation)] = (
            accumulated_text,
            datetime.now(),
        )

        # Emit action metric (Track B instrumentation)
        try:
            from protocols.api.action_metrics import emit_action_metric

            emit_action_metric(
                action_type="dialogue",
                user_id="system",  # System-generated dialogue
                town_id="unknown",  # Would need to be passed in
                citizen_id=speaker.id,
                tokens_in=0,  # Streaming doesn't track input separately
                tokens_out=tokens_used,
                model=model_name,
                latency_ms=0,  # Not tracked in streaming
                credits_charged=0,  # Dialogue is part of INHABIT session
                metadata={
                    "operation": operation,
                    "speaker": speaker.name,
                    "listener": listener.name,
                    "archetype": speaker.archetype,
                    "streaming": True,
                },
            )
        except ImportError:
            pass  # Metrics not available

        # Yield final result
        yield DialogueResult(
            text=accumulated_text,
            tokens_used=tokens_used,
            model=model,
            grounded_memories=context.focal_memories,
            was_template=False,
            was_cached=False,
            speaker_id=speaker.id,
            listener_id=listener.id,
            operation=operation,
        )

    # --- Fallbacks ---

    def _generate_template(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
    ) -> DialogueResult:
        """Generate dialogue from pre-written templates."""
        from agents.town.dialogue_voice import TEMPLATE_DIALOGUES

        templates = TEMPLATE_DIALOGUES.get(speaker.archetype, {}).get(operation, [])
        if not templates:
            # Fallback to Builder greet
            templates = TEMPLATE_DIALOGUES.get("Builder", {}).get("greet", [])
            if not templates:
                templates = ["Hello, {listener_name}."]

        template = random.choice(templates)
        text = template.format(
            listener_name=listener.name,
            speaker_name=speaker.name,
            subject_name="someone",  # For gossip templates
        )

        return DialogueResult(
            text=text,
            tokens_used=0,
            model="template",
            grounded_memories=[],
            was_template=True,
            was_cached=False,
            speaker_id=speaker.id,
            listener_id=listener.id,
            operation=operation,
        )

    def _try_cache(
        self,
        speaker: "Citizen",
        listener: "Citizen",
        operation: str,
    ) -> DialogueResult | None:
        """Try to retrieve from dialogue cache."""
        key = (speaker.archetype, listener.archetype, operation)
        if key in self._cache:
            text, ts = self._cache[key]
            if (datetime.now() - ts).total_seconds() < self._cache_ttl:
                # Personalize with names
                text = text.replace("[LISTENER]", listener.name)
                return DialogueResult(
                    text=text,
                    tokens_used=0,
                    model="cached",
                    grounded_memories=[],
                    was_template=False,
                    was_cached=True,
                    speaker_id=speaker.id,
                    listener_id=listener.id,
                    operation=operation,
                )
        return None

    def _temperature_for_archetype(self, archetype: str) -> float:
        """Get temperature setting for archetype (K-gent MODE_TEMPERATURES pattern)."""
        temps = {
            "Builder": 0.5,  # Practical, grounded
            "Trader": 0.6,  # Calculating
            "Healer": 0.7,  # Warm, empathetic
            "Scholar": 0.4,  # Precise, curious
            "Watcher": 0.5,  # Patient, observant
        }
        return temps.get(archetype, 0.6)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Data structures
    "DialogueTier",
    "DialogueContext",
    "DialogueResult",
    "CitizenBudget",
    "DialogueBudgetConfig",
    # Engine
    "CitizenDialogueEngine",
    # Re-exports from K-gent
    "LLMClient",
    "LLMResponse",
    "MockLLMClient",
    "StreamingLLMResponse",
    "create_llm_client",
    "has_llm_credentials",
]
