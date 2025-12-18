"""
F-gents: Flow Agents

The unified substrate for continuous agent interaction:
- Chat: Streaming conversation with context management
- Research: Tree of thought exploration
- Collaboration: Multi-agent blackboard patterns

See: spec/f-gents/README.md

Migration Note:
The old Forge implementation (intent, contract, crystallize) is deprecated.
Use Flow, FlowConfig, FlowState for new code.
Old exports are still available for backward compatibility.
"""

# === New Flow Implementation ===
from agents.f.config import (
    ChatConfig,
    CollaborationConfig,
    FlowConfig,
    ResearchConfig,
)

# === Deprecated Forge Implementation (Backward Compatibility) ===
# TODO: Add deprecation warnings and eventually remove
from agents.f.contract import (
    CompositionRule,
    Contract,
    Invariant,
    synthesize_contract,
)
from agents.f.crystallize import (
    Artifact,
    ArtifactMetadata,
    ArtifactStatus,
    Version,
    VersionBump,
    assemble_artifact,
    crystallize,
    determine_version_bump,
    extract_tags_from_intent,
    register_with_lgent,
    save_artifact,
)
from agents.f.flow import (
    AgentProtocol,
    Flow,
    FlowAgent,
    FlowEvent,
)
from agents.f.intent import (
    Dependency,
    DependencyType,
    Example,
    Intent,
    parse_intent,
)
from agents.f.j_integration import (
    BoundedComplexity,
    DeterministicOnly,
    EntropyAware,
    IntentFilter,
    RealityGate,
    admits_intent,
    create_safe_gate,
    create_strict_gate,
    gate_intent,
)
from agents.f.modalities import (
    ChatFlow,
    Message,
    SlidingContext,
    SummarizingContext,
    Turn,
    count_tokens,
)
from agents.f.operad import (
    CHAT_OPERAD,
    COLLABORATION_OPERAD,
    FLOW_OPERAD,
    RESEARCH_OPERAD,
    Law,
    Operad,
    Operation,
    get_operad,
)

# Alias for backward compatibility
OpLaw = Law
from agents.f.pipeline import FlowPipeline
from agents.f.polynomial import (
    CHAT_POLYNOMIAL,
    COLLABORATION_POLYNOMIAL,
    FLOW_POLYNOMIAL,
    RESEARCH_POLYNOMIAL,
    FlowPolynomial,
    get_polynomial,
)
from agents.f.prototype import (
    PrototypeConfig,
    SourceCode,
    StaticAnalysisReport,
    ValidationCategory,
    ValidationResult,
    ValidationStatus,
    generate_prototype,
    generate_prototype_async,
    run_static_analysis,
)
from agents.f.state import (
    ContributionType,
    FlowState,
    HypothesisStatus,
    Permission,
)
from agents.f.validate import (
    ExampleResult,
    ExampleResultStatus,
    InvariantCheckResult,
    TestResult,
    TestResultStatus,
    ValidationConfig,
    ValidationReport,
    ValidationTestResult,
    ValidationTestStatus,
    VerdictStatus,
    run_test,
    validate,
    validate_with_self_healing,
    verify_invariant,
)

__all__ = [
    # === New Flow API ===
    # Core
    "Flow",
    "FlowAgent",
    "FlowEvent",
    "AgentProtocol",
    # State
    "FlowState",
    "HypothesisStatus",
    "ContributionType",
    "Permission",
    # Config
    "FlowConfig",
    "ChatConfig",
    "ResearchConfig",
    "CollaborationConfig",
    # Modalities - Chat
    "ChatFlow",
    "Turn",
    "Message",
    "SlidingContext",
    "SummarizingContext",
    "count_tokens",
    # Polynomial
    "FlowPolynomial",
    "FLOW_POLYNOMIAL",
    "CHAT_POLYNOMIAL",
    "RESEARCH_POLYNOMIAL",
    "COLLABORATION_POLYNOMIAL",
    "get_polynomial",
    # Operad
    "Operation",
    "OpLaw",
    "Operad",
    "FLOW_OPERAD",
    "CHAT_OPERAD",
    "RESEARCH_OPERAD",
    "COLLABORATION_OPERAD",
    "get_operad",
    # Pipeline
    "FlowPipeline",
    # === Deprecated Forge API (for backward compatibility) ===
    # Intent parsing (Phase 1)
    "Dependency",
    "DependencyType",
    "Example",
    "Intent",
    "parse_intent",
    # Contract synthesis (Phase 2)
    "CompositionRule",
    "Contract",
    "Invariant",
    "synthesize_contract",
    # Prototype generation (Phase 3)
    "PrototypeConfig",
    "SourceCode",
    "StaticAnalysisReport",
    "ValidationCategory",
    "ValidationResult",
    "ValidationStatus",
    "generate_prototype",
    "generate_prototype_async",
    "run_static_analysis",
    # Validation (Phase 4)
    "ExampleResult",
    "ExampleResultStatus",
    "InvariantCheckResult",
    "TestResult",
    "TestResultStatus",
    "ValidationConfig",
    "ValidationReport",
    "ValidationTestResult",
    "ValidationTestStatus",
    "VerdictStatus",
    "run_test",
    "validate",
    "validate_with_self_healing",
    "verify_invariant",
    # Crystallization (Phase 5)
    "Artifact",
    "ArtifactMetadata",
    "ArtifactStatus",
    "Version",
    "VersionBump",
    "assemble_artifact",
    "crystallize",
    "determine_version_bump",
    "extract_tags_from_intent",
    "register_with_lgent",
    "save_artifact",
    # Reality contracts (J-gent integration)
    "RealityGate",
    "DeterministicOnly",
    "BoundedComplexity",
    "EntropyAware",
    "IntentFilter",
    "create_safe_gate",
    "create_strict_gate",
    "admits_intent",
    "gate_intent",
]
