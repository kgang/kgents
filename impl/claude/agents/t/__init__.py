"""
T-gents: Test Agents for kgents

Category Theory-based testing agents for verification, perturbation, and observation.

Philosophy:
- Testing is algebraic verification, not just examples
- T-gents prove categorical properties: associativity, identity, resilience
- All T-gents marked with __is_test__ = True
- Composable with other agents via >> operator

TruthFunctor Protocol (NEW):
All T-gents are being migrated to the TruthFunctor protocol, which provides:
- DP-native semantics: (states, actions, transition, reward, gamma)
- Automatic PolicyTrace emission
- Constitutional reward scoring (7 principles)
- AnalysisMode mapping (CATEGORICAL, EPISTEMIC, DIALECTICAL, GENERATIVE)

Core Types:
- TruthFunctor[S, A, B]: Base class for all verification probes
- PolicyTrace[B]: Writer monad for accumulated verification trace
- ConstitutionalScore: Reward based on 7 principles (ethical, composable, etc.)
- TruthVerdict[B]: Final verdict with confidence and reasoning

Five Probe Types (replacing old T-gent types):
- NullProbe (was MockAgent, FixtureAgent) - EPISTEMIC mode
- ChaosProbe (was FailingAgent, NoiseAgent, etc.) - DIALECTICAL mode
- WitnessProbe (was SpyAgent, CounterAgent, etc.) - CATEGORICAL mode
- JudgeProbe (was JudgeAgent, OracleAgent) - EPISTEMIC mode
- TrustProbe (was TrustGate) - GENERATIVE mode

Legacy T-gent Types (still supported):

Type I - Nullifiers (Constants & Fixtures):
- MockAgent: Constant morphism c_b: A -> b
- FixtureAgent: Deterministic lookup f: A -> B

Type II - Saboteurs (Chaos & Perturbation):
- FailingAgent: Bottom morphism: A -> Error
- NoiseAgent: Semantic perturbation N_e: A -> A + e
- LatencyAgent: Temporal delay L_d: (A, t) -> (A, t + d)
- FlakyAgent: Probabilistic failure F_p: A -> B | {error}

Type III - Observers (Identity with Side Effects):
- SpyAgent: Writer Monad S: A -> (A, [A])
- PredicateAgent: Gate P: A -> A | {error}
- CounterAgent: Invocation counter C: A -> A
- MetricsAgent: Performance profiler M: A -> A

Type IV - Critics (Semantic Evaluation):
- JudgeAgent: LLM-as-Judge semantic evaluation J: (A, Criteria) -> Judgment
- PropertyAgent: Property-based testing P: (A, Property) -> TestResult
- OracleAgent: Differential testing O: (A, A') -> DiffResult

Type V - Trust Gate (Capital Integration):
- TrustGate: Capital-backed gate with Fool's Bypass (OCap pattern)
- Proposal: Action to be evaluated by the gate
- TrustDecision: Result with approval status and capital changes

Usage:
    # New TruthFunctor protocol
    from agents.t import TruthFunctor, PolicyTrace, ConstitutionalScore
    from agents.t.probes import NullProbe, ChaosProbe, WitnessProbe

    # Legacy T-gents (still supported)
    from agents.t import MockAgent, FailingAgent, SpyAgent

    # Mock expensive operations
    mock = MockAgent(MockConfig(output="result"))

    # Test retry logic
    failing = FailingAgent(FailingConfig(
        error_type=FailureType.NETWORK,
        fail_count=2,
        recovery_token="Success"
    ))

    # Observe pipeline data
    spy = SpyAgent(label="Hypotheses")
    pipeline = generate >> spy >> validate

    # For tool use, import from agents.u instead:
    from agents.u import Tool, ToolRegistry, MCPClient
"""

import warnings
from typing import Any

# TruthFunctor protocol (new DP-native verification)
from .truth_functor import (
    AnalysisMode,
    ConstitutionalScore,
    TruthVerdict,
    ProbeState,
    ProbeAction,
    TraceEntry,
    PolicyTrace,
    TruthFunctor,
    ComposedProbe,
)

# New probe implementations
from .probes import (
    NullProbe,
    NullConfig,
)
# TODO: Import remaining probes when dataclass errors are fixed
# from .probes import (
#     ChaosType,
#     ChaosProbe,
#     WitnessProbe,
#     JudgeProbe,
#     TrustProbe,
#     ChaosConfig,
#     WitnessConfig,
#     JudgeConfig,
#     TrustConfig,
# )

