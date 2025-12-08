"""
E-gents: Evolution Agents for Code Improvement

This module provides composable agents for evolutionary code improvement:

- ASTAnalyzer: Static analysis of Python modules
- MemoryAgent: Persistent memory of past improvements
- TestAgent: Validate experiments (syntax, types, tests)
- CodeJudge: Evaluate against 7 kgents principles
- IncorporateAgent: Apply changes with git safety
- PreFlightChecker: Module health validation (Layer 1 reliability)
- PromptContext: Rich context for high-quality code generation (Layer 1 reliability)
- EvolutionAgent: Composed pipeline

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
]
