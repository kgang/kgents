# Part II: The Creative Polynomial

> *"The creative process has its own rhythms. INCUBATING cannot be rushed. GENERATING cannot be forced. The polynomial respects the natural cycle."*

---

## Overview

The **CreativePolynomial** models the creative process as a state machine with mode-dependent behavior. Unlike productivity systems that treat all time as equally available for input, the creative polynomial recognizes that certain phases (especially INCUBATING) require protection from interruption.

This is the creative equivalent of the CitizenPolynomial's "Right to Rest"—we call it the **"Right to Incubate"**.

---

## The Seven Creative Modes

```python
class CreativeMode(Enum):
    """
    Positions in the creative polynomial.

    These are interpretive frames, not internal states (Barad).
    The mode determines which interactions are valid (directions).
    """

    VOID = auto()        # Pre-creative emptiness, receptive to seeds
    RECEIVING = auto()   # Collecting inspiration, references, raw material
    INCUBATING = auto()  # Background processing, unconscious connections forming
    GENERATING = auto()  # Active creation, flow state, surrendering to the work
    EDITING = auto()     # Refining, selecting, shaping what was generated
    RELEASING = auto()   # Sharing, publishing, letting go of attachment
    REFLECTING = auto()  # Meta-level: what did I learn? What wants to emerge next?
```

### Mode Descriptions

| Mode | Characteristic Activity | Valid Interruptions | Typical Duration |
|------|------------------------|---------------------|------------------|
| **VOID** | Stillness, openness, no agenda | External prompts welcome | 5-30 min |
| **RECEIVING** | Reading, listening, collecting | Anything that adds material | 15-60 min |
| **INCUBATING** | Walking, resting, not-doing | **Almost none** (Right to Incubate) | 30 min - 3 days |
| **GENERATING** | Writing, coding, making | Flow-compatible only | 30 min - 4 hours |
| **EDITING** | Refining, selecting, shaping | Analytical tools | 15 min - 2 hours |
| **RELEASING** | Publishing, sharing, shipping | Celebration, feedback | 5-30 min |
| **REFLECTING** | Meta-analysis, pattern extraction | Anything (most receptive state) | 10-60 min |

---

## Input Types (Directions at Each Position)

```python
# =============================================================================
# Input Types for Creative Modes
# =============================================================================

@dataclass(frozen=True)
class ReceiveInput:
    """Input for receiving inspiration."""
    source_type: str  # "article", "conversation", "observation", "prompt"
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IncubateInput:
    """Input to transition into incubation."""
    seed: str | None = None  # What to incubate on (optional)
    estimated_duration_hours: float = 1.0


@dataclass(frozen=True)
class GenerateInput:
    """Input for active creation."""
    medium: str  # "text", "code", "visual", "audio"
    prompt: str | None = None
    flow_mode: bool = True  # If False, allows more interruption


@dataclass(frozen=True)
class EditInput:
    """Input for refinement."""
    target: str  # What artifact to edit
    operation: str  # "refine", "cut", "expand", "restructure"


@dataclass(frozen=True)
class ReleaseInput:
    """Input to release/publish."""
    artifact: str
    destination: str  # "public", "team", "archive"


@dataclass(frozen=True)
class ReflectInput:
    """Input for meta-reflection."""
    focus: str | None = None  # What to reflect on


@dataclass(frozen=True)
class EmergenceReadyInput:
    """Signal from incubation: something wants to emerge."""
    insight: str | None = None


@dataclass(frozen=True)
class ExternalPromptInput:
    """External prompt/seed while in VOID."""
    prompt: str
    urgency: float = 0.3  # How urgent (0-1)
```

---

## Direction Function (Mode-Dependent Valid Inputs)

The direction function encodes **which inputs are valid at each creative mode**. This is where the "Right to Incubate" is structurally enforced.

