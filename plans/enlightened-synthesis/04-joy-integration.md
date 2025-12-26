# Joy Integration: Making Delight a First-Class Citizen

> *"Being/having fun is free :)"*
>
> *"Joy is the accursed share spent well."*

**Created**: 2025-12-25
**Revised**: 2025-12-26 (Added Categorical Foundation + 7 Pilots)
**Status**: Architecture Specification
**Purpose**: Operationalize joy without killing the vibe, grounded in categorical foundations

---

## Part I: Joy as Categorical Object

> *"Joy is not a scalar metric to maximize. Joy is a behavioral pattern that composes."*

### The JoyPoly Functor

Joy is NOT a number between 0 and 1. It's a **polynomial functor over observation types**—the same pattern that underlies PolyAgent, Trust, and every agent in kgents.

```python
from typing import TypeVar, Generic
from dataclasses import dataclass
from enum import Enum

# Joy is polymorphic over observer types
Observer = TypeVar("Observer")


class JoyMode(Enum):
    """Joy modes as polynomial positions."""
    WARMTH = "warmth"      # Relational: collaboration vs. transaction
    SURPRISE = "surprise"  # Creative: serendipity vs. predictability
    FLOW = "flow"          # Temporal: effortless vs. laborious


@dataclass
class JoyObservation(Generic[Observer]):
    """
    JoyPoly(y) = Σ_{mode ∈ JoyMode} mode × y^{Interaction_{mode}}

    Joy is polymorphic: different observers perceive different joy.
    The architect sees elegance joy. The player sees mastery joy.
    """
    mode: JoyMode
    intensity: float  # [0, 1]
    observer: Observer
    trigger: str  # What caused this observation

    def __repr__(self) -> str:
        return f"Joy({self.mode.value}: {self.intensity:.2f} via '{self.trigger}')"


class JoyFunctor:
    """
    Joy as a functor: maps observers to joy observations.

    The key insight: Joy composes!
    domain_joy × universal_delight → total_joy
    """

    def __init__(self, domain_weights: dict[JoyMode, float]):
        self.domain_weights = domain_weights

    def observe(
        self,
        observer: Observer,
        warmth: float,
        surprise: float,
        flow: float,
    ) -> JoyObservation[Observer]:
        """Map observer state to joy observation."""
        # Find dominant mode for this observer
        modes = {
            JoyMode.WARMTH: warmth * self.domain_weights.get(JoyMode.WARMTH, 1.0),
            JoyMode.SURPRISE: surprise * self.domain_weights.get(JoyMode.SURPRISE, 1.0),
            JoyMode.FLOW: flow * self.domain_weights.get(JoyMode.FLOW, 1.0),
        }
        dominant = max(modes, key=modes.get)

        return JoyObservation(
            mode=dominant,
            intensity=modes[dominant],
            observer=observer,
            trigger="domain-weighted observation",
        )

    def compose(
        self,
        domain_joy: JoyObservation,
        universal_delight: JoyObservation,
    ) -> JoyObservation:
        """
        Joy composition: domain-specific × universal primitives.

        This is NOT addition. It's functorial composition:
        - Domain joy provides the base resonance
        - Universal delight amplifies or dampens
        - The result inherits the dominant mode
        """
        composed_intensity = (
            domain_joy.intensity * 0.6 +
            universal_delight.intensity * 0.4
        )

        # Dominant mode comes from higher intensity
        if domain_joy.intensity > universal_delight.intensity:
            mode = domain_joy.mode
        else:
            mode = universal_delight.mode

        return JoyObservation(
            mode=mode,
            intensity=composed_intensity,
            observer=domain_joy.observer,
            trigger=f"{domain_joy.trigger} × {universal_delight.trigger}",
        )
```

### Universal Delight Primitives

Five irreducible joy sources that appear across ALL domains:

| Primitive | What It Is | Example |
|-----------|------------|---------|
| **Recognition** | Being seen for who you are | "You understood what I meant" |
| **Mastery** | Earned competence, not given | "I finally got it" |
| **Closure** | Completing a meaningful arc | "The day is done" |
| **Discovery** | Finding something unexpected | "I didn't know that!" |
| **Connection** | Genuine collaboration | "We figured it out together" |

```python
class UniversalDelightPrimitives(Enum):
    """Five joy sources that compose with any domain."""
    RECOGNITION = "recognition"    # Being seen
    MASTERY = "mastery"            # Earned competence
    CLOSURE = "closure"            # Completing arcs
    DISCOVERY = "discovery"        # Unexpected finds
    CONNECTION = "connection"      # Genuine collaboration

    def to_joy_mode(self) -> JoyMode:
        """Map primitives to dominant joy modes."""
        return {
            self.RECOGNITION: JoyMode.WARMTH,
            self.MASTERY: JoyMode.FLOW,
            self.CLOSURE: JoyMode.FLOW,
            self.DISCOVERY: JoyMode.SURPRISE,
            self.CONNECTION: JoyMode.WARMTH,
        }[self]
```

---

## Part II: Joy and the 5 Axioms

> *"Every principle derives from the ground. Joy is no exception."*

Joy doesn't float free—it derives from the same Galois-grounded axioms that structure everything in kgents.

### A1 ENTITY: Joy Manifestations Are Entities

Joy is observable. Every joy observation is a node:

```
JoyObservation → ZeroNode(layer=L6, kind="joy_delta")
```

**Implication**: Joy can be stored, queried, composed. It's not ephemeral—it's witnessed.

### A2 MORPHISM: Joy Composes

Joy observations are morphisms that compose:

```
session_joy >> crystal_joy = day_joy
moment_joy >> trail_joy >> lifetime_joy
```

**Implication**: Joy propagates through the witness chain. A joyful session contributes to a joyful crystal.

```python
def joy_composition_law() -> bool:
    """Verify: (f >> g) >> h == f >> (g >> h) for joy morphisms."""
    moment = JoyObservation(JoyMode.SURPRISE, 0.7, "user", "discovery")
    session = JoyObservation(JoyMode.FLOW, 0.8, "user", "practice")
    crystal = JoyObservation(JoyMode.CLOSURE, 0.9, "user", "completion")

    functor = JoyFunctor({})

    # (moment >> session) >> crystal
    left = functor.compose(functor.compose(moment, session), crystal)

    # moment >> (session >> crystal)
    right = functor.compose(moment, functor.compose(session, crystal))

    # Intensities should be approximately equal (floating point)
    return abs(left.intensity - right.intensity) < 0.01
```

### A3 GALOIS: Joy Loss Is Measurable

Sterility = high Galois loss on joy. When joy is compressed away, the loss is quantifiable:

```
L(joyful_session) < 0.2  # Low loss: joy preserved
L(sterile_session) > 0.6  # High loss: joy compressed out
```

