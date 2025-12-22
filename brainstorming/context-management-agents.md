# Context Management for Agents: Lenses, Portals, and Harnesses

> *"Every text edit operation is writing, compiling, and executing a program."*
>
> The agent doesn't see files. The agent sees **coherent slices** through a lens.

---

## The Problem

Raw file operations are messy:
- Files can be 10M lines
- Edits can be anywhere
- Context windows are finite
- Agents can loop infinitely
- Evidence is scattered across a database

**The goal**: Create a **morphism** that transforms:
```
RawFileOps → CoherentAgentView
```

Such that the agent experiences:
- Finite, relevant context
- Sane file names and boundaries
- Guaranteed termination
- Evidence scoped to the task

---

## Part 1: The Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AGENT PERCEPTION                                   │
│                                                                             │
│   The agent sees: coherent documents, sane names, bounded context          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ▲                                              │
│                              │ PORTAL                                       │
│                              │ (projection into harness)                    │
│                              │                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                            LENS                                             │
│                                                                             │
│   Bidirectional transformation: focus ↔ whole                               │
│   - get: Whole → Part (extract relevant slice)                              │
│   - put: Part × Whole → Whole (update whole from slice)                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                              ▲                                              │
│                              │ HARNESS                                      │
│                              │ (guarantees + state machine)                 │
│                              │                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                          RAW REALITY                                        │
│                                                                             │
│   The world: 10M line files, scattered evidence, infinite loops possible   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.1 Harness (Guarantees)

The harness provides **computational guarantees**:

```python
@dataclass
class AgentHarness:
    """Wraps raw reality with safety guarantees."""

    # Termination guarantees
    max_steps: int = 1000              # Bounded iteration
    max_depth: int = 10                # Bounded recursion
    step_budget: StepBudget            # ASHC step allocation

    # Progress guarantees
    monotonic_evidence: bool = True    # Evidence can only grow
    no_undo_promoted: bool = True      # Can't undo promoted decisions

    # Loop detection
    state_hash_history: set[int]       # Detect exact state repetition
    semantic_similarity_threshold: float = 0.95  # Detect semantic loops

    # Resource limits
    token_budget: int                  # Context window budget
    time_budget_ms: int                # Wall clock budget

    def check_loop(self, current_state: AgentState) -> LoopStatus:
        """Detect if we're in a trivially bad loop."""
        state_hash = hash(current_state)

        # Exact repetition
        if state_hash in self.state_hash_history:
            return LoopStatus.EXACT_LOOP

        # Semantic similarity check
        for prev_hash, prev_embedding in self.semantic_history:
            if cosine_sim(current_state.embedding, prev_embedding) > self.semantic_similarity_threshold:
                return LoopStatus.SEMANTIC_LOOP

        self.state_hash_history.add(state_hash)
        return LoopStatus.OK
```

### 1.2 Lens (Bidirectional Transformation)

From optics theory — a lens focuses on a part while maintaining the whole:

```python
@dataclass
class FileLens(Generic[Whole, Part]):
    """
    Bidirectional transformation between whole file and visible slice.

    Optics law: put(get(whole), whole) ≡ whole  (round-trip identity)
    """

    # Forward: extract slice from whole
    get: Callable[[Whole], Part]

    # Backward: update whole from modified slice
    put: Callable[[Part, Whole], Whole]

    # Metadata for agent
    slice_name: str           # Human-readable name for the slice
    slice_context: str        # Why this slice matters
    line_range: tuple[int, int]  # Original line numbers


class VirtualizedFileLens(FileLens[str, str]):
    """
    Virtualize a 10M line file into coherent 100-line chunks.

    The agent sees: "auth_middleware_core.py:validate_token"
    The reality is: line 847234-847334 of monolith.py
    """

    def __init__(self, source_path: str, focus: FocusSpec):
        self.source_path = source_path
        self.focus = focus

        # Compute the slice
        self.start_line, self.end_line = self._compute_range(focus)

        # Generate sane name
        self.slice_name = self._generate_name(focus)

    def get(self, whole: str) -> str:
        """Extract the focused slice."""
        lines = whole.split('\n')
        return '\n'.join(lines[self.start_line:self.end_line])

    def put(self, part: str, whole: str) -> str:
        """Update the whole with modified slice."""
        lines = whole.split('\n')
        new_lines = part.split('\n')
        lines[self.start_line:self.end_line] = new_lines
        return '\n'.join(lines)

    def _generate_name(self, focus: FocusSpec) -> str:
        """Generate a sane, context-giving name."""
        # Instead of: "monolith.py:847234-847334"
        # Generate:   "auth_middleware_core.py:validate_token"

        function_name = focus.function or "unknown"
        module_hint = focus.semantic_module or "chunk"
        return f"{module_hint}.py:{function_name}"

    def _compute_range(self, focus: FocusSpec) -> tuple[int, int]:
        """Compute line range with context padding."""
        # Add context lines before/after for coherence
        context_padding = 10
        return (
            max(0, focus.start_line - context_padding),
            focus.end_line + context_padding
        )
```

### 1.3 Portal (Projection into Agent View)

The portal projects the lens into the agent's perception:

```python
@dataclass
class AgentPortal:
    """
    Projects reality through lenses into agent-perceivable documents.

    The agent sees a coherent "file" that is actually a lens composition.
    """

    lenses: list[FileLens]            # Active lenses
    evidence_scope: EvidenceScope     # What evidence is accessible
    thinking_trace: ThinkingTrace     # Agent's reasoning so far

    def project(self) -> AgentContext:
        """Create the context the agent will perceive."""
        documents = []

        for lens in self.lenses:
            doc = VirtualDocument(
                name=lens.slice_name,
                content=lens.get(self._read_whole(lens)),
                line_range=lens.line_range,
                affordances=self._compute_affordances(lens),
            )
            documents.append(doc)

        return AgentContext(
            documents=documents,
            evidence=self.evidence_scope.accessible(),
            thinking=self.thinking_trace.recent(limit=10),
            budget_remaining=self.harness.remaining_budget(),
        )

    def apply_edit(self, doc_name: str, edit: Edit) -> ApplyResult:
        """Apply an agent's edit back through the lens."""
        lens = self._find_lens(doc_name)

        # Transform edit coordinates (agent space → real space)
        real_edit = lens.transform_edit(edit)

        # Apply to whole
        whole = self._read_whole(lens)
        new_whole = lens.put(edit.apply(lens.get(whole)), whole)

        # Write back
        self._write_whole(lens, new_whole)

        return ApplyResult(
            success=True,
            real_lines_affected=real_edit.line_range,
            lens_recalculation_needed=self._check_lens_stale(lens, new_whole),
        )
```

---

## Part 2: Agent Thinking as Tree Structure

### 2.1 Thinking Nodes

Agent thinking becomes part of the project tree:

```
~/.kgents/project/
├── source/
│   └── (actual code)
├── evidence/
│   └── (ASHC evidence database)
├── decisions/
│   └── (decision tree folders)
└── thinking/                          ← NEW: Agent reasoning
    ├── session_2024-12-21_14:30/
    │   ├── _trace.md                  # Full reasoning trace
    │   ├── step_001_understand.md     # NPHASE: UNDERSTAND
    │   ├── step_002_hypothesize.md    # Hypothesis formation
    │   ├── step_003_test.md           # NPHASE: ACT (test hypothesis)
    │   ├── step_004_reflect.md        # NPHASE: REFLECT
    │   └── _outcome.md                # Final outcome
    └── patterns/
        ├── successful_refactor.pattern  # Learned pattern
        └── failed_optimization.pattern  # Anti-pattern
```

### 2.2 Thinking State Machine

Each thinking step has a state machine:

```python
class ThinkingStepMachine(PolyAgent[ThinkingState, ThinkingInput, ThinkingOutput]):
    """
    State machine for a single thinking step.

    States: IDLE → HYPOTHESIZING → TESTING → CONCLUDING → COMMITTED

    Transitions are guarded by ASHC evidence requirements.
    """

    STATES = {
        "IDLE": ThinkingState(can_hypothesize=True, can_test=False, can_conclude=False),
        "HYPOTHESIZING": ThinkingState(can_hypothesize=True, can_test=True, can_conclude=False),
        "TESTING": ThinkingState(can_hypothesize=False, can_test=True, can_conclude=True),
        "CONCLUDING": ThinkingState(can_hypothesize=False, can_test=False, can_conclude=True),
        "COMMITTED": ThinkingState(can_hypothesize=False, can_test=False, can_conclude=False),
    }

    def transition(self, input: ThinkingInput) -> tuple[ThinkingState, ThinkingOutput]:
        match (self.state, input):
            case ("IDLE", Hypothesize(h)):
                # Must provide initial evidence
                if not self.ashc.has_minimal_evidence(h):
                    return (self.state, Rejected("Need evidence for hypothesis"))
                return ("HYPOTHESIZING", HypothesisFormed(h))

            case ("HYPOTHESIZING", Test(t)):
                # Must have testable hypothesis
                if not self.ashc.is_testable(self.current_hypothesis):
                    return (self.state, Rejected("Hypothesis not testable"))
                return ("TESTING", TestStarted(t))

            case ("TESTING", Conclude(c)):
                # Must have sufficient evidence
                if not self.ashc.has_sufficient_evidence(c):
                    return (self.state, Rejected("Insufficient evidence"))
                return ("CONCLUDING", ConclusionFormed(c))

            case ("CONCLUDING", Commit()):
                # Irreversible transition
                self._persist_to_tree()
                return ("COMMITTED", Committed())

            case _:
                return (self.state, InvalidTransition())
```

### 2.3 Loop Prevention via State Hashing

