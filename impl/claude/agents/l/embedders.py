"""
L-gent Advanced Embedders: High-quality semantic embeddings for Phase 6.

This module provides production-grade embedders for semantic search:
- SentenceTransformerEmbedder: Local transformer models (all-MiniLM-L6-v2, etc.)
- OpenAIEmbedder: OpenAI's text-embedding-3-small/large models
- CachedEmbedder: Wrapper for caching embeddings (D-gent integration)

Phase 6 Goals:
- Better quality than TF-IDF (Phase 5 SimpleEmbedder)
- Support for large catalogs (>1000 entries) with vector DB backends
- Pluggable architecture: Easy to swap embedders
- Optional dependencies: Graceful degradation if libraries missing
"""

from dataclasses import dataclass
from typing import Optional, cast

from .semantic import Embedder

# Sentinel for optional imports
SENTENCE_TRANSFORMERS_AVAILABLE = False
OPENAI_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    pass

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    pass


@dataclass
class EmbeddingMetadata:
    """Metadata about an embedding model."""

    name: str
    dimension: int
    provider: str  # "sentence-transformers", "openai", "custom"
    max_tokens: int
    supports_batch: bool = False


class SentenceTransformerEmbedder:
    """Embedder using sentence-transformers library.

    This provides high-quality semantic embeddings using open-source
    transformer models like:
    - all-MiniLM-L6-v2 (384-dim, fast, good quality)
    - all-mpnet-base-v2 (768-dim, slower, best quality)
    - paraphrase-multilingual (multilingual support)

    Requires: pip install sentence-transformers

    Example:
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
        vector = await embedder.embed("find agents for data processing")
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None,
        normalize: bool = True,
    ):
        """Initialize sentence-transformer embedder.

        Args:
            model_name: HuggingFace model name
            device: Device to run on ("cpu", "cuda", "mps", None=auto)
            normalize: Whether to L2-normalize embeddings (recommended for cosine similarity)

        Raises:
            ImportError: If sentence-transformers not installed
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.normalize = normalize
        self._model = SentenceTransformer(model_name, device=device)
        self._dimension = self._model.get_sentence_embedding_dimension()

    @property
    def dimension(self) -> int:
        """Dimension of embedding vectors."""
        return cast(int, self._dimension)

    @property
    def metadata(self) -> EmbeddingMetadata:
        """Metadata about this embedder."""
        return EmbeddingMetadata(
            name=self.model_name,
            dimension=self._dimension,
            provider="sentence-transformers",
            max_tokens=512,  # Most models support 512 tokens
            supports_batch=True,
        )

    async def embed(self, text: str) -> list[float]:
        """Embed text into dense vector.

        Args:
            text: Text to embed

        Returns:
            Dense embedding vector
        """
        # sentence-transformers returns numpy array, convert to list
        embedding = self._model.encode(
            text, normalize_embeddings=self.normalize, show_progress_bar=False
        )
        return cast(list[float], embedding.tolist())

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self._model.encode(
            texts, normalize_embeddings=self.normalize, show_progress_bar=False
        )
        return cast(list[list[float]], embeddings.tolist())


