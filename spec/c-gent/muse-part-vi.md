# Creative Muse Protocol: Part VI — Iteration Checkpoints & Production Rhythm

> *"CGP Grey has 66 checkpoints from zeroth draft to published video. Breakthrough work requires a similar systematic progression—not to bureaucratize creativity, but to ensure nothing is skipped."*

**Status:** Draft (Aligned with Muse v2.0)
**Dependencies:** Muse v2.0 (The Co-Creative Engine)
**Core Insight:** The co-creative engine produces breakthroughs through 30-50 iterations. This part defines **what happens at each checkpoint** and **how work flows from spark to ship**.

---

## The Gap This Fills

The main Muse spec defines the **engine** (dialectic, volume, contradiction, surprise). This part defines:

1. **Iteration Checkpoints** — The 30-50 discrete moments where quality is locked in
2. **Domain Templates** — CGP Grey-style checkpoint lists for different media
3. **Promise-Fulfillment** — Package defines content (thumbnail before video)
4. **Production Rhythm** — Batching for efficiency without killing quality

---

## Part A: The Checkpoint Principle

### Why Checkpoints Matter

```python
# The difference between amateur and professional:

AMATEUR_PROCESS = """
Spark → Work on it → Work on it more → Good enough → Ship
(No discrete checkpoints, quality is vague, "done" is arbitrary)
"""

PROFESSIONAL_PROCESS = """
Spark → Checkpoint 1 (concept lock) → Checkpoint 2 (structure lock) → ...
→ Checkpoint 47 (final polish) → Checkpoint 48 (ship)
(Discrete moments where specific quality is verified and locked)
"""

# CGP Grey: 66 checkpoints from "zeroth draft" to "published video"
# Each checkpoint: specific question answered, specific quality verified
```

### The Checkpoint Contract

```python
@dataclass(frozen=True)
class Checkpoint:
    """A discrete moment where quality is verified and locked."""

    number: int                    # Position in sequence
    name: str                      # Human-readable name
    question: str                  # What must be answered?
    lock: str                      # What gets locked at this point?
    unlock_condition: str          # What allows regression?

    # Quality gates
    must_pass: list[str]           # Tests that must pass
    co_creative_mode: str          # "amplify", "contradict", "mirror", "none"

    def verify(self, work: Work) -> CheckpointResult:
        """Does the work pass this checkpoint?"""
        ...

# Example: YouTube hook checkpoint
YOUTUBE_CHECKPOINT_03 = Checkpoint(
    number=3,
    name="hook_lock",
    question="Does the first 5 seconds command attention?",
    lock="Opening hook content and structure",
    unlock_condition="Only if thumbnail/title change invalidates hook",
    must_pass=[
        "hook_clarity",       # Is the hook immediately clear?
        "hook_curiosity",     # Does it create forward momentum?
        "hook_authenticity",  # Is it true to the content?
    ],
    co_creative_mode="contradict",  # Challenge the hook
)
```

### Lock and Unlock

```python
class LockUnlockProtocol:
    """
    Once a checkpoint passes, that element is LOCKED.
    Unlocking requires explicit justification and triggers re-verification.

    This prevents:
    - Endless revision of early elements
    - Late changes that invalidate earlier work
    - Quality regression through "small tweaks"
    """

    async def lock(self, checkpoint: Checkpoint, work: Work) -> LockedElement:
        """Lock an element after checkpoint passes."""
        result = checkpoint.verify(work)

        if not result.passed:
            raise CheckpointFailed(checkpoint, result.failures)

        return LockedElement(
            checkpoint=checkpoint,
            content_hash=hash(extract_element(work, checkpoint.lock)),
            locked_at=now(),
            can_unlock_if=checkpoint.unlock_condition,
        )

    async def unlock(
        self,
        locked: LockedElement,
        justification: str,
    ) -> UnlockedElement:
        """Unlock for revision—requires justification."""

        # Log the unlock (for learning)
        self.log_unlock(locked, justification)

        # Identify checkpoints that must re-pass
        invalidated = self.find_invalidated_checkpoints(locked)

        return UnlockedElement(
            original=locked,
            justification=justification,
            must_repass=invalidated,
        )
```

---

## Part B: Domain Checkpoint Templates

### B.1 YouTube Video (48 Checkpoints)

Inspired by CGP Grey's 66-item template, adapted for the co-creative engine:

