"""
E-gent v2 Viral Library: Fitness-based evolutionary memory.

The Viral Library is NOT a filing cabinet—it's a LIVING library where:
- Strong patterns reproduce (high fitness → more offspring)
- Weak patterns die (low fitness → eventual removal)
- The library EVOLVES toward fitness, not just accumulates

Unlike passive memory that records outcomes, the Viral Library:
1. Stores successful DNA (patterns from successful Phages)
2. Weakens failed patterns (fitness decay)
3. Guides mutation (semantic retrieval via L-gent)
4. Informs markets (pattern fitness → odds calculation)
5. Prunes weak patterns (natural selection)

From spec/e-gents/memory.md:
> "The library that never forgets will never learn. Evolution requires death."

Spec Reference: spec/e-gents/memory.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, Callable

from .types import (
    Phage,
    MutationVector,
)


# =============================================================================
# Viral Pattern (DNA of successful mutations)
# =============================================================================


@dataclass
class ViralPattern:
    """
    A reusable mutation pattern with fitness tracking.

    From spec:
    > ViralPattern stores DNA and fitness, NOT outcomes.
    > fitness = success_rate × avg_impact

    Fitness interpretation:
    - > 1.0: High-value pattern (succeeds often with high impact)
    - 0.5-1.0: Viable pattern (moderate success, moderate impact)
    - < 0.5: Weak pattern (candidate for pruning)
    """

    signature: str  # Unique pattern identifier
    dna: str  # Template code/diff pattern
    schema_signature: str = ""  # L-gent schema that generated this

    # Fitness tracking
    success_count: int = 0
    failure_count: int = 0
    total_impact: float = 0.0  # Cumulative impact from successes
    avg_cost: float = 0.0  # Average token cost

    # Context
    exemplar_module: str = ""  # First module where pattern succeeded
    category: str = ""  # Pattern category (substitute, extract, etc.)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)

    # Embedding (for L-gent semantic retrieval)
    embedding: list[float] = field(default_factory=list)

    @property
    def fitness(self) -> float:
        """
        Darwinian fitness: success_rate × avg_impact.

        This is the core selection criterion for the library.
        Patterns with high fitness reproduce; low fitness die.
        """
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0

        success_rate = self.success_count / total
        avg_impact = self.total_impact / max(1, self.success_count)

        return success_rate * avg_impact

    @property
    def success_rate(self) -> float:
        """Fraction of uses that succeeded."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return self.success_count / total

    @property
    def avg_impact_per_success(self) -> float:
        """Average impact per successful use."""
        if self.success_count == 0:
            return 0.0
        return self.total_impact / self.success_count

    @property
    def total_uses(self) -> int:
        """Total number of times this pattern was used."""
        return self.success_count + self.failure_count

    def reinforce(self, impact: float, cost: float = 0.0) -> None:
        """
        Reinforce pattern after success.

        Args:
            impact: Measured impact of this success
            cost: Token cost for this use
        """
        self.success_count += 1
        self.total_impact += impact
        self.last_used = datetime.now()

        # Update average cost
        if cost > 0:
            total_uses = self.success_count + self.failure_count
            self.avg_cost = (
                (self.avg_cost * (total_uses - 1) + cost) / total_uses
                if total_uses > 1
                else cost
            )

    def weaken(self) -> None:
        """Weaken pattern after failure."""
        self.failure_count += 1
        self.last_used = datetime.now()


# =============================================================================
# Library Operations (Input/Output Types)
# =============================================================================


@dataclass
class LibraryStats:
    """Statistics about the Viral Library."""

    total_patterns: int = 0
    total_successes: int = 0
    total_failures: int = 0
    avg_fitness: float = 0.0
    high_fitness_patterns: int = 0  # fitness > 1.0
    viable_patterns: int = 0  # fitness 0.5-1.0
    low_fitness_patterns: int = 0  # fitness < 0.5
    patterns_by_category: dict[str, int] = field(default_factory=dict)


