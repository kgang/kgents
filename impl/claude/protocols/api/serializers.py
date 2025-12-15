"""
AGENTESE Universal Protocol Serializers.

Pydantic models for the AUP contract layer:
- Request/response types for HTTP, WebSocket, and SSE
- Observer context (no view from nowhere)
- Law verification results
- Sympathetic error responses

Design Principles (from spec/principles.md):
1. Minimal Output - Response envelope is lean
2. No View from Nowhere - Observer context REQUIRED
3. Composability - Pipeline composition with law verification
4. Graceful Degradation - Errors include suggestion and available

Category Laws (preserved by contract):
- Identity: Id >> f ≡ f ≡ f >> Id
- Associativity: (f >> g) >> h ≡ f >> (g >> h)
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

try:
    from pydantic import BaseModel, ConfigDict, Field

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    # Stub for when pydantic is not installed
    BaseModel = object  # type: ignore[misc, assignment]

    def _stub_field(*args: Any, **kwargs: Any) -> Any:
        """Stub Field function."""
        return None

    Field = _stub_field

    class ConfigDict:  # type: ignore[no-redef]
        """Stub ConfigDict class."""

        def __init__(self, **kwargs: Any) -> None:
            pass


# =============================================================================
# Observer Context - "There is no view from nowhere"
# =============================================================================


class ObserverContext(BaseModel):
    """
    Observer identity for umwelt construction.

    AGENTESE Principle: There is no view from nowhere.
    Every invocation requires an observer, and different observers
    receive different perceptions of the same entity.

    The observer context is provided via:
    - HTTP headers: X-Observer-Archetype, X-Observer-Id
    - Request body: observer field
    - WebSocket: Initial auth message
    """

    archetype: str = Field(
        default="viewer",
        description="Observer archetype (viewer, architect, philosopher, developer, etc.)",
        examples=["viewer", "architect", "philosopher", "developer", "admin"],
    )
    id: str = Field(
        default="anonymous",
        description="Unique observer identifier (user ID, session ID)",
        examples=["user-123", "session-abc"],
    )
    capabilities: list[str] = Field(
        default_factory=list,
        description="Explicitly granted affordances beyond archetype defaults",
        examples=[["define", "spawn", "dialectic"]],
    )

    if HAS_PYDANTIC:
        model_config = ConfigDict(frozen=True)


# =============================================================================
# Response Metadata
# =============================================================================


class ResponseMeta(BaseModel):
    """
    Metadata for tracing and debugging.

    Every response carries observability context to enable
    distributed tracing and performance analysis.
    """

    observer: str = Field(
        ...,
        description="Observer archetype that received this result",
    )
    span_id: str = Field(
        ...,
        description="OpenTelemetry span ID for tracing",
        examples=["abc123def456"],
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Response generation timestamp (UTC)",
    )
    duration_ms: int | None = Field(
        default=None,
        ge=0,
        description="Invocation duration in milliseconds",
    )
    laws_verified: list[str] = Field(
        default_factory=list,
        description="Category laws verified during this invocation",
        examples=[["identity", "associativity"]],
    )
    cached: bool = Field(
        default=False,
        description="Whether the result was served from cache",
    )


# =============================================================================
# Standard Request/Response Types
# =============================================================================


class AgenteseRequest(BaseModel):
    """
    Standard request body for AGENTESE invocations.

    Used for POST requests to aspect endpoints:
        POST /api/v1/{context}/{holon}/{aspect}
    """

    kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Aspect-specific arguments",
        examples=[{"challenge": "What about edge cases?", "depth": 3}],
    )
    entropy_budget: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Entropy budget for void.* operations (Accursed Share)",
    )
    observer: ObserverContext | None = Field(
        default=None,
        description="Observer context (alternative to headers)",
    )


class AgenteseResponse(BaseModel):
    """
    Standard response envelope for all AGENTESE invocations.

    Design: Minimal Output principle - lean envelope with three fields.
    The result is observer-specific; different observers receive
    different perceptions of the same entity.
    """

    handle: str = Field(
        ...,
        description="Full AGENTESE path that was invoked",
        examples=["world.field.manifest", "concept.justice.refine"],
    )
    result: Any = Field(
        ...,
        description="Observer-specific payload (varies by aspect and observer)",
    )
    meta: ResponseMeta = Field(
        ...,
        description="Tracing and debugging metadata",
    )


# =============================================================================
# Composition (Pipeline) Types
# =============================================================================


class CompositionRequest(BaseModel):
    """
    Request for pipeline composition.

    Chains multiple AGENTESE paths into a single invocation.
    Results flow through the pipeline: output of path N becomes
    input to path N+1.

    Category Laws are preserved:
    - Identity: Id >> path == path == path >> Id
    - Associativity: (a >> b) >> c == a >> (b >> c)
    """

    paths: list[str] = Field(
        ...,
        min_length=1,
        description="AGENTESE paths to compose in order",
        examples=[
            ["world.document.manifest", "concept.summary.refine", "self.memory.engram"]
        ],
    )
    initial_input: Any = Field(
        default=None,
        description="Optional initial value for the pipeline",
    )
    emit_law_check: bool = Field(
        default=True,
        description="Emit law verification events (for observability)",
    )
    observer: ObserverContext | None = Field(
        default=None,
        description="Observer context (alternative to headers)",
    )


class PipelineStep(BaseModel):
    """A single step in a composition pipeline trace."""

    path: str = Field(
        ...,
        description="AGENTESE path for this step",
    )
    span_id: str = Field(
        ...,
        description="Span ID for this step",
    )
    duration_ms: int = Field(
        ...,
        ge=0,
        description="Duration of this step in milliseconds",
    )
    output_type: str = Field(
        default="unknown",
        description="Type of the output (for debugging)",
    )


class CompositionResponse(BaseModel):
    """
    Response for pipeline composition.

    Includes the final result and a trace of each step for
    observability and debugging.
    """

    result: Any = Field(
        ...,
        description="Final result after all paths executed",
    )
    pipeline_trace: list[PipelineStep] = Field(
        default_factory=list,
        description="Trace of each step in the pipeline",
    )
    laws_verified: list[str] = Field(
        default_factory=list,
        description="Category laws verified during composition",
    )
    meta: ResponseMeta = Field(
        ...,
        description="Overall response metadata",
    )


# =============================================================================
# Law Verification Types
# =============================================================================


class LawVerificationResult(BaseModel):
    """
    Result of category law verification.

    Category laws are VERIFIED, not aspirational (AD-005):
    - Identity: Id >> f ≡ f ≡ f >> Id
    - Associativity: (f >> g) >> h ≡ f >> (g >> h)
    """

    identity_holds: bool = Field(
        ...,
        description="Whether identity law holds",
    )
    associativity_holds: bool = Field(
        ...,
        description="Whether associativity law holds",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="Detailed error messages for failed laws",
    )
    locus: str = Field(
        default="",
        description="Dot-path where verification was performed",
    )

    @property
    def all_laws_hold(self) -> bool:
        """Check if all category laws are satisfied."""
        return self.identity_holds and self.associativity_holds


# =============================================================================
# Error Response Types
# =============================================================================

# Error codes following AGENTESE exception taxonomy
ErrorCode = Literal[
    "PATH_NOT_FOUND",
    "AFFORDANCE_DENIED",
    "OBSERVER_REQUIRED",
    "SYNTAX_ERROR",
    "LAW_VIOLATION",
    "BUDGET_EXHAUSTED",
    "COMPOSITION_ERROR",
    "INTERNAL_ERROR",
]


class ErrorResponse(BaseModel):
    """
    Sympathetic error response with guidance.

    AGENTESE Principle: Transparent Infrastructure
    Errors must explain WHY and suggest WHAT TO DO.

    Error Taxonomy:
    - PATH_NOT_FOUND (404): Path doesn't exist
    - AFFORDANCE_DENIED (403): Observer lacks permission
    - OBSERVER_REQUIRED (401): No observer context provided
    - SYNTAX_ERROR (400): Malformed path/request
    - LAW_VIOLATION (422): Composition violates category laws
    - BUDGET_EXHAUSTED (402): Accursed Share depleted
    - COMPOSITION_ERROR (422): Pipeline execution failed
    - INTERNAL_ERROR (500): Unexpected server error
    """

    error: str = Field(
        ...,
        description="Human-readable error message",
    )
    code: ErrorCode = Field(
        ...,
        description="Machine-readable error code",
    )
    path: str | None = Field(
        default=None,
        description="AGENTESE path that caused the error",
    )
    suggestion: str | None = Field(
        default=None,
        description="Sympathetic guidance on how to fix the error",
    )
    available: list[str] | None = Field(
        default=None,
        description="Available alternatives (paths, affordances)",
    )
    why: str | None = Field(
        default=None,
        description="Explanation of why the error occurred",
    )
    span_id: str | None = Field(
        default=None,
        description="Span ID for tracing the error",
    )


# =============================================================================
# Streaming Types (SSE)
# =============================================================================


class SSEChunk(BaseModel):
    """A single chunk in an SSE stream."""

    type: Literal["thinking", "response", "error", "metadata"] = Field(
        ...,
        description="Type of chunk",
    )
    content: str = Field(
        default="",
        description="Chunk content",
    )
    partial: bool = Field(
        default=True,
        description="Whether this is a partial result (more chunks coming)",
    )
    index: int = Field(
        default=0,
        ge=0,
        description="Chunk index in stream",
    )


class SSECompleteEvent(BaseModel):
    """Final event in an SSE stream."""

    result: Any = Field(
        ...,
        description="Complete result",
    )
    span_id: str = Field(
        ...,
        description="Span ID for the operation",
    )
    chunks_count: int = Field(
        default=0,
        ge=0,
        description="Total number of chunks streamed",
    )
    duration_ms: int = Field(
        default=0,
        ge=0,
        description="Total duration in milliseconds",
    )


# =============================================================================
# WebSocket Types
# =============================================================================


class WSSubscribeMessage(BaseModel):
    """
    Client → Server: Subscribe to a channel.

    Channels:
    - "garden": All entity movement + pheromone updates
    - "agent:{id}": Single agent state changes
    - "dialectic": Dialectic phase events
    - "town:{id}": Agent Town updates
    """

    type: Literal["subscribe"] = "subscribe"
    channel: str = Field(
        ...,
        description="Channel to subscribe to",
        examples=["garden", "agent:kent-001", "dialectic", "town:main"],
    )
    filter: dict[str, Any] | None = Field(
        default=None,
        description="Optional filter for the subscription",
    )


class WSUnsubscribeMessage(BaseModel):
    """Client → Server: Unsubscribe from a channel."""

    type: Literal["unsubscribe"] = "unsubscribe"
    channel: str = Field(
        ...,
        description="Channel to unsubscribe from",
    )


class WSInvokeMessage(BaseModel):
    """
    Client → Server: Invoke an AGENTESE path over WebSocket.

    The result is sent back as a WSInvokeResult message.
    """

    type: Literal["invoke"] = "invoke"
    id: str = Field(
        ...,
        description="Client-generated request ID (for matching response)",
    )
    handle: str = Field(
        ...,
        description="Full AGENTESE path to invoke",
    )
    observer: ObserverContext = Field(
        default_factory=ObserverContext,
        description="Observer context for the invocation",
    )
    kwargs: dict[str, Any] = Field(
        default_factory=dict,
        description="Arguments for the aspect",
    )


class WSStateUpdate(BaseModel):
    """
    Server → Client: State update on a subscribed channel.

    The data format depends on the channel type.
    """

    type: Literal["state_update"] = "state_update"
    channel: str = Field(
        ...,
        description="Channel this update is for",
    )
    data: dict[str, Any] = Field(
        ...,
        description="Channel-specific state data",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Update timestamp",
    )


class WSInvokeResult(BaseModel):
    """Server → Client: Result of a WebSocket invoke."""

    type: Literal["invoke_result"] = "invoke_result"
    id: str = Field(
        ...,
        description="Matches the request ID from WSInvokeMessage",
    )
    success: bool = Field(
        ...,
        description="Whether the invocation succeeded",
    )
    result: Any | None = Field(
        default=None,
        description="Invocation result (if success)",
    )
    error: ErrorResponse | None = Field(
        default=None,
        description="Error details (if not success)",
    )
    meta: ResponseMeta | None = Field(
        default=None,
        description="Response metadata (if success)",
    )


class WSDialecticEvent(BaseModel):
    """
    Server → Client: Dialectic phase event.

    Sent on the "dialectic" channel during dialectic operations.
    """

    type: Literal["dialectic_event"] = "dialectic_event"
    phase: Literal["thesis", "antithesis", "synthesis"] = Field(
        ...,
        description="Current dialectic phase",
    )
    content: str = Field(
        ...,
        description="Phase content",
    )
    agent_id: str = Field(
        ...,
        description="Agent that produced this phase",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event timestamp",
    )


# =============================================================================
# Garden/Town State Types (for WebSocket channels)
# =============================================================================


class EntityState(BaseModel):
    """State of a single entity in the garden/town."""

    id: str
    glyph: str
    x: float
    y: float
    color: str = "#ffffff"
    archetype: str | None = None
    phase: str | None = None


class PheromoneState(BaseModel):
    """State of a pheromone deposit."""

    x: float
    y: float
    radius: float
    color: str
    intensity: float = Field(ge=0.0, le=1.0)
    type: str = "default"


class GardenState(BaseModel):
    """
    Complete garden state for WebSocket updates.

    Used on the "garden" and "town:{id}" channels.
    """

    entities: list[EntityState] = Field(default_factory=list)
    pheromones: list[PheromoneState] = Field(default_factory=list)
    entropy: float = Field(default=0.0, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    tick: int = Field(default=0, ge=0)


# =============================================================================
# Affordances Types
# =============================================================================


class AffordancesRequest(BaseModel):
    """Request to list affordances for a path."""

    path: str = Field(
        ...,
        description="AGENTESE path (without aspect)",
        examples=["world.house", "self.soul"],
    )
    observer: ObserverContext | None = Field(
        default=None,
        description="Observer context (alternative to headers)",
    )


class AffordancesResponse(BaseModel):
    """Response listing available affordances for a path."""

    path: str = Field(
        ...,
        description="The queried path",
    )
    affordances: list[str] = Field(
        ...,
        description="Available affordances for this observer",
    )
    observer_archetype: str = Field(
        ...,
        description="Observer archetype used for filtering",
    )
    handle: str = Field(
        default="",
        description="Resolved handle for the path",
    )


# =============================================================================
# Resolve Types
# =============================================================================


class ResolveRequest(BaseModel):
    """Request to resolve a path without invoking."""

    path: str = Field(
        ...,
        description="AGENTESE path to resolve",
    )


class ResolveResponse(BaseModel):
    """Response from path resolution."""

    path: str = Field(
        ...,
        description="The resolved path",
    )
    handle: str = Field(
        ...,
        description="Canonical handle for this node",
    )
    context: str = Field(
        ...,
        description="AGENTESE context (world, self, concept, void, time)",
    )
    holon: str = Field(
        ...,
        description="Entity/holon name",
    )
    exists: bool = Field(
        default=True,
        description="Whether the path exists",
    )
    is_jit: bool = Field(
        default=False,
        description="Whether this is a JIT-compiled node",
    )
