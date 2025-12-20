# U-gent Tool Infrastructure: Claude Code Audit & Possibility Space Exploration

> *"Daring, bold, creative, opinionated but not gaudy"*

**Date**: 2025-12-20
**Purpose**: Deep audit of Claude Code's tool patterns → kgents U-gent infrastructure synthesis → Full possibility space exploration

---

## Part I: Claude Code Tool Audit

### 1.1 Tool Taxonomy

Claude Code implements **21 distinct tools** organized into six categories:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLAUDE CODE TOOL ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  CATEGORY 1: FILE OPERATIONS (4 tools)                                      │
│  ─────────────────────────────────────                                      │
│  Read ───────── Read files with offset/limit, images, PDFs, notebooks      │
│  Write ──────── Create/overwrite (REQUIRES prior Read)                     │
│  Edit ───────── String replacement with old_string/new_string              │
│  NotebookEdit ─ Jupyter cell manipulation                                   │
│                                                                             │
│  CATEGORY 2: SEARCH & NAVIGATION (4 tools)                                  │
│  ──────────────────────────────────────────                                 │
│  Glob ───────── File pattern matching (**/*, *.ts)                         │
│  Grep ───────── Content search via ripgrep (regex, output modes)           │
│  LSP ────────── Language Server Protocol (goToDefinition, references...)   │
│  MCPSearch ──── Load MCP tools before use (deferred loading)               │
│                                                                             │
│  CATEGORY 3: SYSTEM INTERACTION (4 tools)                                   │
│  ──────────────────────────────────────────                                 │
│  Bash ───────── Shell execution (timeout, background, safety protocols)    │
│  WebFetch ───── URL fetch + AI summarization (15-min cache)                │
│  WebSearch ──── Web search with mandatory source citation                  │
│  KillShell ──── Terminate background shells                                │
│                                                                             │
│  CATEGORY 4: TASK MANAGEMENT (5 tools)                                      │
│  ──────────────────────────────────────                                     │
│  TodoWrite ──── Task list with status (pending/in_progress/completed)      │
│  TaskList ───── List tasks (for swarm mode)                                │
│  TaskCreate ─── Create tasks with dependencies/blockers                    │
│  TaskUpdate ─── Update task status/owner                                   │
│  TaskOutput ─── Get output from background agents                          │
│                                                                             │
│  CATEGORY 5: MULTI-AGENT / SWARM (3 tools)                                  │
│  ──────────────────────────────────────────                                 │
│  Task ───────── Launch specialized subagents (Explore, Plan, Guide...)    │
│  TeammateTool ─ Team operations (spawn, message, assignTask, claimTask...) │
│  AskUserQuestion ── Clarification with structured options                  │
│                                                                             │
│  CATEGORY 6: MODE SWITCHING (2 tools)                                       │
│  ──────────────────────────────────                                         │
│  EnterPlanMode ─ Transition to read-only planning                          │
│  ExitPlanMode ── Exit planning with optional swarm launch                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Tool Use Patterns

#### Pattern 1: Read-Before-Write Protocol

Claude Code enforces a **causality constraint**:
```
Read → Edit/Write

❌ Direct Write without Read = ERROR
```

This pattern ensures agents understand before modifying. **Critical for safety**.

#### Pattern 2: Parallel Tool Execution

```
┌──────────────────────────────────────────────────────────────┐
│  PARALLEL EXECUTION (when independent)                        │
│                                                               │
│    git status ─────┐                                          │
│    git diff   ─────┼───→ [Process in parallel]               │
│    git log    ─────┘                                          │
│                                                               │
│  SEQUENTIAL EXECUTION (when dependent)                        │
│                                                               │
│    git add . ───→ git commit ───→ git status                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Key insight**: Claude Code explicitly instructs parallel vs. sequential based on **data dependencies**.

#### Pattern 3: Specialized Tools > Bash Commands

```
❌ bash cat file.txt
✓ Read tool

❌ bash grep pattern
✓ Grep tool

❌ bash echo "message"
✓ Direct output text
```

**Why**: Specialized tools have:
- Better permissions handling
- Structured output
- Optimized for the use case
- Easier to monitor/trace

#### Pattern 4: Subagent Delegation

```
                           ┌──────────────────────┐
                           │     MAIN AGENT       │
                           │  (orchestrator)      │
                           └──────────┬───────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  Explore Agent  │     │   Plan Agent    │     │  Guide Agent    │
    │  (read-only)    │     │  (read-only)    │     │ (documentation) │
    │                 │     │                 │     │                 │
    │ Tools:          │     │ Tools:          │     │ Tools:          │
    │ - Glob          │     │ - Glob          │     │ - Glob          │
    │ - Grep          │     │ - Grep          │     │ - Grep          │
    │ - Read          │     │ - Read          │     │ - Read          │
    │ - Bash (R/O)    │     │ - Bash (R/O)    │     │ - WebFetch      │
    └─────────────────┘     └─────────────────┘     │ - WebSearch     │
                                                    └─────────────────┘
```

**Key insight**: Subagents have **restricted tool sets** based on their role.

#### Pattern 5: Plan-Then-Execute Modal

```
┌──────────────────────────────────────────────────────────────┐
│                    PLAN MODE WORKFLOW                         │
│                                                               │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐           │
│  │  NORMAL   │────►│   PLAN    │────►│  NORMAL   │           │
│  │   MODE    │     │   MODE    │     │   MODE    │           │
│  └───────────┘     └───────────┘     └───────────┘           │
│        │                 │                 │                  │
│        │                 │                 │                  │
│   Full tools        Read-only         Full tools             │
│   Read/Write         Explore          Implement              │
│                                                               │
│  Trigger:           Trigger:          Trigger:               │
│  EnterPlanMode      ExitPlanMode      User approval          │
│                     + approval                                │
└──────────────────────────────────────────────────────────────┘
```

#### Pattern 6: Swarm Coordination

```
┌─────────────────────────────────────────────────────────────────┐
│                    SWARM ARCHITECTURE                            │
│                                                                  │
│                    ┌─────────────────┐                          │
│                    │   TEAM LEAD     │                          │
│                    │                 │                          │
│                    │ - Creates team  │                          │
│                    │ - Assigns tasks │                          │
│                    │ - Gathers results│                         │
│                    └────────┬────────┘                          │
│                             │                                    │
│          ┌──────────────────┼──────────────────┐                │
│          │                  │                  │                │
│          ▼                  ▼                  ▼                │
│   ┌────────────┐     ┌────────────┐     ┌────────────┐         │
│   │  Worker 1  │     │  Worker 2  │     │  Worker 3  │         │
│   │            │     │            │     │            │         │
│   │ Mailbox    │     │ Mailbox    │     │ Mailbox    │         │
│   │ Tasks      │     │ Tasks      │     │ Tasks      │         │
│   └────────────┘     └────────────┘     └────────────┘         │
│                                                                  │
│  TeammateTool operations:                                        │
│  - spawn, spawnTeam, cleanup                                    │
│  - read/write (mailbox)                                         │
│  - assignTask, claimTask                                        │
│  - requestShutdown, approveShutdown                             │
│  - discoverTeams, requestJoin, approveJoin                      │
└─────────────────────────────────────────────────────────────────┘
```

#### Pattern 7: Output Summarization

Claude Code uses **sub-agents for context management**:

```
┌─────────────────────────────────────────────────────────────────┐
│                SUMMARIZATION SUB-AGENTS                          │
│                                                                  │
│  Bash Output Summarizer                                          │
│  └── Decides: should_summarize: true/false                      │
│  └── Extracts: errors, key info, verbatim excerpts              │
│  └── Triggers: verbose logs, test output, build output          │
│                                                                  │
│  Conversation Summarizer                                         │
│  └── Sections: Primary Request, Technical Concepts, Files,      │
│                Errors, Problem Solving, Pending, Current Work   │
│  └── Preserves: All user messages, code snippets, next steps    │
│                                                                  │
│  WebFetch Summarizer                                             │
│  └── Converts: HTML → Markdown → AI Summary                     │
│  └── Cache: 15-minute self-cleaning                             │
│                                                                  │
│  User Sentiment Analyzer                                         │
│  └── Detects: frustration, PR creation requests                 │
│  └── Output: <frustrated>true/false</frustrated>                │
│              <pr_request>true/false</pr_request>                │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Safety Protocols

#### Git Safety Protocol

```
NEVER:
- Update git config
- Force push to main/master
- Skip hooks (--no-verify)
- Use interactive flags (-i)
- Amend pushed commits
- Commit secrets (.env, credentials.json)

ALWAYS:
- Only commit when explicitly asked
- Use HEREDOC for commit messages
- Check authorship before amend
- Verify commit not pushed before amend
- Run git status after commit
```

#### Permission Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERMISSION LAYERS                             │
│                                                                  │
│  Layer 1: Tool Availability                                      │
│  └── Available tools defined at agent spawn                      │
│  └── Subagents get restricted tool sets                         │
│                                                                  │
│  Layer 2: Read-Before-Write                                      │
│  └── Edit/Write require prior Read of same file                 │
│                                                                  │
│  Layer 3: User Approval Gates                                    │
│  └── Plan mode requires consent                                 │
│  └── Swarm launch requires approval                             │
│                                                                  │
│  Layer 3.5: Witness Trust Gate (kgents)                          │
│  └── L0: observe only; L1: read-only; L2: reversible writes      │
│  └── L3: external side effects (network, browser, system tools)  │
│  └── Trust escalations gate tool access across all projections   │
│                                                                  │
│  Layer 4: Hook System                                            │
│  └── User-defined shell commands on tool events                 │
│  └── Can block operations                                       │
│                                                                  │
│  Layer 5: Sandbox Mode                                           │
│  └── Bash sandboxing for untrusted operations                   │
│  └── dangerouslyDisableSandbox requires explicit opt-in         │
│                                                                  │
│  Layer 6: Différance Trace (kgents)                              │
│  └── All tool invocations emit trace + alternatives (ghosts)     │
│  └── Trace required for auditability + replay                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part II: Mapping to kgents Architecture

### 2.1 U-gent Foundation

The existing U-gent spec provides **categorical tool composition**:

```
U-GENT TYPES:

Type I:   Core         Tool[A,B], ToolMeta, PassthroughTool
Type II:  Wrappers     TracedTool, CachedTool, RetryTool
Type III: Execution    ToolExecutor, CircuitBreaker, RetryExecutor
Type IV:  MCP          MCPClient, MCPTool, Transports
Type V:   Security     PermissionClassifier, AuditLogger
Type VI:  Orchestration ParallelOrchestrator, Supervisor, Handoff
```

### 2.2 Claude Code Tools → U-gent Mapping

| Claude Code Tool | U-gent Type | kgents Equivalent | Notes |
|------------------|-------------|-------------------|-------|
| **Read** | I (Core) | `ReadTool[FilePath, FileContent]` | + PDF, image, notebook handling |
| **Write** | I (Core) | `WriteTool[WriteRequest, WriteResult]` | Requires prior Read (causal) |
| **Edit** | I (Core) | `EditTool[EditRequest, EditResult]` | String replacement with uniqueness check |
| **Glob** | I (Core) | `GlobTool[Pattern, list[Path]]` | File pattern matching |
| **Grep** | I (Core) | `GrepTool[GrepQuery, GrepResults]` | Ripgrep wrapper with output modes |
| **Bash** | I (Core) + V (Security) | `BashTool[Command, CommandResult]` | + Sandbox, background, timeout |
| **LSP** | I (Core) | `LSPTool[LSPRequest, LSPResponse]` | 9 operations (goToDef, refs, hover...) |
| **WebFetch** | I (Core) + II (Wrapper) | `WebFetchTool[URL, WebContent]` | + CachedTool wrapper |
| **WebSearch** | I (Core) | `WebSearchTool[Query, SearchResults]` | + mandatory source citation |
| **TodoWrite** | IV (MCP-like) | `TaskTool[TaskList, TaskList]` | State management pattern |
| **Task** | VI (Orchestration) | `AgentSpawner[AgentSpec, AgentHandle]` | Subagent launcher |
| **TeammateTool** | VI (Orchestration) | `SwarmTool[SwarmOp, SwarmResult]` | 15+ operations |
| **MCPSearch** | IV (MCP) | Already U-gent Type IV | Deferred tool loading |
| **EnterPlanMode** | *New: Mode* | `ModeTool[ModeTransition, ModeState]` | Modal workflow |
| **AskUserQuestion** | *New: Interaction* | `ClarificationTool[Question, Answer]` | Human-in-loop |

### 2.3 New U-gent Types Needed

```
┌─────────────────────────────────────────────────────────────────┐
│              PROPOSED U-GENT TYPE EXTENSIONS                     │
│                                                                  │
│  Type VII: Modal                                                 │
│  ────────────────                                                │
│  ModeTool[Transition, State] — Modal workflow transitions        │
│  - EnterPlanMode, ExitPlanMode                                  │
│  - EnterSwarmMode, ExitSwarmMode                                │
│  - EnterTeachingMode, ExitTeachingMode                          │
│                                                                  │
│  Type VIII: Interaction                                          │
│  ─────────────────────                                           │
│  InteractionTool[Query, Response] — Human-in-loop patterns      │
│  - AskUserQuestion (structured options)                         │
│  - ApprovalGate (yes/no/modify)                                 │
│  - FeedbackCollector (rating + text)                            │
│                                                                  │
│  Type IX: Summarization                                          │
│  ──────────────────────                                          │
│  SummarizeTool[Content, Summary] — Context compression          │
│  - BashOutputSummarizer                                         │
│  - ConversationSummarizer                                       │
│  - WebContentSummarizer                                         │
│  - SentimentAnalyzer                                            │
│                                                                  │
│  Type X: Filesystem (Read-First Constraint)                      │
│  ──────────────────────────────────────────                      │
│  CausalTool[Op, Result] — Tools with causal dependencies        │
│  - Read → Write (causal chain)                                  │
│  - Read → Edit (causal chain)                                   │
│  - Enforces read-before-write at type level                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 Integration with AGENTESE

```python
# AGENTESE paths for U-gent tools

world.tools.file.read        # ReadTool
world.tools.file.write       # WriteTool
world.tools.file.edit        # EditTool
world.tools.file.glob        # GlobTool
world.tools.search.grep      # GrepTool
world.tools.search.lsp       # LSPTool
world.tools.system.bash      # BashTool
world.tools.web.fetch        # WebFetchTool
world.tools.web.search       # WebSearchTool
world.tools.mcp.discover     # MCPSearch
world.tools.mcp.invoke       # MCPTool

self.tools.task.list         # TaskList
self.tools.task.create       # TaskCreate
self.tools.task.update       # TaskUpdate
self.tools.mode.plan         # EnterPlanMode
self.tools.mode.execute      # ExitPlanMode
self.tools.swarm.spawn       # AgentSpawner
self.tools.swarm.coordinate  # SwarmTool
self.tools.clarify           # AskUserQuestion
```

```
┌─────────────────────────────────────────────────────────────────┐
│               TOOL CONTROL PLANE (REGISTRATION)                 │
│                                                                 │
│  services/tooling  ──►  world.tools.* (AGENTESE nodes)           │
│        │                     │                                  │
│        │                     ├─ Witness trust gate (L0-L3)       │
│        │                     ├─ Différance trace wrapper         │
│        │                     └─ Tool metadata + contracts        │
│        │                                                        │
│        └── emit events ─────► DataBus / SynergyBus               │
└─────────────────────────────────────────────────────────────────┘
```
Legend: control plane = registration, governance, and audit wiring.

### 2.5 Metaphysical Fullstack Alignment

Conservative alignment to existing projection patterns:

- **Service module**: house tool registry + executors in `services/tooling/`.
- **AGENTESE node**: expose `world.tools.*` from service module, not CLI handlers.
- **Projection surfaces**: rely on AGENTESE universal protocol for CLI/Web/API projections.
- **UI/telemetry**: stream tool lifecycle via EventBus to reactive widgets when needed.

---

## Part III: Reproducing Claude Code CLI Capabilities

```
┌─────────────────────────────────────────────────────────────────┐
│               TOOL DELIVERY PLANE (PROJECTIONS)                 │
│                                                                 │
│  world.tools.*  ──►  Projections                                 │
│        │                 │                                       │
│        │                 ├─ CLI                                  │
│        │                 ├─ Web                                  │
│        │                 └─ API                                  │
│        │                                                        │
│        └── emit events ──► EventBus (UI + streaming)             │
└─────────────────────────────────────────────────────────────────┘
```
Legend: delivery plane = user-facing projections and streaming.

```
SYSTEM DEPENDENCIES (EXISTING INFRASTRUCTURE)
- Witness trust gate (L0-L3) for tool invocation
- Différance tracing for audit + alternatives
- DataBus/EventBus/SynergyBus for lifecycle events
- AGENTESE universal protocol for projections
```

### 3.1 Minimal Viable Toolset

To reproduce Claude Code's core capabilities:

```
PHASE 1: CORE FILE OPS (Essential)
──────────────────────────────────
□ ReadTool[FilePath, FileContent]
  - Line numbers, offset/limit
  - PDF, image, notebook support
  - Directory detection (reject, suggest ls)

□ WriteTool[WriteRequest, WriteResult]
  - Requires prior Read (enforced)
  - Overwrite warning

□ EditTool[EditRequest, EditResult]
  - old_string/new_string replacement
  - Uniqueness check
  - replace_all option
□ AGENTESE node registration (world.tools.*)
  - Default CLI/Web/API projections via universal protocol
  - Witness trust gate (L0-L3) at invocation boundary
  - Différance trace emitted per invocation
  - Tool lifecycle events to DataBus/EventBus

PHASE 2: SEARCH (High Value)
────────────────────────────
□ GlobTool[Pattern, list[Path]]
  - Pattern matching (**/*.ts)
  - Modification time sorting

