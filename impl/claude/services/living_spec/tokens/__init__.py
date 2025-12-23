"""
Living Spec Tokens: Seven semantic token types.

Tokens are the atomic unit of interactive interface. Each token:
1. Has a type identifier
2. Has a span in source text
3. Provides observer-dependent affordances
4. Can be serialized for wire transfer

The seven token types:
1. AGENTESE_PATH — Navigable AGENTESE paths (`world.town.citizen`)
2. TASK_CHECKBOX — Toggleable checkboxes (`- [ ] Task`)
3. PORTAL — Expandable hyperedges (inline document embedding)
4. CODE_BLOCK — Executable/editable code blocks
5. IMAGE — Multimodal image references
6. PRINCIPLE_REF — References to principles (AD-009)
7. REQUIREMENT_REF — References to requirements (7.1, 7.4)
"""

from .base import BaseSpecToken, SpecToken
from .portal import PortalSpecToken, PortalState

# Token type constants
SPEC_TOKEN_TYPES = frozenset(
    {
        "agentese_path",
        "task_checkbox",
        "portal",
        "code_block",
        "image",
        "principle_ref",
        "requirement_ref",
    }
)

__all__ = [
    # Base
    "SpecToken",
    "BaseSpecToken",
    # Portal
    "PortalSpecToken",
    "PortalState",
    # Constants
    "SPEC_TOKEN_TYPES",
]