```python
class LoopDetector:
    """
    Detect trivially bad loops in agent reasoning.

    Three types of loops:
    1. EXACT: Same state hash (including thinking content)
    2. SEMANTIC: High similarity but not identical
    3. STRUCTURAL: Same pattern of transitions
    """

    def __init__(self, max_history: int = 100):
        self.state_hashes: deque[int] = deque(maxlen=max_history)
        self.embeddings: deque[np.ndarray] = deque(maxlen=max_history)
        self.transition_patterns: deque[str] = deque(maxlen=max_history)

    def check(self, state: AgentState, transition: str) -> LoopStatus:
        # 1. Exact loop
        state_hash = self._compute_hash(state)
        if state_hash in self.state_hashes:
            return LoopStatus.EXACT_LOOP

        # 2. Semantic loop
        embedding = self._embed(state)
        for prev_emb in self.embeddings:
            if cosine_similarity(embedding, prev_emb) > 0.95:
                return LoopStatus.SEMANTIC_LOOP

        # 3. Structural loop (repeated transition pattern)
        self.transition_patterns.append(transition)
        pattern = ''.join(list(self.transition_patterns)[-5:])
        if self._is_repeating_pattern(pattern):
            return LoopStatus.STRUCTURAL_LOOP

        # Record for future checks
        self.state_hashes.append(state_hash)
        self.embeddings.append(embedding)

        return LoopStatus.OK

    def _is_repeating_pattern(self, pattern: str) -> bool:
        """Detect if last N transitions form a repeating pattern."""
        # e.g., "ABABAB" or "ABCABC"
        for period in range(1, len(pattern) // 2 + 1):
            if pattern == (pattern[:period] * (len(pattern) // period + 1))[:len(pattern)]:
                return True
        return False
```

---

## Part 3: ASHC Integration (Evidence & Commitment Protocol)

### 3.1 Evidence as Files

Evidence becomes part of the file tree:

```
~/.kgents/evidence/
├── _schema.ashc                       # ASHC schema definition
├── by_claim/
│   ├── claim_001.evidence
│   ├── claim_002.evidence
│   └── claim_003.evidence
├── by_source/
│   ├── test_results/
│   │   ├── test_run_001.evidence
│   │   └── test_run_002.evidence
│   ├── user_feedback/
│   │   └── feedback_001.evidence
│   └── static_analysis/
│       └── lint_001.evidence
└── by_strength/
    ├── strong/                        # High confidence
    ├── moderate/                      # Medium confidence
    └── weak/                          # Low confidence / tentative
```

### 3.2 Evidence Scoping via Lens

Only relevant evidence is visible through the portal:

```python
class EvidenceScope:
    """
    Scopes evidence database to what's relevant for current task.

    The agent can't see all evidence — only what's "accessible"
    through the current lens composition.
    """

    def __init__(self, task: Task, lenses: list[FileLens]):
        self.task = task
        self.lenses = lenses
        self._build_accessibility_graph()

    def _build_accessibility_graph(self):
        """
        Build graph of which evidence is accessible.

        Evidence is accessible if:
        1. It's about a file in the current lens set
        2. It's about a claim related to the current task
        3. It's a dependency of accessible evidence
        """
        self.accessible_ids: set[str] = set()

        # Seed: evidence about files in lens
        for lens in self.lenses:
            self.accessible_ids.update(
                self._evidence_about_file(lens.source_path)
            )

        # Seed: evidence about task claims
        self.accessible_ids.update(
            self._evidence_about_claims(self.task.claims)
        )

        # Closure: add dependencies
        self._compute_transitive_closure()

    def accessible(self) -> list[Evidence]:
        """Return only accessible evidence."""
        return [
            self._load_evidence(eid)
            for eid in self.accessible_ids
        ]

    def accessible_summary(self) -> str:
        """Return a summary for agent context."""
        evidence = self.accessible()
        return f"""
## Available Evidence ({len(evidence)} items)

### By Strength
- Strong: {len([e for e in evidence if e.strength == 'strong'])}
- Moderate: {len([e for e in evidence if e.strength == 'moderate'])}
- Weak: {len([e for e in evidence if e.strength == 'weak'])}

### Recent
{self._format_recent(evidence[:5])}
"""
```

### 3.3 ASHC Commitment Protocol

Before an agent can commit a conclusion:

```python
class ASHCCommitment:
    """
    Argument-Structured Hierarchical Commitment protocol.

    An agent cannot commit a claim without:
    1. Sufficient evidence (quantity threshold)
    2. Strong evidence (quality threshold)
    3. No unaddressed counterevidence
    4. Hierarchical approval (if claim exceeds scope)
    """

    def can_commit(self, claim: Claim, agent: Agent) -> CommitmentResult:
        # 1. Quantity check
        evidence = self.evidence_scope.for_claim(claim)
        if len(evidence) < self.min_evidence_count:
            return CommitmentResult.INSUFFICIENT_QUANTITY

        # 2. Quality check
        strong_count = len([e for e in evidence if e.strength == 'strong'])
        if strong_count < self.min_strong_count:
            return CommitmentResult.INSUFFICIENT_QUALITY

        # 3. Counterevidence check
        counter = self.evidence_scope.against_claim(claim)
        unaddressed = [c for c in counter if not c.addressed]
        if unaddressed:
            return CommitmentResult.UNADDRESSED_COUNTEREVIDENCE

        # 4. Hierarchical scope check
        if claim.scope > agent.authority_level:
            return CommitmentResult.NEEDS_ESCALATION

        return CommitmentResult.CAN_COMMIT

    def commit(self, claim: Claim, agent: Agent) -> CommitResult:
        """Commit a claim — this is irreversible."""
        result = self.can_commit(claim, agent)
        if result != CommitmentResult.CAN_COMMIT:
            raise CommitmentError(result)

        # Write to evidence tree
        self._persist_commitment(claim, agent)

        # Update agent authority (successful commits build trust)
        agent.authority_level += self._trust_increment(claim)

        return CommitResult.COMMITTED
```

---

## Part 4: Token State Machines (Every Edit is a Program)

### 4.1 The Insight

> *"Every text edit operation, to some reasonable level of comprehensibility,
> is writing, compiling, and executing a program."*

Each token type has its own **state machine encoding**:

```
Token Type        State Machine               Compilation Target
─────────────────────────────────────────────────────────────────
AGENTESE_PORTAL   NavigationMachine           → AGENTESE invocation
TASK_TOGGLE       CheckboxMachine             → D-gent state update
CODE_REGION       ExecutionMachine            → Runtime execution
ANNOTATION        AnnotationMachine           → Evidence creation
OPERAD_LINK       CompositionMachine          → Operad composition
DIFF_REGION       MergeMachine                → Git-like merge
SANDBOX_BOUNDARY  SandboxMachine              → WASM isolation
```

### 4.2 Token State Machine Interface

```python
class TokenStateMachine(Protocol, Generic[S, I, O]):
    """
    Every token type implements this protocol.

    The state machine defines:
    - What states the token can be in
    - What inputs transition between states
    - What outputs are produced
    - How to compile to executable form
    """

    @property
    def states(self) -> set[S]:
        """All possible states."""
        ...

    @property
    def initial_state(self) -> S:
        """Starting state."""
        ...

    @property
    def accepting_states(self) -> set[S]:
        """States where the token is "complete"."""
        ...

    def transition(self, state: S, input: I) -> tuple[S, O]:
        """Transition function: (state, input) → (new_state, output)."""
        ...

    def compile(self) -> CompiledProgram:
        """Compile the current state to an executable program."""
        ...

    def execute(self) -> ExecutionResult:
        """Execute the compiled program."""
        return self.compile().run()
```

### 4.3 Example: TASK_TOGGLE State Machine

```python
class TaskToggleMachine(TokenStateMachine[TaskState, TaskInput, TaskOutput]):
    """
    State machine for a task checkbox token.

    States: UNCHECKED ⇄ CHECKED → ARCHIVED

    Edit operations:
    - Toggle: UNCHECKED ↔ CHECKED
    - Archive: CHECKED → ARCHIVED
    - Annotate: (any state) → same state + annotation
    """

    STATES = {"UNCHECKED", "CHECKED", "ARCHIVED"}

    def __init__(self, token: MeaningToken):
        self.token = token
        self.state = "CHECKED" if token.token_data.get("checked") else "UNCHECKED"
        self.annotations: list[Annotation] = []

    def transition(self, state: str, input: TaskInput) -> tuple[str, TaskOutput]:
        match (state, input):
            case ("UNCHECKED", Toggle()):
                return ("CHECKED", StateChanged(new_state="CHECKED"))

            case ("CHECKED", Toggle()):
                return ("UNCHECKED", StateChanged(new_state="UNCHECKED"))

            case ("CHECKED", Archive()):
                return ("ARCHIVED", Archived())

            case (_, Annotate(text)):
                self.annotations.append(Annotation(text))
                return (state, AnnotationAdded(text))

            case ("ARCHIVED", _):
                return (state, Rejected("Cannot modify archived task"))

            case _:
                return (state, InvalidInput())

    def compile(self) -> CompiledProgram:
        """
        Compile to D-gent update program.

        The "program" is a state update instruction for D-gent.
        """
        return DGentUpdateProgram(
            path=self.token.source_path,
            position=self.token.source_position,
            new_state={
                "checked": self.state == "CHECKED",
                "archived": self.state == "ARCHIVED",
                "annotations": [a.to_dict() for a in self.annotations],
            },
            evidence=self._generate_evidence(),
        )

    def _generate_evidence(self) -> Evidence:
        """Generate ASHC evidence for this state change."""
        return Evidence(
            claim=f"Task '{self.token.token_data['description']}' is {self.state}",
            source="task_toggle_machine",
            strength="strong",  # Direct state observation
            timestamp=datetime.now(),
        )
```

### 4.4 Example: OPERAD_LINK State Machine

