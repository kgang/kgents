# T-gent/U-gent Implementation Migration Plan

**Version**: 1.0.0
**Status**: Ready for Implementation
**Author**: Claude (with Kent)
**Date**: 2025-12-11

---

## Executive Summary

This plan migrates the implementation (`impl/claude/agents/`) to match the spec disambiguation between T-gents (Testing) and U-gents (Utility/Tool Use). The migration separates two fundamentally distinct categorical roles:

- **T-gents**: Endofunctors on `Cat_Agent` that preserve composition while injecting test behaviors (perturbation, observation, judgment)
- **U-gents**: Morphisms from `Cat_Agent` to `Cat_External` bridging the agent category to external tool systems

The key insight: T-gents are *internal* (agents testing agents), U-gents are *external* (agents interfacing with the world).

---

## Theoretical Foundation

### Category-Theoretic Distinction

The disambiguation is not merely organizational—it reflects a fundamental categorical distinction:

#### T-gents as Endofunctors

T-gents are endofunctors on the agent category:

```
T: Cat_Agent → Cat_Agent
```

They preserve the categorical structure while adding test behaviors:

| Type | Categorical Role | Functor Type |
|------|------------------|--------------|
| **Nullifiers** | Constant functor | `Δ_b: A ↦ b` (constant morphism) |
| **Saboteurs** | Perturbation functor | `Noise_ε: f ↦ f + ε` (identity + error) |
| **Observers** | Identity with effect | `Spy: f ↦ f ⊗ log` (product with side effect) |
| **Critics** | Evaluation functor | `Judge: (A → B) ↦ Score` (higher-order) |
| **Adversarial** | Composition stress | `Gym: f ↦ ∐(Noise × Fail × Latency)(f)` (coproduct) |

**Key property**: T-gents *do not leave the category*. They transform agents into test agents, but remain within `Cat_Agent`.

#### U-gents as Interface Morphisms

U-gents are morphisms from the agent category to external categories:

```
U: Cat_Agent → Cat_Tool
```

where `Cat_Tool` is the category of typed external interfaces:

| Type | Categorical Role | Morphism Target |
|------|------------------|-----------------|
| **Core** | Base morphism | `Tool[A,B]: A → B` (external) |
| **Wrappers** | Functor decoration | `F: Tool → Tool` (adds tracing, caching) |
| **Execution** | Kleisli arrows | `A → M[B]` where M = Result monad |
| **MCP** | Natural transformation | `η: MCPTool ⇒ Tool` (protocol bridge) |
| **Security** | Fibered morphisms | `Tool ⨉_Perm Context → Tool` (permissioned) |
| **Orchestration** | Higher functors | `∏Tool`, `∐Tool` (products, coproducts) |

**Key property**: U-gents *cross the boundary*. They bridge the agent category to external systems (APIs, databases, protocols).

### The Separation Principle

The migration enforces a fundamental separation:

```
Internal Testing (T) ⊥ External Interfacing (U)
```

This orthogonality is not arbitrary—it reflects:

1. **Closure under Composition**: T-gents compose internally; U-gents compose with external boundaries
2. **Different Error Semantics**: T-gent errors are *intentional* (sabotage); U-gent errors are *external* (network, API)
3. **Different Observability**: T-gents observe *behavior*; U-gents observe *execution*

### Kleisli Category and the Result Monad

Both T-gents and U-gents operate in the Kleisli category of the Result monad:

```python
# The Result monad
Result[A, E] = Success[A] | Failure[E]

# Kleisli arrows
f: A → Result[B, E]
g: B → Result[C, E]

# Kleisli composition (fish operator)
f >=> g: A → Result[C, E]
```

This is crucial for:
- **T-gents**: FailingAgent returns `Failure[TestError]`
- **U-gents**: ToolExecutor returns `Result[Output, ToolError]`

The monad provides **railway-oriented programming**: errors short-circuit, successes continue.

---

## Implementation Phases

### Phase 0: Pre-Flight Verification

Before any changes:

```bash
# Capture baseline
cd impl/claude && pytest -q --tb=no 2>&1 | tail -5 > /tmp/baseline.txt
uv run mypy --strict --explicit-package-bases agents/t 2>&1 | wc -l
```

**Exit criterion**: Tests pass, mypy count captured.

### Phase 1: Create U-gent Module Structure

Create the U-gent module preserving the categorical hierarchy:

```
agents/u/
├── __init__.py           # Public API
├── core.py               # Type I: Tool[A,B], ToolMeta
├── wrappers.py           # Type II: TracedTool, CachedTool, RetryTool
├── executor.py           # Type III: ToolExecutor, CircuitBreaker
├── mcp.py                # Type IV: MCPClient, MCPTool
├── permissions.py        # Type V: PermissionClassifier, AuditLogger
├── orchestration.py      # Type VI: Parallel, Supervisor, Handoff
├── registry.py           # Tool discovery (from L-gent integration)
└── _tests/
    ├── conftest.py
    ├── test_core.py
    ├── test_wrappers.py
    ├── test_executor.py
    ├── test_mcp.py
    ├── test_permissions.py
    └── test_orchestration.py
```

**Commands**:

```bash
mkdir -p impl/claude/agents/u/_tests
touch impl/claude/agents/u/__init__.py
touch impl/claude/agents/u/core.py
```

### Phase 2: Git-Move Tool Files

Preserve git history with `git mv`:

| Source | Destination | Content |
|--------|-------------|---------|
| `agents/t/tool.py` | `agents/u/core.py` | Tool[A,B], ToolMeta, PassthroughTool |
| (extracted) | `agents/u/wrappers.py` | TracedTool, CachedTool, RetryTool |
| `agents/t/executor.py` | `agents/u/executor.py` | ToolExecutor, CircuitBreaker |
| `agents/t/mcp_client.py` | `agents/u/mcp.py` | MCPClient, MCPTool |
| `agents/t/permissions.py` | `agents/u/permissions.py` | PermissionClassifier |
| `agents/t/orchestration.py` | `agents/u/orchestration.py` | Parallel, Supervisor, Handoff |
| `agents/t/registry.py` | `agents/u/registry.py` | ToolRegistry |

```bash
cd impl/claude
git mv agents/t/tool.py agents/u/core.py 2>/dev/null || true
git mv agents/t/executor.py agents/u/executor.py 2>/dev/null || true
git mv agents/t/mcp_client.py agents/u/mcp.py 2>/dev/null || true
git mv agents/t/permissions.py agents/u/permissions.py 2>/dev/null || true
git mv agents/t/orchestration.py agents/u/orchestration.py 2>/dev/null || true
git mv agents/t/registry.py agents/u/registry.py 2>/dev/null || true
```

**Note**: Some files may not exist or have different names. Adapt as needed.

### Phase 3: Implement Deprecation Bridge

The T-gent module must provide backwards compatibility via `__getattr__`:

```python
# agents/t/__init__.py

import warnings
from typing import Any

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

# Type V - Adversarial
# (Add when implemented)

# Deprecation bridge for tool-related imports
_DEPRECATED_EXPORTS: set[str] = {
    "Tool", "ToolMeta", "ToolIdentity", "ToolInterface", "ToolRuntime",
    "ToolError", "ToolErrorType", "ToolTrace", "PassthroughTool",
    "TracedTool", "CachedTool", "RetryTool", "ToolRegistry", "ToolEntry",
    "CircuitState", "CircuitBreakerConfig", "CircuitBreakerTool",
    "ToolExecutor", "RetryExecutor", "RobustToolExecutor", "SecureToolExecutor",
    "MCPTransportType", "MCPServerInfo", "MCPToolSchema", "MCPResource",
    "JsonRpcRequest", "JsonRpcResponse", "MCPTransport", "MCPClient", "MCPTool",
    "PermissionLevel", "SecurityLevel", "AgentContext", "ToolCapabilities",
    "TemporaryToken", "PermissionClassifier", "AuditLogger",
    "SequentialOrchestrator", "ParallelOrchestrator", "SupervisorPattern",
    "HandoffPattern", "DynamicToolSelector", "SelectionStrategy",
}


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
    raise AttributeError(f"module 'agents.t' has no attribute {name!r}")


__all__ = [
    # Type I - Nullifiers
    "MockAgent", "MockConfig", "FixtureAgent", "FixtureConfig",
    # Type II - Saboteurs
    "FailingAgent", "FailingConfig", "FailureType",
    "NoiseAgent", "NoiseConfig", "NoiseType",
    "LatencyAgent", "FlakyAgent",
    # Type III - Observers
    "SpyAgent", "PredicateAgent", "CounterAgent", "MetricsAgent",
    # Type IV - Critics
    "JudgeAgent", "JudgmentCriteria", "PropertyAgent", "OracleAgent",
]
```

### Phase 4: Create U-gent Public API

