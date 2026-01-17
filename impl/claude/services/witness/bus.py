"""
Witness Bus Architecture: Event-Driven Cross-Jewel Communication.

Parallel to services/town/bus_wiring.py — follows the same three-bus pattern.

Event Flow:
    GitWatcherFlux ──yield──▶ WitnessDaemon
                                    │
                                    │ publish()
                                    ▼
                             WitnessSynergyBus ──▶ K-gent (thought → narrative)
                                    │            ──▶ Brain (thought → crystal)
                                    │            ──▶ Gardener (commit → plot)
                                    │
                                    │ wire_synergy_to_event()
                                    ▼
                              WitnessEventBus ──▶ SSE stream
                                              ──▶ WebSocket
                                              ──▶ CLI logging

Key Principle (from meta.md):
    "Timer-driven loops create zombies—use event-driven Flux"

See: docs/skills/data-bus-integration.md
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)


# =============================================================================
# Type Definitions
# =============================================================================

WitnessEventHandler = Callable[[Any], Awaitable[None]]
SynergyHandler = Callable[[str, Any], Awaitable[None]]
UnsubscribeFunc = Callable[[], None]


# =============================================================================
# WitnessTopics (Namespace Constants)
# =============================================================================


class WitnessTopics:
    """Topic namespace for witness events."""

    # Git events
    GIT_COMMIT = "witness.git.commit"
    GIT_CHECKOUT = "witness.git.checkout"
    GIT_PUSH = "witness.git.push"
    GIT_MERGE = "witness.git.merge"

    # Mark events (API-created marks)
    MARK_CREATED = "witness.mark.created"
    MARK_RETRACTED = "witness.mark.retracted"

    # Thought events
    THOUGHT_CAPTURED = "witness.thought.captured"

    # Constitutional events (Phase 1: Constitutional Enforcement)
    CONSTITUTIONAL_EVALUATED = "witness.constitutional.evaluated"

    # Trail events (Context Perception integration - Phase 4)
    TRAIL_CAPTURED = "witness.trail.captured"

    # K-Block events (Membrane integration - Editing IS Witnessing)
    KBLOCK_EDITED = "witness.kblock.edited"
    KBLOCK_SAVED = "witness.kblock.saved"
    KBLOCK_DISCARDED = "witness.kblock.discarded"

    # Daemon lifecycle
    DAEMON_STARTED = "witness.daemon.started"
    DAEMON_STOPPED = "witness.daemon.stopped"

    # AGENTESE events (Law 3: Every invocation emits Mark)
    AGENTESE_INVOKED = "witness.agentese.invoked"
    AGENTESE_COMPLETED = "witness.agentese.completed"
    AGENTESE_ERROR = "witness.agentese.error"

    # Spec Ledger events (Living Spec integration)
    SPEC_SCANNED = "witness.spec.scanned"
    SPEC_DEPRECATED = "witness.spec.deprecated"
    SPEC_EVIDENCE_ADDED = "witness.spec.evidence_added"
    SPEC_CONTRADICTION_FOUND = "witness.spec.contradiction"
    SPEC_ORPHAN_DETECTED = "witness.spec.orphan"

    # Proxy Handle events (AD-015: Transparent Batch Processes)
    PROXY_STARTED = "witness.proxy.started"
    PROXY_COMPLETED = "witness.proxy.completed"
    PROXY_FAILED = "witness.proxy.failed"
    PROXY_STALE = "witness.proxy.stale"

    # Sovereign Ingest events (Inbound Sovereignty ingest flow)
    SOVEREIGN_INGESTED = "witness.sovereign.ingested"

    # Sovereign Analysis events (Inbound Sovereignty analysis flow)
    SOVEREIGN_ANALYSIS_STARTED = "witness.sovereign.analysis_started"
    SOVEREIGN_ANALYSIS_COMPLETED = "witness.sovereign.analysis_completed"
    SOVEREIGN_ANALYSIS_FAILED = "witness.sovereign.analysis_failed"
    SOVEREIGN_PLACEHOLDER_CREATED = "witness.sovereign.placeholder_created"

    # Document Director events (Full lifecycle orchestration)
    DIRECTOR_ANALYSIS_COMPLETE = "witness.director.analysis_complete"
    DIRECTOR_PROMPT_GENERATED = "witness.director.prompt_generated"
    DIRECTOR_EXECUTION_CAPTURED = "witness.director.execution_captured"
    DIRECTOR_PLACEHOLDER_RESOLVED = "witness.director.placeholder_resolved"
    DIRECTOR_STATUS_CHANGED = "witness.director.status_changed"

    # Dialectic Fusion events (Kent+Claude synthesis)
    DIALECTIC_THESIS = "witness.dialectic.thesis"
    DIALECTIC_ANTITHESIS = "witness.dialectic.antithesis"
    DIALECTIC_SYNTHESIS = "witness.dialectic.synthesis"
    DIALECTIC_VETO = "witness.dialectic.veto"

    # Axiom Discovery events (Personal axiom discovery)
    AXIOM_DISCOVERED = "witness.axiom.discovered"
    AXIOM_VALIDATED = "witness.axiom.validated"
    AXIOM_CONTRADICTION = "witness.axiom.contradiction"

    # Skill Injection events (JIT skill surfacing)
    SKILL_INJECTED = "witness.skill.injected"
    SKILL_OUTCOME_RECORDED = "witness.skill.outcome_recorded"
    SKILL_COMPOSITION_SUGGESTED = "witness.skill.composition_suggested"

    # Wildcards
    ALL = "witness.*"
    MARK_ALL = "witness.mark.*"
    GIT_ALL = "witness.git.*"
    THOUGHT_ALL = "witness.thought.*"
    CONSTITUTIONAL_ALL = "witness.constitutional.*"
    TRAIL_ALL = "witness.trail.*"
    KBLOCK_ALL = "witness.kblock.*"
    DAEMON_ALL = "witness.daemon.*"
    AGENTESE_ALL = "witness.agentese.*"
    SPEC_ALL = "witness.spec.*"
    PROXY_ALL = "witness.proxy.*"
    SOVEREIGN_ALL = "witness.sovereign.*"
    DIRECTOR_ALL = "witness.director.*"
    DIALECTIC_ALL = "witness.dialectic.*"
    AXIOM_ALL = "witness.axiom.*"
    SKILL_ALL = "witness.skill.*"


# =============================================================================
# WitnessEventType (SSE Event Type Enum)
# =============================================================================


import os
from enum import Enum


class WitnessEventType(Enum):
    """
    SSE event types sent to frontend via /api/witness/stream.

    SINGLE SOURCE OF TRUTH for backend/frontend event type contract.

    When adding a new event type:
    1. Add enum member here
    2. Add topic mapping(s) in TOPIC_TO_EVENT_TYPE below
    3. Add handler in web/src/hooks/useWitnessStream.ts

    Philosophy:
        "Fail fast, fail loud. Unknown events are bugs, not features."
    """

    # Core events (always visible in witness stream)
    MARK = "mark"
    THOUGHT = "thought"
    CRYSTAL = "crystal"
    KBLOCK = "kblock"
    TRAIL = "trail"

    # Domain events
    SPEC = "spec"
    SOVEREIGN = "sovereign"
    DIRECTOR = "director"
    GIT = "git"
    AGENTESE = "agentese"
    CONSTITUTIONAL = "constitutional"
    PROXY = "proxy"
    DIALECTIC = "dialectic"
    AXIOM = "axiom"
    SKILL = "skill"

    # Lifecycle events (internal, may not need UI handler)
    DAEMON = "daemon"

    # Connection events (special, handled separately in SSE)
    CONNECTED = "connected"
    HEARTBEAT = "heartbeat"

    @property
    def requires_frontend_handler(self) -> bool:
        """Whether this event type must have a frontend SSE handler."""
        # Internal/connection events don't need UI representation
        return self not in {
            WitnessEventType.DAEMON,
            WitnessEventType.HEARTBEAT,
            WitnessEventType.CONNECTED,
        }


# =============================================================================
# Topic to Event Type Mapping (Exhaustive)
# =============================================================================


TOPIC_TO_EVENT_TYPE: dict[str, WitnessEventType] = {
    # Git events → GIT
    WitnessTopics.GIT_COMMIT: WitnessEventType.GIT,
    WitnessTopics.GIT_CHECKOUT: WitnessEventType.GIT,
    WitnessTopics.GIT_PUSH: WitnessEventType.GIT,
    WitnessTopics.GIT_MERGE: WitnessEventType.GIT,
    # Mark events → MARK
    WitnessTopics.MARK_CREATED: WitnessEventType.MARK,
    WitnessTopics.MARK_RETRACTED: WitnessEventType.MARK,
    # Thought events → THOUGHT
    WitnessTopics.THOUGHT_CAPTURED: WitnessEventType.THOUGHT,
    # Constitutional events → CONSTITUTIONAL
    WitnessTopics.CONSTITUTIONAL_EVALUATED: WitnessEventType.CONSTITUTIONAL,
    # Trail events → TRAIL
    WitnessTopics.TRAIL_CAPTURED: WitnessEventType.TRAIL,
    # K-Block events → KBLOCK
    WitnessTopics.KBLOCK_EDITED: WitnessEventType.KBLOCK,
    WitnessTopics.KBLOCK_SAVED: WitnessEventType.KBLOCK,
    WitnessTopics.KBLOCK_DISCARDED: WitnessEventType.KBLOCK,
    # Daemon lifecycle → DAEMON
    WitnessTopics.DAEMON_STARTED: WitnessEventType.DAEMON,
    WitnessTopics.DAEMON_STOPPED: WitnessEventType.DAEMON,
    # AGENTESE events → AGENTESE
    WitnessTopics.AGENTESE_INVOKED: WitnessEventType.AGENTESE,
    WitnessTopics.AGENTESE_COMPLETED: WitnessEventType.AGENTESE,
    WitnessTopics.AGENTESE_ERROR: WitnessEventType.AGENTESE,
    # Spec Ledger events → SPEC
    WitnessTopics.SPEC_SCANNED: WitnessEventType.SPEC,
    WitnessTopics.SPEC_DEPRECATED: WitnessEventType.SPEC,
    WitnessTopics.SPEC_EVIDENCE_ADDED: WitnessEventType.SPEC,
    WitnessTopics.SPEC_CONTRADICTION_FOUND: WitnessEventType.SPEC,
    WitnessTopics.SPEC_ORPHAN_DETECTED: WitnessEventType.SPEC,
    # Proxy Handle events → PROXY
    WitnessTopics.PROXY_STARTED: WitnessEventType.PROXY,
    WitnessTopics.PROXY_COMPLETED: WitnessEventType.PROXY,
    WitnessTopics.PROXY_FAILED: WitnessEventType.PROXY,
    WitnessTopics.PROXY_STALE: WitnessEventType.PROXY,
    # Sovereign events → SOVEREIGN
    WitnessTopics.SOVEREIGN_INGESTED: WitnessEventType.SOVEREIGN,
    WitnessTopics.SOVEREIGN_ANALYSIS_STARTED: WitnessEventType.SOVEREIGN,
    WitnessTopics.SOVEREIGN_ANALYSIS_COMPLETED: WitnessEventType.SOVEREIGN,
    WitnessTopics.SOVEREIGN_ANALYSIS_FAILED: WitnessEventType.SOVEREIGN,
    WitnessTopics.SOVEREIGN_PLACEHOLDER_CREATED: WitnessEventType.SOVEREIGN,
    # Director events → DIRECTOR
    WitnessTopics.DIRECTOR_ANALYSIS_COMPLETE: WitnessEventType.DIRECTOR,
    WitnessTopics.DIRECTOR_PROMPT_GENERATED: WitnessEventType.DIRECTOR,
    WitnessTopics.DIRECTOR_EXECUTION_CAPTURED: WitnessEventType.DIRECTOR,
    WitnessTopics.DIRECTOR_PLACEHOLDER_RESOLVED: WitnessEventType.DIRECTOR,
    WitnessTopics.DIRECTOR_STATUS_CHANGED: WitnessEventType.DIRECTOR,
    # Dialectic Fusion events → DIALECTIC
    WitnessTopics.DIALECTIC_THESIS: WitnessEventType.DIALECTIC,
    WitnessTopics.DIALECTIC_ANTITHESIS: WitnessEventType.DIALECTIC,
    WitnessTopics.DIALECTIC_SYNTHESIS: WitnessEventType.DIALECTIC,
    WitnessTopics.DIALECTIC_VETO: WitnessEventType.DIALECTIC,
    # Axiom Discovery events → AXIOM
    WitnessTopics.AXIOM_DISCOVERED: WitnessEventType.AXIOM,
    WitnessTopics.AXIOM_VALIDATED: WitnessEventType.AXIOM,
    WitnessTopics.AXIOM_CONTRADICTION: WitnessEventType.AXIOM,
    # Skill Injection events → SKILL
    WitnessTopics.SKILL_INJECTED: WitnessEventType.SKILL,
    WitnessTopics.SKILL_OUTCOME_RECORDED: WitnessEventType.SKILL,
    WitnessTopics.SKILL_COMPOSITION_SUGGESTED: WitnessEventType.SKILL,
}


def get_event_type_for_topic(topic: str) -> WitnessEventType:
    """
    Get the SSE event type for a WitnessTopics value.

    FAILS LOUDLY on unknown topics in development.

    Args:
        topic: The WitnessTopics value (e.g., "witness.git.commit")

    Returns:
        The corresponding WitnessEventType

    Raises:
        ValueError: If topic is not mapped (development mode only)

    Note:
        In production, logs error and returns MARK as fallback.
        In development, raises ValueError to catch misconfigurations early.
    """
    event_type = TOPIC_TO_EVENT_TYPE.get(topic)

    if event_type is not None:
        return event_type

    # Unknown topic - this is a bug!
    error_msg = (
        f"Unknown WitnessTopics value: '{topic}'\n\n"
        f"FIX: Add mapping in services/witness/bus.py TOPIC_TO_EVENT_TYPE:\n"
        f"    WitnessTopics.YOUR_TOPIC: WitnessEventType.YOUR_TYPE,\n\n"
        f"Available event types: {[e.value for e in WitnessEventType]}"
    )

    # Fail hard in development
    env = os.environ.get("KGENTS_ENV", "development")
    if env == "development":
        raise ValueError(error_msg)

    # Log and fallback in production
    logger.error(error_msg)
    return WitnessEventType.MARK


def _assert_all_topics_mapped() -> None:
    """
    Import-time validation: Ensure ALL WitnessTopics are mapped.

    Called at module load to catch missing mappings immediately.

    Raises:
        AssertionError: If any non-wildcard topic is unmapped
    """
    all_attrs = [attr for attr in dir(WitnessTopics) if not attr.startswith("_") and attr.isupper()]

    unmapped: list[str] = []
    for attr in all_attrs:
        topic = getattr(WitnessTopics, attr)
        # Skip wildcards (end with *)
        if topic.endswith("*"):
            continue
        if topic not in TOPIC_TO_EVENT_TYPE:
            unmapped.append(f"WitnessTopics.{attr} = '{topic}'")

    if unmapped:
        raise AssertionError(
            "Unmapped WitnessTopics found! Add to TOPIC_TO_EVENT_TYPE:\n"
            + "\n".join(f"  - {t}" for t in unmapped)
        )


# Run validation at import time (fail fast, fail loud)
_assert_all_topics_mapped()


# =============================================================================
# WitnessSynergyBus (Cross-Jewel Pub/Sub)
# =============================================================================


@dataclass
class WitnessSynergyBus:
    """
    Cross-jewel pub/sub bus with wildcard support.

    Follows TownSynergyBus pattern exactly:
    - Exact topic subscriptions
    - Wildcard subscriptions (e.g., "witness.git.*")
    - Non-blocking handler notification
    - Error isolation per handler
    """

    _handlers: dict[str, list[SynergyHandler]] = field(default_factory=dict)
    _wildcard_handlers: list[tuple[str, SynergyHandler]] = field(default_factory=list)
    _emit_count: int = 0
    _error_count: int = 0

    async def publish(self, topic: str, event: Any) -> None:
        """
        Publish an event to a topic.

        Notifies:
        1. Exact topic subscribers
        2. Wildcard subscribers (e.g., "witness.*" matches "witness.git.commit")
        """
        self._emit_count += 1

        # Exact match handlers
        handlers = list(self._handlers.get(topic, []))

        # Wildcard handlers
        for pattern, handler in self._wildcard_handlers:
            if self._matches_wildcard(pattern, topic):
                handlers.append(handler)

        # Notify all (non-blocking, isolated)
        for handler in handlers:
            asyncio.create_task(self._safe_notify(handler, topic, event))

    def subscribe(self, topic: str, handler: SynergyHandler) -> UnsubscribeFunc:
        """
        Subscribe to a topic.

        Supports wildcards:
        - "witness.*" matches all witness events
        - "witness.git.*" matches all git events
        """
        if "*" in topic:
            self._wildcard_handlers.append((topic, handler))

            def unsubscribe() -> None:
                try:
                    self._wildcard_handlers.remove((topic, handler))
                except ValueError:
                    pass

        else:
            self._handlers.setdefault(topic, []).append(handler)

            def unsubscribe() -> None:
                try:
                    self._handlers[topic].remove(handler)
                except (KeyError, ValueError):
                    pass

        return unsubscribe

    def _matches_wildcard(self, pattern: str, topic: str) -> bool:
        """Check if topic matches wildcard pattern."""
        if not pattern.endswith("*"):
            return pattern == topic

        prefix = pattern[:-1]  # Remove *
        return topic.startswith(prefix)

    async def _safe_notify(self, handler: SynergyHandler, topic: str, event: Any) -> None:
        """Safely notify a handler, catching exceptions."""
        try:
            await handler(topic, event)
        except Exception as e:
            self._error_count += 1
            logger.error(f"WitnessSynergyBus handler error on {topic}: {e}")

    @property
    def stats(self) -> dict[str, int]:
        """Get bus statistics."""
        return {
            "total_emitted": self._emit_count,
            "total_errors": self._error_count,
            "topic_count": len(self._handlers),
            "wildcard_count": len(self._wildcard_handlers),
        }

    def clear(self) -> None:
        """Clear all handlers (for testing)."""
        self._handlers.clear()
        self._wildcard_handlers.clear()
        self._emit_count = 0
        self._error_count = 0


# =============================================================================
# WitnessEventBus (Fan-out to UI)
# =============================================================================


@dataclass
class WitnessEventBus:
    """
    EventBus for UI fan-out.

    Subscribers receive all events.
    Used for SSE streams, WebSocket connections, CLI logging.
    """

    _subscribers: list[WitnessEventHandler] = field(default_factory=list)
    _emit_count: int = 0
    _dropped_count: int = 0

    async def publish(self, event: Any) -> None:
        """Publish event to all subscribers."""
        self._emit_count += 1

        for subscriber in list(self._subscribers):
            asyncio.create_task(self._safe_notify(subscriber, event))

    def subscribe(self, handler: WitnessEventHandler) -> UnsubscribeFunc:
        """Subscribe to all events."""
        self._subscribers.append(handler)

        def unsubscribe() -> None:
            try:
                self._subscribers.remove(handler)
            except ValueError:
                pass

        return unsubscribe

    async def _safe_notify(self, handler: WitnessEventHandler, event: Any) -> None:
        """Safely notify a handler."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"WitnessEventBus handler error: {e}")

    @property
    def stats(self) -> dict[str, int]:
        """Get bus statistics."""
        return {
            "total_emitted": self._emit_count,
            "subscriber_count": len(self._subscribers),
            "dropped_count": self._dropped_count,
        }

    def clear(self) -> None:
        """Clear all subscribers (for testing)."""
        self._subscribers.clear()
        self._emit_count = 0
        self._dropped_count = 0


