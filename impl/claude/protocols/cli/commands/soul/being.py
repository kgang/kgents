"""
Being commands: history, propose, commit, crystallize, resume.

These manage cross-session identity and self-modification.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import TYPE_CHECKING, Any

from protocols.cli.shared import InvocationContext, OutputFormatter

if TYPE_CHECKING:
    pass


async def execute_history(ctx: InvocationContext, limit: int) -> int:
    """
    Handle 'soul history' command - view soul change history.

    Shows the archaeology of self: who was I before each change?
    """
    from agents.k.session import SoulSession

    output = OutputFormatter(ctx)
    session = await SoulSession.load()
    changes = session.who_was_i(limit)

    if ctx.json_mode:
        output.emit(json.dumps(changes, indent=2), {"changes": changes})
    else:
        if not changes:
            output.emit(
                "[SOUL:HISTORY] No changes yet. The soul is fresh.",
                {"changes": []},
            )
        else:
            lines = [
                "[SOUL:HISTORY] Who was I?",
                "",
            ]
            for change in changes:
                status_icon = {"committed": "+", "reverted": "-", "pending": "?"}
                icon = status_icon.get(change.get("status", ""), "*")
                lines.append(f"  [{icon}] {change['id']}: {change['description']}")
                if change.get("felt_sense"):
                    lines.append(f"      Felt: {change['felt_sense']}")
                lines.append(f"      ({change.get('aspect', 'unknown')})")
            output.emit("\n".join(lines), {"changes": changes})

    return 0


async def execute_propose(ctx: InvocationContext, description: str | None) -> int:
    """
    Handle 'soul propose' command - K-gent proposes a change.

    Per Heterarchical principle: K-gent proposes, user approves.
    """
    from agents.k.session import SoulSession

    output = OutputFormatter(ctx)

    if not description:
        output.emit(
            "[SOUL:PROPOSE] Error: No description provided\n"
            "Usage: kgents soul propose 'I want to be more concise'",
            {"error": "No description provided"},
        )
        return 1

    session = await SoulSession.load()
    change = await session.propose_change(description)

    if ctx.json_mode:
        output.emit(json.dumps(change.to_dict(), indent=2), change.to_dict())
    else:
        lines = [
            "[SOUL:PROPOSE] Change proposed",
            "",
            f"  ID: {change.id}",
            f"  Description: {change.description}",
            f"  Status: {change.status}",
            "",
            "To approve: kgents soul commit " + change.id,
        ]
        output.emit("\n".join(lines), change.to_dict())

    return 0


async def execute_commit(ctx: InvocationContext, change_id: str | None) -> int:
    """
    Handle 'soul commit' command - approve and commit a change.

    This is where self-modification actually happens.
    """
    from agents.k.session import SoulSession

    output = OutputFormatter(ctx)

    if not change_id:
        # Show pending changes
        session = await SoulSession.load()
        pending = session.pending_changes

        if not pending:
            output.emit(
                "[SOUL:COMMIT] No pending changes. Use 'soul propose' first.",
                {"pending": []},
            )
            return 1

        lines = [
            "[SOUL:COMMIT] Pending changes:",
            "",
        ]
        for change in pending:
            lines.append(f"  {change.id}: {change.description}")
        lines.append("")
        lines.append("Usage: kgents soul commit <id>")
        output.emit("\n".join(lines), {"pending": [c.to_dict() for c in pending]})
        return 1

    session = await SoulSession.load()
    success = await session.commit_change(change_id)

    if success:
        output.emit(
            f"[SOUL:COMMIT] Change {change_id} committed. The soul has changed.",
            {"committed": change_id, "success": True},
        )
        return 0
    else:
        output.emit(
            f"[SOUL:COMMIT] Change {change_id} not found.",
            {"error": f"Change {change_id} not found"},
        )
        return 1


async def execute_crystallize(ctx: InvocationContext, name: str | None) -> int:
    """
    Handle 'soul crystallize' command - save a checkpoint.

    Creates a restore point you can resume from later.
    """
    from agents.k.session import SoulSession

    output = OutputFormatter(ctx)

    if not name:
        name = f"crystal-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    session = await SoulSession.load()
    crystal = await session.crystallize(name)

    if ctx.json_mode:
        output.emit(json.dumps(crystal.to_dict(), indent=2), crystal.to_dict())
    else:
        lines = [
            "[SOUL:CRYSTALLIZE] Soul state saved",
            "",
            f"  Crystal ID: {crystal.id}",
            f"  Name: {crystal.name}",
            f"  Created: {crystal.created_at.isoformat()}",
            "",
            f"To resume: kgents soul resume {crystal.id}",
        ]
        output.emit("\n".join(lines), crystal.to_dict())

    return 0


async def execute_resume(ctx: InvocationContext, crystal_id: str | None) -> int:
    """
    Handle 'soul resume' command - resume from a crystal.

    Time travel to a previous soul state.
    """
    from agents.k.session import SoulPersistence, SoulSession

    output = OutputFormatter(ctx)

    if not crystal_id:
        # List available crystals
        persistence = SoulPersistence()
        crystals = persistence.list_crystals()

        if not crystals:
            output.emit(
                "[SOUL:RESUME] No crystals found. Use 'soul crystallize' first.",
                {"crystals": []},
            )
            return 1

        lines = [
            "[SOUL:RESUME] Available crystals:",
            "",
        ]
        for cid in crystals:
            crystal = persistence.load_crystal(cid)
            if crystal:
                lines.append(f"  {cid}: {crystal.name} ({crystal.created_at.date()})")
        lines.append("")
        lines.append("Usage: kgents soul resume <id>")
        output.emit("\n".join(lines), {"crystals": crystals})
        return 1

    session = await SoulSession.load()
    success = await session.resume_crystal(crystal_id)

    if success:
        output.emit(
            f"[SOUL:RESUME] Resumed from crystal {crystal_id}. The past is present.",
            {"resumed": crystal_id, "success": True},
        )
        return 0
    else:
        output.emit(
            f"[SOUL:RESUME] Crystal {crystal_id} not found.",
            {"error": f"Crystal {crystal_id} not found"},
        )
        return 1
