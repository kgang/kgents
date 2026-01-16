---
path: self.forest.plan.cli-renaissance
status: active
priority: high
created: 2026-01-16
author: claude-opus-4
grounding: zero-seed-analysis, analysis-operad
galois_loss: 0.35
---

# CLI Renaissance: A Plan for Transformative Improvement

> *"The CLI is not a protocol. It is a projection functor."*
> *"42 commands is not curated. It is accumulated."*

This plan synthesizes findings from a comprehensive audit of the kgents CLI, applying Zero Seed derivation and Analysis Operad methodology to identify transformative improvements.

---

## Executive Summary

The kgents CLI has strong categorical foundations but suffers from **organic growth debt**. The core architecture (dimension system, AGENTESE projection, effect declarations) is sound, but the surface layer has accumulated friction that violates constitutional principles.

| Metric | Current | Target |
|--------|---------|--------|
| Galois Loss | L = 0.35 | L < 0.20 |
| Command Count | 42 | < 25 |
| Principle Alignment | 5/7 | 7/7 |
| Spec-Impl Coherence | 75% | 95% |

**The Core Insight**: The CLI's conceptual model is coherent, but its manifestation betrays the principles it claims to embody.

---

## Part I: Diagnostic Synthesis

### 1.1 Zero Seed Layer Analysis

| Layer | Component | Loss | Assessment |
|-------|-----------|------|------------|
| L1 (Axiom) | "CLI = AGENTESE projection" | 0.10 | Sound axiom, well-grounded |
| L2 (Value) | 7 Principles mapping | 0.35 | Curated, Joy-Inducing violated |
| L3 (Prompt) | Command naming | 0.40 | Inconsistent (nouns vs verbs) |
| L4 (Spec) | Dimension system | 0.15 | Well-specified, implemented |
| L5 (Code) | Handler implementations | 0.45 | Three different help patterns |
| L6 (Reflection) | Error messages | 0.15 | SympatheticError is excellent |
| L7 (Interpretation) | User experience | 0.50 | Discoverability poor |

**Weighted Galois Loss: 0.35** (Empirical Tier - good but improvable)

### 1.2 Constitutional Principle Violations

#### CURATED (L = 0.45) — **VIOLATED**

> *"Intentional selection over exhaustive cataloging"*

**Evidence:**
- 42 registered commands in `hollow.py`
- Orphan commands with unclear purpose: `shortcut`, `subscribe`, `q`
- Duplicate aliases: `q` = `query`, `derive` = `derivation`
- Comments show removed commands but no curation of remaining

**Root Cause**: Commands were added incrementally without periodic review. The "parking lot" anti-pattern from Constitution Article 2.

#### JOY-INDUCING (L = 0.50) — **VIOLATED**

> *"Delight in interaction; personality matters"*

**Evidence:**
- Joy commands explicitly removed: `joy`, `challenge`, `oblique`, `constrain`, `yes-and`, `surprise-me`
- Comment in hollow.py: "Joy Commands - temporarily removed for stability"
- Most commands output functional text without personality
- Interactive mode (`-i`) exists but feels utilitarian

**Root Cause**: Stability prioritized over delight. The "coldness" anti-pattern from Constitution Article 4.

#### COMPOSABLE (L = 0.25) — **PARTIALLY VIOLATED**

> *"Agents can be combined: A + B → AB"*

**Evidence:**
- Spec promises: "path >> path works uniformly"
- Reality: No command chaining implemented
- `--json` flag enables programmatic composition (partial success)
- `flow` command exists for pre-defined compositions only

**Root Cause**: Aspirational spec without implementation follow-through.

### 1.3 Architectural Tensions (Dialectical Analysis)

| Tension | Type | Resolution Needed |
|---------|------|-------------------|
| Thin vs. Rich Handlers | PRODUCTIVE | Document pattern, keep localized |
| Sync vs. Async Execution | **PROBLEMATIC** | Add ExecutionContext dimension |
| Handler Meta vs. Static Tiers | APPARENT | Complete migration, remove static |
| Lazy Loading vs. Validation | **PROBLEMATIC** | Two-phase startup |
| Spec Promises vs. Reality | **PROBLEMATIC** | Implement or remove claims |

### 1.4 Spec-Implementation Drift

| Spec Claim | Implementation Status | Gap |
|------------|----------------------|-----|
| "path >> path works uniformly" | NOT IMPLEMENTED | High |
| "Budget estimation" | Warnings only | Medium |
| "Interactive REPL" | Chat removed | Medium |
| "AI registration validation" | Lazy loading conflicts | High |

