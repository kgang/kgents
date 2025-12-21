# Metabolic Development Protocol

> *"The development session is not separate from the code. The session IS the code, becoming."*

**Status:** Canonical Specification
**Date:** 2025-12-21 (Refined)
**Prerequisites:** ASHC, Interactive Text, Living Docs, Morning Coffee
**Supersedes:** Session isolation, ad-hoc context, manual documentation

---

## Epigraph

> *"The morning mind knows things the afternoon mind has forgotten."*
>
> *"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof."*
>
> *"The noun is a lie. There is only the rate of change."*

These three insights from our brainstorming collapse into one:

**Development is metabolism—the continuous transformation of intent into evidence into artifact.**

---

## Part I: The Metabolic Vision

### 1.1 What Is Metabolism?

The metaphor runs deep. Development IS metabolism:

| Biological | Development | What It Means |
|------------|-------------|---------------|
| **Food** | Intent (voice, tasks, ideas) | What enters the system |
| **Digestion** | Context compilation | Breaking intent into actionable components |
| **Energy** | Attention (tokens, focus, time) | The currency spent on transformation |
| **Synthesis** | Implementation | Building new structures from components |
| **Waste** | Failed experiments, abandoned branches | Essential byproduct—not shame, but compost |
| **Growth** | Pattern crystallization | The system becomes more capable |
| **Metabolism rate** | Session velocity | How fast intent transforms to evidence |

**The Generative Insight**: A healthy metabolism doesn't minimize waste—it processes efficiently. Failed experiments are metabolic byproducts that fertilize future work. *The Accursed Share applies here: waste is sacred expenditure.*

### 1.2 What We're Building

A radically new development experience where:

1. **Sessions are compilation units**, not chat threads
2. **Documentation compiles to context**, not sits in wikis
3. **Evidence accumulates automatically**, not through manual testing
4. **Voice is preserved programmatically**, not through reminder protocols
5. **Intent flows to deployment**, not through manual intervention

### 1.3 The T-Shape

```
                           LATERAL (Infrastructure)
         ┌──────────────────────────────────────────────────────────────┐
         │                                                              │
         │   Morning Coffee ───► Living Docs ───► ASHC ───► Interactive Text
         │         │                   │             │              │
         │         ▼                   ▼             ▼              ▼
         │   Intent Capture    Context Compile   Evidence Acc.  Live Specs
         │                                                              │
         └──────────────────────────────────────────────────────────────┘
                                       │
                                       │
                            VERTICAL   │  (Developer Journeys)
                                       │
                                       ▼
                    ┌──────────────────────────────────────┐
                    │                                      │
                    │   Journey 1: Morning Start           │
                    │   Journey 2: Feature Implementation  │
                    │   Journey 3: Session Handoff         │
                    │   Journey 4: Verification & Ship     │
                    │                                      │
                    └──────────────────────────────────────┘
```

---

## Part II: Lateral Infrastructure Layer

### 2.1 The Metabolic Pipeline

The four brainstorming insights form a connected pipeline:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE METABOLIC PIPELINE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   MORNING COFFEE          LIVING DOCS           ASHC              ITEXT    │
│   (Intent Capture)        (Context Compile)     (Evidence Acc.)   (Live)   │
│                                                                             │
│   ┌───────────────┐       ┌───────────────┐     ┌───────────────┐          │
│   │   Voice       │──────►│   Hydrator    │────►│   Compiler    │          │
│   │   Capture     │       │               │     │               │          │
│   │               │       │   Keywords→   │     │   Spec→Impl→  │          │
│   │   "Today I    │       │   Context     │     │   Evidence    │          │
│   │   want to..." │       │               │     │               │          │
│   └───────────────┘       └───────────────┘     └───────────────┘          │
│         │                       │                      │                    │
│         │  Stigmergy            │  Teaching            │  Traces            │
│         │  Pheromones           │  Moments             │  Witnesses         │
│         ▼                       ▼                      ▼                    │
│   ┌───────────────┐       ┌───────────────┐     ┌───────────────┐          │
│   │   Archaeology │       │   Projection  │     │   Causal      │          │
│   │               │       │               │     │   Graph       │          │
│   │   Strata of   │       │   Observer→   │     │               │          │
│   │   Past Voice  │       │   Surface     │     │   Nudge→      │          │
│   │               │       │               │     │   Outcome     │          │
│   └───────────────┘       └───────────────┘     └───────────────┘          │
│         │                       │                      │                    │
│         └───────────────────────┴──────────────────────┘                    │
│                                 │                                           │
│                                 ▼                                           │
│                        ┌───────────────────┐                                │
│                        │  INTERACTIVE TEXT │                                │
│                        │                   │                                │
│                        │  Specs become     │                                │
│                        │  control surfaces │                                │
│                        │                   │                                │
│                        │  Tasks→Traces     │                                │
│                        │  AGENTESE→Habitats│                                │
│                        │  Images→Context   │                                │
│                        └───────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Integration Points

