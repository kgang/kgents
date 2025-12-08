"""
E-gents: Evolution Agents for Code Improvement

This module provides composable agents for evolutionary code improvement:

- ASTAnalyzer: Static analysis of Python modules
- MemoryAgent: Persistent memory of past improvements
- TestAgent: Validate experiments (syntax, types, tests)
- CodeJudge: Evaluate against 7 kgents principles
- IncorporateAgent: Apply changes with git safety
- EvolutionAgent: Composed pipeline

Reliability Layers (from EVOLUTION_RELIABILITY_PLAN.md):

Layer 1 - Prompt Engineering:
- PreFlightChecker: Module health validation before LLM calls
- PromptContext: Rich context (types, errors, patterns) for generation
- build_improvement_prompt: Structured prompts with critical requirements

Layer 2 - Parsing & Validation:
- CodeParser: Multi-strategy parsing with fallbacks (4 strategies)
- SchemaValidator: Fast pre-mypy validation (constructors, types, generics)
- CodeRepairer: Incremental AST-based repair for common errors

Layer 3 - Recovery & Learning:
- RetryStrategy: Intelligent retry with failure-aware prompt refinement
- FallbackStrategy: Progressive simplification (minimal → type-only → docs)
- ErrorMemory: Track and learn from failure patterns across sessions

Architecture:
    EvolutionAgent = Ground >> Hypothesis >> Experiment >> Judge >> Sublate >> Incorporate

Usage:
    from agents.e import EvolutionPipeline, EvolutionConfig

    config = EvolutionConfig(target="bootstrap", dry_run=True)
    pipeline = EvolutionPipeline(config)
    report = await pipeline.run(modules)
"""

from .ast_analyzer import (
    ASTAnalyzer,
    ASTAnalysisInput,
    ASTAnalysisOutput,
    CodeStructure,
    analyze_module_ast,
    generate_targeted_hypotheses,
    ast_analyzer,
)

from .memory import (
    ImprovementMemory,
    ImprovementRecord,
    MemoryAgent,
    MemoryQuery,
    MemoryQueryResult,
    RecordAgent,
    RecordInput,
    memory_agent,
)

from .experiment import (
    CodeModule,
    CodeImprovement,
    Experiment,
    ExperimentStatus,
    ExperimentInput,
    ExperimentResult,
    TestAgent,
    TestInput,
    TestResult,
    extract_code,
    extract_metadata,
    get_code_preview,
    test_agent,
)

from .incorporate import (
    IncorporateAgent,
    IncorporateInput,
    IncorporateResult,
    RollbackAgent,
    RollbackInput,
    RollbackResult,
    incorporate_agent,
    rollback_agent,
)

from .judge import (
    CodeJudge,
    GenericCodeJudge,
    JudgeInput,
    JudgeResult,
    PrincipleScore,
    judge_code_improvement,
    code_judge,
    generic_judge,
)

from .evolution import (
    EvolutionAgent,
    EvolutionConfig,
    EvolutionInput,
    EvolutionPipeline,
    EvolutionReport,
    evolution_agent,
    evolution_pipeline,
)

from .safety import (
    SafetyConfig,
    ConvergenceState,
    SandboxTestInput,
    SandboxTestResult,
    SafeEvolutionInput,
    SafeEvolutionResult,
    SandboxTestAgent,
    ConvergenceAgent,
    SelfEvolutionAgent,
    compute_code_similarity,
    compute_structural_similarity,
    safety_config,
    self_evolution_agent,
    sandbox_test_agent,
    convergence_agent,
)

from .safe_evolution_orchestrator import (
    SafeEvolutionOrchestrator,
    SafeEvolutionOrchestratorInput,
    SafeEvolutionOrchestratorResult,
    safe_evolution_orchestrator,
)

from .preflight import (
    PreFlightChecker,
    PreFlightInput,
    PreFlightReport,
    preflight_checker,
)

from .prompts import (
    PromptContext,
    build_prompt_context,
    build_improvement_prompt,
    build_simple_prompt,
)

from .parser import (
    CodeParser,
    ParseResult,
    ParseStrategy,
    ParserConfig,
    code_parser,
)

from .validator import (
    SchemaValidator,
    ValidationReport,
    Issue,
    IssueSeverity,
    IssueCategory,
    schema_validator,
)

from .repair import (
    CodeRepairer,
    RepairResult,
    Repair,
    code_repairer,
)

from .retry import (
    RetryStrategy,
    RetryConfig,
    RetryAttempt,
    RetryResult,
    retry_strategy,
)

