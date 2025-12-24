"""
kg audit - Spec validation against principles and implementation.

Audit commands:
  kg audit <spec> --principles     Score against 7 principles
  kg audit <spec> --impl           Detect spec/impl drift
  kg audit <spec> --full           Both + action items
  kg audit --system                Audit all Crown Jewels

Every audit emits a witness mark for traceability.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 1)
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext
    from services.audit import AuditResult

# Lazy imports to keep CLI startup fast
_INITIALIZED = False


def _ensure_imports() -> None:
    """Lazy import heavy dependencies."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    # These imports are deferred until command is actually invoked
    global AuditResult, score_principles, detect_drift
    from services.audit import AuditResult, detect_drift, score_principles

    _INITIALIZED = True


# =============================================================================
# Rich Console Helpers
# =============================================================================


def _get_console() -> Any:
    """Get Rich console for pretty output."""
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


def _print_principle_scores(scores: Any, console: Any = None) -> None:
    """Print principle scores in a formatted table."""
    if console:
        from rich.table import Table

        table = Table(title="Principle Scores", show_header=True)
        table.add_column("Principle", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Status")

        principles = [
            ("Tasteful", scores.tasteful),
            ("Curated", scores.curated),
            ("Ethical", scores.ethical),
            ("Joy-Inducing", scores.joy_inducing),
            ("Composable", scores.composable),
            ("Heterarchical", scores.heterarchical),
            ("Generative", scores.generative),
        ]

        for name, score in principles:
            # Color code based on score
            if score >= 0.7:
                status = "[green]✓ Strong[/green]"
            elif score >= 0.4:
                status = "[yellow]⚠ Partial[/yellow]"
            else:
                status = "[red]✗ Weak[/red]"

            table.add_row(name, f"{score:.2f}", status)

        # Add summary row
        mean_score = scores.mean()
        passing = scores.passing_count()
        table.add_row("", "", "")  # Separator
        table.add_row(
            "[bold]Overall[/bold]",
            f"[bold]{mean_score:.2f}[/bold]",
            f"[bold]{passing}/7 passing[/bold]",
        )

        console.print()
        console.print(table)
        console.print()

        # Gates check
        if scores.passes_gates():
            console.print("[green]✓ Passes validation gates (all >= 0.4, 5+ >= 0.7)[/green]")
        else:
            console.print(
                "[red]✗ Fails validation gates (need all >= 0.4, 5+ >= 0.7)[/red]"
            )
        console.print()
    else:
        # Plain text output
        print("\n=== Principle Scores ===")
        print(f"  Tasteful:      {scores.tasteful:.2f}")
        print(f"  Curated:       {scores.curated:.2f}")
        print(f"  Ethical:       {scores.ethical:.2f}")
        print(f"  Joy-Inducing:  {scores.joy_inducing:.2f}")
        print(f"  Composable:    {scores.composable:.2f}")
        print(f"  Heterarchical: {scores.heterarchical:.2f}")
        print(f"  Generative:    {scores.generative:.2f}")
        print(f"\n  Overall:       {scores.mean():.2f} ({scores.passing_count()}/7 passing)")
        print()


def _print_drift_items(drift_items: list[Any], console: Any = None) -> None:
    """Print drift items in a formatted table."""
    if not drift_items:
        if console:
            console.print("[green]✓ No drift detected - spec and impl aligned[/green]\n")
        else:
            print("✓ No drift detected - spec and impl aligned\n")
        return

    if console:
        from rich.table import Table

        table = Table(title="Drift Items", show_header=True)
        table.add_column("Component", style="cyan")
        table.add_column("Spec Says")
        table.add_column("Impl Does")
        table.add_column("Severity")

        for item in drift_items:
            # Color code severity
            sev = item.severity.value
            if sev == "critical":
                sev_str = "[red bold]CRITICAL[/red bold]"
            elif sev == "error":
                sev_str = "[red]ERROR[/red]"
            elif sev == "warning":
                sev_str = "[yellow]WARNING[/yellow]"
            else:
                sev_str = "[dim]INFO[/dim]"

            table.add_row(item.component, item.spec_says[:40], item.impl_does[:40], sev_str)

        console.print()
        console.print(table)
        console.print()

        # Summary
        errors = sum(1 for d in drift_items if d.severity.value in ("error", "critical"))
        if errors > 0:
            console.print(f"[red]✗ {errors} errors found[/red]")
        else:
            console.print(f"[yellow]⚠ {len(drift_items)} warnings found[/yellow]")
        console.print()
    else:
        # Plain text output
        print("\n=== Drift Items ===")
        for item in drift_items:
            print(f"  [{item.severity.value.upper()}] {item.component}")
            print(f"    Spec: {item.spec_says}")
            print(f"    Impl: {item.impl_does}")
        print()


def _print_action_items(action_items: list[str], console: Any = None) -> None:
    """Print action items."""
    if not action_items:
        return

    if console:
        console.print("[bold]Action Items:[/bold]")
        for i, item in enumerate(action_items, 1):
            console.print(f"  {i}. {item}")
        console.print()
    else:
        print("\n=== Action Items ===")
        for i, item in enumerate(action_items, 1):
            print(f"  {i}. {item}")
        print()


# =============================================================================
# Audit Operations
# =============================================================================


async def _audit_principles_async(spec_path: Path) -> Any:
    """Run principle audit."""
    _ensure_imports()
    from services.audit.principles import score_principles_async
    scores = await score_principles_async(spec_path)
    return scores


async def _audit_drift_async(spec_path: Path, impl_path: Path | None = None) -> list[Any]:
    """Run drift audit."""
    _ensure_imports()
    from services.audit.drift import detect_drift_async
    drift_items = await detect_drift_async(spec_path, impl_path)
    return drift_items


async def _audit_full_async(
    spec_path: Path,
    impl_path: Path | None = None,
) -> Any:
    """Run full audit (principles + drift + action items)."""
    _ensure_imports()
    from services.audit.principles import score_principles_async
    from services.audit.drift import detect_drift_async

    # Run both audits
    scores, drift_items = await asyncio.gather(
        score_principles_async(spec_path),
        detect_drift_async(spec_path, impl_path),
    )

    # Build audit result
    result = AuditResult(
        spec_path=spec_path,
        principle_scores=scores,
        drift_items=drift_items,
        impl_path=impl_path,
    )

    # Generate action items
    result.action_items = _generate_action_items(result)

    return result


def _generate_action_items(result: Any) -> list[str]:
    """Generate recommended action items from audit result."""
    items = []

    # Principle failures (< 0.4) and warnings (< 0.7)
    if result.principle_scores:
        scores = result.principle_scores

        # Critical failures (< 0.4)
        if scores.tasteful < 0.4:
            items.append(
                "CRITICAL: Add clear purpose statement and justification for existence"
            )
        elif scores.tasteful < 0.7:
            items.append(
                "Strengthen purpose statement - explain 'why this exists' more clearly"
            )

        if scores.curated < 0.4:
            items.append("CRITICAL: Add intentional selection rationale and heritage citations")
        elif scores.curated < 0.7:
            items.append(
                "Improve curation - add heritage citations and evolution strategy"
            )

        if scores.ethical < 0.4:
            items.append("CRITICAL: Add transparency, privacy, and human agency considerations")
        elif scores.ethical < 0.7:
            items.append(
                "Strengthen ethical considerations - add privacy/data section or limitations"
            )

        if scores.joy_inducing < 0.4:
            items.append("CRITICAL: Add warmth, examples, and engaging language")
        elif scores.joy_inducing < 0.7:
            items.append(
                "Make more engaging - add conversational tone, emoji, or storytelling examples"
            )

        if scores.composable < 0.4:
            items.append(
                "CRITICAL: Document category laws (identity, associativity) and ensure single outputs"
            )
        elif scores.composable < 0.7:
            items.append(
                "Improve composability - add type signatures and composition operators"
            )

        if scores.heterarchical < 0.4:
            items.append("CRITICAL: Describe dual loop (autonomous + functional) patterns")
        elif scores.heterarchical < 0.7:
            items.append(
                "Strengthen heterarchy - mention flux/dynamics and avoid fixed hierarchy language"
            )

        if scores.generative < 0.4:
            items.append("CRITICAL: Show how implementation can be derived from spec (compression)")
        elif scores.generative < 0.7:
            items.append(
                "Improve generativity - add grammar/rules section or mention derivation"
            )

    # Drift errors
    if result.drift_errors:
        items.append(f"Fix {len(result.drift_errors)} critical spec/impl drift errors")

    return items


async def _emit_audit_mark_async(result: Any) -> str:
    """Emit a witness mark for the audit."""
    from protocols.cli.handlers.witness_thin import _create_mark_async

    action = f"Audited {result.spec_path.name}"
    reasoning = result.summary()
    tags = ["audit"]

    # Add principle tags
    if result.principle_scores:
        passing = result.principle_scores.passing_count()
        if passing >= 5:
            tags.append("principles-pass")
        else:
            tags.append("principles-fail")

    # Add drift tags
    if result.has_drift:
        tags.append("drift-detected")

    mark_data = await _create_mark_async(
        action=action,
        reasoning=reasoning,
        tags=tags,
    )

    return str(mark_data["mark_id"])


# =============================================================================
# Bootstrap Helper
# =============================================================================


async def _bootstrap_and_run_audit(coro_func: Any, *args: Any, **kwargs: Any) -> Any:
    """Bootstrap services and run audit coroutine."""
    from protocols.agentese.container import reset_container
    from services.bootstrap import bootstrap_services, reset_registry

    reset_registry()
    reset_container()
    await bootstrap_services()

    return await coro_func(*args, **kwargs)


def _run_audit_async(coro_func: Any) -> Any:
    """Create sync wrapper for audit coroutines."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(_bootstrap_and_run_audit(coro_func, *args, **kwargs))

    return wrapper


# =============================================================================
# Command Handlers
# =============================================================================


def cmd_audit(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Audit a spec against principles and/or implementation.

    Usage:
        kg audit <spec> --principles        Score against 7 principles
        kg audit <spec> --impl              Detect spec/impl drift
        kg audit <spec> --full              Both + action items (default)
        kg audit --system                   Audit all Crown Jewels
        kg audit <spec> --json              Machine-readable output

    Examples:
        kg audit spec/protocols/witness.md --principles
        kg audit spec/agents/brain/brain.md --impl
        kg audit spec/agents/brain/brain.md --full
        kg audit --system
    """
    _ensure_imports()

    if not args or "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse flags
    do_principles = "--principles" in args
    do_impl = "--impl" in args
    do_full = "--full" in args
    do_system = "--system" in args
    json_output = "--json" in args

    # Default to full if no specific audit type
    if not (do_principles or do_impl or do_full or do_system):
        do_full = True

    # System audit
    if do_system:
        return cmd_audit_system(args, ctx)

    # Find spec path
    spec_arg = None
    for arg in args:
        if not arg.startswith("-") and arg != "audit":
            spec_arg = arg
            break

    if not spec_arg:
        print("Error: Spec path required")
        print('Usage: kg audit <spec> [--principles] [--impl] [--full]')
        return 1

    spec_path = Path(spec_arg)
    if not spec_path.exists():
        print(f"Error: Spec file not found: {spec_path}")
        return 1

    console = _get_console()

    try:
        # Run appropriate audit
        if do_principles:
            # Principles only
            scores = _run_audit_async(_audit_principles_async)(spec_path)

            if json_output:
                print(json.dumps(scores.to_dict()))
            else:
                _print_principle_scores(scores, console)

        elif do_impl:
            # Drift only
            drift_items = _run_audit_async(_audit_drift_async)(spec_path, None)

            if json_output:
                print(json.dumps([d.to_dict() for d in drift_items]))
            else:
                _print_drift_items(drift_items, console)

        else:
            # Full audit
            result = _run_audit_async(_audit_full_async)(spec_path, None)

            # Emit witness mark
            mark_id = _run_audit_async(_emit_audit_mark_async)(result)
            result.mark_id = mark_id

            if json_output:
                print(json.dumps(result.to_dict()))
            else:
                if console:
                    console.print(
                        f"\n[bold]Audit Results: {spec_path.name}[/bold]", highlight=False
                    )
                    console.print(f"[dim]Mark ID: {mark_id[:12]}...[/dim]\n")
                else:
                    print(f"\n=== Audit Results: {spec_path.name} ===")
                    print(f"Mark ID: {mark_id[:12]}...\n")

                # Print sections
                if result.principle_scores:
                    _print_principle_scores(result.principle_scores, console)

                if result.drift_items is not None:
                    _print_drift_items(result.drift_items, console)

                if result.action_items:
                    _print_action_items(result.action_items, console)

                # Overall pass/fail
                if console:
                    if result.passes_principles and not result.drift_errors:
                        console.print("[green bold]✓ PASS[/green bold]")
                    else:
                        console.print("[red bold]✗ NEEDS WORK[/red bold]")
                    console.print()
                else:
                    if result.passes_principles and not result.drift_errors:
                        print("✓ PASS\n")
                    else:
                        print("✗ NEEDS WORK\n")

        return 0

    except KeyboardInterrupt:
        if not json_output:
            print("\n\nAudit interrupted by user.", file=sys.stderr)
        return 130  # Standard exit code for SIGINT

    except FileNotFoundError as e:
        if json_output:
            print(json.dumps({"error": "file_not_found", "message": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        if json_output:
            print(json.dumps({"error": "validation_error", "message": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    except PermissionError as e:
        if json_output:
            print(json.dumps({"error": "permission_denied", "message": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        if json_output:
            print(json.dumps({"error": "unexpected_error", "message": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
            import traceback

            traceback.print_exc()
        return 1


def cmd_audit_system(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Audit all Crown Jewels for health.

    Usage:
        kg audit --system              Audit all jewels
        kg audit --system --json       JSON output
    """
    _ensure_imports()

    json_output = "--json" in args
    console = _get_console()

    # Crown Jewels to audit
    jewels = [
        ("Brain", Path("spec/agents/brain/brain.md")),
        ("Witness", Path("spec/protocols/witness.md")),
        ("Town", Path("spec/agents/town/town.md")),
        ("Atelier", Path("spec/agents/atelier/atelier.md")),
    ]

    results = []
    errors = []

    try:
        for name, spec_path in jewels:
            if not spec_path.exists():
                if not json_output:
                    print(f"⚠ Skipping {name}: spec not found at {spec_path}")
                continue

            try:
                result = _run_audit_async(_audit_full_async)(spec_path, None)
                results.append((name, result))
            except KeyboardInterrupt:
                raise  # Propagate to outer handler
            except Exception as e:
                error_msg = f"{name}: {str(e)}"
                errors.append(error_msg)
                if not json_output:
                    print(f"✗ {error_msg}", file=sys.stderr)

        if json_output:
            output = {
                "results": {jewel: result.to_dict() for jewel, result in results},
                "errors": errors if errors else None,
            }
            print(json.dumps(output))
        else:
            # Dashboard view
            if console:
                from rich.table import Table

                table = Table(title="System Health Dashboard", show_header=True)
                table.add_column("Crown Jewel", style="cyan")
                table.add_column("Principles", justify="right")
                table.add_column("Drift", justify="right")
                table.add_column("Status")

                for name, result in results:
                    # Principles score
                    if result.principle_scores:
                        mean_score = result.principle_scores.mean()
                        principles_str = f"{mean_score:.2f}"
                    else:
                        principles_str = "N/A"

                    # Drift count
                    if result.drift_items is not None:
                        drift_errors = len(result.drift_errors)
                        drift_str = f"{drift_errors} errors" if drift_errors > 0 else "✓"
                    else:
                        drift_str = "N/A"

                    # Status
                    if result.passes_principles and not result.drift_errors:
                        status = "[green]✓ Healthy[/green]"
                    elif result.passes_principles or not result.drift_errors:
                        status = "[yellow]⚠ Warning[/yellow]"
                    else:
                        status = "[red]✗ Critical[/red]"

                    table.add_row(name, principles_str, drift_str, status)

                console.print()
                console.print(table)
                console.print()
            else:
                print("\n=== System Health Dashboard ===")
                for name, result in results:
                    mean_score = (
                        result.principle_scores.mean() if result.principle_scores else 0.0
                    )
                    drift_errors = len(result.drift_errors) if result.drift_items else 0
                    print(
                        f"  {name:<12} Principles: {mean_score:.2f}  Drift: {drift_errors} errors"
                    )
                print()

        return 0 if not errors else 1

    except KeyboardInterrupt:
        if not json_output:
            print("\n\nSystem audit interrupted by user.", file=sys.stderr)
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        if json_output:
            print(json.dumps({"error": "unexpected_error", "message": str(e)}))
        else:
            print(f"Error during system audit: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
        return 1


def _print_help() -> None:
    """Print audit command help."""
    help_text = """
kg audit - Validate specs against principles and implementation

USAGE:
  kg audit <spec> [options]        Audit a specific spec
  kg audit --system                Audit all Crown Jewels

OPTIONS:
  --principles                     Score against 7 constitutional principles only
  --impl                           Detect spec/impl drift only
  --full                           Full audit: principles + drift + actions (default)
  --json                           Machine-readable JSON output

EXAMPLES:
  kg audit spec/protocols/witness.md --principles
  kg audit spec/agents/brain/brain.md --impl
  kg audit spec/agents/brain/brain.md --full
  kg audit --system

PRINCIPLE SCORING:
  Scores each spec against 7 principles (0.0-1.0):
    - Tasteful: Clear purpose, justified existence
    - Curated: Intentional selection, not exhaustive
    - Ethical: Transparent, privacy-respecting, human agency
    - Joy-Inducing: Delightful, warm, engaging
    - Composable: Category laws, single outputs
    - Heterarchical: Dual loop, flux topology
    - Generative: Spec is compression, implementation derivable

  Gates: All >= 0.4, at least 5 >= 0.7 to pass

DRIFT DETECTION:
  Compares spec against implementation to find:
    - Missing implementations (spec says, impl doesn't)
    - Extra implementations (impl has, spec doesn't mention)
    - Mismatched components (spec vs impl differ)

OUTPUT:
  - Human-friendly table view (default)
  - JSON for programmatic use (--json)
  - Every audit emits a witness mark for traceability

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md
See: spec/principles.md
"""
    print(help_text.strip())


__all__ = ["cmd_audit"]
