# U-gent Tool Infrastructure Implementation Plan

> *"Tasteful > feature-complete; Joy-inducing > merely functional"*

**Status**: Phase 0 Complete ✓
**Date**: 2025-12-20
**Spec**: spec/services/tooling.md
**Source**: brainstorming/2025-12-20-ugent-tool-infrastructure-claude-code-audit.md

---

## Progress

| Phase | Status | Handoff |
|-------|--------|---------|
| Phase 0: Foundation | ✓ Complete | `ugent-tooling-phase0-handoff.md` |
| Phase 1: Core Tools | ✓ Complete | `ugent-tooling-phase1-handoff.md` |
| Phase 2: System Tools | Blocked on P1 | — |
| Phase 3: Orchestration | Blocked on P2 | — |
| Phase 4: Advanced | Research Complete | `ugent-tooling-phase4-advanced.md` |

**Key Discovery**: Core file tools already exist in `services/conductor/file_guard.py`.
Phase 1 is now an **adapter pattern** exercise, not reimplementation.

---

## Executive Summary

This plan translates the U-gent Tool Infrastructure spec into a phased implementation
that maximizes reuse of existing kgents systems. The goal is to reproduce Claude Code's
core tool capabilities while adding categorical composition and trust-gated execution.

**Key Constraint**: Minimal new surface area. Reuse AGENTESE, Witness, Differance, DataBus.

---

## Phase 0: Foundation (Control Plane Setup)

**Duration**: 1 week
**Owner**: Infrastructure

### Objectives

1. Create service module skeleton
2. Define core types (Tool[A,B], ToolMeta, ToolRegistry)
3. Wire Witness trust gate integration
4. Wire Differance trace integration
5. Add AGENTESE node scaffolding

### Deliverables

```
services/tooling/
    __init__.py           # Package exports
    registry.py           # ToolRegistry, ToolMeta
    executor.py           # ToolExecutor (async with timeout)
    trust_gate.py         # Witness integration
    trace_wrapper.py      # Differance integration
    events.py             # SynergyBus event emission
    contracts.py          # Request/Response dataclasses (Pattern 13)

protocols/agentese/contexts/
    world_tools.py        # @node("world.tools") skeleton
    self_tools.py         # @node("self.tools") skeleton
```

### Control Plane Wiring

```
services/tooling/registry.py
        |
        v
services/providers.py
    +-- get_tool_registry()
    +-- get_tool_executor()
        |
        v
protocols/agentese/contexts/world_tools.py
    @node("world.tools", dependencies=("tool_registry", "tool_executor"))
```

### Dependencies to Register (providers.py)

```python
# Add to services/providers.py

async def get_tool_registry() -> "ToolRegistry":
    from services.tooling import ToolRegistry
    return ToolRegistry()

async def get_tool_executor() -> "ToolExecutor":
    from services.tooling import ToolExecutor
    from services.witness import get_witness_persistence
    from agents.differance import get_differance_store
    witness = await get_witness_persistence()
    differance = await get_differance_store()
    return ToolExecutor(witness=witness, differance=differance)

# In setup_providers():
container.register("tool_registry", get_tool_registry, singleton=True)
container.register("tool_executor", get_tool_executor, singleton=True)
```

### Success Criteria

- [ ] `from services.tooling import ToolRegistry, ToolExecutor` works
- [ ] `@node("world.tools")` appears in `/agentese/discover`
- [ ] Property tests verify Tool[A,B] category laws
- [ ] Trust gate blocks L0 observer from write operations
- [ ] Differance trace emitted on any tool invocation
- [ ] SynergyBus receives `tool.invoked` events

### Tests

```
services/tooling/_tests/
    test_registry.py      # ToolRegistry CRUD
    test_executor.py      # Timeout, async execution
    test_trust_gate.py    # L0-L3 access control
    test_trace.py         # Differance integration
    test_category_laws.py # Identity, associativity
```

---

## Phase 1: Core Tools (Delivery Plane)

**Duration**: 1 week
**Owner**: Infrastructure
**Depends on**: Phase 0

### Objectives