```python
# agents/u/__init__.py
"""
U-gents: Utility agents for tool use and external interaction.

The letter U represents Utility agents—typed morphisms specialized for
external interaction through composable tool interfaces.

Categorical Role:
    U: Cat_Agent → Cat_Tool

Unlike T-gents (endofunctors on Cat_Agent), U-gents bridge the agent
category to external systems. This is a fundamental boundary crossing.

Types:
    I.   Core: Tool[A,B], ToolMeta, PassthroughTool
    II.  Wrappers: TracedTool, CachedTool, RetryTool
    III. Execution: ToolExecutor, CircuitBreaker
    IV.  MCP: MCPClient, MCPTool
    V.   Security: PermissionClassifier, AuditLogger
    VI.  Orchestration: ParallelOrchestrator, Supervisor, Handoff
"""

from __future__ import annotations

# Type I - Core
from .core import (
    Tool,
    ToolMeta,
    ToolIdentity,
    ToolInterface,
    ToolRuntime,
    ToolError,
    ToolErrorType,
    ToolTrace,
    PassthroughTool,
)

# Type II - Wrappers
from .wrappers import TracedTool, CachedTool, RetryTool

# Type III - Execution
from .executor import (
    ToolExecutor,
    RetryExecutor,
    RobustToolExecutor,
    SecureToolExecutor,
    CircuitState,
    CircuitBreakerConfig,
    CircuitBreakerTool,
)

# Type IV - MCP
from .mcp import (
    MCPTransportType,
    MCPServerInfo,
    MCPToolSchema,
    MCPResource,
    JsonRpcRequest,
    JsonRpcResponse,
    MCPTransport,
    MCPClient,
    MCPTool,
)

# Type V - Security
from .permissions import (
    PermissionLevel,
    SecurityLevel,
    AgentContext,
    ToolCapabilities,
    TemporaryToken,
    PermissionClassifier,
    AuditLogger,
)

# Type VI - Orchestration
from .orchestration import (
    SequentialOrchestrator,
    ParallelOrchestrator,
    SupervisorPattern,
    HandoffPattern,
    DynamicToolSelector,
    SelectionStrategy,
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

### Phase 5: Update Cross-References

Search and update imports across the codebase:

```bash
# Find all tool imports from agents.t
grep -r "from agents\.t import.*Tool" impl/claude/
grep -r "from agents\.t import.*MCP" impl/claude/
grep -r "from agents\.t import.*Executor" impl/claude/
grep -r "from agents\.t import.*Permission" impl/claude/
grep -r "from agents\.t import.*Orchestrat" impl/claude/

# Update each file to import from agents.u
```

Key files to check:
- `agents/j/` (J-gent tool orchestration)
- `agents/w/` (W-gent observability)
- `agents/l/` (L-gent tool registry)
- `protocols/cli/` (CLI tool invocation)
- Integration tests in `agents/_tests/`

### Phase 6: Move Test Files

```bash
cd impl/claude

# Move tool-related tests to U-gent
git mv agents/t/_tests/test_tool.py agents/u/_tests/test_core.py 2>/dev/null || true
git mv agents/t/_tests/test_mcp_client.py agents/u/_tests/test_mcp.py 2>/dev/null || true
git mv agents/t/_tests/test_executor.py agents/u/_tests/test_executor.py 2>/dev/null || true
git mv agents/t/_tests/test_permissions.py agents/u/_tests/test_permissions.py 2>/dev/null || true
git mv agents/t/_tests/test_orchestration.py agents/u/_tests/test_orchestration.py 2>/dev/null || true
```

Update imports within moved test files.

### Phase 7: Verification

```bash
# Run full test suite
cd impl/claude && pytest -q

# Check mypy
uv run mypy --strict --explicit-package-bases agents/u agents/t 2>&1 | head -20

# Verify deprecation warnings work
python -c "from agents.t import Tool" 2>&1 | grep -i deprecat

# Verify clean imports work
python -c "from agents.u import Tool; print(Tool)"
```

---

## Type Mapping Reference

### T-gent Types (Final - Testing Only)

```python
# Type I - Nullifiers (constant/lookup morphisms)
MockAgent      # Δ_b: A → b (constant functor)
FixtureAgent   # Lookup morphism from fixture table

# Type II - Saboteurs (perturbation functors)
FailingAgent   # ⊥: A → Error (bottom morphism)
NoiseAgent     # Id + ε: A → A (identity with noise)
LatencyAgent   # (A, t) → (A, t + Δ) (temporal delay)
FlakyAgent     # A → B | Error (probabilistic)

# Type III - Observers (identity with side effects)
SpyAgent       # Id ⊗ log: A → A (identity + logging)
PredicateAgent # Gate: A → A | Error (predicate filter)
CounterAgent   # Id ⊗ count: A → A (identity + counting)
MetricsAgent   # Id ⊗ metrics: A → A (identity + metrics)

# Type IV - Critics (higher-order evaluation)
JudgeAgent     # (A, B) → Score (input/output evaluation)
PropertyAgent  # Agent → Bool (property verification)
OracleAgent    # A → B_expected (ground truth)

