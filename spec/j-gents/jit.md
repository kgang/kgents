# JIT Agent Compilation

The defining feature of J-gents: **compile specialized agents on demand**.

---

## Philosophy

> "The agent that doesn't exist yet is the agent you need most."

Traditional agent frameworks require pre-defining all agent types. J-gents can compile **ephemeral agents** at runtime—agents that exist only for a specific task instance, then vanish.

---

## The Meta-Architect

When a J-gent classifies reality as **PROBABILISTIC** and determines that no existing agent fits the task, it invokes the **MetaArchitect**.

```python
MetaArchitect: (Intent, Context, Constraints) → AgentSource

# Example Input
intent = "Parse Java stack traces and identify OOM patterns"
context = {
    "log_format": "log4j",
    "expected_patterns": ["OutOfMemoryError", "heap space"]
}
constraints = {
    "max_complexity": 10,
    "allowed_imports": ["re", "dataclasses", "typing"],
    "entropy_budget": 0.5
}

# Example Output
source = '''
from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class OOMPattern:
    line_number: int
    heap_type: str
    allocation_size: Optional[int]

class StackTraceParser:
    """JIT-compiled agent for Java OOM analysis."""

    PATTERN = re.compile(r"OutOfMemoryError.*heap.*")

    def parse(self, log_text: str) -> list[OOMPattern]:
        matches = []
        for i, line in enumerate(log_text.split("\\n")):
            if self.PATTERN.search(line):
                matches.append(OOMPattern(
                    line_number=i,
                    heap_type=self._extract_heap_type(line),
                    allocation_size=self._extract_size(line)
                ))
        return matches

    def _extract_heap_type(self, line: str) -> str:
        # Implementation...
        return "eden" if "eden" in line.lower() else "tenured"

    def _extract_size(self, line: str) -> Optional[int]:
        # Implementation...
        match = re.search(r"(\\d+)\\s*bytes", line)
        return int(match.group(1)) if match else None
'''
```

---

## Compilation Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                        JIT Pipeline                          │
└──────────────────────────────────────────────────────────────┘

   Intent + Context
         │
         ▼
   ┌──────────────┐
   │ MetaArchitect │  Generate agent source code
   └──────┬───────┘
          │
          ▼
    SourceCode
          │
          ▼
   ┌──────────────┐
   │  Chaosmonger  │  AST stability analysis
   └──────┬───────┘
          │
          ├─── [unstable] ──► Ground (collapse to safety)
          │
          ▼
   ┌──────────────┐
   │    Judge     │  Taste/ethics evaluation
   └──────┬───────┘
          │
          ├─── [reject] ──► Ground (collapse to safety)
          │
          ▼
   ┌──────────────┐
   │   Compile    │  Type-check + exec() in sandbox
   └──────┬───────┘
          │
          ▼
   ┌──────────────┐
   │   Execute    │  Invoke with task input
   └──────────────┘
```

### Pipeline Stages

#### 1. MetaArchitect Generation

The MetaArchitect is itself an agent:

```python
class MetaArchitect(Agent[ArchitectInput, str]):
    """Generate Python source code for a new agent."""

    async def invoke(self, input: ArchitectInput) -> str:
        # Use LLM to generate agent implementation
        # Constrained by: entropy budget, allowed imports, max complexity
        ...
```

**Inputs:**
- `intent`: Natural language description of agent purpose
- `context`: Available data, expected inputs/outputs
- `constraints`: Safety bounds from parent J-gent

**Output:**
- Valid Python source code defining an agent class

#### 2. Chaosmonger Validation

Pre-Judge filter (see [stability.md](stability.md)):

```python
stability = await Chaosmonger().invoke(StabilityInput(
    source=source,
    config=StabilityConfig(
        max_cyclomatic_complexity=int(entropy_budget * 20),
        max_branching_factor=int(entropy_budget * 5),
        allowed_imports=constraints.allowed_imports,
        forbidden_patterns=["eval", "exec", "__import__"]
    )
))

if not stability.is_stable:
    logger.warning(f"JIT agent unstable: {stability.reason}")
    return ground  # Collapse to safety
```

**Rejection Reasons:**
- Cyclomatic complexity exceeds budget
- Forbidden imports detected
- Unbounded recursion detected
- Branching factor exceeds limit

#### 3. Judge Evaluation

Human values filter (taste, ethics, joy):

```python
judgment = await Judge().invoke(JudgeInput(
    source=source,
    criteria={
        "tasteful": "Is this code elegant and readable?",
        "ethical": "Does it respect privacy and safety?",
        "joyful": "Will using this agent be pleasant?"
    }
))

if not judgment.accepted:
    logger.warning(f"JIT agent rejected: {judgment.reason}")
    return ground
