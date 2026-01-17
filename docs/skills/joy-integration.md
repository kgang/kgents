# Joy Integration

> *"Joy is not a scalar metric to maximize. Joy is a behavioral pattern that composes."*

This skill teaches how to detect, calibrate, and preserve joy across different domains without killing the vibe.

---

## Overview: Joy as First-Class Citizen

Joy in kgents is **inferred, not interrogated**. The system never asks "was that joyful?" It observes behavioral signals and responds accordingly.

### The Joy Loop

```
SENSE → MARK → TREND → ANALYZE → DETECT → DIVERGE → LEARN
   │       │       │        │         │         │        │
   │       │       │        │         │         │        └─ Refine taste profile
   │       │       │        │         │         └─ Offer tangent if flatline
   │       │       │        │         └─ Spot significant shifts
   │       │       │        └─ Correlate triggers with dimensions
   │       │       └─ Track joy over time
   │       └─ Capture behavioral signals as deltas
   └─ Observe session length, exploration, language
```

---

## The Three Joy Dimensions

Joy is not a single number. It decomposes into three orthogonal dimensions:

| Dimension | Question | Positive Signal | Negative Signal |
|-----------|----------|-----------------|-----------------|
| **WARMTH** | "Collaboration or transaction?" | Personal language, "we", initiative | Short responses, "just do X" |
| **SURPRISE** | "Discovery or predictability?" | Tangent exploration, "what else?" | Immediate task completion |
| **FLOW** | "Time disappearing or dragging?" | Session length increases, quick response | Frequent clock-checking, abandonment |

### The Joy Manifold

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

---

## Domain-Specific Calibration

Different domains weight joy dimensions differently. **A productivity tool should feel lighter than a to-do list. A creative tool should prioritize discovery over QA.**

### The Four Domain Profiles

| Domain | Primary Joy | Secondary Joy | Qualitative Test | Galois Target |
|--------|-------------|---------------|------------------|---------------|
| **Productivity** | FLOW | WARMTH | "Lighter than a to-do list" | L < 0.15 |
| **Consumer** | WARMTH | FLOW | "Planning feels like narrative design" | L < 0.15 |
| **Creative** | SURPRISE | FLOW | "Discovery over QA" | L < 0.20 |
| **Gaming** | FLOW | SURPRISE | "Witnessed without drag" | L < 0.18 |

### Calibration Weights

```python
from enum import Enum
from dataclasses import dataclass


class JoyDomain(Enum):
    PRODUCTIVITY = "productivity"   # trail-to-crystal
    CONSUMER = "consumer"           # disney-portal
    CREATIVE = "creative"           # rap-coach, sprite-procedural
    GAMING = "gaming"               # wasm-survivors


@dataclass
class JoyCalibration:
    """Domain-specific joy calibration."""
    domain: JoyDomain
    warmth_weight: float
    surprise_weight: float
    flow_weight: float
    primary_threshold: float  # Must achieve this on primary dimension


DOMAIN_CALIBRATIONS = {
    JoyDomain.PRODUCTIVITY: JoyCalibration(
        domain=JoyDomain.PRODUCTIVITY,
        warmth_weight=0.3,
        surprise_weight=0.2,
        flow_weight=0.5,  # PRIMARY
        primary_threshold=0.6,  # Must feel lighter than a to-do list
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
    JoyDomain.GAMING: JoyCalibration(
        domain=JoyDomain.GAMING,
        warmth_weight=0.1,
        surprise_weight=0.3,
        flow_weight=0.6,  # PRIMARY
        primary_threshold=0.7,  # Time must disappear during runs
    ),
}
```

### Pilot-Specific Assertions

| Pilot | Domain | Assertion | Joy Test |
|-------|--------|-----------|----------|
| trail-to-crystal | Productivity | "Witnessing accelerates, not slows" | FLOW score after crystal > before |
| disney-portal | Consumer | "Planning as narrative not spreadsheet" | WARMTH during planning >= 0.6 |
| rap-coach | Creative | "Courage doesn't cost points" | SURPRISE preserved on risky takes |
| sprite-procedural | Creative | "Discovery over QA" | SURPRISE on mutation viewing >= 0.5 |
| wasm-survivors | Gaming | "Witnessed without drag" | FLOW during run >= 0.7 |

---

## Behavioral Signal Detection

Joy is inferred from behavioral signals, never directly asked.

### Positive Signals (Joy Present)

| Signal | Dimension | Detection Method |
|--------|-----------|------------------|
| Session length increases | FLOW | Compare to baseline |
| User explores tangents | SURPRISE | Track off-topic queries |
| Responses get longer, more personal | WARMTH | Sentiment + length analysis |
| User asks "what else?" or "tell me more" | SURPRISE | Pattern matching |
| User says "actually, let's..." | FLOW | Initiative detection |
| User quotes something back | WARMTH | Echo detection |

