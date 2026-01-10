# Rap Coach: Flow to Crystal

**Status**: production
**Version**: 2.0
**Galois Target**: L < 0.20

> *"The voice is the proof. The session is the trace. Courage leaves marks."*

---

## The Pitch (35 Words)

A psychological safety container for creative practice. The coach witnesses freestyle rap sessions, protects courage, and crystallizes voice evolution. Not a judge. A witness who believes in the artist.

---

## The Mirror Test

Does this feel like Kent on his best day?

| Quality | Passes? | Evidence |
|---------|---------|----------|
| **Daring** | YES | Courage is a functor law, not a feature. High-risk takes are structurally protected. |
| **Bold** | YES | Intent required BEFORE analysis inverts the power dynamic. Artist speaks first. |
| **Creative** | YES | Ghosts (roads not taken) are honored as part of the proof space. |
| **Opinionated** | YES | "The coach is a witness, never a judge" is a non-negotiable stance. |
| **Not gaudy** | YES | Warmth is structural, not decorative. No metrics shown. No scores. |

---

## Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:

- **Implement ALL laws (L1-L14)** - complete set
- **Implement ALL QAs (QA-1 through QA-7)** - complete set
- **Real audio recording and playback** - no mocked audio APIs in production
- **Real feedback generation** - LLM analysis, not placeholder text
- **Emit actual witness marks** - not just capture intent
- **Wire to witness infrastructure** - marks flow through DataBus

### Failure Conditions (Automatic Fail)

The system is **broken** if:

| Condition | Impact | Detection |
|-----------|--------|-----------|
| **FC-1** Microphone access fails silently | Recording impossible | Permission denied without user feedback |
| **FC-2** Audio playback produces no sound | Review impossible | Playback button click → silence |
| **FC-3** Feedback is generic/templated | Not grounded per L2 | Same feedback for different takes |
| **FC-4** Crystal reads like a report, not a witness | Warmth missing per QA-3 | No personal pronouns, no belief |
| **FC-5** Any mock audio in production build | Trust violation | `NODE_ENV=production` + mock imports |
| **FC-6** Judge language appears anywhere | L4 violated | "wrong", "mistake", "should have", "failed" |
| **FC-7** Score/metric shown to user | Metric creep | Any number displayed as quality indicator |

### Quality Gates (Mandatory Blocking)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | Microphone captures audio within 1s of permission grant | Yes |
| **QG-2** | Zero TypeScript errors (`npm run typecheck`) | Yes |
| **QG-3** | All Laws (L1-L14) have corresponding implementation | Yes |
| **QG-4** | VoiceCrystal generates with warmth (not template) | Yes |
| **QG-5** | Intent declaration required before recording (L1 enforced) | Yes |
| **QG-6** | Courage floor enforced (high-risk takes >= 0.5 effective) | Yes |

---

## Part I: Galois Stratification

### Layer 1: AXIOMS (L < 0.10) - MUST Preserve

These are fixed points that survive radical restructuring:

| Axiom | Statement | Kernel Derivation |
|-------|-----------|-------------------|
| **A1 Agency** | The artist speaks first; the system listens | L0.3 (Mirror): Human oracle is ground truth |
| **A2 Witness** | The coach witnesses, never judges | L2.3 (Ethical): Augment, never replace judgment |
| **A3 Courage** | Risk-taking is structurally protected | L2.4 (Joy-Inducing): Delight includes daring |
| **A4 Warmth** | Every interaction expresses belief in the artist | L2.4 (Joy-Inducing): Warmth over coldness |

### Layer 2: VALUES (L < 0.35) - SHOULD Preserve

| Value | Statement | Derives From |
|-------|-----------|--------------|
| **V1 Intent-First** | Intent declared before analysis | A1 (Agency) |
| **V2 Grounded Feedback** | All critique references specific marks | A2 (Witness) |
| **V3 Courage Floor** | High-risk takes have joy floor >= 0.5 | A3 (Courage) |
| **V4 Ghost Preservation** | Unchosen paths remain inspectable | A2 (Witness) |
| **V5 Compression Honesty** | Crystal discloses what was dropped | A2 (Witness) |
| **V6 Voice Continuity** | Through-line of voice is never lost | A4 (Warmth) |
| **V7 Flow Protection** | Recording flow is sacred, never interrupted | A3 (Courage) |

