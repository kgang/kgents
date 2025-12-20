# U-gent Tool Infrastructure: Phase 4 Advanced Patterns

> *"The master's touch was always just compressed experience. Now we can share the compression."*

**Status**: Research Complete, Ready for Implementation
**Date**: 2025-12-20
**Parent**: `plans/ugent-tooling-implementation.md`
**Spec**: `spec/services/tooling.md` (to be extended)

---

## 🎯 GROUNDING IN KENT'S INTENT

*"The Mirror Test: Does K-gent feel like me on my best day?"*
*"Daring, bold, creative, opinionated but not gaudy"*
*"Tasteful > feature-complete; Joy-inducing > merely functional"*

---

## Executive Summary

Phase 4 was originally deferred as "future patterns." After deep research synthesis, this document transforms it from a catch-all bucket into **five distinct jewels of advanced capability**:

| Phase | Name | Duration | Core Insight |
|-------|------|----------|--------------|
| 4A | PolyTool | 1.5 weeks | Mode-dependent tool behavior (Spivak polynomial functors) |
| 4B | SheafTool | 1 week | Local-global coherence for distributed execution |
| 4C | FluxTool + Teaching | 1.5 weeks | Streaming + introspection fusion |
| 4D | MCP Bridge | 1 week | Bidirectional tool discovery |
| 4E | Formal Verification | 0.5 weeks | Static pipeline validation |

**Total**: 5.5 weeks

Each synthesizes cutting-edge 2024-2025 research with kgents' existing categorical foundations.

---

## Research Synthesis

### 1. Polynomial Functors (Spivak/Niu 2024-2025)