□ GrepTool[GrepQuery, GrepResults]
  - Ripgrep backend
  - Output modes: content, files_with_matches, count
  - Context lines (-A, -B, -C)
  - Multiline mode
□ Event hooks for search tooling
  - Emit tool.invoke.* events for UI + audit timelines

PHASE 3: SYSTEM (Power Features)
────────────────────────────────
□ BashTool[Command, CommandResult]
  - Timeout (default 120s, max 600s)
  - Background execution
  - Output truncation (30k chars)
  - Sandbox mode
  - Git safety protocols

□ WebFetchTool[URL, WebContent]
  - HTML → Markdown conversion
  - AI summarization
  - 15-minute cache
  - Redirect handling

PHASE 4: TASK MANAGEMENT
────────────────────────
□ TodoTool[TaskList, TaskList]
  - pending/in_progress/completed
  - activeForm (present continuous)
  - Single in_progress at a time
```

### 3.2 Implementation Strategy

```python
# File: impl/claude/agents/u/core_tools.py

from dataclasses import dataclass
from typing import TypeVar, Generic
from bootstrap.types import Agent
from protocols.agentese.registry import node
from protocols.agentese.contract import Contract, Response

# ═══════════════════════════════════════════════════════════════
# TYPE I: CORE TOOLS
# ═══════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FilePath:
    """Absolute path to a file."""
    path: str

    def __post_init__(self):
        if not self.path.startswith('/'):
            raise ValueError("Path must be absolute")

