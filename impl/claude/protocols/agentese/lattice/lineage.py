"""
AGENTESE Concept Lineage - Genealogical Records

The Genealogical Constraint: No concept exists ex nihilo.
Every concept must declare its parents and justify its existence.

> "The lattice is not a cage—it is a family tree.
>  Every branch knows its roots."

Lineage Flow:
- Affordances flow DOWNWARD (children inherit parent capabilities)
- Constraints flow UPWARD (children must satisfy all parent requirements)
- The Meet finds common ancestors (where concepts converge)
- The Join finds common descendants (what could unify concepts)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.logos import Logos


@dataclass
class ConceptLineage:
    """
    Genealogical record for a concept.

    Every concept in AGENTESE must have a lineage record that tracks:
    - Its parents (extends) - REQUIRED, non-empty for all but 'concept' root
    - Its children (subsumes) - computed/updated as children are added
    - Its justification - why does this concept exist?
    - Its affordances - union of inherited + own affordances
    - Its constraints - intersection of parent constraints
    - Provenance - who created it and when
    """

    # Identity
    handle: str  # e.g., "concept.justice.procedural"

    # Lineage (the family tree)
    extends: list[str]  # Parent concepts (REQUIRED for all but 'concept')
    subsumes: list[str] = field(default_factory=list)  # Child concepts

    # Justification
    justification: str = ""  # Why does this concept exist?

    # Inherited properties
    affordances: set[str] = field(default_factory=set)  # Union of parent affordances
    constraints: set[str] = field(default_factory=set)  # Intersection of constraints

    # Provenance
    created_by: str = "unknown"  # Observer who created it
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Metadata
    domain: str = "general"  # Domain classification
    depth: int = 0  # Distance from 'concept' root (0 = root itself)

    def __post_init__(self) -> None:
        """Ensure extends is always a list."""
        if isinstance(self.extends, tuple):
            self.extends = list(self.extends)
        if isinstance(self.affordances, (list, tuple)):
            self.affordances = set(self.affordances)
        if isinstance(self.constraints, (list, tuple)):
            self.constraints = set(self.constraints)

    @property
    def is_root(self) -> bool:
        """Check if this is the root 'concept' node."""
        return self.handle == "concept" or not self.extends

    @property
    def parent_count(self) -> int:
        """Number of parent concepts."""
        return len(self.extends)

    @property
    def child_count(self) -> int:
        """Number of child concepts."""
        return len(self.subsumes)

    def add_child(self, child_handle: str) -> None:
        """Register a child concept."""
        if child_handle not in self.subsumes:
            self.subsumes.append(child_handle)

    def remove_child(self, child_handle: str) -> None:
        """Unregister a child concept."""
        if child_handle in self.subsumes:
            self.subsumes.remove(child_handle)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "handle": self.handle,
            "extends": self.extends,
            "subsumes": self.subsumes,
            "justification": self.justification,
            "affordances": list(self.affordances),
            "constraints": list(self.constraints),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "domain": self.domain,
            "depth": self.depth,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConceptLineage":
        """Deserialize from dictionary."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(UTC)

        return cls(
            handle=data["handle"],
            extends=data.get("extends", []),
            subsumes=data.get("subsumes", []),
            justification=data.get("justification", ""),
            affordances=set(data.get("affordances", [])),
            constraints=set(data.get("constraints", [])),
            created_by=data.get("created_by", "unknown"),
            created_at=created_at,
            domain=data.get("domain", "general"),
            depth=data.get("depth", 0),
        )


# === Inheritance Computation ===


