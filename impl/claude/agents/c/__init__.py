"""
C-gents: Category Theory Agents

Composability as a first principle. Agents as morphisms.

Core concepts:
- Functors: Structure-preserving transformations (Maybe, Either, List, Async, Logged, Promise)
- Parallel: Concurrent execution patterns
- Conditional: Branching composition

Functor Laws:
- Identity: F(id_A) = id_F(A)
- Composition: F(g ∘ f) = F(g) ∘ F(f)

Category Laws:
- Associativity: (f >> g) >> h = f >> (g >> h)
- Identity: Id >> f = f = f >> Id

See Also:
- spec/agents/composition.md — Composition theory
- spec/agents/functors.md — Functor specification
- spec/agents/functor-catalog.md — Complete functor catalog
- spec/agents/monads.md — Monad patterns
"""

# Functor types and lifted agents
# Conditional composition
from .conditional import (
    BranchAgent,
    FilterAgent,
    GuardedAgent,
    SwitchAgent,
    branch,
    filter_by,
    guarded,
    switch,
)

# Contract validation (Cross-pollination T2.8)
from .contract_validator import (
    ContractLawViolation,
    ContractValidationReport,
    ContractValidator,
    suggest_contract_improvements,
    validate_composition_compatibility,
    validate_contract_laws,
)
from .functor import (
    # Async
    AsyncAgent,
    AsyncFunctor,
    # Either
    Either,
    EitherAgent,
    EitherFunctor,
    # Fix (retry)
    FixAgent,
    FixFunctor,
    Just,
    Left,
    # List
    ListAgent,
    ListFunctor,
    LogEntry,
    # Logged
    LoggedAgent,
    LoggedFunctor,
    # Maybe
    Maybe,
    MaybeAgent,
    MaybeFunctor,
    Nothing,
    Right,
    # Unlift error
    UnliftError,
    async_agent,
    check_composition_law,
    # Law validation
    check_identity_law,
    either,
    fix,
    list_agent,
    logged,
    maybe,
    # Unlift functions (Phase 1: Symmetric Lifting)
    unlift_async,
    unlift_either,
    unlift_fix,
    unlift_list,
    unlift_logged,
    unlift_maybe,
)

# Promise functor (J-gent integration)
from .j_integration import (
    PromiseAgent,
    promise_agent,
    resolve_promise,
)

# Monad composition
from .monad import (
    MaybeEither,
    Monad,
    fail_either,
    pure_either,
    pure_maybe,
)

# Parallel composition
from .parallel import (
    CombineAgent,
    FanOutAgent,
    ParallelAgent,
    RaceAgent,
    combine,
    fan_out,
    parallel,
    race,
)

__all__ = [
    # Maybe
    "Maybe",
    "Just",
    "Nothing",
    "MaybeAgent",
    "MaybeFunctor",
    "maybe",
    "unlift_maybe",
    # Either
    "Either",
    "Right",
    "Left",
    "EitherAgent",
    "EitherFunctor",
    "either",
    "unlift_either",
    # Fix (retry)
    "FixAgent",
    "FixFunctor",
    "fix",
    "unlift_fix",
    # List
    "ListAgent",
    "ListFunctor",
    "list_agent",
    "unlift_list",
    # Async
    "AsyncAgent",
    "AsyncFunctor",
    "async_agent",
    "unlift_async",
    # Logged
    "LoggedAgent",
    "LoggedFunctor",
    "LogEntry",
    "logged",
    "unlift_logged",
    # Promise
    "PromiseAgent",
    "promise_agent",
    "resolve_promise",
    # Law validation
    "check_identity_law",
    "check_composition_law",
    # Unlift error
    "UnliftError",
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
    # Monad
    "Monad",
    "MaybeEither",
    "pure_maybe",
    "pure_either",
    "fail_either",
    # Contract validation (Cross-pollination T2.8)
    "ContractValidator",
    "ContractValidationReport",
    "ContractLawViolation",
    "validate_contract_laws",
    "validate_composition_compatibility",
    "suggest_contract_improvements",
]
