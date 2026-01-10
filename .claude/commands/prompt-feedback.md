Apply TextGRAD feedback to improve the prompt.

Usage: /prompt-feedback "<feedback>"

This command uses the TextGRAD system to apply natural language feedback to the current CLAUDE.md, proposing improvements that can be reviewed and rolled back.

## Examples

```bash
# Be more concise
/prompt-feedback "be more concise in the systems section"

# Add detail
/prompt-feedback "add more detail about testing patterns"

# Remove content
/prompt-feedback "remove the section about deprecated features"

# Clarify
/prompt-feedback "clarify the AGENTESE protocol explanation"
```

## How It Works

1. **Feedback Parsing**: Your feedback is parsed into textual gradients
2. **Rigidity Check**: Sections are filtered by rigidity (soft sections change more easily)
3. **Improvement**: TextGRAD applies changes to targeted sections
4. **Checkpoint**: A checkpoint is created for rollback capability
5. **Preview**: Shows the proposed changes

## TextGRAD Directions

The system understands these improvement directions:
- **CONDENSE**: Make content shorter
- **EXPAND**: Add more detail
- **CLARIFY**: Make content clearer
- **REMOVE**: Remove specific content
- **ADD**: Add new content

## After Applying Feedback

- View the proposed changes in the output
- If satisfied: `kg prompt compile --output CLAUDE.md`
- If not satisfied: `kg prompt rollback <checkpoint_id>`

## Implementation

Run: `uv run python -m protocols.prompt.cli compile --feedback "..."`

See:
- `impl/claude/protocols/prompt/textgrad/`
- `impl/claude/protocols/prompt/cli.py`