```python
class OperadLinkMachine(TokenStateMachine[LinkState, LinkInput, LinkOutput]):
    """
    State machine for cross-operad links.

    States: PROPOSED → VALIDATED → COMPOSED → EXECUTED

    This is more complex — it's a mini-compiler for operad composition.
    """

    STATES = {"PROPOSED", "VALIDATED", "COMPOSED", "EXECUTED", "FAILED"}

    def __init__(self, source_op: str, target_op: str, link_type: str):
        self.source_op = source_op
        self.target_op = target_op
        self.link_type = link_type
        self.state = "PROPOSED"
        self.adapter: Adapter | None = None
        self.composition: PolyAgent | None = None

    def transition(self, state: str, input: LinkInput) -> tuple[str, LinkOutput]:
        match (state, input):
            case ("PROPOSED", Validate()):
                # Type-check the link
                result = self._typecheck()
                if result.compatible:
                    return ("VALIDATED", TypeCheckPassed())
                elif result.adapter_available:
                    self.adapter = result.adapter
                    return ("VALIDATED", TypeCheckPassed(adapter=self.adapter))
                else:
                    return ("FAILED", TypeCheckFailed(result.errors))

            case ("VALIDATED", Compose()):
                # Build the composed agent
                self.composition = self._build_composition()
                return ("COMPOSED", CompositionBuilt(self.composition))

            case ("COMPOSED", Execute(input_data)):
                # Run the composition
                result = await self.composition.invoke(input_data)
                return ("EXECUTED", ExecutionResult(result))

            case _:
                return (state, InvalidInput())

    def compile(self) -> CompiledProgram:
        """
        Compile to an operad composition program.

        This generates actual Python code that composes the operads.
        """
        return OperadCompositionProgram(
            source_op=self.source_op,
            target_op=self.target_op,
            adapter=self.adapter,
            composition_code=self._generate_composition_code(),
        )

    def _generate_composition_code(self) -> str:
        """Generate the composition as executable Python."""
        if self.adapter:
            return f"""
# Cross-operad composition: {self.source_op} >> {self.target_op}
# Adapter: {self.adapter.name}

from agents.poly import sequential
from {self.source_op.module} import {self.source_op.operation}
from {self.target_op.module} import {self.target_op.operation}
from functors import {self.adapter.name}

composition = sequential(
    {self.source_op.operation},
    {self.adapter.name}.transform,
    {self.target_op.operation},
)

# Execute
result = await composition.invoke(input)
"""
        else:
            return f"""
# Direct composition: {self.source_op} >> {self.target_op}

from agents.poly import sequential
from {self.source_op.module} import {self.source_op.operation}
from {self.target_op.module} import {self.target_op.operation}

composition = sequential(
    {self.source_op.operation},
    {self.target_op.operation},
)

result = await composition.invoke(input)
"""
```

---

## Part 5: The Virtualization Morphism

### 5.1 The Core Morphism

```
Φ: RawFileOps × Context → AgentCoherentView

Where:
- RawFileOps = { read, write, delete, ... } on real files
- Context = (Task, Evidence, Thinking, Budget)
- AgentCoherentView = what the agent actually perceives
```

Formally:

```python
class VirtualizationMorphism:
    """
    The morphism that transforms raw file operations into coherent agent views.

    Satisfies:
    1. Lens law: round-trip identity
    2. Coherence: agent view is always consistent
    3. Termination: operations are bounded
    4. Evidence preservation: all changes leave evidence
    """

    def __init__(self, harness: AgentHarness, ashc: ASHCCommitment):
        self.harness = harness
        self.ashc = ashc

    def forward(self, raw_ops: list[RawFileOp], context: Context) -> AgentCoherentView:
        """
        Transform raw operations into agent-perceivable view.

        This is the "get" direction of the lens.
        """
        # 1. Compute relevant lenses from context
        lenses = self._compute_lenses(context)

        # 2. Apply lenses to extract slices
        documents = [
            VirtualDocument(
                name=lens.slice_name,
                content=lens.get(self._read_raw(lens.source_path)),
                metadata=lens.metadata,
            )
            for lens in lenses
        ]

        # 3. Scope evidence
        evidence_scope = EvidenceScope(context.task, lenses)

        # 4. Build agent view
        return AgentCoherentView(
            documents=documents,
            evidence=evidence_scope.accessible(),
            thinking=context.thinking.recent(),
            budget=self.harness.remaining_budget(),
            affordances=self._compute_affordances(documents),
        )

    def backward(self, agent_edits: list[AgentEdit], context: Context) -> list[RawFileOp]:
        """
        Transform agent edits back into raw file operations.

        This is the "put" direction of the lens.
        """
        raw_ops = []

        for edit in agent_edits:
            # 1. Find the lens for this document
            lens = self._find_lens(edit.document_name, context)

            # 2. Transform edit coordinates
            real_edit = lens.transform_edit(edit)

            # 3. Apply to get new whole
            whole = self._read_raw(lens.source_path)
            part = lens.get(whole)
            new_part = edit.apply(part)
            new_whole = lens.put(new_part, whole)

            # 4. Create raw operation
            raw_ops.append(RawFileOp(
                type="write",
                path=lens.source_path,
                content=new_whole,
                evidence=self._generate_evidence(edit, lens),
            ))

            # 5. Check ASHC commitment if needed
            if edit.is_commitment:
                self.ashc.commit(edit.to_claim(), context.agent)

        return raw_ops

    def _compute_lenses(self, context: Context) -> list[FileLens]:
        """
        Compute which lenses to use for this context.

        Strategy:
        1. Start with files mentioned in task
        2. Add files referenced by evidence
        3. Add files in thinking trace
        4. Limit by token budget
        """
        candidates = []

        # Task-mentioned files
        for file_ref in context.task.file_references:
            candidates.extend(self._lenses_for_file(file_ref))

        # Evidence-referenced files
        for evidence in context.evidence:
            if evidence.file_path:
                candidates.extend(self._lenses_for_file(evidence.file_path))

        # Thinking-referenced files
        for thought in context.thinking.recent():
            for file_ref in thought.file_references:
                candidates.extend(self._lenses_for_file(file_ref))

        # Budget-constrain
        return self._select_within_budget(candidates, context.budget)

    def _lenses_for_file(self, file_path: str) -> list[FileLens]:
        """
        Create lenses for a file.

        For large files, create multiple lenses (one per semantic unit).
        For small files, create one lens for the whole file.
        """
        content = self._read_raw(file_path)
        lines = content.split('\n')

        if len(lines) < 200:
            # Small file: one lens
            return [FileLens(
                source_path=file_path,
                get=lambda w: w,
                put=lambda p, w: p,
                slice_name=os.path.basename(file_path),
            )]

        # Large file: multiple lenses by semantic unit
        units = self._parse_semantic_units(content)
        return [
            VirtualizedFileLens(
                source_path=file_path,
                focus=FocusSpec(
                    start_line=unit.start,
                    end_line=unit.end,
                    function=unit.name,
                    semantic_module=unit.module_hint,
                ),
            )
            for unit in units
        ]
```

### 5.2 The Coherence Guarantee

```python
class CoherenceGuarantee:
    """
    Ensures the agent always sees a coherent view.

    Coherence invariants:
    1. No overlapping lenses (each line appears in at most one lens)
    2. No stale lenses (lens reflects current file state)
    3. No orphan evidence (all evidence has accessible source)
    4. No circular thinking (thinking trace is acyclic)
    """

    def verify(self, view: AgentCoherentView) -> list[CoherenceViolation]:
        violations = []

        # 1. Check lens overlap
        line_ownership: dict[tuple[str, int], str] = {}
        for doc in view.documents:
            for line in range(doc.metadata.start_line, doc.metadata.end_line):
                key = (doc.metadata.source_path, line)
                if key in line_ownership:
                    violations.append(OverlappingLenses(
                        line=key,
                        lens1=line_ownership[key],
                        lens2=doc.name,
                    ))
                line_ownership[key] = doc.name

        # 2. Check lens staleness
        for doc in view.documents:
            current_hash = hash(self._read_raw(doc.metadata.source_path))
            if current_hash != doc.metadata.source_hash:
                violations.append(StaleLens(doc.name))

        # 3. Check evidence orphans
        accessible_paths = {doc.metadata.source_path for doc in view.documents}
        for evidence in view.evidence:
            if evidence.file_path and evidence.file_path not in accessible_paths:
                violations.append(OrphanEvidence(evidence.id))

        # 4. Check thinking circularity
        if self._has_cycle(view.thinking):
            violations.append(CircularThinking())

        return violations
```

---

## Part 6: Putting It All Together

### 6.1 The Complete Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. TASK ARRIVES                                                             │
│    "Fix the authentication bug in the middleware"                           │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. HARNESS INITIALIZES                                                      │
│    - Set step budget (1000 steps max)                                       │
│    - Set token budget (100k tokens)                                         │
│    - Initialize loop detector                                               │
│    - Load ASHC schema                                                       │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. LENS COMPUTATION                                                         │
│    - Identify relevant files (auth_middleware.py, tests/test_auth.py)       │
│    - For large files, create semantic unit lenses                           │
│    - Generate sane names: "auth_core.py:validate_token"                     │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. EVIDENCE SCOPING                                                         │
│    - Find evidence about auth middleware                                    │
│    - Find evidence about reported bug                                       │
│    - Compute transitive closure                                             │
│    - Filter to accessible evidence only                                     │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. PORTAL PROJECTION                                                        │
│    Agent sees:                                                              │
│    - auth_core.py:validate_token (100 lines)                                │
│    - auth_core.py:refresh_session (80 lines)                                │
│    - test_auth.py:test_validate (50 lines)                                  │
│    - 3 evidence items (2 strong, 1 moderate)                                │
│    - Budget: 800 steps remaining                                            │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. AGENT THINKS (State Machine)                                             │
│    Step 1: IDLE → HYPOTHESIZING                                             │
│            Hypothesis: "Token expiry check is off by one"                   │
│            Evidence required: ✓ (test failure, code inspection)             │
│                                                                             │
│    Step 2: HYPOTHESIZING → TESTING                                          │
│            Test: Add logging, run tests                                     │
│            Loop check: ✓ OK (no previous state match)                       │
│                                                                             │
│    Step 3: TESTING → CONCLUDING                                             │
│            Conclusion: "Fix expiry check from < to <="                      │
│            Evidence: strong (test now passes)                               │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. AGENT EDITS (Token State Machines)                                       │
│                                                                             │
│    Edit 1: CODE_REGION machine                                              │
│            State: UNMODIFIED → MODIFIED → COMPILED → TESTED                 │
│            Compile: Generate diff patch                                     │
│            Execute: Apply patch to lens                                     │
│                                                                             │
│    Edit 2: TASK_TOGGLE machine                                              │
│            State: UNCHECKED → CHECKED                                       │
│            Compile: D-gent state update                                     │
│            Execute: Mark task complete                                      │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 8. BACKWARD MORPHISM                                                        │
│    - Transform agent edits through lenses                                   │
│    - Apply to real files                                                    │
│    - Generate evidence (test passed, code changed)                          │
│    - ASHC commit (claim: "Bug is fixed", evidence: test passes)             │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 9. THINKING PERSISTED                                                       │
│    Written to: thinking/session_2024-12-21_14:30/                           │
│    - step_001_hypothesize.md                                                │
│    - step_002_test.md                                                       │
│    - step_003_conclude.md                                                   │
│    - _outcome.md                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 The Key Guarantees

