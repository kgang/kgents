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

Type VIII - Security & Permissions (Phase 5):
- PermissionClassifier: ABAC (Attribute-Based Access Control)
- AgentContext: Execution context with security attributes
- ToolCapabilities: Tool requirement declarations
- TemporaryToken: Short-lived permission tokens (15-60 min)
- SecureToolExecutor: Permission-aware tool execution
- AuditLogger: Comprehensive audit trail for compliance

Type IX - Multi-Tool Orchestration (Phase 6):
- SequentialOrchestrator: Chain tools in sequence (explicit wrapper for >>)
- ParallelOrchestrator: Execute tools concurrently (product functor)
- SupervisorPattern: Delegate tasks to worker tools (comma category)
- HandoffPattern: Transfer control between tools (natural transformation)
- DynamicToolSelector: Context-based tool selection (functor from Context → Tool)

Type X - Trust Gate (Phase 7: Capital Integration):
- TrustGate: Capital-backed gate with Fool's Bypass (OCap pattern)
- Proposal: Action to be evaluated by the gate
- TrustDecision: Result with approval status and capital changes
- Algebraic cost computation via CostFactor composition

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

from .counter import (
    CounterAgent,
)
from .evolution_integration import (
    EvolutionPipelineValidationReport,
    PipelineStageReport,
    PipelineValidationConfig,
    evolve_with_law_validation,
    validate_evolution_pipeline,
    validate_evolution_stages_from_pipeline,
)
from .executor import (
    CircuitBreakerConfig,
    CircuitBreakerError,
    CircuitBreakerState,
    CircuitBreakerTool,
    # Circuit Breaker
    CircuitState,
    # Config
    RetryConfig,
    RetryExecutor,
    RobustToolExecutor,
    SecureToolExecutor,
    # Executors
    ToolExecutor,
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
from .mcp_client import (
    HttpSseTransport,
    JsonRpcError,
    # JSON-RPC
    JsonRpcRequest,
    JsonRpcResponse,
    # Client
    MCPClient,
    MCPResource,
    MCPServerInfo,
    MCPTool,
    MCPToolSchema,
    # Transport
    MCPTransport,
    # MCP Protocol Types
    MCPTransportType,
    StdioTransport,
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
from .orchestration import (
    CostBasedSelection,
    # Dynamic Selection
    DynamicToolSelector,
    EnvironmentBasedSelection,
    HandoffCondition,
    # Handoff
    HandoffPattern,
    HandoffRule,
    LatencyBasedSelection,
    # Parallel
    ParallelOrchestrator,
    ParallelResult,
    SelectionContext,
    SelectionStrategy,
    # Sequential
    SequentialOrchestrator,
    # Supervisor
    SupervisorPattern,
    Task,
    WorkerAssignment,
)
from .permissions import (
    # Context and capabilities
    AgentContext,
    AuditLog,
    # Audit
    AuditLogger,
    # Classifier
    PermissionClassifier,
    # Permission types
    PermissionLevel,
    SecurityLevel,
    SensitivityLevel,
    # Tokens
    TemporaryToken,
    ToolCapabilities,
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
from .registry import (
    ToolEntry,
    ToolRegistry,
    get_registry,
    set_registry,
)
from .spy import (
    SpyAgent,
    spy_agent,
)
from .tool import (
    CachedTool,
    PassthroughTool,
    RetryTool,
    Tool,
    ToolError,
    ToolErrorType,
    ToolIdentity,
    ToolInterface,
    ToolMeta,
    ToolRuntime,
    ToolTrace,
    TracedTool,
)
from .trustgate import (
    Proposal,
    TrustDecision,
    TrustGate,
    create_trust_gate,
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
    "SecureToolExecutor",
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
    # Type VIII - Security & Permissions (Phase 5)
    "PermissionLevel",
    "SecurityLevel",
    "SensitivityLevel",
    "AgentContext",
    "ToolCapabilities",
    "TemporaryToken",
    "PermissionClassifier",
    "AuditLogger",
    "AuditLog",
    # Type IX - Multi-Tool Orchestration (Phase 6)
    "SequentialOrchestrator",
    "ParallelOrchestrator",
    "ParallelResult",
    "SupervisorPattern",
    "Task",
    "WorkerAssignment",
    "HandoffPattern",
    "HandoffCondition",
    "HandoffRule",
    "DynamicToolSelector",
    "SelectionContext",
    "SelectionStrategy",
    "CostBasedSelection",
    "LatencyBasedSelection",
    "EnvironmentBasedSelection",
    # Type X - Trust Gate (Phase 7: Capital Integration)
    "Proposal",
    "TrustDecision",
    "TrustGate",
    "create_trust_gate",
]
