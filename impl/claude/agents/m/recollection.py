"""
RecollectionAgent: Generative Memory Retrieval.

The fundamental M-gent: transforms cues into reconstructions.
Unlike a database lookup, recollection is RECONSTRUCTION:
- Partial matches always return something
- Results are influenced by all stored memories
- The "resolution" depends on the depth of the cue
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, Optional, Protocol, TypeVar

from .holographic import HolographicMemory, ResonanceResult

T = TypeVar("T")


@dataclass
class Cue:
    """A cue for memory retrieval.

    Cues can be:
    - Text queries
    - Semantic concepts
    - Pre-computed embeddings
    - Context objects
    """

    text: Optional[str] = None
    concepts: list[str] = field(default_factory=list)
    embedding: Optional[list[float]] = None
    context: Optional[dict[str, Any]] = None

    @property
    def is_valid(self) -> bool:
        """Check if cue has at least one retrieval method."""
        return bool(self.text or self.concepts or self.embedding)


@dataclass
class ReconstructionRequest(Generic[T]):
    """Request for memory reconstruction."""

    cue: Cue
    resonant_patterns: list[ResonanceResult[T]]
    resolution: float  # 0.0 to 1.0
    max_length: Optional[int] = None
    format_hint: Optional[str] = None  # "narrative", "factual", "structured"


@dataclass
class Recollection(Generic[T]):
    """A reconstructed memory.

    Not an exact retrieval, but a generative synthesis
    of resonant patterns.
    """

    content: T
    confidence: float  # 0.0 to 1.0
    resolution: float  # Effective resolution after compression
    sources: list[str]  # IDs of contributing patterns
    timestamp: datetime = field(default_factory=datetime.now)
    reconstruction_method: str = "synthesis"

    @property
    def is_high_quality(self) -> bool:
        """Check if recollection is reliable."""
        return self.confidence >= 0.7 and self.resolution >= 0.5


class Reconstructor(Protocol[T]):
    """Protocol for memory reconstruction.

    Reconstructors take resonant patterns and synthesize
    a coherent memory. Can be LLM-based or rule-based.
    """

    async def reconstruct(
        self,
        request: ReconstructionRequest[T],
    ) -> Recollection[T]:
        """Reconstruct memory from resonant patterns."""
        ...


class SimpleReconstructor(Generic[T]):
    """Simple reconstructor: returns the top match.

    For testing or when LLM reconstruction isn't needed.
    """

    async def reconstruct(
        self,
        request: ReconstructionRequest[T],
    ) -> Recollection[T]:
        """Return the best matching pattern's content."""
        if not request.resonant_patterns:
            # Even with no matches, return something (graceful degradation)
            return Recollection(
                content=None,  # type: ignore
                confidence=0.0,
                resolution=0.0,
                sources=[],
                reconstruction_method="empty",
            )

        # Use the best match
        best = request.resonant_patterns[0]
        return Recollection(
            content=best.pattern.content,
            confidence=best.similarity,
            resolution=best.resolution,
            sources=[best.pattern.id],
            reconstruction_method="top_match",
        )


class WeightedReconstructor(Generic[T]):
    """Weighted reconstructor: combines multiple patterns.

    Synthesizes content from multiple resonant patterns,
    weighted by their similarity scores.
    """

    def __init__(self, combiner: Any = None):
        """Initialize with optional combiner function.

        Args:
            combiner: Function to combine multiple contents
                     Default: concatenate with weights
        """
        self._combiner = combiner

    async def reconstruct(
        self,
        request: ReconstructionRequest[T],
    ) -> Recollection[T]:
        """Synthesize from weighted patterns."""
        if not request.resonant_patterns:
            return Recollection(
                content=None,  # type: ignore
                confidence=0.0,
                resolution=0.0,
                sources=[],
                reconstruction_method="empty",
            )

        # Collect weighted contents
        weighted_contents = [
            (r.pattern.content, r.effective_score) for r in request.resonant_patterns
        ]

        # Combine
        if self._combiner:
            content = self._combiner(weighted_contents)
        else:
            # Default: take highest weighted
            content = max(weighted_contents, key=lambda x: x[1])[0]

        # Aggregate confidence and resolution
        total_weight = sum(w for _, w in weighted_contents)
        confidence = sum(
            r.similarity * r.effective_score for r in request.resonant_patterns
        ) / max(total_weight, 1.0)

        resolution = sum(
            r.resolution * r.effective_score for r in request.resonant_patterns
        ) / max(total_weight, 1.0)

        return Recollection(
            content=content,
            confidence=confidence,
            resolution=resolution,
            sources=[r.pattern.id for r in request.resonant_patterns],
            reconstruction_method="weighted_synthesis",
        )


