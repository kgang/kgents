# Creative Muse Protocol: Part III — The Creative Operad

> *"The grammar of creation: operations that compose, laws that liberate, iterations that refine."*

**Status:** Active (Updated for v2.0)
**Part of:** Creative Muse Protocol (C-gent)
**Dependencies:** muse.md (The Co-Creative Engine v2.0)
**Date:** 2025-01-11

---

## Purpose

This part defines the **Creative Operad**—the grammar of valid creative operations within the co-creative engine. While `muse.md` defines the dialectical process (amplify → select → contradict → defend), this document specifies the **atomic operations** and their **iteration characteristics**.

**Key v2.0 Alignment**: Every operation now specifies:
- **Typical iterations**: How many cycles to breakthrough
- **Volume target**: How many generations at each step
- **Contradiction hooks**: Where the Contradictor can intervene

## Core Insight

**Creative operations form an operad**: a mathematical structure where operations can be composed, and composition follows laws. In v2.0, the operad serves the dialectical engine—operations are the atoms, the engine is the reactor.

---

## I. The Operad Definition

### Formal Structure (v2.0)

```python
from dataclasses import dataclass
from typing import Callable, Any

@dataclass(frozen=True)
class Operation:
    """An operation in the Creative Operad (v2.0)."""
    name: str
    arity: int                      # How many inputs
    signature: str                  # Type signature
    description: str
    effects: frozenset[str]         # Side effects
    valid_modes: frozenset[str]     # Which modes allow this

    # v2.0 additions: iteration characteristics
    typical_iterations: tuple[int, int]  # (min, max) cycles to breakthrough
    volume_target: int                    # How many generations per cycle
    contradiction_hooks: frozenset[str]  # Where Contradictor can intervene
    surprise_potential: float            # 0.0-1.0: how much this can surprise

@dataclass(frozen=True)
class Law:
    """A composition law in the operad."""
    name: str
    equation: str
    description: str

CREATIVE_OPERAD = {
    "name": "CREATIVE_OPERAD",
    "version": "2.0",
    "extends": ["BASE_OPERAD"],
    "engine": "CoCreativeEngine",  # v2.0: operations serve the engine
    "operations": { ... },  # See below
    "laws": [ ... ],        # See below
}
```

### The 21 Creative Operations (v2.0 with Iteration Characteristics)

