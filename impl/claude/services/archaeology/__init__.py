"""
Archaeology Service: Mining git history for priors.

Part of the ASHC (Agentic Self-Hosting Compiler) ecosystem.

This service extracts patterns from the kgents git history to:
1. Generate HistoryCrystals for Brain memory
2. Build priors for the ASHC metacompiler
3. Identify cleanup/archival candidates

AGENTESE Context: self.memory.archaeology.*

See: spec/protocols/repo-archaeology.md
"""

from .ashc_adapter import (
    ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT,
    PriorConversionResult,
    create_seeded_learner,
    generate_priors_report,
    prior_to_edge,
    prior_to_nudge,
    seed_graph_with_priors,
    seed_learner_with_archaeology,
    spec_pattern_to_edge,
    spec_pattern_to_nudge,
)
from .classifier import (
    FeatureStatus,
    FeatureTrajectory,
    classify_all_features,
    classify_feature,
    generate_report,
)
from .crystals import (
    HistoryCrystal,
    generate_all_crystals,
    generate_crystal_report,
    generate_history_crystal,
    store_crystals_in_brain,
)
from .mining import Commit, get_authors, get_commit_count, get_file_activity, parse_git_log
from .patterns import FEATURE_PATTERNS, FeaturePattern, get_patterns_by_category
from .priors import (
    CausalPrior,
    EvolutionPhase,
    EvolutionTrace,
    SpecPattern,
    extract_causal_priors,
    extract_evolution_traces,
    extract_spec_patterns,
    generate_prior_report,
)

__all__ = [
    # Mining
    "Commit",
    "parse_git_log",
    "get_file_activity",
    "get_commit_count",
    "get_authors",
    # Patterns
    "FEATURE_PATTERNS",
    "FeaturePattern",
    "get_patterns_by_category",
    # Classification
    "FeatureStatus",
    "FeatureTrajectory",
    "classify_feature",
    "classify_all_features",
    "generate_report",
    # Priors (for ASHC)
    "EvolutionPhase",
    "SpecPattern",
    "EvolutionTrace",
    "CausalPrior",
    "extract_spec_patterns",
    "extract_evolution_traces",
    "extract_causal_priors",
    "generate_prior_report",
    # Crystals (for Brain)
    "HistoryCrystal",
    "generate_history_crystal",
    "generate_all_crystals",
    "store_crystals_in_brain",
    "generate_crystal_report",
    # ASHC Adapter
    "ARCHAEOLOGICAL_CONFIDENCE_DISCOUNT",
    "PriorConversionResult",
    "prior_to_nudge",
    "prior_to_edge",
    "spec_pattern_to_nudge",
    "spec_pattern_to_edge",
    "seed_graph_with_priors",
    "seed_learner_with_archaeology",
    "create_seeded_learner",
    "generate_priors_report",
]
