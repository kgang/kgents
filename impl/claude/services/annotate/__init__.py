"""
Annotation Service: Spec ↔ Implementation Mapping.

> *"Every spec section should trace to implementation. Every gotcha should be captured."*

The Annotation service provides bidirectional tracing between specs and code:

    kg annotate <spec> --principle composable --section "..." --note "..."
    kg annotate <spec> --impl --section "..." --link "path/to/impl.py:ClassName"
    kg annotate <spec> --gotcha --section "..." --note "Trap to avoid..."
    kg annotate <spec> --show
    kg annotate <spec> --export --json

Crown Jewel Pattern:
    - types.py: Core types (SpecAnnotation, AnnotationKind, etc.)
    - store.py: Database persistence (AnnotationStore)
    - graph.py: Bidirectional spec ↔ impl graph building
    - CLI handler: protocols/cli/handlers/annotate.py (NOT in this service)

Teaching:
    gotcha: Store provides database persistence only. Optional inline YAML
            in spec files is future work (requires careful markdown parsing).

    principle: Composable - Annotations are first-class values that compose
               into larger structures (graphs, coverage reports, etc.)

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 2)
"""

from __future__ import annotations

from .types import (
    AnnotationKind,
    AnnotationQueryResult,
    AnnotationStatus,
    ImplEdge,
    ImplGraph,
    SpecAnnotation,
)

__all__ = [
    "AnnotationKind",
    "AnnotationStatus",
    "SpecAnnotation",
    "ImplEdge",
    "ImplGraph",
    "AnnotationQueryResult",
]
