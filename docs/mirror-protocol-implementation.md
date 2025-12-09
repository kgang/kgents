# Mirror Protocol Implementation Plan

**A Path from Vision to Reality**

---

## Guiding Philosophy

The Mirror Protocol is not a product to ship—it is a practice to cultivate. The implementation must embody the same principles it seeks to instill: gradual transformation, self-awareness, and alignment between stated intentions and actual behaviors.

We will build this the way we would want an organization to transform: incrementally, with reflection at each stage, and with the humility to revise our approach based on what we learn.

---

## Phase 0: Foundation Work (Pre-requisite)

**Goal:** Ensure kgents core is solid before building organizational scaffolding.

### 0.1 Complete Cross-Pollination Gaps

| Integration | Status | Blocks |
|-------------|--------|--------|
| J+T Integration | ✅ Tests passing | - |
| R-gents DSPy Backend | ✅ Implementation done | Needs commit |
| H-gent (Hegelian) | 🔴 Not started | Core to Mirror Protocol |
| O-gent Orchestration | 🟡 Partial | Needs intervention policies |

**Action:** Before Mirror Protocol, we need H-gent. The dialectical engine is the heart of the system.

### 0.2 H-gent Specification

```
spec/h-gents/
├── README.md           # Philosophy of dialectical synthesis
├── contradiction.md    # How contradictions are detected
├── sublation.md        # How tensions resolve
└── kairos.md           # The art of timing
```

**Core Types:**
```python
@dataclass(frozen=True)
class Thesis:
    """A stated principle or value."""
    content: str
    source: str  # Where it was extracted from
    confidence: float

@dataclass(frozen=True)
class Antithesis:
    """An observed behavior that tensions with a thesis."""
    pattern: str
    evidence: list[Trace]
    frequency: float

@dataclass(frozen=True)
class Tension:
    """The productive friction between stated and actual."""
    thesis: Thesis
    antithesis: Antithesis
    divergence: float  # 0 = aligned, 1 = contradictory
    interpretation: str  # Human-readable diagnosis

@dataclass(frozen=True)
class Synthesis:
    """A proposed resolution."""
    tension: Tension
    intervention_type: InterventionType
    proposal: str
    cost: float  # Social friction estimate
```

---

## Phase 1: The Minimal Mirror (Months 1-2)

**Goal:** Build the simplest possible system that demonstrates value.

### 1.1 Single-Platform Start: Obsidian

**Why Obsidian first:**
- Local-first (no API rate limits, no privacy concerns)
- File-based (easy to parse, easy to test)
- Knowledge-focused (principles are explicit)
- Personal use possible (test on ourselves first)

**Scope:**
```
impl/claude/protocols/mirror/
├── __init__.py
├── obsidian/
│   ├── extractor.py      # P-gent: Extract principles from vault
│   ├── witness.py        # W-gent: Observe note patterns
│   └── tension.py        # H-gent: Find contradictions
├── types.py              # Thesis, Antithesis, Tension, Synthesis
└── _tests/
    └── test_obsidian_mirror.py
```

**The First Mirror:**
```python
async def obsidian_mirror(vault_path: str) -> MirrorReport:
    """
    The minimal mirror: extract principles, observe patterns,
    find one tension, suggest one synthesis.
    """
    # Extract what the vault claims to value
    principles = await P_gent.extract_from_obsidian(vault_path)

    # Observe actual patterns
    patterns = await W_gent.observe_obsidian(vault_path)

    # Find tensions
    tensions = await H_gent.contradict(principles, patterns)

    # Return the single most significant tension
    return MirrorReport(
        thesis=tensions[0].thesis,
        antithesis=tensions[0].antithesis,
        reflection=f"You wrote '{tensions[0].thesis.content}' "
                   f"but your vault shows {tensions[0].antithesis.pattern}. "
                   f"What does this tell you?",
    )
```

### 1.2 Concrete First Contradictions to Detect

**For personal Obsidian vaults:**

| Stated (Principle) | Observed (Pattern) | Tension Name |
|--------------------|-------------------|--------------|
| "Daily notes are important" | 47 orphaned daily notes never linked | Ritual Abandonment |
| "I value deep work" | 80% of notes < 200 words | Surface Skimming |
| "Evergreen notes" | Average note untouched for 8 months | Digital Hoarding |
| "Connect ideas" | 60% of notes have 0 outgoing links | Knowledge Silos |

**Implementation priority:** Start with structural patterns (link density, note length, update frequency) before semantic analysis.

### 1.3 Deliverable