**Orphan Implementations** (code without spec):
- `fd3.py` — Semantic channel for machine output
- `prism/` — Auto-constructive CLI from introspection
- `handler_meta.py` — Daemon-first tier classification

---

## Part II: Strategic Vision

### 2.1 The CLI Renaissance Thesis

**Current State**: A powerful categorical engine hidden behind an accumulated interface.

**Target State**: A curated, joy-inducing CLI that embodies all seven principles while maintaining categorical rigor.

**The Transformation**:
```
FROM: 42 commands, inconsistent patterns, hidden joy
  TO: 25 commands, unified patterns, discoverable delight
```

### 2.2 Guiding Principles for Changes

1. **Subtraction over Addition** — Remove before adding
2. **Pattern Unification** — One way to do things
3. **Progressive Disclosure** — Beginners see simple, experts discover depth
4. **Joy as Infrastructure** — Delight is not optional
5. **Spec-First Changes** — Update spec before implementation

### 2.3 Success Metrics

| Metric | Measurement | Target |
|--------|-------------|--------|
| Galois Loss | Zero Seed analysis | L < 0.20 |
| Command Count | `len(COMMAND_REGISTRY)` | < 25 |
| Help Consistency | Pattern audit | 100% unified |
| Discoverability | New user test | Find `play` in < 30s |
| Joy Commands | Count | ≥ 5 active |
| Spec Coverage | Orphan analysis | 0 orphan impls |

---

## Part III: Phased Implementation Plan

### Phase 1: Quick Wins (Week 1)

**Goal**: Visible improvement with minimal risk. Restore principle alignment.

#### 1.1 Add `kg start` Entry Point

**Rationale**: New users face 42 commands with no clear starting point.

**Implementation**:
```python
# protocols/cli/handlers/start.py
@handler("start", tier=1, description="Your starting point for kgents")
async def handle_start(args: list[str]) -> int:
    """Welcome to kgents! Here's how to begin."""
    console.print(Panel("""
[bold]Welcome to kgents![/bold]

[cyan]First time?[/cyan]
  kg play          Interactive tutorials
  kg coffee        Morning ritual (daily practice)

[cyan]Working on code?[/cyan]
  kg brain         Memory and knowledge
  kg witness       Mark your decisions
  kg explore       Navigate the codebase

[cyan]Need help?[/cyan]
  kg --help        All commands
  kg docs          Documentation
    """))
    return 0
```

**Files to modify**:
- `protocols/cli/handlers/start.py` (new)
- `protocols/cli/hollow.py` (register)
- `protocols/cli/help_global.py` (add to Joy Commands section)

**Estimated effort**: 1 hour

#### 1.2 Restore Joy Commands

**Rationale**: Joy-Inducing principle explicitly violated by removal.

**Implementation**: Restore as lightweight implementations:

```python
# protocols/cli/handlers/joy.py

@handler("oblique", tier=1, description="Draw an Oblique Strategy card")
async def handle_oblique(args: list[str]) -> int:
    """Draw wisdom from Brian Eno's Oblique Strategies."""
    strategies = [
        "Honor thy error as a hidden intention",
        "What would your closest friend do?",
        "Remove specifics and convert to ambiguities",
        "Use an old idea",
        "State the problem in words as clearly as possible",
        # ... 100+ more
    ]
    card = random.choice(strategies)
    console.print(Panel(f"[italic]{card}[/italic]", title="🎴 Oblique Strategy"))
    return 0

@handler("surprise", tier=1, description="Discover something unexpected")
async def handle_surprise(args: list[str]) -> int:
    """Surface serendipitous wisdom from the void."""
    # Pull random crystal, forgotten mark, or archived insight
    ...
```

**Commands to restore**:
- `kg oblique` — Oblique Strategy card
- `kg surprise` — Random serendipity from void context
- `kg yes-and` — Improv-style affirmation prompt
- `kg challenge` — Daily coding challenge
- `kg constrain` — Random creative constraint

**Files to modify**:
- `protocols/cli/handlers/joy.py` (new)
- `protocols/cli/hollow.py` (register 5 commands)

**Estimated effort**: 2-3 hours

#### 1.3 Standardize Help Format

**Rationale**: Three different help patterns create cognitive friction.

**Implementation**: Create shared help renderer:

```python
# protocols/cli/help_template.py

def render_command_help(
    name: str,
    description: str,
    usage: str,
    subcommands: list[tuple[str, str]] | None = None,
    flags: list[tuple[str, str, str]] | None = None,
    examples: list[str] | None = None,
    agentese_paths: list[str] | None = None,
    philosophy: str | None = None,
) -> None:
    """Unified help renderer for all commands."""
    # Always use Rich, always same structure
    ...
```

