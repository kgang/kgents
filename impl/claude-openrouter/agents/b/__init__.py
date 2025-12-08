"""
B-gents: Scientific Discovery Agents

Agents for scientific reasoning, hypothesis generation, and empirical inquiry.

Core themes:
- Falsifiability (Popperian epistemology)
- Epistemic humility
- Transparent reasoning
- Composition with other agent genera

Currently implemented:
- HypothesisEngine: Transforms observations into testable hypotheses
- Robin: Personalized scientific companion (composes K-gent + Hypothesis + Hegel)
"""

from .hypothesis import (
    HypothesisEngine,
    HypothesisInput,
    HypothesisOutput,
    Hypothesis,
    NoveltyLevel,
    hypothesis_engine,
    rigorous_engine,
    exploratory_engine,
)

from .robin import (
    RobinAgent,
    RobinInput,
    RobinOutput,
    robin,
    robin_with_persona,
    quick_robin,
)

__all__ = [
    # HypothesisEngine
    "HypothesisEngine",
    "HypothesisInput",
    "HypothesisOutput",
    "Hypothesis",
    "NoveltyLevel",
    "hypothesis_engine",
    "rigorous_engine",
    "exploratory_engine",
    # Robin (scientific companion)
    "RobinAgent",
    "RobinInput",
    "RobinOutput",
    "robin",
    "robin_with_persona",
    "quick_robin",
]