```

#### 4. Compilation

Type-check and compile in restricted namespace:

```python
# Type check with mypy
mypy_result = run_mypy(source)
if not mypy_result.success:
    return ground

# Compile in sandbox namespace
namespace: dict[str, Any] = {
    "__builtins__": restricted_builtins,
    "dataclasses": dataclasses,
    "typing": typing,
    # Only whitelisted imports
}

exec(source, namespace)
agent_class = namespace[extract_class_name(source)]
```

#### 5. Execution

Invoke the JIT agent with timeout and resource limits:

```python
jit_agent = agent_class()

async with timeout(seconds=30):
    result = await jit_agent.invoke(task_input)
```

---

## Ephemeral Agents

JIT-compiled agents are **ephemeral** by default:

| Property | Value | Rationale |
|----------|-------|-----------|
| **Lifetime** | Single task instance | Minimize scope of generated code |
| **Persistence** | Not saved to disk | Avoid polluting spec/ or impl/ |
| **Sandboxing** | Restricted imports, no network | Safety-first |
| **Caching** | Optional, by content hash | Performance optimization |
| **Garbage Collection** | After task completion | Clean shutdown |

### Caching Strategy (Optional)

For repeated tasks, cache compiled agents by hash:

```python
cache_key = hash((intent, context, constraints))

if cache_key in jit_cache:
    return jit_cache[cache_key]
else:
    agent = compile_jit_agent(...)
    jit_cache[cache_key] = agent
    return agent
```

**Cache Invalidation:**
- TTL: 1 hour (default)
- LRU: Max 100 agents
- Manual: On Judge criteria change

---

## Safety Invariants

JIT compilation introduces meta-circular risk. Safety is **paramount**.

### Invariant 1: Sandbox Isolation

JIT agents execute in restricted namespace:

```python
restricted_builtins = {
    # Allowed
    "print", "len", "range", "enumerate", "zip",
    "int", "str", "float", "bool", "list", "dict", "set",
    "dataclasses", "typing",

    # Forbidden
    # "eval", "exec", "compile", "__import__",
    # "open", "input", "globals", "locals"
}
```

### Invariant 2: Import Whitelist

Only pre-approved modules:

```python
DEFAULT_ALLOWED_IMPORTS = {
    "re",           # Regex
    "json",         # JSON parsing
    "dataclasses",  # Data structures
    "typing",       # Type hints
    "datetime",     # Time handling
    "math",         # Math operations
}
```

Network and file I/O forbidden unless explicitly allowed.

### Invariant 3: Type Safety

All JIT agents must pass `mypy --strict`:

```bash
echo "$source" | mypy --strict -
```

If type check fails, collapse to Ground.

### Invariant 4: Time Bounds

Hard timeout enforced:

```python
async with asyncio.timeout(30):  # 30 second max
    result = await jit_agent.invoke(input)
```

### Invariant 5: Depth Bounds

JIT agents cannot spawn more JIT agents (prevents meta-recursion):

```python
if depth >= MAX_JIT_DEPTH:  # Default: depth 0 only
    raise RuntimeError("JIT recursion forbidden")
```

---

## Relationship to Autopoiesis

**Autopoiesis (Existing)**: Measurement of self-production

```python
autopoiesis_score = lines_generated_by_kgents / total_lines
```

**JIT Compilation (New)**: Active self-production on demand

```python
jit_contribution = ephemeral_agents_compiled / total_invocations
```

JIT agents are the **actualization** of autopoiesis:
- Not just measuring self-production
- Actively producing agents at runtime
- Guided by Judge and Chaosmonger

---

## Anti-patterns

### ❌ Infinite JIT Loops

```python
# BAD: JIT agent that compiles another JIT agent
class MetaMetaArchitect:  # FORBIDDEN
    def invoke(self, intent):
        return MetaArchitect().invoke(intent)
```

**Prevention**: Depth limit enforced (`MAX_JIT_DEPTH = 0`)

### ❌ Sandbox Escape Attempts

```python
# BAD: Trying to access forbidden modules
import os  # BLOCKED by import whitelist
exec("malicious code")  # BLOCKED by restricted builtins
```

**Prevention**: AST analysis + restricted namespace

### ❌ Silent Failures

```python
# BAD: Returning Ground without logging
if not stable:
    return ground  # WHY?
```

**Good Practice**:
```python
if not stability.is_stable:
    logger.warning(f"JIT collapse: {stability.reason}")
    metrics.record("jit_collapse", reason=stability.reason)
    return ground
```

### ❌ Unbounded Compilation

```python
# BAD: No entropy budget check
while True:
    agent = MetaArchitect().invoke(...)  # INFINITE LOOP
```

**Prevention**: Entropy budget diminishes with depth

---

## Test-Driven JIT

Every JIT agent should generate its own validation test:

```python
# Generated agent
class StackTraceParser:
    def parse(self, log: str) -> list[OOMPattern]:
        ...

