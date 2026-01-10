Hydrate context from HYDRATE.md. Apply spec/principles.md rigorously.

## Session Initialization Protocol

This command initializes your session with full context. Execute ALL steps in order.

---

## STEP 1: Read Meta Files (MANDATORY)

Read these files IN ORDER:

```bash
# 1. Human intent (NEVER overwrite)
cat plans/_focus.md

# 2. Canopy view (auto-generated)
cat plans/_forest.md

# 3. Learnings (append only, 200-line cap)
cat plans/meta.md

# 4. Project state (keep terse)
cat HYDRATE.md
```

**Boundaries**:
| File | Agent May | Agent Must NOT |
|------|-----------|----------------|
| `_focus.md` | Read for direction | Overwrite (Kent's voice) |
| `_forest.md` | Regenerate from plan headers | Add prose |
| `meta.md` | Append atomic learnings | Add paragraphs (one line per insight) |
| `HYDRATE.md` | Update stale facts | Bloat (compress, don't expand) |

---

## STEP 2: Invoke Living Docs (MANDATORY when arguments provided)

If the user provides arguments describing a task:

```bash
# RUN THIS COMMAND - Unified hydration with observer-dependent defaults
kg docs hydrate "$ARGUMENTS"

# Options:
# --observer <kind>  Observer type: agent (default), human, ide
# --no-ghosts        Disable ancestral wisdom from deleted code
# --no-semantic      Disable Brain semantic enrichment
# --sync             Fast synchronous path (keyword only)
# --json             Output as JSON instead of markdown
```

**Observer Strategies**:
- `agent` (default): Maximum precision (semantic + ghosts enabled)
- `human`: Include surprises (ghosts yes, semantic no)
- `ide`: Speed-first (keyword only)

Parse the output and surface in this order:

1. **CRITICAL GOTCHAS** (show these FIRST, with full context)
2. **Warnings** (show next)
3. **Related files** (list files to explore)
4. **Voice anchors** (Kent's phrases to preserve)

If arguments reference a specific file path:

```bash
# RUN THIS COMMAND
kg docs relevant <file_path>
```

**Example output format**:

```
## Living Docs for: "implement wasm projector"

### CRITICAL GOTCHAS
- wasm-bindgen requires --target web flag for browser use
- Async functions in WASM need wasm-bindgen-futures

### Warnings
- Memory cleanup is manual - call .free() on dropped structs

### Related Files
- impl/claude/services/projectors/wasm.py
- spec/protocols/wasm-projection.md

### Voice Anchors to Preserve
- "Tasteful > feature-complete"
- "The Mirror Test: Does K-gent feel like me on my best day?"
```

---

## STEP 3: Route to Relevant Skills

Based on task keywords, identify the skill(s) to read:

### Task-to-Skill Routing Table

| Task Keywords | Recommended Skill |
|---------------|-------------------|
| agent, polynomial, state machine | `docs/skills/polynomial-agent.md` |
| @node, decorator, endpoint, DI, dependency | `docs/skills/agentese-node-registration.md` |
| path, context, world, self, concept, void | `docs/skills/agentese-path.md` |
| event, bus, reactive, DataBus, SynergyBus | `docs/skills/data-bus-integration.md` |
| UI, responsive, compact, spacious, elastic | `docs/skills/elastic-ui-patterns.md` |
| projection, CLI, TUI, JSON, marimo | `docs/skills/projection-target.md` |
| spec, specification, document | `docs/skills/spec-template.md` + `docs/skills/spec-hygiene.md` |
| test, testing, hypothesis, property | `docs/skills/validation.md` |
| hypergraph, graph, navigation, K-Block | `docs/skills/hypergraph-editor.md` |
| storage, persistence, D-gent, database | `docs/skills/metaphysical-fullstack.md` |
| witness, mark, decision, trace | `docs/skills/witness-for-agents.md` |
| analysis, audit, categorical | `docs/skills/analysis-operad.md` |
| fullstack, architecture, Crown Jewel | `docs/skills/metaphysical-fullstack.md` |
| streaming, SSE, flux | `docs/skills/agentese-node-registration.md` |

**Output format**:
```
Recommended skill: docs/skills/polynomial-agent.md
```

If multiple skills apply:
```
Recommended skills:
  1. docs/skills/agentese-node-registration.md (primary)
  2. docs/skills/agentese-path.md (supporting)
```

For complex workflows, consult `docs/skills/ROUTING.md`.

---

## STEP 4: Health Check

Run at session start:

```bash
kg probe health --all
```

If this fails, surface the failures before proceeding.

---

## STEP 5: Phase Detection

Based on session activity, detect and announce current phase:

| Activity Pattern | Phase |
|------------------|-------|
| Many file reads, no writes | **UNDERSTAND** |
| Code changes, tests running | **ACT** |
| Tests pass, writing notes | **REFLECT** |

---

## Witnessing: Marks & Decisions

> *"The proof IS the decision. The mark IS the witness."*

### During the Session

**Mark significant moments** with `km`:

```bash
km "what happened" --reasoning "why it matters" --tag <type>
```

| When | Tag | Example |
|------|-----|---------|
| Breakthrough understanding | `eureka` | `km "AGENTESE paths are places not actions" --tag eureka` |
| Discovered a trap | `gotcha` | `km "Property shadows method" --tag gotcha` |
| Aesthetic judgment | `taste` | `km "Animation feels alive now" --tag taste` |
| UX pain point | `friction` | `km "Had to restart 3 times" --tag friction` |
| Moment of delight | `joy` | `km "Tests all green on first try" --tag joy` |
| Somatic rejection | `veto` | `km "This feels wrong" --tag veto` |

**Record decisions** with `kg decide`:

```bash
# Quick decision
kg decide --fast "Use SSE not WebSocket" --reasoning "Unidirectional is enough"

# Full dialectic (when Kent and Claude differ)
kg decide --kent "LangChain" --kent-reasoning "Scale, resources" \
          --claude "Build kernel" --claude-reasoning "Joy, novel" \
          --synthesis "Build minimal, validate, then decide" \
          --why "Avoids both risks"
```

### When to Witness

- **After fixing something subtle** -> `km` with `--tag gotcha`
- **When choosing between options** -> `kg decide --fast`
- **When Kent + Claude synthesize** -> `kg decide` with full dialectic
- **When something feels right/wrong** -> `km` with `--tag taste` or `--tag veto`
- **Before ending a productive session** -> `/crystallize`

### Proactive Witnessing

As an agent, you should **proactively** emit marks and decisions:

1. After resolving a non-trivial bug: `km "Fixed X" --reasoning "Y" --tag gotcha`
2. After making an architectural choice: `kg decide --fast "choice" --reasoning "why"`
3. When Kent expresses aesthetic preference: `km "Kent prefers X" --tag taste`
4. When you reach synthesis together: use the full dialectic form

DO NOT wait to be asked. Witness as you go.

---

## Analysis Operad Integration

> *"Analysis is not one thing but four."*

When working on **specifications**, use the Analysis Operad:

```bash
# Before modifying a spec (full four-mode analysis)
kg analyze <spec>

# Quick structural check (no LLM, fast)
kg analyze <spec> --structural

# Specific modes
kg analyze <spec> --mode cat   # Verify composition laws
kg analyze <spec> --mode dia   # Find tensions in design
kg analyze <spec> --mode gen   # Check compression/regenerability
```

**When to Analyze**:
1. **Before modifying any spec** -> Run `kg analyze <spec>`
2. **When spec seems bloated** -> Run `kg analyze --mode gen`
3. **When design has tensions** -> Run `kg analyze --mode dia`
4. **After major changes** -> Re-run analysis to verify no regressions

**Four Modes**:
| Mode | Question | Use When |
|------|----------|----------|
| **categorical** | Do composition laws hold? | Architectural changes |
| **epistemic** | Is this properly grounded? | Justification questions |
| **dialectical** | What tensions exist? | Design trade-offs |
| **generative** | Can this regenerate impl? | Checking spec quality |

---

## The Molasses Test

Before adding to ANY meta file:
1. Is this one atomic insight or a compound? -> If compound, distill first
2. Will future-me understand without context? -> If no, rewrite
3. Can this be deleted in 30 days if unused? -> If no, it's not meta--it's spec

---

## End of Session

Before ending a productive session, run `/crystallize` to:
1. Review the session for significant moments
2. Emit any un-captured marks and decisions
3. Optionally update `meta.md` with atomic learnings
4. Verify with `kg witness show --today`

The goal: nothing valuable evaporates when the session ends.