```python
YOUTUBE_CHECKPOINTS = [
    # === PHASE 0: CONCEPT (Checkpoints 1-8) ===
    Checkpoint(1, "spark_capture",
        question="What's the core idea?",
        lock="Topic and angle",
        co_creative_mode="amplify"),  # Generate 50 angles

    Checkpoint(2, "viability_check",
        question="Is this worth making?",
        lock="Go/no-go decision",
        co_creative_mode="contradict"),  # Challenge the idea

    Checkpoint(3, "promise_draft",
        question="What's the thumbnail/title promise?",
        lock="Core promise (not final execution)",
        co_creative_mode="amplify"),  # Generate 30 promise variants

    Checkpoint(4, "hook_concept",
        question="How does this open?",
        lock="Opening strategy",
        co_creative_mode="contradict"),  # Challenge obvious hooks

    Checkpoint(5, "payoff_clarity",
        question="What's the satisfying ending?",
        lock="Payoff concept",
        co_creative_mode="amplify"),  # Generate payoff options

    Checkpoint(6, "structure_draft",
        question="What are the major beats?",
        lock="Story structure",
        co_creative_mode="mirror"),  # Does structure feel like Kent?

    Checkpoint(7, "surprise_check",
        question="Where's the surprise?",
        lock="Surprise element",
        co_creative_mode="contradict"),  # Is this actually surprising?

    Checkpoint(8, "concept_lock",
        question="Is this concept breakthrough-worthy?",
        lock="Full concept",
        co_creative_mode="mirror"),  # Final concept Mirror Test

    # === PHASE 1: SCRIPT (Checkpoints 9-20) ===
    Checkpoint(9, "script_v0",
        question="What's the zeroth draft?",
        lock="Nothing—this is exploratory",
        co_creative_mode="amplify"),  # Fast generation

    Checkpoint(10, "hook_script",
        question="First 30 seconds locked?",
        lock="Opening script",
        co_creative_mode="contradict"),

    Checkpoint(11, "value_script",
        question="Core value delivery clear?",
        lock="Main content structure",
        co_creative_mode="mirror"),

    Checkpoint(12, "payoff_script",
        question="Ending earns its emotion?",
        lock="Closing script",
        co_creative_mode="contradict"),

    Checkpoint(13, "flow_check",
        question="Does it flow without friction?",
        lock="Transition points",
        co_creative_mode="mirror"),

    Checkpoint(14, "cut_pass",
        question="What can be cut without loss?",
        lock="Trimmed script",
        co_creative_mode="contradict"),  # Challenge every element

    Checkpoint(15, "voice_check",
        question="Does every line sound like Kent?",
        lock="Voice consistency",
        co_creative_mode="mirror"),

    Checkpoint(16, "read_aloud",
        question="Does it work spoken?",
        lock="Speakability",
        co_creative_mode="none"),  # Kent reads, no AI

    Checkpoint(17, "pattern_interrupts",
        question="Where are the attention resets?",
        lock="Pattern interrupt points",
        co_creative_mode="amplify"),

    Checkpoint(18, "open_loops",
        question="What questions keep viewer watching?",
        lock="Curiosity gaps",
        co_creative_mode="amplify"),

    Checkpoint(19, "no_compromises_script",
        question="Does every line pass the taste test?",
        lock="Script quality",
        co_creative_mode="mirror"),  # Full compromise audit

    Checkpoint(20, "script_lock",
        question="Is this script breakthrough-worthy?",
        lock="Final script",
        co_creative_mode="mirror"),

    # === PHASE 2: PRODUCTION (Checkpoints 21-30) ===
    Checkpoint(21, "shot_list",
        question="What needs to be captured?",
        lock="Shot requirements",
        co_creative_mode="none"),

    Checkpoint(22, "b_roll_plan",
        question="What supports the A-roll?",
        lock="B-roll list",
        co_creative_mode="amplify"),

    Checkpoint(23, "location_setup",
        question="Is the environment right?",
        lock="Location",
        co_creative_mode="none"),

    Checkpoint(24, "performance_prep",
        question="Is Kent ready to deliver?",
        lock="Performance state",
        co_creative_mode="none"),

    Checkpoint(25, "a_roll_capture",
        question="Is the core performance captured?",
        lock="A-roll footage",
        co_creative_mode="none"),

    Checkpoint(26, "performance_review",
        question="Does the performance work?",
        lock="Take selection",
        co_creative_mode="mirror"),  # Does this feel like Kent at his best?

    Checkpoint(27, "b_roll_capture",
        question="Is supporting footage captured?",
        lock="B-roll footage",
        co_creative_mode="none"),

    Checkpoint(28, "audio_quality",
        question="Is audio clean and usable?",
        lock="Audio quality",
        co_creative_mode="none"),

    Checkpoint(29, "coverage_check",
        question="Do we have everything needed?",
        lock="Complete footage",
        co_creative_mode="none"),

    Checkpoint(30, "production_lock",
        question="Is production complete?",
        lock="All raw materials",
        co_creative_mode="none"),

    # === PHASE 3: EDIT (Checkpoints 31-40) ===
    Checkpoint(31, "rough_cut",
        question="Does the structure work?",
        lock="Basic structure",
        co_creative_mode="mirror"),

    Checkpoint(32, "hook_edit",
        question="Do first 30 seconds command attention?",
        lock="Opening edit",
        co_creative_mode="contradict"),

    Checkpoint(33, "pacing_pass",
        question="Does pacing maintain engagement?",
        lock="Cut rhythm",
        co_creative_mode="mirror"),

    Checkpoint(34, "pattern_interrupt_edit",
        question="Are attention resets in place?",
        lock="Visual variety",
        co_creative_mode="none"),

    Checkpoint(35, "audio_edit",
        question="Is audio polished?",
        lock="Audio mix",
        co_creative_mode="none"),

    Checkpoint(36, "music_pass",
        question="Does music support without distracting?",
        lock="Music selection",
        co_creative_mode="amplify"),

    Checkpoint(37, "color_pass",
        question="Does color grade support tone?",
        lock="Color grade",
        co_creative_mode="none"),

    Checkpoint(38, "graphics_pass",
        question="Do graphics clarify without cluttering?",
        lock="Graphic elements",
        co_creative_mode="mirror"),

    Checkpoint(39, "final_cut",
        question="Is this the best it can be?",
        lock="Edit",
        co_creative_mode="mirror"),  # Full Mirror Test on edit

    Checkpoint(40, "edit_lock",
        question="Is the edit breakthrough-worthy?",
        lock="Final edit",
        co_creative_mode="mirror"),

    # === PHASE 4: PACKAGE (Checkpoints 41-45) ===
    Checkpoint(41, "thumbnail_generation",
        question="What are the thumbnail options?",
        lock="Nothing—exploration",
        co_creative_mode="amplify"),  # Generate 30 thumbnails

    Checkpoint(42, "thumbnail_selection",
        question="Which thumbnail is strongest?",
        lock="Top 3 thumbnails",
        co_creative_mode="contradict"),

    Checkpoint(43, "title_finalization",
        question="Does title + thumbnail = click?",
        lock="Title",
        co_creative_mode="contradict"),

    Checkpoint(44, "description_seo",
        question="Is description optimized?",
        lock="Description",
        co_creative_mode="none"),

    Checkpoint(45, "package_lock",
        question="Does package fulfill promise?",
        lock="Complete package",
        co_creative_mode="mirror"),

    # === PHASE 5: SHIP (Checkpoints 46-48) ===
    Checkpoint(46, "final_watch",
        question="Does Kent want to watch this?",
        lock="Quality approval",
        co_creative_mode="mirror"),

    Checkpoint(47, "upload_prep",
        question="Is everything ready for upload?",
        lock="Upload package",
        co_creative_mode="none"),

    Checkpoint(48, "ship",
        question="Published?",
        lock="Publication",
        co_creative_mode="none"),
]
```

