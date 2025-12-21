"""
Scope: Explicit Context Contract with Budget Constraints.

A Scope defines:
- What handles are accessible (scope)
- What resources can be consumed (budget)
- When access expires (expiry)

Every AGENTESE invocation should eventually reference a Scope,
making context contracts explicit and priced.

Philosophy:
    "Context is not free. Every token, every second, every operation
    has a cost. Scopes make this cost explicit, enabling resource-
    aware agent behavior."

Rename History:
    Scope → Scope (spec/protocols/witness-primitives.md)
    "Scope of work" - clearer than religious connotation

Laws:
- Law 1 (Budget Enforcement): Exceeding budget triggers review (not silent failure)
- Law 2 (Immutability): Scopes are frozen after creation
- Law 3 (Expiry Honored): Expired Scopes deny access

See: spec/protocols/witness-primitives.md
See: docs/skills/crown-jewel-patterns.md (Pattern 7: Append-Only History)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, NewType
from uuid import uuid4

# =============================================================================
# Type Aliases
# =============================================================================

ScopeId = NewType("ScopeId", str)

# Backwards compatibility alias
ScopeId = ScopeId


def generate_scope_id() -> ScopeId:
    """Generate a unique Scope ID."""
    return ScopeId(f"scope-{uuid4().hex[:12]}")


# Backwards compatibility alias
generate_scope_id = generate_scope_id


# =============================================================================
# Budget
# =============================================================================


@dataclass(frozen=True)
class Budget:
    """
    Resource constraints for a Scope.

    All constraints are optional. None means unlimited.

    Fields:
    - tokens: Max LLM tokens to consume
    - time_seconds: Max wall-clock time in seconds
    - operations: Max discrete operations (API calls, file writes, etc.)
    - capital: Max cost in monetary units (for paid APIs)
    - entropy: Max entropy consumption (for randomness budget)

    Example:
        >>> budget = Budget(tokens=10000, time_seconds=300.0, operations=50)
        >>> budget.can_consume(tokens=100)  # True
        >>> budget.remaining_after(tokens=100)  # Budget(tokens=9900, ...)
    """

    tokens: int | None = None
    time_seconds: float | None = None
    operations: int | None = None
    capital: float | None = None
    entropy: float | None = None

    def can_consume(
        self,
        tokens: int = 0,
        time_seconds: float = 0.0,
        operations: int = 0,
        capital: float = 0.0,
        entropy: float = 0.0,
    ) -> bool:
        """
        Check if consumption would stay within budget.

        Returns True if all constraints allow the consumption.
        """
        if self.tokens is not None and tokens > self.tokens:
            return False
        if self.time_seconds is not None and time_seconds > self.time_seconds:
            return False
        if self.operations is not None and operations > self.operations:
            return False
        if self.capital is not None and capital > self.capital:
            return False
        if self.entropy is not None and entropy > self.entropy:
            return False
        return True

    def remaining_after(
        self,
        tokens: int = 0,
        time_seconds: float = 0.0,
        operations: int = 0,
        capital: float = 0.0,
        entropy: float = 0.0,
    ) -> Budget:
        """
        Return a new Budget with consumption deducted.

        Raises BudgetExceeded if any constraint would go negative.
        """
        new_tokens = (self.tokens - tokens) if self.tokens is not None else None
        new_time = (self.time_seconds - time_seconds) if self.time_seconds is not None else None
        new_ops = (self.operations - operations) if self.operations is not None else None
        new_capital = (self.capital - capital) if self.capital is not None else None
        new_entropy = (self.entropy - entropy) if self.entropy is not None else None

        # Check for budget exceeded
        if new_tokens is not None and new_tokens < 0:
            raise BudgetExceeded(f"Token budget exceeded: {self.tokens} - {tokens} = {new_tokens}")
        if new_time is not None and new_time < 0:
            raise BudgetExceeded(f"Time budget exceeded: {self.time_seconds} - {time_seconds}")
        if new_ops is not None and new_ops < 0:
            raise BudgetExceeded(f"Operations budget exceeded: {self.operations} - {operations}")
        if new_capital is not None and new_capital < 0:
            raise BudgetExceeded(f"Capital budget exceeded: {self.capital} - {capital}")
        if new_entropy is not None and new_entropy < 0:
            raise BudgetExceeded(f"Entropy budget exceeded: {self.entropy} - {entropy}")

        return Budget(
            tokens=new_tokens,
            time_seconds=new_time,
            operations=new_ops,
            capital=new_capital,
            entropy=new_entropy,
        )

    @property
    def is_exhausted(self) -> bool:
        """Check if any budget dimension is at zero."""
        if self.tokens is not None and self.tokens <= 0:
            return True
        if self.time_seconds is not None and self.time_seconds <= 0:
            return True
        if self.operations is not None and self.operations <= 0:
            return True
        if self.capital is not None and self.capital <= 0:
            return True
        if self.entropy is not None and self.entropy <= 0:
            return True
        return False

    @classmethod
    def unlimited(cls) -> Budget:
        """Create an unlimited budget (all None)."""
        return cls()

    @classmethod
    def standard(cls) -> Budget:
        """Create a standard budget for typical operations."""
        return cls(
            tokens=50000,
            time_seconds=300.0,  # 5 minutes
            operations=100,
        )

    @classmethod
    def minimal(cls) -> Budget:
        """Create a minimal budget for quick operations."""
        return cls(
            tokens=1000,
            time_seconds=30.0,
            operations=10,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "tokens": self.tokens,
            "time_seconds": self.time_seconds,
            "operations": self.operations,
            "capital": self.capital,
            "entropy": self.entropy,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Budget:
        """Create from dictionary."""
        return cls(
            tokens=data.get("tokens"),
            time_seconds=data.get("time_seconds"),
            operations=data.get("operations"),
            capital=data.get("capital"),
            entropy=data.get("entropy"),
        )


# =============================================================================
# Exceptions
# =============================================================================


class ScopeError(Exception):
    """Base exception for Scope errors."""

    pass


# Backwards compatibility alias
ScopeError = ScopeError


class BudgetExceeded(ScopeError):
    """Law 1: Budget constraint exceeded - triggers review."""

    pass


class ScopeExpired(ScopeError):
    """Law 3: Scope has expired."""

    pass


# Backwards compatibility alias
ScopeExpired = ScopeExpired


class HandleNotInScope(ScopeError):
    """Attempted to access a handle not in the Scope's scope."""

    pass


