# Creative Muse Protocol: Part II — The Creative Polynomial

> **SUPERSEDED BY muse.md v2.0 (2025-01-11)**
>
> This document describes a seven-mode state machine for creative work. While the concepts remain sound (flow protection, incubation rights, mode-dependent validity), the primary model for co-creation is now the **dialectical engine** in muse.md v2.0.
>
> **What's still useful here:**
> - Section III (Right to Incubate) — valid protection concept
> - Section V (Flow State Protection) — applicable within GENERATING sessions
> - The transition graph (Section IV) — useful for tracking work lifecycle
>
> **What's superseded:**
> - The seven modes as primary model → replaced by diverge-converge spiral
> - Linear stage progression → replaced by 30-50 iteration loops
> - Focus on "what phase is work in?" → replaced by "how do we generate breakthrough?"
>
> **Integration path:** The polynomial could become a *state layer* within the co-creative engine—tracking macro lifecycle while the dialectical spiral operates at the micro level.

---

> *"You cannot edit while receiving. You cannot generate while dormant. Mode-dependent validity is not a limitation—it's the structure of creative flow."*

**Status:** Deprecated (see header)
**Part of:** Creative Muse Protocol (C-gent)
**Superseded by:** muse.md v2.0 (The Co-Creative Engine)
**Dependencies:** Part I (Creative Kernel, Mirror Test, Galois Loss)

---

## Purpose

This part defines the **Creative Polynomial**—the formal state machine for creative work. Unlike linear pipelines, the polynomial captures the reality that creators move non-linearly between distinct modes, each with its own valid inputs and protections.

## Core Insight

**Creativity is a seven-mode polynomial with mode-dependent input validity.** Each mode accepts different inputs; forcing invalid inputs into a mode damages the creative process.

---

## I. The Seven Creative Modes

### Formal Definition

```python
from enum import Enum, auto
from dataclasses import dataclass
from typing import FrozenSet
from datetime import timedelta

class MuseMode(Enum):
    """The seven modes of creative work."""

    DORMANT = auto()     # Fallow period, necessary rest
    RECEIVING = auto()   # Raw inspiration arrives
    INCUBATING = auto()  # Subconscious processing (protected)
    GENERATING = auto()  # Active creation, flow state
    REFINING = auto()    # Conscious editing, taste application
    RELEASING = auto()   # Publication, audience encounter
    EVOLVING = auto()    # Post-release learning

@dataclass(frozen=True)
class CreativePolynomial:
    """
    PolyAgent[MuseMode, CreativeInput, CreativeOutput]

    A polynomial functor where:
    - Positions = The seven MuseModes
    - Directions = Valid inputs per mode
    - Transitions = Movement between modes
    """
    mode: MuseMode
    work: "Work"
    entered_at: "datetime"

    def direction_type(self) -> type:
        """What inputs are valid in this mode?"""
        return DIRECTION_TYPES[self.mode]
```

### Mode Descriptions

| Mode | Description | Duration | Energy |
|------|-------------|----------|--------|
| **DORMANT** | Fallow period, creative rest | Days to weeks | Restorative |
| **RECEIVING** | Inspiration arrives unbidden | Minutes to hours | Receptive |
| **INCUBATING** | Subconscious processing | Hours to months | Underground |
| **GENERATING** | Active creation, flow state | Hours | High output |
| **REFINING** | Conscious editing | Hours to days | Focused |
| **RELEASING** | Publication moment | Minutes | Vulnerable |
| **EVOLVING** | Learning from feedback | Ongoing | Reflective |

---

## II. Direction Functions (Mode-Dependent Inputs)

### The Core Insight

Each mode has a **direction function** that defines valid inputs:

```python
DIRECTION_TYPES: dict[MuseMode, type] = {
    MuseMode.DORMANT: DormantInput,
    MuseMode.RECEIVING: ReceivingInput,
    MuseMode.INCUBATING: IncubatingInput,
    MuseMode.GENERATING: GeneratingInput,
    MuseMode.REFINING: RefiningInput,
    MuseMode.RELEASING: ReleasingInput,
    MuseMode.EVOLVING: EvolvingInput,
}
```