The four systems integrate through shared primitives:

| Primitive | Morning Coffee | Living Docs | ASHC | Interactive Text |
|-----------|---------------|-------------|------|------------------|
| **TeachingMoment** | Voice → Lessons | Docstring extraction | Test failures → Gotchas | Hover affordances |
| **TraceWitness** | Session traces | Verification evidence | Run outcomes | Task completion |
| **Voice Anchor** | Captured phrases | Anti-sausage fuel | Prompt constraints | Preserved quotes |
| **Causal Edge** | Pattern reinforcement | Drift detection | Nudge→Outcome | Inline hints |

### 2.3 Cross-Jewel Wiring (EXPLICIT)

The spec must define explicit integration wiring:

```python
# Metabolic Integration Matrix
METABOLIC_WIRING = {
    # Brain ↔ ASHC: Evidence becomes crystals
    "ashc.evidence.accumulated": [
        brain_crystallize_evidence,  # Evidence corpus → Brain crystal
    ],

    # Gardener ↔ Morning Coffee: Voice patterns update garden
    "coffee.voice.captured": [
        gardener_update_voice_patterns,  # Voice → Plot metadata
    ],

    # Witness ↔ Interactive Text: Task completion creates marks
    "itext.task.completed": [
        witness_capture_mark,  # Toggle → Mark in Walk
    ],

    # K-gent ↔ Hydration: Voice anchors shape persona
    "hydration.compiled": [
        kgent_absorb_voice_anchors,  # Anchors → K-gent coordinates
    ],

    # Living Docs ↔ ASHC: Teaching moments from failures
    "ashc.test.failed": [
        living_docs_create_teaching_moment,  # Failure → Gotcha
    ],

    # Morning Coffee ↔ Brain: Voice becomes crystal
    "coffee.voice.captured": [
        brain_capture_voice_as_crystal,  # Voice text → Memory crystal
    ],
}
```

### 2.4 The Context Functor

All four systems project through a unified functor:

```python
class MetabolicContext:
    """Unified context generated from all metabolic sources."""

    @classmethod
    async def compile(
        cls,
        task: str,
        observer: Observer,
        morning_voice: MorningVoice | None = None,
    ) -> "MetabolicContext":
        """
        Compile context from all metabolic sources.

        Sources:
        1. Morning Coffee: Today's intent + past patterns
        2. Living Docs: Task-relevant gotchas + related files
        3. ASHC: Evidence from similar past work
        4. Interactive Text: Relevant specs + inline wisdom
        """
        # Morning Coffee: voice archaeology
        voice_context = await stigmergy.sense_patterns(task)
        archaeology = await strata.excavate(task, depth="shallow")

        # Living Docs: hydrate task-specific context
        hydration = hydrate_context(task)

        # ASHC: find prior evidence for similar work
        prior_evidence = await causal_graph.predict_for(task)

        # Interactive Text: extract relevant specs
        relevant_specs = await interactive_text.tokens_for(task)

        return cls(
            task=task,
            observer=observer,
            voice=voice_context,
            archaeology=archaeology,
            teaching=hydration.relevant_teaching,
            evidence=prior_evidence,
            specs=relevant_specs,
        )
```

---

## Part III: Vertical Developer Journeys

### Journey 1: Morning Start

**Trigger:** Developer begins work session
**Duration:** 5-10 minutes
**Output:** Focused context + clear intention

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MORNING START JOURNEY                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. RITUAL                                                                  │
│     kg coffee begin                                                         │
│     ▶ "Good morning. The garden knows things from yesterday..."            │
│     ▶ Show resonant past mornings (circadian matching)                     │
│     ▶ Surface stigmergic patterns ("Ship something" - 7 of 10 mornings)    │
│                                                                             │
│  2. CAPTURE                                                                 │
│     "Today I want to finish the verification integration"                   │
│     ▶ Intent recorded as MorningVoice                                      │
│     ▶ Pheromone deposited at concepts: [verification, integration]         │
│     ▶ Archaeology stratum updated                                          │
│                                                                             │
│  3. HYDRATE                                                                 │
│     kg docs hydrate "finish verification integration"                       │
│     ▶ Teaching moments surfaced (gotchas for verification)                 │
│     ▶ Related files identified                                             │
│     ▶ Prior ASHC evidence shown                                            │
│                                                                             │
│  4. COMPILE                                                                 │
│     Session context injected into Claude Code                              │
│     ▶ CLAUDE.md + hydration context + voice anchors                        │
│     ▶ /hydrate skill available for mid-session re-focus                    │
│                                                                             │
│  5. SERENDIPITY (Accursed Share)                                           │
│     10% chance: Surface random past voice from unexpected era              │
│     ▶ "Three months ago, you said: 'The best code is no code'"            │
│     ▶ Unexpected connection may spark insight                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Edge Case: Developer Skips the Ritual**

