# RESEARCH: N-Phase Prompt Compiler

## ATTACH

/hydrate

You are entering **RESEARCH** phase of the N-Phase Cycle (AD-005) for a **Crown Jewel** (Priority 10.0).

---

## Context from PLAN

### The Insight

During consolidation of 4 K-gent chatbot prompts into 1 parameterizable meta-prompt, we discovered a **universal pattern**:

```
4 prompts (~41KB) → 1 meta-prompt (~12.8KB) = 69% compression
```

**The Generalization**: Any project following N-Phase exhibits the same structure:
- Shared Context (file maps, invariants, blockers, components, waves, checkpoints)
- Cumulative State (handles, decisions, entropy, phase ledger)
- Phase Sections (parameterized by phase selector)

**The Meta-Meta-Prompt**: A compiler that generates N-Phase prompts from ProjectDefinitions.

### Handles Created in PLAN

| Artifact | Location | Status |
|----------|----------|--------|
| Plan document | `plans/meta/nphase-prompt-compiler.md` | Complete |
| Architecture design | Inline in plan | Complete |
| Component enumeration | 10 components, 3 waves | Complete |
| Category-theoretic foundation | Laws defined | Complete |
| Strategic payoff analysis | 4 payoffs expanded | Complete |
| Accursed Share explorations | 5 explorations expanded | Complete |

### Entropy Budget

- **Total**: 0.75
- **Allocated for RESEARCH**: 0.05
- **Spent in PLAN**: 0.02
- **Remaining**: 0.73

---

## Your Mission

**Map the terrain to de-risk later phases.**

You are reducing entropy by discovering:
1. **Prior art** — What existing infrastructure can we reuse?
2. **Invariants** — What contracts must be preserved?
3. **Blockers** — What could prevent implementation?

**Principles Alignment**:
- **Curated**: Prevent redundant work by finding what exists
- **Composable**: Note contracts and functor laws
- **Generative**: Identify compression opportunities

---

## Actions to Take NOW

### 1. Map Existing N-Phase Infrastructure

Read these files to understand current N-Phase implementation:

```python
# Core N-Phase specification
Read("spec/protocols/n-phase-cycle.md")

# Phase skill documentation (all 11)
Read("docs/skills/n-phase-cycle/README.md")
Read("docs/skills/n-phase-cycle/plan.md")
Read("docs/skills/n-phase-cycle/research.md")
Read("docs/skills/n-phase-cycle/develop.md")
Read("docs/skills/n-phase-cycle/strategize.md")
Read("docs/skills/n-phase-cycle/cross-synergize.md")
Read("docs/skills/n-phase-cycle/implement.md")
Read("docs/skills/n-phase-cycle/qa.md")
Read("docs/skills/n-phase-cycle/test.md")
Read("docs/skills/n-phase-cycle/educate.md")
Read("docs/skills/n-phase-cycle/measure.md")
Read("docs/skills/n-phase-cycle/reflect.md")

# Meta skills
Read("docs/skills/n-phase-cycle/auto-continuation.md")
Read("docs/skills/n-phase-cycle/phase-accountability.md")
Read("docs/skills/n-phase-cycle/branching-protocol.md")
```

**Extract**:
- Phase template structures (what goes in each phase section)
- Exit criteria patterns (what makes a phase complete)
- Continuation patterns (how phases link)

### 2. Search for Prior Art

```python
# Existing template/generation systems
Grep(pattern="template|Template|render|Render", path="impl/claude", type="py")

# YAML parsing infrastructure
Grep(pattern="yaml|YAML|from_yaml|to_yaml", path="impl/claude", type="py")

# Existing prompt generation
Grep(pattern="prompt|Prompt|generate.*prompt", path="impl/claude", type="py")

# Schema validation patterns
Grep(pattern="@dataclass|validate|Validation", path="impl/claude", type="py")
```

**Questions to answer**:
- Is there existing YAML parsing we can reuse?
- Is there existing template rendering we can reuse?
- Is there existing schema validation we can reuse?
- Are there existing N-Phase prompt generators?

### 3. Map AGENTESE Integration Points

```python
# Current AGENTESE contexts
Read("impl/claude/protocols/agentese/contexts/concept.py")
Read("impl/claude/protocols/agentese/contexts/self_.py")
Read("impl/claude/protocols/agentese/contexts/time_.py")
Read("impl/claude/protocols/agentese/contexts/void.py")

# Logos invocation patterns
Read("impl/claude/protocols/agentese/logos.py")
```

**Questions to answer**:
- Where should `concept.nphase.compile` be registered?
- How do other AGENTESE paths handle complex operations?
- What patterns should we follow for the new paths?

### 4. Analyze Existing ProjectDefinition-like Structures

