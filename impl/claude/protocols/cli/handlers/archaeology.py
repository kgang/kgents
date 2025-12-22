"""
Archaeology Handler: Mine git history for wisdom.

AGENTESE Path Mapping:
    kg archaeology             -> self.memory.archaeology.manifest
    kg archaeology mine        -> self.memory.archaeology.mine
    kg archaeology report      -> self.memory.archaeology.report
    kg archaeology teaching    -> self.memory.archaeology.teaching
    kg archaeology crystallize -> self.memory.archaeology.crystallize
    kg archaeology priors      -> concept.compiler.priors.from_archaeology

Usage:
    kg archaeology mine [--max-commits 500]
    kg archaeology report [--active-only]
    kg archaeology teaching [--category gotcha]
    kg archaeology crystallize [--dry-run]
    kg archaeology priors [--output priors.json]

See: spec/protocols/repo-archaeology.md, plans/git-archaeology-backfill.md
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_archaeology(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Git Archaeology: Mine git history for patterns, teachings, and priors.

    The git log is a trace monoid of development choices. Each commit is a nudge.
    Each revert is a failed experiment. The pattern of commits IS the prior.
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    subcommand = _parse_subcommand(args)

    if subcommand == "mine":
        return _handle_mine(args)
    elif subcommand == "report":
        return _handle_report(args)
    elif subcommand == "teaching":
        return _handle_teaching(args)
    elif subcommand == "crystallize":
        return _handle_crystallize(args)
    elif subcommand == "priors":
        return _handle_priors(args)
    else:
        return _handle_manifest(args)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "manifest"


def _parse_int_arg(args: list[str], name: str, default: int) -> int:
    """Parse integer argument like --max-commits 500."""
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


def _parse_str_arg(args: list[str], name: str, default: str | None = None) -> str | None:
    """Parse string argument like --category gotcha."""
    for i, arg in enumerate(args):
        if arg == f"--{name}" and i + 1 < len(args):
            return args[i + 1]
        elif arg.startswith(f"--{name}="):
            return arg.split("=", 1)[1]
    return default


def _handle_manifest(args: list[str]) -> int:
    """Show archaeology status/overview."""
    try:
        from services.archaeology import get_commit_count, get_patterns_by_status

        commit_count = get_commit_count()
        patterns_by_status = get_patterns_by_status()

        if "--json" in args:
            print(json.dumps({
                "total_commits": commit_count,
                "features": {
                    status: len(patterns)
                    for status, patterns in patterns_by_status.items()
                },
            }))
        else:
            print("Git Archaeology Status")
            print("=" * 40)
            print(f"Total commits: {commit_count}")
            print()
            print("Features by Status:")
            for status, patterns in patterns_by_status.items():
                print(f"  {status.capitalize()}: {len(patterns)}")
            print()
            print("Commands:")
            print("  kg archaeology mine       Parse git history")
            print("  kg archaeology report     Feature trajectory report")
            print("  kg archaeology teaching   Extract teachings from commits")
            print("  kg archaeology crystallize  Persist teachings to Brain")
            print("  kg archaeology priors     Extract ASHC priors")

        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_mine(args: list[str]) -> int:
    """Parse git history and show summary statistics."""
    try:
        from services.archaeology import get_authors, get_commit_count, get_file_activity, parse_git_log

        max_commits = _parse_int_arg(args, "max-commits", 500)

        print(f"Mining git history (max {max_commits} commits)...")

        commits = parse_git_log(max_commits=max_commits)
        commit_count = get_commit_count()
        authors = get_authors()
        hot_files = get_file_activity(limit=10)

        if "--json" in args:
            print(json.dumps({
                "parsed_commits": len(commits),
                "total_commits": commit_count,
                "authors": authors,
                "hot_files": [
                    {"path": f.path, "commits": f.commit_count}
                    for f in hot_files
                ],
                "commit_types": _count_commit_types(commits),
            }))
        else:
            print()
            print(f"Parsed: {len(commits)} / {commit_count} commits")
            print()

            # Authors
            print("Authors:")
            for author, count in sorted(authors.items(), key=lambda x: -x[1])[:5]:
                print(f"  {author}: {count} commits")
            print()

            # Commit types
            print("Commit Types:")
            types = _count_commit_types(commits)
            for ctype, count in sorted(types.items(), key=lambda x: -x[1])[:8]:
                print(f"  {ctype}: {count}")
            print()

            # Hot files
            print("Hot Files (most touched):")
            for f in hot_files[:5]:
                print(f"  {f.path}: {f.commit_count} commits")

        return 0
    except Exception as e:
        print(f"Error mining: {e}")
        return 1


def _handle_report(args: list[str]) -> int:
    """Generate feature trajectory report."""
    try:
        from services.archaeology import (
            ACTIVE_FEATURES,
            FEATURE_PATTERNS,
            classify_all_features,
            generate_report,
            parse_git_log,
        )

        max_commits = _parse_int_arg(args, "max-commits", 500)
        active_only = "--active-only" in args or "--active" in args

        patterns = ACTIVE_FEATURES if active_only else FEATURE_PATTERNS

        print(f"Generating report for {len(patterns)} features...")
        commits = parse_git_log(max_commits=max_commits)
        trajectories = classify_all_features(patterns, commits)
        report = generate_report(trajectories)

        if "--json" in args:
            print(json.dumps({
                "features": len(trajectories),
                "commits_analyzed": len(commits),
                "trajectories": [
                    t.to_report_row() for t in trajectories.values()
                ],
            }))
        else:
            print(report)

        return 0
    except Exception as e:
        print(f"Error generating report: {e}")
        return 1


def _handle_teaching(args: list[str]) -> int:
    """Extract and display teachings from commits."""
    try:
        from services.archaeology import (
            extract_teachings_from_commits,
            generate_teaching_report,
            parse_git_log,
        )

        max_commits = _parse_int_arg(args, "max-commits", 200)
        category_filter = _parse_str_arg(args, "category")

        commits = parse_git_log(max_commits=max_commits)
        teachings = extract_teachings_from_commits(commits)

        # Filter by category if specified
        if category_filter:
            teachings = [t for t in teachings if t.category == category_filter]

        if "--json" in args:
            print(json.dumps({
                "total": len(teachings),
                "by_category": _count_by_category(teachings),
                "teachings": [
                    {
                        "insight": t.teaching.insight,
                        "severity": t.teaching.severity,
                        "category": t.category,
                        "features": list(t.features),
                        "commit": t.commit.sha[:8],
                    }
                    for t in teachings[:50]  # Limit JSON output
                ],
            }))
        else:
            report = generate_teaching_report(teachings)
            print(report)

        return 0
    except Exception as e:
        print(f"Error extracting teachings: {e}")
        return 1


def _handle_crystallize(args: list[str]) -> int:
    """Crystallize commit teachings to Brain persistence."""
    try:
        from services.archaeology import (
            extract_teachings_from_commits,
            parse_git_log,
        )

        max_commits = _parse_int_arg(args, "max-commits", 200)
        dry_run = "--dry-run" in args

        commits = parse_git_log(max_commits=max_commits)
        teachings = extract_teachings_from_commits(commits)

        if dry_run:
            print("Crystallization Dry Run")
            print("=" * 40)
            print(f"Would crystallize: {len(teachings)} teachings")
            print()
            by_category = _count_by_category(teachings)
            for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
                print(f"  {cat}: {count}")
            print()
            print("Run without --dry-run to persist to Brain.")

            if "--json" in args:
                print(json.dumps({
                    "mode": "dry_run",
                    "would_crystallize": len(teachings),
                    "by_category": by_category,
                }))
            return 0

        # Actual crystallization
        # TODO: Wire to Brain persistence when ready
        print("Crystallizing teachings to Brain...")
        print()
        print("NOTE: Full Brain integration pending.")
        print(f"Found {len(teachings)} teachings from {len(commits)} commits.")
        print()
        print("To persist, use: kg docs crystallize (for docstring teachings)")
        print("or wait for archaeology → Brain integration.")

        return 0
    except Exception as e:
        print(f"Error crystallizing: {e}")
        return 1


def _handle_priors(args: list[str]) -> int:
    """Extract ASHC priors from archaeological analysis."""
    try:
        from services.archaeology import (
            ACTIVE_FEATURES,
            classify_all_features,
            extract_causal_priors,
            extract_spec_patterns,
            generate_prior_report,
            parse_git_log,
        )

        max_commits = _parse_int_arg(args, "max-commits", 500)
        output_file = _parse_str_arg(args, "output")

        print("Extracting priors from git history...")

        commits = parse_git_log(max_commits=max_commits)
        trajectories = classify_all_features(ACTIVE_FEATURES, commits)

        # Extract patterns and priors
        spec_patterns = extract_spec_patterns(list(trajectories.values()))
        causal_priors = extract_causal_priors(list(trajectories.values()))

        report = generate_prior_report(spec_patterns, [], causal_priors)

        if output_file:
            # Write priors to file
            priors_data = {
                "spec_patterns": [
                    {
                        "pattern_type": p.pattern_type,
                        "success_correlation": p.success_correlation,
                        "confidence": p.confidence,
                        "examples": list(p.example_specs),
                    }
                    for p in spec_patterns
                ],
                "causal_priors": [
                    {
                        "pattern": p.pattern,
                        "outcome_correlation": p.outcome_correlation,
                        "sample_size": p.sample_size,
                        "confidence": p.confidence,
                    }
                    for p in causal_priors
                ],
            }
            with open(output_file, "w") as f:
                json.dump(priors_data, f, indent=2)
            print(f"Priors written to: {output_file}")
            return 0

        if "--json" in args:
            print(json.dumps({
                "spec_patterns": len(spec_patterns),
                "causal_priors": len(causal_priors),
                "patterns": [p.pattern_type for p in spec_patterns],
            }))
        else:
            print(report)

        return 0
    except Exception as e:
        print(f"Error extracting priors: {e}")
        return 1


def _count_commit_types(commits: list) -> dict[str, int]:
    """Count commits by type."""
    counts: dict[str, int] = {}
    for c in commits:
        ctype = c.commit_type
        counts[ctype] = counts.get(ctype, 0) + 1
    return counts


def _count_by_category(teachings: list) -> dict[str, int]:
    """Count teachings by category."""
    counts: dict[str, int] = {}
    for t in teachings:
        counts[t.category] = counts.get(t.category, 0) + 1
    return counts


def _print_help() -> None:
    """Print archaeology command help."""
    help_text = """