@dataclass
class FileContent:
    """Content read from a file."""
    content: str
    line_count: int
    truncated: bool = False
    metadata: dict | None = None  # For PDFs, images, notebooks

@dataclass
class ReadTool(Tool[FilePath, FileContent]):
    """
    Read file contents with line numbers.

    Category: Type I (Core)
    AGENTESE: world.tools.file.read
    """

    name: str = "read"

    async def invoke(self, input: FilePath) -> FileContent:
        # Implementation with PDF/image/notebook detection
        ...

# Read-Write Causal Chain (Type X)
@dataclass
class ReadState:
    """Proof that file was read."""
    path: FilePath
    content_hash: str
    read_at: float

@dataclass
class WriteRequest:
    """Write request with causal proof."""
    path: FilePath
    content: str
    read_proof: ReadState  # REQUIRED: Must have read first

@dataclass
class WriteTool(CausalTool[WriteRequest, WriteResult]):
    """
    Write file contents (requires prior Read).

    Category: Type I (Core) + Type X (Causal)
    AGENTESE: world.tools.file.write
    """

    async def invoke(self, input: WriteRequest) -> WriteResult:
        # Verify read_proof is valid and recent
        if not self._verify_read_proof(input.read_proof, input.path):
            raise CausalityViolation("Must read file before writing")
        ...