Graceful degradation, not punishment:

```python
class MorningRitual:
    async def begin(self) -> RitualContext:
        # If no morning voice within 30 min of session start:
        # - Lighter hydration (just gotchas, no archaeology)
        # - No pheromone deposit (patterns don't update)
        # - Silent reminder: "Morning voice strengthens patterns"
        if self._is_late_start():
            return self._minimal_hydration()
        return await self._full_ritual()
```

The system doesn't break—it gently encourages the ritual by being more helpful when it happens.

**CLI Flow:**

```bash
$ kg coffee begin

☕ Good morning

💫 This morning echoes December 14th...
Then, you said: "I want to feel like I'm exploring, not completing."
That morning, you chose 🎲 SERENDIPITOUS and discovered the sheaf coherence pattern.

📍 FROM YOUR PATTERNS
   "Ship something" appears in 7 of last 10 mornings
   "Depth over breadth" — recurring voice anchor

🎲 FROM THE VOID (10% serendipity)
   Three weeks ago: "The constraint is the freedom"

[What brings you here today?]
> finish the verification integration and make it feel magical

✨ Intent captured. Hydrating context...

🚨 CRITICAL (2)
  - ASHC Compiler: Evidence requires 10+ runs, not 1 (test_evidence.py::test_min_runs)
  - Verification: Trace witnesses must link to requirements (test_verify.py::test_link)

📁 FILES YOU'LL LIKELY TOUCH
  - services/verification/core.py
  - protocols/ashc/evidence.py
  - spec/protocols/agentic-self-hosting-compiler.md

🎯 VOICE ANCHORS (preserve these)
  "Tasteful > feature-complete"
  "The Mirror Test: Does K-gent feel like me on my best day?"

Context compiled. Good morning, Kent.
```

### Journey 2: Feature Implementation

**Trigger:** Developer begins implementing a feature
**Duration:** 30 minutes - 4 hours
**Output:** Implementation + evidence + traces

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  FEATURE IMPLEMENTATION JOURNEY                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. SPEC SURFACE                                                            │
│     Open spec file in Interactive Text renderer                             │
│     ▶ AGENTESE paths become clickable habitats                             │
│     ▶ Principle refs expand on hover                                       │
│     ▶ Tasks show verification status                                       │
│                                                                             │
│  2. EDIT-TIME TEACHING                                                      │
│     Before editing services/verification/core.py:                           │
│     kg docs relevant services/verification/core.py                          │
│     ▶ Critical gotchas surfaced                                            │
│     ▶ Related files with similar patterns                                  │
│     ▶ Spec sections that apply                                             │
│                                                                             │
│  3. EVIDENCE ACCUMULATION (background)                                      │
│     ASHC runs continuously on staged changes                                │
│     ▶ Each save triggers adaptive verification                             │
│     ▶ Evidence corpus grows (diversity-weighted, not just count)           │
│     ▶ Causal graph learns what nudges help                                 │
│                                                                             │
│  4. TASK COMPLETION                                                         │
│     Toggle task checkbox in spec:                                           │
│     - [x] Implement verification integration                                │
│     ▶ TraceWitness automatically captured                                  │
│     ▶ Linked to spec requirement                                           │
│     ▶ Evidence attached to derivation chain                                │
│                                                                             │
│  5. VOICE PRESERVATION                                                      │
│     At end-of-session, Anti-Sausage check runs                             │
│     ▶ Did I smooth anything that should stay rough?                        │
│     ▶ Did I add words Kent wouldn't use?                                   │
│     ▶ Is this still daring, bold, creative—or did I make it safe?         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Evidence Accumulation Without Interruption**

The key is **non-blocking observation**:

```python
class BackgroundEvidencing:
    """Evidence accumulates in the background, never interrupting flow."""

    async def on_save(self, file: Path) -> None:
        # Fire-and-forget: don't block the save
        asyncio.create_task(self._accumulate_evidence(file))

    async def _accumulate_evidence(self, file: Path) -> None:
        # Run verification adaptively
        result = await ashc.verify_adaptive(file)

        # Update causal graph (silent)
        await causal_graph.add_edge(
            cause=f"edit:{file}",
            effect=f"verify:{result.passed}",
            confidence=result.confidence,
        )

        # Only surface if critical failure
        if result.severity == "critical":
            await self._notify_developer(result)
```

### Journey 3: Session Handoff