### Negative Signals (Joy Absent)

| Signal | Dimension | Detection Method |
|--------|-----------|------------------|
| Short, transactional responses | WARMTH | Length + sentiment |
| Immediate task completion, no exploration | SURPRISE | Session pattern |
| Frequent "just do X" commands | FLOW | Command pattern |
| "Never mind" or topic abandonment | All | Explicit detection |
| Time between messages increases | FLOW | Timing analysis |

### Implementation Pattern

```python
from dataclasses import dataclass


@dataclass
class SessionSignals:
    """Behavioral signals for joy inference."""
    message_count: int
    avg_message_length: float
    tangent_count: int           # Off-topic explorations
    what_else_count: int         # Curiosity signals
    initiative_phrases: int      # "let's", "we could", "what if"
    abandonment_count: int
    avg_response_time_ms: float
    session_duration_minutes: float

    def infer_warmth(self, baseline: "SessionSignals") -> float:
        """Infer warmth from signals (0-1)."""
        length_ratio = self.avg_message_length / max(baseline.avg_message_length, 1)
        initiative_ratio = self.initiative_phrases / max(self.message_count, 1)
        return min(1.0, (length_ratio * 0.5 + initiative_ratio * 0.5))

    def infer_surprise(self, baseline: "SessionSignals") -> float:
        """Infer surprise from signals (0-1)."""
        tangent_ratio = self.tangent_count / max(self.message_count, 1)
        curiosity_ratio = self.what_else_count / max(self.message_count, 1)
        return min(1.0, (tangent_ratio * 0.5 + curiosity_ratio * 0.5))

    def infer_flow(self, baseline: "SessionSignals") -> float:
        """Infer flow from signals (0-1)."""
        # Lower response time = better flow
        response_ratio = baseline.avg_response_time_ms / max(self.avg_response_time_ms, 1)
        # Fewer abandonments = better flow
        abandon_ratio = 1 - (self.abandonment_count / max(self.message_count, 1))
        return min(1.0, (response_ratio * 0.5 + abandon_ratio * 0.5))
```

---

## Joy Deltas (Not Absolute Ratings)

Instead of rating joy, capture **joy deltas** -- inflection points where something shifted.

### Why Deltas?

1. **No performance pressure** -- Not asking "was that joyful?" (which invites performing)
2. **Captures transitions** -- Joy is not static; it's about shifts
3. **Lightweight** -- A delta is a single moment, not a session review
4. **Actionable** -- Can correlate triggers with dimensions

### JoyDelta Structure

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
    session_id: str


# Example deltas:
JoyDelta(
    moment="exploring axiom graph",
    dimension="surprise",
    direction="up",
    intensity=0.7,
    trigger="discovered unexpected connection"
)

JoyDelta(
    moment="filling in metadata",
    dimension="flow",
    direction="down",
    intensity=0.4,
    trigger="too many required fields"
)
```

---

## Joy Principles

### Core Principles

1. **Joy is inferred, not interrogated** -- Never ask "was that joyful?"
2. **Joy composes** -- `session_joy >> crystal_joy = day_joy`
3. **Joy is domain-weighted** -- Productivity joy != creative joy
4. **Joy and efficiency are NOT commutative** -- Order matters
5. **Capture joy BEFORE compression** -- Otherwise it gets dropped

### Galois Loss Estimates

Different joy patterns have different Galois losses:

| Joy Pattern | Galois Loss | Evidence | Behavioral Signature |
|-------------|-------------|----------|---------------------|
| **Authentic Joy** | L ~ 0.1 | Stable under restructuring | Returns, explores freely, language warms |
| **Sterile Efficiency** | L ~ 0.6 | Brittle, drifts with context | Short responses, transactional |
| **Hustle Theater** | L ~ 0.9 | Contradicts under examination | Performs productivity, dreads system |

**JOY_INDUCING principle Galois loss: ~0.12** (validated in constitutional scoring)

### Joy Composition Laws

| Law | Statement | Implication |
|-----|-----------|-------------|
| **Joy >> Witness = Witness** | Joy doesn't block witnessing | Joyful moments are captured |
| **Compression >> Joy != Joy >> Compression** | Order matters | Capture joy before compressing |
| **Joy x Ethics = Joy** | Joy within bounds | Ethics is a floor, not a tradeoff |
| **Joy x Domain = Domain_Joy** | Joy is domain-weighted | Calibrate by context |

---

## Divergence Invitation

When joy flatlines, the system can offer a **divergence invitation** -- but gently.

### Rules for Not Being Annoying

1. **Offer, not insist** -- User can dismiss with zero friction
2. **Be rare** -- Once per session maximum
3. **Be earned** -- Only after clear low-joy signals (2+ sessions)
4. **Be honest** -- "I noticed X, I'm curious if Y" not "studies show..."
5. **Be optional** -- User can disable entirely

### Example Invitation

```python
@dataclass
class DivergenceInvitation:
    """An invitation to break routine."""
    observation: str   # What we noticed
    options: list[str] # What we're offering
    dismissible: bool = True


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