```

### 3.3 AGENTESE Node Registration

```python
# File: impl/claude/protocols/agentese/contexts/world_tools.py

from protocols.agentese.registry import node
from protocols.agentese.contract import Contract, Response

@node(
    "world.tools",
    description="U-gent Tool Infrastructure",
    contracts={
        "file.read": Contract(ReadRequest, FileContent),
        "file.write": Contract(WriteRequest, WriteResult),
        "file.edit": Contract(EditRequest, EditResult),
        "search.glob": Contract(GlobQuery, GlobResults),
        "search.grep": Contract(GrepQuery, GrepResults),
        "search.lsp": Contract(LSPQuery, LSPResult),
        "system.bash": Contract(BashCommand, BashResult),
        "web.fetch": Contract(FetchRequest, WebContent),
        "web.search": Contract(SearchQuery, SearchResults),
    },
    dependencies=("tool_executor", "permission_classifier"),
)
@dataclass
class ToolsNode(BaseLogosNode):
    """world.tools.* — Universal tool interface."""

    executor: ToolExecutor
    permissions: PermissionClassifier

    @aspect(
        category=AspectCategory.ACTION,
        effects=[Effect.READS("filesystem")],
    )
    async def file_read(self, observer: Umwelt, request: ReadRequest) -> FileContent:
        tool = ReadTool()
        return await self.executor.execute(tool, request, observer)