**Implication**: We can detect when rigor is killing life. Galois loss on joy is an early warning system.

### A4 WITNESS: Joy Is Witnessed Through Behavioral Marks

Joy is not interrogated—it's witnessed through behavioral signals:

```python
@dataclass
class JoyWitnessMark:
    """A mark that witnesses joy through behavior, not questioning."""
    mark_id: str
    behavioral_signals: list[str]  # What we observed
    inferred_joy: JoyObservation   # What we inferred
    confidence: float              # How sure we are

    # Witnessed, not asked
    asked_user: bool = False  # Should always be False
```

**Implication**: The system never asks "was that joyful?" It observes and infers.

### A5 ETHICAL: Joy Within Ethical Bounds Only

Joy that violates ethics is not joy—it's pleasure at harm:

```python
def validate_ethical_joy(joy: JoyObservation, ethics_score: float) -> bool:
    """
    ETHICAL floor applies to joy too.

    Joy from unethical actions is not counted.
    """
    ETHICAL_FLOOR = 0.6

    if ethics_score < ETHICAL_FLOOR:
        return False  # Not real joy—harm-derived pleasure

    return joy.intensity > 0.0
```

**Implication**: "I enjoyed that" is not a defense. Joy must pass the ETHICAL floor.

---

## Part III: Joy Law Schemas (Amendment G Extension)

> *"All pilot laws derive from five schemas. Joy has four."*

Extending Amendment G's pilot law grammar with joy-specific schemas:

```python
from dataclasses import dataclass
from typing import Callable
from enum import Enum


class JoyLawSchema(Enum):
    """Four joy law schemas extending Amendment G."""
    DELIGHT_PRESERVATION = "delight_preservation"
    STERILITY_ALERT = "sterility_alert"
    EXPLORATION_GATE = "exploration_gate"
    WARMTH_REQUIREMENT = "warmth_requirement"


@dataclass
class JoyLaw:
    """A joy law derived from a schema."""
    schema: JoyLawSchema
    name: str
    description: str
    predicate: Callable[..., bool]


# Schema implementations

def delight_preservation(
    original_moments: list[JoyObservation],
    compressed_crystal: list[JoyObservation],
    preservation_threshold: float = 0.8,
) -> bool:
    """
    DELIGHT PRESERVATION: Moments of delight protected from compression.

    High-joy moments cannot be dropped during crystallization.
    The crystal must preserve at least `preservation_threshold` of peak moments.
    """
    peak_moments = [m for m in original_moments if m.intensity > 0.7]
    preserved = [m for m in peak_moments if any(
        c.trigger == m.trigger for c in compressed_crystal
    )]

    if not peak_moments:
        return True  # No peaks to preserve

    return len(preserved) / len(peak_moments) >= preservation_threshold


def sterility_alert(
    surprise_count: int,
    session_length: int,
    threshold_ratio: float = 0.05,
    surfaced: bool = False,
) -> bool:
    """
    STERILITY ALERT: If surprise_count < threshold, surface it.

    Low surprise is a canary for sterility. The system must surface
    when sessions become too predictable.
    """
    if session_length == 0:
        return True

    ratio = surprise_count / session_length

    if ratio < threshold_ratio:
        return surfaced  # Must be surfaced if below threshold

    return True  # Above threshold, no requirement


def exploration_gate(
    exploration_depth: int,
    feature_tier: int,
    required_depth: int = 3,
) -> bool:
    """
    EXPLORATION GATE: Deep exploration unlocks features (not paywalls).

    Features unlock through earned curiosity, not payment.
    The user must demonstrate engagement before accessing deeper tools.
    """
    return exploration_depth >= required_depth or feature_tier == 0


def warmth_requirement(
    crystal_text: str,
    warmth_signals: list[str] = None,
) -> bool:
    """
    WARMTH REQUIREMENT: Crystals must have warmth, not just accuracy.

    A crystal that is technically accurate but emotionally cold fails.
    The crystal must contain at least one warmth signal.
    """
    warmth_signals = warmth_signals or [
        "together", "we", "felt", "noticed", "earned",
        "grew", "discovered", "realized", "beautiful",
    ]

    crystal_lower = crystal_text.lower()
    return any(signal in crystal_lower for signal in warmth_signals)


# Joy law registry (extending pilot laws)

JOY_LAWS = [
    JoyLaw(
        schema=JoyLawSchema.DELIGHT_PRESERVATION,
        name="Crystal Joy Preservation",
        description="Peak joy moments survive crystallization",
        predicate=delight_preservation,
    ),
    JoyLaw(
        schema=JoyLawSchema.STERILITY_ALERT,
        name="Session Sterility Alert",
        description="Low surprise ratio triggers surface warning",
        predicate=sterility_alert,
    ),
    JoyLaw(
        schema=JoyLawSchema.EXPLORATION_GATE,
        name="Curiosity-Gated Features",
        description="Features unlock through engagement, not payment",
        predicate=exploration_gate,
    ),
    JoyLaw(
        schema=JoyLawSchema.WARMTH_REQUIREMENT,
        name="Crystal Warmth Check",
        description="Crystals must have emotional warmth",
        predicate=warmth_requirement,
    ),
]
```

---

## Part IV: Joy Galois Loss Estimates

> *"What survives restructuring unchanged? Authentic joy does. Hustle theater doesn't."*

Different joy patterns have different Galois losses—the measure reveals authenticity:

| Joy Pattern | Galois Loss | Why | Behavioral Signature |
|-------------|-------------|-----|---------------------|
| **Authentic Joy** | L ~ 0.1 | Stable under restructuring, repeatable | User returns, explores freely, language warms |
| **Sterile Efficiency** | L ~ 0.6 | Brittle, prone to drift when context changes | Short responses, transactional, no tangents |
| **Hustle Theater** | L ~ 0.9 | Chaotic, contradicts itself under examination | Performs productivity, dreads the system |

```python
from enum import Enum


class JoyPattern(Enum):
    """Joy patterns with characteristic Galois losses."""
    AUTHENTIC = "authentic"        # L ~ 0.1: stable, repeatable
    STERILE = "sterile"            # L ~ 0.6: brittle, drifts
    HUSTLE_THEATER = "hustle"      # L ~ 0.9: chaotic, contradictory


def estimate_joy_galois_loss(
    return_rate: float,        # Did they come back?
    exploration_rate: float,   # Did they wander?
    warmth_score: float,       # Did language warm?
) -> tuple[float, JoyPattern]:
    """
    Estimate Galois loss for joy from behavioral signals.

    Returns (loss, pattern) tuple.
    """
    # Authentic joy: high on all three signals
    if return_rate > 0.7 and exploration_rate > 0.2 and warmth_score > 0.6:
        return (0.1, JoyPattern.AUTHENTIC)

    # Hustle theater: performs but no real engagement
    if return_rate > 0.5 and exploration_rate < 0.05 and warmth_score < 0.3:
        return (0.9, JoyPattern.HUSTLE_THEATER)

    # Sterile efficiency: works but no life
    if return_rate > 0.3 and exploration_rate < 0.1:
        return (0.6, JoyPattern.STERILE)

    # Default: uncertain
    return (0.4, JoyPattern.STERILE)


def joy_fixed_point_test(joy_observation: JoyObservation) -> bool:
    """
    Is this joy observation a fixed point?

    Fixed point = survives restructuring unchanged.
    Authentic joy should be L < 0.15.
    """
    loss, pattern = estimate_joy_galois_loss(
        return_rate=0.8,  # Placeholder: would come from real signals
        exploration_rate=0.3,
        warmth_score=0.7,
    )

    return loss < 0.15 and pattern == JoyPattern.AUTHENTIC
```