### Layer 3: SPECIFICATIONS (L < 0.70) - MAY Diverge

| Spec | Statement | Valid Alternatives |
|------|-----------|-------------------|
| **S1 Voice-First Intent** | Intent spoken, not typed | Could be typed, selected |
| **S2 Beat Library** | 5+ built-in beats | Could integrate external beats |
| **S3 Waveform Visualization** | Real-time amplitude display | Could be minimal/none |
| **S4 Session Duration** | Max 2 min per take | Could be longer/shorter |
| **S5 Three-Screen Flow** | Home → Studio → Crystal | Could be single-screen |
| **S6 Ghost Prompt** | "What line did you almost say?" | Could be implicit detection |

### Layer 4: TUNING (L >= 0.70) - WILL Vary

| Param | Default | Range | Notes |
|-------|---------|-------|-------|
| `COURAGE_FLOOR` | 0.5 | [0.3, 0.7] | Minimum effective intensity for high-risk |
| `COURAGE_BOOST` | 0.15 | [0.0, 0.3] | Boost applied to courageous takes |
| `GALOIS_ALERT_THRESHOLD` | 0.5 | [0.3, 0.7] | When to suggest repair path |
| `MAX_TAKE_DURATION_MS` | 120000 | [60000, 300000] | Per-take recording limit |
| `WARMUP_PROTECTION_TAKES` | 2 | [1, 3] | Auto-courage-protected first N takes |
| `BEAT_BPM_RANGE` | [80, 140] | [60, 180] | Supported beat tempos |

---

## Part II: Laws (L1-L14)

### Categorical Laws (Must Hold)

| Law | Statement | Schema | Kernel |
|-----|-----------|--------|--------|
| **L1 Intent Declaration** | A take is valid only if intent is explicit BEFORE analysis | COHERENCE_GATE | L1.2 (Judge) |
| **L2 Feedback Grounding** | All critique must reference a mark or trace segment | COHERENCE_GATE | L1.3 (Ground) |
| **L3 Voice Continuity** | Crystal summaries must identify through-line of voice | COHERENCE_GATE | L1.7 (Fix) |
| **L4 Courage Preservation** | High-risk takes protected from negative weighting | COURAGE_PRESERVATION | L2.4 (Joy) |
| **L5 Repair Path** | If loss > threshold, propose repair path (not verdict) | DRIFT_ALERT | L1.5 (Contradict) |
| **L6 Ghost Preservation** | Unchosen phrasings remain inspectable | GHOST_PRESERVATION | L1.8 (Galois) |
| **L7 Compression Honesty** | Crystal discloses what was dropped | COMPRESSION_HONESTY | L1.8 (Galois) |

### Empirical Laws (Quality Thresholds)

| Law | Statement | Measurement |
|-----|-----------|-------------|
| **L8 Audio Core** | Recording latency < 50ms, playback immediate | Measured at runtime |
| **L9 Warmup Protection** | First N takes auto-courage-protected | N = WARMUP_PROTECTION_TAKES |
| **L10 No Drag Tax** | Intent picker to recording < 3 seconds | Timed interaction |
| **L11 Silence Recognition** | Pauses > 2s flagged as intentional or recovery | Audio analysis |
| **L12 Beat Sync Sensitivity** | On-beat vs off-beat detected, both valid | Rhythm analysis |
| **L13 Cross-Session Memory** | Crystals compose to reveal voice evolution over time | Crystal composition |
| **L14 Anti-Judge Detection** | No judge language anywhere in system | String analysis |

### Law Predicate Implementations