```

---

## Part IV: Beyond Claude Code — The Full Possibility Space

### 4.1 The Category of Agent-Tool Composition

Claude Code treats tools as **opaque function calls**. kgents treats them as **morphisms**:

```
┌─────────────────────────────────────────────────────────────────┐
│           CLAUDE CODE vs KGENTS TOOL MODEL                       │
│                                                                  │
│  CLAUDE CODE (Imperative):                                       │
│  ─────────────────────────                                       │
│  result = agent.call_tool("search", {"query": "..."})           │
│  result = agent.call_tool("summarize", {"text": result})        │
│  result = agent.call_tool("write", {"path": "...", ...})        │
│                                                                  │
│  KGENTS (Categorical):                                           │
│  ────────────────────                                            │
│  pipeline = search >> summarize >> write                         │
│  result = await pipeline.invoke(initial_input)                  │
│                                                                  │
│  Benefits:                                                       │
│  - Type safety (composition only if types align)                │
│  - Associativity ((f >> g) >> h = f >> (g >> h))               │
│  - Functorial lifting (Trace, Cache, Retry wrappers)            │
│  - Algebraic testing (MockAgent, SpyAgent, FlakyAgent)          │
│  - Parallel composition (f × g × h)                             │
│  - Fallback composition (f + g + h)                             │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Novel Tool Patterns (Beyond Claude Code)

