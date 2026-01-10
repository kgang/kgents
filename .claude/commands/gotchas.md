---
description: Surface critical gotchas and warnings for the current task context
argument-hint: [task]
---

Surface all critical gotchas for current context using Living Docs.

## Arguments: $ARGUMENTS

## Action Protocol

### Step 1: Run the gotchas query

```bash
# If arguments provided (e.g., /gotchas brain):
kg docs teaching --severity critical --module "$ARGUMENTS" --json

# If no arguments:
kg docs teaching --severity critical --json
```

### Step 2: Parse and display

Group gotchas by module and display:

```
[GOTCHAS] Critical gotchas for: <module or "all">

MODULE: <module_name>
─────────────────────────────────
  <symbol>
    Insight: <insight text>
    Evidence: <evidence if available>
    Severity: critical

  <symbol>
    Insight: <insight text>
    Evidence: <evidence if available>

MODULE: <module_name>
─────────────────────────────────
  ...

Total: <N> critical gotchas
```

### Step 3: If no results

If `kg docs teaching` returns empty or the command is not available:

```bash
# Fallback: Search for gotcha annotations in specs
grep -r "gotcha:" spec/ --include="*.md"

# Or search for WARNING/CRITICAL patterns
grep -ri "critical\|gotcha\|anti-pattern" spec/ docs/skills/ --include="*.md"
```

Surface the most relevant findings.

## Common Module Patterns

| Argument | What it filters |
|----------|-----------------|
| `brain` | Brain service gotchas |
| `agentese` | AGENTESE protocol gotchas |
| `witness` | Witness system gotchas |
| `flux` | Flux streaming gotchas |
| `di` or `dependency` | DI/container gotchas |
| `storage` | Storage/persistence gotchas |
| `town` | Agent Town gotchas |

## Examples

```
/gotchas              → All critical gotchas
/gotchas brain        → Brain service gotchas
/gotchas agentese     → AGENTESE protocol gotchas
/gotchas flux         → Flux streaming gotchas
/gotchas di           → Dependency injection gotchas
```

## Key Gotchas to Always Surface

If Living Docs isn't available, these are the critical gotchas from CLAUDE.md:

### DI Enlightened Resolution
```
Container respects Python signature semantics:
- REQUIRED deps (no default) → DependencyNotFoundError immediately
- OPTIONAL deps (= None default) → skipped gracefully
- DECLARED deps (@node(dependencies=(...))) → ALL treated as required

FAIL-FAST: @node validates dependency names at IMPORT time
  If @node(dependencies=("foo",)) but __init__ has no 'foo' param → TypeError
```

### AGENTESE Discovery
```
@node runs at import time: If module not imported, node not registered
_import_node_modules() in gateway.py: Ensures all nodes load before discovery
Two-way mapping needed: AGENTESE path ↔ React route in NavigationTree
```

### Event-Driven Architecture
```
Three buses: DataBus (storage) → SynergyBus (cross-jewel) → EventBus (fan-out)
Bridge pattern: DataBus → SynergyBus via wire_data_to_synergy()
```

### Anti-Patterns
```
Silent catch blocks: swallowing errors shows blank UI; always surface
Timer-driven loops create zombies—use event-driven Flux
Context dumping: large payloads tax every turn
```

## Important

- Actually RUN `kg docs teaching` - don't just describe it
- Parse the JSON output and format it readably
- If the command fails, use the fallback search
- Always surface the embedded gotchas from CLAUDE.md as a baseline
- Group by module for scanability
