"""
Umwelt Protocol: Agent-Specific World Projection.

Each agent inhabits its own world; there is no view from nowhere.

This module implements the Umwelt Protocol from spec/protocols/umwelt.md:
- Umwelt: The agent's projected world (State + DNA + Gravity)
- Projector: Factory that creates Umwelts from the infinite World
- State as Lens: D-gent integration for scoped state access
- Gravity as Ground: F-gent contracts for constraint enforcement

The key insight: agents don't receive the World—they receive a projection.

Note: This is the full Umwelt Protocol with generic types and Lens integration.
For the simpler AGENTESE observer context, see `agents.poly.primitives.Umwelt`.

Migration (2025-12-19):
- Moved from bootstrap/umwelt.py to agents/poly/umwelt.py
- bootstrap/umwelt.py re-exports from here for backward compatibility
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    Any,
    Generic,
    Protocol,
    TypeVar,
)

from agents.d.lens import Lens, identity_lens, key_lens
from agents.d.protocol import DataAgent

# DNA from protocols.config
try:
    from protocols.config.dna import DNA, DNAValidationError
except ImportError:
    DNA = Any  # type: ignore[misc,assignment]
    DNAValidationError = Exception  # type: ignore[misc,assignment]


# === Type Variables ===

S = TypeVar("S")  # State type
D = TypeVar("D")  # DNA (config) type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


# === Contract Protocol (F-gent) ===


class Contract(Protocol):
    """
    F-gent contract for ground constraints.

    Contracts are active validators that check every output,
    not passive data stores queried on demand.
    """

    @property
    def name(self) -> str:
        """Human-readable contract name."""
        ...

    def check(self, output: Any) -> str | None:
        """
        Check if output satisfies contract.

        Returns:
            None if satisfied, error message if violated.
        """
        ...

    def admits(self, intent: str) -> bool:
        """
        Check if an intent is admissible under this contract.

        For J-gent Reality classification.
        """
        ...


# === Grounding Error ===


class GroundingError(Exception):
    """Raised when output violates gravitational constraints."""

    def __init__(
        self,
        agent: str,
        contract: str,
        violation: str,
    ):
        self.agent = agent
        self.contract = contract
        self.violation = violation
        super().__init__(f"Agent '{agent}' violated contract '{contract}': {violation}")


# === Umwelt Type ===


@dataclass(frozen=True)
class Umwelt(Generic[S, D]):
    """
    An agent's projected world.

    Immutable after creation. To change an Umwelt, re-project through Projector.

    Components:
    - state: Lens for scoped state access (D-gent)
    - dna: Agent configuration (G-gent validated)
    - gravity: Ground constraints (F-gent contracts)

    Example:
        >>> umwelt = Umwelt(
        ...     state=key_lens("k.persona"),
        ...     dna=KgentDNA(personality="curious"),
        ...     gravity=(PersonaContract(),),
        ... )
        >>> await umwelt.get()  # Read state through lens
        >>> await umwelt.set(new_state)  # Write state through lens
        >>> umwelt.is_grounded(output)  # Check constraints
    """

    state: Lens[Any, S]  # Scoped state access (pre-focused lens)
    dna: D  # Agent configuration (validated)
    gravity: tuple[Contract, ...] = ()  # Ground constraints

    # Internal: reference to underlying state storage
    _storage: DataAgent[Any] | None = field(default=None, repr=False)

    async def get(self) -> S:
        """Read state through lens."""
        if self._storage is None:
            raise RuntimeError("Umwelt not connected to storage")
        whole = await self._storage.load()
        return self.state.get(whole)

    async def set(self, value: S) -> None:
        """Write state through lens (gravity checked on agent output, not here)."""
        if self._storage is None:
            raise RuntimeError("Umwelt not connected to storage")
        whole = await self._storage.load()
        new_whole = self.state.set(whole, value)
        await self._storage.save(new_whole)

    def is_grounded(self, output: Any) -> bool:
        """Check if output satisfies all gravitational constraints."""
        return all(contract.check(output) is None for contract in self.gravity)

    def check_grounding(self, output: Any) -> list[str]:
        """Return list of constraint violations for output."""
        violations = []
        for contract in self.gravity:
            violation = contract.check(output)
            if violation:
                violations.append(f"{contract.name}: {violation}")
        return violations


# === Lightweight Umwelt (Lens-free) ===


@dataclass(frozen=True)
class LightweightUmwelt(Generic[S, D]):
    """
    Simplified Umwelt for agents with direct state access.

    For agents that don't need lens composition, provides
    direct DataAgent access without lens overhead.
    """

    storage: DataAgent[S]  # Direct state storage
    dna: D  # Agent configuration
    gravity: tuple[Contract, ...] = ()

    async def get(self) -> S:
        """Read state directly."""
        return await self.storage.load()

    async def set(self, value: S) -> None:
        """Write state directly."""
        await self.storage.save(value)

    def is_grounded(self, output: Any) -> bool:
        """Check if output satisfies all gravitational constraints."""
        return all(contract.check(output) is None for contract in self.gravity)


# === Projector ===


class Projector:
    """
    Projects the infinite World into finite agent Umwelts.

    The Projector:
    1. Does NOT give agents access to the World
    2. Creates scoped Lenses for state access
    3. Validates DNA against constraints
    4. Assembles gravitational constraints from F-gent contracts

    Example:
        >>> from agents.d import VolatileAgent
        >>> root = VolatileAgent({"agents": {}})
        >>> projector = Projector(root)
        >>> umwelt = projector.project(
        ...     agent_id="k",
        ...     dna=KgentDNA(personality="curious"),
        ...     gravity=[PersonaContract()],
        ... )
    """

    def __init__(self, root: DataAgent[Any]):
        """
        Initialize with a root D-gent (the "Real").

        Args:
            root: The underlying state store (could be volatile,
                  persistent, or hypothetical)
        """
        self._root = root
        self._gravity_registry: dict[str, list[Contract]] = {}

    def project(
        self,
        agent_id: str,
        dna: Any,
        gravity: list[Contract] | None = None,
        path: str | None = None,
    ) -> Umwelt[Any, Any]:
        """
        Create an Umwelt for an agent.

        The agent receives:
        - A Lens (cannot see outside its focus)
        - Validated DNA (constraint checked)
        - Gravitational constraints (F-gent enforced)

        Args:
            agent_id: Unique agent identifier
            dna: Agent DNA (configuration)
            gravity: Optional list of contracts
            path: Optional custom lens path (default: "agents.{agent_id}")

        Returns:
            Configured Umwelt

        Raises:
            DNAValidationError: If DNA fails constraint validation
        """
        # 1. Create scoped lens
        lens_path = path or f"agents.{agent_id}"
        state_lens = self._create_lens(lens_path)

        # 2. Validate DNA if it has constraints method
        if hasattr(dna, "constraints") and callable(dna.constraints):
            self._validate_dna(dna, agent_id)

        # 3. Assemble gravity
        agent_gravity = gravity or self._gravity_registry.get(agent_id, [])

        return Umwelt(
            state=state_lens,
            dna=dna,
            gravity=tuple(agent_gravity),
            _storage=self._root,
        )

    def project_lightweight(
        self,
        agent_id: str,
        dna: Any,
        storage: DataAgent[Any],
        gravity: list[Contract] | None = None,
    ) -> LightweightUmwelt[Any, Any]:
        """
        Create a lightweight Umwelt with direct storage access.

        For agents that don't need lens composition.

        Args:
            agent_id: Unique agent identifier
            dna: Agent DNA
            storage: Direct D-gent storage
            gravity: Optional contracts

        Returns:
            Configured LightweightUmwelt
        """
        # Validate DNA
        if hasattr(dna, "constraints") and callable(dna.constraints):
            self._validate_dna(dna, agent_id)

        agent_gravity = gravity or self._gravity_registry.get(agent_id, [])

        return LightweightUmwelt(
            storage=storage,
            dna=dna,
            gravity=tuple(agent_gravity),
        )

    def register_gravity(self, agent_id: str, contracts: list[Contract]) -> None:
        """
        Register default gravity for an agent type.

        Args:
            agent_id: Agent identifier (or pattern like "b.*")
            contracts: List of contracts to apply
        """
        self._gravity_registry[agent_id] = contracts

    def _create_lens(self, path: str) -> Lens[Any, Any]:
        """
        Create a lens from a dot-separated path.

        Args:
            path: Path like "agents.k.persona"

        Returns:
            Composed lens focusing on path
        """
        keys = path.split(".")
        if not keys:
            return identity_lens()

        lens = key_lens(keys[0])
        for key in keys[1:]:
            lens = lens >> key_lens(key)
        return lens

    def _validate_dna(self, dna: Any, agent_id: str) -> None:
        """
        Validate DNA against its constraints.

        Raises DNAValidationError if validation fails.
        """
        if not hasattr(dna, "constraints"):
            return

        constraints = dna.constraints() if callable(dna.constraints) else []
        errors = []

        for constraint in constraints:
            valid, msg = constraint.validate(dna)
            if not valid:
                errors.append(f"{constraint.name}: {msg}")

        if errors:
            raise DNAValidationError(
                dna_type=type(dna).__name__,
                errors=errors,
                message=f"DNA validation failed for agent '{agent_id}'",
            )


# === Hypothetical Projector ===


class HypotheticalProjector:
    """
    Creates hypothetical worlds for counter-factual reasoning.

    B-gent uses this to spawn parallel worlds for hypothesis testing.
    The hypothetical world can be modified without affecting the real world.

    Example:
        >>> real_projector = Projector(persistent_root)
        >>> hypothetical = HypotheticalProjector.from_snapshot(real_projector)
        >>> # Spawn agents in hypothetical world
        >>> umwelt_a = hypothetical.project("b.hypothesis", dna_a)
        >>> umwelt_b = hypothetical.project("b.hypothesis", dna_b)
        >>> # Real world unchanged
    """

    def __init__(self, root: DataAgent[Any]):
        """
        Initialize with a volatile (in-memory) root.

        Args:
            root: In-memory D-gent for hypothetical state
        """
        self._projector = Projector(root)
        self._is_hypothetical = True

    @classmethod
    async def from_snapshot(
        cls,
        real_projector: Projector,
        volatile_class: type[DataAgent[Any]] | None = None,
    ) -> "HypotheticalProjector":
        """
        Create hypothetical projector from snapshot of real world.

        Args:
            real_projector: The real world projector
            volatile_class: Optional volatile D-gent class

        Returns:
            HypotheticalProjector with cloned state
        """
        # Import here to avoid circular dependency
        from agents.d.volatile import VolatileAgent

        # Clone current state
        current_state = await real_projector._root.load()

        # Create hypothetical root with cloned state
        if volatile_class is None:
            hypothetical_root: DataAgent[Any] = VolatileAgent(_state=current_state)
        else:
            # For custom volatile classes, assume they accept _state parameter
            hypothetical_root = volatile_class(_state=current_state)  # type: ignore[call-arg]

        return cls(hypothetical_root)

    def project(
        self,
        agent_id: str,
        dna: Any,
        gravity: list[Contract] | None = None,
    ) -> Umwelt[Any, Any]:
        """Project an agent into the hypothetical world."""
        return self._projector.project(agent_id, dna, gravity)

    @property
    def is_hypothetical(self) -> bool:
        """Always True for hypothetical projectors."""
        return True


# === Temporal Projector ===


@dataclass
class TemporalLens(Generic[S]):
    """
    Lens that projects state at a specific timestamp.

    For temporal navigation of agent state history.
    """

    base_lens: Lens[Any, S]
    timestamp: float  # Unix timestamp
    storage: DataAgent[Any]

    async def get(self) -> S | None:
        """
        Get state as it was at timestamp.

        Returns None if no historical state available.
        """
        # This is a placeholder - actual implementation would
        # query D-gent history and find closest state
        history = await self.storage.history()

        # For now, return current state (full implementation
        # would search history by timestamp)
        if not history:
            whole = await self.storage.load()
            return self.base_lens.get(whole)

        return None


class TemporalProjector:
    """
    Projects Umwelts at specific points in time.

    Enables agents to "see" historical state for replay/forensics.

    Example:
        >>> temporal = TemporalProjector(projector, timestamp=one_hour_ago)
        >>> historical_umwelt = temporal.project("k", dna)
        >>> # Agent sees state as it was one hour ago
    """

    def __init__(self, base_projector: Projector, timestamp: float):
        """
        Initialize temporal projector.

        Args:
            base_projector: The base projector
            timestamp: Unix timestamp to project
        """
        self._base = base_projector
        self._timestamp = timestamp

    def project(
        self,
        agent_id: str,
        dna: Any,
        gravity: list[Contract] | None = None,
    ) -> Umwelt[Any, Any]:
        """
        Project agent at historical timestamp.

        Note: DNA is always current (configuration doesn't time-travel).
        Only state is projected historically.
        """
        # Get base umwelt
        umwelt = self._base.project(agent_id, dna, gravity)

        # Wrap lens with temporal projection
        # Note: This is a simplified version; full implementation
        # would integrate more deeply with D-gent history and use TemporalLens
        _ = TemporalLens(
            base_lens=umwelt.state,
            timestamp=self._timestamp,
            storage=self._base._root,
        )

        # Return umwelt with temporal state access
        return umwelt
