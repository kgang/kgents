# U-gent Tool Infrastructure Specification

> *"A tool is not an external function. It is an agent with a contract."*

**Status**: Draft
**Date**: 2025-12-20
**Source**: brainstorming/2025-12-20-ugent-tool-infrastructure-claude-code-audit.md

---

## 1. Overview

This specification defines the U-gent Tool Infrastructure for kgents, drawing from
a comprehensive audit of Claude Code's 21-tool system while aligning with existing
kgents categorical foundations.

### Design Philosophy

The key insight from Claude Code: **tools are well-engineered but imperative**.
The kgents opportunity: **tools as first-class morphisms** in the agent category.

```
CLAUDE CODE MODEL                    KGENTS MODEL
-----------------                    ------------
result = agent.call_tool(...)        pipeline = search >> summarize >> write
result = agent.call_tool(...)  vs    result = await pipeline.invoke(input)
result = agent.call_tool(...)

Imperative, sequential               Categorical, composable
```

### Minimal Surface Area Principle

This spec adds NO new categorical primitives. It reuses:

| Existing System | Role in Tooling |
|-----------------|-----------------|
| AGENTESE | Protocol IS the API (`world.tools.*`) |
| Witness | Trust gates (L0-L3), audit trail |
| Differance | Trace capture, ghost alternatives |
| DataBus/EventBus | Tool lifecycle events |
| SynergyBus | Cross-jewel tool coordination |

---

## 2. Architecture Overview

```
+-----------------------------------------------------------------------+
|                      TOOL INFRASTRUCTURE                               |
+-----------------------------------------------------------------------+
|                                                                       |
|  CONTROL PLANE (Registration + Governance)                            |
|  -----------------------------------------                            |
|                                                                       |
|  services/tooling/               protocols/agentese/contexts/         |
|       |                                    |                          |
|       +-- registry.py                      +-- world_tools.py         |
|       |   (ToolRegistry, ToolMeta)              (@node for world.tools.*) |
|       |                                                               |
|       +-- executor.py                Witness Integration:             |
|       |   (ToolExecutor, CircuitBreaker)   - Trust gate before invoke |
|       |                                    - Audit entry after invoke |
|       +-- wrappers.py                                                 |
|           (TracedTool, CachedTool,   Differance Integration:          |
|            RetryTool, SandboxedTool)  - Trace per invocation          |
|                                       - Ghost alternatives recorded   |
+-----------------------------------------------------------------------+
|                                                                       |
|  DELIVERY PLANE (Projections + Streaming)                             |
|  ----------------------------------------                             |
|                                                                       |
|  world.tools.*  --->  AGENTESE Universal Protocol                     |
|       |                    |                                          |
|       |                    +-- CLI (default projection)               |
|       |                    +-- Web (via API)                          |
|       |                    +-- API (JSON responses)                   |
|       |                                                               |
|       +---> EventBus (tool.invoke.*, tool.complete.*)                 |
|                 |                                                     |
|                 +-- UI streaming                                      |
|                 +-- Audit timeline                                    |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## 3. Tool Type Taxonomy

Mapping Claude Code's implicit types to kgents categorical structure:

### Type I: Core Tools

```python
Tool[A, B] = Agent[A, B] with contract
```

| Tool | Input Type | Output Type | Effects |
|------|-----------|-------------|---------|
| ReadTool | FilePath | FileContent | READS(filesystem) |
| WriteTool | WriteRequest | WriteResult | WRITES(filesystem) |
| EditTool | EditRequest | EditResult | WRITES(filesystem) |
| GlobTool | GlobQuery | list[Path] | READS(filesystem) |
| GrepTool | GrepQuery | GrepResults | READS(filesystem) |
| BashTool | Command | CommandResult | CALLS(shell) |
| WebFetchTool | URL | WebContent | CALLS(network) |
| WebSearchTool | Query | SearchResults | CALLS(network) |

### Type II: Wrappers (Functorial Lifting)

```python
TracedTool[A, B]   = Tool[A, Traced[B]]     # Differance integration
CachedTool[A, B]   = Tool[A, B] + TTL cache # Time-bounded memoization
RetryTool[A, B]    = Tool[A, B] + backoff   # Resilience
SandboxedTool[A, B] = Tool[A, B] + sandbox  # Isolation
```

### Type III: Execution Infrastructure

```python
ToolExecutor      # Async execution with timeout, tracing
CircuitBreaker    # Failure isolation
RetryExecutor     # Exponential backoff
```

### Type IV: Causal Tools (Read-Before-Write)

The read-before-write pattern generalized:

```python
@dataclass
class CausalTool[P, A, B]:
    """Tool requiring proof of prerequisite."""
    proof_type: type[P]