# Generated test (alongside agent)
def test_stack_trace_parser():
    parser = StackTraceParser()
    sample_log = '''
    Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
        at com.example.App.allocate(App.java:42)
    '''
    patterns = parser.parse(sample_log)
    assert len(patterns) == 1
    assert patterns[0].heap_type == "heap"
```

**Test Generation**:
```python
test_source = await TestGenerator().invoke(TestGenInput(
    intent=intent,
    agent_source=source,
    sample_inputs=context.get("examples", [])
))
```

If generated test fails, collapse to Ground.

---

## Example: JIT Log Parser

**Scenario**: Parse custom log format not known at design time

```python
# Task intent
intent = "Parse NGINX access logs and extract 4xx error patterns"

# Context
context = {
    "log_format": 'combined',
    "sample": '127.0.0.1 - - [01/Jan/2025:12:00:00 +0000] "GET /api HTTP/1.1" 404 512'
}

# Constraints from J-gent (depth=1, budget=0.5)
constraints = {
    "max_complexity": 10,  # 0.5 * 20
    "allowed_imports": ["re", "dataclasses", "typing"],
    "entropy_budget": 0.5
}

# MetaArchitect generates:
source = '''
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class AccessLog:
    ip: str
    timestamp: str
    method: str
    path: str
    status: int
    size: int

class NginxParser:
    PATTERN = re.compile(
        r'(?P<ip>\\S+) - - \\[(?P<time>[^\\]]+)\\] '
        r'"(?P<method>\\S+) (?P<path>\\S+) [^"]+" '
        r'(?P<status>\\d+) (?P<size>\\d+)'
    )

    def parse(self, log_line: str) -> Optional[AccessLog]:
        match = self.PATTERN.match(log_line)
        if not match:
            return None
        return AccessLog(
            ip=match.group("ip"),
            timestamp=match.group("time"),
            method=match.group("method"),
            path=match.group("path"),
            status=int(match.group("status")),
            size=int(match.group("size"))
        )

    def find_4xx_errors(self, logs: list[str]) -> list[AccessLog]:
        return [
            log for line in logs
            if (log := self.parse(line)) and 400 <= log.status < 500
        ]
'''

# Pipeline:
# 1. Chaosmonger: ✅ complexity=3, no forbidden imports
# 2. Judge: ✅ tasteful (clear regex), ethical (read-only), joyful (dataclass)
# 3. Compile: ✅ mypy passes
# 4. Execute:
parser = NginxParser()  # Compiled agent
errors = parser.find_4xx_errors(nginx_logs)
# Result: [AccessLog(ip='127.0.0.1', status=404, ...)]
```

**Lifecycle**:
1. Created on-demand for this task
2. Executed successfully
3. Garbage collected after task completion
4. (Optionally) Cached by hash for reuse

---

## Integration with Existing Agents

### Judge Integration

MetaArchitect output flows through Judge:

```python
# agents/e/judge.py already evaluates generated code
judge_result = await Judge().invoke(JudgeInput(
    source=jit_source,
    criteria=JUDGE_CRITERIA
))
```

No changes needed—JIT source is just another artifact.

### Chaosmonger Integration

JIT stability check uses existing Chaosmonger:

```python
# agents/j/chaosmonger.py already analyzes AST
from agents.j import is_stable

if not is_stable(jit_source, budget=entropy_budget):
    return ground
```

### Bootstrap Integration

JIT uses existing Fix + Ground:

```python
# bootstrap/fix.py: Fixed-point iteration
jit_agent = fix(
    lambda src: refine_agent(src),
    initial=draft_source,
    config=FixConfig(entropy_budget=budget)
)

# bootstrap/ground.py: Safety fallback
if jit_fails:
    return Ground(value=fallback_agent)
```

---

## Future Enhancements

### Global Memoization (Phase 4)

Hash-based agent registry:

```python
global_jit_registry = {
    hash(intent + context): compiled_agent
}
```

Agents share JIT compilations across tasks.

### Agent Markets (Phase 5)

Ephemeral agents can be promoted to persistent:

```python
if jit_agent.invocation_count > 100:
    promote_to_spec(jit_agent)  # Save to spec/
```

Community votes on which JIT agents become permanent.

### Multi-Language JIT (Phase 6)

Extend beyond Python:

```python
MetaArchitect(target_language="rust") -> RustAgentSource
```

---

## See Also

- [reality.md](reality.md) - When to invoke JIT compilation
- [stability.md](stability.md) - Safety constraints (Chaosmonger)
- [lazy.md](lazy.md) - Promise-based deferred execution
- [JGENT_SPEC_PLAN.md](JGENT_SPEC_PLAN.md) - Full implementation plan
