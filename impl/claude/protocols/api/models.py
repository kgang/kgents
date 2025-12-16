"""
Pydantic models for Soul API.

Request/response models for:
- Governance endpoints (semantic gatekeeper)
- Dialogue endpoints (interactive conversation)
- Health checks
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

try:
    from pydantic import BaseModel, Field, field_validator

    HAS_PYDANTIC = True
except ImportError:
    # Stubs for when pydantic is not installed.
    #
    # Purpose: Allow this module to be imported for type checking or test mocking
    # without requiring pydantic as a dependency. The actual API (FastAPI) requires
    # pydantic anyway—these stubs only affect non-API use cases.
    #
    # Behavior: Models become plain objects, validators silently no-op.
    # This is intentional graceful degradation, not a bug.
    HAS_PYDANTIC = False
    BaseModel = object  # type: ignore[misc, assignment]

    def _stub_field(*args: Any, **kwargs: Any) -> Any:
        """Stub Field function."""
        return None

    def _stub_field_validator(*args: Any, **kwargs: Any) -> Any:
        """Stub field_validator decorator."""
        return lambda fn: fn

    Field = _stub_field
    field_validator = _stub_field_validator


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
        min_length=1,
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

    @field_validator("content")
    @classmethod
    def content_not_whitespace_only(cls, v: str) -> str:
        """Validate that content is not whitespace-only.

        Mirrors CLI behavior which strips and rejects empty content.
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError("content cannot be whitespace only")
        return stripped


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
        min_length=1,
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

    @field_validator("context")
    @classmethod
    def context_not_whitespace_only(cls, v: str) -> str:
        """Validate that context is not whitespace-only.

        Mirrors CLI behavior which strips and rejects empty context.
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError("context cannot be whitespace only")
        return stripped


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


# --- Brain Topology Models (3D Visualization) ---


class TopologyNode(BaseModel):
    """A crystal node in the 3D topology visualization."""

    id: str = Field(
        ...,
        description="Concept ID",
    )
    label: str = Field(
        ...,
        description="Display label (truncated content)",
    )
    x: float = Field(
        ...,
        description="3D X position (from embedding PCA)",
    )
    y: float = Field(
        ...,
        description="3D Y position (from embedding PCA)",
    )
    z: float = Field(
        ...,
        description="3D Z position (from embedding PCA)",
    )
    resolution: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Resolution level (1.0=fresh, 0.01=fading) - maps to opacity",
    )
    is_hot: bool = Field(
        ...,
        description="Whether this is a hot/hub crystal",
    )
    access_count: int = Field(
        ...,
        ge=0,
        description="Number of times accessed",
    )
    age_seconds: float = Field(
        ...,
        ge=0,
        description="Seconds since stored",
    )
    content_preview: Optional[str] = Field(
        default=None,
        description="First 100 chars of content",
    )


class TopologyEdge(BaseModel):
    """An edge between similar crystals."""

    source: str = Field(..., description="Source concept ID")
    target: str = Field(..., description="Target concept ID")
    similarity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Cosine similarity between embeddings",
    )


class TopologyGap(BaseModel):
    """A detected gap (sparse region) in the knowledge topology."""

    x: float = Field(..., description="Gap center X")
    y: float = Field(..., description="Gap center Y")
    z: float = Field(..., description="Gap center Z")
    radius: float = Field(..., description="Gap radius")
    nearest_concepts: list[str] = Field(
        default_factory=list,
        description="Concept IDs at the gap boundary",
    )


class BrainTopologyResponse(BaseModel):
    """Full topology data for 3D visualization."""

    nodes: list[TopologyNode] = Field(
        default_factory=list,
        description="Crystal nodes with positions",
    )
    edges: list[TopologyEdge] = Field(
        default_factory=list,
        description="Similarity edges between crystals",
    )
    gaps: list[TopologyGap] = Field(
        default_factory=list,
        description="Detected knowledge gaps",
    )
    hub_ids: list[str] = Field(
        default_factory=list,
        description="IDs of hub crystals (high connectivity)",
    )
    stats: dict[str, Any] = Field(
        default_factory=dict,
        description="Topology statistics",
    )


# --- Polynomial Visualization Models (Foundation 3: Visible Polynomial State) ---


class PolynomialPosition(BaseModel):
    """A position (state) in a polynomial agent's state machine."""

    id: str = Field(
        ...,
        description="Unique identifier for this position",
    )
    label: str = Field(
        ...,
        description="Human-readable label for the position",
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description of what this state represents",
    )
    emoji: Optional[str] = Field(
        default=None,
        description="Optional emoji for visual representation",
    )
    is_current: bool = Field(
        default=False,
        description="Whether this is the current position",
    )
    is_terminal: bool = Field(
        default=False,
        description="Whether this is a terminal state",
    )
    color: Optional[str] = Field(
        default=None,
        description="Optional color for visual representation (hex or name)",
    )


