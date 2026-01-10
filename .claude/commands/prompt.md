Show the current compiled CLAUDE.md with optional analysis.

Usage: /prompt [--show-reasoning] [--show-habits]

This command compiles and displays the current CLAUDE.md prompt, optionally showing:
- **Reasoning traces**: Why each section was included (--show-reasoning)
- **Habit influence**: How PolicyVector affected compilation (--show-habits)

## Examples

```bash
# Basic compilation
/prompt

# With reasoning traces
/prompt --show-reasoning

# With habit influence
/prompt --show-habits

# Both
/prompt --show-reasoning --show-habits
```

## What This Shows

### Basic Mode
- Section list with token counts
- Total prompt statistics
- Compiled content

### With --show-reasoning
Shows the reasoning trace for each section, explaining:
- Why the section was included
- Source files used
- Any conditional logic applied

### With --show-habits
Shows the PolicyVector that influenced compilation:
- Verbosity preference (0.0-1.0)
- Formality preference (0.0-1.0)
- Risk tolerance (0.0-1.0)
- Domain focus areas
- Section weights
- Where habits were learned from (git, sessions, code)

## Implementation

Run: `uv run python -m protocols.prompt.cli compile [flags]`

See: `impl/claude/protocols/prompt/cli.py`
