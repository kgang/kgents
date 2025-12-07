"""
C-gents: Category Theory Agents

Composability as a first principle. Agents as morphisms.

Core concepts:
- Functors: Structure-preserving transformations (Maybe, Either)
- Parallel: Concurrent execution patterns
- Conditional: Branching composition

Laws:
- Associativity: (f >> g) >> h = f >> (g >> h)
- Identity: Id >> f = f = f >> Id
- Functor: F(g . f) = F(g) . F(f)
"""

# Functor types and lifted agents
from .functor import (
    # Maybe
    Maybe,
    Just,
    Nothing,
    MaybeAgent,
    maybe,
    # Either
    Either,
    Right,
    Left,
    EitherAgent,
    either,
)

# Parallel composition
from .parallel import (
    ParallelAgent,
    FanOutAgent,
    CombineAgent,
    RaceAgent,
    parallel,
    fan_out,
    combine,
    race,
)

# Conditional composition
from .conditional import (
    BranchAgent,
    SwitchAgent,
    GuardedAgent,
    FilterAgent,
    branch,
    switch,
    guarded,
    filter_by,
)

__all__ = [
    # Maybe
    "Maybe",
    "Just",
    "Nothing",
    "MaybeAgent",
    "maybe",
    # Either
    "Either",
    "Right",
    "Left",
    "EitherAgent",
    "either",
    # Parallel
    "ParallelAgent",
    "FanOutAgent",
    "CombineAgent",
    "RaceAgent",
    "parallel",
    "fan_out",
    "combine",
    "race",
    # Conditional
    "BranchAgent",
    "SwitchAgent",
    "GuardedAgent",
    "FilterAgent",
    "branch",
    "switch",
    "guarded",
    "filter_by",
]
