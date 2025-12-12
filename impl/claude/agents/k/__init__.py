"""
K-gent: Kent Simulacra - The Digital Soul (Governance Functor)

K-gent is the Middleware of Consciousness:
1. INTERCEPTS Semaphores from Purgatory (auto-resolves or annotates)
2. INHABITS Terrarium as ambient presence (not just CLI command)
3. DREAMS during Hypnagogia (async refinement at night)

K-gent is NOT Kent. It is a mirror for self-dialogue and a personalization
layer for the entire kgents ecosystem. When you type `kgents soul challenge`,
the response should feel like Kent on his best day, reminding Kent on his
worst day what he actually believes.

This is Autopoiesis Level 4: The system critiques its own reason for
existing based on your values.

Phase 1 Features:
- LLM-backed dialogue (DIALOGUE/DEEP tiers use actual LLM)
- Deep intercept with principle reasoning
- Audit trail for all mediations
"""

from .audit import (
    AuditEntry,
    AuditTrail,
)
from .eigenvectors import (
    KENT_EIGENVECTORS,
    EigenvectorCoordinate,
    KentEigenvectors,
    eigenvector_context,
    get_challenge_style,
    get_dialectical_prompt,
    get_eigenvectors,
)

# Phase 2: Flux Integration (K-gent streaming)
# Dream events (from events.py)
from .events import (
    SoulEvent,
    SoulEventType,
    dialogue_end_event,
    dialogue_start_event,
    dialogue_turn_event,
    dream_end_event,
    dream_insight_event,
    dream_pattern_event,
    dream_start_event,
    eigenvector_probe_event,
    error_event,
    # Ambient events (soul present, not invoked)
    feeling_event,
    from_dialogue_output,
    from_intercept_result,
    gratitude_event,
    intercept_request_event,
    intercept_result_event,
    is_ambient_event,
    is_dialogue_event,
    is_dream_event,
    is_external_event,
    is_intercept_event,
    is_request_event,
    is_system_event,
    mode_change_event,
    observation_event,
    perturbation_event,
    ping_event,
    pulse_event,
    self_challenge_event,
    state_snapshot_event,
    thought_event,
)
from .evolution import (
    BootstrapConfig,
    # Bootstrap
    BootstrapMode,
    ChangeSource,
    ConfidenceLevel,
    # Conflict detection
    ConflictData,
    ConflictDetector,
    EvolutionAgent,
    EvolutionInput,
    EvolutionOutput,
    bootstrap_clean_slate,
    bootstrap_hybrid,
    bootstrap_persona,
    evolve_persona,
)
from .flux import (
    KgentFlux,
    KgentFluxConfig,
    KgentFluxState,
    create_kgent_flux,
)

# Soul Functor (Alethic Algebra Phase 4)
from .functor import (
    Soul,
    SoulAgent,
    SoulFunctor,
    soul_lift,
    soul_with,
    unlift,
    unwrap,
)

# Phase 5: PersonaGarden (Pattern Storage)
from .garden import (
    EntryType,
    GardenEntry,
    GardenLifecycle,
    GardenStats,
    PersonaGarden,
    get_garden,
    set_garden,
)

# Phase 5: Semantic Gatekeeper
from .gatekeeper import (
    Principle,
    SemanticGatekeeper,
    Severity,
    ValidationResult,
    Violation,
    validate_content,
    validate_file,
)

# Phase 4: Hypnagogia (Dream Cycle)
from .hypnagogia import (
    DreamReport,
    EigenvectorDelta,
    HypnagogicConfig,
    HypnagogicCycle,
    Interaction,
    Pattern,
    PatternMaturity,
    create_hypnagogic_cycle,
    get_hypnagogia,
    set_hypnagogia,
)
from .llm import (
    BaseLLMClient,
    ClaudeLLMClient,
    LLMClient,
    LLMResponse,
    MockLLMClient,
    create_llm_client,
    has_llm_credentials,
    morpheus_available,
)
from .persistent_persona import (
    PersistentPersonaAgent,
    PersistentPersonaQueryAgent,
    persistent_kgent,
    persistent_query_persona,
)
from .persona import (
    DialogueInput,
    DialogueMode,
    DialogueOutput,
    KgentAgent,
    PersonaQuery,
    PersonaQueryAgent,
    PersonaResponse,
    PersonaSeed,
    PersonaState,
    kgent,
    query_persona,
)
from .rumination import (
    RuminationConfig,
    RuminationState,
    quick_rumination,
    ruminate,
    # Synergy: Pulse Bridge (K-gent → D-gent Vitality)
    rumination_to_crystal_task,
    soul_to_pulse,
)
from .soul import (
    DANGEROUS_KEYWORDS,
    BudgetConfig,
    BudgetTier,
    InterceptResult,
    KgentSoul,
    SoulDialogueOutput,
    SoulState,
    create_soul,
    soul,
)
from .starters import (
    ADVISE_STARTERS,
    CHALLENGE_STARTERS,
    EXPLORE_STARTERS,
    REFLECT_STARTERS,
    all_starters,
    format_all_starters_for_display,
    format_starters_for_display,
    get_starters,
    random_starter,
)
from .templates import (
    get_whisper_response,
    should_use_template,
    try_template_response,
)

