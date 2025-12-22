"""
Archaeology Service: Mining git history for priors.

Part of the ASHC (Agentic Self-Hosting Compiler) ecosystem.

This service extracts patterns from the kgents git history to:
1. Generate HistoryCrystals for Brain memory
2. Build priors for the ASHC metacompiler
3. Identify cleanup/archival candidates

AGENTESE Context: self.memory.archaeology.*

This service was recovered from git archaeology itself (commit fdd10657).
The archaeology of archaeology.

See: spec/protocols/repo-archaeology.md
"""

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
from .patterns import (
    ACTIVE_FEATURES,
    FEATURE_PATTERNS,
    FeaturePattern,
    get_patterns_by_category,
    get_patterns_by_status,
)
from .teaching_extractor import (
    CommitTeaching,
    CommitTeachingExtractor,
    extract_teachings_from_commits,
    generate_teaching_report,
)
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

# ASHC Adapter - import conditionally to handle missing ASHC dependencies gracefully
try:
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
    _ASHC_AVAILABLE = True
except ImportError:
    _ASHC_AVAILABLE = False

__all__ = [
    # Mining
    "Commit",
    "parse_git_log",
    "get_file_activity",
    "get_commit_count",
    "get_authors",
    # Patterns
    "ACTIVE_FEATURES",
    "FEATURE_PATTERNS",
    "FeaturePattern",
    "get_patterns_by_category",
    "get_patterns_by_status",
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
    # Teaching Extractor (Commit → TeachingMoment)
    "CommitTeaching",
    "CommitTeachingExtractor",
    "extract_teachings_from_commits",
    "generate_teaching_report",
]

# Conditionally add ASHC adapter exports
if _ASHC_AVAILABLE:
    __all__.extend([
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
    ])
