"""
Docs Handler: Living Documentation Generator

PATTERN: Thin routing shim that delegates to AGENTESE paths.
         Custom handlers parse CLI args and format output nicely.

A thin routing shim to concept.docs.* AGENTESE paths.
All business logic lives in services/living_docs/.

AGENTESE Path Mapping:
    kg docs                 -> concept.docs.manifest
    kg docs generate        -> concept.docs.generate
    kg docs teaching        -> concept.docs.teaching
    kg docs verify          -> concept.docs.verify
    kg docs lint            -> concept.docs.lint

Usage:
    kg docs generate --output docs/reference/
    kg docs generate --overwrite
    kg docs teaching --severity critical
    kg docs verify
    kg docs lint --strict

See: spec/protocols/living-docs.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_docs(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Living Docs: Generate and query documentation from source.

    All business logic is in services/living_docs/. This handler only routes.
    """
    # Parse help flag
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Route to appropriate handler
    if subcommand == "generate":
        return _handle_generate(args)
    elif subcommand == "teaching":
        return _handle_teaching(args)
    elif subcommand == "verify":
        return _handle_verify(args)
    elif subcommand == "lint":
        return _handle_lint(args)
    elif subcommand == "hydrate":
        return _handle_hydrate(args)
    elif subcommand == "relevant":
        return _handle_relevant(args)
    elif subcommand == "crystallize":
        return _handle_crystallize(args)
    else:
        return _handle_manifest(args)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "manifest"


def _parse_output_dir(args: list[str]) -> Path:
    """Extract --output directory from args."""
    for i, arg in enumerate(args):
        if arg == "--output" and i + 1 < len(args):
            return Path(args[i + 1])
        elif arg.startswith("--output="):
            return Path(arg.split("=", 1)[1])
    return Path("docs/reference")


def _handle_manifest(args: list[str]) -> int:
    """Show living docs manifest (status/overview)."""
    try:
        from services.living_docs import get_teaching_stats

        stats = get_teaching_stats()

        if "--json" in args:
            print(
                json.dumps(
                    {
                        "total_teaching_moments": stats.total,
                        "by_severity": stats.by_severity,
                        "with_evidence": stats.with_evidence,
                        "without_evidence": stats.without_evidence,
                        "verified_evidence": stats.verified_evidence,
                    }
                )
            )
        else:
            print("Living Docs Status")
            print("=" * 40)
            print(f"Teaching Moments: {stats.total}")
            print(f"  Critical: {stats.by_severity.get('critical', 0)}")
            print(f"  Warning:  {stats.by_severity.get('warning', 0)}")
            print(f"  Info:     {stats.by_severity.get('info', 0)}")
            print()
            print(f"With Evidence:    {stats.with_evidence}")
            print(f"Without Evidence: {stats.without_evidence}")
            print(f"Verified:         {stats.verified_evidence}")
            print()
            print("Commands:")
            print("  kg docs generate  Generate reference docs")
            print("  kg docs teaching  Query teaching moments")
            print("  kg docs verify    Verify evidence links")

        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_generate(args: list[str]) -> int:
    """Generate reference documentation."""
    try:
        from services.living_docs import generate_to_directory

        output_dir = _parse_output_dir(args)
        overwrite = "--overwrite" in args

        print(f"Generating docs to {output_dir}...")

        manifest = generate_to_directory(output_dir, overwrite=overwrite)

        if "--json" in args:
            print(json.dumps(manifest.to_dict(), default=str))
        else:
            print()
            print(f"Generated {manifest.file_count} files:")
            for f in manifest.files:
                print(f"  {f.path.name}: {f.symbol_count} symbols, {f.teaching_count} teaching")
            print()
            print(
                f"Total: {manifest.total_symbols} symbols, {manifest.total_teaching} teaching moments"
            )
            print(f"Output: {output_dir}")

        return 0
    except Exception as e:
        print(f"Error generating docs: {e}")
        return 1