```python
CREATIVE_OPERATIONS = {
    # === SPARK PHASE (was DORMANT/RECEIVING) ===
    # These feed into the co-creative engine's initial spark

    "rest": Operation(
        name="rest",
        arity=0,
        signature="() → ()",
        description="Do nothing. This IS the operation.",
        effects=frozenset({"restores:energy"}),
        valid_modes=frozenset({"DORMANT"}),
        typical_iterations=(0, 0),  # No iterations—just rest
        volume_target=0,
        contradiction_hooks=frozenset(),
        surprise_potential=0.0,
    ),
    "gentle_wake": Operation(
        name="gentle_wake",
        arity=1,
        signature="Prompt → Maybe[Spark]",
        description="Softly invite without demanding",
        effects=frozenset(),
        valid_modes=frozenset({"DORMANT"}),
        typical_iterations=(1, 3),  # 1-3 gentle attempts
        volume_target=3,  # Just a few gentle prompts
        contradiction_hooks=frozenset(),  # No contradiction—too delicate
        surprise_potential=0.3,
    ),
    "wander": Operation(
        name="wander",
        arity=0,
        signature="() → Stream[Stimulus]",
        description="Open attention, no goal",
        effects=frozenset({"reads:environment"}),
        valid_modes=frozenset({"RECEIVING"}),
        typical_iterations=(5, 20),  # Extended wandering
        volume_target=100,  # High volume of stimuli
        contradiction_hooks=frozenset({"direction"}),
        surprise_potential=0.8,  # High—unexpected stimuli
    ),
    "capture": Operation(
        name="capture",
        arity=1,
        signature="Impulse → RawSpark",
        description="Record without judgment",
        effects=frozenset({"writes:spark_store"}),
        valid_modes=frozenset({"RECEIVING"}),
        typical_iterations=(1, 1),  # Instant—don't think
        volume_target=1,  # Capture THE moment
        contradiction_hooks=frozenset(),  # No contradiction—capture first
        surprise_potential=0.5,
    ),
    "associate": Operation(
        name="associate",
        arity=2,
        signature="(Spark, Spark) → Connection",
        description="Link two ideas freely",
        effects=frozenset(),
        valid_modes=frozenset({"RECEIVING"}),
        typical_iterations=(3, 15),  # Multiple association rounds
        volume_target=50,  # Many possible connections
        contradiction_hooks=frozenset({"obviousness", "novelty"}),
        surprise_potential=0.9,  # Where breakthroughs often emerge
    ),

    # === INCUBATION PHASE ===
    # Minimal iteration—let time work

    "marinate": Operation(
        name="marinate",
        arity=1,
        signature="Spark → Spark",  # Identity, but time passes
        description="Let subconscious process",
        effects=frozenset({"time:passes"}),
        valid_modes=frozenset({"INCUBATING"}),
        typical_iterations=(1, 1),  # One long marination
        volume_target=0,  # No generation—just waiting
        contradiction_hooks=frozenset(),  # Don't interrupt incubation
        surprise_potential=0.7,  # Subconscious often surprises
    ),
    "check_emergence": Operation(
        name="check_emergence",
        arity=1,
        signature="Spark → Maybe[CrystallizedIdea]",
        description="Has it surfaced? (creator-initiated only)",
        effects=frozenset({"reads:felt_sense"}),
        valid_modes=frozenset({"INCUBATING"}),
        typical_iterations=(1, 5),  # Check periodically
        volume_target=0,  # Just checking
        contradiction_hooks=frozenset(),
        surprise_potential=0.6,
    ),

    # === GENERATING PHASE (Core of co-creative engine) ===
    # High iteration, high volume—this is where the dialectic lives

    "flow": Operation(
        name="flow",
        arity=1,
        signature="Idea → Stream[Output]",
        description="Continuous generation, no interruption",
        effects=frozenset({"writes:draft"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(10, 50),  # 10-50 diverge-converge cycles
        volume_target=50,  # 50 variations per cycle (muse.md target)
        contradiction_hooks=frozenset({"direction", "voice", "surprise"}),
        surprise_potential=0.7,
    ),
    "branch": Operation(
        name="branch",
        arity=1,
        signature="Point → (Alternative, Alternative)",
        description="Explore two paths simultaneously",
        effects=frozenset({"writes:alternatives"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(5, 20),  # Each branch needs exploration
        volume_target=50,  # 50 variations per branch
        contradiction_hooks=frozenset({"commitment", "exploration"}),
        surprise_potential=0.85,  # Branching often leads to surprise
    ),
    "commit_chunk": Operation(
        name="commit_chunk",
        arity=1,
        signature="Draft → Draft",
        description="Lock in a section, keep moving",
        effects=frozenset({"mutates:draft"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(3, 10),  # Defense cycles before commit
        volume_target=10,  # Fewer variations—committing
        contradiction_hooks=frozenset({"premature_commitment"}),
        surprise_potential=0.3,  # Commitment, not discovery
    ),

    # === REFINING PHASE ===
    # Medium iteration—apply taste rigorously

    "critique": Operation(
        name="critique",
        arity=1,
        signature="Draft → CritiqueReport",
        description="Analyze what works and doesn't",
        effects=frozenset({"reads:draft"}),
        valid_modes=frozenset({"REFINING"}),
        typical_iterations=(3, 10),  # Multiple critique passes
        volume_target=20,  # Multiple critique angles
        contradiction_hooks=frozenset({"blind_spots", "favorites"}),
        surprise_potential=0.5,
    ),
    "apply_taste": Operation(
        name="apply_taste",
        arity=2,
        signature="(Draft, TasteVector) → Draft",
        description="Transform to match aesthetic vision",
        effects=frozenset({"mutates:draft"}),
        valid_modes=frozenset({"REFINING"}),
        typical_iterations=(5, 30),  # Many iterations to nail taste
        volume_target=30,  # Try many taste applications
        contradiction_hooks=frozenset({"taste_drift", "playing_safe"}),
        surprise_potential=0.6,
    ),
    "compress": Operation(
        name="compress",
        arity=1,
        signature="Draft → Draft",
        description="Remove without losing essence",
        effects=frozenset({"mutates:draft"}),
        valid_modes=frozenset({"REFINING"}),
        typical_iterations=(5, 20),  # Iterative compression
        volume_target=20,  # Many compression approaches
        contradiction_hooks=frozenset({"over_compression", "darlings"}),
        surprise_potential=0.4,
    ),
    "expand": Operation(
        name="expand",
        arity=2,
        signature="(Draft, Focus) → Draft",
        description="Develop underdeveloped section",
        effects=frozenset({"mutates:draft"}),
        valid_modes=frozenset({"REFINING"}),
        typical_iterations=(5, 25),  # Expansion needs exploration
        volume_target=40,  # Many expansion directions
        contradiction_hooks=frozenset({"bloat", "tangent"}),
        surprise_potential=0.6,
    ),
    "reorder": Operation(
        name="reorder",
        arity=2,
        signature="(Draft, NewStructure) → Draft",
        description="Change sequence without changing content",
        effects=frozenset({"mutates:draft"}),
        valid_modes=frozenset({"REFINING"}),
        typical_iterations=(3, 10),  # Structure exploration
        volume_target=15,  # Many orderings to try
        contradiction_hooks=frozenset({"conventional_structure"}),
        surprise_potential=0.7,  # Reordering often surprises
    ),

    # === RELEASING PHASE ===
    # Low iteration—commit to the world

    "finalize": Operation(
        name="finalize",
        arity=1,
        signature="Draft → Artifact",
        description="Convert draft to releasable form",
        effects=frozenset({"reads:draft", "writes:artifact"}),
        valid_modes=frozenset({"RELEASING"}),
        typical_iterations=(2, 5),  # Final polish rounds
        volume_target=5,  # Few variations—finalizing
        contradiction_hooks=frozenset({"premature_release"}),
        surprise_potential=0.2,
    ),
    "release": Operation(
        name="release",
        arity=2,
        signature="(Artifact, Venue) → Publication",
        description="Send into the world",
        effects=frozenset({"writes:public", "irreversible"}),
        valid_modes=frozenset({"RELEASING"}),
        typical_iterations=(1, 1),  # One shot—irreversible
        volume_target=0,  # No generation—just release
        contradiction_hooks=frozenset({"readiness"}),
        surprise_potential=0.1,
    ),

    # === EVOLVING PHASE ===
    # Post-release learning

    "gather_feedback": Operation(
        name="gather_feedback",
        arity=1,
        signature="Publication → FeedbackStream",
        description="Collect audience response",
        effects=frozenset({"reads:public"}),
        valid_modes=frozenset({"EVOLVING"}),
        typical_iterations=(5, 30),  # Ongoing feedback cycles
        volume_target=100,  # Many feedback sources
        contradiction_hooks=frozenset({"selection_bias"}),
        surprise_potential=0.7,  # Audience surprises
    ),
    "reflect": Operation(
        name="reflect",
        arity=1,
        signature="FeedbackStream → Insights",
        description="Extract learning from feedback",
        effects=frozenset(),
        valid_modes=frozenset({"EVOLVING"}),
        typical_iterations=(3, 10),  # Reflection cycles
        volume_target=20,  # Many reflection angles
        contradiction_hooks=frozenset({"defensive_interpretation"}),
        surprise_potential=0.6,
    ),
    "synthesize_learning": Operation(
        name="synthesize_learning",
        arity=2,
        signature="(Insights, CreativeIdentity) → CreativeIdentity",
        description="Update creative identity from learnings",
        effects=frozenset({"mutates:identity"}),
        valid_modes=frozenset({"EVOLVING"}),
        typical_iterations=(2, 5),  # Identity evolution cycles
        volume_target=10,  # Possible identity updates
        contradiction_hooks=frozenset({"over_correction", "stagnation"}),
        surprise_potential=0.5,
    ),

    # === CROSS-PHASE (Available Always) ===
    # The mirror test from muse.md v2.0

    "mirror_test": Operation(
        name="mirror_test",
        arity=1,
        signature="Any → FeltSense",
        description="Check resonance with creator identity—'Is this me on my best day?'",
        effects=frozenset({"reads:identity"}),
        valid_modes=frozenset({"*"}),  # Available in all modes
        typical_iterations=(1, 50),  # Every cycle can include mirror test
        volume_target=0,  # Not generative—evaluative
        contradiction_hooks=frozenset({"self_delusion", "playing_safe"}),
        surprise_potential=0.4,
    ),
}
```

