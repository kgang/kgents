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