1. Implement ReadTool, WriteTool, EditTool, GlobTool, GrepTool
2. Wire AGENTESE aspects for each tool
3. Default CLI/API projections via universal protocol
4. Read-before-write causal constraint

### Deliverables

```
services/tooling/tools/
    __init__.py
    read.py               # ReadTool (PDF, image, notebook support)
    write.py              # WriteTool (causal constraint)
    edit.py               # EditTool (old_string/new_string)
    glob.py               # GlobTool (pattern matching)
    grep.py               # GrepTool (ripgrep backend)
```

### Causal Constraint Implementation

```python
# services/tooling/tools/write.py

@dataclass(frozen=True)
class ReadProof:
    """Evidence that file was read before write."""
    path: FilePath
    content_hash: str
    read_at: datetime
    session_id: str

    def is_valid(self, target_path: FilePath) -> bool:
        if self.path != target_path:
            return False
        # Proof expires after 1 hour
        if datetime.now(UTC) - self.read_at > timedelta(hours=1):
            return False
        return True

@dataclass
class WriteRequest:
    path: FilePath
    content: str
    read_proof: ReadProof  # REQUIRED

class WriteTool(Tool[WriteRequest, WriteResult]):
    async def invoke(self, request: WriteRequest) -> WriteResult:
        if not request.read_proof.is_valid(request.path):
            raise CausalityViolation("Must read file before writing")
        # Verify hash unchanged (file not modified since read)
        current_hash = await self._compute_hash(request.path)
        if current_hash != request.read_proof.content_hash:
            raise CausalityViolation("File modified since read")
        # Proceed with write
        ...
```

### AGENTESE Aspect Wiring

```python
# protocols/agentese/contexts/world_tools.py

@node(
    "world.tools",
    description="U-gent Tool Infrastructure",
    dependencies=("tool_executor",),
    contracts={
        "file.read": Contract(ReadRequest, FileContent),
        "file.write": Contract(WriteRequest, WriteResult),
        "file.edit": Contract(EditRequest, EditResult),
        "search.glob": Contract(GlobQuery, list[Path]),
        "search.grep": Contract(GrepQuery, GrepResults),
    },
)
@dataclass
class ToolsNode(BaseLogosNode):
    executor: ToolExecutor

    @aspect(category=AspectCategory.ACTION, effects=[Effect.READS("filesystem")])
    async def file_read(self, observer: Umwelt, request: ReadRequest) -> FileContent:
        return await self.executor.execute(ReadTool(), request, observer)

    @aspect(category=AspectCategory.ACTION, effects=[Effect.WRITES("filesystem")])
    async def file_write(self, observer: Umwelt, request: WriteRequest) -> WriteResult:
        # Trust gate: L2+ required
        await self.executor.check_trust(observer, TrustLevel.L2)
        return await self.executor.execute(WriteTool(), request, observer)
```

### Success Criteria

- [ ] `logos.invoke("world.tools.file.read", ...)` returns FileContent
- [ ] WriteTool rejects requests without valid ReadProof
- [ ] EditTool applies old_string/new_string replacement
- [ ] GlobTool returns sorted paths by modification time
- [ ] GrepTool supports content/files_with_matches/count modes
- [ ] All tools emit Differance traces
- [ ] CLI projection works: `kg tools file read /path/to/file`

---

## Phase 2: System Tools

**Duration**: 1 week
**Owner**: Infrastructure
**Depends on**: Phase 1

### Objectives

1. Implement BashTool with safety protocols
2. Implement WebFetchTool with caching
3. Implement WebSearchTool with source citation
4. Sandbox mode for untrusted execution

### Deliverables

```
services/tooling/tools/
    bash.py               # BashTool (sandboxed, safety protocols)
    web.py                # WebFetchTool, WebSearchTool
    sandbox.py            # Sandbox isolation layer
```

### BashTool Safety Implementation

