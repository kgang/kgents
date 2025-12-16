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
        ctx.emit(message, data)
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
    """Show comprehensive grow status."""
    from protocols.agentese.contexts.self_grow import GrowthBudget, NurseryConfig

    resolver = _get_resolver()
    budget = resolver._budget
    nursery = resolver._nursery

    if RICH_AVAILABLE:
        # Budget Panel
        budget_pct = int(budget.remaining / budget.config.max_entropy_per_run * 100)
        budget_bar = "█" * (budget_pct // 5) + "░" * (20 - budget_pct // 5)

        budget_text = Text()
        budget_text.append(f"Entropy: [{budget_bar}] {budget_pct}%\n", style="cyan")
        budget_text.append(
            f"Remaining: {budget.remaining:.2f} / {budget.config.max_entropy_per_run}\n"
        )
        budget_text.append(f"Spent this run: {budget.spent_this_run:.2f}\n")
        if budget.spent_by_operation:
            budget_text.append("Breakdown: ")
            for op, cost in budget.spent_by_operation.items():
                budget_text.append(f"{op}={cost:.2f} ", style="dim")

        console.print(
            Panel(budget_text, title="[bold]Entropy Budget[/]", border_style="green")
        )

        # Nursery Panel
        if nursery:
            active = nursery.active
            config = nursery._config

            nursery_text = Text()
            nursery_text.append(
                f"Capacity: {len(active)}/{config.max_capacity}\n", style="yellow"
            )
            nursery_text.append(
                f"Ready for promotion: {len(nursery.get_ready_for_promotion())}\n"
            )
            nursery_text.append(
                f"Ready for pruning: {len(nursery.get_ready_for_pruning())}\n"
            )

            if active:
                nursery_text.append("\nGerminating:\n", style="bold")
                for holon in active[:5]:
                    status = "ready" if holon.should_promote(config) else "growing"
                    nursery_text.append(
                        f"  {holon.proposal.context}.{holon.proposal.entity} "
                        f"[{status}] usage={holon.usage_count}\n"
                    )

            console.print(
                Panel(nursery_text, title="[bold]Nursery[/]", border_style="yellow")
            )

        # Costs Table
        costs_table = Table(title="Operation Costs", show_header=True)
        costs_table.add_column("Operation", style="cyan")
        costs_table.add_column("Cost", justify="right")
        costs_table.add_column("Affordable?", justify="center")

        for op, cost in [
            ("recognize", budget.config.recognize_cost),
            ("propose", budget.config.propose_cost),
            ("validate", budget.config.validate_cost),
            ("germinate", budget.config.germinate_cost),
            ("promote", budget.config.promote_cost),
            ("prune", budget.config.prune_cost),
        ]:
            affordable = "✓" if budget.can_afford(op) else "✗"
            style = "green" if budget.can_afford(op) else "red"
            costs_table.add_row(op, f"{cost:.2f}", affordable, style=style)

        console.print(costs_table)

    else:
        # Plain text fallback
        print("\n=== Entropy Budget ===")
        print(
            f"Remaining: {budget.remaining:.2f} / {budget.config.max_entropy_per_run}"
        )
        print(f"Spent: {budget.spent_this_run:.2f}")

        if nursery:
            print("\n=== Nursery ===")
            print(f"Active: {len(nursery.active)}/{nursery._config.max_capacity}")

    return 0


def _show_budget(ctx: "InvocationContext | None") -> int:
    """Show entropy budget details."""
    resolver = _get_resolver()
    budget = resolver._budget

    status = budget.status()
    _emit(f"Budget: {status['percent']}%", status, ctx)
    _emit(f"Remaining: {status['remaining']:.2f}/{status['max']}", {}, ctx)

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

    # Find proposal
    proposal_id = args[0]
    proposal = None
    for pid, p in session.proposals.items():
        if pid.startswith(proposal_id):
            proposal = p
            break

    if proposal is None:
        _emit(f"Proposal not found: {proposal_id}", {"error": "not_found"}, ctx)
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

        # Show results
        status = "[bold green]PASSED[/]" if result.passed else "[bold red]FAILED[/]"
        console.print(f"\nValidation: {status} (score: {result.overall_score:.2f})")

        # Scores table
        table = Table(title="Seven Gates", show_header=True)
        table.add_column("Principle", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Reason")

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
            reason = result.reasoning.get(principle, "")[:40]

            if score >= 0.7:
                status_icon = "[green]✓ High[/]"
            elif score >= 0.4:
                status_icon = "[yellow]○ Pass[/]"
            else:
                status_icon = "[red]✗ Fail[/]"

            table.add_row(principle.capitalize(), f"{score:.2f}", status_icon, reason)

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

        # Suggestions
        if result.suggestions:
            console.print("\n[bold]Suggestions:[/]")
            for suggestion in result.suggestions[:3]:
                console.print(f"  → {suggestion}")

        if result.passed:
            console.print(
                f"\n[dim]Next: [cyan]kg grow germinate {proposal.proposal_id[:8]}[/][/]"
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
    """Show nursery status."""
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
                    "Germinate a proposal with: [cyan]kg grow germinate <proposal_id>[/]",
                    title="Nursery",
                    border_style="dim",
                )
            )
        else:
            table = Table(
                title=f"Nursery ({len(active)}/{config.max_capacity})", show_header=True
            )
            table.add_column("Handle", style="cyan")
            table.add_column("Usage", justify="right")
            table.add_column("Success", justify="right")
            table.add_column("Age", justify="right")
            table.add_column("Status")

            for holon in active:
                handle = f"{holon.proposal.context}.{holon.proposal.entity}"
                usage = str(holon.usage_count)
                success = f"{holon.success_rate:.0%}" if holon.usage_count > 0 else "-"
                age = f"{holon.age_days}d"

                if holon.should_promote(config):
                    status = "[green]Ready to promote[/]"
                elif holon.should_prune(config):
                    status = "[red]Ready to prune[/]"
                else:
                    status = "[yellow]Growing[/]"

                table.add_row(handle, usage, success, age, status)

            console.print(table)

            # Show thresholds
            console.print(
                f"\n[dim]Promotion: {config.min_usage_for_promotion} uses, {config.min_success_rate_for_promotion:.0%} success[/]"
            )
            console.print(
                f"[dim]Prune after: {config.max_age_days} days or <{config.min_success_rate_for_survival:.0%} success[/]"
            )
    else:
        _emit(f"Nursery: {len(active)}/{config.max_capacity}", {}, ctx)
        for holon in active:
            _emit(
                f"  {holon.proposal.context}.{holon.proposal.entity} "
                f"usage={holon.usage_count} success={holon.success_rate:.0%}",
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

    # Find proposal
    proposal_id = args[0]
    proposal = None
    for pid, p in session.proposals.items():
        if pid.startswith(proposal_id):
            proposal = p
            break

    if proposal is None:
        _emit(f"Proposal not found: {proposal_id}", {"error": "not_found"}, ctx)
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

        return await cortex.list_proposals(status=status, context=context)

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
        return await cortex.search_proposals(query, limit=10)

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
    """Show detailed proposal information."""
    if not args:
        _emit("Usage: kg grow show <proposal_id>", {}, ctx)
        return 1

    proposal_id = args[0]

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
        return 1

    if RICH_AVAILABLE:
        # Build detailed view
        tree = Tree(f"[bold cyan]{proposal.context}.{proposal.entity}[/]")
        tree.add(f"[dim]ID:[/] {proposal.proposal_id}")
        tree.add(f"[dim]Hash:[/] {proposal.content_hash}")
        tree.add(f"[dim]Version:[/] {proposal.version}")
        tree.add(f"[dim]By:[/] {proposal.proposed_by}")
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

        # Show spec markdown
        console.print("\n[bold]Generated Spec:[/]")
        console.print(Panel(proposal.to_markdown()[:500] + "...", border_style="dim"))
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