```python
def creative_directions(mode: CreativeMode) -> FrozenSet[type]:
    """
    Valid inputs for each creative mode.

    Key constraints:
    - INCUBATING has VERY FEW valid inputs (Right to Incubate)
    - GENERATING in flow_mode rejects analytical/editorial inputs
    - REFLECTING is most permissive (can transition anywhere)
    """
    match mode:
        case CreativeMode.VOID:
            # Receptive to anything that seeds creation
            return frozenset({
                ExternalPromptInput,
                ReceiveInput,
                ReflectInput,
            })

        case CreativeMode.RECEIVING:
            # Collecting material
            return frozenset({
                ReceiveInput,      # Continue receiving
                IncubateInput,     # Start incubation
                GenerateInput,     # Jump straight to creation (rare but valid)
                ReflectInput,      # Exit to reflection
            })

        case CreativeMode.INCUBATING:
            # RIGHT TO INCUBATE: Only emergence signal is valid
            # Cannot force, cannot rush, cannot interrupt
            return frozenset({
                EmergenceReadyInput,  # Natural completion signal
            })

        case CreativeMode.GENERATING:
            # Flow state: only flow-compatible inputs
            return frozenset({
                GenerateInput,     # Continue generating
                EditInput,         # Shift to editing
                IncubateInput,     # Return to incubation (stuck)
                ReflectInput,      # Exit to reflection
            })

        case CreativeMode.EDITING:
            # Analytical mode: most tool inputs valid
            return frozenset({
                EditInput,         # Continue editing
                GenerateInput,     # Return to generation
                ReleaseInput,      # Ready to release
                ReflectInput,      # Exit to reflection
            })

        case CreativeMode.RELEASING:
            # Publishing/sharing
            return frozenset({
                ReleaseInput,      # Continue release process
                ReflectInput,      # Natural next step
            })

        case CreativeMode.REFLECTING:
            # Most permissive: can go anywhere from here
            return frozenset({
                ReceiveInput,      # New material
                IncubateInput,     # Start new incubation
                GenerateInput,     # Start new creation
                ReflectInput,      # Continue reflection
                ExternalPromptInput,  # Accept new seeds
            })

        case _:
            return frozenset()


# Type signature for clarity
creative_directions: Callable[[CreativeMode], FrozenSet[type]]
```

### Key Insight: Incubation is Protected

Notice that `CreativeMode.INCUBATING` accepts **only one input type**: `EmergenceReadyInput`. This is the polynomial enforcement of the "Right to Incubate" law.

You cannot:
- Force a creative breakthrough
- Rush unconscious processing
- Interrupt incubation with "helpful" suggestions

The only valid transition out of INCUBATING is when the work itself signals readiness to emerge.

---

## Transition Function

The transition function implements the behavioral logic for each mode.

