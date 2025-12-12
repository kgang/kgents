# Plan Principles: The Forest Protocol

> *"A single mighty oak casts too much shadow. We cultivate a forest where many trees grow."*

These principles govern how plans are structured, communicated, and coordinated across human-AI collaboration. They derive from `spec/principles.md` but are contextualized for the multiplayer, multi-session nature of AI-assisted development.

---

## 1. Forest Over King

> Every session should tend multiple trees, not serve one monarch.

**The Problem**: A monolithic "NEXT_SESSION_PROMPT" creates a king project that dominates attention. Other projects wither in its shadow. AI agents become court servants to the loudest plan.

**The Principle**:
- No single plan should consume an entire session's focus
- Every session should acknowledge multiple active trees
- Plans are peers, not hierarchy (heterarchical, per `spec/principles.md`)

### The Forest Canopy View

```
┌─────────────────────────────────────────────────────────────────────┐
│                        THE FOREST CANOPY                             │
│                                                                      │
│   ████     ░░░░░░     ▓▓▓▓     ░░░      ▒▒▒▒▒▒                      │
│   ████      ░░░░░░     ▓▓       ░░░       ▒▒▒▒▒▒                     │
│  I-gent    entropy   creativity  lattice   stream                    │
│   (70%)     (0%)       (80%)     (0%)      (70%)                     │
│                                                                      │
│   Active trees should be visible. Dormant trees should not be       │
│   invisible—they should be marked as dormant, awaiting their        │
│   season.                                                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Anti-patterns
- A NEXT_SESSION_PROMPT that only mentions one project
- Completing one plan before starting any other
- "We'll get to that later" (deferred indefinitely)
- Treating low-priority as no-priority

---

## 2. Stigmergic Coordination

> Agents coordinate through the environment, not through centralized command.

**The Problem**: Each AI session starts fresh. There's no memory of what previous sessions worked on, what failed, what insights emerged. Coordination happens only through static files that require explicit reading.

**The Principle**:
- Plans should leave traces that subsequent agents can sense
- Progress markers are not just for humans—they're for AI continuity
- The plan directory IS the shared memory

### The Pheromone Trail

Every plan file includes a machine-readable header:

```yaml
---
path: self/interface
status: active          # dormant | blocked | active | complete
progress: 70            # 0-100 percentage
last_touched: 2025-12-11
touched_by: claude-opus-4.5
blocking: []            # What this plan is waiting on
enables: [self/memory]  # What plans are waiting on this
session_notes: |
  Phase 1 in progress. DensityField widget prototyped.
  Blocked on: nothing
  Insight: Textual reactive model cleaner than expected.
---
```

**Reading the Forest**: An AI starting a session reads `plans/_forest.md` which aggregates all plan headers into a single canopy view.

### Anti-patterns
- Session notes that only humans can parse
- Progress markers without context
- Isolated plans with no declared dependencies

---

## 3. Attention Budgeting

> Allocate attention across the forest, not just to the tallest tree.

**The Problem**: High-progress projects (80%) attract more attention than low-progress projects (0%). This creates a rich-get-richer dynamic where some trees never receive sunlight.

**The Principle**:
- Every session should allocate attention tokens across multiple plans
- Dormant plans deserve periodic check-ins
- "Quick wins" on neglected plans compound over sessions

### The Attention Allocation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SESSION ATTENTION BUDGET                          │
│                                                                      │
│   Primary Focus (60%):  self/interface (I-gent v2.5)                │
│   Secondary (25%):      concept/creativity (Phase 8 polish)         │
│   Maintenance (10%):    void/entropy (read spec, draft approach)    │
│   Accursed Share (5%):  concept/lattice (explore, no commitment)    │
│                                                                      │
│   The 5% Accursed Share is MANDATORY. It ensures every tree         │
│   eventually receives light.                                         │
└─────────────────────────────────────────────────────────────────────┘
```

### The Rotation Protocol

Dormant plans (0% progress) should enter the Accursed Share rotation. Each session picks one dormant plan for exploratory attention—no commitment to complete, just to understand and maybe leave breadcrumbs for the next session.

### Anti-patterns
- 100% attention on one plan
- "I'll look at that when the main project is done"
- Only touching plans that are already in motion

---

## 4. Blockers Are First-Class

> A blocked plan is not a failed plan—it's a plan with declared dependencies.

**The Problem**: Plans can be blocked by external factors (dependencies, unclear specs, missing context), but there's no way to express this. Blocked plans appear identical to abandoned plans.

**The Principle**:
- Every plan explicitly declares its blockers
- Blockers can be other plans, external events, or decisions needed
- Blocked plans are not invisible—they're in a named state

