"""Pheromone Operator - Decay pheromone intensity over time.

The pheromone operator manages the lifecycle of Pheromone CRs:
1. On CREATE: Initialize status.current_intensity from spec.intensity
2. On TIMER: Decay intensity by decay_rate, delete if <= 0 or TTL expired
3. On SENSE: Track which agents have sensed the pheromone

This makes stigmergy a first-class K8s primitive:
    kubectl get pheromones --watch

Principle alignment:
- E-gent (Thermodynamics): Pheromones decay - entropy increases
- Accursed Share: DREAM pheromones may decay slower (preserved chaos)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

# kopf is the K8s operator framework
# In production: pip install kopf kubernetes
# For testing without K8s: we provide mock implementations
try:
    import kopf
    from kubernetes import client
    from kubernetes.client.rest import ApiException

    KOPF_AVAILABLE = True
except ImportError:
    KOPF_AVAILABLE = False
    kopf = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Decay configuration
DEFAULT_DECAY_RATE = 0.1  # 10% per minute
DECAY_INTERVAL_SECONDS = 60.0
DREAM_DECAY_MULTIPLIER = 0.5  # DREAM pheromones decay slower (accursed share)

# Pheromone types that decay slower (the sacred waste)
SLOW_DECAY_TYPES = {"DREAM"}


def calculate_decay(
    current_intensity: float,
    decay_rate: float,
    pheromone_type: str,
    elapsed_minutes: float = 1.0,
) -> float:
    """Calculate decayed intensity.

    Args:
        current_intensity: Current intensity (0-1)
        decay_rate: Decay rate per minute
        pheromone_type: Type of pheromone (affects decay for DREAM)
        elapsed_minutes: Time elapsed since last decay

    Returns:
        New intensity after decay (clamped to 0-1)
    """
    effective_rate = decay_rate

    # DREAM pheromones decay slower - the accursed share is preserved
    if pheromone_type in SLOW_DECAY_TYPES:
        effective_rate *= DREAM_DECAY_MULTIPLIER

    new_intensity = current_intensity - (effective_rate * elapsed_minutes)
    return max(0.0, min(1.0, new_intensity))


def should_delete(
    intensity: float,
    created_at: datetime | None,
    ttl_seconds: int | None,
) -> bool:
    """Determine if pheromone should be deleted.

    Args:
        intensity: Current intensity
        created_at: When the pheromone was created
        ttl_seconds: Hard TTL (if set)

    Returns:
        True if pheromone should be deleted
    """
    # Delete if intensity has decayed to zero
    if intensity <= 0:
        return True

    # Delete if TTL has expired
    if ttl_seconds is not None and created_at is not None:
        now = datetime.now(timezone.utc)
        age_seconds = (now - created_at).total_seconds()
        if age_seconds >= ttl_seconds:
            return True

    return False


# ============================================================================
# Kopf Handlers (only registered if kopf is available)
# ============================================================================

if KOPF_AVAILABLE:

    @kopf.on.create("kgents.io", "v1", "pheromones")  # type: ignore[arg-type]
    async def on_pheromone_create(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any]:
        """Initialize pheromone status on creation."""
        intensity = spec.get("intensity", 1.0)
        pheromone_type = spec.get("type", "STATE")

        logger.info(
            f"Pheromone created: {meta['name']} "
            f"type={pheromone_type} intensity={intensity}"
        )

        # Set initial status
        now = datetime.now(timezone.utc).isoformat()
        patch.status["current_intensity"] = intensity
        patch.status["created_at"] = now
        patch.status["last_decay"] = now
        patch.status["sensed_by"] = []

        return {"created": True, "intensity": intensity}

    @kopf.timer("kgents.io", "v1", "pheromones", interval=DECAY_INTERVAL_SECONDS)  # type: ignore[arg-type]
    async def decay_pheromones(
        spec: dict[str, Any],
        meta: dict[str, Any],
        status: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any] | None:
        """Decay pheromone intensity over time."""
        name = meta["name"]
        namespace = meta.get("namespace", "default")

        # Get current values
        current_intensity = status.get("current_intensity", spec.get("intensity", 1.0))
        decay_rate = spec.get("decay_rate", DEFAULT_DECAY_RATE)
        pheromone_type = spec.get("type", "STATE")
        ttl_seconds = spec.get("ttl_seconds")

        # Parse created_at
        created_at_str = status.get("created_at")
        created_at = None
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(
                    created_at_str.replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass

        # Calculate elapsed time since last decay
        last_decay_str = status.get("last_decay")
        elapsed_minutes = 1.0
        if last_decay_str:
            try:
                last_decay = datetime.fromisoformat(
                    last_decay_str.replace("Z", "+00:00")
                )
                now = datetime.now(timezone.utc)
                elapsed_minutes = (now - last_decay).total_seconds() / 60.0
            except (ValueError, AttributeError):
                pass

        # Calculate new intensity
        new_intensity = calculate_decay(
            current_intensity, decay_rate, pheromone_type, elapsed_minutes
        )

        # Check if should delete
        if should_delete(new_intensity, created_at, ttl_seconds):
            logger.info(
                f"Deleting decayed pheromone: {name} (intensity={new_intensity:.3f})"
            )

            # Delete the pheromone
            api = client.CustomObjectsApi()
            try:
                api.delete_namespaced_custom_object(
                    group="kgents.io",
                    version="v1",
                    namespace=namespace,
                    plural="pheromones",
                    name=name,
                )
            except ApiException as e:
                if e.status != 404:  # Already deleted is fine
                    logger.error(f"Failed to delete pheromone {name}: {e}")

            return {"deleted": True, "final_intensity": new_intensity}

        # Update status
        now_str: str = datetime.now(timezone.utc).isoformat()
        patch.status["current_intensity"] = new_intensity
        patch.status["last_decay"] = now_str

        logger.debug(
            f"Decayed pheromone {name}: {current_intensity:.3f} -> {new_intensity:.3f}"
        )

        return {"decayed": True, "intensity": new_intensity}

    @kopf.on.field("kgents.io", "v1", "pheromones", field="status.sensed_by")  # type: ignore[arg-type]
    async def on_pheromone_sensed(
        old: list[str] | None,
        new: list[str] | None,
        meta: dict[str, Any],
        **_: Any,
    ) -> None:
        """Log when agents sense pheromones."""
        old_set = set(old or [])
        new_set = set(new or [])
        new_sensors = new_set - old_set

        if new_sensors:
            logger.info(f"Pheromone {meta['name']} sensed by: {', '.join(new_sensors)}")


# ============================================================================
# Standalone Functions (for testing without K8s)
# ============================================================================


class MockPheromone:
    """In-memory pheromone for testing without K8s."""

    def __init__(
        self,
        name: str,
        pheromone_type: str,
        intensity: float,
        source: str,
        decay_rate: float = DEFAULT_DECAY_RATE,
        payload: str = "",
        ttl_seconds: int | None = None,
    ) -> None:
        self.name = name
        self.type = pheromone_type
        self.intensity = intensity
        self.source = source
        self.decay_rate = decay_rate
        self.payload = payload
        self.ttl_seconds = ttl_seconds
        self.created_at = datetime.now(timezone.utc)
        self.last_decay = self.created_at
        self.sensed_by: list[str] = []

    def decay(self, elapsed_minutes: float = 1.0) -> bool:
        """Apply decay, return True if pheromone should be deleted."""
        self.intensity = calculate_decay(
            self.intensity, self.decay_rate, self.type, elapsed_minutes
        )
        self.last_decay = datetime.now(timezone.utc)
        return should_delete(self.intensity, self.created_at, self.ttl_seconds)

    def sense(self, agent: str) -> None:
        """Record that an agent sensed this pheromone."""
        if agent not in self.sensed_by:
            self.sensed_by.append(agent)


class MockPheromoneField:
    """In-memory pheromone field for testing without K8s."""

    def __init__(self) -> None:
        self._pheromones: dict[str, MockPheromone] = {}

    def emit(
        self,
        name: str,
        pheromone_type: str,
        intensity: float,
        source: str,
        **kwargs: Any,
    ) -> MockPheromone:
        """Emit a new pheromone."""
        ph = MockPheromone(name, pheromone_type, intensity, source, **kwargs)
        self._pheromones[name] = ph
        logger.info(
            f"Emitted pheromone: {name} type={pheromone_type} intensity={intensity}"
        )
        return ph

    def sense(
        self, agent: str, pheromone_type: str | None = None
    ) -> list[MockPheromone]:
        """Sense pheromones in the field.

        Args:
            agent: Agent doing the sensing
            pheromone_type: Filter by type (None = all types)

        Returns:
            List of matching pheromones (sorted by intensity descending)
        """
        result = []
        for ph in self._pheromones.values():
            if pheromone_type is None or ph.type == pheromone_type:
                ph.sense(agent)
                result.append(ph)
        return sorted(result, key=lambda p: p.intensity, reverse=True)

    def tick(self, elapsed_minutes: float = 1.0) -> int:
        """Apply decay to all pheromones, return count deleted."""
        to_delete = []
        for name, ph in self._pheromones.items():
            if ph.decay(elapsed_minutes):
                to_delete.append(name)

        for name in to_delete:
            del self._pheromones[name]
            logger.info(f"Deleted decayed pheromone: {name}")

        return len(to_delete)

    def list(self) -> list[MockPheromone]:
        """List all pheromones."""
        return list(self._pheromones.values())


# Global mock field for testing
_mock_field: MockPheromoneField | None = None


def get_mock_field() -> MockPheromoneField:
    """Get or create the global mock pheromone field."""
    global _mock_field
    if _mock_field is None:
        _mock_field = MockPheromoneField()
    return _mock_field


def reset_mock_field() -> None:
    """Reset the global mock field (for testing)."""
    global _mock_field
    _mock_field = None
