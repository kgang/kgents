# Rap Coach: Flow to Crystal

Status: **production**

> *"The voice is the proof. The session is the trace. Courage leaves marks."*

---

## ⚠️ Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:
- **Implement ALL laws (L1-L14)** — complete set
- **Implement ALL QAs (QA-1 through QA-4)** — complete set
- **Real audio recording and playback** — no mocked audio APIs
- **Real feedback generation** — LLM analysis, not placeholder text
- **Emit actual witness marks** — not just capture intent

### Failure Conditions (Automatic Fail)

The system is **broken** if:

| Condition | Impact |
|-----------|--------|
| **FC-1** Microphone access fails silently | Recording impossible |
| **FC-2** Audio playback produces no sound | Review impossible |
| **FC-3** Feedback is generic/templated | Not grounded per L2 |
| **FC-4** Crystal reads like a report, not a witness | Warmth missing per QA-3 |
| **FC-5** Any mock audio in production build | Trust violation |

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | Microphone captures audio within 1s of permission grant | Yes |
| **QG-2** | Zero TypeScript errors | Yes |
| **QG-3** | All Laws have corresponding implementation | Yes |
| **QG-4** | VoiceCrystal generates with warmth (not template) | Yes |
| **QG-5** | Intent declaration required before recording (L1 enforced) | Yes |

---

## Narrative
Freestyle is a laboratory of voice. Each take is a committed act of agency—raw, imperfect, *real*. Each session becomes a trace of evolving authenticity, and the system's job is to witness without flinching.

## Personality Tag
*Celebrate the rough voice, not the polished one. The coach is a witness, never a judge.*

## Objectives
- Make growth legible without sterilizing the creative chaos of practice. The mess is where voice lives.
- Convert sessions into proof-bearing traces with explicit intent and feedback—every take writes a mark.
- Generate crystals that capture the *change in voice*, not performance metrics. The crystal answers: "Who are you becoming?"

## Epistemic Commitments
- Every take creates a mark with **intent, stance, and principle weights**. Intent must be declared before analysis.
- A session trace is immutable; all feedback must attach to a mark. Raw footage is sacred.
- Crystals must state **what changed in voice and why**, with evidence anchors. The crystal is warm—it sees the artist.
- Galois loss quantifies mismatch between intent and delivery—not as judgment, but as signal.
- Ghosts (rejected phrasings, alternate lines) are part of the proof space. The roads not taken shaped the road taken.

## Laws

- **L1 Intent Declaration Law**: A take is valid only if its intent is explicit *before* analysis. The artist speaks first; the system listens.
- **L2 Feedback Grounding Law**: All critique must reference a mark or trace segment. Unanchored feedback is forbidden.
- **L3 Voice Continuity Law**: Crystal summaries must identify the through-line of voice across a session. The artist's thread is never lost.
- **L4 Courage Preservation Law**: High-risk takes are protected from negative weighting by default. Courage is rewarded, not punished.
- **L5 Repair Path Law**: If loss is high, the system proposes a repair path—not a verdict. Failure is navigable, not final.

## Qualitative Assertions

- **QA-1** The coach must feel like a **collaborator**, not a judge. The warmth is earned—the system believes in the artist.
- **QA-2** The system amplifies **authenticity**, not conformity. Uniqueness is signal; polish is noise.
- **QA-3** A weak session should still produce a **strong crystal**. Even bad days have meaning when witnessed.
- **QA-4** The pace of practice must remain **fluid**. Witnessing cannot add drag; the flow state is sacred.

## Anti-Success (Failure Modes)

The system fails if:

- **Judge emergence**: The coach feels evaluative—the artist hesitates before taking risks, anticipates criticism, or performs *for* the system instead of for themselves. The system has become a critic.
- **Metric creep**: Performance numbers dominate the interface. Loss becomes a score; scores become shame. The system optimizes for measurables, not meaning.
- **Conformity pressure**: The system nudges toward "good" patterns—industry norms, successful templates, safe choices. The artist's weirdness gets smoothed out.
- **Coldness**: The crystal reads like a report, not a witness. There's no warmth, no sense that the system *saw* the artist. The emotional charge is lost.
- **Drag tax**: Any friction that slows the creative loop—prompts that interrupt flow, analysis that blocks the next take, UI that demands attention during practice.