| Guarantee | Mechanism | Verification |
|-----------|-----------|--------------|
| **Termination** | Step budget, loop detection | Harness checks every step |
| **Coherence** | Lens composition, coherence verifier | Pre/post condition checks |
| **Evidence preservation** | Token state machines generate evidence | ASHC commit protocol |
| **No bad loops** | State hash + semantic similarity | Loop detector |
| **Scoped perception** | Evidence scope, lens selection | Portal projection |
| **Edit safety** | Lens round-trip law | Lens.put(Lens.get(w), w) ≡ w |

---

## Part 7: The Token Compilation Target

### 7.1 Every Edit Compiles To...

```
Token Type        Compilation Target          Runtime
─────────────────────────────────────────────────────────────────
AGENTESE_PORTAL   AGENTESE invocation         logos.invoke(path)
TASK_TOGGLE       D-gent state delta          d_gent.update(path, delta)
CODE_REGION       Diff patch + test           git apply + pytest
ANNOTATION        Evidence record             ashc.add_evidence(e)
OPERAD_LINK       Composition expression      poly.sequential(a, b)
DIFF_REGION       Merge operation             git merge --no-commit
SANDBOX_BOUNDARY  WASM instantiation          wasm.instantiate(module)
```

### 7.2 The Compilation Pipeline

```python
class TokenCompiler:
    """
    Compiles token state machines to executable programs.

    Pipeline:
    1. Parse: Token → AST
    2. Check: AST → Typed AST (with evidence requirements)
    3. Lower: Typed AST → IR (intermediate representation)
    4. Optimize: IR → Optimized IR
    5. Emit: Optimized IR → Executable
    """

    def compile(self, token: MeaningToken) -> CompiledProgram:
        # 1. Get the appropriate state machine
        machine = self._get_machine(token.token_type)

        # 2. Parse current state
        ast = machine.parse(token)

        # 3. Type-check (includes ASHC evidence requirements)
        typed_ast = self.typecheck(ast)
        if typed_ast.errors:
            raise CompilationError(typed_ast.errors)

        # 4. Lower to IR
        ir = self.lower(typed_ast)

        # 5. Optimize (dead code elimination, constant folding)
        optimized_ir = self.optimize(ir)

        # 6. Emit executable
        return self.emit(optimized_ir)

    def _get_machine(self, token_type: str) -> TokenStateMachine:
        """Get the appropriate state machine for this token type."""
        machines = {
            "agentese_path": AGENTESEPortalMachine,
            "task_checkbox": TaskToggleMachine,
            "code_block": CodeRegionMachine,
            "annotation": AnnotationMachine,
            "operad_link": OperadLinkMachine,
            "diff_region": DiffRegionMachine,
            "sandbox_boundary": SandboxBoundaryMachine,
        }
        return machines[token_type]
```

---

---

## Part 8: Deep ASHC Integration (Agentic Self-Hosted Compiler)

> *ASHC is not just an evidence store. It's the compiler that decides what's true.*

### 8.1 ASHC as the Proof Engine

ASHC is our **decisioning compiler** — it takes claims and compiles them to commitments via proofs:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ASHC ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CLAIMS (input)                                                            │
│      │                                                                      │
│      ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     PROOF OBLIGATION GENERATOR                       │  │
│   │                                                                     │  │
│   │   Claim: "This code is correct"                                     │  │
│   │      ↓                                                              │  │
│   │   Obligations:                                                      │  │
│   │     1. Tests pass                                                   │  │
│   │     2. Types check                                                  │  │
│   │     3. No regressions                                               │  │
│   │     4. Review approved                                              │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                        EVIDENCE COLLECTOR                            │  │
│   │                                                                     │  │
│   │   Token-level integration:                                          │  │
│   │     - CODE_REGION edits → test execution evidence                   │  │
│   │     - TASK_TOGGLE → completion evidence                             │  │
│   │     - ANNOTATION → review evidence                                  │  │
│   │     - OPERAD_LINK → composition type-check evidence                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                         PROOF COMPILER                               │  │
│   │                                                                     │  │
│   │   Evidence → Proof term → Commitment                                │  │
│   │                                                                     │  │
│   │   If all obligations satisfied: COMMIT                              │  │
│   │   If obligations missing: BLOCK + request evidence                  │  │
│   │   If contradictory: REJECT + explain                                │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│      │                                                                      │
│      ▼                                                                      │
│   COMMITMENTS (output)                                                      │
│      │                                                                      │
│      ▼                                                                      │
│   DECISION TREE (persisted)                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 Token-Level Proof Obligations

Every token type generates **proof obligations** that ASHC must verify:

```python
class TokenProofObligation:
    """
    Every token edit creates proof obligations for ASHC.

    The token cannot be "committed" until ASHC compiles a valid proof.
    """

    token_id: str
    token_type: str
    claim: Claim
    obligations: list[Obligation]
    evidence_collected: list[Evidence]
    proof_status: Literal["pending", "compiling", "proved", "blocked", "rejected"]


# Proof obligations by token type
TOKEN_OBLIGATIONS: dict[str, list[ObligationType]] = {
    "code_block": [
        ObligationType.TESTS_PASS,
        ObligationType.TYPES_CHECK,
        ObligationType.NO_REGRESSION,
    ],
    "task_checkbox": [
        ObligationType.COMPLETION_CRITERIA_MET,
        ObligationType.DEPENDENCIES_SATISFIED,
    ],
    "operad_link": [
        ObligationType.COMPOSITION_TYPE_CHECK,
        ObligationType.LAW_PRESERVATION,
    ],
    "annotation": [
        ObligationType.AUTHOR_VERIFIED,
        ObligationType.NO_CONTRADICTION,
    ],
    "sandbox_boundary": [
        ObligationType.ISOLATION_MAINTAINED,
        ObligationType.RESOURCE_BOUNDS_RESPECTED,
    ],
}
```

### 8.3 ASHC-Aware Token State Machines

Each token state machine now has ASHC hooks:

```python
class ASHCEnabledTokenMachine(TokenStateMachine[S, I, O]):
    """
    Token state machine with deep ASHC integration.

    State transitions generate proof obligations.
    Final transitions require ASHC proof compilation.
    """

    def __init__(self, token: MeaningToken, ashc: ASHCCompiler):
        self.token = token
        self.ashc = ashc
        self.proof_context = ProofContext()

    def transition(self, state: S, input: I) -> tuple[S, O]:
        # 1. Check if transition requires proof
        if self._requires_proof(state, input):
            # Generate proof obligation
            obligation = self._generate_obligation(state, input)
            self.proof_context.add_obligation(obligation)

            # Attempt to compile proof
            proof_result = self.ashc.compile(obligation)

            if proof_result.status == "blocked":
                # Can't transition — need more evidence
                return (state, ProofBlocked(proof_result.missing_evidence))

            if proof_result.status == "rejected":
                # Contradictory evidence
                return (state, ProofRejected(proof_result.contradiction))

        # 2. Collect evidence from this transition
        evidence = self._collect_evidence(state, input)
        self.proof_context.add_evidence(evidence)

        # 3. Perform the transition
        new_state, output = self._do_transition(state, input)

        # 4. If this is a committing transition, require full proof
        if self._is_committing(new_state):
            final_proof = self.ashc.finalize(self.proof_context)
            if not final_proof.is_valid:
                return (state, CommitBlocked(final_proof.issues))

            # Proof valid — persist the commitment
            self.ashc.commit(final_proof)

        return (new_state, output)

    def _collect_evidence(self, state: S, input: I) -> Evidence:
        """
        Automatically collect evidence from state transitions.

        This is where ASHC integration happens at the token level.
        """
        match self.token.token_type:
            case "code_block":
                return CodeEvidence(
                    source=self.token.source_text,
                    test_results=self._run_tests(),
                    type_check_results=self._run_typecheck(),
                    timestamp=datetime.now(),
                )

            case "task_checkbox":
                return TaskEvidence(
                    task_id=self.token.token_id,
                    completion_state=input.new_state if hasattr(input, 'new_state') else None,
                    timestamp=datetime.now(),
                )

            case "operad_link":
                return CompositionEvidence(
                    source_op=self.token.token_data["source_op"],
                    target_op=self.token.token_data["target_op"],
                    type_compatibility=self._check_types(),
                    law_preservation=self._check_laws(),
                )

            case _:
                return GenericEvidence(
                    token_id=self.token.token_id,
                    transition=f"{state} → {input}",
                    timestamp=datetime.now(),
                )
```

### 8.4 The ASHC Compilation Pipeline