### Iteration Summary Table

| Operation | Iterations | Volume | Surprise | Notes |
|-----------|------------|--------|----------|-------|
| `wander` | 5-20 | 100 | 0.8 | Extended exploration |
| `associate` | 3-15 | 50 | 0.9 | **Breakthrough zone** |
| `flow` | 10-50 | 50 | 0.7 | Core engine operation |
| `branch` | 5-20 | 50 | 0.85 | **Breakthrough zone** |
| `apply_taste` | 5-30 | 30 | 0.6 | Taste refinement |
| `compress` | 5-20 | 20 | 0.4 | Essence finding |
| `expand` | 5-25 | 40 | 0.6 | Development |
| `reorder` | 3-10 | 15 | 0.7 | Structure surprise |

**Breakthrough operations** (surprise potential > 0.8): `associate`, `branch`

**The v2.0 Principle**: Operations with high iteration counts and high volume targets are where the co-creative engine does its deepest work. The 30-50 iteration target from `muse.md` maps to the `flow` operation's (10, 50) range.

---

## II. The 11 Creative Laws (v2.0)

### Composition Laws

The original 10 laws remain, plus one new law for iteration bounds.

```python
CREATIVE_LAWS = [
    # === IDENTITY ===
    Law(
        name="identity_preservation",
        equation="mirror_test(work) >> work = work",
        description="Mirror Test doesn't change the work, only evaluates it",
    ),

    # === COMPOSITION ===
    Law(
        name="flow_composition",
        equation="flow(a) >> commit_chunk = flow(a)",
        description="Committing chunks doesn't break flow",
    ),
    Law(
        name="critique_idempotence",
        equation="critique(critique(work)) = critique(work)",
        description="Critiquing a critique report yields same insights",
    ),

    # === MODE BOUNDARIES ===
    Law(
        name="incubation_isolation",
        equation="∀op ∉ {marinate, check_emergence}: op ∉ INCUBATING",
        description="Only marination and emergence checking in incubation",
    ),
    Law(
        name="release_finality",
        equation="release(artifact) >> mutate = ERROR",
        description="Released work cannot be modified (learn for next)",
    ),

    # === LOSSY CREATION ===
    Law(
        name="galois_loss_positive",
        equation="loss(capture(impulse)) > 0",
        description="Capturing always loses some of the original impulse",
    ),
    Law(
        name="compression_irreversible",
        equation="compress(work) >> expand ≠ work",
        description="Compression loses information (this is intentional)",
    ),

    # === MIRROR TEST ===
    Law(
        name="mirror_gates_transitions",
        equation="transition(A, B) → mirror_test(work) = RESONANT",
        description="Gated transitions require passing Mirror Test",
    ),

    # === FLOW PROTECTION ===
    Law(
        name="flow_sanctuary",
        equation="in_flow(creator) → interrupt(creator) = ERROR",
        description="Flow state must not be interrupted",
    ),

    # === ASSOCIATIVITY ===
    Law(
        name="operation_associativity",
        equation="(f >> g) >> h = f >> (g >> h)",
        description="Operation composition is associative",
    ),

    # === v2.0: ITERATION BOUNDS ===
    Law(
        name="iteration_sufficiency",
        equation="iterations(op) < op.typical_iterations.min → NOT_BREAKTHROUGH",
        description="Breakthroughs require meeting minimum iteration thresholds",
    ),
]
```