## kgents Integrations

| Primitive | Role | Chain |
|-----------|------|-------|
| **Witness Mark** | Captures intent + delivery per take | `take → Mark.emit(intent, stance, weights)` |
| **Witness Trace** | Immutable session history | `Mark[] → Trace.seal(session_id)` |
| **Witness Crystal** | Compressive proof of voice evolution | `Trace → Crystal.compress(voice_change)` |
| **ValueCompass** | Voice profile across principles | `Crystal.weights → Compass.render()` |
| **Trail** | Session navigation + evidence anchors | `Trace → Trail.navigate(takes)` |
| **Galois Loss** | Intent/delivery coherence signal | `Mark.intent, Mark.delivery → Galois.loss()` |
| **Differance Ghost** | Alternate lines, rejected phrasings | `take → Ghost.record(alternatives)` |

**Composition Chain** (single session):
```
TakeRecording
  → Mark.emit(intent, stance, weights)
  → [on session_end] Trace.seal()
  → Galois.loss(intent_target) // coherence signal
  → Ghost.record(rejected_phrasings)
  → Crystal.compress(trace, voice_delta)
  → Compass.render(crystal.weights)
  → Trail.display(crystal, trace)
```

## Quality Algebra

> *See: `spec/theory/experience-quality-operad.md` for universal framework*

This pilot instantiates the Experience Quality Operad via `RAP_COACH_QUALITY_ALGEBRA`:

| Dimension | Instantiation |
|-----------|---------------|
| **Contrast** | risk_taking, commitment, authenticity, warmth, flow_state |
| **Arc** | warmup → attempt → courage → growth → reflection |
| **Voice** | witness ("Was it seen without judgment?"), warm ("Did the system care?"), authentic ("Was it real?") |
| **Floor** | no_judgment_leakage, no_flow_drag, intent_declared, courage_protected |

**Weights**: C=0.30, A=0.30, V=0.40

**Implementation**: `impl/claude/services/experience_quality/algebras/rap_coach.py`

**Domain Spec**: `spec/theory/domains/rap-coach-quality.md`

## Canary Success Criteria

- A user can describe their **voice shift** using only the crystal: "I started defensive, but by take 5 I was owning the aggressive register."
- A user can replay a session trace and **understand every critique**—each piece of feedback points to a specific mark.
- The system surfaces at least one **repair path** for a high-loss take: "Next time, try landing the third beat before extending."
- The artist **returns to practice** more often because the system makes practice feel less lonely.

## Out of Scope

- Public publishing, social feeds, or competitive ranking.
- Beat production, mixing, or mastering tools.
- Industry comparison metrics ("you sound like X").

---

## Webapp Interaction Flow (Law-Level Requirements)

> *"The session IS the laboratory. Every take IS a commitment."*

### L6 Screen Architecture Law

The webapp MUST implement exactly these screens:

```
┌─────────────────────────────────────────────────────────────────┐
│                         HOME SCREEN                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  New Session │  │  Session     │  │  Voice Profile       │   │
│  │  (→ Studio)  │  │  History     │  │  (→ Evolution)       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  "The rough voice matters. Let's practice."               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       STUDIO SCREEN                              │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Beat Player (optional background beat)                  │    │
│  │  [Play/Pause] [BPM: 90] [Beat: Lo-Fi Boom Bap]          │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  RECORDING ZONE                                          │    │
│  │  ┌─────────────────────────────────────────────────┐    │    │
│  │  │  ◉ REC  [Intent: ___________]  Take #3          │    │    │
│  │  │  ▓▓▓▓▓▓▓▓░░░░░░░░  00:45 / 01:00               │    │    │
│  │  │  [Stop] [Discard] [Save Take]                   │    │    │
│  │  └─────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Session Trail (scrolling feed of takes)                 │    │
│  │  - Take #2: "aggressive flow" — [Play] [Feedback]       │    │
│  │  - Take #1: "warm up" — [Play] [Feedback]               │    │
│  └─────────────────────────────────────────────────────────┘    │
│  [End Session → Crystal]                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (on End Session)
┌─────────────────────────────────────────────────────────────────┐
│                      CRYSTAL SCREEN                              │
│  ┌───────────────────────┐  ┌───────────────────────────────┐   │
│  │  Voice Crystal         │  │  Session Trail               │   │
│  │  - Voice delta         │  │  - All takes with playback   │   │
│  │  - Through-line        │  │  - Grounded feedback each    │   │
│  │  - Courage moments     │  │  - Ghost phrasings           │   │
│  │  - Warmth summary      │  │                              │   │
│  └───────────────────────┘  └───────────────────────────────┘   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Joy Compass (WARMTH × FLOW × SURPRISE visualization)     │  │
│  └───────────────────────────────────────────────────────────┘  │
│  [New Session] [Export Crystal] [Return Home]                   │
└─────────────────────────────────────────────────────────────────┘
```

