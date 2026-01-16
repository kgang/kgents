# Documentation Map

> *"Read the skills first. Skip them and you'll reinvent wheels we already built."*

This map provides a comprehensive overview of kgents documentation structure, helping developers and AI agents navigate effectively.

---

## Entry Points

| Document | Audience | Purpose |
|----------|----------|---------|
| [README.md](../README.md) | Everyone | Project overview, quick start |
| [CLAUDE.md](../CLAUDE.md) | AI Agents | Session context, voice anchors, anti-sausage protocol |
| [NOW.md](../NOW.md) | All developers | Living document - current state, what's happening |
| [docs/README.md](README.md) | Human developers | Documentation hub with task routing |
| [docs/quickstart.md](quickstart.md) | New developers | Zero to running in 5 minutes |

---

## Core Documentation

### Skills (AUTHORITATIVE - Read First)

**Location**: `docs/skills/` (34 files, 31 skills + 3 index files)

The 30+ practical skills are the most important documentation. Every task has a corresponding skill.

| Category | Skills |
|----------|--------|
| **Universal (Start Here)** | cli-strategy-tools.md, metaphysical-fullstack.md, elastic-ui-patterns.md |
| **Foundation** | polynomial-agent.md |
| **Protocol (AGENTESE)** | agentese-path.md, agentese-node-registration.md |
| **Architecture** | data-bus-integration.md, hypergraph-editor.md |
| **Witness** | witness-for-agents.md, derivation-edges.md |
| **Process** | research-protocol.md, plan-file.md, spec-template.md, spec-hygiene.md, witnessed-regeneration.md |
| **Projection** | projection-target.md, marimo-projection.md, tui-patterns.md |
| **Specialized** | analysis-operad.md, cli-handler-patterns.md, aspect-form-projection.md, zero-seed-for-agents.md, storybook-for-agents.md, mypy-best-practices.md, validation.md, proof-verifier-bridge.md |

**Index Files**: README.md, ROUTING.md, QUICK-REFERENCE.md

### Theory (20 Chapters)

**Location**: `docs/theory/`

Mathematical and categorical foundations:

| Chapter | Topic |
|---------|-------|
| 00 | Overture |
| 01 | Preliminaries |
| 02 | Agent Category |
| 03-05 | Monadic, Operadic, Sheaf Reasoning |
| 06-07 | Galois Modularization, Galois Loss |
| 08 | Polynomial Bootstrap |
| 09-11 | Agent-DP, Value Agent, Meta-DP |
| 12-14 | Multi-Agent, Heterarchy, Binding |
| 15-17 | Analysis Operad, Witness, Dialectic |
| 18-19 | Framework Comparison, kgents |
| 20 | Open Problems |
| 99 | Bibliography |

---

## Reference Documentation

### Systems Reference

**File**: [docs/systems-reference.md](systems-reference.md)

Inventory of all 50+ production systems. CHECK HERE FIRST before building anything new.

Covers: Data Bus, Differance Engine, Witness, Soul, Memory, Town, Constitutional, and more.

### Architecture

| Document | Purpose |
|----------|---------|
| [docs/architecture-overview.md](architecture-overview.md) | Three pillars, functor system |
| [docs/categorical-foundations.md](categorical-foundations.md) | Category theory introduction |
| [docs/cli-reference.md](cli-reference.md) | CLI command reference |
| [docs/local-development.md](local-development.md) | Development environment setup |

### Reference Subdirectories

**Location**: `docs/reference/`

| Subdirectory | Purpose |
|--------------|---------|
| agentese-protocol/ | AGENTESE protocol specification |
| ashc-compiler/ | ASHC compiler documentation |
| categorical-foundation/ | Categorical foundation details |
| teaching/gotchas.md | Common pitfalls and fixes |

---

## Specifications

**Location**: `spec/`

Formal specifications (conceptual, implementation-agnostic):

| Area | Path |
|------|------|
| **Agents** | spec/agents/ (d-gent, f-gent, k-gent, m-gent, operad, etc.) |
| **Protocols** | spec/protocols/ (witness, chat, zero-seed, storage-migration, etc.) |
| **Theory** | spec/theory/ (analysis-operad, dp-native-kgents, etc.) |
| **Principles** | spec/principles/ (CONSTITUTION.md) |
| **Services** | spec/services/ |

---

## Service Documentation

**Location**: `impl/claude/services/*/README.md`

Each Crown Jewel service has its own README:

| Service | Status | README Quality |
|---------|--------|----------------|
| analysis | Active | Comprehensive |
| annotate | Active | Comprehensive |
| code | Active | Comprehensive |
| constitutional | Active | Comprehensive |
| derivation | Active | Comprehensive |
| director | Active | Comprehensive |
| feed | Active | Comprehensive |
| portal | Active | Comprehensive |
| probe | Active | Comprehensive |
| verification | Active | Comprehensive |

---

## Archives

### Active Archive Directories

| Location | Purpose |
|----------|---------|
| `docs/_archive/` | Archived docs, brainstorming, theory chapters |
| `plans/_archive/` | Completed/superseded plans |
| `spec/protocols/_archive/` | Superseded protocol specs |
| `spec/f-gents/_archive/` | Archived f-gent specs |
| `impl/claude/_archive/` | Archived implementation code |
| `brainstorming/_archive/` | Historical brainstorming |
| `_archive/` (root) | Project-level archives |

### Archive Contents

**`docs/_archive/`**:
- `brainstorming/` - Historical brainstorming sessions
- `research/` - Research notes (warp-behavior-audit, servo-embedding, etc.)
- Archived theory chapters (02, 06, 07, 08, 09)

**`plans/_archive/`**:
- `_forest-archived-2025-12-21.md` - Archived forest protocol
- `witness-self-correction-archived-2025-12-22.md`
- `impl-claude-plans-2025-12-25/` - Completed implementation plans

---

## Creative and Gallery

| Location | Purpose |
|----------|---------|
| `docs/creative/` | Creative direction, moodboards |
| `docs/gallery/` | Visual examples, showcases |
| `docs/examples/` | Code examples |

---

## Documentation by Audience

### For Human Developers

1. Start: `docs/quickstart.md`
2. Skills: `docs/skills/README.md`
3. Systems: `docs/systems-reference.md`
4. CLI: `docs/cli-reference.md`

### For AI Agents

1. Context: `CLAUDE.md`
2. Skills: `docs/skills/` (especially `witness-for-agents.md`, `zero-seed-for-agents.md`)
3. Systems: `docs/systems-reference.md`
4. Gotchas: `docs/reference/teaching/gotchas.md`

### For Researchers

1. Theory: `docs/theory/` (all 20 chapters)
2. Foundations: `docs/categorical-foundations.md`
3. Specs: `spec/theory/`

---

## Documentation Health Notes

**Status: All issues resolved** (2026-01-16)

### Resolved Issues

1. **Missing Skills** - All 4 missing skills have been created:
   - `test-patterns.md` - T-gent Types I-V, DI over mocking, property-based testing
   - `building-agent.md` - Agent composition, `>>` operator, factory patterns
   - `crown-jewel-patterns.md` - 14 battle-tested patterns for services
   - `unified-storage.md` - D-gent Universe and DataBus integration

2. **Misplaced Skill** - `nphase-integration.md` moved from `impl/claude/docs/skills/` to `docs/skills/`

3. **Stale References** - `services/park/` reference in `metaphysical-fullstack.md` updated to `services/witness/`

### Authoritative Locations

- **Skills**: `docs/skills/` is the ONLY authoritative location (34 files)

### README Files Statistics

- **Total in project**: 103 (excluding dependencies)
- **In node_modules**: 1,196 (can be ignored)
- **In .venv/.lake**: ~20+ (can be ignored)

Most project READMEs are well-maintained service documentation.

### Theory Files Note

Files `docs/theory/12-multi-agent.md` and `docs/theory/13-heterarchy.md` use generic terms like "emergence" and "coalition" in theoretical context (not references to deleted systems).

---

## Quick Navigation

### By Task

| Task | Go To |
|------|-------|
| Build a feature | `docs/skills/` |
| Add AGENTESE path | `docs/skills/agentese-node-registration.md` |
| Debug DI errors | `docs/skills/agentese-node-registration.md` (Enlightened Resolution) |
| Check what exists | `docs/systems-reference.md` |
| Write tests | `docs/skills/test-patterns.md` |
| Plan work | `docs/skills/plan-file.md` |
| Write specs | `docs/skills/spec-template.md` |

### By Error

| Error | Go To |
|-------|-------|
| `DependencyNotFoundError` | `docs/skills/agentese-node-registration.md` |
| `@node declares X but __init__ has no X` | `docs/skills/agentese-node-registration.md` |
| TypeScript errors | `docs/skills/elastic-ui-patterns.md` |

---

*Updated: 2026-01-16*
*Status: Post-Extinction Edition (Gestalt, Park, Emergence, Coalition, Drills archived)*
