# Creative Muse Protocol - Part V: Collaboration & Constraints

> *"The writers room is jazz. The constraint envelope is sheet music. Both are necessary."*

**Status:** Draft
**Part:** V of VI
**Dependencies:** Parts I-IV (VisionSheaf, CreativePolynomial, ProjectionTargets)

---

## Purpose

This section defines how multiple creators collaborate within a shared CreativeVisionSheaf and how constraint envelopes (regulatory, platform, audience, creative) shape the solution space without corrupting authentic voice.

## Core Insight

**Constraints as generative, not limiting**: The right constraints—whether FCC E/I requirements, YouTube algorithm demands, or self-imposed format rules—create the boundary conditions that make creativity possible. Collaboration synthesizes multiple perspectives through dialectic composition, not consensus smoothing.

---

## Collaborative Creation Model

### The Writers Room Pattern

```python
@dataclass
class CollaborativeSession:
    """Shared creative context with role-based permissions."""
    vision: CreativeVisionSheaf           # Shared coherent vision
    participants: list[Collaborator]       # Who's in the room
    role_permissions: dict[Role, set[Operation]]
    dialectic_log: list[DialecticEntry]    # Trace of synthesis
    breaking_board: BreakingBoard          # Story decomposition workspace

    def synthesize_perspectives(
        self,
        proposals: list[StoryProposal],
    ) -> StoryBeat:
        """Dialectic synthesis: multiple views → unified beat."""
        ...

@dataclass
class Collaborator:
    """A participant in the writers room."""
    id: str
    role: Role                             # Showrunner, Staff, Freelance
    permissions: set[Operation]            # What they can do
    voice_profile: VoiceProfile            # Their authentic signature
    contributions: list[ContributionMark]  # Witness trail
```

### Role Permissions

| Role | Can Propose | Can Veto | Can Modify Vision | Can Ship |
|------|-------------|----------|-------------------|----------|
| **Showrunner** | ✓ | ✓ | ✓ | ✓ |
| **Staff Writer** | ✓ | ✗ | Story beats only | ✗ |
| **Freelance** | ✓ | ✗ | ✗ | ✗ |
| **Story Editor** | ✗ | ✓ (quality gate) | ✗ | ✗ |
| **Guest Expert** | Constrained domain | ✗ | ✗ | ✗ |

### Dialectic Synthesis

```python
@dataclass
class DialecticEntry:
    """Trace of a dialectic synthesis."""
    timestamp: datetime
    participants: list[str]
    kent_position: StoryProposal
    counterposition: StoryProposal
    synthesis: StoryBeat
    reasoning: str                         # Why this synthesis
    dissent: list[DissentMark] | None      # Who disagreed, why

class CollaborativeVisionSheaf(Sheaf[Session, Proposal, StoryBeat]):
    """
    Glue multiple proposals into coherent story beats.

    Local sections: Each participant's proposal for a beat
    Overlap: All share same episode/sequence context
    Compatible: Proposals don't contradict vision principles
    Gluing: Dialectic synthesis → unified beat
    """

    def compatible(self, p1: Proposal, p2: Proposal) -> bool:
        """Compatible if they don't violate shared vision."""
        return (
            p1.episode_id == p2.episode_id
            and not self._contradicts_vision(p1, p2)
            and self._tonally_coherent(p1, p2)
        )

    def glue(self, proposals: dict[str, Proposal]) -> StoryBeat:
        """Synthesize proposals via dialectic."""
        # Take best elements from each, resolve conflicts
        # Output includes attribution trace
        ...
```

### "Breaking" Stories (Decomposition)

```python
@dataclass
class BreakingBoard:
    """
    Workspace for decomposing story into beats.

    "Breaking" a story = finding the natural joints in the narrative arc,
    then distributing work across writers.
    """
    episode: Episode
    proposed_beats: list[StoryBeat]
    assignments: dict[str, list[StoryBeat]]  # writer_id → beats
    dependencies: dict[str, list[str]]       # beat → prerequisite beats

    def break_story(self, premise: Premise) -> list[StoryBeat]:
        """Decompose premise into sequence of beats."""
        ...

    def assign(self, beat: StoryBeat, writer: Collaborator) -> None:
        """Assign beat to writer, respecting dependencies."""
        ...
```

