# Evergreen Prompt System: Wave 3+ Reformation

> *"The prompt that learns itself is the prompt that serves itself."*

**Wave:** 3-6 (Reformulated)
**Phase:** IMPLEMENTATION → Phase 1 (Foundation Fixes)
**Prerequisite:** Wave 2 COMPLETE (2025-12-16), Reformation Session (2025-12-16)
**Last Gap Analysis:** 2025-12-16
**Guard:** `[phase=ACT][entropy=0.10][dogfood=true][reformation=true]`

---

## Executive Summary

This continuation captures a **fundamental reformation** of the Evergreen Prompt System from a template compiler to a **Prompt Monad**—a self-improving system with categorical guarantees, habit learning, and full rollback capability.

The reformation emerged from:
1. Research into state-of-the-art prompt optimization (DSPy, SPEAR, Meta-Prompting, TextGRAD)
2. Developer taste decisions favoring maximum intelligence with maximum accountability
3. Recognition that Meta-Prompting formalized as a **monad** aligns perfectly with kgents' categorical foundation

---

## ⚠️ Critical Gap Analysis (2025-12-16)

A review revealed significant gaps between spec and implementation. This section documents the prioritized fixes.

### Gap Summary

| Priority | Gap | Severity | Status |
|----------|-----|----------|--------|
| **P0** | Rollback not wired to CLI | HIGH | ⏳ Ready to implement |
| **P1** | Async architecture broken | HIGH | ⏳ Ready to implement |
| **P2** | PromptM monad missing | HIGH | ⏳ Design ready |
| **P3** | Law validation incomplete | MEDIUM | ⏳ Tests ready to write |
| **P4** | Habit encoder stubs only | MEDIUM | ⏳ Deferred to Wave 4 |
| **P5** | TextGRAD not implemented | MEDIUM | ⏳ Deferred to Wave 4 |
| **P6** | Metrics not emitted | LOW | ⏳ Deferred to Wave 5 |

### P0: Wire Rollback to CLI (IMMEDIATE)

**Problem**: `rollback/registry.py` exists with full API but is not connected to compiler or CLI.

**Fix**:
```python
# In cli.py compile command
@click.option("--checkpoint/--no-checkpoint", default=True, help="Create checkpoint before compile")
def compile_command(checkpoint: bool, ...):
    if checkpoint:
        registry = get_default_registry()
        before = load_current_prompt()
        result = compiler.compile(context)
        registry.checkpoint(before.content, result.content, ...)

# New subcommand
@cli.command()
@click.argument("checkpoint_id")
def rollback(checkpoint_id: str):
    registry = get_default_registry()
    result = registry.rollback(checkpoint_id)
    click.echo(f"Rolled back to {result.checkpoint_id}")

# New subcommand
@cli.command()
@click.option("--limit", default=10)
def history(limit: int):
    registry = get_default_registry()
    for summary in registry.history(limit):
        click.echo(f"{summary.id}: {summary.reason} ({summary.timestamp})")
```

### P1: Fix Async Architecture (IMMEDIATE)

**Problem**: `loop.run_until_complete()` in `sections/forest.py:289-295` and `sections/context.py` will throw/hang in async contexts.

**Fix**:
```python
# Option A: Make SectionCompiler.compile() async (preferred)
class SectionCompiler(Protocol):
    async def compile(self, context: CompilationContext) -> Section:
        ...

# In compiler.py
async def compile(self, context: CompilationContext) -> CompiledPrompt:
    sections = await asyncio.gather(
        *[compiler.compile(context) for compiler in relevant_compilers]
    )
    ...

# Sync shim for CLI
def compile_sync(self, context: CompilationContext) -> CompiledPrompt:
    return asyncio.run(self.compile(context))

# Option B: Event loop detection guard (quick fix)
def compile(self, context: CompilationContext) -> Section:
    soft = self._create_soft_section()
    try:
        loop = asyncio.get_running_loop()
        # Already in async context - use nest_asyncio or thread pool
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(soft.crystallize(context)).section
    except RuntimeError:
        # No event loop - create one
        return asyncio.run(soft.crystallize(context)).section
```

### P2: Implement PromptM Monad (FOUNDATION)

**Problem**: Spec promises `PromptM` monad but no `monad.py` exists.

**File to create**: `impl/claude/protocols/prompt/monad.py`