# =============================================================================
# Wiring Functions
# =============================================================================


def wire_synergy_to_event(
    synergy_bus: WitnessSynergyBus,
    event_bus: WitnessEventBus,
    topics: list[str] | None = None,
) -> list[UnsubscribeFunc]:
    """
    Wire SynergyBus topics to EventBus fan-out.

    This enables UI subscribers to receive witness events.

    Args:
        synergy_bus: Source synergy bus
        event_bus: Target event bus
        topics: Topics to wire (default: all witness topics)

    Returns:
        List of unsubscribe functions
    """
    unsubscribes: list[UnsubscribeFunc] = []

    if topics is None:
        topics = [WitnessTopics.ALL]

    for topic in topics:

        async def handler(t: str, event: Any) -> None:
            await event_bus.publish(event)

        unsub = synergy_bus.subscribe(topic, handler)
        unsubscribes.append(unsub)

    return unsubscribes


def wire_witness_to_global_synergy(
    witness_bus: WitnessSynergyBus,
) -> list[UnsubscribeFunc]:
    """
    Bridge Witness events to the global SynergyBus.

    This enables cross-jewel handlers to receive Witness events:
    - WitnessToBrainHandler: Captures thoughts as crystals
    - WitnessToGardenHandler: Updates plots from commits

    Args:
        witness_bus: Local Witness synergy bus

    Returns:
        List of unsubscribe functions
    """
    from protocols.synergy import SynergyEventType, get_synergy_bus
    from protocols.synergy.events import (
        create_witness_daemon_started_event,
        create_witness_daemon_stopped_event,
        create_witness_git_commit_event,
        create_witness_thought_event,
    )

    unsubscribes: list[UnsubscribeFunc] = []
    global_bus = get_synergy_bus()

    # Map witness topics to SynergyEvent factories
    async def bridge_thought(topic: str, event: Any) -> None:
        """Bridge thought events to global synergy."""
        if not isinstance(event, dict):
            return

        synergy_event = create_witness_thought_event(
            thought_id=event.get("thought_id", "unknown"),
            content=event.get("content", ""),
            source=event.get("source", "witness"),
            tags=event.get("tags", []),
            confidence=event.get("confidence", 1.0),
        )
        await global_bus.emit(synergy_event)

    async def bridge_git_commit(topic: str, event: Any) -> None:
        """Bridge git commit events to global synergy."""
        if not isinstance(event, dict):
            return

        synergy_event = create_witness_git_commit_event(
            commit_hash=event.get("commit_hash", "unknown"),
            author_email=event.get("author_email", "unknown"),
            message=event.get("message", ""),
            files_changed=event.get("files_changed", 0),
            insertions=event.get("insertions", 0),
            deletions=event.get("deletions", 0),
        )
        await global_bus.emit(synergy_event)

    async def bridge_daemon_started(topic: str, event: Any) -> None:
        """Bridge daemon started events to global synergy."""
        if not isinstance(event, dict):
            return

        synergy_event = create_witness_daemon_started_event(
            daemon_id=event.get("daemon_id", "unknown"),
            pid=event.get("pid", 0),
            watched_paths=event.get("watched_paths", []),
        )
        await global_bus.emit(synergy_event)

    async def bridge_daemon_stopped(topic: str, event: Any) -> None:
        """Bridge daemon stopped events to global synergy."""
        if not isinstance(event, dict):
            return

        synergy_event = create_witness_daemon_stopped_event(
            daemon_id=event.get("daemon_id", "unknown"),
            pid=event.get("pid", 0),
            uptime_seconds=event.get("uptime_seconds", 0.0),
            thoughts_captured=event.get("thoughts_captured", 0),
        )
        await global_bus.emit(synergy_event)

    # Subscribe to specific topics
    unsubscribes.append(witness_bus.subscribe(WitnessTopics.THOUGHT_CAPTURED, bridge_thought))
    unsubscribes.append(witness_bus.subscribe(WitnessTopics.GIT_COMMIT, bridge_git_commit))
    unsubscribes.append(witness_bus.subscribe(WitnessTopics.DAEMON_STARTED, bridge_daemon_started))
    unsubscribes.append(witness_bus.subscribe(WitnessTopics.DAEMON_STOPPED, bridge_daemon_stopped))

    logger.info("Witness → Global SynergyBus bridge wired")
    return unsubscribes


