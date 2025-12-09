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
]