```python
@dataclass
class CreativeOutput:
    """Output from creative transitions."""
    mode: CreativeMode
    success: bool
    message: str = ""
    artifact: Any | None = None  # Created/edited artifact (if any)
    energy_delta: float = 0.0    # Energy change (-1 to 1)
    metadata: dict[str, Any] = field(default_factory=dict)


def creative_transition(
    mode: CreativeMode,
    input: Any,
) -> tuple[CreativeMode, CreativeOutput]:
    """
    Creative process state transition function.

    transition: Mode × Input → (NewMode, Output)

    From Barad: The transition reconfigures the phenomenon.
    The creative process doesn't change—our cut on it changes.
    """

    match mode:
        case CreativeMode.VOID:
            if isinstance(input, ExternalPromptInput):
                # Seed received in void → transition to receiving
                return CreativeMode.RECEIVING, CreativeOutput(
                    mode=CreativeMode.RECEIVING,
                    success=True,
                    message=f"Received prompt: {input.prompt[:50]}...",
                    energy_delta=0.2,
                    metadata={"prompt": input.prompt, "urgency": input.urgency},
                )
            elif isinstance(input, ReceiveInput):
                # Direct material collection
                return CreativeMode.RECEIVING, CreativeOutput(
                    mode=CreativeMode.RECEIVING,
                    success=True,
                    message=f"Began collecting from {input.source_type}",
                    energy_delta=0.1,
                )
            elif isinstance(input, ReflectInput):
                return CreativeMode.REFLECTING, CreativeOutput(
                    mode=CreativeMode.REFLECTING,
                    success=True,
                    message="Entered reflection from void",
                    energy_delta=0.0,
                )
            else:
                # Invalid input for VOID
                return CreativeMode.VOID, CreativeOutput(
                    mode=CreativeMode.VOID,
                    success=False,
                    message=f"VOID does not accept {type(input).__name__}",
                    energy_delta=0.0,
                )

        case CreativeMode.RECEIVING:
            if isinstance(input, ReceiveInput):
                # Continue receiving
                return CreativeMode.RECEIVING, CreativeOutput(
                    mode=CreativeMode.RECEIVING,
                    success=True,
                    message=f"Collected from {input.source_type}",
                    energy_delta=0.1,
                    metadata={"source": input.source_type},
                )
            elif isinstance(input, IncubateInput):
                # Transition to incubation
                return CreativeMode.INCUBATING, CreativeOutput(
                    mode=CreativeMode.INCUBATING,
                    success=True,
                    message=f"Began incubating (est. {input.estimated_duration_hours}h)",
                    energy_delta=-0.3,  # Incubation costs energy upfront
                    metadata={
                        "seed": input.seed,
                        "duration": input.estimated_duration_hours,
                    },
                )
            elif isinstance(input, GenerateInput):
                # Direct to generation (rare but valid)
                return CreativeMode.GENERATING, CreativeOutput(
                    mode=CreativeMode.GENERATING,
                    success=True,
                    message=f"Began generating ({input.medium})",
                    energy_delta=0.4,
                    metadata={"medium": input.medium},
                )
            elif isinstance(input, ReflectInput):
                return CreativeMode.REFLECTING, CreativeOutput(
                    mode=CreativeMode.REFLECTING,
                    success=True,
                    message="Exited receiving for reflection",
                    energy_delta=0.0,
                )
            else:
                return CreativeMode.RECEIVING, CreativeOutput(
                    mode=CreativeMode.RECEIVING,
                    success=False,
                    message=f"RECEIVING does not accept {type(input).__name__}",
                )

        case CreativeMode.INCUBATING:
            # RIGHT TO INCUBATE: Only EmergenceReadyInput is valid
            if isinstance(input, EmergenceReadyInput):
                # Natural emergence → transition to generating
                return CreativeMode.GENERATING, CreativeOutput(
                    mode=CreativeMode.GENERATING,
                    success=True,
                    message="Incubation complete—ready to create",
                    energy_delta=0.6,  # Burst of creative energy
                    metadata={"insight": input.insight},
                )
            else:
                # Reject ALL other inputs
                return CreativeMode.INCUBATING, CreativeOutput(
                    mode=CreativeMode.INCUBATING,
                    success=False,
                    message=(
                        "Cannot interrupt incubation (Right to Incubate). "
                        "Wait for natural emergence signal."
                    ),
                    energy_delta=-0.2,  # Interruption drains energy
                )

        case CreativeMode.GENERATING:
            if isinstance(input, GenerateInput):
                # Continue generating (flow state)
                return CreativeMode.GENERATING, CreativeOutput(
                    mode=CreativeMode.GENERATING,
                    success=True,
                    message=f"Continued generating ({input.medium})",
                    energy_delta=0.3,
                    metadata={
                        "medium": input.medium,
                        "flow": input.flow_mode,
                    },
                )
            elif isinstance(input, EditInput):
                # Shift to editing
                return CreativeMode.EDITING, CreativeOutput(
                    mode=CreativeMode.EDITING,
                    success=True,
                    message=f"Shifted to editing: {input.operation}",
                    energy_delta=-0.1,  # Slight energy drop leaving flow
                    metadata={"target": input.target, "operation": input.operation},
                )
            elif isinstance(input, IncubateInput):
                # Stuck? Return to incubation
                return CreativeMode.INCUBATING, CreativeOutput(
                    mode=CreativeMode.INCUBATING,
                    success=True,
                    message="Returned to incubation (generation stalled)",
                    energy_delta=-0.2,
                    metadata={"reason": "generation_stall"},
                )
            elif isinstance(input, ReflectInput):
                return CreativeMode.REFLECTING, CreativeOutput(
                    mode=CreativeMode.REFLECTING,
                    success=True,
                    message="Exited generation for reflection",
                    energy_delta=0.0,
                )
            else:
                return CreativeMode.GENERATING, CreativeOutput(
                    mode=CreativeMode.GENERATING,
                    success=False,
                    message=f"GENERATING rejects {type(input).__name__} (flow protection)",
                    energy_delta=-0.1,
                )

        case CreativeMode.EDITING:
            if isinstance(input, EditInput):
                # Continue editing
                return CreativeMode.EDITING, CreativeOutput(
                    mode=CreativeMode.EDITING,
                    success=True,
                    message=f"Applied {input.operation} to {input.target}",
                    energy_delta=0.1,
                    metadata={
                        "target": input.target,
                        "operation": input.operation,
                    },
                )
            elif isinstance(input, GenerateInput):
                # Return to generation
                return CreativeMode.GENERATING, CreativeOutput(
                    mode=CreativeMode.GENERATING,
                    success=True,
                    message="Returned to generation from editing",
                    energy_delta=0.2,
                )
            elif isinstance(input, ReleaseInput):
                # Ready to release
                return CreativeMode.RELEASING, CreativeOutput(
                    mode=CreativeMode.RELEASING,
                    success=True,
                    message=f"Releasing to {input.destination}",
                    energy_delta=0.0,
                    metadata={
                        "artifact": input.artifact,
                        "destination": input.destination,
                    },
                )
            elif isinstance(input, ReflectInput):
                return CreativeMode.REFLECTING, CreativeOutput(
                    mode=CreativeMode.REFLECTING,
                    success=True,
                    message="Exited editing for reflection",
                    energy_delta=0.0,
                )
            else:
                return CreativeMode.EDITING, CreativeOutput(
                    mode=CreativeMode.EDITING,
                    success=False,
                    message=f"EDITING does not accept {type(input).__name__}",
                )

        case CreativeMode.RELEASING:
            if isinstance(input, ReleaseInput):
                # Continue release
                return CreativeMode.RELEASING, CreativeOutput(
                    mode=CreativeMode.RELEASING,
                    success=True,
                    message=f"Released {input.artifact}",
                    energy_delta=-0.3,  # Release is draining
                    metadata={"artifact": input.artifact},
                )
            elif isinstance(input, ReflectInput):
                # Natural progression: release → reflect
                return CreativeMode.REFLECTING, CreativeOutput(
                    mode=CreativeMode.REFLECTING,
                    success=True,
                    message="Released and now reflecting",
                    energy_delta=0.0,
                )
            else:
                return CreativeMode.RELEASING, CreativeOutput(
                    mode=CreativeMode.RELEASING,
                    success=False,
                    message=f"RELEASING does not accept {type(input).__name__}",
                )

        case CreativeMode.REFLECTING:
            # REFLECTING is most permissive—can transition anywhere
            if isinstance(input, ReflectInput):
                return CreativeMode.REFLECTING, CreativeOutput(
                    mode=CreativeMode.REFLECTING,
                    success=True,
                    message=f"Continued reflecting on {input.focus or 'the work'}",
                    energy_delta=0.0,
                )
            elif isinstance(input, ReceiveInput):
                return CreativeMode.RECEIVING, CreativeOutput(
                    mode=CreativeMode.RECEIVING,
                    success=True,
                    message="Moved from reflection to receiving new material",
                    energy_delta=0.1,
                )
            elif isinstance(input, IncubateInput):
                return CreativeMode.INCUBATING, CreativeOutput(
                    mode=CreativeMode.INCUBATING,
                    success=True,
                    message="Moved from reflection to incubation",
                    energy_delta=-0.2,
                    metadata={"seed": input.seed},
                )
            elif isinstance(input, GenerateInput):
                return CreativeMode.GENERATING, CreativeOutput(
                    mode=CreativeMode.GENERATING,
                    success=True,
                    message="Moved from reflection to generation",
                    energy_delta=0.4,
                )
            elif isinstance(input, ExternalPromptInput):
                # Accept new seeds while reflecting
                return CreativeMode.VOID, CreativeOutput(
                    mode=CreativeMode.VOID,
                    success=True,
                    message="Returned to void to consider new prompt",
                    energy_delta=0.0,
                    metadata={"prompt": input.prompt},
                )
            else:
                return CreativeMode.REFLECTING, CreativeOutput(
                    mode=CreativeMode.REFLECTING,
                    success=False,
                    message=f"REFLECTING does not accept {type(input).__name__}",
                )

        case _:
            # Unknown mode
            return CreativeMode.VOID, CreativeOutput(
                mode=CreativeMode.VOID,
                success=False,
                message=f"Unknown mode: {mode}",
            )
```