from .fallback import (
    FallbackStrategy,
    FallbackConfig,
    FallbackLevel,
    FallbackResult,
    fallback_strategy,
)

from .error_memory import (
    ErrorMemory,
    ErrorPattern,
    ErrorWarning,
    ErrorMemoryStats,
    error_memory,
)

from .status import (
    GitStatus,
    EvolutionLogData,
    HydrateStatus,
    StatusData,
    GitStatusAgent,
    EvolutionLogAgent,
    HydrateStatusAgent,
    StatusPresenterAgent,
    create_status_reporter,
)

__all__ = [
    # AST Analysis
    "ASTAnalyzer",
    "ASTAnalysisInput",
    "ASTAnalysisOutput",
    "CodeStructure",
    "analyze_module_ast",
    "generate_targeted_hypotheses",
    "ast_analyzer",
    # Memory
    "ImprovementMemory",
    "ImprovementRecord",
    "MemoryAgent",
    "MemoryQuery",
    "MemoryQueryResult",
    "RecordAgent",
    "RecordInput",
    "memory_agent",
    # Experiment
    "CodeModule",
    "CodeImprovement",
    "Experiment",
    "ExperimentStatus",
    "ExperimentInput",
    "ExperimentResult",
    "TestAgent",
    "TestInput",
    "TestResult",
    "extract_code",
    "extract_metadata",
    "get_code_preview",
    "test_agent",
    # Incorporate
    "IncorporateAgent",
    "IncorporateInput",
    "IncorporateResult",
    "RollbackAgent",
    "RollbackInput",
    "RollbackResult",
    "incorporate_agent",
    "rollback_agent",
    # Judge
    "CodeJudge",
    "GenericCodeJudge",
    "JudgeInput",
    "JudgeResult",
    "PrincipleScore",
    "judge_code_improvement",
    "code_judge",
    "generic_judge",
    # Evolution
    "EvolutionAgent",
    "EvolutionConfig",
    "EvolutionInput",
    "EvolutionPipeline",
    "EvolutionReport",
    "evolution_agent",
    "evolution_pipeline",
    # Safety
    "SafetyConfig",
    "ConvergenceState",
    "SandboxTestInput",
    "SandboxTestResult",
    "SafeEvolutionInput",
    "SafeEvolutionResult",
    "SandboxTestAgent",
    "ConvergenceAgent",
    "SelfEvolutionAgent",
    "compute_code_similarity",
    "compute_structural_similarity",
    "safety_config",
    "self_evolution_agent",
    "sandbox_test_agent",
    "convergence_agent",
    # Safe Evolution Orchestrator
    "SafeEvolutionOrchestrator",
    "SafeEvolutionOrchestratorInput",
    "SafeEvolutionOrchestratorResult",
    "safe_evolution_orchestrator",
    # PreFlight (Layer 1 Reliability)
    "PreFlightChecker",
    "PreFlightInput",
    "PreFlightReport",
    "preflight_checker",
    # Prompts (Layer 1 Reliability)
    "PromptContext",
    "build_prompt_context",
    "build_improvement_prompt",
    "build_simple_prompt",
    # Parser (Layer 2 Reliability)
    "CodeParser",
    "ParseResult",
    "ParseStrategy",
    "ParserConfig",
    "code_parser",
    # Validator (Layer 2 Reliability)
    "SchemaValidator",
    "ValidationReport",
    "Issue",
    "IssueSeverity",
    "IssueCategory",
    "schema_validator",
    # Repair (Layer 2 Reliability)
    "CodeRepairer",
    "RepairResult",
    "Repair",
    "code_repairer",
    # Retry (Layer 3 Reliability)
    "RetryStrategy",
    "RetryConfig",
    "RetryAttempt",
    "RetryResult",
    "retry_strategy",
    # Fallback (Layer 3 Reliability)
    "FallbackStrategy",
    "FallbackConfig",
    "FallbackLevel",
    "FallbackResult",
    "fallback_strategy",
    # Error Memory (Layer 3 Reliability)
    "ErrorMemory",
    "ErrorPattern",
    "ErrorWarning",
    "ErrorMemoryStats",
    "error_memory",
    # Status Agents (Phase 2.5e)
    "GitStatus",
    "EvolutionLogData",
    "HydrateStatus",
    "StatusData",
    "GitStatusAgent",
    "EvolutionLogAgent",
    "HydrateStatusAgent",
    "StatusPresenterAgent",
    "create_status_reporter",
]
