"""
WitnessBridge: Connects K-Block operations to Witness marks.

This module provides the actual implementation of the WitnessBridgeProtocol,
enabling K-Block.bind() operations to emit Witness marks automatically.

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Every K-Block derivation (bind operation) should leave a trace in the
    Witness system. This bridge makes that connection explicit.

Usage:
    >>> from services.witness.kblock_bridge import WitnessBridge, install_witness_bridge
    >>>
    >>> # Install globally (typically at application startup)
    >>> install_witness_bridge()
    >>>
    >>> # Now all K-Block bind operations will emit marks
    >>> doc = KBlock.pure("content")
    >>> result = doc >> transform  # Mark emitted automatically
    >>>
    >>> # Uninstall if needed
    >>> uninstall_witness_bridge()

See: spec/protocols/k-block.md
See: spec/protocols/witness-primitives.md
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .mark import Mark, MarkId, UmweltSnapshot

if TYPE_CHECKING:
    from services.k_block.core.kblock import KBlock, LineageEdge


class WitnessBridge:
    """
    Bridge implementation connecting K-Block operations to Witness marks.

    This class implements the WitnessBridgeProtocol from k_block.core.kblock,
    providing the actual logic to create Witness marks from K-Block bind operations.

    The bridge maintains an internal store of emitted marks for later retrieval.
    In a production system, this would typically persist to the MarkStore.

    Attributes:
        _marks: List of emitted marks (in-memory for this implementation)
        _umwelt: Default observer context for emitted marks
    """

    def __init__(self, umwelt: UmweltSnapshot | None = None) -> None:
        """
        Initialize the bridge.

        Args:
            umwelt: Default observer context for emitted marks.
                   If None, uses UmweltSnapshot.system().
        """
        self._marks: list[Mark] = []
        self._umwelt = umwelt or UmweltSnapshot.system()

    def emit_bind_mark(
        self,
        from_block: "KBlock",
        to_block: "KBlock",
        edge: "LineageEdge",
        operation: str,
    ) -> str | None:
        """
        Emit a Witness mark for a K-Block bind operation.

        This method is called by KBlock.bind() when a bridge is installed.
        It creates a Mark capturing the derivation and stores it.

        Args:
            from_block: The source K-Block
            to_block: The result K-Block
            edge: The LineageEdge created by bind()
            operation: Name of the transformation function

        Returns:
            The MarkId of the emitted mark, or None if emission failed
        """
        try:
            mark = Mark.from_kblock_bind(
                from_kblock_id=str(from_block.id),
                to_kblock_id=str(to_block.id),
                from_content=from_block.content,
                to_content=to_block.content,
                operation=operation,
                lineage_edge_dict=edge.to_dict(),
                path=from_block.path,
                umwelt=self._umwelt,
            )
            self._marks.append(mark)
            return str(mark.id)
        except Exception:
            # Bridge failures should not break K-Block operations
            return None

    @property
    def marks(self) -> list[Mark]:
        """Get all emitted marks."""
        return list(self._marks)

    def get_mark(self, mark_id: str) -> Mark | None:
        """Get a specific mark by ID."""
        for mark in self._marks:
            if str(mark.id) == mark_id:
                return mark
        return None

    def clear(self) -> None:
        """Clear all stored marks."""
        self._marks.clear()

    def __len__(self) -> int:
        """Return number of emitted marks."""
        return len(self._marks)


# Module-level singleton bridge
_default_bridge: WitnessBridge | None = None


def get_default_bridge() -> WitnessBridge | None:
    """Get the default bridge instance, if installed."""
    return _default_bridge


def install_witness_bridge(umwelt: UmweltSnapshot | None = None) -> WitnessBridge:
    """
    Install the witness bridge globally.

    After calling this, all K-Block bind operations will emit Witness marks.

    Args:
        umwelt: Optional observer context for emitted marks

    Returns:
        The installed WitnessBridge instance
    """
    global _default_bridge

    # Import here to avoid circular dependencies
    from services.k_block.core.kblock import set_witness_bridge

    _default_bridge = WitnessBridge(umwelt)
    set_witness_bridge(_default_bridge)

    return _default_bridge


def uninstall_witness_bridge() -> None:
    """
    Uninstall the witness bridge.

    After calling this, K-Block bind operations will not emit Witness marks.
    """
    global _default_bridge

    from services.k_block.core.kblock import set_witness_bridge

    set_witness_bridge(None)
    _default_bridge = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "WitnessBridge",
    "get_default_bridge",
    "install_witness_bridge",
    "uninstall_witness_bridge",
]
