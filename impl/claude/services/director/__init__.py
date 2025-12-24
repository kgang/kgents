"""
Document Director: Living document lifecycle management.

> *"Specs become code. Code becomes evidence. Evidence feeds back to specs."*

The Document Director orchestrates the full journey from specification to
implementation:

    Upload → Analyze → Annotate → Generate → Execute → Capture → Verify
       ↑                                                           ↓
       └───────────────── Evidence Feedback Loop ──────────────────┘

Three Laws:
1. Law of Sovereignty: Every document is versioned, witnessed, and possessed
2. Law of Analysis: No document enters without automatic parsing and claim extraction
3. Law of Entanglement: Specs anticipate implementations; implementations evidence specs

State Machine:
    UPLOADED → PROCESSING → READY → EXECUTED
                    ↓
                 FAILED

Components:
    types.py - Core types (DocumentStatus, AnalysisCrystal, ExecutionPrompt, etc.)
    director.py - Main orchestrator
    node.py - AGENTESE interface
    contracts.py - AGENTESE request/response types

See: spec/protocols/document-director.md
"""

from __future__ import annotations

from .director import DocumentDirector, ResolveResult
from .types import (
    # Status
    DocumentStatus,
    # Placeholders
    PlaceholderType,
    # Execution
    ExecutionPrompt,
    # Analysis
    AnalysisCrystal,
    # Capture
    CaptureResult,
    TestResults,
    # Events
    DirectorEvent,
    DocumentTopics,
)

__all__ = [
    # Service
    "DocumentDirector",
    "ResolveResult",
    # Types
    "DocumentStatus",
    "PlaceholderType",
    "ExecutionPrompt",
    "AnalysisCrystal",
    "TestResults",
    "CaptureResult",
    "DocumentTopics",
    "DirectorEvent",
]
