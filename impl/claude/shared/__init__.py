"""
kgents Shared Module

Shared utilities for the kgents implementation:
- capital: Event-sourced ledger for agent capital (void.capital.*)
- costs: Algebraic cost function composition
- budget: Resource budget context managers
- melting: Contract-bounded hallucination (void.pataphysics.*)
"""

from __future__ import annotations

from .budget import (
    ResourceBudget,
    issue_budget,
)
from .capital import (
    BypassToken,
    EventSourcedLedger,
    EventType,
    InsufficientCapitalError,
    LedgerEvent,
)
from .costs import (
    BASE_COST,
    BYPASS_COST,
    JUDGMENT_DEFICIT,
    RESOURCE_PENALTY,
    RISK_PREMIUM,
    CostContext,
    CostFactor,
)
from .melting import (
    ContractViolationError,
    MeltingContext,
    default_pataphysics_solver,
    get_postcondition,
    is_meltable,
    meltable,
    meltable_sync,
)

__all__ = [
    # capital.py
    "BypassToken",
    "EventSourcedLedger",
    "EventType",
    "InsufficientCapitalError",
    "LedgerEvent",
    # costs.py
    "BASE_COST",
    "BYPASS_COST",
    "CostContext",
    "CostFactor",
    "JUDGMENT_DEFICIT",
    "RESOURCE_PENALTY",
    "RISK_PREMIUM",
    # budget.py
    "ResourceBudget",
    "issue_budget",
    # melting.py
    "ContractViolationError",
    "MeltingContext",
    "default_pataphysics_solver",
    "get_postcondition",
    "is_meltable",
    "meltable",
    "meltable_sync",
]