**Migration**: Update handlers one by one to use template.

**Estimated effort**: 4 hours

#### 1.4 Update Global Help

**Rationale**: `kg play` exists but isn't visible in `kg --help`.

**Implementation**:
```python
# In help_global.py, add to HELP_TEXT:
[bold cyan]Getting Started[/bold cyan]
  start         Your starting point (new users begin here)
  play          Interactive tutorials
  coffee        Morning ritual
```

**Estimated effort**: 30 minutes

---

### Phase 2: Command Curation (Week 2)

**Goal**: Reduce command count from 42 to <25 through principled curation.

#### 2.1 Command Audit Framework

For each command, answer:

1. **Grounded?** — Does it trace to a spec or principle?
2. **Used?** — Evidence of actual usage (logs, mentions)?
3. **Unique?** — Is there overlap with another command?
4. **Necessary?** — Could users accomplish this another way?

#### 2.2 Proposed Command Disposition

| Command | Disposition | Rationale |
|---------|-------------|-----------|
| `q`, `query` | **MERGE** → `brain search` | Duplicate functionality |
| `shortcut` | **ARCHIVE** | Low usage, unclear purpose |
| `subscribe` | **ARCHIVE** | Daemon-only, not user-facing |
| `derive` | **MERGE** → `derivation` | Alias confusion |
| `op` | **ARCHIVE** | Opaque name, low discoverability |
| `membrane` | **FOLD** into `self` | AGENTESE context alignment |
| `archaeology` | **KEEP** | Unique, grounded, used |
| `flow` | **KEEP** | Composition primitive |
| `dawn` | **KEEP** | Daily operating surface |

**Full audit table**: See Appendix A.

#### 2.3 Alias Rationalization

**Current aliases** (confusing):
- `q` = `query` (but also could mean "quit")
- `derive` = `derivation` (why two names?)
- `m` = `mark` (ok, short form)

**Proposed policy**:
- Single-letter aliases only for frequently-used commands
- No synonym aliases (derive/derivation)
- Document all aliases in one place

**Approved aliases**:
| Alias | Command | Rationale |
|-------|---------|-----------|
| `m` | `witness mark` | High frequency |
| `w` | `witness` | High frequency |
| `b` | `brain` | High frequency |
| `?` | `start` | Universal help symbol |

#### 2.4 Command Grouping Revision

**Current groups** (in help_global.py):
- Crown Jewels, Forest Protocol, Exploration, Joy Commands, Development Tools

**Proposed groups**:
```
Getting Started     start, play, coffee
Memory & Witness    brain, witness, decide
Development         explore, audit, probe, analyze
AGENTESE Contexts   self, world, concept, void, time
Utilities           docs, completions, migrate
Joy                 oblique, surprise, challenge
```

---

### Phase 3: Architectural Fixes (Week 3-4)

**Goal**: Resolve PROBLEMATIC tensions identified in dialectical analysis.

#### 3.1 ExecutionContext Dimension

**Problem**: Complex event loop handling scattered across code.

**Solution**: Add explicit ExecutionContext to dimension system.

```python
# protocols/cli/dimensions.py

class ExecutionContext(Enum):
    CLI_DIRECT = "cli_direct"      # Normal CLI invocation
    DAEMON_WORKER = "daemon_worker" # Inside daemon thread pool
    DAEMON_MAIN = "daemon_main"    # Daemon main thread
    REPL = "repl"                  # Interactive mode

@dataclass(frozen=True)
class Dimensions:
    category: AspectCategory
    execution: Execution
    statefulness: Statefulness
    seriousness: Seriousness
    reversibility: Reversibility
    explainability: Explainability
    context: ExecutionContext  # NEW

def derive_context() -> ExecutionContext:
    """Derive execution context from environment."""
    if os.environ.get("KGENTS_DAEMON_WORKER"):
        return ExecutionContext.DAEMON_WORKER
    if os.environ.get("KGENTS_DAEMON_MAIN"):
        return ExecutionContext.DAEMON_MAIN
    if sys.flags.interactive:
        return ExecutionContext.REPL
    return ExecutionContext.CLI_DIRECT
```

**Files to modify**:
- `protocols/cli/dimensions.py`
- `protocols/cli/projection.py`
- `spec/protocols/cli.md`

#### 3.2 Two-Phase Startup

**Problem**: Lazy loading conflicts with validation-at-startup.

**Solution**: Fast shell startup + background validation.

