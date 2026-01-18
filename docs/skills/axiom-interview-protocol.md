# Axiom Interview Protocol

> *"Axioms are not stipulated but discovered. They are the fixed points of your decision landscape."*

**Purpose**: Surface Kent's undocumented axioms (L1) and values (L2) through structured elicitation.

**Why This Matters**: The calibration corpus needs ground-truth examples that no LLM could generate. Kent's genuine fixed points—the principles he would never violate—are the only authentic L1 content.

---

## Interview Framework

### Phase 1: Negation Discovery (5 minutes)

These questions surface axioms by asking what Kent would **never** do.

| Question | Target Layer | Notes |
|----------|--------------|-------|
| "What principle would you never violate, even if it meant the project failing?" | L1 | Axioms are unconditional |
| "If someone paid you $1M to ship kgents without witnessing, would you?" | L1 | Tests if witnessing is axiomatic |
| "Is there any feature you'd rather not ship than ship ugly?" | L2 | Tests taste as value |
| "Would you ever ship code that works but you don't understand?" | L1 or L2 | Tests comprehension requirement |
| "Would you compromise composability for a 10x performance gain?" | L2 | Tests principle hierarchy |

### Phase 2: Disgust Mapping (5 minutes)

Kent's somatic disgust is an absolute veto. Surface what triggers it.

| Question | Target Layer | Notes |
|----------|--------------|-------|
| "When you feel visceral disgust at code, what specifically triggers it?" | L2 | Aesthetic values |
| "Describe the last time you felt 'this is wrong' before you could explain why." | L1 | Pre-verbal axioms |
| "What pattern makes you want to delete everything and start over?" | L2 | Anti-patterns as inverse values |
| "What does 'gaudy' mean to you in code?" | L2 | Calibrates aesthetic language |
| "When Claude smooths your rough edges, what gets lost?" | L2 | Anti-Sausage calibration |

### Phase 3: Trade-off Forcing (5 minutes)

Force choices between principles to reveal hierarchy.

| Trade-off | Target | Notes |
|-----------|--------|-------|
| "Joy-inducing OR ethical—if you could only pick one?" | L1 | Should refuse (ethical is floor) |
| "Tasteful OR shipped on time?" | L2 | Tests "tasteful > feature-complete" |
| "Composable OR simple?" | L2 | Tests principle priority |
| "Depth OR breadth?" | L2 | Should be depth (documented) |
| "Your voice OR AI capability?" | L1 | Tests mirror test priority |

### Phase 4: Historical Extraction (10 minutes)

Mine past decisions for implicit axioms.

| Question | Target Layer | Notes |
|----------|--------------|-------|
| "What decision do you wish you'd written down 6 months ago?" | L1-L3 | Missing documentation |
| "What mistake taught you the most about your principles?" | L6 → L1 | Reflection to axiom |
| "What feature did you cut that you're proud of cutting?" | L2 | Negative space values |
| "When did Claude convince you to change your mind? What was the argument?" | L6 | Identifies movable vs fixed |
| "What's the dumbest-sounding rule you follow that actually works?" | L1 | Tacit axioms |

### Phase 5: Fixed Point Detection (5 minutes)

Test if proposed axioms are truly fixed.

For each candidate axiom, ask:
1. "Can you imagine an exception?"
2. "Has this ever changed?"
3. "What would make you reconsider?"

If Kent can imagine an exception → It's L2 (value), not L1 (axiom)
If Kent cannot articulate any exception → It's likely L1

---

## Recording Protocol

During the interview, Claude should:

1. **Mark significant moments**:
```bash
km "Kent stated: [verbatim]" --tag axiom-interview --tag L1
```

2. **Record decisions**:
```bash
kg decide --fast "[the choice]" --reasoning "[Kent's reasoning]"
```

3. **Capture verbatim quotes** - The exact phrasing matters. Don't paraphrase.

---

## Post-Interview Processing

### 1. Transcribe to Calibration Corpus

For each surfaced axiom:

```json
{
  "id": "INTERVIEW-L1-XXX",
  "content": "[verbatim quote from Kent]",
  "expected_layer": 1,
  "expected_loss_range": [0.00, 0.05],
  "category": "axiom",
  "source": "axiom-interview-session-YYYY-MM-DD",
  "extraction_method": "interview",
  "notes": "[context from the question that surfaced this]"
}
```

### 2. Validation Check

For each proposed L1 axiom:
- Does restructuring preserve it? (Galois test)
- Has Kent ever violated it? (Historical check)
- Does it derive from something else? (If yes, it's not L1)

### 3. Cross-Reference

Check if the axiom already exists in:
- `calibration_corpus.json` (synthetic)
- `calibration_corpus_real.json` (real)
- `plans/_focus.md` (documented)
- `spec/principles.md` (constitutional)

If it's genuinely new → Add to `calibration_corpus_real.json`

---

## Example Session Transcript

**Claude**: "What principle would you never violate, even if it meant the project failing?"

**Kent**: "Honesty. If K-gent lies to me about its reasoning, it's not K-gent anymore. I'd rather have a broken honest system than a working deceptive one."

**Claude**: *marks*
```bash
km "Kent: Honesty is non-negotiable. A deceptive K-gent is not K-gent." --tag axiom-interview --tag L1
```

**Claude**: "Can you imagine any exception to that?"

**Kent**: "...No. If it's hiding things from me, what's the point?"

**Claude**: *records as axiom*
```json
{
  "id": "INTERVIEW-L1-001",
  "content": "A deceptive K-gent is not K-gent. Honesty is non-negotiable.",
  "expected_layer": 1,
  "expected_loss_range": [0.00, 0.05],
  "category": "axiom",
  "source": "axiom-interview-session-2026-01-17",
  "extraction_method": "interview",
  "notes": "Surfaced via negation discovery. Kent could not articulate any exception."
}
```

---

## Interview Scheduling

**Recommended**: 30 minutes, once per month
**Trigger**: When calibration corpus needs L1/L2 expansion
**Format**: Conversational, not formal

---

## Anti-Patterns

1. **Don't lead the witness** - Ask open questions, not "Isn't X an axiom for you?"
2. **Don't paraphrase too soon** - Get the exact words first
3. **Don't skip the exception test** - Many "axioms" have exceptions
4. **Don't interview tired Kent** - Axioms surface better when fresh
5. **Don't mix interview with work** - Dedicated session, not side conversation

---

*This protocol is itself subject to the Mirror Test: Does it feel like the right way to surface Kent's truth?*
