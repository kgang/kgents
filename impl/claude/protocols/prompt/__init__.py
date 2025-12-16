"""
Evergreen Prompt System: Self-Cultivating CLAUDE.md

The prompt that reads itself is the prompt that writes itself.

This package provides:
- PROMPT_POLYNOMIAL: State machine for prompt lifecycle
- PromptCompiler: Compile sections into final CLAUDE.md
- Section compilers: Compile individual sections from sources
- Evolution protocol: Propose, validate, approve changes

Wave 3+ additions (Reformation):
- SoftSection: Sections with rigidity spectrum (0.0-1.0)
- Sources: FileSource, LLMSource for content retrieval
- RollbackRegistry: Full history with instant rollback
- Reasoning traces: Transparency for all inference

AGENTESE paths:
- concept.prompt.manifest: Render current CLAUDE.md
- concept.prompt.evolve: Propose prompt evolution
- concept.prompt.validate: Run category law checks
- concept.prompt.compile: Force recompilation

See: spec/protocols/evergreen-prompt-system.md
"""

from .compiler import CompilationContext, CompiledPrompt, PromptCompiler

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
from .polynomial import (
    PROMPT_POLYNOMIAL,
    PromptInput,
    PromptOutput,
    PromptState,
)

# Wave 3+: Rollback
from .rollback import (
    Checkpoint,
    CheckpointId,
    CheckpointSummary,
    RollbackRegistry,
)
from .section_base import (
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
    # State machine
    "PromptState",
    "PromptInput",
    "PromptOutput",
    "PROMPT_POLYNOMIAL",
    # Compilation
    "PromptCompiler",
    "CompilationContext",
    "CompiledPrompt",
    # Sections
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