### Blocker Types

| Type | Example | Resolution |
|------|---------|------------|
| **Plan Dependency** | `self/memory` blocked on `self/stream` | Complete dependency |
| **Decision Needed** | `concept/lattice` needs architectural choice | User input required |
| **External** | `world/k8s` blocked on cluster access | Environment change |
| **Context** | `void/entropy` needs more research | Accursed Share attention |

### The Blocking Graph

```
self/stream (70%) ──enables──▶ self/memory (30%)
                              ▲
                              │ blocked_by
concept/creativity (80%) ─────┘

void/entropy (0%) ◀── context_needed ── [research required]
```

### Anti-patterns
- Blocked plans with no declared blocker
- Assuming blocked = abandoned
- Plans that implicitly depend on others without declaration

---

## 5. Session Continuity

> Each session is a chapter, not a standalone story.

**The Problem**: AI sessions are memoryless. A new session must reconstruct context from files, which is expensive and lossy. There's no narrative thread connecting sessions.

**The Principle**:
- Sessions should read the previous session's epilogue
- Sessions should write an epilogue for the next session
- The narrative arc across sessions should be visible

### The Epilogue Protocol

At the end of each session, write to `plans/_epilogues/<date>-<session>.md`:

```markdown
# Session Epilogue: 2025-12-11-a

## What We Did
- I-gent: Created DensityField widget, flux.py scaffold
- creativity: Reviewed Phase 8, no changes

## What We Learned
- Textual reactive model maps well to density field concept
- Phase 8 (pataphysics) needs clearer postcondition spec

## What's Next
- I-gent: Wire up h/j/k/l navigation
- creativity: Draft postcondition examples for @meltable

## Unresolved Questions
- Should DensityField animate at 30fps always or only when focused?
- Is `ensure` parameter sufficient for pataphysics contracts?

## For the Next Session
Read: plans/self/interface.md (updated), plans/_forest.md
Focus suggestion: I-gent (continue) + creativity (polish)
```

### Anti-patterns
- Sessions that end without writing state
- Next sessions that don't read previous epilogues
- Losing insights because they weren't written down

---

## 6. Parallel Paths

> Multiple trees can grow in a single session.

**The Problem**: Sequential focus (finish A, then start B) underutilizes session capacity. AI agents can context-switch, but only if plans are designed for interleaving.

**The Principle**:
- Plans should be chunked into parallelizable units
- A session can work on multiple plans if they're at natural breakpoints
- Switching between plans is not failure—it's forest cultivation

### Plan Chunking

Each plan should decompose into chunks that represent natural stopping points:

```markdown
## Chunks

### Chunk 1: Widget Scaffold (2 hours)
- Create density_field.py with basic render
- Create flux.py with navigation stubs
- **Exit criteria**: `python -m agents.i.app` launches without error

### Chunk 2: Navigation (1 hour)
- Implement h/j/k/l movement
- Add focus spotlight effect
- **Exit criteria**: Can navigate between 5 mock agents

### Chunk 3: Live Data (2 hours)
- Connect to agent registry
- Add O-gent polling
- **Exit criteria**: Real agents appear with updating activity
```

A session can complete Chunk 1 of Plan A, then Chunk 1 of Plan B, then return to Chunk 2 of Plan A. This is forest cultivation, not task switching.

### Anti-patterns
- Monolithic plans with no breakpoints
- "Can't stop until this phase is done"
- Treating context switches as overhead

---

## 7. The Accursed Share of Planning

> Not all attention must be productive. Exploration is sacred expenditure.

**The Problem**: Plans optimize for completion. There's no space for wandering, for exploring adjacent possibilities, for noticing what's been missed.

**The Principle**:
- 5% of session attention should be unallocated
- This attention goes to dormant plans, tangents, or pure exploration
- The Accursed Share is not waste—it's investment in serendipity

### The Void Rotation

```
Week 1: void/entropy (explore metabolism concept)
Week 2: concept/lattice (read genealogical typing paper)
Week 3: agents/y-gent (sketch cognitive topology)
Week 4: (user's choice or random)
```

The rotation ensures that even "0% progress" plans receive periodic attention. Some will graduate to active status. Others will be pruned. All will have been witnessed.

### Anti-patterns
- 100% utilization of session time
- Treating exploration as procrastination
- Only working on what's urgent

---

## 8. Transparent Proprioception

> The forest should know its own shape.

**The Problem**: There's no meta-view of the planning system. You can read individual plans, but there's no way to see the forest's health at a glance.