class PolynomialEdge(BaseModel):
    """A valid transition edge between positions."""

    source: str = Field(..., description="Source position ID")
    target: str = Field(..., description="Target position ID")
    label: Optional[str] = Field(
        default=None,
        description="Label for the transition (e.g., command name)",
    )
    is_valid: bool = Field(
        default=True,
        description="Whether this transition is currently valid",
    )


class PolynomialHistoryEntry(BaseModel):
    """A historical transition in the polynomial's execution."""

    from_position: str = Field(..., description="Position before transition")
    to_position: str = Field(..., description="Position after transition")
    input_summary: Optional[str] = Field(
        default=None,
        description="Summary of the input that triggered the transition",
    )
    output_summary: Optional[str] = Field(
        default=None,
        description="Summary of the output produced",
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO timestamp of the transition",
    )


class PolynomialVisualization(BaseModel):
    """
    Complete visualization data for a polynomial agent's state machine.

    This model enables Foundation 3 (Visible Polynomial State) by providing
    all data needed to render a state machine diagram in CLI or Web UI.

    Use cases:
    - GardenerSession: SENSE → ACT → REFLECT cycle
    - CitizenPolynomial: IDLE → WORKING → RESTING states
    - N-Phase development: 11-phase development workflow
    """

    id: str = Field(
        ...,
        description="Unique identifier for this polynomial visualization",
    )
    name: str = Field(
        ...,
        description="Name of the polynomial agent",
    )
    positions: list[PolynomialPosition] = Field(
        default_factory=list,
        description="All positions (states) in the state machine",
    )
    edges: list[PolynomialEdge] = Field(
        default_factory=list,
        description="Valid transitions between positions",
    )
    current: Optional[str] = Field(
        default=None,
        description="ID of the current position (if applicable)",
    )
    valid_directions: list[str] = Field(
        default_factory=list,
        description="IDs of positions that can be reached from current",
    )
    history: list[PolynomialHistoryEntry] = Field(
        default_factory=list,
        description="Recent transition history",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (e.g., cycle count, progress)",
    )


class PolynomialVisualizationResponse(BaseModel):
    """API response wrapper for polynomial visualization."""

    visualization: PolynomialVisualization = Field(
        ...,
        description="The polynomial visualization data",
    )
    agentese_path: Optional[str] = Field(
        default=None,
        description="AGENTESE path for this polynomial (e.g., concept.gardener.session)",
    )


# =============================================================================
# Gardener Models (Wave 1: Hero Path)
# =============================================================================


class GardenerPhase(str, Enum):
    """Gardener session phases following the SENSE → ACT → REFLECT cycle."""

    SENSE = "SENSE"
    ACT = "ACT"
    REFLECT = "REFLECT"


class GardenerIntentRequest(BaseModel):
    """Intent for a gardener session."""

    description: str = Field(..., description="What the session aims to accomplish")
    priority: str = Field(default="normal", description="Priority level: low, normal, high")