```typescript
// L1: Intent Declaration
const L1_IntentDeclaration = (take: Take): boolean => {
  return take.intent !== null && take.intent.declaredAt < take.recordingStartedAt;
};

// L4: Courage Preservation
const L4_CouragePreservation = (take: Take, score: number): number => {
  if (take.intent.riskLevel === 'HIGH') {
    return Math.max(COURAGE_FLOOR, score) + COURAGE_BOOST;
  }
  return score;
};

// L5: Repair Path
const L5_RepairPath = (take: Take, galoisLoss: number): RepairPath | null => {
  if (galoisLoss > GALOIS_ALERT_THRESHOLD) {
    return generateRepairPath(take, galoisLoss); // NOT a verdict
  }
  return null;
};

// L14: Anti-Judge Detection
const JUDGE_PATTERNS = [
  /you should/i, /you need to/i, /that was wrong/i,
  /mistake/i, /error/i, /failed/i, /not good/i,
  /try harder/i, /disappointing/i
];
const L14_AntiJudgeDetection = (text: string): boolean => {
  return !JUDGE_PATTERNS.some(pattern => pattern.test(text));
};
```

---

## Part III: Quality Algebra

### RAP_COACH_QUALITY_ALGEBRA

```typescript
const RAP_COACH_QUALITY_ALGEBRA: QualityAlgebra = {
  name: "RAP_COACH",
  description: "Quality algebra for witnessed freestyle practice",

  // CONTRAST: What oscillates in a practice session?
  contrastDimensions: [
    { name: "risk_taking", description: "Safe vs. bold attempts", weight: 1.2 },
    { name: "commitment", description: "Tentative vs. fully committed", weight: 1.0 },
    { name: "authenticity", description: "Performing vs. being real", weight: 1.1 },
    { name: "warmth_received", description: "Cold feedback vs. warm witness", weight: 0.8 },
    { name: "flow_state", description: "Struggling vs. in the zone", weight: 1.0 },
  ],

  // ARC: What phases does a practice session traverse?
  arcPhases: [
    { name: "WARMUP", description: "Finding voice, settling in", required: false },
    { name: "ATTEMPT", description: "Trying something specific", required: true },
    { name: "COURAGE", description: "Taking a real risk", required: false },
    { name: "GROWTH", description: "Feeling the shift", required: true },
    { name: "REFLECTION", description: "Witnessing what changed", required: true },
  ],
  canonicalTransitions: [
    ["WARMUP", "ATTEMPT"],
    ["ATTEMPT", "COURAGE"],
    ["COURAGE", "GROWTH"],
    ["ATTEMPT", "GROWTH"],
    ["GROWTH", "REFLECTION"],
  ],

  // VOICE: What perspectives evaluate quality?
  voices: [
    {
      name: "witness",
      question: "Was it seen without judgment?",
      checker: "checkWitnessVoice",
      weight: 1.5  // Primary voice
    },
    {
      name: "warm",
      question: "Did the system express belief in the artist?",
      checker: "checkWarmVoice",
      weight: 1.3
    },
    {
      name: "authentic",
      question: "Was the practice real, not performed?",
      checker: "checkAuthenticVoice",
      weight: 1.0
    },
  ],

  // FLOOR: Non-negotiable must-haves
  floorChecks: [
    { name: "no_judgment_leakage", threshold: 0, comparison: "==", unit: "count" },
    { name: "no_flow_drag", threshold: 3000, comparison: "<=", unit: "ms" },
    { name: "intent_declared", threshold: 1, comparison: "==", unit: "bool" },
    { name: "courage_protected", threshold: 0.5, comparison: ">=", unit: "ratio" },
    { name: "warmth_present", threshold: 1, comparison: "==", unit: "bool" },
  ],

  // WEIGHTS
  contrastWeight: 0.30,
  arcWeight: 0.30,
  voiceWeight: 0.40,

  // EXPERIENCE TYPES (nesting hierarchy)
  experienceTypes: ["Take", "Session", "Week", "Journey"],
};
```

### Quality Equation

