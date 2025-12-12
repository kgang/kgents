---
path: agents/u-gent
status: complete
progress: 100
last_touched: 2025-12-11
touched_by: claude-opus-4.5
blocking: []
enables: []
session_notes: |
  Migration COMPLETE. All tool code moved from agents/t to agents/u.
  Deprecation bridge in place (agents.t imports warn).
  Files: core.py, mcp.py, executor.py, orchestration.py, permissions.py
  Mypy passes with 0 errors.
---

# U-gents: Utility Agents (Tool Use)

> *"U-gents cross the boundary. They bridge Cat_Agent to Cat_Tool."*

**AGENTESE Context**: External interface
**Status**: Complete (migrated from T-gent)
**Categorical Role**: `U: Cat_Agent → Cat_Tool` (boundary morphism)
**Principles**: Composable, Tasteful

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| **Boundary morphism** | U-gents cross from agent category to external tools |
| **Six types** | Core, Wrappers, Execution, MCP, Security, Orchestration |
| **Separate from T-gents** | T-gents are internal (testing); U-gents are external (tools) |
| **Deprecation bridge** | `from agents.t import Tool` warns and redirects |

---

## Categorical Distinction

U-gents vs T-gents is a fundamental categorical distinction:

| Property | U-gents | T-gents |
|----------|---------|---------|
| **Functor type** | Boundary morphism | Endofunctor |
| **Domain** | Cat_Agent | Cat_Agent |
| **Codomain** | Cat_Tool | Cat_Agent |
| **Error semantics** | External (network, API) | Intentional (sabotage) |
| **Purpose** | Interface with world | Test behavior |

---

## Type I: Core (📋 PLANNED)

Base morphisms to external category:

```python
Tool[A, B]       # Morphism to Cat_Tool
ToolMeta         # Metadata for tool discovery
PassthroughTool  # Identity tool (Id in Cat_Tool)
ToolError        # External error type
ToolTrace        # Execution trace
```

**Location**: `agents/u/core.py`

---

## Type II: Wrappers (📋 PLANNED)

Functor decorations: `F: Tool → Tool`

```python
TracedTool       # F_trace: Tool → Tool (adds tracing)
CachedTool       # F_cache: Tool → Tool (adds caching)
RetryTool        # F_retry: Tool → Tool (adds retry)
```

**Wrapper law**: `traced(f >> g) ≡ traced(f) >> traced(g)` (functoriality)

**Location**: `agents/u/wrappers.py`

---

## Type III: Execution (📋 PLANNED)

Kleisli arrows with effects: `A → Result[B, ToolError]`

```python
ToolExecutor         # Base executor
RetryExecutor        # Exponential backoff
RobustToolExecutor   # Multiple fallbacks
SecureToolExecutor   # Permissioned execution
CircuitBreakerTool   # State machine for failures
```

**Railway-oriented programming**: Errors short-circuit, successes continue.

**Location**: `agents/u/executor.py`

---

## Type IV: MCP (📋 PLANNED)

Natural transformations: `η: MCPTool ⇒ Tool`

```python
MCPClient        # Protocol client
MCPTool          # MCP-wrapped tool
MCPTransport     # Transport layer (stdio, SSE, HTTP)
MCPServerInfo    # Server metadata
MCPToolSchema    # Tool schema
```

MCP is the **model context protocol**—a standardized way for tools to expose themselves.

**Location**: `agents/u/mcp.py`

---

## Type V: Security (📋 PLANNED)

Fibered morphisms: `Tool ⨉_Perm Context → Tool`

```python
PermissionLevel      # READ, WRITE, EXECUTE, ADMIN
SecurityLevel        # LOW, MEDIUM, HIGH, CRITICAL
PermissionClassifier # Classify tool operations
AuditLogger          # Log all tool executions
TemporaryToken       # Scoped access token
```

**Location**: `agents/u/permissions.py`

---

## Type VI: Orchestration (📋 PLANNED)

Higher functors: `∏Tool`, `∐Tool`

```python
SequentialOrchestrator  # Run tools in sequence
ParallelOrchestrator    # Run tools in parallel (∏Tool)
SupervisorPattern       # Central coordination
HandoffPattern          # Natural transformation between tools
DynamicToolSelector     # Runtime tool selection
```

**Location**: `agents/u/orchestration.py`

---

## Migration Plan

Currently, tool-related code lives in `agents/t/`. Migration steps:

1. **Create `agents/u/` structure**
2. **Git-move files** (preserve history)
3. **Implement deprecation bridge** in `agents/t/__init__.py`
4. **Update cross-references**

### Deprecation Bridge

```python
# agents/t/__init__.py
def __getattr__(name: str) -> Any:
    if name in _DEPRECATED_EXPORTS:
        warnings.warn(
            f"Importing {name} from agents.t is deprecated. "
            f"Use agents.u instead: from agents.u import {name}",
            DeprecationWarning,
            stacklevel=2,
        )
        from agents import u
        return getattr(u, name)
    raise AttributeError(...)
```

---

## Public API (📋 PLANNED)

```python
# agents/u/__init__.py

# Type I - Core
from .core import Tool, ToolMeta, PassthroughTool, ToolError, ToolTrace

# Type II - Wrappers
from .wrappers import TracedTool, CachedTool, RetryTool

# Type III - Execution
from .executor import (
    ToolExecutor, RetryExecutor, RobustToolExecutor,
    SecureToolExecutor, CircuitBreakerTool
)

# Type IV - MCP
from .mcp import MCPClient, MCPTool, MCPTransport, MCPServerInfo

# Type V - Security
from .permissions import (
    PermissionLevel, PermissionClassifier, AuditLogger
)

# Type VI - Orchestration
from .orchestration import (
    SequentialOrchestrator, ParallelOrchestrator,
    SupervisorPattern, HandoffPattern
)

# Registry
from .registry import ToolRegistry, ToolEntry
```

---

## Kleisli Composition

U-gents operate in the Kleisli category of the Result monad:

```python
# Kleisli arrows
f: A → Result[B, E]
g: B → Result[C, E]

# Kleisli composition (fish operator)
f >=> g: A → Result[C, E]

# Railway-oriented: errors short-circuit
result = await (f >=> g >=> h).invoke(input)
```

---

## Directory Structure

```
agents/u/
├── __init__.py           # Public API
├── core.py               # Type I: Tool[A,B], ToolMeta
├── wrappers.py           # Type II: TracedTool, CachedTool
├── executor.py           # Type III: ToolExecutor, CircuitBreaker
├── mcp.py                # Type IV: MCPClient, MCPTool
├── permissions.py        # Type V: PermissionClassifier
├── orchestration.py      # Type VI: Parallel, Supervisor
├── registry.py           # Tool discovery
└── _tests/
    ├── test_core.py
    ├── test_wrappers.py
    ├── test_executor.py
    ├── test_mcp.py
    ├── test_permissions.py
    └── test_orchestration.py
```

---

## Cross-References

- **Plans**: `agents/t-gent.md` (Testing separation)
- **Impl**: `agents/t/` (current, to migrate), `agents/u/` (planned)
- **Spec**: `spec/u-gents/README.md` (if exists)

---

*"U-gents bridge the gap. They speak to the external world."*