### v2.0 Law Alignment

The laws now serve the co-creative engine:

| Law | Engine Role |
|-----|-------------|
| `identity_preservation` | Mirror test is evaluation, not transformation |
| `flow_composition` | Protect the diverge-converge spiral |
| `critique_idempotence` | Critique is stable—don't over-critique |
| `incubation_isolation` | Let incubation work undisturbed |
| `release_finality` | No post-release edits—learn for next |
| `galois_loss_positive` | Accept lossy capture—it's generative |
| `compression_irreversible` | Compression is commitment |
| `mirror_gates_transitions` | Mirror test gates phase transitions |
| `flow_sanctuary` | Protect flow state absolutely |
| `operation_associativity` | Operations compose cleanly |
| **`iteration_sufficiency`** | **Breakthrough requires sufficient iteration** |

---

## III. Improvisation Mode (v2.0)

### The Free Jazz Operad Extension

For freestyle creative work (rap, improv comedy, dance), the operad extends with **improvisation operations**. In v2.0, these are **real-time variants** of the co-creative engine—the dialectic compressed into seconds.

```python
IMPROVISATION_OPERATIONS = {
    "yes_and": Operation(
        name="yes_and",
        arity=2,
        signature="(Offer, Response) → Extension",
        description="Accept and build on collaborator's offer",
        effects=frozenset({"realtime"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(1, 1),  # Instant—no time to iterate
        volume_target=1,  # One response in the moment
        contradiction_hooks=frozenset(),  # No contradiction—pure acceptance
        surprise_potential=0.7,
    ),
    "heighten": Operation(
        name="heighten",
        arity=1,
        signature="Pattern → Pattern",
        description="Increase intensity of established pattern",
        effects=frozenset({"realtime"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(1, 3),  # 1-3 heightening beats
        volume_target=1,
        contradiction_hooks=frozenset({"peak_detection"}),
        surprise_potential=0.5,
    ),
    "call_back": Operation(
        name="call_back",
        arity=2,
        signature="(Current, Earlier) → Synthesis",
        description="Reference earlier element for payoff",
        effects=frozenset({"reads:memory"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(1, 1),  # One callback per opportunity
        volume_target=1,
        contradiction_hooks=frozenset(),
        surprise_potential=0.9,  # Callbacks often delight
    ),
    "break_pattern": Operation(
        name="break_pattern",
        arity=1,
        signature="Pattern → Surprise",
        description="Subvert expectation for comedic/dramatic effect",
        effects=frozenset({"realtime"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(1, 1),  # One break—timing is everything
        volume_target=1,
        contradiction_hooks=frozenset(),
        surprise_potential=0.95,  # The whole point is surprise
    ),
    "ride_wave": Operation(
        name="ride_wave",
        arity=1,
        signature="Momentum → Flow",
        description="Maintain energy without forcing direction",
        effects=frozenset({"realtime"}),
        valid_modes=frozenset({"GENERATING"}),
        typical_iterations=(5, 30),  # Ride as long as it lasts
        volume_target=0,  # Not generating—sustaining
        contradiction_hooks=frozenset({"energy_drop"}),
        surprise_potential=0.4,
    ),
}

IMPROVISATION_LAWS = [
    Law(
        name="yes_and_foundation",
        equation="yes_and(offer, _) >> block = VIOLATION",
        description="Never block after accepting an offer",
    ),
    Law(
        name="heighten_bounds",
        equation="heighten^n(pattern) for n > 3 → break_pattern(pattern)",
        description="Patterns can only heighten so far before breaking",
    ),
    Law(
        name="no_preplan",
        equation="script >> improvise = NOT_IMPROVISATION",
        description="Scripted 'improv' isn't improv",
    ),
]
```

### v2.0 Note: Improv as Compressed Dialectic

The co-creative engine runs over 30-50 iterations. Improvisation compresses the same pattern into real-time:

| Engine Phase | Improv Equivalent |
|--------------|-------------------|
| Amplify (50 options) | Instant pattern recognition |
| Select | Split-second choice |
| Contradict | Audience energy as feedback |
| Defend/Pivot | yes_and / break_pattern |

**The surprise coefficient is still the measure**: Did the improv moment surprise even the improviser?

---

## IV. Format Templates (v2.0)

### Reusable Creative Structures with Iteration Guidance

```python
@dataclass(frozen=True)
class FormatTemplate:
    """
    A reusable structural pattern for creative work.

    Like types in programming—templates constrain while enabling.

    v2.0 additions: iteration guidance per beat.
    """
    name: str
    domain: str                   # "youtube", "tv", "music", etc.
    structure: list[StructureBeat]
    constraints: list[str]
    flexibility: float            # 0.0 = rigid, 1.0 = loose
    typical_duration: timedelta
    total_iterations: tuple[int, int]  # v2.0: (min, max) iterations for full template

@dataclass(frozen=True)
class StructureBeat:
    """A moment in a format template."""
    name: str
    description: str
    duration: timedelta | None
    required: bool
    position: str  # "start", "middle", "end", "anywhere"
    iterations: tuple[int, int]  # v2.0: how many iterations for this beat
    volume_target: int           # v2.0: how many options to generate
```

