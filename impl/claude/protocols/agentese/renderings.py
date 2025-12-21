"""
AGENTESE Phase 3: Polymorphic Renderings

Observer-specific renderings for manifest() operations.

The key insight: the same entity renders differently based on who observes it.
An architect sees blueprints, a poet sees metaphors, an economist sees values.

Example:
    >>> house = world.house
    >>> architect_view = await house.manifest(architect_umwelt)  # BlueprintRendering
    >>> poet_view = await house.manifest(poet_umwelt)  # PoeticRendering
    >>> economist_view = await house.manifest(economist_umwelt)  # EconomicRendering

This module extends the base renderings from node.py with additional
archetype-specific rendering types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from .node import (
    BasicRendering,
    BlueprintRendering,
    EconomicRendering,
    PoeticRendering,
    Renderable,
)

# === Additional Rendering Types ===


@dataclass(frozen=True)
class ScientificRendering:
    """
    Scientific rendering for scientist archetypes.

    Focuses on measurable properties, hypotheses, and evidence.
    """

    entity: str
    measurements: dict[str, Any] = field(default_factory=dict)
    observations: tuple[str, ...] = ()
    hypotheses: tuple[str, ...] = ()
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "scientific",
            "entity": self.entity,
            "measurements": self.measurements,
            "observations": list(self.observations),
            "hypotheses": list(self.hypotheses),
            "confidence": self.confidence,
        }

    def to_text(self) -> str:
        lines = [f"SCIENTIFIC ANALYSIS: {self.entity}"]
        if self.measurements:
            lines.append(f"Measurements: {self.measurements}")
        if self.observations:
            lines.append("Observations:")
            for obs in self.observations:
                lines.append(f"  - {obs}")
        if self.hypotheses:
            lines.append(f"Hypotheses: {list(self.hypotheses)}")
        lines.append(f"Confidence: {self.confidence:.2%}")
        return "\n".join(lines)


@dataclass(frozen=True)
class DeveloperRendering:
    """
    Technical rendering for developer archetypes.

    Focuses on code structure, dependencies, and build status.
    """

    entity: str
    language: str = ""
    dependencies: tuple[str, ...] = ()
    structure: dict[str, Any] = field(default_factory=dict)
    build_status: str = "unknown"
    test_coverage: float = 0.0
    issues: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "developer",
            "entity": self.entity,
            "language": self.language,
            "dependencies": list(self.dependencies),
            "structure": self.structure,
            "build_status": self.build_status,
            "test_coverage": self.test_coverage,
            "issues": list(self.issues),
        }

    def to_text(self) -> str:
        lines = [f"TECHNICAL: {self.entity}"]
        if self.language:
            lines.append(f"Language: {self.language}")
        lines.append(f"Build: {self.build_status} | Coverage: {self.test_coverage:.1%}")
        if self.dependencies:
            lines.append(f"Dependencies: {', '.join(self.dependencies)}")
        if self.issues:
            lines.append("Issues:")
            for issue in self.issues:
                lines.append(f"  - {issue}")
        return "\n".join(lines)


@dataclass(frozen=True)
class AdminRendering:
    """
    Operations rendering for admin archetypes.

    Focuses on system health, metrics, and configuration.
    """

    entity: str
    status: str = "unknown"
    health: float = 1.0
    metrics: dict[str, float] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    alerts: tuple[str, ...] = ()
    last_updated: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "admin",
            "entity": self.entity,
            "status": self.status,
            "health": self.health,
            "metrics": self.metrics,
            "config": self.config,
            "alerts": list(self.alerts),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    def to_text(self) -> str:
        lines = [f"SYSTEM: {self.entity}"]
        lines.append(f"Status: {self.status} | Health: {self.health:.1%}")
        if self.metrics:
            lines.append(f"Metrics: {self.metrics}")
        if self.alerts:
            lines.append(f"Alerts: {len(self.alerts)} active")
            for alert in self.alerts[:3]:  # Show first 3
                lines.append(f"  ! {alert}")
        return "\n".join(lines)


@dataclass(frozen=True)
class PhilosopherRendering:
    """
    Conceptual rendering for philosopher archetypes.

    Focuses on definitions, relations, and dialectical structure.
    """

    concept: str
    definition: str = ""
    essence: str = ""
    thesis: str = ""
    antithesis: str = ""
    synthesis: str = ""
    related_concepts: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "philosophical",
            "concept": self.concept,
            "definition": self.definition,
            "essence": self.essence,
            "dialectic": {
                "thesis": self.thesis,
                "antithesis": self.antithesis,
                "synthesis": self.synthesis,
            },
            "related_concepts": list(self.related_concepts),
        }

    def to_text(self) -> str:
        lines = [f"CONCEPT: {self.concept}"]
        if self.definition:
            lines.append(f"Definition: {self.definition}")
        if self.essence:
            lines.append(f"Essence: {self.essence}")
        if self.thesis:
            lines.append("Dialectic:")
            lines.append(f"  Thesis: {self.thesis}")
            lines.append(f"  Antithesis: {self.antithesis}")
            lines.append(f"  Synthesis: {self.synthesis}")
        if self.related_concepts:
            lines.append(f"Related: {', '.join(self.related_concepts)}")
        return "\n".join(lines)


@dataclass(frozen=True)
class MemoryRendering:
    """
    Memory rendering for self.* context.

    Shows memory state, checkpoints, and consolidation status.
    """

    memory_count: int = 0
    consolidated: int = 0
    temporary: int = 0
    checkpoints: tuple[str, ...] = ()
    last_consolidation: datetime | None = None
    capacity_used: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "memory",
            "memory_count": self.memory_count,
            "consolidated": self.consolidated,
            "temporary": self.temporary,
            "checkpoints": list(self.checkpoints),
            "last_consolidation": self.last_consolidation.isoformat()
            if self.last_consolidation
            else None,
            "capacity_used": self.capacity_used,
        }

    def to_text(self) -> str:
        lines = ["MEMORY STATE"]
        lines.append(
            f"Total: {self.memory_count} | Consolidated: {self.consolidated} | Temporary: {self.temporary}"
        )
        lines.append(f"Capacity: {self.capacity_used:.1%}")
        if self.checkpoints:
            lines.append(f"Checkpoints: {', '.join(self.checkpoints[-3:])}")  # Show last 3
        return "\n".join(lines)


@dataclass(frozen=True)
class EntropyRendering:
    """
    Entropy rendering for void.* context (Accursed Share).

    Shows entropy budget and serendipity state.
    """

    remaining: float = 0.0
    total: float = 100.0
    history_length: int = 0
    last_sip: float = 0.0
    gratitude_balance: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "entropy",
            "remaining": self.remaining,
            "total": self.total,
            "percentage": self.remaining / self.total if self.total > 0 else 0.0,
            "history_length": self.history_length,
            "last_sip": self.last_sip,
            "gratitude_balance": self.gratitude_balance,
        }

    def to_text(self) -> str:
        pct = (self.remaining / self.total * 100) if self.total > 0 else 0
        lines = ["ACCURSED SHARE"]
        lines.append(f"Entropy: {self.remaining:.1f}/{self.total:.1f} ({pct:.1f}%)")
        lines.append(f"History: {self.history_length} draws | Last: {self.last_sip:.3f}")
        lines.append(f"Gratitude: {self.gratitude_balance:.2f}")
        return "\n".join(lines)


@dataclass(frozen=True)
class TemporalRendering:
    """
    Temporal rendering for time.* context.

    Shows traces, scheduled actions, and temporal state.
    """

    mark_count: int = 0
    scheduled_count: int = 0
    earliest_trace: datetime | None = None
    latest_trace: datetime | None = None
    next_scheduled: datetime | None = None
    horizon: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "temporal",
            "mark_count": self.mark_count,
            "scheduled_count": self.scheduled_count,
            "earliest_trace": self.earliest_trace.isoformat() if self.earliest_trace else None,
            "latest_trace": self.latest_trace.isoformat() if self.latest_trace else None,
            "next_scheduled": self.next_scheduled.isoformat() if self.next_scheduled else None,
            "horizon": self.horizon,
        }

    def to_text(self) -> str:
        lines = ["TEMPORAL STATE"]
        lines.append(f"Traces: {self.mark_count} | Scheduled: {self.scheduled_count}")
        if self.earliest_trace and self.latest_trace:
            lines.append(f"Range: {self.earliest_trace} → {self.latest_trace}")
        if self.next_scheduled:
            lines.append(f"Next scheduled: {self.next_scheduled}")
        if self.horizon:
            lines.append(f"Horizon: {self.horizon}")
        return "\n".join(lines)


# === Rendering Factory ===


@runtime_checkable
class RenderingFactory(Protocol):
    """Protocol for rendering factories."""

    def create(self, archetype: str, entity: str, state: dict[str, Any]) -> Renderable:
        """Create a rendering for an archetype."""
        ...


@dataclass
class StandardRenderingFactory:
    """
    Factory for creating archetype-specific renderings.

    Maps archetypes to rendering types and creates appropriate
    renderings based on entity state.
    """

    def create(
        self,
        archetype: str,
        entity: str,
        state: dict[str, Any],
    ) -> Renderable:
        """
        Create a rendering appropriate for the archetype.

        Args:
            archetype: The observer's archetype
            entity: The entity being rendered
            state: Entity state to render

        Returns:
            Archetype-appropriate Renderable
        """
        match archetype:
            case "architect":
                return self._create_blueprint(entity, state)
            case "poet":
                return self._create_poetic(entity, state)
            case "economist":
                return self._create_economic(entity, state)
            case "scientist":
                return self._create_scientific(entity, state)
            case "developer":
                return self._create_developer(entity, state)
            case "admin":
                return self._create_admin(entity, state)
            case "philosopher":
                return self._create_philosopher(entity, state)
            case _:
                return self._create_basic(entity, state)

    def _create_blueprint(self, entity: str, state: dict[str, Any]) -> BlueprintRendering:
        return BlueprintRendering(
            dimensions=state.get("dimensions", {}),
            materials=tuple(state.get("materials", [])),
            structural_analysis={
                "load_bearing": state.get("load_bearing", []),
                "stress_points": state.get("stress_points", []),
                "integrity": state.get("integrity", 1.0),
            },
        )

    def _create_poetic(self, entity: str, state: dict[str, Any]) -> PoeticRendering:
        return PoeticRendering(
            description=state.get("description", f"A presence called {entity}"),
            metaphors=tuple(state.get("metaphors", [])),
            mood=state.get("mood", "contemplative"),
        )

    def _create_economic(self, entity: str, state: dict[str, Any]) -> EconomicRendering:
        return EconomicRendering(
            market_value=state.get("value", 0.0),
            comparable_sales=tuple(state.get("comparables", [])),
            appreciation_forecast=state.get("forecast", {}),
        )

    def _create_scientific(self, entity: str, state: dict[str, Any]) -> ScientificRendering:
        return ScientificRendering(
            entity=entity,
            measurements=state.get("measurements", {}),
            observations=tuple(state.get("observations", [])),
            hypotheses=tuple(state.get("hypotheses", [])),
            confidence=state.get("confidence", 0.5),
        )

    def _create_developer(self, entity: str, state: dict[str, Any]) -> DeveloperRendering:
        return DeveloperRendering(
            entity=entity,
            language=state.get("language", ""),
            dependencies=tuple(state.get("dependencies", [])),
            structure=state.get("structure", {}),
            build_status=state.get("build_status", "unknown"),
            test_coverage=state.get("test_coverage", 0.0),
            issues=tuple(state.get("issues", [])),
        )

    def _create_admin(self, entity: str, state: dict[str, Any]) -> AdminRendering:
        return AdminRendering(
            entity=entity,
            status=state.get("status", "unknown"),
            health=state.get("health", 1.0),
            metrics=state.get("metrics", {}),
            config=state.get("config", {}),
            alerts=tuple(state.get("alerts", [])),
        )

    def _create_philosopher(self, entity: str, state: dict[str, Any]) -> PhilosopherRendering:
        return PhilosopherRendering(
            concept=entity,
            definition=state.get("definition", ""),
            essence=state.get("essence", ""),
            thesis=state.get("thesis", ""),
            antithesis=state.get("antithesis", ""),
            synthesis=state.get("synthesis", ""),
            related_concepts=tuple(state.get("related", [])),
        )

    def _create_basic(self, entity: str, state: dict[str, Any]) -> BasicRendering:
        return BasicRendering(
            summary=f"{entity}",
            content=state.get("description", f"An entity called {entity}"),
            metadata=state.get("metadata", {}),
        )


# === Context-Specific Rendering Factories ===


@dataclass
class MemoryRenderingFactory:
    """Factory for self.memory renderings."""

    def create(self, memories: dict[str, Any], checkpoints: list[str]) -> MemoryRendering:
        consolidated = sum(1 for m in memories.values() if not m.get("temporary", True))
        temporary = len(memories) - consolidated

        return MemoryRendering(
            memory_count=len(memories),
            consolidated=consolidated,
            temporary=temporary,
            checkpoints=tuple(checkpoints[-5:]),
            capacity_used=min(1.0, len(memories) / 1000),
        )


@dataclass
class EntropyRenderingFactory:
    """Factory for void.entropy renderings."""

    def create(
        self, pool_remaining: float, pool_total: float, history: list[Any]
    ) -> EntropyRendering:
        last_sip = history[-1].get("amount", 0.0) if history else 0.0

        return EntropyRendering(
            remaining=pool_remaining,
            total=pool_total,
            history_length=len(history),
            last_sip=last_sip,
        )


@dataclass
class TemporalRenderingFactory:
    """Factory for time.* renderings."""

    def create(
        self,
        traces: list[Any],
        scheduled: list[Any],
    ) -> TemporalRendering:
        earliest = traces[0]["timestamp"] if traces else None
        latest = traces[-1]["timestamp"] if traces else None
        next_sched = min((s["at"] for s in scheduled), default=None) if scheduled else None

        return TemporalRendering(
            mark_count=len(traces),
            scheduled_count=len(scheduled),
            earliest_trace=earliest,
            latest_trace=latest,
            next_scheduled=next_sched,
        )


# === Helper Functions ===


def create_rendering_factory() -> StandardRenderingFactory:
    """Create a standard rendering factory."""
    return StandardRenderingFactory()


def render_for_archetype(
    archetype: str,
    entity: str,
    state: dict[str, Any],
    factory: StandardRenderingFactory | None = None,
) -> Renderable:
    """
    Convenience function to render an entity for an archetype.

    Args:
        archetype: The observer's archetype
        entity: The entity being rendered
        state: Entity state to render
        factory: Optional custom factory

    Returns:
        Archetype-appropriate Renderable
    """
    if factory is None:
        factory = StandardRenderingFactory()
    return factory.create(archetype, entity, state)


__all__ = [
    # Re-export base renderings
    "Renderable",
    "BasicRendering",
    "BlueprintRendering",
    "PoeticRendering",
    "EconomicRendering",
    # New rendering types
    "ScientificRendering",
    "DeveloperRendering",
    "AdminRendering",
    "PhilosopherRendering",
    "MemoryRendering",
    "EntropyRendering",
    "TemporalRendering",
    # Factories
    "RenderingFactory",
    "StandardRenderingFactory",
    "MemoryRenderingFactory",
    "EntropyRenderingFactory",
    "TemporalRenderingFactory",
    "create_rendering_factory",
    # Helper
    "render_for_archetype",
]
