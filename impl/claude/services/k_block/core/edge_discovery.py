"""
Edge Discovery: Semantic edge detection beyond markdown links.

Philosophy:
    "The edge IS the proof. The discovery IS the witness."

    Edges exist in three forms:
    1. Explicit: Markdown links, portal tokens
    2. Semantic: Concept references, similar terms
    3. Structural: Layer relationships, contradiction patterns

This module discovers all three, returning edges with confidence scores
and reasoning traces.

See: spec/protocols/k-block.md, services/sovereign/integration.py
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class EdgeKind(str, Enum):
    """
    Types of edges that can be discovered.

    Matches KBlockEdge.edge_type but with additional discovery-specific kinds.
    """

    # Explicit edges (from markdown/portal tokens)
    DERIVES_FROM = "derives_from"  # Parent-child derivation
    IMPLEMENTS = "implements"  # Spec -> Impl
    TESTS = "tests"  # Test -> Source
    REFERENCES = "references"  # Explicit markdown link
    EXTENDS = "extends"  # Extension relationship

    # Semantic edges (discovered via content analysis)
    MENTIONS = "mentions"  # Content mentions concepts from another K-Block
    SIMILAR_TO = "similar_to"  # Semantically similar content
    RELATED_BY_LAYER = "related_by_layer"  # Same layer, related concepts

    # Structural edges (from Zero Seed structure)
    GROUNDS = "grounds"  # L1 -> L2 (axiom grounds value)
    JUSTIFIES = "justifies"  # L2 -> L3 (value justifies goal)
    SPECIFIES = "specifies"  # L3 -> L4 (goal specifies spec)
    REALIZES = "realizes"  # L4 -> L5 (spec realizes implementation)
    REFLECTS_ON = "reflects_on"  # L6 -> L1-L5 (reflection on prior layers)
    REPRESENTS = "represents"  # L7 -> any (representation of content)

    # Contradiction edges (from super-additive loss)
    CONTRADICTS = "contradicts"  # Semantic contradiction
    CONFLICTS_WITH = "conflicts_with"  # Structural conflict


# Layer relationship mapping
LAYER_EDGE_KINDS = {
    (1, 2): EdgeKind.GROUNDS,
    (2, 3): EdgeKind.JUSTIFIES,
    (3, 4): EdgeKind.SPECIFIES,
    (4, 5): EdgeKind.REALIZES,
    (6, 1): EdgeKind.REFLECTS_ON,
    (6, 2): EdgeKind.REFLECTS_ON,
    (6, 3): EdgeKind.REFLECTS_ON,
    (6, 4): EdgeKind.REFLECTS_ON,
    (6, 5): EdgeKind.REFLECTS_ON,
    (7, 1): EdgeKind.REPRESENTS,
    (7, 2): EdgeKind.REPRESENTS,
    (7, 3): EdgeKind.REPRESENTS,
    (7, 4): EdgeKind.REPRESENTS,
    (7, 5): EdgeKind.REPRESENTS,
    (7, 6): EdgeKind.REPRESENTS,
}


@dataclass(frozen=True)
class DiscoveredEdge:
    """
    An edge discovered during content analysis.

    Attributes:
        source_id: Source K-Block ID (or path if not yet in cosmos)
        target_id: Target K-Block ID (or path)
        kind: Type of edge relationship
        confidence: Confidence score [0.0, 1.0]
        reasoning: Why this edge was suggested
        context: Surrounding text or evidence
        line_number: Line number where evidence was found
        metadata: Additional discovery-specific data

    Philosophy:
        Every discovered edge carries its proof (reasoning + context).
        Low-confidence edges are suggestions, not assertions.

    Example:
        >>> edge = DiscoveredEdge(
        ...     source_id="kb_abc123",
        ...     target_id="kb_xyz789",
        ...     kind=EdgeKind.MENTIONS,
        ...     confidence=0.85,
        ...     reasoning="Content mentions 'PolyAgent' concept defined in target",
        ...     context="...using PolyAgent[S,A,B] pattern...",
        ...     line_number=42
        ... )
    """

    source_id: str
    target_id: str
    kind: EdgeKind
    confidence: float
    reasoning: str
    context: str = ""
    line_number: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate confidence is in [0, 1]."""
        if not 0.0 <= self.confidence <= 1.0:
            object.__setattr__(self, "confidence", max(0.0, min(1.0, self.confidence)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "kind": self.kind.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "context": self.context,
            "line_number": self.line_number,
            "metadata": self.metadata,
        }

    def to_kblock_edge(self) -> dict[str, Any]:
        """
        Convert to KBlockEdge format for persistence.

        Returns dict suitable for KBlockEdge.from_dict().
        """
        from datetime import datetime, timezone

        edge_id = hashlib.sha256(
            f"{self.source_id}:{self.target_id}:{self.kind.value}".encode()
        ).hexdigest()[:16]

        return {
            "id": f"edge-{edge_id}",
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.kind.value,
            "context": f"{self.reasoning}\n\nContext: {self.context}"
            if self.context
            else self.reasoning,
            "confidence": self.confidence,
            "mark_id": None,  # Will be set when witnessed
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def __repr__(self) -> str:
        """Readable representation."""
        return (
            f"DiscoveredEdge({self.kind.value}, "
            f"{self.source_id[:12]}... → {self.target_id[:12]}..., "
            f"confidence={self.confidence:.0%})"
        )


@dataclass
class ConceptSignature:
    """
    Extracted concepts and key terms from content.

    Used for semantic similarity and concept reference detection.
    """

    # Key concepts (axioms, constructs, agents)
    concepts: set[str] = field(default_factory=set)

    # Important terms (weighted by frequency)
    terms: Counter[str] = field(default_factory=Counter)

    # Layer-specific keywords
    layer_keywords: set[str] = field(default_factory=set)

    # Referenced paths/files
    paths: set[str] = field(default_factory=set)

    def similarity(self, other: ConceptSignature) -> float:
        """
        Compute similarity score with another signature.

        Uses Jaccard similarity for concepts + weighted term overlap.

        Returns:
            Similarity score [0.0, 1.0]
        """
        # Concept Jaccard similarity
        if self.concepts or other.concepts:
            concept_union = self.concepts | other.concepts
            concept_intersection = self.concepts & other.concepts
            concept_sim = len(concept_intersection) / len(concept_union) if concept_union else 0.0
        else:
            concept_sim = 0.0

        # Term cosine similarity (simplified)
        common_terms = set(self.terms.keys()) & set(other.terms.keys())
        if common_terms:
            # Dot product of normalized term vectors
            dot_product = sum(self.terms[term] * other.terms[term] for term in common_terms)
            # Normalize by magnitudes
            self_magnitude = sum(count**2 for count in self.terms.values()) ** 0.5
            other_magnitude = sum(count**2 for count in other.terms.values()) ** 0.5
            term_sim = (
                dot_product / (self_magnitude * other_magnitude)
                if self_magnitude and other_magnitude
                else 0.0
            )
        else:
            term_sim = 0.0

        # Layer keyword overlap
        if self.layer_keywords or other.layer_keywords:
            layer_union = self.layer_keywords | other.layer_keywords
            layer_intersection = self.layer_keywords & other.layer_keywords
            layer_sim = len(layer_intersection) / len(layer_union) if layer_union else 0.0
        else:
            layer_sim = 0.0

        # Weighted average (concepts matter most, then terms, then layer keywords)
        return 0.5 * concept_sim + 0.35 * term_sim + 0.15 * layer_sim


class EdgeDiscoveryService:
    """
    Service for discovering edges beyond explicit markdown links.

    Discovery strategies:
    1. Explicit: Markdown links, portal tokens
    2. Semantic: Concept references, similar content
    3. Structural: Layer relationships, file conventions
    4. Contradiction: Super-additive loss detection

    Philosophy:
        "Every edge is a hypothesis with evidence."

        We don't assert edges—we suggest them with confidence scores.
        The user or system decides whether to accept the suggestion.
    """

    def __init__(self, kgents_root: Path | None = None):
        """
        Initialize edge discovery service.

        Args:
            kgents_root: Root path of kgents workspace
        """
        self.kgents_root = kgents_root or Path.cwd()
        self._concept_patterns = self._build_concept_patterns()

    def discover_edges(
        self,
        content: str,
        source_path: str,
        source_layer: int | None = None,
        corpus: dict[str, Any] | None = None,
    ) -> list[DiscoveredEdge]:
        """
        Discover all edges from content.

        Args:
            content: Source content (markdown text)
            source_path: Source file path or K-Block ID
            source_layer: Zero Seed layer (1-7) if known
            corpus: Optional corpus of existing K-Blocks for semantic matching

        Returns:
            List of discovered edges with confidence scores
        """
        edges: list[DiscoveredEdge] = []

        # Extract signature for semantic analysis
        signature = self._extract_signature(content, source_layer)

        # 1. Discover explicit edges (markdown links, portal tokens)
        edges.extend(self._discover_explicit_edges(content, source_path))

        # 2. Discover semantic edges (concept references)
        edges.extend(self._discover_semantic_edges(content, source_path, signature, corpus))

        # 3. Discover structural edges (layer relationships)
        if source_layer and corpus:
            edges.extend(self._discover_structural_edges(source_path, source_layer, corpus))

        # 4. Discover contradiction edges (if corpus provided)
        if corpus:
            edges.extend(self._discover_contradiction_edges(content, source_path, corpus))

        return edges

    def _discover_explicit_edges(self, content: str, source_path: str) -> list[DiscoveredEdge]:
        """
        Discover explicit edges from markdown links and portal tokens.

        This replaces the simple regex in integration.py with richer detection.
        """
        edges: list[DiscoveredEdge] = []

        # Markdown links: [text](path)
        link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        for match in re.finditer(link_pattern, content):
            link_text = match.group(1)
            link_target = match.group(2)

            # Skip external URLs
            if link_target.startswith(("http://", "https://", "mailto:", "#")):
                continue

            # Determine edge kind based on link text/target
            kind = self._classify_link_kind(link_text, link_target, source_path)

            # Find line number
            line_num = content[: match.start()].count("\n") + 1

            edges.append(
                DiscoveredEdge(
                    source_id=source_path,
                    target_id=link_target,
                    kind=kind,
                    confidence=0.95,  # Explicit links are high confidence
                    reasoning=f"Explicit markdown link: [{link_text}]({link_target})",
                    context=content[max(0, match.start() - 30) : match.end() + 30],
                    line_number=line_num,
                )
            )

        # Portal tokens: [[concept.entity]] or [[path]]
        portal_pattern = r"\[\[([^\]]+)\]\]"
        for match in re.finditer(portal_pattern, content):
            token = match.group(1)

            # Skip if it looks like a concept path (handled separately)
            if "." in token and not token.endswith((".md", ".py", ".ts")):
                continue  # Concept token, not a file reference

            line_num = content[: match.start()].count("\n") + 1

            edges.append(
                DiscoveredEdge(
                    source_id=source_path,
                    target_id=token,
                    kind=EdgeKind.REFERENCES,
                    confidence=0.90,
                    reasoning=f"Portal token reference: [[{token}]]",
                    context=content[max(0, match.start() - 30) : match.end() + 30],
                    line_number=line_num,
                )
            )

        return edges

    def _discover_semantic_edges(
        self,
        content: str,
        source_path: str,
        signature: ConceptSignature,
        corpus: dict[str, Any] | None,
    ) -> list[DiscoveredEdge]:
        """
        Discover semantic edges via concept references and similarity.

        Detects:
        - Mentions of concepts defined in other K-Blocks
        - Semantically similar content
        """
        edges: list[DiscoveredEdge] = []

        if not corpus:
            return edges

        # Check each K-Block in corpus
        for target_id, target_data in corpus.items():
            if target_id == source_path:
                continue  # Skip self

            target_content = target_data.get("content", "")
            target_layer = target_data.get("layer")

            # Extract target signature
            target_signature = self._extract_signature(target_content, target_layer)

            # Check for concept mentions
            mentioned_concepts = signature.concepts & target_signature.concepts
            if mentioned_concepts:
                edges.append(
                    DiscoveredEdge(
                        source_id=source_path,
                        target_id=target_id,
                        kind=EdgeKind.MENTIONS,
                        confidence=0.75,
                        reasoning=f"Mentions concepts defined in target: {', '.join(list(mentioned_concepts)[:3])}",
                        context=f"Shared concepts: {mentioned_concepts}",
                        metadata={"concepts": list(mentioned_concepts)},
                    )
                )

            # Check semantic similarity
            similarity = signature.similarity(target_signature)
            if similarity > 0.5:  # Threshold for similarity edge
                edges.append(
                    DiscoveredEdge(
                        source_id=source_path,
                        target_id=target_id,
                        kind=EdgeKind.SIMILAR_TO,
                        confidence=min(0.85, similarity),
                        reasoning=f"Semantically similar content (similarity={similarity:.2%})",
                        context=f"Similarity score: {similarity:.2%}",
                        metadata={"similarity": similarity},
                    )
                )

        return edges

    def _discover_structural_edges(
        self,
        source_path: str,
        source_layer: int,
        corpus: dict[str, Any],
    ) -> list[DiscoveredEdge]:
        """
        Discover structural edges based on layer relationships.

        Zero Seed structure:
        - L1 (axioms) GROUNDS L2 (values)
        - L2 (values) JUSTIFIES L3 (goals)
        - L3 (goals) SPECIFIES L4 (specs)
        - L4 (specs) REALIZES L5 (implementation)
        - L6 (reflection) REFLECTS_ON L1-L5
        - L7 (representation) REPRESENTS any layer
        """
        edges: list[DiscoveredEdge] = []

        # Find K-Blocks in adjacent layers
        for target_id, target_data in corpus.items():
            if target_id == source_path:
                continue

            target_layer = target_data.get("layer")
            if target_layer is None:
                continue

            # Check if layer pair defines a structural relationship
            layer_pair = (source_layer, target_layer)
            if layer_pair in LAYER_EDGE_KINDS:
                kind = LAYER_EDGE_KINDS[layer_pair]

                edges.append(
                    DiscoveredEdge(
                        source_id=source_path,
                        target_id=target_id,
                        kind=kind,
                        confidence=0.65,  # Structural edges are moderate confidence
                        reasoning=f"Layer {source_layer} {kind.value.replace('_', ' ')} Layer {target_layer}",
                        context=f"Zero Seed layer relationship: L{source_layer} -> L{target_layer}",
                        metadata={"source_layer": source_layer, "target_layer": target_layer},
                    )
                )

        return edges

    def _discover_contradiction_edges(
        self,
        content: str,
        source_path: str,
        corpus: dict[str, Any],
    ) -> list[DiscoveredEdge]:
        """
        Discover contradiction edges via super-additive loss.

        This is a simplified implementation. Full implementation would use
        Galois loss computer to detect semantic contradictions.

        For now, we use heuristics:
        - Negation patterns ("not X", "X is false")
        - Conflicting statements about same concepts
        """
        edges: list[DiscoveredEdge] = []

        # Extract negative assertions from content
        negation_pattern = (
            r"(?:not|no|never|isn't|aren't|doesn't|don't|can't|cannot)\s+([A-Za-z_]+)"
        )
        negations = set(re.findall(negation_pattern, content.lower()))

        if not negations:
            return edges

        # Check corpus for positive assertions of negated concepts
        for target_id, target_data in corpus.items():
            if target_id == source_path:
                continue

            target_content = target_data.get("content", "")

            # Look for positive assertions
            for negated_term in negations:
                # Pattern matches both:
                # - "X can Y" (can compose)
                # - "Y can X" (compose can)
                # - "X is Y" (composition is associative)
                positive_pattern = (
                    rf"\b{negated_term}\b|\b(?:can|is|are|does|do)\s+{negated_term}\b"
                )
                if re.search(positive_pattern, target_content.lower()):
                    # Make sure it's a positive assertion (not also negated in target)
                    negation_in_target = rf"(?:not|no|never|isn't|aren't|doesn't|don't|can't|cannot)\s+{negated_term}\b"
                    if not re.search(negation_in_target, target_content.lower()):
                        edges.append(
                            DiscoveredEdge(
                                source_id=source_path,
                                target_id=target_id,
                                kind=EdgeKind.CONTRADICTS,
                                confidence=0.60,  # Low confidence without full Galois analysis
                                reasoning=f"Potential contradiction: source negates '{negated_term}', target asserts it",
                                context=f"Negated term: {negated_term}",
                                metadata={"negated_term": negated_term},
                            )
                        )

        return edges

    def _extract_signature(self, content: str, layer: int | None = None) -> ConceptSignature:
        """
        Extract concept signature from content.

        Identifies:
        - Concepts (axioms, constructs, agents)
        - Key terms (weighted by frequency)
        - Layer-specific keywords
        - Referenced paths
        """
        signature = ConceptSignature()

        # Extract concepts using patterns
        for pattern_name, pattern in self._concept_patterns.items():
            matches = re.findall(pattern, content, re.MULTILINE)
            signature.concepts.update(matches)

        # Extract key terms (filter stopwords, weight by frequency)
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "this",
            "that",
            "these",
            "those",
            "it",
            "its",
            "can",
            "will",
            "would",
        }
        words = re.findall(r"\b[a-z_][a-z0-9_]{2,}\b", content.lower())
        signature.terms = Counter(
            word for word in words if word not in stopwords and not word.startswith("_")
        )

        # Extract layer-specific keywords
        if layer:
            layer_keywords = {
                1: {"axiom", "principle", "law", "foundation"},
                2: {"value", "ethical", "moral", "virtue"},
                3: {"goal", "objective", "aim", "target"},
                4: {"spec", "specification", "protocol", "contract"},
                5: {"implementation", "code", "function", "class"},
                6: {"reflection", "retrospective", "learning", "insight"},
                7: {"representation", "documentation", "guide", "tutorial"},
            }
            signature.layer_keywords = layer_keywords.get(layer, set())

        # Extract referenced paths
        path_pattern = r'(?:spec|impl|docs)/[^\s`"<>)]+(?:\.md|\.py|\.ts)?'
        signature.paths = set(re.findall(path_pattern, content))

        return signature

    def _build_concept_patterns(self) -> dict[str, str]:
        """
        Build regex patterns for concept extraction.

        Returns:
            Dict of pattern_name -> regex pattern
        """
        return {
            # Agent names (capitalized, often with suffix)
            "agents": r"\b([A-Z][a-z]*(?:Agent|Gent|Operad|Sheaf|Flux))\b",
            # Axioms/Laws (AXIOM/LAW + identifier)
            "axioms": r"(?:AXIOM|LAW)\s+([A-Z0-9]+)",
            # Principles (from spec/principles.md)
            "principles": r"\b(Tasteful|Curated|Ethical|Joy-Inducing|Composable|Heterarchical|Generative)\b",
            # Category theory constructs
            "categorical": r"\b(Functor|Monad|Operad|Sheaf|Profunctor|Polynomial)\b",
            # kgents-specific constructs
            "constructs": r"\b(K-Block|D-gent|M-gent|K-gent|AGENTESE|Witness|Crystal|Portal)\b",
        }

    def _classify_link_kind(self, link_text: str, link_target: str, source_path: str) -> EdgeKind:
        """
        Classify markdown link kind based on text/target.

        Args:
            link_text: Link text
            link_target: Link target path
            source_path: Source file path

        Returns:
            Appropriate EdgeKind
        """
        link_text_lower = link_text.lower()
        link_target_lower = link_target.lower()

        # Test relationships
        if "_tests/" in link_target or "_test.py" in link_target:
            return EdgeKind.TESTS

        # Implementation relationships
        if "impl/" in source_path and "spec/" in link_target:
            return EdgeKind.IMPLEMENTS

        # Extension relationships
        if any(word in link_text_lower for word in ["extends", "builds on", "inherits"]):
            return EdgeKind.EXTENDS

        # Derivation relationships
        if any(word in link_text_lower for word in ["derives from", "based on", "parent"]):
            return EdgeKind.DERIVES_FROM

        # Default to generic reference
        return EdgeKind.REFERENCES


# -----------------------------------------------------------------------------
# Service Factory
# -----------------------------------------------------------------------------

_edge_discovery_service: EdgeDiscoveryService | None = None


def get_edge_discovery_service(
    kgents_root: Path | None = None,
) -> EdgeDiscoveryService:
    """
    Get or create the global EdgeDiscoveryService.

    Args:
        kgents_root: Root path of kgents workspace

    Returns:
        EdgeDiscoveryService singleton
    """
    global _edge_discovery_service

    if _edge_discovery_service is None:
        _edge_discovery_service = EdgeDiscoveryService(kgents_root)

    return _edge_discovery_service


def reset_edge_discovery_service() -> None:
    """Reset the global service (for testing)."""
    global _edge_discovery_service
    _edge_discovery_service = None


__all__ = [
    "EdgeKind",
    "DiscoveredEdge",
    "ConceptSignature",
    "EdgeDiscoveryService",
    "get_edge_discovery_service",
    "reset_edge_discovery_service",
]
