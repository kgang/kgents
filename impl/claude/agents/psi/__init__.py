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

from .types import (
    # Core types
    Problem,
    Metaphor,
    Operation,
    Example,
    ConceptMapping,
    Projection,
    ChallengeResult,
    MetaphorSolution,
    Solution,
    Distortion,
    # Search state
    SearchState,
    EngineConfig,
    # Learning types
    ProblemFeatures,
    Feedback,
    Outcome,
)

from .corpus import (
    MetaphorCorpus,
    STANDARD_CORPUS,
    create_standard_corpus,
)

from .engine import (
    MetaphorEngine,
)

from .learning import (
    RetrievalModel,
    ThompsonSamplingModel,
    FrequencyModel,
    AbstractionModel,
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
