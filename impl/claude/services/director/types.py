"""
Document Director Types: Core data structures for living document lifecycle.

> *"Specs become code. Code becomes evidence. Evidence feeds back to specs."*

The Document Director orchestrates the full lifecycle from specification to
implementation, managing analysis, placeholders, code generation, and evidence
capture.

State Machine:
    UPLOADED → PROCESSING → READY → EXECUTED
                    ↓
                 FAILED

Teaching:
    gotcha: DocumentStatus extends AnalysisStatus with additional lifecycle states.
            UPLOADED/PROCESSING/READY map to PENDING/ANALYZING/ANALYZED, but we add
            EXECUTED (code generated) and STALE (needs re-analysis).

    gotcha: AnalysisCrystal is stored in overlay/analysis.json and contains derived
            data. It's frozen because it's immutable once created - any change
            requires re-analysis.

    gotcha: Anticipated implementations create entangled placeholders - they link
            specs to not-yet-existing code. When code is uploaded, the link becomes
            bidirectional evidence.

See: spec/protocols/document-director.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# =============================================================================
# Document Status (Extends AnalysisStatus)
# =============================================================================


class DocumentStatus(Enum):
    """
    Document lifecycle status.

    Extends the basic analysis status with lifecycle-aware states:
    - UPLOADED: Ingested, not yet analyzed
    - PROCESSING: Analysis in progress
    - READY: Analysis complete, write enabled, can generate code
    - EXECUTED: Code generated and captured
    - STALE: Content changed, re-analysis needed
    - FAILED: Analysis failed
    - GHOST: Placeholder created from reference in another doc, awaiting real content

    Ghost Philosophy:
        "The file is a lie. There is only the graph."

        Ghosts are the negative space of the document graph — entities that
        SHOULD exist based on references but DON'T yet. They are:
        - Created automatically when parsing finds dangling references
        - Visible in the Director as a de-prioritized section
        - Awaiting either: (a) user fills in content, or (b) user uploads the "real" doc
        - On reconciliation, Zero-Seed mediates the merge if both versions have content
    """

    UPLOADED = "uploaded"  # Ingested, awaiting analysis
    PROCESSING = "processing"  # Analysis in progress
    READY = "ready"  # Full write access enabled
    EXECUTED = "executed"  # Code generation captured
    STALE = "stale"  # Content changed, re-analysis needed
    FAILED = "failed"  # Analysis failed
    GHOST = "ghost"  # Placeholder awaiting real content


# =============================================================================
# Placeholder Types
# =============================================================================


class PlaceholderType(Enum):
    """
    Types of placeholders for not-yet-existing entities.

    Placeholders represent different kinds of "future content":
    - REFERENCE: Simple cross-ref auto-detected during parsing
    - ANTICIPATED: Pledged future implementation (spec promises this will exist)
    - DEFERRED: Explicitly deferred to future work
    - PROOF_OF_CONCEPT: Experimental, may not ship
    """

    REFERENCE = "reference"  # Auto-detected cross-ref
    ANTICIPATED = "anticipated"  # Pledged implementation
    DEFERRED = "deferred"  # Explicitly deferred
    PROOF_OF_CONCEPT = "poc"  # Experimental


# =============================================================================
# Execution Prompt (Spec → Code Generation)
# =============================================================================


@dataclass
class ExecutionPrompt:
    """
    Prompt for Claude Code execution harness.

    Generated from a spec to drive code generation. Contains everything needed
    to implement the spec: content, targets, context, and evidence trail.

    Fields:
        spec_path: Path to source spec
        spec_content: Full spec text
        targets: List of paths to generate (implementations, tests)
        context: Additional context (claims, existing refs)
        mark_id: Witness mark for prompt generation (L-2 evidence)

    Example:
        >>> prompt = ExecutionPrompt(
        ...     spec_path="spec/protocols/witness.md",
        ...     spec_content="# Witness Protocol...",
        ...     targets=["impl/claude/services/witness/evidence.py"],
        ...     context={"claims": [...], "existing_refs": [...]},
        ... )
        >>> task = prompt.to_claude_code_task()
    """

    spec_path: str
    spec_content: str
    targets: list[str]  # Paths to generate
    context: dict[str, Any]  # Claims, existing refs, etc.
    mark_id: str | None = None  # L-2 PROMPT evidence mark

    def to_claude_code_task(self) -> str:
        """
        Format as Claude Code execution task.

        Returns a formatted prompt string that can be sent to Claude Code
        for implementation.
        """
        import json

        claims = self.context.get("claims", [])
        existing = self.context.get("existing_refs", [])

        return f"""Implement the following specification:

# Specification: {self.spec_path}

{self.spec_content}

## Implementation Targets

Generate code for the following paths:
{chr(10).join(f"- {t}" for t in self.targets)}

## Context

Claims from spec:
{json.dumps(claims, indent=2)}

Existing implementations:
{chr(10).join(f"- {r}" for r in existing)}

## Requirements

1. Follow the spec's assertions and constraints exactly
2. Use the existing codebase patterns
3. Create tests for each implementation
4. Document any deviations with reasoning
"""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "spec_path": self.spec_path,
            "spec_content": self.spec_content,
            "targets": self.targets,
            "context": self.context,
            "mark_id": self.mark_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExecutionPrompt:
        """Create from dictionary (from JSON storage)."""
        return cls(
            spec_path=data["spec_path"],
            spec_content=data["spec_content"],
            targets=data.get("targets", []),
            context=data.get("context", {}),
            mark_id=data.get("mark_id"),
        )


# =============================================================================
# Analysis Crystal (Overlay Storage)
# =============================================================================


@dataclass(frozen=True)
class AnalysisCrystal:
    """
    Immutable analysis result stored in overlay.

    Stored at: .kgents/sovereign/{path}/overlay/analysis.json

    This crystal contains all derived data from analyzing a spec:
    - Extracted metadata (title, counts)
    - Claims (assertions, constraints, definitions)
    - Relationships (refs, implementations, tests)
    - Placeholders (missing refs that need to be created)
    - Anticipated implementations (entangled future code)

    Frozen because analysis is immutable - any content change requires re-analysis.

    Fields:
        entity_path: The spec path being analyzed
        analyzed_at: When analysis completed (ISO timestamp)
        analyzer_version: Analyzer version (e.g., "v1", "structural_v2")
        title: Extracted title
        word_count: Total word count
        heading_count: Number of headings
        claims: List of claim dicts from SpecRecord.claims
        discovered_refs: All refs found during parsing
        implementations: impl/ paths referenced
        tests: test paths referenced
        spec_refs: Other spec/ paths referenced
        placeholder_paths: Placeholders created for missing refs
        anticipated: Anticipated implementations (path, reason, phase, owner)
        status: "analyzed" | "stale" | "failed"
        error: Error message if failed
    """

    entity_path: str
    analyzed_at: str  # ISO timestamp
    analyzer_version: str = "v1"

    # Extracted content
    title: str = ""
    word_count: int = 0
    heading_count: int = 0

    # Claims (assertions, constraints, definitions)
    claims: list[dict[str, Any]] = field(default_factory=list)

    # Relationships
    discovered_refs: list[str] = field(default_factory=list)  # All refs found
    implementations: list[str] = field(default_factory=list)  # impl/ paths
    tests: list[str] = field(default_factory=list)  # test paths
    spec_refs: list[str] = field(default_factory=list)  # other spec refs

    # Placeholders created
    placeholder_paths: list[str] = field(default_factory=list)

    # Anticipated implementations (entanglement)
    # Each dict: {path: str, reason: str, phase: str | None, owner: str | None}
    anticipated: list[dict[str, Any]] = field(default_factory=list)

    # Status tracking
    status: str = "analyzed"  # "analyzed" | "stale" | "failed"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "entity_path": self.entity_path,
            "analyzed_at": self.analyzed_at,
            "analyzer_version": self.analyzer_version,
            "title": self.title,
            "word_count": self.word_count,
            "heading_count": self.heading_count,
            "claims": self.claims,
            "discovered_refs": self.discovered_refs,
            "implementations": self.implementations,
            "tests": self.tests,
            "spec_refs": self.spec_refs,
            "placeholder_paths": self.placeholder_paths,
            "anticipated": self.anticipated,
            "status": self.status,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalysisCrystal:
        """Create from dictionary (from JSON storage)."""
        return cls(
            entity_path=data["entity_path"],
            analyzed_at=data.get("analyzed_at", datetime.now(UTC).isoformat()),
            analyzer_version=data.get("analyzer_version", "v1"),
            title=data.get("title", ""),
            word_count=data.get("word_count", 0),
            heading_count=data.get("heading_count", 0),
            claims=data.get("claims", []),
            discovered_refs=data.get("discovered_refs", []),
            implementations=data.get("implementations", []),
            tests=data.get("tests", []),
            spec_refs=data.get("spec_refs", []),
            placeholder_paths=data.get("placeholder_paths", []),
            anticipated=data.get("anticipated", []),
            status=data.get("status", "analyzed"),
            error=data.get("error"),
        )

    @property
    def claim_count(self) -> int:
        """Number of claims extracted."""
        return len(self.claims)

    @property
    def ref_count(self) -> int:
        """Total number of references."""
        return len(self.discovered_refs)

    @property
    def impl_count(self) -> int:
        """Number of implementations referenced."""
        return len(self.implementations)

    @property
    def test_count(self) -> int:
        """Number of tests referenced."""
        return len(self.tests)

    @property
    def placeholder_count(self) -> int:
        """Number of placeholders created."""
        return len(self.placeholder_paths)

    @property
    def anticipated_count(self) -> int:
        """Number of anticipated implementations."""
        return len(self.anticipated)

    @property
    def is_successful(self) -> bool:
        """Check if analysis succeeded."""
        return self.status == "analyzed"


# =============================================================================
# Capture Result (Code Generation Results)
# =============================================================================


@dataclass
class TestResults:
    """
    Test execution results for generated code.

    Tracks which files had passing tests.
    """

    results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def passed_for(self, path: str) -> bool:
        """Check if tests passed for path."""
        result = self.results.get(path, {})
        passed = result.get("passed", False)
        return bool(passed)

    def count_for(self, path: str) -> int:
        """Get test count for path."""
        result = self.results.get(path, {})
        count = result.get("count", 0)
        return int(count) if count is not None else 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {"results": self.results}


@dataclass
class CaptureResult:
    """
    Result of capturing code generation execution.

    Created when Claude Code finishes generating implementations from a spec.
    Contains all generated files and test results, ready for evidence linking.

    Fields:
        spec_path: Source spec that prompted generation
        captured: List of paths successfully captured
        test_results: Test execution results
        mark_ids: List of evidence marks created (L-1 TRACE, L1 TEST)

    Example:
        >>> result = CaptureResult(
        ...     spec_path="spec/protocols/witness.md",
        ...     captured=["impl/claude/services/witness/evidence.py"],
        ...     test_results=TestResults(...),
        ... )
    """

    spec_path: str
    captured: list[str]  # Paths successfully captured
    test_results: TestResults = field(default_factory=TestResults)
    mark_ids: list[str] = field(default_factory=list)  # Evidence marks created

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "spec_path": self.spec_path,
            "captured": self.captured,
            "captured_count": len(self.captured),
            "test_results": self.test_results.to_dict(),
            "mark_ids": self.mark_ids,
            "mark_count": len(self.mark_ids),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CaptureResult:
        """Create from dictionary."""
        test_data = data.get("test_results", {})
        return cls(
            spec_path=data["spec_path"],
            captured=data.get("captured", []),
            test_results=TestResults(results=test_data.get("results", {})),
            mark_ids=data.get("mark_ids", []),
        )


# =============================================================================
# Director Events (WitnessBus Topics)
# =============================================================================


class DocumentTopics:
    """
    Event topics for Document Director lifecycle.

    Published to WitnessBus for reactive subscribers.
    """

    UPLOADED = "document.uploaded"
    ANALYSIS_STARTED = "document.analysis.started"
    ANALYSIS_COMPLETE = "document.analysis.complete"
    ANALYSIS_FAILED = "document.analysis.failed"
    STATUS_CHANGED = "document.status.changed"
    PROMPT_GENERATED = "document.prompt.generated"
    EXECUTION_CAPTURED = "document.execution.captured"
    PLACEHOLDER_RESOLVED = "document.placeholder.resolved"


@dataclass
class DirectorEvent:
    """
    Base event for Document Director operations.

    Fields:
        topic: Event topic (from DocumentTopics)
        path: Document path
        timestamp: When event occurred
        data: Event-specific payload
    """

    topic: str
    path: str
    timestamp: str  # ISO timestamp
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "topic": self.topic,
            "path": self.path,
            "timestamp": self.timestamp,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DirectorEvent:
        """Create from dictionary."""
        return cls(
            topic=data["topic"],
            path=data["path"],
            timestamp=data.get("timestamp", datetime.now(UTC).isoformat()),
            data=data.get("data", {}),
        )

    @classmethod
    def uploaded(cls, path: str, version: int, mark_id: str) -> DirectorEvent:
        """Create UPLOADED event."""
        return cls(
            topic=DocumentTopics.UPLOADED,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
            data={"version": version, "mark_id": mark_id},
        )

    @classmethod
    def analysis_started(cls, path: str) -> DirectorEvent:
        """Create ANALYSIS_STARTED event."""
        return cls(
            topic=DocumentTopics.ANALYSIS_STARTED,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
        )

    @classmethod
    def analysis_complete(
        cls, path: str, crystal: AnalysisCrystal, mark_id: str
    ) -> DirectorEvent:
        """Create ANALYSIS_COMPLETE event."""
        return cls(
            topic=DocumentTopics.ANALYSIS_COMPLETE,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "mark_id": mark_id,
                "claim_count": crystal.claim_count,
                "ref_count": crystal.ref_count,
                "placeholder_count": crystal.placeholder_count,
            },
        )

    @classmethod
    def analysis_failed(cls, path: str, error: str) -> DirectorEvent:
        """Create ANALYSIS_FAILED event."""
        return cls(
            topic=DocumentTopics.ANALYSIS_FAILED,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
            data={"error": error},
        )

    @classmethod
    def status_changed(
        cls, path: str, old_status: DocumentStatus, new_status: DocumentStatus
    ) -> DirectorEvent:
        """Create STATUS_CHANGED event."""
        return cls(
            topic=DocumentTopics.STATUS_CHANGED,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "old_status": old_status.value,
                "new_status": new_status.value,
            },
        )

    @classmethod
    def prompt_generated(cls, path: str, prompt: ExecutionPrompt) -> DirectorEvent:
        """Create PROMPT_GENERATED event."""
        return cls(
            topic=DocumentTopics.PROMPT_GENERATED,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "mark_id": prompt.mark_id,
                "target_count": len(prompt.targets),
                "targets": prompt.targets,
            },
        )

    @classmethod
    def execution_captured(cls, path: str, result: CaptureResult) -> DirectorEvent:
        """Create EXECUTION_CAPTURED event."""
        return cls(
            topic=DocumentTopics.EXECUTION_CAPTURED,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "captured_count": len(result.captured),
                "captured": result.captured,
                "mark_count": len(result.mark_ids),
            },
        )

    @classmethod
    def placeholder_resolved(
        cls, path: str, placeholder_path: str, linked_specs: list[str]
    ) -> DirectorEvent:
        """Create PLACEHOLDER_RESOLVED event."""
        return cls(
            topic=DocumentTopics.PLACEHOLDER_RESOLVED,
            path=path,
            timestamp=datetime.now(UTC).isoformat(),
            data={
                "placeholder_path": placeholder_path,
                "linked_specs": linked_specs,
                "linked_count": len(linked_specs),
            },
        )


# =============================================================================
# Ghost Document Types (Zero-Seed Integration)
# =============================================================================


class GhostOrigin(Enum):
    """
    How a ghost document came into existence.

    Tracking origin is essential for the reconciliation UI:
    - PARSED_REFERENCE: A spec mentioned this path but it doesn't exist
    - ANTICIPATED: @anticipated marker created an expectation
    - USER_CREATED: User explicitly created a placeholder
    """

    PARSED_REFERENCE = "parsed_reference"
    ANTICIPATED = "anticipated"
    USER_CREATED = "user_created"


@dataclass(frozen=True)
class GhostMetadata:
    """
    Metadata for a ghost document.

    Ghosts are the negative space of the graph — they represent
    what SHOULD exist but doesn't yet. This metadata tracks:
    - Who summoned this ghost (which spec referenced it)
    - Why (the context that demanded its existence)
    - When it was created
    - User-contributed content (if any)

    The is_empty flag distinguishes:
    - Pure ghosts: only the path exists (created by reference)
    - Nascent docs: user has started filling content but hasn't "resolved"
    """

    origin: GhostOrigin
    created_by_path: str  # Which spec created this ghost
    created_at: str  # ISO timestamp
    context: str = ""  # Why this ghost exists (from anticipated marker or reference)
    user_content: str = ""  # User-contributed content (if any)

    @property
    def is_empty(self) -> bool:
        """True if ghost has no user content yet."""
        return len(self.user_content.strip()) == 0

    @property
    def has_draft_content(self) -> bool:
        """True if user has started adding content."""
        return len(self.user_content.strip()) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "origin": self.origin.value,
            "created_by_path": self.created_by_path,
            "created_at": self.created_at,
            "context": self.context,
            "user_content": self.user_content,
            "is_empty": self.is_empty,
            "has_draft_content": self.has_draft_content,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GhostMetadata":
        """Create from dictionary (from JSON storage)."""
        return cls(
            origin=GhostOrigin(data.get("origin", "parsed_reference")),
            created_by_path=data.get("created_by_path", ""),
            created_at=data.get("created_at", datetime.now(UTC).isoformat()),
            context=data.get("context", ""),
            user_content=data.get("user_content", ""),
        )


class ReconciliationStrategy(Enum):
    """
    Strategy for reconciling ghost content with uploaded "real" document.

    When a user uploads a document that matches a ghost path, we need
    to decide what to do with any content that was in the ghost:

    - REPLACE: Use uploaded content, discard ghost content
    - MERGE_UPLOADED_WINS: Zero-Seed merge, conflicts resolved by uploaded
    - MERGE_GHOST_WINS: Zero-Seed merge, conflicts resolved by ghost content
    - INTERACTIVE: Present both to user for manual merge
    """

    REPLACE = "replace"
    MERGE_UPLOADED_WINS = "merge_uploaded_wins"
    MERGE_GHOST_WINS = "merge_ghost_wins"
    INTERACTIVE = "interactive"


@dataclass
class ReconciliationRequest:
    """
    Request to reconcile a ghost with an uploaded document.

    This is the input to Zero-Seed reconciliation.

    Teaching:
        gotcha: Both ghost and uploaded can have content. The strategy
                determines how conflicts are resolved.

        gotcha: Zero-Seed integration means we don't just pick one — we can
                actually merge the documents using semantic understanding.
    """

    ghost_path: str
    ghost_content: str  # Current ghost content (may be empty)
    uploaded_content: str  # Newly uploaded content
    ghost_metadata: GhostMetadata
    strategy: ReconciliationStrategy = ReconciliationStrategy.REPLACE

    def needs_merge(self) -> bool:
        """Check if actual merge is needed (both have content)."""
        return (
            len(self.ghost_content.strip()) > 0
            and len(self.uploaded_content.strip()) > 0
            and self.strategy != ReconciliationStrategy.REPLACE
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "ghost_path": self.ghost_path,
            "ghost_content": self.ghost_content,
            "uploaded_content": self.uploaded_content,
            "ghost_metadata": self.ghost_metadata.to_dict(),
            "strategy": self.strategy.value,
            "needs_merge": self.needs_merge(),
        }


@dataclass
class ReconciliationResult:
    """
    Result of ghost reconciliation.

    After Zero-Seed processes the reconciliation request, this captures:
    - The final merged content
    - Any conflicts that required resolution
    - The witness mark documenting the reconciliation
    """

    path: str
    final_content: str
    strategy_used: ReconciliationStrategy
    had_conflicts: bool = False
    conflict_summary: str = ""
    mark_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "final_content": self.final_content,
            "strategy_used": self.strategy_used.value,
            "had_conflicts": self.had_conflicts,
            "conflict_summary": self.conflict_summary,
            "mark_id": self.mark_id,
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Status
    "DocumentStatus",
    # Placeholders
    "PlaceholderType",
    # Execution
    "ExecutionPrompt",
    # Analysis
    "AnalysisCrystal",
    # Capture
    "TestResults",
    "CaptureResult",
    # Events
    "DocumentTopics",
    "DirectorEvent",
    # Ghost types
    "GhostOrigin",
    "GhostMetadata",
    "ReconciliationStrategy",
    "ReconciliationRequest",
    "ReconciliationResult",
]