```python
# services/tooling/tools/bash.py

class BashTool(Tool[BashCommand, BashResult]):
    NEVER_PATTERNS: ClassVar[list[str]] = [
        r"git config.*--global",
        r"git push.*--force",
        r"git.*--no-verify",
        r"rm -rf /",
        r"sudo ",
        r"> /etc/",
    ]

    REQUIRE_TRUST_L3: ClassVar[list[str]] = [
        r"git push",
        r"npm publish",
        r"docker push",
    ]

    async def invoke(self, command: BashCommand) -> BashResult:
        # Safety check: reject dangerous patterns
        for pattern in self.NEVER_PATTERNS:
            if re.search(pattern, command.command):
                raise SafetyViolation(f"Command matches forbidden pattern: {pattern}")

        # Timeout enforcement
        timeout = min(command.timeout_ms, 600_000)  # Max 10 minutes

        # Execute with output truncation
        result = await self._execute(command.command, timeout)
        if len(result.stdout) > 30_000:
            result = result._replace(
                stdout=result.stdout[:30_000] + "\n... (truncated)",
                truncated=True,
            )

        return result
```

### Trust Gate for System Tools

```python
# System tools require highest trust
TOOL_TRUST_REQUIREMENTS = {
    "system.bash": TrustLevel.L3,
    "system.kill": TrustLevel.L2,
    "web.fetch": TrustLevel.L1,
    "web.search": TrustLevel.L1,
}
```

### Success Criteria

- [ ] BashTool rejects dangerous commands
- [ ] BashTool respects timeout (default 2min, max 10min)
- [ ] WebFetchTool caches for 15 minutes
- [ ] WebSearchTool includes mandatory source URLs
- [ ] L3 trust required for BashTool execution
- [ ] Differance records all alternatives considered

---

## Phase 3: Orchestration Tools

**Duration**: 1 week
**Owner**: Infrastructure
**Depends on**: Phase 2

### Objectives

1. Implement TodoTool (task management)
2. Implement ModeTool (plan/execute modal)
3. Implement ClarificationTool (human-in-loop)
4. Parallel tool execution with dependency resolution

### Deliverables

```
services/tooling/tools/
    task.py               # TodoTool, TaskList
    mode.py               # ModeTool (EnterPlanMode, ExitPlanMode)
    clarify.py            # ClarificationTool

services/tooling/
    orchestrator.py       # Parallel execution, dependency resolution
    pipeline.py           # Tool pipeline composition
```

### Tool Pipeline Composition

```python
# services/tooling/pipeline.py

@dataclass
class ToolPipeline:
    """Composable tool pipeline via >> operator."""
    steps: list[Tool]

    def __rshift__(self, other: Tool) -> "ToolPipeline":
        return ToolPipeline(steps=self.steps + [other])

    async def invoke(self, input: Any, observer: Umwelt) -> Any:
        result = input
        for step in self.steps:
            result = await step.invoke(result)
        return result

# Usage:
pipeline = read_tool >> grep_tool >> summarize_tool
result = await pipeline.invoke(initial_input, observer)
```

### Success Criteria

- [ ] TodoTool maintains task state with pending/in_progress/completed
- [ ] ModeTool transitions between plan and execute modes
- [ ] ClarificationTool presents structured options to user
- [ ] Pipeline composition verifies type alignment
- [ ] Parallel execution respects dependency order

---

## Phase 4: Advanced Patterns

**Duration**: 5.5 weeks
**Owner**: TBD
**Depends on**: Phase 3
**Full Spec**: `plans/ugent-tooling-phase4-advanced.md`

### Overview

Phase 4 has been expanded from a deferred bucket into five distinct implementation phases,
informed by comprehensive research synthesis of 2024-2025 cutting-edge developments in:

- Polynomial functors (Spivak/Niu)
- Chain-of-thought transparency
- Streaming and progressive disclosure
- MCP bidirectional protocol
- Formal verification for AI agents

### Sub-Phases

| Phase | Name | Duration | Core Insight |
|-------|------|----------|--------------|
| 4A | PolyTool | 1.5 weeks | Mode-dependent tool behavior (Spivak polynomial functors) |
| 4B | SheafTool | 1 week | Local-global coherence for distributed execution |
| 4C | FluxTool + Teaching | 1.5 weeks | Streaming + introspection fusion |
| 4D | MCP Bridge | 1 week | Bidirectional tool discovery |
| 4E | Formal Verification | 0.5 weeks | Static pipeline validation |

### Key Deliverables

