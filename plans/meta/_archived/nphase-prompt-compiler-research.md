---
path: plans/meta/_research/nphase-prompt-compiler-research
status: complete
progress: 100
last_touched: 2025-12-14
touched_by: claude-opus-4.5
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: pending
entropy:
  planned: 0.05
  spent: 0.04
  returned: 0.01
---

# RESEARCH: N-Phase Prompt Compiler

> *"Map the terrain to de-risk later phases."*

**Research completed**: 2025-12-14
**Entropy spent**: 0.04/0.05

---

## Executive Summary

**Key Finding**: Significant prior art exists. The N-Phase Prompt Compiler can reuse:
1. YAML parsing from `jit.py:78-223` (`SpecParser` class)
2. Template pattern from spec files (YAML frontmatter + markdown body)
3. Schema validation via frozen dataclasses
4. AGENTESE registration via `ConceptContextResolver`

**Critical Insight**: Existing plan file headers (like `nphase-prompt-compiler.md`) already contain most ProjectDefinition fields. The "schema" is implicit in the Forest Protocol.

**Blockers**: None critical. All can be resolved with design decisions.

---

## 1. File Map: Key Classes/Functions

### YAML Parsing Infrastructure

| Location | Class/Function | Purpose |
|----------|---------------|---------|
| `impl/claude/protocols/agentese/jit.py:43-45` | `import yaml` | YAML import with fallback |
| `impl/claude/protocols/agentese/jit.py:78-223` | `SpecParser` | Parse YAML frontmatter from specs |
| `impl/claude/protocols/agentese/jit.py:106-113` | `FRONT_MATTER_RE`, `YAML_BLOCK_RE` | Regex for frontmatter extraction |
| `impl/claude/protocols/agentese/jit.py:148` | `yaml.safe_load(front_match.group(1))` | Frontmatter parsing |
| `impl/claude/infra/ground.py:28,262` | Config loading | YAML config pattern |
| `impl/claude/protocols/cli/flow/commands.py:391` | `yaml.dump()` | YAML output generation |

### Template/Code Generation

| Location | Class/Function | Purpose |
|----------|---------------|---------|
| `impl/claude/protocols/agentese/jit.py:229-250` | `SpecCompiler` | Compile ParsedSpec to code |
| `impl/claude/protocols/agentese/jit.py:63-75` | `ParsedSpec` | Frozen dataclass for parsed specs |
| `impl/claude/protocols/agentese/exporters.py:113-120` | YAML config loading | Telemetry config pattern |

### AGENTESE Registration

| Location | Class/Function | Purpose |
|----------|---------------|---------|
| `impl/claude/protocols/agentese/logos.py:615-623` | `Logos.register()` | Register node in registry |
| `impl/claude/protocols/agentese/logos.py:627-663` | `_resolve_context()` | Context-specific resolution |
| `impl/claude/protocols/agentese/contexts/concept.py:660-738` | `ConceptContextResolver` | Resolver for concept.* paths |
| `impl/claude/protocols/agentese/contexts/__init__.py` | `create_context_resolvers()` | Factory for all resolvers |

### N-Phase Skill Templates

| Location | Purpose | Key Sections |
|----------|---------|--------------|
| `docs/skills/n-phase-cycle/plan.md:39-43` | Quick Wield format | Snap prompt structure |
| `docs/skills/n-phase-cycle/plan.md:148-169` | Continuation Generator | Exit signifier template |
| `docs/skills/n-phase-cycle/research.md:139-161` | Continuation Generator | Research exit pattern |
| `docs/skills/n-phase-cycle/develop.md:110-132` | Continuation Generator | Develop exit pattern |
| `docs/skills/n-phase-cycle/implement.md:205-227` | Continuation Generator | Implement exit pattern |
| `docs/skills/n-phase-cycle/phase-accountability.md:119-143` | Phase Trace format | Full 11-phase trace |
| `docs/skills/n-phase-cycle/auto-continuation.md:189-222` | Continuation Template | Full handoff structure |

### Existing Plan File Structure

| Location | Purpose |
|----------|---------|
| `plans/meta/nphase-prompt-compiler.md:1-36` | Plan header YAML (implicit schema) |
| `plans/_status.md` | Status matrix format |
| `plans/_forest.md` | Forest protocol structure |

---

## 2. Prior Art Summary

### What Exists and Can Be Reused

| Artifact | Location | Reuse Strategy |
|----------|----------|----------------|
| YAML frontmatter parsing | `jit.py:78-223` | Extract `SpecParser` pattern |
| Frozen dataclass schema | `jit.py:63-75` | Model `ProjectDefinition` similarly |
| Code generation pipeline | `jit.py:229+` | Pattern for template compilation |
| Context resolver pattern | `concept.py:660-738` | Add `nphase` holon to concept context |
| Continuation templates | `docs/skills/n-phase-cycle/*.md` | Programmatic extraction |