def register_witness_handlers() -> list[UnsubscribeFunc]:
    """
    Register Witness handlers with the global SynergyBus.

    This enables cross-jewel processing of Witness events:
    - WITNESS_THOUGHT_CAPTURED → WitnessToBrainHandler → Brain crystals
    - WITNESS_GIT_COMMIT → WitnessToBrainHandler → Brain crystals

    Note: Garden handlers deprecated 2025-12-21.
    See: spec/protocols/_archive/gardener-evergreen-heritage.md

    Returns:
        List of unsubscribe functions for cleanup
    """
    from protocols.synergy import SynergyEventType, get_synergy_bus
    from protocols.synergy.handlers import WitnessToBrainHandler

    global_bus = get_synergy_bus()
    unsubscribes: list[UnsubscribeFunc] = []

    # Create handlers (auto_capture=True for production)
    brain_handler = WitnessToBrainHandler(auto_capture=True)

    # Register brain handler for thought events
    unsubscribes.append(
        global_bus.register(SynergyEventType.WITNESS_THOUGHT_CAPTURED, brain_handler)
    )
    # Brain also handles git commits (for crystal capture)
    unsubscribes.append(global_bus.register(SynergyEventType.WITNESS_GIT_COMMIT, brain_handler))

    logger.info("Witness handlers registered with global SynergyBus")
    return unsubscribes