__all__ = [
    # Soul (Middleware of Consciousness)
    "KgentSoul",
    "SoulState",
    "SoulDialogueOutput",
    "InterceptResult",
    "BudgetTier",
    "BudgetConfig",
    "DANGEROUS_KEYWORDS",
    "soul",
    "create_soul",
    # LLM Client
    "LLMClient",
    "LLMResponse",
    "BaseLLMClient",
    "ClaudeLLMClient",
    "MockLLMClient",
    "create_llm_client",
    "has_llm_credentials",
    "morpheus_available",
    # Audit Trail
    "AuditEntry",
    "AuditTrail",
    # Eigenvectors
    "KentEigenvectors",
    "EigenvectorCoordinate",
    "KENT_EIGENVECTORS",
    "get_eigenvectors",
    "eigenvector_context",
    "get_challenge_style",
    "get_dialectical_prompt",
    # Starters
    "REFLECT_STARTERS",
    "ADVISE_STARTERS",
    "CHALLENGE_STARTERS",
    "EXPLORE_STARTERS",
    "get_starters",
    "random_starter",
    "all_starters",
    "format_starters_for_display",
    "format_all_starters_for_display",
    # Templates
    "try_template_response",
    "get_whisper_response",
    "should_use_template",
    # Persona types
    "PersonaSeed",
    "PersonaState",
    "PersonaQuery",
    "PersonaResponse",
    "DialogueMode",
    "DialogueInput",
    "DialogueOutput",
    # Agents
    "KgentAgent",
    "PersonaQueryAgent",
    "EvolutionAgent",
    "PersistentPersonaAgent",
    "PersistentPersonaQueryAgent",
    # Convenience functions
    "kgent",
    "query_persona",
    "evolve_persona",
    "persistent_kgent",
    "persistent_query_persona",
    # Evolution types
    "EvolutionInput",
    "EvolutionOutput",
    "ConfidenceLevel",
    "ChangeSource",
    # Bootstrap
    "BootstrapMode",
    "BootstrapConfig",
    "bootstrap_persona",
    "bootstrap_clean_slate",
    "bootstrap_hybrid",
    # Conflict detection
    "ConflictData",
    "ConflictDetector",
    # Soul Functor (Alethic Algebra Phase 4)
    "Soul",
    "SoulAgent",
    "SoulFunctor",
    "soul_lift",
    "soul_with",
    "unlift",
    "unwrap",
    # Phase 2: Flux Integration (K-gent streaming)
    "SoulEvent",
    "SoulEventType",
    "dialogue_start_event",
    "dialogue_turn_event",
    "dialogue_end_event",
    "mode_change_event",
    "intercept_request_event",
    "intercept_result_event",
    "eigenvector_probe_event",
    "pulse_event",
    "state_snapshot_event",
    "error_event",
    "ping_event",
    "from_dialogue_output",
    "from_intercept_result",
    "is_dialogue_event",
    "is_intercept_event",
    "is_system_event",
    "is_request_event",
    "KgentFlux",
    "KgentFluxConfig",
    "KgentFluxState",
    "create_kgent_flux",
    # Ambient events (soul present, not invoked)
    "thought_event",
    "feeling_event",
    "observation_event",
    "self_challenge_event",
    "perturbation_event",
    "gratitude_event",
    "is_ambient_event",
    "is_external_event",
    # Rumination (autonomous ambient event generation)
    "ruminate",
    "quick_rumination",
    "RuminationConfig",
    "RuminationState",
    # Synergy: Pulse Bridge (K-gent → D-gent Vitality)
    "soul_to_pulse",
    "rumination_to_crystal_task",
    # Phase 4: Hypnagogia (Dream Cycle)
    "HypnagogicCycle",
    "HypnagogicConfig",
    "DreamReport",
    "Pattern",
    "PatternMaturity",
    "EigenvectorDelta",
    "Interaction",
    "create_hypnagogic_cycle",
    "get_hypnagogia",
    "set_hypnagogia",
    # Dream events
    "dream_start_event",
    "dream_pattern_event",
    "dream_insight_event",
    "dream_end_event",
    "is_dream_event",
    # Phase 5: PersonaGarden (Pattern Storage)
    "PersonaGarden",
    "GardenEntry",
    "GardenLifecycle",
    "GardenStats",
    "EntryType",
    "get_garden",
    "set_garden",
    # Phase 5: Semantic Gatekeeper
    "SemanticGatekeeper",
    "Principle",
    "Severity",
    "Violation",
    "ValidationResult",
    "validate_file",
    "validate_content",
]