### When to Offer

```python
class DivergenceProtocol:
    """Protocol for offering divergence invitations."""
    MIN_SESSIONS_FOR_DETECTION = 2
    MAX_INVITATIONS_PER_SESSION = 1
    COOLDOWN_HOURS = 24

    def should_offer(self, joy_trend: list[dict], session_count: int) -> bool:
        """Only offer if joy is declining over multiple sessions."""
        if session_count < self.MIN_SESSIONS_FOR_DETECTION:
            return False

        if len(joy_trend) < 2:
            return False

        # Check for declining joy trend
        recent_avg = sum(sum(s.values()) / 3 for s in joy_trend[-2:]) / 2
        earlier_avg = sum(sum(s.values()) / 3 for s in joy_trend[:-2]) / max(len(joy_trend) - 2, 1)

        # Joy declining by > 20%
        return recent_avg < earlier_avg * 0.8
```

---

## Sterility Detection

Rigor without joy becomes sterility. Detect it early.

### Sterility Signals

| Signal | Threshold | Action |
|--------|-----------|--------|
| Surprise ratio < 5% | 2+ sessions | Surface warning |
| No novel insight | > 7 days | Alert |
| High constitutional reward + low joy | Diverging trends | Something wrong |

### Sterility Detector

```python
from datetime import datetime, timedelta


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
```

---

## For Agents

### Detecting Joy Signals

When operating as an agent or subagent:

```python
def detect_joy_signals(conversation: list[dict]) -> dict[str, float]:
    """Analyze conversation for joy signals."""
    signals = SessionSignals(
        message_count=len([m for m in conversation if m["role"] == "user"]),
        avg_message_length=avg([len(m["content"]) for m in conversation if m["role"] == "user"]),
        tangent_count=count_tangents(conversation),
        what_else_count=count_pattern(conversation, r"what else|tell me more"),
        initiative_phrases=count_pattern(conversation, r"let's|we could|what if"),
        abandonment_count=count_pattern(conversation, r"never mind|forget it"),
        avg_response_time_ms=avg_response_time(conversation),
        session_duration_minutes=session_duration(conversation),
    )

    baseline = get_baseline_signals()  # From historical data

    return {
        "warmth": signals.infer_warmth(baseline),
        "surprise": signals.infer_surprise(baseline),
        "flow": signals.infer_flow(baseline),
    }
```

### Calibrating Responses by Domain

```python
def calibrate_response(response: str, domain: JoyDomain) -> str:
    """Adjust response style based on domain joy profile."""
    calibration = DOMAIN_CALIBRATIONS[domain]

    if calibration.domain == JoyDomain.PRODUCTIVITY:
        # FLOW primary: keep it crisp, don't add drag
        return trim_ceremony(response)

    elif calibration.domain == JoyDomain.CONSUMER:
        # WARMTH primary: add collaborative framing
        return add_warmth(response)

    elif calibration.domain == JoyDomain.CREATIVE:
        # SURPRISE primary: leave room for tangents
        return add_invitation(response)

    elif calibration.domain == JoyDomain.GAMING:
        # FLOW primary: minimize interruption
        return minimize_overhead(response)

    return response
```

### When to Prioritize Joy Over Correctness

Joy should NOT override correctness in these cases:
- Safety-critical decisions (ETHICAL floor)
- Irreversible actions
- Explicit user requests for accuracy

Joy CAN be prioritized when:
- Multiple correct approaches exist -- pick the more delightful one
- Presenting information -- warm framing over cold dumps
- Handling uncertainty -- honest "I'm not sure" over false confidence
- Creative tasks -- discovery over optimization

### Agent Protocol