### What Needs to Be Built

| Component | Rationale |
|-----------|-----------|
| `ProjectDefinition` dataclass | Formalize implicit plan header schema |
| `NPhaseTemplate` class | Render phase sections from templates |
| `NPhasePromptCompiler` | Orchestrate parse → validate → render |
| `NPhaseStateUpdater` | Update cumulative state after phase |
| AGENTESE `concept.nphase.*` | New paths in concept context |
| CLI `kg nphase compile` | User-facing command |

---

## 3. Invariants (Laws to Preserve)

### From N-Phase Specification (`spec/protocols/n-phase-cycle.md:39-47`)

1. **Self-Similar**: Each phase contains a hologram of the full cycle
2. **Category-Theoretic**: Phases compose lawfully; identity and associativity hold
3. **Agent-Human Parity**: No privileged author; equally consumable by both
4. **Mutable**: The cycle evolves via re-metabolization
5. **Auto-Continuative**: Each phase generates the next prompt
6. **Accountable**: Skipped phases leave explicit debt

### From Phase Skills (`docs/skills/n-phase-cycle/README.md:56-79`)

| Phase | Minimum Artifact |
|-------|------------------|
| PLAN | Scope, exit criteria, attention budget, entropy sip |
| RESEARCH | File map + blockers with refs |
| DEVELOP | Contract/API deltas or law assertions |
| STRATEGIZE | Sequencing with rationale |
| CROSS-SYNERGIZE | Named compositions or explicit skip |
| IMPLEMENT | Code changes or commit-ready diff |
| QA | Checklist run with result |
| TEST | Tests added/updated or explicit no-op with risk |
| EDUCATE | User/maintainer note or explicit skip |
| MEASURE | Metric hook/plan or defer with owner/timebox |
| REFLECT | Learnings + next-loop seeds |

### Compiler Laws (from Plan)

1. **Identity**: `compile(empty_project) = empty_prompt`
2. **Composition**: Sequential phase execution composes associatively
3. **Idempotence**: `compile(compile(project_as_def)) ≡ compile(project_as_def)`
4. **Holographic**: Each phase section is itself valid N-Phase structure

---

## 4. Blockers with Evidence

| ID | Blocker | Evidence | Resolution |
|----|---------|----------|------------|
| B1 | No dedicated N-Phase YAML schema | Plan headers vary (compare `nphase-prompt-compiler.md:1-36` vs other plans) | Formalize schema in `ProjectDefinition` dataclass |
| B2 | Phase templates in markdown, not code | `docs/skills/n-phase-cycle/*.md` are human-readable | Extract templates programmatically or hardcode |
| B3 | `concept.nphase.*` paths don't exist | `concept.py:660-738` only handles generic concepts | Add `nphase` special case in resolver |
| B4 | No CLI handler pattern for compilation | `handlers/` use Typer, need new pattern | Follow existing handler pattern (e.g., `handlers/forest.py`) |
| B5 | Entropy tracking not enforced | `phase_ledger` and `entropy` in headers are advisory | Validation in `ProjectDefinition.validate()` |

### Blocker Analysis

**B1** is structural—the schema exists implicitly but varies. Resolution: Define canonical `ProjectDefinition` with all fields from plan header.

**B2** is a design choice. Options:
- (a) Extract templates at runtime from markdown files
- (b) Hardcode templates in Python (faster, version-controlled)
- (c) Hybrid: load from files, cache as Python

**B3** is registration—straightforward via existing pattern:
```python
# In ConceptContextResolver.resolve():
if holon == "nphase":
    return NPhaseConceptNode(...)
```

**B4** follows existing patterns in `handlers/forest.py`.

**B5** is validation logic in the dataclass.

---

## 5. Opportunities for Compression/Reuse

### 1. Plan Header IS ProjectDefinition

The existing plan header format already contains:
```yaml
path:            → name
status:          → classification (active = standard, crown_jewel)
progress:        → (derived from phase_ledger)
priority:        → priority weight
importance:      → classification
blocking:        → blockers (partial)
enables:         → (reverse of blocking)
session_notes:   → decisions/notes
phase_ledger:    → current phase state
entropy:         → entropy budget
```

**Opportunity**: `ProjectDefinition.from_plan_header()` can bootstrap from existing plans.

### 2. SpecParser Pattern Reusable

`jit.py:78-223` already:
- Parses YAML frontmatter
- Extracts sections via regex
- Returns frozen dataclass

