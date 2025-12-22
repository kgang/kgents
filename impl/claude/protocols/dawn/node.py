"""
Dawn Cockpit AGENTESE Node.

Registers the `time.dawn.*` paths for Kent's daily operating surface.

This node is a projection functor — it doesn't own state, it projects
state from FocusManager and SnippetLibrary into AGENTESE-visible affordances.

Architecture:
    Dawn : (Coffee x Portal x Witness x Brain) -> TUI

Teaching:
    gotcha: @node runs at import time. If this module isn't imported in
            gateway.py, the node won't be registered.
            (Evidence: docs/skills/agentese-node-registration.md)

    gotcha: Dependencies use optional pattern (`| None = None`) because
            Witness may not be available during testing or lightweight invocations.
            (Evidence: agentese-node-registration.md → "Enlightened Resolution")

    gotcha: QuerySnippet loading requires AGENTESE invocation. The snippets_copy
            aspect detects unloaded QuerySnippets and invokes their query path
            via logos.invoke() before returning content.
            (Evidence: spec/protocols/dawn-cockpit.md § QuerySnippet)

See: spec/protocols/dawn-cockpit.md
AGENTESE: time.dawn
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, Effect, aspect
from protocols.agentese.node import (
    BaseLogosNode,
    BasicRendering,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    DawnManifestResponse,
    FocusAddRequest,
    FocusAddResponse,
    FocusDemoteRequest,
    FocusItemResponse,
    FocusListResponse,
    FocusMoveResponse,
    FocusPromoteRequest,
    FocusRemoveRequest,
    FocusRemoveResponse,
    SnippetAddRequest,
    SnippetAddResponse,
    SnippetCopyRequest,
    SnippetCopyResponse,
    SnippetListResponse,
    SnippetRemoveRequest,
    SnippetRemoveResponse,
    SnippetResponse,
    focus_item_to_response,
    snippet_to_response,
)
from .focus import Bucket, FocusManager
from .snippets import SnippetLibrary

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.witness import WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Affordances
# =============================================================================

DAWN_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "focus_list",
    "focus_add",
    "focus_remove",
    "focus_promote",
    "focus_demote",
    "snippets_list",
    "snippets_copy",
    "snippets_add",
    "snippets_remove",
)


# =============================================================================
# Dawn Node
# =============================================================================


@node(
    path="time.dawn",
    description="Daily operating surface — projection of focus, snippets, and coffee",
    dependencies=(),  # All deps are optional via __init__ defaults
)
@dataclass
class DawnNode(BaseLogosNode):
    """
    time.dawn - Kent's daily operating surface.

    This node exposes focus management and snippet operations through AGENTESE.
    It is a projection functor that composes existing services into a unified
    daily interface.

    Aspects:
        manifest: Current state, counts, last coffee
        focus.list: List focus items by bucket
        focus.add: Add new focus item
        focus.remove: Remove focus item
        focus.promote: Move item to higher bucket
        focus.demote: Move item to lower bucket
        snippets.list: List all snippets
        snippets.copy: Copy snippet (records in Witness)
        snippets.add: Add custom snippet
        snippets.remove: Remove custom snippet
    """

    _handle: str = "time.dawn"

    # Dependencies injected by container (all optional)
    focus_manager: FocusManager | None = None
    snippet_library: SnippetLibrary | None = None
    witness_persistence: "WitnessPersistence | None" = None

    def __post_init__(self) -> None:
        """Initialize defaults if not injected, load persisted data."""
        if self.focus_manager is None:
            fm = FocusManager()
            fm.load()  # Load persisted focus items
            object.__setattr__(self, "focus_manager", fm)
        if self.snippet_library is None:
            lib = SnippetLibrary()
            lib.load_defaults()
            lib.load_custom()  # Load persisted custom snippets
            object.__setattr__(self, "snippet_library", lib)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes get same affordances for daily operation."""
        return DAWN_AFFORDANCES

    # =========================================================================
    # Manifest
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="View Dawn cockpit state — focus counts, snippet counts, coffee status",
    )
    async def manifest(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Renderable:
        """
        What is Dawn? Project to observer's view.

        Returns counts and status for the daily operating surface.
        """
        assert self.focus_manager is not None
        assert self.snippet_library is not None

        today = self.focus_manager.list(bucket=Bucket.TODAY)
        week = self.focus_manager.list(bucket=Bucket.WEEK)
        someday = self.focus_manager.list(bucket=Bucket.SOMEDAY)
        stale = self.focus_manager.get_stale()

        response = DawnManifestResponse(
            focus_count=len(self.focus_manager),
            today_count=len(today),
            week_count=len(week),
            someday_count=len(someday),
            snippet_count=len(self.snippet_library),
            stale_count=len(stale),
        )

        content = f"""
## 🌅 Dawn Cockpit

**Focus Items**: {response.focus_count}
  - TODAY: {response.today_count}
  - WEEK: {response.week_count}
  - SOMEDAY: {response.someday_count}
  - ⚠️ Stale: {response.stale_count}

**Snippets**: {response.snippet_count}
  - Static: {len(self.snippet_library.list_static())}
  - Query: {len(self.snippet_library.list_query())}
  - Custom: {len(self.snippet_library.list_custom())}

---

**Aspects**: focus.list, focus.add, snippets.list, snippets.copy

> *"The cockpit doesn't fly the plane. The pilot flies the plane."*
"""

        return BasicRendering(
            summary=f"Dawn: {response.today_count} today, {response.snippet_count} snippets",
            content=content,
            metadata=response.__dict__,
        )

    # =========================================================================
    # Focus Aspects
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List focus items, optionally filtered by bucket",
    )
    async def focus_list(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        bucket: str | None = None,
        **kwargs: Any,
    ) -> FocusListResponse:
        """
        List focus items.

        Args:
            bucket: Optional bucket filter ("today", "week", "someday")

        Returns:
            FocusListResponse with items and counts
        """
        assert self.focus_manager is not None

        bucket_enum = Bucket(bucket) if bucket else None
        items = self.focus_manager.list(bucket=bucket_enum)

        return FocusListResponse(
            items=tuple(focus_item_to_response(i) for i in items),
            total_count=len(items),
            bucket_filter=bucket,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("focus")],
        help="Add a new focus item",
    )
    async def focus_add(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        target: str,
        label: str | None = None,
        bucket: str = "today",
        **kwargs: Any,
    ) -> FocusAddResponse:
        """
        Add a new focus item.

        Args:
            target: AGENTESE path or file path
            label: Human-readable label (inferred if not provided)
            bucket: Which bucket ("today", "week", "someday")

        Returns:
            FocusAddResponse with created item
        """
        assert self.focus_manager is not None

        bucket_enum = Bucket(bucket)
        item = self.focus_manager.add(target, label=label, bucket=bucket_enum)

        return FocusAddResponse(
            item=focus_item_to_response(item),
            success=True,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.DELETES("focus")],
        help="Remove a focus item",
    )
    async def focus_remove(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        item_id: str,
        **kwargs: Any,
    ) -> FocusRemoveResponse:
        """
        Remove a focus item.

        Args:
            item_id: ID of item to remove

        Returns:
            FocusRemoveResponse indicating success
        """
        assert self.focus_manager is not None

        removed = self.focus_manager.remove(item_id)

        return FocusRemoveResponse(
            removed=removed,
            item_id=item_id,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("focus")],
        help="Promote focus item to higher bucket (toward TODAY)",
    )
    async def focus_promote(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        item_id: str,
        **kwargs: Any,
    ) -> FocusMoveResponse | None:
        """
        Promote focus item to higher bucket.

        Args:
            item_id: ID of item to promote

        Returns:
            FocusMoveResponse with old/new buckets, or None if not found
        """
        assert self.focus_manager is not None

        old_item = self.focus_manager.get(item_id)
        if old_item is None:
            return None

        old_bucket = old_item.bucket
        new_item = self.focus_manager.promote(item_id)
        if new_item is None:
            return None

        return FocusMoveResponse(
            item=focus_item_to_response(new_item),
            previous_bucket=old_bucket.value,
            new_bucket=new_item.bucket.value,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("focus")],
        help="Demote focus item to lower bucket (toward SOMEDAY)",
    )
    async def focus_demote(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        item_id: str,
        **kwargs: Any,
    ) -> FocusMoveResponse | None:
        """
        Demote focus item to lower bucket.

        Args:
            item_id: ID of item to demote

        Returns:
            FocusMoveResponse with old/new buckets, or None if not found
        """
        assert self.focus_manager is not None

        old_item = self.focus_manager.get(item_id)
        if old_item is None:
            return None

        old_bucket = old_item.bucket
        new_item = self.focus_manager.demote(item_id)
        if new_item is None:
            return None

        return FocusMoveResponse(
            item=focus_item_to_response(new_item),
            previous_bucket=old_bucket.value,
            new_bucket=new_item.bucket.value,
        )

    # =========================================================================
    # Snippet Aspects
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[],
        help="List all snippets (static, query, custom)",
    )
    async def snippets_list(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> SnippetListResponse:
        """
        List all snippets.

        Returns:
            SnippetListResponse with all snippets and counts
        """
        assert self.snippet_library is not None

        static = self.snippet_library.list_static()
        query = self.snippet_library.list_query()
        custom = self.snippet_library.list_custom()

        all_snippets = static + query + custom

        return SnippetListResponse(
            snippets=tuple(snippet_to_response(s) for s in all_snippets),
            total_count=len(all_snippets),
            static_count=len(static),
            query_count=len(query),
            custom_count=len(custom),
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.READS("snippets")],
        help="Copy a snippet to clipboard (records in Witness)",
    )
    async def snippets_copy(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        snippet_id: str,
        **kwargs: Any,
    ) -> SnippetCopyResponse | None:
        """
        Copy a snippet and record the action in Witness.

        Law 2 (copy_records): Every copy action records in Witness.

        For QuerySnippets, this aspect invokes the AGENTESE path stored in
        snippet.query to load content dynamically. The loaded content is
        cached in the snippet library for future access.

        Args:
            snippet_id: ID of snippet to copy

        Returns:
            SnippetCopyResponse with content and witness mark ID
        """
        assert self.snippet_library is not None

        snippet = self.snippet_library.get(snippet_id)
        if snippet is None:
            return None

        # Get content (already loaded for static/custom, may need loading for query)
        snippet_dict = snippet.to_dict()
        content = snippet_dict.get("content")

        # QuerySnippet loading via AGENTESE
        if content is None and snippet_dict.get("type") == "query":
            query_path = snippet_dict.get("query")
            if query_path:
                content = await self._load_query_snippet(query_path, observer)
                # Cache the loaded content
                if content:
                    self.snippet_library.update_query_content(snippet_id, content)

        # Final fallback if still no content
        if content is None:
            content = f"[Query snippet: {snippet_dict.get('query', 'unknown')}]"

        # Record in Witness if available (Law 2: copy_records)
        witness_mark_id: str | None = None
        if self.witness_persistence is not None:
            try:
                result = await self.witness_persistence.save_mark(
                    action=f"Copied snippet: {snippet_dict['label']}",
                    reasoning=f"Daily work facilitation ({snippet_dict.get('type', 'unknown')} snippet)",
                    principles=["joy_inducing"],
                    author="dawn",
                )
                witness_mark_id = result.mark_id if result else None
            except Exception as e:
                logger.debug(f"Witness recording failed: {e}")

        return SnippetCopyResponse(
            snippet_id=snippet_id,
            label=snippet_dict["label"],
            content=content,
            copied=True,
            witness_mark_id=witness_mark_id,
        )

    async def _load_query_snippet(
        self,
        query_path: str,
        observer: Observer | "Umwelt[Any, Any]",
    ) -> str | None:
        """
        Load content for a QuerySnippet by invoking its AGENTESE path.

        This method bridges Dawn's lazy-loaded snippets with the AGENTESE
        protocol. Query paths like "self.memory.recent" or "self.witness.thoughts"
        are resolved through the gateway/logos infrastructure.

        Args:
            query_path: AGENTESE path (e.g., "self.memory.recent")
            observer: Observer context for the invocation

        Returns:
            Content string, or None if loading failed

        Teaching:
            gotcha: Query paths may reference non-existent nodes during startup
                    or testing. Always catch exceptions gracefully.
                    (Evidence: agentese-node-registration.md)
        """
        try:
            from protocols.agentese.logos import Logos

            logos = Logos()

            # Parse path into node.aspect format
            # e.g., "self.memory.recent" → invoke on "self.memory" with aspect "recent"
            parts = query_path.split(".")
            if len(parts) < 2:
                logger.debug(f"Invalid query path format: {query_path}")
                return None

            # Try to invoke the full path as an aspect
            result = await logos.invoke(query_path, observer)

            # Extract content from result
            if result is None:
                return None

            # Handle different result types
            if isinstance(result, str):
                return result
            if hasattr(result, "content"):
                return str(result.content)
            if hasattr(result, "to_text"):
                return str(result.to_text())
            if hasattr(result, "to_dict"):
                result_dict = result.to_dict()
                # Try common content keys
                for key in ("content", "summary", "text", "thoughts"):
                    if key in result_dict and result_dict[key]:
                        return str(result_dict[key])
                # Fallback to formatted dict
                return str(result_dict)

            return str(result)

        except Exception as e:
            logger.debug(f"QuerySnippet load failed for {query_path}: {e}")
            return None

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("snippets")],
        help="Add a custom snippet",
    )
    async def snippets_add(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        label: str,
        content: str,
        **kwargs: Any,
    ) -> SnippetAddResponse:
        """
        Add a custom snippet.

        Args:
            label: Human-readable label
            content: The snippet content

        Returns:
            SnippetAddResponse with created snippet
        """
        assert self.snippet_library is not None

        snippet = self.snippet_library.add_custom(label, content)

        return SnippetAddResponse(
            snippet=snippet_to_response(snippet),
            success=True,
        )

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.DELETES("snippets")],
        help="Remove a custom snippet",
    )
    async def snippets_remove(
        self,
        observer: Observer | "Umwelt[Any, Any]",
        snippet_id: str,
        **kwargs: Any,
    ) -> SnippetRemoveResponse:
        """
        Remove a custom snippet.

        Only custom snippets can be removed.

        Args:
            snippet_id: ID of snippet to remove

        Returns:
            SnippetRemoveResponse indicating success
        """
        assert self.snippet_library is not None

        removed = self.snippet_library.remove_custom(snippet_id)

        return SnippetRemoveResponse(
            removed=removed,
            snippet_id=snippet_id,
        )

    # =========================================================================
    # Aspect Router
    # =========================================================================

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to the appropriate method."""
        # Route to the appropriate aspect method
        if aspect in ("focus_list", "focus.list"):
            return await self.focus_list(observer, **kwargs)
        if aspect in ("focus_add", "focus.add"):
            return await self.focus_add(observer, **kwargs)
        if aspect in ("focus_remove", "focus.remove"):
            return await self.focus_remove(observer, **kwargs)
        if aspect in ("focus_promote", "focus.promote"):
            return await self.focus_promote(observer, **kwargs)
        if aspect in ("focus_demote", "focus.demote"):
            return await self.focus_demote(observer, **kwargs)
        if aspect in ("snippets_list", "snippets.list"):
            return await self.snippets_list(observer, **kwargs)
        if aspect in ("snippets_copy", "snippets.copy"):
            return await self.snippets_copy(observer, **kwargs)
        if aspect in ("snippets_add", "snippets.add"):
            return await self.snippets_add(observer, **kwargs)
        if aspect in ("snippets_remove", "snippets.remove"):
            return await self.snippets_remove(observer, **kwargs)

        raise ValueError(f"Unknown aspect: {aspect}")


# =============================================================================
# Factory Functions
# =============================================================================

_dawn_node: DawnNode | None = None


def get_dawn_node() -> DawnNode:
    """Get or create the singleton DawnNode."""
    global _dawn_node
    if _dawn_node is None:
        _dawn_node = DawnNode()
    return _dawn_node


def create_dawn_node(
    focus_manager: FocusManager | None = None,
    snippet_library: SnippetLibrary | None = None,
    witness_persistence: "WitnessPersistence | None" = None,
) -> DawnNode:
    """Create a new DawnNode with optional dependencies (for testing)."""
    return DawnNode(
        focus_manager=focus_manager,
        snippet_library=snippet_library,
        witness_persistence=witness_persistence,
    )


def reset_dawn_node() -> None:
    """Reset singleton (for testing)."""
    global _dawn_node
    _dawn_node = None


__all__ = [
    "DAWN_AFFORDANCES",
    "DawnNode",
    "get_dawn_node",
    "create_dawn_node",
    "reset_dawn_node",
]
