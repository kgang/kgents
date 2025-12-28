# Trail to Crystal: Daily Lab

Status: **production**

> *"The day is the proof. Honest gaps are signal. Compression is memory."*
> *"The trail extends across days; today is the leading edge, not the entirety."*

---

## ⚠️ Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:
- **Implement ALL laws (L1-L9)** — complete set
- **Implement ALL QAs (QA-1 through QA-8)** — complete set
- **Real mark emission and trace persistence** — not mocked
- **Real crystal compression** — LLM-generated meaning, not templates
- **Emit actual witness marks** — not just capture intent

### Failure Conditions (Automatic Fail)

The system is **broken** if:

| Condition | Impact |
|-----------|--------|
| **FC-1** Marks don't persist across sessions | Trail lost |
| **FC-2** Crystal generation produces template text | Not a memory artifact |
| **FC-3** Day closure fails to seal trace | L1 violated |
| **FC-4** Past days inaccessible | L9 violated |
| **FC-5** Contract drift at runtime | L6 violated |

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | Marks persist and reload on refresh | Yes |
| **QG-2** | Zero TypeScript errors | Yes |
| **QG-3** | All Laws have corresponding implementation | Yes |
| **QG-4** | Crystal generated at day close is warm/meaningful | Yes |
| **QG-5** | Past days navigable (L9) | Yes |
| **QG-6** | Contract coherence tests pass (L6) | Yes |

---

## Narrative
Every day is a sequence of choices. The lab turns that sequence into a visible proof of intention and a lasting crystal of meaning—not a productivity metric, but a *witness* to how you spent your attention. Days accumulate into a continuous trail; crystals persist as memory artifacts worthy of re-visitation.

## Personality Tag
*Reward honest gaps instead of concealing them. The system is a witness, not a surveillance apparatus.*

## Objectives
- Make daily action legible as a coherent trace **without adding overhead**. Witnessing should feel lighter than a to-do list.
- Transform ordinary work into a **proof of agency**. Every mark says "I chose this."
- Produce crystals that preserve **meaning while compressing noise**. The crystal is a memory artifact, not a summary.

## Epistemic Commitments
- Every action must be a mark with **reason and principle weights**. Intent is declared, not inferred.
- The daily trace is **immutable and audit-friendly**. What happened, happened.
- Crystals are **mandatory at day close** and must justify inclusion. The ritual is non-negotiable.
- Constitutional scoring is **explainable in plain language**. No opaque numbers; the weights mean something.
- Gaps are **honored**—untracked time is not shameful; it's part of the honest record.

## Laws

- **L1 Day Closure Law**: A day is complete only when a crystal is produced. The ritual seals the trace.
- **L2 Intent First Law**: Actions without declared intent are marked as provisional. The system asks before assuming.
- **L3 Noise Quarantine Law**: High-loss marks cannot define the day narrative. Signal rises; noise stays in the trace.
- **L4 Compression Honesty Law**: All crystals must disclose what was dropped. The compression is transparent.
- **L5 Provenance Law**: Every crystal statement must link to at least one mark. No orphan claims.
- **L6 Contract Coherence Law**: API contracts have a single source of truth; frontend and backend verify against it. See `pilots/CONTRACT_COHERENCE.md`.
- **L7 Request Model Law**: All API endpoints accepting complex inputs MUST use Pydantic request models. No bare parameters for JSON bodies.
- **L8 Error Normalization Law**: API error responses MUST be normalized to strings before rendering. FastAPI validation errors (`{type, loc, msg}[]`) must be extracted into human-readable messages.
- **L9 Trail Continuity Law**: The trail extends across days; past days remain navigable, past crystals remain accessible. Today is the default view, but the full trail is always reachable.

## Qualitative Assertions

- **QA-1** The daily ritual must feel **lighter than a to-do list**. If it's friction, it's failing.
- **QA-2** The system should **reward honest gaps** rather than conceal them. Untracked time is data, not shame.
- **QA-3** The user should feel **witnessed, not surveilled**. The system is a collaborator, not a panopticon.
- **QA-4** The crystal should feel like a **memory artifact**, not a summary. It deserves to be re-read.
- **QA-5** API contracts must have a **single source of truth** in `shared-primitives/contracts/`. No dual definitions.
- **QA-6** Both frontend and backend must have **contract verification tests**. Drift is caught at test time.
- **QA-7** Contract drift must be **caught at CI time**, not runtime. Users never see interface mismatches.
- **QA-8** Re-visitation should feel like **honoring, not dwelling**. The crystal gallery is a cabinet of curiosities, not a hall of regrets. Navigation backward should feel like gratitude, not nostalgia.