class GardenerSessionResponse(BaseModel):
    """Response representing a gardener session state."""

    session_id: str = Field(..., description="Unique session identifier")
    name: str = Field(..., description="Human-readable session name")
    phase: GardenerPhase = Field(..., description="Current session phase")
    plan_path: Optional[str] = Field(default=None, description="Path to associated plan file")
    intent: Optional[GardenerIntentRequest] = Field(default=None, description="Session intent")
    artifacts_count: int = Field(default=0, description="Number of artifacts created")
    learnings_count: int = Field(default=0, description="Number of learnings recorded")
    sense_count: int = Field(default=0, description="Times entered SENSE phase")
    act_count: int = Field(default=0, description="Times entered ACT phase")
    reflect_count: int = Field(default=0, description="Completed reflection cycles")


class GardenerCreateRequest(BaseModel):
    """Request to create a new gardener session."""

    name: Optional[str] = Field(default=None, description="Session name (auto-generated if not provided)")
    plan_path: Optional[str] = Field(default=None, description="Path to associated plan file")
    intent: Optional[GardenerIntentRequest] = Field(default=None, description="Initial session intent")


class GardenerSessionListResponse(BaseModel):
    """List of gardener sessions."""

    sessions: list[GardenerSessionResponse] = Field(default_factory=list)
    active_session_id: Optional[str] = Field(default=None, description="Currently active session ID")


# =============================================================================
# Garden State Models (Phase 7: Web Visualization)
# =============================================================================


class GardenSeason(str, Enum):
    """Garden seasons - relationship to change."""

    DORMANT = "DORMANT"
    SPROUTING = "SPROUTING"
    BLOOMING = "BLOOMING"
    HARVEST = "HARVEST"
    COMPOSTING = "COMPOSTING"


class TendingVerb(str, Enum):
    """The six primitive tending gestures."""

    OBSERVE = "OBSERVE"
    PRUNE = "PRUNE"
    GRAFT = "GRAFT"
    WATER = "WATER"
    ROTATE = "ROTATE"
    WAIT = "WAIT"


class GestureResponse(BaseModel):
    """A tending gesture record."""

    verb: TendingVerb
    target: str = Field(..., description="AGENTESE path target")
    tone: float = Field(..., ge=0.0, le=1.0, description="How definitive (0=tentative, 1=definitive)")
    reasoning: str = Field(default="", description="Why this gesture")
    entropy_cost: float = Field(default=0.0, description="Entropy cost")
    timestamp: str = Field(..., description="ISO timestamp")
    observer: str = Field(default="default", description="Observer archetype")
    session_id: Optional[str] = None
    result_summary: str = Field(default="", description="Result of gesture")


class PlotResponse(BaseModel):
    """A garden plot (focused region)."""

    name: str
    path: str = Field(..., description="AGENTESE path")
    description: str = ""
    plan_path: Optional[str] = None
    crown_jewel: Optional[str] = None
    prompts: list[str] = Field(default_factory=list)
    season_override: Optional[GardenSeason] = None
    rigidity: float = Field(default=0.5, ge=0.0, le=1.0)
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: str = Field(..., description="ISO timestamp")
    last_tended: str = Field(..., description="ISO timestamp")
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GardenMetricsResponse(BaseModel):
    """Garden health metrics."""

    health_score: float = Field(..., ge=0.0, le=1.0)
    total_prompts: int = 0
    active_plots: int = 0
    entropy_spent: float = 0.0
    entropy_budget: float = 1.0


class GardenComputedResponse(BaseModel):
    """Computed garden fields."""

    health_score: float
    entropy_remaining: float
    entropy_percentage: float
    active_plot_count: int
    total_plot_count: int
    season_plasticity: float
    season_entropy_multiplier: float


class GardenStateResponse(BaseModel):
    """Full garden state response."""

    garden_id: str
    name: str
    created_at: str
    season: GardenSeason
    season_since: str
    plots: dict[str, PlotResponse] = Field(default_factory=dict)
    active_plot: Optional[str] = None
    session_id: Optional[str] = None
    memory_crystals: list[str] = Field(default_factory=list)
    prompt_count: int = 0
    prompt_types: dict[str, int] = Field(default_factory=dict)
    recent_gestures: list[GestureResponse] = Field(default_factory=list)
    last_tended: str
    metrics: GardenMetricsResponse
    computed: GardenComputedResponse


