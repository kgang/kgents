# Run 001 Learnings

**Run**: 001 (Genesis)
**Status**: GO
**Date**: 2025-12-26

---

## Key Insights

### 1. Joy Functor Calibration Reveals Domain Trade-offs

The 04-joy-integration.md specifies SURPRISE as secondary and FLOW as tertiary for rap-coach. However, the PROTO_SPEC emphasizes "The loop is tight" and "pace of practice must remain FLUID" - suggesting FLOW might be more important than initially calibrated.

**Insight**: Joy calibration may need domain-expert input beyond spec authors. The difference between SURPRISE 0.3/FLOW 0.7 vs SURPRISE 0.7/FLOW 0.3 is significant for creative domains.

**Recommendation for Run 002**: Create a calibration validation step that checks PROTO_SPEC language against joy weights.

### 2. Courage Protection is a Functor Law, Not Just a Feature

Initially conceived as a feature ("protect high-risk takes"), the L4 Courage Preservation Law is actually a functor law:

```
Courage: Take -> ProtectedTake
protect(score, courage_level) = max(FLOOR, score) + BOOST

This MUST satisfy:
- protect(0, HIGH) > protect(0, LOW)  -- Courage always wins
- protect(x, HIGH) >= x              -- Protection never hurts
```

**Insight**: The law can be verified categorically. Future runs should include property-based tests for this.

### 3. Warmth is Structural, Not Decorative

The anti-coldness requirement is deeper than "add warm words." Warmth must be structural:

- **Input warmth**: How the system asks for intent
- **Process warmth**: How feedback is grounded (L2)
- **Output warmth**: How crystals read

The `AntiJudgeDetector` is necessary but not sufficient. We also need warmth in:
- Error messages
- Loading states
- Empty states

**Recommendation for Run 002**: Create a WarmthAudit that scans all user-facing strings.

### 4. Through-Line (L3) Needs LLM Assistance

The current `VoiceThroughline.from_session()` uses heuristics (register analysis, joy mode counting). This is insufficient for real through-line detection.

A proper through-line requires semantic understanding:
- What was the artist working on across takes?
- What themes recurred?
- What was being avoided?

**Recommendation for Run 002**: Integrate LLM crystallization for through-line detection, similar to how `services/witness/crystal.py` uses LLM for insight generation.

### 5. Repair Paths (L5) Need Galois Loss Per Take

Currently, we compute session-level Galois loss. For L5 to work properly, we need:

```
For each take:
  intent_text = intent.expression_goal + intent.register
  delivery_text = take.transcription
  loss = galois_distance(intent_text, delivery_text)
  if loss > 0.5:
    generate_repair_path(take, loss)
```

**Recommendation for Run 002**: Implement per-take Galois loss computation using `services/zero_seed/galois/distance.py`.

### 6. Ghost Alternatives Are Underspecified

The PROTO_SPEC mentions ghosts: "Ghosts (rejected phrasings, alternate lines) are part of the proof space."

The current implementation has a placeholder `GhostAlternative` type but no capture mechanism. How does the artist record ghosts?

Options:
1. Explicit: Artist types rejected lines after take
2. Implicit: System detects self-corrections in transcription
3. Prompted: System asks "what did you almost say?"

**Recommendation for Run 002**: Design ghost capture UX with artist input.

---

## Prompt Improvements for Run 002

### 1. Include PROTO_SPEC Personality Tag Earlier

The personality tag should be in the first paragraph of any generation prompt:

```markdown
**Personality**: "This pilot celebrates the rough voice, not the polished one.
The coach is a witness, never a judge."
```

This was buried in the spec but should anchor all generation.

### 2. Make Laws Explicit in Generation

Each generated file should reference which laws it implements:

```python
"""
This module implements L4 Courage Preservation Law.
See: pilots/rap-coach-flow-lab/PROTO_SPEC.md

L4: "High-risk takes are protected from negative weighting by default.
    Courage is rewarded, not punished."
"""
```

### 3. Include Anti-Success Patterns as Test Cases

Anti-success patterns should generate test cases:

```python
def test_no_judge_emergence():
    """Anti-success: Coach should never feel evaluative."""
    detector = AntiJudgeDetector()
    for response in ALL_WARMTH_TEMPLATES:
        assert not detector.is_judge_language(response)
```

---

## Contract Amendments Needed

### 1. Add `GhostAlternative` Capture Mechanism

The `GhostAlternative` type exists but needs:
- Capture trigger in UX
- Optional vs required status
- Relationship to mark

### 2. Consider `TakeAudio` Type

Current spec assumes text/transcription. For actual rap coaching:
- Audio file reference
- Waveform analysis data
- Beat alignment markers

This is out of scope for theoretical validation but needed for production.

### 3. Add `SessionWarmth` Aggregate Type

For warmth monitoring across sessions:

```typescript
interface SessionWarmth {
  warmth_score: number;  // [0, 1]
  judge_language_count: number;
  coach_language_count: number;
  courage_acknowledgments: number;
}
```

---

## Pattern Recognition

This is Run 001 (genesis), so no cross-run patterns yet.

**Seed Patterns to Watch**:
1. Does joy calibration stabilize across runs?
2. Do warmth templates need expansion?
3. Is the courage floor (0.5) appropriate?
4. Does through-line detection improve with LLM?

---

## Theory Validation Status

The core theory this pilot validates:

> **"Joy composes and Courage is preserved."**

### Joy Composes: PARTIALLY VALIDATED

- RAP_COACH_JOY functor defined and composes with base JoyFunctor
- SessionJoyProfile aggregates observations
- Warmth responses generated from observations

**Missing**: Actual composition proof (show that `session_joy >> crystal_joy = day_joy`)

### Courage is Preserved: VALIDATED

- CourageProtectionEngine implements floor and boost
- CourageMoment preserved in VoiceCrystal
- AntiJudgeDetector prevents judge emergence

**Evidence**: The L4 law is structurally enforced - a courageous take cannot have intensity below 0.5.

---

## Witness Crystal

```bash
kg decide --fast "Run-001 learnings crystallized" \
   --reasoning "Joy calibration needs domain input, courage protection is a functor law, warmth is structural" \
   --json
```

---

## Next Run Focus

Run 002 should focus on:

1. **Per-take Galois loss** for L5 repair paths
2. **LLM-assisted through-line** for L3
3. **Ghost capture UX** design
4. **Property-based tests** for L4 functor law
5. **Warmth audit** across all strings

---

*Crystallized: 2025-12-26 | Protocol: Witnessed Regeneration v1.0*
