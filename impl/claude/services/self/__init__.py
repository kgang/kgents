"""
Self-Reflective OS Service: Constitution + Drift Detection + Timeline + Inspection + Git + Decisions.

"The Constitution is not documentation - it is executable architecture."
"Drift is not failure - it's the natural cost of creating."
"The timeline is the heartbeat. Every action leaves a mark."
"Inspection is introspection. The system that sees itself can trust itself."
"The git history IS the implementation chronicle."
"Decisions without traces are reflexes. Decisions with traces are agency."

This service exposes the 22 Constitutional K-Blocks via AGENTESE paths
and provides spec/impl coherence monitoring through drift detection.

AGENTESE Paths - Constitution:
- self.constitution.view      - View the Constitutional graph
- self.constitution.navigate  - Navigate derivation chains from a K-Block
- self.constitution.axioms    - Get L0 axiom K-Blocks (A1, A2, A3, G)
- self.constitution.principles - Get L1-L2 principle K-Blocks
- self.constitution.architecture - Get L3 architecture K-Blocks
- self.constitution.inspect   - Deep inspect a specific K-Block

AGENTESE Paths - Drift Detection:
- self.drift.report           - Comprehensive drift analysis report
- self.drift.orphans          - K-Blocks without derivation roots
- self.drift.coverage         - Principle coverage scores

AGENTESE Paths - Development Timeline:
- self.timeline.view          - Get aggregated timeline
- self.timeline.search        - Search marks by query
- self.timeline.for_file      - Get witnesses for a file
- self.timeline.activity      - Development activity summary

AGENTESE Paths - Inspection:
- self.inspect.file           - Inspect a file with full context
- self.inspect.kblock         - Inspect a K-Block with derivation chain
- self.inspect.quick          - Lightweight inspection for quick lookups

AGENTESE Paths - Git History:
- self.git.history            - Recent commits with metadata
- self.git.file_history       - History for a specific file
- self.git.blame              - Who wrote each line
- self.git.diff               - Show commit diff
- self.git.search             - Search commit messages
- self.git.spec_impl          - Linked spec/impl pairs

AGENTESE Paths - Decisions:
- self.decisions.list         - List all decisions
- self.decisions.search       - Search decisions
- self.decisions.get          - Get a specific decision
- self.decisions.for_file     - Decisions about a file

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit backend routes needed
- All transports collapse to logos.invoke(path, observer, ...)

See: spec/bootstrap.md for axiom definitions
See: spec/protocols/zero-seed1/ashc.md for ASHC derivation
See: plans/self-reflective-os/ for design specifications
"""

from __future__ import annotations

# Decisions Service
from .decisions_service import (
    Decision,
    DecisionSearchResult,
    DecisionsService,
    QuickDecision,
    get_decisions_service,
    reset_decisions_service,
)

# Derivation Analysis
from .derivation_analyzer import (
    DerivationAnalyzer,
    DerivationChain as AnalyzerDerivationChain,
    DerivationStep,
    OrphanReport,
    create_derivation_analyzer,
    get_derivation_analyzer,
)

# Drift Detection
from .drift_service import (
    Divergence,
    DivergenceSeverity,
    DivergenceType,
    DriftReport,
    DriftService,
    create_drift_service,
    get_drift_service,
)

# Git History Service
from .git_service import (
    BlameLine,
    CommitDetail,
    CommitInfo,
    FileHistory as GitFileHistory,
    GitHistoryService,
    SpecImplPair,
    get_git_service,
    reset_git_service,
)

# Inspection Service
from .inspection_service import (
    LAYER_NAMES,
    DerivationChain as InspectionDerivationChain,
    DerivationStep as InspectionDerivationStep,
    DriftStatus,
    FileHistory,
    InspectionResult,
    InspectionService,
    QuickInspection,
    create_inspection_service,
    get_inspection_service,
    get_layer_name,
)

# Codebase Scanner
from .models import (
    ClassInfo,
    DerivationChain as CodebaseDerivationChain,
    Edge,
    FunctionInfo,
    KBlockGraph,
    KBlockInspection as CodebaseKBlockInspection,
    ModuleKBlock,
)

