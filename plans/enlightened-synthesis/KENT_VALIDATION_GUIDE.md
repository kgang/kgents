# Kent Validation Guide: Week 4 Gate

> *"The day is the proof. Honest gaps are signal. Compression is memory."*

**Purpose**: This guide walks Kent through validating the trail-to-crystal pilot by using it for 1 real work day.
**Date**: Week 4 (Current)
**Prerequisites**: P0, P1, P2 complete (1,700+ tests passing)

---

## Quick Start (5 Minutes)

### 1. Start the Backend
```bash
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

### 2. Start the Frontend
```bash
cd impl/claude/pilots-web
npm install  # Only needed first time
npm run dev
```

### 3. Open in Browser
Navigate to: **http://localhost:3000**

---

## The Validation Day

### Morning Ritual (~2 minutes)

1. **Open the Daily Lab pilot**
2. **Create your first mark** of the day:
   - What: Brief description of what you're doing
   - Why: What principle/intent is guiding this?
   - Time: Auto-captured

**Target**: Mark capture should feel < 5 seconds

### Throughout the Day

**Mark significant moments:**
- Starting a task
- Completing something meaningful
- Making a decision
- Switching context
- Moments of insight or frustration

**Don't mark:**
- Every tiny action
- Routine/habitual tasks (unless significant)
- Breaks (let gaps exist—they're data!)

**Target**: 10-30 marks for a typical day

### End of Day (~2 minutes)

1. **Review your trail** - See all marks in timeline
2. **Notice the gaps** - System surfaces untracked time
3. **Generate crystal** - Compress the day into meaning
4. **Export/share** - Create shareable artifact

---

## Qualitative Assertions to Validate

### QA-1: Lighter Than a To-Do List

**The Test**: Does marking feel like effort, or like witnessing?

| Metric | Target | What to Notice |
|--------|--------|----------------|
| Time to mark | < 5 seconds | Did you hesitate? |
| End-of-day crystal | < 2 minutes | Did it feel like homework? |
| Overall feeling | "witnessed, not surveilled" | Would you use this tomorrow? |

**Pass**: The ritual feels lighter than writing a to-do list.
**Fail**: You dread opening it, feel watched, or feel obligated.

---

### QA-2: Honest Gaps Are Data

**The Test**: When gaps appear, do you feel shame or neutrality?

| What to Notice | Pass | Fail |
|----------------|------|------|
| Gap presentation | Neutral data | Error message |
| Language used | "resting", "reflecting", "space" | "idle", "untracked", "missing" |
| Your reaction | "Interesting" | "I should have..." |

**Pass**: Gaps feel like part of the story, not failures.
**Fail**: You feel guilty about untracked time.

---

### QA-3: Crystals Deserve Re-Reading

**The Test**: Would you voluntarily return to this crystal?

| Aspect | Pass | Fail |
|--------|------|------|
| Warmth | Has texture, feels human | Bullet list, sterile |
| Shareability | Would share without embarrassment | Would edit before sharing |
| Memory quality | "This captures my day" | "This summarizes events" |

**Pass**: The crystal feels like a memory artifact.
**Fail**: The crystal reads like a report.

---

### QA-4: Bold Choices Protected

**The Test**: If you made a risky decision today, was it penalized?

| Scenario | Pass | Fail |
|----------|------|------|
| High-risk mark | No negative weighting | Score penalty |
| Creative leap | Celebrated | Flagged as concern |
| Unconventional choice | Protected by COURAGE_PRESERVATION | Discouraged |

**Pass**: Daring feels safe within the system.
**Fail**: You played safe because you felt scored.

---

### QA-5: Explain Your Day with Crystal + Trail

**The Test**: Can you answer "what did you do today?" using only the pilot?

| Requirement | Pass | Fail |
|-------------|------|------|
| Crystal sufficiency | Explains the narrative | Missing key context |
| Trail sufficiency | Shows the sequence | Gaps in the story |
| External sources needed? | No | Yes (checked calendar, email) |

**Pass**: Crystal + trail is sufficient for "what did I do today?"
**Fail**: You needed other sources to remember.

---

### QA-6: No Hustle Theater

**The Test**: Did the system create pressure to perform?

| Anti-Pattern | Present? | Notes |
|--------------|----------|-------|
| Streak counters | Should be NO | |
| Leaderboards | Should be NO | |
| Productivity metrics | Should be NO | |
| "Mark more" pressure | Should be NO | |
| Gamification | Should be NO | |

**Pass**: Zero performance pressure.
**Fail**: Any gamification or hustle mechanics.

---

## Feedback Template

After your validation day, fill out this feedback:

```markdown
# Kent Validation Day Feedback

**Date**: ____
**Total Marks**: ____
**Total Gaps**: ____

## QA-1: Lighter Than a To-Do List
- [ ] PASS / [ ] FAIL
- Notes:

## QA-2: Honest Gaps Are Data
- [ ] PASS / [ ] FAIL
- Notes:

## QA-3: Crystals Deserve Re-Reading
- [ ] PASS / [ ] FAIL
- Notes:

## QA-4: Bold Choices Protected
- [ ] PASS / [ ] FAIL
- Notes:

## QA-5: Explain Day with Crystal + Trail
- [ ] PASS / [ ] FAIL
- Notes:

## QA-6: No Hustle Theater
- [ ] PASS / [ ] FAIL
- Notes:

## Overall

### What Worked
-

### What Didn't Work
-

### Somatic Response
(Trust your gut—"This feels dead" is valid feedback)
-

### Mirror Test
> "Does this feel like me on my best day?"
- [ ] YES / [ ] NO

### Go/No-Go Decision
- [ ] GO: Ship trail-to-crystal
- [ ] NO-GO: Redesign needed (specify what)
```

---

## If Something Breaks

### Backend Issues
```bash
# Check logs
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000 --log-level debug

# Run tests to verify
uv run pytest services/witness/_tests/ -q
```

### Frontend Issues
```bash
# Check types
cd impl/claude/pilots-web
npm run typecheck

# Check logs in browser console
```

### API Not Responding
- Verify backend is running on port 8000
- Check CORS settings in protocols/api/app.py
- Try: `curl http://localhost:8000/api/health`

---

## The Mirror Test

> *"Does this feel like Kent on my best day — daring, bold, creative, opinionated but not gaudy?"*

At the end of the day, ask yourself:

1. **Would I use this tomorrow?**
2. **Did it help me remember or just track?**
3. **Did I feel witnessed or surveilled?**
4. **Does the crystal have warmth?**
5. **Is this tasteful, or just feature-complete?**

If any answer is "no" — that's signal. The system should redesign before shipping.

---

## The Mantra

```
The day is the proof.
Honest gaps are signal.
Compression is memory.
Joy composes.
The mark IS the witness.
```

---

**Filed**: 2025-12-26
**Status**: Ready for Kent Validation
**Next Step**: Complete 1 real day, fill out feedback template

*"Daring, bold, creative, opinionated but not gaudy."*