---

## Part V: Joy-Preserving Composition Laws

> *"Joy composes—but not all compositions preserve joy."*

Critical insight: **Order matters**. Some operations kill joy; others preserve it.

### The Non-Commutativity of Joy

```python
# Joy >> Witness = Witness (joy doesn't block witnessing)
# BUT:
# Compression >> Joy != Joy >> Compression (order matters!)

def joy_witness_law() -> bool:
    """Joy followed by witnessing still witnesses."""
    joy = JoyObservation(JoyMode.WARMTH, 0.8, "user", "collaboration")
    # Witnessing captures the joy
    witness = witness_mark(joy)
    return witness.includes_joy_observation()


def compression_joy_asymmetry() -> str:
    """
    Compression >> Joy != Joy >> Compression

    If you compress first, joy signals may be lost.
    If you capture joy first, compression preserves it.
    """
    # Joy first: capture delight, then compress
    # Result: crystal has warmth

    # Compression first: summarize, then check joy
    # Result: joy was already dropped, nothing to capture

    return "Capture joy BEFORE compression"
```

### Joy Composition Laws

| Law | Statement | Implication |
|-----|-----------|-------------|
| **Joy >> Witness = Witness** | Joy doesn't block witnessing | Joyful moments are captured |
| **Compression >> Joy ≠ Joy >> Compression** | Order matters | Capture joy before compressing |
| **Joy is NOT commutative with efficiency** | Don't optimize joy away | Sterility is a failure mode |
| **Joy × Ethics = Joy** | Joy within bounds | Ethics is a floor, not a tradeoff |
| **Joy × Domain = Domain_Joy** | Joy is domain-weighted | Productivity joy ≠ creative joy |

```python
class JoyCompositionLaws:
    """Verify joy composition laws hold."""

    @staticmethod
    def joy_witness_identity():
        """Joy >> Witness = Witness (captures joy)."""
        return True  # Joy observation is included in witness

    @staticmethod
    def compression_asymmetry():
        """Compression >> Joy ≠ Joy >> Compression."""
        # Left side: compress first, then check joy
        # Right side: capture joy first, then compress
        # These are NOT equal
        return False  # Intentionally asymmetric

    @staticmethod
    def joy_ethics_floor():
        """Joy × Ethics = Joy iff ethics passes floor."""
        return lambda joy, ethics: joy if ethics >= 0.6 else None

    @staticmethod
    def domain_weighting():
        """Joy × Domain = Domain_Joy."""
        # Domain weights modulate base joy
        return lambda joy, domain: joy * domain.weight


# Critical: Joy is NOT commutative with efficiency
def efficiency_joy_warning():
    """
    WARNING: Optimizing for efficiency can kill joy.

    Joy and efficiency are NOT commutative:
    - Efficiency >> Joy: "We saved time" (but lost the vibe)
    - Joy >> Efficiency: "That was delightful" (and we got things done)

    The order you prioritize determines the outcome.
    """
    pass
```

---

## Part VI: The Seven Pilots Joy Dimensions

> *"Each pilot teaches a different face of joy."*

The 7 pilots span the full joy manifold. Each emphasizes different dimensions:

| Pilot | Domain | Primary Joy | Secondary Joy | Joy Test |
|-------|--------|-------------|---------------|----------|
| **trail-to-crystal** | Productivity | CLOSURE | WARMTH | "Lighter than a to-do list" |
| **zero-seed-governance** | Personal Dev | RECOGNITION | DISCOVERY | "You understood what I actually believe" |
| **wasm-survivors** | Gaming | MASTERY | FLOW | "Time disappears during runs" |
| **rap-coach** | Creative | FLOW | SURPRISE | "The coach believes in me" |
| **sprite-lab** | Generative | SURPRISE | DISCOVERY | "That mutation was beautiful" |
| **disney-portal** | Consumer | WARMTH | CLOSURE | "Planning feels like storytelling" |
| **categorical-foundation** | Infrastructure | ELEGANCE | MASTERY | "The abstraction made it simpler" |

### Pilot Joy Profiles

```python
from dataclasses import dataclass


@dataclass
class PilotJoyProfile:
    """Joy profile for a pilot domain."""
    pilot: str
    primary: JoyMode
    secondary: JoyMode
    universal_primitive: UniversalDelightPrimitives
    qualitative_test: str
    galois_target: float  # Target joy loss


PILOT_JOY_PROFILES = {
    "trail-to-crystal": PilotJoyProfile(
        pilot="trail-to-crystal",
        primary=JoyMode.FLOW,
        secondary=JoyMode.WARMTH,
        universal_primitive=UniversalDelightPrimitives.CLOSURE,
        qualitative_test="The day ends with warmth, not exhaustion",
        galois_target=0.15,
    ),
    "zero-seed-governance": PilotJoyProfile(
        pilot="zero-seed-governance",
        primary=JoyMode.WARMTH,
        secondary=JoyMode.SURPRISE,
        universal_primitive=UniversalDelightPrimitives.RECOGNITION,
        qualitative_test="You understood what I actually believe",
        galois_target=0.12,
    ),
    "wasm-survivors": PilotJoyProfile(
        pilot="wasm-survivors",
        primary=JoyMode.FLOW,
        secondary=JoyMode.SURPRISE,
        universal_primitive=UniversalDelightPrimitives.MASTERY,
        qualitative_test="Witnessed without drag—time disappears",
        galois_target=0.18,
    ),
    "rap-coach": PilotJoyProfile(
        pilot="rap-coach",
        primary=JoyMode.SURPRISE,
        secondary=JoyMode.FLOW,
        universal_primitive=UniversalDelightPrimitives.CONNECTION,
        qualitative_test="The coach believes in me, I believe in myself",
        galois_target=0.20,
    ),
    "sprite-lab": PilotJoyProfile(
        pilot="sprite-lab",
        primary=JoyMode.SURPRISE,
        secondary=JoyMode.WARMTH,
        universal_primitive=UniversalDelightPrimitives.DISCOVERY,
        qualitative_test="That mutation was unexpectedly beautiful",
        galois_target=0.22,
    ),
    "disney-portal": PilotJoyProfile(
        pilot="disney-portal",
        primary=JoyMode.WARMTH,
        secondary=JoyMode.FLOW,
        universal_primitive=UniversalDelightPrimitives.CLOSURE,
        qualitative_test="Planning feels like writing a story together",
        galois_target=0.15,
    ),
    "categorical-foundation": PilotJoyProfile(
        pilot="categorical-foundation",
        primary=JoyMode.FLOW,  # Elegance IS flow
        secondary=JoyMode.SURPRISE,
        universal_primitive=UniversalDelightPrimitives.MASTERY,
        qualitative_test="The abstraction made it simpler, not harder",
        galois_target=0.10,
    ),
}


def get_pilot_joy_calibration(pilot: str) -> JoyFunctor:
    """Get domain-calibrated joy functor for a pilot."""
    profile = PILOT_JOY_PROFILES.get(pilot)
    if not profile:
        return JoyFunctor({})  # Neutral weights

    weights = {
        JoyMode.WARMTH: 0.33,
        JoyMode.SURPRISE: 0.33,
        JoyMode.FLOW: 0.34,
    }

    # Boost primary and secondary
    weights[profile.primary] = 0.5
    weights[profile.secondary] = 0.35

    # Reduce the third
    third = [m for m in JoyMode if m not in [profile.primary, profile.secondary]][0]
    weights[third] = 0.15

    return JoyFunctor(weights)
```