```python
@dataclass(frozen=True)
class PromptM(Generic[A]):
    """
    The Prompt Monad: a self-improving prompt computation.

    Laws (must hold):
    - Left Identity:  unit(x) >>= f ≡ f(x)
    - Right Identity: m >>= unit ≡ m
    - Associativity:  (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
    """
    value: A
    reasoning_trace: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    checkpoint_id: str | None = None

    @staticmethod
    def unit(value: A) -> "PromptM[A]":
        return PromptM(value=value)

    def bind(self, f: Callable[[A], "PromptM[B]"]) -> "PromptM[B]":
        result = f(self.value)
        return PromptM(
            value=result.value,
            reasoning_trace=self.reasoning_trace + result.reasoning_trace,
            provenance=self.provenance + result.provenance,
            checkpoint_id=result.checkpoint_id,
        )

    def map(self, f: Callable[[A], B]) -> "PromptM[B]":
        return PromptM(
            value=f(self.value),
            reasoning_trace=self.reasoning_trace,
            provenance=self.provenance,
            checkpoint_id=self.checkpoint_id,
        )
```

### P3: Add Law Validation Tests (VERIFICATION)

**Problem**: `_validate_laws()` only checks empties/duplicates. `test_monad.py` doesn't exist.

**Files to create**:
- `impl/claude/protocols/prompt/_tests/test_monad.py`
- `impl/claude/protocols/prompt/_tests/test_laws.py`

```python
# test_monad.py
def test_monad_left_identity():
    """unit(x) >>= f ≡ f(x)"""
    x = Section(name="test", content="hello", token_cost=5, required=True)
    f = lambda s: PromptM.unit(s.with_content(s.content.upper()))

    left = PromptM.unit(x).bind(f)
    right = f(x)

    assert left.value.content == right.value.content

def test_monad_right_identity():
    """m >>= unit ≡ m"""
    m = PromptM.unit(Section(name="test", content="hello", token_cost=5, required=True))
    result = m.bind(PromptM.unit)
    assert result.value.content == m.value.content

def test_monad_associativity():
    """(m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)"""
    m = PromptM.unit(Section(name="test", content="hello", token_cost=5, required=True))
    f = lambda s: PromptM.unit(s.with_content(s.content.upper()))
    g = lambda s: PromptM.unit(s.with_content(s.content + "!"))

    left = m.bind(f).bind(g)
    right = m.bind(lambda x: f(x).bind(g))

    assert left.value.content == right.value.content

# test_laws.py
@pytest.mark.asyncio
async def test_crystallize_idempotence():
    """crystallize(crystallize(s)) ≡ crystallize(s)"""
    soft = SoftSection(name="test", sources=[...])
    context = CompilationContext()

    once = await soft.crystallize(context)
    twice = await SoftSection.from_hard(once.section).crystallize(context)

    assert once.section.content == twice.section.content

def test_rollback_invertibility():
    """rollback(checkpoint(p)) ≡ p"""
    registry = RollbackRegistry(storage=InMemoryCheckpointStorage())
    original_content = "# Original prompt"

    checkpoint_id = registry.checkpoint(
        before_content=original_content,
        after_content="# Modified prompt",
        before_sections=("test",),
        after_sections=("test",),
        reason="test",
    )

    result = registry.rollback(checkpoint_id)
    assert result.restored_content == original_content
```

---

## Part I: Research Synthesis

### Key Academic/Industry Findings