### Example Templates (v2.0 with Iteration Guidance)

```python
# YouTube Format Templates
YOUTUBE_ESSAY = FormatTemplate(
    name="Video Essay",
    domain="youtube",
    structure=[
        StructureBeat("hook", "Grab attention, pose question", timedelta(seconds=10), True, "start",
                      iterations=(20, 50), volume_target=50),  # Hook is CRITICAL—many iterations
        StructureBeat("context", "Why this matters", timedelta(seconds=30), True, "start",
                      iterations=(5, 15), volume_target=20),
        StructureBeat("thesis", "Central argument", timedelta(seconds=15), True, "start",
                      iterations=(10, 30), volume_target=30),  # Thesis needs precision
        StructureBeat("evidence_1", "First supporting point", None, True, "middle",
                      iterations=(5, 15), volume_target=20),
        StructureBeat("evidence_2", "Second supporting point", None, True, "middle",
                      iterations=(5, 15), volume_target=20),
        StructureBeat("evidence_3", "Third supporting point", None, False, "middle",
                      iterations=(5, 10), volume_target=15),
        StructureBeat("counterargument", "Address objections", None, False, "middle",
                      iterations=(5, 10), volume_target=15),
        StructureBeat("synthesis", "Bring it together", timedelta(seconds=60), True, "end",
                      iterations=(10, 25), volume_target=30),
        StructureBeat("cta", "What to do next", timedelta(seconds=15), True, "end",
                      iterations=(3, 10), volume_target=10),
    ],
    constraints=[
        "Hook must be under 10 seconds",
        "Pattern interrupt every 30 seconds",
        "Payoff must match promise",
    ],
    flexibility=0.3,  # Fairly structured
    typical_duration=timedelta(minutes=12),
    total_iterations=(70, 180),  # v2.0: sum of beat iterations
)

# TV Format Templates
SITCOM_EPISODE = FormatTemplate(
    name="Sitcom Episode",
    domain="tv",
    structure=[
        StructureBeat("cold_open", "Pre-title comedic scene", timedelta(minutes=2), True, "start",
                      iterations=(15, 40), volume_target=40),  # Cold open must land
        StructureBeat("title", "Opening credits", timedelta(seconds=30), True, "start",
                      iterations=(1, 1), volume_target=0),  # Fixed
        StructureBeat("act_1", "Setup—introduce conflict", timedelta(minutes=5), True, "middle",
                      iterations=(10, 30), volume_target=30),
        StructureBeat("act_2a", "Complication—conflict deepens", timedelta(minutes=5), True, "middle",
                      iterations=(10, 25), volume_target=25),
        StructureBeat("act_2b", "Crisis—lowest point", timedelta(minutes=5), True, "middle",
                      iterations=(15, 35), volume_target=35),  # Crisis needs intensity
        StructureBeat("act_3", "Resolution—conflict resolved", timedelta(minutes=4), True, "end",
                      iterations=(10, 25), volume_target=25),
        StructureBeat("tag", "Post-credits button", timedelta(seconds=30), False, "end",
                      iterations=(5, 15), volume_target=20),  # Tag should surprise
    ],
    constraints=[
        "A-plot and B-plot must intersect",
        "Character must learn (or pointedly not learn)",
        "Callbacks to earlier seasons encouraged",
    ],
    flexibility=0.4,
    typical_duration=timedelta(minutes=22),
    total_iterations=(65, 170),
)

# Music Format Templates
POP_SONG = FormatTemplate(
    name="Pop Song",
    domain="music",
    structure=[
        StructureBeat("intro", "Musical introduction", timedelta(seconds=10), False, "start",
                      iterations=(5, 15), volume_target=15),
        StructureBeat("verse_1", "First verse", timedelta(seconds=30), True, "start",
                      iterations=(15, 40), volume_target=40),
        StructureBeat("pre_chorus", "Build to chorus", timedelta(seconds=15), False, "anywhere",
                      iterations=(10, 25), volume_target=25),
        StructureBeat("chorus", "Main hook", timedelta(seconds=30), True, "anywhere",
                      iterations=(30, 80), volume_target=80),  # CHORUS IS EVERYTHING
        StructureBeat("verse_2", "Second verse", timedelta(seconds=30), True, "middle",
                      iterations=(10, 25), volume_target=30),
        StructureBeat("chorus_2", "Chorus repeat", timedelta(seconds=30), True, "middle",
                      iterations=(5, 10), volume_target=10),  # Variation on chorus 1
        StructureBeat("bridge", "Contrast section", timedelta(seconds=20), False, "middle",
                      iterations=(15, 35), volume_target=35),  # Bridge surprises
        StructureBeat("final_chorus", "Big finish", timedelta(seconds=45), True, "end",
                      iterations=(10, 20), volume_target=20),
        StructureBeat("outro", "Musical exit", timedelta(seconds=10), False, "end",
                      iterations=(3, 10), volume_target=10),
    ],
    constraints=[
        "Chorus must arrive by 1:00",
        "Hook must be singable",
        "Total duration under 4:00 for radio",
    ],
    flexibility=0.5,
    typical_duration=timedelta(minutes=3, seconds=30),
    total_iterations=(100, 260),  # Pop song needs VOLUME
)
```