### B.2 Album Track (52 Checkpoints)

```python
ALBUM_TRACK_CHECKPOINTS = [
    # === PHASE 0: SEED (Checkpoints 1-8) ===
    Checkpoint(1, "sonic_spark",
        question="What's the initial musical idea?",
        lock="Core melody/riff/progression",
        co_creative_mode="amplify"),  # Generate 50 variations

    Checkpoint(2, "emotional_target",
        question="What feeling should this evoke?",
        lock="Emotional destination",
        co_creative_mode="contradict"),

    Checkpoint(3, "lyric_concept",
        question="What is this song about?",
        lock="Thematic territory",
        co_creative_mode="amplify"),

    Checkpoint(4, "hook_hunt",
        question="What's the memorable element?",
        lock="Hook concept",
        co_creative_mode="amplify"),  # Generate 100 hook options

    Checkpoint(5, "contrast_check",
        question="What makes this different from other tracks?",
        lock="Uniqueness within album",
        co_creative_mode="contradict"),

    Checkpoint(6, "album_fit",
        question="Does this belong on this album?",
        lock="Album coherence",
        co_creative_mode="mirror"),

    Checkpoint(7, "surprise_element",
        question="Where's the unexpected moment?",
        lock="Surprise concept",
        co_creative_mode="contradict"),

    Checkpoint(8, "concept_lock",
        question="Is this seed worth developing?",
        lock="Song concept",
        co_creative_mode="mirror"),

    # === PHASE 1: DEVELOP (Checkpoints 9-24) ===
    # Lyrics
    Checkpoint(9, "verse_1_draft", ...),
    Checkpoint(10, "chorus_draft", ...),
    Checkpoint(11, "verse_2_draft", ...),
    Checkpoint(12, "bridge_draft", ...),
    Checkpoint(13, "lyric_no_compromises", ...),
    Checkpoint(14, "lyric_lock", ...),

    # Melody
    Checkpoint(15, "verse_melody", ...),
    Checkpoint(16, "chorus_melody", ...),
    Checkpoint(17, "bridge_melody", ...),
    Checkpoint(18, "melody_variation", ...),
    Checkpoint(19, "melody_lock", ...),

    # Arrangement
    Checkpoint(20, "structure_draft", ...),
    Checkpoint(21, "intro_outro", ...),
    Checkpoint(22, "dynamics_map", ...),
    Checkpoint(23, "arrangement_no_compromises", ...),
    Checkpoint(24, "arrangement_lock", ...),

    # === PHASE 2: RECORD (Checkpoints 25-36) ===
    # ... tracking, performances, takes

    # === PHASE 3: MIX (Checkpoints 37-46) ===
    # ... rough mix, balance, effects, polish

    # === PHASE 4: MASTER (Checkpoints 47-50) ===
    # ... mastering, sequencing, final approval

    # === PHASE 5: SHIP (Checkpoints 51-52) ===
    Checkpoint(51, "final_listen",
        question="Does Kent want to listen to this?",
        lock="Quality approval",
        co_creative_mode="mirror"),

    Checkpoint(52, "ship",
        question="Released?",
        lock="Publication",
        co_creative_mode="none"),
]
```

