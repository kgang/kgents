🌱 Metabolic Development Protocol: Implementation Master Plan

  "Development is metabolism—the continuous transformation of intent into evidence into artifact."

  ---
  ## Implementation Status (2025-12-21)

  | Phase | Checkpoint | Status | Tests | Files |
  |-------|------------|--------|-------|-------|
  | **0** | 0.1 Stigmergy→Coffee | ✅ Complete | 8 | `coffee/stigmergy.py` |
  | **0** | 0.2 Hydrator→Brain | ✅ Complete | 12 | `living_docs/brain_adapter.py` |
  | **0** | 0.3 Session Polynomial | ✅ Complete | 4 | `metabolism/polynomial.py` |
  | **1** | 1.1 Circadian Resonance | ✅ Complete | 24 | `coffee/circadian.py` |
  | **1** | 1.2 Serendipity | ✅ Complete | (included above) | (same file) |
  | **1** | 1.3 Full Morning Flow | ⏳ Pending | - | Wire to CLI |
  | **2** | 2.1 ASHC Continuous | ✅ Complete | 29 | `metabolism/evidencing.py` |
  | **2** | 2.2 Interactive Text | ❌ Not started | - | - |
  | **2** | 2.3 Verification Graph | ❌ Not started | - | - |
  | **3-4** | All | ❌ Not started | - | - |

  **Total Tests**: 53+ | **Handoff Ready**: D-gent Persistence (`HANDOFF_DGENT_PERSISTENCE.md`)

  ---
  Voice Anchors (Ground Truth)

  Before we begin, let me quote what grounds this work:

  - "Daring, bold, creative, opinionated but not gaudy"
  - "The Mirror Test: Does K-gent feel like me on my best day?"
  - "Tasteful > feature-complete"
  - "The persona is a garden, not a museum"
  - "Depth over breadth"

  ---
  Executive Summary

  The Metabolic Development Protocol synthesizes four conceptual streams into a unified developer experience that fundamentally transforms how development happens:

  | Stream           | Purpose                                  | Existing Implementation                    |
  |------------------|------------------------------------------|--------------------------------------------|
  | Morning Coffee   | Intent capture with stigmergic memory    | services/liminal/coffee/ (partial)         |
  | Living Docs      | Context compilation for observers        | services/living_docs/ (hydrator exists)    |
  | ASHC             | Evidence accumulation through repetition | protocols/ashc/ (276 tests, Phases 1-2.75) |
  | Interactive Text | Specs as live control surfaces           | Spec only, no impl                         |

  The T-Shape: Lateral infrastructure (4 systems) × Vertical developer journeys (4 flows)

  ---
  Part I: The Vision Gap Analysis

  What Exists Today (Updated 2025-12-21)

  | Component                   | State                            | Gap                                                           |
  |-----------------------------|----------------------------------|---------------------------------------------------------------|
  | MorningVoice capture        | ✅ Basic questions + persistence | ✅ Stigmergy wired (Phase 0.1)                                |
  | Hydrator                    | ✅ Keyword matching for gotchas  | ✅ Brain adapter + ASHC evidence wired (Phase 0.2, 2.1)       |
  | PheromoneField (stigmergy)  | ✅ Core primitives in agents/m/  | ✅ VoiceStigmergy service (Phase 0.1)                         |
  | ASHC compiler               | ✅ Evidence + Adaptive Bayesian  | ✅ BackgroundEvidencing + DiversityScore (Phase 2.1)          |
  | Witness service             | ✅ 90+ tests, cross-jewel wiring | ✅ Ready for metabolic integration                            |
  | CircadianResonance          | ✅ Implemented                   | ✅ Resonance + Patterns + Serendipity (Phase 1.1-1.2)         |
  | Interactive Text            | 📋 Spec exists                   | ❌ Zero implementation                                        |
  | MetabolicSession polynomial | ✅ Implemented                   | ✅ SESSION_POLYNOMIAL (Phase 0.3)                             |
  | D-gent Persistence          | 📋 Handoff written               | ❌ Still using JSON files (handoff ready)                     |

  What Makes This Transformative

  The spec isn't about adding features—it's about collapsing the boundary between session and artifact:

  1. Sessions become compilation units, not chat threads
  2. Documentation compiles to context, not sits in wikis
  3. Evidence accumulates automatically, not through manual testing
  4. Voice is preserved programmatically, not through reminder protocols
  5. Intent flows to deployment, not through manual intervention

  ---
  Part II: Multi-Part Implementation Plan

  Phase 0: Foundation Wiring (1 week)

  Prerequisite: Wire existing systems together

  Checkpoint 0.1: Stigmergy → Coffee Integration

  User Journey: "Morning voice deposits pheromones"

  kg coffee begin
    ↓
  Voice captured: "Today I want to finish verification integration"
    ↓
  Pheromone deposited at: [verification, integration, finish]
    ↓
  kg coffee end (accomplished)
    ↓
  Pheromones reinforced (intensity × 1.5)

  Deliverables:
  - Wire PheromoneField to CaptureSession in services/liminal/coffee/
  - Create VoiceStigmergy service: MorningVoice → PheromoneDeposit[]
  - Persist pheromone field via D-gent (XDG-compliant)
  - Add reinforcement on kg coffee end with accomplished=true

  Verification: test_voice_deposits_pheromones.py — voice → pheromones → decay over 24h

  ---
  Checkpoint 0.2: Hydrator → Brain Integration

  User Journey: "Hydration uses semantic similarity, not just keywords"

  kg docs hydrate "finish verification integration"
    ↓
  Brain vectors find semantically similar gotchas
    ↓
  ASHC prior evidence for similar work surfaces
    ↓
  Context compiled with semantic depth

  Deliverables:
  - HydrationBrainAdapter: Use Brain crystals for semantic matching
  - Add prior_evidence: list[ASHCEvidence] to HydrationContext
  - Integrate ASHC causal graph predictions into hydration

  Verification: Semantic match outperforms keyword match on diverse task descriptions

  ---
  Checkpoint 0.3: Session Polynomial Stub

  User Journey: "Session has observable state"

  # The MetabolicPolynomial from spec becomes reality
  session = MetabolicSession.begin()  # → AWAKENING
  await session.capture_voice("...")  # → HYDRATING
  await session.hydrate()             # → FLOWING
  # ... development happens ...
  await session.end()                 # → CRYSTALLIZING → DORMANT

  Deliverables:
  - services/metabolism/session.py: MetabolicPolynomial implementation
  - Session persistence via D-gent
  - State transitions emit events to SynergyBus

  Verification: State machine transitions are valid per spec; events fire on each transition

  ---
  Phase 1: Morning Start Journey (2 weeks)

  The ritual that grounds every session

  Checkpoint 1.1: Circadian Resonance

  User Journey: "The garden knows things from yesterday"

  $ kg coffee begin

  ☕ Good morning

  💫 This morning echoes December 14th...
     Then, you said: "I want to feel like I'm exploring, not completing."
     That morning, you chose 🎲 SERENDIPITOUS and discovered sheaf coherence.

  📍 FROM YOUR PATTERNS
     "Ship something" appears in 7 of last 10 mornings
     "Depth over breadth" — recurring voice anchor

  Deliverables:
  - CircadianResonance: Match current morning to similar past mornings
  - VoiceArchaeology: Stratigraphy of past voice (SURFACE/SHALLOW/FOSSIL)
  - PatternDetector: Identify recurring themes without ML

  Verification: Resonance matching works across 30+ days of voice history

  ---
  Checkpoint 1.2: Serendipity Integration (Accursed Share)

  User Journey: "10% chance of unexpected wisdom"

  🎲 FROM THE VOID (10% serendipity)
     Three weeks ago: "The constraint is the freedom"

  Deliverables:
  - 10% serendipity trigger on kg coffee begin
  - Deep archaeology sampling (FOSSIL layer, not recent)
  - void.metabolism.serendipity AGENTESE path

  Verification: Serendipity fires ~10% of sessions; wisdom is > 14 days old

  ---
  Checkpoint 1.3: Full Morning Start Flow

  User Journey: "From intent to hydrated context in 5 minutes"

  Complete kg coffee begin → capture → hydrate → ready flow:

  $ kg coffee begin

  ☕ Good morning
  # ... resonance, patterns, serendipity ...

  [What brings you here today?]
  > finish the verification integration and make it feel magical

  ✨ Intent captured. Hydrating context...

  🚨 CRITICAL (2)
    - ASHC Compiler: Evidence requires 10+ runs (test_evidence.py)
    - Verification: Trace witnesses must link to requirements

  📁 FILES YOU'LL LIKELY TOUCH
    - services/verification/core.py
    - protocols/ashc/evidence.py

  🎯 VOICE ANCHORS (preserve these)
    "Tasteful > feature-complete"
    "The Mirror Test"

  Context compiled. Good morning, Kent.

  Deliverables:
  - Full CLI handler: kg coffee begin
  - Integration with Hydrator + ASHC prior evidence
  - Session polynomial transition: DORMANT → AWAKENING → HYDRATING → FLOWING
  - Context injection for Claude Code (HYDRATE.md generation)

  Verification: End-to-end flow works; context is relevant to stated intent

  ---
  Phase 2: Evidence Pipeline (2 weeks)

  Background evidence accumulation

  Checkpoint 2.1: ASHC Continuous Mode

  User Journey: "Verification happens in the background"

  # Developer saves file
  services/verification/core.py saved
    ↓
  [Background] ASHC adaptive verification triggered
    ↓
  Evidence corpus grows (+1 run, diversity score updated)
    ↓
  Causal graph learns: "type hints" → +8% pass rate
    ↓
  [Only on critical failure] Developer notified

  Deliverables:
  - BackgroundEvidencing class: fire-and-forget verification
  - DiversityScoring: Weight by input variation, not run count
  - Causal graph learning: nudge → outcome tracking
  - Silent accumulation (only critical failures surface)

  Verification: 100 identical runs ≠ 100x confidence; diversity scoring prevents inflation

  ---
  Checkpoint 2.2: Interactive Text Core

  User Journey: "Specs are live control surfaces"

  - [x] Implement verification integration
    ↓ (click)
  TraceWitness captured
    ↓
  Linked to requirement 7.1
    ↓
  Evidence attached to derivation chain

  Deliverables:
  - services/interactive-text/ Crown Jewel structure
  - Token parser: AGENTESE paths, task checkboxes, images, code blocks
  - TaskCheckboxToken.on_toggle() → TraceWitness capture
  - Roundtrip fidelity: parse(render(parse(doc))) ≡ parse(doc)

  Verification: Task completion in spec creates linked TraceWitness

  ---
  Checkpoint 2.3: Verification Graph

  User Journey: "See the derivation chain"

  Principle (Composable)
      └── Requirement 5.1: Agents compose via >>
          └── Task: Implement composition operator
              └── Trace: test_compose.py::test_pipeline passed
                  └── Evidence: 47 runs, 94% pass rate

  Deliverables:
  - VerificationGraph: Principle → Requirement → Task → Trace → Evidence
  - AGENTESE path: concept.docs.derivation
  - CLI: kg docs derivation spec/agents/poly.md

  Verification: Full derivation chain traceable from principle to evidence

  ---
  Phase 3: Voice Intelligence (2 weeks)

  Pattern learning without ML

  Checkpoint 3.1: Full Stigmergy Implementation

  User Journey: "Patterns emerge from repeated deposits"

  # After 10 mornings mentioning "verification"
  patterns = await stigmergy.sense_patterns("today I want to work on testing")
  # → [("verification", 0.87), ("testing", 0.72), ("evidence", 0.45)]

  Deliverables:
  - PheromoneField with configurable decay (5% per day default)
  - End-of-day reinforcement loop (cron or session-end)
  - Pattern detection via gradient strength
  - void.metabolism.patterns AGENTESE path

  Verification: Patterns stabilize after 10+ deposits; decay prevents fossilization

  ---
  Checkpoint 3.2: Anti-Sausage Automation

  User Journey: "Voice drift is detected and flagged"

  $ kg voice check --since-last-commit

  ⚠️  VOICE DRIFT DETECTED

  ORIGINAL: "Daring, bold, creative, opinionated but not gaudy"
  PARAPHRASED AS: "Creative and opinionated design principles"

  SUGGESTION: Use the original quote directly.

  Deliverables:
  - VoiceDriftDetector: Identify paraphrased anchors
  - Session-end verification (opt-in)
  - Git hook integration for pre-commit check
  - self.metabolism.voice.check AGENTESE path

  Verification: Paraphrased anchors are flagged with suggested restoration

  ---
  Checkpoint 3.3: Circadian Full Implementation

  User Journey: "Weekly patterns detected"

  📍 YOUR WEEKLY RHYTHM
     Mondays: "planning mode" (4 of last 5)
     Thursdays: "ship something" (3 of last 4)
     Fridays: "exploration" (2 of last 3)

  Deliverables:
  - Weekly pattern detection
  - Time-of-day awareness (morning vs evening Kent)
  - Circadian coordinates in MorningVoice

  Verification: Weekly patterns emerge from 4+ weeks of data

  ---
  Phase 4: Session Handoff & Ship (1 week)

  Clean endings, clear continuations

  Checkpoint 4.1: Handoff Generation

  User Journey: "Next session has perfect context"

  $ kg coffee end

  ☕ Session closing

  Did you accomplish your morning intention? [Y/n/partial]
  > partial

  What did you complete?
  > Got trace witness wiring done, but magic is still missing

  📝 HANDOFF GENERATED
     Intent: Finish verification integration with magic
     Progress:
       - Trace witness wiring complete
     Blockers:
       - "Magic" still undefined (needs design)
     Next Steps:
       1. Define what "magical" means for verification
       2. Implement the magical bits
     Voice Anchors:
       - "Tasteful > feature-complete"
       - "magical" → preserved as personal anchor

  kg handoff > /tmp/handoff-2025-12-21.md

  Deliverables:
  - MetabolicHandoff type with compression
  - kg coffee end CLI handler
  - kg handoff generation command
  - Session polynomial transition: FLOWING → CRYSTALLIZING → DORMANT

  Verification: Handoff prompt is self-contained; next session can continue without context loss

  ---
  Checkpoint 4.2: Celebration Loop

  User Journey: "Shipping reinforces patterns"

  $ kg commit-push

  ✅ All tests pass
  ✅ mypy clean
  ✅ lint clean

  📦 SHIPPED: verification integration

  🎉 CELEBRATION LOOP
     Patterns reinforced (×2.0 multiplier):
       - verification
       - integration
       - trace
     Voice crystallized: "Ship something" → FOSSIL layer in 90 days

  Deliverables:
  - CelebrationLoop: Ship success → pattern reinforcement
  - Fossil layer promotion (patterns that persist 90+ days)
  - Evidence summary in commit message
  - Cross-jewel events: Ship → Brain crystal, Gardener plot update

  Verification: Ship event reinforces patterns more than task completion

  ---
  Checkpoint 4.3: Waste Compost (Accursed Share)

  User Journey: "Failed experiments are learnings, not shame"

  🗑️  COMPOST (what didn't work)
     - Tried making verification synchronous—blocked UI, reverted
     - Explored caching strategy—too complex for now, documented for later

  Deliverables:
  - CompostPile: Store abandoned approaches
  - void.metabolism.compost AGENTESE path
  - Include compost in handoff generation
  - Future fertilization: surface relevant past failures when starting similar work

  Verification: Compost entries persist; relevant failures surface on similar tasks

  ---
  Part III: User Journeys with Verification Criteria

  Journey 1: Morning Start

  | Step               | Verification Criterion                                  |
  |--------------------|---------------------------------------------------------|
  | kg coffee begin    | Session polynomial transitions DORMANT → AWAKENING      |
  | Resonance surfaced | At least one resonant morning shown (if history exists) |
  | Patterns shown     | Top 3 patterns from stigmergy field                     |
  | Serendipity fires  | ~10% of sessions show deep archaeology                  |
  | Voice captured     | Intent stored, pheromones deposited                     |
  | Hydration runs     | Context includes gotchas, files, voice anchors          |
  | Session ready      | Polynomial in FLOWING state                             |

  Journey 2: Feature Implementation

  | Step            | Verification Criterion                          |
  |-----------------|-------------------------------------------------|
  | File saved      | Background verification triggers (non-blocking) |
  | Evidence grows  | Diversity score increases, not just run count   |
  | Task toggled    | TraceWitness captured and linked to requirement |
  | Causal learning | Nudge → outcome edges added to graph            |
  | Voice preserved | Session output doesn't paraphrase anchors       |

  Journey 3: Session Handoff

  | Step                 | Verification Criterion                          |
  |----------------------|-------------------------------------------------|
  | kg coffee end        | Polynomial transitions FLOWING → CRYSTALLIZING  |
  | Accomplishment asked | Intent compared to outcome                      |
  | Patterns reinforced  | Stigmergy field updated based on accomplishment |
  | Handoff generated    | Self-contained prompt with compression          |
  | Compost captured     | Abandoned approaches documented                 |
  | Session closed       | Polynomial in DORMANT state                     |

  Journey 4: Verification & Ship

  | Step                | Verification Criterion                   |
  |---------------------|------------------------------------------|
  | Evidence reviewed   | ASHC evidence summary available          |
  | Drift checked       | Spec↔impl divergence surfaced            |
  | Voice checked       | Anti-sausage verification runs           |
  | Ship happens        | kg commit-push with evidence summary     |
  | Celebration loop    | Patterns reinforced with ×2.0 multiplier |
  | Archaeology updated | Voice deposits to FOSSIL layer over time |

  ---
  Part IV: Cross-Jewel Wiring Matrix

  The metabolic system integrates across Crown Jewels:

  | Event                | Source           | Target      | Handler                            |
  |----------------------|------------------|-------------|------------------------------------|
  | voice.captured       | Coffee           | Brain       | brain_capture_voice_as_crystal     |
  | voice.captured       | Coffee           | Gardener    | gardener_update_voice_patterns     |
  | context.hydrated     | Living Docs      | K-gent      | kgent_absorb_voice_anchors         |
  | evidence.accumulated | ASHC             | Brain       | brain_crystallize_evidence         |
  | task.completed       | Interactive Text | Witness     | witness_capture_mark               |
  | test.failed          | ASHC             | Living Docs | living_docs_create_teaching_moment |
  | approach.abandoned   | Session          | Compost     | compost_add_entry                  |
  | session.ended        | Coffee           | All         | crystallize_session                |
  | ship.succeeded       | Git              | All         | celebration_loop                   |

  Implementation: Wire via SynergyBus using existing patterns from Witness Phase 2.

  ---
  Part V: Technical Architecture

  impl/claude/services/
  ├── metabolism/                    # NEW: Metabolic core
  │   ├── __init__.py
  │   ├── session.py                 # MetabolicPolynomial, SessionState
  │   ├── handoff.py                 # HandoffGenerator, MetabolicHandoff
  │   ├── celebration.py             # CelebrationLoop, pattern reinforcement
  │   ├── compost.py                 # CompostPile, abandoned approach storage
  │   └── node.py                    # AGENTESE: self.metabolism.*
  ├── liminal/coffee/                # EXISTS: Extend with stigmergy
  │   ├── capture.py                 # Add stigmergy wiring
  │   ├── stigmergy.py               # NEW: VoiceStigmergy service
  │   ├── circadian.py               # NEW: CircadianResonance
  │   └── archaeology.py             # NEW: VoiceArchaeology
  ├── living_docs/                   # EXISTS: Extend with Brain/ASHC
  │   ├── hydrator.py                # Add Brain vectors, ASHC evidence
  │   └── brain_adapter.py           # NEW: Semantic matching via Brain
  ├── interactive_text/              # NEW: Crown Jewel
  │   ├── __init__.py
  │   ├── parser.py                  # Markdown → AST with tokens
  │   ├── tokens/                    # Token type implementations
  │   ├── sheaf.py                   # DocumentSheaf coherence
  │   ├── polynomial.py              # Document state machine
  │   └── node.py                    # AGENTESE: self.document.interactive
  └── witness/                       # EXISTS: Integrate with metabolic events
      └── bus.py                     # Add metabolic event handlers

  ---
  Part VI: Risk Mitigations

  | Risk                             | Mitigation                                                    |
  |----------------------------------|---------------------------------------------------------------|
  | Context overload                 | Hard limits: MAX_TEACHING=5, MAX_FILES=8, MAX_EVIDENCE=3      |
  | Stale stigmergy                  | 5% daily decay, reinforcement cap of 10.0                     |
  | Evidence inflation               | Diversity scoring: unique_inputs / total_runs                 |
  | Voice drift                      | Paraphrase detection + pre-commit hook                        |
  | Session boundary ambiguity       | Prefer explicit; implicit detection prompts, doesn't auto-end |
  | Background verification blocking | Fire-and-forget async; only critical failures surface         |

  ---
  Part VII: Success Metrics

  | Metric                  | Target                                             | Measurement                |
  |-------------------------|----------------------------------------------------|----------------------------|
  | Morning ritual adoption | 80% of sessions start with kg coffee begin         | CLI telemetry              |
  | Context relevance       | 70%+ of surfaced gotchas are "useful"              | User feedback on hydration |
  | Evidence confidence     | Diversity score ≥ 0.5 for shipped features         | ASHC metrics               |
  | Voice preservation      | < 5% paraphrase rate on anchors                    | Drift detector             |
  | Pattern stability       | Top 3 patterns stable after 10 deposits            | Stigmergy field stats      |
  | Handoff completeness    | 90% of next sessions continue without context loss | Manual review              |

  ---
  Part VIII: Implementation Schedule

  | Week     | Phase   | Checkpoints                                                             |
  |----------|---------|-------------------------------------------------------------------------|
  | Week 1   | Phase 0 | 0.1 (Stigmergy→Coffee), 0.2 (Hydrator→Brain), 0.3 (Session Polynomial)  |
  | Week 2-3 | Phase 1 | 1.1 (Circadian), 1.2 (Serendipity), 1.3 (Full Morning Start)            |
  | Week 4-5 | Phase 2 | 2.1 (ASHC Continuous), 2.2 (Interactive Text), 2.3 (Verification Graph) |
  | Week 6-7 | Phase 3 | 3.1 (Full Stigmergy), 3.2 (Anti-Sausage), 3.3 (Circadian Full)          |
  | Week 8   | Phase 4 | 4.1 (Handoff), 4.2 (Celebration), 4.3 (Compost)                         |

  Total: 8 weeks to transformative developer experience

  ---
  Part IX: The Transformative Impact

  This isn't an incremental improvement. It's a fundamental shift in how development happens:

  | Before                              | After                                                |
  |-------------------------------------|------------------------------------------------------|
  | Sessions are isolated chat threads  | Sessions are compilation units with memory           |
  | Context is manually gathered        | Context compiles from voice + stigmergy + evidence   |
  | Testing is manual verification      | Evidence accumulates continuously in background      |
  | Voice drifts through LLM processing | Voice is preserved and checked programmatically      |
  | Handoffs lose context               | Handoffs compress without loss                       |
  | Failed experiments are hidden       | Failed experiments are composted for future learning |
  | Success is forgotten                | Success reinforces patterns, crystallizes voice      |

  "The master's touch was always just compressed experience. Now we compile the compression."

  ---
  Closing: Why This Matters

  The Metabolic Development Protocol embodies every kgents principle:

  | Principle     | How Metabolic Development Embodies It             |
  |---------------|---------------------------------------------------|
  | Tasteful      | Focused context, not exhaustive dumps             |
  | Curated       | Relevant gotchas, not all gotchas                 |
  | Ethical       | Evidence over claims; waste visible, not hidden   |
  | Joy-Inducing  | Morning ritual feels like coming home             |
  | Composable    | Four systems compose into unified pipeline        |
  | Heterarchical | Sessions flow, not stack                          |
  | Generative    | Context compiles from source; spec generates impl |