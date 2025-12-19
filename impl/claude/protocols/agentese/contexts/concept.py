"""
AGENTESE Concept Context Resolver

The Abstract: platonics, definitions, logic, compressed wisdom.

concept.* handles resolve to abstract concepts that can be:
- Refined via dialectical challenge
- Related to other concepts
- Defined (autopoiesis) with REQUIRED lineage

Principle Alignment: Generative (compressed wisdom)

The Genealogical Constraint: No concept exists ex nihilo.
Every concept must declare its parents and justify its existence.

> "No concept born without parents. No orphan in the family tree."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from ..exceptions import TastefulnessError
from ..lattice.checker import ConsistencyResult, get_lattice_checker
from ..lattice.errors import LatticeError, LineageError
from ..lattice.lineage import (
    STANDARD_PARENTS,
    ConceptLineage,
    compute_affordances,
    compute_constraints,
    compute_depth,
)
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..renderings import PhilosopherRendering, ScientificRendering

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

    from ..logos import Logos


# === Concept Affordances by Archetype ===

CONCEPT_ARCHETYPE_AFFORDANCES: dict[str, tuple[str, ...]] = {
    "philosopher": ("refine", "dialectic", "synthesize", "analyze", "critique"),
    "scientist": ("hypothesize", "validate", "relate", "classify"),
    "engineer": ("implement", "decompose", "optimize", "validate"),
    "artist": ("interpret", "express", "transform", "inspire"),
    "teacher": ("explain", "simplify", "exemplify", "assess"),
    "default": ("relate",),
}


# === Concept Node ===


@dataclass
class ConceptNode(BaseLogosNode):
    """
    A node in the concept.* context.

    Represents an abstract concept that can be:
    - Perceived (manifest)
    - Refined via dialectic (refine)
    - Related to other concepts (relate)
    - Defined/created (define) with REQUIRED lineage

    The Genealogical Constraint:
    Every concept (except 'concept' root) must have at least one parent.

    Examples:
        concept.justice - The abstract idea of justice
        concept.recursion - A programming concept
        concept.entropy - A physics/information concept
    """

    _handle: str
    name: str = ""
    definition: str = ""
    domain: str = "general"
    examples: tuple[str, ...] = ()
    related_concepts: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    # Lineage tracking (Genealogical Constraint)
    lineage: ConceptLineage | None = None

    # Integration points
    _registry: Any = None  # L-gent for concept lookup
    _grammarian: Any = None  # G-gent for validation
    _logos: "Logos | None" = None  # Logos resolver for lineage validation

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self._handle.split(".")[-1] if "." in self._handle else self._handle

    @property
    def extends(self) -> list[str]:
        """Get parent concepts from lineage."""
        if self.lineage:
            return self.lineage.extends
        return []

    @property
    def subsumes(self) -> list[str]:
        """Get child concepts from lineage."""
        if self.lineage:
            return self.lineage.subsumes
        return []

    @property
    def has_lineage(self) -> bool:
        """Check if this concept has lineage information."""
        return self.lineage is not None

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances for concepts."""
        base_extra = ("define", "relate")
        archetype_extra = CONCEPT_ARCHETYPE_AFFORDANCES.get(archetype, ())
        return base_extra + archetype_extra

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Perceive the concept.

        Different archetypes receive different presentations
        of the same concept. Uses polymorphic renderings.
        """
        meta = self._umwelt_to_meta(observer)

        match meta.archetype:
            case "philosopher":
                # Generate dialectical structure for philosopher
                thesis = self.definition or f"The concept of {self.name}"
                antithesis = (
                    f"Against {self.name}: The concept may be an illusion or mere convention."
                )
                synthesis = f"Beyond the opposition: {self.name} must be understood as both constructed and real."

                return PhilosopherRendering(
                    concept=self.name,
                    definition=self.definition,
                    essence=f"The essence of {self.name} lies in its conditions of possibility.",
                    thesis=thesis,
                    antithesis=antithesis,
                    synthesis=synthesis,
                    related_concepts=self.related_concepts,
                )
            case "scientist":
                return ScientificRendering(
                    entity=self.name,
                    measurements={},  # Concepts are not directly measurable
                    observations=self.examples,
                    hypotheses=(
                        f"H1: {self.name} correlates with observable phenomenon X",
                        f"H2: {self.name} can be operationalized as measurement Y",
                    ),
                    confidence=0.5,  # Theoretical concepts start at 50%
                )
            case "engineer":
                return BasicRendering(
                    summary=f"Concept: {self.name}",
                    content=self._engineering_rendering(),
                    metadata={
                        "domain": self.domain,
                        "implementation_status": "abstract",
                    },
                )
            case _:
                return BasicRendering(
                    summary=f"Concept: {self.name}",
                    content=self.definition or f"The concept of {self.name}.",
                    metadata={
                        "domain": self.domain,
                        "examples": list(self.examples),
                        "related": list(self.related_concepts),
                    },
                )

    def _philosophical_rendering(self) -> str:
        """Render concept for philosophical inquiry."""
        lines = [
            f"**{self.name}**",
            "",
            self.definition or "A concept requiring definition.",
            "",
            "Questions for dialectical inquiry:",
            f"  - What is the essence of {self.name}?",
            "  - What are the necessary and sufficient conditions?",
            f"  - How does {self.name} relate to its opposites?",
        ]
        if self.related_concepts:
            lines.append(f"\nRelated concepts: {', '.join(self.related_concepts)}")
        return "\n".join(lines)

    def _scientific_rendering(self) -> str:
        """Render concept for scientific analysis."""
        lines = [
            f"**{self.name}** (Domain: {self.domain})",
            "",
            self.definition or "A concept requiring operationalization.",
            "",
            "Scientific considerations:",
            f"  - How can {self.name} be measured?",
            "  - What predictions does it enable?",
            "  - What falsifiable claims does it entail?",
        ]
        if self.examples:
            lines.append(f"\nExamples: {', '.join(self.examples)}")
        return "\n".join(lines)

    def _engineering_rendering(self) -> str:
        """Render concept for engineering implementation."""
        lines = [
            f"**{self.name}** (Domain: {self.domain})",
            "",
            self.definition or "A concept requiring implementation.",
            "",
            "Implementation considerations:",
            "  - What are the core operations?",
            "  - What are the invariants?",
            "  - What are the edge cases?",
        ]
        return "\n".join(lines)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle concept-specific aspects."""
        match aspect:
            case "refine":
                return await self._refine(observer, **kwargs)
            case "dialectic":
                return await self._dialectic(observer, **kwargs)
            case "relate":
                return await self._relate(observer, **kwargs)
            case "define":
                return await self._define_child(observer, **kwargs)
            case "synthesize":
                return await self._synthesize(observer, **kwargs)
            case "analyze":
                return await self._analyze(observer, **kwargs)
            case "critique":
                return await self._critique(observer, **kwargs)
            case "hypothesize":
                return await self._hypothesize(observer, **kwargs)
            case "validate":
                return await self._validate(observer, **kwargs)
            case "implement":
                return await self._implement(observer, **kwargs)
            case "decompose":
                return await self._decompose(observer, **kwargs)
            case "explain":
                return await self._explain(observer, **kwargs)
            case "simplify":
                return await self._simplify(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _refine(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Dialectical refinement of the concept.

        Think harder about the definition through challenge.
        """
        challenge = kwargs.get("challenge", "What are its necessary conditions?")

        # Generate a refined view through dialectical challenge
        refined_definition = (
            f"{self.definition}\n\n"
            f"Challenged by: {challenge}\n\n"
            f"The concept of {self.name} must be understood in relation to "
            f"its conditions of possibility and its limitations."
        )

        return {
            "original": self.definition,
            "challenge": challenge,
            "refined": refined_definition,
            "status": "refined",
            "note": "Full dialectical refinement requires Ψ-gent integration",
        }

    async def _dialectic(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Engage in dialectical reasoning about the concept."""
        thesis = kwargs.get("thesis", self.definition)

        # Generate antithesis
        antithesis = f"Against {self.name}: The concept may be an illusion or mere convention."

        # Gesture toward synthesis
        synthesis = (
            f"Beyond the opposition: {self.name} must be understood "
            f"as both constructed and real, both universal and particular."
        )

        return {
            "thesis": thesis,
            "antithesis": antithesis,
            "synthesis": synthesis,
            "status": "dialectic complete",
        }

    async def _relate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Find relations to other concepts."""
        target = kwargs.get("target")

        relations = list(self.related_concepts)

        if target:
            # Add relation if not already present
            if target not in relations:
                relations.append(target)
            return {
                "source": self.name,
                "target": target,
                "relation": f"{self.name} is related to {target}",
                "all_relations": relations,
            }

        return {
            "concept": self.name,
            "related": relations,
            "note": "Use target= to explore specific relations",
        }

    async def _define_child(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> "ConceptNode":
        """
        Create a child concept (autopoiesis) with REQUIRED lineage.

        The Genealogical Constraint: No concept exists ex nihilo.
        Every concept must declare its parents and justify its existence.

        Args (via kwargs):
            name: Name of the new concept (REQUIRED)
            definition: Definition text (REQUIRED for non-exploratory concepts)
            extends: List of parent concept handles (defaults to [self._handle])
            justification: Why this concept needs to exist
            domain: Domain classification (defaults to parent's domain)

        Returns:
            ConceptNode with lineage information

        Raises:
            LineageError: If no parents provided
            LatticeError: If lattice position is invalid
            TastefulnessError: If definition is missing
        """
        name = kwargs.get("name", "unnamed")
        definition = kwargs.get("definition", "")
        domain = kwargs.get("domain", self.domain)
        justification = kwargs.get("justification", "")

        # Get parent concepts - default to this concept
        extends = kwargs.get("extends", [self._handle])
        if isinstance(extends, str):
            extends = [extends]

        # Ensure at least one parent (Genealogical Constraint)
        if not extends:
            extends = [self._handle]  # Default to current concept as parent

        child_handle = f"concept.{name}"

        # Get the lattice checker
        checker = get_lattice_checker(logos=self._logos)

        # Check lattice position
        result = await checker.check_position(
            new_handle=child_handle,
            parents=extends,
        )

        if not result.valid:
            if result.violation_type == "parent_missing":
                raise LineageError(
                    f"Cannot create '{name}': parent concepts do not exist",
                    handle=child_handle,
                    missing_parents=[p for p in extends if p not in STANDARD_PARENTS],
                )
            elif result.violation_type == "cycle":
                raise LatticeError(
                    f"Cannot create '{name}': would create cycle",
                    handle=child_handle,
                    violation_type="cycle",
                    cycle_path=result.cycle_path,
                )
            elif result.violation_type == "affordance_conflict":
                raise LatticeError(
                    f"Cannot create '{name}': parent affordances conflict",
                    handle=child_handle,
                    violation_type="affordance_conflict",
                    conflicting_affordances=result.conflicting_affordances,
                )
            else:
                raise LatticeError(
                    f"Cannot create '{name}': {result.reason}",
                    handle=child_handle,
                )

        # Validate against Tasteful principle if G-gent available
        if self._grammarian and not definition:
            raise TastefulnessError(
                f"Cannot define {name} without a definition",
                validation_errors=["Definition required"],
            )

        # Compute inherited affordances and constraints
        inherited_affordances: set[str] = set()
        inherited_constraints: set[str] = set()
        parent_lineages: list[ConceptLineage] = []

        for parent_handle in extends:
            parent_lineage = checker.get_lineage(parent_handle)
            if parent_lineage:
                inherited_affordances |= parent_lineage.affordances
                if inherited_constraints:
                    inherited_constraints &= parent_lineage.constraints
                else:
                    inherited_constraints = parent_lineage.constraints.copy()
                parent_lineages.append(parent_lineage)

        # Create lineage record
        lineage = ConceptLineage(
            handle=child_handle,
            extends=extends,
            subsumes=[],
            justification=justification,
            affordances=inherited_affordances,
            constraints=inherited_constraints,
            created_by=getattr(observer.dna, "name", "unknown"),
            created_at=datetime.now(UTC),
            domain=domain,
            depth=compute_depth(parent_lineages),
        )

        # Register lineage with checker
        checker.register_lineage(lineage)

        # Update parent lineages to include this child
        for parent_handle in extends:
            parent_lineage = checker.get_lineage(parent_handle)
            if parent_lineage:
                parent_lineage.add_child(child_handle)

        # Create the concept node with lineage
        child = ConceptNode(
            _handle=child_handle,
            name=name,
            definition=definition,
            domain=domain,
            related_concepts=tuple(extends),
            lineage=lineage,
            _registry=self._registry,
            _grammarian=self._grammarian,
            _logos=self._logos,
        )

        return child

    async def _synthesize(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Synthesize this concept with another."""
        other = kwargs.get("other", "")

        synthesis = (
            f"Synthesis of {self.name} and {other}: "
            f"A new concept that preserves the truth of both "
            f"while transcending their limitations."
        )

        return {
            "source": self.name,
            "other": other,
            "synthesis": synthesis,
        }

    async def _analyze(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Analyze the concept's structure."""
        return {
            "concept": self.name,
            "domain": self.domain,
            "definition_length": len(self.definition),
            "example_count": len(self.examples),
            "relation_count": len(self.related_concepts),
            "analysis": f"{self.name} is a {self.domain} concept with {len(self.examples)} examples.",
        }

    async def _critique(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a critique of the concept."""
        return {
            "concept": self.name,
            "critique": [
                f"Is {self.name} well-defined?",
                f"Does {self.name} conflate distinct phenomena?",
                f"What are the ideological presuppositions of {self.name}?",
                f"How has {self.name} been historically constructed?",
            ],
        }

    async def _hypothesize(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate hypotheses about the concept."""
        return {
            "concept": self.name,
            "hypotheses": [
                f"H1: {self.name} correlates with observable phenomenon X",
                f"H2: {self.name} can be operationalized as measurement Y",
                f"H3: {self.name} predicts outcome Z under conditions C",
            ],
            "note": "Full hypothesis generation requires B-gent integration",
        }

    async def _validate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Validate the concept definition."""
        criteria = kwargs.get("criteria", [])

        validation = {
            "has_definition": bool(self.definition),
            "has_examples": len(self.examples) > 0,
            "has_relations": len(self.related_concepts) > 0,
            "domain_specified": self.domain != "general",
        }

        return {
            "concept": self.name,
            "validation": validation,
            "valid": all(validation.values()),
            "criteria_checked": criteria,
        }

    async def _implement(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Describe how to implement the concept."""
        language = kwargs.get("language", "python")

        return {
            "concept": self.name,
            "language": language,
            "implementation_sketch": f"""
# Implementation of {self.name}

class {self.name.title().replace(" ", "")}:
    \"\"\"
    {self.definition or f"Implementation of the {self.name} concept."}
    \"\"\"

    def __init__(self):
        pass

    # TODO: Implement core operations
            """.strip(),
            "note": "Full implementation requires J-gent code generation",
        }

    async def _decompose(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Decompose the concept into components."""
        return {
            "concept": self.name,
            "components": [
                f"{self.name}.core - The essential definition",
                f"{self.name}.boundary - Where the concept ends",
                f"{self.name}.operations - What you can do with it",
                f"{self.name}.invariants - What must remain true",
            ],
        }

    async def _explain(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Explain the concept simply."""
        level = kwargs.get("level", "basic")

        explanations = {
            "basic": f"{self.name} is: {self.definition or 'a concept that needs to be understood.'}",
            "intermediate": f"{self.name}: {self.definition}\n\nExamples: {', '.join(self.examples) if self.examples else 'None provided.'}",
            "advanced": self._philosophical_rendering(),
        }

        return {
            "concept": self.name,
            "level": level,
            "explanation": explanations.get(level, explanations["basic"]),
        }

    async def _simplify(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Simplify the concept for accessibility."""
        return {
            "concept": self.name,
            "simple_definition": self.definition.split(".")[0] + "."
            if self.definition
            else f"{self.name} is an idea.",
            "analogy": f"{self.name} is like... (analogy needed)",
            "note": "Full simplification requires Ψ-gent metaphor generation",
        }


# === Concept Context Resolver ===


@dataclass
class ConceptContextResolver:
    """
    Resolver for concept.* context.

    Resolution strategy:
    1. Check registry (known concepts)
    2. Create exploratory concept node
    """

    registry: Any = None  # L-gent for concept lookup
    grammarian: Any = None  # G-gent for validation

    # Cache of resolved concepts
    _cache: dict[str, ConceptNode] = field(default_factory=dict)

    def resolve(self, holon: str, rest: list[str]) -> ConceptNode:
        """
        Resolve a concept.* path to a ConceptNode.

        Args:
            holon: The concept name (e.g., "justice" from "concept.justice")
            rest: Additional path components

        Returns:
            Resolved ConceptNode
        """
        handle = f"concept.{holon}"

        # Check cache
        if handle in self._cache:
            return self._cache[handle]

        # Special-case: N-Phase prompt compiler handles
        if holon == "nphase":
            node = ConceptNode(
                _handle=handle,
                name="nphase",
                domain="compiler",
                definition="N-Phase prompt compiler (compile/validate/template/bootstrap)",
                examples=("concept.nphase.compile", "concept.nphase.validate"),
                related_concepts=("forest", "do", "agent-town"),
                _registry=self.registry,
                _grammarian=self.grammarian,
            )
            self._cache[handle] = node
            return node

        # Check registry if available
        if self.registry:
            try:
                entry = self.registry.get(handle)
                if entry:
                    node = self._hydrate_from_registry(entry, handle)
                    self._cache[handle] = node
                    return node
            except Exception:
                pass

        # Create placeholder concept for exploration
        node = ConceptNode(
            _handle=handle,
            name=holon,
            domain="general",
            _registry=self.registry,
            _grammarian=self.grammarian,
        )
        self._cache[handle] = node
        return node

    def _hydrate_from_registry(self, entry: Any, handle: str) -> ConceptNode:
        """Hydrate a ConceptNode from a registry entry."""
        return ConceptNode(
            _handle=handle,
            name=getattr(entry, "name", handle.split(".")[-1]),
            definition=getattr(entry, "description", ""),
            domain=getattr(entry, "domain", "general"),
            examples=tuple(getattr(entry, "examples", [])),
            related_concepts=tuple(getattr(entry, "related", [])),
            _registry=self.registry,
            _grammarian=self.grammarian,
        )

    def register(self, handle: str, node: ConceptNode) -> None:
        """Register a concept in the cache."""
        self._cache[handle] = node

    def list_handles(self, prefix: str = "concept.") -> list[str]:
        """List cached handles."""
        return [h for h in self._cache if h.startswith(prefix)]


# === Factory Functions ===


def create_concept_resolver(
    registry: Any = None,
    grammarian: Any = None,
) -> ConceptContextResolver:
    """Create a ConceptContextResolver with optional integrations."""
    return ConceptContextResolver(registry=registry, grammarian=grammarian)


def create_concept_node(
    name: str,
    definition: str = "",
    domain: str = "general",
    examples: list[str] | None = None,
    related: list[str] | None = None,
) -> ConceptNode:
    """Create a ConceptNode with standard configuration."""
    return ConceptNode(
        _handle=f"concept.{name}",
        name=name,
        definition=definition,
        domain=domain,
        examples=tuple(examples or []),
        related_concepts=tuple(related or []),
    )


# === Standalone define_concept Function ===


async def define_concept(
    logos: "Logos",
    handle: str,
    observer: "Umwelt[Any, Any]",
    spec: str,
    extends: list[str],
    subsumes: list[str] | None = None,
    justification: str = "",
) -> ConceptNode:
    """
    Create a new concept with required lineage.

    AGENTESE: concept.*.define

    The Genealogical Constraint: No concept exists ex nihilo.
    Every concept must declare its parents and justify its existence.

    Args:
        logos: The Logos resolver
        handle: The AGENTESE handle (e.g., "concept.justice.procedural")
        observer: The observer creating this concept
        spec: The concept definition/specification
        extends: Parent concept handles (REQUIRED, non-empty)
        subsumes: Optional child concept handles
        justification: Why does this concept need to exist?

    Returns:
        The newly created ConceptNode with lineage

    Raises:
        LineageError: If extends is empty (ex nihilo creation)
        LineageError: If parent concepts don't exist
        LatticeError: If position would create cycle or conflicts
    """
    from ..exceptions import PathNotFoundError

    # 1. Validate lineage (HARD REQUIREMENT)
    if not extends:
        raise LineageError(
            f"Cannot create '{handle}': concepts cannot exist ex nihilo",
            handle=handle,
        )

    # 2. Validate parents exist
    missing_parents = []
    for parent in extends:
        # Check standard parents first
        if parent in STANDARD_PARENTS:
            continue
        # Then check Logos
        try:
            logos.resolve(parent, observer)
        except PathNotFoundError:
            missing_parents.append(parent)

    if missing_parents:
        raise LineageError(
            f"Cannot create '{handle}': parent concepts do not exist",
            handle=handle,
            missing_parents=missing_parents,
        )

    # 3. L-gent lattice consistency check
    checker = get_lattice_checker(logos=logos)
    result = await checker.check_position(
        new_handle=handle,
        parents=extends,
        children=subsumes or [],
    )

    if not result.valid:
        if result.violation_type == "cycle":
            raise LatticeError(
                f"Cannot create '{handle}': would create cycle",
                handle=handle,
                violation_type="cycle",
                cycle_path=result.cycle_path,
            )
        elif result.violation_type == "affordance_conflict":
            raise LatticeError(
                f"Cannot create '{handle}': parent affordances conflict",
                handle=handle,
                violation_type="affordance_conflict",
                conflicting_affordances=result.conflicting_affordances,
            )
        else:
            raise LatticeError(
                f"Cannot create '{handle}': {result.reason}",
                handle=handle,
            )

    # 4. Compute inherited affordances and constraints
    inherited_affordances: set[str] = set()
    inherited_constraints: set[str] | None = None
    parent_lineages: list[ConceptLineage] = []

    for parent_handle in extends:
        parent_lineage = checker.get_lineage(parent_handle)
        if parent_lineage:
            inherited_affordances |= parent_lineage.affordances
            if inherited_constraints is None:
                inherited_constraints = parent_lineage.constraints.copy()
            else:
                inherited_constraints &= parent_lineage.constraints
            parent_lineages.append(parent_lineage)

    # 5. Create lineage record
    lineage = ConceptLineage(
        handle=handle,
        extends=extends,
        subsumes=subsumes or [],
        justification=justification,
        affordances=inherited_affordances,
        constraints=inherited_constraints or set(),
        created_by=getattr(observer.dna, "name", "unknown"),
        created_at=datetime.now(UTC),
        domain=_extract_domain(handle),
        depth=compute_depth(parent_lineages),
    )

    # 6. Register lineage
    checker.register_lineage(lineage)

    # 7. Update parent lineages
    for parent_handle in extends:
        parent_lineage = checker.get_lineage(parent_handle)
        if parent_lineage:
            parent_lineage.add_child(handle)

    # 8. Extract name from handle
    name = handle.split(".")[-1] if "." in handle else handle

    # 9. Create and return ConceptNode
    node = ConceptNode(
        _handle=handle,
        name=name,
        definition=spec,
        domain=_extract_domain(handle),
        lineage=lineage,
        _logos=logos,
    )

    # 10. Register in Logos cache
    logos._cache[handle] = node

    return node


def _extract_domain(handle: str) -> str:
    """Extract domain from handle path."""
    parts = handle.split(".")
    if len(parts) >= 3:
        # concept.justice.procedural -> justice
        return parts[1]
    elif len(parts) == 2:
        # concept.justice -> general
        return "general"
    return "general"


# === Lattice Visualization Helpers ===


def get_concept_tree(
    root_handle: str = "concept",
    max_depth: int = 10,
) -> dict[str, Any]:
    """
    Get the concept tree starting from a root.

    Args:
        root_handle: Starting concept handle
        max_depth: Maximum traversal depth

    Returns:
        Nested dictionary representing the tree structure
    """
    checker = get_lattice_checker()

    def _build_tree(handle: str, depth: int) -> dict[str, Any]:
        if depth >= max_depth:
            return {"handle": handle, "truncated": True}

        lineage = checker.get_lineage(handle)
        if not lineage:
            return {"handle": handle, "children": []}

        return {
            "handle": handle,
            "depth": lineage.depth,
            "affordances": list(lineage.affordances),
            "constraints": list(lineage.constraints),
            "children": [_build_tree(child, depth + 1) for child in lineage.subsumes],
        }

    return _build_tree(root_handle, 0)


def render_concept_lattice(
    root_handle: str = "concept",
    max_depth: int = 10,
) -> str:
    """
    Render the concept lattice as ASCII tree.

    Args:
        root_handle: Starting concept handle
        max_depth: Maximum traversal depth

    Returns:
        ASCII representation of the tree
    """
    lines = ["CONCEPT LATTICE", "=" * 40, ""]
    checker = get_lattice_checker()

    stats = {"nodes": 0, "edges": 0, "max_depth": 0, "orphans": 0}

    def _render_node(handle: str, prefix: str, is_last: bool, depth: int) -> None:
        if depth >= max_depth:
            return

        lineage = checker.get_lineage(handle)
        if not lineage:
            stats["orphans"] += 1
            return

        stats["nodes"] += 1
        stats["max_depth"] = max(stats["max_depth"], lineage.depth)

        # Render this node
        connector = "└── " if is_last else "├── "
        name = handle.split(".")[-1] if "." in handle else handle
        lines.append(f"{prefix}{connector}{name}")

        # Render children
        children = lineage.subsumes
        stats["edges"] += len(children)

        for i, child in enumerate(children):
            is_child_last = i == len(children) - 1
            child_prefix = prefix + ("    " if is_last else "│   ")
            _render_node(child, child_prefix, is_child_last, depth + 1)

    # Start with root
    root_lineage = checker.get_lineage(root_handle)
    if root_lineage:
        name = root_handle.split(".")[-1] if "." in root_handle else root_handle
        lines.append(f"{name} (Top)")
        for i, child in enumerate(root_lineage.subsumes):
            _render_node(child, "", i == len(root_lineage.subsumes) - 1, 1)
    else:
        lines.append(f"{root_handle} (not found)")

    # Stats
    lines.append("")
    lines.append("=" * 40)
    lines.append(
        f"Nodes: {stats['nodes']} | "
        f"Edges: {stats['edges']} | "
        f"Depth: {stats['max_depth']} | "
        f"Orphans: {stats['orphans']}"
    )
    lines.append("=" * 40)

    return "\n".join(lines)