async def compute_affordances(
    logos: "Logos",
    parents: list[str],
    observer: "Umwelt[Any, Any]",
) -> set[str]:
    """
    Compute inherited affordances from parents.

    Affordances are ADDITIVE (union): children get all parent capabilities.

    Args:
        logos: Logos resolver for looking up parent nodes
        parents: List of parent concept handles
        observer: Observer context for affordance lookup

    Returns:
        Union of all parent affordances
    """
    from protocols.agentese.node import AgentMeta

    affordances: set[str] = set()

    for parent_handle in parents:
        try:
            parent = logos.resolve(parent_handle, observer)
            # Get affordances for observer
            meta = AgentMeta(
                name=getattr(observer.dna, "name", "unknown"),
                archetype=getattr(observer.dna, "archetype", "default"),
                capabilities=getattr(observer.dna, "capabilities", ()),
            )
            parent_affordances = parent.affordances(meta)
            affordances |= set(parent_affordances)
        except Exception:
            # Parent not found - skip (will be caught by checker)
            pass

    return affordances


async def compute_constraints(
    logos: "Logos",
    parents: list[str],
    observer: "Umwelt[Any, Any]",
) -> set[str]:
    """
    Compute inherited constraints from parents.

    Constraints are RESTRICTIVE (intersection): children must satisfy ALL.

    Args:
        logos: Logos resolver for looking up parent nodes
        parents: List of parent concept handles
        observer: Observer context

    Returns:
        Intersection of all parent constraints
    """
    if not parents:
        return set()

    constraints: set[str] | None = None

    for parent_handle in parents:
        try:
            parent = logos.resolve(parent_handle, observer)
            parent_constraints = set(getattr(parent, "constraints", []))

            if constraints is None:
                constraints = parent_constraints
            else:
                constraints &= parent_constraints
        except Exception:
            # Parent not found - skip
            pass

    return constraints or set()


def compute_depth(parent_lineages: list[ConceptLineage]) -> int:
    """
    Compute depth from parent lineages.

    Depth = max(parent depths) + 1
    Root has depth 0.
    """
    if not parent_lineages:
        return 0
    return max(p.depth for p in parent_lineages) + 1


# === Root Concept Bootstrap ===


def create_root_lineage() -> ConceptLineage:
    """
    Create the root 'concept' lineage.

    The root is the only concept allowed to have no parents.
    It is the Adam of the conceptual family tree.
    """
    return ConceptLineage(
        handle="concept",
        extends=[],  # Root has no parents
        subsumes=[],  # Children will be added
        justification="The primordial concept from which all others derive.",
        affordances={"manifest", "define", "relate", "refine", "witness"},
        constraints=set(),  # No constraints at root
        created_by="system",
        created_at=datetime.now(UTC),
        domain="meta",
        depth=0,
    )


# === Standard Parent Concepts ===


STANDARD_PARENTS = {
    "concept": create_root_lineage(),
    "concept.entity": ConceptLineage(
        handle="concept.entity",
        extends=["concept"],
        justification="Base concept for all things that exist.",
        affordances={"manifest", "define", "relate", "refine", "witness", "identify"},
        constraints=set(),
        domain="ontology",
        depth=1,
    ),
    "concept.process": ConceptLineage(
        handle="concept.process",
        extends=["concept"],
        justification="Base concept for all procedures and transformations.",
        affordances={
            "manifest",
            "define",
            "relate",
            "refine",
            "witness",
            "execute",
            "compose",
        },
        constraints={"has_input", "has_output"},
        domain="ontology",
        depth=1,
    ),
    "concept.relation": ConceptLineage(
        handle="concept.relation",
        extends=["concept"],
        justification="Base concept for all relationships between entities.",
        affordances={
            "manifest",
            "define",
            "relate",
            "refine",
            "witness",
            "connect",
            "traverse",
        },
        constraints={"has_source", "has_target"},
        domain="ontology",
        depth=1,
    ),
    "concept.property": ConceptLineage(
        handle="concept.property",
        extends=["concept"],
        justification="Base concept for all attributes and qualities.",
        affordances={"manifest", "define", "relate", "refine", "witness", "measure"},
        constraints={"has_domain"},
        domain="ontology",
        depth=1,
    ),
}