```python
class ASHCCompiler:
    """
    The Agentic Self-Hosted Compiler.

    Compiles claims + evidence into proofs or identifies what's missing.
    """

    def compile(self, context: ProofContext) -> ProofResult:
        """
        Attempt to compile a proof from the current context.

        Returns:
        - PROVED: All obligations satisfied
        - BLOCKED: Some obligations missing evidence
        - REJECTED: Contradictory evidence found
        """

        # 1. Check each obligation
        unsatisfied = []
        for obligation in context.obligations:
            evidence = context.evidence_for(obligation)

            if not evidence:
                unsatisfied.append(ObligationStatus(
                    obligation=obligation,
                    status="missing",
                    needed=obligation.evidence_requirements,
                ))
            elif self._is_contradicted(obligation, evidence):
                return ProofResult(
                    status="rejected",
                    contradiction=self._explain_contradiction(obligation, evidence),
                )
            elif not self._is_sufficient(obligation, evidence):
                unsatisfied.append(ObligationStatus(
                    obligation=obligation,
                    status="insufficient",
                    have=len(evidence),
                    need=obligation.minimum_evidence,
                ))

        if unsatisfied:
            return ProofResult(
                status="blocked",
                missing_evidence=[o.needed for o in unsatisfied],
            )

        # 2. Construct proof term
        proof_term = self._construct_proof(context)

        # 3. Verify proof (self-hosted: the proof proves itself)
        if not self._verify(proof_term):
            return ProofResult(
                status="rejected",
                error="Proof term failed verification",
            )

        return ProofResult(
            status="proved",
            proof=proof_term,
        )

    def _construct_proof(self, context: ProofContext) -> ProofTerm:
        """
        Construct a proof term from satisfied obligations.

        The proof term is a structured representation that can be:
        1. Verified independently
        2. Serialized and stored
        3. Used as evidence for higher-level claims
        """
        return ProofTerm(
            claim=context.claim,
            obligations=context.obligations,
            evidence_links=[
                (obl.id, [e.id for e in context.evidence_for(obl)])
                for obl in context.obligations
            ],
            timestamp=datetime.now(),
            compiler_version=self.version,
        )
```

### 8.5 Evidence as Virtualized Files

The ASHC evidence database becomes part of the file tree, with lenses:

```python
class EvidenceFileLens(FileLens[EvidenceDB, EvidenceSlice]):
    """
    Lens into the ASHC evidence database.

    The agent sees evidence as files, but they're actually
    database queries filtered by accessibility.
    """

    def __init__(self, scope: EvidenceScope, ashc: ASHCCompiler):
        self.scope = scope
        self.ashc = ashc

    def get(self, db: EvidenceDB) -> EvidenceSlice:
        """
        Extract accessible evidence as virtual files.

        The agent sees:
          evidence/
            claim_001.evidence
            claim_002.evidence

        But this is actually a database query filtered by scope.
        """
        accessible = self.scope.accessible_evidence(db)

        return EvidenceSlice(
            files={
                f"evidence/{e.claim_id}.evidence": self._format_evidence(e)
                for e in accessible
            },
            metadata={
                "total_in_db": db.count(),
                "accessible": len(accessible),
                "scope": self.scope.describe(),
            },
        )

    def put(self, slice: EvidenceSlice, db: EvidenceDB) -> EvidenceDB:
        """
        Update evidence database from agent's edits.

        Agent edits to evidence files become:
        1. New evidence records
        2. Annotations on existing evidence
        3. Contradiction markers
        """
        for path, content in slice.files.items():
            claim_id = self._extract_claim_id(path)

            if claim_id in db:
                # Update existing
                db.update(claim_id, self._parse_evidence(content))
            else:
                # Create new evidence
                db.insert(self._parse_evidence(content))

        return db

    def _format_evidence(self, evidence: Evidence) -> str:
        """Format evidence as a readable file."""
        return f"""
# Evidence: {evidence.claim_id}

**Claim:** {evidence.claim}
**Strength:** {evidence.strength}
**Source:** {evidence.source}
**Timestamp:** {evidence.timestamp}

## Content

{evidence.content}

## Proof Status

{self.ashc.proof_status(evidence.claim_id)}

## Related Evidence

{self._format_related(evidence)}
"""
```

### 8.6 Token × ASHC Integration Matrix

Every token operation flows through ASHC:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     TOKEN × ASHC INTEGRATION MATRIX                         │
├─────────────────┬───────────────────────────────────────────────────────────┤
│ Token Operation │ ASHC Integration                                          │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ CODE_REGION     │                                                           │
│   edit          │ → Generate obligation: TESTS_PASS, TYPES_CHECK           │
│   run           │ → Collect evidence: test output, type errors             │
│   commit        │ → Compile proof, require all obligations met             │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ TASK_TOGGLE     │                                                           │
│   toggle        │ → Generate obligation: COMPLETION_CRITERIA               │
│   check         │ → Collect evidence: criteria evaluation                  │
│   commit        │ → Compile proof, mark task in decision tree              │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ OPERAD_LINK     │                                                           │
│   create        │ → Generate obligation: TYPE_COMPATIBILITY                │
│   validate      │ → Collect evidence: type check results                   │
│   compose       │ → Generate obligation: LAW_PRESERVATION                  │
│   execute       │ → Compile proof, allow execution only if proved          │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ ANNOTATION      │                                                           │
│   create        │ → Generate evidence: author + content + context          │
│   reply         │ → Generate evidence: thread continuation                 │
│   resolve       │ → Compile proof: resolution is justified                 │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ SANDBOX_BOUNDARY│                                                           │
│   create        │ → Generate obligation: ISOLATION_MAINTAINED              │
│   execute       │ → Collect evidence: resource usage, no escape            │
│   promote       │ → Compile proof: sandbox results valid for main          │
├─────────────────┼───────────────────────────────────────────────────────────┤
│ DIFF_REGION     │                                                           │
│   accept        │ → Generate obligation: MERGE_CORRECT                     │
│   reject        │ → Generate evidence: rejection reason                    │
│   edit          │ → Generate obligation: MANUAL_MERGE_VALID                │
└─────────────────┴───────────────────────────────────────────────────────────┘
```

### 8.7 The Self-Hosting Property

ASHC compiles itself:

```python
class SelfHostedASHC(ASHCCompiler):
    """
    ASHC is self-hosted: it uses its own proof system to verify itself.

    When ASHC compiles a proof, that compilation is itself a claim
    that generates proof obligations.

    This creates a tower:
      Level 0: Application claims (code correctness, task completion)
      Level 1: ASHC proofs of Level 0 claims
      Level 2: ASHC proofs that Level 1 proofs are valid
      Level N: ...

    The tower is grounded by:
    - Axioms (trusted primitives)
    - External oracles (test runners, type checkers)
    - Human judgment (Kent's disgust veto)
    """

    def compile_self_proof(self, proof: ProofTerm) -> MetaProof:
        """
        Compile a proof that this proof is valid.

        This is the self-hosting step.
        """
        meta_claim = Claim(
            statement=f"Proof {proof.id} is valid",
            level=proof.level + 1,
        )

        meta_obligations = [
            Obligation.PROOF_WELL_FORMED,
            Obligation.EVIDENCE_AUTHENTIC,
            Obligation.OBLIGATIONS_COMPLETE,
        ]

        # The meta-evidence is the proof itself
        meta_evidence = [
            Evidence(
                content=proof.serialize(),
                source="proof_term",
                strength="axiomatic",  # Proofs are their own evidence
            ),
        ]

        return self.compile(ProofContext(
            claim=meta_claim,
            obligations=meta_obligations,
            evidence=meta_evidence,
        ))
```

---

## Part 9: The Paradigm Shift — The Typed-Hypergraph

> *"The lens was a lie. There is only the link."*

### 9.1 The Realization

Parts 1-8 describe a **lens-based** architecture: extract slices, compose them, project to agents. This is useful but fundamentally limited.

The breakthrough: **composition with `>>` is just typed hyperlinks**.

```
auth_middleware ──[tests]──→ test_auth.py
                ──[implements]──→ auth_spec.md
                ──[calls]──→ jwt_utils.py
                ──[evidence]──→ security_claims/
```

This reframes everything:

| Lens Paradigm | Typed-Hypergraph Paradigm |
|---------------|---------------------------|
| Extract slice from whole | Navigate to related node(s) |
| Pre-compose views | Lazy traversal on demand |
| Agent receives static view | Agent navigates live graph |
| `lens("a") >> lens("b")` | `a ──[aspect]──→ {b₁, b₂, ...}` |
| Orchestrator decides focus | Agent decides where to go |
| Files as nouns | **Links as verbs** |
| Binary edges | **Hyperedges** (one → many) |

### 9.2 The Core Insight: Aspects ARE Link Types

AGENTESE aspects aren't just operations—they're **typed edges** in a knowledge graph:

```python
# These are the SAME thing:
await logos("world.auth_middleware.tests", observer)     # AGENTESE invocation
auth_middleware ──[tests]──→ ???                         # Graph traversal

