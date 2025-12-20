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

### Phase 5: Ghost Layer (Complete)

Added `<details>` blocks showing alternatives and "roads not taken" to three key docs.

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

### Session 5 (2025-12-20) — Ghost Layer

Added 8 ghosts across 3 documents using `<details>` blocks:

**architecture-overview.md** (3 ghosts):
| Ghost | What It Reveals |
|-------|-----------------|
| Why not microservices? | Composition breaks at network boundaries |
| The Original Functor Zoo | Before AD-001 unified everything |
| Agent[A,B] was almost enough | Why we needed PolyAgent |

**metaphysical-fullstack.md** (3 ghosts):
| Ghost | What It Reveals |
|-------|-----------------|
| Adapters in Infrastructure | Domain logic needs domain knowledge |
| The Express.js Pattern | Explicit routes create drift |
| The Frontend/Backend Split | Components live with services |

**quickstart.md** (2 ghosts):
| Ghost | What It Reveals |
|-------|-----------------|
| Why not start with K-gent? | Pedagogy requires foundations first |
| The Fifth Context | void.* holds everything we chose not to choose |

Key decisions:
- 🌫️ emoji for ethereal, not heavy
- Each ghost is short (discovery, not lecture)
- Voice anchors quoted where relevant
- Ghosts reveal taste, not just history

Learning: *"The persona is a garden, not a museum"* — ghosts show that the garden was cultivated, not found.

### Session 6 (2025-12-20) — Warmth Restoration + Developer Focus

Phase 5 compression went too far—50 lines was *minimal* rather than *warm*. Session 6 restored density and developer-focus:

**README.md** (50 → ~180 lines):
- Restructured "For Developers: Quick Start" with numbered steps
- Requirements table (Python, uv, Node, Claude CLI, Docker)
- Step-by-step: Clone → Backend/Frontend → LLM Setup → Postgres → Verify
- LLM Setup section explaining Morpheus gateway (Claude CLI vs API keys)
- "What Works Without LLM" table showing feature availability
- Added "What Makes This Different" section explaining vs. LangChain/AutoGPT/DSPy
- Added "The Vocabulary" table with 8 core terms and links
- Added "The Seven Principles" in terse one-line form
- Added "For AI Agents" section with anti-sausage protocol, voice anchors
- ASCII art progress bars for Crown Jewels status
- Removed half-baked CLI command examples — CLI under active development

**docs/README.md** (restructured):
- "The One Rule" section: Read skills first
- "Where to Start (By Goal)" table with time estimates
- "Common Pitfalls" section: Silent Skip, Frontend Type Drift, Import-Time Registration, Timer Zombie
- "For AI Agents" section with critical learnings
- "The Composition Formula" showing how skills compose

**docs/quickstart.md**:
- Expanded install section with test and mypy commands
- Added "Common Gotchas" section with 4 common failures
- Fixed GitHub URL (kgang → kentgang)
- Removed half-baked CLI command examples (soul, brain) — CLI under active development

Key decisions:
- Dense with information > sparse with elegance
- Developer concerns enumerated early
- AI agents get explicit sections
- Common failures documented before they happen
- Warmth through directness: *"Skip them and you'll reinvent wheels we already built"*

Learning: Compression serves discovery; density serves productivity. Both are needed.

---

*Created: 2025-12-20 | Sessions: 6 complete*
*Grounded in: "Daring, bold, creative, opinionated but not gaudy"*
