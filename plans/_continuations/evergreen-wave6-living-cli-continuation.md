# Evergreen Wave 6 Continuation: Living CLI + AGENTESE Paths

> *"The prompt that can be invoked is the prompt that can improve itself."*

**Wave:** 6 (Final Wave)
**Status:** READY TO START
**Date:** 2025-12-16
**Previous Wave:** Wave 5 (Multi-Source Fusion + Metrics) ✅ COMPLETE
**Guard:** `[phase=ACT][entropy=0.08][dogfood=true][final_wave=true]`

---

## Context for Claude

You are continuing the Evergreen Prompt System implementation. Waves 1-5 are complete with **317 tests passing**. This is the final wave that brings everything together into a usable CLI experience.

### What's Already Built

```
impl/claude/protocols/prompt/
├── __init__.py                      # Package exports (all waves)
├── polynomial.py                    # PROMPT_POLYNOMIAL state machine
├── section_base.py                  # Section types + utilities
├── compiler.py                      # Compilation pipeline
├── monad.py                         # PromptM monad with laws
├── soft_section.py                  # SoftSection with rigidity spectrum
├── cli.py                           # Basic CLI (compile, history, rollback, diff)
│
├── sections/                        # 9 section compilers
│   ├── identity.py, principles.py, agentese.py
│   ├── systems.py, directories.py, skills.py
│   ├── commands.py, forest.py, context.py
│   └── habits.py                    # Wave 4
│
├── sources/                         # Content sources
│   ├── base.py, file_source.py, git_source.py, llm_source.py
│
├── rollback/                        # Full rollback capability
│   ├── checkpoint.py, registry.py, storage.py
│
├── habits/                          # Habit learning (Wave 4)
│   ├── encoder.py, git_analyzer.py, session_analyzer.py
│   ├── code_analyzer.py, policy.py
│
├── textgrad/                        # Self-improvement (Wave 4)
│   ├── improver.py, feedback_parser.py, gradient.py
│
├── fusion/                          # Multi-source fusion (Wave 5)
│   ├── similarity.py, conflict.py, resolution.py, fusioner.py
│
├── metrics/                         # Observability (Wave 5)
│   ├── schema.py, emitter.py
│
└── _tests/                          # 317 tests
```

### Current CLI (Wave 3)

```bash
# Basic commands exist
uv run python -m protocols.prompt.cli compile [--checkpoint/--no-checkpoint] [--reason]
uv run python -m protocols.prompt.cli compare
uv run python -m protocols.prompt.cli history [--limit N]
uv run python -m protocols.prompt.cli rollback <checkpoint_id>
uv run python -m protocols.prompt.cli diff <id1> <id2>
```

---

## Wave 6 Mission: Living CLI + AGENTESE Paths

Wave 6 brings everything together into a **living, self-improving CLI experience**:

1. **Rich CLI Commands** - Full `/prompt` command with all flags
2. **AGENTESE Paths** - Register `concept.prompt.*` paths
3. **Slash Commands** - `.claude/commands/` for Claude Code integration
4. **Self-Improvement Loop** - `--feedback` and `--auto-improve` flags

### Target User Experience

```bash
# View current prompt
kg prompt                           # or: kg concept.prompt.manifest

# View with reasoning traces
kg prompt --show-reasoning          # Shows why each section was included

# View with habit influence
kg prompt --show-habits             # Shows how PolicyVector affected compilation

# Provide feedback (TextGRAD)
kg prompt --feedback "be more concise in systems section"

# Auto-improve with safety
kg prompt --auto-improve            # Proposes improvement, asks for approval

# History and rollback
kg prompt --history                 # Timeline of changes
kg prompt --rollback abc123         # Restore checkpoint
kg prompt --diff abc123 def456      # Compare checkpoints

# Preview changes before compiling
kg prompt --preview                 # Show what would change

# Emit metrics
kg prompt --emit-metrics            # Write to metrics/evergreen/
```

