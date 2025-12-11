"""
AGENTESE Test Fixtures

Provides mock observers, nodes, and Umwelts for testing.
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from ..node import (
    AgentMeta,
    BasicRendering,
    Renderable,
)
from ..logos import Logos, SimpleRegistry


# === Mock DNA Types ===


@dataclass(frozen=True)
class MockDNA:
    """Mock DNA for testing Umwelt integration."""

    name: str = "test_agent"
    archetype: str = "default"
    capabilities: tuple[str, ...] = ()


@dataclass(frozen=True)
class ArchitectDNA(MockDNA):
    """DNA for architect archetype."""

    name: str = "architect"
    archetype: str = "architect"
    capabilities: tuple[str, ...] = ("design", "measure")


@dataclass(frozen=True)
class PoetDNA(MockDNA):
    """DNA for poet archetype."""

    name: str = "poet"
    archetype: str = "poet"
    capabilities: tuple[str, ...] = ("describe", "metaphorize")


# === Mock Umwelt ===


@dataclass
class MockUmwelt:
    """
    Mock Umwelt for testing without full infrastructure.

    Implements the minimal interface needed for AGENTESE testing.
    """

    dna: MockDNA = field(default_factory=MockDNA)
    gravity: tuple[Any, ...] = ()

    def __init__(
        self,
        dna: MockDNA | None = None,
        archetype: str = "default",
        gravity: tuple[Any, ...] = (),
    ):
        """Create mock Umwelt with optional archetype shortcut."""
        if dna is not None:
            object.__setattr__(self, "dna", dna)
        else:
            object.__setattr__(self, "dna", MockDNA(archetype=archetype))
        object.__setattr__(self, "gravity", gravity)

    async def get(self) -> dict[str, Any]:
        """Return mock state."""
        return {"agent": self.dna.name}

    async def set(self, value: Any) -> None:
        """Mock state update."""
        pass

    def is_grounded(self, output: Any) -> bool:
        """Always returns True for mock."""
        return True


# === Mock Nodes ===


@dataclass
class MockNode:
    """
    Mock LogosNode for testing protocol compliance.
    """

    handle: str = "test.mock"
    _affordances: dict[str, tuple[str, ...]] = field(default_factory=dict)
    _manifest_result: Renderable | None = None

    def affordances(self, observer: AgentMeta) -> list[str]:
        """Return affordances based on archetype."""
        base = ["manifest", "witness", "affordances"]
        extra = self._affordances.get(observer.archetype, ())
        return base + list(extra)

    def lens(self, aspect: str) -> Any:
        """Return mock agent."""
        from ..node import AspectAgent

        return AspectAgent(self, aspect)

    async def manifest(self, observer: MockUmwelt) -> Renderable:
        """Return mock rendering."""
        if self._manifest_result:
            return self._manifest_result
        return BasicRendering(
            summary=f"Mock: {self.handle}",
            content=f"Rendered for {observer.dna.archetype}",
        )

    async def invoke(
        self,
        aspect: str,
        observer: MockUmwelt,
        **kwargs: Any,
    ) -> Any:
        """Mock invocation."""
        if aspect == "manifest":
            return await self.manifest(observer)
        if aspect == "affordances":
            meta = AgentMeta(
                name=observer.dna.name,
                archetype=observer.dna.archetype,
            )
            return self.affordances(meta)
        return {"aspect": aspect, "kwargs": kwargs, "observer": observer.dna.name}


# === Fixtures ===


@pytest.fixture
def mock_dna() -> MockDNA:
    """Default mock DNA."""
    return MockDNA()


@pytest.fixture
def architect_dna() -> ArchitectDNA:
    """Architect DNA."""
    return ArchitectDNA()


@pytest.fixture
def poet_dna() -> PoetDNA:
    """Poet DNA."""
    return PoetDNA()


@pytest.fixture
def mock_umwelt() -> MockUmwelt:
    """Default mock Umwelt."""
    return MockUmwelt()


@pytest.fixture
def architect_umwelt() -> MockUmwelt:
    """Architect Umwelt."""
    return MockUmwelt(dna=ArchitectDNA())


@pytest.fixture
def poet_umwelt() -> MockUmwelt:
    """Poet Umwelt."""
    return MockUmwelt(dna=PoetDNA())


@pytest.fixture
def mock_node() -> MockNode:
    """Basic mock node."""
    return MockNode()


@pytest.fixture
def polymorphic_node() -> MockNode:
    """Node with archetype-specific affordances."""
    return MockNode(
        handle="world.house",
        _affordances={
            "architect": ("renovate", "measure", "blueprint", "demolish"),
            "poet": ("describe", "metaphorize", "inhabit"),
            "economist": ("appraise", "forecast", "compare"),
        },
    )


@pytest.fixture
def agent_meta() -> AgentMeta:
    """Default agent metadata."""
    return AgentMeta(name="test", archetype="default")


@pytest.fixture
def architect_meta() -> AgentMeta:
    """Architect metadata."""
    return AgentMeta(name="architect", archetype="architect", capabilities=("design",))


@pytest.fixture
def poet_meta() -> AgentMeta:
    """Poet metadata."""
    return AgentMeta(name="poet", archetype="poet", capabilities=("write",))


@pytest.fixture
def simple_registry() -> SimpleRegistry:
    """Empty registry."""
    return SimpleRegistry()


@pytest.fixture
def populated_registry() -> SimpleRegistry:
    """Registry with some nodes."""
    registry = SimpleRegistry()
    registry.register("world.house", MockNode(handle="world.house"))
    registry.register("world.garden", MockNode(handle="world.garden"))
    registry.register("concept.justice", MockNode(handle="concept.justice"))
    return registry


@pytest.fixture
def temp_spec_dir():
    """Temporary spec directory for JIT testing."""
    with TemporaryDirectory() as tmpdir:
        spec_root = Path(tmpdir)

        # Create world context directory
        world_dir = spec_root / "world"
        world_dir.mkdir()

        # Create example spec
        example_spec = world_dir / "library.md"
        example_spec.write_text(
            """# Library

A collection of books.

## Affordances

- manifest: View the library
- browse: Search for books
- borrow: Check out a book
"""
        )

        yield spec_root


@pytest.fixture
def logos(simple_registry: SimpleRegistry) -> Logos:
    """Basic Logos resolver."""
    return Logos(registry=simple_registry)


@pytest.fixture
def logos_with_nodes(populated_registry: SimpleRegistry) -> Logos:
    """Logos with pre-populated nodes."""
    return Logos(registry=populated_registry)


@pytest.fixture
def logos_with_specs(temp_spec_dir: Path) -> Logos:
    """Logos with spec directory for JIT testing."""
    return Logos(registry=SimpleRegistry(), spec_root=temp_spec_dir)
