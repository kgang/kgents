# Consolidate K-gent Chatbot Prompts

## ATTACH

/hydrate

You are consolidating 4 N-Phase prompt files into 1 parameterizable meta-prompt.

---

## Context

### The Problem

The K-gent chatbot work has 4 separate prompt files (~60KB total):
- `kgent-chatbot-research.md` (RESEARCH phase)
- `kgent-chatbot-develop.md` (DEVELOP phase)
- `kgent-chatbot-strategize.md` (STRATEGIZE phase)
- `kgent-chatbot-cross-synergize.md` (CROSS-SYNERGIZE phase)

**Issues**:
1. Heavy context repetition across files (~40% redundant)
2. Hard to see overall progress
3. Each file duplicates: file maps, invariants, entropy budget, blockers
4. Phase transitions require copying state manually

### The Solution

Create ONE meta-prompt: `kgent-chatbot-nphase.md` with:
1. **Shared context** (file maps, invariants, blockers) — written once
2. **Phase selector** — parameter at top chooses which phase to execute
3. **Cumulative state** — each phase appends to shared state section
4. **Auto-continuation** — phase completion generates next phase prompt

---

## Your Mission

1. **Read all 4 source files** to extract:
   - Common context (appears in 2+ files)
   - Phase-specific actions (unique to each phase)
   - State that accumulates across phases

2. **Design the meta-prompt structure**:
   ```markdown
   # K-gent Chatbot N-Phase Meta-Prompt

   ## Phase Selector
   Execute: [RESEARCH | DEVELOP | STRATEGIZE | CROSS-SYNERGIZE | IMPLEMENT | QA | TEST]

   ## Shared Context (Always Loaded)
   [File map, invariants, blockers — single source of truth]

   ## Cumulative State (Updated Each Phase)
   [Handles created, decisions made, entropy spent]

   ## Phase: RESEARCH
   [Phase-specific mission + actions, collapsed if not selected]

   ## Phase: DEVELOP
   [...]
   ```

3. **Write the consolidated prompt** to:
   ```
   prompts/kgent-chatbot-nphase.md
   ```

4. **Archive the 4 original files** to:
   ```
   prompts/_archive/2025-12-14-completed/kgent-chatbot-research.md
   prompts/_archive/2025-12-14-completed/kgent-chatbot-develop.md
   prompts/_archive/2025-12-14-completed/kgent-chatbot-strategize.md
   prompts/_archive/2025-12-14-completed/kgent-chatbot-cross-synergize.md
   ```

---

## Extraction Guide

### Common Context (Extract Once)

From all 4 files, extract these shared elements:

**File Map** (from DEVELOP, most complete):
```
impl/claude/weave/trace_monoid.py:94-107   — append_mut()
impl/claude/weave/turn.py:60-191           — Turn[T] schema
impl/claude/weave/causal_cone.py:77-115    — project_context()
impl/claude/agents/k/soul.py:285-381       — KgentSoul.dialogue()
impl/claude/agents/k/flux.py:214-251       — KgentFlux.start()
impl/claude/agents/k/llm.py:227-268        — create_llm_client()
impl/claude/protocols/terrarium/gateway.py:272-382 — /perturb, /observe
impl/claude/protocols/terrarium/mirror.py:117-146  — HolographicBuffer
```

**Invariants** (from DEVELOP):
- Turn Immutability (frozen dataclass)
- Identity (event ID preserved)
- Associativity (composition order)
- Fire-and-Forget (HolographicBuffer)
- Topological Order (CausalCone)

**Blockers** (from DEVELOP):
- B1: No streaming in dialogue
- B2: LLM uses subprocess (no streaming)
- B3: Partial turn unclear
- B4: Turn lacks serialization
- B5: Token budget ambiguous

**Entropy Budget** (from PLAN):
- Total: 0.75
- Per-phase allocation: ~0.05-0.10 each

### Phase-Specific Content

**RESEARCH**: Map terrain, surface prior art, document blockers
**DEVELOP**: Design specs, resolve blockers, define laws
**STRATEGIZE**: Order backlog, sequence waves, checkpoint criteria
**CROSS-SYNERGIZE**: Find compositions, surface synergies, parallel execution

---

## Output Structure

