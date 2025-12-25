"""
ASHC-Chat Integration

Helper functions for detecting spec edits and triggering ASHC compilation in chat flow.

See: services/chat/ashc_bridge.py for the core bridge
See: protocols/api/chat.py for the API integration
"""

from __future__ import annotations

import re
from typing import Any

from services.chat.ashc_bridge import (
    ASHCBridge,
    ASHCChatOutput,
    is_spec_file,
)
from protocols.ashc.adaptive import ConfidenceTier


# =============================================================================
# Spec Edit Detection
# =============================================================================


def detect_spec_edit_in_message(message: str) -> tuple[str, str] | None:
    """
    Detect if a message contains a spec file edit.

    Looks for patterns like:
    - "Edit spec/agents/new.md: ..."
    - "Update spec/protocols/chat.md to add ..."
    - File mentions with spec/ paths

    Returns:
        (spec_path, proposed_changes) if detected, None otherwise
    """
    # Pattern 1: Explicit edit command
    edit_pattern = r"(?:edit|update|modify)\s+([^\s:]+spec/[^\s:]+\.md)(?:\s*:)?\s*(.+)"
    match = re.search(edit_pattern, message, re.IGNORECASE | re.DOTALL)
    if match:
        spec_path = match.group(1)
        changes = match.group(2).strip()
        return (spec_path, changes)

    # Pattern 2: File path followed by content block
    file_block_pattern = r"(spec/[^\s]+\.md)\s*```(?:markdown|md)?\s*(.+?)\s*```"
    match = re.search(file_block_pattern, message, re.DOTALL)
    if match:
        spec_path = match.group(1)
        content = match.group(2).strip()
        return (spec_path, content)

    return None


def infer_confidence_tier_from_message(message: str) -> ConfidenceTier:
    """
    Infer ASHC confidence tier from user message.

    Looks for signals like:
    - "trivial", "simple", "easy" → TRIVIALLY_EASY
    - "should work", "likely" → LIKELY_WORKS
    - "not sure", "uncertain", "experimental" → UNCERTAIN
    - "might break", "risky" → LIKELY_FAILS
    """
    message_lower = message.lower()

    if any(word in message_lower for word in ["trivial", "simple", "easy", "obvious"]):
        return ConfidenceTier.TRIVIALLY_EASY
    elif any(word in message_lower for word in ["should work", "likely", "probably"]):
        return ConfidenceTier.LIKELY_WORKS
    elif any(word in message_lower for word in ["uncertain", "not sure", "experimental", "try"]):
        return ConfidenceTier.UNCERTAIN
    elif any(word in message_lower for word in ["might break", "risky", "dangerous"]):
        return ConfidenceTier.LIKELY_FAILS
    else:
        return ConfidenceTier.LIKELY_WORKS  # Default


# =============================================================================
# ASHC Compilation Trigger
# =============================================================================


_ashc_bridge: ASHCBridge | None = None


def get_ashc_bridge() -> ASHCBridge:
    """Get or create singleton ASHC bridge."""
    global _ashc_bridge
    if _ashc_bridge is None:
        _ashc_bridge = ASHCBridge(enable_compilation=False)  # Disabled for now
    return _ashc_bridge


async def maybe_compile_spec(
    message: str,
    enable_compilation: bool = False,
) -> ASHCChatOutput | None:
    """
    Check if message contains spec edit and compile if so.

    Args:
        message: User message
        enable_compilation: If True, actually run ASHC (expensive). If False, skip.

    Returns:
        ASHCChatOutput if spec was detected and compiled, None otherwise
    """
    # Detect spec edit
    edit = detect_spec_edit_in_message(message)
    if edit is None:
        return None

    spec_path, proposed_changes = edit

    # Validate it's actually a spec file
    if not is_spec_file(spec_path):
        return None

    # Infer confidence tier
    tier = infer_confidence_tier_from_message(message)

    # Compile if enabled
    if not enable_compilation:
        return None

    bridge = get_ashc_bridge()
    output = await bridge.compile_spec(
        spec_path=spec_path,
        proposed_changes=proposed_changes,
        tier=tier,
        max_runs=10,  # Keep it fast for chat
    )

    return output


# =============================================================================
# Evidence Integration
# =============================================================================


def integrate_ashc_into_chat_evidence(
    chat_evidence: dict[str, Any],
    ashc_output: ASHCChatOutput,
) -> dict[str, Any]:
    """
    Merge ASHC evidence into chat evidence dict.

    Updates:
    - ashc_equivalence: equivalence score
    - ashc_data: full ASHC output dict (for UI display)
    - confidence: boosted if ASHC verification succeeds
    """
    # Merge ASHC equivalence score
    chat_evidence["ashc_equivalence"] = ashc_output.equivalence_score

    # Add full ASHC data for UI
    chat_evidence["ashc_data"] = ashc_output.to_dict()

    # Boost confidence if ASHC verified the spec
    if ashc_output.is_verified:
        chat_evidence["confidence"] = max(chat_evidence.get("confidence", 0.5), 0.9)

    return chat_evidence


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "detect_spec_edit_in_message",
    "infer_confidence_tier_from_message",
    "maybe_compile_spec",
    "integrate_ashc_into_chat_evidence",
    "get_ashc_bridge",
]
