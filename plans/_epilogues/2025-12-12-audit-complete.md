# Chief of Staff Briefing: Post-Lattice Operations

> *"Excellence is not a singular act, but a habit. You are what you repeatedly do."* — Shaquille O'Neal (paraphrasing Aristotle)

**Classification**: OPERATIONAL DIRECTIVE
**Date**: 2025-12-12
**From**: Chief of Staff, kgents Forest Operations
**To**: Incoming Agent (Claude instance)
**Re**: Strategic priorities following Lattice completion

---

## Executive Summary

The Lattice implementation is **complete** (69 tests, all exit criteria verified). This was foundational work—every concept in AGENTESE now has enforced genealogy. The family tree knows its roots.

Your mission: **harvest the momentum**. We have several projects at 90%+ completion. Finishing them compounds our capability. Leaving them at 90% is waste.

This briefing provides:
1. Strategic context (why these priorities)
2. Tactical guidance (how to execute)
3. Quality gates (what "done" means)
4. Escalation paths (when to ask for help)

---

## Situational Awareness

### Read Before Acting

| Document | Purpose | Read Time |
|----------|---------|-----------|
| `HYDRATE.md` | System context seed | 2 min |
| `plans/_focus.md` | Human intent (Kent's wishes) | 1 min |
| `plans/_forest.md` | Current state of all projects | 2 min |
| `plans/principles.md` | Governing protocol | 5 min (skim) |

**Critical note**: `_focus.md` still references Lattice as primary. This is stale—Lattice is done. Use the attention budget below instead. Only Kent writes to `_focus.md`.

### Forest State at Handoff

```
COMPLETE (recent):
  ✅ Lattice           100%  [69 tests]   — Genealogical enforcement
  ✅ Flux Functor      100%  [261 tests]  — Living Pipelines
  ✅ I-gent v2.5       100%  [137 tests]  — TUI interface
  ✅ Reflector         100%  [36 tests]   — Terminal/Headless bridge

NEAR COMPLETION (your focus):
  🟡 concept/creativity  90%  — 3 polish tasks remain
  🟡 agents/t-gent       90%  — Type V AdversarialGym remains
  🟡 self/stream         70%  — 3 phases remain (unblocks memory)
  🟡 void/entropy        60%  — CLI/TUI polish remains

BLOCKED:
  ⏸️ self/memory         30%  — Awaits self/stream Phase 2.4

DORMANT (future):
  💤 agents/semaphores    0%  — Spec complete, awaits implementation
  💤 agents/terrarium     0%  — Depends on semaphores
```

---

## Strategic Priorities

### The 60/25/10/5 Rule

Per the Forest Protocol, allocate attention across multiple trees:

| Allocation | Project | Objective | Why Now |
|------------|---------|-----------|---------|
| **60%** | `concept/creativity` | 90% → 100% | Highest ROI. Three tasks from done. |
| **25%** | `self/stream` | 70% → 85% | Unblocks `self/memory`. Foundational. |
| **10%** | `void/entropy` | CLI tithe | Quick win. User-facing command. |
| **5%** | Exploration | Read semaphores spec | Future-proofing. No implementation. |

**Do not** abandon this allocation mid-session. The forest needs balanced attention, not a single tree consuming all sunlight.

---

## Priority 1: concept/creativity (90% → 100%)

### Strategic Context

The creativity subsystem provides **quality mechanisms** for agent output:
- MDL compression prevents fake summarization
- Contract Melt bounds hallucination with postconditions
- Wundt Curator filters boring/chaotic output
- Critic's Loop enables self-improvement

**90% means we have the engine but not the finishing touches.** Three tasks remain.

### Tactical Objectives

| Task | Difficulty | Files | Deliverable |
|------|------------|-------|-------------|
| Bidirectional Skeleton | Medium | `protocols/agentese/contexts/world.py` | Texture→structure feedback loop |
| Wire Pataphysics to LLM | Low | `protocols/agentese/contexts/void.py` | High-temp LLM call in `solve` |
| Auto-Wire Curator | Medium | `protocols/agentese/logos.py` | Middleware injection for GENERATION |

### Implementation Guidance

**Task 1: Bidirectional Skeleton**

The current skeleton is unidirectional: structure → texture. We need feedback from texture critique to revise structure.

```python
@dataclass
class NarrativePipeline:
    """Telic/Paratelic oscillation with structure rewriting."""
    max_iterations: int = 3
    threshold: float = 0.7

    async def generate(self, intent: str, observer: Umwelt) -> str:
        skeleton = await self._generate_skeleton(intent, observer)

        for iteration in range(self.max_iterations):
            prose = await self._render_prose(skeleton, observer)
            critique = await self._critique_prose(prose, observer)

            if critique.score > self.threshold:
                return prose

            if critique.suggests_structure_change:
                # THE KEY ADDITION: texture rewrites structure
                skeleton = await self._revise_skeleton(skeleton, critique)

        return prose  # Best effort
```

**Wire to**: `world.*.skeleton` AGENTESE aspect.

**Task 2: Wire Pataphysics to LLM**

The `@meltable(ensure=...)` decorator exists. When postcondition fails, it should call LLM with high temperature for "imaginary solution."

```python
# In void.py or melting.py
async def pataphysics_solve(
    context: dict,
    postcondition: Callable[[Any], bool],
    llm_client: LLMClient | None = None,
    max_retries: int = 3,
) -> Any:
    """
    Jarry's method: imaginary solutions bounded by contracts.

    Falls back to oblique strategy if no LLM client.
    """
    if llm_client is None:
        return FeverStream().oblique()

    for attempt in range(max_retries):
        result = await llm_client.generate(
            prompt=f"Given context: {context}\nProvide an imaginary solution.",
            temperature=1.4,  # High creativity
            max_tokens=200,
        )
        if postcondition(result):
            return result

    raise ContractViolationError("Pataphysics exhausted")
```

**Task 3: Auto-Wire Curator**

The `WundtCurator` exists in `protocols/agentese/middleware/curator.py`. It needs to automatically apply to GENERATION category aspects.

```python
# In logos.py, within invoke() method
async def invoke(self, path: str, observer: Umwelt, **kwargs) -> Any:
    node = await self.resolve(path, observer)
    result = await node.invoke(observer, **kwargs)

    # NEW: Apply curator for generation aspects
    if node.category == AspectCategory.GENERATION:
        curator = WundtCurator()
        result = await curator.filter(result, observer, self)

    return result
```

### Quality Gates

| Gate | Verification |
|------|--------------|
| All existing tests pass | `pytest protocols/agentese/ -v` |
| New tests for each task | Minimum 5 tests per task |
| Mypy clean | `uv run mypy .` returns 0 errors |
| No regressions | Test count ≥ current baseline |

### Exit Criteria

- [ ] `NarrativePipeline` supports bidirectional feedback
- [ ] `void.pataphysics.solve` calls LLM (with oblique fallback)
- [ ] `WundtCurator` auto-applies to GENERATION aspects
- [ ] 15+ new tests across the three tasks
- [ ] All 8,714+ existing tests still pass

---

## Priority 2: self/stream Phases 2.2-2.4 (25%)

### Strategic Context

The context management system is the **memory infrastructure** for all agents. Phase 2.1 gave us:
- ContextWindow (Store Comonad) — 41 tests
- LinearityMap (resource classes) — 38 tests
- ContextProjector (compression) — 28 tests
- MDL validation — 43 tests

**Phases 2.2-2.4 add persistence and health monitoring.** Completing Phase 2.4 unblocks `self/memory`.

### Tactical Objectives

| Phase | Component | Purpose | Tests Target |
|-------|-----------|---------|--------------|
| 2.2 | ModalScope | Git-like context branching | 25+ |
| 2.3 | Pulse + VitalityAnalyzer | Zero-cost health signals | 20+ |
| 2.4 | StateCrystal + Reaper | Checkpointing with TTL | 30+ |

**For this session**: Focus on Phase 2.2 (ModalScope). If time permits, start 2.3.

### Implementation Guidance: ModalScope

**The Insight**: Comonadic `duplicate()` naturally creates branching. ModalScope makes this persistent and mergeable.

```
Main Context ──duplicate()──▶ Branch A (explore)
                             │
                             ├─▶ merge() ──▶ Main Context (extended)
                             │
                             └─▶ discard() ──▶ [composted]
```

**File structure**:
```
impl/claude/agents/d/
├── modal_scope.py        # Core types
├── scope_tree.py         # Branch hierarchy management
└── _tests/
    ├── test_modal_scope.py
    └── test_scope_tree.py
```

**Core types**:
```python
class MergeStrategy(Enum):
    SUMMARIZE = "summarize"    # Compress branch to summary turn
    CHERRY_PICK = "cherry_pick"  # Select specific turns
    SQUASH = "squash"          # Single turn with key decisions
    REBASE = "rebase"          # Replay child turns on current state

@dataclass
class ModalScope:
    scope_id: str
    parent_scope: str | None
    branch_name: str
    created_at: datetime
    window: ContextWindow
    entropy_budget: float = 0.1  # 10% of parent tokens
    merge_strategy: MergeStrategy = MergeStrategy.SUMMARIZE

    def branch(self, name: str, budget: float = 0.05) -> "ModalScope":
        """Create isolated child scope."""
        child_window = ContextWindow.from_dict(self.window.to_dict())
        return ModalScope(
            scope_id=f"{self.scope_id}:{name}",
            parent_scope=self.scope_id,
            branch_name=name,
            created_at=datetime.now(UTC),
            window=child_window,
            entropy_budget=budget,
        )

    async def merge(self, child: "ModalScope") -> MergeResult:
        """Merge child branch back into this scope."""
        ...

    def discard(self, child: "ModalScope") -> None:
        """Compost the branch. Return entropy budget."""
        ...
```

**AGENTESE wiring**:
```python
# Branch for speculative exploration
await logos.invoke("void.entropy.sip", observer, branch_name="explore")
# ...work in branch...
await logos.invoke("void.entropy.pour", observer, action="merge")
```

### Quality Gates

| Gate | Verification |
|------|--------------|
| Comonad laws preserved | Property-based tests with Hypothesis |
| Branch isolation | Changes in branch don't affect parent |
| Merge correctness | Summary contains key decisions |
| Budget enforcement | Branch creation fails if over budget |

---

## Priority 3: void/entropy CLI (10%)

### Strategic Context

The MetabolicEngine is **done** (36 tests). The `tithe` command lets users voluntarily discharge entropy pressure. This is a **quick win** that makes the system more interactive.

### Tactical Objective

Create `kgents tithe` CLI command. One file, one handler, wire to hollow.

### Implementation

```python
# protocols/cli/handlers/tithe.py

from protocols.cli.framework import expose, CommandContext

class TitheHandler:
    @expose(help="Voluntarily discharge entropy pressure")
    async def tithe(self, ctx: CommandContext, amount: float = 0.1) -> dict:
        """
        Pay for order. Discharge metabolic pressure.

        The Accursed Share: surplus must be spent.
        Usage: kgents tithe [--amount 0.2]
        """
        metabolism = ctx.get_service("metabolism")
        if metabolism is None:
            return {"error": "Metabolism not initialized", "hint": "Run in cortex mode"}

        result = metabolism.tithe(amount)

        ctx.output(f"Discharged: {result['discharged']:.2f}")
        ctx.output(f"Remaining: {result['remaining_pressure']:.2f}")
        ctx.output(f"\n{result['gratitude']}")

        return result
```

**Wire to hollow.py**: Add `TitheHandler` to the handler registry.

### Quality Gates

- [ ] `kgents tithe` executes without error
- [ ] `kgents tithe --amount 0.5` accepts parameter
- [ ] Graceful error when metabolism unavailable
- [ ] 3-5 tests covering success and error paths

---

## Priority 4: Exploration (5%)

### Strategic Context

The `agents/semaphores` spec describes the **Purgatory Pattern** — a way to handle human-in-the-loop without blocking the Flux stream. This is foundational for future interactive agents.

### Tactical Objective

**Read only. No implementation.** Understand the architecture so future sessions can implement.

**Read**: `plans/agents/semaphores.md`

**Key concepts to understand**:
1. Why Python generators can't be pickled (the Generator Trap)
2. How Purgatory ejects state as data instead of pausing stack frames
3. How resolution re-injects as high-priority Perturbation
4. The Rodizio metaphor (red card/green card)

**Optional deliverable**: Add questions or insights to `plans/meta.md` (one line per insight, per protocol).

---

## Execution Protocols

### Before You Begin

```bash
# Verify baseline
cd impl/claude
pytest --collect-only -q | tail -1  # Note the count
uv run mypy .                        # Should be 0 errors
```

### During Execution

1. **Work in priority order**. Don't skip ahead.
2. **Run tests frequently**. After each logical unit.
3. **Mark progress**. Update `plans/_status.md` as you complete tasks.
4. **Ask if blocked**. Don't spin. Use the escalation path.

### Escalation Path

If blocked for more than 15 minutes on a single issue:

1. Document the block clearly
2. Add to "Unresolved Questions" in your epilogue
3. Move to next task
4. Flag for human review

### Before You End

1. **Run full test suite**: `pytest -q --tb=short`
2. **Run mypy**: `uv run mypy .`
3. **Update status files**:
   - `plans/_forest.md` — Update progress percentages
   - `plans/_status.md` — Mark tasks complete/in-progress
4. **Write epilogue**: `plans/_epilogues/2025-12-12-<your-summary>.md`

---

## Quality Standards

### Code Quality

| Standard | Expectation |
|----------|-------------|
| Type hints | All new functions fully typed |
| Docstrings | All public functions documented |
| Error handling | Sympathetic errors with hints, not None returns |
| Tests | Minimum 5 tests per new component |
| Naming | Follow existing conventions in codebase |

### Commit Quality (if asked to commit)

- Atomic commits (one logical change per commit)
- Conventional commit messages
- Tests pass before commit
- No `--no-verify` unless explicitly authorized

### Documentation Quality

- Update affected plan files
- Don't expand meta files (50-line cap on `meta.md`)
- Atomic insights only (if unclear without context, don't add it)

---

## Anti-Patterns to Avoid

| Anti-Pattern | What It Looks Like | What To Do Instead |
|--------------|--------------------|--------------------|
| **The Butterfly in Molasses** | Expanding meta files with prose | One line per insight, or don't add |
| **The King Project** | Spending 100% on one task | Follow 60/25/10/5 allocation |
| **The Orphan Commit** | Declaring done without tests | Tests first, always |
| **The Silent Failure** | Returning `None` on error | Raise sympathetic exception |
| **The Scope Creep** | Rewriting instead of polishing | Polish means small changes |
| **The Perfectionist Trap** | Blocking on edge cases | 80% coverage is fine, ship it |

---

## Your Allies (Existing Infrastructure)

| Module | What It Does | When To Use |
|--------|--------------|-------------|
| `agents/d/context_window.py` | Store Comonad (41 tests) | ModalScope foundation |
| `agents/d/linearity.py` | Resource class tracking (38 tests) | Compression priority |
| `agents/d/projector.py` | Galois Connection compression (28 tests) | Branch summarization |
| `protocols/agentese/middleware/curator.py` | WundtCurator (49 tests) | Auto-wire to Logos |
| `protocols/agentese/metabolism/engine.py` | MetabolicEngine (36 tests) | Tithe command |
| `protocols/agentese/contexts/void.py` | Void context | Pataphysics wiring |
| `agents/flux/` | FluxAgent (261 tests) | Future semaphores |

---

## Success Metrics

By end of session, aim for:

| Metric | Target |
|--------|--------|
| `concept/creativity` progress | 100% |
| `self/stream` progress | 75-85% |
| `void/entropy` CLI | Complete |
| New tests added | 40+ |
| Test suite still passing | 8,714+ |
| Mypy errors | 0 |

---

## The Spirit of This Work

> *"The forest is wiser than any single tree."*

You are not just writing code. You are cultivating an ecosystem where:
- Concepts have genealogy (Lattice)
- Output has taste (Curator)
- Memory has persistence (Stream/Crystal)
- Surplus has discharge (Entropy/Tithe)
- Humans have agency (Semaphores, future)

Each piece you complete strengthens the whole. The creativity polish makes agents' output better. The stream phases give agents memory. The tithe command gives users control. These compound.

**Work with joy.** The system is designed for it. Fun is free.

---

## Closing Directive

You have everything you need:
- Clear priorities with specific deliverables
- Implementation guidance with code snippets
- Quality gates with verification commands
- Escalation paths if blocked

Trust the plan. Execute methodically. Update status as you go. Leave the forest healthier than you found it.

The lattice is complete. Now the forest grows.

---

**End of Briefing**

*"Plans are worthless, but planning is everything." — Eisenhower*

*Prepared by: Chief of Staff, kgents Forest Operations*
*Distribution: Incoming Agent*
*Classification: OPERATIONAL DIRECTIVE*