```
Q = F × (0.30×C + 0.30×A + 0.40×V^(1/3))

where:
  F = Floor gate (0 if any floor check fails, 1 otherwise)
  C = Contrast coverage [0,1] (variance across risk, commitment, authenticity, warmth, flow)
  A = Arc phase coverage [0,1] (ATTEMPT + GROWTH + REFLECTION required)
  V = Voice approval (geometric mean of witness, warm, authentic)
```

---

## Part IV: Qualitative Assertions

| QA | Assertion | Verification Method |
|----|-----------|---------------------|
| **QA-1** | The coach must feel like a **collaborator**, not a judge | Language analysis: no imperative "you should" |
| **QA-2** | The system amplifies **authenticity**, not conformity | No "correct" register hierarchy |
| **QA-3** | A weak session should still produce a **strong crystal** | Crystal generation with low-intensity takes |
| **QA-4** | The pace of practice must remain **fluid** | Intent → recording < 3 seconds |
| **QA-5** | The artist **wants to return** because practice feels less lonely | Retention metric proxy |
| **QA-6** | The crystal captures **who you're becoming**, not how you performed | Crystal language analysis |
| **QA-7** | Courage moments are **celebrated**, not just protected | Explicit acknowledgment in feedback |

---

## Part V: Anti-Success (Failure Modes)

| Anti-Pattern | Symptom | Axiom Violated | Detection |
|--------------|---------|----------------|-----------|
| **Judge Emergence** | Artist hesitates before risks, performs FOR the system | A2 (Witness) | Decreased risk-taking over sessions |
| **Metric Creep** | Loss becomes a score; scores become shame | A4 (Warmth) | Any numeric quality exposed to user |
| **Conformity Pressure** | System nudges toward "good" patterns | A1 (Agency) | Preferred register bias in feedback |
| **Coldness** | Crystal reads like a report | A4 (Warmth) | No personal pronouns, no belief statements |
| **Drag Tax** | Friction slows creative loop | V7 (Flow Protection) | Intent-to-recording > 3 seconds |
| **Surveillance Drift** | Artist feels watched, not witnessed | A2 (Witness) | Excessive data collection, no opt-out |

---

## Part VI: kgents Integrations

| Primitive | Role | Integration Chain |
|-----------|------|-------------------|
| **Witness Mark** | Captures intent + delivery per take | `take → Mark.emit(intent, stance, weights)` |
| **Witness Trace** | Immutable session history | `Mark[] → Trace.seal(session_id)` |
| **Witness Crystal** | Compressive proof of voice evolution | `Trace → Crystal.compress(voice_change)` |
| **Galois Loss** | Intent/delivery coherence signal | `Mark.intent, Mark.delivery → Galois.loss()` |
| **DataBus** | Event propagation | `Mark.emit → DataBus → UI update` |
| **SynergyBus** | Cross-jewel coordination | `Crystal.create → SynergyBus → Brain.teach` |

### Composition Chain (Single Session)

```
VoiceIntentDeclaration
  → TakeRecording.start()
  → TakeRecording.stop()
  → Mark.emit(intent, audio_blob_id, risk_level)
  → [for each saved take] Feedback.generate(mark, transcription)
  → [on session_end] Trace.seal(session_id)
  → Galois.loss(intent_aggregate, delivery_aggregate)
  → Ghost.record(prompted_alternatives)
  → Crystal.compress(trace, voice_delta, warmth_disclosure)
  → DataBus.emit("crystal.created", crystal)
```

### AGENTESE Paths

```
world.rapcoach.session.start           # Begin new session
world.rapcoach.session.end             # End session, trigger crystal
world.rapcoach.take.record             # Record a take
world.rapcoach.take.feedback           # Get feedback for take
world.rapcoach.crystal.view            # View session crystal
self.rapcoach.voice.profile            # Voice evolution over time
self.rapcoach.courage.moments          # All courage moments
time.rapcoach.session.history          # Past sessions
```

---

## Part VII: Webapp Architecture

