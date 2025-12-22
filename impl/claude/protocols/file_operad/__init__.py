"""
FILE_OPERAD: The Metaphysical Filesystem

"The text IS the interface. The filesystem IS the meta-OS."

This module implements the FILE_OPERAD protocol from spec/protocols/file-operad.md.
Key components:

- PortalToken: Expandable cross-operad links
- PortalTree: Tree of expanded portals (the agent's view)
- PortalRenderer: Multi-surface rendering (CLI, LLM, Markdown)
- FileWiringTrace: Persistent trail of portal expansions

The core insight: "Navigation is expansion. Expansion is navigation."
"""

from __future__ import annotations

from .ashc_bridge import (
    EvidenceSource,
    EvidenceType,
    FileOperadEvidence,
    FileTraceToEvidenceAdapter,
    LawProofCompiler,
    LawVerificationResult,
    LawVerifier,
    ProofObligation,
    SandboxToEvidenceAdapter,
    VerificationResult,
)
from .law_parser import (
    LawDefinition,
    LawStatus,
    extract_verification_code,
    list_laws_in_operad,
    parse_law_file,
    parse_law_markdown,
)
from .portal import (
    PortalLink,
    PortalOpenSignal,
    PortalRenderer,
    PortalState,
    PortalToken,
    PortalTree,
)
from .sandbox import (
    InvalidTransitionError,
    SandboxConfig,
    SandboxId,
    SandboxPhase,
    SandboxPolynomial,
    SandboxResult,
    SandboxRuntime,
    SandboxStore,
    get_sandbox_store,
    reset_sandbox_store,
)
from .source_portals import (
    SOURCE_EDGE_TYPES,
    SUPPORTED_EXTENSIONS,
    SourcePortalDiscovery,
    SourcePortalLink,
    SourcePortalToken,
    build_source_portal_tree,
    discover_portals,
    render_portals_cli,
)
from .trace import (
    FileTraceStore,
    FileWiringTrace,
    enable_persistence,
    get_file_trace_store,
    record_expansion,
    record_file_operation,
    reset_file_trace_store,
    sync_file_trace_store,
)
from .wasm_executor import (
    CodeAnalyzer,
    ExecutionMode,
    ExecutionResult,
    ExecutorBridge,
    ExecutorConfig,
    IsolationLevel,
    LocalWASMExecutor,
    RemoteExecutorConfig,
    RemoteWASMExecutor,
    configure_remote_executor,
    execute_sandbox,
    get_executor_bridge,
    reset_executor_bridge,
)

__all__ = [
    # Portal types
    "PortalState",
    "PortalLink",
    "PortalToken",
    "PortalTree",
    "PortalRenderer",
    "PortalOpenSignal",
    # Trace types
    "FileWiringTrace",
    "FileTraceStore",
    # Global store management
    "get_file_trace_store",
    "reset_file_trace_store",
    "enable_persistence",
    "sync_file_trace_store",
    # Recording API
    "record_expansion",
    "record_file_operation",
    # Sandbox types (Session 5)
    "SandboxPhase",
    "SandboxRuntime",
    "SandboxId",
    "SandboxConfig",
    "SandboxResult",
    "SandboxPolynomial",
    "SandboxStore",
    "InvalidTransitionError",
    # Sandbox store management
    "get_sandbox_store",
    "reset_sandbox_store",
    # Law parser (Session 6a)
    "LawStatus",
    "LawDefinition",
    "parse_law_file",
    "parse_law_markdown",
    "list_laws_in_operad",
    "extract_verification_code",
    # ASHC bridge (Session 6b)
    "EvidenceSource",
    "EvidenceType",
    "VerificationResult",
    "FileOperadEvidence",
    "FileTraceToEvidenceAdapter",
    "SandboxToEvidenceAdapter",
    "ProofObligation",
    "LawProofCompiler",
    "LawVerificationResult",
    "LawVerifier",
    # Source portals (Phase 4)
    "SOURCE_EDGE_TYPES",
    "SUPPORTED_EXTENSIONS",
    "SourcePortalDiscovery",
    "SourcePortalLink",
    "SourcePortalToken",
    "build_source_portal_tree",
    "discover_portals",
    "render_portals_cli",
    # WASM executor (Session 7)
    "ExecutionMode",
    "IsolationLevel",
    "ExecutionResult",
    "ExecutorConfig",
    "CodeAnalyzer",
    "LocalWASMExecutor",
    "RemoteExecutorConfig",
    "RemoteWASMExecutor",
    "ExecutorBridge",
    "get_executor_bridge",
    "reset_executor_bridge",
    "execute_sandbox",
    "configure_remote_executor",
]
