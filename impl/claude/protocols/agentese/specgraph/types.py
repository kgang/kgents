"""
SpecGraph Types: Core data structures for spec-impl compilation.

The SpecGraph represents the dependency graph of specifications.
Each node contains structured metadata for compilation.

Reference: plans/autopoietic-architecture.md (AD-009)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class SpecDomain(str, Enum):
    """Valid AGENTESE context domains."""

    WORLD = "world"
    SELF = "self"
    CONCEPT = "concept"
    VOID = "void"
    TIME = "time"


class DriftStatus(str, Enum):
    """Status of spec-impl alignment."""

    ALIGNED = "aligned"  # Spec and impl match
    DIVERGED = "diverged"  # Spec and impl differ
    MISSING_SPEC = "missing_spec"  # Impl exists without spec
    MISSING_IMPL = "missing_impl"  # Spec exists without impl
    PARTIAL = "partial"  # Some components missing
    UNKNOWN = "unknown"  # Cannot determine


@dataclass(frozen=True)
class PolynomialSpec:
    """Specification for a polynomial agent."""

    positions: tuple[str, ...]
    transition_fn: str  # Name of transition function
    directions_fn: str | None = None  # Optional directions function


@dataclass(frozen=True)
class OperationSpec:
    """Specification for an operad operation."""

    name: str
    arity: int  # -1 or 0 means variadic
    signature: str = ""
    description: str = ""
    variadic: bool = False  # Explicit variadic flag (inferred from arity <= 0 if not set)

    @property
    def is_variadic(self) -> bool:
        """Check if operation is variadic."""
        return self.variadic or self.arity <= 0


@dataclass(frozen=True)
class LawSpec:
    """Specification for an operad law."""

    name: str
    equation: str
    description: str = ""


@dataclass(frozen=True)
class OperadSpec:
    """Specification for an operad."""

    operations: tuple[OperationSpec, ...]
    laws: tuple[LawSpec, ...] = ()
    extends: str | None = None  # Parent operad to extend


@dataclass(frozen=True)
class SheafSpec:
    """Specification for sheaf coherence."""

    sections: tuple[str, ...]
    gluing_fn: str


class AspectCategory(str, Enum):
    """Category of AGENTESE aspect (matching AspectCategory in affordances.py)."""

    PERCEPTION = "perception"  # Read-only observation
    GENERATION = "generation"  # Creates new artifacts
    MUTATION = "mutation"  # Modifies existing state
    ENTROPY = "entropy"  # Draws from or returns to void


@dataclass(frozen=True)
class AspectSpec:
    """Specification for a single AGENTESE aspect."""

    name: str
    category: AspectCategory = AspectCategory.PERCEPTION
    effects: tuple[str, ...] = ()  # e.g., ("state_mutation", "llm_call")
    help: str = ""


@dataclass(frozen=True)
class AgentesePath:
    """AGENTESE path specification."""

    path: str  # e.g., "world.town"
    aspects: tuple[str, ...] = ()  # Simple aspect names (backward compatible)
    aspect_specs: tuple[AspectSpec, ...] = ()  # Rich aspect definitions (optional)

    def get_aspect_names(self) -> tuple[str, ...]:
        """Get all aspect names (from either simple or rich format)."""
        if self.aspect_specs:
            return tuple(a.name for a in self.aspect_specs)
        return self.aspects


@dataclass(frozen=True)
class ServiceSpec:
    """Specification for Layer 4 service module (Crown Jewel pattern)."""

    crown_jewel: bool = True  # Is this a Crown Jewel service?
    adapters: tuple[str, ...] = ()  # Required adapters (e.g., "crystals", "streaming")
    frontend: bool = False  # Has frontend component?
    persistence: str = ""  # Persistence strategy (e.g., "d-gent", "sqlite", "in-memory")


@dataclass
class SpecNode:
    """
    A node in the SpecGraph.

    Each spec file becomes a SpecNode with structured metadata.
    """

    # Required metadata
    domain: SpecDomain
    holon: str  # Unique identifier within domain
    source_path: Path

    # Optional structural components
    polynomial: PolynomialSpec | None = None
    operad: OperadSpec | None = None
    sheaf: SheafSpec | None = None
    agentese: AgentesePath | None = None
    service: ServiceSpec | None = None  # Layer 4 metadata

    # Computed fields
    dependencies: list[str] = field(default_factory=list)  # Other holons this depends on
    raw_content: str = ""  # Original markdown content

    @property
    def full_path(self) -> str:
        """Full AGENTESE path (domain.holon)."""
        return f"{self.domain.value}.{self.holon}"

    @property
    def has_polynomial(self) -> bool:
        return self.polynomial is not None

    @property
    def has_operad(self) -> bool:
        return self.operad is not None

    @property
    def has_sheaf(self) -> bool:
        return self.sheaf is not None

    @property
    def has_service(self) -> bool:
        return self.service is not None

    @property
    def layer_count(self) -> int:
        """Count of implemented layers (1-7 scale)."""
        count = 0
        if self.has_sheaf:
            count += 1  # Layer 1
        if self.has_polynomial:
            count += 1  # Layer 2
        if self.has_operad:
            count += 1  # Layer 3
        if self.has_service:
            count += 1  # Layer 4
        if self.agentese:
            count += 2  # Layers 5-6 (node + protocol)
        return count

    def __repr__(self) -> str:
        return f"SpecNode({self.full_path}, layers={self.layer_count})"


@dataclass
class SpecGraph:
    """
    The dependency graph of specifications.

    Nodes are SpecNodes, edges are dependencies between holons.
    """

    nodes: dict[str, SpecNode] = field(default_factory=dict)  # path -> SpecNode

    def add(self, node: SpecNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.full_path] = node

    def get(self, path: str) -> SpecNode | None:
        """Get a node by path."""
        return self.nodes.get(path)

    def roots(self) -> list[SpecNode]:
        """Get nodes with no dependencies (compilation roots)."""
        all_deps = set()
        for node in self.nodes.values():
            all_deps.update(node.dependencies)
        return [n for n in self.nodes.values() if n.full_path not in all_deps]

    def __len__(self) -> int:
        return len(self.nodes)


@dataclass
class CompileResult:
    """Result of compiling a spec to impl."""

    spec_path: str
    impl_path: str
    success: bool
    generated_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ReflectResult:
    """Result of reflecting impl to spec."""

    impl_path: str
    spec_node: SpecNode | None = None
    spec_content: str = ""  # Generated YAML frontmatter + markdown
    confidence: float = 0.0  # How confident in extraction (0-1)
    errors: list[str] = field(default_factory=list)


@dataclass
class DriftReport:
    """Report of spec-impl drift for a single module."""

    module: str
    status: DriftStatus
    spec_path: str | None = None
    impl_path: str | None = None
    spec_hash: str | None = None
    impl_hash: str | None = None
    missing_components: list[str] = field(default_factory=list)
    extra_components: list[str] = field(default_factory=list)
    details: str = ""


# === Exports ===

__all__ = [
    # Enums
    "SpecDomain",
    "DriftStatus",
    "AspectCategory",
    # Spec components
    "PolynomialSpec",
    "OperationSpec",
    "LawSpec",
    "OperadSpec",
    "SheafSpec",
    "AspectSpec",
    "AgentesePath",
    "ServiceSpec",
    # Core types
    "SpecNode",
    "SpecGraph",
    # Results
    "CompileResult",
    "ReflectResult",
    "DriftReport",
]