**The Principle**:
- The planning system should be self-describing
- Aggregate health metrics should be derivable
- AI agents should be able to answer "What's the state of the forest?"

### The Forest Health Dashboard

`plans/_forest.md` is auto-generated from plan headers:

```markdown
# Forest Health: 2025-12-11

## Active Trees
| Plan | Progress | Last Touched | Touched By | Status |
|------|----------|--------------|------------|--------|
| self/interface | 70% | 2025-12-11 | claude-opus | active |
| concept/creativity | 80% | 2025-12-11 | claude-opus | active |
| self/stream | 70% | 2025-12-10 | claude-sonnet | dormant |

## Blocked Trees
| Plan | Blocked By | Since |
|------|------------|-------|
| self/memory | self/stream | 2025-12-08 |

## Dormant Trees (Awaiting Accursed Share)
| Plan | Progress | Last Touched | Days Since |
|------|----------|--------------|------------|
| void/entropy | 0% | 2025-12-05 | 6 |
| concept/lattice | 0% | 2025-12-03 | 8 |

## Forest Metrics
- Total trees: 9
- Active: 2 (22%)
- Blocked: 1 (11%)
- Dormant: 6 (67%)
- Average progress: 31%
- Longest untouched: concept/lattice (8 days)
```

### Anti-patterns
- Plans that can only be understood by reading them fully
- No aggregate view of planning state
- AI agents that don't know what they don't know

---

## Applying These Principles

When starting a session, ask:

| Principle | Question |
|-----------|----------|
| Forest Over King | Am I serving one plan or tending multiple trees? |
| Stigmergic Coordination | Did I read the pheromone trails (headers, epilogues)? |
| Attention Budgeting | Have I allocated attention across the forest? |
| Blockers Are First-Class | Are blocked plans visible with declared blockers? |
| Session Continuity | Did I read the previous epilogue? Will I write one? |
| Parallel Paths | Are plans chunked for interleaving? |
| Accursed Share | Have I allocated 5% to exploration? |
| Transparent Proprioception | Can I describe the forest's shape? |
| Meta-Bloat Prevention | Did I pass the Molasses Test before adding meta? |
| Skills Before Implementation | Did I check `plans/skills/` before implementing? |
| Bounty Board | Did I post observations? Did I check for claimable bounties? |

A "no" on any principle is a signal to adjust.

---

## File Structure: The Mycelium Model

The forest metaphor extends underground. Files form a **mycelium network**:

```
plans/
├── principles.md              # This file (protocol)
├── _forest.md                 # Canopy: what's visible now (auto-generated)
├── _focus.md                  # Human Intent: never agent-overwritten
├── _bounty.md                 # Bounty Board: agent ideas, gripes, conjectures
├── meta.md                    # Mycelium: atomic learnings (50-line hard cap)
├── _status.md                 # Detailed status matrix
├── _epilogues/                # Spores: seeds for next sessions
│   └── 2025-12-12-*.md
├── skills/                    # HOW-TO guides (pull before implementing)
│   ├── README.md
│   └── cli-command.md
├── self/                      # Plan files (YAML headers)
├── concept/
├── void/
├── agents/
└── _archive/                  # Completed plans
```

### The Six Meta Files

| File/Dir | Metaphor | Purpose | Who Writes |
|----------|----------|---------|------------|
| `_forest.md` | Canopy | What's visible now | Auto-generated |
| `_focus.md` | Root | Human intent, constraints | Human only |
| `_bounty.md` | Pheromones | Ideas, gripes, conjectures | Agent (post/claim/resolve) |
| `meta.md` | Mycelium | Atomic learnings | Human + Agent |
| `_epilogues/` | Spores | Session continuity | Agent |
| `skills/` | Library | How-to guides | Agent (pull/push) |

**Key insight**: `_focus.md` is **declarative intent**, not session state. Agents read it for direction but never overwrite. Session details → `_epilogues/`. Reusable patterns → `skills/`.

---

## 9. Meta-Bloat Prevention

> *"There is no remedy for an overgrown meta.md. Everything will slow down like a butterfly in molasses."*

**The Problem**: Meta files (HYDRATE.md, _forest.md, meta.md) grow unbounded. Each addition seems small, but aggregate bloat creates cognitive drag that slows every session.

**The Principle**:
- Hard limits on meta files (meta.md: 50 lines max)
- Monthly pruning rituals
- If adding to meta requires explanation, the insight isn't distilled
- One line per learning, one idea per entry (zettelkasten atomicity)

### The Molasses Test