A CLI tool:
```bash
$ kgents mirror obsidian ~/Documents/MyVault

╭─────────────────────────────────────────────────────╮
│                    Mirror Report                     │
├─────────────────────────────────────────────────────┤
│ Thesis: "I use daily notes for reflection"          │
│ Source: README.md, line 12                          │
│                                                     │
│ Antithesis: 73% of daily notes contain only         │
│ tasks, no reflective content                        │
│                                                     │
│ Divergence: 0.73                                    │
│                                                     │
│ Reflection: Your daily practice has drifted from    │
│ reflection to task management. Is this serving you? │
╰─────────────────────────────────────────────────────╯
```

---

## Phase 2: The Organizational Witness (Months 3-4)

**Goal:** Extend to multi-user, add read-only Slack/Notion observation.

### 2.1 MCP Server Architecture

```
mcp-servers/
├── mirror-obsidian/
│   ├── server.py
│   └── tools/
│       ├── extract_principles.py
│       ├── analyze_patterns.py
│       └── generate_report.py
│
├── mirror-notion/
│   ├── server.py
│   └── tools/
│       ├── index_workspace.py
│       ├── extract_principles.py
│       └── track_document_health.py
│
└── mirror-slack/
    ├── server.py
    └── tools/
        ├── analyze_patterns.py      # Read-only
        ├── track_commitments.py     # Read-only
        └── measure_response_times.py # Read-only
```

### 2.2 The Witness Protocol (W-gent Extension)

**Key constraint:** Phase 2 is observation only. No interventions.

```python
@dataclass
class WitnessConfig:
    """Configuration for organizational observation."""

    # Privacy boundaries
    sanctuary_channels: set[str]  # Channels to ignore
    blind_mode: bool = False      # Metrics only, no content

    # What to observe
    observe_response_times: bool = True
    observe_commitment_patterns: bool = True
    observe_decision_flows: bool = True
    observe_influence_patterns: bool = True

    # What NOT to observe
    observe_message_content: bool = False  # Start conservative
    observe_dm_patterns: bool = False
```

**Organizational Patterns to Detect:**

| Pattern | Signal | What It Reveals |
|---------|--------|-----------------|
| Response Velocity | Time between message and first reply | Async vs sync culture |
| Decision Latency | Time from question to resolution | Bureaucratic friction |
| Shadow Hierarchy | Who gets responded to fastest | Actual vs formal power |
| Commitment Decay | % of "I'll do X" that happen | Follow-through culture |
| Information Flow | Where announcements originate | Communication topology |

### 2.3 The Tri-Lattice Data Model

```python
@dataclass
class DeonticGraph:
    """What the organization says it values."""
    nodes: list[Principle]
    edges: list[PrincipleRelation]  # supports, conflicts, elaborates

    @classmethod
    def from_notion(cls, workspace_id: str) -> DeonticGraph: ...

    @classmethod
    def from_obsidian(cls, vault_path: str) -> DeonticGraph: ...

@dataclass
class OnticGraph:
    """What the organization actually does."""
    actors: list[Actor]  # Anonymized by default
    artifacts: list[Artifact]  # Documents, decisions, etc.
    interactions: list[Interaction]

    @classmethod
    def from_slack(cls, workspace_id: str, config: WitnessConfig) -> OnticGraph: ...

@dataclass
class TensionGraph:
    """Where stated and actual diverge."""
    tensions: list[Tension]

    @classmethod
    def from_dialectic(cls, deontic: DeonticGraph, ontic: OnticGraph) -> TensionGraph: ...
```

### 2.4 Deliverable

**The Organizational Diagnostic Report**

A comprehensive document (Notion page or Obsidian note) generated after 4 weeks of observation:

```markdown
# Organizational Mirror Report
Generated: 2025-02-15
Observation Period: 2025-01-15 to 2025-02-15
Consent Level: Leadership Only

## Executive Summary

Your organization states 12 core principles. We observed alignment
with 7 and tension with 5.

Overall Integrity Score: 0.58 (where 1.0 = perfect alignment)

## The Three Most Significant Tensions

### 1. The Async Paradox (Divergence: 0.82)
**Stated:** "We value asynchronous communication"
**Observed:** Average expected response time: 8 minutes
**Pattern:** 73% of messages receive a response within 15 minutes
**Interpretation:** Your async principle may be aspirational rather than actual.

### 2. The Flat Hierarchy Illusion (Divergence: 0.71)
**Stated:** "We have a flat organizational structure"
**Observed:** 94% of strategic decisions flow through 2 individuals
**Pattern:** These individuals are CCed on 78% of all project channels
**Interpretation:** Formal flatness may mask informal hierarchy.

### 3. The Documentation Drift (Divergence: 0.65)
**Stated:** "We document all major decisions"
**Observed:** 34% of decisions referenced in Slack have Notion records
**Pattern:** Documentation decreases 40% during high-pressure periods
**Interpretation:** Documentation is sacrificed under load.

## Patterns That Align Well

- Customer mentions in channels (High alignment with "customer obsessed")
- Code review thoroughness (Aligns with "quality over speed")
- Meeting-free Fridays (Actually observed 89% compliance)
```