### Screen Flow (L6 Screen Architecture)

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
│  │  INTENT ZONE (Voice-First per S1)                        │    │
│  │  "What are you going for?"  [Speak Intent]               │    │
│  │  Risk: [Low] [Medium] [HIGH - Courage Protected]         │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  RECORDING ZONE                                          │    │
│  │  ◉ REC  ▓▓▓▓▓▓▓▓░░░░░░░░  00:45 / 02:00                │    │
│  │  [Stop] [Discard] [Save Take]                           │    │
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
│  │  - Who you became      │  │  - All takes with playback   │   │
│  │  - Through-line        │  │  - Grounded feedback each    │   │
│  │  - Courage moments     │  │  - Ghost alternatives        │   │
│  │  - What was dropped    │  │                              │   │
│  └───────────────────────┘  └───────────────────────────────┘   │
│  [New Session] [Export Crystal] [Return Home]                   │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

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
│   │   ├── BeatPlayer.tsx
│   │   ├── RecordingZone.tsx
│   │   ├── IntentPicker.tsx      # Voice-first intent (S1)
│   │   ├── TakeCard.tsx
│   │   ├── FeedbackPanel.tsx
│   │   ├── GhostPrompt.tsx       # "What did you almost say?"
│   │   └── VoiceCrystal.tsx
│   ├── audio/
│   │   ├── recorder.ts           # MediaRecorder wrapper
│   │   ├── player.ts             # Playback engine
│   │   ├── beats.ts              # Beat library
│   │   ├── waveform.ts           # Visualization
│   │   └── silenceDetector.ts    # L11 implementation
│   ├── witness/
│   │   ├── marks.ts              # TakeMark emission
│   │   ├── courage.ts            # L4 Courage functor
│   │   ├── crystal.ts            # VoiceCrystal generation
│   │   └── galois.ts             # Intent/delivery loss
│   ├── feedback/
│   │   ├── analyzer.ts           # Audio feature extraction
│   │   ├── coach.ts              # LLM feedback (warm, grounded)
│   │   └── antiJudge.ts          # L14 detection
│   └── quality/
│       └── algebra.ts            # RAP_COACH_QUALITY_ALGEBRA
├── beats/                        # Built-in beat library
│   ├── boom-bap-90.mp3
│   ├── trap-140.mp3
│   ├── lofi-85.mp3
│   ├── jazzy-95.mp3
│   └── minimal-100.mp3
└── runs/
    └── run-{N}/                  # Regeneration history
```

---

## Part VIII: Autonomous Systems

### A. Development System

```yaml
autonomous_development:
  trigger: "PROTO_SPEC change or /regenerate command"

  phases:
    1_contract_generation:
      input: "PROTO_SPEC Part III (Quality Algebra) + Part II (Laws)"
      output: "contracts/rap-coach.ts"
      validation: "TypeScript compiles"

    2_scaffold_generation:
      input: "PROTO_SPEC Part VII (File Structure)"
      output: "Directory tree + stub files"
      validation: "All imports resolve"

    3_law_implementation:
      input: "PROTO_SPEC Part II (Laws L1-L14)"
      output: "witness/*.ts, feedback/*.ts, quality/*.ts"
      validation: "Law predicates return boolean"

    4_component_generation:
      input: "PROTO_SPEC Part VII (Screen Flow)"
      output: "screens/*.tsx, components/*.tsx"
      validation: "npm run typecheck passes"

    5_integration_wiring:
      input: "PROTO_SPEC Part VI (kgents Integrations)"
      output: "DataBus subscriptions, Mark emissions"
      validation: "Marks flow to witness service"

  regeneration_laws:
    RL1_axiom_preservation:
      must_preserve: ["A1 Agency", "A2 Witness", "A3 Courage", "A4 Warmth"]
      violation_action: "HALT and request human review"

    RL2_value_stability:
      should_preserve: ["V1-V7"]
      violation_action: "WARN and continue with justification"

    RL3_spec_divergence:
      may_change: ["S1-S6"]
      requirement: "Document why alternative is better"

    RL4_tuning_freedom:
      will_vary: ["COURAGE_FLOOR", "COURAGE_BOOST", etc.]
      requirement: "Stay within defined ranges"
