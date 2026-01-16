"""
LLM Invocation Marks - Comprehensive tracking beyond Datadog.

Every LLM call is witnessed with:
- Full content capture (prompts, responses)
- Causal chains (what triggered this, what did it trigger)
- Ripple effects (state changes, crystals created/modified)
- Galois loss quantification
- Multi-dimensional classification

Philosophy:
"The invocation IS the trace. The ripple IS the causality."

This schema enables:
1. Causal debugging: "What cascade led to this?"
2. Cost attribution: "Which user action caused 50 LLM calls?"
3. Quality tracking: "Which invocations have high galois_loss?"
4. Pattern detection: "Do cascades correlate with low coherence?"
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class StateChange:
    """
    A single state change caused by an LLM invocation.

    Tracks what entity changed, how it changed, and content hashes
    for verification.

    Attributes:
        entity_type: Type of entity (crystal/kblock/edge/mark)
        entity_id: ID of the changed entity
        change_type: Type of change (created/updated/deleted/linked)
        before_hash: Content hash before change (None for creation)
        after_hash: Content hash after change
    """

    entity_type: str
    """Type of entity: crystal/kblock/edge/mark."""

    entity_id: str
    """ID of the changed entity."""

    change_type: str
    """Type of change: created/updated/deleted/linked."""

    before_hash: str | None
    """Content hash before change (None for creation)."""

    after_hash: str
    """Content hash after change."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "change_type": self.change_type,
            "before_hash": self.before_hash,
            "after_hash": self.after_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StateChange":
        """Deserialize from dict."""
        return cls(
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            change_type=data["change_type"],
            before_hash=data.get("before_hash"),
            after_hash=data["after_hash"],
        )