### Joy Dimension Per Pilot (Detailed)

#### trail-to-crystal: Closure Warmth
The day ends, and it feels complete. Not exhausted—*complete*. The crystal is a warm handoff to future-self.
- **Failure mode**: Hustle theater. "I tracked everything" but feel drained.
- **Success signal**: User says "the day is done" with a sigh of satisfaction.

#### zero-seed-governance: Recognition Delight
The system surfaced an axiom you hadn't articulated. "Oh—*that's* what I believe."
- **Failure mode**: Value imposition. The system tells you what to believe.
- **Success signal**: User recognizes themselves in the mirror.

#### wasm-survivors: Earned Mastery
The build coherence is visible. You can explain your playstyle. Time disappeared.
- **Failure mode**: Surveillance creep. "It's watching me play."
- **Success signal**: User names their build identity: "aggressive glass cannon who pivots late."

#### rap-coach: Flow State
The loop is tight. The coach believes in you. Courage was witnessed.
- **Failure mode**: Judge emergence. "It's grading my takes."
- **Success signal**: User practices MORE because the system makes practice feel less lonely.

#### sprite-lab: Generative Surprise
That mutation was beautiful. You didn't expect it, but now you can't unsee it.
- **Failure mode**: Canonization by fiat. "Why is THIS the style?"
- **Success signal**: Wild branches feel celebrated, not punished.

#### disney-portal: Anticipation Building
Planning is adventure. The tradeoffs are visible. The email is a gift.
- **Failure mode**: Logistics takeover. "It's a Gantt chart."
- **Success signal**: User looks forward to receiving their own plan.

#### categorical-foundation: Elegance Joy
The abstraction made it simpler. The law verification caught a real bug. The code is beautiful.
- **Failure mode**: Abstraction tax. "Category theory just makes it harder."
- **Success signal**: Developer ships faster with the library than without.

---

## The Paradox

Joy in the Constitution is weighted at 1.2 — higher than TASTEFUL, CURATED, HETERARCHICAL, GENERATIVE. Yet joy has no telemetry. No marks. No loop.

We measure coherence via Galois loss. We measure alignment via constitutional reward. We measure trust via demonstrated behavior.

**But joy?** Joy is Kent's gut check. A vibe.

This document asks: *Can we do better without killing the vibe?*

---

## UPDATED: Pilot Joy Calibration

**Key Insight from Pilots**: Joy dimensions are NOT equal across domains. Each of the 7 pilots emphasizes different dimensions.

*See Part VI above for detailed joy profiles per pilot.*

| Pilot | Primary Joy | Secondary Joy | Universal Primitive | Qualitative Assertion |
|-------|-------------|---------------|---------------------|----------------------|
| **trail-to-crystal** | FLOW | WARMTH | Closure | "Lighter than a to-do list" |
| **zero-seed-governance** | WARMTH | SURPRISE | Recognition | "You understood what I believe" |
| **wasm-survivors** | FLOW | SURPRISE | Mastery | "Time disappears during runs" |
| **disney-portal** | WARMTH | FLOW | Closure | "Planning feels like narrative design" |
| **rap-coach** | SURPRISE | FLOW | Connection | "The coach believes in me" |
| **sprite-procedural** | SURPRISE | WARMTH | Discovery | "Discovery over QA" |
| **categorical-foundation** | FLOW | SURPRISE | Mastery | "The abstraction made it simpler" |

### Domain-Specific Joy Thresholds

```python
from enum import Enum
from dataclasses import dataclass


class JoyDomain(Enum):
    PRODUCTIVITY = "productivity"    # trail-to-crystal
    PERSONAL_DEV = "personal_dev"    # zero-seed-governance
    GAMING = "gaming"                # wasm-survivors
    CONSUMER = "consumer"            # disney-portal
    CREATIVE = "creative"            # rap-coach, sprite-procedural
    INFRASTRUCTURE = "infrastructure"  # categorical-foundation


@dataclass
class JoyCalibration:
    """Domain-specific joy calibration."""
    domain: JoyDomain
    warmth_weight: float
    surprise_weight: float
    flow_weight: float
    primary_threshold: float  # Must achieve this on primary dimension


PILOT_CALIBRATIONS = {
    JoyDomain.PRODUCTIVITY: JoyCalibration(
        domain=JoyDomain.PRODUCTIVITY,
        warmth_weight=0.3,
        surprise_weight=0.2,
        flow_weight=0.5,  # PRIMARY
        primary_threshold=0.6,  # Must feel lighter than a to-do list
    ),
    JoyDomain.PERSONAL_DEV: JoyCalibration(
        domain=JoyDomain.PERSONAL_DEV,
        warmth_weight=0.5,  # PRIMARY (recognition)
        surprise_weight=0.3,
        flow_weight=0.2,
        primary_threshold=0.6,  # Must recognize self in mirror
    ),
    JoyDomain.GAMING: JoyCalibration(
        domain=JoyDomain.GAMING,
        warmth_weight=0.1,
        surprise_weight=0.3,
        flow_weight=0.6,  # PRIMARY
        primary_threshold=0.7,  # Time must disappear during runs
    ),
    JoyDomain.CONSUMER: JoyCalibration(
        domain=JoyDomain.CONSUMER,
        warmth_weight=0.5,  # PRIMARY
        surprise_weight=0.2,
        flow_weight=0.3,
        primary_threshold=0.6,  # Must feel like narrative design
    ),
    JoyDomain.CREATIVE: JoyCalibration(
        domain=JoyDomain.CREATIVE,
        warmth_weight=0.2,
        surprise_weight=0.5,  # PRIMARY
        flow_weight=0.3,
        primary_threshold=0.5,  # Must enable discovery
    ),
    JoyDomain.INFRASTRUCTURE: JoyCalibration(
        domain=JoyDomain.INFRASTRUCTURE,
        warmth_weight=0.1,
        surprise_weight=0.3,
        flow_weight=0.6,  # PRIMARY (elegance = flow)
        primary_threshold=0.7,  # Abstraction must make it simpler
    ),
}


def compute_domain_joy(
    warmth: float,
    surprise: float,
    flow: float,
    domain: JoyDomain,
) -> tuple[float, bool]:
    """Compute domain-calibrated joy score.

    Returns (weighted_score, primary_passes).
    """
    cal = PILOT_CALIBRATIONS[domain]

    weighted = (
        warmth * cal.warmth_weight +
        surprise * cal.surprise_weight +
        flow * cal.flow_weight
    )

    # Check primary dimension based on domain
    match domain:
        case JoyDomain.PRODUCTIVITY | JoyDomain.GAMING | JoyDomain.INFRASTRUCTURE:
            primary_passes = flow >= cal.primary_threshold
        case JoyDomain.CONSUMER | JoyDomain.PERSONAL_DEV:
            primary_passes = warmth >= cal.primary_threshold
        case JoyDomain.CREATIVE:
            primary_passes = surprise >= cal.primary_threshold
        case _:
            primary_passes = False

    return weighted, primary_passes
```