# Type V - Adversarial (compositional chaos)
AdversarialGym       # Agent → GymReport (stress testing)
StressCoordinate     # (noise, failure, latency, drift)
MultiDimensionalGym  # Agent → Dict[Coord, Report]
```

### U-gent Types (New - Tool Use Only)

```python
# Type I - Core (base morphisms to external category)
Tool[A, B]       # Morphism to Cat_Tool
ToolMeta         # Metadata for tool discovery
PassthroughTool  # Identity tool (Id in Cat_Tool)

# Type II - Wrappers (functor decorations)
TracedTool       # F_trace: Tool → Tool (adds tracing)
CachedTool       # F_cache: Tool → Tool (adds caching)
RetryTool        # F_retry: Tool → Tool (adds retry)

# Type III - Execution (Kleisli arrows with effects)
ToolExecutor     # A → Result[B, ToolError]
CircuitBreaker   # State machine for failure handling
RetryExecutor    # Exponential backoff executor

# Type IV - MCP (natural transformations)
MCPClient        # Protocol client
MCPTool          # MCP-wrapped tool
MCPTransport     # Transport layer (stdio, SSE, HTTP)

# Type V - Security (fibered morphisms)
PermissionClassifier  # Tool ⨉_Perm Context → Permission
AuditLogger          # Tool execution trace

# Type VI - Orchestration (higher functors)
ParallelOrchestrator  # ∏Tool (product of tools)
SupervisorPattern     # Central coordination
HandoffPattern        # Natural transformation between tools
```

---

## Categorical Verification Checklist

After migration, verify categorical properties:

### T-gent Laws

```python
# Identity law: Spy is transparent
assert (spy >> f).invoke(x) == f.invoke(x)

# Composition law: Mock composes
assert (mock >> f >> g).invoke(x) == (mock >> (f >> g)).invoke(x)

# Perturbation law: Noise preserves identity semantically
assert NoiseAgent(ε=0) ≡ Identity  # Zero noise = identity
```

### U-gent Laws

```python
# Tool composition: Types must align
tool_a: Tool[A, B]
tool_b: Tool[B, C]
composed: Tool[A, C] = tool_a >> tool_b  # Type-safe

# Kleisli composition: Error handling
result = await (f >=> g >=> h).invoke(input)  # Railway-oriented

# Wrapper functoriality: Wrapping preserves composition
traced(f >> g) ≡ traced(f) >> traced(g)  # Functor law
```

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Import breakage | Medium | High | Deprecation bridge via `__getattr__` |
| Git history loss | Low | Medium | Use `git mv` for all moves |
| Test failures | High | Medium | Run tests after each phase |
| Mypy regressions | Medium | Low | Capture baseline, compare after |
| Missing files | Medium | Low | Check existence before `git mv` |

---

## Success Criteria

- [ ] `from agents.t import MockAgent` works (testing)
- [ ] `from agents.t import Tool` emits deprecation warning
- [ ] `from agents.u import Tool` works cleanly
- [ ] All tests pass (7,080+ tests)
- [ ] Mypy count ≤ baseline
- [ ] HYDRATE.md updated
- [ ] Cross-references updated

---

## Post-Migration: Type V Adversarial Implementation

The migration creates space for proper Type V implementation in T-gents:

```python
# agents/t/adversarial.py

@dataclass
class StressCoordinate:
    """A point in the stress-test space."""
    noise: float       # 0.0 - 1.0
    failure: float     # Probability of FailingAgent injection
    latency: float     # Max latency to inject (ms)
    drift: float       # Semantic drift factor


class AdversarialGym:
    """
    Monte Carlo stress testing via T-gent composition.

    The Gym is a functor:
        Gym: Agent → GymReport

    It composes the agent under test with random T-gents
    from Types I-IV and measures resilience.
    """

    async def stress_test(
        self,
        agent: Agent[A, B],
        coordinates: list[StressCoordinate],
        iterations: int = 100,
    ) -> GymReport:
        """Run Monte Carlo stress testing."""
        ...
```

This completes the categorical picture:
- Types I-IV: Individual test functors
- Type V: Composition of test functors (the "gym")

---

## Appendix: The Functor Hierarchy

```
                    Cat_Agent
                        │
           ┌────────────┼────────────┐
           │            │            │
           ▼            ▼            ▼
       T-gents      U-gents      Other
    (endofunctor)  (boundary)   (agents)
           │            │
    ┌──────┼──────┐     │
    │      │      │     │
    ▼      ▼      ▼     ▼
  Null   Sab    Obs  Cat_Tool
  (Δ)   (⊥+ε)  (Id⊗)    │
           │            │
           ▼            ▼
        Critics      MCP
       (higher)   (natural
        order)    transform)
           │
           ▼
       Adversarial
       (∐ composition)
```

---

*"The spec is the contract. The impl is the fulfillment. The category is the truth."*
