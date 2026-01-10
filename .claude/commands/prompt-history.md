---
description: Show the evolution history of the CLAUDE.md prompt
argument-hint: [--limit N]
---

Show the evolution history of the prompt.

Usage: /prompt-history [--limit N]

This command shows a timeline of prompt changes, with checkpoint IDs that can be used for rollback.

## Examples

```bash
# Show last 10 changes
/prompt-history

# Show last 5 changes
/prompt-history --limit 5

# Show all history
/prompt-history --limit 100
```

## What This Shows

For each checkpoint:
- **Checkpoint ID**: Short ID for referencing (use with rollback)
- **Timestamp**: When the change was made
- **Reason**: Why the change was made
- **Sections**: Number of sections (and change count)
- **Characters**: Content length (and change count)

## Timeline Format

```
PROMPT EVOLUTION TIMELINE
============================================================

├─ [abc12345] 2025-12-16 10:30
│     Reason: TextGRAD: be more concise...
│     Sections: 8 (+1)
│     Characters: 5432 (-200)
│
└─ [def67890] 2025-12-16 09:15
      Reason: CLI compilation
      Sections: 7 (0)
      Characters: 5632 (+100)

Total checkpoints: 2
Use 'rollback <id>' to restore a previous version.
```

## Checkpoint Storage

Checkpoints are stored in: `~/.kgents/prompt-history/`

Each checkpoint contains:
- Full content before and after
- Section lists
- Reasoning traces
- Metadata

## Implementation

Run: `uv run python -m protocols.prompt.cli history [--limit N]`

See: `impl/claude/protocols/prompt/rollback/`
