"""
Experiment Service: Evidence-Gathering with Bayesian Stopping.

Enables running experiments to gather empirical evidence about:
- Code generation quality (via VoidHarness)
- Parser robustness (via parsing strategies)
- Category law satisfaction (via probes)

Philosophy:
    "The proof IS the decision. The mark IS the witness."

    Experiments gather evidence, emit marks for witnessing,
    and use Bayesian stopping to avoid wasteful over-testing.

Heritage: Phase 3 of Claude Code CLI Integration Strategy
See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md
"""

from .bayesian import BayesianStoppingModel
from .runner import ExperimentRunner
from .store import ExperimentStore
from .types import (
    EvidenceBundle,
    Experiment,
    ExperimentConfig,
    ExperimentStatus,
    ExperimentType,
    GenerateConfig,
    LawsConfig,
    ParseConfig,
    Trial,
)

__all__ = [
    # Core types
    "Experiment",
    "ExperimentConfig",
    "ExperimentType",
    "ExperimentStatus",
    "Trial",
    "EvidenceBundle",
    # Config types
    "GenerateConfig",
    "ParseConfig",
    "LawsConfig",
    # Logic
    "BayesianStoppingModel",
    "ExperimentRunner",
    "ExperimentStore",
]