---

## Constraint Layer

### Constraint Envelope

```python
@dataclass
class ConstraintEnvelope:
    """The solution space boundaries."""
    regulatory: list[RegulatoryConstraint]  # FCC E/I, COPPA, ratings
    platform: list[PlatformConstraint]      # YouTube algo, runtime limits
    audience: AudienceProfile               # Age-band calibration
    creative: list[SelfImposedConstraint]   # Format rules, style guide

    def satisfies(self, work: Work) -> ConstraintResult:
        """Check if work fits within envelope."""
        violations = []

        for constraint in self.regulatory:
            if not constraint.satisfied_by(work):
                violations.append(
                    Violation(
                        type="regulatory",
                        constraint=constraint,
                        severity="BLOCKING",
                    )
                )

        for constraint in self.platform:
            if not constraint.satisfied_by(work):
                violations.append(
                    Violation(
                        type="platform",
                        constraint=constraint,
                        severity="WARNING",  # Can ship, but won't perform
                    )
                )

        # ... audience, creative checks

        return ConstraintResult(
            satisfies=len(violations) == 0,
            violations=violations,
            recommendations=self._suggest_fixes(violations),
        )

    def visualize(self) -> ConstraintDiagram:
        """
        Show the solution space as overlapping constraint boundaries.
        Useful for understanding where creative freedom exists.
        """
        ...

@dataclass
class RegulatoryConstraint:
    """Legal/regulatory requirements (MUST satisfy)."""
    name: str                              # "FCC E/I compliance"
    description: str
    validator: Callable[[Work], bool]
    citation: str | None                   # Legal code reference

@dataclass
class PlatformConstraint:
    """Platform algorithm/format requirements (SHOULD satisfy)."""
    name: str                              # "YouTube first 30s hook"
    description: str
    validator: Callable[[Work], bool]
    performance_impact: float              # 0.0-1.0 if violated

@dataclass
class AudienceConstraint:
    """Audience expectations/needs (SHOULD satisfy)."""
    age_band: AgeBand
    cognitive_load_max: float
    attention_span_seconds: int
    taboo_topics: set[str]
    required_elements: set[str]            # Safety, positivity, etc.
```

### Constraint Composition

```python
# Constraints compose as intersection
youtube_kids_envelope = (
    COPPA_CONSTRAINTS
    & YOUTUBE_KIDS_CONSTRAINTS
    & PRESCHOOL_AUDIENCE_CONSTRAINTS
    & self_imposed_format_rules
)

# Check satisfaction
result = youtube_kids_envelope.satisfies(episode)
if not result.satisfies:
    for violation in result.violations:
        if violation.severity == "BLOCKING":
            raise ConstraintViolationError(violation)
        else:
            logger.warning(f"Platform constraint violated: {violation}")
```

---

## Age-Band Calibration

### Age Bands