# The aspect IS the link type
# The result IS the destination node(s)
```

This means:
- Every AGENTESE path is a **graph query**
- Every aspect is an **edge type**
- Every node has **affordances** (outgoing edge types)
- Navigation is **lazy** (you don't load until you traverse)

### 9.3 The Typed-Hypergraph Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         THE TYPED-HYPERGRAPH                                 │
│                                                                             │
│                        ┌──────────────────┐                                 │
│                        │  auth_middleware │                                 │
│                        │    (holon)       │                                 │
│                        └────────┬─────────┘                                 │
│                                 │                                           │
│            ┌────────────────────┼────────────────────┐                      │
│            │                    │                    │                      │
│      [tests]               [implements]         [calls]                     │
│            │                    │                    │                      │
│            ▼                    ▼                    ▼                      │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                │
│   │ test_auth   │      │ auth_spec   │      │ jwt_utils   │                │
│   └──────┬──────┘      └──────┬──────┘      └──────┬──────┘                │
│          │                    │                    │                        │
│    [covers]            [derived_from]         [uses]                        │
│          │                    │                    │                        │
│          ▼                    ▼                    ▼                        │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                │
│   │ edge_cases  │      │ RFC_7519    │      │ crypto_lib  │                │
│   │ (evidence)  │      │ (concept)   │      │ (external)  │                │
│   └─────────────┘      └─────────────┘      └─────────────┘                │
│                                                                             │
│   Link types (aspects): tests, implements, calls, covers, derived_from,     │
│                         uses, evidence, refutes, extends, ...               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.4 Historical Lineage

This is not new. We're rediscovering:

| System | Insight |
|--------|---------|
| **Memex** (Bush, 1945) | Associative trails through linked documents |
| **Hypertext** (Nelson, 1965) | Typed bidirectional links |
| **Zettelkasten** (Luhmann) | Atomic notes with semantic connections |
| **The Web** (Berners-Lee) | Universal hyperlinks (but untyped!) |
| **Semantic Web** (W3C) | Typed links with RDF predicates |
| **Roam/Obsidian** | Backlinks and graph navigation |

Our contribution: **AGENTESE aspects AS hyperedge types, with observer-dependent traversal**.

### 9.5.1 Why "Hypergraph"?

A regular graph has binary edges: A → B. A **hypergraph** has edges that connect one node to *many* nodes simultaneously:

```
A ──[tests]──→ {B₁, B₂, B₃}   # One aspect, multiple destinations
```

This is exactly what AGENTESE aspects do:
- `world.auth_middleware.tests` → returns a *set* of test files
- `world.module.imports` → returns a *set* of dependencies
- `world.claim.evidence` → returns a *set* of evidence items

The "hyper" captures the one-to-many nature of semantic relationships.

### 9.6 The Hypergraph Protocol

```python
@dataclass
class ContextNode:
    """A node in the typed hyperlink graph."""

    # Identity
    path: str                           # AGENTESE path (e.g., "world.auth_middleware")
    holon: str                          # The entity name

    # Content (lazy-loaded)
    _content: str | None = None

    # Outgoing edges (affordances)
    def edges(self, observer: Observer) -> dict[str, list["ContextNode"]]:
        """
        What links are available from here?

        Returns: {aspect_name: [destination_nodes]}

        Observer-dependent: different observers see different edges.
        """
        affordances = logos.query(f"?{self.path}.*", observer=observer)
        return {
            aspect: self._resolve_destinations(aspect, observer)
            for aspect in affordances
        }

    # Lazy content loading
    async def content(self) -> str:
        """Load content only when needed."""
        if self._content is None:
            self._content = await self._load()
        return self._content

    # Navigation
    async def follow(self, aspect: str, observer: Observer) -> list["ContextNode"]:
        """
        Traverse a typed link.

        This IS an AGENTESE invocation:
        follow("tests") == logos(f"{self.path}.tests", observer)
        """
        result = await logos(f"{self.path}.{aspect}", observer)
        return self._to_nodes(result)


@dataclass
class ContextGraph:
    """
    The typed hyperlink graph of context.

    Not a pre-loaded structure — a navigation protocol.
    """

    # Current position(s) in the graph
    focus: set[ContextNode]

    # Trail of navigation (Memex-style)
    trail: list[tuple[ContextNode, str, ContextNode]]  # (from, aspect, to)

    # Observer determines edge visibility
    observer: Observer

    async def navigate(self, aspect: str) -> "ContextGraph":
        """
        Follow a link type from all focused nodes.

        Returns new graph with updated focus.
        """
        new_focus = set()
        new_trail = list(self.trail)

        for node in self.focus:
            destinations = await node.follow(aspect, self.observer)
            for dest in destinations:
                new_focus.add(dest)
                new_trail.append((node, aspect, dest))

        return ContextGraph(
            focus=new_focus,
            trail=new_trail,
            observer=self.observer,
        )

    async def affordances(self) -> dict[str, int]:
        """
        What links can we follow from here?

        Returns: {aspect_name: count_of_destinations}
        """
        all_edges: dict[str, int] = defaultdict(int)
        for node in self.focus:
            for aspect, dests in node.edges(self.observer).items():
                all_edges[aspect] += len(dests)
        return dict(all_edges)

    def backtrack(self) -> "ContextGraph":
        """Go back along the trail."""
        if not self.trail:
            return self

        *rest, (prev_node, _, _) = self.trail
        return ContextGraph(
            focus={prev_node},
            trail=rest,
            observer=self.observer,
        )
```

### 9.7 Agent Navigation (Not Orchestration)

The lens paradigm requires an **orchestrator** to compose views. The typed-hypergraph paradigm lets the **agent navigate**:

```python
class NavigatingAgent:
    """
    Agent that navigates the context graph, not receives pre-composed views.
    """

    def __init__(self, start: ContextNode, observer: Observer):
        self.graph = ContextGraph(
            focus={start},
            trail=[],
            observer=observer,
        )

    async def explore(self, goal: str) -> ExplorationResult:
        """
        Navigate the graph toward a goal.

        The agent decides where to go based on:
        1. Available affordances (edges)
        2. Goal relevance
        3. Budget remaining
        """
        while not self._goal_reached(goal):
            # What can I do from here?
            affordances = await self.graph.affordances()

            # Which edge is most relevant to my goal?
            best_edge = self._select_edge(affordances, goal)

            if best_edge is None:
                # Dead end — backtrack
                self.graph = self.graph.backtrack()
                continue

            # Navigate
            self.graph = await self.graph.navigate(best_edge)

            # Load content of new nodes (lazy!)
            for node in self.graph.focus:
                content = await node.content()
                self._process(content)

        return ExplorationResult(
            trail=self.graph.trail,
            findings=self._findings,
        )
```

### 9.8 The Minimal Output Principle (Respected)

The Constitution demands:
> *"Agents should generate the smallest output that can be reliably composed."*

The typed-hypergraph paradigm respects this naturally:

```python
# LENS PARADIGM (violates minimal output)
def get_context() -> AgentCoherentView:
    """Returns ALL relevant content upfront."""
    return AgentCoherentView(
        documents=[...],      # Megabytes of content
        evidence=[...],       # Entire evidence scope
        thinking=[...],       # Full trace
    )

# TYPED-HYPERGRAPH PARADIGM (respects minimal output)
def get_context() -> ContextNode:
    """Returns a starting node with affordances."""
    return ContextNode(
        path="world.auth_middleware",
        # Content not loaded yet!
        # Edges not traversed yet!
        # Agent decides what to load.
    )
```

The agent receives **a handle, not a haystack**.

### 9.9 Hyperedge Types as AGENTESE Aspects

Standard hyperedge types map to aspects:

```python
class StandardEdges:
    """
    Universal edge types for the context graph.

    Each edge type IS an AGENTESE aspect.
    """

    # Structural edges
    CONTAINS = "contains"         # world.module.contains → submodules
    PARENT = "parent"             # world.function.parent → module
    IMPORTS = "imports"           # world.module.imports → dependencies
    IMPORTED_BY = "imported_by"   # Reverse of imports

    # Testing edges
    TESTS = "tests"               # world.module.tests → test files
    TESTED_BY = "tested_by"       # Reverse
    COVERS = "covers"             # world.test.covers → code paths

    # Specification edges
    IMPLEMENTS = "implements"     # world.code.implements → spec
    SPECIFIED_BY = "specified_by" # Reverse
    DERIVES_FROM = "derives_from" # world.spec.derives_from → parent spec

    # Evidence edges (ASHC integration)
    EVIDENCE = "evidence"         # world.claim.evidence → supporting evidence
    REFUTES = "refutes"           # world.evidence.refutes → contradicted claims
    SUPPORTS = "supports"         # world.evidence.supports → supported claims

    # Temporal edges
    EVOLVED_FROM = "evolved_from" # world.v2.evolved_from → v1
    SUPERSEDES = "supersedes"     # world.new.supersedes → old

    # Semantic edges
    RELATED = "related"           # Loose semantic similarity
    SIMILAR = "similar"           # High embedding similarity
    CONTRASTS = "contrasts"       # Semantic opposition


# Registration: each edge type becomes an aspect
@node("world.{holon}")
class UniversalHolon:
    """Every holon has these standard aspects (edges)."""

    @aspect(category=AspectCategory.PERCEPTION)
    async def contains(self, observer: Observer) -> list[ContextNode]:
        """What's inside this holon?"""

    @aspect(category=AspectCategory.PERCEPTION)
    async def tests(self, observer: Observer) -> list[ContextNode]:
        """What tests cover this holon?"""

    @aspect(category=AspectCategory.PERCEPTION)
    async def evidence(self, observer: Observer) -> list[ContextNode]:
        """What evidence relates to this holon?"""

    # ... etc for all edge types
```

### 9.10 Observer-Dependent Hyperedges

Different observers see different edges:

```python
class ObserverDependentEdges:
    """
    The same node has different affordances for different observers.

    This is the phenomenological insight: "what exists depends on who's looking."
    """

    async def edges(self, node: ContextNode, observer: Observer) -> dict[str, list[ContextNode]]:
        match observer.archetype:
            case "developer":
                return {
                    "tests": await node.follow("tests", observer),
                    "imports": await node.follow("imports", observer),
                    "callers": await node.follow("callers", observer),
                    "implements": await node.follow("implements", observer),
                }

            case "security_auditor":
                return {
                    "auth_flows": await node.follow("auth_flows", observer),
                    "data_flows": await node.follow("data_flows", observer),
                    "vulnerabilities": await node.follow("vulnerabilities", observer),
                    "evidence": await node.follow("evidence", observer),
                }

            case "architect":
                return {
                    "dependencies": await node.follow("dependencies", observer),
                    "dependents": await node.follow("dependents", observer),
                    "patterns": await node.follow("patterns", observer),
                    "violations": await node.follow("violations", observer),
                }

            case "newcomer":
                # Simpler view for onboarding
                return {
                    "docs": await node.follow("docs", observer),
                    "examples": await node.follow("examples", observer),
                    "related": await node.follow("related", observer),
                }
```

### 9.11 Bidirectional Hyperedges (Unlike the Web)

The web's links are unidirectional. Ours are bidirectional:

```python
class BidirectionalEdge:
    """
    Every edge has a reverse.

    If A ──[tests]──→ B, then B ──[tested_by]──→ A.
    """

    REVERSE_MAP = {
        "tests": "tested_by",
        "imports": "imported_by",
        "implements": "implemented_by",
        "contains": "contained_in",
        "calls": "called_by",
        "evidence": "evidences",  # Evidence FOR something
        "supports": "supported_by",
        "refutes": "refuted_by",
    }

    @classmethod
    def reverse(cls, edge_type: str) -> str:
        """Get the reverse edge type."""
        if edge_type in cls.REVERSE_MAP:
            return cls.REVERSE_MAP[edge_type]
        if edge_type in cls.REVERSE_MAP.values():
            # Find the key
            for k, v in cls.REVERSE_MAP.items():
                if v == edge_type:
                    return k
        raise UnknownEdgeType(edge_type)