### B.3 Novel Chapter (36 Checkpoints)

```python
NOVEL_CHAPTER_CHECKPOINTS = [
    # === CONCEPT (1-6) ===
    Checkpoint(1, "chapter_purpose",
        question="What must this chapter accomplish?",
        lock="Narrative function",
        co_creative_mode="contradict"),

    # === DRAFT (7-18) ===
    # Scene-by-scene development with contradict mode

    # === VOICE (19-24) ===
    # Line-by-line Mirror Test

    # === POLISH (25-34) ===
    # Cut pass, clarity pass, no compromises

    # === SHIP (35-36) ===
    Checkpoint(35, "chapter_complete",
        question="Does this chapter pass all tests?",
        lock="Chapter quality",
        co_creative_mode="mirror"),

    Checkpoint(36, "chapter_lock",
        question="Ready for book integration?",
        lock="Final chapter",
        co_creative_mode="none"),
]
```

---

## Part C: Promise-Fulfillment (Package Before Content)

### The Insight

From YouTube research: **The thumbnail/title you make FIRST defines what you create.** This inverts traditional production.

```python
# Traditional: Create → Package
# Promise-First: Package → Create

class PromiseFulfillmentEngine:
    """
    The promise (thumbnail, title, cover, hook) is not packaging—
    it's a CREATIVE CONSTRAINT that focuses generation.
    """

    async def create_from_promise(
        self,
        domain: str,
        co_creative_session: CoCreativeSession,
    ) -> Work:
        # Step 1: Generate 50 promises (before any content exists)
        promises = await self.amplify_promises(domain, count=50)

        # Step 2: Kent selects the most compelling promise
        selected_promise = await kent_select(promises)

        # Step 3: Contradict the promise
        challenge = await self.contradict_promise(selected_promise)
        # "This promise implies X. Can you actually deliver X?"

        # Step 4: Defend or refine
        response = await kent_respond(challenge)
        final_promise = self.apply_response(selected_promise, response)

        # Step 5: Promise becomes creative constraint
        constraint = final_promise.as_creative_constraint()

        # Step 6: Create content that fulfills the promise
        content = await co_creative_session.create_with_constraint(constraint)

        # Step 7: Verify fulfillment
        fulfillment_score = self.measure_fulfillment(final_promise, content)

        if fulfillment_score < 0.8:
            # Promise and content misaligned
            # Either reshape content or reshape promise
            ...

        return Work(promise=final_promise, content=content)
```