```python
# Forest plan file headers
Grep(pattern="^---$", path="plans", glob="*.md", output_mode="files_with_matches")

# Phase ledger structures
Grep(pattern="phase_ledger:", path="plans", glob="*.md")

# Entropy tracking
Grep(pattern="entropy:", path="plans", glob="*.md")
```

**Questions to answer**:
- Do existing plan files already have structure we can formalize?
- Is there implicit schema in plan file headers?
- Can we extract ProjectDefinitions from existing plans?

### 5. Surface Blockers

For each potential blocker, find **evidence** (file:line):

| Potential Blocker | Investigation |
|-------------------|---------------|
| No YAML parsing in impl | Search for existing YAML usage |
| Template engine complexity | Check if Jinja2/similar exists |
| Schema validation overhead | Profile existing dataclass validation |
| AGENTESE path registration | Check how new paths are added |
| Phase template extraction | Can we programmatically extract from skill docs? |

---

## Deliverables

### 1. Research Notes

Create: `plans/meta/_research/nphase-prompt-compiler-research.md`

Include:
- **File Map**: Key classes/functions with line references
- **Prior Art Summary**: What exists, what can be reused
- **Invariants**: Laws that must be preserved (from N-Phase spec)
- **Blockers**: With evidence (file:line)
- **Opportunities**: Compression/reuse opportunities found

### 2. Questions for DEVELOP

Surface design questions:
- Should ProjectDefinition be YAML or Python dataclass first?
- Should phase templates be extracted from docs or hardcoded?
- Should the compiler produce markdown or structured AST?
- How should state updates be persisted?

### 3. Updated File Map

Capture locations for:
```
impl/claude/protocols/agentese/contexts/concept.py:???  — AGENTESE path registration
impl/claude/protocols/cli/handlers/???.py              — CLI handler pattern
docs/skills/n-phase-cycle/*.md                         — Phase templates source
plans/*.md                                             — Existing plan headers
```

---

## Exit Criteria

Before transitioning to DEVELOP, verify:

- [ ] All 11 phase skill docs read and patterns extracted
- [ ] Prior art search complete (YAML, templates, validation)
- [ ] AGENTESE integration points mapped
- [ ] Blockers surfaced with file:line evidence
- [ ] Research notes written to designated location
- [ ] Entropy spent: ≤0.05
- [ ] Did not modify any files (RESEARCH is read-only)

---

## Continuation Imperative

Upon completing RESEARCH, generate the prompt for DEVELOP:

```markdown
⟿[DEVELOP]
/hydrate

handles: research_notes=plans/meta/_research/nphase-prompt-compiler-research.md;
         file_map=[...]; blockers=[...]; prior_art=[...]
ledger: {PLAN: complete, RESEARCH: complete}
entropy: spent=0.07, remaining=0.68

mission: Design compression. Define ProjectDefinition schema, template engine,
         compiler architecture. Resolve blockers with design decisions.

exit: Schema defined; templates specified; laws testable; API contracts clear.
continuation: ⟿[STRATEGIZE]
```

---

## Principles Check

Before exiting RESEARCH:

- [ ] Did not modify any files (RESEARCH is read-only)
- [ ] Documented all blockers with file:line evidence
- [ ] Identified all prior art (no redundant implementation planned)
- [ ] Noted all contracts that must be preserved
- [ ] Entropy spent: ≤0.05

---

## Quick Reference

### Key Files to Read

| File | Purpose | Priority |
|------|---------|----------|
| `spec/protocols/n-phase-cycle.md` | N-Phase specification | HIGH |
| `docs/skills/n-phase-cycle/README.md` | Phase skill overview | HIGH |
| `docs/skills/n-phase-cycle/auto-continuation.md` | Continuation patterns | HIGH |
| `impl/claude/protocols/agentese/contexts/concept.py` | AGENTESE registration | MEDIUM |
| `prompts/kgent-chatbot-nphase.md` | Reference implementation | HIGH |

### Key Patterns to Find

| Pattern | What to Extract |
|---------|-----------------|
| Phase template structure | Section headers, content patterns |
| Exit criteria format | How phases define "done" |
| Continuation syntax | `⟿[PHASE]` generation |
| Schema validation | Dataclass patterns |
| YAML parsing | Existing infrastructure |

---

## The Vision

When complete, users will be able to:

```bash
# Define a project
cat > my-feature.yaml << EOF
name: "Add Authentication"
scope:
  goal: "JWT-based auth with refresh tokens"
components:
  - id: C1
    name: "Auth middleware"
    ...
EOF

# Compile to N-Phase prompt
kg nphase compile my-feature.yaml > prompts/auth-nphase.md

# Execute phases
claude --prompt prompts/auth-nphase.md --phase RESEARCH
```

**This is the leverage point.** One command to go from idea to structured execution.

---

*"The map is not the territory, but without the map we wander."*
