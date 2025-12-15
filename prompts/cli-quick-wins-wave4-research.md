# CLI Quick Wins Wave 4: RESEARCH Phase

> *"Map the landscape, surface constraints, and capture unknowns to de-risk later phases."*

---

## Context

**Plan**: `plans/devex/cli-quick-wins-wave4.md`
**Phase**: RESEARCH (First phase for this plan)
**Parent Work**: REPL Waves 1-3 (97 tests), Agent Town Phase 4 (437 tests), K-gent Phase 1 (88 tests)
**Source**: Synthesized from 15 creative exploration sessions

---

## Mission

Reconcile the proposed CLI commands against:
1. **Existing AGENTESE infrastructure** - What Logos paths/handlers already exist?
2. **CLI handler patterns** - What is the current architecture in `protocols/cli/handlers/`?
3. **Agent implementations** - Do H-gent, A-gent, P-gent, J-gent already support these operations?
4. **REPL integration** - How do new commands wire into the AGENTESE REPL?

---

## Handles (AGENTESE)

```
concept.forest.manifest[phase=RESEARCH][plan=cli-quick-wins-wave4]@span=cli_research
void.entropy.sip[amount=0.10]@span=exploration_budget
self.soul.manifest[observer=researcher][focus=reconciliation]
```

---

## Phase Ledger Update

```yaml
phase_ledger:
  PLAN: touched      # 2025-12-14 - Chief audit created plan
  RESEARCH: touching # This session
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.10
  sip_allowed: true
```

---

## Research Targets

### Priority 1: H-gent Infrastructure (CJ-12 to CJ-18)

| File/Pattern | What to Find |
|--------------|--------------|
| `impl/claude/agents/h/` | Does H-gent exist? Jung/Hegel/Lacan modules? |
| `rg "class.*Jung\|Hegel\|Lacan"` | Existing implementations |
| `rg "shadow\|dialectic\|synthesis"` impl/claude | Existing handlers |
| `spec/agents/h-gent.md` | H-gent specification |
| `protocols/agentese/contexts/concept.py` | How thinking agents integrate |

**Questions to Answer**:
- Is there already a `kg shadow` or `kg dialectic` command?
- What contracts do H-gent modules expose?
- How do H-gent operations fit into the Logos resolver?

### Priority 2: A-gent Creative Commands (CJ-24 to CJ-28)

| File/Pattern | What to Find |
|--------------|--------------|
| `impl/claude/agents/a/` | A-gent (creativity) implementation |
| `rg "oblique\|constrain\|yes.and"` | Existing creative handlers |
| `spec/agents/a-gent.md` | A-gent specification |
| Brian Eno Oblique Strategies | External: deck contents, licensing |

**Questions to Answer**:
- Does A-gent already have creativity methods?
- Are Oblique Strategies public domain or licensed?
- What's the pattern for "random prompt" generation?

### Priority 3: CLI Handler Architecture

| File/Pattern | What to Find |
|--------------|--------------|
| `protocols/cli/handlers/` | All existing handlers |
| `protocols/cli/handlers/soul.py` | K-gent soul pattern (reference) |
| `protocols/cli/hollow.py` | CLI routing |
| `protocols/cli/repl.py` | REPL integration |
| `rg "@handler"` | Handler decorator pattern |

**Questions to Answer**:
- What's the canonical pattern for a new CLI handler?
- How do handlers integrate with REPL navigation?
- Are there handler tests to follow as templates?

### Priority 4: Logos Path Resolution

| File/Pattern | What to Find |
|--------------|--------------|
| `protocols/agentese/logos.py` | Path resolution |
| `protocols/agentese/registry.py` | Registered paths |
| `rg "def invoke"` protocols/agentese | Invocation patterns |

**Questions to Answer**:
- How would `kg shadow` map to `concept.thinking.shadow.invoke`?
- What affordances does each path expose?
- How do new paths get registered?

### Priority 5: Cross-Pollination (CJ-37 to CJ-42)

