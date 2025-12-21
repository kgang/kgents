"""
Docs Handler: Living Documentation Generator

A thin routing shim to concept.docs.* AGENTESE paths.
All business logic lives in services/living_docs/.

AGENTESE Path Mapping:
    kg docs                 -> concept.docs.manifest
    kg docs generate        -> concept.docs.generate
    kg docs teaching        -> concept.docs.teaching
    kg docs verify          -> concept.docs.verify

Usage:
    kg docs generate --output docs/reference/
    kg docs generate --overwrite
    kg docs teaching --severity critical
    kg docs verify

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
            print(json.dumps({
                "total_teaching_moments": stats.total,
                "by_severity": stats.by_severity,
                "with_evidence": stats.with_evidence,
                "without_evidence": stats.without_evidence,
                "verified_evidence": stats.verified_evidence,
            }))
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
            print(f"Total: {manifest.total_symbols} symbols, {manifest.total_teaching} teaching moments")
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
            print(json.dumps([
                {
                    "insight": r.moment.insight,
                    "severity": r.moment.severity,
                    "symbol": r.symbol,
                    "module": r.module,
                    "evidence": r.moment.evidence,
                }
                for r in results
            ]))
        else:
            if not results:
                print("No teaching moments found matching filters.")
                return 0

            # Group by severity
            by_severity: dict[str, list] = {"critical": [], "warning": [], "info": []}
            for r in results:
                by_severity[r.moment.severity].append(r)

            icons = {"critical": "\U0001F6A8", "warning": "\u26A0\uFE0F", "info": "\u2139\uFE0F"}

            for sev in ["critical", "warning", "info"]:
                items = by_severity[sev]
                if items:
                    print(f"\n{icons[sev]} {sev.upper()} ({len(items)})")
                    print("-" * 40)
                    for r in items[:10]:  # Limit output
                        print(f"{r.symbol}: {r.moment.insight[:60]}...")
                        if r.moment.evidence:
                            print(f"  Evidence: {r.moment.evidence}")
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
            print(json.dumps({
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
            }))
        else:
            print("Evidence Verification")
            print("=" * 40)
            print(f"Total with evidence: {len(results)}")
            print(f"Verified:            {len(verified)}")
            print(f"Missing:             {len(missing)}")

            if missing:
                print()
                print("\u26A0\uFE0F Missing Evidence Links:")
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


def _print_help() -> None:
    """Print docs command help."""
    help_text = """
kg docs - Living Documentation Generator

Commands:
  kg docs                         Show documentation status
  kg docs generate                Generate reference documentation
  kg docs teaching                Query teaching moments (gotchas)
  kg docs verify                  Verify evidence links exist

Options:
  --output <dir>                  Output directory (default: docs/reference/)
  --overwrite                     Overwrite existing files
  --severity <level>              Filter by severity (critical, warning, info)
  --module <pattern>              Filter by module pattern
  --strict                        Exit 1 if verify finds missing links
  --json                          Output as JSON
  --help, -h                      Show this help message

Examples:
  kg docs generate --output docs/reference/ --overwrite
  kg docs teaching --severity critical
  kg docs teaching --module services.brain
  kg docs verify --strict

AGENTESE Paths:
  concept.docs.manifest           Documentation status
  concept.docs.generate           Generate reference docs
  concept.docs.teaching           Query teaching moments
"""
    print(help_text.strip())


__all__ = ["cmd_docs"]