#### Pattern A: Polynomial Tools

Tools with **mode-dependent behavior** (extending PolyAgent):

```python
class PolyTool[S, A, B](PolyAgent[S, A, B], Tool[A, B]):
    """
    Tool with mode-dependent input/output.

    Example: SearchTool that behaves differently in:
    - EXPLORE mode: broad, serendipitous results
    - PRECISE mode: exact matches only
    - VERIFY mode: fact-checking existing claims
    """

    def directions(self, state: S) -> type[A]:
        """Input type depends on state."""
        match state:
            case SearchMode.EXPLORE:
                return ExploratoryQuery
            case SearchMode.PRECISE:
                return ExactQuery
            case SearchMode.VERIFY:
                return VerificationQuery
```

#### Pattern B: Sheaf Tools

Tools with **local-global coherence**:

```python
class SheafTool[Q, R](Tool[Q, R]):
    """
    Tool that maintains coherence across local views.

    Example: CodebaseTool that:
    - Gives consistent answers across file queries
    - Detects when local edits break global invariants
    - Merges conflicting local views into coherent global state
    """

    async def query_local(self, path: str, query: Q) -> LocalSection[R]:
        """Query a single file/module."""
        ...

    async def glue_sections(self, sections: list[LocalSection[R]]) -> R:
        """Merge local sections into global response."""
        ...

    async def check_coherence(self) -> CoherenceReport:
        """Verify local views are compatible."""
        ...
```

#### Pattern C: Traced Tools (Différance)

Tools that remember **what almost was**:

```python
class DifferanceTool[A, B](Tool[A, B]):
    """
    Tool that tracks alternatives considered but not taken.

    Enables:
    - "Why did you choose X over Y?"
    - Time-travel to alternative branches
    - Ghost heritage graphs
    """

    async def invoke(self, input: A) -> Traced[B]:
        # Returns B + trace of alternatives
        ...

    async def explore_ghost(self, trace: WiringTrace) -> B:
        """Explore a path not taken."""
        ...
```

#### Pattern D: Flux Tools (Streaming)

Tools that operate on **continuous streams**:

```python
class FluxTool[A, B](Tool[Flux[A], Flux[B]]):
    """
    Tool lifted to streaming domain.

    Example: StreamingSearchTool that:
    - Yields results as they're found
    - Handles backpressure
    - Supports perturbation (query refinement mid-stream)
    """

    async def invoke(self, stream: Flux[A]) -> Flux[B]:
        async for item in stream:
            yield await self._process_item(item)

    async def perturb(self, perturbation: Perturbation) -> None:
        """Inject event into running stream."""
        ...
```

#### Pattern E: Operad-Validated Tools

Tools whose composition is **grammatically constrained**:

```python
TOOL_OPERAD = Operad(
    name="TOOL",
    operations={
        "seq": Operation(arity=2, ...),       # Sequential
        "par": Operation(arity="*", ...),     # Parallel
        "fallback": Operation(arity="*", ...), # Try until success
        "feedback": Operation(arity=2, ...),  # Iterative refinement
    },
    laws=[
        Law("seq_assoc", "(f;g);h = f;(g;h)"),
        Law("par_comm", "f||g = g||f"),
        Law("feedback_progress", "eventually terminates or yields"),
    ],
)

# Composition validated against operad
pipeline = TOOL_OPERAD.compose(
    "seq",
    [search_tool, summarize_tool, write_tool]
)
```

### 4.3 Crown Jewel Tool Integration

