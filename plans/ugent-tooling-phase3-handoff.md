# U-gent Tooling Phase 3: Orchestration Tools

> *"Tools that coordinate other tools."*

## Status: Ready

**Depends on**: Phase 2 (System Tools) ✅ Complete
**Duration**: ~1 week

---

## Context

**Phases 0-2 Complete**:
- Phase 0: Foundation (`Tool[A,B]`, `ToolRegistry`, `ToolExecutor`)
- Phase 1: Core Tools (`ReadTool`, `WriteTool`, `EditTool`, `GlobTool`, `GrepTool`)
- Phase 2: System Tools (`BashTool`, `KillShellTool`, `WebFetchTool`, `WebSearchTool`)

**Current State**:
- 9 tools implemented, 158 tests passing
- Categorical composition works (`pipeline = ReadTool() >> GrepTool()`)
- Trust levels enforced (L0-L3)
- Safety patterns active (12 NEVER_PATTERNS for BashTool)

---

## Phase 3 Objectives

1. **TodoTool** — Task state management (pending/in_progress/completed)
2. **ModeTool** — Plan/execute modal transitions
3. **ClarifyTool** — Structured human-in-the-loop questions
4. **Orchestrator** — Parallel execution with dependency resolution

---

## Deliverables

```
services/tooling/tools/
    task.py           # TodoTool, TodoListTool
    mode.py           # EnterPlanModeTool, ExitPlanModeTool
    clarify.py        # ClarifyTool (AskUserQuestion equivalent)

services/tooling/
    orchestrator.py   # Parallel execution, dependency DAG
```

---

## Key Patterns

### TodoTool State Machine

```python
class TodoStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

# Constraint: Only ONE task in_progress at a time
# Constraint: Mark complete IMMEDIATELY after finishing
```

### ModeTool Transitions

```
EXECUTE_MODE ──EnterPlanMode──> PLAN_MODE
PLAN_MODE ──ExitPlanMode──> EXECUTE_MODE (requires user approval)
```

### ClarifyTool Contract

```python
@dataclass
class ClarifyRequest:
    questions: list[Question]  # 1-4 questions
    # Each question has: header, question, options (2-4), multiSelect

@dataclass
class ClarifyResponse:
    answers: dict[str, str]  # question_id → selected_option
```

### Orchestrator DAG

```python
# Parallel execution of independent tools
await orchestrator.execute_parallel([
    (tool_a, request_a),
    (tool_b, request_b),  # Independent, runs in parallel
])

# Sequential when dependencies exist
await orchestrator.execute_dag({
    "read": (ReadTool(), request),
    "grep": (GrepTool(), depends_on=["read"]),
})
```

---

## Contracts (Already in contracts.py)

```python
# Task tools
TodoItem, TodoListRequest, TodoListResponse
TodoCreateRequest, TodoCreateResponse
TodoUpdateRequest, TodoUpdateResponse

# Mode tools
EnterPlanModeRequest, EnterPlanModeResponse
ExitPlanModeRequest, ExitPlanModeResponse

# Clarify
ClarifyRequest, ClarifyResponse
```

---

## Success Criteria

- [ ] `from services.tooling.tools import TodoTool, ModeTool, ClarifyTool`
- [ ] TodoTool enforces single in_progress constraint
- [ ] ModeTool transitions require user approval for exit
- [ ] ClarifyTool presents 1-4 structured questions
- [ ] Orchestrator executes independent tools in parallel
- [ ] Pipeline composition verifies type alignment at construction
- [ ] All tools emit Differance traces
- [ ] `uv run pytest services/tooling/tools/_tests/test_task.py -v` passes
- [ ] `uv run pytest services/tooling/tools/_tests/test_mode.py -v` passes
- [ ] `uv run pytest services/tooling/tools/_tests/test_orchestrator.py -v` passes

---

## Open Questions

| Question | Options | Recommendation |
|----------|---------|----------------|
| Todo persistence | In-memory / SQLite / DataBus | In-memory (session-scoped) |
| Plan file location | Fixed / Configurable | Configurable via request |
| Parallel failure mode | Fail-fast / Collect-all | Collect-all with error aggregation |
| Max parallelism | Unlimited / Bounded | Bounded (5 concurrent) |

---

*"Orchestration is composition at the workflow level."*