@dataclass
class WriteRequest:
    path: FilePath
    content: str
    read_proof: ReadProof  # REQUIRED: evidence file was read

# Type enforces causality at compile time
write_tool: CausalTool[ReadProof, WriteRequest, WriteResult]
```

### Type V: Modal Tools

```python
@dataclass
class ModeTool[T, S]:
    """Tool for modal workflow transitions."""
    from_mode: T
    to_mode: T
    approval_required: bool
```

---

## 4. AGENTESE Integration

### Path Structure

```
world.tools.*         -- External tool interface
    |
    +-- file.*        -- Filesystem operations
    |   +-- read      -- ReadTool
    |   +-- write     -- WriteTool (requires read proof)
    |   +-- edit      -- EditTool (requires read proof)
    |   +-- glob      -- GlobTool
    |   +-- notebook  -- NotebookEditTool
    |
    +-- search.*      -- Search operations
    |   +-- grep      -- GrepTool
    |   +-- lsp       -- LSPTool (if available)
    |
    +-- system.*      -- System interaction
    |   +-- bash      -- BashTool (sandboxed by default)
    |   +-- kill      -- KillShellTool
    |
    +-- web.*         -- Network operations
        +-- fetch     -- WebFetchTool (cached)
        +-- search    -- WebSearchTool

self.tools.*          -- Task/workflow tools
    |
    +-- task.*        -- Task management
    |   +-- list      -- List current tasks
    |   +-- create    -- Create task
    |   +-- update    -- Update task status
    |
    +-- mode.*        -- Modal transitions
    |   +-- plan      -- Enter plan mode
    |   +-- execute   -- Exit plan mode
    |
    +-- clarify       -- AskUserQuestion equivalent
```

### Node Registration

```python
# protocols/agentese/contexts/world_tools.py

from protocols.agentese.registry import node
from protocols.agentese.contract import Contract, Response

@node(
    "world.tools",
    description="U-gent Tool Infrastructure",
    dependencies=("tool_executor", "witness_persistence"),
    contracts={
        "file.read": Contract(ReadRequest, FileContent),
        "file.write": Contract(WriteRequest, WriteResult),
        "file.edit": Contract(EditRequest, EditResult),
        "search.grep": Contract(GrepQuery, GrepResults),
        "system.bash": Contract(BashCommand, BashResult),
        "web.fetch": Contract(FetchRequest, WebContent),
    },
)
@dataclass
class ToolsNode(BaseLogosNode):
    """world.tools.* -- Universal tool interface."""

    executor: ToolExecutor
    witness: WitnessPersistence  # For audit trail

    @aspect(
        category=AspectCategory.ACTION,
        effects=[Effect.READS("filesystem")],
    )
    async def file_read(
        self, observer: Umwelt, request: ReadRequest
    ) -> FileContent:
        # Trust gate check via Witness
        await self._check_trust(observer, TrustLevel.L1)

        # Execute with tracing
        result = await self.executor.execute(
            ReadTool(), request, observer
        )

        # Emit event for UI/audit
        await self._emit_tool_event("file.read", request, result)

        return result
```

---

## 5. Trust Gate Integration

Tools integrate with existing Witness trust levels:

| Trust Level | Tool Access | Examples |
|-------------|-------------|----------|
| L0 (READ_ONLY) | Read-only tools | ReadTool, GlobTool, GrepTool |
| L1 (BOUNDED) | Writes to safe paths | WriteTool (.kgents/ only) |
| L2 (SUGGESTION) | Propose, require confirm | WriteTool (any path, confirmed) |
| L3 (AUTONOMOUS) | Full access | All tools, unconfirmed |

```python
# services/tooling/trust_gate.py

