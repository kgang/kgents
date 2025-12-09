"""
T-gents: Test Agents for kgents

Category Theory-based testing agents for verification, perturbation, and observation.

Philosophy:
- Testing is algebraic verification, not just examples
- T-gents prove categorical properties: associativity, identity, resilience
- All T-gents marked with __is_test__ = True
- Composable with other agents via >> operator

Implemented T-gents:

Type I - Nullifiers (Constants & Fixtures):
- MockAgent: Constant morphism c_b: A → b
- FixtureAgent: Deterministic lookup f: A → B

Type II - Saboteurs (Chaos & Perturbation):
- FailingAgent: Bottom morphism ⊥: A → Error
- NoiseAgent: Semantic perturbation N_ε: A → A + ε
- LatencyAgent: Temporal delay L_Δ: (A, t) → (A, t + Δ)
- FlakyAgent: Probabilistic failure F_p: A → B ∪ {⊥}

Type III - Observers (Identity with Side Effects):
- SpyAgent: Writer Monad S: A → (A, [A])
- PredicateAgent: Gate P: A → A ∪ {⊥}
- CounterAgent: Invocation counter C: A → A
- MetricsAgent: Performance profiler M: A → A

Type IV - Critics (Semantic Evaluation):
- JudgeAgent: LLM-as-Judge semantic evaluation J: (A, Criteria) → Judgment
- PropertyAgent: Property-based testing P: (A, Property) → TestResult
- OracleAgent: Differential testing O: (A, A') → DiffResult

Type V - Tools (Phase 2: Tool Use):
- Tool[A, B]: Typed morphism for external interaction
- ToolRegistry: Catalog and discovery (L-gent integration)
- ToolTrace: Observability (W-gent integration)
- Tool wrappers: TracedTool, CachedTool, RetryTool

Type VI - Execution Runtime (Phase 3):
- ToolExecutor: Result monad wrapper for Railway Oriented Programming
- CircuitBreakerTool: Fail-fast pattern for unhealthy services
- RetryExecutor: Exponential backoff with jitter
- RobustToolExecutor: Composite executor (circuit breaker + retry + Result monad)

Type VII - MCP Integration (Phase 4):
- MCPClient: Model Context Protocol client for remote tool servers
- MCPTool: Tool[A, B] implementation for MCP remote tools
- StdioTransport: Local process communication (most common)
- HttpSseTransport: Remote HTTP/SSE communication
- JSON-RPC 2.0: Protocol message types

Usage:
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

    # Tool use (Phase 2)
    from agents.t import Tool, ToolRegistry

    # Register and discover tools
    registry = ToolRegistry()
    await registry.register(web_search_tool)
    tools = await registry.find_by_signature(str, Summary)
"""

from .failing import (
    FailingAgent,
    FailingConfig,
    FailureType,
    failing_agent,
    syntax_failing,
    import_failing,
)

from .mock import (
    MockAgent,
    MockConfig,
    mock_agent,
)

from .fixture import (
    FixtureAgent,
    FixtureConfig,
    fixture_agent,
)

from .spy import (
    SpyAgent,
    spy_agent,
)

from .predicate import (
    PredicateAgent,
    predicate_agent,
    not_none,
    not_empty,
    is_positive,
    is_non_negative,
)

from .noise import (
    NoiseAgent,
    NoiseConfig,
    NoiseType,
)

from .latency import (
    LatencyAgent,
)

from .flaky import (
    FlakyAgent,
)

from .counter import (
    CounterAgent,
)

from .metrics import (
    MetricsAgent,
    PerformanceMetrics,
)

from .judge import (
    JudgeAgent,
    JudgmentCriteria,
    JudgmentResult,
    self_evaluate_t_gent,
)

from .property import (
    PropertyAgent,
    PropertyTestResult,
    IntGenerator,
    StringGenerator,
    ChoiceGenerator,
    identity_property,
    not_none_property,
    length_preserved_property,
)

from .oracle import (
    OracleAgent,
    RegressionOracle,
    DiffResult,
    semantic_equality,
    numeric_equality,
)

from .law_validator import (
    LawValidator,
    LawValidationReport,
    LawViolation,
    check_associativity,
    check_left_identity,
    check_right_identity,
    check_functor_identity,
    check_functor_composition,
    check_monad_left_identity,
    check_monad_right_identity,
    check_monad_associativity,
    validate_evolution_pipeline_laws,
)

from .evolution_integration import (
    PipelineValidationConfig,
    PipelineStageReport,
    EvolutionPipelineValidationReport,
    validate_evolution_pipeline,
    validate_evolution_stages_from_pipeline,
    evolve_with_law_validation,
)

from .tool import (
    Tool,
    ToolMeta,
    ToolIdentity,
    ToolInterface,
    ToolRuntime,
    ToolError,
    ToolErrorType,
    ToolTrace,
    PassthroughTool,
    TracedTool,
    CachedTool,
    RetryTool,
)

from .registry import (
    ToolRegistry,
    ToolEntry,
    get_registry,
    set_registry,
)

from .executor import (
    # Circuit Breaker
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreakerState,
    CircuitBreakerError,
    CircuitBreakerTool,
    # Executors
    ToolExecutor,
    RetryExecutor,
    RobustToolExecutor,
    # Config
    RetryConfig,
)

from .mcp_client import (
    # MCP Protocol Types
    MCPTransportType,
    MCPServerInfo,
    MCPToolSchema,
    MCPResource,
    # JSON-RPC
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcError,
    # Transport
    MCPTransport,
    StdioTransport,
    HttpSseTransport,
    # Client
    MCPClient,
    MCPTool,
)

__all__ = [
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
    # E-gent Integration (Cross-pollination T2.6)
    "PipelineValidationConfig",
    "PipelineStageReport",
    "EvolutionPipelineValidationReport",
    "validate_evolution_pipeline",
    "validate_evolution_stages_from_pipeline",
    "evolve_with_law_validation",
    # Type V - Tools (Phase 2: Tool Use)
    "Tool",
    "ToolMeta",
    "ToolIdentity",
    "ToolInterface",
    "ToolRuntime",
    "ToolError",
    "ToolErrorType",
    "ToolTrace",
    "PassthroughTool",
    "TracedTool",
    "CachedTool",
    "RetryTool",
    "ToolRegistry",
    "ToolEntry",
    "get_registry",
    "set_registry",
    # Type VI - Execution Runtime (Phase 3)
    "CircuitState",
    "CircuitBreakerConfig",
    "CircuitBreakerState",
    "CircuitBreakerError",
    "CircuitBreakerTool",
    "ToolExecutor",
    "RetryExecutor",
    "RobustToolExecutor",
    "RetryConfig",
    # Type VII - MCP Integration (Phase 4)
    "MCPTransportType",
    "MCPServerInfo",
    "MCPToolSchema",
    "MCPResource",
    "JsonRpcRequest",
    "JsonRpcResponse",
    "JsonRpcError",
    "MCPTransport",
    "StdioTransport",
    "HttpSseTransport",
    "MCPClient",
    "MCPTool",
]
