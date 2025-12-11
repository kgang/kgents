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
    # Either
    Either,
    EitherAgent,
    # Fix (retry)
    FixAgent,
    Just,
    Left,
    # List
    ListAgent,
    LogEntry,
    # Logged
    LoggedAgent,
    # Maybe
    Maybe,
    MaybeAgent,
    Nothing,
    Right,
    async_agent,
    check_composition_law,
    # Law validation
    check_identity_law,
    either,
    fix,
    list_agent,
    logged,
    maybe,
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
    "maybe",
    # Either
    "Either",
    "Right",
    "Left",
    "EitherAgent",
    "either",
    # Fix (retry)
    "FixAgent",
    "fix",
    # List
    "ListAgent",
    "list_agent",
    # Async
    "AsyncAgent",
    "async_agent",
    # Logged
    "LoggedAgent",
    "LogEntry",
    "logged",
    # Promise
    "PromiseAgent",
    "promise_agent",
    "resolve_promise",
    # Law validation
    "check_identity_law",
    "check_composition_law",
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
