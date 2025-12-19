"""
L-gent Semantic Search: Vector-based intent matching for agent discovery.

This module implements the "Brain 2" of L-gent's three-brain architecture:
semantic search using embeddings to find artifacts by intent rather than keywords.

Phase 5 Implementation:
- SemanticBrain: Vector-based search engine
- Embedder protocol: Pluggable embedding backends
- Simple TF-IDF fallback: No external dependencies required
- D-gent VectorAgent integration: Optional vector DB backend

Design Philosophy:
- Graceful degradation: Work without ML dependencies (TF-IDF fallback)
- Pluggable: Support sentence-transformers, OpenAI, or custom embedders
- Fast: <100ms query latency for interactive use
- Composable: Works alongside keyword and graph search
"""

from dataclasses import dataclass
from typing import Any, Protocol

from .types import CatalogEntry, Status


@dataclass
class SemanticResult:
    """Result from semantic search with similarity score."""

    id: str
    entry: CatalogEntry
    similarity: float  # Cosine similarity (0.0 to 1.0)
    explanation: str  # Why this matched


class Embedder(Protocol):
    """Protocol for embedding text into vector space.

    Implementations can use:
    - TF-IDF (fast, no dependencies)
    - sentence-transformers (good quality, requires torch)
    - OpenAI embeddings (highest quality, requires API key)
    - Custom models (domain-specific)
    """

    async def embed(self, text: str) -> list[float]:
        """Embed text into a dense vector.

        Args:
            text: Text to embed (description, intent, query)

        Returns:
            Dense vector (dimension determined by implementation)
        """
        ...

    @property
    def dimension(self) -> int:
        """Dimension of embedding vectors."""
        ...


