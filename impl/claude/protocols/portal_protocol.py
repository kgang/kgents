"""
Portal Token Protocol: Shared Contract for Portal Implementations.

This protocol defines the structural interface that any portal token
implementation must satisfy, enabling interoperability between the
Outline model (context/outline.py) and File Operad infrastructure
(file_operad/portal.py) without tight coupling.

Spec: plans/portal-fullstack-integration.md §6 (Phase 4)

Design Decision:
    Protocol (structural typing) > ABC (nominal typing)
    - Duck typing enables both implementations to satisfy the protocol
      without inheritance coupling
    - Each impl keeps its own fields/methods; only the shared interface matters
    - Bridge pattern translates between representations

Teaching:
    gotcha: typing.Protocol uses structural subtyping. A class satisfies
            the protocol if it has the right attributes/methods, even without
            explicit inheritance. Don't use isinstance() for runtime checks.
            (Evidence: test_portal_protocol.py::test_structural_typing)

    gotcha: Protocol properties must be implemented as properties (not just
            attributes) for full protocol compliance. Use @property decorator.
            (Evidence: test_portal_protocol.py::test_property_protocol)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    pass


# =============================================================================
# Core Protocol
# =============================================================================


@runtime_checkable
class PortalTokenProtocol(Protocol):
    """
    Contract that all portal token implementations must satisfy.

    This is the MINIMAL interface for interoperability:
    - edge_type: Semantic classification of the hyperedge
    - path: Where the portal leads (AGENTESE path or file path)
    - is_expanded: Current expansion state
    - depth: Nesting level in the expansion tree
    - to_dict(): JSON-serializable representation

    Both implementations (outline.PortalToken and file_operad.PortalToken)
    must provide these, enabling the bridge to translate between them.

    Implementation Note:
        This protocol uses @runtime_checkable so isinstance() works,
        but prefer duck typing or explicit type annotations over runtime checks.
    """

    @property
    def edge_type(self) -> str:
        """
        The hyperedge type this portal represents.

        Examples: "tests", "imports", "enables", "feeds", "triggered_by"

        The edge type determines the semantic relationship between
        the source and destination of the portal.
        """
        ...

    @property
    def path(self) -> str:
        """
        The destination path (AGENTESE path or filesystem path).

        For outline tokens: First destination in the destinations list
        For file_operad tokens: The link.path value

        This is the primary target when the portal is expanded.
        """
        ...

    @property
    def is_expanded(self) -> bool:
        """
        Whether the portal is currently expanded (showing content).

        Collapsed: Shows summary (e.g., "▶ [tests] ──→ 3 files")
        Expanded: Shows inline content with nested structure
        """
        ...

    @property
    def depth(self) -> int:
        """
        Nesting depth in the expansion tree.

        depth=0: Root level portal
        depth=1: First expansion
        depth=2+: Nested expansions (may trigger witness marks)

        Used for:
        - Rendering indentation
        - Expansion limits
        - Witness mark threshold (depth 2+ = significant)
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """
        JSON-serializable representation.

        Must include at minimum:
        - edge_type: str
        - path: str
        - is_expanded: bool
        - depth: int

        May include implementation-specific fields.
        """
        ...


@runtime_checkable
class ExpandableTokenProtocol(PortalTokenProtocol, Protocol):
    """
    Extended protocol for tokens that can be expanded asynchronously.

    This extends the base protocol with expand/collapse operations.
    The file_operad PortalToken implements this (with sync load()).
    The outline PortalToken does NOT—expansion is handled by OutlineOperations.

    Note: expand() is sync here because file_operad.PortalToken.load() is sync.
          For async operations, use the bridge methods.
    """

    def load(self) -> bool:
        """
        Load the destination content synchronously.

        Returns True if loading succeeded, False otherwise.
        Sets internal state based on success/failure.

        Note: This is sync because it reads from filesystem.
              For async expansion with witness marks, use the bridge.
        """
        ...

    def collapse(self) -> None:
        """
        Collapse this portal, hiding content.

        Content may be cached for quick re-expansion.
        """
        ...


# =============================================================================
# Conversion Protocol
# =============================================================================


class PortalBridgeProtocol(Protocol):
    """
    Protocol for bidirectional portal token conversion.

    Implementations translate between different PortalToken representations
    while preserving the essential information.
    """

    def outline_to_file(self, outline_token: Any) -> Any:
        """
        Convert outline PortalToken to file_operad PortalToken.

        Args:
            outline_token: protocols.context.outline.PortalToken

        Returns:
            protocols.file_operad.portal.PortalToken
        """
        ...

    def file_to_outline(self, file_token: Any) -> Any:
        """
        Convert file_operad PortalToken to outline PortalToken.

        Args:
            file_token: protocols.file_operad.portal.PortalToken

        Returns:
            protocols.context.outline.PortalToken
        """
        ...


# =============================================================================
# Type Aliases (for documentation and type hints)
# =============================================================================


# These are not enforced at runtime, but help with documentation
PortalPath = str  # e.g., "tests/auth" or "WITNESS_OPERAD/walk"
EdgeTypeName = str  # e.g., "tests", "imports", "enables"
PortalDepth = int  # Non-negative integer


# =============================================================================
# Helper Functions
# =============================================================================


def satisfies_protocol(obj: Any) -> bool:
    """
    Check if an object satisfies the PortalTokenProtocol.

    Uses runtime_checkable protocol, but prefer static typing where possible.

    Args:
        obj: Any object to check

    Returns:
        True if obj has the required attributes and methods

    Example:
        from protocols.context.outline import PortalToken as OutlineToken
        from protocols.file_operad.portal import PortalToken as FileToken

        outline_token = OutlineToken(...)
        file_token = FileToken(...)

        assert satisfies_protocol(outline_token)
        assert satisfies_protocol(file_token)
    """
    return isinstance(obj, PortalTokenProtocol)


def get_canonical_dict(token: PortalTokenProtocol) -> dict[str, Any]:
    """
    Extract the canonical representation from any portal token.

    This normalizes the output regardless of which implementation
    the token comes from.

    Args:
        token: Any object satisfying PortalTokenProtocol

    Returns:
        Dict with: edge_type, path, is_expanded, depth
    """
    return {
        "edge_type": token.edge_type,
        "path": token.path,
        "is_expanded": token.is_expanded,
        "depth": token.depth,
    }


__all__ = [
    # Protocols
    "PortalTokenProtocol",
    "ExpandableTokenProtocol",
    "PortalBridgeProtocol",
    # Type aliases
    "PortalPath",
    "EdgeTypeName",
    "PortalDepth",
    # Helper functions
    "satisfies_protocol",
    "get_canonical_dict",
]