---

## Phase 3: The Gentle Interventions (Months 5-7)

**Goal:** Begin active assistance, but only when invited.

### 3.1 Intervention Types

```python
class InterventionType(Enum):
    # Passive (always available)
    REFLECT = "reflect"       # Surface a pattern when asked
    REMEMBER = "remember"     # Recall relevant past decisions

    # Active (requires opt-in)
    REMIND = "remind"         # Gentle commitment tracking
    SUGGEST = "suggest"       # Propose principle-aligned actions
    DRAFT = "draft"           # Generate documentation

    # Structural (requires explicit approval)
    RITUAL = "ritual"         # Create recurring processes
    AUDIT = "audit"           # Systematic principle review
```

### 3.2 The Intervention Cost Function

Before any active intervention, calculate social cost:

```python
def calculate_intervention_cost(
    tension: Tension,
    context: OrganizationalContext,
    timing: datetime,
) -> float:
    """
    Estimate the social friction of intervening.

    High cost = wait for better moment (kairos)
    Low cost = safe to proceed
    """

    # Base cost from tension severity
    base_cost = tension.divergence

    # Multipliers
    visibility_multiplier = 1.5 if context.is_public_channel else 1.0
    stress_multiplier = 1.0 + context.current_org_stress_level
    timing_multiplier = 0.5 if is_retrospective_moment(timing) else 1.0
    relationship_multiplier = 0.7 if context.agent_trust_level > 0.8 else 1.2

    return (
        base_cost
        * visibility_multiplier
        * stress_multiplier
        * timing_multiplier
        * relationship_multiplier
    )
```

### 3.3 The Kairos Engine

**The right intervention at the wrong time is the wrong intervention.**

```python
@dataclass
class Kairos:
    """An opportune moment for intervention."""

    moment_type: KairosType
    tension: Tension
    recommended_intervention: InterventionType
    cost_at_this_moment: float

class KairosType(Enum):
    RETROSPECTIVE = "retrospective"     # Scheduled reflection time
    DECISION_POINT = "decision_point"   # Active decision being made
    PATTERN_PEAK = "pattern_peak"       # Behavior just repeated notably
    EXPLICIT_ASK = "explicit_ask"       # User asked for feedback
    NEW_MEMBER = "new_member"           # Onboarding moment
    CRISIS_AFTERMATH = "crisis_after"   # Post-incident review

async def wait_for_kairos(tension: Tension) -> Kairos:
    """
    Hold a tension until the right moment to surface it.

    This is the art of the Mirror Protocol—knowing when
    to speak and when to remain silent.
    """
    while True:
        moment = await detect_opportune_moment()
        cost = calculate_intervention_cost(tension, moment)

        if cost < INTERVENTION_THRESHOLD:
            return Kairos(
                moment_type=moment.type,
                tension=tension,
                recommended_intervention=select_intervention(tension, moment),
                cost_at_this_moment=cost,
            )

        await asyncio.sleep(CHECK_INTERVAL)
```

### 3.4 Concrete Interventions (Phase 3 Scope)

**The Commitment Companion** (Slack)
```
When: User says "I'll have X done by Y"
Action:
  - Record commitment (with consent)
  - On date Y, DM: "You mentioned finishing X today.
    How's it going? (Reply 'done', '延期', or 'cancel')"
  - Track patterns privately
  - After 4 weeks, share personal completion rate
```

**The Decision Archaeologist** (Notion)
```
When: User creates a decision document
Action:
  - Search for related past decisions
  - Suggest: "Before finalizing, you might want to see:
    - [Similar decision from Q2] - outcome was X
    - [Related principle] from handbook"
  - Link documents automatically
```

**The Staleness Sentinel** (Notion/Obsidian)
```
When: Document hasn't been touched in 90 days but is linked frequently
Action:
  - Add subtle indicator: "Last reviewed: 94 days ago"
  - On next edit anywhere in workspace, suggest review
```

### 3.5 Deliverable

**Slack App: "Mirror"**

