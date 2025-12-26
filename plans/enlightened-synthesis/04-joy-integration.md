# Joy Integration: Making Delight a First-Class Citizen

> *"Being/having fun is free :)"*
>
> *"Joy is the accursed share spent well."*

**Created**: 2025-12-25
**Revised**: 2025-12-26 (Added Pilot Joy Dimensions)
**Status**: Architecture Specification
**Purpose**: Operationalize joy without killing the vibe, calibrated per pilot domain

---

## The Paradox

Joy in the Constitution is weighted at 1.2 — higher than TASTEFUL, CURATED, HETERARCHICAL, GENERATIVE. Yet joy has no telemetry. No marks. No loop.

We measure coherence via Galois loss. We measure alignment via constitutional reward. We measure trust via demonstrated behavior.

**But joy?** Joy is Kent's gut check. A vibe.

This document asks: *Can we do better without killing the vibe?*

---

## NEW: Pilot Joy Calibration

**Key Insight from Pilots**: Joy dimensions are NOT equal across domains. Each pilot emphasizes different dimensions.

| Pilot | Primary Joy | Secondary Joy | Qualitative Assertion |
|-------|-------------|---------------|----------------------|
| **trail-to-crystal** | FLOW | WARMTH | "Lighter than a to-do list" |
| **wasm-survivors** | FLOW | SURPRISE | "Time disappears during runs" |
| **disney-portal** | WARMTH | FLOW | "Planning feels like narrative design" |
| **rap-coach** | SURPRISE | FLOW | "Discovery over QA" |
| **sprite-procedural** | SURPRISE | WARMTH | "Discovery over QA" |

### Domain-Specific Joy Thresholds

```python
from enum import Enum
from dataclasses import dataclass


class JoyDomain(Enum):
    PRODUCTIVITY = "productivity"  # trail-to-crystal
    GAMING = "gaming"              # wasm-survivors
    CONSUMER = "consumer"          # disney-portal
    CREATIVE = "creative"          # rap-coach, sprite-procedural


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

    # Check primary dimension
    if domain == JoyDomain.PRODUCTIVITY or domain == JoyDomain.GAMING:
        primary_passes = flow >= cal.primary_threshold
    elif domain == JoyDomain.CONSUMER:
        primary_passes = warmth >= cal.primary_threshold
    else:  # CREATIVE
        primary_passes = surprise >= cal.primary_threshold

    return weighted, primary_passes
```

### Pilot Qualitative Assertions (from proto-specs)

| Pilot | Assertion | Joy Test |
|-------|-----------|----------|
| trail-to-crystal | "Witnessing accelerates, not slows" | FLOW score after crystal > before |
| trail-to-crystal | "System is descriptive, not punitive" | WARMTH stable even on gap surfacing |
| wasm-survivors | "Witnessed without drag" | FLOW during run ≥ 0.7 |
| disney-portal | "Planning as narrative not spreadsheet" | WARMTH during planning ≥ 0.6 |
| rap-coach | "Courage doesn't cost points" | SURPRISE preserved on risky takes |
| sprite-procedural | "Discovery over QA" | SURPRISE on mutation viewing ≥ 0.5 |

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
- **Lines**: ~550
- **Status**: Joy Integration Architecture
- **Implementation Week**: Week 7 (parallel with Trust)
- **Key Files**:
  - `services/joy/delta.py`
  - `services/joy/inference.py`
  - `services/joy/divergence.py`
  - `services/joy/taste_profile.py`
