"""
LinearityMap: Resource class tracking for context management.

In linear type systems, resources must be used exactly once. Since Python
cannot enforce linearity at the type level, we use a runtime ledger to
track resource classes and enforce constraints during context compression.

Resource Classes:
- DROPPABLE: May be discarded (observations, intermediate computations)
- REQUIRED: Must flow to output (reasoning traces, decisions)
- PRESERVED: Must survive verbatim (focus fragments, user inputs)

Category Theory:
- Resources form a partial order: DROPPABLE < REQUIRED < PRESERVED
- Compression respects this order (never drop higher-priority resources)
- Monotonicity: Once promoted, a resource cannot be demoted

AGENTESE: self.stream.linearity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum, auto
from typing import Any, Callable, Generic, TypeVar
from uuid import uuid4

T = TypeVar("T")


class ResourceClass(IntEnum):
    """
    Resource classes ordered by importance.

    Higher values = higher priority = harder to drop.
    """

    DROPPABLE = 1  # May be discarded freely
    REQUIRED = 2  # Must flow to output
    PRESERVED = 3  # Must survive verbatim


@dataclass(frozen=True)
class ResourceTag:
    """
    A tag marking a resource with its class and provenance.

    Immutable to prevent accidental class demotion.
    """

    resource_id: str
    resource_class: ResourceClass
    created_at: datetime
    provenance: str  # Where this resource came from
    rationale: str  # Why it has this class


@dataclass
class TrackedResource(Generic[T]):
    """
    A resource with its linearity metadata.

    The resource itself is wrapped so we can track its lifecycle.
    """

    value: T
    tag: ResourceTag
    accessed_count: int = 0
    last_accessed: datetime | None = None

    def access(self) -> T:
        """Access the resource, updating tracking."""
        self.accessed_count += 1
        self.last_accessed = datetime.now(UTC)
        return self.value


@dataclass
class LinearityMap:
    """
    Runtime ledger for resource class tracking.

    Maintains a mapping from resource IDs to their classes and values.
    Enforces monotonicity (no demotions) and provides queries for
    compression decisions.

    Example:
        lm = LinearityMap()

        # Tag an observation (can be dropped)
        obs_id = lm.tag("user clicked button", ResourceClass.DROPPABLE, "ui_event")

        # Tag a decision (must be preserved in output)
        dec_id = lm.tag("chose option A", ResourceClass.REQUIRED, "decision")

        # Tag a focus fragment (must survive verbatim)
        focus_id = lm.tag("critical user instruction", ResourceClass.PRESERVED, "user_input")

        # Query what can be dropped
        droppable = lm.droppable()  # Returns observations

        # Promote if needed (one-way)
        lm.promote(obs_id, ResourceClass.REQUIRED, "became decision-relevant")
    """

    _resources: dict[str, TrackedResource[Any]] = field(default_factory=dict)
    _class_index: dict[ResourceClass, set[str]] = field(default_factory=dict)

    # Statistics
    _promotions: int = 0
    _drops: int = 0

    def __post_init__(self) -> None:
        """Initialize class index."""
        for rc in ResourceClass:
            if rc not in self._class_index:
                self._class_index[rc] = set()

    def tag(
        self,
        value: T,
        resource_class: ResourceClass,
        provenance: str,
        rationale: str = "",
        resource_id: str | None = None,
    ) -> str:
        """
        Tag a resource with its class.

        Returns the resource ID for future reference.
        """
        rid = resource_id or f"res_{uuid4().hex[:12]}"

        tag = ResourceTag(
            resource_id=rid,
            resource_class=resource_class,
            created_at=datetime.now(UTC),
            provenance=provenance,
            rationale=rationale or f"tagged as {resource_class.name}",
        )

        tracked = TrackedResource(value=value, tag=tag)
        self._resources[rid] = tracked
        self._class_index[resource_class].add(rid)

        return rid

    def get(self, resource_id: str) -> Any | None:
        """Get a resource by ID, tracking access."""
        tracked = self._resources.get(resource_id)
        if tracked is None:
            return None
        return tracked.access()

    def get_tag(self, resource_id: str) -> ResourceTag | None:
        """Get the tag for a resource."""
        tracked = self._resources.get(resource_id)
        return tracked.tag if tracked else None

    def get_class(self, resource_id: str) -> ResourceClass | None:
        """Get the class of a resource."""
        tag = self.get_tag(resource_id)
        return tag.resource_class if tag else None

    def promote(
        self,
        resource_id: str,
        new_class: ResourceClass,
        rationale: str,
    ) -> bool:
        """
        Promote a resource to a higher class.

        Enforces monotonicity: cannot demote resources.
        Returns True if promotion succeeded.
        """
        tracked = self._resources.get(resource_id)
        if tracked is None:
            return False

        current_class = tracked.tag.resource_class

        # Enforce monotonicity
        if new_class <= current_class:
            return False  # Cannot demote or stay same

        # Remove from old class index
        self._class_index[current_class].discard(resource_id)

        # Create new tag with promotion history
        new_tag = ResourceTag(
            resource_id=resource_id,
            resource_class=new_class,
            created_at=tracked.tag.created_at,  # Keep original creation time
            provenance=tracked.tag.provenance,
            rationale=f"{tracked.tag.rationale} → promoted: {rationale}",
        )

        # Update tracked resource
        self._resources[resource_id] = TrackedResource(
            value=tracked.value,
            tag=new_tag,
            accessed_count=tracked.accessed_count,
            last_accessed=tracked.last_accessed,
        )

        # Add to new class index
        self._class_index[new_class].add(resource_id)
        self._promotions += 1

        return True

    def drop(self, resource_id: str) -> bool:
        """
        Drop a resource if it's DROPPABLE.

        Returns True if dropped, False if protected or not found.
        """
        tracked = self._resources.get(resource_id)
        if tracked is None:
            return False

        if tracked.tag.resource_class != ResourceClass.DROPPABLE:
            return False  # Cannot drop non-droppable resources

        # Remove from indices
        self._class_index[ResourceClass.DROPPABLE].discard(resource_id)
        del self._resources[resource_id]
        self._drops += 1

        return True

    def drop_all_droppable(self) -> int:
        """
        Drop all DROPPABLE resources.

        Returns count of dropped resources.
        """
        droppable_ids = list(self._class_index[ResourceClass.DROPPABLE])
        dropped = 0

        for rid in droppable_ids:
            if self.drop(rid):
                dropped += 1

        return dropped

    # === Queries ===

    def droppable(self) -> list[str]:
        """Get IDs of all DROPPABLE resources."""
        return list(self._class_index[ResourceClass.DROPPABLE])

    def required(self) -> list[str]:
        """Get IDs of all REQUIRED resources."""
        return list(self._class_index[ResourceClass.REQUIRED])

    def preserved(self) -> list[str]:
        """Get IDs of all PRESERVED resources."""
        return list(self._class_index[ResourceClass.PRESERVED])

    def by_class(self, resource_class: ResourceClass) -> list[str]:
        """Get IDs of all resources of a given class."""
        return list(self._class_index.get(resource_class, set()))

    def all_ids(self) -> list[str]:
        """Get all resource IDs."""
        return list(self._resources.keys())

    def count(self) -> dict[str, int]:
        """Get counts by resource class."""
        return {
            "droppable": len(self._class_index[ResourceClass.DROPPABLE]),
            "required": len(self._class_index[ResourceClass.REQUIRED]),
            "preserved": len(self._class_index[ResourceClass.PRESERVED]),
            "total": len(self._resources),
        }

    # === Bulk Operations ===

    def tag_batch(
        self,
        items: list[tuple[T, ResourceClass, str]],
    ) -> list[str]:
        """
        Tag multiple resources at once.

        Each tuple is (value, class, provenance).
        Returns list of resource IDs.
        """
        return [self.tag(value, rc, prov) for value, rc, prov in items]

    def partition(self) -> dict[ResourceClass, list[Any]]:
        """
        Partition resources by class.

        Returns dict mapping class to list of values.
        """
        result: dict[ResourceClass, list[Any]] = {rc: [] for rc in ResourceClass}

        for rid, tracked in self._resources.items():
            result[tracked.tag.resource_class].append(tracked.value)

        return result

    # === Statistics ===

    @property
    def stats(self) -> dict[str, Any]:
        """Get statistics about the linearity map."""
        counts = self.count()
        return {
            **counts,
            "promotions": self._promotions,
            "drops": self._drops,
            "droppable_ratio": (
                counts["droppable"] / counts["total"] if counts["total"] > 0 else 0.0
            ),
        }

    # === Serialization ===

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for persistence."""
        return {
            "resources": {
                rid: {
                    "value": tracked.value,
                    "tag": {
                        "resource_id": tracked.tag.resource_id,
                        "resource_class": tracked.tag.resource_class.name,
                        "created_at": tracked.tag.created_at.isoformat(),
                        "provenance": tracked.tag.provenance,
                        "rationale": tracked.tag.rationale,
                    },
                    "accessed_count": tracked.accessed_count,
                    "last_accessed": (
                        tracked.last_accessed.isoformat()
                        if tracked.last_accessed
                        else None
                    ),
                }
                for rid, tracked in self._resources.items()
            },
            "stats": {
                "promotions": self._promotions,
                "drops": self._drops,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LinearityMap":
        """Deserialize from dict."""
        lm = cls()

        for rid, rdata in data.get("resources", {}).items():
            tag_data = rdata["tag"]
            tag = ResourceTag(
                resource_id=tag_data["resource_id"],
                resource_class=ResourceClass[tag_data["resource_class"]],
                created_at=datetime.fromisoformat(tag_data["created_at"]),
                provenance=tag_data["provenance"],
                rationale=tag_data["rationale"],
            )

            tracked = TrackedResource(
                value=rdata["value"],
                tag=tag,
                accessed_count=rdata.get("accessed_count", 0),
                last_accessed=(
                    datetime.fromisoformat(rdata["last_accessed"])
                    if rdata.get("last_accessed")
                    else None
                ),
            )

            lm._resources[rid] = tracked
            lm._class_index[tag.resource_class].add(rid)

        stats = data.get("stats", {})
        lm._promotions = stats.get("promotions", 0)
        lm._drops = stats.get("drops", 0)

        return lm


# === Classifier Functions ===


def classify_by_role(role: str) -> ResourceClass:
    """
    Classify a message by its role.

    User messages are PRESERVED (verbatim instructions).
    System messages are REQUIRED (reasoning context).
    Assistant messages are DROPPABLE by default (can be summarized).
    """
    match role.lower():
        case "user":
            return ResourceClass.PRESERVED
        case "system":
            return ResourceClass.REQUIRED
        case "assistant":
            return ResourceClass.DROPPABLE
        case _:
            return ResourceClass.DROPPABLE


def classify_by_content(content: str) -> ResourceClass:
    """
    Heuristic classification by content markers.

    Look for signals of importance in the text.
    """
    content_lower = content.lower()

    # PRESERVED markers (exact requirements, quotes, code)
    preserved_markers = [
        "must ",
        "required:",
        "critical:",
        "verbatim:",
        "exactly:",
        "```",  # Code blocks
        '"""',  # Docstrings
        "user said:",
    ]
    if any(marker in content_lower for marker in preserved_markers):
        return ResourceClass.PRESERVED

    # REQUIRED markers (decisions, conclusions)
    required_markers = [
        "therefore",
        "decision:",
        "conclusion:",
        "because",
        "the reason",
        "i will",
        "we should",
        "chosen approach:",
    ]
    if any(marker in content_lower for marker in required_markers):
        return ResourceClass.REQUIRED

    # Default to DROPPABLE
    return ResourceClass.DROPPABLE


def create_classifier(
    role_weight: float = 0.5,
    content_weight: float = 0.5,
) -> Callable[[str, str], ResourceClass]:
    """
    Create a composite classifier combining role and content heuristics.

    Returns function (role, content) -> ResourceClass.
    """

    def classify(role: str, content: str) -> ResourceClass:
        role_class = classify_by_role(role)
        content_class = classify_by_content(content)

        # Weighted max (higher class wins)
        role_score = role_class.value * role_weight
        content_score = content_class.value * content_weight

        # Take the higher classification
        if role_score >= content_score:
            return role_class
        return content_class

    return classify