- Opt-in per user
- Commands:
  - `/mirror reflect` - Show my patterns this week
  - `/mirror remember <topic>` - Surface relevant history
  - `/mirror track "commitment"` - Add to my commitment list
  - `/mirror patterns` - Team patterns (if team opted in)

**Notion Integration: "Mirror Sidebar"**

- Shows principle alignment score for current document
- Surfaces related decisions
- Flags potential contradictions with other documents

---

## Phase 4: The Dialectical Engine (Months 8-10)

**Goal:** Full H-gent implementation with synthesis capabilities.

### 4.1 H-gent Core Implementation

```python
class HGent(Agent[DialecticInput, Synthesis]):
    """
    The Hegelian agent: holds contradictions until they resolve.

    Philosophy:
    - Contradictions are not bugs, they are features
    - Tension is the energy source for growth
    - Synthesis is not compromise, it is transcendence
    """

    async def invoke(self, input: DialecticInput) -> Synthesis:
        # Step 1: Identify the real contradiction
        # (Not all differences are contradictions)
        contradiction = await self.find_true_contradiction(
            input.thesis,
            input.antithesis
        )

        if contradiction is None:
            return Synthesis.no_tension(input)

        # Step 2: Determine the nature of the tension
        tension_type = await self.classify_tension(contradiction)

        # Step 3: Generate synthesis options
        syntheses = await self.generate_syntheses(
            contradiction,
            tension_type
        )

        # Step 4: Evaluate and select
        return await self.select_synthesis(syntheses, input.context)

    async def classify_tension(self, contradiction: Contradiction) -> TensionType:
        """
        Not all contradictions resolve the same way.

        Types:
        - BEHAVIORAL: Principle is right, behavior needs adjustment
        - ASPIRATIONAL: Principle is aspirational, behavior is realistic
        - OUTDATED: Principle no longer serves, should be updated
        - CONTEXTUAL: Both are right in different contexts
        - FUNDAMENTAL: Deep conflict requiring organizational choice
        """
        ...
```

### 4.2 Synthesis Strategies

```python
class SynthesisStrategy(Protocol):
    """Different ways to resolve a contradiction."""

    async def synthesize(
        self,
        thesis: Thesis,
        antithesis: Antithesis,
        context: OrgContext,
    ) -> Synthesis: ...

class BehavioralAlignment(SynthesisStrategy):
    """The principle is right; adjust behavior."""

    async def synthesize(self, thesis, antithesis, context) -> Synthesis:
        return Synthesis(
            resolution_type="behavioral",
            proposal=f"Reinforce '{thesis.content}' through...",
            interventions=[
                Intervention.reminder(),
                Intervention.ritual(),
            ],
        )

class PrincipleRevision(SynthesisStrategy):
    """The behavior reveals truth; update the principle."""

    async def synthesize(self, thesis, antithesis, context) -> Synthesis:
        return Synthesis(
            resolution_type="revision",
            proposal=f"Consider updating '{thesis.content}' to reflect...",
            interventions=[
                Intervention.discussion_prompt(),
                Intervention.document_update(),
            ],
        )

class ContextualIntegration(SynthesisStrategy):
    """Both are right in different contexts; make context explicit."""

    async def synthesize(self, thesis, antithesis, context) -> Synthesis:
        return Synthesis(
            resolution_type="contextual",
            proposal=f"'{thesis.content}' applies when X; "
                     f"observed pattern applies when Y",
            interventions=[
                Intervention.principle_elaboration(),
            ],
        )
```

### 4.3 The Sublation Loop

```python
async def sublation_loop(org: Organization) -> None:
    """
    The continuous process of organizational becoming.

    This loop runs perpetually, holding tensions until
    they resolve and surfacing new ones as they emerge.
    """
    held_tensions: list[Tension] = []

    while True:
        # Observe current state
        deontic = await P_gent.extract_principles(org)
        ontic = await W_gent.observe_behaviors(org)

        # Find new tensions
        new_tensions = await H_gent.find_tensions(deontic, ontic)
        held_tensions.extend(new_tensions)

        # Check for kairos moments
        for tension in held_tensions:
            kairos = await detect_kairos(tension, org)

            if kairos and kairos.cost < THRESHOLD:
                # The moment is right
                synthesis = await H_gent.synthesize(tension)

                if await O_gent.approve_intervention(synthesis):
                    await J_gent.execute_intervention(synthesis)
                    held_tensions.remove(tension)

        # Rest and repeat
        await asyncio.sleep(OBSERVATION_INTERVAL)
```

---

