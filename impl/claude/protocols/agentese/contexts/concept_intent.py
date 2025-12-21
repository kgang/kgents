"""
AGENTESE Concept Intent Context: Typed Task Decomposition.

Task-related nodes for concept.intent.* paths:
- IntentNode: Typed task trees with dependencies

This node provides AGENTESE access to the IntentTree primitive for
typed, structured task decomposition.

AGENTESE Paths:
    concept.intent.manifest   - Show intent trees
    concept.intent.create     - Create a new intent
    concept.intent.decompose  - Add child intents
    concept.intent.fulfill    - Mark intent complete
    concept.intent.block      - Mark intent blocked

See: services/witness/intent.py
See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..affordances import (
    AspectCategory,
    aspect,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

# =============================================================================
# Global Store Instance
# =============================================================================

_intent_store: dict[str, Any] = {}


def _get_intent(intent_id: str) -> Any | None:
    """Get intent by ID."""
    return _intent_store.get(intent_id)


def _add_intent(intent: Any) -> None:
    """Add intent to store."""
    _intent_store[str(intent.id)] = intent


# =============================================================================
# IntentNode: AGENTESE Interface to Intent/IntentTree
# =============================================================================


INTENT_AFFORDANCES: tuple[str, ...] = ("manifest", "create", "decompose", "fulfill", "block")


@node(
    "concept.intent",
    description="Typed task decomposition with dependencies",
)
@dataclass
class IntentNode(BaseLogosNode):
    """
    concept.intent - Typed task decomposition.

    An IntentTree is a directed graph of Intents where:
    - Each Intent has a type (EXPLORE, DESIGN, IMPLEMENT, REFINE, VERIFY)
    - Intents can have parent/child relationships (decomposition)
    - Intents can have dependencies (ordering constraints)

    Laws (from intent.py):
    - Law 1 (Typed): Every Intent has exactly one IntentType
    - Law 2 (Tree Structure): Parent-child relationships form a tree
    - Law 3 (Dependencies): Dependencies form a DAG (no cycles)
    - Law 4 (Status Propagation): Parent status reflects children

    AGENTESE: concept.intent.*
    """

    _handle: str = "concept.intent"

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Intent affordances available to all archetypes."""
        return INTENT_AFFORDANCES

    # ==========================================================================
    # Core Protocol Methods
    # ==========================================================================

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Show intent trees.

        Returns:
            List of intents with status and types
        """
        from services.witness.intent import IntentStatus, IntentType

        # Collect stats
        total = len(_intent_store)
        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}

        for intent in _intent_store.values():
            type_name = intent.intent_type.value
            status_name = intent.status.name
            by_type[type_name] = by_type.get(type_name, 0) + 1
            by_status[status_name] = by_status.get(status_name, 0) + 1

        # Find root intents (no parent)
        roots = [i for i in _intent_store.values() if i.parent_id is None]
        recent_roots = sorted(roots, key=lambda i: i.created_at, reverse=True)[:5]

        manifest_data = {
            "path": self.handle,
            "description": "Typed task decomposition with dependencies",
            "total_intents": total,
            "by_type": by_type,
            "by_status": by_status,
            "root_intents": [
                {
                    "id": str(i.id),
                    "description": i.description[:50] + "..."
                    if len(i.description) > 50
                    else i.description,
                    "type": i.intent_type.value,
                    "status": i.status.name,
                    "children_count": len(i.children_ids),
                    "dependencies_count": len(i.depends_on),
                }
                for i in recent_roots
            ],
            "intent_types": [t.value for t in IntentType],
            "laws": [
                "Law 1: Every Intent has exactly one IntentType",
                "Law 2: Parent-child relationships form a tree",
                "Law 3: Dependencies form a DAG (no cycles)",
                "Law 4: Parent status reflects children",
            ],
        }

        return BasicRendering(
            summary="Intents (Task Decomposition)",
            content=self._format_manifest_cli(manifest_data),
            metadata=manifest_data,
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle Intent-specific aspects."""
        match aspect:
            case "create":
                return self._create_intent(**kwargs)
            case "decompose":
                return self._decompose_intent(**kwargs)
            case "fulfill":
                return self._fulfill_intent(**kwargs)
            case "block":
                return self._block_intent(**kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # ==========================================================================
    # Aspect Implementations
    # ==========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        help="Create a new intent (Law 1: must have type)",
    )
    def _create_intent(
        self,
        description: str = "",
        intent_type: str = "implement",
        parent_id: str | None = None,
        depends_on: list[str] | None = None,
        priority: int = 0,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Create a new Intent.

        Args:
            description: What this intent aims to achieve
            intent_type: Type of work (explore, design, implement, refine, verify, archive)
            parent_id: ID of parent intent (for decomposition)
            depends_on: IDs of intents this depends on
            priority: Higher = more important
            tags: Tags for categorization

        Returns:
            Created Intent info
        """
        from services.witness.intent import Intent, IntentId, IntentType

        # Parse intent type (Law 1)
        try:
            itype = IntentType(intent_type.lower())
        except ValueError:
            valid_types = [t.value for t in IntentType]
            return {"error": f"Invalid intent_type. Valid: {valid_types}"}

        # Parse parent (Law 2)
        pid = IntentId(parent_id) if parent_id else None

        # Parse dependencies (Law 3)
        deps = tuple(IntentId(d) for d in (depends_on or []))

        # Create intent
        intent = Intent.create(
            description=description,
            intent_type=itype,
            parent_id=pid,
            depends_on=deps,
            priority=priority,
            tags=tuple(tags) if tags else (),
        )

        # Store
        _add_intent(intent)

        # Update parent's children if applicable
        if pid and (parent := _get_intent(str(pid))):
            # Note: Intent is frozen, so we'd need to replace with updated version
            # For now, track relationship in response
            pass

        return {
            "id": str(intent.id),
            "description": description,
            "type": itype.value,
            "status": intent.status.name,
            "parent_id": parent_id,
            "depends_on": list(depends_on) if depends_on else [],
            "priority": priority,
            "created_at": intent.created_at.isoformat(),
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Decompose intent into children (Law 2: tree structure)",
    )
    def _decompose_intent(
        self,
        intent_id: str = "",
        children: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        Decompose an intent into child intents.

        Law 2: Creates a tree structure.
        """
        if not intent_id:
            return {"error": "intent_id is required"}

        intent = _get_intent(intent_id)
        if intent is None:
            return {"error": f"Intent {intent_id} not found"}

        if not children:
            return {"error": "children list is required"}

        # Create child intents
        created_children = []
        for child_data in children:
            result = self._create_intent(
                description=child_data.get("description", ""),
                intent_type=child_data.get("type", "implement"),
                parent_id=intent_id,
                depends_on=child_data.get("depends_on"),
                priority=child_data.get("priority", 0),
                tags=child_data.get("tags"),
            )
            if "error" not in result:
                created_children.append(result)

        return {
            "parent_id": intent_id,
            "children_created": len(created_children),
            "children": created_children,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Mark intent as complete (Law 4: propagates to parent)",
    )
    def _fulfill_intent(
        self,
        intent_id: str = "",
    ) -> dict[str, Any]:
        """
        Mark an Intent as fulfilled/complete.

        Law 4: Status propagates to parent.
        """
        if not intent_id:
            return {"error": "intent_id is required"}

        intent = _get_intent(intent_id)
        if intent is None:
            return {"error": f"Intent {intent_id} not found"}

        # Fulfill the intent
        fulfilled = intent.fulfill()
        _add_intent(fulfilled)  # Replace with updated version

        return {
            "intent_id": intent_id,
            "status": fulfilled.status.name,
            "completed_at": fulfilled.completed_at.isoformat() if fulfilled.completed_at else None,
            "parent_id": str(fulfilled.parent_id) if fulfilled.parent_id else None,
        }

    @aspect(
        category=AspectCategory.MUTATION,
        help="Mark intent as blocked (Law 4: propagates to parent)",
    )
    def _block_intent(
        self,
        intent_id: str = "",
        reason: str = "",
    ) -> dict[str, Any]:
        """
        Mark an Intent as blocked.

        Law 4: Status propagates to parent.
        """
        if not intent_id:
            return {"error": "intent_id is required"}

        intent = _get_intent(intent_id)
        if intent is None:
            return {"error": f"Intent {intent_id} not found"}

        # Block the intent
        blocked = intent.block(reason=reason)
        _add_intent(blocked)  # Replace with updated version

        return {
            "intent_id": intent_id,
            "status": blocked.status.name,
            "reason": reason,
            "parent_id": str(blocked.parent_id) if blocked.parent_id else None,
        }

    # ==========================================================================
    # CLI Formatting Helpers
    # ==========================================================================

    def _format_manifest_cli(self, data: dict[str, Any]) -> str:
        """Format manifest for CLI output."""
        lines = [
            "Intents (Task Decomposition)",
            "=" * 40,
            "",
            f"Total intents: {data['total_intents']}",
            "",
        ]

        # By type
        if data["by_type"]:
            lines.append("By Type:")
            for t, count in sorted(data["by_type"].items()):
                lines.append(f"  {t}: {count}")
            lines.append("")

        # By status
        if data["by_status"]:
            lines.append("By Status:")
            for s, count in sorted(data["by_status"].items()):
                lines.append(f"  {s}: {count}")
            lines.append("")

        # Root intents
        if data["root_intents"]:
            lines.append("Root Intents:")
            for i in data["root_intents"]:
                status_icon = {"COMPLETE": "v", "ACTIVE": ">", "BLOCKED": "x"}.get(i["status"], "o")
                lines.append(f"  {status_icon} [{i['type']}] {i['description']}")
                if i["children_count"]:
                    lines.append(f"    Children: {i['children_count']}")
        else:
            lines.append("No intents yet. Use create to start.")

        return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "IntentNode",
]
