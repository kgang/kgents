# Flowfile Examples

These flowfiles demonstrate the **Composable** and **Generative** principles in action.

## Available Flows

| Flow | Purpose | Key Agents |
|------|---------|------------|
| `code-review.flow.yaml` | Principled code review | P-gent, Bootstrap |
| `hypothesis-test.flow.yaml` | Scientific method for code | B-gent, T-gent, L-gent |
| `metaphor-solve.flow.yaml` | Problem solving via metaphor | Psi-gent, Bootstrap |
| `tongue-create.flow.yaml` | DSL synthesis | G-gent, T-gent, L-gent |

## Usage

```bash
# Run a flowfile
kgents flow run code-review.flow.yaml src/main.py

# Explain what a flow does
kgents flow explain hypothesis-test.flow.yaml

# Validate a flowfile
kgents flow validate tongue-create.flow.yaml

# Run with variables
kgents flow run metaphor-solve.flow.yaml "how to improve team communication" \
  --var domain=organization \
  --var abstraction=0.7
```

## Composition Patterns

### Sequential (Default)
Steps execute in order, each receiving output from the previous.

### Conditional
Steps can be skipped based on Jinja2 expressions:
```yaml
condition: "{{ judge.output.verdict != 'ACCEPT' }}"
```

### Debug Snapshots
Enable `debug: true` on any step to capture state for TUI inspection.

### Error Handling
- `halt`: Stop on first error (default)
- `continue`: Log error, continue to next step
- `retry`: Retry up to N times

## Creating Your Own Flows

1. Start with a clear pipeline: Parse → Transform → Validate
2. Use `debug: true` liberally during development
3. Add `condition` for optional steps
4. Register artifacts with L-gent for discoverability

*"Spec is compression; design should generate implementation."* — Principle 7
