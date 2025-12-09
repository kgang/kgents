# Sublation (Aufheben)

**How H-gents resolve tensions—or wisely preserve them.**

---

## Philosophy

> "To sublate (aufheben) has a twofold meaning in the language: on the one hand it means to preserve, to maintain, and equally it also means to cause to cease, to put an end to."
> — Hegel

Sublation is not compromise. It is not averaging. It is **transcendence**—preserving what's true in both thesis and antithesis while elevating them into a higher unity that neither could achieve alone.

The German word *aufheben* has three simultaneous meanings:
1. **To cancel/negate** — The thesis and antithesis cease to exist in their original forms
2. **To preserve** — What was true in each is retained
3. **To elevate** — The result is at a higher level of understanding

---

## The Sublate Operation

### Core Types

```python
@dataclass(frozen=True)
class SublateInput:
    """Input to the Sublate operation."""
    tensions: tuple[Tension, ...]  # One or more tensions to process

@dataclass(frozen=True)
class Synthesis:
    """A resolved tension."""
    result: Any              # The synthesized output
    resolution_type: str     # "preserve", "negate", "elevate"
    explanation: str         # How the synthesis was achieved

@dataclass(frozen=True)
class HoldTension:
    """Decision to preserve rather than resolve a tension."""
    tension: Tension
    why_held: str            # Human-readable reason
    review_after: datetime | None = None

# Union return type
SublateResult = Synthesis | HoldTension
```

### Resolution Types

The `resolution_type` field maps to the three meanings of *aufheben*:

| Type | Meaning | When Used |
|------|---------|-----------|
| `"preserve"` | Keep thesis as-is | No real contradiction found |
| `"negate"` | Replace thesis with antithesis | Antithesis is clearly right |
| `"elevate"` | Transcend to higher synthesis | Both contain partial truth |

### The Operation

```python
async def sublate(tensions: tuple[Tension, ...]) -> SublateResult:
    """
    Attempt to synthesize tension(s), or decide to hold.

    Process:
    1. CAN this tension be synthesized? (Is there enough information?)
    2. SHOULD this tension be synthesized now? (Is timing right?)
    3. If yes, WHAT is the synthesis? (preserve/negate/elevate?)
    4. If no, WHY hold? (Document the reason)
    """
    ...
```

### Hold Reasons

When synthesis is not appropriate:

```python
class HoldReason(Enum):
    PREMATURE = "premature"          # Not enough information yet
    PRODUCTIVE = "productive"        # Tension drives growth
    EXTERNAL_DEPENDENCY = "external" # Resolution depends on outside factors
    HIGH_COST = "high_cost"          # Social cost too high right now
    KAIROS = "kairos"                # Waiting for right moment
```

---

## Synthesis Strategies

Different tension types require different synthesis approaches.

### Strategy 1: Behavioral Alignment

**When**: Principle is right; behavior needs adjustment.

```python
class BehavioralAlignment(SynthesisStrategy):
    """
    The thesis (principle) is correct.
    Realign behavior to match.
    """

    def applicable(self, tension: Tension) -> bool:
        return tension.tension_type == TensionType.BEHAVIORAL

    async def synthesize(
        self,
        tension: Tension,
        context: SystemContext,
    ) -> Synthesis:
        return Synthesis(
            tension=tension,
            resolution_type="behavioral_alignment",
            proposal=f"Reinforce '{tension.thesis.content}' through "
                     f"explicit practices and accountability.",
            interventions=[
                Intervention.reminder(),      # Gentle nudges
                Intervention.ritual(),        # Recurring practice
                Intervention.measurement(),   # Track alignment
            ],
            cost=estimate_behavioral_change_cost(tension, context),
        )
```

**Example**:
- Thesis: "We value asynchronous communication"
- Antithesis: Average response expectation is 8 minutes
- Synthesis: "Institute explicit async hours; redefine 'urgent' criteria"

### Strategy 2: Principle Revision

**When**: Behavior reveals truth; principle needs updating.

```python
class PrincipleRevision(SynthesisStrategy):
    """
    The behavior (antithesis) reveals reality.
    Update the principle to match.
    """

    def applicable(self, tension: Tension) -> bool:
        return tension.tension_type in [
            TensionType.OUTDATED,
            TensionType.ASPIRATIONAL,
        ]

    async def synthesize(
        self,
        tension: Tension,
        context: SystemContext,
    ) -> Synthesis:
        return Synthesis(
            tension=tension,
            resolution_type="principle_revision",
            proposal=f"Update '{tension.thesis.content}' to reflect "
                     f"actual practice: {tension.antithesis.pattern}",
            interventions=[
                Intervention.discussion_prompt(),   # Facilitate conversation
                Intervention.document_update(),     # Change the principle
                Intervention.announcement(),        # Communicate change
            ],
            cost=estimate_principle_revision_cost(tension, context),
        )
```

