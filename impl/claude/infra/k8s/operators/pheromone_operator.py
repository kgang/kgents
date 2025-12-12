"""Pheromone Operator - Passive Stigmergy Garbage Collection.

PASSIVE STIGMERGY (v2.0):
The pheromone operator ONLY DELETES pheromones, never UPDATES them.
Intensity is calculated on read using the decay function:
    intensity(t) = initialIntensity * (0.5 ^ ((now - emittedAt) / halfLifeMinutes))

This prevents etcd write storms - critical for K8s health.

The operator:
1. On CREATE: Initialize emittedAt if not set, set phase to ACTIVE
2. On TIMER (every 5 min): DELETE pheromones below evaporation threshold
3. On CHAOS type: Trigger chaos injection for resilience testing

This makes stigmergy a first-class K8s primitive:
    kubectl get pheromones --watch

Principle alignment:
- E-gent (Thermodynamics): Pheromones decay - entropy increases
- Accursed Share: DREAM pheromones have longer half-life
- Tasteful: No etcd write storms (DELETE only, no UPDATE)
- Graceful Degradation: CHAOS pheromones train resilience
"""

from __future__ import annotations

import logging
import random
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

# Passive Stigmergy Configuration
DEFAULT_HALF_LIFE_MINUTES = 10.0
DREAM_HALF_LIFE_MULTIPLIER = 2.0  # DREAM pheromones last twice as long
EVAPORATION_THRESHOLD = 0.01  # Delete when intensity < 1%
GC_INTERVAL_SECONDS = 300.0  # Garbage collection every 5 minutes (not 60s)

# Pheromone types with extended half-life (the sacred waste)
SLOW_DECAY_TYPES = {"DREAM"}