# AGENTESE Nodes
from .node import (
    ActivityRendering,
    BlameRendering,
    CodebaseDerivationRendering,
    CodebaseInspectionRendering,
    CodebaseManifestRendering,
    CodebaseNode,
    CommitListRendering,
    ConstitutionNode,
    CoverageRendering,
    DecisionDetailRendering,
    DecisionListRendering,
    # Decisions Node
    DecisionsNode,
    DriftNode,
    DriftReportRendering,
    FileHistoryRendering,
    # Git Node
    GitNode,
    GraphRendering,
    # Inspection Node
    InspectionNode,
    InspectionRendering,
    MarkSearchRendering,
    OrphanListRendering,
    QuickInspectionRendering,
    TimelineRendering,
    # Witness Timeline Node
    WitnessTimelineNode,
)

# Reflection Service
from .reflection_service import (
    ConstitutionalGraph,
    DerivationChain,
    KBlockInspection,
    SelfReflectionService,
    get_reflection_service,
)
from .scanner import CodebaseScanner, FileMetadata, SpecFile, SpecImplLink

# Witness Timeline Service
from .witness_timeline_service import (
    ActorType,
    DevelopmentActivity,
    EventType,
    TimelineEvent,
    TimelineFilter,
    WitnessTimelineService,
    create_witness_timeline_service,
    get_witness_timeline_service,
)

__all__ = [
    # Constitution Node
    "ConstitutionNode",
    # Codebase Node
    "CodebaseNode",
    "CodebaseScanner",
    "CodebaseManifestRendering",
    "CodebaseDerivationRendering",
    "CodebaseInspectionRendering",
    "GraphRendering",
    # Codebase Types
    "ModuleKBlock",
    "KBlockGraph",
    "CodebaseKBlockInspection",
    "CodebaseDerivationChain",
    "ClassInfo",
    "FunctionInfo",
    "Edge",
    # Spec Scanning Types
    "SpecFile",
    "SpecImplLink",
    "FileMetadata",
    # Drift Node
    "DriftNode",
    "DriftReportRendering",
    "OrphanListRendering",
    "CoverageRendering",
    # Reflection Service
    "SelfReflectionService",
    "get_reflection_service",
    # Drift Service
    "Divergence",
    "DivergenceSeverity",
    "DivergenceType",
    "DriftReport",
    "DriftService",
    "create_drift_service",
    "get_drift_service",
    # Derivation Analyzer
    "DerivationAnalyzer",
    "DerivationStep",
    "InspectionDerivationStep",
    "OrphanReport",
    "create_derivation_analyzer",
    "get_derivation_analyzer",
    # Types from reflection_service
    "ConstitutionalGraph",
    "DerivationChain",
    "KBlockInspection",
    # Alias for analyzer chain
    "AnalyzerDerivationChain",
    # Witness Timeline Node
    "WitnessTimelineNode",
    "TimelineRendering",
    "ActivityRendering",
    "MarkSearchRendering",
    # Witness Timeline Service
    "EventType",
    "ActorType",
    "TimelineEvent",
    "TimelineFilter",
    "DevelopmentActivity",
    "WitnessTimelineService",
    "get_witness_timeline_service",
    "create_witness_timeline_service",
    # Inspection Node
    "InspectionNode",
    "InspectionRendering",
    "QuickInspectionRendering",
    # Inspection Service
    "DriftStatus",
    "FileHistory",
    "InspectionDerivationChain",
    "QuickInspection",
    "InspectionResult",
    "InspectionService",
    "get_inspection_service",
    "create_inspection_service",
    "get_layer_name",
    "LAYER_NAMES",
    # Git Node
    "GitNode",
    "CommitListRendering",
    "FileHistoryRendering",
    "BlameRendering",
    # Git History Service
    "GitHistoryService",
    "CommitInfo",
    "CommitDetail",
    "BlameLine",
    "GitFileHistory",
    "SpecImplPair",
    "get_git_service",
    "reset_git_service",
    # Decisions Node
    "DecisionsNode",
    "DecisionListRendering",
    "DecisionDetailRendering",
    # Decisions Service
    "DecisionsService",
    "Decision",
    "QuickDecision",
    "DecisionSearchResult",
    "get_decisions_service",
    "reset_decisions_service",
]
