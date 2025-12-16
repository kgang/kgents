"""
self.grow - Autopoietic Holon Generator

AGENTESE grows its own ontology through a governed process:

1. RECOGNIZE: Detect gaps via error pattern analysis
2. PROPOSE: Generate spec proposals from gaps
3. VALIDATE: Pass seven gates + law checks
4. GERMINATE: JIT compile into nursery
5. PROMOTE: Staged approval → production
6. PRUNE: Compost failed holons with learnings
7. ROLLBACK: Revert promotions within window

Paths:
- self.grow.recognize - Gap recognition
- self.grow.propose - Proposal generation
- self.grow.validate - Multi-gate validation
- self.grow.germinate - Nursery germination
- self.grow.nursery - Germinating holon management
- self.grow.promote - Staged promotion
- self.grow.rollback - Rollback management
- self.grow.prune - Composting with learnings
- self.grow.budget - Entropy budget management

Operad Laws:
- BUDGET_INVARIANT: Operations cost entropy
- VALIDATION_GATE: germinate requires passed validation
- APPROVAL_GATE: promote requires approval/gardener
- ROLLBACK_WINDOW: rollback only within expiry
- COMPOSABILITY: recognize >> propose >> validate

Affordances by Archetype:
- gardener: Full growth capabilities
- architect: Recognize, propose, validate, witness
- admin: Promote, rollback, prune, witness
- scholar: Witness, read-only access
- default: Read-only witness

AGENTESE: self.grow.*
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ...node import BaseLogosNode

# Import nodes
from .budget import BudgetNode, create_budget_node

# Import cortex (persistence layer)
from .cortex import GrowthCortex, create_growth_cortex
from .germinate import GerminateNode, create_germinate_node
from .nursery import NurseryNode, create_nursery_node
from .operad import GROWTH_OPERAD, GrowthOperad
from .promote import PromoteNode, create_promote_node
from .propose import ProposeNode, create_propose_node
from .prune import PruneNode, create_prune_node
from .recognize import RecognizeNode, create_recognize_node
from .rollback import RollbackNode, create_rollback_node

# Import schemas
from .schemas import (
    SELF_GROW_AFFORDANCES,
    GapRecognition,
    GerminatingHolon,
    GrowthBudget,
    GrowthBudgetConfig,
    GrowthRelevantError,
    HolonProposal,
    NurseryConfig,
    PromotionResult,
    PromotionStage,
    RecognitionQuery,
    RollbackResult,
    RollbackToken,
    ValidationResult,
)
from .validate import ValidateNode, create_validate_node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    from ...logos import Logos


# === Self Grow Context Resolver ===


@dataclass
class SelfGrowResolver:
    """
    Resolver for self.grow.* context.

    Provides access to the autopoietic holon generator:
    - self.grow.recognize - Gap recognition
    - self.grow.propose - Proposal generation
    - self.grow.validate - Multi-gate validation
    - self.grow.germinate - Nursery germination
    - self.grow.nursery - Germinating holon management
    - self.grow.promote - Staged promotion
    - self.grow.rollback - Rollback management
    - self.grow.prune - Composting with learnings
    - self.grow.budget - Entropy budget management
    """

    # Integration points
    _logos: "Logos | None" = None
    _base_path: Path | None = None

    # Shared state
    _budget: GrowthBudget | None = None
    _nursery: NurseryNode | None = None

    # Singleton nodes
    _recognize: RecognizeNode | None = None
    _propose: ProposeNode | None = None
    _validate: ValidateNode | None = None
    _germinate: GerminateNode | None = None
    _promote: PromoteNode | None = None
    _rollback: RollbackNode | None = None
    _prune: PruneNode | None = None
    _budget_node: BudgetNode | None = None

    def __post_init__(self) -> None:
        """Initialize shared state and nodes."""
        # Create shared budget if not provided
        if self._budget is None:
            self._budget = GrowthBudget()

        # Create shared nursery if not provided
        if self._nursery is None:
            self._nursery = create_nursery_node(budget=self._budget)

        # Create all nodes with shared state
        self._recognize = create_recognize_node(
            logos=self._logos,
            budget=self._budget,
        )
        self._propose = create_propose_node(budget=self._budget)
        self._validate = create_validate_node(
            logos=self._logos,
            budget=self._budget,
        )
        self._germinate = create_germinate_node(
            logos=self._logos,
            budget=self._budget,
            nursery=self._nursery,
        )
        self._promote = create_promote_node(
            budget=self._budget,
            nursery=self._nursery,
            base_path=self._base_path,
        )
        self._rollback = create_rollback_node(
            rollback_tokens=self._promote._rollback_tokens,
        )
        self._prune = create_prune_node(
            budget=self._budget,
            nursery=self._nursery,
        )
        self._budget_node = create_budget_node()
        self._budget_node._budget = self._budget

    def resolve(self, holon: str, rest: list[str]) -> BaseLogosNode:
        """
        Resolve a self.grow.* path to a node.

        Args:
            holon: The grow subsystem (recognize, propose, validate, etc.)
            rest: Additional path components

        Returns:
            Resolved node
        """
        match holon:
            case "recognize":
                return self._recognize or create_recognize_node()
            case "propose":
                return self._propose or create_propose_node()
            case "validate":
                return self._validate or create_validate_node()
            case "germinate":
                return self._germinate or create_germinate_node()
            case "nursery":
                return self._nursery or create_nursery_node()
            case "promote":
                return self._promote or create_promote_node()
            case "rollback":
                return self._rollback or create_rollback_node()
            case "prune":
                return self._prune or create_prune_node()
            case "budget":
                return self._budget_node or create_budget_node()
            case _:
                # Return recognize as default (gap discovery)
                return self._recognize or create_recognize_node()


# === Factory ===


def create_self_grow_resolver(
    logos: "Logos | None" = None,
    base_path: Path | None = None,
    budget: GrowthBudget | None = None,
    nursery: NurseryNode | None = None,
) -> SelfGrowResolver:
    """
    Create a SelfGrowResolver with optional configuration.

    Args:
        logos: Logos instance for composition/registry checks
        base_path: Base path for spec/impl files
        budget: Shared growth budget
        nursery: Shared nursery node

    Returns:
        Configured SelfGrowResolver
    """
    resolver = SelfGrowResolver(
        _logos=logos,
        _base_path=base_path,
        _budget=budget,
        _nursery=nursery,
    )
    resolver.__post_init__()
    return resolver


# === Exports ===


__all__ = [
    # Resolver
    "SelfGrowResolver",
    "create_self_grow_resolver",
    # Cortex (persistence layer)
    "GrowthCortex",
    "create_growth_cortex",
    # Nodes
    "RecognizeNode",
    "ProposeNode",
    "ValidateNode",
    "GerminateNode",
    "NurseryNode",
    "PromoteNode",
    "RollbackNode",
    "PruneNode",
    "BudgetNode",
    # Node factories
    "create_recognize_node",
    "create_propose_node",
    "create_validate_node",
    "create_germinate_node",
    "create_nursery_node",
    "create_promote_node",
    "create_rollback_node",
    "create_prune_node",
    "create_budget_node",
    # Schemas
    "SELF_GROW_AFFORDANCES",
    "GrowthRelevantError",
    "RecognitionQuery",
    "GapRecognition",
    "HolonProposal",
    "ValidationResult",
    "GerminatingHolon",
    "NurseryConfig",
    "PromotionStage",
    "PromotionResult",
    "RollbackToken",
    "RollbackResult",
    "GrowthBudget",
    "GrowthBudgetConfig",
    # Operad
    "GROWTH_OPERAD",
    "GrowthOperad",
]