from services.witness import TrustLevel, ActionGate

class ToolTrustGate:
    """Trust gate integration for tools."""

    TOOL_REQUIREMENTS: dict[str, TrustLevel] = {
        "file.read": TrustLevel.L0,
        "file.write": TrustLevel.L2,
        "file.edit": TrustLevel.L2,
        "search.grep": TrustLevel.L0,
        "system.bash": TrustLevel.L3,  # Highest trust required
        "web.fetch": TrustLevel.L1,
        "web.search": TrustLevel.L1,
    }

    async def check(
        self,
        tool_path: str,
        observer: Umwelt,
    ) -> GateResult:
        required = self.TOOL_REQUIREMENTS.get(tool_path, TrustLevel.L3)
        current = await self._get_trust_level(observer)

        if current >= required:
            return GateResult(allowed=True)

        # L2 can proceed with confirmation
        if current == TrustLevel.L2 and required == TrustLevel.L2:
            return GateResult(
                allowed=False,
                requires_confirmation=True,
                message=f"Tool {tool_path} requires confirmation",
            )

        return GateResult(
            allowed=False,
            message=f"Trust level {current} insufficient for {tool_path}",
        )
```

---

## 6. Differance Integration

Every tool invocation produces a trace:

```python
# services/tooling/trace_wrapper.py

from agents.differance import WiringTrace, Alternative, DifferanceStore

class TracedToolExecutor:
    """Wraps tool execution with Differance tracing."""

    def __init__(self, executor: ToolExecutor, store: DifferanceStore):
        self.executor = executor
        self.store = store

    async def execute(
        self,
        tool: Tool[A, B],
        input: A,
        observer: Umwelt,
        alternatives: list[Alternative] | None = None,
    ) -> Traced[B]:
        # Create trace before execution
        trace_id = generate_trace_id()
        start_time = time.monotonic()

        # Execute tool
        try:
            result = await self.executor.execute(tool, input, observer)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        # Create trace
        trace = WiringTrace(
            id=trace_id,
            path=f"world.tools.{tool.name}",
            input=input,
            output=result,
            success=success,
            error=error,
            duration_ms=(time.monotonic() - start_time) * 1000,
            alternatives=alternatives or [],
            timestamp=datetime.now(UTC),
        )

        # Store trace
        await self.store.record(trace)

        # Emit event for UI
        await self._emit_trace_event(trace)

        return Traced(result=result, trace=trace)
```

---

## 7. Event Emission

Tools emit events through the existing bus infrastructure:

```python
# services/tooling/events.py

from protocols.synergy import SynergyEventType, create_synergy_event

# New event types (extend SynergyEventType enum)
TOOL_INVOKED = "tool.invoked"
TOOL_COMPLETED = "tool.completed"
TOOL_FAILED = "tool.failed"
TOOL_TRUST_DENIED = "tool.trust_denied"

async def emit_tool_event(
    bus: SynergyBus,
    event_type: str,
    tool_path: str,
    input_summary: str,
    result_summary: str | None,
    duration_ms: float,
    trust_level: TrustLevel,
) -> None:
    """Emit tool lifecycle event to SynergyBus."""
    event = create_synergy_event(
        event_type=event_type,
        source=f"world.tools.{tool_path}",
        payload={
            "tool_path": tool_path,
            "input": input_summary,
            "result": result_summary,
            "duration_ms": duration_ms,
            "trust_level": trust_level.name,
        },
    )
    await bus.emit(event)
