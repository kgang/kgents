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
    InvariantCheckResult,
    TestResult,
    TestResultStatus,
    ValidationConfig,
    ValidationReport,
    VerdictStatus,
    run_test,
    validate,
    validate_with_self_healing,
    verify_invariant,
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
    "InvariantCheckResult",
    "TestResult",
    "TestResultStatus",
    "ValidationConfig",
    "ValidationReport",
    "VerdictStatus",
    "run_test",
    "validate",
    "validate_with_self_healing",
    "verify_invariant",
]