The consolidated `kgent-chatbot-nphase.md` should be:
- ~15KB (down from ~60KB across 4 files)
- Self-contained (all context in one file)
- Parameterizable (phase selector at top)
- Auto-continuing (each phase generates next phase prompt)

### Template

```markdown
# K-gent Chatbot: N-Phase Meta-Prompt

## ATTACH

/hydrate

**Select Phase**: `PHASE=[RESEARCH|DEVELOP|STRATEGIZE|CROSS-SYNERGIZE|IMPLEMENT|QA|TEST]`

---

## Project Overview

Permanent K-gent chatbot on Terrarium with real LLM calls (Claude Opus 4.5).

**Parallel Tracks**:
- A: Core Chatbot (Soul → Flux → WebSocket)
- B: Trace Monoid (Turn emission, CausalCone)
- C: Dashboard (Debugger screen)
- D: LLM Infrastructure (streaming, budget)

---

## Shared Context

### File Map
[extracted from DEVELOP]

### Invariants (Category Laws)
[extracted from DEVELOP]

### Blockers
[extracted from DEVELOP, updated as resolved]

---

## Cumulative State

### Handles Created
| Phase | Artifact | Location | Status |
|-------|----------|----------|--------|
| PLAN | Scope definition | plans/deployment/permanent-kgent-chatbot.md | Complete |
| RESEARCH | Research notes | plans/deployment/_research/kgent-chatbot-research-notes.md | Complete |
| DEVELOP | API spec | plans/deployment/_specs/kgent-chatbot-api.md | Complete |
| STRATEGIZE | Ordered backlog | [inline below] | Complete |
| CROSS-SYNERGIZE | Synergy map | [pending] | Pending |

### Decisions Made
[accumulated from each phase]

### Entropy Budget
| Phase | Allocated | Spent | Remaining |
|-------|-----------|-------|-----------|
| PLAN | 0.05 | 0.05 | 0.70 |
| RESEARCH | 0.05 | 0.04 | 0.66 |
| DEVELOP | 0.10 | 0.08 | 0.58 |
| STRATEGIZE | 0.07 | 0.05 | 0.53 |
| CROSS-SYNERGIZE | 0.10 | — | — |

---

## Phase: RESEARCH

<details>
<summary>Expand if PHASE=RESEARCH</summary>

### Mission
Map terrain, de-risk later phases by discovering prior art, invariants, blockers.

### Actions
1. Read essential files (file map above)
2. Search for prior art (SoulEngine, LLM clients, WebSocket handlers)
3. Surface blockers with file:line evidence
4. Document in research notes

### Exit Criteria
- [ ] File map complete (30+ locations)
- [ ] Invariants documented (5+ laws)
- [ ] Blockers surfaced with evidence (5+)
- [ ] Research notes written

### Continuation
On completion: `⟿[DEVELOP]`

</details>

---

## Phase: DEVELOP

<details>
<summary>Expand if PHASE=DEVELOP</summary>

### Mission
Design compression: minimal specs that regenerate code. Resolve blockers with design decisions.

### Actions
1. Resolve each blocker (B1-B5) with design decision
2. Define laws with test contracts
3. Write API spec

### Exit Criteria
- [ ] All blockers have resolution
- [ ] 7 laws defined with test names
- [ ] API spec written

### Continuation
On completion: `⟿[STRATEGIZE]`

</details>

---

[Similar sections for STRATEGIZE, CROSS-SYNERGIZE, IMPLEMENT, QA, TEST]
```

---

## Verification

After writing `kgent-chatbot-nphase.md`:

1. **Size check**: Should be <20KB
2. **Completeness**: All 4 source phases represented
3. **No loss**: All decisions, file maps, invariants preserved
4. **Parameterizable**: Phase selector works
5. **Archive originals**: Move 4 files to _archive

---

## Accursed Share (5%)

Explore:
- Could this pattern generalize to ALL multi-phase prompts?
- Is there a meta-meta-prompt that generates N-Phase prompts?
- Should the phase selector be YAML frontmatter instead of markdown?

---

## Exit Criteria

- [ ] `kgent-chatbot-nphase.md` written (~15KB)
- [ ] 4 original files archived
- [ ] No information lost
- [ ] Pattern documented for future consolidations

---

*"Compression is understanding." — spec/principles.md*