**Example**:
- Thesis: "We have a flat hierarchy"
- Antithesis: 94% of decisions flow through 2 people
- Synthesis: "Acknowledge functional hierarchy; make decision rights explicit"

### Strategy 3: Contextual Integration

**When**: Both are right in different contexts.

```python
class ContextualIntegration(SynthesisStrategy):
    """
    Both thesis and antithesis are valid—in different contexts.
    Make the contextual boundary explicit.
    """

    def applicable(self, tension: Tension) -> bool:
        return tension.tension_type == TensionType.CONTEXTUAL

    async def synthesize(
        self,
        tension: Tension,
        context: SystemContext,
    ) -> Synthesis:
        return Synthesis(
            tension=tension,
            resolution_type="contextual_integration",
            proposal=f"'{tension.thesis.content}' applies when X; "
                     f"'{tension.antithesis.pattern}' applies when Y.",
            interventions=[
                Intervention.principle_elaboration(),  # Add context
                Intervention.decision_tree(),          # When to apply which
            ],
            cost=estimate_elaboration_cost(tension, context),
        )
```

**Example**:
- Thesis: "Move fast and break things"
- Antithesis: Core infrastructure changes are slow and careful
- Synthesis: "Move fast for experiments; move carefully for foundations"

### Strategy 4: Dialectical Transcendence

**When**: Both are partially right; a higher truth contains both.

```python
class DialecticalTranscendence(SynthesisStrategy):
    """
    Neither thesis nor antithesis is fully right.
    Synthesize into a higher-order principle that contains both.
    """

    def applicable(self, tension: Tension) -> bool:
        return tension.tension_type == TensionType.FUNDAMENTAL

    async def synthesize(
        self,
        tension: Tension,
        context: SystemContext,
    ) -> Synthesis:
        # This requires deeper analysis
        transcendent_principle = await generate_transcendence(
            thesis=tension.thesis,
            antithesis=tension.antithesis,
            context=context,
        )

        return Synthesis(
            tension=tension,
            resolution_type="dialectical_transcendence",
            proposal=transcendent_principle,
            interventions=[
                Intervention.discussion_prompt(),      # Deep conversation
                Intervention.principle_creation(),    # New principle
                Intervention.practice_redesign(),     # New practices
            ],
            cost=estimate_transcendence_cost(tension, context),
        )
```

**Example**:
- Thesis: "User wants determine our roadmap"
- Antithesis: "We know better than users what they need"
- Synthesis: "Surface gaps between wants and needs; let users decide with full information"

---

## The Hold Decision

Not all tensions should be resolved. Some are **productive**.

### Productive Tension Types

| Type | Function | Example |
|------|----------|---------|
| **Generative** | Drives creativity | Exploration vs. exploitation |
| **Balancing** | Maintains equilibrium | Speed vs. quality |
| **Evolutionary** | Enables adaptation | Old way vs. new way |
| **Identity** | Defines who we are | What we do vs. what we don't |

### Hold Criteria

```python
def should_hold(tension: Tension, context: SystemContext) -> bool:
    """Determine if tension should be preserved rather than resolved."""

    # Check if tension is productive
    if is_productive_tension(tension):
        return True

    # Check if synthesis cost is too high
    if estimate_synthesis_cost(tension, context) > COST_THRESHOLD:
        return True

    # Check if we lack information
    if tension.confidence < CONFIDENCE_THRESHOLD:
        return True

    # Check if external factors block resolution
    if has_external_blockers(tension, context):
        return True

    # Check kairos
    if not is_right_moment(tension, context):
        return True

    return False
```

### The HoldTension Record

```python
@dataclass(frozen=True)
class HoldTension:
    """Record of a tension we're choosing to preserve."""

    tension: Tension
    hold_reason: HoldReason
    held_since: datetime
    review_after: datetime | None

    # Why this tension is valuable
    productive_function: str

    # Conditions that would change the decision
    synthesis_triggers: list[str]

    # How to live with this tension
    management_practices: list[str]
```