class RecollectionAgent(Generic[T]):
    """The fundamental M-gent: generative memory retrieval.

    Transforms cues into reconstructions through:
    1. Resonate with holographic memory
    2. Compute effective resolution
    3. Generatively reconstruct

    Example:
        memory = HolographicMemory(embedder=my_embedder)
        agent = RecollectionAgent(memory)

        # Store some memories
        await memory.store("m1", "User prefers dark mode", ["preference", "ui"])
        await memory.store("m2", "User works at night", ["schedule", "preference"])

        # Recall
        recollection = await agent.invoke(Cue(text="What are user preferences?"))
        print(recollection.content)  # Synthesized from both memories
    """

    def __init__(
        self,
        memory: HolographicMemory[T],
        reconstructor: Optional[Reconstructor[T]] = None,
        default_limit: int = 10,
        default_threshold: float = 0.3,
    ):
        """Initialize RecollectionAgent.

        Args:
            memory: HolographicMemory to retrieve from
            reconstructor: Strategy for reconstruction (default: SimpleReconstructor)
            default_limit: Default max patterns to retrieve
            default_threshold: Default minimum similarity threshold
        """
        self._memory = memory
        self._reconstructor = reconstructor or SimpleReconstructor()
        self._default_limit = default_limit
        self._default_threshold = default_threshold

    async def invoke(
        self,
        cue: Cue,
        limit: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> Recollection[T]:
        """Recall memory from a cue.

        Args:
            cue: The retrieval cue
            limit: Max patterns to consider
            threshold: Minimum similarity threshold

        Returns:
            Reconstructed memory
        """
        if not cue.is_valid:
            return Recollection(
                content=None,  # type: ignore
                confidence=0.0,
                resolution=0.0,
                sources=[],
                reconstruction_method="invalid_cue",
            )

        limit = limit or self._default_limit
        threshold = threshold or self._default_threshold

        # Get resonant patterns
        resonant = await self._retrieve_resonant(cue, limit, threshold)

        # Compute overall resolution
        resolution = self._compute_resolution(resonant)

        # Reconstruct
        request = ReconstructionRequest(
            cue=cue,
            resonant_patterns=resonant,
            resolution=resolution,
        )

        return await self._reconstructor.reconstruct(request)

    async def recall_by_concept(
        self,
        concept: str,
        limit: int = 10,
    ) -> Recollection[T]:
        """Recall memories associated with a concept.

        Args:
            concept: Semantic concept
            limit: Max patterns

        Returns:
            Reconstructed memory
        """
        cue = Cue(concepts=[concept])
        resonant = await self._memory.retrieve_by_concept(concept, limit)

        resolution = self._compute_resolution(resonant)
        request = ReconstructionRequest(
            cue=cue,
            resonant_patterns=resonant,
            resolution=resolution,
        )

        return await self._reconstructor.reconstruct(request)

    async def _retrieve_resonant(
        self,
        cue: Cue,
        limit: int,
        threshold: float,
    ) -> list[ResonanceResult[T]]:
        """Retrieve resonant patterns for a cue."""
        results: list[ResonanceResult[T]] = []

        # Text-based retrieval
        if cue.text:
            text_results = await self._memory.retrieve(
                query=cue.text,
                limit=limit,
                threshold=threshold,
            )
            results.extend(text_results)

        # Embedding-based retrieval
        elif cue.embedding:
            embed_results = await self._memory.retrieve(
                query=cue.embedding,
                limit=limit,
                threshold=threshold,
            )
            results.extend(embed_results)

        # Concept-based retrieval
        for concept in cue.concepts:
            concept_results = await self._memory.retrieve_by_concept(
                concept=concept,
                limit=limit,
            )
            # Add if not already present
            seen_ids = {r.pattern.id for r in results}
            for r in concept_results:
                if r.pattern.id not in seen_ids:
                    results.append(r)

        # Sort by effective score and limit
        results.sort(key=lambda r: r.effective_score, reverse=True)
        return results[:limit]

    def _compute_resolution(
        self,
        patterns: list[ResonanceResult[T]],
    ) -> float:
        """Compute overall resolution from pattern set."""
        if not patterns:
            return 0.0

        # Weighted average of resolutions
        total_weight = sum(p.similarity for p in patterns)
        if total_weight == 0:
            return 0.0

        weighted_resolution = sum(p.resolution * p.similarity for p in patterns)
        return weighted_resolution / total_weight


class ContextualRecollectionAgent(RecollectionAgent[T]):
    """RecollectionAgent with context-dependent recall.

    The same cue retrieves different memories depending on:
    - Current task (what am I doing?)
    - Emotional state (how am I feeling?)
    - Environment (where am I?)

    Based on encoding specificity principle.
    """

    def __init__(
        self,
        memory: HolographicMemory[T],
        reconstructor: Optional[Reconstructor[T]] = None,
        task_weight: float = 0.4,
        mood_weight: float = 0.3,
        location_weight: float = 0.3,
    ):
        """Initialize with context weights."""
        super().__init__(memory, reconstructor)
        self._task_weight = task_weight
        self._mood_weight = mood_weight
        self._location_weight = location_weight

    async def invoke_with_context(
        self,
        cue: Cue,
        current_task: Optional[str] = None,
        current_mood: Optional[str] = None,
        current_location: Optional[str] = None,
    ) -> Recollection[T]:
        """Recall with context boosting.

        Args:
            cue: The retrieval cue
            current_task: Current task context
            current_mood: Current emotional state
            current_location: Current location/environment

        Returns:
            Context-boosted recollection
        """
        # Get base resonant patterns
        resonant = await self._retrieve_resonant(
            cue,
            self._default_limit * 2,  # Get more, then filter
            self._default_threshold,
        )

        # Apply context boosting
        boosted = []
        for r in resonant:
            boost = self._compute_context_boost(
                r.pattern,
                current_task,
                current_mood,
                current_location,
            )
            # Create new ResonanceResult with boosted similarity
            boosted.append(
                ResonanceResult(
                    pattern=r.pattern,
                    similarity=min(1.0, r.similarity * boost),
                    resolution=r.resolution,
                )
            )

        # Re-sort and limit
        boosted.sort(key=lambda r: r.effective_score, reverse=True)
        boosted = boosted[: self._default_limit]

        resolution = self._compute_resolution(boosted)
        request = ReconstructionRequest(
            cue=cue,
            resonant_patterns=boosted,
            resolution=resolution,
        )

        return await self._reconstructor.reconstruct(request)

    def _compute_context_boost(
        self,
        pattern: Any,
        task: Optional[str],
        mood: Optional[str],
        location: Optional[str],
    ) -> float:
        """Compute context relevance boost (0.5 to 1.5)."""
        # Check if pattern has context metadata
        context = getattr(pattern, "context", {}) or {}

        boosts = []

        if task and "task" in context:
            match = 1.0 if task.lower() in context["task"].lower() else 0.5
            boosts.append(match * self._task_weight)

        if mood and "mood" in context:
            match = 1.0 if mood.lower() == context["mood"].lower() else 0.5
            boosts.append(match * self._mood_weight)

        if location and "location" in context:
            match = 1.0 if location.lower() in context["location"].lower() else 0.5
            boosts.append(match * self._location_weight)

        if not boosts:
            return 1.0

        # Return boost factor (0.5 to 1.5)
        avg_boost = sum(boosts) / len(boosts)
        return 0.5 + avg_boost