```

---

## 8. File Targets

### Control Plane (Registration + Governance)

| File | Purpose |
|------|---------|
| `services/tooling/__init__.py` | Package exports |
| `services/tooling/registry.py` | ToolRegistry, ToolMeta |
| `services/tooling/executor.py` | ToolExecutor, CircuitBreaker |
| `services/tooling/wrappers.py` | TracedTool, CachedTool, RetryTool |
| `services/tooling/trust_gate.py` | Trust level checking |
| `services/tooling/events.py` | Event emission |
| `services/tooling/contracts.py` | Request/Response dataclasses |

### Delivery Plane (AGENTESE Nodes)

| File | Purpose |
|------|---------|
| `protocols/agentese/contexts/world_tools.py` | @node for world.tools.* |
| `protocols/agentese/contexts/self_tools.py` | @node for self.tools.* |

### Tool Implementations

| File | Purpose |
|------|---------|
| `services/tooling/tools/read.py` | ReadTool implementation |
| `services/tooling/tools/write.py` | WriteTool implementation |
| `services/tooling/tools/edit.py` | EditTool implementation |
| `services/tooling/tools/glob.py` | GlobTool implementation |
| `services/tooling/tools/grep.py` | GrepTool implementation |
| `services/tooling/tools/bash.py` | BashTool implementation |
| `services/tooling/tools/web.py` | WebFetchTool, WebSearchTool |

---

## 9. Composition Laws

Tools must satisfy category laws (verified via BootstrapWitness):

```python
# Identity Law
Id >> tool == tool == tool >> Id

# Associativity Law
(tool_a >> tool_b) >> tool_c == tool_a >> (tool_b >> tool_c)

# Read-Before-Write (Causal Law)
write(path, content) REQUIRES read(path) in causal history
```

---

## 10. Safety Protocols

### Bash Safety (from Claude Code)

```python
BASH_NEVER:
- Update git config
- Force push to main/master
- Skip hooks (--no-verify)
- Use interactive flags (-i)
- Amend pushed commits
- Commit secrets

BASH_ALWAYS:
- Use HEREDOC for commit messages
- Check authorship before amend
- Verify commit not pushed before amend
- Run git status after commit
```

### Sandbox Mode

```python
class SandboxedBashTool:
    """BashTool with sandbox isolation."""

    sandbox_enabled: bool = True
    allowed_commands: set[str] = {"git", "npm", "pytest", "mypy"}
    denied_patterns: list[str] = [
        "rm -rf /",
        "sudo",
        "chmod 777",
        "> /etc/",
    ]
```

---

## 11. Open Questions

### Q1: Tool vs. Aspect vs. Agent Boundary

When is functionality a **tool** vs. an **AGENTESE aspect** vs. a full **agent**?

**Current position**: Tools are aspects of the `world.tools` node. They become
agents when they require persistent state or mode-dependent behavior (PolyAgent).

**Needs resolution before**: Phase 1 implementation

### Q2: Causal Proof Persistence

How long should ReadProof remain valid for a WriteTool invocation?

**Options**:
- A) Session-scoped (proof valid for current session)
- B) Time-bounded (proof expires after N seconds)
- C) Hash-verified (proof valid if file unchanged)

**Recommendation**: (C) with (B) as fallback

**Needs resolution before**: Phase 1 WriteRequest implementation

### Q3: Ghost Recording Granularity

How much alternative information should Differance capture for tool traces?

**Options**:
- A) Minimal (just input/output)
- B) Medium (+ rejected alternatives)
- C) Full (+ all considered options, timing, internal state)

**Recommendation**: (B) by default, (C) opt-in for debugging

**Needs resolution before**: Phase 0 Differance integration

### Q4: MCP Bidirectional Support

Should kgents tools be exposed AS MCP servers for external tool discovery?

**Current position**: Yes, but Phase 2+ (after core tools stable)

**Needs resolution before**: Phase 2 planning

### Q5: Parallel Execution Semantics

When tools execute in parallel, how should failures be handled?

**Options**:
- A) Fail-fast (abort all on first failure)
- B) Collect-all (wait for all, report all failures)
- C) Configurable per-pipeline

**Recommendation**: (C) with (B) as default

**Needs resolution before**: Phase 3 orchestration

---

## Related

- `spec/protocols/agentese.md` -- AGENTESE universal protocol
- `spec/protocols/differance.md` -- Trace capture
- `docs/skills/metaphysical-fullstack.md` -- Architecture pattern
- `docs/skills/crown-jewel-patterns.md` -- Implementation patterns
- `docs/skills/agentese-node-registration.md` -- Node registration

---

*"Daring, bold, creative, opinionated but not gaudy"*

