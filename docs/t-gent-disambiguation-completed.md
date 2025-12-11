# T-gent Disambiguation: Completed Spec Changes & Impl Migration Guide

**Status**: Spec Complete, Impl Pending
**Date**: 2025-12-11
**Authors**: Claude (with Kent)

---

## Executive Summary

The letter **T** previously served dual purposes in kgents: **T**esting agents and **T**ool use framework. This has been resolved in the specification:

| Before | After |
|--------|-------|
| T-gents = Testing (I-IV) + Tools (V-IX) | T-gents = Testing (I-V) |
| U-gents = Understudy (distillation) | U-gents = Utility (tool use, I-VI) |
| Understudy as separate genus | Distillation merged into B-gent |

**Completed**: All spec changes
**Pending**: Implementation migration (`impl/claude/agents/`)

---

## What Changed in Spec

### T-gents (Testing)

**Now exclusively for verification** (Types I-V):

| Type | Name | Purpose |
|------|------|---------|
| I | Nullifiers | MockAgent, FixtureAgent |
| II | Saboteurs | FailingAgent, NoiseAgent, LatencyAgent, FlakyAgent |
| III | Observers | SpyAgent, PredicateAgent, CounterAgent, MetricsAgent |
| IV | Critics | JudgeAgent, PropertyAgent, OracleAgent |
| V | Adversarial | AdversarialGym, StressCoordinate, MultiDimensionalGym |

**Files Changed**:
- `spec/t-gents/README.md` - Added Type V summary, migration note to U-gents
- `spec/t-gents/taxonomy.md` - Added Type V row to summary table
- `spec/t-gents/tool-use.md` - **DEPRECATED** with pointer to U-gents

### U-gents (Utility/Tool Use)

**Completely rewritten** for tool use (Types I-VI):

| Type | Name | Purpose | From T-gents |
|------|------|---------|--------------|
| I | Core | Tool[A,B], ToolMeta, PassthroughTool | T-gents V |
| II | Wrappers | TracedTool, CachedTool, RetryTool | T-gents V |
| III | Execution | ToolExecutor, CircuitBreaker, RetryExecutor | T-gents VI |
| IV | MCP | MCPClient, MCPTool, Transports | T-gents VII |
| V | Security | PermissionClassifier, AuditLogger | T-gents VIII |
| VI | Orchestration | ParallelOrchestrator, Supervisor, Handoff | T-gents IX |

**Files Changed**:
- `spec/u-gents/README.md` - Completely rewritten (was "Understudy")
- `spec/u-gents/tool-use.md` - **NEW** (migrated from T-gents)

### B-gents (Economics)

**Added distillation** (formerly U-gent "Understudy"):

**Files Changed**:
- `spec/b-gents/distillation.md` - Enhanced with Understudy content
- `spec/b-gents/README.md` - Added distillation to specs table

### Cross-References

**Files Changed**:
- `spec/README.md` - Added U-gents to reading order, added cross-pollination entries
- `CLAUDE.md` - Updated agent taxonomy table
- `HYDRATE.md` - Updated T-gent Disambiguation section
- `spec/t-gents/IMPLEMENTATION_PLAN.md` - Created and marked complete

---

## Impl Migration Guide

The implementation in `impl/claude/agents/` must now mirror the spec changes.

### Phase 1: Create U-gent Directory

```bash
mkdir -p impl/claude/agents/u
touch impl/claude/agents/u/__init__.py
```

### Phase 2: Move Tool Files from T-gent to U-gent

| Source | Destination | Notes |
|--------|-------------|-------|
| `agents/t/tool.py` | `agents/u/tool.py` | Core Tool[A,B] class |
| `agents/t/registry.py` | `agents/u/registry.py` | ToolRegistry |
| `agents/t/executor.py` | `agents/u/executor.py` | ToolExecutor, CircuitBreaker |
| `agents/t/mcp_client.py` | `agents/u/mcp.py` | MCPClient, MCPTool |
| `agents/t/permissions.py` | `agents/u/permissions.py` | PermissionClassifier |
| `agents/t/orchestration.py` | `agents/u/orchestration.py` | Parallel, Supervisor, Handoff |

**Use `git mv`** to preserve history:
```bash
git mv impl/claude/agents/t/tool.py impl/claude/agents/u/tool.py
# ... etc
```

### Phase 3: Update T-gent `__init__.py`

Remove tool-related exports, add deprecation warnings:

```python
# impl/claude/agents/t/__init__.py

# Type I - Nullifiers (UNCHANGED)
from .mock import MockAgent, MockConfig
from .fixture import FixtureAgent, FixtureConfig

# Type II - Saboteurs (UNCHANGED)
from .failing import FailingAgent, FailingConfig, FailureType
from .noise import NoiseAgent, NoiseConfig, NoiseType
from .latency import LatencyAgent
from .flaky import FlakyAgent

# Type III - Observers (UNCHANGED)
from .spy import SpyAgent
from .predicate import PredicateAgent
from .counter import CounterAgent
from .metrics import MetricsAgent

# Type IV - Critics (UNCHANGED)
from .judge import JudgeAgent, JudgmentCriteria
from .property import PropertyAgent
from .oracle import OracleAgent

# Type V - Adversarial (NEW PROMOTION)
from .adversarial import AdversarialGym, StressCoordinate, MultiDimensionalGym

# DEPRECATED: Tool-related imports moved to agents.u
# Keep for backwards compatibility with deprecation warning
import warnings

def __getattr__(name: str):
    _deprecated_tool_exports = {
        "Tool", "ToolMeta", "ToolIdentity", "ToolInterface", "ToolRuntime",
        "ToolError", "ToolErrorType", "ToolTrace", "PassthroughTool",
        "TracedTool", "CachedTool", "RetryTool", "ToolRegistry", "ToolEntry",
        "CircuitState", "CircuitBreakerConfig", "CircuitBreakerTool",
        "ToolExecutor", "RetryExecutor", "RobustToolExecutor", "SecureToolExecutor",
        "MCPTransportType", "MCPServerInfo", "MCPToolSchema", "MCPResource",
        "JsonRpcRequest", "JsonRpcResponse", "MCPTransport", "MCPClient", "MCPTool",
        "PermissionLevel", "SecurityLevel", "AgentContext",
        "ToolCapabilities", "TemporaryToken", "PermissionClassifier", "AuditLogger",
        "SequentialOrchestrator", "ParallelOrchestrator", "SupervisorPattern",
        "HandoffPattern", "DynamicToolSelector", "SelectionStrategy",
    }
    if name in _deprecated_tool_exports:
        warnings.warn(
            f"Importing {name} from agents.t is deprecated. "
            f"Use agents.u instead: from agents.u import {name}",
            DeprecationWarning,
            stacklevel=2
        )
        from agents import u
        return getattr(u, name)
    raise AttributeError(f"module 'agents.t' has no attribute {name!r}")
```

### Phase 4: Create U-gent `__init__.py`

```python
# impl/claude/agents/u/__init__.py
"""
U-gents: Utility agents for tool use and external interaction.

The letter U represents Utility agents—typed morphisms specialized for
external interaction through composable tool interfaces.

Types:
    I.   Core: Tool[A,B], ToolMeta, PassthroughTool
    II.  Wrappers: TracedTool, CachedTool, RetryTool
    III. Execution: ToolExecutor, CircuitBreaker, RetryExecutor
    IV.  MCP: MCPClient, MCPTool, Transports
    V.   Security: PermissionClassifier, AuditLogger
    VI.  Orchestration: ParallelOrchestrator, Supervisor, Handoff
"""

# Type I - Core
from .tool import (
    Tool, ToolMeta, ToolIdentity, ToolInterface, ToolRuntime,
    ToolError, ToolErrorType, ToolTrace, PassthroughTool,
)

# Type II - Wrappers
from .tool import TracedTool, CachedTool, RetryTool

# Type III - Execution
from .executor import (
    ToolExecutor, RetryExecutor, RobustToolExecutor, SecureToolExecutor,
    CircuitState, CircuitBreakerConfig, CircuitBreakerTool,
)

# Type IV - MCP
from .mcp import (
    MCPTransportType, MCPServerInfo, MCPToolSchema, MCPResource,
    JsonRpcRequest, JsonRpcResponse, MCPTransport, MCPClient, MCPTool,
)

# Type V - Security
from .permissions import (
    PermissionLevel, SecurityLevel, AgentContext,
    ToolCapabilities, TemporaryToken, PermissionClassifier, AuditLogger,
)

# Type VI - Orchestration
from .orchestration import (
    SequentialOrchestrator, ParallelOrchestrator, SupervisorPattern,
    HandoffPattern, DynamicToolSelector, SelectionStrategy,
)

# Registry
from .registry import ToolRegistry, ToolEntry

__all__ = [
    # Type I - Core
    "Tool", "ToolMeta", "ToolIdentity", "ToolInterface", "ToolRuntime",
    "ToolError", "ToolErrorType", "ToolTrace", "PassthroughTool",
    # Type II - Wrappers
    "TracedTool", "CachedTool", "RetryTool",
    # Type III - Execution
    "ToolExecutor", "RetryExecutor", "RobustToolExecutor", "SecureToolExecutor",
    "CircuitState", "CircuitBreakerConfig", "CircuitBreakerTool",
    # Type IV - MCP
    "MCPTransportType", "MCPServerInfo", "MCPToolSchema", "MCPResource",
    "JsonRpcRequest", "JsonRpcResponse", "MCPTransport", "MCPClient", "MCPTool",
    # Type V - Security
    "PermissionLevel", "SecurityLevel", "AgentContext",
    "ToolCapabilities", "TemporaryToken", "PermissionClassifier", "AuditLogger",
    # Type VI - Orchestration
    "SequentialOrchestrator", "ParallelOrchestrator", "SupervisorPattern",
    "HandoffPattern", "DynamicToolSelector", "SelectionStrategy",
    # Registry
    "ToolRegistry", "ToolEntry",
]
```

### Phase 5: Update Imports Across Codebase

Search and replace imports:

```bash
# Find all files importing tool-related items from agents.t
grep -r "from agents.t import.*Tool" impl/claude/
grep -r "from agents.t import.*MCP" impl/claude/
grep -r "from agents.t import.*Executor" impl/claude/
grep -r "from agents.t import.*Permission" impl/claude/
grep -r "from agents.t import.*Orchestrat" impl/claude/
```

Update to use `agents.u`:

```python
# Before
from agents.t import Tool, MCPClient, ToolExecutor

# After
from agents.u import Tool, MCPClient, ToolExecutor
```

### Phase 6: Move Test Files

```bash
# If tests are colocated, move them too
git mv impl/claude/agents/t/_tests/test_tool.py impl/claude/agents/u/_tests/test_tool.py
git mv impl/claude/agents/t/_tests/test_mcp*.py impl/claude/agents/u/_tests/
# ... etc
```

### Phase 7: Update Cross-Pollination

Update any files that reference T-gent tool use:

| Pattern to Find | Replace With |
|-----------------|--------------|
| `T-gent tool` | `U-gent tool` |
| `agents.t.Tool` | `agents.u.Tool` |
| `spec/t-gents/tool-use.md` | `spec/u-gents/tool-use.md` |

---

## Type Mapping Reference

### T-gent Types (Final)

```python
# Type I - Nullifiers
"MockAgent", "MockConfig", "FixtureAgent", "FixtureConfig"

# Type II - Saboteurs
"FailingAgent", "FailingConfig", "FailureType"
"NoiseAgent", "NoiseConfig", "NoiseType"
"LatencyAgent", "FlakyAgent"

# Type III - Observers
"SpyAgent", "PredicateAgent", "CounterAgent", "MetricsAgent"

# Type IV - Critics
"JudgeAgent", "JudgmentCriteria", "PropertyAgent", "OracleAgent"

# Type V - Adversarial
"AdversarialGym", "StressCoordinate", "MultiDimensionalGym", "GymReport"
```

### U-gent Types (New)

```python
# Type I - Core
"Tool", "ToolMeta", "ToolIdentity", "ToolInterface", "ToolRuntime"
"ToolError", "ToolErrorType", "ToolTrace"
"PassthroughTool"

# Type II - Wrappers
"TracedTool", "CachedTool", "RetryTool"
"ToolRegistry", "ToolEntry"

# Type III - Execution
"CircuitState", "CircuitBreakerConfig", "CircuitBreakerTool"
"ToolExecutor", "RetryExecutor", "RobustToolExecutor", "SecureToolExecutor"

# Type IV - MCP
"MCPTransportType", "MCPServerInfo", "MCPToolSchema", "MCPResource"
"JsonRpcRequest", "JsonRpcResponse", "MCPTransport", "MCPClient", "MCPTool"

# Type V - Security
"PermissionLevel", "SecurityLevel", "AgentContext"
"ToolCapabilities", "TemporaryToken", "PermissionClassifier", "AuditLogger"

# Type VI - Orchestration
"SequentialOrchestrator", "ParallelOrchestrator", "SupervisorPattern"
"HandoffPattern", "DynamicToolSelector", "SelectionStrategy"
```

---

## Verification Checklist

After impl migration, verify:

- [ ] `from agents.t import MockAgent` works (testing)
- [ ] `from agents.t import Tool` emits deprecation warning, still works
- [ ] `from agents.u import Tool` works (clean path)
- [ ] All tests pass
- [ ] No mypy regressions
- [ ] HYDRATE.md impl section updated

---

## Risks and Mitigations

### Risk: Import Breakage

**Mitigation**: Deprecation warnings via `__getattr__` hook. Old imports work but warn.

### Risk: Git History Loss

**Mitigation**: Use `git mv` for all file moves.

### Risk: Test Failures

**Mitigation**: Run full test suite after each phase.

---

## Appendix: Spec File Changes Summary

| File | Status | Description |
|------|--------|-------------|
| `spec/t-gents/README.md` | Modified | Testing-only, Types I-V |
| `spec/t-gents/taxonomy.md` | Modified | Added Type V row |
| `spec/t-gents/tool-use.md` | Deprecated | Points to U-gents |
| `spec/t-gents/IMPLEMENTATION_PLAN.md` | Created | Migration tracking |
| `spec/u-gents/README.md` | Rewritten | Tool Use (Types I-VI) |
| `spec/u-gents/tool-use.md` | Created | Full tool spec (migrated) |
| `spec/b-gents/distillation.md` | Enhanced | Understudy content |
| `spec/b-gents/README.md` | Modified | Added distillation ref |
| `spec/README.md` | Modified | Added U-gents |
| `CLAUDE.md` | Modified | Updated taxonomy |
| `HYDRATE.md` | Modified | Updated status |

---

## Conclusion

The spec disambiguation is complete. The implementation migration follows the same pattern:

1. **Create U-gent directory** (`impl/claude/agents/u/`)
2. **Move tool files** with `git mv`
3. **Update exports** with deprecation bridge
4. **Update imports** across codebase
5. **Verify tests** pass

*"The spec is the contract. The impl is the fulfillment."*