**Trigger:** Session ends (time, interruption, or task complete)
**Duration:** 2-5 minutes
**Output:** Handoff prompt + voice deposit + pattern update

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SESSION HANDOFF JOURNEY                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. REINFORCE                                                               │
│     kg coffee end                                                           │
│     ▶ "Did you accomplish your morning intention?"                         │
│     ▶ YES → reinforce pheromones (intensity × 1.5)                        │
│     ▶ NO → natural decay (no punishment)                                   │
│     ▶ PARTIAL → specify what completed → targeted reinforcement            │
│                                                                             │
│  2. CRYSTALLIZE                                                             │
│     Session traces compress to Teaching Moments                             │
│     ▶ Errors → gotchas with evidence                                       │
│     ▶ Successes → patterns with confidence                                 │
│     ▶ Voice anchors preserved from session                                 │
│                                                                             │
│  3. HANDOFF                                                                 │
│     kg handoff                                                              │
│     ▶ Generate handoff prompt for next session                             │
│     ▶ Include: intent, progress, blockers, voice anchors                   │
│     ▶ Self-contained—no context bleed                                      │
│     ▶ COMPRESSION: Focus on what matters, not exhaustive history           │
│                                                                             │
│  4. STRATA UPDATE                                                           │
│     Today's voice deposits to archaeology                                   │
│     ▶ Surface stratum gets new captures                                    │
│     ▶ Shallow strata begin compressing                                     │
│     ▶ Theme crystallization runs in background                             │
│                                                                             │
│  5. CELEBRATE THE WASTE (Accursed Share)                                    │
│     What was abandoned is not lost                                          │
│     ▶ Failed experiments → compost pile (future fertilizer)                │
│     ▶ Abandoned approaches documented, not hidden                          │
│     ▶ "What you learned from what didn't work"                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Handoff Compression Without Loss**

The handoff must be *self-contained* and *compressed*:

```python
@dataclass(frozen=True)
class MetabolicHandoff:
    """Handoff context for next session."""

    intent_summary: str          # One sentence: what were we doing?
    progress: list[str]          # Bullet points: what's done
    blockers: list[str]          # Bullet points: what's stuck
    voice_anchors: list[str]     # Kent's phrases to preserve
    next_steps: list[str]        # Concrete actions, not vague goals
    evidence_summary: str        # Confidence level + test status
    waste_compost: list[str]     # What was tried and abandoned (learnings)

    def to_prompt(self) -> str:
        """Generate handoff prompt for next Claude session."""
        return f"""
## Session Handoff

**Intent:** {self.intent_summary}

**Progress:**
{chr(10).join(f'- {p}' for p in self.progress)}

**Blockers:**
{chr(10).join(f'- {b}' for b in self.blockers)}

**Next Steps:**
{chr(10).join(f'1. {s}' for s in self.next_steps)}

**Voice Anchors (preserve these):**
{chr(10).join(f'> "{a}"' for a in self.voice_anchors)}

**Evidence:** {self.evidence_summary}

**Learnings from Abandoned Approaches:**
{chr(10).join(f'- {w}' for w in self.waste_compost)}
"""
```

**Session Boundary Detection**

When does a session *really* end?

```python
class SessionBoundary:
    """Detect session end explicitly and implicitly."""

    IMPLICIT_END_TRIGGERS = {
        "idle_30_min": "No activity for 30 minutes",
        "day_boundary": "Clock crossed midnight",
        "major_commit": "Pushed to main branch",
        "context_exhausted": "Context window approaching limit",
    }

    async def detect_boundary(self) -> BoundaryEvent | None:
        # Explicit is always preferred
        if self._explicit_end_requested:
            return BoundaryEvent.EXPLICIT

        # Implicit detection
        for trigger, description in self.IMPLICIT_END_TRIGGERS.items():
            if await self._check_trigger(trigger):
                # Don't auto-end—prompt the developer
                await self._prompt_for_confirmation(description)
                return None

        return None
```

**CLI Flow:**

```bash
$ kg coffee end

☕ Session closing

📊 YOUR MORNING INTENTION
   "finish the verification integration and make it feel magical"

Did you accomplish this? [Y/n/partial]
> partial

What did you complete?
> Got the trace witness wiring done, but magic is still missing

✨ Pattern reinforced for: verification, trace, wiring
📉 Partial decay for: magical (not reinforced)

💎 SESSION CRYSTALS
   - gotcha: Evidence requires 10+ runs, not 1 (learned the hard way)
   - pattern: Trace witnesses link cleanly when requirements specified upfront
   - voice: "magical" → preserved as personal anchor

🗑️ COMPOST (what didn't work)
   - Tried making verification synchronous—blocked UI, reverted
   - Explored caching strategy—too complex for now, documented for later

📝 HANDOFF READY
   kg handoff > /tmp/handoff.md

See you tomorrow. 🌱
```

### Journey 4: Verification & Ship