### Input Types

```python
@dataclass(frozen=True)
class DormantInput:
    """Almost nothing is valid—this is rest."""
    gentle_prompt: str | None = None  # Soft invitation, not demand
    # INVALID: Deadlines, critiques, new ideas, "what about..."

@dataclass(frozen=True)
class ReceivingInput:
    """Raw inspiration only."""
    stimulus: str | None = None       # External trigger
    wandering: str | None = None      # Daydream content
    # INVALID: "Is this good?", critique, structure, expectations

@dataclass(frozen=True)
class IncubatingInput:
    """Almost nothing—protected mode."""
    # This is the "Right to Incubate"
    # INVALID: "Show me what you have", deadlines, check-ins
    # ONLY VALID: gentle_emergence (the idea surfaces naturally)

@dataclass(frozen=True)
class GeneratingInput:
    """Active creation inputs."""
    flow_aid: str | None = None       # Tools, references
    momentum: bool = True             # Keep going
    # INVALID: Heavy critique, "actually, let's change direction"

@dataclass(frozen=True)
class RefiningInput:
    """Editing and improvement inputs."""
    critique: str | None = None       # Specific feedback
    taste_check: str | None = None    # "Does this feel right?"
    constraint: str | None = None     # "Make it shorter"
    # INVALID: New inspiration (go back to RECEIVING first)

@dataclass(frozen=True)
class ReleasingInput:
    """Publication moment inputs."""
    confirmation: bool = False        # "Yes, release it"
    venue: str | None = None          # Where to publish
    # INVALID: Major changes (go back to REFINING first)

@dataclass(frozen=True)
class EvolvingInput:
    """Post-release learning inputs."""
    audience_feedback: str | None = None
    metrics: dict | None = None
    self_reflection: str | None = None
    # INVALID: Retrofitting the released work
```

### Invalid Input Matrix

| Mode | INVALID Inputs | Why |
|------|---------------|-----|
| DORMANT | Deadlines, critiques | Rest requires absence of pressure |
| RECEIVING | Judgment, structure | Kills nascent ideas |
| INCUBATING | Exposure, check-ins | Forces premature crystallization |
| GENERATING | Heavy critique | Breaks flow state |
| REFINING | New inspiration | Scope creep, restart |
| RELEASING | Major changes | Decision paralysis |
| EVOLVING | Retrofitting | Work is released; learn for next |

---

## III. The Right to Incubate

### The Protected Mode

```python
class IncubationProtection:
    """
    The Right to Incubate: A creative work in INCUBATING mode
    MUST NOT be prematurely exposed or forced to crystallize.

    This is the creative equivalent of "Right to Rest" in labor.
    """

    @staticmethod
    def valid_inputs() -> FrozenSet[type]:
        """Almost nothing is valid during incubation."""
        return frozenset()  # Empty! Only emergence is valid

    @staticmethod
    def violations() -> list[str]:
        return [
            "Asking to see progress",
            "Setting artificial deadlines",
            "Requesting updates",
            "Comparing to other works",
            "Questioning whether you're 'really' working",
        ]

    @staticmethod
    def valid_emergence() -> str:
        """The ONLY valid exit: the idea surfaces naturally."""
        return "The creator feels the work is ready to emerge"
```

### Incubation Duration

```python
@dataclass(frozen=True)
class IncubationBounds:
    """Typical incubation durations by creative domain."""

    # Short-form
    freestyle_verse: timedelta = timedelta(seconds=0)  # No incubation
    tweet: timedelta = timedelta(minutes=5)

    # Medium-form
    song: timedelta = timedelta(days=7)
    essay: timedelta = timedelta(days=14)

    # Long-form
    novel_chapter: timedelta = timedelta(weeks=4)
    album_concept: timedelta = timedelta(months=2)

    # Epic
    series_arc: timedelta = timedelta(months=6)

    # NO UPPER BOUND: Some works incubate for years
```

### Forced Incubation Exit (Anti-Pattern)

