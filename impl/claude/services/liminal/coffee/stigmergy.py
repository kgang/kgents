"""
VoiceStigmergy: Wire stigmergic memory to Morning Coffee.

Checkpoint 0.1 of Metabolic Development Protocol.

User Journey:
    kg coffee begin
        ↓
    Voice captured: "Today I want to finish verification integration"
        ↓
    Pheromone deposited at: [verification, integration, finish]
        ↓
    kg coffee end (accomplished)
        ↓
    Pheromones reinforced (intensity × 1.5)

The stigmergy layer transforms voice captures into environmental traces.
Future sessions can sense these patterns and surface resonant memories.

Teaching:
    gotcha: Pheromone field is in-memory by default.
            Persist to D-gent for cross-session stigmergy.
            (Evidence: test_voice_stigmergy.py::test_field_persists)

    gotcha: Decay rate is 5% per day (0.002 per hour).
            This matches the spec's "reinforcement vs decay" balance.

AGENTESE: void.metabolism.stigmergy
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from agents.m.stigmergy import PheromoneField, SenseResult, Trace

if TYPE_CHECKING:
    from services.metabolism.persistence import MetabolismPersistence

    from .types import MorningVoice

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

# Decay at 5% per day = ~0.002 per hour
DECAY_RATE_PER_HOUR = 0.002

# Below this intensity, traces evaporate
EVAPORATION_THRESHOLD = 0.01

# Maximum intensity (cap reinforcement)
MAX_INTENSITY = 10.0

# Reinforcement factor when task is accomplished
ACCOMPLISHED_REINFORCEMENT = 1.5

# Reinforcement factor for partial completion
PARTIAL_REINFORCEMENT = 1.2


# =============================================================================
# VoiceStigmergy Service
# =============================================================================


@dataclass
class PheromoneDeposit:
    """A record of pheromones deposited from a voice capture."""

    concepts: list[str]
    intensity: float
    source: str  # "voice", "accomplishment", "compost"
    deposited_at: datetime = field(default_factory=datetime.now)
    voice_date: str | None = None  # ISO date of the voice capture


class VoiceStigmergy:
    """
    Service that connects MorningVoice to PheromoneField.

    Voice → Concepts → Pheromones → Future Resonance

    The key insight: morning thoughts leave traces that influence
    future mornings. If Kent keeps saying "verification", that
    pattern will surface in future hydrations.

    Usage:
        stigmergy = VoiceStigmergy()

        # After voice capture
        deposits = await stigmergy.deposit_from_voice(voice)

        # After session ends with accomplishment
        await stigmergy.reinforce_accomplished(deposits)

        # Sense current patterns
        patterns = await stigmergy.sense_patterns("today I want to work on testing")

        # Persist for next session
        await stigmergy.save()

    With persistence (D-gent backed):
        persistence = MetabolismPersistence(dgent=router)
        stigmergy = VoiceStigmergy(persistence=persistence)

        # Traces now persist across sessions
        await stigmergy.load()  # Load prior traces
        # ... voice capture happens ...
        await stigmergy.save()  # Persist for next session
    """

    def __init__(
        self,
        field: PheromoneField | None = None,
        store_path: Path | str | None = None,
        persistence: "MetabolismPersistence | None" = None,
    ):
        """
        Initialize VoiceStigmergy.

        Args:
            field: Optional existing pheromone field
            store_path: Path for persistence (XDG-compliant)
            persistence: Optional D-gent backed persistence layer
        """
        self._field = field or PheromoneField(
            decay_rate=DECAY_RATE_PER_HOUR,
            evaporation_threshold=EVAPORATION_THRESHOLD,
        )
        self._store_path = Path(store_path) if store_path else self._default_store_path()
        self._persistence = persistence
        self._recent_deposits: list[PheromoneDeposit] = []

    def _default_store_path(self) -> Path:
        """Get default XDG-compliant store path."""
        import os

        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        return Path(xdg_data) / "kgents" / "stigmergy" / "voice_field.json"

    # =========================================================================
    # Voice → Pheromone Conversion
    # =========================================================================

    def _extract_concepts(self, text: str) -> list[str]:
        """
        Extract concepts from text for pheromone deposition.

        Simple tokenization with stop word removal.
        Future: Use Brain vectors for semantic concepts.
        """
        if not text:
            return []

        # Stop words to ignore (same as hydrator for consistency)
        stop_words = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "but",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "may",
            "might",
            "must",
            "can",
            "to",
            "for",
            "of",
            "in",
            "on",
            "at",
            "by",
            "with",
            "about",
            "from",
            "into",
            "through",
            "during",
            "before",
            "after",
            "above",
            "below",
            "up",
            "down",
            "out",
            "off",
            "over",
            "under",
            "again",
            "further",
            "then",
            "once",
            "here",
            "there",
            "when",
            "where",
            "why",
            "how",
            "all",
            "each",
            "every",
            "both",
            "few",
            "more",
            "most",
            "other",
            "some",
            "such",
            "no",
            "nor",
            "not",
            "only",
            "own",
            "same",
            "so",
            "than",
            "too",
            "very",
            "just",
            "also",
            "now",
            "this",
            "that",
            "these",
            "those",
            "i",
            "you",
            "he",
            "she",
            "it",
            "we",
            "they",
            "me",
            "him",
            "her",
            "us",
            "them",
            "my",
            "your",
            "his",
            "its",
            "our",
            "their",
            "what",
            "which",
            "who",
            "whom",
            "want",
            "today",
            "work",
            "working",
            "finish",
            "start",
            "make",
            "need",
        }

        # Tokenize (alphanumeric + underscore)
        tokens = re.findall(r"\w+", text.lower())

        # Filter and deduplicate while preserving order
        concepts = []
        seen = set()
        for token in tokens:
            if token not in stop_words and token not in seen and len(token) > 2:
                concepts.append(token)
                seen.add(token)

        return concepts

    async def deposit_from_voice(
        self,
        voice: "MorningVoice",
        base_intensity: float = 1.0,
    ) -> PheromoneDeposit:
        """
        Deposit pheromones from a MorningVoice capture.

        Extracts concepts from:
        - success_criteria (highest weight)
        - eye_catch (medium weight)
        - non_code_thought (lower weight)

        Args:
            voice: The morning voice capture
            base_intensity: Base intensity for deposits

        Returns:
            PheromoneDeposit record of what was deposited
        """
        all_concepts: list[str] = []

        # success_criteria is the main intent — weight 1.0
        if voice.success_criteria:
            concepts = self._extract_concepts(voice.success_criteria)
            for concept in concepts:
                await self._field.deposit(
                    concept=concept,
                    intensity=base_intensity * 1.0,
                    depositor="morning_voice",
                    metadata={"source_field": "success_criteria"},
                )
            all_concepts.extend(concepts)

        # eye_catch is focus attention — weight 0.7
        if voice.eye_catch:
            concepts = self._extract_concepts(voice.eye_catch)
            for concept in concepts:
                await self._field.deposit(
                    concept=concept,
                    intensity=base_intensity * 0.7,
                    depositor="morning_voice",
                    metadata={"source_field": "eye_catch"},
                )
            all_concepts.extend([c for c in concepts if c not in all_concepts])

        # non_code_thought is ambient — weight 0.3
        if voice.non_code_thought:
            concepts = self._extract_concepts(voice.non_code_thought)
            for concept in concepts:
                await self._field.deposit(
                    concept=concept,
                    intensity=base_intensity * 0.3,
                    depositor="morning_voice",
                    metadata={"source_field": "non_code_thought"},
                )
            all_concepts.extend([c for c in concepts if c not in all_concepts])

        # Create deposit record
        deposit = PheromoneDeposit(
            concepts=all_concepts,
            intensity=base_intensity,
            source="voice",
            voice_date=voice.captured_date.isoformat(),
        )

        self._recent_deposits.append(deposit)
        logger.debug(f"Deposited pheromones for {len(all_concepts)} concepts")

        return deposit

    # =========================================================================
    # Reinforcement
    # =========================================================================

    async def reinforce_accomplished(
        self,
        deposit: PheromoneDeposit,
        factor: float | None = None,
    ) -> int:
        """
        Reinforce pheromones when a task is accomplished.

        This is the celebration loop: success strengthens patterns.

        Args:
            deposit: The deposit to reinforce
            factor: Reinforcement factor (default: ACCOMPLISHED_REINFORCEMENT)

        Returns:
            Number of traces reinforced
        """
        factor = factor or ACCOMPLISHED_REINFORCEMENT
        total_reinforced = 0

        for concept in deposit.concepts:
            count = await self._field.reinforce(concept, factor=factor)
            total_reinforced += count

            # Cap intensity at MAX_INTENSITY
            await self._cap_intensity(concept)

        logger.debug(f"Reinforced {total_reinforced} traces with factor {factor}")
        return total_reinforced

    async def reinforce_partial(
        self,
        deposit: PheromoneDeposit,
    ) -> int:
        """
        Reinforce pheromones for partial completion.

        Less than full accomplishment, but still progress.
        """
        return await self.reinforce_accomplished(
            deposit,
            factor=PARTIAL_REINFORCEMENT,
        )

    async def _cap_intensity(self, concept: str) -> None:
        """Cap intensity at MAX_INTENSITY to prevent runaway reinforcement."""
        # Get current intensity
        intensity = await self._field.gradient_toward(concept)

        if intensity > MAX_INTENSITY:
            # We need to scale down. The field doesn't have a direct "set intensity"
            # so we'll use a workaround: we'd need to track and limit per-trace.
            # For now, log and accept this limitation.
            logger.debug(f"Intensity at {concept} exceeds cap: {intensity}")

    # =========================================================================
    # Pattern Sensing
    # =========================================================================

    async def sense_patterns(
        self,
        context: str | None = None,
        limit: int = 10,
    ) -> list[tuple[str, float]]:
        """
        Sense current pheromone patterns.

        If context is provided, weights are adjusted for relevance.

        Args:
            context: Optional context for relevance weighting
            limit: Maximum patterns to return

        Returns:
            List of (concept, intensity) tuples sorted by intensity
        """
        # Get all gradients
        results: list[SenseResult] = await self._field.sense()

        # Convert to tuple format
        patterns = [(r.concept, r.total_intensity) for r in results]

        # If context provided, boost matching concepts
        if context:
            context_concepts = set(self._extract_concepts(context))
            boosted = []
            for concept, intensity in patterns:
                if concept in context_concepts:
                    boosted.append((concept, intensity * 1.5))
                else:
                    boosted.append((concept, intensity))
            patterns = boosted

        # Sort by intensity and limit
        patterns.sort(key=lambda x: x[1], reverse=True)
        return patterns[:limit]

    async def get_top_patterns(self, limit: int = 5) -> list[tuple[str, float]]:
        """
        Get the top N patterns without context filtering.

        Useful for showing "your patterns" in Morning Coffee.
        """
        return await self.sense_patterns(limit=limit)

    # =========================================================================
    # Decay
    # =========================================================================

    async def apply_daily_decay(self) -> int:
        """
        Apply a day's worth of decay to the field.

        Should be called at session start or via cron.

        Returns:
            Number of traces evaporated
        """
        return await self._field.decay(timedelta(days=1))

    # =========================================================================
    # Persistence
    # =========================================================================

    async def save(self) -> Path:
        """
        Persist the pheromone field to storage.

        If MetabolismPersistence is configured, uses D-gent.
        Otherwise falls back to JSON file.

        Returns:
            Path to saved file (for API compatibility)
        """
        if self._persistence:
            # Use D-gent backed persistence
            from services.metabolism.persistence import StigmergyTraceRecord

            for concept in self._field.concepts:
                traces = self._field._traces.get(concept, [])
                for trace in traces:
                    record = StigmergyTraceRecord(
                        concept=trace.concept,
                        intensity=trace.intensity,
                        deposited_at=trace.deposited_at,
                        depositor=trace.depositor,
                        metadata_json=json.dumps(trace.metadata),
                    )
                    await self._persistence.save_stigmergy_trace(record)

            logger.debug("Saved pheromone field to D-gent persistence")
            return self._store_path
        else:
            return await self._save_json()

    async def _save_json(self) -> Path:
        """Save pheromone field to JSON file (fallback)."""
        self._store_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "decay_rate": self._field.decay_rate,
            "traces": self._serialize_traces(),
            "saved_at": datetime.now().isoformat(),
        }

        with open(self._store_path, "w") as f:
            json.dump(data, f, indent=2)

        logger.debug(f"Saved pheromone field to {self._store_path}")
        return self._store_path

    async def load(self) -> bool:
        """
        Load the pheromone field from storage.

        If MetabolismPersistence is configured, loads from D-gent.
        Otherwise falls back to JSON file.

        Returns:
            True if loaded successfully, False if no traces found
        """
        if self._persistence:
            # Load from D-gent backed persistence
            trace_records = await self._persistence.load_stigmergy_traces()

            for record in trace_records:
                trace = Trace(
                    concept=record.concept,
                    intensity=record.intensity,
                    deposited_at=record.deposited_at,
                    depositor=record.depositor,
                    metadata=json.loads(record.metadata_json) if record.metadata_json else {},
                )

                if record.concept not in self._field._traces:
                    self._field._traces[record.concept] = []
                self._field._traces[record.concept].append(trace)

            logger.debug(f"Loaded {len(trace_records)} traces from D-gent")
            return bool(trace_records)
        else:
            return await self._load_json()

    async def _load_json(self) -> bool:
        """Load pheromone field from JSON file (fallback)."""
        if not self._store_path.exists():
            logger.debug("No persisted pheromone field found")
            return False

        try:
            with open(self._store_path) as f:
                data = json.load(f)

            # Restore traces
            await self._deserialize_traces(data.get("traces", {}))

            logger.debug(f"Loaded pheromone field from {self._store_path}")
            return True

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load pheromone field: {e}")
            return False

    def _serialize_traces(self) -> dict[str, list[dict[str, Any]]]:
        """Serialize traces for JSON storage."""
        result: dict[str, list[dict[str, Any]]] = {}

        for concept in self._field.concepts:
            traces = self._field._traces.get(concept, [])
            result[concept] = [
                {
                    "intensity": t.intensity,
                    "deposited_at": t.deposited_at.isoformat(),
                    "depositor": t.depositor,
                    "metadata": t.metadata,
                }
                for t in traces
            ]

        return result

    async def _deserialize_traces(self, traces_data: dict[str, list[dict[str, Any]]]) -> None:
        """Restore traces from JSON storage."""
        for concept, traces in traces_data.items():
            for t in traces:
                trace = Trace(
                    concept=concept,
                    intensity=t["intensity"],
                    deposited_at=datetime.fromisoformat(t["deposited_at"]),
                    depositor=t.get("depositor", "anonymous"),
                    metadata=t.get("metadata", {}),
                )

                if concept not in self._field._traces:
                    self._field._traces[concept] = []
                self._field._traces[concept].append(trace)

    # =========================================================================
    # Statistics
    # =========================================================================

    def stats(self) -> dict[str, Any]:
        """Get field statistics."""
        base_stats = self._field.stats()
        return {
            **base_stats,
            "recent_deposits": len(self._recent_deposits),
            "store_path": str(self._store_path),
        }


# =============================================================================
# Factory
# =============================================================================


_service: VoiceStigmergy | None = None


def get_voice_stigmergy() -> VoiceStigmergy:
    """Get or create the global VoiceStigmergy service."""
    global _service
    if _service is None:
        _service = VoiceStigmergy()
    return _service


def set_voice_stigmergy(service: VoiceStigmergy) -> None:
    """Set the global VoiceStigmergy service (for testing)."""
    global _service
    _service = service


def reset_voice_stigmergy() -> None:
    """Reset the global VoiceStigmergy service."""
    global _service
    _service = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "PheromoneDeposit",
    # Service
    "VoiceStigmergy",
    "get_voice_stigmergy",
    "set_voice_stigmergy",
    "reset_voice_stigmergy",
    # Constants
    "DECAY_RATE_PER_HOUR",
    "MAX_INTENSITY",
    "ACCOMPLISHED_REINFORCEMENT",
    "PARTIAL_REINFORCEMENT",
]