class OpenAIEmbedder:
    """Embedder using OpenAI's embedding models.

    This provides the highest quality embeddings using OpenAI's API:
    - text-embedding-3-small (1536-dim, fast, good quality)
    - text-embedding-3-large (3072-dim, slower, best quality)
    - text-embedding-ada-002 (1536-dim, legacy)

    Requires:
    - pip install openai
    - OPENAI_API_KEY environment variable set

    Example:
        embedder = OpenAIEmbedder(model="text-embedding-3-small")
        vector = await embedder.embed("find agents for data processing")
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        dimensions: Optional[int] = None,
    ):
        """Initialize OpenAI embedder.

        Args:
            model: OpenAI model name
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            dimensions: Optional dimension reduction (only for text-embedding-3-*)

        Raises:
            ImportError: If openai not installed
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai not installed. Install with: pip install openai")

        self.model = model
        self._client = openai.OpenAI(api_key=api_key) if api_key else openai.OpenAI()

        # Determine dimension
        if dimensions:
            self._dimension = dimensions
        else:
            # Default dimensions for known models
            if model == "text-embedding-3-small":
                self._dimension = 1536
            elif model == "text-embedding-3-large":
                self._dimension = 3072
            elif model == "text-embedding-ada-002":
                self._dimension = 1536
            else:
                # Unknown model, will detect on first embed
                self._dimension = 1536

    @property
    def dimension(self) -> int:
        """Dimension of embedding vectors."""
        return self._dimension

    @property
    def metadata(self) -> EmbeddingMetadata:
        """Metadata about this embedder."""
        return EmbeddingMetadata(
            name=self.model,
            dimension=self._dimension,
            provider="openai",
            max_tokens=8191,  # OpenAI embedding models support 8191 tokens
            supports_batch=True,
        )

    async def embed(self, text: str) -> list[float]:
        """Embed text into dense vector.

        Args:
            text: Text to embed

        Returns:
            Dense embedding vector
        """
        response = self._client.embeddings.create(
            input=text,
            model=self.model,
        )
        embedding = response.data[0].embedding
        # Update dimension if this is the first call
        if self._dimension != len(embedding):
            self._dimension = len(embedding)
        return cast(list[float], embedding)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts efficiently.

        Args:
            texts: List of texts to embed (max 2048 per batch)

        Returns:
            List of embedding vectors
        """
        # OpenAI supports batching up to 2048 texts
        response = self._client.embeddings.create(
            input=texts,
            model=self.model,
        )
        embeddings = [item.embedding for item in response.data]
        return embeddings


class CachedEmbedder:
    """Wrapper that caches embeddings using D-gent PersistentAgent.

    This reduces API costs for OpenAI embeddings and speeds up repeated
    queries. The cache is persisted to disk and shared across sessions.

    Example:
        base_embedder = OpenAIEmbedder()
        embedder = CachedEmbedder(base_embedder, cache_path="embeddings_cache.json")
        vector = await embedder.embed("same query")  # Hits cache on second call
    """

    def __init__(self, base_embedder: Embedder, cache_path: str = ".kgents/embeddings_cache.json"):
        """Initialize cached embedder.

        Args:
            base_embedder: Underlying embedder to wrap
            cache_path: Path to cache file
        """
        self.base_embedder = base_embedder
        self.cache_path = cache_path
        self._cache: dict[str, list[float]] = {}
        self._load_cache()

    @property
    def dimension(self) -> int:
        """Dimension of embedding vectors."""
        return self.base_embedder.dimension

    async def embed(self, text: str) -> list[float]:
        """Embed text, using cache if available.

        Args:
            text: Text to embed

        Returns:
            Dense embedding vector
        """
        # Check cache
        if text in self._cache:
            return self._cache[text]

        # Miss: compute and cache
        embedding = await self.base_embedder.embed(text)
        self._cache[text] = embedding
        self._save_cache()
        return embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts, using cache where possible.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        results = []
        uncached_texts = []
        uncached_indices = []

        # Separate cached and uncached
        for i, text in enumerate(texts):
            if text in self._cache:
                results.append((i, self._cache[text]))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Compute uncached
        if uncached_texts:
            # Check if base embedder supports batching
            if hasattr(self.base_embedder, "embed_batch"):
                uncached_embeddings = await self.base_embedder.embed_batch(uncached_texts)
            else:
                # Fallback: embed one by one
                uncached_embeddings = [
                    await self.base_embedder.embed(text) for text in uncached_texts
                ]

            # Cache and collect results
            for idx, text, embedding in zip(uncached_indices, uncached_texts, uncached_embeddings):
                self._cache[text] = embedding
                results.append((idx, embedding))

            self._save_cache()

        # Sort by original order
        results.sort(key=lambda x: x[0])
        return [emb for _, emb in results]

    def _load_cache(self) -> None:
        """Load cache from disk."""
        import json
        import os

        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    self._cache = json.load(f)
            except Exception:
                # Corrupted cache, start fresh
                self._cache = {}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        import json
        import os

        # Create directory if needed
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)

        # Atomic write (temp + rename)
        temp_path = self.cache_path + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(self._cache, f)
        os.replace(temp_path, self.cache_path)


# Convenience functions


def create_best_available_embedder(
    prefer: str = "sentence-transformers",
) -> Embedder:
    """Create the best available embedder based on installed dependencies.

    Args:
        prefer: Preferred provider ("sentence-transformers", "openai")

    Returns:
        Best available embedder (falls back to SimpleEmbedder if nothing else available)
    """
    if prefer == "sentence-transformers" and SENTENCE_TRANSFORMERS_AVAILABLE:
        return SentenceTransformerEmbedder()
    elif prefer == "openai" and OPENAI_AVAILABLE:
        return OpenAIEmbedder()
    elif SENTENCE_TRANSFORMERS_AVAILABLE:
        return SentenceTransformerEmbedder()
    elif OPENAI_AVAILABLE:
        return OpenAIEmbedder()
    else:
        # Fallback to SimpleEmbedder
        from .semantic import SimpleEmbedder

        return SimpleEmbedder()


async def compare_embedders(
    text: str, embedders: list[tuple[str, Embedder]]
) -> dict[str, list[float]]:
    """Compare multiple embedders on the same text.

    Useful for debugging and quality assessment.

    Args:
        text: Text to embed
        embedders: List of (name, embedder) tuples

    Returns:
        Dictionary mapping embedder names to embeddings
    """
    results = {}
    for name, embedder in embedders:
        embedding = await embedder.embed(text)
        results[name] = embedding
    return results
