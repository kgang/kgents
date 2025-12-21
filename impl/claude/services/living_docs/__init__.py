"""
Living Docs: Documentation as Projection

Treats documentation as a projection functor:
    LivingDocs : (Source x Spec) -> Observer -> Surface

The same source projects differently to different observers.
There is no canonical "documentation" - only projections.

See: spec/protocols/living-docs.md
"""

from .extractor import DocstringExtractor
from .generator import (
    GeneratedFile,
    GenerationManifest,
    ReferenceGenerator,
    generate_gotchas,
    generate_reference,
    generate_to_directory,
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
]