# Backwards compatibility (legacy types that emit deprecation warnings)
from .compat import (
    MockAgent as MockAgentCompat,
    FixtureAgent as FixtureAgentCompat,
    FailingAgent as FailingAgentCompat,
    NoiseAgent as NoiseAgentCompat,
    LatencyAgent as LatencyAgentCompat,
    FlakyAgent as FlakyAgentCompat,
    SpyAgent as SpyAgentCompat,
    PredicateAgent as PredicateAgentCompat,
    CounterAgent as CounterAgentCompat,
    MetricsAgent as MetricsAgentCompat,
    JudgeAgent as JudgeAgentCompat,
    OracleAgent as OracleAgentCompat,
    TrustGate as TrustGateCompat,
)

# Operad for probe composition
try:
    from agents.operad.domains.probe import PROBE_OPERAD
except ImportError:
    PROBE_OPERAD = None  # Fallback if operad not available

from .counter import (
    CounterAgent,
)

# ARCHIVED: E-gent integration (2025-12-16)
# These are kept for backwards compatibility but raise NotImplementedError
from .evolution_integration import (
    EvolutionPipelineValidationReport,
    PipelineStageReport,
    PipelineValidationConfig,
    evolve_with_law_validation,
    validate_evolution_pipeline,
    validate_evolution_stages_from_pipeline,
)
from .failing import (
    FailingAgent,
    FailingConfig,
    FailureType,
    failing_agent,
    import_failing,
    syntax_failing,
)
from .fixture import (
    FixtureAgent,
    FixtureConfig,
    fixture_agent,
)
from .flaky import (
    FlakyAgent,
)

# Test Helpers (convenience functions)
from .helpers import (
    assert_agent_output,
    assert_agent_raises,
    assert_composition_associative,
    assert_functor_composition,
    assert_functor_identity,
    counting_agent,
    quick_mock,
)
from .judge import (
    JudgeAgent,
    JudgmentCriteria,
    JudgmentResult,
    self_evaluate_t_gent,
)
from .latency import (
    LatencyAgent,
)
from .law_validator import (
    LawValidationReport,
    LawValidator,
    LawViolation,
    check_associativity,
    check_functor_composition,
    check_functor_identity,
    check_left_identity,
    check_monad_associativity,
    check_monad_left_identity,
    check_monad_right_identity,
    check_right_identity,
    validate_evolution_pipeline_laws,
)
from .metrics import (
    MetricsAgent,
    PerformanceMetrics,
)
from .mock import (
    MockAgent,
    MockConfig,
    mock_agent,
)
from .noise import (
    NoiseAgent,
    NoiseConfig,
    NoiseType,
)
from .oracle import (
    DiffResult,
    OracleAgent,
    RegressionOracle,
    numeric_equality,
    semantic_equality,
)
from .predicate import (
    PredicateAgent,
    is_non_negative,
    is_positive,
    not_empty,
    not_none,
    predicate_agent,
)
from .property import (
    ChoiceGenerator,
    IntGenerator,
    PropertyAgent,
    PropertyTestResult,
    StringGenerator,
    identity_property,
    length_preserved_property,
    not_none_property,
)
from .spy import (
    SpyAgent,
    spy_agent,
)
from .trustgate import (
    Proposal,
    TrustDecision,
    TrustGate,
    create_trust_gate,
)

__all__ = [
    # TruthFunctor Protocol (DP-Native Verification)
    "AnalysisMode",
    "ConstitutionalScore",
    "TruthVerdict",
    "ProbeState",
    "ProbeAction",
    "TraceEntry",
    "PolicyTrace",
    "TruthFunctor",
    "ComposedProbe",
    # New Probe Types
    "NullProbe",
    # TODO: Export remaining probes when implemented
    # "ChaosType",
    # "ChaosProbe",
    # "WitnessProbe",
    # "JudgeProbe",
    # "TrustProbe",
    # Probe Configs
    "NullConfig",
    # "ChaosConfig",
    # "WitnessConfig",
    # "JudgeConfig",
    # "TrustConfig",
    # Operad
    "PROBE_OPERAD",
    # Type I - Nullifiers
    "MockAgent",
    "MockConfig",
    "mock_agent",
    "FixtureAgent",
    "FixtureConfig",
    "fixture_agent",
    # Type II - Saboteurs
    "FailingAgent",
    "FailingConfig",
    "FailureType",
    "failing_agent",
    "syntax_failing",
    "import_failing",
    "NoiseAgent",
    "NoiseConfig",
    "NoiseType",
    "LatencyAgent",
    "FlakyAgent",
    # Type III - Observers
    "SpyAgent",
    "spy_agent",
    "PredicateAgent",
    "predicate_agent",
    "CounterAgent",
    "MetricsAgent",
    "PerformanceMetrics",
    # Type IV - Critics
    "JudgeAgent",
    "JudgmentCriteria",
    "JudgmentResult",
    "self_evaluate_t_gent",
    "PropertyAgent",
    "PropertyTestResult",
    "IntGenerator",
    "StringGenerator",
    "ChoiceGenerator",
    "identity_property",
    "not_none_property",
    "length_preserved_property",
    "OracleAgent",
    "RegressionOracle",
    "DiffResult",
    "semantic_equality",
    "numeric_equality",
    # Predicate helpers
    "not_none",
    "not_empty",
    "is_positive",
    "is_non_negative",
    # Law Validation (Cross-pollination T2.6)
    "LawValidator",
    "LawValidationReport",
    "LawViolation",
    "check_associativity",
    "check_left_identity",
    "check_right_identity",
    "check_functor_identity",
    "check_functor_composition",
    "check_monad_left_identity",
    "check_monad_right_identity",
    "check_monad_associativity",
    "validate_evolution_pipeline_laws",
    # E-gent Integration (ARCHIVED 2025-12-16)
    # Kept for backwards compatibility but raise NotImplementedError
    "PipelineValidationConfig",
    "PipelineStageReport",
    "EvolutionPipelineValidationReport",
    "validate_evolution_pipeline",
    "validate_evolution_stages_from_pipeline",
    "evolve_with_law_validation",
    # Type V - Trust Gate (Capital Integration)
    "Proposal",
    "TrustDecision",
    "TrustGate",
    "create_trust_gate",
    # Test Helpers (convenience functions)
    "assert_agent_output",
    "assert_agent_raises",
    "assert_composition_associative",
    "assert_functor_identity",
    "assert_functor_composition",
    "quick_mock",
    "counting_agent",
]


