"""
Inspection commands: starters, manifest, eigenvectors, audit, garden, validate.

These provide visibility into the soul's state and configuration.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from protocols.cli.shared import InvocationContext, OutputFormatter

if TYPE_CHECKING:
    pass


async def execute_starters(ctx: InvocationContext, soul: Any) -> int:
    """Handle 'soul starters' command."""
    from agents.k import all_starters

    output = OutputFormatter(ctx)
    starters = all_starters()

    if ctx.json_mode:
        output.emit(json.dumps(starters, indent=2), {"starters": starters})
    else:
        from agents.k import format_all_starters_for_display

        formatted = format_all_starters_for_display()
        output.emit(formatted, {"starters": starters})

    return 0


async def execute_manifest(ctx: InvocationContext, soul: Any) -> int:
    """Handle 'soul manifest' command."""
    output = OutputFormatter(ctx)
    state = soul.manifest()
    brief = soul.manifest_brief()

    if ctx.json_mode:
        output.emit(json.dumps(brief, indent=2), brief)
    else:
        lines = [
            "[SOUL] Manifest",
            "",
            f"  Mode: {state.active_mode.value}",
            f"  Session interactions: {state.interactions_count}",
            f"  Session tokens: {state.tokens_used_session}",
            "",
            "  Eigenvectors:",
        ]

        for name, value in brief["eigenvectors"].items():
            lines.append(f"    {name}: {value:.2f}")

        output.emit("\n".join(lines), brief)

    return 0


async def execute_eigenvectors(ctx: InvocationContext, soul: Any) -> int:
    """Handle 'soul eigenvectors' command."""
    output = OutputFormatter(ctx)
    eigenvectors = soul.eigenvectors

    if ctx.json_mode:
        data = eigenvectors.to_dict()
        output.emit(json.dumps(data, indent=2), {"eigenvectors": data})
    else:
        prompt = eigenvectors.to_system_prompt_section()
        output.emit(prompt, {"eigenvectors": eigenvectors.to_dict()})

    return 0


def execute_audit(
    ctx: InvocationContext, soul: Any, summary_mode: bool, limit: int
) -> int:
    """Handle 'soul audit' command."""
    output = OutputFormatter(ctx)
    audit_trail = soul.audit

    if summary_mode:
        # Show summary
        summary = audit_trail.summary()

        if ctx.json_mode:
            output.emit(json.dumps(summary, indent=2), summary)
        else:
            formatted = audit_trail.format_summary()
            output.emit(formatted, summary)
    else:
        # Show recent entries
        entries = audit_trail.recent(limit)
        entries_data = [e.to_dict() for e in entries]

        if ctx.json_mode:
            output.emit(json.dumps(entries_data, indent=2), {"entries": entries_data})
        else:
            formatted = audit_trail.format_recent(limit)
            output.emit(formatted, {"entries": entries_data})

    return 0


async def execute_garden(
    ctx: InvocationContext, soul: Any, sync_hypnagogia: bool
) -> int:
    """
    Handle 'soul garden' command - view PersonaGarden state.

    Shows the current state of the persona garden including:
    - Entry counts by type and lifecycle
    - Established patterns (trees)
    - Recent seeds
    """
    from agents.k.garden import get_garden
    from agents.k.hypnagogia import get_hypnagogia

    output = OutputFormatter(ctx)
    garden = get_garden()

    # Optionally sync from hypnagogia
    if sync_hypnagogia:
        hypnagogia = get_hypnagogia()
        synced = await garden.sync_from_hypnagogia(hypnagogia)
        if synced > 0:
            output.emit(
                f"[GARDEN] Synced {synced} pattern(s) from hypnagogia",
                {"synced": synced},
            )

    # Get stats
    stats = await garden.stats()

    if ctx.json_mode:
        data = {
            "total_entries": stats.total_entries,
            "by_type": stats.by_type,
            "by_lifecycle": stats.by_lifecycle,
            "average_confidence": stats.average_confidence,
            "total_evidence": stats.total_evidence,
            "entries": [e.to_dict() for e in garden.entries.values()],
        }
        output.emit(json.dumps(data, indent=2), data)
    else:
        # Human-friendly output
        output.emit(garden.format_summary(), {"stats": stats.__dict__})

    return 0


async def execute_validate(
    ctx: InvocationContext,
    soul: Any,
    file_path: str | None,
    use_llm: bool,
) -> int:
    """
    Handle 'soul validate' command - check code against principles.

    The Semantic Gatekeeper checks code for principle violations:
    - Heuristic pattern matching (fast, always available)
    - LLM semantic analysis (deeper, requires --deep flag)
    """
    from agents.k.gatekeeper import SemanticGatekeeper

    output = OutputFormatter(ctx)

    if file_path is None:
        output.emit(
            "[GATEKEEPER] Error: No file path provided\n"
            "Usage: kgents soul validate <file> [--deep] [--json]",
            {"error": "No file path provided"},
        )
        return 1

    # Create gatekeeper with soul's LLM if available and requested
    llm = soul._llm if use_llm and soul.has_llm else None
    gatekeeper = SemanticGatekeeper(llm=llm, use_llm=use_llm)

    output.emit(
        f"[GATEKEEPER] Validating: {file_path}" + (" (deep)" if use_llm else ""),
        {"status": "validating", "file": file_path, "deep": use_llm},
    )

    result = await gatekeeper.validate_file(file_path)

    if ctx.json_mode:
        output.emit(json.dumps(result.to_dict(), indent=2), result.to_dict())
    else:
        output.emit(result.format(), result.to_dict())

    return 0 if result.passed else 1


async def execute_dream(ctx: InvocationContext, soul: Any, dry_run: bool) -> int:
    """
    Handle 'soul dream' command - trigger hypnagogia manually.

    The dream cycle processes accumulated interactions and:
    - Extracts patterns from dialogue history
    - Promotes strong patterns (SEED -> TREE)
    - Adjusts eigenvector confidence based on evidence
    - Composts stale patterns
    """
    from agents.k.hypnagogia import get_hypnagogia

    output = OutputFormatter(ctx)
    hypnagogia = get_hypnagogia()

    # Check if LLM is available for deeper pattern analysis
    if soul.has_llm and hypnagogia._llm is None:
        # Share the soul's LLM client with hypnagogia
        hypnagogia._llm = soul._llm

    output.emit(
        f"[SOUL:DREAM] Starting {'(dry run)' if dry_run else ''}...",
        {"status": "starting", "dry_run": dry_run},
    )

    # Execute dream cycle
    report = await hypnagogia.dream(soul, dry_run=dry_run)

    if ctx.json_mode:
        output.emit(json.dumps(report.to_dict(), indent=2), report.to_dict())
    else:
        # Human-friendly output
        output.emit(report.summary, report.to_dict())

        # Show additional details if interesting
        if report.patterns_discovered:
            output.emit("\nPatterns discovered:", {})
            for pattern in report.patterns_discovered[:5]:
                output.emit(f"  - {pattern.content}", {})

    return 0