---

## Implementation Tasks

### P0: Enhance CLI Commands

**File:** `impl/claude/protocols/prompt/cli.py`

Add these flags to the existing CLI:

```python
@click.command()
@click.option("--show-reasoning", is_flag=True, help="Show reasoning traces")
@click.option("--show-habits", is_flag=True, help="Show habit influence")
@click.option("--feedback", type=str, help="Apply TextGRAD feedback")
@click.option("--auto-improve", is_flag=True, help="Self-improve with approval")
@click.option("--preview", is_flag=True, help="Preview changes without writing")
@click.option("--emit-metrics", is_flag=True, help="Emit metrics to JSONL")
def compile(...):
    ...
```

**Key behaviors:**
- `--show-reasoning`: Include `reasoning_trace` in output
- `--show-habits`: Show PolicyVector influence on each section
- `--feedback`: Parse feedback, apply TextGRAD, checkpoint result
- `--auto-improve`: Run HabitEncoder, propose changes, ask for confirmation
- `--preview`: Compile but don't write, show diff against current
- `--emit-metrics`: Call MetricsEmitter during compilation

### P1: Create AGENTESE Context

**File:** `impl/claude/protocols/agentese/contexts/prompt.py`

Register `concept.prompt.*` paths:

```python
from protocols.agentese import LogosContext, register_context

@register_context("concept.prompt")
class PromptContext(LogosContext):
    """AGENTESE context for prompt system operations."""

    async def manifest(self, umwelt: Umwelt) -> str:
        """Render current CLAUDE.md."""
        compiler = PromptCompiler()
        result = compiler.compile(CompilationContext.from_umwelt(umwelt))
        return result.content

    async def evolve(self, umwelt: Umwelt, feedback: str = "") -> EvolutionResult:
        """Propose prompt evolution via TextGRAD."""
        ...

    async def validate(self, umwelt: Umwelt) -> ValidationResult:
        """Run category law checks."""
        ...

    async def compile(self, umwelt: Umwelt, **options) -> CompiledPrompt:
        """Force recompilation with options."""
        ...

    async def history(self, umwelt: Umwelt, limit: int = 10) -> list[CheckpointSummary]:
        """Get evolution history."""
        ...

    async def rollback(self, umwelt: Umwelt, checkpoint_id: str) -> RollbackResult:
        """Rollback to checkpoint."""
        ...

    async def diff(self, umwelt: Umwelt, id1: str, id2: str) -> DiffResult:
        """Diff two checkpoints."""
        ...
```

**Paths to register:**
- `concept.prompt.manifest` → Current CLAUDE.md
- `concept.prompt.evolve` → Propose evolution (TextGRAD)
- `concept.prompt.validate` → Run law checks
- `concept.prompt.compile` → Force recompilation
- `concept.prompt.history` → Version history
- `concept.prompt.rollback` → Restore checkpoint
- `concept.prompt.diff` → Compare checkpoints

### P2: Create Slash Commands

**Directory:** `.claude/commands/`

Create Claude Code slash commands:

```markdown
# .claude/commands/prompt.md
Show the current compiled CLAUDE.md with optional flags.

Usage: /prompt [--show-reasoning] [--show-habits]

This command compiles and displays the current prompt, optionally showing:
- Reasoning traces (why each section was included)
- Habit influence (how PolicyVector affected compilation)
```

```markdown
# .claude/commands/prompt-feedback.md
Apply TextGRAD feedback to improve the prompt.

Usage: /prompt-feedback "<feedback>"

Examples:
- /prompt-feedback "be more concise in the systems section"
- /prompt-feedback "add more detail about testing patterns"

The feedback is parsed, applied via TextGRAD, and checkpointed for rollback.
```

```markdown
# .claude/commands/prompt-history.md
Show the evolution history of the prompt.

Usage: /prompt-history [--limit N]

Shows a timeline of prompt changes with checkpoint IDs for rollback.
```