## Phase 5: The Living Organization (Months 11-12)

**Goal:** The system becomes invisible; the organization becomes self-aware.

### 5.1 The Fixed Point

```python
async def measure_organizational_integrity(org: Organization) -> float:
    """
    The integrity score: how aligned is stated with actual?

    Score of 1.0 means the organization fully lives its values.
    This is asymptotic—never fully reached, always approached.
    """
    deontic = await P_gent.extract_principles(org)
    ontic = await W_gent.observe_behaviors(org)
    tensions = await H_gent.find_tensions(deontic, ontic)

    if not tensions:
        return 1.0

    total_divergence = sum(t.divergence for t in tensions)
    return 1.0 - (total_divergence / len(tensions))
```

**The goal is not to reach 1.0. The goal is for the organization to know its own score and care about moving it.**

### 5.2 Internalization Markers

How do we know the Mirror Protocol has succeeded?

| Marker | Observation | What It Means |
|--------|-------------|---------------|
| Self-referencing | Team cites principles without prompting | Values are internalized |
| Proactive documentation | Decisions documented without reminder | Process is habit |
| Tension acknowledgment | "We say X but do Y" in human discussions | Self-awareness |
| Ritual ownership | Team creates own accountability rituals | Agency transferred |
| Mirror consultation | "What would Mirror say about this?" | Trust established |

### 5.3 The Fadeout Protocol

```python
async def assess_internalization(org: Organization) -> InternalizationReport:
    """
    Determine if the organization has internalized the mirror.

    When internalization is high, the system should do less.
    """
    markers = await observe_internalization_markers(org)

    if markers.self_referencing > 0.8 and markers.proactive_documentation > 0.7:
        return InternalizationReport(
            recommendation="reduce_intervention_frequency",
            message="The organization is demonstrating self-awareness. "
                    "Consider reducing Mirror's active presence.",
        )

    return InternalizationReport(
        recommendation="maintain_current_level",
        areas_for_focus=markers.weakest_areas,
    )
```

---

## Implementation Priorities

### Immediate (This Month)

1. **Commit current work** - J+T integration, R-gents Phase 2
2. **Spec H-gent** - Write `spec/h-gents/README.md` with the dialectical philosophy
3. **Obsidian extractor** - P-gent for local vaults (the first P-gent integration point)

### Near-term (Next 2 Months)

4. **Personal Mirror CLI** - Test on our own Obsidian vaults
5. **Tension detection** - H-gent contradiction finding (structural patterns first)
6. **Mirror report generation** - The first diagnostic output

### Medium-term (Months 3-6)

7. **MCP servers** - Notion and Slack read-only integration
8. **Organizational witness** - W-gent for multi-user contexts
9. **Kairos engine** - Timing-aware intervention system

### Longer-term (Months 6-12)

10. **Active interventions** - Slack app, Notion sidebar
11. **Full H-gent** - Synthesis generation and selection
12. **Sublation loop** - Continuous organizational transformation

---

## Open Design Questions

### 1. The Authority Problem

Who decides when the Mirror is right and the organization is wrong vs. vice versa?

**Current thinking:** The Mirror never decides. It only surfaces tensions. Humans decide resolutions. The system can suggest synthesis options but cannot impose them.

### 2. The Privacy Gradient

How do we handle the spectrum from "completely transparent" to "completely private"?

**Current thinking:** Start maximally conservative (metrics only, no content analysis). Let organizations opt into deeper observation over time as trust builds.

### 3. The Adversarial User

What happens when someone games the system? (e.g., writing principles they don't intend to follow just to look good)

**Current thinking:** The W-gent will observe the gap. Gaming creates larger tensions, not smaller ones. The system is ungameable because it measures alignment, not just stated values.

### 4. The Bootstrap Paradox

How does kgents hold itself accountable to the Mirror Protocol?

**Current thinking:** We use it on ourselves first. The kgents project should have its own Mirror running, surfacing tensions between our spec and our implementation.

---

## The Spirit of the Work

This implementation plan is itself subject to the Mirror Protocol. We have stated an intention (transform organizations through dialectical reflection). Our actual behavior (the code we write) will either align or diverge.

The first test of the Mirror Protocol is whether we can build it in a way that embodies its principles:

- **Gradual transformation** - We don't try to build everything at once
- **Self-awareness** - We acknowledge what we don't know
- **Integrity** - Our implementation matches our specification
- **Humility** - We revise our approach based on what we learn

The Mirror Protocol is not a feature to ship. It is a practice to cultivate—first in ourselves, then in our tools, then in the organizations we serve.
