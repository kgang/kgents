# Evolution Improvement Decision Framework

**A guide for evaluating experimental improvements from the evolution pipeline**

---

## Philosophy: Tasteful Evolution

Evolution should improve the system **without** compromising its principles:
- **Tasteful**: Does it simplify or clarify? (Not just add features)
- **Composable**: Does it enhance composition? (Not break it)
- **Generative**: Can it be regenerated from spec? (Not one-off hacks)
- **Ethical**: Does it respect boundaries? (Not over-automate)

**Key question**: Would this improvement make kgents more itself, or less?

---

## Decision Criteria

For each improvement that **passed tests**, evaluate:

### 1. **Alignment with Principles** (REQUIRED)

Does this improvement align with kgents principles?

- [ ] **Tasteful**: Reduces complexity OR clarifies purpose
- [ ] **Curated**: Adds unique value (not redundant)
- [ ] **Ethical**: Augments judgment (doesn't replace it)
- [ ] **Joyful**: Makes development more delightful
- [ ] **Composable**: Enhances agent composition
- [ ] **Heterarchical**: Respects flat structure
- [ ] **Generative**: Can be regenerated from spec

**If any principle is violated, REJECT immediately.**

### 2. **Type of Improvement**

What category does this fall into?

- **Fix**: Addresses a bug or tension → **High priority**
- **Refactor**: Improves structure without changing behavior → **Medium priority**
- **Feature**: Adds new capability → **Low priority** (be skeptical)
- **Test**: Adds test coverage → **High priority**

**Bias**: Prefer fixes and tests over features. New features need strong justification.

### 3. **Confidence Score**

LLM-assigned confidence (from evolution pipeline):

- **>0.85**: High confidence → Review carefully, likely good
- **0.70-0.85**: Medium confidence → Needs scrutiny
- **<0.70**: Low confidence → Skeptical by default

### 4. **Complexity vs. Value**

Does the improvement's value justify its complexity?

**Value dimensions**:
- Prevents bugs
- Clarifies intent
- Enables composition
- Improves observability
- Reduces boilerplate

**Complexity dimensions**:
- Lines of code added
- New abstractions introduced
- New dependencies
- Cognitive load

**Rule of thumb**: Value should be 3x the complexity.

### 5. **Spec Regenerability**

Could this improvement be regenerated from the spec?

- **Yes**: Good - it's a natural consequence of spec principles
- **Unsure**: Medium - might need spec update
- **No**: Bad - it's a one-off hack, likely doesn't belong

### 6. **Breaking Changes**

Does this change existing APIs or behavior?

- **No breaking changes**: Safe to incorporate
- **Minor breaking changes**: Requires version bump, documentation
- **Major breaking changes**: REJECT unless absolutely necessary

---

## Decision Process

For each improvement that passed tests:

### Phase 1: Quick Filter (30 seconds)

1. **Read the description**: What is it trying to do?
2. **Check the improvement type**: Fix/Refactor/Feature/Test?
3. **Glance at confidence**: >0.85 or <0.85?

**Quick reject if**:
- Feature with confidence <0.85
- Description sounds like over-engineering
- "AI" or "LLM" in description for bootstrap agents (they should be mechanical)

### Phase 2: Detailed Review (2-5 minutes)

1. **Read the full diff**: What actually changed?
2. **Check against principles**: Does it violate any?
3. **Evaluate complexity**: How many lines? New concepts?
4. **Consider alternatives**: Is there a simpler way?

**Questions to ask**:
- Would Kent write this?
- Does this make the code more or less joyful to work with?
- Will this make sense 6 months from now?
- Can this be explained in 2 sentences?

### Phase 3: Decision (30 seconds)

Make one of three decisions:

#### ✅ INCORPORATE
- High confidence (>0.85)
- Clear value
- No principle violations
- Simple and elegant

**Action**: Apply the improvement, test manually, commit with message

#### ⏸️ HOLD
- Good idea but needs refinement
- Violates one principle slightly (could be fixed)
- Unsure if it fits the vision

**Action**: Save to `held_improvements/` with notes, revisit later

#### ❌ REJECT
- Low confidence (<0.70)
- Violates principles
- Adds complexity without value
- Over-engineered

**Action**: Log rejection reason, move on

---

## Practical Workflow

### Step 1: Identify Candidates

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Look for experiments that passed
# From evolution logs, find: "✓ All tests passed"
grep -r "✓ All tests passed" --include="*.log"
```

### Step 2: Review Each Candidate

For each candidate improvement:

1. **Find the experiment ID** (e.g., `sublate_fc26`)
2. **Look at the generated code** (if saved)
3. **Read the hypothesis** that motivated it
4. **Check the confidence** score

### Step 3: Make Decision

Use the 3-phase process above.

### Step 4: Execute Decision

**If INCORPORATE**:
```bash
# Manually apply the improvement (evolution pipeline should have saved it)
# Or re-run with --auto-apply for that specific module

# Test manually
/Users/kentgang/git/kgents/.venv/bin/python -m pytest tests/

# Commit
git add <changed-files>
git commit -m "evolve: <improvement-description>

<rationale>

Confidence: <confidence-score>
Type: <fix|refactor|feature|test>
Experiment: <experiment-id>

🤖 Generated with Evolution Pipeline
"
```

**If HOLD**:
```bash
# Save for later review
mkdir -p held_improvements
echo "<improvement details>" > held_improvements/<experiment-id>.md
```

**If REJECT**:
```bash
# Just move on - maybe log the reason
```

---

## Red Flags (Immediate Reject)

Watch out for these anti-patterns:

❌ **"Add AI-powered..."** - Bootstrap agents should be deterministic
❌ **"Extract into manager/factory/builder"** - Likely over-engineered
❌ **"Add comprehensive error handling everywhere"** - Conflicts are data, not errors
❌ **"Make everything async"** - Only if necessary
❌ **"Add caching/memoization"** - Premature optimization
❌ **"Introduce new dependencies"** - Bootstrap should be minimal
❌ **"Add backwards compatibility layer"** - Just change the code

---

## Example Decision

**Improvement**: `sublate_fc26` - "Add ComposedSublate middleware pattern to wrap specialized resolution strategies"

### Phase 1: Quick Filter
- **Type**: Refactor (likely)
- **Confidence**: Unknown (need to check)
- **First impression**: "Middleware pattern" sounds like it could be over-engineering OR could be good composition

### Phase 2: Detailed Review
- **Read diff**: (Would read the actual code changes)
- **Principle check**:
  - Composable? Could be enhancing composition ✓
  - Tasteful? Depends on complexity
  - Generative? Middleware is a spec-able pattern ✓
- **Complexity**: Need to see the diff

### Phase 3: Decision
- **If diff is <50 lines and clarifies Sublate composition**: ✅ INCORPORATE
- **If diff is >100 lines or adds new abstraction**: ⏸️ HOLD
- **If it's just wrapper boilerplate**: ❌ REJECT

---

## Session Template

When reviewing improvements, document decisions:

```markdown
## Evolution Review Session - <Date>

**Total candidates**: X
**Incorporated**: Y
**Held**: Z
**Rejected**: W

### Incorporated

1. **<experiment-id>**: <description>
   - **Rationale**: <why incorporated>
   - **Commit**: <commit-hash>

### Held

1. **<experiment-id>**: <description>
   - **Reason for hold**: <what needs work>
   - **Saved to**: held_improvements/<experiment-id>.md

### Rejected

1. **<experiment-id>**: <description>
   - **Reason**: <why rejected>
```

---

## Remember

**Evolution is a suggestion engine, not a decision engine.**

You (Kent + Claude Code) are the judge. Trust your taste. When in doubt, reject. It's better to have a clean, principled codebase than to accumulate "good ideas" that don't quite fit.

**Tasteful curation > Feature accumulation**
