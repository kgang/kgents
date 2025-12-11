"""
F-gents: Forge Agents

Permanent artifact synthesis from natural language intent.

Motto: "Intent crystallizes into artifact; contracts enable composition"
"""

from agents.f.contract import (
    CompositionRule,
    Contract,
    Invariant,
    synthesize_contract,
)
from agents.f.intent import (
    Dependency,
    DependencyType,
    Example,
    Intent,
    parse_intent,
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
from agents.f.validate import (
    ExampleResult,
    ExampleResultStatus,
    InvariantCheckResult,
    TestResult,  # Backward compat alias
    TestResultStatus,  # Backward compat alias
    ValidationConfig,
    ValidationReport,
    ValidationTestResult,  # Backward compat alias
    ValidationTestStatus,  # Backward compat alias
    VerdictStatus,
    run_test,
    validate,
    validate_with_self_healing,
    verify_invariant,
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
from agents.f.j_integration import (
    RealityGate,
    DeterministicOnly,
    BoundedComplexity,
    EntropyAware,
    IntentFilter,
    create_safe_gate,
    create_strict_gate,
    admits_intent,
    gate_intent,
)

__all__ = [
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
    "TestResult",  # Backward compat alias
    "TestResultStatus",  # Backward compat alias
    "ValidationConfig",
    "ValidationReport",
    "ValidationTestResult",  # Backward compat alias
    "ValidationTestStatus",  # Backward compat alias
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