```python
class AgeBand(Enum):
    PRESCHOOL = "2-5"     # Simple arcs, repetition, safety
    CHILDREN = "6-8"      # A/B stories, faster pacing, mild peril
    TWEEN = "9-12"        # Complex plots, emotional nuance, identity themes
    TEEN = "13-17"        # Mature themes, irony, social complexity
    ADULT = "18+"         # Full range

@dataclass
class AgeBandProfile:
    """Cognitive and emotional characteristics of an age band."""
    band: AgeBand
    attention_span_seconds: int
    max_concurrent_plots: int
    emotional_sophistication: float        # 0.0-1.0
    abstraction_tolerance: float           # 0.0-1.0
    repetition_tolerance: float            # 1.0 (needs) → 0.0 (annoyed)
    safety_requirements: set[str]
    taboo_topics: set[str]
    preferred_pacing_bpm: int              # Beats per minute

AGE_BAND_PROFILES = {
    AgeBand.PRESCHOOL: AgeBandProfile(
        band=AgeBand.PRESCHOOL,
        attention_span_seconds=300,        # 5 min segments
        max_concurrent_plots=1,
        emotional_sophistication=0.2,
        abstraction_tolerance=0.1,
        repetition_tolerance=1.0,          # NEEDS repetition
        safety_requirements={"no_peril", "always_safe", "clear_resolution"},
        taboo_topics={"death", "conflict", "fear", "loss"},
        preferred_pacing_bpm=60,           # Slow, predictable
    ),

    AgeBand.CHILDREN: AgeBandProfile(
        band=AgeBand.CHILDREN,
        attention_span_seconds=600,        # 10 min segments
        max_concurrent_plots=2,            # A/B story
        emotional_sophistication=0.5,
        abstraction_tolerance=0.3,
        repetition_tolerance=0.6,          # Some repetition good
        safety_requirements={"ultimate_safety", "growth_oriented"},
        taboo_topics={"death", "serious_injury", "betrayal"},
        preferred_pacing_bpm=90,
    ),

    AgeBand.TWEEN: AgeBandProfile(
        band=AgeBand.TWEEN,
        attention_span_seconds=1200,       # 20 min segments
        max_concurrent_plots=3,            # A/B/C stories
        emotional_sophistication=0.8,
        abstraction_tolerance=0.7,
        repetition_tolerance=0.2,          # Gets bored easily
        safety_requirements={"growth_oriented"},
        taboo_topics={"graphic_violence", "sexual_content"},
        preferred_pacing_bpm=120,          # Fast, dynamic
    ),
}
```

### Calibration

```python
def calibrate_for_age_band(
    story: Story,
    target_band: AgeBand,
) -> CalibratedStory:
    """
    Adjust story elements to fit age band profile.

    - Simplify/complexify plot structure
    - Adjust emotional intensity
    - Modify pacing
    - Filter taboo topics
    - Add/remove repetition
    """
    profile = AGE_BAND_PROFILES[target_band]

    # Check plot complexity
    if len(story.plots) > profile.max_concurrent_plots:
        story = simplify_plots(story, profile.max_concurrent_plots)

    # Check emotional intensity
    for beat in story.beats:
        if beat.emotional_intensity > profile.emotional_sophistication:
            beat = soften_emotion(beat, profile.emotional_sophistication)

    # Filter taboo topics
    for topic in profile.taboo_topics:
        if topic in story.themes:
            raise AgeBandViolation(f"Topic '{topic}' not suitable for {target_band}")

    # Adjust pacing
    story = retempo(story, target_bpm=profile.preferred_pacing_bpm)

    return CalibratedStory(story, profile)
```

---

## The Dual Audience Problem

### Dual Optimization

```python
@dataclass
class DualAudienceTarget:
    """
    Content that must satisfy two audiences simultaneously.

    Examples:
    - Children's content → kids AND parents
    - YouTube content → creator AND algorithm
    - Educational content → students AND teachers
    """
    primary: AudienceProfile      # Who experiences it directly
    secondary: AudienceProfile    # Who enables/gates it

    def optimize(self, work: Work) -> OptimizationResult:
        """
        Find the Pareto frontier where both audiences are satisfied.

        This is NOT "lowest common denominator"—it's "synthesis that
        delights both without compromise."
        """
        primary_satisfaction = self.primary.evaluate(work)
        secondary_satisfaction = self.secondary.evaluate(work)

        if primary_satisfaction.score < 0.7:
            return OptimizationResult(
                success=False,
                message="Primary audience not satisfied",
            )

        if secondary_satisfaction.score < 0.5:
            return OptimizationResult(
                success=False,
                message="Secondary audience (gatekeeper) not satisfied",
                recommendation=secondary_satisfaction.suggestions,
            )

        return OptimizationResult(success=True)

# Example: YouTube kids content
dual_target = DualAudienceTarget(
    primary=AudienceProfile(
        age_band=AgeBand.CHILDREN,
        values={"joy", "learning", "safety"},
        preferences={"animation", "songs", "characters"},
    ),
    secondary=AudienceProfile(
        age_band=AgeBand.ADULT,
        values={"educational", "non_annoying", "brand_safe"},
        preferences={"clever_writing", "production_quality"},
    ),
)
```

