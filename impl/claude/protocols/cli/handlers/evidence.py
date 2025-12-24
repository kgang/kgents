"""
Evidence Handler: Evidence mining & ROI tracking.

AGENTESE Path Mapping:
    kg evidence              -> self.memory.evidence.manifest
    kg evidence mine         -> self.memory.evidence.mine
    kg evidence correlate    -> self.memory.evidence.correlate
    kg evidence roi          -> self.memory.evidence.roi
    kg evidence report       -> self.memory.evidence.report
    kg evidence lifecycle    -> self.memory.evidence.lifecycle.*

Usage:
    kg evidence                           # Show status/manifest
    kg evidence mine [--repo PATH]        # Mine git patterns
    kg evidence correlate [--mark-id ID]  # Link marks ↔ commits
    kg evidence roi [--days 30]           # Calculate ROI
    kg evidence report [--format json]    # Full report
    kg evidence lifecycle init            # Initialize tracking
    kg evidence lifecycle refresh         # Re-mine and update
    kg evidence lifecycle export [--format json|markdown]  # Export

Philosophy:
    "Evidence is stratified. Each level unlocks trust."
    L-2 (Prompt) → L-1 (Trace) → L0 (Mark) → L1 (Test) → L2 (Proof) → L3 (Bet)

See: services/witness/evidence.py (Evidence Ladder)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


@handler("evidence", is_async=True, tier=1, description="Evidence mining & ROI")
async def cmd_evidence(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Evidence Mining: Mine git history for evidence patterns and ROI.

    The commit graph is a trace monoid of evidenced decisions. Each commit
    carries evidence. Each test is a repeatable claim. Each mark is human
    attention. The pattern IS the proof.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = _parse_subcommand(args)

    if subcommand == "mine":
        return await _handle_mine(args)
    elif subcommand == "correlate":
        return await _handle_correlate(args)
    elif subcommand == "roi":
        return await _handle_roi(args)
    elif subcommand == "report":
        return await _handle_report(args)
    elif subcommand == "lifecycle":
        return await _handle_lifecycle(args)
    else:
        return await _handle_manifest(args)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "manifest"


def _parse_str_arg(args: list[str], name: str, default: str | None = None) -> str | None:
    """Parse string argument like --repo /path."""
    for i, arg in enumerate(args):
        if arg == f"--{name}" and i + 1 < len(args):
            return args[i + 1]
        elif arg.startswith(f"--{name}="):
            return arg.split("=", 1)[1]
    return default


def _parse_int_arg(args: list[str], name: str, default: int) -> int:
    """Parse integer argument like --days 30."""
    for i, arg in enumerate(args):
        if arg == f"--{name}" and i + 1 < len(args):
            try:
                return int(args[i + 1])
            except ValueError:
                return default
        elif arg.startswith(f"--{name}="):
            try:
                return int(arg.split("=", 1)[1])
            except ValueError:
                return default
    return default


async def _handle_manifest(args: list[str]) -> int:
    """Show evidence status/overview."""
    try:
        # Import evidence service functions (to be implemented)
        try:
            from services.evidence import (
                get_evidence_count,
                get_evidence_by_level,
                get_recent_evidence,
            )
        except ImportError:
            print("Evidence service not yet implemented.")
            print()
            print("Placeholder Status:")
            print("=" * 40)
            print("Total evidence: 0")
            print()
            print("Evidence by Level:")
            print("  L-∞ (Orphan): 0")
            print("  L-2 (Prompt): 0")
            print("  L-1 (Trace): 0")
            print("  L0 (Mark): 0")
            print("  L1 (Test): 0")
            print("  L2 (Proof): 0")
            print("  L3 (Bet): 0")
            print()
            print("Commands:")
            print("  kg evidence mine        Mine git patterns for evidence")
            print("  kg evidence correlate   Link marks ↔ commits")
            print("  kg evidence roi         Calculate ROI metrics")
            print("  kg evidence report      Generate full evidence report")
            print("  kg evidence lifecycle   Manage evidence lifecycle")
            print()
            print("To implement: Create functions in services/evidence/__init__.py")
            return 1

        count = await get_evidence_count()
        by_level = await get_evidence_by_level()
        recent = await get_recent_evidence(limit=5)

        if "--json" in args:
            print(
                json.dumps(
                    {
                        "total_evidence": count,
                        "by_level": {
                            level.level_label: len(evds) for level, evds in by_level.items()
                        },
                        "recent": [e.to_dict() for e in recent],
                    }
                )
            )
        else:
            print("Evidence Status")
            print("=" * 40)
            print(f"Total evidence: {count}")
            print()
            print("Evidence by Level:")
            for level, evds in sorted(by_level.items(), key=lambda x: x[0].value):
                print(f"  {level.level_label} ({level.display_name}): {len(evds)}")
            print()
            print("Recent Evidence:")
            for e in recent:
                print(f"  {e.level.level_label} | {e.source_type} | {e.created_at.strftime('%Y-%m-%d %H:%M')}")

        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def _handle_mine(args: list[str]) -> int:
    """Mine git history for evidence patterns."""
    try:
        repo_path = _parse_str_arg(args, "repo", ".")

        try:
            from services.evidence import mine_evidence_from_git
        except ImportError:
            print("Evidence mining not yet implemented.")
            print()
            print(f"Would mine repository: {repo_path}")
            print()
            print("To implement:")
            print("  1. Create mine_evidence_from_git() in services/evidence/__init__.py")
            print("  2. Extract evidence from:")
            print("     - Commit messages (decisions, gotchas)")
            print("     - Test additions/removals (L1 evidence)")
            print("     - Mark references in commits (L0 evidence)")
            print("     - Trace references (L-1 evidence)")
            print()
            return 1

        print(f"Mining evidence from repository: {repo_path}")
        print()

        result = await mine_evidence_from_git(repo_path=repo_path)

        if "--json" in args:
            print(json.dumps(result.to_dict()))
        else:
            print(f"Evidence mined: {result.total_evidence}")
            print()
            print("By Level:")
            for level, count in result.by_level.items():
                print(f"  {level}: {count}")

        return 0
    except Exception as e:
        print(f"Error mining evidence: {e}")
        return 1


async def _handle_correlate(args: list[str]) -> int:
    """Correlate marks with commits/evidence."""
    try:
        mark_id = _parse_str_arg(args, "mark-id")

        try:
            from services.evidence import correlate_marks_to_commits
        except ImportError:
            print("Evidence correlation not yet implemented.")
            print()
            if mark_id:
                print(f"Would correlate mark: {mark_id}")
            else:
                print("Would correlate all marks with git commits")
            print()
            print("To implement:")
            print("  1. Create correlate_marks_to_commits() in services/evidence/__init__.py")
            print("  2. Match mark timestamps with commit timestamps")
            print("  3. Link marks to commits that reference them")
            print("  4. Build evidence genealogy graph")
            print()
            return 1

        print("Correlating marks with commits...")
        print()

        result = await correlate_marks_to_commits(mark_id=mark_id)

        if "--json" in args:
            print(json.dumps(result.to_dict()))
        else:
            print(f"Correlations found: {result.total_correlations}")
            print()
            for corr in result.correlations[:10]:
                print(f"  Mark {corr.mark_id} → Commit {corr.commit_sha[:8]}")

        return 0
    except Exception as e:
        print(f"Error correlating: {e}")
        return 1


async def _handle_roi(args: list[str]) -> int:
    """Calculate evidence ROI metrics."""
    try:
        days = _parse_int_arg(args, "days", 30)

        try:
            from services.evidence import calculate_evidence_roi
        except ImportError:
            print("Evidence ROI calculation not yet implemented.")
            print()
            print(f"Would calculate ROI for last {days} days")
            print()
            print("ROI Metrics to Track:")
            print("  - Evidence per commit (density)")
            print("  - Time from mark → test (assurance lag)")
            print("  - Test coverage growth rate")
            print("  - Orphan reduction rate (weeds tended)")
            print("  - Confidence trajectory (decay vs. renewal)")
            print()
            print("To implement:")
            print("  1. Create calculate_evidence_roi() in services/evidence/__init__.py")
            print("  2. Query evidence by timeframe")
            print("  3. Calculate metrics above")
            print("  4. Return ROI report with trends")
            print()
            return 1

        print(f"Calculating evidence ROI (last {days} days)...")
        print()

        result = await calculate_evidence_roi(days=days)

        if "--json" in args:
            print(json.dumps(result.to_dict()))
        else:
            print("Evidence ROI Report")
            print("=" * 40)
            print(f"Timeframe: {days} days")
            print()
            print(f"Evidence density: {result.evidence_per_commit:.2f} per commit")
            print(f"Assurance lag: {result.mark_to_test_hours:.1f} hours (mark → test)")
            print(f"Test coverage: {result.test_coverage_percent:.1f}%")
            print(f"Orphan rate: {result.orphan_percent:.1f}% (weeds in garden)")
            print(f"Confidence trend: {result.confidence_trend}")

        return 0
    except Exception as e:
        print(f"Error calculating ROI: {e}")
        return 1


async def _handle_report(args: list[str]) -> int:
    """Generate full evidence report."""
    try:
        format_type = _parse_str_arg(args, "format", "text")

        try:
            from services.evidence import generate_evidence_report
        except ImportError:
            print("Evidence reporting not yet implemented.")
            print()
            print(f"Would generate report in format: {format_type}")
            print()
            print("Report Sections:")
            print("  1. Evidence Overview (total, by level)")
            print("  2. Genealogy Graph (evidence lineage)")
            print("  3. Orphan Analysis (weeds needing tending)")
            print("  4. ROI Metrics (efficiency, assurance)")
            print("  5. Recommendations (what to witness next)")
            print()
            print("To implement:")
            print("  1. Create generate_evidence_report() in services/evidence/__init__.py")
            print("  2. Aggregate all evidence data")
            print("  3. Format as text/json/markdown")
            print()
            return 1

        print("Generating evidence report...")
        print()

        report = await generate_evidence_report(format=format_type)

        if format_type == "json" or "--json" in args:
            print(json.dumps(report.to_dict()))
        else:
            print(report.to_text())

        return 0
    except Exception as e:
        print(f"Error generating report: {e}")
        return 1


async def _handle_lifecycle(args: list[str]) -> int:
    """Manage evidence lifecycle."""
    # Parse lifecycle subcommand
    lifecycle_cmd = None
    for arg in args[1:]:  # Skip 'lifecycle' itself
        if not arg.startswith("-"):
            lifecycle_cmd = arg.lower()
            break

    if lifecycle_cmd == "init":
        return await _handle_lifecycle_init(args)
    elif lifecycle_cmd == "refresh":
        return await _handle_lifecycle_refresh(args)
    elif lifecycle_cmd == "export":
        return await _handle_lifecycle_export(args)
    else:
        print("Evidence Lifecycle Commands")
        print("=" * 40)
        print("  kg evidence lifecycle init     Initialize evidence tracking")
        print("  kg evidence lifecycle refresh  Re-mine and update evidence")
        print("  kg evidence lifecycle export   Export evidence to file")
        print()
        print("Run 'kg evidence lifecycle <command> --help' for details")
        return 0


async def _handle_lifecycle_init(args: list[str]) -> int:
    """Initialize evidence tracking."""
    try:
        try:
            from services.evidence import initialize_evidence_tracking
        except ImportError:
            print("Evidence initialization not yet implemented.")
            print()
            print("Would initialize evidence tracking:")
            print("  - Create evidence database tables")
            print("  - Set up genealogy graph indices")
            print("  - Initialize baseline metrics")
            print()
            return 1

        print("Initializing evidence tracking...")
        result = await initialize_evidence_tracking()

        print(f"✓ Evidence tracking initialized")
        print(f"  Database: {result.database_status}")
        print(f"  Indices: {result.indices_created}")

        return 0
    except Exception as e:
        print(f"Error initializing: {e}")
        return 1


async def _handle_lifecycle_refresh(args: list[str]) -> int:
    """Refresh evidence by re-mining."""
    try:
        try:
            from services.evidence import refresh_evidence
        except ImportError:
            print("Evidence refresh not yet implemented.")
            print()
            print("Would refresh evidence:")
            print("  - Re-mine git history")
            print("  - Update correlations")
            print("  - Recalculate ROI metrics")
            print()
            return 1

        print("Refreshing evidence...")
        result = await refresh_evidence()

        print(f"✓ Evidence refreshed")
        print(f"  New evidence: {result.new_evidence_count}")
        print(f"  Updated: {result.updated_count}")

        return 0
    except Exception as e:
        print(f"Error refreshing: {e}")
        return 1


async def _handle_lifecycle_export(args: list[str]) -> int:
    """Export evidence to file."""
    try:
        format_type = _parse_str_arg(args, "format", "json")
        output_file = _parse_str_arg(args, "output", f"evidence-export.{format_type}")

        try:
            from services.evidence import export_evidence
        except ImportError:
            print("Evidence export not yet implemented.")
            print()
            print(f"Would export evidence to: {output_file}")
            print(f"Format: {format_type}")
            print()
            return 1

        print(f"Exporting evidence to {output_file}...")
        result = await export_evidence(output_file=output_file, format=format_type)

        print(f"✓ Evidence exported")
        print(f"  File: {output_file}")
        print(f"  Evidence count: {result.evidence_count}")

        return 0
    except Exception as e:
        print(f"Error exporting: {e}")
        return 1


def _print_help() -> None:
    """Print evidence command help."""
    help_text = """