### Pilot Qualitative Assertions (from proto-specs)

| Pilot | Assertion | Joy Test |
|-------|-----------|----------|
| trail-to-crystal | "Witnessing accelerates, not slows" | FLOW score after crystal > before |
| trail-to-crystal | "System is descriptive, not punitive" | WARMTH stable even on gap surfacing |
| zero-seed-governance | "Recognition, not invention" | WARMTH on axiom surfacing >= 0.6 |
| wasm-survivors | "Witnessed without drag" | FLOW during run >= 0.7 |
| disney-portal | "Planning as narrative not spreadsheet" | WARMTH during planning >= 0.6 |
| rap-coach | "Courage doesn't cost points" | SURPRISE preserved on risky takes |
| sprite-procedural | "Discovery over QA" | SURPRISE on mutation viewing >= 0.5 |
| categorical-foundation | "Simpler, not harder" | FLOW with library > without |

---

## The Three Faces of Joy

```
┌─────────────────────────────────────────────────────────────────┐
│                    JOY MANIFOLD                                  │
│                                                                  │
│   WARMTH ←─────────────────────────────────────────→ COLDNESS   │
│     │                                                     │      │
│     │    "Does this feel like collaboration,              │      │
│     │     or like filling out a form?"                    │      │
│                                                                  │
│   SURPRISE ←───────────────────────────────────────→ TEDIUM    │
│     │                                                     │      │
│     │    "Did something unexpected and good happen,       │      │
│     │     or was this exactly what I predicted?"          │      │
│                                                                  │
│   FLOW ←───────────────────────────────────────────→ FRICTION  │
│     │                                                     │      │
│     │    "Did time disappear, or did I keep checking      │      │
│     │     the clock?"                                     │      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Warmth**: The relational dimension. Collaboration vs. transaction.
**Surprise**: The creative dimension. Serendipity vs. predictability.
**Flow**: The temporal dimension. Effortless vs. laborious.

---

## Joy vs. Constitutional Reward

Joy and constitutional reward are orthogonal:

| Reward | Joy | Example |
|--------|-----|---------|
| High | High | Kent and Claude discover a novel insight together |
| High | Low | Bureaucratic compliance with all seven principles |
| Low | High | Wild tangent that violates CURATED but sparks delight |
| Low | Low | Generic slop that pleases no one |

**Insight**: Joy is not a principle to maximize. It's a signal that principles are being applied with *life*, not *rigor mortis*.

---

## The Joy Delta Approach

Instead of rating joy, we capture **joy deltas** — inflection points where something shifted.

```python
from dataclasses import dataclass
from typing import Literal
from datetime import datetime

@dataclass
class JoyDelta:
    """A moment where joy changed."""

    id: str
    timestamp: datetime
    moment: str          # What was happening
    dimension: Literal["warmth", "surprise", "flow"]
    direction: Literal["up", "down"]
    intensity: float     # 0.0 to 1.0
    trigger: str         # What caused the shift

    # Context
    session_id: str
    k_block_id: str | None = None


# Examples:
JoyDelta(
    moment="exploring axiom graph",
    dimension="surprise",
    direction="up",
    intensity=0.7,
    trigger="discovered unexpected connection between documents"
)