## Anti-Success (Failure Modes)

The system fails if:

- **Hustle theater**: The system optimizes for "productivity"—more marks, more actions, more tracked time. The user feels pressure to perform for the system instead of for themselves.
- **Gap shame**: Untracked time feels like failure. The UI treats gaps as errors to be minimized. Honest rest becomes invisible.
- **Surveillance drift**: The system feels like it's watching, judging, scoring. The user changes behavior *because* they're being tracked, not because they chose to.
- **Summary flatness**: The crystal reads like a bulleted list—no warmth, no meaning, no sense of the day's texture. Compression becomes erasure.
- **Ritual burden**: The end-of-day crystal feels like homework. The user dreads the closure instead of looking forward to it.
- **Contract drift**: Frontend and backend disagree on API shapes. Runtime crashes reveal what tests should have caught. The user sees "undefined" errors instead of their trail.
- **Nostalgia trap**: The gallery becomes a place to dwell on "better days." The user feels worse after visiting past crystals. Navigation backward becomes avoidance of today. The gallery shows rankings or "best day" metrics.

## kgents Integrations

| Primitive | Role | Chain |
|-----------|------|-------|
| **Witness Mark** | Captures action + intent | `action → Mark.emit(reason, weights)` |
| **Witness Trace** | Immutable day history | `Mark[] → Trace.seal(day_id)` |
| **Witness Crystal** | Compressive memory artifact | `Trace → Crystal.compress(meaning)` |
| **ValueCompass** | Constitutional alignment summary | `Crystal.weights → Compass.render()` |
| **Trail** | Day navigation + evidence anchors | `Trace → Trail.navigate(marks)` |
| **Galois Loss** | Signal/noise separation | `Mark.weights → Galois.loss(intent_target)` |
| **Cartography** | Temporal navigation across days | `Trail.navigate(date) → DayPosition` |

**Composition Chain** (single day):
```
Action
  → Mark.emit(reason, weights)
  → Trace.append(mark)
  → [throughout] Galois.loss(intent_target) // noise detection
  → [on day_close] Crystal.compress(trace, meaning)
  → Compass.render(crystal.weights)
  → Trail.display(crystal, trace)
```

**Composition Chain** (multi-day navigation):
```
Trail[]
  → Cartography.navigate(date)        // temporal navigation
  → Trail.display(day.crystal, day.trace)
  → Gallery.display(crystals[])       // crystal collection view
```

## Quality Algebra

> *See: `spec/theory/experience-quality-operad.md` for universal framework*

This pilot instantiates the Experience Quality Operad via `DAILY_LAB_QUALITY_ALGEBRA`:

| Dimension | Instantiation |
|-----------|---------------|
| **Contrast** | focus_depth, intentionality, energy_flow, gap_honesty |
| **Arc** | intention → engagement → drift → recovery → closure |
| **Voice** | honest ("Gaps acknowledged?"), meaningful ("Worth remembering?"), witnessed ("Felt seen not surveilled?") |
| **Floor** | no_hustle_theater, no_gap_shame, no_surveillance_drift, marks_persist |

**Weights**: C=0.25, A=0.30, V=0.45

**Implementation**: `impl/claude/services/experience_quality/algebras/daily_lab.py`

**Domain Spec**: `spec/theory/domains/daily-lab-quality.md`

## Canary Success Criteria

- A user can explain their day **using only the crystal and trail**: "I spent the morning on deep work, drifted after lunch, and closed strong. The gap was rest, not distraction."
- The system surfaces at least one **honest gap without shaming**: "Untracked time: 2h. This is noted, not judged."
- The day ends with a **single, shareable artifact**. The crystal is portable and meaningful to others.
- The user **wants to produce the crystal**—it feels like closure, not obligation.
- The user can **navigate to any past day** and view its trail and crystal without friction.
- The **crystal gallery** feels like a personal museum, not a performance review.

## Out of Scope

- Team analytics, time tracking, or billing.
- Productivity scoring or comparison to benchmarks.
- Integration with project management tools.
- Day-to-day comparison, ranking, or "best day" metrics.