def _handle_teaching(args: list[str]) -> int:
    """Query teaching moments."""
    try:
        from services.living_docs import query_teaching

        # Parse filters
        severity = None
        module_pattern = None

        for i, arg in enumerate(args):
            if arg == "--severity" and i + 1 < len(args):
                severity = args[i + 1]
            elif arg.startswith("--severity="):
                severity = arg.split("=", 1)[1]
            elif arg == "--module" and i + 1 < len(args):
                module_pattern = args[i + 1]
            elif arg.startswith("--module="):
                module_pattern = arg.split("=", 1)[1]

        results = query_teaching(
            severity=severity,  # type: ignore[arg-type]
            module_pattern=module_pattern,
        )

        if "--json" in args:
            print(
                json.dumps(
                    [
                        {
                            "insight": r.moment.insight,
                            "severity": r.moment.severity,
                            "symbol": r.symbol,
                            "module": r.module,
                            "evidence": r.moment.evidence,
                        }
                        for r in results
                    ]
                )
            )
        else:
            if not results:
                print("No teaching moments found matching filters.")
                return 0

            # Group by severity
            from services.living_docs import TeachingResult

            by_severity: dict[str, list[TeachingResult]] = {
                "critical": [],
                "warning": [],
                "info": [],
            }
            for r in results:
                by_severity[r.moment.severity].append(r)

            icons = {"critical": "\U0001f6a8", "warning": "\u26a0\ufe0f", "info": "\u2139\ufe0f"}

            for sev in ["critical", "warning", "info"]:
                items = by_severity[sev]
                if items:
                    print(f"\n{icons[sev]} {sev.upper()} ({len(items)})")
                    print("-" * 40)
                    for item in items[:10]:  # Limit output
                        print(f"{item.symbol}: {item.moment.insight[:60]}...")
                        if item.moment.evidence:
                            print(f"  Evidence: {item.moment.evidence}")
                    if len(items) > 10:
                        print(f"  ...and {len(items) - 10} more")

            print(f"\nTotal: {len(results)} teaching moments")

        return 0
    except Exception as e:
        print(f"Error querying teaching: {e}")
        return 1


def _handle_verify(args: list[str]) -> int:
    """Verify evidence links exist."""
    try:
        from services.living_docs import verify_evidence

        results = verify_evidence()
        missing = [r for r in results if not r.evidence_exists]
        verified = [r for r in results if r.evidence_exists]

        if "--json" in args:
            print(
                json.dumps(
                    {
                        "total": len(results),
                        "verified": len(verified),
                        "missing": len(missing),
                        "missing_details": [
                            {
                                "symbol": r.result.symbol,
                                "evidence": r.result.moment.evidence,
                                "insight": r.result.moment.insight,
                            }
                            for r in missing
                        ],
                    }
                )
            )
        else:
            print("Evidence Verification")
            print("=" * 40)
            print(f"Total with evidence: {len(results)}")
            print(f"Verified:            {len(verified)}")
            print(f"Missing:             {len(missing)}")

            if missing:
                print()
                print("\u26a0\ufe0f Missing Evidence Links:")
                for r in missing[:10]:
                    print(f"  {r.result.symbol}: {r.result.moment.evidence}")
                if len(missing) > 10:
                    print(f"  ...and {len(missing) - 10} more")

            # Return 1 if strict mode and missing links
            if "--strict" in args and missing:
                return 1

        return 0
    except Exception as e:
        print(f"Error verifying evidence: {e}")
        return 1


def _handle_lint(args: list[str]) -> int:
    """Lint documentation for missing docstrings."""
    try:
        from pathlib import Path

        from services.living_docs import get_changed_files, lint_directory

        # Determine path to lint
        lint_path = Path(".")
        for i, arg in enumerate(args):
            if arg == "lint":
                continue
            if arg.startswith("-"):
                continue
            # Remaining non-flag arg is the path
            lint_path = Path(arg)
            break

        # Parse flags
        strict = "--strict" in args
        changed_only = "--changed" in args

        # Get changed files if needed
        changed_files = None
        if changed_only:
            repo_root = Path(".").resolve()
            # Walk up to find .git
            while repo_root != repo_root.parent:
                if (repo_root / ".git").exists():
                    break
                repo_root = repo_root.parent
            changed_files = get_changed_files(repo_root)
            if not changed_files:
                print("No changed Python files found.")
                return 0

        # Run linter
        stats = lint_directory(lint_path, changed_only=changed_only, changed_files=changed_files)

        if "--json" in args:
            print(json.dumps(stats.to_dict(), indent=2))
        else:
            print("Documentation Lint")
            print("=" * 40)
            print(f"Files checked:   {stats.files_checked}")
            print(f"Symbols checked: {stats.symbols_checked}")
            print(f"Errors:          {stats.errors}")
            print(f"Warnings:        {stats.warnings}")

            if stats.results:
                print()

                # Group by severity
                errors = [r for r in stats.results if r.severity == "error"]
                warnings = [r for r in stats.results if r.severity == "warning"]

                if errors:
                    print("\U0001f6a8 ERRORS:")
                    for r in errors[:20]:
                        print(f"  {r.module}:{r.line} - {r.symbol}: {r.message}")
                    if len(errors) > 20:
                        print(f"  ... and {len(errors) - 20} more errors")

                if warnings:
                    print("\n\u26a0\ufe0f WARNINGS:")
                    for r in warnings[:10]:
                        print(f"  {r.module}:{r.line} - {r.symbol}: {r.message}")
                    if len(warnings) > 10:
                        print(f"  ... and {len(warnings) - 10} more warnings")

            if stats.errors == 0 and stats.warnings == 0:
                print()
                print("\u2705 All documentation checks passed!")

        # Return 1 if strict mode and any errors
        if strict and stats.errors > 0:
            return 1

        return 0
    except Exception as e:
        print(f"Error linting documentation: {e}")
        return 1


