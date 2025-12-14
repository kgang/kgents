"""
TownFlux: The Simulation Loop as Event Stream.

From Bataille: The flux is not just time—it is *expenditure*.
Each phase accumulates surplus that must be spent.
If not spent gloriously, it will be spent catastrophically.

The Flux provides:
- Phase advancement (morning → evening → ...)
- Event generation
- Precondition enforcement
- Metrics tracking

See: spec/town/operad.md
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, AsyncIterator

from agents.town.citizen import Citizen
from agents.town.environment import TownEnvironment
from agents.town.operad import (
    GOSSIP_METABOLICS,
    GREET_METABOLICS,
    PRECONDITION_CHECKER,
    SOLO_METABOLICS,
    TOWN_OPERAD,
    TRADE_METABOLICS,
)
from agents.town.polynomial import CitizenInput, CitizenPhase

# =============================================================================
# Town Phase (Time Slices)
# =============================================================================


class TownPhase(Enum):
    """
    Phases in the daily cycle.

    Phase 2 has 4 phases: MORNING, AFTERNOON, EVENING, NIGHT.
    Each phase has different activity weights and token costs.
    """

    MORNING = auto()
    AFTERNOON = auto()
    EVENING = auto()
    NIGHT = auto()


# =============================================================================
# Town Event
# =============================================================================


@dataclass
class TownEvent:
    """
    An event in the town simulation.

    Events are the outputs of the flux stream.
    They can be observed, piped, and recorded.
    """

    phase: TownPhase
    operation: str
    participants: list[str]  # Citizen names
    success: bool
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    drama_contribution: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "phase": self.phase.name,
            "operation": self.operation,
            "participants": list(self.participants),
            "success": self.success,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "tokens_used": self.tokens_used,
            "drama_contribution": self.drama_contribution,
            "metadata": dict(self.metadata),
        }


# =============================================================================
# TownFlux
# =============================================================================


class TownFlux:
    """
    Town simulation as Flux stream.

    Emits TownEvents that can be observed, piped, and recorded.

    From Bataille: The flux is expenditure.
    Surplus accumulates and must be spent.
    """

    def __init__(
        self,
        environment: TownEnvironment,
        seed: int | None = None,
    ) -> None:
        self.environment = environment
        self.rng = random.Random(seed)
        self.current_phase: TownPhase = TownPhase.MORNING
        self.day = 1
        self.total_events = 0
        self.total_tokens = 0
        # D-gent memory integration: pending memories to store
        self._pending_memories: list[tuple[Citizen, str, Any]] = []

    @property
    def citizens(self) -> list[Citizen]:
        """All citizens in the environment."""
        return list(self.environment.citizens.values())

    def _next_phase(self) -> TownPhase:
        """Advance to the next phase."""
        match self.current_phase:
            case TownPhase.MORNING:
                self.current_phase = TownPhase.AFTERNOON
            case TownPhase.AFTERNOON:
                self.current_phase = TownPhase.EVENING
            case TownPhase.EVENING:
                self.current_phase = TownPhase.NIGHT
            case TownPhase.NIGHT:
                self.current_phase = TownPhase.MORNING
                self.day += 1
        return self.current_phase

    def _select_operation(self) -> str:
        """Select an operation based on phase and probabilities."""
        ops = list(TOWN_OPERAD.operations.keys())
        # Filter to town-specific ops
        town_ops = ["greet", "gossip", "trade", "solo"]
        ops = [op for op in ops if op in town_ops]

        # Weight by phase (Phase 2: 4-phase cycle)
        match self.current_phase:
            case TownPhase.MORNING:
                # Morning: more work, less socializing
                weights = {"greet": 0.2, "gossip": 0.1, "trade": 0.3, "solo": 0.4}
            case TownPhase.AFTERNOON:
                # Afternoon: peak activity, balanced
                weights = {"greet": 0.25, "gossip": 0.2, "trade": 0.35, "solo": 0.2}
            case TownPhase.EVENING:
                # Evening: more socializing
                weights = {"greet": 0.3, "gossip": 0.3, "trade": 0.2, "solo": 0.2}
            case TownPhase.NIGHT:
                # Night: consolidation, reflection, less activity
                weights = {"greet": 0.1, "gossip": 0.2, "trade": 0.1, "solo": 0.6}

        return self.rng.choices(
            list(weights.keys()), weights=list(weights.values()), k=1
        )[0]

    def _select_participants(self, operation: str) -> list[Citizen]:
        """Select participants for an operation."""
        available = self.environment.available_citizens()
        if not available:
            return []

        if operation == "solo":
            return [self.rng.choice(available)]
        else:
            # Binary operation—need 2 co-located citizens
            # Group by region
            by_region: dict[str, list[Citizen]] = {}
            for c in available:
                by_region.setdefault(c.region, []).append(c)

            # Find a region with at least 2 citizens
            candidates = [cs for cs in by_region.values() if len(cs) >= 2]
            if not candidates:
                # No co-located pairs—fall back to solo
                return [self.rng.choice(available)]

            region_citizens = self.rng.choice(candidates)
            return self.rng.sample(region_citizens, 2)

    def _execute_operation(
        self,
        operation: str,
        participants: list[Citizen],
    ) -> TownEvent:
        """Execute an operation and return the event."""
        # Handle fallback: if binary operation but only 1 participant, do solo
        if operation in ("greet", "gossip", "trade") and len(participants) == 1:
            operation = "solo"

        # Check preconditions
        preconditions = PRECONDITION_CHECKER.validate_operation(
            operation, participants, self.environment
        )
        for result in preconditions:
            if not result.passed:
                return TownEvent(
                    phase=self.current_phase,
                    operation=operation,
                    participants=[c.name for c in participants],
                    success=False,
                    message=f"Precondition failed: {result.message}",
                )

        # Get metabolics
        metabolics_map = {
            "greet": GREET_METABOLICS,
            "gossip": GOSSIP_METABOLICS,
            "trade": TRADE_METABOLICS,
            "solo": SOLO_METABOLICS,
        }
        metabolics = metabolics_map.get(operation)
        tokens = metabolics.token_cost if metabolics else 100
        drama = metabolics.drama_potential if metabolics else 0.1

        # Execute the operation
        if operation == "greet":
            return self._execute_greet(participants, tokens, drama)
        elif operation == "gossip":
            return self._execute_gossip(participants, tokens, drama)
        elif operation == "trade":
            return self._execute_trade(participants, tokens, drama)
        elif operation == "solo":
            return self._execute_solo(participants[0], tokens, drama)
        else:
            return TownEvent(
                phase=self.current_phase,
                operation=operation,
                participants=[c.name for c in participants],
                success=False,
                message=f"Unknown operation: {operation}",
            )

    def _execute_greet(
        self,
        participants: list[Citizen],
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a greeting."""
        a, b = participants[:2]

        # Transition to socializing
        a.transition(CitizenInput.greet(b.id))
        b.transition(CitizenInput.greet(a.id))

        # Update relationships
        warmth_factor = (a.eigenvectors.warmth + b.eigenvectors.warmth) / 2
        a.update_relationship(b.id, 0.1 * warmth_factor)
        b.update_relationship(a.id, 0.1 * warmth_factor)

        return TownEvent(
            phase=self.current_phase,
            operation="greet",
            participants=[a.name, b.name],
            success=True,
            message=f"{a.name} greeted {b.name} at the {a.region}.",
            tokens_used=tokens,
            drama_contribution=drama,
            metadata={"region": a.region, "warmth_factor": warmth_factor},
        )

    async def _recall_gossip_subjects(self, citizen: Citizen) -> list[str]:
        """
        Recall subjects from citizen's gossip memories.

        Returns list of subject names the citizen has gossiped about.
        """
        try:
            response = await citizen.memory.query(limit=20)
            subjects = []
            if response.state and isinstance(response.state, dict):
                for key, value in response.state.items():
                    if isinstance(value, dict) and value.get("type") == "gossip":
                        subj = value.get("subject")
                        if subj:
                            subjects.append(subj)
            return subjects
        except Exception:
            return []

    def _get_remembered_subjects(self, citizen: Citizen) -> list[str]:
        """
        Synchronous access to remembered gossip subjects.

        Uses the memory store directly for synchronous access.
        """
        try:
            store = citizen.memory._store
            subjects = []
            for key, value in store.state.items():
                if isinstance(value, dict) and value.get("type") == "gossip":
                    subj = value.get("subject")
                    if subj:
                        subjects.append(subj)
            return subjects
        except Exception:
            return []

    def _execute_gossip(
        self,
        participants: list[Citizen],
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a gossip exchange with memory integration."""
        a, b = participants[:2]

        # Need a third party to gossip about
        others = [c for c in self.citizens if c.id not in (a.id, b.id)]
        if not others:
            return TownEvent(
                phase=self.current_phase,
                operation="gossip",
                participants=[a.name, b.name],
                success=False,
                message="No one to gossip about.",
            )

        # Prefer subjects with existing memories (30% chance to use memory)
        subject = self.rng.choice(others)
        if self.rng.random() < 0.3:
            # Try to find a subject from memory
            remembered = self._get_remembered_subjects(a)
            if remembered:
                # Find citizens matching remembered names
                for c in others:
                    if c.name in remembered:
                        subject = c
                        break

        # Transition to socializing
        a.transition(CitizenInput.greet(b.id))  # Socializing
        b.transition(CitizenInput.greet(a.id))

        # Transfer knowledge (simplified)
        a_opinion = a.get_relationship(subject.id)
        b.update_relationship(subject.id, a_opinion * 0.5)  # Telephone game

        # Gossip increases drama
        actual_drama = drama * 1.5 if a_opinion < 0 else drama

        # Store gossip event in memory (D-gent integration)
        gossip_memory = {
            "type": "gossip",
            "speaker": a.name,
            "listener": b.name,
            "subject": subject.name,
            "opinion": a_opinion,
            "phase": self.current_phase.name,
            "day": self.day,
        }
        # Queue memory storage (handled async in step())
        self._pending_memories.append((a, f"gossip_{self.day}_{a.id}", gossip_memory))
        self._pending_memories.append((b, f"heard_{self.day}_{b.id}", gossip_memory))

        return TownEvent(
            phase=self.current_phase,
            operation="gossip",
            participants=[a.name, b.name],
            success=True,
            message=f"{a.name} told {b.name} about {subject.name}.",
            tokens_used=tokens,
            drama_contribution=actual_drama,
            metadata={"subject": subject.name, "opinion": a_opinion},
        )

    def _execute_trade(
        self,
        participants: list[Citizen],
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a trade."""
        a, b = participants[:2]

        # Transition to socializing
        a.transition(CitizenInput.greet(b.id))
        b.transition(CitizenInput.greet(a.id))

        # Trade creates mutual benefit (simplified)
        trust_factor = (a.eigenvectors.trust + b.eigenvectors.trust) / 2
        a.update_relationship(b.id, 0.2 * trust_factor)
        b.update_relationship(a.id, 0.2 * trust_factor)

        # Accumulate surplus (from Bataille)
        surplus = 0.1 * tokens
        a.accumulate_surplus(surplus / 2)
        b.accumulate_surplus(surplus / 2)

        return TownEvent(
            phase=self.current_phase,
            operation="trade",
            participants=[a.name, b.name],
            success=True,
            message=f"{a.name} traded with {b.name}.",
            tokens_used=tokens,
            drama_contribution=drama,
            metadata={"trust_factor": trust_factor, "surplus_generated": surplus},
        )

    def _execute_solo(
        self,
        citizen: Citizen,
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a solo activity."""
        activities = ["working", "reflecting", "creating"]
        activity = self.rng.choice(activities)

        if activity == "working":
            citizen.transition(CitizenInput.work(activity))
        elif activity == "reflecting":
            citizen.transition(CitizenInput.reflect())
        else:
            citizen.transition(CitizenInput.work(activity))

        # Solo activities build surplus
        citizen.accumulate_surplus(0.05 * tokens)

        return TownEvent(
            phase=self.current_phase,
            operation="solo",
            participants=[citizen.name],
            success=True,
            message=f"{citizen.name} spent time {activity}.",
            tokens_used=tokens,
            drama_contribution=drama,
            metadata={"activity": activity},
        )

    async def step(self) -> AsyncIterator[TownEvent]:
        """
        Execute one phase step and yield events.

        This is the main simulation loop entry point.
        Phase 2: 4-phase cycle with different activity levels.
        """
        # Wake all resting citizens at start of morning
        if self.current_phase == TownPhase.MORNING:
            for citizen in self.environment.resting_citizens():
                citizen.wake()

        # Generate events for this phase (varies by phase)
        num_events = self._events_for_phase()

        for _ in range(num_events):
            operation = self._select_operation()
            participants = self._select_participants(operation)

            if not participants:
                continue

            event = self._execute_operation(operation, participants)

            self.total_events += 1
            self.total_tokens += event.tokens_used
            self.environment.total_token_spend += event.tokens_used

            yield event

        # Phase-specific end-of-phase actions
        match self.current_phase:
            case TownPhase.EVENING:
                # Some citizens begin to rest
                for citizen in self.environment.available_citizens():
                    if self.rng.random() < 0.3:
                        citizen.rest()
            case TownPhase.NIGHT:
                # Most citizens rest during night
                for citizen in self.environment.available_citizens():
                    if self.rng.random() < 0.7:
                        citizen.rest()

        # Process pending memories (D-gent integration)
        await self._process_pending_memories()

        # Advance phase
        self._next_phase()

        # Check accursed share (from Bataille)
        await self._check_accursed_share()

    def _events_for_phase(self) -> int:
        """Get number of events for current phase."""
        match self.current_phase:
            case TownPhase.MORNING:
                return self.rng.randint(2, 4)
            case TownPhase.AFTERNOON:
                return self.rng.randint(3, 5)  # Peak activity
            case TownPhase.EVENING:
                return self.rng.randint(2, 4)
            case TownPhase.NIGHT:
                return self.rng.randint(1, 2)  # Reduced activity

    async def _process_pending_memories(self) -> None:
        """
        Process pending memory storage (D-gent integration).

        Stores gossip and other events in citizen memories.
        """
        for citizen, key, content in self._pending_memories:
            await citizen.remember(content, key=key)
        self._pending_memories.clear()

    async def _check_accursed_share(self) -> None:
        """
        Check if accumulated surplus needs to be spent.

        From Bataille: The surplus is accursed—it demands expenditure.
        """
        total_surplus = self.environment.total_accursed_surplus()
        threshold = 10.0  # Arbitrary threshold for MPP

        if total_surplus > threshold:
            # Spend surplus gloriously (simplified: just reduce it)
            for citizen in self.citizens:
                citizen.spend_surplus(citizen.accursed_surplus * 0.5)

    def get_status(self) -> dict[str, Any]:
        """Get current simulation status."""
        return {
            "day": self.day,
            "phase": self.current_phase.name,
            "total_events": self.total_events,
            "total_tokens": self.total_tokens,
            "tension_index": self.environment.tension_index(),
            "cooperation_level": self.environment.cooperation_level(),
            "accursed_surplus": self.environment.total_accursed_surplus(),
            "citizens": {
                c.name: {
                    "region": c.region,
                    "phase": c.phase.name,
                }
                for c in self.citizens
            },
        }


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "TownPhase",
    "TownEvent",
    "TownFlux",
]
