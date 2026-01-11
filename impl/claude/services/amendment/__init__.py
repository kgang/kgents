"""
Amendment Service: Constitutional Evolution via Formal Amendments.

The amendment service enables kgents to evolve its own constitution through
a formal, witnessed amendment process. This is Week 11-12 of the Self-Reflective OS.

Philosophy:
    "The constitution is not frozen. It evolves through witnessed amendments."

The amendment workflow follows a strict lifecycle:
    DRAFT -> PROPOSED -> UNDER_REVIEW -> APPROVED/REJECTED -> APPLIED/REVERTED

All transitions are witnessed, creating an auditable trail of constitutional evolution.

Example usage:
    >>> from services.amendment import AmendmentWorkflowService, AmendmentType
    >>>
    >>> svc = AmendmentWorkflowService()
    >>> amendment = await svc.create_draft(
    ...     title="Refine TASTEFUL principle",
    ...     description="Add explicit anti-pattern examples",
    ...     amendment_type=AmendmentType.PRINCIPLE_MODIFICATION,
    ...     target_kblock="principles/tasteful.md",
    ...     target_layer=2,
    ...     proposed_content="...",
    ...     proposer="kent",
    ...     reasoning="Anti-patterns help prevent common mistakes",
    ...     principles_affected=["TASTEFUL"],
    ... )
    >>> await svc.propose(amendment.id)
    >>> await svc.approve(amendment.id, "Clear improvement")
    >>> await svc.apply(amendment.id)

See: spec/protocols/zero-seed1/galois.md (constitutional evaluation)
See: plans/self-reflective-os/ (Week 11-12: Amendment System)
"""

from .model import (
    Amendment,
    AmendmentStatus,
    AmendmentType,
)
from .node import AmendmentNode
from .workflow import AmendmentWorkflowService

__all__ = [
    # Model
    "Amendment",
    "AmendmentStatus",
    "AmendmentType",
    # Service
    "AmendmentWorkflowService",
    # AGENTESE Node
    "AmendmentNode",
]
