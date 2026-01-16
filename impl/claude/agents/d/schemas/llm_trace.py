"""
LLM Invocation Trace Schemas.

Every LLM call captured with full causality - more granular than Datadog.

Key additions over traditional traces:
- Causal parent/children (what triggered this, what it triggered)
- Ripple effects (crystals created/modified)
- Galois loss (coherence measurement)

Philosophy:
    "Marks are meant to be as granular if not more granular than the traces
     that Datadog or Splunk captures, since we're also capturing the causal
     chain/hierarchy and those ripple effects in addition to any raw data
     we capture itself."

Usage:
    >>> from agents.d.schemas.llm_trace import LLMInvocationMark, StateChange
    >>> from agents.d.universe import Universe, get_universe
    >>>
    >>> # Create trace
    >>> trace = LLMInvocationMark(
    ...     id="llm-123",
    ...     timestamp=datetime.now(UTC),
    ...     model="claude-3.5-sonnet",
    ...     provider="anthropic",
    ...     prompt_tokens=100,
    ...     completion_tokens=50,
    ...     total_tokens=150,
    ...     latency_ms=1200,
    ...     temperature=0.0,
    ...     system_prompt_hash="abc123",
    ...     user_prompt="Explain kgents",
    ...     response="kgents is...",
    ...     causal_parent_id=None,
    ...     triggered_by="user_input",
    ...     state_changes=(
    ...         StateChange(
    ...             entity_type="crystal",
    ...             entity_id="crystal-456",
    ...             change_type="created",
    ...             before_hash=None,
    ...             after_hash="def789",
    ...         ),
    ...     ),
    ...     crystals_created=("crystal-456",),
    ...     crystals_modified=(),
    ...     edges_created=(),
    ...     galois_loss=0.15,
    ...     coherence=0.85,
    ...     invocation_type="generation",
    ...     error=None,
    ...     success=True,
    ... )
    >>>
    >>> # Store in Universe
    >>> universe = get_universe()
    >>> trace_id = await universe.store(trace, "llm.invocation")
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class StateChange:
    """
    A single state change from an LLM invocation.

    Captures what changed as a result of this LLM call:
    - Crystals created/updated/deleted
    - K-Blocks created
    - Edges linked
    - Marks added

    Example:
        >>> StateChange(
        ...     entity_type="crystal",
        ...     entity_id="crystal-123",
        ...     change_type="created",
        ...     before_hash=None,
        ...     after_hash="abc123",
        ... )
    """

    entity_type: str
    """Type of entity: "crystal", "kblock", "edge", "mark", "thought"."""

    entity_id: str
    """ID of the entity that changed."""

    change_type: str
    """Type of change: "created", "updated", "deleted", "linked"."""

    before_hash: str | None
    """Hash of entity before change (None for creates)."""

    after_hash: str
    """Hash of entity after change."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "change_type": self.change_type,
            "before_hash": self.before_hash,
            "after_hash": self.after_hash,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "StateChange":
        """Deserialize from dict."""
        return cls(
            entity_type=d["entity_type"],
            entity_id=d["entity_id"],
            change_type=d["change_type"],
            before_hash=d.get("before_hash"),
            after_hash=d["after_hash"],
        )