kg archaeology - Mine git history for wisdom

Commands:
  kg archaeology              Show archaeology status
  kg archaeology mine         Parse git history (commits, authors, hot files)
  kg archaeology report       Generate feature trajectory report
  kg archaeology teaching     Extract teachings from commits (gotchas, warnings)
  kg archaeology crystallize  Persist teachings to Brain
  kg archaeology priors       Extract ASHC priors for metacompiler

Options:
  --max-commits <n>    Maximum commits to analyze (default: 500)
  --active-only        Only analyze active features (not extinct)
  --category <cat>     Filter teachings by category (gotcha|warning|critical|decision|pattern)
  --output <file>      Output priors to JSON file
  --dry-run           Preview without persisting
  --json              Output as JSON
  --help, -h          Show this help message

Examples:
  kg archaeology mine --max-commits 1000
  kg archaeology report --active-only
  kg archaeology teaching --category gotcha
  kg archaeology teaching --json | jq '.teachings[].insight'
  kg archaeology crystallize --dry-run
  kg archaeology priors --output ashc-priors.json

Philosophy:
  "The past is not dead. It is not even past." - Faulkner
  "The artifact remembers so the agent can forget." - Stigmergy

AGENTESE Paths:
  self.memory.archaeology.mine           Parse git history
  self.memory.archaeology.trajectories   List feature trajectories
  self.memory.archaeology.crystallize    Crystallize teachings
  concept.compiler.priors.from_archaeology  Get ASHC priors
"""
    print(help_text.strip())


__all__ = ["cmd_archaeology"]