### Promise Types by Domain

```python
PROMISE_TYPES = {
    "youtube": {
        "thumbnail": "Visual hook that creates curiosity",
        "title": "Text hook that completes the curiosity gap",
        "fulfillment_test": "Does video deliver what thumbnail+title promises?",
    },
    "music": {
        "album_art": "Visual that establishes sonic expectation",
        "album_title": "Name that frames the listening experience",
        "track_titles": "Names that create anticipation for each song",
        "fulfillment_test": "Does music deliver the promised emotional journey?",
    },
    "book": {
        "cover": "Visual that establishes genre and tone",
        "title": "Name that captures the book's essence",
        "blurb": "Promise of what reader will experience",
        "fulfillment_test": "Does book deliver the promised experience?",
    },
    "tv": {
        "logline": "One sentence that sells the show",
        "pilot_cold_open": "First scene that hooks viewer",
        "fulfillment_test": "Does series deliver the world the pilot promises?",
    },
}
```

---

## Part D: Production Rhythm (Batching for Efficiency)

### The Batching Principle

```python
class ProductionRhythm:
    """
    Breakthrough work requires depth, but depth requires sustainable pace.
    Batching enables both:
    - Deep focus during production
    - Recovery between batches
    - Efficiency through setup amortization
    """

    @dataclass(frozen=True)
    class RhythmPattern:
        batch_size: int              # How many works per batch
        production_window: timedelta  # Time for batch production
        release_interval: timedelta   # Time between releases
        recovery_window: timedelta    # Time between batches

        def annual_output(self) -> int:
            """How many works per year at this rhythm?"""
            cycle_time = self.production_window + self.recovery_window
            cycles_per_year = timedelta(days=365) / cycle_time
            return int(cycles_per_year * self.batch_size)

        def efficiency_gain(self) -> float:
            """Efficiency vs. one-at-a-time production."""
            # Setup amortization: set up once, produce many
            # Context retention: stay in mode longer
            # Flow state: reach flow once, produce multiple outputs
            return 1.0 + (0.4 * (self.batch_size / 4))

# Example rhythms
YOUTUBE_WEEKLY = RhythmPattern(
    batch_size=4,
    production_window=timedelta(days=14),  # 2 weeks to produce 4 videos
    release_interval=timedelta(days=7),     # Release one per week
    recovery_window=timedelta(days=7),      # 1 week recovery
)  # Annual output: ~52 videos, 1.4x efficiency

ALBUM_ANNUAL = RhythmPattern(
    batch_size=12,                          # 12-track album
    production_window=timedelta(weeks=20),  # 5 months to produce
    release_interval=timedelta(days=0),     # All at once
    recovery_window=timedelta(weeks=12),    # 3 months recovery
)  # Annual output: ~1.5 albums, 2.2x efficiency
```

### Rhythm Guards

```python
class RhythmGuards:
    """Protect quality from rhythm pressure."""

    @staticmethod
    def quality_over_schedule(
        work: Work,
        deadline: datetime,
        quality_threshold: float,
    ) -> ShipDecision:
        """
        NEVER ship below quality threshold.

        If deadline approaches and quality isn't there:
        1. Delay release (preferred)
        2. Pull from batch and replace
        3. Skip release and maintain rhythm with existing content

        NEVER: Ship subpar work to hit deadline
        """
        quality = measure_quality(work)

        if quality >= quality_threshold:
            return ShipDecision.SHIP

        if deadline - now() > timedelta(days=3):
            return ShipDecision.ITERATE

        if has_replacement_content():
            return ShipDecision.REPLACE

        return ShipDecision.DELAY  # Delay is better than shipping garbage

    @staticmethod
    def burnout_detection(
        recent_sessions: list[CoCreativeSession],
    ) -> BurnoutRisk:
        """
        Detect rhythm that kills creativity.

        Signs:
        - Surprise coefficient declining
        - Defense conviction weakening
        - Pivot count increasing
        - Session duration increasing
        """
        trend = analyze_trend(recent_sessions)

        if trend.surprise_declining and trend.conviction_weakening:
            return BurnoutRisk.HIGH

        if trend.session_duration_increasing:
            return BurnoutRisk.MODERATE

        return BurnoutRisk.LOW
```

