"""
AutoUpgrader: Automatic data promotion through the projection lattice.

Data starts in the fastest tier (Memory) and automatically promotes to more
durable tiers based on access patterns, age, and explicit importance markers.

Promotion rules:
- Memory → JSONL: After N accesses or T seconds
- JSONL → SQLite: After M accesses or U seconds
- SQLite → Postgres: Explicit marking or cross-session persistence

This is the NEW simplified D-gent architecture (data-architecture-rewrite).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Awaitable, Callable

from .bus import DataBus, DataEvent, DataEventType
from .datum import Datum
from .protocol import DgentProtocol
from .router import Backend, DgentRouter

# Synergy event imports (optional dependency)
try:
    from protocols.synergy.bus import SynergyEventBus, get_synergy_bus
    from protocols.synergy.events import (
        create_data_degraded_event,
        create_data_upgraded_event,
    )

    _HAS_SYNERGY = True
except ImportError:
    _HAS_SYNERGY = False

logger = logging.getLogger(__name__)


class UpgradeReason(Enum):
    """Reasons for promoting data to a higher tier."""

    ACCESS_COUNT = auto()  # Frequently accessed
    AGE = auto()  # Survived long enough
    EXPLICIT = auto()  # User marked as important
    SIZE = auto()  # Too large for current tier
    CROSS_SESSION = auto()  # Needs to survive restart


@dataclass
class UpgradePolicy:
    """
    Policy for when to upgrade data to a more durable tier.

    Default values are conservative - tune based on your use case.
    """

    # Memory → JSONL
    memory_to_jsonl_accesses: int = 3  # After N reads
    memory_to_jsonl_seconds: float = 60.0  # After T seconds alive

    # JSONL → SQLite
    jsonl_to_sqlite_accesses: int = 10  # After N reads
    jsonl_to_sqlite_seconds: float = 3600.0  # After 1 hour

    # SQLite → Postgres (only explicit or cross-session)
    # Postgres requires explicit marking or cross-session flag
    sqlite_to_postgres_explicit_only: bool = True


@dataclass
class UpgradeStats:
    """Statistics about upgrade activity."""

    upgrades_memory_to_jsonl: int = 0
    upgrades_jsonl_to_sqlite: int = 0
    upgrades_sqlite_to_postgres: int = 0
    upgrade_failures: int = 0
    last_upgrade_time: float | None = None


@dataclass
class DatumStats:
    """Statistics for a single datum (for upgrade decisions)."""

    id: str
    tier: Backend
    access_count: int = 0
    created_at: float = 0.0
    last_accessed: float = 0.0
    marked_important: bool = False


class AutoUpgrader:
    """
    Background process for automatic data promotion.

    Listens to the DataBus for access events and promotes data
    through the projection lattice based on the upgrade policy.

    Usage:
        upgrader = AutoUpgrader(
            source=memory_backend,
            targets={
                Backend.JSONL: jsonl_backend,
                Backend.SQLITE: sqlite_backend,
            },
            bus=data_bus,
        )
        await upgrader.start()  # Background task
        ...
        await upgrader.stop()
    """

    def __init__(
        self,
        source: DgentProtocol,
        source_tier: Backend,
        targets: dict[Backend, DgentProtocol],
        bus: DataBus | None = None,
        policy: UpgradePolicy | None = None,
        check_interval: float = 30.0,  # Seconds between upgrade checks
        synergy_bus: "SynergyEventBus | None" = None,
        emit_synergy: bool = True,  # Whether to emit synergy events
    ) -> None:
        """
        Initialize the AutoUpgrader.

        Args:
            source: The source backend (typically Memory or JSONL)
            source_tier: Which tier the source is
            targets: Map of tier → backend for upgrade targets
            bus: DataBus for listening to events (optional)
            policy: Upgrade policy (uses defaults if None)
            check_interval: How often to check for upgrade candidates
            synergy_bus: SynergyEventBus for cross-jewel events (optional)
            emit_synergy: Whether to emit synergy events (default True)
        """
        self.source = source
        self.source_tier = source_tier
        self.targets = targets
        self.bus = bus
        self.policy = policy or UpgradePolicy()
        self.check_interval = check_interval
        self._synergy_bus = synergy_bus
        self._emit_synergy = emit_synergy

        self._stats = UpgradeStats()
        self._datum_stats: dict[str, DatumStats] = {}
        self._running = False
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self._unsubscribe: Callable[[], None] | None = None

        # Callbacks
        self._on_upgrade: list[Callable[[Datum, Backend, Backend], Awaitable[None]]] = []

    def on_upgrade(self, callback: Callable[[Datum, Backend, Backend], Awaitable[None]]) -> None:
        """Register callback for upgrade events."""
        self._on_upgrade.append(callback)

    async def _notify_upgrade(self, datum: Datum, from_tier: Backend, to_tier: Backend) -> None:
        """Notify listeners of an upgrade."""
        for callback in self._on_upgrade:
            try:
                await callback(datum, from_tier, to_tier)
            except Exception as e:
                logger.warning(f"Upgrade callback error: {e}")

    async def _emit_upgrade_synergy(
        self,
        datum_id: str,
        from_tier: Backend,
        to_tier: Backend,
        reason: str = "access_pattern",
    ) -> None:
        """
        Emit synergy event for tier transition.

        Makes tier promotions visible in UI via the SynergyBus.
        """
        if not self._emit_synergy or not _HAS_SYNERGY:
            return

        # Get the bus (use injected or global singleton)
        bus = self._synergy_bus or get_synergy_bus()

        try:
            event = create_data_upgraded_event(
                datum_id=datum_id,
                old_tier=from_tier.name,
                new_tier=to_tier.name,
                reason=reason,
            )
            await bus.emit(event)
            logger.debug(
                f"Synergy: DATA_UPGRADED {datum_id[:8]}... {from_tier.name} → {to_tier.name}"
            )
        except Exception as e:
            # Don't fail upgrades if synergy emission fails
            logger.warning(f"Synergy emission failed: {e}")

    async def _handle_bus_event(self, event: DataEvent) -> None:
        """Handle DataBus events to track access patterns."""
        async with self._lock:
            if event.datum_id not in self._datum_stats:
                self._datum_stats[event.datum_id] = DatumStats(
                    id=event.datum_id,
                    tier=self.source_tier,
                    created_at=event.timestamp,
                )

            stats = self._datum_stats[event.datum_id]

            if event.event_type == DataEventType.PUT:
                stats.created_at = event.timestamp

            elif event.event_type == DataEventType.DELETE:
                # Remove tracking for deleted data
                self._datum_stats.pop(event.datum_id, None)

            # Track access (PUT counts as access too)
            stats.access_count += 1
            stats.last_accessed = event.timestamp

    def _should_upgrade(self, stats: DatumStats, now: float) -> Backend | None:
        """
        Determine if datum should upgrade, and to which tier.

        Returns the target tier or None if no upgrade needed.
        """
        policy = self.policy

        if stats.tier == Backend.MEMORY:
            # Memory → JSONL check
            if stats.access_count >= policy.memory_to_jsonl_accesses:
                return Backend.JSONL
            if now - stats.created_at >= policy.memory_to_jsonl_seconds:
                return Backend.JSONL

        elif stats.tier == Backend.JSONL:
            # JSONL → SQLite check
            if stats.access_count >= policy.jsonl_to_sqlite_accesses:
                return Backend.SQLITE
            if now - stats.created_at >= policy.jsonl_to_sqlite_seconds:
                return Backend.SQLITE

        elif stats.tier == Backend.SQLITE:
            # SQLite → Postgres only explicit
            if not policy.sqlite_to_postgres_explicit_only and stats.marked_important:
                return Backend.POSTGRES

        return None

    async def _upgrade_datum(self, datum_id: str, from_tier: Backend, to_tier: Backend) -> bool:
        """
        Upgrade a single datum from one tier to another.

        Returns True if successful.
        """
        if to_tier not in self.targets:
            logger.debug(f"No target backend for tier {to_tier}")
            return False

        target = self.targets[to_tier]

        try:
            # Get from source
            datum = await self.source.get(datum_id)
            if datum is None:
                # Already deleted
                return False

            # Write to target
            await target.put(datum)

            # Update tracking
            async with self._lock:
                if datum_id in self._datum_stats:
                    self._datum_stats[datum_id].tier = to_tier

            # Update stats
            if from_tier == Backend.MEMORY and to_tier == Backend.JSONL:
                self._stats.upgrades_memory_to_jsonl += 1
            elif from_tier == Backend.JSONL and to_tier == Backend.SQLITE:
                self._stats.upgrades_jsonl_to_sqlite += 1
            elif from_tier == Backend.SQLITE and to_tier == Backend.POSTGRES:
                self._stats.upgrades_sqlite_to_postgres += 1

            self._stats.last_upgrade_time = asyncio.get_event_loop().time()

            # Notify listeners
            await self._notify_upgrade(datum, from_tier, to_tier)

            # Emit synergy event for UI visibility
            await self._emit_upgrade_synergy(datum_id, from_tier, to_tier)

            logger.debug(f"Upgraded {datum_id[:8]}... from {from_tier} to {to_tier}")
            return True

        except Exception as e:
            logger.warning(f"Upgrade failed for {datum_id[:8]}...: {e}")
            self._stats.upgrade_failures += 1
            return False

    async def _check_upgrades(self) -> int:
        """
        Check all tracked data for upgrade candidates.

        Returns number of upgrades performed.
        """
        import time

        now = time.time()
        upgrades = 0

        async with self._lock:
            candidates = list(self._datum_stats.items())

        for datum_id, stats in candidates:
            target_tier = self._should_upgrade(stats, now)
            if target_tier is not None:
                success = await self._upgrade_datum(datum_id, stats.tier, target_tier)
                if success:
                    upgrades += 1

        return upgrades

    async def _run_loop(self) -> None:
        """Main upgrade check loop."""
        while self._running:
            try:
                await self._check_upgrades()
            except Exception as e:
                logger.error(f"Upgrade check error: {e}")

            await asyncio.sleep(self.check_interval)

    async def start(self) -> None:
        """Start the background upgrade process."""
        if self._running:
            return

        self._running = True

        # Subscribe to bus if available
        if self.bus is not None:
            self._unsubscribe = self.bus.subscribe_all(self._handle_bus_event)

        # Start background task
        self._task = asyncio.create_task(self._run_loop())
        logger.info("AutoUpgrader started")

    async def stop(self) -> None:
        """Stop the background upgrade process."""
        self._running = False

        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        # Unsubscribe from bus
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None

        logger.info("AutoUpgrader stopped")

    async def force_upgrade(self, datum_id: str, to_tier: Backend) -> bool:
        """
        Force upgrade a specific datum to a target tier.

        Bypasses the normal policy checks.
        """
        async with self._lock:
            if datum_id in self._datum_stats:
                from_tier = self._datum_stats[datum_id].tier
            else:
                from_tier = self.source_tier

        return await self._upgrade_datum(datum_id, from_tier, to_tier)

    def mark_important(self, datum_id: str) -> None:
        """Mark a datum as important (for Postgres promotion)."""
        if datum_id in self._datum_stats:
            self._datum_stats[datum_id].marked_important = True

    @property
    def stats(self) -> UpgradeStats:
        """Get upgrade statistics."""
        return self._stats

    def get_datum_stats(self, datum_id: str) -> DatumStats | None:
        """Get tracking stats for a specific datum."""
        return self._datum_stats.get(datum_id)


# --- Migration Utilities ---


async def migrate_data(
    source: DgentProtocol,
    target: DgentProtocol,
    batch_size: int = 100,
    delete_source: bool = False,
) -> int:
    """
    Migrate all data from source to target.

    Args:
        source: Source backend
        target: Target backend
        batch_size: How many records to process at once
        delete_source: Whether to delete from source after migration

    Returns:
        Number of records migrated

    Note:
        Uses a large limit internally since most backends don't support
        proper pagination. For very large datasets, consider a custom
        migration approach.
    """
    # Get all data (backends use efficient streaming internally)
    all_data = await source.list(limit=1_000_000)
    migrated = 0

    # Process in batches
    for i in range(0, len(all_data), batch_size):
        batch = all_data[i : i + batch_size]
        for datum in batch:
            await target.put(datum)
            if delete_source:
                await source.delete(datum.id)
            migrated += 1

    return migrated


async def verify_migration(
    source: DgentProtocol,
    target: DgentProtocol,
) -> tuple[bool, list[str]]:
    """
    Verify that all data in source exists in target.

    Returns:
        (success, list of missing IDs)
    """
    missing = []
    source_data = await source.list(limit=1_000_000)

    for datum in source_data:
        exists = await target.exists(datum.id)
        if not exists:
            missing.append(datum.id)

    return len(missing) == 0, missing
