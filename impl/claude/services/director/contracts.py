"""
Document Director Service Contracts: BE/FE type sync via AGENTESE contracts.

These dataclasses define the request/response shapes for each aspect.
The AGENTESE contract system generates TypeScript types from these.

See: spec/protocols/document-director.md
See: docs/skills/agentese-contract-protocol.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# Manifest (concept.document.manifest)
# =============================================================================


@dataclass
class DirectorManifestResponse:
    """Response for manifest aspect - director status."""

    total_documents: int
    by_status: dict[str, int]  # Status → count
    recent_uploads: list[str]  # Last 5 uploaded paths
    recent_analyses: list[str]  # Last 5 analyzed paths


# =============================================================================
# Upload (concept.document.upload)
# =============================================================================


@dataclass
class UploadRequest:
    """Request to upload a document."""

    path: str  # The document path
    content: str  # The content (UTF-8 text)
    source: str = "api"  # Where it came from


@dataclass
class UploadResponse:
    """Response from upload - ingest + analysis queued."""

    path: str
    version: int
    ingest_mark_id: str
    status: str  # "uploaded" | "processing"
    analysis_queued: bool


# =============================================================================
# Analyze (concept.document.analyze)
# =============================================================================


@dataclass
class AnalyzeRequest:
    """Request to analyze (or re-analyze) a document."""

    path: str
    force: bool = False  # Force re-analysis even if already analyzed


@dataclass
class AnalyzeResponse:
    """Response from analysis."""

    path: str
    status: str  # "processing" | "ready" | "failed"
    claim_count: int = 0
    ref_count: int = 0
    placeholder_count: int = 0
    analysis_mark_id: str | None = None
    error: str | None = None


# =============================================================================
# Status (concept.document.status)
# =============================================================================


@dataclass
class StatusRequest:
    """Request document status."""

    path: str


@dataclass
class StatusResponse:
    """Response with document lifecycle status."""

    path: str
    status: str  # "uploaded" | "processing" | "ready" | "executed" | "stale" | "failed"
    version: int
    analysis: dict[str, Any] = field(default_factory=dict)  # AnalysisCrystal summary
    actions_available: list[str] = field(default_factory=list)  # e.g., ["edit", "generate_prompt"]


# =============================================================================
# Prompt (concept.document.prompt)
# =============================================================================


@dataclass
class PromptRequest:
    """Request to generate execution prompt."""

    path: str


@dataclass
class PromptResponse:
    """Response with execution prompt."""

    spec_path: str
    targets: list[str]  # Paths to generate
    prompt_text: str  # The formatted prompt for Claude Code
    mark_id: str | None = None  # L-2 PROMPT witness mark


# =============================================================================
# Capture (concept.document.capture)
# =============================================================================


@dataclass
class CaptureRequest:
    """Request to capture execution results."""

    path: str  # The spec path
    generated_files: dict[str, str]  # path → content
    test_passed: bool = False  # Did tests pass?
    test_output: str | None = None  # Test results


@dataclass
class CaptureResponse:
    """Response from capture."""

    spec_path: str
    captured_count: int
    resolved_placeholders: list[str]
    evidence_marks: list[str]  # Mark IDs created


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Manifest
    "DirectorManifestResponse",
    # Upload
    "UploadRequest",
    "UploadResponse",
    # Analyze
    "AnalyzeRequest",
    "AnalyzeResponse",
    # Status
    "StatusRequest",
    "StatusResponse",
    # Prompt
    "PromptRequest",
    "PromptResponse",
    # Capture
    "CaptureRequest",
    "CaptureResponse",
]
