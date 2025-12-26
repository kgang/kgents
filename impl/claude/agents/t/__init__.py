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
# Import WitnessProbe for law validation (replacement for law_validator.py)
from .probes.witness_probe import (
    WitnessProbe,
    WitnessConfig,
    witness_probe,
    IDENTITY_LAW,
    ASSOCIATIVITY_LAW,
)
# Import all remaining probes (dataclass errors fixed)
from .probes import (
    ChaosType,
    ChaosProbe,
    ChaosConfig,
    JudgeProbe,
    JudgeConfig,
    TrustProbe,
    TrustConfig,
)

# Operad for probe composition
try:
    from agents.operad.domains.probe import PROBE_OPERAD
except ImportError:
    PROBE_OPERAD = None  # Fallback if operad not available

# ARCHIVED: E-gent integration (2025-12-16)
# Removed: evolution_integration.py deleted (see commit for restoration if needed)
from .failing import (
    FailingAgent,
    FailingConfig,
    FailureType,
    failing_agent,
    import_failing,
    syntax_failing,
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
# DEPRECATED: law_validator.py removed (2025-12-25)
# Use WitnessProbe instead - all functionality migrated
# See: agents.t.probes.WitnessProbe for law validation
from .metrics import (
    MetricsAgent,
    PerformanceMetrics,
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
from .trustgate import (
    Proposal,
    TrustDecision,
    TrustGate,
    create_trust_gate,
)

# Note: Legacy compat.py removed (2025-12-25)
# MockAgent, FixtureAgent, SpyAgent, CounterAgent deprecated.
# Use NullProbe, WitnessProbe instead.

# Legacy Config types removed (2025-12-25)
# Use NullConfig, WitnessConfig instead.
# Legacy convenience functions removed (2025-12-25)
# Use null_probe(), witness_probe() instead.

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
    "WitnessProbe",  # CATEGORICAL mode - law verification (replaces LawValidator)
    "ChaosType",
    "ChaosProbe",
    "JudgeProbe",
    "TrustProbe",
    # Probe Configs (New)
    "NullConfig",
    "WitnessConfig",
    "witness_probe",  # Convenience function for WitnessProbe
    "IDENTITY_LAW",
    "ASSOCIATIVITY_LAW",
    "ChaosConfig",
    "JudgeConfig",
    "TrustConfig",
    # Operad
    "PROBE_OPERAD",
    # Type I - Nullifiers (LEGACY - removed 2025-12-25, use NullProbe)
    # Type II - Saboteurs (LEGACY - removed 2025-12-25, use ChaosProbe)
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
    # Type III - Observers (LEGACY - use WitnessProbe)
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
    # Law Validation - REMOVED (2025-12-25)
    # Use WitnessProbe instead: from agents.t.probes import WitnessProbe
    # Migration: law_validator.py functionality → WitnessProbe with PolicyTrace
    # E-gent Integration - REMOVED (2025-12-25)
    # Archived with E-gent removal: evolution_integration.py deleted
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
