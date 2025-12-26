# Rap Coach: Flow to Crystal

Status: proto-spec

> *"The voice is the proof. The session is the trace. Courage leaves marks."*

## Narrative
Freestyle is a laboratory of voice. Each take is a committed act of agency—raw, imperfect, *real*. Each session becomes a trace of evolving authenticity, and the system's job is to witness without flinching.

## Personality Tag
*This pilot celebrates the rough voice, not the polished one. The coach is a witness, never a judge.*

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

This pilot fails if:

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

## Canary Success Criteria

- A user can describe their **voice shift** using only the crystal: "I started defensive, but by take 5 I was owning the aggressive register."
- A user can replay a session trace and **understand every critique**—each piece of feedback points to a specific mark.
- The system surfaces at least one **repair path** for a high-loss take: "Next time, try landing the third beat before extending."
- The artist **returns to practice** more often because the system makes practice feel less lonely.

## Out of Scope

- Public publishing, social feeds, or competitive ranking.
- Beat production, mixing, or mastering tools.
- Industry comparison metrics ("you sound like X").