```python
# protocols/cli/hollow.py

async def validate_registrations_background():
    """Run validation in background after CLI is responsive."""
    await asyncio.sleep(0.1)  # Let CLI respond first
    results = await validate_all_registrations()
    if results.has_errors:
        # Surface on next command or via daemon notification
        cache_validation_warnings(results)

def main():
    # Phase 1: Fast startup (< 50ms)
    setup_minimal_shell()

    # Phase 2: Background validation (non-blocking)
    if not os.environ.get("KGENTS_SKIP_VALIDATION"):
        asyncio.create_task(validate_registrations_background())
```

#### 3.3 Spec Alignment: Command Composition

**Problem**: Spec claims `path >> path` works, but it doesn't.

**Decision Point**: Implement or remove from spec?

**Option A: Implement** (Recommended)
```python
# protocols/cli/compose.py

async def compose_commands(left: str, right: str) -> Any:
    """Compose two AGENTESE paths."""
    left_result = await logos.invoke(left, observer)
    # Pass left_result as input to right
    right_result = await logos.invoke(right, observer, input=left_result)
    return right_result

# CLI syntax: kg "self.brain.search 'auth'" ">>" "concept.analyze"
```

**Option B: Remove from spec**
- Update `spec/protocols/cli.md` Part IX
- Document that composition is via `flow` command only

**Recommendation**: Option A, but scoped to AGENTESE paths only (not arbitrary shell commands).

#### 3.4 Create Missing Specs

**Orphan implementations need specs**:

1. **`spec/protocols/fd3.md`** — Semantic Data Channel
   - Purpose: Machine-readable output channel
   - Protocol: JSON-lines on fd3
   - Use cases: Agent integration, tooling

2. **`spec/protocols/prism.md`** — Auto-Constructive CLI
   - Purpose: Generate CLI from AGENTESE introspection
   - Architecture: Node → Affordances → Commands
   - Laws: Consistency with manual handlers

3. **`spec/protocols/handler-tiers.md`** — Daemon Routing
   - Purpose: Classify commands for daemon execution
   - Tiers: 1 (pure async), 2 (PTY), 3 (interactive)
   - Migration: From static sets to decorators

---

### Phase 4: Polish & Verification (Week 5)

**Goal**: Verify improvements, document changes, celebrate.

#### 4.1 Verification Protocol

```bash
# Run Zero Seed analysis again
kg analyze protocols/cli/ --mode zero-seed

# Verify Galois loss improved
# Target: L < 0.20

# Run categorical law verification
kg probe laws --path "protocols/cli"

# User testing
# Task: New user finds `play` command
# Target: < 30 seconds
```

#### 4.2 Documentation Updates

- Update `docs/cli-reference.md` with final command list
- Update `docs/quickstart.md` with new entry point
- Create `docs/skills/cli-joy-patterns.md` for joy command patterns
- Archive removed command documentation

#### 4.3 Announcement

Create `CHANGELOG.md` entry:
```markdown
## CLI Renaissance (2026-01)

### Added
- `kg start` — New user entry point
- Joy commands restored: oblique, surprise, challenge, yes-and, constrain
- ExecutionContext dimension for cleaner async handling

### Changed
- Command count reduced from 42 to 24
- Unified help format across all commands
- Aliases rationalized (see migration guide)

### Removed
- `kg shortcut`, `kg subscribe`, `kg op` (archived)
- Duplicate aliases: `q`, `derive`

### Fixed
- Spec-impl alignment for command composition
- Lazy loading / validation conflict resolved
```

---

## Part IV: Risk Analysis

### 4.1 Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Removing used command | Medium | High | Audit usage before removal |
| Breaking daemon integration | Medium | High | Test daemon paths explicitly |
| Joy commands feel gimmicky | Low | Medium | Ground in principles, test with users |
| Scope creep | High | Medium | Strict phase boundaries |

### 4.2 Rollback Plan

All changes are reversible:
- Commands archived, not deleted
- Specs versioned in git
- Feature flags for new behavior

```python
# Emergency rollback
export KGENTS_CLI_LEGACY=1  # Restore pre-renaissance behavior
```

---

## Part V: Resource Estimates

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 1: Quick Wins | 8 hours | None |
| Phase 2: Curation | 12 hours | Phase 1 |
| Phase 3: Architecture | 20 hours | Phases 1-2 |
| Phase 4: Polish | 8 hours | Phases 1-3 |
| **Total** | **48 hours** | ~2 weeks elapsed |

---

## Appendices

### Appendix A: Full Command Audit Table