### The Mirror Test vs. The Algorithm

```python
@dataclass
class AuthenticityTension:
    """
    The tension between authentic voice and external demands.

    Mirror Test: "Does this feel like me on my best day?"
    Algorithm Test: "Will this perform on the platform?"

    These can align OR conflict. When they conflict, authentic voice wins,
    but we still want to understand the performance cost.
    """
    mirror_score: float           # 0.0-1.0, subjective
    algorithm_score: float        # 0.0-1.0, predicted performance

    @property
    def alignment(self) -> float:
        """How well do authenticity and performance align?"""
        return 1.0 - abs(self.mirror_score - self.algorithm_score)

    @property
    def recommendation(self) -> str:
        if self.mirror_score > 0.8 and self.algorithm_score > 0.7:
            return "SHIP: Authentic AND performant"
        elif self.mirror_score > 0.8 and self.algorithm_score < 0.5:
            return "SHIP: Authentic, accept performance cost"
        elif self.mirror_score < 0.5 and self.algorithm_score > 0.8:
            return "REJECT: Performant but inauthentic (soul-corrupting)"
        else:
            return "ITERATE: Neither authentic nor performant"
```

---

## Feedback Loops That Don't Corrupt

### The CTR-Retention Diagnostic

```python
@dataclass
class PerformanceDiagnostic:
    """
    Analytics as information, not directives.

    CTR (Click-Through Rate) and AVD (Average View Duration) tell you
    WHERE attention drops, not WHAT to do about it.

    The Mirror Test tells you what to do.
    """
    ctr: float                    # 0.0-1.0
    avd_seconds: float
    avd_percentage: float         # What % of video watched
    retention_curve: list[float]  # Per-second retention

    def diagnose(self) -> DiagnosticResult:
        """Interpret metrics WITHOUT prescribing solutions."""
        issues = []

        if self.ctr < 0.05:
            issues.append(
                Issue(
                    type="discovery",
                    description="Thumbnail/title not connecting",
                    data_point=f"CTR: {self.ctr:.1%}",
                    mirror_question="Does the packaging reflect the content?",
                )
            )

        if self.avd_percentage < 0.3:
            issues.append(
                Issue(
                    type="hook",
                    description="Losing audience in first 30s",
                    data_point=f"30s retention: {self.retention_curve[30]:.1%}",
                    mirror_question="Does the opening promise match the content?",
                )
            )

        # Find the sharpest drop
        max_drop_idx = self._find_max_drop(self.retention_curve)
        if max_drop_idx:
            issues.append(
                Issue(
                    type="pacing",
                    description=f"Sharp drop at {max_drop_idx}s",
                    data_point=f"Lost {self._drop_magnitude(max_drop_idx):.1%}",
                    mirror_question="What happened at that moment? Was it authentic?",
                )
            )

        return DiagnosticResult(
            issues=issues,
            interpretation=self._synthesize_interpretation(issues),
            recommendation="Use Mirror Test to decide what to change",
        )

@dataclass
class Issue:
    """An observed performance issue."""
    type: str                     # discovery, hook, pacing, payoff
    description: str
    data_point: str               # The number
    mirror_question: str          # The question to ask yourself
```

### Analytics as Context, Not Command

