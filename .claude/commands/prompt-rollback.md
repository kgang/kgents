---
description: Rollback CLAUDE.md prompt to a previous checkpoint
argument-hint: <checkpoint_id>
---

Rollback the prompt to a previous checkpoint.

Usage: /prompt-rollback <checkpoint_id>

This command restores CLAUDE.md to a previous version, creating a new checkpoint of the current state (so you can undo the rollback if needed).

## Examples

```bash
# Rollback to a specific checkpoint
/prompt-rollback abc12345

# Use full ID if needed
/prompt-rollback abc12345def67890abcdef1234567890
```

## Finding Checkpoint IDs

Use `/prompt-history` to see available checkpoints:

```bash
/prompt-history
```

Copy the checkpoint ID (at least 8 characters) from the output.

## What Happens

1. **Find Checkpoint**: Locates the checkpoint matching your ID
2. **Create Safety Checkpoint**: Saves current state before rollback
3. **Restore Content**: Restores the saved content from checkpoint
4. **Show Result**: Displays what was restored

## Output

```
Rolling back to checkpoint: abc12345def67890abcdef1234567890
  Original reason: TextGRAD: be more concise...

✓ Rollback successful!
  New checkpoint: 111222333444555666777888999aaa
  Restored content: 5432 chars

Reasoning trace:
  - Found checkpoint abc12345...
  - Created safety checkpoint 111222...
  - Restored content from abc12345...
```

## Undo a Rollback

If the rollback wasn't what you wanted:

```bash
/prompt-rollback <new_checkpoint_id>
```

The "New checkpoint" ID shown after rollback is your safety net.

## Implementation

Run: `uv run python -m protocols.prompt.cli rollback <id>`

See: `impl/claude/protocols/prompt/rollback/`
