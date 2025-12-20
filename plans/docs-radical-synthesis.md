# Documentation Radical Synthesis

> *"Don't enumerate the flowers. Describe the garden's grammar."*

---

## The Synthesis

Three sources converge:
1. **docs-radical-vision.md** — The philosophy (50-line README, AGENTESE structure, executable examples, ghost layer)
2. **docs-renaissance.md** — The audit (broken links, voice dilution, missing CONTRIBUTING.md ✅ now exists)
3. **2025-12-20-readme-public-presentation-audit.md** — The pragmatics (trust signals, Python version consistency, MkDocs nav)

**The Tension**: Radical vision says "50 lines, everything discovered." Pragmatic audit says "trust signals, clear onboarding, fix broken links."

**The Resolution**: Radical minimalism WITH trust infrastructure. The README is compressed, but links to substance. The garden has a path in—but exploring is the point.

---

## The Unified Vision

### What We're Creating

A documentation system that EMBODIES kgents principles:

| Principle | How Docs Embody It |
|-----------|-------------------|
| **Tasteful** | 50-line README says "no" to bloat |
| **Curated** | 5 contexts, not 50 pages |
| **Ethical** | Status badges are honest (experimental vs ship-ready) |
| **Joy-Inducing** | Examples run, ghosts show alternatives, discovery rewards |
| **Composable** | Docs structure mirrors code structure |
| **Heterarchical** | Multiple entry points (README, REPL, tour) |
| **Generative** | Docs generated from spec where possible |

### The Target Structure

```
kgents/
├── README.md              ← THE INVITATION (50 lines max)
├── CONTRIBUTING.md        ← Already exists, good
├── CHANGELOG.md           ← THE HISTORY
├── docs/
│   ├── README.md          ← THE MAP (entry point for docs/)
│   ├── world/             ← External-facing (visitors, evaluators)
│   │   └── quickstart.md  ← Zero to agent
│   ├── self/              ← Internal (developers in the codebase)
│   │   └── skills/        ← The 13 skills
│   ├── concept/           ← Abstract (theory, philosophy)
│   │   ├── principles.md  ← Symlink or redirect to spec/
│   │   └── categorical-foundations.md
│   ├── void/              ← Accursed share (experiments, ghosts, graveyard)
│   │   └── _archive/      ← What almost was
│   └── time/              ← Temporal (changelog archaeology)
│       └── archaeology.md ← How we got here
└── spec/                  ← THE LAW (unchanged)
```

---

## Execution Phases

### Phase 1: The 50-Line README (This Session)

Compress README.md to radical minimalism while maintaining trust signals.

**Target structure** (≤50 lines):

```markdown
# kgents

> *"The noun is a lie. There is only the rate of change."*

[One paragraph: philosophical stance]

## Feel It

[One code example: composition with >>]

## Install

[Three lines: clone, sync, verify]

## Explore

[Four links: Quickstart, Principles, Skills, Architecture]

## The Garden

[ASCII art or status table showing Crown Jewels]

---

MIT License | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)

*"The persona is a garden, not a museum."*
```

**What gets cut**:
- Seven Principles section (moved to principles.md link)
- Observation Is Interaction section (moved to quickstart)
- The Alphabet Garden table (too detailed for README)
- Project Structure (moved to docs/)
- Full Development section (in CONTRIBUTING.md already)
- Documentation section (in docs/README.md)
- Philosophy section (already in principles.md)

**What stays**:
- Opening quote and philosophical stance
- One compelling code example
- Install instructions
- Key exploration links
- Crown Jewels status (compressed)
- Trust signals (MIT, Contributing, Changelog)
- Closing aphorism

### Phase 2: AGENTESE Context Annotations (Session 2 — Complete)

**The Insight**: Full restructure was rejected as *gaudy, not tasteful*. The existing docs structure works. AGENTESE contexts are implementation ontology, not reader navigation. Users think "How do I do X?" not "Am I in world context?"