```python
class ForcedIncubationExit(Exception):
    """
    Raised when someone tries to force a work out of incubation.

    This is a VIOLATION of the creative process.
    """

    def __init__(self, work_id: str, forcing_agent: str, reason: str):
        self.work_id = work_id
        self.forcing_agent = forcing_agent
        self.reason = reason
        super().__init__(
            f"VIOLATION: {forcing_agent} attempted to force {work_id} "
            f"out of incubation. Reason given: '{reason}'. "
            f"Incubation cannot be forced—only the creator can feel emergence."
        )
```

---

## IV. Mode Transitions

### Transition Graph

```
                    ┌──────────────────────────────────────┐
                    │                                      │
                    ▼                                      │
              ┌─────────┐                                  │
              │ DORMANT │◄─────────────────────────────────┤
              └────┬────┘                                  │
                   │ spark                                 │
                   ▼                                       │
              ┌───────────┐                                │
              │ RECEIVING │                                │
              └─────┬─────┘                                │
                    │ captured                             │
                    ▼                                      │
              ┌────────────┐                               │
         ┌────│ INCUBATING │◄────────┐                     │
         │    └──────┬─────┘         │                     │
         │           │ emerged       │ retreat             │
         │           ▼               │                     │
         │    ┌────────────┐         │                     │
         │    │ GENERATING │─────────┤                     │
         │    └──────┬─────┘         │                     │
         │           │ draft_complete│                     │
         │           ▼               │                     │
         │    ┌──────────┐           │                     │
         │    │ REFINING │───────────┘                     │
         │    └────┬─────┘                                 │
         │         │ satisfied                             │
         │         ▼                                       │
         │    ┌───────────┐                                │
         │    │ RELEASING │                                │
         │    └─────┬─────┘                                │
         │          │ released                             │
         │          ▼                                      │
         │    ┌──────────┐                                 │
         └────│ EVOLVING │─────────────────────────────────┘
              └──────────┘     (feedback loop to dormant or new receiving)
```

### Transition Rules

```python
VALID_TRANSITIONS: dict[MuseMode, set[MuseMode]] = {
    MuseMode.DORMANT: {MuseMode.RECEIVING},           # Only spark exits dormant
    MuseMode.RECEIVING: {MuseMode.INCUBATING, MuseMode.DORMANT},  # Capture or discard
    MuseMode.INCUBATING: {MuseMode.GENERATING, MuseMode.DORMANT}, # Emerge or abandon
    MuseMode.GENERATING: {MuseMode.REFINING, MuseMode.INCUBATING}, # Complete or retreat
    MuseMode.REFINING: {MuseMode.RELEASING, MuseMode.GENERATING, MuseMode.INCUBATING},
    MuseMode.RELEASING: {MuseMode.EVOLVING},          # Only forward
    MuseMode.EVOLVING: {MuseMode.DORMANT, MuseMode.RECEIVING},    # Rest or new spark
}

def can_transition(from_mode: MuseMode, to_mode: MuseMode) -> bool:
    """Check if transition is valid."""
    return to_mode in VALID_TRANSITIONS.get(from_mode, set())
```

### Transition Triggers

```python
@dataclass(frozen=True)
class TransitionTrigger:
    """What causes a mode transition?"""

    from_mode: MuseMode
    to_mode: MuseMode
    trigger: str
    requires_mirror_test: bool  # Does creator need to feel it?

TRANSITION_TRIGGERS = [
    TransitionTrigger(MuseMode.DORMANT, MuseMode.RECEIVING,
                      "spark", requires_mirror_test=False),
    TransitionTrigger(MuseMode.RECEIVING, MuseMode.INCUBATING,
                      "captured", requires_mirror_test=True),
    TransitionTrigger(MuseMode.INCUBATING, MuseMode.GENERATING,
                      "emerged", requires_mirror_test=True),  # CRITICAL
    TransitionTrigger(MuseMode.GENERATING, MuseMode.REFINING,
                      "draft_complete", requires_mirror_test=True),
    TransitionTrigger(MuseMode.REFINING, MuseMode.RELEASING,
                      "satisfied", requires_mirror_test=True),  # CRITICAL
    TransitionTrigger(MuseMode.RELEASING, MuseMode.EVOLVING,
                      "released", requires_mirror_test=False),
    TransitionTrigger(MuseMode.EVOLVING, MuseMode.DORMANT,
                      "rest_needed", requires_mirror_test=True),
]
```

