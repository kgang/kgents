"""
Grow CLI Handler: Autopoietic Holon Generator.

self.grow enables AGENTESE to extend its own ontology through a governed,
entropy-budgeted process. This CLI provides an intuitive interface for
the complete growth pipeline.

Usage:
    kg grow                       # Interactive dashboard
    kg grow status                # Budget and nursery status
    kg grow recognize             # Scan for ontological gaps
    kg grow propose <context> <entity>  # Draft a new proposal
    kg grow validate <proposal_id>      # Validate a proposal
    kg grow nursery               # View germinating holons
    kg grow germinate <proposal_id>     # Add to nursery
    kg grow promote <germination_id>    # Promote to production
    kg grow rollback <handle>     # Rollback a promoted holon
    kg grow prune                 # Cleanup failed holons

    Persistent Storage (Cortex):
    kg grow list                  # List all proposals from cortex
    kg grow list --status draft   # Filter by status
    kg grow list --context world  # Filter by context
    kg grow search <query>        # Semantic search proposals
    kg grow show <proposal_id>    # Show proposal details

    Interactive Mode:
    kg grow wizard                # Guided proposal creation
    kg grow demo                  # Demo the full pipeline

AGENTESE: self.grow.*
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

# Rich imports for beautiful output (graceful degradation)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt
    from rich.table import Table
    from rich.text import Text
    from rich.tree import Tree

    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None  # type: ignore[assignment]


# =============================================================================
# State Management
# =============================================================================


@dataclass
class GrowSession:
    """Track grow session state."""

    resolver: Any = None
    cortex: Any = None  # GrowthCortex for persistence
    proposals: dict[str, Any] = field(default_factory=dict)
    last_gaps: list[Any] = field(default_factory=list)
    _initialized: bool = False


_session: GrowSession | None = None


def _get_session() -> GrowSession:
    """Get or create grow session."""
    global _session
    if _session is None:
        _session = GrowSession()
    return _session


def _get_resolver() -> Any:
    """Get or create the SelfGrowResolver."""
    session = _get_session()
    if session.resolver is None:
        from protocols.agentese.contexts.self_grow import create_self_grow_resolver

        session.resolver = create_self_grow_resolver()
    return session.resolver


async def _get_cortex() -> Any:
    """Get or create the GrowthCortex for persistence."""
    session = _get_session()
    if session.cortex is None:
        from protocols.agentese.contexts.self_grow import create_growth_cortex
        from protocols.cli.instance_db.storage import StorageProvider

        try:
            # Try to get storage provider
            storage = await StorageProvider.from_config()
            session.cortex = create_growth_cortex(relational=storage.relational)

            # Initialize schema (runs migrations if needed)
            await session.cortex.init_schema()
        except Exception:
            # Fall back to in-memory (no persistence)
            session.cortex = create_growth_cortex()

    return session.cortex


def _run_async(coro: Any) -> Any:
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already an event loop, create a new one in a thread
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(coro)


# =============================================================================
# Output Helpers
# =============================================================================


def _emit(message: str, data: dict[str, Any], ctx: "InvocationContext | None") -> None:
    """Emit output to console and optional context."""
    if ctx is not None:
        ctx.output(message, data)
    else:
        print(message)


def _print_help() -> None:
    """Print help for grow command."""
    print(__doc__)


def _print_banner() -> None:
    """Print the grow banner."""
    if RICH_AVAILABLE:
        banner = Panel(
            "[bold cyan]self.grow[/] - The Autopoietic Holon Generator\n\n"
            '[dim]"The system that cannot grow new organs is already dead."[/]',
            border_style="cyan",
            padding=(1, 2),
        )
        console.print(banner)
    else:
        print("=" * 60)
        print("  self.grow - The Autopoietic Holon Generator")
        print('  "The system that cannot grow new organs is already dead."')
        print("=" * 60)


# =============================================================================
# Status Commands
# =============================================================================


def _show_status(ctx: "InvocationContext | None") -> int:
    """Show comprehensive grow status dashboard."""
    from protocols.agentese.contexts.self_grow import GrowthBudget, NurseryConfig

    resolver = _get_resolver()
    budget = resolver._budget
    nursery = resolver._nursery
    session = _get_session()

    # Gather pipeline stats
    draft_count = len(session.proposals)
    ready_to_promote = len(nursery.get_ready_for_promotion()) if nursery else 0
    ready_to_prune = len(nursery.get_ready_for_pruning()) if nursery else 0
    nursery_count = len(nursery.active) if nursery else 0
    nursery_capacity = nursery._config.max_capacity if nursery else 10

    # Fetch persistent proposals count
    async def _count_proposals() -> int:
        try:
            cortex = await _get_cortex()
            proposals = await cortex.list_proposals(status="draft")
            return len(proposals)
        except Exception:
            return 0

    try:
        persistent_drafts = _run_async(_count_proposals())
        draft_count = max(draft_count, persistent_drafts)
    except Exception:
        pass

    # Budget calculation (used in both branches)
    budget_pct = int(budget.remaining / budget.config.max_entropy_per_run * 100)

    if RICH_AVAILABLE:
        # Budget info
        budget_bar = "█" * (budget_pct // 5) + "░" * (20 - budget_pct // 5)

        # Tier styling
        if budget_pct >= 75:
            tier = "[green]ABUNDANT[/]"
            bar_style = "green"
        elif budget_pct >= 40:
            tier = "[yellow]HEALTHY[/]"
            bar_style = "yellow"
        elif budget_pct >= 10:
            tier = "[orange1]LIMITED[/]"
            bar_style = "orange1"
        else:
            tier = "[red]EXHAUSTED[/]"
            bar_style = "red"

        # Build dashboard content
        lines = []
        lines.append("")
        lines.append(
            f"  [bold]Budget:[/] [{bar_style}]{budget_bar}[/] {budget_pct}% {tier}"
        )
        lines.append(f"  [bold]Nursery:[/] {nursery_count}/{nursery_capacity} holons")
        lines.append("")
        lines.append("  [bold]Pipeline Activity:[/]")

        # Show activity with color-coded counts
        if draft_count > 0:
            lines.append(f"    [cyan]•[/] {draft_count} proposal(s) in draft")
        else:
            lines.append("    [dim]• No proposals in draft[/]")

        if ready_to_promote > 0:
            promote_names = [
                f"{h.proposal.context}.{h.proposal.entity}"
                for h in (nursery.get_ready_for_promotion() if nursery else [])[:2]
            ]
            names_str = ", ".join(promote_names)
            if len(nursery.get_ready_for_promotion() if nursery else []) > 2:
                names_str += ", ..."
            lines.append(
                f"    [green]•[/] {ready_to_promote} holon(s) ready to promote ({names_str})"
            )
        else:
            lines.append("    [dim]• No holons ready to promote[/]")

        if ready_to_prune > 0:
            lines.append(f"    [red]•[/] {ready_to_prune} holon(s) ready to prune")
        else:
            lines.append("    [dim]• No holons ready to prune[/]")

        lines.append("")
        lines.append("  [bold]Quick Actions:[/]")
        lines.append("    [cyan]kg grow propose[/]   Create a new holon proposal")
        lines.append("    [cyan]kg grow list[/]      View persisted proposals")
        lines.append("    [cyan]kg grow nursery[/]   View germinating holons")
        lines.append("    [cyan]kg grow wizard[/]    Interactive guided creation")
        lines.append("")

        dashboard = Panel(
            "\n".join(lines),
            title="[bold cyan]self.grow Dashboard[/]",
            subtitle="[dim]The Autopoietic Holon Generator[/]",
            border_style="cyan",
        )
        console.print(dashboard)

        # Show suggested next action based on state
        if ready_to_promote > 0:
            holon = nursery.get_ready_for_promotion()[0]
            console.print(
                f"\n[green]Suggested:[/] Promote ready holon: "
                f"[cyan]kg grow promote {holon.germination_id[:8]}[/]"
            )
        elif ready_to_prune > 0:
            console.print(
                "\n[yellow]Suggested:[/] Clean up failed holons: [cyan]kg grow prune[/]"
            )
        elif draft_count > 0:
            console.print(
                "\n[dim]Tip: Validate your drafts with [cyan]kg grow list[/] → [cyan]kg grow validate <id>[/][/]"
            )
        else:
            console.print(
                "\n[dim]Tip: Get started with [cyan]kg grow wizard[/] or [cyan]kg grow demo[/][/]"
            )

    else:
        # Plain text fallback
        print("\n=== self.grow Status ===")
        print(
            f"Budget: {budget_pct}% ({budget.remaining:.2f}/{budget.config.max_entropy_per_run})"
        )
        print(f"Nursery: {nursery_count}/{nursery_capacity}")
        print("\nPipeline:")
        print(f"  Drafts: {draft_count}")
        print(f"  Ready to promote: {ready_to_promote}")
        print(f"  Ready to prune: {ready_to_prune}")

    return 0


def _show_budget(ctx: "InvocationContext | None") -> int:
    """Show entropy budget details with regeneration timeline."""
    resolver = _get_resolver()
    budget = resolver._budget

    status = budget.status()
    pct = status["percent"]
    remaining = status["remaining"]
    max_budget = status["max"]

    # Determine capability tier
    if pct >= 75:
        tier = "[bold green]ABUNDANT[/]"
        tier_desc = "All operations available"
    elif pct >= 40:
        tier = "[bold yellow]HEALTHY[/]"
        tier_desc = "Most operations available"
    elif pct >= 10:
        tier = "[bold orange1]LIMITED[/]"
        tier_desc = "Some operations may be blocked"
    else:
        tier = "[bold red]EXHAUSTED[/]"
        tier_desc = "Only view operations available"

    if RICH_AVAILABLE:
        # Visual progress bar (20 chars)
        filled = int(pct / 5)
        bar = "█" * filled + "░" * (20 - filled)

        # Color the bar based on tier
        if pct >= 75:
            bar_styled = f"[green]{bar}[/]"
        elif pct >= 40:
            bar_styled = f"[yellow]{bar}[/]"
        elif pct >= 10:
            bar_styled = f"[orange1]{bar}[/]"
        else:
            bar_styled = f"[red]{bar}[/]"

        console.print(f"\n[bold]Entropy Budget:[/] {tier} ({pct}%)")
        console.print(f"  {bar_styled} {remaining:.2f} / {max_budget:.2f}")
        console.print(f"  [dim]{tier_desc}[/]")

        # Regeneration timeline
        regen_rate = budget.config.regeneration_rate_per_hour
        if remaining < max_budget:
            deficit = max_budget - remaining
            hours_to_full = deficit / regen_rate
            hours = int(hours_to_full)
            minutes = int((hours_to_full - hours) * 60)

            console.print("\n[bold]Regeneration:[/]")
            console.print(f"  Rate: +{regen_rate:.2f} per hour")
            if hours > 0:
                console.print(f"  Full in: {hours}h {minutes}m")
            else:
                console.print(f"  Full in: {minutes}m")
            console.print(f"  Next +0.10 in: ~{int(60 / (regen_rate * 10))}m")
        else:
            console.print("\n[green]Budget is full![/]")

        # Can afford section
        operations = [
            ("recognize", budget.config.recognize_cost),
            ("propose", budget.config.propose_cost),
            ("validate", budget.config.validate_cost),
            ("germinate", budget.config.germinate_cost),
            ("promote", budget.config.promote_cost),
            ("prune", budget.config.prune_cost),
        ]

        console.print("\n[bold]Can Afford:[/]")
        for op, cost in operations:
            can_afford = remaining >= cost
            icon = "[green]✓[/]" if can_afford else "[red]✗[/]"
            style = "" if can_afford else "[dim]"
            end_style = "[/]" if not can_afford else ""
            console.print(f"  {icon} {style}{op:<12} ({cost:.2f}){end_style}")

        # Spending breakdown if any
        if status["spent_by_operation"]:
            console.print("\n[bold]Spent This Session:[/]")
            for op, cost in status["spent_by_operation"].items():
                console.print(f"  {op}: {cost:.2f}")
    else:
        # Plain text fallback
        _emit(f"Budget: {tier} ({pct}%)", status, ctx)
        _emit(f"Remaining: {remaining:.2f}/{max_budget}", {}, ctx)
        _emit(
            f"Regeneration: +{budget.config.regeneration_rate_per_hour}/hour", {}, ctx
        )

        if status["spent_by_operation"]:
            _emit("\nSpending breakdown:", {}, ctx)
            for op, cost in status["spent_by_operation"].items():
                _emit(f"  {op}: {cost:.2f}", {}, ctx)

    return 0


# =============================================================================
# Recognition
# =============================================================================


def _recognize(args: list[str], ctx: "InvocationContext | None") -> int:
    """Scan for ontological gaps."""
    from protocols.agentese.contexts.self_grow import RecognitionQuery
    from protocols.agentese.contexts.self_grow.recognize import cluster_errors_into_gaps

    resolver = _get_resolver()
    session = _get_session()

    # Check if we have sample errors (for demo)
    if "--demo" in args:
        from protocols.agentese.contexts.self_grow import GrowthRelevantError

        # Generate demo errors
        demo_errors = [
            GrowthRelevantError(
                error_id=str(i),
                timestamp=datetime.now(),
                trace_id=f"trace-{i}",
                error_type="PathNotFoundError",
                attempted_path="world.garden.bloom",
                context="world",
                holon="garden",
                aspect="bloom",
                observer_archetype=["poet", "gardener", "scholar"][i % 3],
                observer_name="demo",
            )
            for i in range(15)
        ]
        resolver._recognize._error_stream = demo_errors

    # Cluster errors into gaps
    gaps = cluster_errors_into_gaps(resolver._recognize._error_stream)
    session.last_gaps = gaps

    if RICH_AVAILABLE:
        if not gaps:
            console.print(
                Panel(
                    "[dim]No ontological gaps detected.[/]\n\n"
                    "Try [cyan]kg grow recognize --demo[/] to see sample gaps.",
                    title="Gap Recognition",
                    border_style="dim",
                )
            )
        else:
            table = Table(title="Recognized Gaps", show_header=True)
            table.add_column("#", style="dim", width=3)
            table.add_column("Handle", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Evidence", justify="right")
            table.add_column("Confidence", justify="right")

            for i, gap in enumerate(gaps[:10], 1):
                handle = f"{gap.context}.{gap.holon}"
                if gap.aspect:
                    handle += f".{gap.aspect}"
                conf_style = "green" if gap.confidence >= 0.7 else "yellow"
                table.add_row(
                    str(i),
                    handle,
                    gap.gap_type,
                    str(gap.evidence_count),
                    f"[{conf_style}]{gap.confidence:.2f}[/]",
                )

            console.print(table)
            console.print(
                f"\n[dim]Use [cyan]kg grow propose {gaps[0].context} {gaps[0].holon}[/] "
                "to create a proposal.[/]"
            )
    else:
        _emit(f"Found {len(gaps)} gaps:", {"count": len(gaps)}, ctx)
        for gap in gaps[:10]:
            _emit(
                f"  {gap.context}.{gap.holon} [{gap.gap_type}] "
                f"evidence={gap.evidence_count} confidence={gap.confidence:.2f}",
                {},
                ctx,
            )

    return 0


# =============================================================================
# Proposal
# =============================================================================


def _propose(args: list[str], ctx: "InvocationContext | None") -> int:
    """Create a proposal for a new holon."""
    from protocols.agentese.contexts.self_grow import GapRecognition, HolonProposal
    from protocols.agentese.contexts.self_grow.propose import generate_proposal_from_gap

    if len(args) < 2:
        _emit(
            "Usage: kg grow propose <context> <entity> [--why <justification>]", {}, ctx
        )
        _emit(
            "Example: kg grow propose world garden --why 'Agents need botanical exploration'",
            {},
            ctx,
        )
        return 1

    context = args[0]
    entity = args[1]

    # Parse optional justification
    why_exists = None
    if "--why" in args:
        why_idx = args.index("--why")
        if why_idx + 1 < len(args):
            why_exists = " ".join(args[why_idx + 1 :])

    # Check for existing gap
    session = _get_session()
    matching_gap = None
    for gap in session.last_gaps:
        if gap.context == context and gap.holon == entity:
            matching_gap = gap
            break

    if matching_gap is None:
        matching_gap = GapRecognition.create(context=context, holon=entity)

    # Generate proposal
    proposal = generate_proposal_from_gap(
        matching_gap,
        proposed_by="cli_user",
        why_exists=why_exists,
    )

    # Store in session
    session.proposals[proposal.proposal_id] = proposal

    # Persist to cortex
    async def _persist() -> None:
        cortex = await _get_cortex()
        await cortex.store_proposal(proposal, status="draft")

    try:
        _run_async(_persist())
    except Exception as e:
        # Non-fatal - proposal still in session
        if RICH_AVAILABLE:
            console.print(f"[dim yellow]Note: Could not persist to cortex: {e}[/]")

    if RICH_AVAILABLE:
        # Show proposal details
        tree = Tree(f"[bold cyan]{context}.{entity}[/]")
        tree.add(f"[dim]ID:[/] {proposal.proposal_id[:8]}...")
        tree.add(f"[dim]Hash:[/] {proposal.content_hash[:16]}...")

        why_branch = tree.add("[bold]Why This Exists[/]")
        why_branch.add(proposal.why_exists)

        aff_branch = tree.add("[bold]Affordances[/]")
        for archetype, verbs in proposal.affordances.items():
            aff_branch.add(f"[yellow]{archetype}[/]: {', '.join(verbs)}")

        if proposal.behaviors:
            beh_branch = tree.add("[bold]Behaviors[/]")
            for aspect, desc in proposal.behaviors.items():
                beh_branch.add(f"[cyan]{aspect}[/]: {desc}")

        console.print(Panel(tree, title="Proposal Created", border_style="green"))
        console.print(
            f"\n[dim]Next: [cyan]kg grow validate {proposal.proposal_id[:8]}[/][/]"
        )
    else:
        _emit(
            f"Created proposal: {proposal.proposal_id}",
            {"id": proposal.proposal_id},
            ctx,
        )
        _emit(f"Handle: {context}.{entity}", {}, ctx)
        _emit(f"Hash: {proposal.content_hash}", {}, ctx)

    return 0


# =============================================================================
# Validation
# =============================================================================


def _validate(args: list[str], ctx: "InvocationContext | None") -> int:
    """Validate a proposal against all gates."""
    from protocols.agentese.contexts.self_grow.validate import validate_proposal_sync

    session = _get_session()

    if not args:
        # Show available proposals
        if not session.proposals:
            _emit(
                "No proposals to validate. Create one with: kg grow propose <context> <entity>",
                {},
                ctx,
            )
            return 1

        _emit("Available proposals:", {}, ctx)
        for pid, p in session.proposals.items():
            _emit(f"  {pid[:8]}... -> {p.context}.{p.entity}", {}, ctx)
        return 0

    # Find proposal (check session first, then cortex)
    proposal_id = args[0]
    proposal = None
    for pid, p in session.proposals.items():
        if pid.startswith(proposal_id):
            proposal = p
            break

    # If not in session, try cortex
    if proposal is None:

        async def _fetch_from_cortex() -> Any:
            cortex = await _get_cortex()
            proposals = await cortex.list_proposals()
            for p in proposals:
                if p.proposal_id.startswith(proposal_id):
                    return p
            return None

        try:
            proposal = _run_async(_fetch_from_cortex())
        except Exception:
            pass  # Fall through to not found

    if proposal is None:
        _emit(f"Proposal not found: {proposal_id}", {"error": "not_found"}, ctx)
        _emit("Use 'kg grow list' to see available proposals.", {}, ctx)
        return 1

    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating...", total=None)

            result = validate_proposal_sync(proposal)

            progress.update(task, completed=True)

        # Show results with threshold context
        threshold = 0.70  # The required score for "high"
        high_count = sum(1 for s in result.scores.values() if s >= threshold)
        required_high = 5  # Need 5+ high scores to pass

        if result.passed:
            status = f"[bold green]PASSED[/] ({high_count}/{required_high} high scores)"
        else:
            status = (
                f"[bold red]FAILED[/] ({high_count}/{required_high} high scores needed)"
            )

        console.print(f"\nValidation: {status}")
        console.print(
            f"[dim]Overall: {result.overall_score:.2f} | Threshold: {threshold}[/]"
        )

        # Scores table with visual bars
        table = Table(title="Seven Gates", show_header=True, show_lines=False)
        table.add_column("Principle", style="cyan", width=14)
        table.add_column("Score", justify="center", width=12)
        table.add_column("Status", justify="center", width=10)
        table.add_column("Reason", no_wrap=False)

        for principle in [
            "tasteful",
            "curated",
            "ethical",
            "joy",
            "composable",
            "heterarchical",
            "generative",
        ]:
            score = result.scores.get(principle, 0.0)
            reason = result.reasoning.get(principle, "")

            # Visual score bar (10 chars)
            filled = int(score * 10)
            bar = "█" * filled + "░" * (10 - filled)

            if score >= 0.7:
                status_icon = "[green]✓ High[/]"
                bar_styled = f"[green]{bar}[/]"
            elif score >= 0.4:
                status_icon = "[yellow]○ Pass[/]"
                bar_styled = f"[yellow]{bar}[/]"
            else:
                status_icon = "[red]✗ Low[/]"
                bar_styled = f"[red]{bar}[/]"

            # Truncate reason smartly
            reason_short = reason[:50] + "..." if len(reason) > 50 else reason

            table.add_row(
                principle.capitalize(),
                f"{bar_styled} {score:.2f}",
                status_icon,
                reason_short,
            )

        console.print(table)

        # Law checks
        console.print("\n[bold]Law Checks:[/]")
        console.print(f"  Identity: {'✓' if result.law_checks.identity_holds else '✗'}")
        console.print(
            f"  Associativity: {'✓' if result.law_checks.associativity_holds else '✗'}"
        )
        if result.law_checks.errors:
            console.print(f"  [dim]Notes: {', '.join(result.law_checks.errors[:2])}[/]")

        # Abuse check
        console.print(f"\n[bold]Abuse Check:[/] {result.abuse_check.risk_level}")
        if result.abuse_check.concerns:
            for concern in result.abuse_check.concerns[:3]:
                console.print(f"  [yellow]⚠[/] {concern}")

        # Generate actionable suggestions based on low scores
        suggestions = list(result.suggestions) if result.suggestions else []

        # Add specific advice for low-scoring gates
        low_gates = [
            (p, result.scores.get(p, 0.0))
            for p in [
                "tasteful",
                "curated",
                "ethical",
                "joy",
                "composable",
                "heterarchical",
                "generative",
            ]
            if result.scores.get(p, 0.0) < 0.7
        ]

        gate_advice = {
            "tasteful": "Expand why_exists to 100+ chars explaining the holon's unique value",
            "curated": "Add archetype-specific affordances (gardener, scholar, architect)",
            "ethical": "Review for potential misuse vectors and add safeguards",
            "joy": "Include playful or delightful affordances like 'surprise' or 'celebrate'",
            "composable": "Add relations: composes_with, extends, or depends_on other holons",
            "heterarchical": "Ensure the holon doesn't create rigid hierarchies",
            "generative": "Add generative affordances like 'refine', 'define', or 'evolve'",
        }

        for gate, score in low_gates:
            if gate in gate_advice and gate_advice[gate] not in suggestions:
                suggestions.insert(0, f"[{gate}] {gate_advice[gate]}")

        if suggestions:
            console.print("\n[bold]How to Improve:[/]")
            for suggestion in suggestions[:5]:
                console.print(f"  → {suggestion}")

        # Show next step based on result
        if result.passed:
            console.print("\n[green]✓[/] Ready for germination!")
            console.print(
                f"[dim]Next: [cyan]kg grow germinate {proposal.proposal_id[:8]}[/][/]"
            )
        else:
            console.print("\n[yellow]![/] Fix the issues above and re-validate.")
            console.print(
                f'[dim]Re-create proposal: [cyan]kg grow propose {proposal.context} {proposal.entity} --why "<improved justification>"[/][/]'
            )

    else:
        result = validate_proposal_sync(proposal)
        status = "PASSED" if result.passed else "FAILED"
        _emit(
            f"Validation {status}: {result.overall_score:.2f}",
            {"passed": result.passed},
            ctx,
        )

    return 0


# =============================================================================
# Nursery
# =============================================================================


def _show_nursery(ctx: "InvocationContext | None") -> int:
    """Show nursery status with readiness indicators."""
    resolver = _get_resolver()
    nursery = resolver._nursery

    if nursery is None:
        _emit("Nursery not configured", {"error": "no_nursery"}, ctx)
        return 1

    active = nursery.active
    config = nursery._config

    if RICH_AVAILABLE:
        if not active:
            console.print(
                Panel(
                    "[dim]The nursery is empty.[/]\n\n"
                    "Germinate a proposal with: [cyan]kg grow germinate <proposal_id>[/]\n\n"
                    "[dim]Or try [cyan]kg grow demo[/] to see the full pipeline in action.[/]",
                    title="Nursery",
                    border_style="dim",
                )
            )
        else:
            table = Table(
                title=f"Nursery ({len(active)}/{config.max_capacity})",
                show_header=True,
                header_style="bold",
            )
            table.add_column("ID", style="dim", width=10)
            table.add_column("Handle", style="cyan")
            table.add_column("Usage Progress", justify="center", width=18)
            table.add_column("Success", justify="center", width=12)
            table.add_column("Age", justify="right", width=6)
            table.add_column("Status", width=20)

            for holon in active:
                handle = f"{holon.proposal.context}.{holon.proposal.entity}"
                germ_id = holon.germination_id[:8] + "..."

                # Usage progress bar toward promotion threshold
                usage_pct = min(
                    100, int(holon.usage_count / config.min_usage_for_promotion * 100)
                )
                usage_filled = usage_pct // 10
                usage_bar = "█" * usage_filled + "░" * (10 - usage_filled)
                usage_str = (
                    f"{usage_bar} {holon.usage_count}/{config.min_usage_for_promotion}"
                )

                # Success rate with color
                if holon.usage_count > 0:
                    success_rate = holon.success_rate
                    if success_rate >= config.min_success_rate_for_promotion:
                        success_str = f"[green]{success_rate:.0%}[/]"
                    elif success_rate >= config.min_success_rate_for_survival:
                        success_str = f"[yellow]{success_rate:.0%}[/]"
                    else:
                        success_str = f"[red]{success_rate:.0%}[/]"
                else:
                    success_str = "[dim]-[/]"

                age = f"{holon.age_days}d"

                # Status with actionable hint
                if holon.should_promote(config):
                    status = "[green]✓ Ready[/]"
                elif holon.should_prune(config):
                    status = "[red]✗ Failing[/]"
                elif holon.age_days > config.max_age_days * 0.7:
                    status = "[orange1]⚠ Aging[/]"
                else:
                    status = "[yellow]◐ Growing[/]"

                table.add_row(germ_id, handle, usage_str, success_str, age, status)

            console.print(table)

            # Show thresholds legend
            console.print("\n[bold]Thresholds:[/]")
            console.print(
                f"  [green]✓ Promote[/]: {config.min_usage_for_promotion}+ uses AND "
                f"{config.min_success_rate_for_promotion:.0%}+ success"
            )
            console.print(
                f"  [red]✗ Prune[/]: {config.max_age_days}+ days OR "
                f"<{config.min_success_rate_for_survival:.0%} success"
            )

            # Show actionable next steps
            ready_to_promote = nursery.get_ready_for_promotion()
            ready_to_prune = nursery.get_ready_for_pruning()

            if ready_to_promote:
                holon = ready_to_promote[0]
                console.print(
                    f"\n[green]Action:[/] Promote ready holon: "
                    f"[cyan]kg grow promote {holon.germination_id[:8]}[/]"
                )
            if ready_to_prune:
                console.print(
                    "\n[yellow]Action:[/] Prune failing holons: [cyan]kg grow prune[/]"
                )
    else:
        _emit(f"Nursery: {len(active)}/{config.max_capacity}", {}, ctx)
        for holon in active:
            status = "ready" if holon.should_promote(config) else "growing"
            _emit(
                f"  [{holon.germination_id[:8]}] {holon.proposal.context}.{holon.proposal.entity} "
                f"usage={holon.usage_count}/{config.min_usage_for_promotion} "
                f"success={holon.success_rate:.0%} status={status}",
                {},
                ctx,
            )

    return 0


def _germinate(args: list[str], ctx: "InvocationContext | None") -> int:
    """Add a proposal to the nursery."""
    from protocols.agentese.contexts.self_grow import ValidationResult
    from protocols.agentese.contexts.self_grow.germinate import generate_jit_source
    from protocols.agentese.contexts.self_grow.validate import validate_proposal_sync

    session = _get_session()
    resolver = _get_resolver()

    if not args:
        _emit("Usage: kg grow germinate <proposal_id>", {}, ctx)
        return 1

    # Find proposal (check session first, then cortex)
    proposal_id = args[0]
    proposal = None
    for pid, p in session.proposals.items():
        if pid.startswith(proposal_id):
            proposal = p
            break

    # If not in session, try cortex
    if proposal is None:

        async def _fetch_from_cortex() -> Any:
            cortex = await _get_cortex()
            proposals = await cortex.list_proposals()
            for p in proposals:
                if p.proposal_id.startswith(proposal_id):
                    return p
            return None

        try:
            proposal = _run_async(_fetch_from_cortex())
        except Exception:
            pass

    if proposal is None:
        _emit(f"Proposal not found: {proposal_id}", {"error": "not_found"}, ctx)
        _emit("Use 'kg grow list' to see available proposals.", {}, ctx)
        return 1

    # Validate first
    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Validating...", total=None)
            validation = validate_proposal_sync(proposal)
            progress.update(task, description="Generating JIT source...")
            jit_source = generate_jit_source(proposal)
            progress.update(task, completed=True)
    else:
        validation = validate_proposal_sync(proposal)
        jit_source = generate_jit_source(proposal)

    if not validation.passed:
        _emit(
            f"Validation failed: {validation.blockers}",
            {"error": "validation_failed"},
            ctx,
        )
        return 1

    # Add to nursery
    nursery = resolver._nursery
    try:
        holon = nursery.add(
            proposal=proposal,
            validation=validation,
            germinated_by="cli_user",
            jit_source=jit_source,
        )

        if RICH_AVAILABLE:
            console.print(
                Panel(
                    f"[bold green]Germinated![/]\n\n"
                    f"Handle: [cyan]{proposal.context}.{proposal.entity}[/]\n"
                    f"ID: {holon.germination_id[:8]}...\n"
                    f"JIT Source: {len(jit_source.splitlines())} lines\n\n"
                    f"[dim]The holon is now in the nursery, being tested experimentally.[/]",
                    title="Germination Complete",
                    border_style="green",
                )
            )
            console.print("\n[dim]Use [cyan]kg grow nursery[/] to track usage.[/]")
        else:
            _emit(
                f"Germinated: {holon.germination_id}", {"id": holon.germination_id}, ctx
            )

    except Exception as e:
        _emit(f"Germination failed: {e}", {"error": str(e)}, ctx)
        return 1

    return 0


# =============================================================================
# Wizard (Interactive Mode)
# =============================================================================


def _wizard(ctx: "InvocationContext | None") -> int:
    """Interactive proposal creation wizard."""
    if not RICH_AVAILABLE:
        _emit("Wizard requires rich library. Install with: pip install rich", {}, ctx)
        return 1

    _print_banner()
    console.print()

    # Step 1: Context
    console.print("[bold]Step 1: Choose Context[/]")
    console.print("  [cyan]world[/]   - External entities (house, garden, library)")
    console.print("  [cyan]self[/]    - Internal capabilities (memory, status)")
    console.print("  [cyan]concept[/] - Platonic forms (laws, dialectic)")
    console.print("  [cyan]void[/]    - Entropy sources (chaos, serendipity)")
    console.print("  [cyan]time[/]    - Temporal operations (trace, schedule)")
    console.print()

    context = Prompt.ask(
        "Context",
        choices=["world", "self", "concept", "void", "time"],
        default="world",
    )

    # Step 2: Entity name
    console.print("\n[bold]Step 2: Name Your Holon[/]")
    console.print("[dim]Use lowercase with underscores (e.g., flower_garden)[/]")

    entity = Prompt.ask("Entity name")
    if not entity or not entity.replace("_", "").isalnum():
        console.print("[red]Invalid entity name[/]")
        return 1

    # Step 3: Justification
    console.print("\n[bold]Step 3: Justify Its Existence[/]")
    console.print("[dim]Why does this holon need to exist? (Tasteful principle)[/]")

    why_exists = Prompt.ask("Justification")

    # Step 4: Affordances
    console.print("\n[bold]Step 4: Define Affordances[/]")
    console.print("[dim]What can observers do with this holon?[/]")

    default_affordances = ["manifest", "witness"]
    console.print(f"Default: {', '.join(default_affordances)}")

    extra = Prompt.ask("Additional affordances (comma-separated)", default="")
    affordances = default_affordances + [
        a.strip() for a in extra.split(",") if a.strip()
    ]

    # Create proposal
    from protocols.agentese.contexts.self_grow import GapRecognition, HolonProposal
    from protocols.agentese.contexts.self_grow.propose import generate_proposal_from_gap

    gap = GapRecognition.create(context=context, holon=entity)
    proposal = generate_proposal_from_gap(
        gap,
        proposed_by="cli_wizard",
        why_exists=why_exists,
        affordances={
            "default": affordances,
            "scholar": affordances + ["inspect"],
            "gardener": affordances + ["inspect", "refine"],
        },
    )

    session = _get_session()
    session.proposals[proposal.proposal_id] = proposal

    # Persist to cortex
    async def _persist() -> None:
        cortex = await _get_cortex()
        await cortex.store_proposal(proposal, status="draft")

    try:
        _run_async(_persist())
    except Exception as e:
        console.print(f"[dim yellow]Note: Could not persist to cortex: {e}[/]")

    console.print("\n")
    console.print(
        Panel(
            f"[bold green]Proposal Created![/]\n\n"
            f"Handle: [cyan]{context}.{entity}[/]\n"
            f"ID: {proposal.proposal_id[:8]}...\n"
            f"Affordances: {', '.join(affordances)}",
            title="Success",
            border_style="green",
        )
    )

    # Ask to validate
    if Confirm.ask("\nValidate this proposal now?", default=True):
        return _validate([proposal.proposal_id[:8]], ctx)

    return 0


# =============================================================================
# Demo
# =============================================================================


def _demo(ctx: "InvocationContext | None") -> int:
    """Run a demo of the full growth pipeline."""
    if not RICH_AVAILABLE:
        _emit("Demo requires rich library", {}, ctx)
        return 1

    _print_banner()
    console.print()
    console.print("[bold]Running Growth Pipeline Demo...[/]\n")

    from protocols.agentese.contexts.self_grow import (
        GapRecognition,
        GrowthRelevantError,
        ValidationResult,
    )
    from protocols.agentese.contexts.self_grow.germinate import generate_jit_source
    from protocols.agentese.contexts.self_grow.propose import generate_proposal_from_gap
    from protocols.agentese.contexts.self_grow.validate import validate_proposal_sync

    resolver = _get_resolver()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Step 1: Generate demo errors
        task = progress.add_task("Generating demo errors...", total=None)
        demo_errors = [
            GrowthRelevantError(
                error_id=str(i),
                timestamp=datetime.now(),
                trace_id=f"trace-{i}",
                error_type="PathNotFoundError",
                attempted_path="world.botanical_garden.explore",
                context="world",
                holon="botanical_garden",
                aspect="explore",
                observer_archetype=["poet", "gardener", "scholar", "architect"][i % 4],
                observer_name="demo",
            )
            for i in range(20)
        ]
        progress.update(task, description="Created 20 demo errors", completed=True)

        # Step 2: Cluster into gaps
        task = progress.add_task("Recognizing gaps...", total=None)
        from protocols.agentese.contexts.self_grow.recognize import (
            cluster_errors_into_gaps,
        )

        gaps = cluster_errors_into_gaps(demo_errors)
        progress.update(task, description=f"Found {len(gaps)} gap(s)", completed=True)

        # Step 3: Create proposal
        task = progress.add_task("Creating proposal...", total=None)
        gap = (
            gaps[0]
            if gaps
            else GapRecognition.create(context="world", holon="botanical_garden")
        )
        proposal = generate_proposal_from_gap(
            gap,
            proposed_by="demo",
            why_exists="Agents frequently need world.botanical_garden for exploring plant species and ecosystems.",
        )
        progress.update(
            task, description="Proposal: world.botanical_garden", completed=True
        )

        # Step 4: Validate
        task = progress.add_task("Validating (7 gates + laws + abuse)...", total=None)
        validation = validate_proposal_sync(proposal)
        status = "PASSED" if validation.passed else "FAILED"
        progress.update(
            task,
            description=f"Validation {status} ({validation.overall_score:.2f})",
            completed=True,
        )

        # Step 5: Generate JIT
        task = progress.add_task("Generating JIT source...", total=None)
        jit_source = generate_jit_source(proposal)
        progress.update(
            task,
            description=f"Generated {len(jit_source.splitlines())} lines",
            completed=True,
        )

        # Step 6: Add to nursery
        task = progress.add_task("Adding to nursery...", total=None)
        nursery = resolver._nursery
        if validation.passed:
            holon = nursery.add(
                proposal=proposal,
                validation=validation,
                germinated_by="demo",
                jit_source=jit_source,
            )
            progress.update(
                task,
                description=f"Germinated! ID: {holon.germination_id[:8]}",
                completed=True,
            )
        else:
            progress.update(
                task, description="Skipped (validation failed)", completed=True
            )

    console.print()

    # Show summary
    table = Table(title="Pipeline Summary", show_header=True)
    table.add_column("Step", style="cyan")
    table.add_column("Result")

    table.add_row("1. Recognize", f"{len(gaps)} gap(s) found")
    table.add_row("2. Propose", f"world.botanical_garden ({proposal.proposal_id[:8]})")
    table.add_row("3. Validate", f"{status} ({validation.overall_score:.2f})")
    table.add_row("4. JIT Compile", f"{len(jit_source.splitlines())} lines")
    table.add_row(
        "5. Germinate", f"Nursery: {nursery.count}/{nursery._config.max_capacity}"
    )

    console.print(table)

    # Show budget
    budget = resolver._budget
    console.print(
        f"\n[dim]Entropy spent: {budget.spent_this_run:.2f} | Remaining: {budget.remaining:.2f}[/]"
    )

    console.print("\n[bold]Demo complete![/] The holon is now in the nursery.")
    console.print(
        "[dim]In production, it would be tested until ready for promotion.[/]"
    )

    return 0


# =============================================================================
# List, Search, Show Commands (Cortex-backed)
# =============================================================================


def _list_proposals(args: list[str], ctx: "InvocationContext | None") -> int:
    """List all proposals from the cortex."""

    async def _do_list() -> list[Any]:
        cortex = await _get_cortex()

        # Parse filters
        status = None
        context = None
        for i, arg in enumerate(args):
            if arg == "--status" and i + 1 < len(args):
                status = args[i + 1]
            elif arg == "--context" and i + 1 < len(args):
                context = args[i + 1]

        return list(await cortex.list_proposals(status=status, context=context))

    try:
        proposals = _run_async(_do_list())
    except Exception as e:
        _emit(f"Error listing proposals: {e}", {"error": str(e)}, ctx)
        return 1

    if not proposals:
        if RICH_AVAILABLE:
            console.print(
                Panel(
                    "[dim]No proposals found.[/]\n\n"
                    "Create one with: [cyan]kg grow propose <context> <entity>[/]",
                    title="Proposals",
                    border_style="dim",
                )
            )
        else:
            _emit("No proposals found.", {}, ctx)
        return 0

    if RICH_AVAILABLE:
        table = Table(title=f"Proposals ({len(proposals)})", show_header=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Handle", style="cyan")
        table.add_column("Status", style="yellow")
        table.add_column("By", style="dim")
        table.add_column("Why (truncated)")

        for p in proposals[:20]:
            handle = f"{p.context}.{p.entity}"
            why_short = (
                (p.why_exists or "")[:40] + "..."
                if len(p.why_exists or "") > 40
                else (p.why_exists or "")
            )
            table.add_row(
                p.proposal_id[:8] + "...",
                handle,
                "draft",  # TODO: get status from row
                p.proposed_by or "-",
                why_short,
            )

        console.print(table)
        console.print("\n[dim]Use [cyan]kg grow show <id>[/] for details.[/]")
    else:
        _emit(f"Found {len(proposals)} proposals:", {}, ctx)
        for p in proposals[:20]:
            _emit(f"  {p.proposal_id[:8]}... {p.context}.{p.entity}", {}, ctx)

    return 0


def _search_proposals(args: list[str], ctx: "InvocationContext | None") -> int:
    """Semantic search for proposals."""
    if not args:
        _emit("Usage: kg grow search <query>", {}, ctx)
        _emit('Example: kg grow search "botanical exploration"', {}, ctx)
        return 1

    query = " ".join(args)

    async def _do_search() -> list[Any]:
        cortex = await _get_cortex()
        return list(await cortex.search_proposals(query, limit=10))

    try:
        proposals = _run_async(_do_search())
    except Exception as e:
        _emit(f"Error searching: {e}", {"error": str(e)}, ctx)
        return 1

    if not proposals:
        if RICH_AVAILABLE:
            console.print(f'[dim]No proposals matching "{query}"[/]')
        else:
            _emit(f"No proposals found for: {query}", {}, ctx)
        return 0

    if RICH_AVAILABLE:
        console.print(f'[bold]Search results for "[cyan]{query}[/]":[/]\n')

        for i, p in enumerate(proposals[:10], 1):
            handle = f"{p.context}.{p.entity}"
            why_short = (
                (p.why_exists or "")[:60] + "..."
                if len(p.why_exists or "") > 60
                else (p.why_exists or "")
            )
            console.print(f"  [cyan]{i}.[/] {handle}")
            console.print(f"     [dim]{why_short}[/]")
            console.print(f"     ID: {p.proposal_id[:8]}...")
            console.print()
    else:
        _emit(f"Found {len(proposals)} proposals:", {}, ctx)
        for p in proposals:
            _emit(f"  {p.proposal_id[:8]}... {p.context}.{p.entity}", {}, ctx)

    return 0


def _show_proposal(args: list[str], ctx: "InvocationContext | None") -> int:
    """Show detailed proposal information with optional validation scores."""
    from protocols.agentese.contexts.self_grow.validate import validate_proposal_sync

    if not args:
        _emit("Usage: kg grow show <proposal_id> [--scores]", {}, ctx)
        _emit("  --scores  Include validation score breakdown", {}, ctx)
        return 1

    # Parse args
    show_scores = "--scores" in args
    filtered_args = [a for a in args if a != "--scores"]
    proposal_id = filtered_args[0] if filtered_args else None

    if not proposal_id:
        _emit("Usage: kg grow show <proposal_id> [--scores]", {}, ctx)
        return 1

    async def _do_fetch() -> Any:
        cortex = await _get_cortex()
        proposals = await cortex.list_proposals()
        for p in proposals:
            if p.proposal_id.startswith(proposal_id):
                return p
        return None

    try:
        proposal = _run_async(_do_fetch())
    except Exception as e:
        _emit(f"Error fetching proposal: {e}", {"error": str(e)}, ctx)
        return 1

    if proposal is None:
        # Check session proposals too
        session = _get_session()
        for pid, p in session.proposals.items():
            if pid.startswith(proposal_id):
                proposal = p
                break

    if proposal is None:
        _emit(f"Proposal not found: {proposal_id}", {"error": "not_found"}, ctx)
        _emit("Use 'kg grow list' to see available proposals.", {}, ctx)
        return 1

    if RICH_AVAILABLE:
        # Build detailed view
        tree = Tree(f"[bold cyan]{proposal.context}.{proposal.entity}[/]")
        tree.add(f"[dim]ID:[/] {proposal.proposal_id}")
        tree.add(f"[dim]Hash:[/] {proposal.content_hash[:16]}...")
        tree.add(f"[dim]Version:[/] {proposal.version}")
        tree.add(f"[dim]By:[/] {proposal.proposed_by or 'unknown'}")
        if proposal.proposed_at:
            tree.add(f"[dim]At:[/] {proposal.proposed_at.isoformat()}")

        why_branch = tree.add("[bold]Why This Exists[/]")
        why_branch.add(proposal.why_exists or "(no justification)")

        if proposal.affordances:
            aff_branch = tree.add("[bold]Affordances[/]")
            for archetype, verbs in proposal.affordances.items():
                aff_branch.add(f"[yellow]{archetype}[/]: {', '.join(verbs)}")

        if proposal.behaviors:
            beh_branch = tree.add("[bold]Behaviors[/]")
            for aspect, desc in proposal.behaviors.items():
                beh_branch.add(f"[cyan]{aspect}[/]: {desc}")

        if proposal.relations:
            rel_branch = tree.add("[bold]Relations[/]")
            for rel_type, targets in proposal.relations.items():
                rel_branch.add(f"[magenta]{rel_type}[/]: {', '.join(targets)}")

        console.print(Panel(tree, title="Proposal Details", border_style="cyan"))

        # Show validation scores if requested
        if show_scores:
            console.print("\n[bold]Validation Scores:[/]")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Validating...", total=None)
                result = validate_proposal_sync(proposal)
                progress.update(task, completed=True)

            # Score summary
            threshold = 0.70
            high_count = sum(1 for s in result.scores.values() if s >= threshold)

            if result.passed:
                status = f"[green]PASSED[/] ({high_count}/5 high)"
            else:
                status = f"[red]FAILED[/] ({high_count}/5 needed)"

            console.print(f"  Status: {status} | Overall: {result.overall_score:.2f}")
            console.print()

            for principle in [
                "tasteful",
                "curated",
                "ethical",
                "joy",
                "composable",
                "heterarchical",
                "generative",
            ]:
                score = result.scores.get(principle, 0.0)
                filled = int(score * 10)
                bar = "█" * filled + "░" * (10 - filled)

                if score >= 0.7:
                    bar_styled = f"[green]{bar}[/]"
                    icon = "✓"
                elif score >= 0.4:
                    bar_styled = f"[yellow]{bar}[/]"
                    icon = "○"
                else:
                    bar_styled = f"[red]{bar}[/]"
                    icon = "✗"

                console.print(f"  {icon} {principle:<13} {bar_styled} {score:.2f}")

            # Next step suggestion
            if result.passed:
                console.print(
                    f"\n[green]Ready![/] [cyan]kg grow germinate {proposal.proposal_id[:8]}[/]"
                )
            else:
                console.print(
                    f"\n[yellow]Needs work.[/] [cyan]kg grow validate {proposal.proposal_id[:8]}[/]"
                )
        else:
            console.print(
                "\n[dim]Tip: Add [cyan]--scores[/] for validation breakdown[/]"
            )

        # Show next actions
        console.print("\n[dim]Actions:[/]")
        console.print(
            f"  [cyan]kg grow validate {proposal.proposal_id[:8]}[/]  Full validation"
        )
        console.print(
            f"  [cyan]kg grow germinate {proposal.proposal_id[:8]}[/]  Add to nursery"
        )
    else:
        _emit(f"Proposal: {proposal.context}.{proposal.entity}", {}, ctx)
        _emit(f"ID: {proposal.proposal_id}", {}, ctx)
        _emit(f"Why: {proposal.why_exists}", {}, ctx)

    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


def cmd_grow(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    self.grow: The Autopoietic Holon Generator.

    Grow your own AGENTESE holons through a governed pipeline:
    RECOGNIZE → PROPOSE → VALIDATE → GERMINATE → PROMOTE
    """
    if "--help" in args or "-h" in args:
        _print_help()
        return 0

    if not args:
        return _show_status(ctx)

    subcommand = args[0].lower()

    match subcommand:
        # Status commands
        case "status":
            return _show_status(ctx)
        case "budget":
            return _show_budget(ctx)

        # Pipeline commands
        case "recognize":
            return _recognize(args[1:], ctx)
        case "propose":
            return _propose(args[1:], ctx)
        case "validate":
            return _validate(args[1:], ctx)
        case "nursery":
            return _show_nursery(ctx)
        case "germinate":
            return _germinate(args[1:], ctx)

        # Cortex-backed commands (persistent storage)
        case "list":
            return _list_proposals(args[1:], ctx)
        case "search":
            return _search_proposals(args[1:], ctx)
        case "show":
            return _show_proposal(args[1:], ctx)

        # Interactive modes
        case "wizard":
            return _wizard(ctx)
        case "demo":
            return _demo(ctx)

        # Help
        case "help":
            _print_help()
            return 0

        case _:
            _emit(f"Unknown command: {subcommand}", {"error": subcommand}, ctx)
            _emit("Use 'kg grow --help' for available commands.", {}, ctx)
            return 1
