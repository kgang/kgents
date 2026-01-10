---
description: Trace execution path, data flow, or dependency chain for a target
argument-hint: [target]
---

Trace the execution path, data flow, or dependency chain for a target.

## Target: $ARGUMENTS

If no arguments provided, ask what to trace.

## Trace Types

### 1. Call Trace (default)
Trace how a function/method is called throughout the codebase.

```bash
# Find all callers
grep -r "target_function" --include="*.py"
```

### 2. Data Flow Trace (`--data`)
Trace how data flows from input to output.

```
Input → Transform A → Transform B → Output
  ↓
  Where does this get modified?
  What are the intermediate representations?
```

### 3. Dependency Trace (`--deps`)
Trace what a module depends on and what depends on it.

```
Upstream (imports):
  └── module_a
  └── module_b

Downstream (imported by):
  └── consumer_x
  └── consumer_y
```

### 4. Event Trace (`--events`)
Trace event flow through Flux/async systems.

```
Event Source → FluxAgent → Perturbation Queue → Handler → Output
```

## Output Format

```
[TRACE] <type>: <target>

Path:
1. <step> (<file>:<line>)
2. <step> (<file>:<line>)
...

Key Observations:
- <insight about the path>
- <potential issue or optimization>

Related Paths:
- <alternative path if exists>
```

## Arguments

- `function_name` — Trace calls to this function
- `--data` — Trace data flow instead of calls
- `--deps` — Trace dependency graph
- `--events` — Trace event flow
- `--depth N` — Limit trace depth (default: 5)

## Examples

```
/trace cmd_soul
/trace FluxAgent.start --depth 3
/trace agents/flux --deps
/trace SemaphoreToken --data
```