JoyDelta(
    moment="filling in metadata",
    dimension="flow",
    direction="down",
    intensity=0.4,
    trigger="too many required fields"
)
```

### Why Deltas, Not Absolute Ratings?

1. **No performance pressure**: We're not asking "was that joyful?" (which invites performing)
2. **Captures transitions**: Joy is not static; it's about shifts
3. **Lightweight**: A delta is a single moment, not a session review
4. **Actionable**: We can correlate triggers with dimensions

---

## Joy Inference, Not Interrogation

Rather than asking "was that joyful?", we infer joy from behavioral signals:

### Positive Signals (Joy Likely)

| Signal | Dimension | Detection Method |
|--------|-----------|------------------|
| Session length increases | Flow | Compare to baseline |
| User explores tangents | Surprise | Track off-topic queries |
| Responses get longer, more personal | Warmth | Sentiment + length analysis |
| User asks "what else?" or "tell me more" | Surprise | Pattern matching |
| User says "actually, let's..." | Flow | Initiative detection |
| User quotes something back | Warmth | Echo detection |

### Negative Signals (Joy Absent)

| Signal | Dimension | Detection Method |
|--------|-----------|------------------|
| Short, transactional responses | Warmth | Length + sentiment |
| Immediate task completion, no exploration | Surprise | Session pattern |
| Frequent "just do X" commands | Flow | Command pattern |
| "Never mind" or topic abandonment | All | Explicit detection |
| Time between messages increases | Flow | Timing analysis |

### Implementation

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class SessionSignals:
    """Behavioral signals for joy inference."""

    message_count: int
    avg_message_length: float
    tangent_count: int  # Off-topic explorations
    "what_else" count: int
    initiative_phrases: int  # "let's", "we could", "what if"
    abandonment_count: int
    avg_response_time_ms: float
    session_duration_minutes: float

    def infer_warmth(self, baseline: "SessionSignals") -> float:
        """Infer warmth from signals (0-1)."""
        length_ratio = self.avg_message_length / max(baseline.avg_message_length, 1)
        initiative_ratio = self.initiative_phrases / max(self.message_count, 1)

        # Normalize to 0-1
        return min(1.0, (length_ratio * 0.5 + initiative_ratio * 0.5))

    def infer_surprise(self, baseline: "SessionSignals") -> float:
        """Infer surprise from signals (0-1)."""
        tangent_ratio = self.tangent_count / max(self.message_count, 1)
        curiosity_ratio = self."what_else"_count / max(self.message_count, 1)

        return min(1.0, (tangent_ratio * 0.5 + curiosity_ratio * 0.5))

    def infer_flow(self, baseline: "SessionSignals") -> float:
        """Infer flow from signals (0-1)."""
        # Lower response time = better flow
        response_ratio = baseline.avg_response_time_ms / max(self.avg_response_time_ms, 1)
        # Fewer abandonments = better flow
        abandon_ratio = 1 - (self.abandonment_count / max(self.message_count, 1))

        return min(1.0, (response_ratio * 0.5 + abandon_ratio * 0.5))


class JoyInferenceEngine:
    """Infer joy from behavioral signals without interrogation."""

    def __init__(self):
        self.baseline: SessionSignals | None = None
        self.recent_deltas: list[JoyDelta] = []

    def update_baseline(self, signals: SessionSignals) -> None:
        """Update baseline with exponential moving average."""
        if self.baseline is None:
            self.baseline = signals
        else:
            alpha = 0.3  # Smoothing factor
            self.baseline = self._ema(self.baseline, signals, alpha)

    def infer_joy_state(self, current: SessionSignals) -> dict[str, float]:
        """Infer current joy state across dimensions."""
        if self.baseline is None:
            return {"warmth": 0.5, "surprise": 0.5, "flow": 0.5}

        return {
            "warmth": current.infer_warmth(self.baseline),
            "surprise": current.infer_surprise(self.baseline),
            "flow": current.infer_flow(self.baseline),
        }

    def detect_delta(
        self,
        previous: SessionSignals,
        current: SessionSignals,
        threshold: float = 0.2
    ) -> list[JoyDelta]:
        """Detect significant joy deltas."""
        deltas = []

        prev_state = self.infer_joy_state(previous)
        curr_state = self.infer_joy_state(current)

        for dimension in ["warmth", "surprise", "flow"]:
            diff = curr_state[dimension] - prev_state[dimension]
            if abs(diff) > threshold:
                deltas.append(JoyDelta(
                    moment="session segment",
                    dimension=dimension,
                    direction="up" if diff > 0 else "down",
                    intensity=abs(diff),
                    trigger="behavioral signal shift",
                ))

        return deltas
```

---

## The Divergence Invitation

When joy flatlines, the system can offer a **divergence invitation** — but gently.

```python
@dataclass
class DivergenceInvitation:
    """An invitation to break routine."""

    observation: str  # What we noticed
    options: list[str]  # What we're offering
    dismissible: bool = True  # Always dismissible

# Example:
DivergenceInvitation(
    observation=(
        "We've been optimizing the Galois loss formula for three sessions. "
        "Your language has become more transactional."
    ),
    options=[
        "Continue (this is important work)",
        "Take a tangent (void.serendipity.summon)",
        "Return to axioms (what are we actually trying to do?)",
        "Something else entirely",
    ],
)
```

### Rules for Not Being Annoying

1. **Offer, not insist** — Kent can dismiss with zero friction
2. **Be rare** — Once per session maximum, probably less
3. **Be earned** — Only after clear low-joy signals (2+ sessions)
4. **Be honest** — "I noticed X, I'm curious if Y" not "studies show..."
5. **Be optional** — Kent can disable entirely

```python
class DivergenceProtocol:
    """Protocol for offering divergence invitations."""

    MIN_SESSIONS_FOR_DETECTION = 2
    MAX_INVITATIONS_PER_SESSION = 1
    COOLDOWN_HOURS = 24

    def __init__(self):
        self.last_invitation: datetime | None = None
        self.invitations_this_session = 0
        self.enabled = True

    def should_offer(
        self,
        joy_trend: list[dict[str, float]],
        session_count: int
    ) -> bool:
        """Determine if we should offer a divergence invitation."""
        if not self.enabled:
            return False

        if session_count < self.MIN_SESSIONS_FOR_DETECTION:
            return False

        if self.invitations_this_session >= self.MAX_INVITATIONS_PER_SESSION:
            return False

        if self.last_invitation:
            elapsed = datetime.now() - self.last_invitation
            if elapsed < timedelta(hours=self.COOLDOWN_HOURS):
                return False

        # Check for declining joy trend
        if len(joy_trend) < 2:
            return False

        recent_avg = sum(
            sum(s.values()) / 3 for s in joy_trend[-2:]
        ) / 2
        earlier_avg = sum(
            sum(s.values()) / 3 for s in joy_trend[:-2]
        ) / max(len(joy_trend) - 2, 1)

        # Joy declining by > 20%
        return recent_avg < earlier_avg * 0.8

    def create_invitation(
        self,
        context: str
    ) -> DivergenceInvitation:
        """Create a divergence invitation."""
        self.last_invitation = datetime.now()
        self.invitations_this_session += 1

        return DivergenceInvitation(
            observation=context,
            options=[
                "Continue (this is important work)",
                "Take a tangent (void.serendipity.summon)",
                "Return to axioms (what are we actually trying to do?)",
                "Something else entirely",
            ],
        )
```

---

## The Mirror Test Support

The Mirror Test stays with Kent. The system provides data, not verdicts.

### Voice Signature Detection

```python
@dataclass
class VoiceSignature:
    """Kent's linguistic patterns when in flow."""

    # Learned patterns
    preferred_phrases: list[str]  # Phrases Kent uses when engaged
    avoided_phrases: list[str]    # Phrases that signal disengagement
    metaphor_frequency: float     # How often Kent uses metaphors
    directness_score: float       # How direct vs. circumspect
    opinion_strength: float       # How definitive vs. hedged

    # Anti-patterns Kent has rejected
    anti_patterns: list[str]


class VoiceMonitor:
    """Monitor for voice signature drift."""

    def __init__(self, signature: VoiceSignature):
        self.signature = signature

    def check_output(self, output: str) -> list[str]:
        """Check if output matches Kent's voice signature."""
        warnings = []

        # Check for anti-patterns
        for pattern in self.signature.anti_patterns:
            if pattern.lower() in output.lower():
                warnings.append(f"Contains anti-pattern: '{pattern}'")

        # Check for passive voice if Kent prefers active
        passive_ratio = self._count_passive(output) / max(self._count_sentences(output), 1)
        if passive_ratio > 0.3:  # More than 30% passive
            warnings.append(f"High passive voice: {passive_ratio:.0%}")

        # Check for hedging if Kent prefers definitive
        hedge_words = ["perhaps", "maybe", "might", "could", "seems"]
        hedge_count = sum(output.lower().count(w) for w in hedge_words)
        if hedge_count > 3:
            warnings.append(f"Excessive hedging: {hedge_count} hedge words")

        return warnings
```