```markdown
# .claude/commands/prompt-rollback.md
Rollback the prompt to a previous checkpoint.

Usage: /prompt-rollback <checkpoint_id>

Use /prompt-history to find checkpoint IDs.
```

### P3: Rich Output Formatting

**File:** `impl/claude/protocols/prompt/cli_output.py` (new)

Create rich output formatters:

```python
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree
from rich.table import Table
from rich.syntax import Syntax

class PromptOutputFormatter:
    """Format prompt compilation output for CLI."""

    def format_compiled(
        self,
        prompt: CompiledPrompt,
        show_reasoning: bool = False,
        show_habits: bool = False,
    ) -> str:
        """Format compiled prompt for display."""
        ...

    def format_reasoning_tree(self, traces: list[str]) -> Tree:
        """Format reasoning traces as a tree."""
        ...

    def format_habit_table(self, policy: PolicyVector) -> Table:
        """Format habit influence as a table."""
        ...

    def format_diff(self, diff: DiffResult) -> str:
        """Format diff with syntax highlighting."""
        ...

    def format_history_timeline(self, history: list[CheckpointSummary]) -> str:
        """Format history as a timeline."""
        ...
```

### P4: Wire Metrics Emission

**Update:** `impl/claude/protocols/prompt/compiler.py`

Wire metrics emission into the compilation pipeline:

```python
async def compile(self, context: CompilationContext) -> CompiledPrompt:
    start_time = time.time()

    # ... existing compilation logic ...

    # Emit metrics if enabled
    if context.emit_metrics:
        from .metrics import emit_compilation_metrics
        emit_compilation_metrics(
            prompt=result,
            context=context,
            compilation_time_ms=(time.time() - start_time) * 1000,
            checkpoint_id=checkpoint_id,
        )

    return result
```

### P5: Tests

**File:** `impl/claude/protocols/prompt/_tests/test_cli_wave6.py`

```python
class TestCLIWave6:
    """Tests for Wave 6 CLI enhancements."""

    def test_show_reasoning_flag(self):
        """--show-reasoning includes traces in output."""
        ...

    def test_show_habits_flag(self):
        """--show-habits shows PolicyVector influence."""
        ...

    def test_feedback_flag(self):
        """--feedback applies TextGRAD improvement."""
        ...

    def test_auto_improve_flag(self):
        """--auto-improve proposes changes for approval."""
        ...

    def test_preview_flag(self):
        """--preview shows diff without writing."""
        ...

    def test_emit_metrics_flag(self):
        """--emit-metrics writes to JSONL."""
        ...


class TestAGENTESEPromptContext:
    """Tests for concept.prompt.* AGENTESE paths."""

    def test_manifest_returns_compiled_prompt(self):
        ...

    def test_evolve_applies_textgrad(self):
        ...

    def test_validate_checks_laws(self):
        ...

    def test_history_returns_checkpoints(self):
        ...

    def test_rollback_restores_checkpoint(self):
        ...

    def test_diff_compares_checkpoints(self):
        ...
```

---

## Files to Create

| File | Purpose |
|------|---------|
| `cli_output.py` | Rich output formatting (trees, tables, diffs) |
| `protocols/agentese/contexts/prompt.py` | AGENTESE paths registration |
| `.claude/commands/prompt.md` | Slash command: /prompt |
| `.claude/commands/prompt-feedback.md` | Slash command: /prompt-feedback |
| `.claude/commands/prompt-history.md` | Slash command: /prompt-history |
| `.claude/commands/prompt-rollback.md` | Slash command: /prompt-rollback |
| `_tests/test_cli_wave6.py` | Wave 6 CLI tests |
| `_tests/test_agentese_prompt.py` | AGENTESE paths tests |

---

## Success Criteria

### Quantitative
- [ ] All CLI flags work (`--show-reasoning`, `--show-habits`, `--feedback`, etc.)
- [ ] All AGENTESE paths registered and functional
- [ ] All slash commands work in Claude Code
- [ ] Metrics emitted to `metrics/evergreen/*.jsonl`
- [ ] Test count > 340 (currently 317)