### Iteration Investment by Beat Type

| Beat Type | Iterations | Why |
|-----------|------------|-----|
| **Hook/Chorus** | 30-80 | This is what people remember |
| **Opening/Cold Open** | 15-50 | First impression is everything |
| **Crisis/Bridge** | 15-35 | Emotional peak needs precision |
| **Evidence/Body** | 5-15 | Supporting material, less critical |
| **Outro/Tag** | 3-15 | Landing, but less weight |

**The v2.0 principle**: Iteration investment should match importance. Don't spend 50 iterations on an outro while settling for 10 on a chorus.

### Template Operations (v2.0)

```python
def apply_template(
    work: Work,
    template: FormatTemplate,
    session: CoCreativeSession,
) -> StructuredWork:
    """Apply format template with iteration-aware processing."""
    structured = StructuredWork(template=template)

    for beat in template.structure:
        # Run co-creative engine for each beat
        # with beat-specific iteration targets
        beat_content = await co_create_beat(
            work=work,
            beat=beat,
            min_iterations=beat.iterations[0],
            max_iterations=beat.iterations[1],
            volume_target=beat.volume_target,
            session=session,
        )
        structured.add_beat(beat.name, beat_content)

    return structured

def deviate_from_template(
    work: StructuredWork,
    deviation: Deviation,
    justification: str,
) -> StructuredWork:
    """
    Intentionally break template rules (with reason).

    v2.0: Deviation triggers extra contradiction cycles.
    The Contradictor will challenge: "Why deviate here?"
    """
    # Record deviation and justification
    # Trigger contradiction: is this daring or lazy?
    challenge = await contradict_deviation(deviation, justification)

    if challenge.requires_defense:
        defense = await require_defense(deviation, challenge)
        if defense.conviction < 0.8:
            # Weak defense—maybe reconsider
            warn(f"Deviation defense conviction only {defense.conviction}")

    return work.with_deviation(deviation, justification, defense)
```

---

## V. The Difference Operad (Ghost Alternatives) — v2.0

### Capturing the Paths Not Taken

In v2.0, the Ghost Operad becomes **essential** to the co-creative engine. With 50 options generated per cycle and only 1 selected, we produce **49 ghosts per iteration**. Over 30-50 iterations, that's **1,500-2,500 ghosts per session**.

These aren't waste—they're the negative space that defines the work.

```python
@dataclass(frozen=True)
class GhostWork:
    """
    A work that could have been but wasn't.

    Every creative decision closes off alternatives.
    The Muse preserves these ghosts for learning and future resurrection.

    v2.0: Ghosts are now first-class citizens of the co-creative process.
    """
    branch_point: str           # Where did we diverge?
    alternative: str            # What would have been?
    rationale: str              # Why didn't we take this path?
    work_id: str                # Reference to actual work
    iteration: int              # v2.0: Which iteration produced this ghost?
    surprise_at_rejection: float  # v2.0: How surprising was it to reject this?
    contradictor_opinion: str | None  # v2.0: Did the Contradictor champion this?

class DifferanceOperation:
    """
    Operations for tracking creative alternatives.

    Named after Derrida's différance—meaning is created
    by what is NOT present as much as what IS.

    v2.0: Integrated with the co-creative engine's contradiction phase.
    """

    @staticmethod
    def mark_branch(
        work: Work,
        decision: str,
        alternatives: list[str],
        session: CoCreativeSession,
    ) -> list[GhostWork]:
        """Record a decision point and its alternatives."""
        ghosts = []
        for alt in alternatives:
            # v2.0: Calculate surprise at rejection
            surprise = await measure_rejection_surprise(alt, session.taste)

            ghosts.append(GhostWork(
                branch_point=decision,
                alternative=alt,
                rationale=session.latest_defense.reasoning if session.latest_defense else "Chose differently",
                work_id=work.id,
                iteration=session.current_iteration,
                surprise_at_rejection=surprise,
                contradictor_opinion=session.contradictor_advocacy.get(alt),
            ))
        return ghosts

    @staticmethod
    async def resurrect_ghost(
        ghost: GhostWork,
        taste: TasteVector,
    ) -> Work:
        """
        What if we had taken the other path?

        v2.0: Resurrection starts a new co-creative session
        with the ghost as the initial spark.
        """
        session = CoCreativeSession(
            spark=ghost.alternative,
            context=f"Resurrected from {ghost.work_id}, iteration {ghost.iteration}",
        )

        # Run the full co-creative process on the ghost
        return await session.run()

    @staticmethod
    async def analyze_ghosts(
        session: CoCreativeSession,
    ) -> GhostAnalysis:
        """
        v2.0: Post-session ghost analysis.

        What patterns emerge in what was rejected?
        Which ghosts did the Contradictor champion?
        Are there ghosts worth resurrecting?
        """
        ghosts = session.all_ghosts

        # Find patterns in rejections
        rejection_patterns = extract_patterns([g.alternative for g in ghosts])

        # Find contradictor-championed ghosts
        championed = [g for g in ghosts if g.contradictor_opinion]

        # Find surprisingly rejected (high surprise_at_rejection)
        surprising_rejections = [g for g in ghosts if g.surprise_at_rejection > 0.7]

        return GhostAnalysis(
            total_ghosts=len(ghosts),
            rejection_patterns=rejection_patterns,
            contradictor_championed=championed,
            worth_resurrecting=surprising_rejections[:5],  # Top 5
        )
```

