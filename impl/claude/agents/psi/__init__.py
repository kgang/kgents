"""
Psi-gent: The Morphic Engine.

Reasoning by analogy as geometric transformation.
Find the metaphor that makes a hard problem easy.

Core Components:
- MetaphorEngine: Six-stage pipeline (RETRIEVE → PROJECT → CHALLENGE → SOLVE → TRANSLATE → VERIFY)
- MetaphorCorpus: Static + dynamic metaphor collection
- Learning: Thompson sampling for metaphor selection

Example:
    from agents.psi import MetaphorEngine, Problem

    problem = Problem(
        id="perf-001",
        description="The API is slow. Users are complaining.",
        domain="software",
        constraints=("Must improve within sprint",)
    )

    engine = MetaphorEngine()
    solution = engine.solve_problem(problem)

    if solution.distortion.acceptable:
        print(f"Solution: {solution.translated_answer}")
        for action in solution.specific_actions:
            print(f"  - {action}")
"""

from .corpus import (
    STANDARD_CORPUS,
    MetaphorCorpus,
    create_standard_corpus,
)
from .engine import (
    MetaphorEngine,
)
from .learning import (
    AbstractionModel,
    FrequencyModel,
    RetrievalModel,
    ThompsonSamplingModel,
)
from .types import (
    ChallengeResult,
    ConceptMapping,
    Distortion,
    EngineConfig,
    Example,
    Feedback,
    Metaphor,
    MetaphorSolution,
    Operation,
    Outcome,
    # Core types
    Problem,
    # Learning types
    ProblemFeatures,
    Projection,
    # Search state
    SearchState,
    Solution,
)

__all__ = [
    # Types
    "Problem",
    "Metaphor",
    "Operation",
    "Example",
    "ConceptMapping",
    "Projection",
    "ChallengeResult",
    "MetaphorSolution",
    "Solution",
    "Distortion",
    "SearchState",
    "EngineConfig",
    "ProblemFeatures",
    "Feedback",
    "Outcome",
    # Corpus
    "MetaphorCorpus",
    "STANDARD_CORPUS",
    "create_standard_corpus",
    # Engine
    "MetaphorEngine",
    # Learning
    "RetrievalModel",
    "ThompsonSamplingModel",
    "FrequencyModel",
    "AbstractionModel",
]
