"""
CLI entry points for the Evergreen Prompt System.

Usage:
    python -m protocols.prompt.cli compile [--output PATH] [--checkpoint/--no-checkpoint]
    python -m protocols.prompt.cli compare [--compiled PATH]
    python -m protocols.prompt.cli history [--limit N]
    python -m protocols.prompt.cli rollback <checkpoint_id>
    python -m protocols.prompt.cli diff <id1> <id2>

Wave 6 additions:
    python -m protocols.prompt.cli compile --show-reasoning
    python -m protocols.prompt.cli compile --show-habits
    python -m protocols.prompt.cli compile --feedback "be more concise"
    python -m protocols.prompt.cli compile --auto-improve
    python -m protocols.prompt.cli compile --preview
    python -m protocols.prompt.cli compile --emit-metrics

See: plans/_continuations/evergreen-wave6-living-cli-continuation.md
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .cli_output import PromptOutputFormatter
from .compiler import CompilationContext, PromptCompiler
from .rollback import RollbackRegistry, get_default_registry
from .sections import get_default_compilers, get_full_compilers


def compile_prompt(
    output_path: Path | None = None,
    checkpoint: bool = True,
    reason: str | None = None,
    show_reasoning: bool = False,
    show_habits: bool = False,
    feedback: str | None = None,
    auto_improve: bool = False,
    preview: bool = False,
    emit_metrics: bool = False,
    refine: bool = False,
    export_path: Path | None = None,
    include_dynamic: bool = True,
) -> str:
    """
    Compile CLAUDE.md from sections.

    Args:
        output_path: Optional path to save compiled prompt
        checkpoint: If True, create a checkpoint before compilation
        reason: Reason for this compilation (for checkpoint)
        show_reasoning: If True, show reasoning traces
        show_habits: If True, show habit influence (PolicyVector)
        feedback: If provided, apply TextGRAD feedback
        auto_improve: If True, run habit encoder and propose improvements
        preview: If True, show preview without writing
        emit_metrics: If True, emit metrics to JSONL
        refine: If True, start interactive refinement dialogue
        export_path: If provided, export to this path (no checkpoint)
        include_dynamic: If True, include Forest and Context sections (default)

    Returns the compiled content and optionally writes to file.
    """
    start_time = time.time()
    formatter = PromptOutputFormatter()

    # Set up compiler with section compilers
    # Use full compilers (includes Forest + Context) by default
    compilers = get_full_compilers() if include_dynamic else get_default_compilers()
    compiler = PromptCompiler(section_compilers=compilers, version=1)

    # Create context pointing to project root
    # Assuming this is run from impl/claude/
    project_root = Path(__file__).parent.parent.parent.parent.parent
    context = CompilationContext(
        project_root=project_root,
        include_timestamp=True,
    )

    # Load current prompt for checkpoint comparison
    before_content = ""
    before_sections: tuple[str, ...] = ()
    claude_md_path = project_root / "CLAUDE.md"

    if checkpoint or preview or feedback:
        if claude_md_path.exists():
            before_content = claude_md_path.read_text(encoding="utf-8")
            # Extract section names from existing content (simple heuristic)
            before_sections = tuple(
                line.strip("# ").strip()
                for line in before_content.split("\n")
                if line.startswith("## ")
            )

    # Handle export mode (simple output, no checkpoint)
    if export_path:
        exp_compilers = get_full_compilers() if include_dynamic else get_default_compilers()
        exp_compiler = PromptCompiler(section_compilers=exp_compilers, version=1)
        result = exp_compiler.compile(context)
        result.save(export_path)
        print(f"Exported prompt to: {export_path}")
        print(f"  Size: {len(result.content)} chars (~{result.token_count} tokens)")
        return result.content

    # Handle interactive refine mode
    if refine:
        result = _run_interactive_refine(
            project_root=project_root,
            before_content=before_content,
            formatter=formatter,
        )
        if result:
            return result

    # Apply TextGRAD feedback if provided
    if feedback:
        result = _apply_textgrad_feedback(
            sections=_content_to_sections(before_content),
            feedback=feedback,
            formatter=formatter,
        )
        if result:
            return result

    # Auto-improve if requested
    if auto_improve:
        result = _run_auto_improve(
            project_root=project_root,
            before_content=before_content,
            formatter=formatter,
        )
        if result:
            return result

    # Compile
    result = compiler.compile(context)
    compilation_time_ms = (time.time() - start_time) * 1000

    # Preview mode - show diff without writing
    if preview:
        preview_output = formatter.format_preview(before_content, result.content)
        print(preview_output)
        return result.content

    # Load or generate PolicyVector for show_habits
    policy = None
    if show_habits:
        policy = _get_policy_vector(project_root)

    # Create checkpoint if enabled and content changed
    checkpoint_id = None
    if checkpoint and before_content and before_content != result.content:
        registry = get_default_registry()
        registry.set_current(before_content, before_sections)
        checkpoint_id = registry.checkpoint(
            before_content=before_content,
            after_content=result.content,
            before_sections=before_sections,
            after_sections=tuple(result.section_names()),
            reason=reason or "CLI compilation",
        )
        print(f"  Checkpoint: {checkpoint_id}")

    # Emit metrics if enabled
    if emit_metrics:
        _emit_compilation_metrics(
            prompt=result,
            context=context,
            compilation_time_ms=compilation_time_ms,
            checkpoint_id=checkpoint_id,
        )
        print("  Metrics emitted to metrics/evergreen/")

    # Save if output path provided
    if output_path:
        result.save(output_path)

        # Format output
        if show_reasoning or show_habits:
            output = formatter.format_compiled(
                result,
                show_reasoning=show_reasoning,
                show_habits=show_habits,
                policy=policy,
            )
            print(output)
        else:
            print(f"Compiled prompt saved to: {output_path}")
            print(f"  Sections: {result.section_names()}")
            print(f"  Tokens: ~{result.token_count}")
            print(f"  Time: {compilation_time_ms:.1f}ms")

        return result.content

    # No output path - print to stdout
    if show_reasoning or show_habits:
        output = formatter.format_compiled(
            result,
            show_reasoning=show_reasoning,
            show_habits=show_habits,
            policy=policy,
        )
        print(output)
    else:
        print(result.content)

    return result.content


def _content_to_sections(content: str) -> dict[str, str]:
    """Parse CLAUDE.md content into sections dict."""
    sections: dict[str, str] = {}
    current_section = None
    current_lines: list[str] = []

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = line[3:].strip()
            current_lines = []
        elif current_section:
            current_lines.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_lines)

    return sections


def _apply_textgrad_feedback(
    sections: dict[str, str],
    feedback: str,
    formatter: PromptOutputFormatter,
) -> str | None:
    """Apply TextGRAD feedback to sections."""
    try:
        from .rollback import get_default_registry
        from .textgrad import TextGRADImprover

        print(f"Applying TextGRAD feedback: {feedback[:50]}...")

        registry = get_default_registry()
        improver = TextGRADImprover(
            learning_rate=0.5,
            rollback_registry=registry,
        )

        result = improver.improve(sections, feedback)

        output = formatter.format_improvement_result(
            original=result.original_content,
            improved=result.improved_content,
            sections_modified=result.sections_modified,
            reasoning_trace=result.reasoning_trace,
            checkpoint_id=result.checkpoint_id,
        )
        print(output)

        if result.content_changed:
            print("\nTo apply this change, use: kg prompt compile --output CLAUDE.md")
            print("To rollback: kg prompt rollback <checkpoint_id>")

        return result.improved_content

    except ImportError as e:
        print(f"TextGRAD not available: {e}")
        return None
    except Exception as e:
        print(f"Error applying feedback: {e}")
        return None


def _run_auto_improve(
    project_root: Path,
    before_content: str,
    formatter: PromptOutputFormatter,
) -> str | None:
    """Run auto-improvement with habit encoder."""
    try:
        from .habits import HabitEncoder
        from .habits.policy import PolicyVector

        print("Running auto-improvement with habit encoder...")

        # Encode habits
        encoder = HabitEncoder(project_root=project_root)
        policy = encoder.encode()

        # Show policy
        table = formatter.format_habit_table(policy)
        print(table)
        print()

        # Generate improvement suggestions based on policy
        suggestions = _generate_improvement_suggestions(policy, before_content)

        if suggestions:
            print("\nSuggested improvements based on your habits:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")

            print("\nWould you like to apply these suggestions? (y/n)")
            # In a real implementation, we'd wait for user input
            # For now, just show the suggestions
            print("(Auto-apply not implemented - use --feedback to apply specific changes)")
        else:
            print("No improvements suggested based on current habits.")

        return None

    except ImportError as e:
        print(f"Habit encoder not available: {e}")
        return None
    except Exception as e:
        print(f"Error in auto-improve: {e}")
        return None


def _generate_improvement_suggestions(
    policy: "PolicyVector",
    content: str,
) -> list[str]:
    """Generate improvement suggestions based on policy."""
    suggestions: list[str] = []

    # Verbosity suggestions
    if policy.verbosity < 0.4:
        if len(content) > 10000:
            suggestions.append("Consider condensing content (your style prefers conciseness)")
    elif policy.verbosity > 0.7:
        suggestions.append("Consider adding more detail (your style prefers thoroughness)")

    # Domain focus suggestions
    if policy.domain_focus:
        top_domain = max(policy.domain_focus, key=lambda x: x[1])
        domain_name, focus = top_domain
        if focus > 0.6:
            suggestions.append(f"Consider emphasizing {domain_name} content (high focus area)")

    return suggestions


def _run_interactive_refine(
    project_root: Path,
    before_content: str,
    formatter: PromptOutputFormatter,
) -> str | None:
    """
    Run interactive refinement dialogue.

    This allows iterative feedback until the user is satisfied.
    Each round applies TextGRAD feedback and shows the result.

    Note: In non-interactive contexts (like Claude Code), this prints
    instructions and the user should use --feedback directly.
    """
    print("=" * 60)
    print("INTERACTIVE REFINEMENT MODE")
    print("=" * 60)
    print()
    print("Enter feedback to improve the prompt, or:")
    print("  'done' - Exit and keep current version")
    print("  'undo' - Rollback to previous checkpoint")
    print("  'show' - Show current prompt")
    print("  'help' - Show help")
    print()

    # Check if we're in an interactive terminal
    if not sys.stdin.isatty():
        print("Note: Not running in interactive terminal.")
        print("Use --feedback '<text>' to apply specific feedback.")
        print()
        return None

    sections = _content_to_sections(before_content)
    current_content = before_content
    last_checkpoint_id = None

    try:
        from .rollback import get_default_registry
        from .textgrad import TextGRADImprover

        registry = get_default_registry()
        improver = TextGRADImprover(
            learning_rate=0.5,
            rollback_registry=registry,
        )

        while True:
            try:
                feedback = input("\nEnter feedback (or command): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nExiting interactive mode.")
                break

            if not feedback:
                continue

            if feedback.lower() == "done":
                print("\nExiting interactive refinement. Current version retained.")
                break
            elif feedback.lower() == "help":
                print("\nCommands:")
                print("  done - Exit and keep current version")
                print("  undo - Rollback to last checkpoint")
                print("  show - Show current prompt (first 500 chars)")
                print("  history - Show checkpoint history")
                print("  <any text> - Apply as feedback via TextGRAD")
                continue
            elif feedback.lower() == "show":
                print("\nCurrent prompt (first 500 chars):")
                print("-" * 40)
                print(current_content[:500] + "...")
                continue
            elif feedback.lower() == "undo":
                if last_checkpoint_id:
                    result = registry.rollback(last_checkpoint_id)
                    if result.success:
                        current_content = result.restored_content or current_content
                        sections = _content_to_sections(current_content)
                        print(f"\n[OK] Rolled back to {last_checkpoint_id[:8]}")
                        last_checkpoint_id = None
                    else:
                        print(f"\n[FAIL] Rollback failed: {result.message}")
                else:
                    print("\nNo checkpoint to undo.")
                continue
            elif feedback.lower() == "history":
                history = registry.history(limit=5)
                print("\nRecent checkpoints:")
                for h in history:
                    print(f"  [{h.id[:8]}] {h.reason}")
                continue

            # Apply feedback via TextGRAD
            print(f"\nApplying feedback: {feedback[:50]}...")

            result = improver.improve(sections, feedback)

            if result.content_changed:
                output = formatter.format_improvement_result(
                    original=result.original_content,
                    improved=result.improved_content,
                    sections_modified=result.sections_modified,
                    reasoning_trace=result.reasoning_trace,
                    checkpoint_id=result.checkpoint_id,
                )
                print(output)
                current_content = result.improved_content
                sections = _content_to_sections(current_content)
                last_checkpoint_id = result.checkpoint_id
                print("\nFeedback applied. Enter more feedback, 'done', or 'undo'.")
            else:
                print("\nNo changes made (identity). Try different feedback.")

        return current_content

    except ImportError as e:
        print(f"TextGRAD not available: {e}")
        return None
    except Exception as e:
        print(f"Error in interactive refine: {e}")
        return None


def _get_policy_vector(project_root: Path) -> "PolicyVector":
    """Get or create a PolicyVector for the project."""
    try:
        from .habits import HabitEncoder

        encoder = HabitEncoder(project_root=project_root)
        return encoder.encode()
    except Exception:
        from .habits.policy import PolicyVector

        return PolicyVector.default()


def _emit_compilation_metrics(
    prompt: "CompiledPrompt",
    context: "CompilationContext",
    compilation_time_ms: float,
    checkpoint_id: str | None,
) -> None:
    """Emit compilation metrics."""
    try:
        from .metrics import emit_compilation_metrics

        emit_compilation_metrics(
            prompt=prompt,
            context=context,
            compilation_time_ms=compilation_time_ms,
            checkpoint_id=checkpoint_id,
        )
    except Exception as e:
        print(f"Warning: Failed to emit metrics: {e}")


def compare_prompts(compiled_path: Path | None = None) -> None:
    """
    Compare compiled prompt to hand-written CLAUDE.md.

    Shows what's present in each and key differences.
    """
    project_root = Path(__file__).parent.parent.parent.parent.parent
    hand_written_path = project_root / "CLAUDE.md"

    if not hand_written_path.exists():
        print(f"Error: Hand-written CLAUDE.md not found at {hand_written_path}")
        sys.exit(1)

    hand_written = hand_written_path.read_text()

    if compiled_path and compiled_path.exists():
        compiled = compiled_path.read_text()
    else:
        compiled = compile_prompt()

    print("=" * 60)
    print("COMPARISON: Hand-written vs Compiled CLAUDE.md")
    print("=" * 60)

    # Key sections to check
    key_sections = [
        "kgents - Kent's Agents",
        "Project Philosophy",
        "AGENTESE",
        "Built Infrastructure",
        "Key Directories",
        "Skills Directory",
        "DevEx Commands",
        "Core Principles",
    ]

    print("\nSection presence:")
    print("-" * 40)
    print(f"{'Section':<25} {'Hand-written':<12} {'Compiled':<12}")
    print("-" * 40)

    for section in key_sections:
        hw_present = "YES" if section in hand_written else "NO"
        comp_present = "YES" if section in compiled else "NO"
        print(f"{section:<25} {hw_present:<12} {comp_present:<12}")

    print("\n" + "-" * 40)
    print(f"Hand-written length: {len(hand_written)} chars (~{len(hand_written) // 4} tokens)")
    print(f"Compiled length:     {len(compiled)} chars (~{len(compiled) // 4} tokens)")

    # Show first diff if any
    hw_lines = hand_written.split("\n")
    comp_lines = compiled.split("\n")

    print(f"\nHand-written lines: {len(hw_lines)}")
    print(f"Compiled lines:     {len(comp_lines)}")


def show_history(limit: int = 10) -> None:
    """
    Show checkpoint history.

    Args:
        limit: Maximum number of entries to show
    """
    registry = get_default_registry()
    history = registry.history(limit=limit)
    formatter = PromptOutputFormatter()

    if not history:
        print("No checkpoint history found.")
        print("  Storage: ~/.kgents/prompt-history/")
        return

    output = formatter.format_history_timeline(history)
    print(output)


def do_rollback(checkpoint_id: str) -> None:
    """
    Rollback to a specific checkpoint.

    Args:
        checkpoint_id: ID of checkpoint to restore (can be partial)
    """
    registry = get_default_registry()

    # Support partial IDs (at least 8 chars)
    if len(checkpoint_id) < 8:
        print(f"Error: Checkpoint ID must be at least 8 characters (got {len(checkpoint_id)})")
        sys.exit(1)

    # Find matching checkpoint
    history = registry.history(limit=100)
    matches = [h for h in history if h.id.startswith(checkpoint_id)]

    if not matches:
        print(f"Error: No checkpoint found matching '{checkpoint_id}'")
        print("\nRecent checkpoints:")
        for h in history[:5]:
            print(f"  {h}")
        sys.exit(1)

    if len(matches) > 1:
        print(f"Error: Multiple checkpoints match '{checkpoint_id}':")
        for h in matches:
            print(f"  {h}")
        print("\nPlease provide a more specific ID.")
        sys.exit(1)

    # Perform rollback
    full_id = matches[0].id
    print(f"Rolling back to checkpoint: {full_id}")
    print(f"  Original reason: {matches[0].reason}")

    result = registry.rollback(full_id)

    if result.success:
        print("\n✓ Rollback successful!")
        print(f"  New checkpoint: {result.checkpoint_id}")
        print(f"  Restored content: {len(result.restored_content or '')} chars")

        # Show reasoning trace
        if result.reasoning_trace:
            print("\nReasoning trace:")
            for trace in result.reasoning_trace[-5:]:  # Last 5 traces
                print(f"  - {trace}")
    else:
        print(f"\n✗ Rollback failed: {result.message}")
        sys.exit(1)


def show_diff(id1: str, id2: str) -> None:
    """
    Show diff between two checkpoints.

    Args:
        id1: First checkpoint ID
        id2: Second checkpoint ID
    """
    from .rollback.checkpoint import CheckpointId

    registry = get_default_registry()
    formatter = PromptOutputFormatter()

    diff = registry.diff(CheckpointId(id1), CheckpointId(id2))

    if diff is None:
        print("Error: Could not compute diff (checkpoint not found)")
        sys.exit(1)

    if not diff:
        print("No differences between checkpoints.")
    else:
        output = formatter.format_diff(diff)
        print(output)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Evergreen Prompt System CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compile subcommand
    compile_parser = subparsers.add_parser("compile", help="Compile CLAUDE.md from sections")
    compile_parser.add_argument("--output", "-o", type=Path, help="Output path for compiled prompt")
    compile_parser.add_argument(
        "--checkpoint/--no-checkpoint",
        dest="checkpoint",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Create checkpoint before compile (default: True)",
    )
    compile_parser.add_argument(
        "--reason", "-r", type=str, help="Reason for this compilation (for checkpoint)"
    )
    # Wave 6 flags
    compile_parser.add_argument(
        "--show-reasoning",
        action="store_true",
        help="Show reasoning traces for each section",
    )
    compile_parser.add_argument(
        "--show-habits",
        action="store_true",
        help="Show habit influence (PolicyVector) on compilation",
    )
    compile_parser.add_argument(
        "--feedback", type=str, help="Apply TextGRAD feedback to improve the prompt"
    )
    compile_parser.add_argument(
        "--auto-improve",
        action="store_true",
        help="Run habit encoder and propose improvements",
    )
    compile_parser.add_argument(
        "--preview", action="store_true", help="Preview changes without writing"
    )
    compile_parser.add_argument(
        "--emit-metrics",
        action="store_true",
        help="Emit metrics to metrics/evergreen/*.jsonl",
    )
    compile_parser.add_argument(
        "--refine", action="store_true", help="Start interactive refinement dialogue"
    )
    compile_parser.add_argument(
        "--export", type=Path, help="Export to path (no checkpoint, simpler output)"
    )
    compile_parser.add_argument(
        "--no-dynamic",
        action="store_true",
        help="Exclude dynamic sections (Forest, Context)",
    )

    # compare subcommand
    compare_parser = subparsers.add_parser(
        "compare", help="Compare compiled prompt to hand-written CLAUDE.md"
    )
    compare_parser.add_argument(
        "--compiled",
        "-c",
        type=Path,
        help="Path to compiled prompt (generates if not provided)",
    )

    # history subcommand
    history_parser = subparsers.add_parser("history", help="Show checkpoint history")
    history_parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=10,
        help="Maximum entries to show (default: 10)",
    )

    # rollback subcommand
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to a previous checkpoint")
    rollback_parser.add_argument(
        "checkpoint_id", type=str, help="Checkpoint ID to restore (at least 8 chars)"
    )

    # diff subcommand
    diff_parser = subparsers.add_parser("diff", help="Show diff between two checkpoints")
    diff_parser.add_argument("id1", type=str, help="First checkpoint ID")
    diff_parser.add_argument("id2", type=str, help="Second checkpoint ID")

    args = parser.parse_args()

    if args.command == "compile":
        compile_prompt(
            output_path=args.output,
            checkpoint=args.checkpoint,
            reason=args.reason,
            show_reasoning=args.show_reasoning,
            show_habits=args.show_habits,
            feedback=args.feedback,
            auto_improve=args.auto_improve,
            preview=args.preview,
            emit_metrics=args.emit_metrics,
            refine=args.refine,
            export_path=args.export,
            include_dynamic=not args.no_dynamic,
        )
        # Only print content if no special flags and no output path
        if (
            not args.output
            and not args.show_reasoning
            and not args.show_habits
            and not args.feedback
            and not args.auto_improve
            and not args.preview
            and not args.refine
            and not args.export
        ):
            pass  # Content already printed
    elif args.command == "compare":
        compare_prompts(args.compiled)
    elif args.command == "history":
        show_history(limit=args.limit)
    elif args.command == "rollback":
        do_rollback(args.checkpoint_id)
    elif args.command == "diff":
        show_diff(args.id1, args.id2)


if __name__ == "__main__":
    main()