@dataclass(frozen=True)
class LLMInvocationMark:
    """
    Every LLM call captured with full causality.

    Extends WitnessMark with LLM-specific fields.

    The Five Dimensions of LLM Tracing:
    1. Raw Data (request/response, tokens, latency)
    2. Causal Chain (what triggered this, what it triggered)
    3. Ripple Effects (state changes propagated)
    4. Quality Metrics (Galois loss, coherence)
    5. Classification (type, tags, error state)

    This is MORE granular than Datadog because we capture:
    - Full causal lineage (not just parent span)
    - Semantic quality (Galois loss)
    - State mutations (what changed)
    - Ripple effects (what cascaded)

    Philosophy:
        "The proof IS the decision. The mark IS the witness.
         The trace IS the causality."

    Example:
        >>> trace = LLMInvocationMark(
        ...     id="llm-20250101-123456",
        ...     timestamp=datetime.now(UTC),
        ...     model="claude-3.5-sonnet",
        ...     provider="anthropic",
        ...     prompt_tokens=150,
        ...     completion_tokens=200,
        ...     total_tokens=350,
        ...     latency_ms=2500,
        ...     temperature=0.7,
        ...     system_prompt_hash="abc123",
        ...     user_prompt="What are the principles of kgents?",
        ...     response="The principles are: tasteful, curated...",
        ...     causal_parent_id="mark-xyz",
        ...     triggered_by="user_input",
        ...     state_changes=(
        ...         StateChange(
        ...             entity_type="crystal",
        ...             entity_id="crystal-456",
        ...             change_type="created",
        ...             before_hash=None,
        ...             after_hash="def789",
        ...         ),
        ...     ),
        ...     crystals_created=("crystal-456",),
        ...     crystals_modified=(),
        ...     edges_created=(),
        ...     galois_loss=0.15,
        ...     coherence=0.85,
        ...     invocation_type="generation",
        ...     error=None,
        ...     success=True,
        ...     tags=frozenset(["session:abc", "agent:k-gent"]),
        ... )
    """

    # -------------------------------------------------------------------------
    # Identity
    # -------------------------------------------------------------------------

    id: str
    """Unique trace ID (e.g., "llm-20250101-123456")."""

    timestamp: datetime
    """When the invocation started (UTC)."""

    # -------------------------------------------------------------------------
    # LLM Request Metadata
    # -------------------------------------------------------------------------

    model: str
    """Model identifier (e.g., "claude-3.5-sonnet", "gpt-4")."""

    provider: str
    """Provider name (e.g., "anthropic", "openai", "ollama")."""

    prompt_tokens: int
    """Number of tokens in prompt."""

    completion_tokens: int
    """Number of tokens in completion."""

    total_tokens: int
    """Total tokens (prompt + completion)."""

    latency_ms: int
    """Latency in milliseconds."""

    temperature: float
    """Temperature parameter used."""

    # -------------------------------------------------------------------------
    # Content (Full Capture)
    # -------------------------------------------------------------------------

    system_prompt_hash: str
    """SHA-256 hash of system prompt (full stored separately for dedup)."""

    user_prompt: str
    """Full user prompt (always stored for traceability)."""

    response: str
    """Full LLM response."""

    # -------------------------------------------------------------------------
    # Causality (THE KEY DIFFERENTIATOR)
    # -------------------------------------------------------------------------

    causal_parent_id: str | None
    """ID of mark/trace that triggered this invocation."""

    triggered_by: str
    """Trigger source: "user_input", "agent_decision", "scheduled", "cascade"."""

    # -------------------------------------------------------------------------
    # Ripple Effects (What Changed)
    # -------------------------------------------------------------------------

    state_changes: tuple[StateChange, ...]
    """All state changes resulting from this invocation."""

    crystals_created: tuple[str, ...]
    """Crystal IDs created by this invocation."""

    crystals_modified: tuple[str, ...]
    """Crystal IDs modified by this invocation."""

    edges_created: tuple[str, ...]
    """Edge IDs created (for K-Block graph)."""

    # -------------------------------------------------------------------------
    # Quality Metrics
    # -------------------------------------------------------------------------

    galois_loss: float
    """Galois loss of response (semantic coherence measure)."""

    coherence: float
    """Coherence = 1 - loss. Higher is better."""

    # -------------------------------------------------------------------------
    # Classification
    # -------------------------------------------------------------------------

    invocation_type: str
    """Type: "generation", "analysis", "classification", "embedding"."""

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------

    error: str | None
    """Error message if invocation failed."""

    success: bool
    """Whether invocation succeeded."""

    # -------------------------------------------------------------------------
    # Tags & Context
    # -------------------------------------------------------------------------

    tags: frozenset[str] = field(default_factory=frozenset)
    """Tags for filtering (e.g., "session:abc", "agent:k-gent")."""

    witness_mark_id: str | None = None
    """Link to witness mark if also stored as WitnessMark."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "model": self.model,
            "provider": self.provider,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
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
            "edges_created": list(self.edges_created),
            "galois_loss": self.galois_loss,
            "coherence": self.coherence,
            "invocation_type": self.invocation_type,
            "error": self.error,
            "success": self.success,
            "tags": list(self.tags),
            "witness_mark_id": self.witness_mark_id,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LLMInvocationMark":
        """Deserialize from dict."""
        return cls(
            id=d["id"],
            timestamp=datetime.fromisoformat(d["timestamp"]),
            model=d["model"],
            provider=d.get("provider", "anthropic"),
            prompt_tokens=d["prompt_tokens"],
            completion_tokens=d["completion_tokens"],
            total_tokens=d.get("total_tokens", d["prompt_tokens"] + d["completion_tokens"]),
            latency_ms=d["latency_ms"],
            temperature=d.get("temperature", 0.0),
            system_prompt_hash=d["system_prompt_hash"],
            user_prompt=d["user_prompt"],
            response=d["response"],
            causal_parent_id=d.get("causal_parent_id"),
            triggered_by=d.get("triggered_by", "unknown"),
            state_changes=tuple(StateChange.from_dict(sc) for sc in d.get("state_changes", [])),
            crystals_created=tuple(d.get("crystals_created", [])),
            crystals_modified=tuple(d.get("crystals_modified", [])),
            edges_created=tuple(d.get("edges_created", [])),
            galois_loss=d.get("galois_loss", 0.0),
            coherence=d.get("coherence", 1.0),
            invocation_type=d.get("invocation_type", "generation"),
            error=d.get("error"),
            success=d.get("success", True),
            tags=frozenset(d.get("tags", [])),
            witness_mark_id=d.get("witness_mark_id"),
        )


# =============================================================================
# Schema for Universe Registration
# =============================================================================

from agents.d.universe import DataclassSchema

LLM_INVOCATION_SCHEMA = DataclassSchema(
    name="llm.invocation",
    type_cls=LLMInvocationMark,
)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "StateChange",
    "LLMInvocationMark",
    "LLM_INVOCATION_SCHEMA",
]
