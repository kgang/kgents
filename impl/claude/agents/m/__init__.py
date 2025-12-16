"""
M-gents: Memory Agents for intelligent recall.

This package provides associative memory on top of D-gent persistence.

New Architecture (data-architecture-rewrite):
- MgentProtocol: 7 core methods (remember, recall, forget, cherish, consolidate, wake, status)
- Memory: Frozen dataclass for all memories (with lifecycle, resolution, relevance)
- AssociativeMemory: Embedding-based similarity search
- Lifecycle: ACTIVE -> DORMANT -> DREAMING -> COMPOSTING
- ConsolidationEngine: Background memory processing ("sleep" cycles)
- SoulMemory: K-gent identity continuity (beliefs, patterns, context, seeds)

Integration:
- Builds ON D-gent (every Memory references a Datum)
- DataBus: Reactive updates when data changes
- BusListener: Auto-indexing of new data

Legacy Support:
- PheromoneField/Stigmergy: Kept for K-gent coordination
"""

# New Architecture
from .memory import Lifecycle, Memory, simple_embedding
from .protocol import (
    ConsolidationReport,
    ExtendedMgentProtocol,
    MemoryStatus,
    MgentProtocol,
    RecallResult,
)
from .associative import AssociativeMemory, HashEmbedder
from .lifecycle import (
    LifecycleEvent,
    LifecycleManager,
    RelevancePolicy,
    ResolutionPolicy,
    TimeoutPolicy,
)
from .consolidation_engine import ConsolidationConfig, ConsolidationEngine
from .bus_listener import BusEventHandler, MgentBusListener
from .soul_memory import MemoryCategory, SoulMemory, create_soul_memory

# Legacy - Stigmergy (kept for K-gent)
from .stigmergy import (
    EnhancedStigmergicAgent,
    PheromoneField,
    SenseResult,
    SimpleConceptSpace,
    StigmergicAgent,
    Trace,
    create_ant_colony_optimization,
)

# Legacy stubs (DEPRECATED - for backward compatibility only)
from .legacy import (
    ActionHistory,
    AssociativeWebMemory,
    BudgetedMemory,
    Cue,
    DgentBackedHolographicMemory,
    HolographicMemory,
    ProspectiveAgent,
    RecollectionAgent,
    ResolutionBudget,
    Situation,
    TieredMemory,
    create_budgeted_memory,
    create_mock_bank,
)

# Importers
from .importers import (
    FrontmatterData,
    ImportProgress,
    MarkdownEngram,
    MarkdownImporter,
    ObsidianVaultParser,
    WikiLink,
    create_importer_with_best_embedder,
    create_lgent_embedder,
    extract_code_blocks,
    extract_frontmatter,
    extract_headings,
    extract_tags,
    extract_wikilinks,
    generate_concept_id,
    parse_markdown,
    strip_markdown_formatting,
)

__all__ = [
    # Core Types
    "Memory",
    "Lifecycle",
    "simple_embedding",
    # Protocol
    "MgentProtocol",
    "ExtendedMgentProtocol",
    "RecallResult",
    "ConsolidationReport",
    "MemoryStatus",
    # Associative Memory
    "AssociativeMemory",
    "HashEmbedder",
    # Lifecycle
    "LifecycleManager",
    "TimeoutPolicy",
    "RelevancePolicy",
    "ResolutionPolicy",
    "LifecycleEvent",
    # Consolidation
    "ConsolidationEngine",
    "ConsolidationConfig",
    # Bus Integration
    "MgentBusListener",
    "BusEventHandler",
    # Soul Memory (K-gent)
    "SoulMemory",
    "MemoryCategory",
    "create_soul_memory",
    # Stigmergy (Legacy)
    "PheromoneField",
    "Trace",
    "SenseResult",
    "StigmergicAgent",
    "EnhancedStigmergicAgent",
    "SimpleConceptSpace",
    "create_ant_colony_optimization",
    # Importers
    "MarkdownEngram",
    "FrontmatterData",
    "WikiLink",
    "ImportProgress",
    "ObsidianVaultParser",
    "MarkdownImporter",
    "create_importer_with_best_embedder",
    "create_lgent_embedder",
    "extract_frontmatter",
    "extract_wikilinks",
    "extract_tags",
    "extract_headings",
    "extract_code_blocks",
    "strip_markdown_formatting",
    "generate_concept_id",
    "parse_markdown",
]