---

## V. Flow State Protection

### The GENERATING Sanctuary

```python
class FlowStateProtection:
    """
    When in GENERATING mode, the creator has entered flow state.
    Interruptions are costly—each one can cost 15-30 minutes to recover.
    """

    minimum_uninterrupted: timedelta = timedelta(minutes=90)
    recovery_cost_per_interruption: timedelta = timedelta(minutes=23)

    @staticmethod
    def valid_interrupts() -> list[str]:
        """Only these are acceptable during flow."""
        return [
            "Fire",
            "Medical emergency",
            "Creator-initiated pause",
        ]

    @staticmethod
    def invalid_interrupts() -> list[str]:
        """These break flow and should be blocked."""
        return [
            "Notifications",
            "Questions about progress",
            "New ideas (capture them for later)",
            "Critiques (save for REFINING)",
            "Administrative tasks",
        ]
```

### Mode-Specific Environments

```python
@dataclass(frozen=True)
class ModeEnvironment:
    """Optimal environment for each mode."""

    mode: MuseMode
    physical_space: str
    tools_available: list[str]
    tools_hidden: list[str]
    notification_level: str
    social_context: str

MODE_ENVIRONMENTS = {
    MuseMode.DORMANT: ModeEnvironment(
        mode=MuseMode.DORMANT,
        physical_space="Comfortable, non-work",
        tools_available=["relaxation", "nature"],
        tools_hidden=["work tools", "projects"],
        notification_level="off",
        social_context="non-demanding",
    ),
    MuseMode.RECEIVING: ModeEnvironment(
        mode=MuseMode.RECEIVING,
        physical_space="Open, stimulating",
        tools_available=["notebook", "voice recorder"],
        tools_hidden=["editing tools", "publishing"],
        notification_level="off",
        social_context="wandering conversations",
    ),
    MuseMode.INCUBATING: ModeEnvironment(
        mode=MuseMode.INCUBATING,
        physical_space="Private, protected",
        tools_available=["journal"],
        tools_hidden=["collaboration", "feedback"],
        notification_level="off",
        social_context="solitary",
    ),
    MuseMode.GENERATING: ModeEnvironment(
        mode=MuseMode.GENERATING,
        physical_space="Focused studio",
        tools_available=["creation tools", "references"],
        tools_hidden=["email", "social", "analytics"],
        notification_level="blocked",
        social_context="flow-compatible collaborators only",
    ),
    MuseMode.REFINING: ModeEnvironment(
        mode=MuseMode.REFINING,
        physical_space="Analytical space",
        tools_available=["editing tools", "critique notes"],
        tools_hidden=["new inspiration sources"],
        notification_level="scheduled",
        social_context="trusted editors",
    ),
    MuseMode.RELEASING: ModeEnvironment(
        mode=MuseMode.RELEASING,
        physical_space="Launch station",
        tools_available=["publishing tools"],
        tools_hidden=["editing tools"],  # No last-minute changes!
        notification_level="on",
        social_context="support network",
    ),
    MuseMode.EVOLVING: ModeEnvironment(
        mode=MuseMode.EVOLVING,
        physical_space="Reflective space",
        tools_available=["analytics", "feedback channels"],
        tools_hidden=["the released work"],  # Don't retrofit
        notification_level="curated",
        social_context="learning community",
    ),
}
```

---

## VI. Integration with Creative Kernel

### Polynomial-Kernel Connection

```
L0.3 MIRROR → Mode transitions require felt sense
L0.2 MORPHISM → Transitions are morphisms between modes
L1.7 FIX → Flow state is a fixed point (stable creative output)

CreativePolynomial ← PolyAgent[MuseMode, CreativeInput, CreativeOutput]
                  ← L2.5 COMPOSABLE (polynomial functors compose)
```