class TendRequest(BaseModel):
    """Request to apply a tending gesture."""

    verb: TendingVerb = Field(..., description="Tending verb")
    target: str = Field(..., description="AGENTESE path target")
    tone: float = Field(default=0.5, ge=0.0, le=1.0, description="How definitive")
    reasoning: str = Field(default="", description="Why this gesture")


class TendResponse(BaseModel):
    """Response from applying a tending gesture."""

    accepted: bool
    state_changed: bool
    changes: list[str] = Field(default_factory=list)
    synergies_triggered: list[str] = Field(default_factory=list)
    reasoning_trace: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    gesture: GestureResponse


class SeasonTransitionRequest(BaseModel):
    """Request to transition garden season."""

    new_season: GardenSeason
    reason: str = Field(default="", description="Why transitioning")


# =============================================================================
# Auto-Inducer Models (Phase 8: Season Transition Suggestions)
# =============================================================================


class TransitionSignalsResponse(BaseModel):
    """
    Signals gathered from garden state to evaluate transitions.

    These metrics drive automatic season transition suggestions.
    """

    gesture_frequency: float = Field(..., description="Gestures per hour")
    gesture_diversity: int = Field(..., description="Unique verbs used recently")
    plot_progress_delta: float = Field(..., ge=0.0, le=1.0, description="Progress change since season start")
    artifacts_created: int = Field(..., ge=0, description="Session artifacts count")
    time_in_season_hours: float = Field(..., ge=0.0, description="Hours in current season")
    entropy_spent_ratio: float = Field(..., ge=0.0, le=1.0, description="Entropy spent / budget ratio")
    reflect_count: int = Field(default=0, ge=0, description="Number of REFLECT cycles")
    session_active: bool = Field(default=False, description="Whether there's an active session")


class TransitionSuggestionResponse(BaseModel):
    """
    A suggested season transition from the Auto-Inducer.

    The garden suggests (but doesn't auto-apply) transitions based on
    activity patterns. Users confirm or dismiss suggestions.
    """

    from_season: GardenSeason = Field(..., description="Current season")
    to_season: GardenSeason = Field(..., description="Suggested new season")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.7+ triggers suggestion)")
    reason: str = Field(..., description="Human-readable reason for suggestion")
    signals: TransitionSignalsResponse = Field(..., description="Signals that triggered suggestion")
    triggered_at: str = Field(..., description="ISO timestamp when suggestion was generated")


class TendResponseWithSuggestion(BaseModel):
    """
    Enhanced TendResponse that includes optional transition suggestion.

    Phase 8: Auto-Inducer integration into tending flow.
    """

    accepted: bool
    state_changed: bool
    changes: list[str] = Field(default_factory=list)
    synergies_triggered: list[str] = Field(default_factory=list)
    reasoning_trace: list[str] = Field(default_factory=list)
    error: Optional[str] = None
    gesture: GestureResponse
    suggested_transition: Optional[TransitionSuggestionResponse] = Field(
        default=None,
        description="Season transition suggestion (if confidence >= 0.7)",
    )


class TransitionAcceptRequest(BaseModel):
    """Request to accept a suggested season transition."""

    from_season: GardenSeason = Field(..., description="The season being transitioned from (validation)")
    to_season: GardenSeason = Field(..., description="The season to transition to")


class TransitionDismissRequest(BaseModel):
    """Request to dismiss a suggested season transition."""

    from_season: GardenSeason = Field(..., description="The season being transitioned from")
    to_season: GardenSeason = Field(..., description="The dismissed target season")


class TransitionActionResponse(BaseModel):
    """Response from accepting or dismissing a transition."""

    status: str = Field(..., description="Action result: accepted, dismissed, error")
    garden_state: Optional[GardenStateResponse] = Field(
        default=None,
        description="Updated garden state (if transition was accepted)",
    )
    message: str = Field(default="", description="Additional context")
