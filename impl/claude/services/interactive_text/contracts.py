"""
Interactive Text AGENTESE Contract Definitions.

Defines the core type interfaces for the Meaning Token Frontend Architecture:
- MeaningToken: Semantic primitive that carries meaning independent of rendering
- Affordance: Interaction possibility offered by a token
- Observer: Entity receiving projections with specific umwelt
- TokenDefinition: Complete definition of a meaning token type
- DocumentState: States in the document polynomial state machine

These types form the foundation of the projection-based architecture where
meaning tokens project to any observer surface through projection functors.

Contract Protocol (Phase 7: Autopoietic Architecture):
- Response() for perception aspects (manifest, hover)
- Contract() for mutation aspects (toggle, navigate)

See: .kiro/specs/meaning-token-frontend/design.md
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import uuid4

# =============================================================================
# Enums
# =============================================================================


class AffordanceAction(str, Enum):
    """Actions that can be performed on a token."""

    HOVER = "hover"
    CLICK = "click"
    RIGHT_CLICK = "right-click"
    DRAG = "drag"
    DOUBLE_CLICK = "double-click"


class ObserverDensity(str, Enum):
    """Display density preference for projections."""

    COMPACT = "compact"
    COMFORTABLE = "comfortable"
    SPACIOUS = "spacious"


class ObserverRole(str, Enum):
    """Role-based access control for affordances."""

    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"


class DocumentState(str, Enum):
    """States in the document polynomial state machine.

    Per AD-002, documents have state-dependent behavior. The polynomial
    captures valid inputs per state and transition rules.
    """

    VIEWING = "VIEWING"
    EDITING = "EDITING"
    SYNCING = "SYNCING"
    CONFLICTING = "CONFLICTING"


# =============================================================================
# Core Types
# =============================================================================


@dataclass(frozen=True)
class TokenPattern:
    """Pattern for recognizing a meaning token in text.

    Attributes:
        name: Unique identifier for this pattern
        regex: Compiled regex pattern for matching
        priority: Higher priority patterns match first (default 0)
    """

    name: str
    regex: re.Pattern[str]
    priority: int = 0

    def __post_init__(self) -> None:
        """Validate pattern configuration."""
        if not self.name:
            raise ValueError("TokenPattern name cannot be empty")


@dataclass(frozen=True)
class Affordance:
    """An interaction possibility offered by a token.

    Affordances define what actions can be performed on a token and
    how those actions are handled through AGENTESE paths.

    Attributes:
        name: Human-readable name for the affordance
        action: The type of interaction (hover, click, etc.)
        handler: AGENTESE path or callback reference for handling
        enabled: Whether this affordance is currently available
        description: Optional description for UI hints
    """

    name: str
    action: AffordanceAction
    handler: str  # AGENTESE path or callback reference
    enabled: bool = True
    description: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "action": self.action.value,
            "handler": self.handler,
            "enabled": self.enabled,
            "description": self.description,
        }


@dataclass(frozen=True)
class Observer:
    """Entity receiving projections with specific umwelt.

    The Observer represents the context in which tokens are projected.
    Different observers receive different projections based on their
    capabilities, density preferences, and roles.

    Attributes:
        id: Unique identifier for this observer
        capabilities: Set of available capabilities (llm, verification, network)
        density: Display density preference
        role: Access control role
        metadata: Additional observer-specific data
    """

    id: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    density: ObserverDensity = ObserverDensity.COMFORTABLE
    role: ObserverRole = ObserverRole.VIEWER
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        capabilities: frozenset[str] | None = None,
        density: ObserverDensity = ObserverDensity.COMFORTABLE,
        role: ObserverRole = ObserverRole.VIEWER,
        metadata: dict[str, Any] | None = None,
    ) -> Observer:
        """Create a new observer with a generated ID."""
        return cls(
            id=uuid4().hex,
            capabilities=capabilities or frozenset(),
            density=density,
            role=role,
            metadata=metadata or {},
        )

    def has_capability(self, capability: str) -> bool:
        """Check if observer has a specific capability."""
        return capability in self.capabilities

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "capabilities": list(self.capabilities),
            "density": self.density.value,
            "role": self.role.value,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class TokenDefinition:
    """Complete definition of a meaning token type.

    TokenDefinitions are registered in the TokenRegistry and define
    how tokens are recognized, what affordances they offer, and how
    they project to different targets.

    Attributes:
        name: Unique identifier for this token type
        pattern: Pattern for recognizing this token in text
        affordances: Tuple of affordances offered by this token type
        projectors: Mapping of target names to projector module paths
        description: Human-readable description of this token type
    """

    name: str
    pattern: TokenPattern
    affordances: tuple[Affordance, ...]
    projectors: dict[str, str] = field(default_factory=dict)
    description: str | None = None

    def __post_init__(self) -> None:
        """Validate token definition."""
        if not self.name:
            raise ValueError("TokenDefinition name cannot be empty")

    def get_affordance(self, action: AffordanceAction) -> Affordance | None:
        """Get affordance by action type."""
        return next((a for a in self.affordances if a.action == action), None)


# =============================================================================
# Abstract Base Classes
# =============================================================================

T = TypeVar("T")  # Projection target type


class MeaningToken(ABC, Generic[T]):
    """Base class for meaning tokens—semantic primitives that project to renderings.

    MeaningTokens are the atomic unit of interface in the projection-based
    architecture. They carry meaning independent of how they are rendered,
    and project to different observer surfaces through projection functors.

    Type Parameters:
        T: The type of the projection target (e.g., str for CLI, ReactElement for web)
    """

    @property
    @abstractmethod
    def token_type(self) -> str:
        """Token type name from registry."""
        ...

    @property
    @abstractmethod
    def source_text(self) -> str:
        """Original text that was recognized as this token."""
        ...

    @property
    @abstractmethod
    def source_position(self) -> tuple[int, int]:
        """(start, end) position in source document."""
        ...

    @property
    def token_id(self) -> str:
        """Unique identifier for this token instance."""
        # Default implementation based on position
        start, end = self.source_position
        return f"{self.token_type}:{start}:{end}"

    @abstractmethod
    async def get_affordances(self, observer: Observer) -> list[Affordance]:
        """Get available affordances for this observer.

        Affordances may be filtered based on observer capabilities and role.

        Args:
            observer: The observer requesting affordances

        Returns:
            List of available affordances for this observer
        """
        ...

    @abstractmethod
    async def project(self, target: str, observer: Observer) -> T:
        """Project token to target-specific rendering.

        Args:
            target: Target name (e.g., "cli", "web", "json")
            observer: The observer receiving the projection

        Returns:
            Target-specific rendering of this token
        """
        ...

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "token_type": self.token_type,
            "source_text": self.source_text,
            "source_position": self.source_position,
            "token_id": self.token_id,
        }


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True)
class InteractionResult:
    """Result of interacting with a token.

    Captures the outcome of a token interaction including any
    trace witness for formal verification.

    Attributes:
        success: Whether the interaction succeeded
        data: Result data from the interaction
        witness_id: ID of the trace witness (for verification)
        error: Error message if interaction failed
        timestamp: When the interaction occurred
    """

    success: bool
    data: Any = None
    witness_id: str | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def success_result(cls, data: Any, witness_id: str | None = None) -> InteractionResult:
        """Create a successful interaction result."""
        return cls(success=True, data=data, witness_id=witness_id)

    @classmethod
    def not_available(cls, action: str) -> InteractionResult:
        """Create a result for unavailable action."""
        return cls(success=False, error=f"Action '{action}' not available")

    @classmethod
    def failure(cls, error: str) -> InteractionResult:
        """Create a failed interaction result."""
        return cls(success=False, error=error)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Enums
    "AffordanceAction",
    "ObserverDensity",
    "ObserverRole",
    "DocumentState",
    # Core types
    "TokenPattern",
    "Affordance",
    "Observer",
    "TokenDefinition",
    # Abstract base
    "MeaningToken",
    # Results
    "InteractionResult",
]