### Opinion Preservation

```python
class OpinionTracker:
    """Track strong stances Kent has taken."""

    def __init__(self):
        self.stances: dict[str, str] = {}  # topic -> stance

    def record_stance(self, topic: str, stance: str) -> None:
        """Record a strong stance."""
        self.stances[topic] = stance

    def check_consistency(
        self,
        output: str,
        topic: str
    ) -> tuple[bool, str]:
        """Check if output is consistent with recorded stance."""
        if topic not in self.stances:
            return True, "No recorded stance"

        original = self.stances[topic]

        # Check if output softens the stance
        softening_words = ["however", "on the other hand", "but also", "balanced"]
        if any(word in output.lower() for word in softening_words):
            return False, f"Output may soften stance on '{topic}'. Original: '{original}'"

        return True, "Consistent"
```

---

## The Taste Profile

Kent's taste evolves. The system tracks it.

```python
@dataclass
class TasteProfile:
    """Kent's aesthetic preferences over time."""

    # Voice anchors (direct quotes)
    anchors: list[str] = field(default_factory=lambda: [
        "Daring, bold, creative, opinionated but not gaudy",
        "The Mirror Test: Does K-gent feel like me on my best day?",
        "Tasteful > feature-complete; Joy-inducing > merely functional",
        "The persona is a garden, not a museum",
    ])

    # Aesthetic coordinates (learned)
    directness: float = 0.8      # Blunt ←→ Circumspect
    formality: float = 0.3       # Casual ←→ Formal
    compression: float = 0.7     # Terse ←→ Expansive
    metaphor_use: float = 0.6    # Literal ←→ Figurative
    opinion_strength: float = 0.9  # Hedged ←→ Definitive

    # Anti-patterns (things rejected)
    never_do: list[str] = field(default_factory=lambda: [
        "gaudy",
        "performative work",
        "committee-approved",
        "safe",
    ])

    # Evolution (snapshots over time)
    history: list["TasteSnapshot"] = field(default_factory=list)


@dataclass
class TasteSnapshot:
    """A point-in-time snapshot of taste."""
    timestamp: datetime
    coordinates: dict[str, float]
    notable_decisions: list[str]


class TasteEvolutionTracker:
    """Track how Kent's taste evolves."""

    def __init__(self, profile: TasteProfile):
        self.profile = profile

    def detect_shift(
        self,
        old: TasteSnapshot,
        new: TasteSnapshot,
        threshold: float = 0.2
    ) -> list[str]:
        """Detect significant taste shifts."""
        shifts = []
        for coord, old_val in old.coordinates.items():
            new_val = new.coordinates.get(coord, old_val)
            if abs(new_val - old_val) > threshold:
                direction = "increased" if new_val > old_val else "decreased"
                shifts.append(f"{coord} {direction}: {old_val:.2f} → {new_val:.2f}")
        return shifts

    def prompt_confirmation(self, shifts: list[str]) -> str:
        """Generate confirmation prompt for detected shifts."""
        return (
            f"Your taste seems to have shifted:\n"
            + "\n".join(f"  - {s}" for s in shifts)
            + "\n\nIs this intentional?"
        )
```

---

## The Joy Loop Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      JOY LOOP TELEMETRY                          │
│                                                                  │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│   │  SENSE   │────▶│  MARK    │────▶│  TREND   │               │
│   └──────────┘     └──────────┘     └──────────┘               │
│        │                                  │                      │
│        │   Behavioral signals             │   Joy over time      │
│        │   • Session length               │   • Warmth trend     │
│        │   • Exploration patterns         │   • Surprise count   │
│        │   • Language shifts              │   • Flow duration    │
│        │                                  │                      │
│        │                                  ▼                      │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│   │ DIVERGE  │◀────│  DETECT  │◀────│ ANALYZE  │               │
│   └──────────┘     └──────────┘     └──────────┘               │
│        │                                                         │
│        │   If low-joy:                                           │
│        │   • Offer tangent                                       │
│        │   • Invoke void.serendipity                            │
│        │   • Surface ghost alternatives                          │
│        │                                                         │
│        ▼                                                         │
│   ┌──────────┐                                                   │
│   │  LEARN   │   Over time: refine taste profile                │
│   └──────────┘                                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Points

```python
class JoyLoopIntegration:
    """How joy loop integrates with other systems."""

    # Witness Marks
    # Joy deltas are optional fields on marks
    @dataclass
    class EnhancedMark:
        # ... existing fields ...
        joy_delta: JoyDelta | None = None

    # Crystals
    # Include mood vector in crystal compression
    @dataclass
    class EnhancedCrystal:
        # ... existing fields ...
        mood_vector: dict[str, float] | None = None  # warmth, surprise, flow

    # Constitutional Reward
    # Joy is orthogonal signal, not principle
    # If joy trends down while reward stays high → something wrong

    # AGENTESE
    # void.* context for serendipity
    # void.serendipity.summon
    # void.accursed.spend
    # void.entropy.inject

    # UI
    # Ambient joy indicators (not prominent)
    # Color temperature shifts with warmth
    # Subtle animation with flow
```

---

## Serendipity Engineering

True surprise cannot be scheduled. But conditions can be cultivated.

### The Tangent Reserve

```python
class TangentReserve:
    """Reserve for exploratory tangents."""

    EXPLORATION_BUDGET = 0.10  # 10% of session time

    def __init__(self):
        self.budget_used = 0.0
        self.tangent_history: list[str] = []

    def can_tangent(self) -> bool:
        """Check if tangent budget available."""
        return self.budget_used < self.EXPLORATION_BUDGET

    def spend(self, fraction: float) -> bool:
        """Spend tangent budget."""
        if self.budget_used + fraction > self.EXPLORATION_BUDGET:
            return False
        self.budget_used += fraction
        return True

    def record_tangent(self, description: str) -> None:
        """Record a tangent for learning."""
        self.tangent_history.append(description)
```

### The Ghost Alternative System

