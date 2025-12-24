"""
Probe Service: Fast categorical law checks and health probes.

"The laws hold, or they don't. No middle ground."

This service implements Phase 4 of the Claude Code CLI integration strategy,
providing quick categorical law verification and Crown Jewel health checks.

Philosophy:
    Probes are FAST - no LLM calls for basic law verification.
    Probes only emit witness marks on FAILURE - keep them cheap.
    Exit code 0 = pass, 1 = fail (for CI integration).

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md §Phase 4
"""

from .budget import BudgetProbe
from .health import HealthProbe
from .laws import AssociativityProbe, CoherenceProbe, IdentityProbe
from .types import HealthStatus, ProbeResult, ProbeStatus, ProbeType

__all__ = [
    # Types
    "ProbeResult",
    "ProbeStatus",
    "ProbeType",
    "HealthStatus",
    # Law probes
    "IdentityProbe",
    "AssociativityProbe",
    "CoherenceProbe",
    # Health probes
    "HealthProbe",
    # Budget probes
    "BudgetProbe",
]