| Approach | Key Insight | Source |
|----------|-------------|--------|
| **DSPy** | Prompts are programs, not strings. Optimize via training data. | [dspy.ai](https://dspy.ai/) |
| **SPEAR** | "Prompts as first-class citizens" with a prompt algebra | [arXiv:2508.05012](https://arxiv.org/html/2508.05012) |
| **Meta-Prompting** | Self-improvement formalized as a **functor** (task → prompt) and **monad** (recursive refinement) | [arXiv:2311.11482](https://arxiv.org/abs/2311.11482) |
| **TextGRAD** | Natural language feedback as "textual gradients" for improvement | [IntuitionLabs](https://intuitionlabs.ai/articles/meta-prompting-llm-self-optimization) |
| **PersonalLLM** | Personalization from heterogeneous preferences across interactions | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/file/a730abbcd6cf4a371ca9545db5922442-Paper-Conference.pdf) |

### The Critical Insight

The Meta-Prompting paper by Zhang, Yuan, and Yao formalizes:
- **Meta Prompting as Functor**: `MP : Category(Tasks) → Category(Prompts)`
- **Recursive Meta Prompting as Monad**: Self-improvement loop with unit/bind operations

This is **exactly** the categorical structure kgents uses for PolyAgents, Operads, and Sheaves. The convergence is not coincidental—it's the universal mathematical substrate.

---

## Part II: Developer Taste Decisions (Binding)

These decisions were made by Kent during the reformation session and are **binding constraints** on implementation:

| Question | Decision | Implication |
|----------|----------|-------------|
| **Transparency** | Show reasoning | All inference must produce reasoning traces. No opaque magic. |
| **Learning sources** | Git + sessions + code patterns | Deep learning from all observable signals. Most powerful, most invasive. |
| **Conflict resolution** | Merge heuristically | No hard precedence. Semantic fusion of file + inferred + policy sources. |
| **Autonomy level** | Auto-change with rollback | System can change freely but maintains full history. Always reversible. |

**The Pattern**: Maximum intelligence with maximum accountability. Confident but auditable.

---

## Part III: The Spectrum of Crystallization

The reformation introduces a **rigidity spectrum** for prompt sections:

```
Level 0          Level 1           Level 2            Level 3             Level 4
Pure Template    File-Dynamic      Policy-Learned     Inference-Augmented Monadic Self-Improvement
(Waves 1-2)      (Original Wave 3) (Reformation)      (Reformation)       (Reformation)
    │                 │                 │                  │                    │
    ▼                 ▼                 ▼                  ▼                    ▼
┌────────┐      ┌────────┐        ┌────────┐         ┌────────┐          ┌────────┐
│IDENTITY│      │ FOREST │        │ HABITS │         │  SOFT  │          │TEXTGRAD│
│= const │      │= f(fs) │        │= f(git)│         │= f(llm)│          │= RMP   │
└────────┘      └────────┘        └────────┘         └────────┘          └────────┘
                                       │                  │                    │
                                       └──────────────────┴────────────────────┘
                                                    THE REFORMATION
```

**Key Concept**: Every section exists somewhere on this spectrum. The `rigidity` field (0.0 to 1.0) indicates where.

---

## Part IV: The Prompt Monad Architecture

### Core Type

```python
@dataclass(frozen=True)
class PromptM(Generic[A]):
    """
    The Prompt Monad: a self-improving prompt computation.

    Monadic Laws (must hold):
    - Left Identity:  unit(x) >>= f ≡ f(x)
    - Right Identity: m >>= unit ≡ m
    - Associativity:  (m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)
    """
    value: A
    reasoning_trace: tuple[str, ...]  # Per transparency decision
    provenance: tuple[Source, ...]    # Where this came from
    checkpoint_id: str | None         # For rollback capability

    @staticmethod
    def unit(value: A) -> "PromptM[A]":
        """Lift a value into the monad."""
        return PromptM(value=value, reasoning_trace=(), provenance=(), checkpoint_id=None)

    def bind(self, f: Callable[[A], "PromptM[B]"]) -> "PromptM[B]":
        """Monadic bind: chain computations, accumulating traces."""
        result = f(self.value)
        return PromptM(
            value=result.value,
            reasoning_trace=self.reasoning_trace + result.reasoning_trace,
            provenance=self.provenance + result.provenance,
            checkpoint_id=result.checkpoint_id,
        )

    def improve(self, feedback: str) -> "PromptM[A]":
        """TextGRAD self-improvement: apply natural language feedback."""
        # Implementation uses LLM to interpret feedback and modify value
        ...
```

### The Polynomial Agent

The prompt system itself is a PolyAgent:

```python
class PromptMode(Enum):
    CRYSTALLIZING = auto()   # Compiling sections from sources
    LEARNING = auto()        # Encoding habits from observations
    IMPROVING = auto()       # TextGRAD self-improvement
    FUSING = auto()          # Merging conflicting sources
    SERVING = auto()         # Providing compiled prompt

PROMPT_MONAD_POLYNOMIAL = PolyAgent(
    positions=frozenset(PromptMode),
    directions=lambda mode: {
        PromptMode.CRYSTALLIZING: frozenset([SoftSectionInput, ContextInput]),
        PromptMode.LEARNING: frozenset([GitHistoryInput, SessionLogInput, CodePatternInput]),
        PromptMode.IMPROVING: frozenset([FeedbackInput, TextGradientInput]),
        PromptMode.FUSING: frozenset([FileSectionInput, InferredSectionInput, PolicyInput]),
        PromptMode.SERVING: frozenset([QueryInput]),
    }[mode],
    transition=prompt_monad_transition,
)
```

### The Operad

```python
PROMPT_OPERAD = Operad(
    operations={
        "crystallize": Operation(arity=1, compose=crystallize_compose),  # Soft → Hard
        "learn": Operation(arity=0, compose=habit_encode),               # Observe → Policy
        "improve": Operation(arity=2, compose=textgrad_compose),         # Prompt × Feedback → Prompt
        "fuse": Operation(arity="*", compose=fusion_compose),            # Sources* → Merged
        "rollback": Operation(arity=1, compose=rollback_compose),        # Checkpoint → Prompt
    },
    laws=[
        # Rollback law: rollback(checkpoint(p)) ≡ p
        OperadLaw("invertibility", lambda p, cp: rollback(checkpoint(p, cp)) == p),
        # Improvement law: improve(p, ∅) ≡ p (empty feedback = identity)
        OperadLaw("identity", lambda p: improve(p, "") == p),
        # Crystallization law: crystallize(crystallize(s)) ≡ crystallize(s) (idempotent)
        OperadLaw("idempotence", lambda s: crystallize(crystallize(s)) == crystallize(s)),
    ]
)
```

---

## Part V: Reformulated Wave Structure

### Wave 3: Soft Section Protocol

**Goal**: Introduce the rigidity spectrum and reasoning traces

```python
@dataclass(frozen=True)
class SoftSection:
    """A section that exists on the rigidity spectrum."""

    name: str
    rigidity: float  # 0.0 = pure LLM inference, 1.0 = pure template
    sources: tuple[SectionSource, ...]  # Ordered by priority
    merge_strategy: MergeStrategy
    reasoning_trace: tuple[str, ...]

    async def crystallize(self, context: CompilationContext) -> Section:
        """
        Crystallize from available sources.

        Algorithm:
        1. Try sources in priority order
        2. For each source that produces content, record it
        3. If multiple sources, apply merge_strategy
        4. Record reasoning trace throughout
        5. Return hard Section with full provenance
        """
        traces = []
        candidates = []

        for source in self.sources:
            traces.append(f"Trying source: {source.name}")
            content = await source.fetch(context)
            if content:
                traces.append(f"  → Got {len(content)} chars from {source.name}")
                candidates.append((source, content))

        if not candidates:
            traces.append("No sources produced content, using LLM inference")
            content = await self._infer_via_llm(context)
            traces.append(f"  → LLM inferred {len(content)} chars")
        elif len(candidates) == 1:
            content = candidates[0][1]
        else:
            traces.append(f"Merging {len(candidates)} sources via {self.merge_strategy}")
            content = await self._merge(candidates, context)

        return Section(
            name=self.name,
            content=content,
            token_cost=estimate_tokens(content),
            required=self.rigidity > 0.5,  # High rigidity = required
            source_paths=tuple(c[0].path for c in candidates if c[0].path),
            reasoning_trace=tuple(traces),
        )
```

**Deliverables**:
- [ ] `SoftSection` dataclass with rigidity spectrum
- [ ] `SectionSource` abstraction (FileSource, GitSource, LLMSource)
- [ ] `MergeStrategy` enum and implementations (FIRST_WINS, CONCAT, SEMANTIC_FUSION)
- [ ] Reasoning trace accumulation throughout
- [ ] Update `ForestSection`, `ContextSection` to use SoftSection
- [ ] New `HabitsSection` (stub, fully implemented in Wave 4)
- [ ] Tests for crystallization with various source combinations

### Wave 4: Habit Encoder + TextGRAD

**Goal**: Learn from developer patterns, enable self-improvement

```python
@dataclass
class HabitEncoder:
    """
    Encode developer habits from observable patterns.

    Sources (per taste decision):
    - Git history: commit patterns, file organization, code style
    - Session logs: Claude Code interaction patterns
    - Code patterns: AST analysis of actual code
    """

    git_analyzer: GitPatternAnalyzer
    session_analyzer: SessionPatternAnalyzer
    code_analyzer: CodePatternAnalyzer

    async def encode(self) -> PolicyVector:
        """
        Produce a policy vector from observed habits.

        The vector weights various prompt decisions:
        - Section priorities (which sections matter most)
        - Style preferences (terse vs verbose, formal vs casual)
        - Focus areas (what topics get attention)
        """
        traces = []

        traces.append("Analyzing git history...")
        git_patterns = await self.git_analyzer.analyze()
        traces.append(f"  → Found {len(git_patterns.patterns)} patterns")

        traces.append("Analyzing session logs...")
        session_patterns = await self.session_analyzer.analyze()
        traces.append(f"  → Found {len(session_patterns.patterns)} patterns")

        traces.append("Analyzing code patterns...")
        code_patterns = await self.code_analyzer.analyze()
        traces.append(f"  → Found {len(code_patterns.patterns)} patterns")

        traces.append("Merging into policy vector...")
        policy = self._merge_patterns(git_patterns, session_patterns, code_patterns)

        return PolicyVector(
            weights=policy,
            reasoning_trace=tuple(traces),
        )


@dataclass
class TextGRADImprover:
    """
    Improve prompts using natural language feedback.

    Based on TextGRAD paper: treat feedback as "textual gradients"
    that guide prompt improvement.
    """

    async def improve(
        self,
        prompt: CompiledPrompt,
        feedback: str,
    ) -> PromptM[CompiledPrompt]:
        """
        Apply textual gradient to improve the prompt.

        Algorithm:
        1. Parse feedback to identify target sections
        2. Generate improvement proposals for each section
        3. Apply improvements, recording reasoning
        4. Checkpoint for rollback capability
        5. Return improved prompt in monad
        """
        traces = [f"Received feedback: {feedback[:100]}..."]

        # Identify which sections the feedback targets
        targeted = await self._identify_targets(prompt, feedback)
        traces.append(f"Feedback targets {len(targeted)} sections: {[s.name for s in targeted]}")

        # Generate improvements
        improvements = []
        for section in targeted:
            traces.append(f"Generating improvement for {section.name}...")
            improved = await self._improve_section(section, feedback)
            improvements.append(improved)
            traces.append(f"  → Improved: {improved.summary}")

        # Apply and checkpoint
        new_prompt = prompt.with_sections(improvements)
        checkpoint_id = await self._checkpoint(prompt, new_prompt, feedback)
        traces.append(f"Checkpointed as {checkpoint_id}")

        return PromptM(
            value=new_prompt,
            reasoning_trace=tuple(traces),
            provenance=(Source.TEXTGRAD,),
            checkpoint_id=checkpoint_id,
        )
```

**Deliverables**:
- [ ] `HabitEncoder` with three analyzers
- [ ] `GitPatternAnalyzer` (commit frequency, file patterns, message style)
- [ ] `SessionPatternAnalyzer` (interaction patterns from logs)
- [ ] `CodePatternAnalyzer` (AST-based style detection)
- [ ] `PolicyVector` dataclass with weights
- [ ] `TextGRADImprover` with feedback parsing
- [ ] Integration with `HabitsSection` from Wave 3
- [ ] Tests for pattern recognition and improvement

### Wave 5: Multi-Source Fusion + Rollback Registry

**Goal**: Heuristic merging with full history

```python
@dataclass
class PromptFusion:
    """
    Fuse multiple sources with heuristic conflict resolution.

    Per taste decision: merge heuristically, not with hard precedence.
    Uses semantic similarity and coherence metrics.
    """

    async def fuse(
        self,
        file_section: Section | None,
        inferred_section: Section | None,
        habit_adjustments: PolicyVector,
    ) -> FusedSection:
        """
        Fuse sources using semantic analysis.

        Algorithm:
        1. Compute semantic similarity between sources
        2. Identify conflicts (contradictory statements)
        3. For each conflict, use habit_adjustments to resolve
        4. Merge non-conflicting content
        5. Return fused section with full reasoning trace
        """
        traces = []

        if file_section and not inferred_section:
            traces.append("Only file source available, using directly")
            return FusedSection(content=file_section.content, traces=traces)

        if inferred_section and not file_section:
            traces.append("Only inferred source available, using directly")
            return FusedSection(content=inferred_section.content, traces=traces)

        # Both sources exist - semantic fusion
        traces.append("Both sources exist, performing semantic fusion...")

        similarity = await self._compute_similarity(file_section, inferred_section)
        traces.append(f"Semantic similarity: {similarity:.2f}")

        if similarity > 0.9:
            traces.append("High similarity, preferring file source")
            return FusedSection(content=file_section.content, traces=traces)

        conflicts = await self._identify_conflicts(file_section, inferred_section)
        traces.append(f"Found {len(conflicts)} conflicts")

        resolutions = []
        for conflict in conflicts:
            resolution = await self._resolve_via_policy(conflict, habit_adjustments)
            traces.append(f"  Conflict '{conflict.summary}' → {resolution.choice}")
            resolutions.append(resolution)

        merged = await self._merge_with_resolutions(
            file_section, inferred_section, resolutions
        )
        traces.append(f"Merged to {len(merged)} chars")

        return FusedSection(content=merged, traces=traces)


@dataclass
class RollbackRegistry:
    """
    Full history with instant rollback capability.

    Per taste decision: auto-change with rollback.
    Every change is recorded. You can always go back.
    """

    storage: Path  # Where checkpoints live

    def checkpoint(
        self,
        before: CompiledPrompt,
        after: CompiledPrompt,
        reason: str,
    ) -> CheckpointId:
        """
        Save state before auto-change.

        Records:
        - Full before/after content
        - Diff
        - Reason for change
        - Timestamp
        - Reasoning traces from both
        """
        checkpoint_id = self._generate_id()

        checkpoint = Checkpoint(
            id=checkpoint_id,
            timestamp=datetime.now(),
            before=before,
            after=after,
            diff=self._compute_diff(before, after),
            reason=reason,
            reasoning_traces=after.reasoning_traces,
        )

        self._save(checkpoint)
        return checkpoint_id

    def rollback(self, checkpoint_id: CheckpointId) -> CompiledPrompt:
        """
        Restore to checkpoint.

        Does NOT delete forward history - you can roll forward again.
        """
        checkpoint = self._load(checkpoint_id)

        # Record the rollback as its own checkpoint
        self.checkpoint(
            before=self._current(),
            after=checkpoint.before,
            reason=f"Rollback to {checkpoint_id}",
        )

        return checkpoint.before

    def history(self, limit: int = 20) -> list[CheckpointSummary]:
        """Show evolution history with diffs and reasoning."""
        ...

    def diff(self, id1: CheckpointId, id2: CheckpointId) -> str:
        """Show diff between any two checkpoints."""
        ...
```

**Deliverables**:
- [ ] `PromptFusion` with semantic similarity
- [ ] Conflict detection and resolution
- [ ] `RollbackRegistry` with checkpoint storage
- [ ] History browsing and diff viewing
- [ ] Forward/backward rollback (time travel)
- [ ] Integration with compilation pipeline
- [ ] Tests for fusion edge cases and rollback laws

### Wave 6: Living CLI

**Goal**: Interactive prompt cultivation

```python
# CLI command structure
PROMPT_COMMANDS = {
    "/prompt": "Show current compiled prompt",
    "/prompt --show-reasoning": "Show with all reasoning traces",
    "/prompt --show-habits": "Show how habits influenced this prompt",
    "/prompt --feedback '<text>'": "Provide feedback for self-improvement",
    "/prompt --history": "Show evolution history",
    "/prompt --rollback <id>": "Rollback to checkpoint",
    "/prompt --preview": "Show what would change if recompiled now",
    "/prompt --auto-improve": "Let system freely improve (with rollback)",
    "/prompt --refine": "Interactive refinement dialogue",
    "/prompt --diff <id1> <id2>": "Diff between checkpoints",
    "/prompt --export": "Export current prompt to file",
}

class PromptCLIHandler:
    """Handler for /prompt commands."""

    async def handle(self, args: list[str]) -> CLIResponse:
        if "--show-reasoning" in args:
            return await self._show_with_reasoning()
        elif "--show-habits" in args:
            return await self._show_habit_influence()
        elif "--feedback" in args:
            feedback = self._extract_feedback(args)
            return await self._apply_feedback(feedback)
        elif "--history" in args:
            return await self._show_history()
        elif "--rollback" in args:
            checkpoint_id = self._extract_id(args)
            return await self._rollback(checkpoint_id)
        elif "--preview" in args:
            return await self._preview_recompilation()
        elif "--auto-improve" in args:
            return await self._auto_improve()
        elif "--refine" in args:
            return await self._interactive_refine()
        else:
            return await self._show_current()

    async def _show_with_reasoning(self) -> CLIResponse:
        """Show prompt with all reasoning traces expanded."""
        prompt = await self.compiler.compile()

        output = []
        for section in prompt.sections:
            output.append(f"## {section.name}")
            output.append(section.content)
            if section.reasoning_trace:
                output.append("")
                output.append("### Reasoning Trace")
                for trace in section.reasoning_trace:
                    output.append(f"  - {trace}")
            output.append("")

        return CLIResponse(content="\n".join(output))

    async def _apply_feedback(self, feedback: str) -> CLIResponse:
        """Apply TextGRAD improvement from feedback."""
        current = await self.compiler.compile()

        improved = await self.improver.improve(current, feedback)

        return CLIResponse(
            content=f"Applied feedback. Checkpoint: {improved.checkpoint_id}\n\n"
                    f"Changes:\n{improved.reasoning_trace[-5:]}",  # Last 5 traces
            checkpoint_id=improved.checkpoint_id,
        )

    async def _interactive_refine(self) -> CLIResponse:
        """Start interactive refinement dialogue."""
        # This would be a multi-turn interaction
        ...
```

**Deliverables**:
- [ ] `/prompt` base command
- [ ] `--show-reasoning` flag
- [ ] `--show-habits` flag
- [ ] `--feedback` with TextGRAD integration
- [ ] `--history` with browsable timeline
- [ ] `--rollback` with confirmation
- [ ] `--preview` showing pending changes
- [ ] `--auto-improve` with safety messaging
- [ ] `--refine` interactive mode
- [ ] Integration tests for all commands

---

## Part VI: Category Laws (Must Hold)

### Monadic Laws

```python
def test_monad_left_identity():
    """unit(x) >>= f ≡ f(x)"""
    x = Section(name="test", content="hello")
    f = lambda s: PromptM.unit(s.with_content(s.content.upper()))

    left = PromptM.unit(x).bind(f)
    right = f(x)

    assert left.value == right.value

def test_monad_right_identity():
    """m >>= unit ≡ m"""
    m = PromptM.unit(Section(name="test", content="hello"))

    result = m.bind(PromptM.unit)

    assert result.value == m.value

def test_monad_associativity():
    """(m >>= f) >>= g ≡ m >>= (λx. f(x) >>= g)"""
    m = PromptM.unit(Section(name="test", content="hello"))
    f = lambda s: PromptM.unit(s.with_content(s.content.upper()))
    g = lambda s: PromptM.unit(s.with_content(s.content + "!"))

    left = m.bind(f).bind(g)
    right = m.bind(lambda x: f(x).bind(g))

    assert left.value == right.value
```

### Operad Laws

```python
def test_rollback_invertibility():
    """rollback(checkpoint(p)) ≡ p"""
    registry = RollbackRegistry()
    prompt = compile_prompt()

    checkpoint_id = registry.checkpoint(prompt, prompt.improved(), "test")
    restored = registry.rollback(checkpoint_id)

    assert restored.content == prompt.content

def test_improvement_identity():
    """improve(p, "") ≡ p"""
    improver = TextGRADImprover()
    prompt = compile_prompt()

    improved = await improver.improve(prompt, "")

    assert improved.value.content == prompt.content

def test_crystallization_idempotence():
    """crystallize(crystallize(s)) ≡ crystallize(s)"""
    soft = SoftSection(name="test", rigidity=0.5, sources=(...))
    context = CompilationContext(...)

    once = await soft.crystallize(context)
    twice = await SoftSection.from_hard(once).crystallize(context)

    assert once.content == twice.content
```

### Existing Laws (Still Hold)

```python
def test_compilation_determinism():
    """Same inputs → same output"""
    # From Wave 1 - must still hold

def test_section_composability():
    """(a >> b) >> c ≡ a >> (b >> c)"""
    # From Wave 1 - must still hold
```

---

## Part VII: File Structure

```
impl/claude/protocols/prompt/
├── __init__.py                    # Package exports (updated)
├── polynomial.py                  # PROMPT_POLYNOMIAL (Wave 1) + PROMPT_MONAD_POLYNOMIAL (Wave 3+)
├── section_base.py                # Section types + Wave 2 utilities
├── compiler.py                    # Compilation pipeline (updated for SoftSection)
├── cli.py                         # CLI commands (Wave 6)
│
├── monad.py                       # NEW: PromptM monad implementation
├── soft_section.py                # NEW: SoftSection and rigidity spectrum
├── sources/                       # NEW: Section sources
│   ├── __init__.py
│   ├── file_source.py             # Read from files
│   ├── git_source.py              # Read from git
│   ├── llm_source.py              # Infer via LLM
│   └── merged_source.py           # Combine multiple sources
│
├── habits/                        # NEW: Habit encoding (Wave 4)
│   ├── __init__.py
│   ├── encoder.py                 # HabitEncoder main class
│   ├── git_analyzer.py            # Git pattern analysis
│   ├── session_analyzer.py        # Session log analysis
│   ├── code_analyzer.py           # AST-based code analysis
│   └── policy.py                  # PolicyVector dataclass
│
├── textgrad/                      # NEW: Self-improvement (Wave 4)
│   ├── __init__.py
│   ├── improver.py                # TextGRADImprover
│   ├── feedback_parser.py         # Parse natural language feedback
│   └── gradient.py                # Textual gradient computation
│
├── fusion/                        # NEW: Multi-source fusion (Wave 5)
│   ├── __init__.py
│   ├── fusioner.py                # PromptFusion main class
│   ├── similarity.py              # Semantic similarity
│   ├── conflict.py                # Conflict detection
│   └── resolution.py              # Policy-based resolution
│
├── rollback/                      # NEW: Rollback registry (Wave 5)
│   ├── __init__.py
│   ├── registry.py                # RollbackRegistry
│   ├── checkpoint.py              # Checkpoint dataclass
│   └── storage.py                 # Checkpoint storage backend
│
├── sections/                      # Section compilers (updated)
│   ├── __init__.py
│   ├── identity.py                # Hardcoded (rigidity=1.0)
│   ├── principles.py              # Dynamic (rigidity=0.8)
│   ├── agentese.py                # Hardcoded (rigidity=1.0)
│   ├── systems.py                 # Dynamic (rigidity=0.7)
│   ├── directories.py             # Hardcoded (rigidity=1.0)
│   ├── skills.py                  # Dynamic (rigidity=0.6)
│   ├── commands.py                # Hardcoded (rigidity=1.0)
│   ├── forest.py                  # NEW: Soft (rigidity=0.4)
│   ├── context.py                 # NEW: Soft (rigidity=0.3)
│   ├── memory.py                  # NEW: Soft (rigidity=0.2)
│   └── habits.py                  # NEW: Soft (rigidity=0.1)
│
└── _tests/
    ├── test_polynomial.py         # 27 tests (Wave 1)
    ├── test_compiler.py           # 14 tests (Wave 1)
    ├── test_dynamic_sections.py   # 26 tests (Wave 2)
    ├── test_monad.py              # NEW: Monadic law tests
    ├── test_soft_section.py       # NEW: Rigidity spectrum tests
    ├── test_habits.py             # NEW: Habit encoding tests
    ├── test_textgrad.py           # NEW: Self-improvement tests
    ├── test_fusion.py             # NEW: Multi-source fusion tests
    ├── test_rollback.py           # NEW: Rollback registry tests
    └── test_cli_prompt.py         # NEW: CLI integration tests
```

---

## Part VIII: Implementation Order

Based on dependency analysis and Kent's indication that safety comes first:

### Phase 1: Foundation (Wave 3a)
1. **Rollback Registry** - Safety net for everything else
2. **SoftSection** - Core abstraction for rigidity spectrum
3. **Sources abstraction** - FileSource, basic LLMSource

### Phase 2: Dynamic Sections (Wave 3b)
4. **ForestSection** with soft fallback
5. **ContextSection** with git integration
6. **Reasoning trace accumulation**

### Phase 3: Learning (Wave 4)
7. **GitPatternAnalyzer**
8. **PolicyVector**
9. **HabitEncoder** (minimal viable version)
10. **HabitsSection**

### Phase 4: Self-Improvement (Wave 4b)
11. **TextGRADImprover** (basic version)
12. **Feedback parsing**
13. Integration with compilation

### Phase 5: Fusion (Wave 5)
14. **Semantic similarity**
15. **Conflict detection**
16. **PromptFusion**

### Phase 6: CLI (Wave 6)
17. `/prompt` base command
18. `--show-reasoning` and `--show-habits`
19. `--feedback` with TextGRAD
20. `--rollback` and `--history`
21. `--auto-improve` and `--refine`

---

## Part IX: Dogfooding Checkpoints

After each phase:

```bash
# Run tests
cd impl/claude
uv run python -m pytest protocols/prompt/_tests/ -v

# Compile with new features
uv run python -m protocols.prompt.cli compile --output /tmp/compiled.md

# Show reasoning (when available)
uv run python -m protocols.prompt.cli compile --show-reasoning

# Compare to hand-written
uv run python -m protocols.prompt.cli compare
```

### Representative Tasks

| Phase | Test Task | Success Criterion |
|-------|-----------|-------------------|
| 1 | Rollback after bad edit | Restore works, forward history preserved |
| 2 | Work on forest focus | Forest section shows actual plan state |
| 3 | Compare to git style | Habits section reflects actual patterns |
| 4 | Provide feedback | TextGRAD improves targeted section |
| 5 | Conflicting sources | Fusion produces coherent result |
| 6 | Full CLI workflow | All commands work end-to-end |

---

## Part X: Anti-Patterns to Avoid

1. **Over-engineering the monad**: Start simple, add complexity as needed
2. **Opaque magic**: Always show reasoning traces (per taste decision)
3. **No rollback on auto-changes**: Every change must be reversible
4. **Hard precedence in fusion**: Use heuristics, not if/else (per taste decision)
5. **Ignoring existing code**: Wave 1-2 code exists and works—extend, don't rewrite
6. **Testing only happy paths**: Test edge cases, especially in fusion and rollback
7. **Forgetting the laws**: Monadic and operad laws must be verified

---

## Part XI: Session Startup

When starting a fresh session with this prompt:

```
Reformation continuation loaded.

Current state:
- Wave: 3+ (Reformulated)
- Phase: Implementation Phase 1 (Foundation Fixes)
- Last gap analysis: 2025-12-16
- Taste decisions: Show reasoning, Git+sessions+code, Merge heuristically, Auto-change+rollback
- Architecture: Prompt Monad with rigidity spectrum

Priority queue (from gap analysis):
- P0: Wire rollback to CLI (safety net) ⏳
- P1: Fix async architecture ⏳
- P2: Implement PromptM monad ⏳
- P3: Add law validation tests ⏳

Key files to read:
- plans/evergreen-prompt-implementation.md (updated plan with gaps)
- spec/protocols/evergreen-prompt-system.md Part I-C (gap analysis)
- impl/claude/protocols/prompt/ (existing code)

Starting with: P0 - Wire rollback to CLI
```

---

## Part XII: Open Questions (To Resolve During Implementation)

1. **Session log storage**: Where are Claude Code session logs stored? Need to find for `SessionPatternAnalyzer`.

2. **Semantic similarity backend**: Use embeddings? Local model? LLM-as-judge? Cost/latency tradeoffs.

3. **Checkpoint storage format**: JSON? SQLite? Git-backed? Need persistence story.

4. **LLM source caching**: How to cache inferred sections to avoid repeated calls?

5. **Spec update timing**: Update `evergreen-prompt-system.md` now or after implementation proves out?

---

*"The prompt that learns itself is the prompt that serves itself. The monad that improves itself is the monad that transcends itself. Wave 3+ is not compilation—it is cultivation."*

*Reformation Session: 2025-12-16*
*Version: 0.4.0-reformation*