# =============================================================================
# WitnessBusManager (Orchestrator)
# =============================================================================


@dataclass
class WitnessBusManager:
    """
    Manages the two-bus architecture for Witness.

    Note: Witness uses SynergyBus + EventBus (no DataBus layer).
    The daemon publishes directly to SynergyBus.

    Provides lifecycle management and wiring coordination.
    """

    synergy_bus: WitnessSynergyBus = field(default_factory=WitnessSynergyBus)
    event_bus: WitnessEventBus = field(default_factory=WitnessEventBus)
    _wiring_unsubs: list[UnsubscribeFunc] = field(default_factory=list)
    _cross_jewel_unsubs: list[UnsubscribeFunc] = field(default_factory=list)
    _is_wired: bool = False

    def wire_all(self) -> None:
        """Wire all buses together."""
        if self._is_wired:
            return

        # SynergyBus → EventBus (all witness topics)
        self._wiring_unsubs.extend(wire_synergy_to_event(self.synergy_bus, self.event_bus))

        self._is_wired = True

    def wire_cross_jewel_handlers(self) -> None:
        """
        Wire cross-jewel event handlers.

        Handlers registered:
        - WitnessToBrainHandler: thought → crystal storage

        Note: Garden handlers deprecated 2025-12-21.

        Also bridges local WitnessSynergyBus → global SynergyBus.
        """
        # Bridge local bus to global synergy
        bridge_unsubs = wire_witness_to_global_synergy(self.synergy_bus)
        self._cross_jewel_unsubs.extend(bridge_unsubs)

        # Register handlers with global bus
        handler_unsubs = register_witness_handlers()
        self._cross_jewel_unsubs.extend(handler_unsubs)

        logger.info("Witness cross-jewel handlers wired")

    def unwire_all(self) -> None:
        """Disconnect all wiring."""
        for unsub in self._wiring_unsubs:
            unsub()
        self._wiring_unsubs.clear()

        for unsub in self._cross_jewel_unsubs:
            unsub()
        self._cross_jewel_unsubs.clear()

        self._is_wired = False

    def clear(self) -> None:
        """Clear all buses and wiring (for testing)."""
        self.unwire_all()
        self.synergy_bus.clear()
        self.event_bus.clear()

    @property
    def stats(self) -> dict[str, dict[str, int]]:
        """Get combined statistics."""
        return {
            "synergy_bus": self.synergy_bus.stats,
            "event_bus": self.event_bus.stats,
        }