# =============================================================================
# Scope Status
# =============================================================================


class ScopeStatus(Enum):
    """Status of a Scope."""

    ACTIVE = auto()  # Currently valid
    EXHAUSTED = auto()  # Budget depleted
    EXPIRED = auto()  # Past expiry time
    REVOKED = auto()  # Manually revoked


# Backwards compatibility alias
ScopeStatus = ScopeStatus


# =============================================================================
# Scope: The Core Primitive
# =============================================================================


@dataclass(frozen=True)
class Scope:
    """
    Explicitly priced and scoped context contract.

    Laws:
    - Law 1 (Budget Enforcement): Exceeding budget triggers review
    - Law 2 (Immutability): Scopes are frozen after creation
    - Law 3 (Expiry Honored): Expired Scopes deny access

    A Scope defines:
    - What AGENTESE handles can be accessed (scoped_handles)
    - What resources can be consumed (budget)
    - When access expires (expires_at)

    Example:
        >>> scope = Scope.create(
        ...     description="Implement Mark",
        ...     scoped_handles=("time.trace.*", "time.walk.*"),
        ...     budget=Budget.standard(),
        ... )
        >>> scope.is_valid()  # True
        >>> scope.can_access("time.trace.node.manifest")  # True
        >>> scope.can_access("brain.terrace.manifest")  # False (not in scope)
    """

    # Identity
    id: ScopeId = field(default_factory=generate_scope_id)

    # Description
    description: str = ""

    # Scope: which AGENTESE handles can be accessed
    # Supports glob patterns: "time.*", "self.witness.*", etc.
    scoped_handles: tuple[str, ...] = ()

    # Budget constraints
    budget: Budget = field(default_factory=Budget.unlimited)

    # Timing
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # =========================================================================
    # Factory Methods
    # =========================================================================

    @classmethod
    def create(
        cls,
        description: str,
        scoped_handles: tuple[str, ...] | None = None,
        budget: Budget | None = None,
        duration: timedelta | None = None,
        expires_at: datetime | None = None,  # Backwards compat: direct expiry
    ) -> Scope:
        """
        Create a new Scope.

        Args:
            description: Human-readable description of what this Scope is for
            scoped_handles: AGENTESE handle patterns that can be accessed
            budget: Resource constraints (default: unlimited)
            duration: How long the Scope is valid (None = no expiry)
            expires_at: Direct expiry time (backwards compat, overrides duration)

        Returns:
            New Scope instance
        """
        # Backwards compat: expires_at takes precedence over duration
        final_expires_at = expires_at
        if final_expires_at is None and duration is not None:
            final_expires_at = datetime.now() + duration

        return cls(
            description=description,
            scoped_handles=scoped_handles or (),
            budget=budget or Budget.unlimited(),
            expires_at=final_expires_at,
        )

    # =========================================================================
    # Validity Checks (Law 3)
    # =========================================================================

    def is_valid(self) -> bool:
        """
        Check if this Scope is currently valid.

        Law 3: Expired Scopes deny access.
        """
        if self.expires_at is not None and datetime.now() > self.expires_at:
            return False
        if self.budget.is_exhausted:
            return False
        return True

    def check_valid(self) -> None:
        """Raise ScopeExpired if not valid."""
        if self.expires_at is not None and datetime.now() > self.expires_at:
            raise ScopeExpired(f"Scope {self.id} expired at {self.expires_at}")
        if self.budget.is_exhausted:
            raise BudgetExceeded(f"Scope {self.id} budget exhausted")

    @property
    def time_remaining(self) -> timedelta | None:
        """Get remaining time until expiry (None if no expiry)."""
        if self.expires_at is None:
            return None
        remaining = self.expires_at - datetime.now()
        return max(remaining, timedelta(0))

    # =========================================================================
    # Scope Checks
    # =========================================================================

    def can_access(self, handle: str) -> bool:
        """
        Check if a handle is within scope.

        Supports glob patterns:
        - "time.*" matches "time.trace.node.manifest"
        - "self.witness.*" matches "self.witness.thoughts"
        - Exact matches also work
        """
        if not self.scoped_handles:
            # Empty scope = no access (explicit is better than implicit)
            return False

        for pattern in self.scoped_handles:
            if self._matches_pattern(handle, pattern):
                return True
        return False

    @staticmethod
    def _matches_pattern(handle: str, pattern: str) -> bool:
        """Check if handle matches pattern (supports * glob)."""
        if pattern == handle:
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]  # Remove ".*"
            return handle.startswith(prefix + ".")
        if pattern.endswith("*"):
            prefix = pattern[:-1]  # Remove "*"
            return handle.startswith(prefix)
        return False

    def check_access(self, handle: str) -> None:
        """Raise HandleNotInScope if handle is not accessible."""
        if not self.can_access(handle):
            raise HandleNotInScope(
                f"Handle '{handle}' not in scope. Allowed: {self.scoped_handles}"
            )

    # =========================================================================
    # Budget Operations (Law 1)
    # =========================================================================

    def can_consume(
        self,
        tokens: int = 0,
        time_seconds: float = 0.0,
        operations: int = 0,
    ) -> bool:
        """Check if consumption would stay within budget."""
        return self.budget.can_consume(
            tokens=tokens,
            time_seconds=time_seconds,
            operations=operations,
        )

    def consume(
        self,
        tokens: int = 0,
        time_seconds: float = 0.0,
        operations: int = 0,
    ) -> Scope:
        """
        Return new Scope with consumption deducted.

        Law 1: Exceeding budget triggers BudgetExceeded (review trigger).
        Law 2: Returns a new Scope (original is immutable).
        """
        self.check_valid()

        new_budget = self.budget.remaining_after(
            tokens=tokens,
            time_seconds=time_seconds,
            operations=operations,
        )

        # Create new Scope with updated budget (Law 2: immutability)
        return Scope(
            id=self.id,
            description=self.description,
            scoped_handles=self.scoped_handles,
            budget=new_budget,
            created_at=self.created_at,
            expires_at=self.expires_at,
            metadata=self.metadata,
        )

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "id": str(self.id),
            "description": self.description,
            "scoped_handles": list(self.scoped_handles),
            "budget": self.budget.to_dict(),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Scope:
        """Create from dictionary."""
        return cls(
            id=ScopeId(data["id"]),
            description=data.get("description", ""),
            scoped_handles=tuple(data.get("scoped_handles", [])),
            budget=Budget.from_dict(data.get("budget", {})),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
            metadata=data.get("metadata", {}),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        valid = "valid" if self.is_valid() else "invalid"
        scope_str = ", ".join(self.scoped_handles[:2]) + (
            "..." if len(self.scoped_handles) > 2 else ""
        )
        return f"Scope(id={str(self.id)[:16]}..., scope=[{scope_str}], {valid})"

    # =========================================================================
    # Backwards Compatibility Properties
    # =========================================================================

    @property
    def kind(self) -> str:
        """Backwards compat: all scopes are 'resource' kind."""
        return "resource"

    @property
    def scope(self) -> tuple[str, ...]:
        """Backwards compat: alias for scoped_handles."""
        return self.scoped_handles


# Backwards compatibility alias
Scope = Scope


# =============================================================================
# ScopeStore: Persistence
# =============================================================================


@dataclass
class ScopeStore:
    """
    Persistent storage for Scopes.

    Tracks active Scopes and their consumption history.
    """

    _scopes: dict[ScopeId, Scope] = field(default_factory=dict)

    def add(self, scope: Scope) -> None:
        """Add a Scope to the store."""
        self._scopes[scope.id] = scope

    def get(self, scope_id: ScopeId) -> Scope | None:
        """Get a Scope by ID."""
        return self._scopes.get(scope_id)

    def update(self, scope: Scope) -> None:
        """Update a Scope (replace with new version)."""
        self._scopes[scope.id] = scope

    def active(self) -> list[Scope]:
        """Get all currently valid Scopes."""
        return [s for s in self._scopes.values() if s.is_valid()]

    def expired(self) -> list[Scope]:
        """Get all expired Scopes."""
        return [s for s in self._scopes.values() if not s.is_valid()]

    def __len__(self) -> int:
        return len(self._scopes)


# Backwards compatibility alias
ScopeStore = ScopeStore


# =============================================================================
# Global Store
# =============================================================================

_global_scope_store: ScopeStore | None = None


def get_scope_store() -> ScopeStore:
    """Get the global scope store."""
    global _global_scope_store
    if _global_scope_store is None:
        _global_scope_store = ScopeStore()
    return _global_scope_store


# Backwards compatibility alias
get_scope_store = get_scope_store


def reset_scope_store() -> None:
    """Reset the global scope store (for testing)."""
    global _global_scope_store
    _global_scope_store = None


# Backwards compatibility alias
reset_scope_store = reset_scope_store


# =============================================================================
# Backwards Compatibility Aliases (Offering → Scope)
# =============================================================================

# Type aliases
OfferingId = ScopeId
generate_offering_id = generate_scope_id

# Status
OfferingStatus = ScopeStatus

# Exceptions
OfferingError = ScopeError
OfferingExpired = ScopeExpired

# Core types
Offering = Scope

# Store
OfferingStore = ScopeStore
get_offering_store = get_scope_store
reset_offering_store = reset_scope_store


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # New names (preferred)
    "ScopeId",
    "generate_scope_id",
    "Budget",
    "ScopeStatus",
    "ScopeError",
    "BudgetExceeded",
    "ScopeExpired",
    "HandleNotInScope",
    "Scope",
    "ScopeStore",
    "get_scope_store",
    "reset_scope_store",
    # Backwards compatibility (Offering → Scope)
    "OfferingId",
    "generate_offering_id",
    "OfferingStatus",
    "OfferingError",
    "OfferingExpired",
    "Offering",
    "OfferingStore",
    "get_offering_store",
    "reset_offering_store",
]
