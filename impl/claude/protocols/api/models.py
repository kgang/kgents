"""
Pydantic models for Soul API.

Request/response models for:
- Governance endpoints (semantic gatekeeper)
- Dialogue endpoints (interactive conversation)
- Health checks
"""

from __future__ import annotations

from typing import Any, Optional

try:
    from pydantic import BaseModel, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    # Stub for when pydantic is not installed
    BaseModel = object  # type: ignore[misc, assignment]

    def _stub_field(*args: Any, **kwargs: Any) -> Any:
        """Stub Field function."""
        return None

    Field = _stub_field


# --- Governance Models ---


class GovernanceRequest(BaseModel):
    """Request for governance evaluation of an operation."""

    action: str = Field(
        ...,
        description="The operation/action to evaluate (e.g., 'delete database', 'deploy to production')",
        examples=["delete user_data table", "rm -rf /tmp/cache"],
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for the operation",
        examples=[{"environment": "production", "user": "admin"}],
    )
    budget: Optional[str] = Field(
        default="dialogue",
        description="Token budget tier: dormant, whisper, dialogue, deep",
        examples=["dialogue", "deep"],
    )


class GovernanceResponse(BaseModel):
    """Response from governance evaluation."""

    approved: bool = Field(
        ...,
        description="Whether the operation was auto-approved",
    )
    reasoning: str = Field(
        ...,
        description="LLM-generated reasoning for the decision",
        examples=[
            "This operation aligns with minimalism principles - removing unused data."
        ],
    )
    alternatives: list[str] = Field(
        default_factory=list,
        description="Alternative approaches if operation was rejected",
        examples=[["Use soft delete instead", "Archive before deleting"]],
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the decision (0.0 to 1.0)",
        examples=[0.85],
    )
    tokens_used: int = Field(
        ...,
        ge=0,
        description="Number of tokens used in evaluation",
        examples=[150],
    )
    recommendation: str = Field(
        ...,
        description="Final recommendation: approve, reject, or escalate",
        examples=["approve", "reject", "escalate"],
    )
    principles: list[str] = Field(
        default_factory=list,
        description="Matching principles from K-gent eigenvectors",
        examples=[["Aesthetic: Minimalism", "Does this need to exist?"]],
    )


# --- Dialogue Models ---


class DialogueRequest(BaseModel):
    """Request for dialogue with K-gent Soul."""

    prompt: str = Field(
        ...,
        description="The message/question for K-gent",
        examples=[
            "What patterns am I avoiding?",
            "How should I approach this decision?",
        ],
    )
    mode: Optional[str] = Field(
        default="reflect",
        description="Dialogue mode: reflect, advise, challenge, explore",
        examples=["reflect", "advise"],
    )
    budget: Optional[str] = Field(
        default="dialogue",
        description="Token budget tier: dormant, whisper, dialogue, deep",
        examples=["dialogue", "deep"],
    )


class DialogueResponse(BaseModel):
    """Response from K-gent dialogue."""

    response: str = Field(
        ...,
        description="K-gent's response",
        examples=[
            "You're avoiding the hard decision by focusing on implementation details."
        ],
    )
    mode: str = Field(
        ...,
        description="The dialogue mode used",
        examples=["reflect"],
    )
    eigenvectors: dict[str, Any] = Field(
        default_factory=dict,
        description="K-gent's personality coordinates (eigenvectors)",
        examples=[
            {
                "aesthetic": 0.9,
                "categorical": 0.8,
                "gratitude": 0.7,
            }
        ],
    )
    tokens_used: int = Field(
        ...,
        ge=0,
        description="Number of tokens used in response",
        examples=[250],
    )
    referenced_preferences: list[str] = Field(
        default_factory=list,
        description="Preferences referenced in the response",
        examples=[["Prefer minimal solutions", "Question defaults"]],
    )
    referenced_patterns: list[str] = Field(
        default_factory=list,
        description="Behavioral patterns referenced in the response",
        examples=[["Procrastination through perfectionism"]],
    )


# --- Health Models ---