### Qualitative
- [ ] `/prompt` shows a useful, readable output
- [ ] `/prompt --feedback "..."` produces sensible changes
- [ ] Reasoning traces are helpful, not noisy
- [ ] History timeline is easy to understand
- [ ] The system feels self-sustaining

### The Ultimate Test

```bash
# Can you use the system to improve itself?
kg prompt --feedback "be more concise in the systems section"
# → TextGRAD applies improvement
# → Checkpoint created
# → Test with new prompt
# → If worse: kg prompt --rollback <id>
```

If this works smoothly: **Wave 6 is complete. The Evergreen Prompt System is alive.**

---

## N-Phase Cycle

### UNDERSTAND Phase
- [ ] Study existing CLI patterns in `protocols/cli/handlers/`
- [ ] Study AGENTESE context registration in `protocols/agentese/contexts/`
- [ ] Study slash command format in `.claude/commands/` (if any exist)
- [ ] Review Rich library for output formatting

### ACT Phase
- [ ] P0: Enhance CLI with all flags
- [ ] P1: Create AGENTESE context for `concept.prompt.*`
- [ ] P2: Create slash commands
- [ ] P3: Create rich output formatters
- [ ] P4: Wire metrics emission
- [ ] P5: Write comprehensive tests

### REFLECT Phase (Dogfooding)
- [ ] Start fresh session with compiled prompt
- [ ] Use `/prompt --show-reasoning` to see traces
- [ ] Provide feedback: `/prompt --feedback "be more concise"`
- [ ] Verify improvement was checkpointed
- [ ] Rollback: `/prompt --rollback <id>`
- [ ] Use AGENTESE: `kg concept.prompt.manifest`
- [ ] Complete a real development task with the system
- [ ] Write epilogue: `plans/_epilogues/2025-12-XX-evergreen-wave6-complete.md`

---

## Dependencies and Patterns

### CLI Handler Pattern (from existing codebase)

```python
# protocols/cli/handlers/example.py
import click
from rich.console import Console

console = Console()

@click.command()
@click.option("--verbose", "-v", is_flag=True)
def example(verbose: bool):
    """Example command."""
    if verbose:
        console.print("[dim]Verbose output...[/dim]")
    console.print("[green]Done![/green]")
```

### AGENTESE Context Pattern (from existing codebase)

```python
# protocols/agentese/contexts/example.py
from dataclasses import dataclass
from protocols.agentese import LogosContext, Umwelt

@dataclass
class ExampleContext(LogosContext):
    """Example AGENTESE context."""

    async def manifest(self, umwelt: Umwelt) -> str:
        """Return manifestation for observer."""
        return "example content"
```

### Slash Command Format

```markdown
# .claude/commands/example.md
Brief description of what this command does.

Usage: /example [args]

Detailed explanation and examples.
```

---

## Anti-Patterns to Avoid

1. **Over-complicated output** - Keep it readable, not overwhelming
2. **Silent failures** - Always show errors clearly
3. **Breaking existing CLI** - Ensure backward compatibility
4. **Skipping checkpoints** - Always checkpoint before changes
5. **Ignoring metrics** - Emit metrics for observability
6. **Untested paths** - Every AGENTESE path needs tests

---

## Begin

When you receive this prompt:

1. Verify Wave 5 is complete: `uv run python -m pytest protocols/prompt/_tests/ -q`
2. Study the existing CLI in `cli.py`
3. Study AGENTESE context registration
4. Announce: "Starting Wave 6: Living CLI + AGENTESE Paths"
5. Begin with P0 (enhance CLI commands)

---

*"The prompt that can be invoked is the prompt that has arrived. Wave 6 is not the end—it is the beginning of self-cultivation."*

*Version 0.5.0 — Living CLI Architecture (2025-12-16)*
