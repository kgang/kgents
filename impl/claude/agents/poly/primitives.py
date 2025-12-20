"""
Polynomial Primitives: The 17 Atomic Agents.

These are the building blocks from which all other agents are composed.
Each primitive is a polynomial agent with well-defined states and transitions.

Categories:
- Bootstrap (7): Core compositional primitives
- Perception (3): Observer-interaction primitives
- Entropy (3): Accursed Share / void.* primitives
- Memory (2): D-gent persistence primitives
- Teleological (2): E-gent evolution + N-gent narrative primitives

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, FrozenSet

from .protocol import PolyAgent, from_function

# =============================================================================
# Type Definitions
# =============================================================================


class GroundState(Enum):
    """States for the Ground primitive."""

    GROUNDED = auto()
    FLOATING = auto()


class JudgeState(Enum):
    """States for the Judge primitive."""

    DELIBERATING = auto()
    DECIDED = auto()


class ContradictState(Enum):
    """States for the Contradict primitive."""

    SEEKING = auto()
    FOUND = auto()


class SublateState(Enum):
    """States for the Sublate primitive."""

    ANALYZING = auto()
    SYNTHESIZED = auto()


class FixState(Enum):
    """States for the Fix primitive."""

    TRYING = auto()
    SUCCEEDED = auto()
    FAILED = auto()


class WitnessState(Enum):
    """States for the Witness primitive."""

    RECORDING = auto()
    REPLAYING = auto()


class SipState(Enum):
    """States for the Sip primitive."""

    THIRSTY = auto()
    SATED = auto()


class TitheState(Enum):
    """States for the Tithe primitive."""

    OWING = auto()
    PAID = auto()


@dataclass(frozen=True)
class Claim:
    """A claim to be judged."""

    content: str
    confidence: float = 0.5


@dataclass(frozen=True)
class Verdict:
    """Result of judgment."""

    claim: Claim
    accepted: bool
    reasoning: str


@dataclass(frozen=True)
class Thesis:
    """A position to be contradicted."""

    content: str


@dataclass(frozen=True)
class Antithesis:
    """The contradiction of a thesis."""

    thesis: Thesis
    contradiction: str


@dataclass(frozen=True)
class Synthesis:
    """The resolution of thesis and antithesis."""

    thesis: Thesis
    antithesis: Antithesis
    resolution: str


@dataclass(frozen=True)
class Handle:
    """A handle to an entity for observation."""

    path: str
    entity: Any = None


@dataclass(frozen=True)
class Umwelt:
    """Observer context for perception."""

    observer_type: str
    capabilities: FrozenSet[str] = frozenset()


@dataclass(frozen=True)
class Manifestation:
    """Result of manifesting a handle."""

    handle: Handle
    umwelt: Umwelt
    perception: Any


@dataclass(frozen=True)
class Trace:
    """A recorded trace of events."""

    events: tuple[Any, ...]
    timestamp: float = 0.0


@dataclass(frozen=True)
class EntropyRequest:
    """Request for entropy from the void."""

    amount: float = 0.5


@dataclass(frozen=True)
class EntropyGrant:
    """Entropy granted from the void."""

    value: float
    source: str = "void.entropy"


@dataclass(frozen=True)
class Offering:
    """An offering to the void (gratitude tithe)."""

    content: Any
    gratitude_level: float = 0.5


@dataclass(frozen=True)
class Spec:
    """Specification for autopoietic creation."""

    name: str
    signature: str
    behavior: str


@dataclass(frozen=True)
class Definition:
    """Result of autopoietic definition."""

    spec: Spec
    created: bool
    message: str


# =============================================================================
# Memory Primitives Types (D-gent)
# =============================================================================


class RememberState(Enum):
    """States for the Remember primitive."""

    IDLE = auto()
    STORING = auto()
    STORED = auto()


class ForgetState(Enum):
    """States for the Forget primitive."""

    IDLE = auto()
    FORGETTING = auto()
    FORGOTTEN = auto()


@dataclass(frozen=True)
class Memory:
    """A memory to store or recall."""

    key: str
    content: Any
    timestamp: float = 0.0


@dataclass(frozen=True)
class MemoryResult:
    """Result of a memory operation."""

    key: str
    success: bool
    message: str
    content: Any = None


# =============================================================================
# Teleological Primitives Types (Evolve, Narrate)
# Note: Evolve was originally part of E-gent (archived 2025-12-16)
# These are now standalone generic primitives
# =============================================================================


class EvolveState(Enum):
    """States for the Evolve primitive."""

    DORMANT = auto()
    MUTATING = auto()
    SELECTING = auto()
    CONVERGED = auto()


class NarrateState(Enum):
    """States for the Narrate primitive."""

    LISTENING = auto()
    COMPOSING = auto()
    TOLD = auto()


@dataclass(frozen=True)
class Organism:
    """An entity subject to evolution."""

    genome: tuple[Any, ...]
    fitness: float = 0.0
    generation: int = 0


@dataclass(frozen=True)
class Evolution:
    """Result of evolutionary step."""

    organism: Organism
    mutation_applied: bool
    selected: bool
    message: str


@dataclass(frozen=True)
class Story:
    """A narrative constructed from events."""

    title: str
    events: tuple[Any, ...]
    moral: str
    narrator: str = "witness"


# =============================================================================
# Bootstrap Primitives (7)
# =============================================================================


# 1. Id: Identity primitive
ID = PolyAgent[str, Any, Any](
    name="Id",
    positions=frozenset({"ready"}),
    _directions=lambda s: frozenset({Any}),
    _transition=lambda s, x: ("ready", x),
)


# 2. Ground: Grounding primitive (queries → grounded facts)
def _ground_transition(state: GroundState, input: Any) -> tuple[GroundState, Any]:
    """Ground an input to factual basis."""
    # In real implementation, this would call grounding logic
    if isinstance(input, str) and input.strip():
        return GroundState.GROUNDED, {"grounded": True, "content": input}
    return GroundState.FLOATING, {"grounded": False, "content": input}


GROUND = PolyAgent[GroundState, Any, dict[str, Any]](
    name="Ground",
    positions=frozenset({GroundState.GROUNDED, GroundState.FLOATING}),
    _directions=lambda s: frozenset({Any}),
    _transition=_ground_transition,
)


# 3. Judge: Judgment primitive (claims → verdicts)
def _judge_transition(state: JudgeState, input: Claim) -> tuple[JudgeState, Verdict]:
    """Judge a claim."""
    if isinstance(input, Claim):
        accepted = input.confidence > 0.5
        return (
            JudgeState.DECIDED,
            Verdict(
                claim=input,
                accepted=accepted,
                reasoning=f"Confidence {'exceeds' if accepted else 'below'} threshold",
            ),
        )
    # Default to rejection for non-claims
    default_claim = Claim(content=str(input))
    return (
        JudgeState.DECIDED,
        Verdict(claim=default_claim, accepted=False, reasoning="Not a valid claim"),
    )


JUDGE = PolyAgent[JudgeState, Claim, Verdict](
    name="Judge",
    positions=frozenset({JudgeState.DELIBERATING, JudgeState.DECIDED}),
    _directions=lambda s: frozenset({Claim, Any})  # type: ignore[arg-type]
    if s == JudgeState.DELIBERATING
    else frozenset(),
    _transition=_judge_transition,
)


# 4. Contradict: Contradiction primitive (thesis → antithesis)
def _contradict_transition(
    state: ContradictState, input: Thesis
) -> tuple[ContradictState, Antithesis]:
    """Generate antithesis for a thesis."""
    if isinstance(input, Thesis):
        return (
            ContradictState.FOUND,
            Antithesis(thesis=input, contradiction=f"Contrary to: {input.content}"),
        )
    default_thesis = Thesis(content=str(input))
    return (
        ContradictState.FOUND,
        Antithesis(thesis=default_thesis, contradiction=f"Contrary to: {input}"),
    )


CONTRADICT = PolyAgent[ContradictState, Thesis, Antithesis](
    name="Contradict",
    positions=frozenset({ContradictState.SEEKING, ContradictState.FOUND}),
    _directions=lambda s: frozenset({Thesis, Any}),  # type: ignore[arg-type]
    _transition=_contradict_transition,
)


# 5. Sublate: Synthesis primitive ((thesis, antithesis) → synthesis)
def _sublate_transition(
    state: SublateState, input: tuple[Thesis, Antithesis]
) -> tuple[SublateState, Synthesis]:
    """Synthesize thesis and antithesis."""
    if isinstance(input, tuple) and len(input) == 2:
        thesis, antithesis = input
        if isinstance(thesis, Thesis) and isinstance(antithesis, Antithesis):
            return (
                SublateState.SYNTHESIZED,
                Synthesis(
                    thesis=thesis,
                    antithesis=antithesis,
                    resolution=f"Aufhebung of {thesis.content}",
                ),
            )
    # Default synthesis
    return (
        SublateState.SYNTHESIZED,
        Synthesis(
            thesis=Thesis(content=str(input)),
            antithesis=Antithesis(thesis=Thesis(content=str(input)), contradiction="default"),
            resolution="default synthesis",
        ),
    )


SUBLATE = PolyAgent[SublateState, tuple[Thesis, Antithesis], Synthesis](
    name="Sublate",
    positions=frozenset({SublateState.ANALYZING, SublateState.SYNTHESIZED}),
    _directions=lambda s: frozenset({tuple, Any}),  # type: ignore[arg-type]
    _transition=_sublate_transition,
)


# 6. Compose: Meta-composition primitive
COMPOSE: PolyAgent[str, Any, Any] = from_function(
    name="Compose",
    fn=lambda pair: (
        pair[0],
        pair[1],
    ),  # Identity on pairs; actual composition in operad
)


# 7. Fix: Fixed-point / retry primitive
def _fix_directions(state: FixState) -> FrozenSet[Any]:
    """Valid inputs for Fix based on state."""
    match state:
        case FixState.TRYING:
            return frozenset({Any})
        case FixState.SUCCEEDED | FixState.FAILED:
            return frozenset()  # No more inputs accepted


def _fix_transition(state: FixState, input: tuple[Any, int]) -> tuple[FixState, Any]:
    """
    Fixed-point transition.

    Input is (value, retry_count).
    Transitions to SUCCEEDED if retry_count > 3, else stays TRYING.
    """
    value, retries = input if isinstance(input, tuple) else (input, 0)
    if retries >= 3:
        return FixState.FAILED, {"failed": True, "value": value, "retries": retries}
    # Simulate "trying" - in real implementation, this would invoke inner agent
    if value is not None:
        return FixState.SUCCEEDED, {"succeeded": True, "value": value}
    return FixState.TRYING, {"trying": True, "retries": retries + 1}


FIX = PolyAgent[FixState, tuple[Any, int], dict[str, Any]](
    name="Fix",
    positions=frozenset({FixState.TRYING, FixState.SUCCEEDED, FixState.FAILED}),
    _directions=_fix_directions,
    _transition=_fix_transition,
)


# =============================================================================
# Perception Primitives (3)
# =============================================================================


# 8. Manifest: Observer-dependent perception
def _manifest_transition(state: str, input: tuple[Handle, Umwelt]) -> tuple[str, Manifestation]:
    """Manifest a handle according to observer umwelt."""
    if isinstance(input, tuple) and len(input) == 2:
        handle, umwelt = input
        if isinstance(handle, Handle) and isinstance(umwelt, Umwelt):
            # Observer-dependent perception
            perception = f"[{umwelt.observer_type}] sees {handle.path}"
            return (
                "observing",
                Manifestation(handle=handle, umwelt=umwelt, perception=perception),
            )
    # Default manifestation
    default_handle = Handle(path=str(input))
    default_umwelt = Umwelt(observer_type="default")
    return (
        "observing",
        Manifestation(
            handle=default_handle,
            umwelt=default_umwelt,
            perception=str(input),
        ),
    )


MANIFEST = PolyAgent[str, tuple[Handle, Umwelt], Manifestation](
    name="Manifest",
    positions=frozenset({"observing"}),
    _directions=lambda s: frozenset({tuple, Any}),  # type: ignore[arg-type]
    _transition=_manifest_transition,
)


# 9. Witness: Trace recording and replay
def _witness_directions(state: WitnessState) -> FrozenSet[Any]:
    """Valid inputs for Witness based on state."""
    match state:
        case WitnessState.RECORDING:
            return frozenset({Any})
        case WitnessState.REPLAYING:
            return frozenset({"replay", Any})


def _witness_transition(state: WitnessState, input: Any) -> tuple[WitnessState, Trace | Any]:
    """Record or replay traces."""
    if input == "replay":
        return WitnessState.REPLAYING, Trace(events=(), timestamp=0.0)
    # Recording mode
    import time

    return WitnessState.RECORDING, Trace(events=(input,), timestamp=time.time())


WITNESS = PolyAgent[WitnessState, Any, Trace | Any](
    name="Witness",
    positions=frozenset({WitnessState.RECORDING, WitnessState.REPLAYING}),
    _directions=_witness_directions,
    _transition=_witness_transition,
)


# 10. Lens: Composable sub-agent extraction
LENS: PolyAgent[str, Any, Any] = from_function(
    name="Lens",
    fn=lambda selector: selector,  # In real impl, extracts sub-agent
)


# =============================================================================
# Entropy Primitives (3)
# =============================================================================


# 11. Sip: Draw from the Accursed Share
def _sip_transition(state: SipState, input: EntropyRequest) -> tuple[SipState, EntropyGrant]:
    """Draw entropy from the void."""
    import random

    if isinstance(input, EntropyRequest):
        amount = input.amount
    else:
        amount = 0.5

    return (
        SipState.SATED,
        EntropyGrant(value=random.random() * amount, source="void.entropy.sip"),
    )


SIP = PolyAgent[SipState, EntropyRequest, EntropyGrant](
    name="Sip",
    positions=frozenset({SipState.THIRSTY, SipState.SATED}),
    _directions=lambda s: frozenset({EntropyRequest, Any})  # type: ignore[arg-type]
    if s == SipState.THIRSTY
    else frozenset(),
    _transition=_sip_transition,
)


# 12. Tithe: Pay gratitude to the void
def _tithe_transition(state: TitheState, input: Offering) -> tuple[TitheState, dict[str, Any]]:
    """Tithe gratitude to the void."""
    if isinstance(input, Offering):
        return (
            TitheState.PAID,
            {
                "tithed": True,
                "offering": str(input.content),
                "gratitude": input.gratitude_level,
            },
        )
    return (
        TitheState.PAID,
        {"tithed": True, "offering": str(input), "gratitude": 0.5},
    )


TITHE = PolyAgent[TitheState, Offering, dict[str, Any]](
    name="Tithe",
    positions=frozenset({TitheState.OWING, TitheState.PAID}),
    _directions=lambda s: frozenset({Offering, Any})  # type: ignore[arg-type]
    if s == TitheState.OWING
    else frozenset(),
    _transition=_tithe_transition,
)


# 13. Define: Autopoietic creation
def _define_transition(state: str, input: Spec) -> tuple[str, Definition]:
    """Autopoietically define a new agent."""
    if isinstance(input, Spec):
        return (
            "creating",
            Definition(spec=input, created=True, message=f"Defined: {input.name}"),
        )
    # Default definition
    default_spec = Spec(name=str(input), signature="Any -> Any", behavior="identity")
    return (
        "creating",
        Definition(spec=default_spec, created=False, message="Invalid spec"),
    )


DEFINE = PolyAgent[str, Spec, Definition](
    name="Define",
    positions=frozenset({"creating"}),
    _directions=lambda s: frozenset({Spec, Any}),  # type: ignore[arg-type]
    _transition=_define_transition,
)


# =============================================================================
# Memory Primitives (2) - D-gent
# =============================================================================


# 14. Remember: Persist to memory
def _remember_transition(state: RememberState, input: Memory) -> tuple[RememberState, MemoryResult]:
    """Store a memory."""
    import time

    if isinstance(input, Memory):
        # timestamp preserved in Memory object, validation only
        _ = input.timestamp if input.timestamp > 0 else time.time()
        return (
            RememberState.STORED,
            MemoryResult(
                key=input.key,
                success=True,
                message=f"Remembered: {input.key}",
                content=input.content,
            ),
        )
    # Default: treat input as content with auto-generated key
    key = f"memory_{time.time()}"
    return (
        RememberState.STORED,
        MemoryResult(
            key=key,
            success=True,
            message=f"Remembered: {key}",
            content=input,
        ),
    )


REMEMBER = PolyAgent[RememberState, Memory, MemoryResult](
    name="Remember",
    positions=frozenset({RememberState.IDLE, RememberState.STORING, RememberState.STORED}),
    _directions=lambda s: frozenset({Memory, Any})  # type: ignore[arg-type]
    if s in (RememberState.IDLE, RememberState.STORING)
    else frozenset(),
    _transition=_remember_transition,
)


# 15. Forget: Remove from memory
def _forget_transition(state: ForgetState, input: str) -> tuple[ForgetState, MemoryResult]:
    """Forget a memory by key."""
    if isinstance(input, str):
        return (
            ForgetState.FORGOTTEN,
            MemoryResult(
                key=input,
                success=True,
                message=f"Forgotten: {input}",
                content=None,
            ),
        )
    # Default: stringify input as key
    key = str(input)
    return (
        ForgetState.FORGOTTEN,
        MemoryResult(
            key=key,
            success=True,
            message=f"Forgotten: {key}",
            content=None,
        ),
    )


FORGET = PolyAgent[ForgetState, str, MemoryResult](
    name="Forget",
    positions=frozenset({ForgetState.IDLE, ForgetState.FORGETTING, ForgetState.FORGOTTEN}),
    _directions=lambda s: frozenset({str, Any})  # type: ignore[arg-type]
    if s in (ForgetState.IDLE, ForgetState.FORGETTING)
    else frozenset(),
    _transition=_forget_transition,
)


# =============================================================================
# Teleological Primitives (2) - Evolve, Narrate
# =============================================================================


# 16. Evolve: Teleological evolution step
def _evolve_transition(state: EvolveState, input: Organism) -> tuple[EvolveState, Evolution]:
    """Evolve an organism through mutation and selection."""
    import random

    if isinstance(input, Organism):
        # Mutation: randomly perturb genome
        mutated_genome = tuple(
            g + random.gauss(0, 0.1) if isinstance(g, (int, float)) else g for g in input.genome
        )
        mutation_applied = mutated_genome != input.genome

        # Selection: higher fitness survives
        selected = input.fitness > 0.5

        # New fitness based on mutation
        new_fitness = input.fitness + random.gauss(0, 0.1)
        new_fitness = max(0, min(1, new_fitness))  # Clamp to [0, 1]

        new_organism = Organism(
            genome=mutated_genome,
            fitness=new_fitness,
            generation=input.generation + 1,
        )

        new_state = EvolveState.CONVERGED if new_fitness > 0.9 else EvolveState.SELECTING

        return (
            new_state,
            Evolution(
                organism=new_organism,
                mutation_applied=mutation_applied,
                selected=selected,
                message=f"Gen {new_organism.generation}: fitness={new_fitness:.3f}",
            ),
        )

    # Default: create organism from input
    default_organism = Organism(genome=(input,), fitness=0.5, generation=0)
    return (
        EvolveState.MUTATING,
        Evolution(
            organism=default_organism,
            mutation_applied=False,
            selected=False,
            message="Initialized organism",
        ),
    )


EVOLVE = PolyAgent[EvolveState, Organism, Evolution](
    name="Evolve",
    positions=frozenset(
        {
            EvolveState.DORMANT,
            EvolveState.MUTATING,
            EvolveState.SELECTING,
            EvolveState.CONVERGED,
        }
    ),
    _directions=lambda s: frozenset({Organism, Any})  # type: ignore[arg-type]
    if s != EvolveState.CONVERGED
    else frozenset(),
    _transition=_evolve_transition,
)


# 17. Narrate: Construct story from events (N-gent witness)
def _narrate_transition(state: NarrateState, input: tuple[Any, ...]) -> tuple[NarrateState, Story]:
    """Narrate a story from witnessed events."""
    if isinstance(input, tuple) and len(input) > 0:
        # Extract narrative structure
        events = input
        n_events = len(events)

        # Auto-generate title and moral based on events
        first_event = str(events[0])[:20]
        last_event = str(events[-1])[:20]

        title = f"The tale of {n_events} moments"
        moral = f"From '{first_event}...' to '{last_event}...'"

        return (
            NarrateState.TOLD,
            Story(
                title=title,
                events=events,
                moral=moral,
                narrator="witness",
            ),
        )

    # Default: single-event story
    return (
        NarrateState.TOLD,
        Story(
            title="A moment witnessed",
            events=(input,),
            moral="Every moment tells a story.",
            narrator="witness",
        ),
    )


NARRATE = PolyAgent[NarrateState, tuple[Any, ...], Story](
    name="Narrate",
    positions=frozenset({NarrateState.LISTENING, NarrateState.COMPOSING, NarrateState.TOLD}),
    _directions=lambda s: frozenset({tuple, Any})  # type: ignore[arg-type]
    if s in (NarrateState.LISTENING, NarrateState.COMPOSING)
    else frozenset(),
    _transition=_narrate_transition,
)


# =============================================================================
# Primitive Registry
# =============================================================================


PRIMITIVES: dict[str, PolyAgent[Any, Any, Any]] = {
    # Bootstrap (7)
    "id": ID,
    "ground": GROUND,
    "judge": JUDGE,
    "contradict": CONTRADICT,
    "sublate": SUBLATE,
    "compose": COMPOSE,
    "fix": FIX,
    # Perception (3)
    "manifest": MANIFEST,
    "witness": WITNESS,
    "lens": LENS,
    # Entropy (3)
    "sip": SIP,
    "tithe": TITHE,
    "define": DEFINE,
    # Memory (2) - D-gent
    "remember": REMEMBER,
    "forget": FORGET,
    # Teleological (2) - Evolve, Narrate
    "evolve": EVOLVE,
    "narrate": NARRATE,
}


def get_primitive(name: str) -> PolyAgent[Any, Any, Any] | None:
    """Get a primitive by name."""
    return PRIMITIVES.get(name.lower())


def all_primitives() -> list[PolyAgent[Any, Any, Any]]:
    """Get all primitives."""
    return list(PRIMITIVES.values())


def primitive_names() -> list[str]:
    """Get all primitive names."""
    return list(PRIMITIVES.keys())


__all__ = [
    # Types - Bootstrap
    "GroundState",
    "JudgeState",
    "ContradictState",
    "SublateState",
    "FixState",
    "Claim",
    "Verdict",
    "Thesis",
    "Antithesis",
    "Synthesis",
    # Types - Perception
    "WitnessState",
    "Handle",
    "Umwelt",
    "Manifestation",
    "Trace",
    # Types - Entropy
    "SipState",
    "TitheState",
    "EntropyRequest",
    "EntropyGrant",
    "Offering",
    "Spec",
    "Definition",
    # Types - Memory (D-gent)
    "RememberState",
    "ForgetState",
    "Memory",
    "MemoryResult",
    # Types - Teleological (E-gent, N-gent)
    "EvolveState",
    "NarrateState",
    "Organism",
    "Evolution",
    "Story",
    # Primitives - Bootstrap (7)
    "ID",
    "GROUND",
    "JUDGE",
    "CONTRADICT",
    "SUBLATE",
    "COMPOSE",
    "FIX",
    # Primitives - Perception (3)
    "MANIFEST",
    "WITNESS",
    "LENS",
    # Primitives - Entropy (3)
    "SIP",
    "TITHE",
    "DEFINE",
    # Primitives - Memory (2)
    "REMEMBER",
    "FORGET",
    # Primitives - Teleological (2)
    "EVOLVE",
    "NARRATE",
    # Registry
    "PRIMITIVES",
    "get_primitive",
    "all_primitives",
    "primitive_names",
]