### v2.0 Ghost Metrics

| Metric | Formula | Meaning |
|--------|---------|---------|
| Ghost Volume | iterations × (volume - 1) | Total alternatives not taken |
| Rejection Surprise | avg(surprise_at_rejection) | Are we rejecting surprising things? |
| Contradictor Agreement | ghosts where contradictor agreed with rejection | Engine harmony |
| Resurrection Rate | resurrected / total_ghosts | How often do we revisit? |

**The v2.0 insight**: A session with no surprising rejections probably isn't generating enough volume. A session with too many contradictor-championed ghosts might be ignoring good challenges.

---

## VI. Integration with Co-Creative Engine (v2.0)

### From Polynomial Modes to Engine Phases

In v1.0, operations were tied to polynomial modes (DORMANT, RECEIVING, GENERATING, etc.). In v2.0, **the co-creative engine is the primary structure**, and modes are phases within the engine:

```python
# v1.0 mental model:
# Mode → Valid Operations → Execute

# v2.0 mental model:
# Engine Phase → Operation with Iteration Target → Dialectic Loop → Breakthrough
```

### Operation-Engine Integration

```python
async def execute_operation_v2(
    engine: CoCreativeEngine,
    operation: Operation,
    *args,
    **kwargs,
) -> OperationResult:
    """Execute operation within co-creative engine context."""

    # Validate operation is valid for current engine phase
    if not engine.allows_operation(operation):
        raise InvalidOperationForPhase(
            f"Cannot perform {operation.name} in engine phase {engine.phase}"
        )

    # Determine iteration target
    min_iter, max_iter = operation.typical_iterations
    target_iterations = engine.calibrate_iterations(min_iter, max_iter)

    # Track ghosts (alternatives not taken)
    ghosts_produced = []

    # Run dialectic loop for this operation
    current = args[0] if args else None
    for iteration in range(target_iterations):
        # AMPLIFY: Generate options
        options = await engine.amplify(current, count=operation.volume_target)

        # SELECT: Kent picks
        selected = await engine.kent_select(options)
        ghosts_produced.extend([opt for opt in options if opt != selected])

        # CONTRADICT (if hooks defined)
        if operation.contradiction_hooks:
            challenge = await engine.contradict(
                selected,
                hooks=operation.contradiction_hooks,
            )
            response = await engine.kent_respond(challenge)
            current = engine.apply_response(current, response)
        else:
            current = selected

        # Check for early exit (escape velocity)
        if await engine.has_escape_velocity(current):
            break

    return OperationResult(
        output=current,
        iterations_used=iteration + 1,
        ghosts=ghosts_produced,
        surprise_coefficient=await engine.measure_surprise(current),
    )
```

### Phase-Operation Mapping

| Engine Phase | Primary Operations | Iteration Target |
|--------------|-------------------|------------------|
| SPARK | `gentle_wake`, `wander`, `capture`, `associate` | 1-20 |
| SPIRAL | `flow`, `branch`, `commit_chunk` | 10-50 |
| REFINE | `critique`, `apply_taste`, `compress`, `expand`, `reorder` | 5-30 |
| CRYSTALLIZE | `finalize` | 2-5 |
| RELEASE | `release` | 1 |
| EVOLVE | `gather_feedback`, `reflect`, `synthesize_learning` | 3-30 |

---

## VII. Laws Summary Table (v2.0)

| # | Law | Equation | Category | Engine Role |
|---|-----|----------|----------|-------------|
| 1 | identity_preservation | `mirror_test >> work = work` | Identity | Evaluate, don't transform |
| 2 | flow_composition | `flow >> commit_chunk = flow` | Composition | Protect spiral integrity |
| 3 | critique_idempotence | `critique(critique(x)) = critique(x)` | Idempotence | Don't over-critique |
| 4 | incubation_isolation | Only marinate, check_emergence in INCUBATING | Mode Boundary | Let incubation work |
| 5 | release_finality | `release >> mutate = ERROR` | Irreversibility | No post-release edits |
| 6 | galois_loss_positive | `loss(capture(impulse)) > 0` | Lossy Creation | Accept capture loss |
| 7 | compression_irreversible | `compress >> expand ≠ id` | Lossy Creation | Compression commits |
| 8 | mirror_gates_transitions | Transitions require `mirror_test = RESONANT` | Mirror Test | Gate phase changes |
| 9 | flow_sanctuary | `in_flow → interrupt = ERROR` | Protection | Protect flow state |
| 10 | operation_associativity | `(f >> g) >> h = f >> (g >> h)` | Associativity | Clean composition |
| **11** | **iteration_sufficiency** | `iterations < min → NOT_BREAKTHROUGH` | **Iteration** | **Breakthrough requires work** |

---

## VIII. AGENTESE Integration (v2.0)