class HealthResponse(BaseModel):
    """Response from health check endpoint."""

    status: str = Field(
        ...,
        description="Service status: ok, degraded, error",
        examples=["ok"],
    )
    version: str = Field(
        ...,
        description="API version",
        examples=["v1"],
    )
    has_llm: bool = Field(
        ...,
        description="Whether LLM is configured and available",
    )
    components: dict[str, str] = Field(
        default_factory=dict,
        description="Status of individual components",
        examples=[{"soul": "ok", "llm": "ok", "auth": "ok"}],
    )


# --- Brain Models (Holographic Brain) ---


class BrainCaptureRequest(BaseModel):
    """Request to capture content to holographic memory."""

    content: str = Field(
        ...,
        description="The content to capture into memory",
        examples=["Python is great for machine learning", "Meeting notes from standup"],
    )
    concept_id: Optional[str] = Field(
        default=None,
        description="Optional concept identifier (auto-generated if not provided)",
        examples=["note_20231215_standup", "insight_ml_patterns"],
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional metadata to attach to the capture",
        examples=[{"source": "meeting", "importance": "high"}],
    )


class BrainCaptureResponse(BaseModel):
    """Response from brain capture operation."""

    status: str = Field(
        ...,
        description="Capture status: captured, error",
        examples=["captured"],
    )
    concept_id: str = Field(
        ...,
        description="The concept ID of the captured content",
        examples=["capture_20231215_123456_abc123"],
    )
    storage: str = Field(
        ...,
        description="Where content was stored: memory_crystal, local_memory",
        examples=["memory_crystal"],
    )


class BrainGhostRequest(BaseModel):
    """Request to surface ghost memories based on context."""

    context: str = Field(
        ...,
        description="Context string to find relevant memories",
        examples=["AI and machine learning", "Python programming"],
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of memories to surface",
        examples=[5, 10],
    )


class GhostMemory(BaseModel):
    """A surfaced ghost memory."""

    concept_id: str = Field(
        ...,
        description="Concept identifier",
    )
    content: Optional[str] = Field(
        default=None,
        description="The memory content",
    )
    relevance: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score (0.0 to 1.0)",
    )


class BrainGhostResponse(BaseModel):
    """Response from ghost surfacing operation."""

    status: str = Field(
        ...,
        description="Surface status: surfaced, no_ghosts, error",
        examples=["surfaced"],
    )
    context: str = Field(
        ...,
        description="The context used for surfacing",
    )
    surfaced: list[GhostMemory] = Field(
        default_factory=list,
        description="List of surfaced memories",
    )
    count: int = Field(
        ...,
        ge=0,
        description="Number of memories surfaced",
    )


class BrainMapResponse(BaseModel):
    """Response from brain cartography/map request."""

    summary: str = Field(
        ...,
        description="Summary of the memory topology",
        examples=["Memory nodes: 42"],
    )
    concept_count: int = Field(
        ...,
        ge=0,
        description="Total number of concepts in memory",
    )
    landmarks: int = Field(
        default=0,
        ge=0,
        description="Number of landmarks in topology",
    )
    hot_patterns: int = Field(
        default=0,
        ge=0,
        description="Number of hot (recently accessed) patterns",
    )
    dimension: int = Field(
        ...,
        ge=1,
        description="Embedding dimension",
    )


class BrainStatusResponse(BaseModel):
    """Response from brain status check."""

    status: str = Field(
        ...,
        description="Brain status: healthy, degraded, unavailable",
        examples=["healthy"],
    )
    embedder_type: str = Field(
        ...,
        description="Type of embedder in use",
        examples=["SentenceTransformerEmbedder", "SimpleEmbedder"],
    )
    embedder_dimension: int = Field(
        ...,
        ge=1,
        description="Embedding dimension",
        examples=[384, 64],
    )
    concept_count: int = Field(
        ...,
        ge=0,
        description="Number of concepts in memory",
    )
    has_cartographer: bool = Field(
        ...,
        description="Whether CartographerAgent is configured",
    )
