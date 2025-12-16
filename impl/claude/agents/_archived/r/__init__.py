"""
R-gents: The Refinery.

Agents that transform "prompt engineering" from manual art into formal
optimization process. By treating prompts as "differentiable" weights,
R-gents automate the ascent toward competence.

Core Insight:
  If we can measure the error of an agent (via T-gents), and we can
  articulate *why* it failed (via Textual Gradients), we can
  mathematically compute a better agent.

The Endofunctor:
  R: Agent[A, B] -> Agent'[A, B]
  where Loss(Agent') < Loss(Agent)

See spec/r-gents/README.md for full specification.
"""

# Phase 4: Advanced Features
from .advanced import (
    AdvancedRefinery,
    # Part 5: Unified
    AdvancedRefineryConfig,
    AnthropicFinetunePreparer,
    AutoTeleprompterSelector,
    BootstrapFinetuneTeleprompter,
    CrossModelTransferAnalyzer,
    DatasetCharacteristics,
    DriftDetectionMethod,
    DriftReport,
    FinetuneConfig,
    FinetuneDataset,
    FinetuneJob,
    FinetunePreparer,
    # Part 4: Fine-tuning
    FinetuneStatus,
    ModelDriftDetector,
    # Part 3: Transfer analysis
    ModelProfile,
    OpenAIFinetunePreparer,
    # Part 2: Drift detection
    PerformanceSample,
    ReoptimizationTrigger,
    StrategyRecommendation,
    TaskAnalysis,
    TaskAnalyzer,
    # Part 1: Auto-selection
    TaskComplexity,
    TransferPrediction,
)
from .dspy_backend import (
    # DSPy-backed teleprompters (Phase 2)
    DSPyBootstrapFewShot,
    # DSPy utilities
    DSPyLLMConfig,
    DSPyMIPROv2,
    DSPyModuleWrapper,
    LLMOpro,
    # LLM-backed teleprompters (Phase 2)
    LLMTextGrad,
    create_anthropic_llm_func,
    # LLM function creators
    create_openai_llm_func,
    example_to_dspy,
    examples_to_dspy,
    # Factory
    get_dspy_teleprompter,
    # DSPy availability
    is_dspy_available,
    signature_to_dspy,
)

# Phase 3: Cross-Genus Integrations
from .integrations import (
    BGentBudgetProtocol,
    BudgetConstrainedRefinery,
    # B-gent integration
    BudgetDenied,
    BudgetGrant,
    BudgetSpendReport,
    FGentRefineryBridge,
    LGentOptimizationIndex,
    # T-gent integration
    MetricSignal,
    # L-gent integration
    OptimizationCatalogEntry,
    PrototypeRefinementRequest,
    PrototypeRefinementResult,
    # F-gent integration
    RefinePhase,
    # Unified hub
    RGentIntegrationConfig,
    RGentIntegrationHub,
    TextualLossSignal,
    TGentLossAdapter,
)
from .refinery import (
    # Teleprompters
    BaseTeleprompter,
    BootstrapFewShotTeleprompter,
    MIPROv2Teleprompter,
    OPROTeleprompter,
    # Main interface
    RefineryAgent,
    # ROI
    ROIOptimizer,
    TeleprompterFactory,
    TextGradTeleprompter,
)
from .types import (
    Example,
    FieldSpec,
    # Economics (B-gent integration)
    OptimizationBudget,
    OptimizationDecision,
    OptimizationIteration,
    OptimizationTrace,
    OptimizedAgentMeta,
    ROIEstimate,
    # Core types
    Signature,
    Teleprompter,
    # Strategy
    TeleprompterStrategy,
    # Optimization
    TextualGradient,
)

__all__ = [
    # Core types
    "Signature",
    "FieldSpec",
    "Example",
    # Optimization
    "TextualGradient",
    "OptimizationIteration",
    "OptimizationTrace",
    "OptimizedAgentMeta",
    # Strategy
    "TeleprompterStrategy",
    "Teleprompter",
    # Economics
    "OptimizationBudget",
    "ROIEstimate",
    "OptimizationDecision",
    # Teleprompters
    "BaseTeleprompter",
    "BootstrapFewShotTeleprompter",
    "TextGradTeleprompter",
    "MIPROv2Teleprompter",
    "OPROTeleprompter",
    "TeleprompterFactory",
    # ROI
    "ROIOptimizer",
    # Main interface
    "RefineryAgent",
    # DSPy availability
    "is_dspy_available",
    # DSPy-backed teleprompters (Phase 2)
    "DSPyBootstrapFewShot",
    "DSPyMIPROv2",
    # LLM-backed teleprompters (Phase 2)
    "LLMTextGrad",
    "LLMOpro",
    # Factory
    "get_dspy_teleprompter",
    # LLM function creators
    "create_openai_llm_func",
    "create_anthropic_llm_func",
    # DSPy utilities
    "DSPyLLMConfig",
    "DSPyModuleWrapper",
    "signature_to_dspy",
    "example_to_dspy",
    "examples_to_dspy",
    # Phase 3: F-gent integration
    "RefinePhase",
    "PrototypeRefinementRequest",
    "PrototypeRefinementResult",
    "FGentRefineryBridge",
    # Phase 3: T-gent integration
    "MetricSignal",
    "TextualLossSignal",
    "TGentLossAdapter",
    # Phase 3: B-gent integration
    "BudgetDenied",
    "BudgetGrant",
    "BudgetSpendReport",
    "BGentBudgetProtocol",
    "BudgetConstrainedRefinery",
    # Phase 3: L-gent integration
    "OptimizationCatalogEntry",
    "LGentOptimizationIndex",
    # Phase 3: Unified hub
    "RGentIntegrationConfig",
    "RGentIntegrationHub",
    # Phase 4: Auto-selection
    "TaskComplexity",
    "DatasetCharacteristics",
    "TaskAnalysis",
    "StrategyRecommendation",
    "TaskAnalyzer",
    "AutoTeleprompterSelector",
    # Phase 4: Drift detection
    "PerformanceSample",
    "DriftReport",
    "DriftDetectionMethod",
    "ModelDriftDetector",
    "ReoptimizationTrigger",
    # Phase 4: Transfer analysis
    "ModelProfile",
    "TransferPrediction",
    "CrossModelTransferAnalyzer",
    # Phase 4: Fine-tuning
    "FinetuneStatus",
    "FinetuneJob",
    "FinetuneConfig",
    "FinetuneDataset",
    "FinetunePreparer",
    "OpenAIFinetunePreparer",
    "AnthropicFinetunePreparer",
    "BootstrapFinetuneTeleprompter",
    # Phase 4: Unified
    "AdvancedRefineryConfig",
    "AdvancedRefinery",
]
