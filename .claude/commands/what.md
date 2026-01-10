# /what — Session Status Crystallization

> *"The proof is not in the prose. The proof is in the clarity."*

Crystallize what just happened and what's next. Designed for **rapid re-orientation** after interruption.

## Usage

```
/what                    # Full session summary
/what metacompiler       # Focus on specific domain
/what --brief            # One-screen summary
```

## Protocol

### 1. Scan Current State

Read (in parallel):
- `git diff --stat` — What changed?
- `git log -3 --oneline` — Recent commits?
- `NOW.md` — Current work context
- Active plan file if any (`plans/*.md` with in-progress phases)

### 2. Generate Status Report

Format your response as:

```markdown
## Session Pulse: [HH:MM elapsed or "fresh"]

### What Just Happened
- [One-liner per significant action, max 5]
- Include: files touched, tests run, proofs generated

### Evidence State (if ASHC work)
- Pass rate: X% (n=N runs)
- Learned priors: [beneficial] / [harmful]
- Proof obligations: N pending

### Crown Jewel Movement (if applicable)
| Jewel | Before | After | Delta |
|-------|--------|-------|-------|
| [name]| X% | Y% | +Z% |

### Voice Check
- Anti-sausage: ✅ Edge preserved / ⚠️ Smoothed (what?)
- Mirror test: Feels like Kent? [Yes/Partially/No]

### What's Next
1. [Immediate next action with command hint]
2. [Follow-on if first completes]

### Quick Resume
\`\`\`bash
# Verify state
kg docs verify && uv run pytest -x -q --tb=no

# Continue with
<suggested command>
\`\`\`
```

## Domain-Specific Sections

When `$ARGUMENTS` specifies a domain, include relevant depth:

| Argument | Extra Section |
|----------|---------------|
| `metacompiler` | Evidence corpus stats, causal graph insights, work bet status |
| `proof` | Proof obligations pending, lemmas verified, discharge rate |
| `docs` | Teaching moments added, verification score, staleness |
| `witness` | Event counts, cross-jewel handler status, bus health |
| `<jewel-name>` | Crown jewel specific metrics |

## Anti-Patterns

- ❌ Don't regenerate NOW.md (that's `/chief`'s job)
- ❌ Don't create new meta files
- ❌ Don't dump full file contents (crystallize, don't expand)
- ❌ Don't suggest work (that's `/hydrate`'s job)

## Philosophy

/what is a **camera**, not a **curator**. It captures the moment without judgment.

- Brevity > completeness
- Facts > interpretation
- Commands > prose

*"Crystallize the session. Don't narrate it."*