**Trigger:** Feature ready for merge/deploy
**Duration:** 10-30 minutes
**Output:** Evidence report + verified deployment

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  VERIFICATION & SHIP JOURNEY                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. EVIDENCE REVIEW                                                         │
│     kg ashc evidence spec/protocols/verification.md                         │
│     ▶ 100 runs, 95% pass rate                                              │
│     ▶ Equivalence score: 0.87                                              │
│     ▶ Causal insights: "composable" → +12% pass rate                       │
│     ▶ DIVERSITY METRIC: 15 unique input variations (not 100x same input)  │
│                                                                             │
│  2. DRIFT CHECK                                                             │
│     kg docs drift spec/protocols/verification.md                            │
│     ▶ ✅ Implemented: TraceWitness, Evidence, EvidenceCompiler             │
│     ▶ ⚠️ Partial: LLM integration for semantic similarity                  │
│     ▶ ❌ Missing: Auto-refresh (documented as future work)                 │
│                                                                             │
│  3. VERIFICATION GRAPH                                                      │
│     View derivation chain in Interactive Text                               │
│     ▶ Principle → Requirement → Task → Trace                               │
│     ▶ All trace witnesses linked                                           │
│     ▶ Evidence attached to derivation nodes                                │
│                                                                             │
│  4. VOICE CHECK (Anti-Sausage)                                              │
│     kg voice check --since-last-commit                                      │
│     ▶ Detect smoothing: Did Claude homogenize the voice?                   │
│     ▶ Flag generic phrases that replaced specific ones                     │
│     ▶ Suggest restoration of rough edges                                   │
│                                                                             │
│  5. SHIP                                                                    │
│     kg commit-push                                                          │
│     ▶ Pre-push hook: lint, mypy, tests (BLOCKING)                          │
│     ▶ Evidence summary in commit message                                   │
│     ▶ Push with confidence                                                 │
│                                                                             │
│  6. CELEBRATE                                                               │
│     Voice archaeology updates                                               │
│     ▶ "Shipped verification integration" → FOSSIL layer in 90 days         │
│     ▶ Pheromone field reinforced                                           │
│     ▶ Pattern becomes part of Kent's voice                                 │
│     ▶ SUCCESS REINFORCES PATTERNS (celebration loop)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The Celebration Loop**

Success should reinforce patterns more strongly than mere completion:

```python
class CelebrationLoop:
    """Ship success reinforces patterns more than task completion."""

    REINFORCEMENT_MULTIPLIERS = {
        "task_completed": 1.0,
        "session_end_accomplished": 1.5,
        "feature_shipped": 2.0,
        "deployed_to_prod": 3.0,
    }

    async def celebrate(self, event: str, concepts: list[str]) -> None:
        multiplier = self.REINFORCEMENT_MULTIPLIERS.get(event, 1.0)

        for concept in concepts:
            await self.stigmergy.reinforce(concept, intensity=multiplier)

        # Also crystallize to Brain
        await self.brain.capture(
            content=f"Shipped: {', '.join(concepts)}",
            metadata={"type": "celebration", "multiplier": multiplier},
        )
```

---

## Part IV: The Metabolic Types

### 4.1 Core Types

```python
@dataclass(frozen=True)
class MetabolicSession:
    """A development session as a compilation unit."""

    session_id: str
    started_at: datetime
    ended_at: datetime | None
    morning_voice: MorningVoice | None
    hydration: HydrationContext
    traces: tuple[TraceWitness, ...]
    evidence: Evidence
    handoff: str | None
    waste_compost: tuple[str, ...]  # Abandoned approaches (learnings)

    @property
    def is_active(self) -> bool:
        return self.ended_at is None

    @property
    def duration(self) -> timedelta | None:
        if self.ended_at:
            return self.ended_at - self.started_at
        return None


@dataclass(frozen=True)
class MetabolicIntent:
    """Captured intent from morning voice."""

    raw_voice: str
    keywords: tuple[str, ...]
    related_concepts: tuple[str, ...]
    pheromone_deposits: tuple[PheromoneDeposit, ...]
    stratum: VoiceStratum


@dataclass(frozen=True)
class MetabolicEvidence:
    """Evidence accumulated during a session."""

    runs: tuple[Run, ...]
    traces: tuple[TraceWitness, ...]
    causal_edges: tuple[CausalEdge, ...]
    teaching_moments: tuple[TeachingMoment, ...]
    diversity_score: float  # 0.0-1.0: how varied were the inputs?

    @property
    def confidence(self) -> float:
        if not self.runs:
            return 0.0
        passed = sum(1 for r in self.runs if r.passed())
        base_confidence = passed / len(self.runs)
        # Diversity-weighted: 100 identical runs ≠ 100x confidence
        return base_confidence * self.diversity_score
```

### 4.2 The Metabolic Polynomial