class SimpleEmbedder:
    """TF-IDF based embedder (no ML dependencies).

    This is a fallback implementation that provides reasonable semantic
    matching without requiring heavy ML libraries. It's fast and good
    enough for small catalogs (<1000 entries).

    For larger catalogs or better quality, use SentenceTransformerEmbedder
    or OpenAIEmbedder.
    """

    def __init__(self, dimension: int = 128):
        """Initialize TF-IDF embedder.

        Args:
            dimension: Number of dimensions (top-K terms to keep)
        """
        self._dimension = dimension
        self._vocabulary: dict[str, int] = {}
        self._idf: dict[str, float] = {}
        self._doc_count = 0

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(self, text: str) -> list[float]:
        """Embed text using TF-IDF representation.

        Args:
            text: Text to embed

        Returns:
            TF-IDF vector (sparse, but represented densely)
        """
        # Tokenize (simple word splitting)
        tokens = self._tokenize(text)

        # Compute term frequencies
        tf = self._compute_tf(tokens)

        # Convert to vector using IDF weights
        vector = [0.0] * self._dimension
        for term, freq in tf.items():
            if term in self._vocabulary:
                idx = self._vocabulary[term]
                if idx < self._dimension:
                    idf = self._idf.get(term, 1.0)
                    vector[idx] = freq * idf

        # Normalize
        return self._normalize(vector)

    async def fit(self, documents: list[str]) -> None:
        """Build vocabulary and IDF weights from documents.

        Args:
            documents: Corpus of text to build vocabulary from
        """
        # Count documents
        self._doc_count = len(documents)

        # Build document frequency
        df: dict[str, int] = {}
        for doc in documents:
            tokens = set(self._tokenize(doc))
            for token in tokens:
                df[token] = df.get(token, 0) + 1

        # Sort by document frequency (most common terms first)
        sorted_terms = sorted(df.items(), key=lambda x: x[1], reverse=True)

        # Build vocabulary (top K terms)
        self._vocabulary = {
            term: idx for idx, (term, _) in enumerate(sorted_terms[: self._dimension])
        }

        # Compute IDF
        import math

        self._idf = {term: math.log(self._doc_count / count) for term, count in df.items()}

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization (lowercas + word split)."""
        import re

        # Lowercase and extract words
        words = re.findall(r"\b\w+\b", text.lower())
        return words

    def _compute_tf(self, tokens: list[str]) -> dict[str, float]:
        """Compute term frequencies."""
        tf: dict[str, float] = {}
        total = len(tokens)
        if total == 0:
            return tf

        for token in tokens:
            tf[token] = tf.get(token, 0.0) + 1.0

        # Normalize by document length
        for token in tf:
            tf[token] /= total

        return tf

    def _normalize(self, vector: list[float]) -> list[float]:
        """L2 normalization for cosine similarity."""
        import math

        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude == 0:
            return vector
        return [x / magnitude for x in vector]


class SemanticBrain:
    """Semantic search engine using vector embeddings.

    This is "Brain 2" of the three-brain architecture. It finds artifacts
    by semantic similarity to user intent, enabling fuzzy matching and
    discovery.

    Example:
        brain = SemanticBrain(embedder=SimpleEmbedder())
        await brain.fit(registry)
        results = await brain.search("summarize financial documents")
    """

    def __init__(self, embedder: Embedder):
        """Initialize semantic search brain.

        Args:
            embedder: Embedding implementation (SimpleEmbedder, etc.)
        """
        self.embedder = embedder
        self._embeddings: dict[str, list[float]] = {}
        self._entries: dict[str, CatalogEntry] = {}

    async def fit(self, entries: dict[str, CatalogEntry]) -> None:
        """Build semantic index from catalog entries.

        Args:
            entries: Catalog entries to index
        """
        # Fit embedder if it's a SimpleEmbedder
        if isinstance(self.embedder, SimpleEmbedder):
            documents = [self._make_searchable_text(entry) for entry in entries.values()]
            await self.embedder.fit(documents)

        # Embed all entries
        for entry_id, entry in entries.items():
            text = self._make_searchable_text(entry)
            embedding = await self.embedder.embed(text)
            self._embeddings[entry_id] = embedding
            self._entries[entry_id] = entry

    async def search(
        self,
        intent: str,
        filters: dict[str, Any] | None = None,
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[SemanticResult]:
        """Search for entries by semantic similarity to intent.

        Args:
            intent: Natural language description of what user wants
            filters: Optional filters (entity_type, status, etc.)
            threshold: Minimum similarity score (0.0 to 1.0)
            limit: Maximum number of results

        Returns:
            List of semantic results, ranked by similarity
        """
        # Embed query
        query_embedding = await self.embedder.embed(intent)

        # Compute similarities
        candidates: list[tuple[str, float]] = []
        for entry_id, embedding in self._embeddings.items():
            entry = self._entries[entry_id]

            # Apply filters
            if filters:
                if not self._matches_filters(entry, filters):
                    continue

            # Cosine similarity
            similarity = self._cosine_similarity(query_embedding, embedding)

            if similarity >= threshold:
                candidates.append((entry_id, similarity))

        # Sort by similarity (descending)
        candidates.sort(key=lambda x: x[1], reverse=True)

        # Build results
        results = []
        for entry_id, similarity in candidates[:limit]:
            entry = self._entries[entry_id]
            results.append(
                SemanticResult(
                    id=entry_id,
                    entry=entry,
                    similarity=similarity,
                    explanation=f"Semantic similarity: {similarity:.2f}",
                )
            )

        return results

    async def add_entry(self, entry: CatalogEntry) -> None:
        """Add or update entry in semantic index.

        Args:
            entry: Catalog entry to index
        """
        # For SimpleEmbedder, we need to refit when adding new entries
        # to ensure the vocabulary includes new terms
        if isinstance(self.embedder, SimpleEmbedder):
            # Add entry first
            self._entries[entry.id] = entry
            # Refit on all entries to update vocabulary
            documents = [self._make_searchable_text(e) for e in self._entries.values()]
            await self.embedder.fit(documents)
            # Re-embed all entries with updated vocabulary
            for entry_id, entry_obj in self._entries.items():
                text = self._make_searchable_text(entry_obj)
                embedding = await self.embedder.embed(text)
                self._embeddings[entry_id] = embedding
        else:
            # For other embedders, just embed the new entry
            text = self._make_searchable_text(entry)
            embedding = await self.embedder.embed(text)
            self._embeddings[entry.id] = embedding
            self._entries[entry.id] = entry

    async def remove_entry(self, entry_id: str) -> None:
        """Remove entry from semantic index.

        Args:
            entry_id: ID of entry to remove
        """
        self._embeddings.pop(entry_id, None)
        self._entries.pop(entry_id, None)

    def _make_searchable_text(self, entry: CatalogEntry) -> str:
        """Create searchable text from entry metadata."""
        parts = [entry.name, entry.description]

        # Add type information
        if entry.input_type:
            parts.append(f"input: {entry.input_type}")
        if entry.output_type:
            parts.append(f"output: {entry.output_type}")

        # Add domain information (for tongues)
        if entry.tongue_domain:
            parts.append(f"domain: {entry.tongue_domain}")

        return " ".join(parts)

    def _matches_filters(self, entry: CatalogEntry, filters: dict[str, Any]) -> bool:
        """Check if entry matches filter criteria."""
        for key, value in filters.items():
            if key == "entity_type":
                if entry.entity_type != value:
                    return False
            elif key == "status":
                if entry.status != value:
                    return False
            elif key == "deprecated":
                # Check if status is DEPRECATED
                is_deprecated = entry.status == Status.DEPRECATED
                if is_deprecated != value:
                    return False
            # Add more filter types as needed

        return True

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        import math

        # Ensure same dimension
        if len(vec1) != len(vec2):
            return 0.0

        # Dot product
        dot = sum(a * b for a, b in zip(vec1, vec2))

        # Magnitudes
        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)


# Convenience functions


async def create_semantic_brain(
    entries: dict[str, CatalogEntry] | None = None, embedder: Embedder | None = None
) -> SemanticBrain:
    """Create and optionally fit a semantic search brain.

    Args:
        entries: Optional catalog entries to index immediately
        embedder: Optional custom embedder (defaults to SimpleEmbedder)

    Returns:
        SemanticBrain instance
    """
    if embedder is None:
        embedder = SimpleEmbedder()

    brain = SemanticBrain(embedder)

    if entries:
        await brain.fit(entries)

    return brain
