# /handoff — Session Transfer Protocol

> *"The next Claude should hit the ground running. No archaeology required."*

Generate a **self-contained prompt** that enables seamless session continuation. Optimized for kgents' proof-based, metacompiler, and living docs workflows.

## Usage

```
/handoff                 # Full handoff for next session
/handoff --minimal       # Essential context only (< 100 words)
/handoff --domain X      # Focus handoff on specific domain
```

## Protocol

### 1. Gather State (in parallel)

```bash
git status               # Uncommitted work?
git log -5 --oneline     # Recent trajectory
git diff --stat          # What's in flight?
```

Read:
- `NOW.md` — Current work state
- `plans/_focus.md` — Kent's standing intent (quote voice anchors!)
- Active plan file if any

### 2. Generate Handoff Prompt

Output a **complete, self-contained prompt** the user can paste into a new session:

```markdown
# Session Handoff: [3-5 word title]

> /hydrate
>
> [Voice anchor from _focus.md, quoted directly]

## Ground Truth

**NOW.md says**: [one-liner summarizing current work]
**Git state**: [clean/dirty] on [branch], [N commits ahead/behind]

## What's Done

- [Completed item with file path] ✓
- [Completed item] ✓
- (max 5 items)

## What's In Flight

- [Uncommitted change]: [file path]
- [Partial implementation]: [what's missing]

## What's Next

1. **[Immediate action]** — [why this matters]
   ```bash
   <verification command>
   ```

2. [Follow-on action]

## Evidence State (if ASHC/proof work)

| Metric | Value |
|--------|-------|
| Pass rate | X% (n=N) |
| Pending obligations | N |
| Learned priors | +N / -M |

## Gotchas the Next Claude Should Know

- ⚠️ [Non-obvious pattern or decision]
- ⚠️ [Dependency or constraint]
- (max 3, from actual session learnings)

## Verification

```bash
# Confirm state before continuing
uv run pytest -x -q --tb=no
kg docs verify
git status
```

---
*Handoff generated: [timestamp]*
*Anti-sausage check: [passed/flagged]*
```

## Domain-Specific Handoffs

When `--domain` is specified:

| Domain | Include |
|--------|---------|
| `metacompiler` | Causal graph state, work bet status, evidence corpus size |
| `proof` | Proof obligations, lemma dependency graph, discharge attempts |
| `docs` | Teaching moments added, freshness state, verification score |
| `witness` | Bus wiring state, handler registration, cross-jewel events |
| `<jewel>` | Crown jewel polynomial state, test counts, completion % |

## Minimal Mode (`--minimal`)

For quick context switches:

```markdown
# Quick Handoff: [title]

/hydrate

**State**: [one-liner]
**Next**: [one action]
**Verify**: `<command>`
```

## Anti-Patterns

- ❌ Don't include full file contents (reference paths instead)
- ❌ Don't explain concepts (the next Claude has CLAUDE.md)
- ❌ Don't dilute voice anchors (quote _focus.md directly)
- ❌ Don't skip the verification commands

## Output Location

Present the handoff for review. Suggest:
- Copy to clipboard for immediate use
- Or save to `plans/HANDOFF.md` if state is complex

**DO NOT** auto-create files. The user reviews first.

## Philosophy

A good handoff is **generative**, not descriptive. The next Claude should be able to:
1. Verify the claimed state in < 30 seconds
2. Start meaningful work immediately
3. Avoid rediscovering gotchas

*"The handoff IS the spec for session resumption."*

---

## Connection to Living Docs

Handoffs follow the same principles as `kg docs`:
- **Provenance**: Claims link to evidence
- **Freshness**: Verification commands confirm state
- **Projection**: Tailored to the next observer (Claude)

The handoff prompt is a **TeachingMoment** for the next session.