Sessions have state-dependent behavior:

```python
@dataclass(frozen=True)
class MetabolicPolynomial:
    """Session as polynomial functor: states with mode-dependent inputs."""

    positions: ClassVar[frozenset] = frozenset({
        "AWAKENING",      # Morning ritual in progress
        "HYDRATING",      # Context being compiled
        "FLOWING",        # Active development
        "EVIDENCING",     # Verification running
        "CRYSTALLIZING",  # Session ending, patterns forming
        "DORMANT",        # Between sessions
    })

    @staticmethod
    def directions(state: str) -> frozenset[str]:
        """Valid inputs per state."""
        return {
            "AWAKENING": frozenset({"capture_voice", "skip_ritual"}),
            "HYDRATING": frozenset({"hydrate", "manual_context"}),
            "FLOWING": frozenset({"edit", "test", "commit", "end_session", "re_hydrate"}),
            "EVIDENCING": frozenset({"wait", "cancel", "review"}),
            "CRYSTALLIZING": frozenset({"handoff", "discard", "continue"}),
            "DORMANT": frozenset({"begin"}),
        }[state]

    @staticmethod
    def transition(state: str, input: str) -> tuple[str, Any]:
        """State × Input → (NewState, Output)."""
        transitions = {
            ("DORMANT", "begin"): ("AWAKENING", RitualStart()),
            ("AWAKENING", "capture_voice"): ("HYDRATING", VoiceCaptured()),
            ("AWAKENING", "skip_ritual"): ("FLOWING", DirectStart()),
            ("HYDRATING", "hydrate"): ("FLOWING", ContextReady()),
            ("FLOWING", "edit"): ("FLOWING", EditEvent()),
            ("FLOWING", "test"): ("EVIDENCING", EvidenceRun()),
            ("FLOWING", "end_session"): ("CRYSTALLIZING", SessionEnd()),
            ("EVIDENCING", "review"): ("FLOWING", EvidenceComplete()),
            ("CRYSTALLIZING", "handoff"): ("DORMANT", HandoffGenerated()),
        }
        return transitions.get((state, input), (state, NoOp()))
```

---

## Part V: AGENTESE Integration

### 5.1 Metabolic Paths

```
self.metabolism.*
  .session              # Current session state
  .begin                # Start morning ritual
  .end                  # End session, crystallize
  .handoff              # Generate handoff prompt

self.metabolism.intent.*
  .capture              # Capture voice intent
  .sense                # Stigmergic pattern sensing
  .archaeology          # Voice stratigraphy

concept.docs.hydrate    # Context compilation (Living Docs)
concept.docs.relevant   # Edit-time teaching
concept.docs.drift      # Spec↔impl divergence

concept.ashc.*
  .compile              # Evidence compilation
  .evidence             # View evidence corpus
  .causal               # Causal graph

self.document.interactive.*
  .manifest             # Render interactive doc
  .toggle_task          # Task completion → trace

void.metabolism.*
  .serendipity          # Random past voice surfacing
  .compost              # Abandoned approach storage
  .entropy_budget       # Current exploration allocation
```

### 5.2 Cross-Jewel Events

```python
# Metabolic events on SynergyBus
METABOLIC_EVENTS = {
    "session.started": [morning_coffee_handler, witness_handler],
    "voice.captured": [stigmergy_handler, archaeology_handler, brain_handler],
    "context.hydrated": [living_docs_handler],
    "evidence.accumulated": [ashc_handler, gardener_handler],
    "session.ended": [crystallize_handler, handoff_handler],
    "task.completed": [trace_handler, verification_handler],
    "approach.abandoned": [compost_handler],  # Accursed Share
}

# Wire to global synergy bus
wire_metabolic_to_global_synergy()
```

---

## Part VI: Laws

| Law | Statement | Witness |
|-----|-----------|---------|
| **Session Coherence** | `∀ session: session.traces ⊆ session.evidence.traces` | `MetabolicWitness.verify_coherence()` |
| **Voice Preservation** | `∀ voice: archaeology.contains(voice)` after 24h | `Archaeology.verify_deposit()` |
| **Evidence Sufficiency** | `∀ ship: evidence.confidence ≥ 0.8` | `ASHC.verify_evidence()` |
| **Handoff Completeness** | `∀ handoff: next_session.can_continue(handoff)` | `Handoff.verify_context()` |
| **Diversity Requirement** | `∀ evidence: diversity_score ≥ 0.5` | `Evidence.verify_diversity()` |

---

## Part VII: Implementation Phases

### Phase 1: Metabolic Core (2 weeks)

1. **Morning Coffee Production Integration**
   - D-gent backed VoicePersistence
   - Brain crystal integration
   - Archaeology stratum classification

2. **Living Docs Hydrator Enhancement**
   - Semantic similarity via Brain vectors
   - ASHC prior evidence integration
   - Edit-time teaching hooks