**Source**: [David Spivak](https://dspivak.net/) and [Polynomial Functors: A Mathematical Theory of Interaction](https://arxiv.org/abs/2312.00990) (Cambridge University Press, August 2025)

> "Dynamical systems—machines that take time-varying input, change their state, and produce output—can be wired together to form more complex systems. The theory of 'mode-dependent' dynamical systems can be naturally recast within the category Poly."

**Key insight for kgents**: Tools aren't just morphisms `A → B`. They're **mode-dependent**—a WriteTool in "overwrite" mode behaves differently than in "append" mode. This is exactly what PolyAgent captures.

**Connection to existing code**: `impl/claude/agents/poly/primitives.py` already defines 17 polynomial primitives. PolyTool extends this pattern to the tooling domain.

### 2. Chain-of-Thought for Tool Transparency (2025)

**Sources**:
- [LLM Observability: A Guide to AI Transparency for Agents](https://www.aryaxai.com/article/llm-observability-a-guide-to-ai-transparency-for-agents)
- [Chain-of-Thought Prompting](https://www.ibm.com/think/topics/chain-of-thoughts)
- [Thoughts without Thinking: Reconsidering CoT in Agentic Pipelines](https://arxiv.org/html/2505.00875v1) (CHI 2025)

> "Agentic systems have been proposed as a means to produce explainability, in that they can produce a record of how instructions are passed between agents, allowing end users to trace conclusions back to their source data."

> "Tracing all prompts, sub-prompts, context fetches from RAG systems, and final responses is the first step. For agents of AI that engage in multi-turn conversations, full traceability of their 'chain of thought' is essential for debugging and ensuring AI transparency."

**Key insight**: Teaching mode (Pattern 14 from `docs/skills/crown-jewel-patterns.md`) should extend to tools. Every tool invocation should optionally explain *why* it's being invoked and *what alternatives were considered*.

**Connection to existing code**: Différance traces already capture "ghost alternatives." FluxTool makes these visible in real-time.

### 3. Streaming & Progressive Disclosure (2025)

**Sources**:
- [Serverless Strategies for Streaming LLM Responses](https://aws.amazon.com/blogs/compute/serverless-strategies-for-streaming-llm-responses/) (AWS)
- [Progressive Disclosure in Agent Skills](https://www.marthakelly.com/blog/progressive-disclosure-agent-skills)
- [Progressive Disclosure AI Design Pattern](https://www.aiuxdesign.guide/patterns/progressive-disclosure)
- [Streaming Tool Calls Feature Request](https://github.com/langgenius/dify/issues/19916) (Dify)

> "For long-running tasks or agent-based workflows, being able to observe each intermediate reasoning step (e.g., tool selection, invocation, partial results) in real-time is desirable."

> "This pattern solves the context window scaling problem. Agents with filesystem and code execution tools don't need to read the entirety of a skill into their context window—they load metadata cheaply at startup, then selectively access deeper content through tool invocation."

**Key insight**: FluxTool should emit partial results during execution, not just final output. The UI can progressively render as data arrives.

**Connection to existing code**: `impl/claude/agents/flux/` already implements Flux agents. FluxTool applies this to the tooling layer.

### 4. MCP Bidirectional Protocol (2025)

**Sources**:
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [MCP Apps Extension](http://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/)
- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) (Anthropic)
- [MCP Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)

> "The protocol supports secure, bidirectional connections between data sources and AI-powered tools."

> "In December 2025, Anthropic donated the MCP to the Agentic AI Foundation (AAIF), a directed fund under the Linux Foundation, co-founded by Anthropic, Block and OpenAI, with support from Google, Microsoft, Amazon Web Services (AWS), Cloudflare, and Bloomberg."

> "In March 2025, OpenAI officially adopted the MCP, following a decision to integrate the standard across its products."

**Key insight**: kgents tools should be exposable AS MCP servers, not just MCP consumers. This enables external agents to discover and invoke kgents tools.

### 5. Formal Verification for Tool Composition (2025)

**Sources**:
- [Position: Trustworthy AI Agents Require Integration of LLMs and Formal Methods](https://zhehou.github.io/papers/Position-Trustworthy-AI-Agents-Require-the-Integration-of-Large-Language-Models-and-Formal-Methods.pdf)
- [Prediction: AI will make formal verification go mainstream](https://martin.kleppmann.com/2025/12/08/ai-formal-verification.html) (Martin Kleppmann)
- [AWS Kiro: Formal Verification in Agentic Development](https://www.webpronews.com/aws-kiros-reasoning-revolution-formal-verification-reshapes-agentic-coding/)

> "AI will bring formal verification into the software engineering mainstream. Proof assistants and proof-oriented programming languages such as Rocq, Isabelle, Lean, F*, and Agda make it possible to write a formal specification that code is supposed to satisfy, and then mathematically prove the code always satisfies that spec."

> "LLM-based coding assistants are getting pretty good at writing proof scripts in various languages. At present, a human with specialist expertise still has to guide the process, but this may become fully automated in the next few years, which would totally change the economics of formal verification."

**Key insight**: Tool pipelines can be statically verified. An Operad defines *what compositions are valid*; formal verification can prove *that they preserve invariants*.

### 6. Categorical Foundations for Explainable AI (2024)

**Sources**:
- [Categorical Foundations of Explainable AI](https://www.researchgate.net/publication/370338927_Categorical_Foundations_of_Explainable_AI_A_Unifying_Formalism_of_Structures_and_Semantics)
- [Category Theory for Artificial General Intelligence](https://link.springer.com/chapter/10.1007/978-3-031-65572-2_13) (AGI 2024)
- [Token Space: A Category Theory Framework for AI Computations](https://arxiv.org/abs/2404.11624)

> "This work formalizes the notions of 'learning agent' and 'explainable learning agent' as morphisms in feedback monoidal categories."

> "Category theory has been successfully applied beyond pure mathematics and applications to artificial intelligence (AI) and machine learning (ML) have been developed. There are three types of category theory for AI and ML: category theory for data representation learning, category theory for learning (optimization) algorithms, and category theory for compositional architecture design and analysis."

**Key insight**: The kgents Witness primitive is already a trace functor. Extend it to capture not just *what happened* but *why*.

### 7. Composable Agent Architectures (2025)

**Sources**:
- [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) (Anthropic)
- [Inside the Machine: How Composable Agents Are Rewiring AI Architecture](https://www.tribe.ai/applied-ai/inside-the-machine-how-composable-agents-are-rewiring-ai-architecture-in-2025) (Tribe AI)
- [Microsoft Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview)

> "The basic building block of agentic systems is an LLM enhanced with augmentations such as retrieval, tools, and memory. One approach to implementing augmentations is through our recently released Model Context Protocol."

> "Composable agent orchestration is where the real innovation is happening in AI system design. While it introduces challenges in orchestration, communication, and state management, the benefits of building with specialized components far outweigh the costs."

**Key insight**: kgents' categorical approach (PolyAgent + Operad + Sheaf) is exactly the right architecture for composable agents. Phase 4 extends this to tools.

### 8. LLM Tool Orchestration Research (2025)

**Sources**:
- [LLM-Assisted Tool Runs: Architecture & Applications](https://www.emergentmind.com/topics/llm-assisted-tool-runs)
- [Less is More: Optimizing Function Calling for LLM Execution on Edge Devices](https://arxiv.org/abs/2411.15399)
- [Streaming, Fast and Slow: Cognitive Load-Aware Streaming](https://arxiv.org/html/2504.17999v2)

> "Task scheduling algorithms overlap LLM decoding and tool execution, leveraging isolated processes and event-driven architectures. Compiler layers identify temporally-local sequences of similar function calls and fuse them into composite operations for highly parallel tool dispatch with minimal round-trip overhead."

> "This fusion approach yields up to 4–5× higher parallelization rates and 12–40% lower token usage and latency on geospatial and scientific workloads."

> "Research shows that selectively reducing the number of tools available to LLMs significantly improves their function-calling performance, execution time, and power efficiency on edge devices. Experimental results show execution time reduced by up to 70% and power consumption by up to 40%."

**Key insight**: Tool selection and composition can be optimized. The Operad approach enables static analysis of tool pipelines for optimization.

---

## Phase 4A: PolyTool — Mode-Dependent Tool Behavior

**Duration**: 1.5 weeks
**The Big Idea**: Tools aren't stateless functions. They have *modes* that affect their behavior.

### Conceptual Foundation

```
CURRENT MODEL                          POLYTOOL MODEL
--------------                         --------------
Tool[A, B]                             PolyTool[S, A, B]
  |                                      |
  v                                      v
A ──────────────► B                    Position ──► Direction ──► (NewPosition, B)
                                         │              │
                                         │              │
                                      "mode"       "valid inputs"

Example:                               Example:
write: WriteRequest → WriteResult      write: OVERWRITE × WriteRequest → (OVERWRITE, WriteResult)
                                       write: APPEND × WriteRequest → (APPEND, WriteResult)
                                       write: PATCH × PatchRequest → (SMART, MergeResult)
```

### Implementation

```python
# services/tooling/poly_tool.py

from enum import Enum, auto
from typing import FrozenSet, Generic, TypeVar

S = TypeVar("S", bound=Enum)  # State/Mode type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


class WriteMode(Enum):
    """Modes for WriteTool."""
    OVERWRITE = auto()    # Replace file entirely
    APPEND = auto()       # Add to end
    PREPEND = auto()      # Add to beginning
    PATCH = auto()        # Apply diff
    SMART = auto()        # LLM-assisted merge


class PolyTool(Tool[A, B], Generic[S, A, B]):
    """
    Mode-dependent tool with polynomial structure.

    Extends Tool[A, B] with:
    - positions: Set of valid modes
    - directions: Mode → Set of valid input types
    - transition: (Mode, Input) → (NewMode, Output)

    This is the tool-layer analog of PolyAgent.

    Category Laws:
        - Mode transitions are deterministic
        - Mode composition is associative
        - Identity mode exists (passthrough)

    See: Spivak & Niu, "Polynomial Functors" (2025)
    """

    @property
    @abstractmethod
    def positions(self) -> FrozenSet[S]:
        """Valid modes for this tool."""
        ...

    @abstractmethod
    def directions(self, mode: S) -> FrozenSet[type]:
        """Valid input types for the given mode."""
        ...

    @abstractmethod
    async def transition(
        self, mode: S, request: A
    ) -> tuple[S, B]:
        """Execute in mode, returning (new_mode, result)."""
        ...

    async def invoke(self, request: A) -> B:
        """Standard Tool interface (uses default mode)."""
        _, result = await self.transition(self.default_mode, request)
        return result

    async def invoke_in_mode(self, mode: S, request: A) -> tuple[S, B]:
        """Invoke with explicit mode, returning new mode."""
        if mode not in self.positions:
            raise InvalidMode(f"Mode {mode} not in {self.positions}")
        if type(request) not in self.directions(mode):
            raise InvalidInput(f"Input type {type(request)} not valid in mode {mode}")
        return await self.transition(mode, request)


class PolyWriteTool(PolyTool[WriteMode, WriteRequest, WriteResult]):
    """
    Mode-dependent write with polynomial structure.

    Modes:
    - OVERWRITE: Replace file entirely
    - APPEND: Add to end of file
    - PREPEND: Add to beginning of file
    - PATCH: Apply unified diff
    - SMART: LLM-assisted merge (escalation target)

    Mode Escalation:
    - PATCH on conflict → SMART
    - SMART on repeated conflict → OVERWRITE (with warning)
    """

    @property
    def name(self) -> str:
        return "file.write"

    @property
    def positions(self) -> FrozenSet[WriteMode]:
        return frozenset(WriteMode)

    @property
    def default_mode(self) -> WriteMode:
        return WriteMode.OVERWRITE

    def directions(self, mode: WriteMode) -> FrozenSet[type]:
        """What inputs are valid in this mode."""
        match mode:
            case WriteMode.PATCH:
                return frozenset({PatchRequest})
            case WriteMode.SMART:
                return frozenset({SmartMergeRequest, PatchRequest})
            case _:
                return frozenset({WriteRequest})

    async def transition(
        self, mode: WriteMode, request: WriteRequest
    ) -> tuple[WriteMode, WriteResult]:
        """Execute and potentially change mode."""
        try:
            result = await self._write_in_mode(mode, request)
            return (mode, result)  # Stay in current mode on success
        except ConflictError as e:
            # Mode escalation on conflict
            next_mode = self._escalate_mode(mode)
            if next_mode == mode:
                raise  # Can't escalate further
            # Retry in escalated mode
            return await self.transition(next_mode, request)

    def _escalate_mode(self, mode: WriteMode) -> WriteMode:
        """Determine escalation path for mode."""
        escalation = {
            WriteMode.PATCH: WriteMode.SMART,
            WriteMode.SMART: WriteMode.OVERWRITE,
            WriteMode.OVERWRITE: WriteMode.OVERWRITE,  # Terminal
            WriteMode.APPEND: WriteMode.OVERWRITE,
            WriteMode.PREPEND: WriteMode.OVERWRITE,
        }
        return escalation[mode]
```

### Operad Integration

```python
# services/tooling/tool_operad.py

TOOL_OPERAD = Operad(
    name="TOOL",
    operations={
        # Sequential composition
        "sequence": Operation(
            arity=2,
            compose=sequential_compose,
            description="Execute tools in sequence: A >> B",
        ),
        # Parallel composition (independent tools)
        "parallel": Operation(
            arity=2,
            compose=parallel_compose,
            description="Execute tools in parallel: A || B",
        ),
        # Mode-dependent branching
        "branch": Operation(
            arity=3,
            compose=mode_branch_compose,
            description="Branch based on mode: if mode then A else B",
        ),
        # Fixed-point (retry with mode escalation)
        "fix_mode": Operation(
            arity=1,
            compose=mode_escalation_fix,
            description="Retry with mode escalation until success or terminal",
        ),
        # Inherit from base DESIGN_OPERAD
        **DESIGN_OPERAD.operations,
    },
    laws=[
        Law("sequence_associativity", verify_sequence_assoc),
        Law("parallel_commutativity", verify_parallel_commute),
        Law("branch_determinism", verify_branch_deterministic),
        Law("mode_escalation_termination", verify_escalation_terminates),
        *DESIGN_OPERAD.laws,
    ],
)
```

### Why This Matters

| Use Case | Without PolyTool | With PolyTool |
|----------|------------------|---------------|
| Write conflict | Fails, user retries | Auto-escalates PATCH → SMART → OVERWRITE |
| Bash safety | Fixed sandbox | Starts sandboxed, escalates on trust promotion |
| Grep large files | Always batch | Switches to streaming mode on size threshold |
| Edit with diff | One strategy | Mode selection based on file type and size |

---

## Phase 4B: SheafTool — Local-Global Coherence

**Duration**: 1 week
**The Big Idea**: Tools executing across distributed resources maintain global coherence.

### Conceptual Foundation

```
LOCAL EXECUTIONS                       GLOBAL RESULT
----------------                       -------------

File A ──► EditTool ──► Result A  ─┐
                                   │
File B ──► EditTool ──► Result B  ─┼──► SheafTool.glue() ──► GlobalResult
                                   │
File C ──► EditTool ──► Result C  ─┘

COHERENCE CONSTRAINT:
If File A and File B share imports,
Result A and Result B must agree on those imports.
```

### Implementation

```python
# services/tooling/sheaf_tool.py

from dataclasses import dataclass
from typing import Callable, Generic, TypeVar
from itertools import combinations

R = TypeVar("R")  # Resource type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Local result type
G = TypeVar("G")  # Global result type


@dataclass
class SheafTool(Generic[R, A, B, G]):
    """
    Local tool executions → Global coherent result.

    When the same logical operation runs on multiple files/resources,
    the Sheaf ensures results are compatible and can be glued.

    This is the tool-layer analog of TownSheaf/ProjectSheaf.

    Components:
    - overlap: Determine shared structure between resources
    - compatible: Check if local results agree on overlap
    - glue: Combine local results into global result

    See: spec/principles.md AD-006 (Unified Categorical Foundation)
    """

    overlap: Callable[[R, R], R | None]
    compatible: Callable[[B, B, R], bool]
    glue: Callable[[list[tuple[R, B]]], G]

    async def execute_globally(
        self,
        tool: Tool[A, B],
        resources: list[R],
        request: A,
        localizer: Callable[[A, R], A],
    ) -> G:
        """
        Execute tool across all resources with global coherence.

        Args:
            tool: The tool to execute
            resources: Resources to execute on
            request: Base request (will be localized per resource)
            localizer: Function to localize request for each resource

        Returns:
            Global result glued from local results

        Raises:
            SheafInconsistency: If local results conflict on overlaps
        """
        # Execute locally on each resource
        local_results: list[tuple[R, B]] = []
        for resource in resources:
            localized_request = localizer(request, resource)
            result = await tool.invoke(localized_request)
            local_results.append((resource, result))

        # Check compatibility on overlaps
        for (r1, res1), (r2, res2) in combinations(local_results, 2):
            overlap_resource = self.overlap(r1, r2)
            if overlap_resource is not None:
                if not self.compatible(res1, res2, overlap_resource):
                    raise SheafInconsistency(
                        f"Results incompatible on overlap: {overlap_resource}",
                        resource1=r1,
                        resource2=r2,
                        overlap=overlap_resource,
                    )

        # Glue into global result
        return self.glue(local_results)


class SheafInconsistency(ToolError):
    """Local tool results are incompatible on their overlap."""

    def __init__(
        self,
        message: str,
        resource1: Any,
        resource2: Any,
        overlap: Any,
    ):
        super().__init__(message)
        self.resource1 = resource1
        self.resource2 = resource2
        self.overlap = overlap
```

### Example: Multi-file Refactor

```python
# Example: Renaming a function across multiple files

@dataclass
class RefactorSummary:
    """Global result of multi-file refactor."""
    files_changed: int
    total_replacements: int
    all_changes: dict[Path, list[Replacement]]


def shared_imports(f1: Path, f2: Path) -> set[str] | None:
    """Determine shared imports between two files."""
    imports1 = extract_imports(f1)
    imports2 = extract_imports(f2)
    shared = imports1 & imports2
    return shared if shared else None


def refactor_compatible(
    r1: EditResult, r2: EditResult, shared: set[str]
) -> bool:
    """Check that both refactors renamed the same things in shared imports."""
    for import_name in shared:
        if import_name in r1.renames and import_name in r2.renames:
            if r1.renames[import_name] != r2.renames[import_name]:
                return False  # Inconsistent rename!
    return True


def glue_refactors(results: list[tuple[Path, EditResult]]) -> RefactorSummary:
    """Combine all local refactors into global summary."""
    return RefactorSummary(
        files_changed=len(results),
        total_replacements=sum(r.replacement_count for _, r in results),
        all_changes={path: r.replacements for path, r in results},
    )


REFACTOR_SHEAF = SheafTool[Path, RenameRequest, EditResult, RefactorSummary](
    overlap=shared_imports,
    compatible=refactor_compatible,
    glue=glue_refactors,
)

# Usage
result = await REFACTOR_SHEAF.execute_globally(
    tool=edit_tool,
    resources=matching_files,
    request=RenameRequest(old="getCwd", new="getCurrentWorkingDirectory"),
    localizer=lambda req, path: req.for_file(path),
)
```

### Why This Matters

| Use Case | Without SheafTool | With SheafTool |
|----------|-------------------|----------------|
| Multi-file refactor | Manual consistency checks | Automatic coherence verification |
| Distributed grep | Duplicate results | Consistent deduplication |
| Parallel web fetch | Cache inconsistency | Coherent cache updates |
| Multi-file edit | Partial rollback on failure | Atomic all-or-nothing |

---

## Phase 4C: FluxTool + Teaching Layer

**Duration**: 1.5 weeks
**The Big Idea**: Tools stream partial results AND explain their reasoning.

### Conceptual Foundation

```
TRADITIONAL TOOL                       FLUXTOOL
--------------                         --------

invoke(request) ──────────────► result    invoke(request) ──► AsyncIterator[Event]
                                                                    │
     (black box)                              ┌──────────────────────┼──────────────────────┐
                                              │                      │                      │
                                              v                      v                      v
                                          STARTED              PARTIAL              COMPLETE
                                              │                      │                      │
                                              v                      v                      v
                                    "Beginning grep..."   "Found 15 in src/"   "Total: 42 matches"
                                              │
                                              v
                                    (if teaching_mode)
                                              │
                                              v
                                         REASONING
                                              │
                                              v
                                    "Using ripgrep because
                                     pattern is regex and
                                     codebase > 10k files"
                                              │
                                              v
                                        ALTERNATIVE
                                              │
                                              v
                                    "Considered: manual grep,
                                     LSP references"
```

### Implementation

```python
# services/tooling/flux_tool.py

from dataclasses import dataclass
from enum import Enum, auto
from typing import AsyncIterator, Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")


class ProgressEventType(Enum):
    """Types of progress events from FluxTool."""
    STARTED = auto()      # Tool invocation begins
    REASONING = auto()    # Why this tool was chosen (teaching mode)
    PARTIAL = auto()      # Intermediate result
    ALTERNATIVE = auto()  # Path not taken (Différance ghost)
    COMPLETE = auto()     # Final result


@dataclass(frozen=True)
class ProgressEvent(Generic[B]):
    """Event emitted during FluxTool execution."""
    type: ProgressEventType
    timestamp: datetime
    data: dict[str, Any]

    @classmethod
    def started(cls, tool: str, request_summary: str) -> "ProgressEvent":
        return cls(
            type=ProgressEventType.STARTED,
            timestamp=datetime.now(UTC),
            data={"tool": tool, "request": request_summary},
        )

    @classmethod
    def reasoning(
        cls, explanation: str, alternatives: list[str]
    ) -> "ProgressEvent":
        return cls(
            type=ProgressEventType.REASONING,
            timestamp=datetime.now(UTC),
            data={"explanation": explanation, "alternatives": alternatives},
        )

    @classmethod
    def partial(cls, data: Any) -> "ProgressEvent":
        return cls(
            type=ProgressEventType.PARTIAL,
            timestamp=datetime.now(UTC),
            data={"partial": data},
        )

    @classmethod
    def alternative(cls, ghost: "GhostAlternative") -> "ProgressEvent":
        return cls(
            type=ProgressEventType.ALTERNATIVE,
            timestamp=datetime.now(UTC),
            data={"ghost": ghost.to_dict()},
        )

    @classmethod
    def complete(cls, result: B) -> "ProgressEvent[B]":
        return cls(
            type=ProgressEventType.COMPLETE,
            timestamp=datetime.now(UTC),
            data={"result": result},
        )


@dataclass
class FluxTool(Tool[A, AsyncIterator[ProgressEvent[B]]], Generic[A, B]):
    """
    Streaming tool with progressive disclosure.

    Wraps a standard Tool[A, B] to produce streaming events:
    - STARTED: Tool invocation begins
    - REASONING: Why this tool was chosen (teaching mode only)
    - PARTIAL: Intermediate results as they become available
    - ALTERNATIVE: Paths not taken (Différance ghosts)
    - COMPLETE: Final result

    This is the tool-layer analog of FluxAgent.

    See: spec/agents/flux.md
    """

    inner: Tool[A, B]
    teaching_mode: bool = False
    partial_interval_ms: int = 100  # Emit partials every N ms

    @property
    def name(self) -> str:
        return f"flux.{self.inner.name}"

    @property
    def streaming(self) -> bool:
        return True

    async def invoke(self, request: A) -> AsyncIterator[ProgressEvent[B]]:
        """Execute with streaming progress events."""
        # STARTED
        yield ProgressEvent.started(
            tool=self.inner.name,
            request_summary=self._summarize_request(request),
        )

        # REASONING (teaching mode only)
        if self.teaching_mode:
            yield ProgressEvent.reasoning(
                explanation=self._explain_tool_choice(request),
                alternatives=self._list_alternatives(request),
            )

        # PARTIAL events during execution
        async for partial in self._stream_execution(request):
            yield ProgressEvent.partial(partial)

        # Collect final result
        result = await self._await_final()

        # ALTERNATIVE events (Différance ghosts)
        if self.teaching_mode:
            for ghost in self._collect_ghosts():
                yield ProgressEvent.alternative(ghost)

        # COMPLETE
        yield ProgressEvent.complete(result)

    def _explain_tool_choice(self, request: A) -> str:
        """Generate explanation for why this tool was chosen."""
        # This would integrate with the tool selection reasoning
        return f"Using {self.inner.name} because: [reasoning from selector]"

    def _list_alternatives(self, request: A) -> list[str]:
        """List alternative tools that were considered."""
        # This would query the tool registry for alternatives
        return ["alternative_tool_1", "alternative_tool_2"]

    async def _stream_execution(self, request: A) -> AsyncIterator[Any]:
        """Stream partial results during execution."""
        # For tools that support streaming (e.g., bash output)
        if hasattr(self.inner, "stream"):
            async for partial in self.inner.stream(request):
                yield partial
        # For non-streaming tools, emit progress indicators
        else:
            yield {"status": "executing", "progress": 0.5}

    def _collect_ghosts(self) -> list["GhostAlternative"]:
        """Collect Différance ghost alternatives."""
        # This would integrate with the Différance store
        return []


@dataclass(frozen=True)
class GhostAlternative:
    """A path not taken (Différance trace)."""
    tool_name: str
    reason_not_chosen: str
    estimated_outcome: str

    def to_dict(self) -> dict:
        return {
            "tool": self.tool_name,
            "reason": self.reason_not_chosen,
            "outcome": self.estimated_outcome,
        }
```

### Teaching Layer Integration

```python
# services/tooling/teaching.py

from dataclasses import dataclass
from typing import Callable


@dataclass
class ToolTeachingContext:
    """
    Context for teaching mode explanations.

    Integrates with Pattern 14 (Teaching Mode Toggle) from
    docs/skills/crown-jewel-patterns.md.
    """

    enabled: bool
    verbosity: int = 1  # 1=concise, 2=detailed, 3=exhaustive

    def explain_selection(
        self,
        selected_tool: str,
        alternatives: list[str],
        request: Any,
    ) -> str | None:
        """Generate tool selection explanation."""
        if not self.enabled:
            return None

        if self.verbosity == 1:
            return f"Selected {selected_tool} for this task."
        elif self.verbosity == 2:
            alt_str = ", ".join(alternatives[:3])
            return (
                f"Selected {selected_tool}. "
                f"Alternatives considered: {alt_str}."
            )
        else:  # verbosity == 3
            return self._detailed_explanation(selected_tool, alternatives, request)

    def explain_mode(self, mode: Enum, tool: str) -> str | None:
        """Explain why a particular mode was selected."""
        if not self.enabled:
            return None
        return f"Using {tool} in {mode.name} mode because: [mode reasoning]"

    def explain_escalation(
        self, from_mode: Enum, to_mode: Enum, reason: str
    ) -> str | None:
        """Explain mode escalation."""
        if not self.enabled:
            return None
        return f"Escalating from {from_mode.name} to {to_mode.name}: {reason}"


class TeachingToolExecutor(ToolExecutor):
    """
    Tool executor with teaching mode integration.

    Wraps standard execution with explanations when teaching mode is enabled.
    """

    def __init__(
        self,
        executor: ToolExecutor,
        teaching_context: Callable[[], ToolTeachingContext],
    ):
        self._executor = executor
        self._get_context = teaching_context

    async def execute(
        self,
        tool: Tool[A, B],
        request: A,
        observer: Umwelt,
    ) -> B:
        ctx = self._get_context()

        # Pre-execution teaching
        if ctx.enabled:
            explanation = ctx.explain_selection(
                tool.name,
                self._get_alternatives(tool, request),
                request,
            )
            await self._emit_teaching_event(explanation)

        # Execute
        result = await self._executor.execute(tool, request, observer)

        # Post-execution teaching
        if ctx.enabled:
            await self._emit_ghost_alternatives(tool, request, result)

        return result
```

### Frontend Integration

```typescript
// hooks/useFluxTool.ts

import { useState, useEffect, useMemo } from 'react';
import { useTeachingModeSafe } from './useTeachingMode';

interface ProgressEvent<B> {
  type: 'STARTED' | 'REASONING' | 'PARTIAL' | 'ALTERNATIVE' | 'COMPLETE';
  timestamp: string;
  data: Record<string, any>;
}

interface FluxToolState<B> {
  status: 'idle' | 'streaming' | 'complete' | 'error';
  events: ProgressEvent<B>[];
  result: B | null;
  reasoning: string | null;
  alternatives: string[];
  ghosts: GhostAlternative[];
  error: Error | null;
}

export function useFluxTool<A, B>(
  toolPath: string,
  request: A | null,
): FluxToolState<B> {
  const { enabled: teachingMode } = useTeachingModeSafe();
  const [state, setState] = useState<FluxToolState<B>>({
    status: 'idle',
    events: [],
    result: null,
    reasoning: null,
    alternatives: [],
    ghosts: [],
    error: null,
  });

  useEffect(() => {
    if (!request) return;

    const eventSource = new EventSource(
      `/api/agentese/world.tools.${toolPath}?stream=true&teaching=${teachingMode}`
    );

    setState(s => ({ ...s, status: 'streaming', events: [] }));

    eventSource.onmessage = (event) => {
      const progressEvent: ProgressEvent<B> = JSON.parse(event.data);

      setState(s => {
        const newEvents = [...s.events, progressEvent];

        switch (progressEvent.type) {
          case 'COMPLETE':
            return {
              ...s,
              status: 'complete',
              events: newEvents,
              result: progressEvent.data.result,
            };
          case 'REASONING':
            return {
              ...s,
              events: newEvents,
              reasoning: progressEvent.data.explanation,
              alternatives: progressEvent.data.alternatives,
            };
          case 'ALTERNATIVE':
            return {
              ...s,
              events: newEvents,
              ghosts: [...s.ghosts, progressEvent.data.ghost],
            };
          default:
            return { ...s, events: newEvents };
        }
      });
    };

    eventSource.onerror = (error) => {
      setState(s => ({ ...s, status: 'error', error: new Error('Stream failed') }));
      eventSource.close();
    };

    return () => eventSource.close();
  }, [toolPath, request, teachingMode]);

  return state;
}
```

### Why This Matters

| Use Case | Without FluxTool | With FluxTool |
|----------|------------------|---------------|
| Long bash command | Wait for completion | See output line-by-line |
| Large file grep | Loading spinner | Progressive result count |
| Tool selection | Black box | "Using ripgrep because..." |
| Debugging | Check logs after | See ghosts in real-time |

---

## Phase 4D: MCP Bidirectional Bridge

**Duration**: 1 week
**The Big Idea**: kgents tools are discoverable as MCP servers.

### Implementation

```python
# services/tooling/mcp_server.py

from dataclasses import dataclass
from typing import Any

from services.tooling import ToolRegistry, ToolExecutor


@dataclass
class MCPToolSchema:
    """MCP tool schema for discovery."""
    name: str
    description: str
    inputSchema: dict
    annotations: dict[str, Any] | None = None


@dataclass
class MCPToolResult:
    """MCP tool invocation result."""
    content: list[dict]
    isError: bool = False


class KgentsMCPServer:
    """
    Bidirectional MCP bridge.

    Exposes kgents tools as MCP server endpoints:
    - External agents can discover kgents tools via list_tools
    - External agents can invoke kgents tools via call_tool

    Also provides MCP client for invoking external tools:
    - kgents agents can discover external MCP tools
    - kgents agents can invoke external MCP tools

    See: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
    """

    def __init__(
        self,
        registry: ToolRegistry,
        executor: ToolExecutor,
    ):
        self.registry = registry
        self.executor = executor

    # =========================================================================
    # Server Mode: Expose kgents tools to external agents
    # =========================================================================

    async def handle_list_tools(self) -> list[MCPToolSchema]:
        """
        MCP discovery: list available tools.

        Returns all registered kgents tools as MCP tool schemas.
        """
        schemas = []
        for meta in self.registry.all_tools():
            schema = MCPToolSchema(
                name=f"kgents.{meta.name}",
                description=meta.description,
                inputSchema=self._to_json_schema(meta.input_type),
                annotations={
                    "trust_required": meta.trust_required,
                    "effects": [f"{e.value}:{r}" for e, r in meta.effects],
                    "category": meta.category.name,
                    "timeout_ms": meta.timeout_default_ms,
                    "cacheable": meta.cacheable,
                    "streaming": meta.streaming,
                },
            )
            schemas.append(schema)
        return schemas

    async def handle_call_tool(
        self,
        name: str,
        arguments: dict,
        observer: "Umwelt | None" = None,
    ) -> MCPToolResult:
        """
        MCP invocation: call a kgents tool.

        Args:
            name: Tool name (must start with "kgents.")
            arguments: Tool arguments as dict
            observer: Optional observer context (for trust gating)

        Returns:
            MCP tool result

        Raises:
            MCPError: If tool not found or invocation fails
        """
        if not name.startswith("kgents."):
            raise MCPError(
                code="UNKNOWN_TOOL",
                message=f"Unknown tool namespace: {name}",
            )

        tool_name = name[7:]  # Remove "kgents." prefix
        meta = self.registry.get(tool_name)
        if meta is None:
            raise MCPError(
                code="UNKNOWN_TOOL",
                message=f"Unknown tool: {tool_name}",
            )

        # Create request from arguments
        try:
            request = meta.input_type(**arguments)
        except (TypeError, ValueError) as e:
            raise MCPError(
                code="INVALID_PARAMS",
                message=f"Invalid arguments: {e}",
            )

        # Execute through standard pipeline (trust gates, tracing, etc.)
        try:
            result = await self.executor.execute(
                meta.tool,
                request,
                observer or self._default_observer(),
            )
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": self._serialize_result(result),
                }],
                isError=False,
            )
        except ToolError as e:
            return MCPToolResult(
                content=[{
                    "type": "text",
                    "text": f"Tool error: {e}",
                }],
                isError=True,
            )

    # =========================================================================
    # Client Mode: Invoke external MCP tools from kgents
    # =========================================================================

    async def discover_external_tools(
        self,
        server_url: str,
    ) -> list[MCPToolSchema]:
        """
        Discover tools from an external MCP server.

        Returns list of available tools on the server.
        """
        async with self._mcp_client(server_url) as client:
            return await client.list_tools()

    async def call_external_tool(
        self,
        server_url: str,
        tool_name: str,
        arguments: dict,
    ) -> Any:
        """
        Invoke a tool on an external MCP server.

        Args:
            server_url: MCP server URL
            tool_name: Tool name on the server
            arguments: Tool arguments

        Returns:
            Tool result
        """
        async with self._mcp_client(server_url) as client:
            result = await client.call_tool(tool_name, arguments)
            return self._parse_result(result)

    def _to_json_schema(self, dataclass_type: type) -> dict:
        """Convert dataclass to JSON Schema."""
        # Use dataclass-json or similar for schema generation
        return {"type": "object", "properties": {}}  # Placeholder

    def _serialize_result(self, result: Any) -> str:
        """Serialize result to JSON string."""
        import json
        if hasattr(result, "to_dict"):
            return json.dumps(result.to_dict())
        return json.dumps(result)

    def _default_observer(self) -> "Umwelt":
        """Default observer for MCP calls (L1 trust)."""
        from agents.poly.primitives import Umwelt
        return Umwelt(observer_type="mcp_client", capabilities=frozenset())


class MCPError(Exception):
    """MCP protocol error."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
```

### AGENTESE Integration

```python
# protocols/agentese/contexts/world_mcp.py

@node(
    "world.mcp",
    description="MCP Bidirectional Bridge",
    dependencies=("mcp_server", "tool_registry"),
    contracts={
        "discover": Response(MCPDiscoveryResponse),
        "invoke": Contract(MCPInvokeRequest, MCPInvokeResponse),
    },
)
@dataclass
class MCPNode(BaseLogosNode):
    """world.mcp.* -- MCP bridge for external tool interaction."""

    mcp_server: KgentsMCPServer

    @aspect(category=AspectCategory.PERCEPTION)
    async def discover(self, observer: Umwelt) -> MCPDiscoveryResponse:
        """Discover available kgents tools via MCP."""
        tools = await self.mcp_server.handle_list_tools()
        return MCPDiscoveryResponse(
            tools=[t.name for t in tools],
            count=len(tools),
        )

    @aspect(
        category=AspectCategory.ACTION,
        effects=[Effect.CALLS("external_mcp")],
    )
    async def invoke_external(
        self,
        observer: Umwelt,
        request: MCPInvokeRequest,
    ) -> MCPInvokeResponse:
        """Invoke a tool on an external MCP server."""
        result = await self.mcp_server.call_external_tool(
            server_url=request.server_url,
            tool_name=request.tool_name,
            arguments=request.arguments,
        )
        return MCPInvokeResponse(result=result)
```

### Why This Matters

| Use Case | Without MCP Bridge | With MCP Bridge |
|----------|-------------------|-----------------|
| Claude Desktop | Can't use kgents tools | Discovers and invokes kgents tools |
| External agents | Isolated systems | Compose with kgents capabilities |
| Tool ecosystem | kgents is an island | kgents is a first-class MCP citizen |
| Enterprise integration | Custom adapters | Standard MCP protocol |

---

## Phase 4E: Formal Operad Verification

**Duration**: 0.5 weeks
**The Big Idea**: Prove pipeline compositions are valid before execution.

### Implementation

```python
# services/tooling/verify.py

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any
from itertools import pairwise


class VerificationStatus(Enum):
    """Status of pipeline verification."""
    VALID = auto()
    WARNING = auto()
    INVALID = auto()


@dataclass(frozen=True)
class VerificationError:
    """Error found during verification."""
    step: int
    error_type: str
    message: str
    severity: str  # "error" | "warning"


@dataclass(frozen=True)
class VerificationResult:
    """Result of pipeline verification."""
    status: VerificationStatus
    errors: tuple[VerificationError, ...]
    warnings: tuple[VerificationError, ...]
    pipeline_hash: int

    @property
    def valid(self) -> bool:
        return self.status == VerificationStatus.VALID


class PipelineVerifier:
    """
    Static verification of tool pipelines.

    Uses operad laws to prove compositions are valid
    without executing them.

    Checks:
    - Type flow: output type of step N matches input type of step N+1
    - Effect compatibility: reads don't follow deletes on same resource
    - Trust compatibility: escalating trust doesn't skip levels
    - Operad laws: composition satisfies operad constraints

    This is inspired by formal verification research:
    - Kleppmann (2025): "AI will make formal verification mainstream"
    - AWS Kiro: Formal verification in agentic development
    """

    def verify(self, pipeline: ToolPipeline) -> VerificationResult:
        """
        Verify a tool pipeline statically.

        Returns verification result without executing the pipeline.
        """
        errors: list[VerificationError] = []
        warnings: list[VerificationError] = []

        # Check type flow
        type_errors = self._verify_type_flow(pipeline)
        errors.extend(type_errors)

        # Check effect compatibility
        effect_warnings = self._verify_effect_compatibility(pipeline)
        warnings.extend(effect_warnings)

        # Check trust compatibility
        trust_errors = self._verify_trust_flow(pipeline)
        errors.extend(trust_errors)

        # Verify operad laws
        law_errors = self._verify_operad_laws(pipeline)
        errors.extend(law_errors)

        # Determine status
        if errors:
            status = VerificationStatus.INVALID
        elif warnings:
            status = VerificationStatus.WARNING
        else:
            status = VerificationStatus.VALID

        return VerificationResult(
            status=status,
            errors=tuple(errors),
            warnings=tuple(warnings),
            pipeline_hash=hash(tuple(s.name for s in pipeline.steps)),
        )

    def _verify_type_flow(
        self, pipeline: ToolPipeline
    ) -> list[VerificationError]:
        """Verify type compatibility between pipeline steps."""
        errors = []
        for i, (prev, curr) in enumerate(pairwise(pipeline.steps)):
            if not self._types_compatible(prev.output_type, curr.input_type):
                errors.append(VerificationError(
                    step=i + 1,
                    error_type="TYPE_MISMATCH",
                    message=(
                        f"Type mismatch: {prev.name} outputs {prev.output_type.__name__} "
                        f"but {curr.name} expects {curr.input_type.__name__}"
                    ),
                    severity="error",
                ))
        return errors

    def _verify_effect_compatibility(
        self, pipeline: ToolPipeline
    ) -> list[VerificationError]:
        """Verify effect compatibility (e.g., no read after delete)."""
        warnings = []
        deleted_resources: set[str] = set()

        for i, step in enumerate(pipeline.steps):
            # Check if reading a deleted resource
            for effect, resource in step.effects:
                if effect == ToolEffect.READS and resource in deleted_resources:
                    warnings.append(VerificationError(
                        step=i,
                        error_type="CAUSALITY_WARNING",
                        message=f"Reading {resource} after it was deleted",
                        severity="warning",
                    ))

            # Track deletions
            for effect, resource in step.effects:
                if effect == ToolEffect.DELETES:
                    deleted_resources.add(resource)

        return warnings

    def _verify_trust_flow(
        self, pipeline: ToolPipeline
    ) -> list[VerificationError]:
        """Verify trust level requirements are satisfiable."""
        errors = []
        max_trust_so_far = 0

        for i, step in enumerate(pipeline.steps):
            required = step.trust_required
            if required > max_trust_so_far + 1:
                errors.append(VerificationError(
                    step=i,
                    error_type="TRUST_SKIP",
                    message=(
                        f"{step.name} requires L{required} trust "
                        f"but pipeline only at L{max_trust_so_far}"
                    ),
                    severity="error",
                ))
            max_trust_so_far = max(max_trust_so_far, required)

        return errors

    def _verify_operad_laws(
        self, pipeline: ToolPipeline
    ) -> list[VerificationError]:
        """Verify operad composition laws."""
        errors = []

        for law in TOOL_OPERAD.laws:
            result = law.verify_pipeline(pipeline)
            if result.status == LawStatus.FAILED:
                errors.append(VerificationError(
                    step=-1,  # Pipeline-level
                    error_type="LAW_VIOLATION",
                    message=f"Operad law '{law.name}' violated: {result.message}",
                    severity="error",
                ))

        return errors

    def _types_compatible(self, output_type: type, input_type: type) -> bool:
        """Check if output type is compatible with input type."""
        # Handle Any types
        if output_type is Any or input_type is Any:
            return True
        # Handle exact match
        if output_type == input_type:
            return True
        # Handle subclass
        try:
            return issubclass(output_type, input_type)
        except TypeError:
            return False
```

### AGENTESE Integration

```python
# protocols/agentese/contexts/concept_tools.py

@node(
    "concept.tools",
    description="Tool Infrastructure Concepts",
    dependencies=("pipeline_verifier",),
    contracts={
        "verify": Contract(VerifyRequest, VerifyResponse),
    },
)
@dataclass
class ConceptToolsNode(BaseLogosNode):
    """concept.tools.* -- Conceptual operations on tool infrastructure."""

    verifier: PipelineVerifier

    @aspect(category=AspectCategory.PERCEPTION)
    async def verify(
        self, observer: Umwelt, request: VerifyRequest
    ) -> VerifyResponse:
        """Verify a tool pipeline without executing it."""
        # Parse pipeline from request
        pipeline = self._parse_pipeline(request.pipeline_spec)

        # Verify
        result = self.verifier.verify(pipeline)

        return VerifyResponse(
            valid=result.valid,
            status=result.status.name,
            errors=[e.message for e in result.errors],
            warnings=[w.message for w in result.warnings],
        )
```

### Why This Matters

| Use Case | Without Verification | With Verification |
|----------|---------------------|-------------------|
| Pipeline typo | Runtime TypeError | Caught at composition |
| Read after delete | Mysterious failure | Warning at composition |
| Trust escalation | Permission denied at step 5 | Error before execution |
| IDE integration | Run to find errors | Squiggles as you type |

---

## Implementation Order

```
Phase 4A: PolyTool         ─┬─► Phase 4C: FluxTool + Teaching
   (1.5 weeks)              │      (1.5 weeks)
                            │
Phase 4B: SheafTool        ─┤
   (1 week)                 │
                            ├──► Phase 4D: MCP Bridge
                            │      (1 week)
                            │
                            └──► Phase 4E: Verification
                                   (0.5 weeks)

Total: 5.5 weeks
```

---

## Deliverables Summary

| Phase | Files | Tests | AGENTESE Path |
|-------|-------|-------|---------------|
| 4A: PolyTool | `services/tooling/poly_tool.py`, `tool_operad.py` | `test_poly_tool.py`, `test_mode_escalation.py` | `world.tools.:mode` |
| 4B: SheafTool | `services/tooling/sheaf_tool.py` | `test_sheaf_coherence.py`, `test_multi_file.py` | `world.tools.:global` |
| 4C: FluxTool | `services/tooling/flux_tool.py` | `test_flux_streaming.py`, `test_progress_events.py` | `world.tools.:stream` |
| 4C: Teaching | `services/tooling/teaching.py` | `test_teaching_layer.py` | (integrated) |
| 4D: MCP Bridge | `services/tooling/mcp_server.py`, `contexts/world_mcp.py` | `test_mcp_bidirectional.py`, `test_mcp_discovery.py` | `world.mcp.*` |
| 4E: Verification | `services/tooling/verify.py`, `contexts/concept_tools.py` | `test_pipeline_verification.py`, `test_operad_laws.py` | `concept.tools.verify` |

---

## Success Criteria

### Phase 4A: PolyTool
- [ ] PolyWriteTool demonstrates mode escalation PATCH → SMART → OVERWRITE on conflict
- [ ] PolyBashTool starts sandboxed, escalates on trust promotion
- [ ] Mode transitions are deterministic and logged
- [ ] TOOL_OPERAD verifies composition laws including mode operations

### Phase 4B: SheafTool
- [ ] Multi-file refactor completes with coherence guarantee
- [ ] SheafInconsistency raised when local results conflict
- [ ] Parallel execution with automatic deduplication
- [ ] Rollback-on-any-failure for atomic operations

### Phase 4C: FluxTool + Teaching
- [ ] Bash command streams output line-by-line to UI
- [ ] REASONING events explain tool selection (teaching mode)
- [ ] ALTERNATIVE events show Différance ghosts
- [ ] Frontend hook renders progressive results

### Phase 4D: MCP Bridge
- [ ] External MCP client discovers kgents tools via `handle_list_tools`
- [ ] External MCP client invokes kgents tools via `handle_call_tool`
- [ ] kgents discovers external MCP server tools
- [ ] kgents invokes external MCP tools through standard pipeline

### Phase 4E: Verification
- [ ] Type mismatch caught at composition time
- [ ] Read-after-delete warning generated
- [ ] Trust escalation error for skipped levels
- [ ] All TOOL_OPERAD laws verified (including STRUCTURAL honest ones)

---

## References

### Category Theory & Polynomial Functors
- [David Spivak](https://dspivak.net/) — Polynomial functor research
- [Polynomial Functors: A Mathematical Theory of Interaction](https://arxiv.org/abs/2312.00990) — Niu & Spivak (2025)
- [Poly: An abundant categorical setting for mode-dependent dynamics](https://arxiv.org/abs/2005.01894) — Spivak (2020)
- [Category Theorists in AI](https://golem.ph.utexas.edu/category/2025/02/category_theorists_in_ai.html) — n-Category Café
- [Category Theory for Artificial General Intelligence](https://link.springer.com/chapter/10.1007/978-3-031-65572-2_13) — AGI 2024

### Explainability & Transparency
- [Categorical Foundations of Explainable AI](https://www.researchgate.net/publication/370338927_Categorical_Foundations_of_Explainable_AI_A_Unifying_Formalism_of_Structures_and_Semantics)
- [LLM Observability: A Guide to AI Transparency for Agents](https://www.aryaxai.com/article/llm-observability-a-guide-to-ai-transparency-for-agents)
- [Chain-of-Thought Prompting](https://www.ibm.com/think/topics/chain-of-thoughts) — IBM
- [Thoughts without Thinking: Reconsidering CoT in Agentic Pipelines](https://arxiv.org/html/2505.00875v1) — CHI 2025

### Streaming & Progressive Disclosure
- [Serverless Strategies for Streaming LLM Responses](https://aws.amazon.com/blogs/compute/serverless-strategies-for-streaming-llm-responses/) — AWS
- [Progressive Disclosure in Agent Skills](https://www.marthakelly.com/blog/progressive-disclosure-agent-skills)
- [Progressive Disclosure AI Design Pattern](https://www.aiuxdesign.guide/patterns/progressive-disclosure)
- [Streaming, Fast and Slow: Cognitive Load-Aware Streaming](https://arxiv.org/html/2504.17999v2)

### MCP Protocol
- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [Introducing the Model Context Protocol](https://www.anthropic.com/news/model-context-protocol) — Anthropic
- [MCP Apps Extension](http://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/)
- [Model Context Protocol Wikipedia](https://en.wikipedia.org/wiki/Model_Context_Protocol)

### Formal Verification
- [Position: Trustworthy AI Agents Require LLMs and Formal Methods](https://zhehou.github.io/papers/Position-Trustworthy-AI-Agents-Require-the-Integration-of-Large-Language-Models-and-Formal-Methods.pdf)
- [Prediction: AI will make formal verification mainstream](https://martin.kleppmann.com/2025/12/08/ai-formal-verification.html) — Kleppmann
- [AWS Kiro: Formal Verification in Agentic Development](https://www.webpronews.com/aws-kiros-reasoning-revolution-formal-verification-reshapes-agentic-coding/)

### Agent Architectures
- [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic
- [Inside the Machine: Composable Agents in 2025](https://www.tribe.ai/applied-ai/inside-the-machine-how-composable-agents-are-rewiring-ai-architecture-in-2025) — Tribe AI
- [LLM-Assisted Tool Runs: Architecture & Applications](https://www.emergentmind.com/topics/llm-assisted-tool-runs)
- [Less is More: Optimizing Function Calling for Edge Devices](https://arxiv.org/abs/2411.15399)

---

## Related Documents

- `plans/ugent-tooling-implementation.md` — Parent implementation plan
- `spec/services/tooling.md` — Specification (to be extended)
- `docs/skills/crown-jewel-patterns.md` — Pattern 14 (Teaching Mode)
- `docs/skills/polynomial-agent.md` — PolyAgent patterns
- `impl/claude/agents/poly/primitives.py` — 17 polynomial primitives
- `impl/claude/agents/flux/` — Flux agent implementation

---

*"The pieces were always there—this research shows how to wire them together."*

*"Daring, bold, creative, opinionated but not gaudy"*
