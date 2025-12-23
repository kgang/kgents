"""
Living Spec AGENTESE Node: self.spec.* universal protocol.

Exposes the Living Spec system via AGENTESE paths:
- self.spec.manifest     - View spec with tokens and hyperedges
- self.spec.edit         - Enter editing monad (create K-Block)
- self.spec.commit       - Exit monad with witness trace
- self.spec.discard      - Exit monad without saving
- self.spec.navigate     - Follow hyperedge to related specs
- self.spec.expand       - Inline portal expansion
- self.spec.checkpoint   - Create restore point
- self.spec.rewind       - Restore to checkpoint

Philosophy:
    "The protocol IS the API."
    "Different observers, different perceptions."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .contracts import CommitResult, Observer
from .monad import SpecMonad
from .node import SpecNode
from .polynomial import Effect, SpecPolynomial, SpecState
from .sheaf import ViewType

# -----------------------------------------------------------------------------
# Active Monad Registry
# -----------------------------------------------------------------------------

# Simple registry for active monads (in production, would use proper storage)
_active_monads: dict[str, SpecMonad] = {}


def get_active_monad(path: str) -> SpecMonad | None:
    """Get active monad for a path."""
    return _active_monads.get(path)


def set_active_monad(path: str, monad: SpecMonad) -> None:
    """Register active monad for a path."""
    _active_monads[path] = monad


def clear_active_monad(path: str) -> None:
    """Clear active monad for a path."""
    _active_monads.pop(path, None)


# -----------------------------------------------------------------------------
# Rendering Helpers
# -----------------------------------------------------------------------------


@dataclass
class BasicRendering:
    """Simple rendering result for AGENTESE aspects."""

    summary: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for wire transfer."""
        return {
            "summary": self.summary,
            "content": self.content,
            "metadata": self.metadata,
        }


# -----------------------------------------------------------------------------
# Living Spec AGENTESE Node
# -----------------------------------------------------------------------------


