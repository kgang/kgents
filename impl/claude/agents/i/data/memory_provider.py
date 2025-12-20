"""
Memory Data Provider for Four Pillars visualization.

Provides M-gent memory data to I-gent dashboard screens:
- Memory Crystal: Holographic patterns with resolution levels
- Pheromone Field: Stigmergic traces and gradients
- Language Games: Wittgensteinian memory access
- Active Inference: Free energy budgets and beliefs

Both demo mode (synthetic data) and real mode (live agent memory) supported.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from agents.m import (
        ActiveInferenceAgent,
        LanguageGame,
        MemoryCrystal,
        PheromoneField,
    )


class CrystalStats(TypedDict):
    """Type-safe crystal statistics."""

    dimension: int
    concept_count: int
    hot_count: int
    avg_resolution: float
    min_resolution: float
    max_resolution: float


class FieldStats(TypedDict):
    """Type-safe pheromone field statistics."""

    concept_count: int
    trace_count: int
    deposit_count: int
    evaporation_count: int
    avg_intensity: float
    decay_rate: float


class InferenceStats(TypedDict):
    """Type-safe inference statistics."""

    precision: float
    entropy: float
    concept_count: int
    memory_count: int


class MemoryHealthReport(TypedDict):
    """Overall memory health summary."""

    health_score: float
    crystal_health: float
    field_health: float
    inference_health: float
    status: str


@dataclass
class MemoryDataProvider:
    """
    Provides Four Pillars data to I-gent dashboard.

    In demo mode, creates synthetic data.
    In real mode, connects to live agent memory.
    """

    demo_mode: bool = False

    # Four Pillars instances
    memory_crystal: "MemoryCrystal[Any] | None" = None
    pheromone_field: "PheromoneField | None" = None
    inference_agent: "ActiveInferenceAgent[Any] | None" = None
    language_games: dict[str, "LanguageGame[Any]"] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.demo_mode:
            self._setup_demo_data()

    def _setup_demo_data(self) -> None:
        """Create demo data for visualization."""
        try:
            from agents.m import (
                ActiveInferenceAgent,
                Belief,
                MemoryCrystal,
                PheromoneField,
                create_dialectical_game,
                create_recall_game,
            )

            # Crystal with varied resolutions
            self.memory_crystal = MemoryCrystal[str](dimension=64)

            # Hot patterns (frequently accessed)
            self.memory_crystal.store(
                "python_async",
                "Python async/await patterns for concurrent programming",
                [0.9] * 64,
            )
            self.memory_crystal.store(
                "rust_ownership",
                "Rust ownership model and borrowing rules",
                [0.85] * 64,
            )

            # Warm patterns
            self.memory_crystal.store(
                "typescript_generics",
                "TypeScript generic type patterns",
                [0.6] * 64,
            )
            self.memory_crystal.store(
                "functional_patterns",
                "Functional programming patterns - map, filter, reduce",
                [0.55] * 64,
            )

            # Cool patterns
            self.memory_crystal.store(
                "docker_basics",
                "Docker containerization basics",
                [0.4] * 64,
            )

            # Cold patterns (candidates for demotion)
            self.memory_crystal.store(
                "old_api_notes",
                "Notes about deprecated API v1",
                [0.2] * 64,
            )
            self.memory_crystal.demote("old_api_notes", factor=0.3)

            # Pheromone field with traces
            self.pheromone_field = PheromoneField(decay_rate=0.1)

            # Inference agent with meaningful priors
            belief = Belief(
                distribution={
                    "python": 0.35,
                    "rust": 0.25,
                    "typescript": 0.20,
                    "functional": 0.12,
                    "other": 0.08,
                },
                precision=1.2,
            )
            self.inference_agent = ActiveInferenceAgent(belief)

            # Language games
            self.language_games = {
                "recall": create_recall_game(),
                "dialectical": create_dialectical_game(),
            }

        except ImportError:
            # M-gent not available
            pass

    async def deposit_demo_traces(self) -> None:
        """Deposit some demo pheromone traces."""
        if self.pheromone_field is None:
            return

        # Create a gradient showing usage patterns
        await self.pheromone_field.deposit("python", 5.0, "coder_agent")
        await self.pheromone_field.deposit("python", 3.0, "reviewer_agent")
        await self.pheromone_field.deposit("python", 2.0, "test_agent")
        await self.pheromone_field.deposit("rust", 4.0, "coder_agent")
        await self.pheromone_field.deposit("rust", 1.5, "test_agent")
        await self.pheromone_field.deposit("typescript", 2.0, "coder_agent")
        await self.pheromone_field.deposit("typescript", 1.0, "reviewer_agent")
        await self.pheromone_field.deposit("functional", 1.5, "coder_agent")
        await self.pheromone_field.deposit("docker", 0.5, "devops_agent")

    def get_crystal_stats(self) -> CrystalStats | None:
        """Get crystal statistics with type safety."""
        if self.memory_crystal is None:
            return None

        stats = self.memory_crystal.stats()
        return CrystalStats(
            dimension=stats["dimension"],
            concept_count=stats["concept_count"],
            hot_count=stats["hot_count"],
            avg_resolution=stats["avg_resolution"],
            min_resolution=stats["min_resolution"],
            max_resolution=stats["max_resolution"],
        )

    async def get_field_stats(self) -> FieldStats | None:
        """Get pheromone field statistics with type safety."""
        if self.pheromone_field is None:
            return None

        stats = self.pheromone_field.stats()
        return FieldStats(
            concept_count=stats["concept_count"],
            trace_count=stats["trace_count"],
            deposit_count=stats["deposit_count"],
            evaporation_count=stats["evaporation_count"],
            avg_intensity=stats["avg_intensity"],
            decay_rate=stats["decay_rate"],
        )

    def get_inference_stats(self) -> InferenceStats | None:
        """Get active inference statistics with type safety."""
        if self.inference_agent is None:
            return None

        return InferenceStats(
            precision=self.inference_agent.belief.precision,
            entropy=self.inference_agent.belief.entropy(),
            concept_count=len(self.inference_agent.belief.distribution),
            memory_count=len(self.inference_agent._memory_budgets),
        )

    def compute_health(self) -> MemoryHealthReport:
        """Compute overall memory health score."""
        crystal_health = 0.0
        field_health = 0.0
        inference_health = 0.0

        # Crystal health based on average resolution
        if self.memory_crystal is not None:
            stats = self.memory_crystal.stats()
            crystal_health = stats["avg_resolution"]

        # Field health based on activity (deposit count)
        if self.pheromone_field is not None:
            stats = self.pheromone_field.stats()
            # Normalize deposit count (assume 10+ is healthy)
            deposit_health = min(1.0, stats["deposit_count"] / 10.0)
            # Penalize if no traces
            trace_health = 1.0 if stats["trace_count"] > 0 else 0.0
            field_health = (deposit_health + trace_health) / 2.0

        # Inference health based on precision
        if self.inference_agent is not None:
            # Precision > 1 is good, < 1 is bad
            precision = self.inference_agent.belief.precision
            inference_health = min(1.0, precision / 1.5)

        # Overall health is weighted average
        health_score = crystal_health * 0.4 + field_health * 0.3 + inference_health * 0.3

        # Status thresholds
        if health_score >= 0.7:
            status = "HEALTHY"
        elif health_score >= 0.4:
            status = "DEGRADED"
        else:
            status = "CRITICAL"

        return MemoryHealthReport(
            health_score=health_score,
            crystal_health=crystal_health,
            field_health=field_health,
            inference_health=inference_health,
            status=status,
        )

    def render_health_indicator(self) -> str:
        """Render compact memory health indicator for status bars."""
        report = self.compute_health()

        # Color based on status
        if report["status"] == "HEALTHY":
            color = "#1dd1a1"
        elif report["status"] == "DEGRADED":
            color = "#feca57"
        else:
            color = "#ff6b6b"

        return f"MEM: [{color}]{report['health_score']:.0%}[/]"


def create_memory_provider(demo_mode: bool = False) -> MemoryDataProvider:
    """Factory function for memory data provider."""
    return MemoryDataProvider(demo_mode=demo_mode)


async def create_memory_provider_async(demo_mode: bool = False) -> MemoryDataProvider:
    """
    Factory function for memory data provider with demo traces.

    If demo_mode is True, also deposits demo pheromone traces.
    """
    provider = MemoryDataProvider(demo_mode=demo_mode)
    if demo_mode:
        await provider.deposit_demo_traces()
    return provider


__all__ = [
    "MemoryDataProvider",
    "CrystalStats",
    "FieldStats",
    "InferenceStats",
    "MemoryHealthReport",
    "create_memory_provider",
    "create_memory_provider_async",
]