```

### B. QA System

```yaml
autonomous_qa:
  trigger: "PR opened or /qa command"

  law_verification:
    categorical_laws:
      - L1_intent_before_recording: "Intent timestamp < recording timestamp"
      - L2_feedback_grounded: "Every feedback has anchor_take_id"
      - L3_voice_continuity: "Crystal has throughline field"
      - L4_courage_floor: "High-risk takes >= 0.5 effective"
      - L5_repair_not_verdict: "High-loss feedback has suggestion, not judgment"
      - L6_ghosts_preserved: "Ghost alternatives stored and retrievable"
      - L7_compression_disclosed: "Crystal has dropped_elements field"

    empirical_laws:
      - L8_audio_latency: "Recording latency < 50ms"
      - L9_warmup_protected: "First N takes are courage-protected"
      - L10_no_drag: "Intent to recording < 3000ms"
      - L14_no_judge: "No JUDGE_PATTERNS in any user-facing string"

  quality_gates:
    - qg1_mic_permission: "Grant permission → audio captured within 1s"
    - qg2_typecheck: "npm run typecheck exits 0"
    - qg3_laws_implemented: "Every L1-L14 has implementation file"
    - qg4_warmth_crystal: "Crystal generation uses warm templates"
    - qg5_intent_required: "Cannot record without intent"
    - qg6_courage_enforced: "High-risk floor >= 0.5"

  failure_conditions:
    - fc1_silent_mic_fail: "Permission denied → user sees feedback"
    - fc2_silent_playback: "Playback click → audio plays"
    - fc3_generic_feedback: "Different takes → different feedback"
    - fc4_cold_crystal: "Crystal has personal pronouns and belief"
    - fc5_mock_in_prod: "No mock imports in production bundle"
    - fc6_judge_language: "No JUDGE_PATTERNS anywhere"
    - fc7_visible_score: "No numeric quality shown to user"

  canary_tests:
    - user_describes_voice_shift: "Crystal alone enables 'I started X, ended Y'"
    - feedback_traceable: "Every critique points to specific take"
    - repair_path_offered: "High-loss take gets suggestion"
    - wants_to_return: "Session ends with encouraging message"
```

### C. Operations System

```yaml
autonomous_ops:
  trigger: "Deploy or /ops command"

  monitoring:
    health_checks:
      - audio_api: "MediaRecorder available"
      - permission_api: "navigator.mediaDevices accessible"
      - storage: "IndexedDB writable"
      - witness_service: "DataBus connected"

    quality_metrics:
      - session_completion_rate: "Sessions with crystal / sessions started"
      - courage_take_ratio: "High-risk takes / total takes"
      - return_rate: "Users with 2+ sessions / total users"
      - crystal_warmth_score: "LLM evaluation of crystal warmth"

    alerts:
      - audio_failure_spike: "Audio errors > 5% in 1h"
      - courage_decline: "Courage ratio drops > 20% week-over-week"
      - cold_crystal_detected: "Warmth score < 0.5"

  incident_response:
    audio_unavailable:
      detection: "MediaRecorder errors > threshold"
      action: "Fallback to text-only mode with warm message"
      message: "Your mic isn't cooperating right now. Want to write instead?"

    llm_timeout:
      detection: "Feedback generation > 10s"
      action: "Use cached warm template with take reference"
      message: "Still thinking about that one... Here's what I noticed..."

    storage_full:
      detection: "IndexedDB quota exceeded"
      action: "Prompt export, then clear oldest takes"
      message: "You've been practicing a lot! Let's save your crystals."