# =============================================================================
# Global Instance
# =============================================================================

_witness_bus_manager: WitnessBusManager | None = None


def get_witness_bus_manager() -> WitnessBusManager:
    """Get the global WitnessBusManager instance."""
    global _witness_bus_manager
    if _witness_bus_manager is None:
        _witness_bus_manager = WitnessBusManager()
    return _witness_bus_manager


def reset_witness_bus_manager() -> None:
    """Reset the global WitnessBusManager (for testing)."""
    global _witness_bus_manager
    if _witness_bus_manager is not None:
        _witness_bus_manager.clear()
    _witness_bus_manager = None


def get_synergy_bus() -> WitnessSynergyBus:
    """
    Get the global WitnessSynergyBus.

    Convenience function for code that needs to publish to the bus
    without managing the full WitnessBusManager lifecycle.

    Used by AgenteseGateway for Mark event publishing.
    """
    return get_witness_bus_manager().synergy_bus


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Topics
    "WitnessTopics",
    # Event Types (Single Source of Truth)
    "WitnessEventType",
    "TOPIC_TO_EVENT_TYPE",
    "get_event_type_for_topic",
    # Buses
    "WitnessSynergyBus",
    "WitnessEventBus",
    # Wiring
    "wire_synergy_to_event",
    "wire_witness_to_global_synergy",
    "register_witness_handlers",
    # Manager
    "WitnessBusManager",
    "get_witness_bus_manager",
    "reset_witness_bus_manager",
    "get_synergy_bus",
    # Types
    "WitnessEventHandler",
    "SynergyHandler",
    "UnsubscribeFunc",
]