| File/Pattern | What to Find |
|--------------|--------------|
| `agents/k/` | K-gent implementation |
| `rg "Judge\|approve\|verdict"` | Judge agent patterns |
| `agents/town/citizen.py` | Eigenvector personality (reference) |

**Questions to Answer**:
- How would "Would Kent Approve?" combine K-gent + Judge?
- What's the pattern for multi-agent composition in CLI?

---

## Actions

1. **Parallel file reads** (do these simultaneously):
   - `impl/claude/agents/h/` directory structure
   - `impl/claude/agents/a/` directory structure
   - `impl/claude/protocols/cli/handlers/soul.py` (template)
   - `impl/claude/protocols/agentese/logos.py` (routing)
   - `impl/claude/protocols/cli/repl.py` (REPL integration)

2. **Pattern searches**:
   - `rg "@handler" impl/claude/protocols/cli/` - Handler patterns
   - `rg "class.*Agent" impl/claude/agents/` - Agent class patterns
   - `rg "shadow\|dialectic\|jung\|hegel\|lacan" impl/claude/` - Existing H-gent work
   - `rg "oblique\|creative\|constrain" impl/claude/` - Existing A-gent work

3. **WebSearch** (external knowledge):
   - "Brian Eno Oblique Strategies deck contents license"
   - "CLI command handler patterns Python 2025"

4. **Prior art check**:
   - Review `plans/devex/agentese-repl-master-plan.md` for overlap
   - Check `plans/devex/agentese-repl-crown-jewel.md` Wave 4 plans
   - Review recent epilogues for relevant learnings

---

## Exit Criteria

- [ ] File map complete: All relevant modules identified with refs
- [ ] Blockers enumerated: Any missing dependencies (file:line)
- [ ] Prior art documented: What already exists that can be reused
- [ ] Unknowns listed: Questions requiring DEVELOP phase resolution
- [ ] No code changes: Research only
- [ ] Branch candidates: Any new tracks that should split off

---

## Deliverables

1. **File Map**: Table of all files relevant to CLI Quick Wins Wave 4
2. **Blockers**: List of missing dependencies with evidence
3. **Prior Art**: What handlers/agents already exist
4. **Unknowns**: Questions for DEVELOP phase
5. **Branch Candidates**: Any new plans that should spawn

---

## Branch Check (At Exit)

At RESEARCH exit, classify any branches:

| Type | Criteria |
|------|----------|
| **Blocking** | Must resolve before DEVELOP |
| **Parallel** | Can run alongside this plan |
| **Deferred** | Park for future cycle |
| **Void** | Donate to Accursed Share |

---

## Anti-Patterns to Avoid

- **Premature coding**: No implementation yet—mapping only
- **Shallow search**: Check specs, docs, skills, not just impl/
- **Undocumented blockers**: Write down everything with file:line
- **Missing prior art**: Don't duplicate existing work
- **Analysis paralysis**: Time-box to 1-2 hours max

---

## Next Phase Auto-Inducer

After completing RESEARCH, generate:

```markdown
⟿[DEVELOP]

This is the *DEVELOP* phase for **CLI Quick Wins Wave 4**.

/hydrate
handles: files=${files_mapped}; invariants=${contracts_found}; blockers=${blockers}; prior_art=${existing_handlers}; ledger={PLAN:touched, RESEARCH:touched}; entropy=${entropy_remaining}; branches=${branch_candidates}
mission: define contracts for new CLI commands; specify handler signatures; map Logos paths; assert composition laws.
actions: Write handler contracts; define input/output types; specify error handling; note REPL integration points.
exit: Handler contracts + Logos paths + test skeletons; ledger.DEVELOP=touched; continuation → STRATEGIZE.

Exit Criteria:
- [ ] Handler signatures defined for all Priority 1-3 commands
- [ ] Logos paths specified for each command
- [ ] Error handling patterns documented
- [ ] Test skeleton structure planned
- [ ] REPL integration points identified
```

---

*"Map the landscape before building the road."*
