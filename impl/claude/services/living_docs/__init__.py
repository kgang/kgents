"""
Living Docs: Documentation as Projection

Treats documentation as a projection functor:
    LivingDocs : (Source x Spec) -> Observer -> Surface

The same source projects differently to different observers.
There is no canonical "documentation" - only projections.

See: spec/protocols/living-docs.md
"""

from .brain_adapter import (
    ASHCEvidence,
    HydrationBrainAdapter,
    ScoredTeachingResult,
    get_hydration_brain_adapter,
    reset_hydration_brain_adapter,
    set_hydration_brain_adapter,
)
from .crystallizer import (
    CrystallizationStats,
    TeachingCrystallizer,
    crystallize_all_teaching,
    crystallize_all_teaching_sync,
)
from .extractor import DocstringExtractor
from .generator import (
    GeneratedFile,
    GenerationManifest,
    ReferenceGenerator,
    generate_gotchas,
    generate_reference,
    generate_to_directory,
)
from .hydrator import (
    HydrationContext,
    Hydrator,
    hydrate_context,
    hydrate_context_with_ghosts,
    hydrate_from_brain,
    relevant_for_file,
)
from .linter import (
    DocstringLinter,
    LintResult,
    LintStats,
    get_changed_files,
    lint_directory,
    lint_file,
)
from .projector import LivingDocsProjector, project
from .spec_extractor import SpecExtractor
from .teaching import (
    TeachingCollector,
    TeachingQuery,
    TeachingResult,
    TeachingStats,
    VerificationResult,
    get_teaching_stats,
    query_teaching,
    verify_evidence,
)
from .types import (
    DocNode,
    LivingDocsObserver,
    Surface,
    TeachingMoment,
    Tier,
    Verification,
)

__all__ = [
    # Core Types
    "DocNode",
    "TeachingMoment",
    "LivingDocsObserver",
    "Surface",
    "Verification",
    "Tier",
    # Extractors
    "DocstringExtractor",
    "SpecExtractor",
    # Projector
    "LivingDocsProjector",
    "project",
    # Generator
    "ReferenceGenerator",
    "GeneratedFile",
    "GenerationManifest",
    "generate_reference",
    "generate_gotchas",
    "generate_to_directory",
    # Teaching Query (Phase 4)
    "TeachingCollector",
    "TeachingQuery",
    "TeachingResult",
    "TeachingStats",
    "VerificationResult",
    "query_teaching",
    "verify_evidence",
    "get_teaching_stats",
    # Hydration (Phase 6)
    "HydrationContext",
    "Hydrator",
    "hydrate_context",
    "hydrate_context_with_ghosts",
    "hydrate_from_brain",
    "relevant_for_file",
    # Brain Adapter (Metabolic Checkpoint 0.2)
    "HydrationBrainAdapter",
    "ScoredTeachingResult",
    "ASHCEvidence",
    "get_hydration_brain_adapter",
    "set_hydration_brain_adapter",
    "reset_hydration_brain_adapter",
    # Linter (Documentation Enforcement)
    "DocstringLinter",
    "LintResult",
    "LintStats",
    "lint_file",
    "lint_directory",
    "get_changed_files",
    # Crystallizer (Memory-First Docs)
    "CrystallizationStats",
    "TeachingCrystallizer",
    "crystallize_all_teaching",
    "crystallize_all_teaching_sync",
]