**What Was Done** (lighter touch approach):
1. ✅ Audited all links in docs/README.md — all valid
2. ✅ Added `context:` frontmatter to 8 key docs (quickstart, architecture, skills, etc.)
3. ✅ Created `docs/concept/` with symlink to `spec/principles.md`
4. ✅ Updated docs/README.md with AGENTESE context mapping section
5. ✅ Fixed link from `../spec/principles.md` to `concept/principles.md`

**What Was NOT Done** (deliberately):
- Did NOT move files into world/, self/, void/, time/ directories
- Did NOT disrupt working navigation
- Did NOT create empty placeholder directories

**The Learning**: *"Sometimes the best gardening is knowing when not to prune."*

### Phase 3: Pragmatic Fixes (Future Session)

From the audit:
- Normalize Python version references (3.12+ everywhere)
- Update MkDocs nav if using MkDocs
- Review research/ docs for staleness

**Note**: Broken links (functor-field-guide.md, operators-guide.md) were already moved to _archive/ in previous consolidation.

### Phase 4: Executable Examples (Complete)

Created `docs/examples/` with 5 standalone Python examples:
- `composition.py` - PolyAgent sequential composition, associativity
- `operad_laws.py` - AgentOperad law verification
- `voice_gate.py` - Anti-sausage protocol demonstration
- `trust_levels.py` - Witness trust escalation L0→L3
- `warp_traces.py` - TraceNode causality chains

All examples:
- Run standalone: `python docs/examples/<file>.py`
- Are <50 lines each
- Print meaningful, joy-inducing output
- Demonstrate unique kgents philosophy

### Phase 5: Ghost Layer (Future Session)

Add `<details>` blocks showing alternatives and ghosts

---

## Session Log

### Session 1 (2025-12-20) — The 50-Line README
- Compressed README from 258 → 50 lines
- Preserved voice anchors and opinionated stances
- Cut: Seven Principles section, Alphabet Garden, Philosophy (all linked)
- Kept: Opening quote, code example, install, Crown Jewels, trust signals

### Session 2 (2025-12-20) — AGENTESE Context Annotations
- Rejected full restructure as "gaudy, not tasteful"
- Added context frontmatter to 8 docs
- Created docs/concept/ with symlink to principles
- Updated docs/README.md with context mapping
- Learning: Don't restructure for elegance alone

### Session 3 (2025-12-20) — Pragmatic Fixes + Research Reality Check
- Fixed Python version: `local-development.md` 3.11+ → 3.12+
- Updated 4 research docs to reflect implementation reality:
  - `warp-behavior-audit.md`: Added ✅ IMPLEMENTED status, test coverage
  - `existing-leverage.md`: All phases COMPLETE, not future work
  - `rust-core-strategy.md`: Clarified Python WARP is done; Rust is future optimization
  - `servo-embedding-2025.md`: Servo is future; WARP primitives already built
- Learning: Research docs were treating active code as abstractions. Reality matters.

### Session 4 (2025-12-20) — Executable Examples

Created `docs/examples/` with 5 joy-inducing, standalone Python examples:

| Example | Philosophy Demonstrated |
|---------|------------------------|
| `composition.py` | "Agents compose via >>" - shows associativity |
| `operad_laws.py` | "Composition has laws" - runtime verification |
| `voice_gate.py` | "Quote, don't summarize" - anti-sausage protocol |
| `trust_levels.py` | "Earned, never granted" - trust escalation |
| `warp_traces.py` | "Traces encode causality" - WARP primitives |

Key decisions:
- Each example <50 lines (compression is quality)
- All examples print meaningful output (not just tests)
- Focus on unique kgents philosophy, not generic Python

Learning: Examples that demonstrate philosophy > examples that demonstrate syntax.

---

*Created: 2025-12-20 | Sessions: 4 complete*
*Grounded in: "Daring, bold, creative, opinionated but not gaudy"*