```
┌─────────────────────────────────────────────────────────────────┐
│          CROWN JEWEL ↔ TOOL INTEGRATION MATRIX                   │
│                                                                  │
│  BRAIN (Memory Cathedral)                                        │
│  └── CrystalTool: capture → associate → surface                 │
│  └── RecallTool: semantic search over crystals                  │
│                                                                  │
│  WITNESS (Autonomous Agency)                                     │
│  └── WatchTool: event-driven observation                        │
│  └── ActTool: trust-gated execution                             │
│  └── EscalateTool: human-in-loop for high-stakes                │
│                                                                  │
│  GARDENER (Cultivation Practice)                                 │
│  └── TendTool: observe, prune, graft, water, rotate, wait      │
│  └── SeasonTool: transition garden phases                       │
│                                                                  │
│  GESTALT (Living Code Garden)                                    │
│  └── DriftTool: detect semantic drift                           │
│  └── EvolveTool: safe codebase mutations                        │
│                                                                  │
│  ATELIER (Creative Workshop)                                     │
│  └── SketchTool: rapid prototyping                              │
│  └── CritiqueTool: aesthetic evaluation                         │
│                                                                  │
│  TOWN (Agent Simulation)                                         │
│  └── DialogueTool: citizen conversation                         │
│  └── CoalitionTool: agent collaboration                         │
│                                                                  │
│  PARK (Westworld Hosts)                                          │
│  └── InhabitTool: player inhabits citizen                       │
│  └── ScenarioTool: crisis/simulation control                    │
│                                                                  │
│  EMERGENCE (Cymatics Design)                                     │
│  └── PatternTool: select/tune/blend patterns                    │
│  └── QualiaTool: modulate experience parameters                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.4 The Meta-Tool: AGENTESE as Tool

The deepest insight: **AGENTESE itself is a tool**:

```python
class AgenteseTool(Tool[str, Any]):
    """
    Universal tool that invokes any AGENTESE path.

    This is the "one tool to rule them all" —
    every capability is accessible via path invocation.
    """

    async def invoke(self, path: str, **kwargs) -> Any:
        return await logos.invoke(path, self.observer, **kwargs)

# Example: Instead of 20 specialized tools
result = await agentese_tool.invoke("world.tools.file.read", path="/foo/bar")
result = await agentese_tool.invoke("self.memory.capture", content="...")
result = await agentese_tool.invoke("concept.gardener.tend", gesture="prune")
```

This collapses the tool zoo into a **single universal interface**.

### 4.5 Event-Driven Tool Substrate

Beyond request-response, tools can be **event-driven**:

```
┌─────────────────────────────────────────────────────────────────┐
│              EVENT-DRIVEN TOOL ARCHITECTURE                      │
│                                                                  │
│  DataBus (Storage Events)                                        │
│  └── PUT, DELETE, UPGRADE, DEGRADE                              │
│  └── Tools can subscribe to data changes                        │
│                                                                  │
│  SynergyBus (Cross-Jewel Events)                                 │
│  └── 60+ event types                                            │
│  └── Tools emit events on completion                            │
│  └── Other tools react to events                                │
│                                                                  │
│  Example: Auto-indexing Pipeline                                 │
│  ─────────────────────────────                                   │
│  WriteTool ──emit──► DataBus(PUT)                               │
│                          │                                       │
│                          ▼                                       │
│              MgentBusListener                                    │
│                          │                                       │
│                          ▼                                       │
│              IndexTool ──emit──► SynergyBus(INDEXED)            │
│                                       │                          │
│                                       ▼                          │
│                          SearchTool (cache invalidated)          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.6 The Teaching Tool Layer

Tools that explain themselves:

```python
class TeachingTool[A, B](Tool[A, B]):
    """
    Tool wrapper that adds explanations.

    When teaching_mode is enabled:
    - Explains why it's being invoked
    - Shows intermediate steps
    - Offers alternative approaches
    - Connects to conceptual foundations
    """

    async def invoke(self, input: A) -> Taught[B]:
        # Normal execution
        result = await self.inner.invoke(input)

        # Add teaching layer if enabled
        if self.teaching_enabled:
            explanation = await self._explain(input, result)
            alternatives = await self._suggest_alternatives(input)
            concepts = await self._link_concepts(input, result)

            return Taught(
                result=result,
                explanation=explanation,
                alternatives=alternatives,
                concepts=concepts,
            )

        return Taught(result=result)
```

---

## Part V: Implementation Roadmap

### Phase 0: Foundation (Week 1)