# Deprecated exports that moved to agents.u
_DEPRECATED_TO_U: dict[str, str] = {
    # Core
    "Tool": "core",
    "ToolMeta": "core",
    "ToolIdentity": "core",
    "ToolInterface": "core",
    "ToolRuntime": "core",
    "ToolError": "core",
    "ToolErrorType": "core",
    "ToolTrace": "core",
    "PassthroughTool": "core",
    # Wrappers
    "TracedTool": "core",
    "CachedTool": "core",
    "RetryTool": "core",
    # Registry
    "ToolRegistry": "registry",
    "ToolEntry": "registry",
    "get_registry": "registry",
    "set_registry": "registry",
    # Executor
    "ToolExecutor": "executor",
    "RetryExecutor": "executor",
    "RobustToolExecutor": "executor",
    "SecureToolExecutor": "executor",
    "CircuitState": "executor",
    "CircuitBreakerConfig": "executor",
    "CircuitBreakerState": "executor",
    "CircuitBreakerError": "executor",
    "CircuitBreakerTool": "executor",
    "RetryConfig": "executor",
    # MCP
    "MCPTransportType": "mcp",
    "MCPServerInfo": "mcp",
    "MCPToolSchema": "mcp",
    "MCPResource": "mcp",
    "JsonRpcRequest": "mcp",
    "JsonRpcResponse": "mcp",
    "JsonRpcError": "mcp",
    "MCPTransport": "mcp",
    "StdioTransport": "mcp",
    "HttpSseTransport": "mcp",
    "MCPClient": "mcp",
    "MCPTool": "mcp",
    # Permissions
    "PermissionLevel": "permissions",
    "SecurityLevel": "permissions",
    "SensitivityLevel": "permissions",
    "AgentContext": "permissions",
    "ToolCapabilities": "permissions",
    "TemporaryToken": "permissions",
    "PermissionClassifier": "permissions",
    "AuditLogger": "permissions",
    "AuditLog": "permissions",
    # Orchestration
    "SequentialOrchestrator": "orchestration",
    "ParallelOrchestrator": "orchestration",
    "ParallelResult": "orchestration",
    "SupervisorPattern": "orchestration",
    "Task": "orchestration",
    "WorkerAssignment": "orchestration",
    "HandoffPattern": "orchestration",
    "HandoffCondition": "orchestration",
    "HandoffRule": "orchestration",
    "DynamicToolSelector": "orchestration",
    "SelectionContext": "orchestration",
    "SelectionStrategy": "orchestration",
    "CostBasedSelection": "orchestration",
    "LatencyBasedSelection": "orchestration",
    "EnvironmentBasedSelection": "orchestration",
}


def __getattr__(name: str) -> Any:
    if name in _DEPRECATED_TO_U:
        module = _DEPRECATED_TO_U[name]
        warnings.warn(
            f"Importing {name} from agents.t is deprecated. "
            f"Use agents.u instead: from agents.u.{module} import {name}",
            DeprecationWarning,
            stacklevel=2,
        )
        from agents import u

        submodule = getattr(u, module)
        return getattr(submodule, name)
    raise AttributeError(f"module 'agents.t' has no attribute {name!r}")