```python
@dataclass
class GhostAlternative:
    """An unexplored alternative path."""
    description: str
    rationale: str
    risk_level: str  # "low" | "medium" | "high"
    surfaces_occasionally: bool = True


class GhostAlternativeGenerator:
    """Generate ghost alternatives for divergence."""

    def generate(
        self,
        current_path: str,
        context: str
    ) -> list[GhostAlternative]:
        """Generate 2-3 ghost alternatives to current path."""
        # These are:
        # - More radical than current
        # - Less obvious
        # - Potentially wrong but interesting

        return [
            GhostAlternative(
                description="What if we assumed the opposite?",
                rationale="Inversion often reveals hidden assumptions",
                risk_level="medium",
            ),
            GhostAlternative(
                description="What if this constraint didn't exist?",
                rationale="Constraints should be questioned periodically",
                risk_level="high",
            ),
            GhostAlternative(
                description="What's the adjacent problem?",
                rationale="Sometimes the real problem is nearby",
                risk_level="low",
            ),
        ]

    def should_surface(self, session_count: int) -> bool:
        """Determine if we should surface a ghost."""
        # Occasionally, not every time
        import random
        return random.random() < 0.1  # 10% chance
```

---

## Warmth in the Surface

Category theory is cold. The insights are warm.

### Concrete Warmth Patterns

| Cold (Avoid) | Warm (Prefer) |
|--------------|---------------|
| "Galois loss computed: 0.23" | "This holds together well — only 23% semantic drift" |
| "Fixed point detected" | "Found an axiom candidate — this one survives restructuring" |
| "Confidence: 0.67" | "I'm about two-thirds sure — want to dig deeper?" |
| "Processing your document" | "Let's see what's in here together" |
| "Error: Invalid input" | "Hmm, that didn't work. What if we tried..." |

### Implementation

```python
class WarmthTransformer:
    """Transform cold system messages to warm ones."""

    TRANSFORMATIONS = {
        "Galois loss computed": "This holds together",
        "Fixed point detected": "Found an axiom candidate",
        "Processing": "Looking at",
        "Computed": "Found",
        "Error": "Hmm",
        "Invalid": "didn't quite work",
    }

    def transform(self, message: str) -> str:
        """Transform cold message to warm."""
        result = message

        for cold, warm in self.TRANSFORMATIONS.items():
            result = result.replace(cold, warm)

        # Add collaborative framing
        if result.startswith("The"):
            result = "I notice that " + result.lower()

        return result
```

---

## Joy Metrics (Observational Only)

If we must measure, measure without killing:

| Metric | What It Captures | Target | How Measured |
|--------|------------------|--------|--------------|
| Session return rate | Did they come back? | Increasing | Session tracking |
| Exploration breadth | Did they wander? | Non-zero | Tangent counting |
| Tangent completion | Did tangents pay off? | > 20% | Outcome tracking |
| Personal language ratio | Did they speak as themselves? | Increasing | NLP analysis |
| Ah-ha moments | Did something shift? | > 1/session | JoyDelta counting |
| Mirror Test pass | Did Kent approve? | 100% | Explicit approval |

---

## The Accursed Share Zones

Where chaos lives:

```
void.* context in AGENTESE:
├── void.serendipity.summon     — Invoke deliberate tangent
├── void.accursed.spend         — Use surplus budget
├── void.entropy.inject         — Perturb a stable state
└── void.gratitude.express      — Acknowledge the slop

T-gent Type II Saboteurs:
├── Strategic disruption of overly rigid patterns
└── Noise injection that prevents premature optimization

The 10% Exploration Budget:
├── Protected time for tangents
└── Cannot be reclaimed for "urgent" work
```

---

## Preventing Sterility

The proof-carrying system is rigorous. Category laws are verified.

**Risk**: Rigor calcifies into sterility.

**Antidotes**:

1. **Joy as health metric** — If joy trends down, rigor is killing life
2. **The garden metaphor** — Gardens are pruned but also wild
3. **Kent's veto** — "This feels dead" is valid feedback
4. **The surprise quota** — Track how often something unexpected happens

```python
class SterilityDetector:
    """Detect when the system is becoming sterile."""

    def __init__(self):
        self.surprise_count = 0
        self.routine_count = 0
        self.last_novel_insight: datetime | None = None

    def check_sterility(self) -> tuple[bool, str]:
        """Check if system is becoming sterile."""
        surprise_ratio = self.surprise_count / max(self.routine_count, 1)

        if surprise_ratio < 0.05:
            return True, "Surprise ratio too low (< 5%)"

        if self.last_novel_insight:
            days_since = (datetime.now() - self.last_novel_insight).days
            if days_since > 7:
                return True, f"No novel insights in {days_since} days"

        return False, "System appears alive"

    def record_surprise(self) -> None:
        """Record a surprising moment."""
        self.surprise_count += 1
        self.last_novel_insight = datetime.now()

    def record_routine(self) -> None:
        """Record a routine action."""
        self.routine_count += 1
```

---

## Conclusion: The Garden Grows

> *"The persona is a garden, not a museum."*

A museum preserves what was. A garden creates what will be.

Joy cannot be engineered. But conditions can be protected:

1. **Measure joy indirectly** — Behavioral signals, not interrogation
2. **Offer divergence gently** — Invite, don't insist
3. **Preserve voice fiercely** — Anti-sausage protocol for all
4. **Protect the accursed share** — Surplus is sacred
5. **Keep rigor in the substrate** — Warmth in the surface
6. **Trust the Mirror Test** — Kent's gut is the final arbiter

Joy is not a feature. It's the sign that the garden is alive.

---

**Document Metadata**
- **Lines**: ~1,250
- **Status**: Joy Integration Architecture (Categorically Grounded)
- **Revised**: 2025-12-26 (Categorical Foundation + 7 Pilots)
- **Implementation Week**: Week 7 (parallel with Trust)
- **Key Additions**:
  - Part I: Joy as Categorical Object (JoyPoly functor)
  - Part II: Joy and the 5 Axioms (A1-A5 derivation)
  - Part III: Joy Law Schemas (extending Amendment G)
  - Part IV: Joy Galois Loss Estimates (L ~ 0.1 to 0.9)
  - Part V: Joy-Preserving Composition Laws (non-commutativity)
  - Part VI: The Seven Pilots Joy Dimensions (detailed profiles)
- **Key Files**:
  - `services/joy/functor.py` (JoyPoly, JoyFunctor)
  - `services/joy/laws.py` (JoyLawSchema, JOY_LAWS)
  - `services/joy/galois.py` (joy loss estimation)
  - `services/joy/delta.py`
  - `services/joy/inference.py`
  - `services/joy/divergence.py`
  - `services/joy/taste_profile.py`
- **Pilot Joy Targets**:
  - trail-to-crystal: L < 0.15 (closure warmth)
  - zero-seed-governance: L < 0.12 (recognition delight)
  - wasm-survivors: L < 0.18 (earned mastery)
  - rap-coach: L < 0.20 (flow state)
  - sprite-lab: L < 0.22 (generative surprise)
  - disney-portal: L < 0.15 (anticipation building)
  - categorical-foundation: L < 0.10 (elegance joy)