@dataclass
class LivingSpecNode:
    """
    AGENTESE node for living spec operations.

    Provides aspects for:
    - PERCEPTION: manifest, edges, tokens
    - MUTATION: edit, commit, discard, checkpoint, rewind
    - NAVIGATION: navigate, expand

    Usage:
        node = LivingSpecNode()
        result = await node.manifest(observer, path="spec/protocols/k-block.md")
    """

    handle: str = "self.spec"
    _current_observer: Observer | None = field(default=None, repr=False)

    # -------------------------------------------------------------------------
    # Perception Aspects
    # -------------------------------------------------------------------------

    async def manifest(self, observer: Observer, path: str) -> BasicRendering:
        """
        View a spec with tokens and edges.

        Shows the spec content with extracted tokens (AGENTESE paths,
        tasks, code blocks, etc.) and available hyperedges.

        Args:
            observer: Current observer
            path: Spec path (file path or AGENTESE path)

        Returns:
            BasicRendering with spec manifest
        """
        spec = SpecNode(path=path)
        manifest = await spec.to_manifest(observer)

        # Check for active monad
        monad = get_active_monad(path)
        isolation = monad.isolation.name if monad else "NONE"

        return BasicRendering(
            summary=f"Spec: {path}",
            content=manifest.get("content", ""),
            metadata={
                "path": path,
                "kind": manifest.get("kind", "spec"),
                "tokens": manifest.get("tokens", []),
                "edges": manifest.get("edges", {}),
                "affordances": manifest.get("affordances", []),
                "isolation": isolation,
                "monad_active": monad is not None,
            },
        )

    async def edges(self, observer: Observer, path: str) -> BasicRendering:
        """
        Get hyperedges for a spec.

        Returns observer-dependent edges (tests, implements, etc.).

        Args:
            observer: Current observer
            path: Spec path

        Returns:
            BasicRendering with edges
        """
        spec = SpecNode(path=path)
        edges = spec.edges(observer)

        edge_summary = ", ".join(f"{k}:{len(v)}" for k, v in edges.items())

        return BasicRendering(
            summary=f"Edges: {edge_summary}",
            content="",
            metadata={
                "path": path,
                "edges": {k: [n.path for n in v] for k, v in edges.items()},
                "edge_count": sum(len(v) for v in edges.values()),
            },
        )

    async def tokens(self, observer: Observer, path: str) -> BasicRendering:
        """
        Get interactive tokens for a spec.

        Returns extracted tokens with their affordances.

        Args:
            observer: Current observer
            path: Spec path

        Returns:
            BasicRendering with tokens
        """
        spec = SpecNode(path=path)
        tokens = await spec.tokens()

        token_summary = ", ".join(
            f"{t.token_type}:{sum(1 for _ in tokens if _.token_type == t.token_type)}"
            for t in set(tokens)
        )

        return BasicRendering(
            summary=f"Tokens: {len(tokens)}",
            content="",
            metadata={
                "path": path,
                "tokens": [t.to_dict() for t in tokens],
                "token_count": len(tokens),
                "by_type": self._count_by_type(tokens),
            },
        )

    def _count_by_type(self, tokens: list[Any]) -> dict[str, int]:
        """Count tokens by type."""
        counts: dict[str, int] = {}
        for t in tokens:
            counts[t.token_type] = counts.get(t.token_type, 0) + 1
        return counts

    # -------------------------------------------------------------------------
    # Mutation Aspects
    # -------------------------------------------------------------------------

    async def edit(self, observer: Observer, path: str) -> BasicRendering:
        """
        Enter editing monad for a spec.

        Creates a K-Block and enters isolated editing mode.

        Args:
            observer: Current observer
            path: Spec path to edit

        Returns:
            BasicRendering with monad info
        """
        # Check if already editing
        existing = get_active_monad(path)
        if existing:
            return BasicRendering(
                summary=f"Already editing: {path}",
                content=existing.working_content,
                metadata={
                    "monad_id": existing.id,
                    "isolation": existing.isolation.name,
                    "is_dirty": existing.is_dirty,
                    "checkpoints": len(existing.checkpoints),
                },
            )

        # Create new monad
        spec = SpecNode(path=path)
        monad = await SpecMonad.pure_async(spec)
        set_active_monad(path, monad)

        return BasicRendering(
            summary=f"Editing: {path}",
            content=monad.working_content,
            metadata={
                "monad_id": monad.id,
                "isolation": monad.isolation.name,
                "is_dirty": monad.is_dirty,
                "base_hash": monad.content_hash,
                "line_count": len(monad.working_content.split("\n")),
            },
        )

    async def update(
        self,
        observer: Observer,
        path: str,
        content: str,
        reasoning: str | None = None,
    ) -> BasicRendering:
        """
        Update content within monad.

        Args:
            observer: Current observer
            path: Spec path
            content: New content
            reasoning: Why this change

        Returns:
            BasicRendering with update result
        """
        monad = get_active_monad(path)
        if not monad:
            return BasicRendering(
                summary="No active edit",
                content="Use 'edit' first to create a monad",
                metadata={"error": "no_monad", "path": path},
            )

        monad.set_content(content)

        return BasicRendering(
            summary=f"Updated: {path}",
            content=content[:200] + "..." if len(content) > 200 else content,
            metadata={
                "monad_id": monad.id,
                "isolation": monad.isolation.name,
                "is_dirty": monad.is_dirty,
                "content_hash": monad.content_hash,
            },
        )

    async def commit(
        self,
        observer: Observer,
        path: str,
        reasoning: str,
    ) -> BasicRendering:
        """
        Commit changes with witness trace.

        Args:
            observer: Current observer
            path: Spec path
            reasoning: Why these changes were made

        Returns:
            BasicRendering with commit result
        """
        monad = get_active_monad(path)
        if not monad:
            return BasicRendering(
                summary="No active edit",
                content="Use 'edit' first to create a monad",
                metadata={"error": "no_monad", "path": path},
            )

        result = await monad.commit(reasoning, actor=observer.id)
        clear_active_monad(path)

        return BasicRendering(
            summary=f"Committed: {path}",
            content=f"Version: {result.version_id}\nMark: {result.mark_id}\n{result.delta_summary}",
            metadata={
                "version_id": str(result.version_id),
                "mark_id": str(result.mark_id) if result.mark_id else None,
                "path": result.path,
                "delta_summary": result.delta_summary,
            },
        )

    async def discard(self, observer: Observer, path: str) -> BasicRendering:
        """
        Discard changes without committing.

        Args:
            observer: Current observer
            path: Spec path

        Returns:
            BasicRendering confirming discard
        """
        monad = get_active_monad(path)
        if not monad:
            return BasicRendering(
                summary="No active edit",
                content="Nothing to discard",
                metadata={"error": "no_monad", "path": path},
            )

        monad.discard()
        clear_active_monad(path)

        return BasicRendering(
            summary=f"Discarded: {path}",
            content="Changes discarded. Monad closed.",
            metadata={"path": path},
        )

    async def checkpoint(
        self,
        observer: Observer,
        path: str,
        name: str,
    ) -> BasicRendering:
        """
        Create a checkpoint (restore point).

        Args:
            observer: Current observer
            path: Spec path
            name: Checkpoint name

        Returns:
            BasicRendering with checkpoint info
        """
        monad = get_active_monad(path)
        if not monad:
            return BasicRendering(
                summary="No active edit",
                content="Use 'edit' first to create a monad",
                metadata={"error": "no_monad", "path": path},
            )

        cp = monad.checkpoint(name)

        return BasicRendering(
            summary=f"Checkpoint: {name}",
            content=f"Created checkpoint {cp.id}",
            metadata={
                "checkpoint_id": cp.id,
                "checkpoint_name": cp.name,
                "content_hash": cp.content_hash,
                "total_checkpoints": len(monad.checkpoints),
            },
        )

    async def rewind(
        self,
        observer: Observer,
        path: str,
        checkpoint_id: str,
    ) -> BasicRendering:
        """
        Rewind to a checkpoint.

        Args:
            observer: Current observer
            path: Spec path
            checkpoint_id: Checkpoint to restore

        Returns:
            BasicRendering with rewind result
        """
        monad = get_active_monad(path)
        if not monad:
            return BasicRendering(
                summary="No active edit",
                content="Use 'edit' first to create a monad",
                metadata={"error": "no_monad", "path": path},
            )

        try:
            monad.rewind(checkpoint_id)
            return BasicRendering(
                summary=f"Rewound to: {checkpoint_id}",
                content=monad.working_content[:200] + "...",
                metadata={
                    "checkpoint_id": checkpoint_id,
                    "content_hash": monad.content_hash,
                },
            )
        except ValueError as e:
            return BasicRendering(
                summary="Rewind failed",
                content=str(e),
                metadata={"error": "checkpoint_not_found", "checkpoint_id": checkpoint_id},
            )

    # -------------------------------------------------------------------------
    # Navigation Aspects
    # -------------------------------------------------------------------------

    async def navigate(
        self,
        observer: Observer,
        path: str,
        edge_type: str,
    ) -> BasicRendering:
        """
        Navigate to related specs via hyperedge.

        Args:
            observer: Current observer
            path: Current spec path
            edge_type: Type of edge to follow (tests, implements, etc.)

        Returns:
            BasicRendering with destinations
        """
        spec = SpecNode(path=path)
        edges = spec.edges(observer)

        if edge_type not in edges:
            return BasicRendering(
                summary=f"No edge: {edge_type}",
                content=f"Available edges: {', '.join(edges.keys())}",
                metadata={
                    "error": "edge_not_found",
                    "edge_type": edge_type,
                    "available": list(edges.keys()),
                },
            )

        destinations = edges[edge_type]

        return BasicRendering(
            summary=f"[{edge_type}] → {len(destinations)} specs",
            content="\n".join(f"- {n.path}" for n in destinations),
            metadata={
                "edge_type": edge_type,
                "destinations": [n.path for n in destinations],
                "count": len(destinations),
            },
        )

    async def expand(
        self,
        observer: Observer,
        path: str,
        edge_type: str,
    ) -> BasicRendering:
        """
        Expand portal inline (load destination content).

        Args:
            observer: Current observer
            path: Current spec path
            edge_type: Type of edge to expand

        Returns:
            BasicRendering with expanded content
        """
        spec = SpecNode(path=path)
        portal = spec.as_portal(edge_type, observer)

        if not portal:
            return BasicRendering(
                summary=f"No portal: {edge_type}",
                content="Edge not found or not visible to observer",
                metadata={"error": "portal_not_found", "edge_type": edge_type},
            )

        result = await portal.expand()

        if result.effect == "expansion_complete":
            return BasicRendering(
                summary=f"Expanded: [{edge_type}]",
                content="\n---\n".join(
                    f"## {dest}\n{portal._content_cache.get(dest, '')[:500]}"
                    for dest in portal.destinations
                ),
                metadata={
                    "edge_type": edge_type,
                    "destinations": list(portal.destinations),
                    "state": portal.state.name,
                },
            )
        else:
            return BasicRendering(
                summary=f"Expansion failed: {result.effect}",
                content=str(result.data),
                metadata={"error": result.effect, "data": result.data},
            )


# -----------------------------------------------------------------------------
# Node Registration (for AGENTESE gateway)
# -----------------------------------------------------------------------------

# Singleton instance
_node_instance: LivingSpecNode | None = None


def get_living_spec_node() -> LivingSpecNode:
    """Get or create the Living Spec node singleton."""
    global _node_instance
    if _node_instance is None:
        _node_instance = LivingSpecNode()
    return _node_instance


def reset_living_spec_node() -> None:
    """Reset the node singleton (for testing)."""
    global _node_instance
    _node_instance = None
    _active_monads.clear()