kg evidence - Evidence mining & ROI tracking

Commands:
  kg evidence                Show evidence status/manifest
  kg evidence mine           Mine git history for evidence patterns
  kg evidence correlate      Correlate marks with commits
  kg evidence roi            Calculate ROI metrics
  kg evidence report         Generate full evidence report
  kg evidence lifecycle      Manage evidence lifecycle (init, refresh, export)

Options:
  --repo <path>       Repository path (default: current directory)
  --mark-id <id>      Specific mark to correlate
  --days <n>          Days for ROI calculation (default: 30)
  --format <type>     Output format: text|json|markdown
  --output <file>     Output file for export
  --json              Output as JSON
  --help, -h          Show this help message

Examples:
  kg evidence mine --repo /path/to/repo
  kg evidence correlate --mark-id mark-abc123
  kg evidence roi --days 90 --json
  kg evidence report --format json
  kg evidence lifecycle init
  kg evidence lifecycle refresh
  kg evidence lifecycle export --format markdown --output evidence.md

Evidence Levels:
  L-∞ (Orphan)  - Artifact without lineage (weed)
  L-2 (Prompt)  - Generative thought that created artifact
  L-1 (Trace)   - Runtime behavior observation
  L0 (Mark)     - Human attention marker
  L1 (Test)     - Automated repeatable check
  L2 (Proof)    - Formal law verification
  L3 (Bet)      - Economic stake on confidence

Philosophy:
  "Evidence is stratified. Each level unlocks trust."
  "The proof IS the decision. The mark IS the witness."
  "Orphans are weeds. Weeds exist; we tend them."

AGENTESE Paths:
  self.memory.evidence.mine            Mine evidence from git
  self.memory.evidence.correlate       Link marks ↔ commits
  self.memory.evidence.roi             Calculate ROI metrics
  self.memory.evidence.genealogy       Query evidence lineage graph

See: services/witness/evidence.py (Evidence Ladder)
"""
    print(help_text.strip())


__all__ = ["cmd_evidence"]