---

## State Diagram

```
                              ┌─────────────┐
                              │    VOID     │ ◄───────────┐
                              │ (receptive) │             │
                              └─────┬───────┘             │
                                    │                     │
                       ┌────────────┴────────────┐       │
                       │                         │       │
                       ▼                         ▼       │
                ┌────────────┐           ┌────────────┐  │
                │ RECEIVING  │           │ REFLECTING │ ─┘
                │ (collect)  │◄─────────►│(meta-view) │
                └─────┬──────┘           └──────┬─────┘
                      │                         ▲
                      ▼                         │
                ┌────────────┐                 │
                │INCUBATING  │                 │
                │ (protected)│                 │
                └─────┬──────┘                 │
                      │ EmergenceReady         │
                      │ ONLY                   │
                      ▼                        │
                ┌────────────┐                 │
                │ GENERATING │                 │
                │(flow state)│─────────────────┘
                └─────┬──────┘
                      │
                      ▼
                ┌────────────┐
                │  EDITING   │
                │ (refining) │
                └─────┬──────┘
                      │
                      ▼
                ┌────────────┐
                │ RELEASING  │
                │ (sharing)  │
                └─────┬──────┘
                      │
                      └─────────► REFLECTING
```

**Key Transitions:**
- INCUBATING → GENERATING: Only via `EmergenceReadyInput` (cannot be forced)
- REFLECTING → *: Can transition to any mode (most flexible)
- GENERATING → INCUBATING: Valid escape when stuck
- Any mode → REFLECTING: Always valid (escape hatch)

