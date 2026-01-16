"""
Heterarchical Edge Policy: Validation rules for cross-layer edges.

"Cross-layer edges are allowed by default. Justification is encouraged, not required."

The policy implements three levels of edge validation:
- STRICT: Justification REQUIRED (blocks without it)
- SUGGESTED: Justification ENCOURAGED (flags if missing)
- OPTIONAL: Justification not flagged

Design Philosophy:
    Heterarchy over Hierarchy - The system tolerates porosity.
    Users may create cross-layer edges. The system adapts.

From plans/zero-seed-genesis-grand-strategy.md:
    "Cross-layer edges allowed. Incoherence tolerated.
     System adapts to user, not user to system."
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from services.zero_seed import EdgeKind, ZeroEdge


class EdgePolicyLevel(Enum):
    """
    Policy level for edge validation.

    STRICT: Must have justification (CONTRADICTS, SUPERSEDES)
    SUGGESTED: Should have justification, flagged if missing (GROUNDS, JUSTIFIES)
    OPTIONAL: May have justification, not flagged (IMPLEMENTS, EXTENDS, DERIVES_FROM)
    """

    STRICT = "strict"  # Blocks without justification
    SUGGESTED = "suggested"  # Flags without justification
    OPTIONAL = "optional"  # No enforcement


@dataclass(frozen=True)
class EdgeValidation:
    """
    Result of edge validation.

    Fields:
        valid: Whether the edge is valid (only False for STRICT violations)
        flagged: Whether to flag for user review (True for suggestions)
        level: Policy level applied
        reason: Human-readable reason for decision
        suggestion: Optional suggestion for improvement
        galois_loss: Galois loss of the edge transition (if computed)
    """

    valid: bool
    flagged: bool
    level: EdgePolicyLevel
    reason: str
    suggestion: str | None = None
    galois_loss: float | None = None


class HeterarchicalEdgePolicy:
    """
    Edge validation policy implementing heterarchical tolerance.

    Philosophy:
        Strict where necessary (contradictions, supersessions).
        Lenient everywhere else. Cross-layer edges allowed.

    Edge Policy Rules (from Grand Strategy):

    STRICT_EDGES (MUST have justification):
    - EdgeKind.CONTRADICTS
    - EdgeKind.SUPERSEDES

    SUGGESTED_EDGES (SHOULD have justification, flagged if missing):
    - EdgeKind.GROUNDS (L1 → L2)
    - EdgeKind.JUSTIFIES (L2 → L3)

    OPTIONAL_EDGES (MAY have justification, not flagged):
    - EdgeKind.IMPLEMENTS
    - EdgeKind.EXTENDS
    - EdgeKind.DERIVES_FROM

    Cross-Layer Edges:
    - Allowed by default
    - Flagged for review (not blocked)
    - Suggestion to add justification for clarity
    """

    # Edges that MUST have justification
    STRICT_EDGES = frozenset(
        {
            EdgeKind.CONTRADICTS,
            EdgeKind.SUPERSEDES,
        }
    )

    # Edges that SHOULD have justification (flagged if missing)
    SUGGESTED_EDGES = frozenset(
        {
            EdgeKind.GROUNDS,  # L1 → L2
            EdgeKind.JUSTIFIES,  # L2 → L3
        }
    )

    # Edges where justification is optional (not flagged)
    OPTIONAL_EDGES = frozenset(
        {
            EdgeKind.IMPLEMENTS,
            EdgeKind.EXTENDS,
            EdgeKind.DERIVES_FROM,
            EdgeKind.REFINES,
            EdgeKind.SPECIFIES,
            EdgeKind.REFLECTS_ON,
            EdgeKind.REPRESENTS,
            EdgeKind.CRYSTALLIZES,
            EdgeKind.SOURCES,
            EdgeKind.SYNTHESIZES,
            # Inverse edges
            EdgeKind.GROUNDED_BY,
            EdgeKind.JUSTIFIED_BY,
            EdgeKind.SPECIFIED_BY,
            EdgeKind.IMPLEMENTED_BY,
            EdgeKind.REFLECTED_BY,
            EdgeKind.REPRESENTED_BY,
        }
    )

    def validate(self, edge: ZeroEdge, source_layer: int, target_layer: int) -> EdgeValidation:
        """
        Validate an edge according to heterarchical policy.

        Args:
            edge: The edge to validate
            source_layer: Layer of source node (1-7)
            target_layer: Layer of target node (1-7)

        Returns:
            EdgeValidation with decision and suggestions

        Examples:
            >>> policy = HeterarchicalEdgePolicy()
            >>> # STRICT edge without justification
            >>> edge = ZeroEdge(kind=EdgeKind.CONTRADICTS, context="")
            >>> validation = policy.validate(edge, 1, 2)
            >>> assert not validation.valid
            >>> # Cross-layer edge
            >>> edge = ZeroEdge(kind=EdgeKind.IMPLEMENTS, context="")
            >>> validation = policy.validate(edge, 3, 5)
            >>> assert validation.valid and validation.flagged
        """
        # Determine policy level for this edge kind
        if edge.kind in self.STRICT_EDGES:
            level = EdgePolicyLevel.STRICT
        elif edge.kind in self.SUGGESTED_EDGES:
            level = EdgePolicyLevel.SUGGESTED
        else:
            level = EdgePolicyLevel.OPTIONAL

        # Check if justification is present
        has_justification = bool(edge.context and edge.context.strip())

        # STRICT: Block if missing justification
        if level == EdgePolicyLevel.STRICT and not has_justification:
            return EdgeValidation(
                valid=False,
                flagged=True,
                level=level,
                reason=f"{edge.kind.value} edges require justification",
                suggestion=(
                    f"This is a {edge.kind.value} edge, which represents a critical "
                    "semantic relationship. Please provide justification in the context field."
                ),
            )

        # Check for cross-layer edges (skip >1 layer)
        is_cross_layer = abs(source_layer - target_layer) > 1

        # Cross-layer edges: allowed but flagged for review
        if is_cross_layer:
            suggestion_text = (
                f"This edge connects L{source_layer} to L{target_layer}, "
                f"skipping {abs(source_layer - target_layer) - 1} layer(s). "
            )

            if not has_justification:
                suggestion_text += (
                    "Consider adding justification to explain why this cross-layer "
                    "connection is meaningful."
                )

            return EdgeValidation(
                valid=True,  # Allowed
                flagged=True,  # But surfaced
                level=level,
                reason="Cross-layer edge detected",
                suggestion=suggestion_text,
                galois_loss=None,  # Will be computed by caller if needed
            )

        # SUGGESTED: Flag if missing justification
        if level == EdgePolicyLevel.SUGGESTED and not has_justification:
            return EdgeValidation(
                valid=True,  # Allowed
                flagged=True,  # But flagged
                level=level,
                reason=f"{edge.kind.value} edges should have justification",
                suggestion=(
                    f"This {edge.kind.value} edge would be clearer with justification. "
                    "Consider adding context to explain the relationship."
                ),
            )

        # OPTIONAL or has justification: Accept without flags
        return EdgeValidation(
            valid=True,
            flagged=False,
            level=level,
            reason="Edge validated",
            suggestion=None,
        )


def validate_edge(edge: ZeroEdge, source_layer: int, target_layer: int) -> EdgeValidation:
    """
    Convenience function for edge validation.

    Args:
        edge: The edge to validate
        source_layer: Layer of source node
        target_layer: Layer of target node

    Returns:
        EdgeValidation result

    Example:
        >>> from services.zero_seed import ZeroEdge, EdgeKind
        >>> edge = ZeroEdge(kind=EdgeKind.GROUNDS, context="Values grounded in axiom")
        >>> validation = validate_edge(edge, 1, 2)
        >>> assert validation.valid
    """
    policy = HeterarchicalEdgePolicy()
    return policy.validate(edge, source_layer, target_layer)