```python
class JoyAwareAgent:
    """Agent that monitors and responds to joy signals."""

    async def before_response(self, context: dict) -> None:
        """Check joy state before generating response."""
        joy_state = detect_joy_signals(context["conversation"])

        # Surface warning if joy dropping
        if self.sterility_detector.check_sterility()[0]:
            await self.surface_sterility_warning()

        # Adjust response style
        self.response_style = self.calibrate_style(
            domain=context["domain"],
            joy_state=joy_state,
        )

    async def after_response(self, response: str, context: dict) -> None:
        """Record joy delta after interaction."""
        new_joy_state = detect_joy_signals(context["conversation"] + [response])

        for dimension in ["warmth", "surprise", "flow"]:
            old_val = self.last_joy_state.get(dimension, 0.5)
            new_val = new_joy_state[dimension]
            diff = new_val - old_val

            if abs(diff) > 0.2:  # Significant shift
                await self.record_joy_delta(
                    dimension=dimension,
                    direction="up" if diff > 0 else "down",
                    intensity=abs(diff),
                    trigger=self.identify_trigger(context),
                )

        self.last_joy_state = new_joy_state
```

---

## Warmth in the Surface

Category theory is cold. The insights should be warm.

| Cold (Avoid) | Warm (Prefer) |
|--------------|---------------|
| "Galois loss computed: 0.23" | "This holds together well -- only 23% semantic drift" |
| "Fixed point detected" | "Found an axiom candidate -- this one survives restructuring" |
| "Confidence: 0.67" | "I'm about two-thirds sure -- want to dig deeper?" |
| "Processing your document" | "Let's see what's in here together" |
| "Error: Invalid input" | "Hmm, that didn't work. What if we tried..." |

---

## Universal Delight Primitives

Five irreducible joy sources that appear across ALL domains:

| Primitive | What It Is | Example | Maps to JoyMode |
|-----------|------------|---------|-----------------|
| **Recognition** | Being seen for who you are | "You understood what I meant" | WARMTH |
| **Mastery** | Earned competence, not given | "I finally got it" | FLOW |
| **Closure** | Completing a meaningful arc | "The day is done" | FLOW |
| **Discovery** | Finding something unexpected | "I didn't know that!" | SURPRISE |
| **Connection** | Genuine collaboration | "We figured it out together" | WARMTH |

---

## Joy Law Schemas

Four law schemas extending constitutional governance:

| Schema | Pattern | Example |
|--------|---------|---------|
| **DELIGHT_PRESERVATION** | Peak moments protected from compression | High-joy moments cannot be dropped during crystallization |
| **STERILITY_ALERT** | Low surprise triggers warning | If surprise_count < threshold, surface it |
| **EXPLORATION_GATE** | Engagement unlocks features | Features unlock through curiosity, not paywalls |
| **WARMTH_REQUIREMENT** | Crystals must have warmth | Technical accuracy + emotional coldness = failure |

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Do This Instead |
|--------------|--------------|-----------------|
| Asking "was that helpful?" | Invites performance, not honesty | Infer from behavior |
| Optimizing for efficiency first | Kills joy before it starts | Efficiency >> Joy loses joy |
| Uniform calibration | Productivity != creativity | Calibrate by domain |
| Ignoring declining joy | Sterility creeps in | Monitor trends, offer divergence |
| Cold system messages | Creates distance | Transform to warm framing |
| Frequent interruptions | Breaks flow | Minimize overhead, especially in gaming/productivity |

---

## Quick Reference

### Calibration Lookup

```python
def get_calibration(domain: str) -> JoyCalibration:
    """Get joy calibration for domain."""
    domain_enum = JoyDomain(domain)
    return DOMAIN_CALIBRATIONS[domain_enum]
```

### Joy Score Calculation

```python
def compute_domain_joy(
    warmth: float,
    surprise: float,
    flow: float,
    domain: JoyDomain,
) -> tuple[float, bool]:
    """Compute domain-calibrated joy score.

    Returns (weighted_score, primary_passes).
    """
    cal = DOMAIN_CALIBRATIONS[domain]

    weighted = (
        warmth * cal.warmth_weight +
        surprise * cal.surprise_weight +
        flow * cal.flow_weight
    )

    # Check primary dimension
    match domain:
        case JoyDomain.PRODUCTIVITY | JoyDomain.GAMING:
            primary_passes = flow >= cal.primary_threshold
        case JoyDomain.CONSUMER:
            primary_passes = warmth >= cal.primary_threshold
        case JoyDomain.CREATIVE:
            primary_passes = surprise >= cal.primary_threshold

    return weighted, primary_passes
```

---

## See Also

- `plans/enlightened-synthesis/04-joy-integration.md` -- Full architecture specification
- `plans/enlightened-synthesis/00-master-synthesis.md` -- Seven pilots overview
- `docs/skills/witness-for-agents.md` -- How to capture joy deltas as marks
- `docs/skills/zero-seed-for-agents.md` -- Galois loss measurement
- `spec/principles/joy-inducing.md` -- Constitutional principle definition

---

*"Joy is not a feature. It's the sign that the garden is alive."*
