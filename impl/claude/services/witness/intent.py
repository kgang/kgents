"""
IntentTree: Typed Task Decomposition with Dependencies.

An IntentTree is a directed graph of Intents where:
- Each Intent has a type (EXPLORE, DESIGN, IMPLEMENT, REFINE, VERIFY)
- Intents can have parent/child relationships (decomposition)
- Intents can have dependencies (ordering constraints)
- Status propagates through the tree

Philosophy:
    "Every task decomposes. The IntentTree makes decomposition
    explicit and typed. It answers: What are we doing? What kind
    of work is it? What must happen first?"

Laws:
- Law 1 (Typed): Every Intent has exactly one IntentType
- Law 2 (Tree Structure): Parent-child relationships form a tree
- Law 3 (Dependencies): Dependencies form a DAG (no cycles)
- Law 4 (Status Propagation): Parent status reflects children

See: spec/protocols/warp-primitives.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, NewType
from uuid import uuid4

# =============================================================================
# Type Aliases
# =============================================================================

IntentId = NewType("IntentId", str)


def generate_intent_id() -> IntentId:
    """Generate a unique Intent ID."""
    return IntentId(f"intent-{uuid4().hex[:12]}")


# =============================================================================
# Intent Type (Law 1)
# =============================================================================


class IntentType(Enum):
    """
    Typed intent categories.

    Law 1: Every Intent has exactly one IntentType.

    Types:
    - EXPLORE: Discover and understand (research, investigation)
    - DESIGN: Plan and architect (specifications, proposals)
    - IMPLEMENT: Build and create (code, content)
    - REFINE: Improve and polish (optimization, cleanup)
    - VERIFY: Test and validate (testing, review)
    - ARCHIVE: Preserve and document (documentation, backup)
    """

    EXPLORE = "explore"
    DESIGN = "design"
    IMPLEMENT = "implement"
    REFINE = "refine"
    VERIFY = "verify"
    ARCHIVE = "archive"


# =============================================================================
# Intent Status (Law 4)
# =============================================================================


class IntentStatus(Enum):
    """
    Status of an Intent.

    Law 4: Parent status reflects children.
    - All children COMPLETE → Parent can be COMPLETE
    - Any child BLOCKED → Parent is BLOCKED
    - Any child ACTIVE → Parent is ACTIVE
    """

    PENDING = auto()  # Not yet started
    ACTIVE = auto()  # Currently being worked on
    COMPLETE = auto()  # Successfully finished
    BLOCKED = auto()  # Blocked by dependency or external factor
    CANCELLED = auto()  # Cancelled


# =============================================================================
# Intent: The Core Node
# =============================================================================


@dataclass(frozen=True)
class Intent:
    """
    Typed goal node in the intent graph.

    Laws:
    - Law 1 (Typed): Has exactly one IntentType
    - Law 2 (Tree): parent_id points to parent (or None for root)
    - Law 3 (Dependencies): depends_on forms a DAG

    Example:
        >>> root = Intent.create(
        ...     description="Implement Mark",
        ...     intent_type=IntentType.IMPLEMENT,
        ... )
        >>> child = Intent.create(
        ...     description="Write tests",
        ...     intent_type=IntentType.VERIFY,
        ...     parent_id=root.id,
        ... )
    """

    # Identity
    id: IntentId = field(default_factory=generate_intent_id)

    # Description
    description: str = ""

    # Law 1: Type
    intent_type: IntentType = IntentType.IMPLEMENT

    # Law 2: Tree structure
    parent_id: IntentId | None = None
    children_ids: tuple[IntentId, ...] = ()

    # Law 3: Dependencies
    depends_on: tuple[IntentId, ...] = ()

    # Law 4: Status
    status: IntentStatus = IntentStatus.PENDING

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Metadata
    priority: int = 0  # Higher = more important
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def create(
        cls,
        description: str,
        intent_type: IntentType = IntentType.IMPLEMENT,
        parent_id: IntentId | None = None,
        depends_on: tuple[IntentId, ...] = (),
        priority: int = 0,
        tags: tuple[str, ...] = (),
    ) -> Intent:
        """Create a new Intent."""
        return cls(
            description=description,
            intent_type=intent_type,
            parent_id=parent_id,
            depends_on=depends_on,
            priority=priority,
            tags=tags,
        )

    # =========================================================================
    # Status Transitions
    # =========================================================================

    def start(self) -> Intent:
        """Transition to ACTIVE status."""
        if self.status not in {IntentStatus.PENDING, IntentStatus.BLOCKED}:
            return self

        return Intent(
            id=self.id,
            description=self.description,
            intent_type=self.intent_type,
            parent_id=self.parent_id,
            children_ids=self.children_ids,
            depends_on=self.depends_on,
            status=IntentStatus.ACTIVE,
            created_at=self.created_at,
            started_at=datetime.now(),
            priority=self.priority,
            tags=self.tags,
            metadata=self.metadata,
        )

    def complete(self) -> Intent:
        """Transition to COMPLETE status."""
        if self.status not in {IntentStatus.ACTIVE, IntentStatus.PENDING}:
            return self

        return Intent(
            id=self.id,
            description=self.description,
            intent_type=self.intent_type,
            parent_id=self.parent_id,
            children_ids=self.children_ids,
            depends_on=self.depends_on,
            status=IntentStatus.COMPLETE,
            created_at=self.created_at,
            started_at=self.started_at or datetime.now(),
            completed_at=datetime.now(),
            priority=self.priority,
            tags=self.tags,
            metadata=self.metadata,
        )

    def block(self, reason: str = "") -> Intent:
        """Transition to BLOCKED status."""
        metadata = dict(self.metadata)
        if reason:
            metadata["block_reason"] = reason

        return Intent(
            id=self.id,
            description=self.description,
            intent_type=self.intent_type,
            parent_id=self.parent_id,
            children_ids=self.children_ids,
            depends_on=self.depends_on,
            status=IntentStatus.BLOCKED,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            priority=self.priority,
            tags=self.tags,
            metadata=metadata,
        )

    def cancel(self) -> Intent:
        """Transition to CANCELLED status."""
        return Intent(
            id=self.id,
            description=self.description,
            intent_type=self.intent_type,
            parent_id=self.parent_id,
            children_ids=self.children_ids,
            depends_on=self.depends_on,
            status=IntentStatus.CANCELLED,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=datetime.now(),
            priority=self.priority,
            tags=self.tags,
            metadata=self.metadata,
        )

    def with_child(self, child_id: IntentId) -> Intent:
        """Return Intent with added child."""
        if child_id in self.children_ids:
            return self

        return Intent(
            id=self.id,
            description=self.description,
            intent_type=self.intent_type,
            parent_id=self.parent_id,
            children_ids=self.children_ids + (child_id,),
            depends_on=self.depends_on,
            status=self.status,
            created_at=self.created_at,
            started_at=self.started_at,
            completed_at=self.completed_at,
            priority=self.priority,
            tags=self.tags,
            metadata=self.metadata,
        )

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def is_active(self) -> bool:
        """Check if Intent is active."""
        return self.status == IntentStatus.ACTIVE

    @property
    def is_complete(self) -> bool:
        """Check if Intent is complete."""
        return self.status == IntentStatus.COMPLETE

    @property
    def is_blocked(self) -> bool:
        """Check if Intent is blocked."""
        return self.status == IntentStatus.BLOCKED

    @property
    def is_terminal(self) -> bool:
        """Check if Intent is in terminal state."""
        return self.status in {IntentStatus.COMPLETE, IntentStatus.CANCELLED}

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "description": self.description,
            "intent_type": self.intent_type.value,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "children_ids": [str(cid) for cid in self.children_ids],
            "depends_on": [str(did) for did in self.depends_on],
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "priority": self.priority,
            "tags": list(self.tags),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Intent:
        """Create from dictionary."""
        return cls(
            id=IntentId(data["id"]),
            description=data.get("description", ""),
            intent_type=IntentType(data.get("intent_type", "implement")),
            parent_id=IntentId(data["parent_id"]) if data.get("parent_id") else None,
            children_ids=tuple(IntentId(cid) for cid in data.get("children_ids", [])),
            depends_on=tuple(IntentId(did) for did in data.get("depends_on", [])),
            status=IntentStatus[data.get("status", "PENDING")],
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            started_at=datetime.fromisoformat(data["started_at"])
            if data.get("started_at")
            else None,
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
            priority=data.get("priority", 0),
            tags=tuple(data.get("tags", [])),
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        desc = self.description[:30] + "..." if len(self.description) > 30 else self.description
        return (
            f"Intent(id={str(self.id)[:16]}..., "
            f"type={self.intent_type.value}, "
            f"status={self.status.name}, "
            f"desc='{desc}')"
        )


# =============================================================================
# IntentTree: The Graph Structure
# =============================================================================


class CyclicDependencyError(Exception):
    """Law 3: Dependencies form a DAG - cycle detected."""

    pass


@dataclass
class IntentTree:
    """
    Typed intent graph with dependencies.

    Laws:
    - Law 2 (Tree Structure): Parent-child is a tree
    - Law 3 (Dependencies): Dependencies form a DAG
    - Law 4 (Status Propagation): Parent status reflects children

    The IntentTree maintains the graph structure and provides
    traversal, querying, and status propagation.
    """

    _intents: dict[IntentId, Intent] = field(default_factory=dict)
    root_id: IntentId | None = None

    # =========================================================================
    # Modification
    # =========================================================================

    def add(self, intent: Intent) -> None:
        """
        Add an Intent to the tree.

        Law 2: Validates tree structure.
        Law 3: Validates no cycles in dependencies.
        """
        # Set as root if first intent and no parent
        if len(self._intents) == 0 and intent.parent_id is None:
            self.root_id = intent.id

        # Validate parent exists (if specified)
        if intent.parent_id is not None:
            if intent.parent_id not in self._intents:
                raise ValueError(f"Parent {intent.parent_id} not found")

            # Update parent's children
            parent = self._intents[intent.parent_id]
            self._intents[intent.parent_id] = parent.with_child(intent.id)

        # Validate dependencies exist and no cycles
        for dep_id in intent.depends_on:
            if dep_id not in self._intents:
                raise ValueError(f"Dependency {dep_id} not found")

        # Check for cycles
        if intent.depends_on:
            self._check_no_cycles(intent)

        self._intents[intent.id] = intent

    def _check_no_cycles(self, new_intent: Intent) -> None:
        """Law 3: Verify adding this intent doesn't create a cycle."""
        # Build dependency graph and check for cycles
        visited: set[IntentId] = set()
        stack: set[IntentId] = set()

        def has_cycle(intent_id: IntentId) -> bool:
            if intent_id in stack:
                return True
            if intent_id in visited:
                return False

            visited.add(intent_id)
            stack.add(intent_id)

            # Get dependencies
            if intent_id == new_intent.id:
                deps = new_intent.depends_on
            else:
                intent = self._intents.get(intent_id)
                deps = intent.depends_on if intent else ()

            for dep_id in deps:
                if has_cycle(dep_id):
                    return True

            stack.remove(intent_id)
            return False

        if has_cycle(new_intent.id):
            raise CyclicDependencyError(
                f"Adding intent {new_intent.id} would create a dependency cycle"
            )

    def get(self, intent_id: IntentId) -> Intent | None:
        """Get an Intent by ID."""
        return self._intents.get(intent_id)

    def update(self, intent: Intent) -> None:
        """Update an existing Intent."""
        self._intents[intent.id] = intent

    # =========================================================================
    # Querying
    # =========================================================================

    def children(self, intent_id: IntentId) -> list[Intent]:
        """Get all children of an Intent."""
        intent = self._intents.get(intent_id)
        if intent is None:
            return []

        return [self._intents[cid] for cid in intent.children_ids if cid in self._intents]

    def dependencies(self, intent_id: IntentId) -> list[Intent]:
        """Get all dependencies of an Intent."""
        intent = self._intents.get(intent_id)
        if intent is None:
            return []

        return [self._intents[did] for did in intent.depends_on if did in self._intents]

    def dependents(self, intent_id: IntentId) -> list[Intent]:
        """Get all Intents that depend on this one."""
        return [intent for intent in self._intents.values() if intent_id in intent.depends_on]

    def by_type(self, intent_type: IntentType) -> list[Intent]:
        """Get all Intents of a given type."""
        return [intent for intent in self._intents.values() if intent.intent_type == intent_type]

    def by_status(self, status: IntentStatus) -> list[Intent]:
        """Get all Intents with a given status."""
        return [intent for intent in self._intents.values() if intent.status == status]

    def ready_to_start(self) -> list[Intent]:
        """
        Get Intents that are ready to be started.

        An Intent is ready if:
        - Status is PENDING
        - All dependencies are COMPLETE
        """
        ready = []
        for intent in self._intents.values():
            if intent.status != IntentStatus.PENDING:
                continue

            # Check all dependencies are complete
            deps_complete = all(
                self._intents[did].status == IntentStatus.COMPLETE
                for did in intent.depends_on
                if did in self._intents
            )

            if deps_complete:
                ready.append(intent)

        return sorted(ready, key=lambda i: -i.priority)

    def blocked(self) -> list[Intent]:
        """Get all blocked Intents."""
        blocked = []
        for intent in self._intents.values():
            if intent.status == IntentStatus.BLOCKED:
                blocked.append(intent)
                continue

            # Also pending intents with incomplete deps
            if intent.status == IntentStatus.PENDING and intent.depends_on:
                has_incomplete_dep = any(
                    self._intents.get(did)
                    and self._intents[did].status not in {IntentStatus.COMPLETE}
                    for did in intent.depends_on
                )
                if has_incomplete_dep:
                    blocked.append(intent)

        return blocked

    # =========================================================================
    # Status Propagation (Law 4)
    # =========================================================================

    def propagate_status(self, intent_id: IntentId) -> None:
        """
        Propagate status changes up the tree.

        Law 4: Parent status reflects children.
        """
        intent = self._intents.get(intent_id)
        if intent is None or intent.parent_id is None:
            return

        parent = self._intents.get(intent.parent_id)
        if parent is None:
            return

        # Check all children's status
        children = self.children(parent.id)
        if not children:
            return

        all_complete = all(c.status == IntentStatus.COMPLETE for c in children)
        any_blocked = any(c.status == IntentStatus.BLOCKED for c in children)
        any_active = any(c.status == IntentStatus.ACTIVE for c in children)

        new_status = parent.status
        if all_complete:
            # All children complete, parent can complete
            new_status = IntentStatus.COMPLETE
        elif any_blocked:
            new_status = IntentStatus.BLOCKED
        elif any_active:
            new_status = IntentStatus.ACTIVE

        if new_status != parent.status:
            updated = Intent(
                id=parent.id,
                description=parent.description,
                intent_type=parent.intent_type,
                parent_id=parent.parent_id,
                children_ids=parent.children_ids,
                depends_on=parent.depends_on,
                status=new_status,
                created_at=parent.created_at,
                started_at=parent.started_at,
                completed_at=datetime.now()
                if new_status == IntentStatus.COMPLETE
                else parent.completed_at,
                priority=parent.priority,
                tags=parent.tags,
                metadata=parent.metadata,
            )
            self._intents[parent.id] = updated

            # Recurse upward
            self.propagate_status(parent.id)

    # =========================================================================
    # Traversal
    # =========================================================================

    def all(self) -> list[Intent]:
        """Get all Intents."""
        return list(self._intents.values())

    def leaves(self) -> list[Intent]:
        """Get all leaf Intents (no children)."""
        return [intent for intent in self._intents.values() if not intent.children_ids]

    def roots(self) -> list[Intent]:
        """Get all root Intents (no parent)."""
        return [intent for intent in self._intents.values() if intent.parent_id is None]

    # =========================================================================
    # Properties
    # =========================================================================

    def __len__(self) -> int:
        return len(self._intents)

    @property
    def root(self) -> Intent | None:
        """Get the root Intent."""
        if self.root_id is None:
            return None
        return self._intents.get(self.root_id)

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "root_id": str(self.root_id) if self.root_id else None,
            "intents": [intent.to_dict() for intent in self._intents.values()],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IntentTree:
        """Create from dictionary."""
        tree = cls()
        tree.root_id = IntentId(data["root_id"]) if data.get("root_id") else None

        for intent_data in data.get("intents", []):
            intent = Intent.from_dict(intent_data)
            tree._intents[intent.id] = intent

        return tree


# =============================================================================
# Global Store
# =============================================================================

_global_intent_tree: IntentTree | None = None


def get_intent_tree() -> IntentTree:
    """Get the global intent tree."""
    global _global_intent_tree
    if _global_intent_tree is None:
        _global_intent_tree = IntentTree()
    return _global_intent_tree


def reset_intent_tree() -> None:
    """Reset the global intent tree (for testing)."""
    global _global_intent_tree
    _global_intent_tree = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "IntentId",
    "generate_intent_id",
    # Types
    "IntentType",
    "IntentStatus",
    # Exceptions
    "CyclicDependencyError",
    # Core
    "Intent",
    "IntentTree",
    # Global
    "get_intent_tree",
    "reset_intent_tree",
]