---

## Part E: Integration with Co-Creative Engine

### Checkpoint as Co-Creative Moment

Each checkpoint is an opportunity for the co-creative engine:

```python
async def execute_checkpoint(
    checkpoint: Checkpoint,
    work: Work,
    session: CoCreativeSession,
) -> CheckpointResult:
    """Execute a checkpoint with appropriate co-creative mode."""

    if checkpoint.co_creative_mode == "amplify":
        # Generate options for this checkpoint's element
        options = await session.amplify(
            extract_element(work, checkpoint.lock),
            count=50,
        )
        selected = await kent_select(options)
        work = apply_selection(work, checkpoint.lock, selected)

    elif checkpoint.co_creative_mode == "contradict":
        # Challenge the current state of this element
        element = extract_element(work, checkpoint.lock)
        challenge = await session.contradict(element)
        response = await kent_respond(challenge)
        work = apply_response(work, response)

    elif checkpoint.co_creative_mode == "mirror":
        # Apply externalized Mirror Test
        result = await session.mirror_test(work)
        if result.level < ResonanceLevel.PROFOUND:
            # Iterate until it passes
            work = await iterate_until_passes(work, session)

    # Verify checkpoint passes
    result = checkpoint.verify(work)

    if result.passed:
        await session.lock(checkpoint, work)

    return result
```

### Progress Through Template

```python
async def progress_through_template(
    template: list[Checkpoint],
    initial_spark: Spark,
) -> Work:
    """Progress work through all checkpoints."""

    session = CoCreativeSession(spark=initial_spark)
    work = Work.from_spark(initial_spark)

    for checkpoint in template:
        result = await execute_checkpoint(checkpoint, work, session)

        if not result.passed:
            # Cannot proceed until checkpoint passes
            work = await iterate_until_checkpoint_passes(
                checkpoint, work, session,
            )

        # Update progress
        session.record_checkpoint(checkpoint, result)

        # Check for escape velocity
        if session.has_escape_velocity():
            # Work has found itself—accelerate through remaining checkpoints
            work = await accelerated_finish(work, template[checkpoint.number:])
            break

    return work
```

---

## AGENTESE Interface

```python
@node(
    path="self.muse.checkpoints",
    description="Checkpoint-driven production management",
    contracts={
        # Template operations
        "get_template": Contract(TemplateRequest, list[Checkpoint]),
        "customize_template": Contract(CustomizeRequest, list[Checkpoint]),

        # Checkpoint operations
        "execute_checkpoint": Contract(CheckpointRequest, CheckpointResult),
        "lock_checkpoint": Contract(LockRequest, LockedElement),
        "unlock_checkpoint": Contract(UnlockRequest, UnlockedElement),

        # Progress operations
        "get_progress": Contract(ProgressRequest, ProgressReport),
        "next_checkpoint": Contract(NextRequest, Checkpoint),

        # Rhythm operations
        "set_rhythm": Contract(RhythmRequest, RhythmPattern),
        "check_burnout": Contract(BurnoutRequest, BurnoutRisk),
    },
)
```

---

## Laws

| # | Law | Description |
|---|-----|-------------|
| 1 | checkpoint_complete | Each checkpoint fully completes before next begins |
| 2 | lock_integrity | Locked elements change only through explicit unlock |
| 3 | unlock_justification | Every unlock requires stated justification |
| 4 | promise_precedes | Promise (package) defined before content creation |
| 5 | quality_over_rhythm | Never ship below quality threshold for deadline |
| 6 | burnout_protection | Rhythm adjusts when burnout risk is high |
| 7 | co_creative_integration | Checkpoints use appropriate co-creative mode |

---

## Anti-Patterns

- **Checkpoint Skipping**: Jumping ahead without locking previous checkpoints
- **Premature Lock**: Locking before element passes quality gate
- **Silent Unlock**: Changing locked elements without formal unlock
- **Promise Drift**: Package that diverges from content during production
- **Rhythm Tyranny**: Shipping subpar work to maintain schedule
- **Template Rigidity**: Following template mechanically without co-creative depth

---

*"66 checkpoints is not bureaucracy. It's the difference between hoping for quality and guaranteeing it."*

*Part VI — Iteration Checkpoints & Production Rhythm | Aligned with Muse v2.0*