@dataclass(frozen=True)
class LLMInvocationMark:
    """
    Comprehensive tracking of a single LLM invocation.

    Captures EVERYTHING about an LLM call:
    - What was requested (action, reasoning)
    - LLM-specific metrics (model, tokens, latency, temperature)
    - Full content (system prompt hash, user prompt, response)
    - Causality (parent invocation, trigger type)
    - Ripple effects (state changes, crystals created/modified)
    - Quality metrics (galois_loss, coherence)
    - Classification (invocation_type)
    - Provenance (timestamp, tags)

    This schema enables:
    - Causal chain reconstruction: "What led to this?"
    - Cost attribution: "Which user action caused this cascade?"
    - Quality analysis: "Which invocations have low coherence?"
    - Pattern detection: "Do cascades correlate with bugs?"

    Attributes:
        id: Unique identifier for this invocation
        action: What was requested (e.g., "Generate analysis")
        reasoning: Why this invocation was made
        model: Model identifier (e.g., "claude-opus-4-5")
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        latency_ms: Latency in milliseconds
        temperature: Temperature parameter
        system_prompt_hash: SHA256 of system prompt (for deduplication)
        user_prompt: Full user prompt (stored for debugging)
        response: Full response (stored for debugging)
        causal_parent_id: Parent invocation ID (None if root)
        triggered_by: What triggered this (user_input/agent_decision/scheduled/cascade)
        state_changes: Tuple of StateChange objects
        crystals_created: IDs of crystals created by this invocation
        crystals_modified: IDs of crystals modified by this invocation
        galois_loss: Loss metric L(invocation) in [0, 1]
        coherence: 1 - galois_loss
        invocation_type: Classification (generation/analysis/classification/embedding)
        timestamp: When this invocation occurred
        tags: Classification tags
    """

    id: str
    """Unique identifier for this invocation."""

    action: str
    """What was requested (e.g., 'Generate analysis', 'Classify intent')."""

    reasoning: str
    """Why this invocation was made."""

    # LLM-specific metrics
    model: str
    """Model identifier (e.g., 'claude-opus-4-5', 'gpt-4')."""

    prompt_tokens: int
    """Number of prompt tokens."""

    completion_tokens: int
    """Number of completion tokens."""

    latency_ms: int
    """Latency in milliseconds."""

    temperature: float
    """Temperature parameter used."""

    # Content (full capture)
    system_prompt_hash: str
    """SHA256 hash of system prompt (for deduplication)."""

    user_prompt: str
    """Full user prompt (stored for debugging)."""

    response: str
    """Full response (stored for debugging)."""

    # Causality (THE KEY)
    causal_parent_id: str | None
    """Parent invocation ID (None if root invocation)."""

    triggered_by: str
    """What triggered this: user_input/agent_decision/scheduled/cascade."""

    # Ripple effects
    state_changes: tuple[StateChange, ...]
    """State changes caused by this invocation."""

    crystals_created: tuple[str, ...]
    """IDs of crystals created by this invocation."""

    crystals_modified: tuple[str, ...]
    """IDs of crystals modified by this invocation."""

    # Quality
    galois_loss: float
    """Galois loss L(invocation) in [0, 1]."""

    # Classification
    invocation_type: str
    """Type: generation/analysis/classification/embedding."""

    # Provenance
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this invocation occurred."""

    tags: frozenset[str] = frozenset()
    """Classification tags (e.g., 'high-cost', 'cascade', 'user-initiated')."""

    @property
    def coherence(self) -> float:
        """Coherence = 1 - loss. Core Galois insight."""
        return 1.0 - self.galois_loss

    @property
    def total_tokens(self) -> int:
        """Total tokens (prompt + completion)."""
        return self.prompt_tokens + self.completion_tokens

    @property
    def tokens_per_second(self) -> float:
        """Completion tokens per second."""
        if self.latency_ms == 0:
            return 0.0
        return self.completion_tokens / (self.latency_ms / 1000.0)

    @property
    def is_cascade(self) -> bool:
        """Is this part of a cascade (has parent)?"""
        return self.causal_parent_id is not None

    @property
    def is_root(self) -> bool:
        """Is this a root invocation (no parent)?"""
        return self.causal_parent_id is None

    @property
    def ripple_magnitude(self) -> int:
        """Magnitude of ripple effects (total state changes + crystals)."""
        return len(self.state_changes) + len(self.crystals_created) + len(self.crystals_modified)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "action": self.action,
            "reasoning": self.reasoning,
            "model": self.model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "latency_ms": self.latency_ms,
            "temperature": self.temperature,
            "system_prompt_hash": self.system_prompt_hash,
            "user_prompt": self.user_prompt,
            "response": self.response,
            "causal_parent_id": self.causal_parent_id,
            "triggered_by": self.triggered_by,
            "state_changes": [sc.to_dict() for sc in self.state_changes],
            "crystals_created": list(self.crystals_created),
            "crystals_modified": list(self.crystals_modified),
            "galois_loss": self.galois_loss,
            "invocation_type": self.invocation_type,
            "timestamp": self.timestamp.isoformat(),
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LLMInvocationMark":
        """Deserialize from dict."""
        return cls(
            id=data["id"],
            action=data["action"],
            reasoning=data["reasoning"],
            model=data["model"],
            prompt_tokens=data["prompt_tokens"],
            completion_tokens=data["completion_tokens"],
            latency_ms=data["latency_ms"],
            temperature=data["temperature"],
            system_prompt_hash=data["system_prompt_hash"],
            user_prompt=data["user_prompt"],
            response=data["response"],
            causal_parent_id=data.get("causal_parent_id"),
            triggered_by=data["triggered_by"],
            state_changes=tuple(StateChange.from_dict(sc) for sc in data.get("state_changes", [])),
            crystals_created=tuple(data.get("crystals_created", [])),
            crystals_modified=tuple(data.get("crystals_modified", [])),
            galois_loss=data.get("galois_loss", 0.0),
            invocation_type=data["invocation_type"],
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(UTC),
            tags=frozenset(data.get("tags", [])),
        )


# Schema registration for Universe
from agents.d.universe import DataclassSchema

STATE_CHANGE_SCHEMA = DataclassSchema(name="llm.state_change", type_cls=StateChange)

LLM_INVOCATION_MARK_SCHEMA = DataclassSchema(name="llm.invocation_mark", type_cls=LLMInvocationMark)


__all__ = [
    "StateChange",
    "LLMInvocationMark",
    "STATE_CHANGE_SCHEMA",
    "LLM_INVOCATION_MARK_SCHEMA",
]