### L7 Audio Core Law

The webapp MUST implement real-time audio recording and playback:

| Component | Requirement | Rationale |
|-----------|-------------|-----------|
| **Microphone Access** | Request on first session, remember permission | Recording requires audio input |
| **Recording** | Real-time waveform visualization, max 2 min per take | Visual feedback during freestyle |
| **Playback** | Instant playback of any take, with beat sync if used | Review is essential to practice |
| **Beat Library** | 5+ built-in beats at various BPMs | Background beat aids flow |
| **Audio Quality** | 44.1kHz, 16-bit minimum | Quality matters for review |
| **Latency** | < 50ms input-to-monitor | Flow requires low latency |

**Technical Stack**:
- Web Audio API for recording and playback
- MediaRecorder API for capturing takes
- AudioWorklet for real-time processing (if needed)
- IndexedDB for local audio storage
- Optional: Whisper API for transcription

### L8 Intent Declaration Flow Law

Before EVERY take, the user MUST declare intent:

```
┌─────────────────────────────────────────────────────────────────┐
│  INTENT DECLARATION (L1 Compliance)                              │
│                                                                  │
│  "What are you going for this take?"                             │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  [Aggressive] [Smooth] [Experimental] [Recovery]         │    │
│  │  [Custom: _______________]                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Risk Level: [Low] [Medium] [HIGH — Courage Protected]          │
│                                                                  │
│  [Start Recording]                                               │
└─────────────────────────────────────────────────────────────────┘
```

**Critical**: Recording CANNOT start until intent is declared. This is L1 Law enforcement.

### L9 Take Mark Law

Each take MUST emit a mark with:

| Field | Source | Purpose |
|-------|--------|---------|
| `intent` | User declaration (L1) | What was attempted |
| `risk_level` | User selection | Courage protection (L4) |
| `audio_blob_id` | Recording result | Linkage to audio |
| `duration_ms` | Recording length | Session statistics |
| `beat_id` | Selected beat (if any) | Context |
| `stance` | Detected from intent | Principle weights |
| `timestamp` | System | Temporal ordering |

**Mark emission**: On "Save Take" button press.

### L10 Feedback Grounding Law

ALL feedback MUST reference a specific take (L2 compliance):

```
┌─────────────────────────────────────────────────────────────────┐
│  FEEDBACK for Take #3 (anchored per L2)                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  [▶ Play Take #3]  00:45  Intent: "aggressive flow"      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  Joy Signal: ████████░░ 0.78 (WARMTH dominant)                  │
│                                                                  │
│  Coach says:                                                     │
│  "That was real. I felt it. The third beat landing was tight.   │
│   The ending felt rushed—maybe let it breathe next time."       │
│                                                                  │
│  [0:12-0:18] — Strong pocket here                               │
│  [0:32-0:38] — This is where it got interesting                 │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Repair Path (if Galois loss > 0.4):                      │    │
│  │  "Try landing the third beat before extending."           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

**Feedback sources**:
1. **LLM Analysis**: Transcription → semantic analysis → grounded feedback
2. **Audio Features**: Rhythm detection, energy contour, pause patterns
3. **User Self-Reflection**: Optional "How did that feel?" prompt

### L11 Courage Preservation Flow Law

When risk_level = HIGH:

1. **Pre-recording indicator**: "🔥 Courage Mode — You're protected"
2. **During recording**: Subtle courage indicator visible
3. **After recording**: Joy floor enforced (≥ 0.5 effective intensity)
4. **In feedback**: Courage explicitly acknowledged ("That took guts.")
5. **In crystal**: Courage moments highlighted as achievements

**Critical**: High-risk takes NEVER receive negative framing. Even "misses" are met with warmth.

### L12 Ghost Capture Law

For each take, the user MAY record ghost alternatives:

- "What line did you almost say?"
- "What flow did you consider?"
- "What did you hold back?"

Ghosts appear in crystal as "roads not taken" — honored, not regretted.

### L13 Voice Crystal Law

Session end produces a VoiceCrystal with:

| Field | Content | Source |
|-------|---------|--------|
| `voice_delta` | How voice evolved this session | Comparison of first vs. last take |
| `through_line` | The thread across all takes | LLM synthesis of intents and outcomes |
| `courage_moments` | High-risk takes that were protected | L4 compliance |
| `compression_disclosure` | What was dropped | Amendment G |
| `warmth_summary` | Warm, personal session summary | JoyPoly functor |
| `repair_paths` | Actionable suggestions (not verdicts) | L5 compliance |

**Crystal tone**: Warm, supportive, sees the artist. Never cold, never a report.

### L14 Principled Build Law

```bash
# From clean clone
cd pilots/rap-coach-flow-lab
npm install
npm run dev        # Dev server at localhost:3000

