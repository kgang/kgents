"""
Interactive Text Crown Jewel: Meaning Token Frontend Architecture.

The Interactive Text service implements a radical paradigm shift where there is no
"frontend" - only meaning tokens that project to observer surfaces. Text files ARE
interfaces, not descriptions of interfaces.

AGENTESE Paths (via @node("self.document")):
- self.document.manifest     - Render document with observer-appropriate affordances
- self.document.token.hover  - Get hover information for a token
- self.document.token.navigate - Navigate to token's target
- self.document.task.toggle  - Toggle task checkbox with trace witness
- self.document.image.analyze - Get AI analysis of image

Core Concepts:
- MeaningToken: Semantic primitive that carries meaning independent of rendering
- ProjectionFunctor: Natural transformation from tokens to target-specific rendering
- DocumentPolynomial: State machine governing document modes (VIEWING, EDITING, etc.)
- DocumentSheaf: Coherence structure ensuring multi-view consistency
- Observer: Entity receiving projections with specific umwelt (capabilities, density)

The Metaphysical Fullstack Pattern (AD-009):
- Tokens are the atomic unit of interface
- Projections are observations, not constructions
- The protocol IS the API (AGENTESE paths)
- Coherence is mathematical (sheaf theory)

See: .kiro/specs/meaning-token-frontend/design.md
"""

from .contracts import (
    # Core types
    Affordance,
    AffordanceAction,
    # Document types
    DocumentState,
    # Result types
    InteractionResult,
    MeaningToken,
    Observer,
    ObserverDensity,
    ObserverRole,
    TokenDefinition,
    TokenPattern,
)
from .events import (
    # Event class
    DocumentEvent,
    # Event bus
    DocumentEventBus,
    DocumentEventHandler,
    # Event types
    DocumentEventType,
    DocumentSubscriber,
    # Event-emitting polynomial
    EventEmittingPolynomial,
    # Global bus
    get_document_event_bus,
    reset_document_event_bus,
)
from .parser import (
    DocumentEdit,
    IncrementalParser,
    # Parsers
    MarkdownParser,
    ParsedDocument,
    SourceMap,
    # Data models
    SourcePosition,
    TextSpan,
    # Convenience functions
    parse_markdown,
    render_markdown,
)
from .polynomial import (
    Aborted,
    CancelResult,
    ClickResult,
    ConflictDetected,
    DiffView,
    # State machine
    DocumentPolynomial,
    DragResult,
    EditContinue,
    EditSession,
    HoverInfo,
    LocalWins,
    NoOp,
    RefreshResult,
    RemoteWins,
    Resolved,
    SaveRequest,
    SyncComplete,
    # Output types
    TransitionOutput,
)
from .registry import TokenRegistry
from .sheaf import (
    # Sheaf
    DocumentSheaf,
    # Protocol
    DocumentView,
    Edit,
    FileChange,
    # Exceptions
    SheafConditionError,
    # Verification
    SheafConflict,
    SheafVerification,
    # Implementation
    SimpleDocumentView,
    TokenChange,
    # Core types
    TokenState,
)

__all__ = [
    # Core types
    "Affordance",
    "AffordanceAction",
    "MeaningToken",
    "Observer",
    "ObserverDensity",
    "ObserverRole",
    "TokenDefinition",
    "TokenPattern",
    # Document types
    "DocumentState",
    # Result types
    "InteractionResult",
    # Registry
    "TokenRegistry",
    # Polynomial state machine
    "DocumentPolynomial",
    "TransitionOutput",
    "NoOp",
    "EditSession",
    "RefreshResult",
    "HoverInfo",
    "ClickResult",
    "DragResult",
    "SaveRequest",
    "CancelResult",
    "EditContinue",
    "SyncComplete",
    "LocalWins",
    "RemoteWins",
    "ConflictDetected",
    "Resolved",
    "Aborted",
    "DiffView",
    # Event types
    "DocumentEventType",
    # Event class
    "DocumentEvent",
    # Event bus
    "DocumentEventBus",
    "DocumentEventHandler",
    "DocumentSubscriber",
    # Event-emitting polynomial
    "EventEmittingPolynomial",
    # Global bus
    "get_document_event_bus",
    "reset_document_event_bus",
    # Sheaf types
    "TokenState",
    "TokenChange",
    "FileChange",
    "Edit",
    "DocumentView",
    "SimpleDocumentView",
    "DocumentSheaf",
    "SheafConflict",
    "SheafVerification",
    "SheafConditionError",
    # Parser types
    "SourcePosition",
    "TextSpan",
    "ParsedDocument",
    "SourceMap",
    "DocumentEdit",
    "MarkdownParser",
    "IncrementalParser",
    "parse_markdown",
    "render_markdown",
]
