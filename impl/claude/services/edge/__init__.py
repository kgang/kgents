"""
Edge Service: Heterarchical Tolerance and Edge Validation.

"The system adapts to user, not user to system."

This module implements the heterarchical tolerance system for Zero Seed,
enabling cross-layer edges and nonsense quarantine with Linear-inspired
design philosophy.

Key Principles:
- Cross-layer edges allowed by default (heterarchy over hierarchy)
- Justification encouraged, not required (except for critical edges)
- Nonsense quarantined, not blocked (graceful degradation)
- Performance unaffected by incoherent input

Philosophy:
    Linear Adaptation - The product shapes to the user, not vice versa.
    Never punish. Never lecture. Never block. Metabolize or quarantine.

Core Components:
- HeterarchicalEdgePolicy: Validation rules for edges
- NonsenseQuarantine: Incoherence quarantine system
- Cross-layer loss computation (via galois)

See: spec/protocols/heterarchy.md
See: plans/zero-seed-genesis-grand-strategy.md (Part VII)
"""

from __future__ import annotations

from .policy import (
    EdgePolicyLevel,
    EdgeValidation,
    HeterarchicalEdgePolicy,
    validate_edge,
)
from .quarantine import (
    NonsenseQuarantine,
    QuarantineDecision,
    QuarantineEffects,
    evaluate_for_quarantine,
)

__all__ = [
    # Policy
    "HeterarchicalEdgePolicy",
    "EdgePolicyLevel",
    "EdgeValidation",
    "validate_edge",
    # Quarantine
    "NonsenseQuarantine",
    "QuarantineDecision",
    "QuarantineEffects",
    "evaluate_for_quarantine",
]
