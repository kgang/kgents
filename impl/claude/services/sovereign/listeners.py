"""
Sovereign Event Listeners: React to cosmos changes and reingest to SovereignStore.

> *"When content escapes K-Block isolation, it must return to the sovereign membrane."*

This module bridges the two persistence layers:
- Cosmos: Versioned content (K-Block saves go here)
- SovereignStore: Witnessed copies with extracted edges (ingested files live here)

The Pattern:
    K-Block save → Cosmos commit → KBLOCK_SAVED event → Reingest to SovereignStore

Why This Matters:
    Without reingesting, edits made via K-Block won't be reflected in:
    - WitnessedGraph edges (won't find new references)
    - Sovereign entity metadata (won't track versions)
    - Future K-Block creates (will read stale content from SovereignStore)

The Loop:
    1. User uploads file → Ingest to SovereignStore (create witnessed copy + edges)
    2. User edits via K-Block → Changes in isolation
    3. User saves (:w) → Commit to Cosmos (append-only log)
    4. KBLOCK_SAVED event → Reingest to SovereignStore (update witnessed copy + edges)
    5. User reloads → K-Block reads from Cosmos (latest version)

Teaching:
    gotcha: We reingest on SAVE, not on EDIT. Isolation means changes don't
            escape until explicitly committed. This respects the K-Block monad.

    gotcha: We use source="kblock-save" to distinguish from original ingests.
            The witness trail shows: ingest → edit → save → reingest.

See: spec/protocols/inbound-sovereignty.md
See: spec/protocols/k-block.md
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from services.witness.bus import WitnessSynergyBus

    from .ingest import Ingestor
    from .store import SovereignStore

logger = logging.getLogger(__name__)


# =============================================================================
# K-Block Save Listener
# =============================================================================


async def on_kblock_saved(
    event: dict[str, Any],
    ingestor: "Ingestor",
) -> None:
    """
    Handle KBLOCK_SAVED event by reingesting content to SovereignStore.

    When a K-Block escapes isolation (via :w save), the content is committed
    to Cosmos. We need to update the SovereignStore copy so that:
    1. Future K-Block creates read the latest content
    2. Edge extraction picks up new references
    3. WitnessedGraph sees the updated edges

    Args:
        event: The KBLOCK_SAVED event payload
        ingestor: The Ingestor instance to use

    Event payload:
        {
            "path": str,              # The cosmos path
            "kblock_id": str,         # K-Block ID
            "version_id": str,        # Cosmos version ID
            "mark_id": str | None,    # Witness mark ID (if witnessed)
            "reasoning": str | None,  # Why the save happened
            "timestamp": str,         # ISO timestamp
        }
    """
    path = event.get("path")
    version_id = event.get("version_id")
    mark_id = event.get("mark_id")

    if not path:
        logger.warning("[sovereign.listeners] KBLOCK_SAVED event missing 'path'")
        return

    logger.debug(
        f"[sovereign.listeners] KBLOCK_SAVED: {path} (version={version_id}, mark={mark_id})"
    )

    try:
        # Read the committed content from Cosmos
        # Note: We can't import Cosmos directly due to circular deps,
        # so we get it from the ingestor's store reference
        from services.k_block.core import get_cosmos

        cosmos = get_cosmos()
        content = await cosmos.read(path)

        if content is None:
            logger.warning(
                f"[sovereign.listeners] Content not found in Cosmos for {path} "
                f"(version={version_id})"
            )
            return

        # Reingest to SovereignStore
        # This will:
        # - Create a new version in the sovereign copy
        # - Extract edges from the updated content
        # - Create witness marks for the new edges
        # - Update the overlay with derived data
        await ingestor.reingest(
            path=path,
            new_content=content.encode("utf-8"),  # Cosmos stores str, SovereignStore wants bytes
            source="kblock-save",
            author="system",
        )

        logger.info(
            f"[sovereign.listeners] Reingested {path} to SovereignStore "
            f"(cosmos_version={version_id}, witness_mark={mark_id})"
        )

    except Exception as e:
        # Non-critical: don't fail the K-Block save if reingest fails
        # The content is safely in Cosmos; SovereignStore sync can be retried
        logger.error(
            f"[sovereign.listeners] Failed to reingest {path} on KBLOCK_SAVED: {e}",
            exc_info=True,
        )


# =============================================================================
# Bus Wiring
# =============================================================================


async def wire_sovereign_listeners(
    bus: "WitnessSynergyBus",
    store: "SovereignStore",
) -> list[Any]:
    """
    Wire Sovereign event listeners to the bus.

    Subscribes to:
    - KBLOCK_SAVED: Reingest content to SovereignStore after K-Block commits

    Args:
        bus: The SynergyBus instance
        store: The SovereignStore instance

    Returns:
        List of unsubscribe callbacks (for cleanup)
    """
    from services.witness.bus import WitnessTopics

    from .ingest import Ingestor

    # Create ingestor (assumes witness is available via providers)
    try:
        from services.providers import get_witness_persistence

        witness = await get_witness_persistence()
    except Exception:
        logger.warning(
            "[sovereign.listeners] Witness not available, marks won't be created on reingest"
        )
        witness = None

    ingestor = Ingestor(store, witness)

    # Subscribe to KBLOCK_SAVED
    async def kblock_saved_handler(topic: str, event: Any) -> None:
        # event should be a dict for KBLOCK_SAVED
        if isinstance(event, dict):
            await on_kblock_saved(event, ingestor)

    unsub_kblock_saved = bus.subscribe(WitnessTopics.KBLOCK_SAVED, kblock_saved_handler)

    logger.info("[sovereign.listeners] Wired to bus (KBLOCK_SAVED → reingest)")

    return [unsub_kblock_saved]


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "on_kblock_saved",
    "wire_sovereign_listeners",
]
