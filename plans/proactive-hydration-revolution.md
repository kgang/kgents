# Proactive Hydration Revolution

> *"The gotchas you don't read are the bugs you will write."*

**Status**: Active
**Created**: 2025-01-10
**Goal**: Transform kgents from reactive documentation to proactive context injection

---

## The Problem

kgents has excellent infrastructure that is **criminally underutilized**:

1. **`kg docs hydrate`** — Surfaces task-relevant gotchas, ancestral wisdom, voice anchors
2. **24 Skills** — Battle-tested guides for every task type
3. **Witness System** — Captures decisions and marks

**The Gap**: Claude doesn't use these automatically. They require human prompting.

```
Current State:
  User: "implement X"
  Claude: [starts coding without context]

Desired State:
  User: "implement X"
  Claude: [silently hydrates, surfaces gotchas, reads relevant skill, then codes]
```

---

## The Vision: Three-Layer Proactive Context

### Layer 1: Mandatory Hydration Protocol
Every implementation task triggers automatic hydration:
```
Task → kg docs hydrate → Surface 🚨 Critical → Proceed
```

### Layer 2: Skill Routing Table
Pattern-matched skill selection:
```
"add agent" → polynomial-agent.md
"AGENTESE node" → agentese-node-registration.md
```

### Layer 3: File-Level Gotchas
Every file edit surfaces relevant gotchas:
```
Edit services/brain/persistence.py → kg docs relevant → Warn about gotchas
```

---

## Implementation Plan

### Phase 1: CLAUDE.md Protocol Injection

Add mandatory protocols to CLAUDE.md:

```markdown
## Proactive Hydration Protocol (MANDATORY)

### On Task Start
Before ANY implementation task, Claude MUST:
1. Infer task description from user request
2. Run: `kg docs hydrate "<task>" --no-ghosts`
3. Parse output, surface 🚨 Critical gotchas at response start
4. Consult skill from routing table

### On File Edit
Before editing any file, Claude MUST:
1. Run: `kg docs relevant <path>`
2. Surface gotchas relevant to that file
3. Apply gotchas to proposed changes

### Skill Routing Table
| Task Pattern | Skill |
|--------------|-------|
| agent, state machine, polynomial | polynomial-agent.md |
| AGENTESE, @node, node registration | agentese-node-registration.md |
| persist, storage, dual-track | metaphysical-fullstack.md |
| test, testing, T-gent | test-patterns.md |
| UI, frontend, component, elastic | elastic-ui-patterns.md |
| event, bus, reactive | data-bus-integration.md |
| spec, specification | spec-template.md |
| witness, mark, decision | witness-for-agents.md |
```

### Phase 2: Skills Summary (Context-Friendly)

Create `docs/skills/QUICK-REFERENCE.md` — fits in context window:
- One-line summary per skill
- Key gotcha per skill
- Primary use case

### Phase 3: Enhanced /hydrate Skill

Update `.claude/commands/hydrate.md` to:
1. Actually invoke `kg docs hydrate` (not just suggest it)
2. Parse and surface output
3. Route to relevant skill

### Phase 4: Skill Integration Commands

Create new slash commands:
- `/skill <name>` — Read and apply a specific skill
- `/gotchas` — Surface all critical gotchas for current context

---

## Success Metrics

1. **Zero blind coding**: Every task starts with hydrated context
2. **Skill utilization**: Skills consulted in >80% of relevant tasks
3. **Gotcha prevention**: Critical gotchas surfaced before mistakes made
4. **Voice preservation**: Kent's voice anchors in every implementation response

---

## Anti-Goals

- NOT adding more documentation (we have enough)
- NOT requiring user to remember commands
- NOT optional protocols (MANDATORY means mandatory)

---

## The Radical Transformation

**Before**: Claude is a skilled but amnesiac coder
**After**: Claude is a skilled coder with institutional memory

The infrastructure exists. The knowledge is captured.
**We just need to wire the invocation.**

---

*"The proof IS the decision. The mark IS the witness."*
