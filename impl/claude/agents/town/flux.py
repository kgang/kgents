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
from typing import TYPE_CHECKING, Any, AsyncIterator

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
from agents.town.trace_bridge import TownTrace, TownTraceEvent
from protocols.nphase.operad import NPhase

if TYPE_CHECKING:
    from agents.town.dialogue_engine import CitizenDialogueEngine
    from agents.town.event_bus import EventBus
    from agents.town.visualization import TownNATSBridge, TownSSEEndpoint
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

    Phase 7: Added dialogue fields for LLM-backed citizen speech.
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

    # Phase 7: Dialogue fields
    dialogue: str | None = None  # Generated citizen speech
    dialogue_tokens: int = 0  # LLM tokens for dialogue
    dialogue_model: str = ""  # Model used (haiku/sonnet/template)
    dialogue_was_template: bool = False  # Was template fallback used?
    dialogue_grounded: list[str] = field(default_factory=list)  # Memory refs

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        result = {
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
        # Phase 7: Include dialogue fields if present
        if self.dialogue is not None:
            result["dialogue"] = self.dialogue
            result["dialogue_tokens"] = self.dialogue_tokens
            result["dialogue_model"] = self.dialogue_model
            result["dialogue_was_template"] = self.dialogue_was_template
            result["dialogue_grounded"] = list(self.dialogue_grounded)
        return result


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
        dialogue_engine: "CitizenDialogueEngine | None" = None,
        event_bus: "EventBus[TownEvent] | None" = None,
    ) -> None:
        self.environment = environment
        self.rng = random.Random(seed)
        self.current_phase: TownPhase = TownPhase.MORNING
        self.day = 1
        self.total_events = 0
        self.total_tokens = 0
        # D-gent memory integration: pending memories to store
        self._pending_memories: list[tuple[Citizen, str, Any]] = []
        # Trace integration: append events for replay scrubber
        self.trace = TownTrace()
        # Phase 7: Optional dialogue engine for LLM-backed speech
        self._dialogue_engine = dialogue_engine
        # Phase 8: Optional event bus for fan-out to SSE/NATS/widgets
        self._event_bus = event_bus

    @property
    def citizens(self) -> list[Citizen]:
        """All citizens in the environment."""
        return list(self.environment.citizens.values())

    def set_event_bus(self, event_bus: "EventBus[TownEvent]") -> None:
        """
        Wire event bus for fan-out to subscribers.

        Call this to enable live streaming of events to
        SSE endpoints, NATS bridges, and widget updates.
        """
        self._event_bus = event_bus

    @property
    def event_bus(self) -> "EventBus[TownEvent] | None":
        """Get the wired event bus, if any."""
        return self._event_bus

    def _emit_flux_metric(
        self,
        operation: str,
        participants: list[Citizen],
        tokens_used: int,
        dialogue_tokens: int,
        model: str,
    ) -> None:
        """
        Emit action metric for flux operation (Track B).

        These are system-generated events, not user-initiated,
        so they don't charge credits but do track token consumption
        for cost analysis.
        """
        try:
            from protocols.api.action_metrics import emit_action_metric

            emit_action_metric(
                action_type=f"flux_{operation}",
                user_id="system",
                town_id=getattr(self.environment, "name", "unknown"),
                citizen_id=participants[0].id if participants else None,
                tokens_in=0,
                tokens_out=dialogue_tokens,
                model=model,
                latency_ms=0,
                credits_charged=0,
                metadata={
                    "operation": operation,
                    "phase": self.current_phase.name,
                    "participants": [c.name for c in participants],
                    "total_tokens": tokens_used,
                },
            )
        except ImportError:
            pass  # Metrics not available

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

    async def _execute_operation(
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

        # Execute the operation (Phase 7: async for dialogue)
        if operation == "greet":
            return await self._execute_greet(participants, tokens, drama)
        elif operation == "gossip":
            return await self._execute_gossip(participants, tokens, drama)
        elif operation == "trade":
            return await self._execute_trade(participants, tokens, drama)
        elif operation == "solo":
            return await self._execute_solo(participants[0], tokens, drama)
        else:
            return TownEvent(
                phase=self.current_phase,
                operation=operation,
                participants=[c.name for c in participants],
                success=False,
                message=f"Unknown operation: {operation}",
            )

    async def _execute_greet(
        self,
        participants: list[Citizen],
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a greeting with optional dialogue generation."""
        a, b = participants[:2]

        # Transition to socializing
        a.transition(CitizenInput.greet(b.id))
        b.transition(CitizenInput.greet(a.id))

        # Update relationships
        warmth_factor = (a.eigenvectors.warmth + b.eigenvectors.warmth) / 2
        a.update_relationship(b.id, 0.1 * warmth_factor)
        b.update_relationship(a.id, 0.1 * warmth_factor)

        # Phase 7: Generate dialogue if engine available
        dialogue_result = None
        if self._dialogue_engine is not None:
            dialogue_result = await self._dialogue_engine.generate(
                speaker=a,
                listener=b,
                operation="greet",
                phase=self.current_phase,
            )

        # Track B: Emit metric for town operation
        self._emit_flux_metric(
            operation="greet",
            participants=[a, b],
            tokens_used=tokens,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            model=dialogue_result.model if dialogue_result else "template",
        )

        return TownEvent(
            phase=self.current_phase,
            operation="greet",
            participants=[a.name, b.name],
            success=True,
            message=f"{a.name} greeted {b.name} at the {a.region}.",
            tokens_used=tokens,
            drama_contribution=drama,
            metadata={"region": a.region, "warmth_factor": warmth_factor},
            # Phase 7: Dialogue fields
            dialogue=dialogue_result.text if dialogue_result else None,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            dialogue_model=dialogue_result.model if dialogue_result else "",
            dialogue_was_template=dialogue_result.was_template
            if dialogue_result
            else False,
            dialogue_grounded=dialogue_result.grounded_memories
            if dialogue_result
            else [],
        )

    async def _recall_gossip_subjects(self, citizen: Citizen) -> list[str]:
        """
        Recall subjects from citizen's gossip memories.

        Returns list of subject names the citizen has gossiped about.
        """
        try:
            # Access internal storage directly (CitizenMemory has no query method)
            storage = citizen.memory._storage
            subjects = []
            for key, value in storage.items():
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

        Uses the memory storage directly for synchronous access.
        """
        try:
            storage = citizen.memory._storage
            subjects = []
            for key, value in storage.items():
                if isinstance(value, dict) and value.get("type") == "gossip":
                    subj = value.get("subject")
                    if subj:
                        subjects.append(subj)
            return subjects
        except Exception:
            return []

    async def _execute_gossip(
        self,
        participants: list[Citizen],
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a gossip exchange with memory integration and dialogue."""
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

        # Phase 7: Generate dialogue if engine available
        dialogue_result = None
        if self._dialogue_engine is not None:
            dialogue_result = await self._dialogue_engine.generate(
                speaker=a,
                listener=b,
                operation="gossip",
                phase=self.current_phase,
                recent_events=[f"talking about {subject.name}"],
            )

        # Track B: Emit metric
        self._emit_flux_metric(
            operation="gossip",
            participants=[a, b],
            tokens_used=tokens,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            model=dialogue_result.model if dialogue_result else "template",
        )

        return TownEvent(
            phase=self.current_phase,
            operation="gossip",
            participants=[a.name, b.name],
            success=True,
            message=f"{a.name} told {b.name} about {subject.name}.",
            tokens_used=tokens,
            drama_contribution=actual_drama,
            metadata={"subject": subject.name, "opinion": a_opinion},
            # Phase 7: Dialogue fields
            dialogue=dialogue_result.text if dialogue_result else None,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            dialogue_model=dialogue_result.model if dialogue_result else "",
            dialogue_was_template=dialogue_result.was_template
            if dialogue_result
            else False,
            dialogue_grounded=dialogue_result.grounded_memories
            if dialogue_result
            else [],
        )

    async def _execute_trade(
        self,
        participants: list[Citizen],
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a trade with optional dialogue generation."""
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

        # Phase 7: Generate dialogue if engine available
        dialogue_result = None
        if self._dialogue_engine is not None:
            dialogue_result = await self._dialogue_engine.generate(
                speaker=a,
                listener=b,
                operation="trade",
                phase=self.current_phase,
            )

        # Track B: Emit metric
        self._emit_flux_metric(
            operation="trade",
            participants=[a, b],
            tokens_used=tokens,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            model=dialogue_result.model if dialogue_result else "template",
        )

        return TownEvent(
            phase=self.current_phase,
            operation="trade",
            participants=[a.name, b.name],
            success=True,
            message=f"{a.name} traded with {b.name}.",
            tokens_used=tokens,
            drama_contribution=drama,
            metadata={"trust_factor": trust_factor, "surplus_generated": surplus},
            # Phase 7: Dialogue fields
            dialogue=dialogue_result.text if dialogue_result else None,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            dialogue_model=dialogue_result.model if dialogue_result else "",
            dialogue_was_template=dialogue_result.was_template
            if dialogue_result
            else False,
            dialogue_grounded=dialogue_result.grounded_memories
            if dialogue_result
            else [],
        )

    async def _execute_solo(
        self,
        citizen: Citizen,
        tokens: int,
        drama: float,
    ) -> TownEvent:
        """Execute a solo activity with optional dialogue generation."""
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

        # Phase 7: Generate solo dialogue (inner monologue) if engine available
        # Note: For solo, we use a "phantom listener" (self)
        dialogue_result = None
        if self._dialogue_engine is not None and activity == "reflecting":
            dialogue_result = await self._dialogue_engine.generate(
                speaker=citizen,
                listener=citizen,  # Self-dialogue
                operation="solo_reflect",
                phase=self.current_phase,
            )

        # Track B: Emit metric
        self._emit_flux_metric(
            operation="solo",
            participants=[citizen],
            tokens_used=tokens,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            model=dialogue_result.model if dialogue_result else "template",
        )

        return TownEvent(
            phase=self.current_phase,
            operation="solo",
            participants=[citizen.name],
            success=True,
            message=f"{citizen.name} spent time {activity}.",
            tokens_used=tokens,
            drama_contribution=drama,
            metadata={"activity": activity},
            # Phase 7: Dialogue fields
            dialogue=dialogue_result.text if dialogue_result else None,
            dialogue_tokens=dialogue_result.tokens_used if dialogue_result else 0,
            dialogue_model=dialogue_result.model if dialogue_result else "",
            dialogue_was_template=dialogue_result.was_template
            if dialogue_result
            else False,
            dialogue_grounded=dialogue_result.grounded_memories
            if dialogue_result
            else [],
        )

    async def emit_nphase_transition(
        self,
        town_id: str,
        citizen: Citizen,
        target: NPhase | str | None = None,
        *,
        nats: "TownNATSBridge" | None = None,
        sse: "TownSSEEndpoint" | None = None,
        payload: Any | None = None,
    ) -> dict[str, Any]:
        """
        Advance a citizen's compressed N-Phase state and emit events.

        Publishes to NATS (`town.{town_id}.nphase.transition`) and optionally
        to the SSE endpoint for dashboards.
        """
        ledger = citizen.advance_nphase(target, payload)
        if nats:
            await nats.publish_nphase_transition(town_id, citizen.id, ledger)
        if sse:
            await sse.push_nphase_transition(citizen.id, ledger)
        return ledger

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

            # Phase 7: async execute for dialogue generation
            event = await self._execute_operation(operation, participants)

            self.total_events += 1
            self.total_tokens += event.tokens_used
            self.environment.total_token_spend += event.tokens_used

            # Append to trace for replay scrubber
            self.trace.append(event)

            yield event

            # Phase 8: Publish to event bus for SSE/NATS/widget subscribers
            if self._event_bus is not None:
                await self._event_bus.publish(event)

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

    async def perturb(
        self,
        operation: str,
        participant_ids: list[str] | None = None,
    ) -> TownEvent | None:
        """
        Inject a perturbation event into the flux.

        Perturbation Principle (spec/principles.md §6):
        - Pads inject events, never bypass state
        - Events go through normal execution path
        - Trace captures perturbation origin

        Args:
            operation: Operation to execute ("greet", "gossip", "trade", "solo")
            participant_ids: Optional specific participants (random if None)

        Returns:
            The generated TownEvent, or None if operation couldn't execute

        Note: Phase 7 made this async to support dialogue generation.
        """
        # Validate operation
        valid_ops = {"greet", "gossip", "trade", "solo"}
        if operation not in valid_ops:
            return None

        # Select participants
        participants: list[Citizen]
        if participant_ids:
            participant_list: list[Citizen | None] = [
                self.environment.citizens.get(pid)
                for pid in participant_ids
                if pid in self.environment.citizens
            ]
            participants = [p for p in participant_list if p is not None]
        else:
            participants = self._select_participants(operation)

        if not participants:
            return None

        # Execute through normal path (perturbation principle: inject, don't bypass)
        # Phase 7: async for dialogue generation
        event = await self._execute_operation(operation, participants)

        # Track perturbation metadata
        event.metadata["perturbation"] = True
        event.metadata["perturbation_source"] = "hitl_pad"

        self.total_events += 1
        self.total_tokens += event.tokens_used
        self.environment.total_token_spend += event.tokens_used

        # Append to trace with perturbation marker
        trace_event = self.trace.append(event)
        trace_event.metadata["perturbation"] = True

        return event

    async def perturb_async(
        self,
        operation: str,
        participant_ids: list[str] | None = None,
    ) -> TownEvent | None:
        """
        Async version of perturb for API integration.

        Same as perturb() but awaitable for use in FastAPI endpoints.
        Kept for backward compatibility—perturb() is now async.
        """
        return await self.perturb(operation, participant_ids)


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "TownPhase",
    "TownEvent",
    "TownFlux",
    "TownTrace",
    "TownTraceEvent",
]