```python
# === CO-CREATIVE ENGINE (v2.0 primary interface) ===
# Start a co-creative session
await logos.invoke("self.muse.session.start",
                   spark="melancholy summer",
                   domain="music",
                   target_iterations=50)

# Run the dialectic loop
await logos.invoke("self.muse.session.amplify", count=50)
await logos.invoke("self.muse.session.select", selected_id="opt-23")
await logos.invoke("self.muse.session.contradict")
await logos.invoke("self.muse.session.defend", reasoning="The minor key creates...")
await logos.invoke("self.muse.session.pivot", new_direction="What if major key?")

# Check breakthrough metrics
await logos.invoke("self.muse.session.surprise")         # Surprise coefficient
await logos.invoke("self.muse.session.escape_velocity")  # Has it crystallized?
await logos.invoke("self.muse.session.breakthrough_probability")

# === OPERATIONS (with iteration targets) ===
await logos.invoke("self.muse.op.flow",
                   work_id="poem-1",
                   min_iterations=10,
                   max_iterations=50)
await logos.invoke("self.muse.op.critique", work_id="essay-draft")
await logos.invoke("self.muse.op.capture", impulse="A flash of insight...")
await logos.invoke("self.muse.op.branch", point="verse-2-line-3")

# === TEMPLATE OPERATIONS ===
await logos.invoke("self.muse.template.apply",
                   work_id="video-3",
                   template="youtube_essay",
                   respect_iteration_targets=True)
await logos.invoke("self.muse.template.list", domain="tv")
await logos.invoke("self.muse.template.deviate",
                   work_id="song-1",
                   deviation="skip_pre_chorus",
                   justification="Goes against expectation")

# === GHOST OPERATIONS (v2.0 enhanced) ===
await logos.invoke("self.muse.ghost.mark",
                   work_id="song-1",
                   decision="chorus melody",
                   alternatives=["rising", "falling", "static"])
await logos.invoke("self.muse.ghost.analyze", session_id="session-42")
await logos.invoke("self.muse.ghost.resurrect",
                   ghost_id="ghost-123",
                   start_new_session=True)
await logos.invoke("self.muse.ghost.worth_resurrecting", session_id="session-42")

# === IMPROVISATION ===
await logos.invoke("self.muse.improv.yes_and", offer="Let's say it's a submarine")
await logos.invoke("self.muse.improv.heighten", pattern="increasing absurdity")
await logos.invoke("self.muse.improv.break_pattern", pattern="the submarine")
await logos.invoke("self.muse.improv.call_back", earlier="the first mention of water")

# === TASTE OPERATIONS (v2.0) ===
await logos.invoke("self.muse.taste.current")           # Get current taste vector
await logos.invoke("self.muse.taste.apply",
                   work_id="draft-1",
                   taste_vector="KENT_TASTE")
await logos.invoke("self.muse.taste.drift_check", session_id="session-42")
await logos.invoke("self.muse.taste.externalized_mirror_test", work_id="final-draft")
```

---

## IX. Anti-Patterns (v2.0)

### Original Anti-Patterns (Still Valid)

- **Operation Phase Mismatch**: Critiquing during SPIRAL (kills flow)
- **Template Rigidity**: Following template at expense of creative truth
- **Ghost Hoarding**: Keeping too many alternatives (decision paralysis)
- **Law Violation**: Breaking laws without explicit justification
- **Improv Blocking**: Saying "no" to offers in collaborative improv
- **Compression Regret**: Trying to expand after compression (information is lost)

### New v2.0 Anti-Patterns

| Anti-Pattern | Symptom | Fix |
|--------------|---------|-----|
| **Iteration Starvation** | Settling for first good option | Meet minimum iteration targets |
| **Volume Anemia** | Generating 5 options instead of 50 | Trust the engine—volume enables selection |
| **Contradiction Avoidance** | Agreeing too easily with AI | Engage with challenges; defend or discover |
| **Ghost Blindness** | Ignoring rejected alternatives | Analyze ghosts post-session |
| **Premature Escape** | Declaring escape velocity too early | Check all metrics, not just "feels done" |
| **Taste Drift Denial** | Not noticing taste evolution | Run drift checks regularly |
| **Surprise Complacency** | Accepting unsurprising outcomes | Target surprise coefficient > 0.7 |

### The Cardinal Sin: Shortcutting the Dialectic

```python
# WRONG: AI generates, Kent accepts
options = await amplify(spark, count=50)
result = options[0]  # Just take the first one

# RIGHT: Full dialectic loop
options = await amplify(spark, count=50)
selected = await kent_select(options)
challenge = await contradict(selected)
response = await kent_respond(challenge)
# ... continue until escape velocity
```

**The v2.0 principle**: Every shortcut costs surprise coefficient. Breakthrough requires the full dialectic.

---

## X. Relationship to muse.md v2.0

This document (Part III) provides the **atomic operations and laws** that the co-creative engine (muse.md) orchestrates.

| muse.md | Part III (This Document) |
|---------|--------------------------|
| The Co-Creative Engine | Operations the engine uses |
| Dialectic Loop | Operation execution with iterations |
| Taste Vector | `apply_taste` operation |
| Surprise Coefficient | `surprise_potential` per operation |
| Breakthrough Formula | `iteration_sufficiency` law |
| Domain Engines | Format Templates |
| Ghost Alternatives | Différance Operad |

**Read muse.md first** to understand the engine. **Read Part III** to understand the operations.

---

*"The operad is the grammar. The laws are the freedom within structure. The iterations are the work."*

*Part III of Creative Muse Protocol | The Creative Operad | v2.0 Aligned*