def calculate_intensity(spec: dict[str, Any]) -> float:
    """Calculate current pheromone intensity from decay parameters.

    PASSIVE STIGMERGY: This is a pure function that calculates intensity
    from stored parameters. NO WRITES to etcd.

    Formula: intensity(t) = initialIntensity * (0.5 ^ (elapsed / halfLife))

    Args:
        spec: Pheromone spec containing decay parameters

    Returns:
        Current intensity (0.0-1.0)
    """
    # Get emission time (prefer emittedAt, fallback to legacy created_at)
    emitted_str = spec.get("emittedAt")

    # Handle legacy pheromones with old schema
    if not emitted_str:
        # Legacy: use intensity directly if no emittedAt
        return float(spec.get("intensity", spec.get("initialIntensity", 1.0)))

    try:
        emitted_at = datetime.fromisoformat(emitted_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return float(spec.get("initialIntensity", 1.0))

    # Get decay parameters
    initial = spec.get("initialIntensity", spec.get("intensity", 1.0))
    half_life = spec.get("halfLifeMinutes", DEFAULT_HALF_LIFE_MINUTES)

    # Legacy conversion: decay_rate to half_life
    if "decay_rate" in spec and "halfLifeMinutes" not in spec:
        # Approximate: decay_rate of 0.1 per minute ≈ half_life of ~7 minutes
        decay_rate = spec["decay_rate"]
        if decay_rate > 0:
            half_life = 0.693 / decay_rate  # ln(2) / decay_rate

    # Apply type-specific multiplier
    pheromone_type = spec.get("type", "STATE")
    if pheromone_type in SLOW_DECAY_TYPES:
        half_life *= DREAM_HALF_LIFE_MULTIPLIER

    # Calculate elapsed time
    now = datetime.now(timezone.utc)
    elapsed_minutes = (
        now - emitted_at.replace(tzinfo=timezone.utc)
    ).total_seconds() / 60.0

    # Exponential decay: intensity = initial * (0.5 ^ (elapsed / half_life))
    intensity = float(initial) * (0.5 ** (elapsed_minutes / half_life))

    return float(max(0.0, min(1.0, intensity)))


def should_evaporate(
    spec: dict[str, Any],
    meta: dict[str, Any],
) -> bool:
    """Determine if pheromone should be garbage collected.

    Args:
        spec: Pheromone spec
        meta: Pheromone metadata

    Returns:
        True if pheromone should be deleted
    """
    # Calculate current intensity
    intensity = calculate_intensity(spec)

    # Delete if below evaporation threshold
    if intensity < EVAPORATION_THRESHOLD:
        return True

    # Check hard TTL
    ttl_seconds = spec.get("ttl_seconds")
    if ttl_seconds is not None:
        created_str = meta.get("creationTimestamp")
        if created_str:
            try:
                created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                age_seconds = (now - created_at).total_seconds()
                if age_seconds >= ttl_seconds:
                    return True
            except (ValueError, AttributeError):
                pass

    return False


# ============================================================================
# Kopf Handlers (only registered if kopf is available)
# ============================================================================

if KOPF_AVAILABLE:

    @kopf.on.create("kgents.io", "v1", "pheromones")  # type: ignore[arg-type]
    async def on_pheromone_create(
        spec: dict[str, Any],
        meta: dict[str, Any],
        patch: kopf.Patch,
        **_: Any,
    ) -> dict[str, Any]:
        """Initialize pheromone on creation.

        PASSIVE STIGMERGY: We only set phase, not current_intensity.
        If emittedAt is missing, it defaults to creationTimestamp.
        """
        pheromone_type = spec.get("type", "STATE")
        initial = spec.get("initialIntensity", spec.get("intensity", 1.0))

        logger.info(
            f"Pheromone created: {meta['name']} "
            f"type={pheromone_type} initialIntensity={initial}"
        )

        # Set phase to ACTIVE (no current_intensity - calculated on read)
        patch.status["phase"] = "ACTIVE"
        patch.status["sensed_by"] = []

        # Handle CHAOS pheromones immediately
        if pheromone_type == "CHAOS":
            await _handle_chaos_pheromone(spec, meta)

        return {"created": True, "type": pheromone_type}

    @kopf.timer("kgents.io", "v1", "pheromones", interval=GC_INTERVAL_SECONDS)  # type: ignore[arg-type]
    async def garbage_collect_pheromones(
        spec: dict[str, Any],
        meta: dict[str, Any],
        **_: Any,
    ) -> dict[str, Any] | None:
        """Garbage collect evaporated pheromones.

        PASSIVE STIGMERGY: This timer ONLY DELETES pheromones.
        It NEVER updates status.current_intensity.

        Runs every 5 minutes (not every minute) because we're only
        garbage collecting, not updating state.
        """
        name = meta["name"]
        namespace = meta.get("namespace", "default")

        # Calculate current intensity (pure function, no writes)
        intensity = calculate_intensity(spec)

        # Check if should evaporate
        if not should_evaporate(spec, meta):
            logger.debug(f"Pheromone {name} still active (intensity={intensity:.4f})")
            return None

        # DELETE the pheromone (no status update)
        logger.info(f"Evaporating pheromone: {name} (intensity={intensity:.4f})")

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

        return {"evaporated": True, "final_intensity": intensity}

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
# Chaos Injection (void.entropy.sip implementation)
# ============================================================================


async def _handle_chaos_pheromone(spec: dict[str, Any], meta: dict[str, Any]) -> None:
    """Handle CHAOS pheromones for resilience testing.

    This implements void.entropy.sip - controlled chaos injection.
    The Accursed Share in action: "waste" of killing healthy pods
    trains the system for resilience.
    """
    if not KOPF_AVAILABLE:
        return

    payload_str = spec.get("payload", "{}")
    try:
        import json

        payload = json.loads(payload_str) if payload_str else {}
    except json.JSONDecodeError:
        payload = {}

    action = payload.get("action")
    namespace = payload.get("namespace", meta.get("namespace", "kgents-agents"))

    logger.warning(f"CHAOS pheromone received: action={action} namespace={namespace}")

    if action == "terminate_random_pod":
        await _terminate_random_pod(namespace)
    elif action == "network_partition":
        # Future: implement network chaos via NetworkPolicy
        logger.info("Network partition chaos not yet implemented")
    elif action == "resource_pressure":
        # Future: implement resource chaos
        logger.info("Resource pressure chaos not yet implemented")


async def _terminate_random_pod(namespace: str) -> None:
    """Terminate a random pod in the namespace.

    This is the void.entropy.sip implementation - controlled chaos
    that trains the Left Brain (operators) for resilience.
    """
    if not KOPF_AVAILABLE:
        return

    try:
        api = client.CoreV1Api()
        pods = api.list_namespaced_pod(
            namespace, label_selector="app.kubernetes.io/part-of=kgents"
        )

        if not pods.items:
            logger.warning(f"No kgents pods found in {namespace} for chaos injection")
            return

        # Select random victim
        victim = random.choice(pods.items)
        victim_name = victim.metadata.name

        logger.warning(
            f"CHAOS: Terminating pod {victim_name} in {namespace} "
            f"(void.entropy.sip - the accursed share)"
        )

        api.delete_namespaced_pod(victim_name, namespace)

    except ApiException as e:
        logger.error(f"CHAOS: Failed to terminate pod: {e}")


# ============================================================================
# Standalone Functions (for testing without K8s)
# ============================================================================


class MockPheromone:
    """In-memory pheromone for testing without K8s.

    PASSIVE STIGMERGY: Uses half-life decay model, intensity calculated on read.
    """

    def __init__(
        self,
        name: str,
        pheromone_type: str,
        initial_intensity: float = 1.0,
        source: str = "",
        half_life_minutes: float = DEFAULT_HALF_LIFE_MINUTES,
        payload: str = "",
        ttl_seconds: int | None = None,
        target: str | None = None,
    ) -> None:
        self.name = name
        self.type = pheromone_type
        self.initial_intensity = initial_intensity
        self.source = source
        self.half_life_minutes = half_life_minutes
        self.payload = payload
        self.ttl_seconds = ttl_seconds
        self.target = target
        self.emitted_at = datetime.now(timezone.utc)
        self.sensed_by: list[str] = []

    @property
    def intensity(self) -> float:
        """Calculate current intensity (Passive Stigmergy)."""
        spec = {
            "emittedAt": self.emitted_at.isoformat(),
            "initialIntensity": self.initial_intensity,
            "halfLifeMinutes": self.half_life_minutes,
            "type": self.type,
        }
        return calculate_intensity(spec)

    def should_evaporate(self) -> bool:
        """Check if pheromone should be garbage collected."""
        # Below threshold
        if self.intensity < EVAPORATION_THRESHOLD:
            return True

        # TTL expired
        if self.ttl_seconds is not None:
            age = (datetime.now(timezone.utc) - self.emitted_at).total_seconds()
            if age >= self.ttl_seconds:
                return True

        return False

    def sense(self, agent: str) -> None:
        """Record that an agent sensed this pheromone."""
        if agent not in self.sensed_by:
            self.sensed_by.append(agent)

    def to_spec(self) -> dict[str, Any]:
        """Convert to CRD-like spec for compatibility."""
        return {
            "type": self.type,
            "emittedAt": self.emitted_at.isoformat() + "Z",
            "initialIntensity": self.initial_intensity,
            "halfLifeMinutes": self.half_life_minutes,
            "source": self.source,
            "target": self.target,
            "payload": self.payload,
            "ttl_seconds": self.ttl_seconds,
        }


class MockPheromoneField:
    """In-memory pheromone field for testing without K8s.

    PASSIVE STIGMERGY: Intensity calculated on sense(), GC on tick().
    """

    def __init__(self) -> None:
        self._pheromones: dict[str, MockPheromone] = {}

    def emit(
        self,
        name: str,
        pheromone_type: str,
        initial_intensity: float = 1.0,
        source: str = "",
        half_life_minutes: float = DEFAULT_HALF_LIFE_MINUTES,
        **kwargs: Any,
    ) -> MockPheromone:
        """Emit a new pheromone."""
        # Handle legacy 'intensity' parameter
        if "intensity" in kwargs and "initial_intensity" not in kwargs:
            initial_intensity = kwargs.pop("intensity")

        ph = MockPheromone(
            name=name,
            pheromone_type=pheromone_type,
            initial_intensity=initial_intensity,
            source=source,
            half_life_minutes=half_life_minutes,
            **kwargs,
        )
        self._pheromones[name] = ph
        logger.info(
            f"Emitted pheromone: {name} type={pheromone_type} "
            f"initialIntensity={initial_intensity} halfLife={half_life_minutes}min"
        )

        # Handle CHAOS pheromones
        if pheromone_type == "CHAOS":
            logger.warning(f"CHAOS pheromone emitted: {name}")

        return ph

    def sense(
        self,
        agent: str,
        pheromone_type: str | None = None,
        target: str | None = None,
    ) -> list[MockPheromone]:
        """Sense pheromones in the field.

        PASSIVE STIGMERGY: Intensity is calculated on each sense() call.

        Args:
            agent: Agent doing the sensing
            pheromone_type: Filter by type (None = all types)
            target: Filter by target (None = include broadcast and targeted)

        Returns:
            List of matching pheromones (sorted by intensity descending)
        """
        result = []
        for ph in self._pheromones.values():
            # Filter by type
            if pheromone_type is not None and ph.type != pheromone_type:
                continue

            # Filter by target (include broadcast pheromones where target is None)
            if target is not None and ph.target is not None and ph.target != target:
                continue

            ph.sense(agent)
            result.append(ph)

        # Sort by current intensity (calculated on each access)
        return sorted(result, key=lambda p: p.intensity, reverse=True)

    def tick(self) -> int:
        """Garbage collect evaporated pheromones.

        PASSIVE STIGMERGY: Only DELETE, never update intensity.
        Called periodically to clean up evaporated pheromones.

        Returns:
            Number of pheromones evaporated
        """
        to_delete = []
        for name, ph in self._pheromones.items():
            if ph.should_evaporate():
                to_delete.append(name)

        for name in to_delete:
            del self._pheromones[name]
            logger.info(f"Evaporated pheromone: {name}")

        return len(to_delete)

    def list(self) -> list[MockPheromone]:
        """List all pheromones."""
        return list(self._pheromones.values())

    def get(self, name: str) -> MockPheromone | None:
        """Get a specific pheromone by name."""
        return self._pheromones.get(name)


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