| Command | Grounded | Used | Unique | Disposition |
|---------|----------|------|--------|-------------|
| `brain` | ✓ | ✓ | ✓ | KEEP |
| `witness` | ✓ | ✓ | ✓ | KEEP |
| `coffee` | ✓ | ✓ | ✓ | KEEP |
| `explore` | ✓ | ✓ | ✓ | KEEP |
| `audit` | ✓ | ✓ | ✓ | KEEP |
| `probe` | ✓ | ✓ | ✓ | KEEP |
| `analyze` | ✓ | ✓ | ✓ | KEEP |
| `decide` | ✓ | ✓ | ✓ | KEEP |
| `docs` | ✓ | ✓ | ✓ | KEEP |
| `play` | ✓ | ? | ✓ | KEEP (promote) |
| `dawn` | ✓ | ✓ | ✓ | KEEP |
| `flow` | ✓ | ✓ | ✓ | KEEP |
| `init` | ✓ | ✓ | ✓ | KEEP |
| `self` | ✓ | ✓ | ✓ | KEEP |
| `world` | ✓ | ✓ | ✓ | KEEP |
| `concept` | ✓ | ✓ | ✓ | KEEP |
| `void` | ✓ | ✓ | ✓ | KEEP |
| `time` | ✓ | ✓ | ✓ | KEEP |
| `experiment` | ✓ | ✓ | ✓ | KEEP |
| `compose` | ✓ | ✓ | ✓ | KEEP |
| `annotate` | ✓ | ✓ | ✓ | KEEP |
| `derivation` | ✓ | ✓ | ✓ | KEEP |
| `completions` | ✓ | ✓ | ✓ | KEEP |
| `migrate` | ✓ | ✓ | ✓ | KEEP |
| `query` | ✓ | ✓ | ✗ | MERGE → `brain search` |
| `q` | ✗ | ? | ✗ | REMOVE (alias confusion) |
| `shortcut` | ✗ | ✗ | ✓ | ARCHIVE |
| `subscribe` | ✓ | ✗ | ✓ | ARCHIVE (daemon-only) |
| `op` | ✗ | ✗ | ✗ | ARCHIVE |
| `derive` | ✗ | ✗ | ✗ | REMOVE (use `derivation`) |
| `membrane` | ✓ | ✓ | ✗ | FOLD → `self.membrane` |
| `wipe` | ✓ | ✓ | ✓ | KEEP (with warnings) |
| `context` | ✓ | ✓ | ✓ | KEEP |
| `portal` | ✓ | ✓ | ✓ | KEEP |
| `archaeology` | ✓ | ✓ | ✓ | KEEP |
| `evidence` | ✓ | ✓ | ✓ | KEEP |
| `graph` | ✓ | ✓ | ✓ | KEEP |
| `do` | ✓ | ✓ | ✓ | KEEP |
| `why` | ✓ | ✓ | ✓ | KEEP |
| `sovereign` | ✓ | ? | ✓ | EVALUATE |

**Result**: 42 → ~28 commands (with 5 joy commands added = 33 total, then curate to 25)

### Appendix B: Help Template Specification

```python
"""
Standard sections (in order):
1. Philosophy quote (optional, for Crown Jewels)
2. Description (1-2 sentences)
3. Usage syntax
4. Subcommands table (if any)
5. Flags table (if any)
6. Examples (2-3)
7. AGENTESE paths (for context commands)
8. Related commands
"""
```

### Appendix C: Joy Command Specifications

#### `kg oblique`
- **Source**: Brian Eno's Oblique Strategies (100+ cards)
- **Output**: Single card in styled panel
- **Flag**: `--all` to list all strategies

#### `kg surprise`
- **Source**: Void context serendipity
- **Behavior**: Surface random crystal, mark, or archived wisdom
- **Flag**: `--fossil` for only ancient wisdom

#### `kg challenge`
- **Source**: Generated or curated coding challenges
- **Behavior**: Present challenge appropriate to current context
- **Flag**: `--difficulty easy|medium|hard`

#### `kg yes-and`
- **Source**: Improv principle
- **Behavior**: Take user input, affirm and extend
- **Use case**: Brainstorming, overcoming blocks

#### `kg constrain`
- **Source**: Creative constraints library
- **Behavior**: Add random constraint to current work
- **Examples**: "No conditionals", "Under 50 lines", "One function only"

---

## Signatures

**Author**: Claude Opus 4 (2026-01-16)
**Grounding**: Zero Seed Analysis, Analysis Operad, Constitutional Principles
**Status**: Ready for review

---

*"The proof IS the decision. The curation IS the taste."*