---

## The CreativePolynomial Definition

```python
from agents.poly.protocol import PolyAgent

CREATIVE_POLYNOMIAL: PolyAgent[CreativeMode, Any, CreativeOutput] = PolyAgent(
    name="CreativePolynomial",
    positions=frozenset(CreativeMode),
    _directions=creative_directions,
    _transition=creative_transition,
)
"""
The Creative polynomial agent.

Models the creative process as a polynomial state machine:
- positions: 7 modes (VOID, RECEIVING, INCUBATING, GENERATING, EDITING, RELEASING, REFLECTING)
- directions: mode-dependent valid inputs
- transition: creative process transitions

Key Properties:
    1. Right to Incubate: INCUBATING mode cannot be interrupted
       Only EmergenceReadyInput is valid during INCUBATING

    2. Flow Protection: GENERATING mode rejects analytical/editorial inputs
       when in flow_mode=True

    3. Reflection Flexibility: REFLECTING is the most permissive mode,
       can transition to any other mode

    4. Energy Tracking: All transitions include energy_delta to model
       the energetic cost/gain of each mode shift

Example:
    >>> poly = CREATIVE_POLYNOMIAL
    >>> mode = CreativeMode.VOID
    >>>
    >>> # Receive a prompt
    >>> mode, output = poly.invoke(mode, ExternalPromptInput("Write about trees"))
    >>> print(mode)
    CreativeMode.RECEIVING
    >>>
    >>> # Begin incubation
    >>> mode, output = poly.invoke(mode, IncubateInput(seed="trees", estimated_duration_hours=2.0))
    >>> print(mode)
    CreativeMode.INCUBATING
    >>>
    >>> # Try to interrupt (fails)
    >>> mode, output = poly.invoke(mode, GenerateInput(medium="text"))
    >>> print(output.success)
    False
    >>> print(output.message)
    "Cannot interrupt incubation (Right to Incubate). Wait for natural emergence signal."
    >>>
    >>> # Natural emergence
    >>> mode, output = poly.invoke(mode, EmergenceReadyInput(insight="Trees as memory"))
    >>> print(mode)
    CreativeMode.GENERATING
"""
```