```
□ Create impl/claude/agents/u/ directory structure
□ Implement Tool[A,B] base class with >> composition
□ Implement PassthroughTool (identity)
□ Property tests for category laws
□ Integrate with existing Agent protocol
□ Register tool kernel as a service module (metaphysical fullstack)
□ Add AGENTESE node scaffolding for world.tools.* projections
□ Wire DataBus/EventBus emission hooks for tool lifecycle events
□ Add Différance integration wrapper for tool invocation traces
□ Define Witness trust gate for tool invocation (L0-L3)
```

### Phase 1: Core Tools (Week 2)

```
□ ReadTool with PDF/image/notebook support
□ WriteTool with causal constraint (requires Read)
□ EditTool with old_string/new_string
□ GlobTool with pattern matching
□ GrepTool with ripgrep backend
□ AGENTESE node registration (world.tools.*)
□ Default CLI + API projections via AGENTESE universal protocol
```

### Phase 2: System Tools (Week 3)

```
□ BashTool with safety protocols
□ WebFetchTool with caching
□ WebSearchTool with source citation
□ LSPTool with 9 operations
□ Sandbox mode implementation
□ Trust + trace integration for system tools
  - Witness gates before external side effects
  - Différance records rejected alternatives
```

### Phase 3: Orchestration (Week 4)

```
□ TodoTool (task management)
□ AgentSpawner (subagent launch)
□ SwarmTool (team coordination)
□ ModeTool (plan/execute modal)
□ ClarificationTool (human-in-loop)
```

### Phase 4: Advanced Patterns (Week 5+)

```
□ PolyTool (mode-dependent behavior)
□ SheafTool (local-global coherence)
□ DifferanceTool (ghost tracking)
□ FluxTool (streaming)
□ Operad validation
□ Teaching layer
```

---

## Part VI: Open Questions

### Q1: Tool vs. Aspect vs. Agent

When is something a **tool** vs. an **aspect** vs. an **agent**?

```
CURRENT THINKING:

Tool    = External interaction (filesystem, web, system)
Aspect  = AGENTESE affordance (perception, action, introspection)
Agent   = Autonomous entity with state and judgment

Tool ⊂ Agent (tools are specialized agents)
Aspect ↔ Tool (aspects may invoke tools)

The line blurs when everything is a morphism.
```

### Q2: Permission Granularity

Claude Code has coarse permissions (read-only subagents). How fine-grained should kgents be?

```
OPTIONS:

A) Per-tool (can use ReadTool but not WriteTool)
B) Per-path (can access /src/** but not /secrets/**)
C) Per-capability (can read but not delete)
D) Per-context (higher trust in interactive, lower in automated)
E) Categorical (subobject classifier as in U-gent spec)

RECOMMENDATION: (D) + (E) — Context-aware with categorical foundation.
```

### Q3: Causality Enforcement

The read-before-write pattern is useful. How to generalize?

```
GENERALIZATION:

CausalTool[A, B, Proof] where Proof = evidence of prerequisite

Examples:
- WriteTool requires ReadProof
- CommitTool requires TestsPassedProof
- PushTool requires ReviewApprovedProof
- DeployTool requires StagingSuccessProof

This is dependent types for tools.
```

### Q4: MCP Integration Depth

Claude Code uses MCP but wraps it. How deep should kgents integrate?

```
OPTIONS:

A) MCP as external protocol (thin wrapper)
B) MCP as native U-gent type (Type IV currently)
C) kgents tools exposed AS MCP servers
D) Bidirectional (kgents ↔ MCP)

RECOMMENDATION: (D) — kgents as both MCP client AND server.
Full interoperability with the ecosystem.
```

---

## Conclusion

Claude Code's tool infrastructure is **well-engineered but imperative**. kgents has the opportunity to go beyond by treating tools as **first-class morphisms** in the agent category.

The key innovations:

1. **Categorical Composition**: Tools compose via `>>` with verified laws
2. **Type-Safe Causality**: Read-before-write as dependent types
3. **Polynomial Tools**: Mode-dependent behavior
4. **Sheaf Coherence**: Local-global consistency
5. **Différance Tracing**: Ghost heritage for explainability
6. **AGENTESE Universality**: One path-based interface for all tools
7. **Event-Driven Substrate**: Reactive tool pipelines
8. **Teaching Layer**: Tools that explain themselves

The Mirror Test: *Does this feel like Kent on his best day?*

This design is **daring** (categorical foundations), **bold** (beyond Claude Code), **creative** (novel patterns), and **opinionated** (tools as morphisms, not functions) — but not gaudy. It builds on what works while exploring the full possibility space.

---

*"A tool is not an external function. It is an agent with a contract."*

— U-gent Philosophy