@dataclass
class MutationSuggestion:
    """
    A mutation suggestion from the library.

    Includes both the pattern and a relevance score
    based on semantic similarity × fitness.
    """

    pattern: ViralPattern
    score: float  # similarity × fitness
    similarity: float  # Semantic similarity to context
    mutation_hint: str  # Suggestion for applying this pattern

    def to_mutation_vector(
        self,
        original_code: str,
        temperature: float = 1.0,
    ) -> MutationVector:
        """
        Convert suggestion to a MutationVector for the Mutator.

        Note: The actual mutation code is generated by the caller,
        this just provides the vector template.
        """
        return MutationVector(
            schema_signature=self.pattern.schema_signature,
            original_code=original_code,
            mutated_code="",  # To be filled by Mutator
            description=self.mutation_hint,
            confidence=self.pattern.success_rate,
            enthalpy_delta=-0.3,  # Default; should be from schema
            entropy_delta=0.1,
            temperature=temperature,
        )


@dataclass
class PruneReport:
    """Report from a prune operation."""

    pruned_count: int
    remaining_count: int
    avg_fitness_before: float
    avg_fitness_after: float
    pruned_signatures: list[str] = field(default_factory=list)


# =============================================================================
# L-gent Integration Protocol
# =============================================================================


class SemanticRegistryProtocol(Protocol):
    """Protocol for L-gent SemanticRegistry integration."""

    async def register_archetype(
        self,
        name: str,
        embedding: list[float] | None = None,
        text: str | None = None,
        signature: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register a pattern as an archetype."""
        ...

    def deregister_archetype(self, name: str) -> bool:
        """Remove an archetype."""
        ...

    async def find_similar_archetypes(
        self,
        embedding: list[float],
        prefix: str = "",
        threshold: float = 0.5,
        top_k: int = 10,
    ) -> list[tuple[str, float]]:
        """Find similar archetypes by embedding."""
        ...

    async def embed_text(self, text: str) -> list[float]:
        """Embed text into a vector."""
        ...


class ChronicleProtocol(Protocol):
    """Protocol for N-gent chronicle integration (optional)."""

    async def record(
        self,
        event: str,
        data: dict[str, Any],
    ) -> None:
        """Record an event in the chronicle."""
        ...


# =============================================================================
# Viral Library
# =============================================================================


@dataclass
class ViralLibraryConfig:
    """Configuration for the Viral Library."""

    # Fitness thresholds
    prune_threshold: float = 0.3  # Patterns below this fitness are pruned
    high_fitness_threshold: float = 1.0  # Patterns above this are "strong"
    viable_fitness_threshold: float = 0.5  # Patterns above this are "viable"

    # Pruning behavior
    auto_prune_interval: int = 100  # Prune after N operations
    max_patterns: int = 1000  # Maximum patterns before forced prune

    # Embedding
    archetype_prefix: str = "viral:"  # Prefix for L-gent archetype names

    # Persistence
    persist_on_change: bool = True  # Auto-persist after changes


class ViralLibrary:
    """
    Fitness-based evolutionary memory for mutation patterns.

    The Viral Library stores successful mutation DNA and evolves over time:
    - Successful patterns are reinforced (fitness increases)
    - Failed patterns are weakened (fitness decreases)
    - Low-fitness patterns are pruned (natural selection)
    - Patterns guide future mutations via semantic retrieval

    From spec/e-gents/memory.md:
    > Memory is not a filing cabinet. Memory is a living library where:
    > - Strong patterns reproduce (high fitness → more offspring)
    > - Weak patterns die (low fitness → eventual removal)
    > - The library evolves toward fitness, not just accumulates

    Integration:
    - L-gent: Semantic retrieval via archetype embeddings
    - B-gent: Pattern fitness → market odds calculation
    - D-gent: Persistence (optional)
    - N-gent: Chronicle (optional)
    """

    def __init__(
        self,
        config: ViralLibraryConfig | None = None,
        l_gent: SemanticRegistryProtocol | None = None,
        n_gent: ChronicleProtocol | None = None,
        persistence_fn: Callable[[dict[str, ViralPattern]], None] | None = None,
    ) -> None:
        """
        Initialize the Viral Library.

        Args:
            config: Library configuration
            l_gent: L-gent SemanticRegistry for semantic retrieval
            n_gent: N-gent chronicle for event logging
            persistence_fn: Optional function to persist patterns
        """
        self.config = config or ViralLibraryConfig()
        self.l_gent = l_gent
        self.n_gent = n_gent
        self._persistence_fn = persistence_fn

        # Pattern storage
        self._patterns: dict[str, ViralPattern] = {}

        # Counters
        self._total_successes: int = 0
        self._total_failures: int = 0
        self._operations_since_prune: int = 0

    # -------------------------------------------------------------------
    # Core Properties
    # -------------------------------------------------------------------

    @property
    def patterns(self) -> dict[str, ViralPattern]:
        """Read-only access to patterns."""
        return dict(self._patterns)

    @property
    def total_patterns(self) -> int:
        """Total number of patterns in library."""
        return len(self._patterns)

    @property
    def total_successes(self) -> int:
        """Total successful uses across all patterns."""
        return self._total_successes

    @property
    def total_failures(self) -> int:
        """Total failed uses across all patterns."""
        return self._total_failures

    # -------------------------------------------------------------------
    # Recording Operations
    # -------------------------------------------------------------------

    async def record_success(
        self,
        phage: Phage,
        impact: float,
        cost: float = 0.0,
    ) -> ViralPattern:
        """
        Record a successful phage, reinforcing or creating a pattern.

        From spec:
        > On Phage Success:
        > - Extract pattern signature from Phage DNA
        > - If pattern exists: increment success_count, add to total_impact
        > - If pattern new: create entry, register with L-gent SemanticRegistry
        > - Update fitness score: success_rate × avg_impact

        Args:
            phage: The successful Phage
            impact: Measured impact (test coverage, complexity reduction, etc.)
            cost: Token cost for this mutation

        Returns:
            The reinforced or created pattern
        """
        signature = self._extract_signature(phage)

        if signature in self._patterns:
            # Existing pattern: reinforce
            pattern = self._patterns[signature]
            pattern.reinforce(impact, cost)
        else:
            # New pattern: birth
            pattern = await self._create_pattern(phage, impact, cost)
            self._patterns[signature] = pattern

            # Register with L-gent for semantic retrieval
            if self.l_gent:
                await self._register_with_lgent(pattern)

        self._total_successes += 1
        self._operations_since_prune += 1

        # Chronicle the event
        if self.n_gent:
            await self.n_gent.record(
                event="pattern_reinforced",
                data={
                    "signature": signature,
                    "fitness": pattern.fitness,
                    "success_count": pattern.success_count,
                },
            )

        # Auto-persist and auto-prune
        await self._maybe_persist()
        await self._maybe_auto_prune()

        return pattern

    async def record_failure(self, phage: Phage) -> ViralPattern | None:
        """
        Record a failed phage, weakening the pattern.

        From spec:
        > On Phage Failure:
        > - Find pattern by signature
        > - Increment failure_count
        > - Recalculate fitness (may drop below prune threshold)

        Args:
            phage: The failed Phage

        Returns:
            The weakened pattern, or None if pattern not found
        """
        signature = self._extract_signature(phage)

        if signature not in self._patterns:
            # Unknown pattern - can't weaken what doesn't exist
            self._total_failures += 1
            return None

        pattern = self._patterns[signature]
        pattern.weaken()

        self._total_failures += 1
        self._operations_since_prune += 1

        # Check for death condition
        if pattern.fitness < self.config.prune_threshold:
            await self._schedule_prune(signature)

        # Chronicle the event
        if self.n_gent:
            await self.n_gent.record(
                event="pattern_weakened",
                data={
                    "signature": signature,
                    "fitness": pattern.fitness,
                    "failure_count": pattern.failure_count,
                },
            )

        # Auto-persist
        await self._maybe_persist()

        return pattern

    # -------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------

    async def suggest_mutations(
        self,
        context_embedding: list[float],
        top_k: int = 10,
        min_fitness: float = 0.0,
    ) -> list[MutationSuggestion]:
        """
        Get mutation suggestions based on semantic similarity.

        From spec:
        > On Query:
        > - Use L-gent semantic similarity to find relevant patterns
        > - Return patterns sorted by (similarity × fitness)
        > - Generate MutationVectors from matching patterns

        Args:
            context_embedding: Embedding of the code context to mutate
            top_k: Maximum suggestions to return
            min_fitness: Minimum fitness threshold

        Returns:
            List of MutationSuggestions sorted by score
        """
        if not self.l_gent:
            # Fallback: return top patterns by fitness alone
            return self._suggest_by_fitness_only(top_k, min_fitness)

        # Find similar archetypes via L-gent
        similar = await self.l_gent.find_similar_archetypes(
            embedding=context_embedding,
            prefix=self.config.archetype_prefix,
            threshold=0.3,  # Low threshold, we filter by score later
            top_k=top_k * 2,  # Get extras for filtering
        )

        suggestions = []
        for archetype_name, similarity in similar:
            # Extract signature from archetype name
            signature = archetype_name[len(self.config.archetype_prefix) :]

            if signature not in self._patterns:
                continue

            pattern = self._patterns[signature]

            if pattern.fitness < min_fitness:
                continue

            # Score by similarity × fitness
            score = similarity * pattern.fitness

            suggestions.append(
                MutationSuggestion(
                    pattern=pattern,
                    score=score,
                    similarity=similarity,
                    mutation_hint=self._generate_hint(pattern),
                )
            )

        # Sort by score
        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions[:top_k]

    def get_fitness(self, signature: str) -> float:
        """
        Get fitness score for a pattern.

        Used by B-gent PredictionMarket for odds calculation.

        Args:
            signature: Pattern signature

        Returns:
            Fitness score, or 0.0 if not found
        """
        pattern = self._patterns.get(signature)
        return pattern.fitness if pattern else 0.0

    def get_pattern(self, signature: str) -> ViralPattern | None:
        """Get a pattern by signature."""
        return self._patterns.get(signature)

    def get_stats(self) -> LibraryStats:
        """
        Get library statistics.

        From spec:
        > Returns: total_patterns, total_successes, total_failures,
        > avg_fitness, high_fitness_patterns, low_fitness_patterns,
        > patterns_by_kind
        """
        if not self._patterns:
            return LibraryStats()

        fitnesses = [p.fitness for p in self._patterns.values()]
        avg_fitness = sum(fitnesses) / len(fitnesses) if fitnesses else 0.0

        high_fitness = sum(
            1 for f in fitnesses if f > self.config.high_fitness_threshold
        )
        viable = sum(
            1
            for f in fitnesses
            if self.config.viable_fitness_threshold
            <= f
            <= self.config.high_fitness_threshold
        )
        low_fitness = sum(
            1 for f in fitnesses if f < self.config.viable_fitness_threshold
        )

        by_category: dict[str, int] = {}
        for pattern in self._patterns.values():
            cat = pattern.category or "unknown"
            by_category[cat] = by_category.get(cat, 0) + 1

        return LibraryStats(
            total_patterns=len(self._patterns),
            total_successes=self._total_successes,
            total_failures=self._total_failures,
            avg_fitness=avg_fitness,
            high_fitness_patterns=high_fitness,
            viable_patterns=viable,
            low_fitness_patterns=low_fitness,
            patterns_by_category=by_category,
        )

    # -------------------------------------------------------------------
    # Pruning (Natural Selection)
    # -------------------------------------------------------------------

    async def prune(
        self,
        threshold: float | None = None,
        force: bool = False,
    ) -> PruneReport:
        """
        Remove patterns with fitness below threshold.

        From spec:
        > This is natural selection: weak patterns die,
        > making room for new experiments.

        Args:
            threshold: Fitness threshold (defaults to config)
            force: Prune even if below auto_prune_interval

        Returns:
            PruneReport with details
        """
        threshold = threshold if threshold is not None else self.config.prune_threshold

        # Calculate pre-prune stats
        avg_before = self._calculate_avg_fitness()

        # Find patterns to prune
        to_prune = [
            sig
            for sig, pattern in self._patterns.items()
            if pattern.fitness < threshold
        ]

        pruned_signatures = []
        for sig in to_prune:
            pattern = self._patterns[sig]

            # Deregister from L-gent
            if self.l_gent:
                self.l_gent.deregister_archetype(f"{self.config.archetype_prefix}{sig}")

            # Chronicle death
            if self.n_gent:
                lifespan = (datetime.now() - pattern.created_at).total_seconds()
                await self.n_gent.record(
                    event="pattern_death",
                    data={
                        "signature": sig,
                        "fitness": pattern.fitness,
                        "lifespan_seconds": lifespan,
                        "total_uses": pattern.total_uses,
                    },
                )

            # Remove from library
            del self._patterns[sig]
            pruned_signatures.append(sig)

        # Calculate post-prune stats
        avg_after = self._calculate_avg_fitness()

        # Reset prune counter
        self._operations_since_prune = 0

        # Persist changes
        await self._maybe_persist()

        return PruneReport(
            pruned_count=len(pruned_signatures),
            remaining_count=len(self._patterns),
            avg_fitness_before=avg_before,
            avg_fitness_after=avg_after,
            pruned_signatures=pruned_signatures,
        )

    # -------------------------------------------------------------------
    # Internal Helpers
    # -------------------------------------------------------------------

    def _extract_signature(self, phage: Phage) -> str:
        """Extract pattern signature from a Phage."""
        if phage.mutation:
            return phage.mutation.signature
        # Fallback: generate from phage DNA
        return phage.dna or f"phage_{phage.id}"

    async def _create_pattern(
        self,
        phage: Phage,
        impact: float,
        cost: float,
    ) -> ViralPattern:
        """Create a new pattern from a successful Phage."""
        signature = self._extract_signature(phage)

        # Get embedding if L-gent available
        embedding: list[float] = []
        if self.l_gent and phage.mutation:
            try:
                text = phage.mutation.description or phage.mutation.mutated_code[:500]
                embedding = await self.l_gent.embed_text(text)
            except Exception:
                pass  # Proceed without embedding

        return ViralPattern(
            signature=signature,
            dna=phage.mutation.mutated_code if phage.mutation else "",
            schema_signature=phage.mutation.schema_signature if phage.mutation else "",
            success_count=1,
            failure_count=0,
            total_impact=impact,
            avg_cost=cost,
            exemplar_module=phage.target_module,
            category=self._infer_category(phage),
            embedding=embedding,
        )

    def _infer_category(self, phage: Phage) -> str:
        """Infer pattern category from Phage."""
        if phage.mutation:
            sig = phage.mutation.schema_signature
            if "comprehension" in sig:
                return "substitute"
            if "extract" in sig:
                return "extract"
            if "inline" in sig:
                return "inline"
            if "flatten" in sig or "restructure" in sig:
                return "restructure"
        return "unknown"

    async def _register_with_lgent(self, pattern: ViralPattern) -> None:
        """Register pattern with L-gent SemanticRegistry."""
        if not self.l_gent:
            return

        archetype_name = f"{self.config.archetype_prefix}{pattern.signature}"

        await self.l_gent.register_archetype(
            name=archetype_name,
            embedding=pattern.embedding if pattern.embedding else None,
            text=pattern.dna[:500] if not pattern.embedding else None,
            signature=pattern.signature,
            metadata={
                "schema_signature": pattern.schema_signature,
                "category": pattern.category,
            },
        )

    def _generate_hint(self, pattern: ViralPattern) -> str:
        """Generate a mutation hint from a pattern."""
        category = pattern.category

        hints = {
            "substitute": f"Consider using {pattern.schema_signature or 'substitution pattern'}",
            "extract": "Extract this code into a separate function or constant",
            "inline": "Consider inlining this single-use variable or trivial function",
            "restructure": "Flatten nesting or restructure for clarity",
        }

        return hints.get(category, f"Apply pattern: {pattern.schema_signature}")

    async def _schedule_prune(self, signature: str) -> None:
        """Schedule a pattern for pruning (marks for next prune cycle)."""
        # For now, just log; actual pruning happens in prune()
        if self.n_gent:
            pattern = self._patterns.get(signature)
            if pattern:
                await self.n_gent.record(
                    event="pattern_scheduled_for_prune",
                    data={
                        "signature": signature,
                        "fitness": pattern.fitness,
                    },
                )

    def _calculate_avg_fitness(self) -> float:
        """Calculate average fitness across all patterns."""
        if not self._patterns:
            return 0.0
        fitnesses = [p.fitness for p in self._patterns.values()]
        return sum(fitnesses) / len(fitnesses)

    def _suggest_by_fitness_only(
        self,
        top_k: int,
        min_fitness: float,
    ) -> list[MutationSuggestion]:
        """Fallback: suggest patterns by fitness alone (no L-gent)."""
        eligible = [p for p in self._patterns.values() if p.fitness >= min_fitness]
        eligible.sort(key=lambda p: p.fitness, reverse=True)

        return [
            MutationSuggestion(
                pattern=p,
                score=p.fitness,  # No similarity component
                similarity=1.0,  # Assume perfect match
                mutation_hint=self._generate_hint(p),
            )
            for p in eligible[:top_k]
        ]

    async def _maybe_persist(self) -> None:
        """Persist patterns if configured."""
        if self.config.persist_on_change and self._persistence_fn:
            self._persistence_fn(self._patterns)

    async def _maybe_auto_prune(self) -> None:
        """Auto-prune if interval reached or max patterns exceeded."""
        should_prune = (
            self._operations_since_prune >= self.config.auto_prune_interval
            or len(self._patterns) > self.config.max_patterns
        )

        if should_prune:
            await self.prune()


# =============================================================================
# Factory Functions
# =============================================================================


def create_library(
    config: ViralLibraryConfig | None = None,
    l_gent: SemanticRegistryProtocol | None = None,
) -> ViralLibrary:
    """Create a Viral Library with default configuration."""
    return ViralLibrary(config=config, l_gent=l_gent)


def create_strict_library(
    l_gent: SemanticRegistryProtocol | None = None,
) -> ViralLibrary:
    """Create a strict library (high prune threshold, smaller capacity)."""
    config = ViralLibraryConfig(
        prune_threshold=0.5,  # Aggressive pruning
        max_patterns=500,
        auto_prune_interval=50,
    )
    return ViralLibrary(config=config, l_gent=l_gent)


def create_exploratory_library(
    l_gent: SemanticRegistryProtocol | None = None,
) -> ViralLibrary:
    """Create an exploratory library (low prune threshold, larger capacity)."""
    config = ViralLibraryConfig(
        prune_threshold=0.1,  # Keep more patterns
        max_patterns=2000,
        auto_prune_interval=200,
    )
    return ViralLibrary(config=config, l_gent=l_gent)


# =============================================================================
# Market Integration
# =============================================================================


def fitness_to_odds(fitness: float) -> float:
    """
    Convert pattern fitness to betting odds.

    From spec:
    > High fitness → low odds (likely to succeed)
    > Low fitness → high odds (unlikely to succeed)

    Args:
        fitness: Pattern fitness (0.0 to ~2.0 typical)

    Returns:
        Odds for betting (e.g., 2.0 = 2:1)
    """
    if fitness > 0.8:
        return 1.25  # 80% expected success
    elif fitness > 0.5:
        return 2.0  # 50% expected success
    elif fitness > 0.2:
        return 5.0  # 20% expected success
    else:
        return 10.0  # 10% expected success (new/weak pattern)


def odds_from_library(
    library: ViralLibrary,
    phage: Phage,
    base_odds: float = 5.0,
) -> float:
    """
    Get betting odds for a phage based on library fitness.

    Args:
        library: Viral Library to query
        phage: Phage to get odds for
        base_odds: Default odds if pattern not found

    Returns:
        Betting odds
    """
    if phage.mutation:
        fitness = library.get_fitness(phage.mutation.signature)
        if fitness > 0:
            return fitness_to_odds(fitness)

    return base_odds