---

## The "Right to Incubate" Law

### Formalization

**Law**: During `CreativeMode.INCUBATING`, the polynomial MUST reject all inputs except `EmergenceReadyInput`.

**Rationale**: Incubation is the unconscious processing phase where connections form outside conscious awareness. Interrupting this process:
1. Disrupts neurological consolidation
2. Forces premature closure on incomplete insights
3. Creates shallow work that lacks depth
4. Violates the natural rhythm of the creative process

**Implementation**: The law is enforced at two levels:

1. **Direction Function** (structural):
   ```python
   case CreativeMode.INCUBATING:
       return frozenset({EmergenceReadyInput})
   ```

2. **Transition Function** (behavioral):
   ```python
   case CreativeMode.INCUBATING:
       if isinstance(input, EmergenceReadyInput):
           # Natural completion
           return CreativeMode.GENERATING, ...
       else:
           # Reject with error
           return CreativeMode.INCUBATING, CreativeOutput(
               success=False,
               message="Cannot interrupt incubation (Right to Incubate)",
               energy_delta=-0.2,  # Interruption attempt drains energy
           )
   ```

### Why This Matters

Most productivity tools treat all time as equally available for input. They assume:
- You can task-switch at will
- Interruptions are minor inconveniences
- "Just do the work" is always valid advice

The CreativePolynomial rejects this model. It recognizes that **incubation has its own telos**—it completes when it completes, not when you want it to complete.

This is parallel to the CitizenPolynomial's "Right to Rest":

| Polynomial | Protected Mode | Valid Input | Rationale |
|------------|---------------|-------------|-----------|
| **CitizenPolynomial** | RESTING | WakeInput only | Rest is restorative, cannot be interrupted |
| **CreativePolynomial** | INCUBATING | EmergenceReadyInput only | Incubation forms connections, cannot be rushed |

---

## Usage Examples

### Example 1: Full Creative Cycle