def _handle_hydrate(args: list[str]) -> int:
    """Generate hydration context for a task.

    Enhanced with unified hydration (AD-017 Living Docs):
    - Default: ghost hydration (includes ancestral wisdom from deleted code)
    - Use --from-brain: unified path querying Brain directly (PREFERRED)
    - Use --no-ghosts: skip ghost hydration (faster, no async)
    """
    try:
        import asyncio

        from services.living_docs import (
            hydrate_context,
            hydrate_context_with_ghosts,
            hydrate_from_brain,
        )

        # Extract task from args (everything after "hydrate" that's not a flag)
        task_parts = []
        skip_next = False
        from_brain = "--from-brain" in args
        no_ghosts = "--no-ghosts" in args
        for i, arg in enumerate(args):
            if skip_next:
                skip_next = False
                continue
            if arg == "hydrate":
                continue
            if arg.startswith("-"):
                if arg in ("--output", "--severity", "--module"):
                    skip_next = True
                continue
            task_parts.append(arg)

        if not task_parts:
            print("Usage: kg docs hydrate <task description>")
            print("")
            print("Examples:")
            print('  kg docs hydrate "implement wasm projector"')
            print('  kg docs hydrate "fix brain persistence"')
            print('  kg docs hydrate "town dialogue" --from-brain')
            print('  kg docs hydrate "quick check" --no-ghosts')
            return 1

        task = " ".join(task_parts)

        # Choose hydration path
        if from_brain:
            # AD-017 unified path: query Brain directly
            try:
                context = asyncio.run(hydrate_from_brain(task))
            except Exception:
                # Graceful degradation: fall back to ghost hydration
                context = asyncio.run(hydrate_context_with_ghosts(task))
        elif no_ghosts:
            # Fast sync path: no async, no ghosts
            context = hydrate_context(task)
        else:
            # Default: ghost hydration (Memory-First Docs Phase 4)
            try:
                context = asyncio.run(hydrate_context_with_ghosts(task))
            except Exception:
                # Graceful degradation: fall back to sync hydration
                context = hydrate_context(task)

        if "--json" in args:
            print(json.dumps(context.to_dict(), indent=2))
        else:
            print(context.to_markdown())

        return 0
    except Exception as e:
        print(f"Error generating hydration context: {e}")
        return 1


def _handle_relevant(args: list[str]) -> int:
    """Show relevant context for a specific file."""
    try:
        from services.living_docs import relevant_for_file

        # Extract file path from args
        file_path = None
        for i, arg in enumerate(args):
            if arg == "relevant":
                continue
            if arg.startswith("-"):
                continue
            file_path = arg
            break

        if not file_path:
            print("Usage: kg docs relevant <file_path>")
            print("")
            print("Examples:")
            print("  kg docs relevant services/brain/persistence.py")
            print("  kg docs relevant protocols/agentese/logos.py")
            return 1

        context = relevant_for_file(file_path)

        if "--json" in args:
            print(json.dumps(context.to_dict(), indent=2))
        else:
            # Compact output for pre-edit context
            if context.relevant_teaching:
                print("Relevant Gotchas:")
                print("-" * 40)
                for t in context.relevant_teaching:
                    icon = {
                        "critical": "\U0001f6a8",
                        "warning": "\u26a0\ufe0f",
                        "info": "\u2139\ufe0f",
                    }.get(t.moment.severity, "\u2022")
                    print(f"{icon} {t.symbol}: {t.moment.insight[:60]}...")
                    if t.moment.evidence:
                        print(f"   Evidence: {t.moment.evidence}")
                print()

            if context.related_modules:
                print("Related Modules:")
                for module in context.related_modules[:5]:
                    print(f"  - {module}")
                print()

            if not context.relevant_teaching and not context.related_modules:
                print(f"No specific gotchas found for: {file_path}")
                print("(This might be a simple module or new code)")

        return 0
    except Exception as e:
        print(f"Error finding relevant context: {e}")
        return 1