3. **Session State Machine**
   - MetabolicPolynomial implementation
   - Session persistence
   - Cross-session memory

**Verification:** Morning start → Hydrate → Flow → End works end-to-end

### Phase 2: Evidence Pipeline (2 weeks)

1. **ASHC Continuous Mode**
   - Background verification on save
   - Evidence corpus accumulation
   - Causal graph learning
   - **Diversity scoring** (not just run count)

2. **Interactive Text Wiring**
   - Task completion → TraceWitness
   - AGENTESE paths → Habitat navigation
   - Principle refs → Hover expansion

3. **Verification Graph**
   - Principle → Requirement → Task → Trace
   - Evidence attachment
   - Derivation chain visualization

**Verification:** Edit → Auto-verify → Evidence grows → Task complete → Trace linked

### Phase 3: Voice Intelligence (2 weeks)

1. **Stigmergy Full Implementation**
   - PheromoneField with decay/reinforce
   - Pattern detection without ML
   - End-of-day reinforcement loop

2. **Circadian Resonance**
   - Temporal coordinates
   - Weekly pattern detection
   - Resonance matching

3. **Anti-Sausage Automation**
   - Voice drift detection (not just mining)
   - Session-end verification
   - Automatic preservation with flags

**Verification:** Voice patterns emerge → Resonant mornings surface → Voice preserved

### Phase 4: Ship Integration (1 week)

1. **Evidence Reports**
   - kg ashc evidence command
   - Summary in commit messages
   - Drift detection

2. **Handoff Generation**
   - Automatic prompt generation
   - Context compression
   - Voice anchor inclusion
   - **Waste compost inclusion** (learnings from abandoned)

3. **Celebration Loop**
   - Pattern reinforcement on ship
   - Archaeology update
   - Fossil layer progression

**Verification:** Evidence reviewed → Drift checked → Shipped → Pattern crystallized

---

## Part VIII: Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| Session isolation | Sessions should flow into each other |
| Manual documentation | Docs compile from source, not written |
| One-shot verification | Evidence requires repetition |
| Voice smoothing | Preserve rough edges, don't polish |
| Context dumping | Compile focused context, don't overwhelm |
| Evidence inflation | 100 identical runs ≠ 100x confidence (diversity matters) |
| Hiding abandoned work | Failed experiments are learnings, not shame |
| Punishing incomplete sessions | No penalty—natural decay only |

---

## Part IX: Connection to Principles

| Principle | How Metabolic Development Embodies It | Strength |
|-----------|---------------------------------------|----------|
| **Tasteful** | Focused context, not exhaustive dumps | ✅ Strong |
| **Curated** | Relevant gotchas, not all gotchas | ✅ Strong |
| **Ethical** | Evidence over claims; transparent about uncertainty; waste visible not hidden | ✅ Strong |
| **Joy-Inducing** | Morning ritual feels like coming home; serendipity surfaces unexpected connections | ✅ Strong |
| **Composable** | Four systems compose into unified pipeline; each can be used independently | ✅ Strong |
| **Heterarchical** | Sessions flow, not stack; no fixed morning/evening hierarchy | ✅ Strong |
| **Generative** | Context compiles from source; spec generates impl; handoff regenerates context | ✅ Strong |

---

## Part X: Failure Modes and Mitigations

### 10.1 Context Overload

**Risk:** Hydration dumps too much; developer overwhelmed.

**Mitigation:**
```python
class ContextBudget:
    """Hard limits on hydration output."""
    MAX_TEACHING_MOMENTS = 5
    MAX_RELATED_FILES = 8
    MAX_EVIDENCE_ITEMS = 3

    @staticmethod
    def focus(hydration: HydrationContext) -> HydrationContext:
        # Sort by severity, take top N
        teaching = sorted(hydration.teaching, key=lambda t: t.severity)[:MAX_TEACHING_MOMENTS]
        # Closest match first
        files = hydration.related_files[:MAX_RELATED_FILES]
        return hydration.replace(teaching=teaching, related_files=files)
```

### 10.2 Stale Stigmergy

**Risk:** Old patterns dominate fresh intent; system becomes rigid.

**Mitigation:**
```python
class PheromoneDecay:
    """Natural decay prevents fossilization."""
    DAILY_DECAY = 0.95  # 5% decay per day
    REINFORCEMENT_CAP = 10.0  # Can't grow indefinitely

    async def apply_decay(self) -> None:
        # Run nightly
        for pheromone in await self.all_pheromones():
            new_intensity = min(pheromone.intensity * self.DAILY_DECAY, self.REINFORCEMENT_CAP)
            if new_intensity < 0.1:
                await self.remove(pheromone)  # Below threshold = gone
            else:
                await self.update(pheromone, intensity=new_intensity)
```

