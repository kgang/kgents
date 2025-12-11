"""
AGENTESE Concept Context Resolver

The Abstract: platonics, definitions, logic, compressed wisdom.

concept.* handles resolve to abstract concepts that can be:
- Refined via dialectical challenge
- Related to other concepts
- Defined (autopoiesis)

Principle Alignment: Generative (compressed wisdom)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..exceptions import TastefulnessError
from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)
from ..renderings import PhilosopherRendering, ScientificRendering

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


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
    - Defined/created (define)

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

    # Integration points
    _registry: Any = None  # L-gent for concept lookup
    _grammarian: Any = None  # G-gent for validation

    def __post_init__(self) -> None:
        if not self.name:
            self.name = (
                self._handle.split(".")[-1] if "." in self._handle else self._handle
            )

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
                antithesis = f"Against {self.name}: The concept may be an illusion or mere convention."
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
        antithesis = (
            f"Against {self.name}: The concept may be an illusion or mere convention."
        )

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
        """Create a child concept (autopoiesis)."""
        name = kwargs.get("name", "unnamed")
        definition = kwargs.get("definition", "")
        domain = kwargs.get("domain", self.domain)

        child_handle = f"concept.{name}"
        child = ConceptNode(
            _handle=child_handle,
            name=name,
            definition=definition,
            domain=domain,
            related_concepts=(self.name,),
            _registry=self._registry,
            _grammarian=self._grammarian,
        )

        # Validate against Tasteful principle if G-gent available
        if self._grammarian and not definition:
            raise TastefulnessError(
                f"Cannot define {name} without a definition",
                validation_errors=["Definition required"],
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