1. **PolyTool** — Mode-dependent tool behavior with mode escalation (PATCH → SMART → OVERWRITE)
2. **SheafTool** — Multi-file operations with coherence guarantees
3. **FluxTool** — Streaming partial results + teaching explanations
4. **MCP Bridge** — kgents tools exposed as MCP servers for external discovery
5. **Verification** — Static pipeline validation via operad laws

### Research Sources

See `plans/ugent-tooling-phase4-advanced.md` for comprehensive research synthesis including:

- [Polynomial Functors](https://arxiv.org/abs/2312.00990) — Niu & Spivak (2025)
- [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) — Anthropic
- [Model Context Protocol](https://modelcontextprotocol.io/) — MCP specification
- [Formal Verification for AI Agents](https://martin.kleppmann.com/2025/12/08/ai-formal-verification.html) — Kleppmann

---

## Dependency Order

```
          Phase 0: Foundation
                |
    +-----------+-----------+
    |                       |
    v                       v
Phase 1: Core Tools    (Witness integration)
    |                       |
    +----------+------------+
               |
               v
        Phase 2: System Tools
               |
               v
        Phase 3: Orchestration
               |
               v
        Phase 4: Advanced Patterns
               |
    +----------+----------+----------+
    |          |          |          |
    v          v          v          v
  4A:       4B:        4C:        4D:
PolyTool  SheafTool  FluxTool   MCP Bridge
    |          |          |          |
    +----------+----------+----------+
               |
               v
            4E: Formal Verification
```

See `plans/ugent-tooling-phase4-advanced.md` for detailed Phase 4 breakdown.

---

## Gap Analysis

### What Exists (Reuse)

| System | Status | Role in Tooling |
|--------|--------|-----------------|
| AGENTESE | 100% | Protocol IS the API |
| @node decorator | 100% | Node registration |
| Witness trust | 100% | L0-L3 trust gates |
| Witness persistence | 100% | Audit trail |
| Differance store | 100% | Trace capture |
| Differance trace | 100% | Ghost alternatives |
| SynergyBus | 100% | Event emission |
| DataBus | 100% | Storage events |
| contracts.py pattern | 100% | Type-safe request/response |

### What's Missing (New Code)

| Component | Priority | Effort |
|-----------|----------|--------|
| services/tooling/ skeleton | P0 | Small |
| Tool[A,B] base class | P0 | Small |
| ToolExecutor | P0 | Medium |
| ToolTrustGate | P0 | Small |
| TracedToolExecutor | P0 | Small |
| ReadTool | P1 | Medium |
| WriteTool + causal | P1 | Medium |
| EditTool | P1 | Small |
| GlobTool | P1 | Small |
| GrepTool | P1 | Medium |
| BashTool + safety | P2 | Large |
| Sandbox layer | P2 | Medium |
| WebFetchTool | P2 | Medium |
| Pipeline composition | P3 | Medium |

### What's Ambiguous (Needs Decision)

| Question | Options | Impact |
|----------|---------|--------|
| ReadProof validity | Session/Time/Hash | WriteTool design |
| Ghost granularity | Minimal/Medium/Full | Storage cost |
| Parallel failure | Fail-fast/Collect-all | Pipeline behavior |
| MCP bidirectional | Phase 2/Phase 4 | Scope |
| Tool vs Aspect boundary | Spec position | Architecture |

---

## Tool Registry Schema

```python
# services/tooling/registry.py

@dataclass(frozen=True)
class ToolMeta:
    """Metadata for a registered tool."""
    name: str                          # e.g., "file.read"
    description: str                   # Human-readable description
    input_type: type                   # Request dataclass
    output_type: type                  # Response dataclass
    effects: list[Effect]              # READS, WRITES, CALLS
    trust_required: TrustLevel         # Minimum trust level
    category: ToolCategory             # CORE, WRAPPER, ORCHESTRATION
    timeout_default_ms: int = 120_000  # Default timeout
    cacheable: bool = False            # Whether result can be cached
    streaming: bool = False            # Whether tool supports streaming

class ToolRegistry:
    """Central registry for all tools."""

    _tools: dict[str, ToolMeta]

    def register(self, meta: ToolMeta) -> None:
        if meta.name in self._tools:
            raise DuplicateToolError(f"Tool {meta.name} already registered")
        self._tools[meta.name] = meta

    def get(self, name: str) -> ToolMeta | None:
        return self._tools.get(name)

    def list_by_trust(self, max_trust: TrustLevel) -> list[ToolMeta]:
        return [
            meta for meta in self._tools.values()
            if meta.trust_required <= max_trust
        ]

    def list_by_category(self, category: ToolCategory) -> list[ToolMeta]:
        return [
            meta for meta in self._tools.values()
            if meta.category == category
        ]
```

---

## Governance Hooks

### Trust Gate (Pre-Invocation)

```python
async def pre_invoke_hook(
    tool_path: str,
    observer: Umwelt,
    request: Any,
) -> GateResult:
    """Called before every tool invocation."""
    # Check trust level
    gate = ToolTrustGate()
    result = await gate.check(tool_path, observer)

    if not result.allowed:
        # Log denied attempt
        await emit_tool_event(
            TOOL_TRUST_DENIED,
            tool_path,
            observer.identity,
            result.message,
        )
        raise TrustViolation(result.message)

    return result
```

### Trace Capture (Post-Invocation)

```python
async def post_invoke_hook(
    tool_path: str,
    observer: Umwelt,
    request: Any,
    result: Any,
    duration_ms: float,
    alternatives: list[Alternative],
) -> None:
    """Called after every tool invocation."""
    # Record in Differance
    trace = WiringTrace(
        path=tool_path,
        input=request,
        output=result,
        duration_ms=duration_ms,
        alternatives=alternatives,
        observer_id=observer.identity,
    )
    await differance_store.record(trace)

    # Emit to SynergyBus
    await emit_tool_event(
        TOOL_COMPLETED,
        tool_path,
        summarize(request),
        summarize(result),
        duration_ms,
    )
```

### Audit Entry (Witness)

```python
async def record_action(
    tool_path: str,
    observer: Umwelt,
    request: Any,
    result: Any,
    reversible: bool,
    inverse_action: str | None,
) -> None:
    """Record action in Witness for rollback window."""
    await witness.record_action(
        action=f"tool:{tool_path}",
        success=True,
        message=summarize(result),
        reversible=reversible,
        inverse_action=inverse_action,
    )
```

---

## Milestones

| Week | Phase | Deliverable | Owner |
|------|-------|-------------|-------|
| W1 | Phase 0 | Foundation skeleton | Infra |
| W2 | Phase 1 | Core tools (read/write/edit/glob/grep) | Infra |
| W3 | Phase 2 | System tools (bash/web) | Infra |
| W4 | Phase 3 | Orchestration (todo/mode/pipeline) | Infra |
| W5-6 | Phase 4A | PolyTool (mode-dependent behavior) | TBD |
| W7 | Phase 4B | SheafTool (local-global coherence) | TBD |
| W8-9 | Phase 4C | FluxTool + Teaching Layer | TBD |
| W10 | Phase 4D | MCP Bidirectional Bridge | TBD |
| W10.5 | Phase 4E | Formal Operad Verification | TBD |

**Total**: ~10.5 weeks (Phases 0-4)

---

## Related

- `spec/services/tooling.md` -- Specification
- `plans/ugent-tooling-phase4-advanced.md` -- Phase 4 detailed research & proposal
- `docs/skills/metaphysical-fullstack.md` -- Architecture pattern
- `docs/skills/crown-jewel-patterns.md` -- Implementation patterns (incl. Pattern 14: Teaching Mode)
- `docs/skills/polynomial-agent.md` -- PolyAgent patterns (foundation for PolyTool)
- `docs/skills/agentese-node-registration.md` -- Node registration
- `docs/skills/data-bus-integration.md` -- Event bus patterns
- `impl/claude/agents/poly/primitives.py` -- 17 polynomial primitives
- `impl/claude/agents/flux/` -- Flux agent implementation (foundation for FluxTool)

---

*The Mirror Test: Does this feel like Kent on his best day?*
*Daring (categorical composition), Bold (beyond Claude Code),*
*Creative (novel patterns), Opinionated (tools as morphisms).*

