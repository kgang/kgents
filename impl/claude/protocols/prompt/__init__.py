"""
Evergreen Prompt System: Self-Cultivating CLAUDE.md

NOTE: Core compilation infrastructure archived 2025-12-18.
See: protocols/_archived/evergreen-prompt-2025-12-18/README.md

Remaining exports:
- section_base: Section dataclass, NPhase enum, utilities
- soft_section: SoftSection for rigidity spectrum
- sources: FileSource, LLMSource for content retrieval
- rollback: RollbackRegistry for history
- monad: PromptM monad for composition
- fusion: Conflict detection and resolution
- metrics: Compilation metrics
- habits: Code/git analysis

AGENTESE paths (deprecated - use self.forest.* instead):
- concept.prompt.manifest: Render current CLAUDE.md
- concept.prompt.evolve: Propose prompt evolution
"""

# Wave 5: Fusion
from .fusion import (
    Conflict,
    ConflictDetector,
    ConflictType,
    FusionResult,
    PolicyResolver,
    PromptFusion,
    Resolution,
    SemanticSimilarity,
    SimilarityResult,
)

# Wave 5: Metrics
from .metrics import (
    CompilationMetric,
    FusionMetric,
    HabitMetric,
    MetricsEmitter,
    MetricType,
    SectionMetric,
)

# Wave 3+: Prompt Monad
from .monad import (
    PromptM,
    Source,
    join,
    lift_provenance,
    lift_trace,
    sequence,
    traverse,
)

# Wave 3+: Rollback
from .rollback import (
    Checkpoint,
    CheckpointId,
    CheckpointSummary,
    RollbackRegistry,
)
from .section_base import (
    NPhase,
    Section,
    SectionCompiler,
    extract_markdown_section,
    extract_principle_summary,
    extract_skills_from_directory,
    glob_source_paths,
    # Wave 2: File reading utilities
    read_file_safe,
)

# Wave 3+: Soft sections and rigidity spectrum
from .soft_section import (
    CrystallizationResult,
    MergeStrategy,
    SoftSection,
)

# Wave 3+: Sources
from .sources import (
    FileSource,
    LLMSource,
    MockLLMSource,
    SectionSource,
    SourcePriority,
    SourceResult,
)

__all__ = [
    # Sections (base types only - compilers archived)
    "NPhase",
    "Section",
    "SectionCompiler",
    # Wave 2: File reading utilities
    "read_file_safe",
    "extract_markdown_section",
    "extract_principle_summary",
    "extract_skills_from_directory",
    "glob_source_paths",
    # Wave 3+: Soft sections
    "SoftSection",
    "MergeStrategy",
    "CrystallizationResult",
    # Wave 3+: Sources
    "SectionSource",
    "SourceResult",
    "SourcePriority",
    "FileSource",
    "LLMSource",
    "MockLLMSource",
    # Wave 3+: Rollback
    "Checkpoint",
    "CheckpointId",
    "CheckpointSummary",
    "RollbackRegistry",
    # Wave 3+: Prompt Monad
    "Source",
    "PromptM",
    "sequence",
    "traverse",
    "join",
    "lift_trace",
    "lift_provenance",
    # Wave 5: Fusion
    "PromptFusion",
    "FusionResult",
    "SemanticSimilarity",
    "SimilarityResult",
    "ConflictDetector",
    "Conflict",
    "ConflictType",
    "PolicyResolver",
    "Resolution",
    # Wave 5: Metrics
    "MetricType",
    "CompilationMetric",
    "SectionMetric",
    "FusionMetric",
    "HabitMetric",
    "MetricsEmitter",
]