```python
class FeedbackIntegration:
    """
    How to use analytics without corrupting voice.

    INFORM: Use data to understand audience behavior
    DON'T DOMINATE: Don't let metrics dictate creative decisions
    """

    def integrate_performance_data(
        self,
        vision: CreativeVisionSheaf,
        analytics: PerformanceDiagnostic,
    ) -> IntegrationResult:
        """
        Surface analytics as context for the vision, not replacement.
        """
        # Diagnostic tells you WHERE attention dropped
        diagnostic = analytics.diagnose()

        # Mirror Test tells you WHETHER to change it
        for issue in diagnostic.issues:
            mirror_response = self._ask_mirror(issue.mirror_question)

            if mirror_response.authentic:
                # Authentic but didn't perform → accept the cost
                logger.info(
                    f"Issue '{issue.type}' present but authentic. "
                    f"Accepting performance cost."
                )
            else:
                # Inauthentic AND didn't perform → fix it
                logger.warning(
                    f"Issue '{issue.type}' AND inauthentic. "
                    f"Recommend revision: {issue.description}"
                )

        return IntegrationResult(
            diagnostics=diagnostic,
            recommendations=[...],
            vision_integrity=self._measure_integrity(vision),
        )
```

---

## Laws

| # | Law | Description |
|---|-----|-------------|
| 1 | **Dialectic Synthesis** | `glue(proposals) ≠ average(proposals)` — synthesis creates new, doesn't smooth |
| 2 | **Constraint Composition** | `(A & B).satisfies(w) ⇒ A.satisfies(w) ∧ B.satisfies(w)` — constraints compose as intersection |
| 3 | **Age-Band Monotonicity** | `calibrate(s, PRESCHOOL).complexity ≤ calibrate(s, TWEEN).complexity` |
| 4 | **Mirror Primacy** | `mirror_score < threshold ⇒ reject(work)` regardless of algorithm_score |
| 5 | **Attribution Trace** | Every synthesized beat includes contributor attribution |
| 6 | **Permission Enforcement** | `role.permissions ⊄ required ⇒ operation.deny()` |

---

## Anti-Patterns

- **Consensus Smoothing**: Averaging proposals loses the unique perspectives
- **Metric-Driven Creation**: Optimizing for CTR/AVD first corrupts voice
- **Constraint Ignorance**: Shipping work that violates regulatory constraints
- **Age-Band Violation**: Content too complex/simple for target audience
- **Dual Audience Compromise**: "Lowest common denominator" pleases nobody
- **Analytics Paralysis**: Letting poor performance prevent authentic work
- **Permission Creep**: Allowing operations outside role boundaries

---

## Integration

### AGENTESE Paths

```
# Collaboration
self.muse.collaborate.session         → Create collaborative session
self.muse.collaborate.propose         → Submit story proposal
self.muse.collaborate.synthesize      → Run dialectic synthesis
self.muse.collaborate.break           → Decompose story into beats

# Constraints
self.muse.constraints.envelope        → Get current constraint set
self.muse.constraints.validate        → Check work against constraints
self.muse.constraints.calibrate       → Calibrate for age band
self.muse.constraints.dual_optimize   → Optimize for dual audience

# Feedback
self.muse.feedback.diagnose          → Interpret analytics
self.muse.feedback.integrate         → Surface analytics as context
self.muse.feedback.mirror            → Apply Mirror Test
```

### Cross-Jewel Events

```python
# Via SynergyBus
CollaborativeSessionCreated(session_id, participants, vision_id)
StoryBeatSynthesized(beat_id, proposals, synthesis, dissent)
ConstraintViolationDetected(work_id, violation, severity)
AgeBandCalibrated(work_id, from_band, to_band, modifications)
PerformanceDiagnosticAvailable(work_id, diagnostic)
MirrorTestFailed(work_id, mirror_score, reason)
```

---

## Implementation Reference

See: `impl/claude/services/muse/collaboration.py`, `impl/claude/services/muse/constraints.py`

---

*"The writers room is jazz—improvisation within structure. The constraint envelope is the sheet music—boundaries that make freedom possible. Analytics are the audience applause—nice to hear, but not why you play."*

*Synthesized: 2025-01-11 | Part V of VI | Collaboration, Constraints, Dual Audiences*