def _handle_crystallize(args: list[str]) -> int:
    """Crystallize teaching moments to Brain persistence.

    This implements the Memory-First Documentation protocol:
    Teaching moments extracted from code are persisted to Brain,
    where they can survive code deletion.
    """
    try:
        from services.living_docs.crystallizer import crystallize_all_teaching_sync

        # Parse filters
        module_pattern = None
        severity = None

        for i, arg in enumerate(args):
            if arg == "--module" and i + 1 < len(args):
                module_pattern = args[i + 1]
            elif arg.startswith("--module="):
                module_pattern = arg.split("=", 1)[1]
            elif arg == "--severity" and i + 1 < len(args):
                severity = args[i + 1]
            elif arg.startswith("--severity="):
                severity = arg.split("=", 1)[1]

        # Check for dry run
        dry_run = "--dry-run" in args

        if dry_run:
            # Just count, don't persist
            from services.living_docs import query_teaching

            results = query_teaching(
                severity=severity,  # type: ignore[arg-type]
                module_pattern=module_pattern,
            )

            if "--json" in args:
                print(
                    json.dumps(
                        {
                            "mode": "dry_run",
                            "would_crystallize": len(results),
                            "by_severity": {
                                "critical": len(
                                    [r for r in results if r.moment.severity == "critical"]
                                ),
                                "warning": len(
                                    [r for r in results if r.moment.severity == "warning"]
                                ),
                                "info": len([r for r in results if r.moment.severity == "info"]),
                            },
                        }
                    )
                )
            else:
                print("Crystallization Dry Run")
                print("=" * 40)
                print(f"Would crystallize: {len(results)} teaching moments")
                print(f"  Critical: {len([r for r in results if r.moment.severity == 'critical'])}")
                print(f"  Warning:  {len([r for r in results if r.moment.severity == 'warning'])}")
                print(f"  Info:     {len([r for r in results if r.moment.severity == 'info'])}")
                print()
                print("Run without --dry-run to persist to Brain.")

            return 0

        # Actual crystallization
        print("Crystallizing teaching moments to Brain...")

        stats = crystallize_all_teaching_sync(
            module_pattern=module_pattern,
            severity=severity,
        )

        if "--json" in args:
            print(json.dumps(stats.to_dict(), indent=2))
        else:
            print()
            print("Crystallization Complete")
            print("=" * 40)
            print(f"Total found:        {stats.total_found}")
            print(f"Newly crystallized: {stats.newly_crystallized}")
            print(f"Already existed:    {stats.already_existed}")
            print(f"With evidence:      {stats.with_evidence}")
            print()
            print("By Severity:")
            print(f"  Critical: {stats.by_severity.get('critical', 0)}")
            print(f"  Warning:  {stats.by_severity.get('warning', 0)}")
            print(f"  Info:     {stats.by_severity.get('info', 0)}")

            if stats.errors:
                print()
                print(f"\u26a0\ufe0f Errors ({len(stats.errors)}):")
                for error in stats.errors[:5]:
                    print(f"  - {error}")
                if len(stats.errors) > 5:
                    print(f"  ... and {len(stats.errors) - 5} more")

        return 0
    except Exception as e:
        print(f"Error crystallizing teaching: {e}")
        return 1


def _print_help() -> None:
    """Print docs command help."""
    help_text = """
kg docs - Living Documentation Generator

Commands:
  kg docs                         Show documentation status
  kg docs generate                Generate reference documentation
  kg docs teaching                Query teaching moments (gotchas)
  kg docs verify                  Verify evidence links exist
  kg docs lint                    Lint for missing docstrings (CI enforcement)
  kg docs hydrate <task>          Generate context for a task (Claude-friendly)
  kg docs relevant <file>         Show gotchas relevant to a file
  kg docs crystallize             Persist teaching moments to Brain (Memory-First)

Options:
  --output <dir>                  Output directory (default: docs/reference/)
  --overwrite                     Overwrite existing files
  --severity <level>              Filter by severity (critical, warning, info)
  --module <pattern>              Filter by module pattern
  --strict                        Exit 1 if verify/lint finds issues
  --changed                       Lint only git-changed files
  --dry-run                       Preview crystallization without persisting
  --from-brain                    Unified hydration: query Brain directly (AD-017)
  --no-ghosts                     Skip ancestral wisdom in hydrate (faster)
  --json                          Output as JSON
  --help, -h                      Show this help message

Examples:
  kg docs generate --output docs/reference/ --overwrite
  kg docs teaching --severity critical
  kg docs teaching --module services.brain
  kg docs verify --strict
  kg docs lint --strict
  kg docs lint --changed
  kg docs lint path/to/file.py
  kg docs hydrate "implement wasm projector"
  kg docs relevant services/brain/persistence.py
  kg docs crystallize --dry-run
  kg docs crystallize --severity critical

AGENTESE Paths:
  concept.docs.manifest           Documentation status
  concept.docs.generate           Generate reference docs
  concept.docs.teaching           Query teaching moments
  concept.docs.lint               Lint documentation
  concept.docs.hydrate            Task-focused context
  self.memory.crystallize_teaching  Persist teaching to Brain
"""
    print(help_text.strip())


__all__ = ["cmd_docs"]