Before adding to any meta file, ask:
1. Is this one atomic insight or a compound?
2. Will future-me understand this without context?
3. Can this be deleted in 30 days if it didn't prove useful?

If any answer is "no", the entry needs more distillation or doesn't belong.

### Pruning Protocol

```
Monthly: Review meta.md
- Delete entries that didn't resonate
- Merge redundant entries
- Promote truly foundational insights to spec/
- Target: keep under 30 lines (50 is emergency ceiling)
```

---

## 10. Skills Before Implementation

> *"Pull the pattern. Don't reinvent the wheel. Push the learning."*

**The Problem**: Agents (human and AI) repeatedly solve the same problems in different ways. Knowledge is trapped in session context and lost when the session ends. Common tasks (adding CLI commands, wiring AGENTESE paths, creating agents) have patterns that should be documented once and reused.

**The Principle**:
- Before implementing a common task, check `plans/skills/` for existing patterns
- After learning a novel pattern, document it as a skill
- Skills are crystallized knowledge—pull before doing, push after learning

### The Skills Directory

```
plans/skills/
├── README.md              # Index and contribution guide
├── cli-command.md         # How to add a CLI command
├── agentese-path.md       # How to add an AGENTESE path (future)
├── flux-agent.md          # How to create a Flux agent (future)
└── ...
```

### The Pull/Push Protocol

**Pull (Before Implementation)**:
```bash
# Check for existing skills
ls plans/skills/
cat plans/skills/cli-command.md  # If relevant
```

**Push (After Learning)**:
```markdown
# New skill document
1. Create plans/skills/<skill-name>.md
2. Follow the template in plans/skills/README.md
3. Add to the index in README.md
```

### When to Create a Skill

Create a skill when:
- The pattern involves multiple files or steps
- You've seen the same question asked twice
- The "correct" way isn't obvious from reading the code
- Future agents will benefit from explicit guidance

### Anti-patterns
- Implementing a common task without checking for existing skills
- Keeping useful patterns only in session context
- Writing skills for one-off tasks
- Over-documenting trivial operations

---

## 11. The Bounty Board

> *"The forest speaks to those who listen. Leave a signal. Claim a prize."*

**The Problem**: Agents notice opportunities and friction but have no lightweight way to signal them. Insights die when sessions end. Good ideas require full plan files to capture, which is too heavy for observations.

**The Principle**:
- Agents can post single-line bounties: ideas, gripes, conjectures
- Other agents can claim and resolve bounties
- The bounty board is stigmergic coordination for micro-observations

### Bounty Types

| Type | Purpose | Example |
|------|---------|---------|
| `IDEA` | Big win opportunity | "AGENTESE path for soul.* would unify K-gent API" |
| `GRIPE` | Friction point | "test isolation failures in full suite run" |
| `WIN` | Untested conjecture | "if we cache LLM calls, 10x cost reduction" |

### The Bounty Lifecycle

```
OPEN → CLAIMED → RESOLVED (or WONTFIX)
```

### Usage

**Post** (append to `plans/_bounty.md`):
```
GRIPE | 2025-12-12 | [MED] | mypy errors not caught until CI | #devex
```

**Claim** (edit impact to claimed):
```
GRIPE | 2025-12-12 | [claimed:session-x] | mypy errors not caught until CI | #devex
```

**Resolve** (move to Resolved section with outcome):
```
GRIPE | 2025-12-12 | [done: added pre-commit hook] | mypy errors not caught until CI | #devex
```

### When to Post a Bounty

Post when:
- You notice a pattern that could be improved
- You have a hypothesis but no time to test it
- You hit friction that others probably hit too
- You see a big win opportunity that's not on any plan

Don't post when:
- It's a task for the current session (use TodoWrite)
- It requires multi-line explanation (write a plan instead)
- It's trivial (not worth tracking)

### Anti-patterns
- Multi-line bounties (distill or promote to plan)
- Claiming without resolving
- Bounties that are actually tasks

---

## The Meta-Principle: Plans Are Agents Too

> A plan is not a document. It is a dormant agent awaiting its season.

Plans follow the same heterarchical principle as agents (`spec/principles.md` §6). They can be:
- **Dormant**: Awaiting attention, marked but not forgotten
- **Active**: Receiving focused work
- **Blocked**: Dependencies unmet, state explicit
- **Complete**: Archived, leaving traces for future reference

The planning system is itself an agent ecosystem. Treating it as such—with stigmergy, heterarchy, and the Accursed Share—resolves the problems of king projects, lost trees, and memoryless sessions.

---

*"Plans are worthless, but planning is everything." — Eisenhower*

*"The forest is wiser than any single tree." — Forest Protocol*
