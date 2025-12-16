"""
Section Sources: Abstraction for where section content comes from.

Sources form the foundation of the rigidity spectrum:
- FileSource: Read from static files (rigidity ~0.8-1.0)
- GitSource: Read from git history (rigidity ~0.6-0.8)
- LLMSource: Infer via LLM (rigidity ~0.0-0.3)
- MergedSource: Combine multiple sources (rigidity varies)

Each source can:
1. Attempt to fetch content
2. Report whether it succeeded
3. Record reasoning traces for transparency
"""

from .base import (
    FallbackSource,
    SectionSource,
    SourcePriority,
    SourceResult,
    TemplateSource,
)
from .file_source import FileSource, GlobFileSource
from .git_source import GitBranchSource, GitSource
from .llm_source import LLMSource, MockLLMSource

__all__ = [
    # Base types
    "SectionSource",
    "SourceResult",
    "SourcePriority",
    "TemplateSource",
    "FallbackSource",
    # File sources
    "FileSource",
    "GlobFileSource",
    # LLM sources
    "LLMSource",
    "MockLLMSource",
    # Git sources (Wave 3 Phase 2)
    "GitSource",
    "GitBranchSource",
]