# Verify
npm run test       # All tests pass
npm run typecheck  # Zero errors
```

**Audio testing**: Requires microphone access. Mock audio available for CI.

---

## Webapp File Structure

```
pilots/rap-coach-flow-lab/
├── PROTO_SPEC.md           # This file (the soul)
├── README.md               # Execution guide
├── package.json            # Dependencies + scripts
├── tsconfig.json           # TypeScript config
├── vite.config.ts          # Build config
├── contracts/
│   └── rap-coach.ts        # API contracts (source of truth)
├── src/
│   ├── main.tsx            # React entry
│   ├── App.tsx             # Router + layout
│   ├── screens/
│   │   ├── HomeScreen.tsx
│   │   ├── StudioScreen.tsx
│   │   └── CrystalScreen.tsx
│   ├── components/
│   │   ├── BeatPlayer.tsx     # Background beat control
│   │   ├── RecordingZone.tsx  # Mic input + waveform
│   │   ├── IntentPicker.tsx   # L1 intent declaration
│   │   ├── TakeCard.tsx       # Single take display
│   │   ├── FeedbackPanel.tsx  # L2 grounded feedback
│   │   ├── JoyCompass.tsx     # WARMTH × FLOW × SURPRISE
│   │   └── VoiceCrystal.tsx   # Session crystal display
│   ├── audio/
│   │   ├── recorder.ts        # MediaRecorder wrapper
│   │   ├── player.ts          # Playback engine
│   │   ├── beats.ts           # Beat library
│   │   └── waveform.ts        # Visualization
│   ├── witness/
│   │   ├── marks.ts           # TakeMark emission
│   │   ├── joy.ts             # RAP_COACH_JOY functor
│   │   ├── courage.ts         # L4 protection
│   │   └── crystal.ts         # VoiceCrystal generation
│   └── feedback/
│       ├── analyzer.ts        # Audio feature extraction
│       └── coach.ts           # LLM feedback generation
├── beats/                     # Built-in beat library (mp3/ogg)
│   ├── boom-bap-90.mp3
│   ├── trap-140.mp3
│   └── lofi-85.mp3
└── runs/
    └── run-{N}/               # Regeneration history
```

---

## Generation Checklist (For Sub-Agents)

Before claiming this pilot is complete, verify:

- [ ] **Microphone works**: Audio recording captures voice
- [ ] **Intent required**: Cannot record without declaring intent (L1)
- [ ] **Takes save correctly**: Audio stored, mark emitted
- [ ] **Playback works**: Any take can be replayed
- [ ] **Feedback is grounded**: All feedback references specific take (L2)
- [ ] **Courage protected**: High-risk takes get ≥ 0.5 joy floor (L4)
- [ ] **Crystal generates**: Session end produces warm VoiceCrystal
- [ ] **Through-line detected**: Crystal identifies voice evolution (L3)
- [ ] **Zero judgment language**: Coach never evaluates, only witnesses
- [ ] **Repair paths offered**: High-loss takes get actionable suggestions (L5)
- [ ] **Typecheck passes**: `npm run typecheck` exits 0
- [ ] **Tests pass**: `npm run test` exits 0