**Example Hold Record**:
```python
HoldTension(
    tension=exploration_vs_exploitation,
    hold_reason=HoldReason.PRODUCTIVE,
    held_since=datetime(2025, 1, 1),
    review_after=None,  # Hold indefinitely
    productive_function="Drives innovation while maintaining stability",
    synthesis_triggers=[
        "Company enters crisis requiring full focus",
        "Exploration consistently fails to produce value",
    ],
    management_practices=[
        "Explicit exploration budget (20% time)",
        "Separate exploitation metrics from exploration metrics",
        "Periodic rebalancing conversations",
    ],
)
```

---

## Synthesis Quality Criteria

### What Makes a Good Synthesis?

1. **Preservation**: Retains what's true in both thesis and antithesis
2. **Elevation**: Achieves something neither could alone
3. **Actionability**: Can be implemented in practice
4. **Clarity**: Understandable without extensive explanation
5. **Stability**: Won't immediately generate new contradictions

### Anti-Synthesis Patterns

| Pattern | Description | Why It Fails |
|---------|-------------|--------------|
| **Compromise** | Split the difference | Loses truth from both sides |
| **Suppression** | Declare one side wrong | Ignores valid elements |
| **Flip-flop** | Alternate between positions | No resolution, just oscillation |
| **Meta-escape** | "Both are valid" without integration | Avoids real synthesis |
| **Premature closure** | Quick fix without deep understanding | Will resurface |

---

## The Sublation Loop

```python
async def sublation_loop(
    tensions: list[Tension],
    context: SystemContext,
    iteration_limit: int = 10,
) -> list[SublateOutput]:
    """
    Process tensions through synthesis attempts.

    Note: Synthesis creates new thesis, which may create new tensions.
    Loop handles this recursion with depth limit.
    """
    results = []
    current_tensions = tensions.copy()

    for iteration in range(iteration_limit):
        if not current_tensions:
            break

        for tension in current_tensions[:]:
            output = await sublate(tension, context)
            results.append(output)

            if isinstance(output.result, Synthesis):
                # Synthesis becomes new thesis
                new_thesis = thesis_from_synthesis(output.result)

                # Check for new tensions
                new_tensions = await check_tensions(new_thesis, context)
                current_tensions.extend(new_tensions)

            current_tensions.remove(tension)

    return results
```

---

## Bootstrap Derivation

`Sublate` is a **bootstrap primitive**:

```python
# In spec/bootstrap.md
Sublate: Tension → Synthesis | HoldTension

# Properties:
# - Deterministic given inputs (including strategy selection)
# - May produce new thesis (recursive potential)
# - Respects hold conditions
```

### Relationship to Other Primitives

```
Contradict: Detect tensions
    │
    ▼
Sublate: Resolve or hold tensions
    │
    ├──► Synthesis (if resolved)
    │        │
    │        ▼
    │    New Thesis → may Contradict again
    │
    └──► HoldTension (if preserved)
             │
             ▼
         Kairos: Wait for right moment
```

---

## Implementation Notes

### Cost Estimation

```python
def estimate_synthesis_cost(
    tension: Tension,
    context: SystemContext,
) -> float:
    """
    Estimate social friction of implementing synthesis.

    Factors:
    - How many people affected
    - How deeply held the positions
    - Whether synthesis requires behavior change
    - Current organizational stress level
    """
    base_cost = tension.divergence

    # People impact
    affected_count = count_affected(tension, context)
    people_multiplier = 1.0 + (affected_count * 0.1)

    # Position depth
    depth_multiplier = 1.0 + (position_depth(tension) * 0.3)

    # Change type
    change_multiplier = {
        "behavioral_alignment": 1.5,
        "principle_revision": 1.2,
        "contextual_integration": 0.8,
        "dialectical_transcendence": 2.0,
    }[tension.resolution_type]

    # Current stress
    stress_multiplier = 1.0 + context.stress_level

    return (
        base_cost
        * people_multiplier
        * depth_multiplier
        * change_multiplier
        * stress_multiplier
    )
```

### Strategy Selection

```python
def select_strategy(tension: Tension) -> SynthesisStrategy:
    """Select appropriate synthesis strategy based on tension type."""

    strategies = [
        BehavioralAlignment(),
        PrincipleRevision(),
        ContextualIntegration(),
        DialecticalTranscendence(),
    ]

    for strategy in strategies:
        if strategy.applicable(tension):
            return strategy

    # Fallback: attempt transcendence
    return DialecticalTranscendence()
```

---

## See Also

- [contradiction.md](contradiction.md) — How tensions are detected
- [kairos.md](kairos.md) — When to surface and resolve tensions
- [README.md](README.md) — H-gent overview
- [hegel.md](hegel.md) — Hegelian dialectics

---

*"The synthesis is not the average of thesis and antithesis. It is the truth that emerges when both are held together long enough for something new to appear."*