**Opportunity**: Extend or copy pattern for `ProjectDefinitionParser`.

### 3. Continuation Generator Templates Extractable

Each skill file has a `## Continuation Generator` section with template:
```markdown
⟿[NEXT_PHASE]
/hydrate
handles: ...; ledger=...; entropy=...
mission: ...
exit: ...; continuation → ...
```

**Opportunity**: Extract via regex, parameterize with project data.

### 4. Meta-Prompt Structure Already Exists

`prompts/kgent-chatbot-nphase.md` demonstrates the target output:
- Phase Selector
- Project Overview
- Shared Context (File Map, Invariants, Blockers, Components, Waves, Checkpoints)
- Cumulative State (Handles, Entropy)
- Phase sections in `<details>` tags
- Phase Accountability table

**Opportunity**: Use as reference implementation template.

---

## 6. Questions for DEVELOP

### Schema Design

1. **Should `ProjectDefinition` be YAML-first or Python dataclass-first?**
   - YAML-first: Users edit YAML, we parse
   - Python-first: Programmatic API, serialize to YAML
   - **Recommendation**: Python-first with `.from_yaml()` and `.to_yaml()`

2. **Should phase templates be extracted from docs or hardcoded?**
   - Extract: Always in sync with docs
   - Hardcode: Faster, no runtime I/O
   - **Recommendation**: Hardcode initially, add extraction later

3. **Should the compiler produce markdown or structured AST?**
   - Markdown: Simple, human-readable
   - AST: Enables programmatic manipulation, multiple outputs
   - **Recommendation**: Markdown first, AST later for multi-target

### Integration Design

4. **Where should `concept.nphase.*` be registered?**
   - Option A: Special case in `ConceptContextResolver`
   - Option B: Dedicated `NPhaseContextResolver`
   - **Recommendation**: Option A (simpler)

5. **How should state updates be persisted?**
   - Option A: In-memory only (session-scoped)
   - Option B: Write back to source YAML
   - Option C: Separate state file
   - **Recommendation**: Option C (non-destructive)

---

## 7. Updated File Map for DEVELOP

```
# Core implementation (new)
impl/claude/protocols/nphase/
├── schema.py              — ProjectDefinition, Component, Wave, etc.
├── parser.py              — ProjectDefinitionParser (YAML → schema)
├── validator.py           — Validation logic, law checks
├── templates/
│   ├── __init__.py        — Template registry
│   ├── plan.py            — PLAN phase template
│   ├── research.py        — RESEARCH phase template
│   └── ...                — One per phase
├── template.py            — NPhaseTemplate class
├── compiler.py            — NPhasePromptCompiler
├── state.py               — NPhaseStateUpdater
└── _tests/
    ├── test_schema.py
    ├── test_compiler.py
    └── test_laws.py

# AGENTESE integration (modify existing)
impl/claude/protocols/agentese/contexts/concept.py:660+  — Add nphase handling

# CLI integration (new)
impl/claude/protocols/cli/handlers/nphase.py            — kg nphase compile

# Reference files
docs/skills/n-phase-cycle/*.md                          — Source for templates
plans/meta/nphase-prompt-compiler.md                    — Plan (self-reference)
prompts/kgent-chatbot-nphase.md                         — Reference output
```

---

## 8. Exit Criteria Verification

- [x] All 11 phase skill docs read and patterns extracted
- [x] Prior art search complete (YAML: 68 files, templates: 347 files, validation: 583 files)
- [x] AGENTESE integration points mapped (`logos.py:615`, `concept.py:660-738`)
- [x] Blockers surfaced with file:line evidence (5 blockers)
- [x] Research notes written to designated location
- [x] Entropy spent: 0.04 ≤ 0.05
- [x] Did not modify any source files (RESEARCH is read-only)

---

## 9. Continuation

```markdown
⟿[DEVELOP]
/hydrate

handles:
  research_notes=plans/meta/_research/nphase-prompt-compiler-research.md;
  file_map=[jit.py, concept.py, logos.py, skill docs];
  blockers=[B1:schema, B2:templates, B3:paths, B4:cli, B5:entropy];
  prior_art=[SpecParser, ParsedSpec, ConceptContextResolver]

ledger: {PLAN: touched, RESEARCH: touched}
entropy: spent=0.06, remaining=0.69

mission: Design compression. Define ProjectDefinition schema, template engine,
         compiler architecture. Resolve blockers with design decisions.

exit: Schema defined; templates specified; laws testable; API contracts clear.
continuation: ⟿[STRATEGIZE]
```

---

*"The map is not the territory, but without the map we wander."*