```

---

## Part IX: Regeneration Laws

### RL-1: Axiom Preservation (MUST)

Any regeneration MUST preserve:
- **A1**: Artist speaks first (intent before analysis)
- **A2**: Witness, not judge (no evaluative language)
- **A3**: Courage protected (floor enforced)
- **A4**: Warmth structural (belief in artist)

**Violation**: HALT regeneration, request human review.

### RL-2: Value Stability (SHOULD)

Any regeneration SHOULD preserve V1-V7. If diverging:
1. Document which value changed
2. Explain why the change improves the pilot
3. Show how axioms are still satisfied

### RL-3: Specification Divergence (MAY)

Any regeneration MAY diverge from S1-S6. When diverging:
1. Name the superseded specification
2. Explain the improvement
3. Update this PROTO_SPEC

### RL-4: Explicit Supersession

When improving the spec itself:
1. Create new version in `runs/run-{N}/PROTO_SPEC_DELTA.md`
2. Document what changed and why
3. Update main PROTO_SPEC after validation

---

## Part X: Canary Success Criteria

1. **Voice Shift Description**: A user can describe their voice shift using only the crystal: *"I started defensive, but by take 5 I was owning the aggressive register."*

2. **Traceable Critique**: A user can replay a session trace and understand every piece of feedback—each critique points to a specific take.

3. **Repair Path Offered**: The system surfaces at least one repair path for a high-loss take: *"Next time, try landing the third beat before extending."*

4. **Wants to Return**: The artist returns to practice more often because the system makes practice feel less lonely.

5. **No Judge Feeling**: The artist never hesitates to take a risk because they fear the system's response.

---

## Out of Scope

- Public publishing, social feeds, or competitive ranking
- Beat production, mixing, or mastering tools
- Industry comparison metrics ("you sound like X")
- Transcription accuracy optimization (it's a means, not an end)
- Multi-user collaboration (this is solo practice)

---

## Appendix A: Warm Language Templates

```typescript
const WARMTH_TEMPLATES = {
  // After high-courage take
  courage_acknowledged: [
    "That took guts. I saw it.",
    "You went there. That's what practice is for.",
    "Bold move. The rough edges are where voice lives.",
  ],

  // After any take (base warmth)
  take_witnessed: [
    "I heard you.",
    "That was real.",
    "You showed up. That's the work.",
  ],

  // Crystal opening
  crystal_opening: [
    "Here's what I saw in your practice today:",
    "You put in the work. Let me tell you what I noticed:",
    "This session had moments. Here they are:",
  ],

  // Crystal closing
  crystal_closing: [
    "The voice is evolving. Keep going.",
    "You're building something. I believe in it.",
    "See you next time. The practice continues.",
  ],

  // Repair path framing (NOT verdict)
  repair_framing: [
    "If you want to explore this more:",
    "One thing that might be interesting to try:",
    "Here's a path if you're curious:",
  ],
};
```

---

## Appendix B: Generation Checklist

Before claiming this pilot is complete, verify:

### Laws
- [ ] L1: Intent required before recording (UI blocks record without intent)
- [ ] L2: Feedback references specific take (anchor_take_id field)
- [ ] L3: Crystal has through-line field
- [ ] L4: Courage floor enforced (>= 0.5 for HIGH risk)
- [ ] L5: High-loss takes get repair path, not verdict
- [ ] L6: Ghosts stored and retrievable
- [ ] L7: Crystal discloses dropped elements
- [ ] L8: Audio latency < 50ms
- [ ] L9: First N takes auto-protected
- [ ] L10: Intent → recording < 3s
- [ ] L11: Silence detection implemented
- [ ] L12: Beat sync analysis (both on/off valid)
- [ ] L13: Cross-session crystal composition
- [ ] L14: No judge patterns in any string

### Quality Assertions
- [ ] QA-1: Collaborator feel (language analysis)
- [ ] QA-2: Authenticity amplified (no preferred register)
- [ ] QA-3: Weak session → strong crystal
- [ ] QA-4: Fluid pace (< 3s friction)
- [ ] QA-5: Artist wants to return
- [ ] QA-6: Crystal captures becoming, not performance
- [ ] QA-7: Courage celebrated, not just protected

### Technical
- [ ] Microphone works
- [ ] Playback works
- [ ] TypeScript compiles (`npm run typecheck`)
- [ ] Tests pass (`npm run test`)
- [ ] No mock audio in production
- [ ] DataBus wired
- [ ] Marks emit correctly

---

*"The proof IS the decision. The mark IS the witness."*

**Filed**: 2025-12-29
**Protocol**: Witnessed Regeneration v2.0
