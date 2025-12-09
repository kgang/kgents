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

from .types import (
    # Core types
    Signature,
    FieldSpec,
    Example,
    # Optimization
    TextualGradient,
    OptimizationIteration,
    OptimizationTrace,
    OptimizedAgentMeta,
    # Strategy
    TeleprompterStrategy,
    Teleprompter,
    # Economics (B-gent integration)
    OptimizationBudget,
    ROIEstimate,
    OptimizationDecision,
)

from .refinery import (
    # Teleprompters
    BaseTeleprompter,
    BootstrapFewShotTeleprompter,
    TextGradTeleprompter,
    MIPROv2Teleprompter,
    OPROTeleprompter,
    TeleprompterFactory,
    # ROI
    ROIOptimizer,
    # Main interface
    RefineryAgent,
)

from .dspy_backend import (
    # DSPy availability
    is_dspy_available,
    # DSPy-backed teleprompters (Phase 2)
    DSPyBootstrapFewShot,
    DSPyMIPROv2,
    # LLM-backed teleprompters (Phase 2)
    LLMTextGrad,
    LLMOpro,
    # Factory
    get_dspy_teleprompter,
    # LLM function creators
    create_openai_llm_func,
    create_anthropic_llm_func,
    # DSPy utilities
    DSPyLLMConfig,
    DSPyModuleWrapper,
    signature_to_dspy,
    example_to_dspy,
    examples_to_dspy,
)

# Phase 3: Cross-Genus Integrations
from .integrations import (
    # F-gent integration
    RefinePhase,
    PrototypeRefinementRequest,
    PrototypeRefinementResult,
    FGentRefineryBridge,
    # T-gent integration
    MetricSignal,
    TextualLossSignal,
    TGentLossAdapter,
    # B-gent integration
    BudgetDenied,
    BudgetGrant,
    BudgetSpendReport,
    BGentBudgetProtocol,
    BudgetConstrainedRefinery,
    # L-gent integration
    OptimizationCatalogEntry,
    LGentOptimizationIndex,
    # Unified hub
    RGentIntegrationConfig,
    RGentIntegrationHub,
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
]
