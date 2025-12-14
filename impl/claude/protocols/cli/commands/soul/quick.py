"""
Quick commands: vibe, drift, tense.

These provide instant insight into the soul's current state
without requiring a dialogue turn.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from protocols.cli.shared import InvocationContext, OutputFormatter

if TYPE_CHECKING:
    pass


async def execute_vibe(ctx: InvocationContext, soul: Any) -> int:
    """
    Handle 'soul vibe' command - one-liner eigenvector summary.

    Shows personality coordinates with emoji indicators.

    Example output:
        ✂️ Minimal (0.15) | 🔬 Abstract (0.92) | 🙏 Sacred (0.78) |
        🌲 Peer (0.88) | 🌱 Generative (0.90) | 🎭 Playful (0.75)
    """
    output = OutputFormatter(ctx)
    eigenvectors = soul.eigenvectors

    # Emoji mapping for each eigenvector
    emoji_map = {
        "aesthetic": ("✂️", "Minimal", "Baroque"),
        "categorical": ("🔬", "Concrete", "Abstract"),
        "gratitude": ("🙏", "Util", "Sacred"),
        "heterarchy": ("🌲", "Hierarchy", "Peer"),
        "generativity": ("🌱", "Docs", "Gen"),
        "joy": ("🎭", "Austere", "Playful"),
    }

    vibe_parts = []
    for eigen in eigenvectors.all_eigenvectors():
        name = eigen.name.lower()
        emoji, low, high = emoji_map.get(name, ("•", "Low", "High"))

        # Pick label based on value
        if eigen.value < 0.4:
            label = low
        elif eigen.value > 0.6:
            label = high
        else:
            label = "Balanced"

        vibe_parts.append(f"{emoji} {label} ({eigen.value:.2f})")

    vibe_string = " | ".join(vibe_parts)

    semantic = {
        "command": "vibe",
        "eigenvectors": eigenvectors.to_dict(),
        "vibe_string": vibe_string,
    }

    if ctx.json_mode:
        output.emit(json.dumps(semantic, indent=2), semantic)
    else:
        output.emit(f"[SOUL:VIBE] {vibe_string}", semantic)

    return 0


async def execute_drift(ctx: InvocationContext, soul: Any) -> int:
    """
    Handle 'soul drift' command - compare eigenvectors vs previous session.

    Shows changes since last session using SoulSession.who_was_i().

    Example output:
        Since yesterday: Joy +0.02, Aesthetic -0.01. You're loosening up.
    """
    from agents.k.session import SoulSession

    output = OutputFormatter(ctx)
    session = await SoulSession.load()
    changes = session.who_was_i(limit=5)
    current = soul.eigenvectors.to_dict()

    # If no changes, show current state with note
    if not changes:
        semantic = {
            "command": "drift",
            "current": current,
            "changes": [],
            "message": "No historical changes yet. The soul is fresh.",
        }
        if ctx.json_mode:
            output.emit(json.dumps(semantic, indent=2), semantic)
        else:
            output.emit(
                "[SOUL:DRIFT] No drift detected yet. The soul is fresh.",
                semantic,
            )
        return 0

    # Try to find eigenvector changes in history
    drift_messages = []
    total_drift = 0.0

    for change in changes:
        if "eigenvector" in change.get("aspect", "").lower():
            desc = change.get("description", "")
            drift_messages.append(f"• {desc}")
            # Extract any delta values mentioned
            if "+" in desc or "-" in desc:
                total_drift += 0.01  # Approximate

    # Generate a summary message based on changes
    if drift_messages:
        summary = "Recent drifts:\n" + "\n".join(drift_messages[:3])
    else:
        # No eigenvector-specific changes, give a poetic summary
        latest = changes[0] if changes else {}
        felt_sense = latest.get("felt_sense") or "steady"
        summary = f"Soul feels {felt_sense}. No major coordinate shifts."

    semantic = {
        "command": "drift",
        "current": current,
        "changes": changes[:5],
        "summary": summary,
    }

    if ctx.json_mode:
        output.emit(json.dumps(semantic, indent=2), semantic)
    else:
        output.emit(f"[SOUL:DRIFT] {summary}", semantic)

    return 0


async def execute_tense(ctx: InvocationContext, soul: Any) -> int:
    """
    Handle 'soul tense' command - surface current eigenvector tensions.

    Identifies pairs of eigenvectors that create productive tension.

    Example output:
        Tensions detected:
        ⚡ Minimal (0.15) vs Abstract (0.92): How to be both minimal AND abstract?
        ⚡ Sacred (0.78) vs Generative (0.90): Generation without utilitarian reduction?
    """
    output = OutputFormatter(ctx)
    eigenvectors = soul.eigenvectors

    # Define tension pairs and their descriptions
    tension_pairs = [
        ("aesthetic", "categorical", "How to be both minimal AND abstract?"),
        ("gratitude", "generativity", "Generation without utilitarian reduction?"),
        ("heterarchy", "aesthetic", "Peer coordination while keeping things minimal?"),
        ("joy", "categorical", "Playfulness in abstract thinking?"),
    ]

    tensions = []
    for e1, e2, question in tension_pairs:
        v1 = getattr(eigenvectors, e1).value
        v2 = getattr(eigenvectors, e2).value

        # Tension is high when both are extreme (away from 0.5)
        extremity1 = abs(v1 - 0.5)
        extremity2 = abs(v2 - 0.5)
        tension_score = extremity1 * extremity2

        if tension_score > 0.1:  # Threshold for "notable" tension
            tensions.append(
                {
                    "pair": (e1, e2),
                    "values": (v1, v2),
                    "question": question,
                    "score": tension_score,
                }
            )

    # Sort by tension score
    tensions.sort(key=lambda t: t["score"], reverse=True)

    semantic = {
        "command": "tense",
        "tensions": tensions,
        "eigenvectors": eigenvectors.to_dict(),
    }

    if ctx.json_mode:
        output.emit(json.dumps(semantic, indent=2), semantic)
    else:
        if tensions:
            lines = ["[SOUL:TENSE] Tensions detected:", ""]
            for t in tensions[:3]:
                e1, e2 = t["pair"]
                v1, v2 = t["values"]
                lines.append(f"  ⚡ {e1.title()} ({v1:.2f}) vs {e2.title()} ({v2:.2f})")
                lines.append(f"     {t['question']}")
                lines.append("")
            output.emit("\n".join(lines), semantic)
        else:
            output.emit(
                "[SOUL:TENSE] No significant tensions detected. Eigenvectors are balanced.",
                semantic,
            )

    return 0
