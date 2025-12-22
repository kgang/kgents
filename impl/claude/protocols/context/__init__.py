"""
Context Perception Protocol.

The visualization layer for the typed-hypergraph. Makes navigation feel like
collaborating on an outline—text you can open, close, copy, paste, link, and navigate.

The vibe: Two intelligences (human + agent) editing an outline together.
The outline happens to be a metaphysical representation of their distributed cognition.

Spec: spec/protocols/context-perception.md

Four-Layer Stack:
    Layer 4: CONTEXT PERCEPTION (this module)
             └── Text snippets + semi-transparent UI + magical operations
    Layer 3: PORTAL TOKENS (portal-token.md)
             └── Expandable meaning tokens + state machines
    Layer 2: EXPLORATION HARNESS (exploration-harness.md)
             └── Budget, loop detection, evidence accumulation
    Layer 1: TYPED-HYPERGRAPH (typed-hypergraph.md)
             └── Nodes, hyperedges, trails, observer-dependent affordances

Teaching:
    gotcha: TextSnippet.visible_text is what the user sees. The metadata
            (source_path, copied_at, links) is invisible but travels with copy/paste.
            (Evidence: test_outline.py::test_copy_preserves_provenance)

    gotcha: Outline operations are "normal" on the surface but do hidden magic.
            expand() doesn't just show content—it records a trail step.
            (Evidence: test_outline.py::test_expand_records_trail)
"""

from .outline import (
    # Core data structures
    TextSnippet,
    OutlineNode,
    Outline,
    Clipboard,
    Range,
    Location,
    # Operations
    OutlineOperations,
    # Factory functions
    create_outline,
    create_snippet,
)
from .parser import (
    # Token types
    RecognizedToken,
    TokenType,
    # Parsing
    parse_text,
    extract_tokens,
    # Metadata
    encode_invisible_metadata,
    decode_invisible_metadata,
)
from .lens import (
    # Lens types
    FileLens,
    FocusSpec,
    # Factory
    create_lens_for_function,
    create_lens_for_class,
    create_lens_for_range,
)
from .portal_bridge import (
    # Bridge types
    BridgeState,
    PortalExpansionResult,
    OutlinePortalBridge,
    # Factory
    create_bridge,
    create_bridge_from_file,
)
from .renderer import (
    # Surface types
    Surface,
    RenderConfig,
    # Renderer
    OutlineRenderer,
    # Factory
    render_outline,
    render_for_llm,
    SURFACE_CONFIG,
)

__all__ = [
    # outline.py
    "TextSnippet",
    "OutlineNode",
    "Outline",
    "Clipboard",
    "Range",
    "Location",
    "OutlineOperations",
    "create_outline",
    "create_snippet",
    # parser.py
    "RecognizedToken",
    "TokenType",
    "parse_text",
    "extract_tokens",
    "encode_invisible_metadata",
    "decode_invisible_metadata",
    # lens.py
    "FileLens",
    "FocusSpec",
    "create_lens_for_function",
    "create_lens_for_class",
    "create_lens_for_range",
    # portal_bridge.py
    "BridgeState",
    "PortalExpansionResult",
    "OutlinePortalBridge",
    "create_bridge",
    "create_bridge_from_file",
    # renderer.py
    "Surface",
    "RenderConfig",
    "OutlineRenderer",
    "render_outline",
    "render_for_llm",
    "SURFACE_CONFIG",
]