class BidirectionalGraph:
    """
    Maintain bidirectional links automatically.

    When you add A ──[tests]──→ B, automatically add B ──[tested_by]──→ A.
    """

    async def add_edge(self, source: ContextNode, edge_type: str, target: ContextNode):
        # Forward edge
        await self._store_edge(source, edge_type, target)

        # Reverse edge (automatic)
        reverse_type = BidirectionalEdge.reverse(edge_type)
        await self._store_edge(target, reverse_type, source)
```

### 9.12 Trail Persistence (Memex Reborn)

Vannevar Bush's Memex imagined **trails** through linked information. We persist them:

```python
@dataclass
class Trail:
    """
    A replayable path through the context graph.

    Trails are first-class objects that can be:
    - Saved and shared
    - Replayed by other agents
    - Annotated with insights
    - Composed into longer trails
    """

    id: str
    name: str
    created_by: Observer
    created_at: datetime

    # The path taken
    steps: list[TrailStep]

    # Annotations along the way
    annotations: dict[int, str]  # step_index → annotation

    @dataclass
    class TrailStep:
        node: str          # AGENTESE path
        edge_taken: str    # Aspect followed
        insight: str | None  # What was learned here

    async def replay(self, observer: Observer) -> ContextGraph:
        """
        Replay this trail, ending at the final position.

        Like following someone else's research path.
        """
        graph = ContextGraph(
            focus={await ContextNode.from_path(self.steps[0].node)},
            trail=[],
            observer=observer,
        )

        for step in self.steps[1:]:
            graph = await graph.navigate(step.edge_taken)

        return graph

    def annotate(self, step_index: int, annotation: str) -> "Trail":
        """Add an annotation at a step."""
        new_annotations = dict(self.annotations)
        new_annotations[step_index] = annotation
        return dataclasses.replace(self, annotations=new_annotations)


# ASHC integration: trails as evidence
class TrailAsEvidence:
    """
    A trail can BE evidence for a claim.

    "I navigated from A to B via C and found X" is a proof.
    """

    async def trail_to_evidence(self, trail: Trail, claim: str) -> Evidence:
        return Evidence(
            claim=claim,
            source="navigation_trail",
            content=trail.serialize(),
            strength="moderate",  # Trails are exploratory, not definitive
            metadata={
                "trail_id": trail.id,
                "steps": len(trail.steps),
                "created_by": trail.created_by.archetype,
            },
        )
```

### 9.13 Integration with Parts 1-8

The typed-hypergraph paradigm doesn't replace Parts 1-8. It reframes them:

| Original Concept | Typed-Hypergraph Reframe |
|------------------|--------------------------|
| **Lens** | A subgraph — the nodes reachable via certain hyperedge types |
| **Portal** | The graph view projected to the agent |
| **Harness** | Navigation budget (max steps, max depth, loop detection) |
| **Evidence Scope** | Subgraph reachable via `evidence` edges |
| **Thinking Trace** | The trail of navigation |
| **Token State Machine** | Node edit operations |
| **ASHC Commitment** | Requires evidence edges to support claims |
| **Coherence Guarantee** | Graph consistency (no dangling edges) |

### 9.14 The AGENTESE Context Node

Context management becomes an AGENTESE holon:

```python
@node("self.context")
class ContextGraphNode:
    """
    The context graph as a first-class AGENTESE node.

    Path: self.context.*
    """

    graph: ContextGraph

    @aspect(category=AspectCategory.PERCEPTION)
    async def manifest(self, observer: Observer) -> ContextManifest:
        """Where am I in the graph?"""
        return ContextManifest(
            focus=[n.path for n in self.graph.focus],
            trail_length=len(self.graph.trail),
            affordances=await self.graph.affordances(),
        )

    @aspect(category=AspectCategory.MUTATION, effects=[Effect.NAVIGATES("context")])
    async def navigate(self, observer: Observer, edge: str) -> NavigationResult:
        """Follow an edge."""
        self.graph = await self.graph.navigate(edge)
        return NavigationResult(
            new_focus=[n.path for n in self.graph.focus],
            edge_taken=edge,
        )

    @aspect(category=AspectCategory.MUTATION)
    async def focus(self, observer: Observer, path: str) -> FocusResult:
        """Jump to a specific node."""
        node = await ContextNode.from_path(path)
        self.graph = ContextGraph(
            focus={node},
            trail=[],  # New trail starts
            observer=observer,
        )
        return FocusResult(path=path)

    @aspect(category=AspectCategory.PERCEPTION)
    async def trail(self, observer: Observer) -> Trail:
        """Get the current navigation trail."""
        return Trail.from_graph(self.graph)

    @aspect(category=AspectCategory.MUTATION)
    async def backtrack(self, observer: Observer) -> BacktrackResult:
        """Go back one step."""
        self.graph = self.graph.backtrack()
        return BacktrackResult(
            new_focus=[n.path for n in self.graph.focus],
        )

    @aspect(category=AspectCategory.COMPOSITION)
    async def subgraph(self, observer: Observer, edge_types: list[str], depth: int = 3) -> Subgraph:
        """
        Extract a subgraph reachable via certain edge types.

        This is the "lens" operation — but expressed as graph traversal.
        """
        return await self._bfs_extract(edge_types, depth)
```

### 9.15 CLI Integration

```bash
# Navigate the context graph
kg context focus world.auth_middleware
kg context navigate tests
kg context navigate evidence
kg context backtrack

# View current position
kg context manifest
# → Focus: [world.test_auth]
# → Trail: world.auth_middleware ──[tests]──→ world.test_auth
# → Affordances: covers (3), imports (2), related (5)

# Follow affordances
kg context navigate covers
# → Focus: [world.auth_edge_case_1, world.auth_edge_case_2, ...]

# Save a trail
kg context trail save "auth-investigation"

# Replay a trail
kg context trail replay "auth-investigation"
```

### 9.16 Why This Matters

The lens paradigm treats the agent as a **passive receiver** of curated views.

The typed-hypergraph paradigm treats the agent as an **active navigator** of semantic space.

| Lens Agent | Hypergraph Navigator |
|------------|----------------------|
| Receives pre-composed context | Explores live hypergraph |
| Orchestrator decides what's relevant | Agent decides where to go |
| Static snapshot | Dynamic traversal |
| Bounded by orchestrator's foresight | Bounded by navigation budget |
| Can only see what's given | Can discover unexpected connections |
| Binary relationships | **Hyperedge** relationships (one → many) |

The hypergraph navigator can **surprise us**. It can find connections the orchestrator didn't anticipate. It can follow its own associative trails through sets of related nodes.

This is closer to how humans actually think.

---

## Part 10: The Portal Token — Inline Document Expansion

> *"You don't go to the document. The document comes to you."*

### 10.1 The Critical UX Insight

Following a hyperedge should NOT navigate away. It should **expand inline** as a collapsible section. The experience of "opening a doc inside another doc" is the experience of **opening a meaning token**.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  auth_middleware.py                                                          │
│                                                                             │
│  def validate_token(token: str) -> bool:                                    │
│      """Validate JWT token."""                                              │
│      ...                                                                    │
│                                                                             │
│  ▶ [tests] ──→ 3 files                     ← COLLAPSED (click to expand)   │
│                                                                             │
│  ▼ [implements] ──→ auth_spec.md           ← EXPANDED                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  # Authentication Specification                                         ││
│  │                                                                         ││
│  │  ## Token Validation                                                    ││
│  │  Tokens MUST be validated according to RFC 7519...                      ││
│  │                                                                         ││
│  │  ▶ [derived_from] ──→ RFC_7519          ← NESTED COLLAPSED              ││
│  │  ▶ [evidence] ──→ 2 items                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                             │
│  ▶ [calls] ──→ jwt_utils.py                                                 │
│  ▶ [evidence] ──→ security_claims/                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 The Portal Token

This is a new **meaning token type**: `PORTAL_EXPANSION`

```python
class PortalExpansionToken(MeaningToken):
    """
    A meaning token that represents an expandable hyperedge.

    When COLLAPSED: Shows the edge type and destination count
    When EXPANDED: Renders the destination document(s) inline

    The token state IS the navigation state.
    """

    token_type = "portal_expansion"

    # The hyperedge this portal represents
    source_path: str              # "world.auth_middleware"
    edge_type: str                # "tests"
    destinations: list[str]       # ["world.test_auth", "world.test_auth_edge", ...]

    # State
    expanded: bool = False
    expansion_depth: int = 0      # How deep in the nesting

    # Lazy content
    _loaded_content: dict[str, str] | None = None

    def render_collapsed(self) -> str:
        """Render the collapsed state."""
        count = len(self.destinations)
        noun = "file" if count == 1 else "files"
        return f"▶ [{self.edge_type}] ──→ {count} {noun}"

    def render_expanded(self) -> str:
        """Render the expanded state with inline content."""
        lines = [f"▼ [{self.edge_type}] ──→ {len(self.destinations)} files"]

        for dest_path in self.destinations:
            content = self._loaded_content.get(dest_path, "Loading...")
            lines.append(self._indent_block(content, self.expansion_depth + 1))

        return "\n".join(lines)
