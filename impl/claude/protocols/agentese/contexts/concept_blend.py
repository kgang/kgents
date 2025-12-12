"""
AGENTESE Conceptual Blending Context

Implements Fauconnier's Conceptual Blending Theory for creative synthesis.

concept.blend.* handles:
- forge: Create blend from two input spaces
- analyze: Decompose an existing blend
- generic: Find generic space (shared structure)
- emergent: Extract emergent features

Source: Fauconnier & Turner (2002), Koestler's Bisociation

Principle Alignment:
- Generative (compressed wisdom via blending)
- Joy-Inducing (emergent features create surprise)
- Composable (blends can be inputs to further blends)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..node import (
    BaseLogosNode,
    BasicRendering,
    Renderable,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# === Blend Affordances ===

BLEND_AFFORDANCES: tuple[str, ...] = ("forge", "analyze", "generic", "emergent")


# === BlendResult Dataclass ===


@dataclass(frozen=True)
class BlendResult:
    """
    Result of conceptual blending operation.

    Frozen to ensure immutability and enable hashing for caching.

    Attributes:
        input_space_a: First mental space (concept path or description)
        input_space_b: Second mental space (concept path or description)
        generic_space: Shared abstract structural relations
        blended_space: The novel synthesis description
        emergent_features: Properties that exist only in the blend
        alignment_score: Structural isomorphism quality (0.0-1.0)
    """

    input_space_a: str
    input_space_b: str
    generic_space: tuple[str, ...]
    blended_space: str
    emergent_features: tuple[str, ...]
    alignment_score: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "input_space_a": self.input_space_a,
            "input_space_b": self.input_space_b,
            "generic_space": list(self.generic_space),
            "blended_space": self.blended_space,
            "emergent_features": list(self.emergent_features),
            "alignment_score": self.alignment_score,
        }

    def to_text(self) -> str:
        """Convert to human-readable text."""
        lines = [
            f"Blend: {self.input_space_a} + {self.input_space_b}",
            f"Result: {self.blended_space}",
            f"Alignment: {self.alignment_score:.2f}",
        ]
        if self.emergent_features:
            lines.append(f"Emergent: {', '.join(self.emergent_features)}")
        return "\n".join(lines)


# === Pure Functions for Blending ===


def extract_tokens(text: str) -> set[str]:
    """
    Extract conceptual tokens from text.

    Uses word tokenization with normalization.

    Args:
        text: Input text to tokenize

    Returns:
        Set of normalized tokens
    """
    # Remove punctuation and convert to lowercase
    normalized = re.sub(r"[^\w\s]", " ", text.lower())
    # Split and filter out short words (likely not concepts)
    words = {w for w in normalized.split() if len(w) > 2}
    return words


def extract_relations(concept: str) -> set[str]:
    """
    Extract structural relations from a concept description.

    Uses heuristic patterns to identify relations:
    - "has_X" patterns from nouns
    - "can_X" patterns from verbs
    - "is_X" patterns from adjectives

    Args:
        concept: Concept description or path

    Returns:
        Set of relation strings
    """
    tokens = extract_tokens(concept)
    relations: set[str] = set()

    # Common relational patterns
    for token in tokens:
        # Assume nouns indicate "has" relations
        relations.add(f"has_{token}")
        # Also add the token itself as a property
        relations.add(f"is_{token}")

    return relations


def find_generic_space(relations_a: set[str], relations_b: set[str]) -> list[str]:
    """
    Find the generic space: shared abstract structure between two concepts.

    The generic space contains relations that exist in both input spaces,
    possibly with different surface forms but similar structure.

    Args:
        relations_a: Relations from first concept
        relations_b: Relations from second concept

    Returns:
        List of shared relations (the generic space)
    """
    # Direct overlap
    direct_overlap = relations_a & relations_b

    # Structural similarity: find has_X patterns that overlap
    a_has = {r.replace("has_", "") for r in relations_a if r.startswith("has_")}
    b_has = {r.replace("has_", "") for r in relations_b if r.startswith("has_")}

    # Find tokens that are semantically similar (simplified: word stems)
    shared_concepts: set[str] = set()
    for a_token in a_has:
        for b_token in b_has:
            # Simple similarity: shared prefix of 3+ chars
            if len(a_token) >= 3 and len(b_token) >= 3:
                if a_token[:3] == b_token[:3]:
                    shared_concepts.add(f"has_{a_token[:3]}*")

    # Combine direct overlap with structural similarity
    generic = list(direct_overlap) + list(shared_concepts)

    # If no overlap found, create abstract relations
    if not generic:
        if relations_a and relations_b:
            # Both have relations but no overlap - abstract to "has_entity"
            generic = ["has_participants", "has_properties"]

    return sorted(set(generic))


def identify_emergent_features(
    blend_description: str,
    relations_a: set[str],
    relations_b: set[str],
) -> list[str]:
    """
    Identify emergent features in the blend.

    Emergent features are properties that exist in the blend
    but not in either input space.

    Args:
        blend_description: The blended concept description
        relations_a: Relations from first input
        relations_b: Relations from second input

    Returns:
        List of emergent feature descriptions
    """
    blend_tokens = extract_tokens(blend_description)
    input_tokens = extract_tokens(" ".join(relations_a | relations_b))

    # Tokens in blend that aren't in inputs
    novel_tokens = blend_tokens - input_tokens

    # Filter to meaningful tokens (length > 3)
    emergent = [t for t in novel_tokens if len(t) > 3]

    # If no tokens found, generate conceptual emergents
    if not emergent and blend_description:
        # The blend itself is emergent if it combines the inputs
        emergent = [f"synthesis_of_{len(relations_a)}_{len(relations_b)}_relations"]

    return sorted(emergent)


def compute_alignment_score(
    generic_space: list[str],
    relations_a: set[str],
    relations_b: set[str],
) -> float:
    """
    Compute alignment score: quality of structural isomorphism.

    Higher scores indicate better structural alignment between inputs.

    Args:
        generic_space: The shared relations
        relations_a: Relations from first input
        relations_b: Relations from second input

    Returns:
        Score between 0.0 (no alignment) and 1.0 (perfect alignment)
    """
    if not relations_a and not relations_b:
        return 0.0

    max_relations = max(len(relations_a), len(relations_b), 1)
    score = len(generic_space) / max_relations

    # Clamp to [0, 1]
    return max(0.0, min(1.0, score))


def forge_blend(
    concept_a: str,
    concept_b: str,
) -> BlendResult:
    """
    Create a conceptual blend from two input spaces.

    Implements the Structure Mapping Engine (SME) pattern:
    1. Extract relations from each concept
    2. Find structural isomorphism (generic space)
    3. Project unmapped elements into blend
    4. Identify emergent features

    Args:
        concept_a: First concept (path or description)
        concept_b: Second concept (path or description)

    Returns:
        BlendResult with synthesis
    """
    # 1. Extract relations
    relations_a = extract_relations(concept_a)
    relations_b = extract_relations(concept_b)

    # 2. Find generic space
    generic = find_generic_space(relations_a, relations_b)

    # 3. Create blend description
    # Extract concept names (last part of path or full description)
    name_a = concept_a.split(".")[-1] if "." in concept_a else concept_a
    name_b = concept_b.split(".")[-1] if "." in concept_b else concept_b

    blended = f"Synthesis of {name_a} and {name_b}"

    # Add detail based on generic space
    if generic:
        shared = ", ".join(
            g.replace("has_", "").replace("is_", "") for g in generic[:3]
        )
        blended = f"{blended} via shared {shared}"

    # 4. Identify emergent features
    emergent = identify_emergent_features(blended, relations_a, relations_b)

    # 5. Compute alignment
    alignment = compute_alignment_score(generic, relations_a, relations_b)

    return BlendResult(
        input_space_a=concept_a,
        input_space_b=concept_b,
        generic_space=tuple(generic),
        blended_space=blended,
        emergent_features=tuple(emergent),
        alignment_score=alignment,
    )


# === BlendNode ===


@dataclass
class BlendNode(BaseLogosNode):
    """
    concept.blend - Conceptual Blending operations.

    Provides access to Fauconnier blending operations:
    - forge: Create blend from two concepts
    - analyze: Decompose existing blend
    - generic: Find generic space only
    - emergent: Extract emergent features

    AGENTESE: concept.blend.*

    Principle Alignment:
    - Generative: Creates compressed wisdom
    - Joy-Inducing: Emergent features surprise
    - Composable: Blends can blend again
    """

    _handle: str = "concept.blend"

    # Cache of recent blends
    _cache: dict[tuple[str, str], BlendResult] = field(default_factory=dict)

    @property
    def handle(self) -> str:
        return self._handle

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """All archetypes have access to blend operations."""
        return BLEND_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View blending capability."""
        return BasicRendering(
            summary="Conceptual Blending (Fauconnier)",
            content=(
                "Blend two concepts to create novel synthesis.\n\n"
                "Affordances:\n"
                "  - forge: Create blend from two concepts\n"
                "  - analyze: Decompose existing blend\n"
                "  - generic: Find shared structure\n"
                "  - emergent: Extract novel features\n"
            ),
            metadata={
                "affordances": list(BLEND_AFFORDANCES),
                "cache_size": len(self._cache),
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle blend-specific aspects."""
        match aspect:
            case "forge":
                return await self._forge(observer, **kwargs)
            case "analyze":
                return await self._analyze(observer, **kwargs)
            case "generic":
                return await self._generic(observer, **kwargs)
            case "emergent":
                return await self._emergent(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _forge(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> BlendResult:
        """
        Create a conceptual blend from two inputs.

        Args:
            concept_a: First concept (path or description)
            concept_b: Second concept (path or description)

        Returns:
            BlendResult with synthesis
        """
        concept_a = kwargs.get("concept_a", "")
        concept_b = kwargs.get("concept_b", "")

        if not concept_a or not concept_b:
            # Return empty blend result
            return BlendResult(
                input_space_a=concept_a,
                input_space_b=concept_b,
                generic_space=(),
                blended_space="",
                emergent_features=(),
                alignment_score=0.0,
            )

        # Check cache
        cache_key = (concept_a, concept_b)
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Create blend
        result = forge_blend(concept_a, concept_b)

        # Cache result
        self._cache[cache_key] = result

        return result

    async def _analyze(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Analyze an existing blend description.

        Args:
            blend: Blend description to analyze

        Returns:
            Analysis dict with decomposition
        """
        blend = kwargs.get("blend", "")
        if not blend:
            return {"error": "blend required"}

        # Extract tokens as proxy for concepts
        tokens = extract_tokens(blend)
        relations = extract_relations(blend)

        return {
            "blend": blend,
            "tokens": sorted(tokens),
            "relations": sorted(relations),
            "complexity": len(tokens),
            "note": "Full analysis requires input space context",
        }

    async def _generic(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[str]:
        """
        Find generic space between two concepts.

        Args:
            concept_a: First concept
            concept_b: Second concept

        Returns:
            List of shared relations
        """
        concept_a = kwargs.get("concept_a", "")
        concept_b = kwargs.get("concept_b", "")

        relations_a = extract_relations(concept_a)
        relations_b = extract_relations(concept_b)

        return find_generic_space(relations_a, relations_b)

    async def _emergent(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> list[str]:
        """
        Extract emergent features from a blend.

        Args:
            blend: Blend description
            concept_a: First input concept (optional, for context)
            concept_b: Second input concept (optional, for context)

        Returns:
            List of emergent features
        """
        blend = kwargs.get("blend", "")
        concept_a = kwargs.get("concept_a", "")
        concept_b = kwargs.get("concept_b", "")

        relations_a = extract_relations(concept_a) if concept_a else set()
        relations_b = extract_relations(concept_b) if concept_b else set()

        return identify_emergent_features(blend, relations_a, relations_b)


# === Factory Functions ===


def create_blend_node() -> BlendNode:
    """Create a BlendNode with default configuration."""
    return BlendNode()