### Mirror Test Integration

```python
async def attempt_transition(
    current: CreativePolynomial,
    target_mode: MuseMode,
    trigger: str,
) -> CreativePolynomial | None:
    """Attempt a mode transition, respecting Mirror Test."""

    # 1. Check if transition is valid
    if not can_transition(current.mode, target_mode):
        raise InvalidTransitionError(current.mode, target_mode)

    # 2. Find trigger definition
    trigger_def = next(
        (t for t in TRANSITION_TRIGGERS
         if t.from_mode == current.mode and t.to_mode == target_mode),
        None
    )

    if trigger_def is None:
        raise UndefinedTransitionError(current.mode, target_mode)

    # 3. If transition requires Mirror Test, ask creator
    if trigger_def.requires_mirror_test:
        felt_sense = await ask_creator_mirror_test(
            f"Does this work feel ready to move from {current.mode} to {target_mode}?"
        )

        if felt_sense != FeltSense.RESONANT:
            return None  # Not ready to transition

    # 4. Execute transition
    return CreativePolynomial(
        mode=target_mode,
        work=current.work,
        entered_at=datetime.now(),
    )
```

---

## VII. Laws

| # | Law | Description |
|---|-----|-------------|
| 1 | mode_exclusivity | Work is in exactly ONE mode at any time |
| 2 | valid_transition | Transitions MUST follow VALID_TRANSITIONS graph |
| 3 | mirror_test_gates | Transitions marked `requires_mirror_test` MUST pass Mirror Test |
| 4 | incubation_protection | INCUBATING mode accepts almost no inputs |
| 5 | flow_sanctuary | GENERATING mode blocks non-emergency interrupts |
| 6 | no_retrofitting | EVOLVING mode learns for future, doesn't change released work |

---

## VIII. AGENTESE Integration

```python
# Mode queries
await logos.invoke("self.muse.mode.current", work_id="novel-ch3")
# → MuseMode.INCUBATING

await logos.invoke("self.muse.mode.valid_inputs", mode=MuseMode.GENERATING)
# → GeneratingInput fields

await logos.invoke("self.muse.mode.transition",
                   work_id="novel-ch3",
                   target=MuseMode.GENERATING)
# → Attempts transition (may trigger Mirror Test)

# Environment suggestions
await logos.invoke("self.muse.environment.suggest", mode=MuseMode.GENERATING)
# → ModeEnvironment for flow state
```

---

## IX. Anti-Patterns

- **Mode Blending**: Editing while receiving inspiration (kills the idea)
- **Forced Emergence**: Pulling work out of incubation before it's ready
- **Flow Interruption**: Notifications during GENERATING (23-minute recovery cost)
- **Retrofit Compulsion**: Changing released work instead of learning for next
- **Dormant Guilt**: Treating rest as "not working" (rest IS the work)
- **Skip Incubation**: Going directly from RECEIVING to GENERATING (rushed, thin)

---

*"The mode IS the protection. The polynomial IS the permission."*

---

## Relationship to muse.md v2.0

The v2.0 rewrite asks a different question. This document asks: *"What mode is the work in?"* v2.0 asks: *"How does breakthrough emerge?"*

The seven modes describe a **lifecycle** (work moves from DORMANT to EVOLVING over weeks/months). The v2.0 spiral describes **micro-iterations** (30-50 diverge-converge cycles within a single session).

**Potential synthesis:**

```
MACRO (Polynomial):     RECEIVING → INCUBATING → GENERATING → REFINING → RELEASING
                                                      │
                                                      ▼
MICRO (v2.0 Spiral):    spark → amplify → select → contradict → defend/pivot → repeat 30-50x
                                                      │
                                                      ▼
                                              escape velocity reached
```

The polynomial tells you *what protections apply* (flow state protection in GENERATING, incubation rights in INCUBATING). The spiral tells you *how to produce breakthrough work within those modes*.

If this integration proves valuable, a future spec could unify them. For now, v2.0 is the primary model.

---

*Part II of Creative Muse Protocol | The Creative Polynomial | DEPRECATED 2025-01-11*