```python
from services.muse.polynomial import (
    CREATIVE_POLYNOMIAL,
    CreativeMode,
    ExternalPromptInput,
    IncubateInput,
    EmergenceReadyInput,
    GenerateInput,
    EditInput,
    ReleaseInput,
    ReflectInput,
)

poly = CREATIVE_POLYNOMIAL

# Start in VOID
mode = CreativeMode.VOID

# Receive prompt
mode, output = poly.invoke(mode, ExternalPromptInput("Spec for creative process"))
assert mode == CreativeMode.RECEIVING
print(output.message)  # "Received prompt: Spec for creative process..."

# Begin incubation
mode, output = poly.invoke(mode, IncubateInput(
    seed="creative process as polynomial",
    estimated_duration_hours=4.0,
))
assert mode == CreativeMode.INCUBATING
print(output.message)  # "Began incubating (est. 4.0h)"

# Try to force generation (fails)
mode, output = poly.invoke(mode, GenerateInput(medium="text"))
assert output.success == False
assert mode == CreativeMode.INCUBATING  # Still incubating
print(output.message)  # "Cannot interrupt incubation..."

# ... time passes, insight forms ...

# Natural emergence
mode, output = poly.invoke(mode, EmergenceReadyInput(
    insight="Creative process mirrors polynomial structure with protected states"
))
assert mode == CreativeMode.GENERATING
print(output.energy_delta)  # 0.6 (burst of energy)

# Generate
mode, output = poly.invoke(mode, GenerateInput(medium="text", prompt="Write the spec"))
assert mode == CreativeMode.GENERATING

# Move to editing
mode, output = poly.invoke(mode, EditInput(target="spec", operation="refine"))
assert mode == CreativeMode.EDITING

# Release
mode, output = poly.invoke(mode, ReleaseInput(artifact="spec/muse-part-ii.md", destination="public"))
assert mode == CreativeMode.RELEASING

# Reflect
mode, output = poly.invoke(mode, ReflectInput(focus="What did I learn?"))
assert mode == CreativeMode.REFLECTING
```

### Example 2: Returning to Incubation When Stuck

```python
# In GENERATING mode
mode = CreativeMode.GENERATING

# Try to generate but feel stuck
mode, output = poly.invoke(mode, GenerateInput(medium="code", prompt="Implement feature X"))

# Recognize stuckness → return to incubation
mode, output = poly.invoke(mode, IncubateInput(seed="Why is feature X hard?"))
assert mode == CreativeMode.INCUBATING
assert output.metadata["reason"] == "generation_stall"

# ... incubate ...

# Emerge with new approach
mode, output = poly.invoke(mode, EmergenceReadyInput(insight="Feature X needs refactor first"))
assert mode == CreativeMode.GENERATING
```

---

## Integration with Muse

The CreativePolynomial provides the state machine foundation for the Muse's whisper system:

```python
class MuseService:
    """The Muse tracks creative state and suggests at appropriate moments."""

    def __init__(self):
        self.creative_poly = CREATIVE_POLYNOMIAL
        self.mode = CreativeMode.VOID
        self.mode_history: list[tuple[CreativeMode, datetime]] = []

    async def track_transition(self, input: Any) -> CreativeOutput:
        """Track a creative mode transition."""
        old_mode = self.mode
        self.mode, output = self.creative_poly.invoke(self.mode, input)

        # Record transition
        self.mode_history.append((self.mode, datetime.now()))

        # Whisper logic (respects mode)
        if self._should_whisper(old_mode, self.mode, output):
            whisper = self._generate_whisper(self.mode, output)
            # Present whisper to user...

        return output

    def _should_whisper(
        self,
        old_mode: CreativeMode,
        new_mode: CreativeMode,
        output: CreativeOutput,
    ) -> bool:
        """Decide if Muse should whisper based on transition."""
        # NEVER whisper during INCUBATING
        if new_mode == CreativeMode.INCUBATING:
            return False

        # Consider whispering after GENERATING → EDITING transition
        if old_mode == CreativeMode.GENERATING and new_mode == CreativeMode.EDITING:
            return True  # Suggest crystallization before editing

        # Consider whispering after RELEASING → REFLECTING
        if old_mode == CreativeMode.RELEASING and new_mode == CreativeMode.REFLECTING:
            return True  # Suggest capturing learnings

        return False
```

---

## Cross-References

- **Part I**: Context and motivation for creative polynomial
- **CitizenPolynomial**: `impl/claude/agents/town/polynomial.py` (Right to Rest pattern)
- **Polynomial Agent Skill**: `docs/skills/polynomial-agent.md`
- **Muse Service**: `spec/services/muse.md`
- **AD-002**: `spec/principles/decisions/AD-002-polynomial.md` (Polynomial generalization)

---

*Synthesized: 2025-12-20 | The Right to Incubate | Emergence cannot be forced*