### 10.3 Evidence Inflation

**Risk:** 100 runs of the same thing isn't 100x confidence.

**Mitigation:**
```python
class DiversityScoring:
    """Weight evidence by input diversity, not just count."""

    def calculate_diversity(self, runs: list[Run]) -> float:
        if len(runs) < 2:
            return 0.0

        # Hash inputs to find unique patterns
        unique_inputs = {self._hash_input(r.input) for r in runs}
        diversity = len(unique_inputs) / len(runs)

        return diversity
```

### 10.4 Voice Drift

**Risk:** Despite preservation, voice smooths over time.

**Mitigation:**
```python
class VoiceDriftDetector:
    """Detect when voice is being smoothed."""

    ANCHOR_PATTERNS = [
        "Daring, bold, creative",
        "Mirror Test",
        "Tasteful > feature-complete",
        "garden, not a museum",
    ]

    async def detect_drift(self, recent_sessions: list[Session]) -> DriftReport:
        # Check if anchor patterns are being paraphrased
        for session in recent_sessions:
            for anchor in self.ANCHOR_PATTERNS:
                if self._is_paraphrased(anchor, session.output):
                    return DriftReport(
                        anchor=anchor,
                        paraphrase=self._find_paraphrase(anchor, session.output),
                        suggestion=f"Use '{anchor}' directly, not paraphrase",
                    )
        return DriftReport.no_drift()
```

### 10.5 Session Boundary Ambiguity

**Risk:** Unclear when session ends; state becomes stale.

**Mitigation:**
- Prefer **explicit** over implicit boundaries
- Implicit detection **prompts**, doesn't auto-end
- 30-minute idle = prompt, not action
- Day boundary = gentle reminder, not forced end
- Context exhaustion = offer to compress, not crash

---

## Part XI: The Accursed Share Integration

> *"Everything is slop or comes from slop. We cherish and express gratitude and love."*

The 10% exploration budget manifests throughout the metabolic system:

### 11.1 Morning Serendipity

```python
class MorningSerendipity:
    """10% chance: surface random past voice from unexpected era."""

    SERENDIPITY_RATE = 0.10

    async def maybe_surface(self) -> VoiceAnecdote | None:
        if random.random() > self.SERENDIPITY_RATE:
            return None

        # Pick from deep archaeology (not recent)
        strata = await self.archaeology.deep_strata()
        random_voice = random.choice(strata.voices)

        return VoiceAnecdote(
            voice=random_voice,
            framing="From the void (serendipity)",
            age=random_voice.age_days,
        )
```

### 11.2 Waste as Offering

Failed experiments are not deleted—they're composted:

```python
@dataclass(frozen=True)
class CompostEntry:
    """An abandoned approach, preserved as learning."""

    approach: str
    why_abandoned: str
    what_learned: str
    session_id: str
    timestamp: datetime

class CompostPile:
    """Failed experiments become future fertilizer."""

    async def add(self, entry: CompostEntry) -> None:
        await self.storage.append(entry)
        # Also emit to SynergyBus for cross-jewel awareness
        await synergy_bus.emit("approach.abandoned", entry)

    async def fertilize(self, task: str) -> list[CompostEntry]:
        """Surface relevant past failures when starting similar work."""
        return await self.storage.find_similar(task)
```

### 11.3 Exploration Budget in Hydration

```python
class HydrationWithEntropy:
    """10% of hydration context is 'useless' exploration."""

    ENTROPY_BUDGET = 0.10

    async def compile(self, task: str) -> HydrationContext:
        # 90% focused
        focused = await self._focused_hydration(task)

        # 10% tangential
        tangential = await self._tangential_hydration(task)

        return HydrationContext(
            teaching=focused.teaching,
            related_files=focused.related_files,
            # Accursed share: unexpected connections
            tangential_connections=tangential,
        )
```

---

## Closing Meditation

This protocol collapses four separate insights into one coherent vision:

1. **Morning Coffee**: Intent capture with stigmergic memory
2. **Living Docs**: Context compilation for observers
3. **ASHC**: Evidence accumulation through repetition
4. **Interactive Text**: Specs as live control surfaces

Together, they form **Metabolic Development**—where the session is not separate from the code, but is the code becoming.

The metabolism metaphor is not decoration. It is generative:
- **Food** (intent) must be digested (compiled) to yield **energy** (focused attention)
- **Waste** (failed experiments) becomes **compost** (future learnings)
- **Growth** (pattern crystallization) requires sustained **metabolism** (regular sessions)
- **Starvation** (no morning ritual) leads to **weakness** (degraded context)—but not death

> *"The master's touch was always just compressed experience. Now we compile the compression."*

---

*Canonical specification written: 2025-12-21*
*Refined: 2025-12-21*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