```

### 10.3 The Token State Machine

Expanding/collapsing a portal is a **state machine transition** (from Part 4):

```python
class PortalStateMachine(TokenStateMachine[PortalState, PortalInput, PortalOutput]):
    """
    State machine for portal expansion tokens.

    States: COLLAPSED ⇄ LOADING → EXPANDED ⇄ COLLAPSED

    Opening a portal:
    1. COLLAPSED → LOADING (triggers content fetch)
    2. LOADING → EXPANDED (content arrives)

    The state transition IS the navigation event.
    """

    STATES = {"COLLAPSED", "LOADING", "EXPANDED", "ERROR"}

    def __init__(self, token: PortalExpansionToken, graph: ContextGraph):
        self.token = token
        self.graph = graph
        self.state = "EXPANDED" if token.expanded else "COLLAPSED"

    async def transition(self, state: str, input: PortalInput) -> tuple[str, PortalOutput]:
        match (state, input):
            case ("COLLAPSED", Expand()):
                # Start loading — this IS following the hyperedge
                asyncio.create_task(self._load_destinations())
                return ("LOADING", LoadingStarted())

            case ("LOADING", ContentLoaded(content)):
                self.token._loaded_content = content
                self.token.expanded = True

                # Record in trail — the expansion IS navigation
                self.graph.trail.append((
                    self.token.source_path,
                    self.token.edge_type,
                    self.token.destinations,
                ))

                return ("EXPANDED", ExpansionComplete(content))

            case ("EXPANDED", Collapse()):
                self.token.expanded = False
                return ("COLLAPSED", Collapsed())

            case ("LOADING", LoadError(err)):
                return ("ERROR", ErrorOccurred(err))

            case _:
                return (state, InvalidTransition())

    async def _load_destinations(self):
        """Lazy load destination content."""
        content = {}
        for dest_path in self.token.destinations:
            node = await ContextNode.from_path(dest_path)
            content[dest_path] = await node.content()

        await self.transition(self.state, ContentLoaded(content))
```

### 10.4 Nested Portals (Recursive Expansion)

Documents contain portals. Expanded documents reveal MORE portals. This creates a **tree of expansions**:

```python
class PortalTree:
    """
    The tree of expanded portals IS the agent's current view.

    Root: The starting document
    Children: Expanded portals within it
    Grandchildren: Portals expanded within those
    ...

    The tree structure IS the trail.
    """

    @dataclass
    class PortalNode:
        path: str
        edge_type: str | None      # None for root
        expanded: bool
        children: list["PortalNode"]
        depth: int

    root: PortalNode
    max_depth: int = 5             # Prevent infinite expansion

    def expand(self, portal_path: list[str]) -> "PortalTree":
        """
        Expand a portal at the given path.

        portal_path = ["tests", "covers"] means:
        - From root, expand "tests" portal
        - Within that, expand "covers" portal
        """
        ...

    def collapse(self, portal_path: list[str]) -> "PortalTree":
        """Collapse a portal, hiding its children."""
        ...

    def to_trail(self) -> Trail:
        """
        Convert the expansion tree to a Memex trail.

        DFS traversal of expanded nodes = the trail of exploration.
        """
        ...

    def render(self) -> str:
        """Render the tree as nested collapsible sections."""
        return self._render_node(self.root, indent=0)

    def _render_node(self, node: PortalNode, indent: int) -> str:
        lines = []

        if node.edge_type:  # Not root
            prefix = "▼" if node.expanded else "▶"
            lines.append(" " * indent + f"{prefix} [{node.edge_type}] ──→ {node.path}")

        if node.expanded:
            # Render content
            content = self._get_content(node.path)
            lines.append(self._indent(content, indent + 2))

            # Render children (nested portals)
            for child in node.children:
                lines.append(self._render_node(child, indent + 2))

        return "\n".join(lines)
```

### 10.5 The Signal: Opening a File

When a portal expands, it signals to the system: **"We are opening this file."**

```python
class PortalOpenSignal:
    """
    The signal emitted when a portal expands.

    This tells the system:
    1. Which file(s) are now "open" (in context)
    2. The edge type that led here (why it's relevant)
    3. The nesting depth (how focused we are)
    4. The parent context (what we came from)
    """

    paths_opened: list[str]
    edge_type: str
    parent_path: str
    depth: int
    timestamp: datetime

    def to_context_event(self) -> ContextEvent:
        """Convert to a context system event."""
        return ContextEvent(
            type="files_opened",
            paths=self.paths_opened,
            reason=f"Followed [{self.edge_type}] from {self.parent_path}",
            depth=self.depth,
        )


# Integration with ASHC — opening creates evidence
class PortalOpenEvidence:
    """
    Opening a portal creates evidence of exploration.

    "Agent opened tests for auth_middleware" is a fact.
    """

    async def record_open(self, signal: PortalOpenSignal) -> Evidence:
        return Evidence(
            claim=f"Explored {signal.edge_type} of {signal.parent_path}",
            source="portal_expansion",
            strength="weak",  # Exploration, not conclusion
            content={
                "opened": signal.paths_opened,
                "edge_type": signal.edge_type,
                "depth": signal.depth,
            },
        )
```

### 10.6 Cross-Synergy: Token × Hypergraph × Trail

This is where everything connects:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    THE PORTAL TOKEN UNIFIES EVERYTHING                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TYPED-HYPERGRAPH (Part 9)                                                  │
│       │                                                                     │
│       │  "Follow this hyperedge"                                            │
│       ▼                                                                     │
│  PORTAL TOKEN (Part 10)                                                     │
│       │                                                                     │
│       │  "Expand this collapsible section"                                  │
│       ▼                                                                     │
│  TOKEN STATE MACHINE (Part 4)                                               │
│       │                                                                     │
│       │  "COLLAPSED → LOADING → EXPANDED"                                   │
│       ▼                                                                     │
│  TRAIL (Part 9.12)                                                          │
│       │                                                                     │
│       │  "Record expansion in trail"                                        │
│       ▼                                                                     │
│  ASHC EVIDENCE (Part 8)                                                     │
│       │                                                                     │
│       │  "Exploration creates evidence"                                     │
│       ▼                                                                     │
│  AGENT CONTEXT                                                              │
│       │                                                                     │
│       └──→ "These files are now 'open' for the agent"                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.7 The UX Principle

> **Navigation is expansion. Expansion is navigation.**

The agent doesn't "go to" a file. The agent "opens" it inline. The tree of expansions IS:
- The **current view** (what's visible)
- The **trail** (how we got here)
- The **context** (what's "open")
- The **evidence** (what we explored)

### 10.8 Literate Exploration

This creates a **literate exploration** experience — like literate programming, but for understanding:

```markdown
# Investigation: Auth Bug

I started at `auth_middleware.py`:

▼ [tests] ──→ test_auth.py
┌────────────────────────────────────────
│ def test_token_expiry():
│     """Token should expire after 1 hour."""
│     token = create_token(expires_in=3600)
│
│     ▼ [covers] ──→ validate_token
│     ┌────────────────────────────────
│     │ def validate_token(token):
│     │     # BUG: Using < instead of <=
│     │     if token.exp < now():  # ← FOUND IT
│     │         return False
│     └────────────────────────────────
└────────────────────────────────────────

The trail of expansions documents my investigation.
Collapsing hides detail. Expanding reveals it.
The document IS the exploration.
```

### 10.9 Implementation: The Portal Renderer

```python
class PortalRenderer:
    """
    Renders the portal tree for different projection surfaces.
    """

    async def render(self, tree: PortalTree, target: ProjectionTarget) -> str:
        match target:
            case ProjectionTarget.CLI:
                return self._render_cli(tree)

            case ProjectionTarget.WEB:
                return self._render_html(tree)

            case ProjectionTarget.LLM:
                return self._render_for_llm(tree)

            case ProjectionTarget.MARKDOWN:
                return self._render_markdown(tree)

    def _render_cli(self, tree: PortalTree) -> str:
        """
        CLI: Use Unicode box-drawing for nesting.
        ▶/▼ for collapsed/expanded.
        """
        ...

    def _render_html(self, tree: PortalTree) -> str:
        """
        Web: Use <details><summary> with data attributes.

        <details data-portal-path="world.auth_middleware.tests"
                 data-edge-type="tests"
                 data-depth="1">
            <summary>▶ [tests] ──→ 3 files</summary>
            <div class="portal-content">
                <!-- Lazy loaded content -->
            </div>
        </details>
        """
        ...

    def _render_for_llm(self, tree: PortalTree) -> str:
        """
        LLM: Include metadata about expansion state.

        <!-- PORTAL: tests (EXPANDED, depth=1) -->
        <file path="test_auth.py">
        ...
        </file>
        <!-- END PORTAL -->
        """
        ...

    def _render_markdown(self, tree: PortalTree) -> str:
        """
        Markdown: Use nested blockquotes or custom syntax.

        > ▼ [tests] ──→ test_auth.py
        > > ```python
        > > def test_token_expiry():
        > > ...
        > > ```
        """
        ...
```

### 10.10 The Affordance: What Can I Expand?

Every portal shows its **destinations** before expansion:

```
▶ [tests] ──→ 3 files              # I can see there are 3 test files
▶ [implements] ──→ auth_spec.md    # I can see it implements a spec
▶ [evidence] ──→ 5 items           # I can see there's evidence
```

This is the **affordance** — the agent sees what's *possible* before committing to explore. The count/summary helps the agent decide:
- "3 test files might be worth expanding"
- "5 evidence items — I should look at those"
- "Only 1 spec — quick to check"

Future: Show a file is large for large files. Give ability to grab first 200 or last 200 lines of any file instead of full expansion (will give limited affordances, i.e. probably no reactivity)

---

## Part 11: Closing Thought (Final)

> *"The agent doesn't see files. The agent doesn't even see lenses. The agent sees **portal tokens** — typed hyperedges that expand into nested worlds."*

The morphism from raw reality to agent perception is not a lens extraction. It's a **typed-hypergraph navigation protocol** made tangible through **portal tokens**.

- Every aspect is a hyperedge type
- Every hyperedge is a portal waiting to expand
- Every expansion adds to the trail
- Every trail is evidence of exploration
- The tree of expansions IS the agent's understanding

**Navigation is expansion. Expansion is navigation. The document IS the exploration.**

The file is a lie. The lens is a lie. There is only the typed-hypergraph.

---

*Brainstormed: 2024-12-21*
*Evolved: 2024-12-22 — The Typed-Hypergraph Paradigm + Portal Tokens*
*Builds on: Interactive Text v2, ASHC, PolyAgent, Memex, Zettelkasten, AGENTESE, Literate Programming*
*Status: Pre-architecture — paradigm shift identified, UX crystallized, ready for formalization*
