"""
Living Spec Crown Jewel: Unified Transactional Specification Editing.

The Living Spec service unifies five previously separate specs into one coherent system:
- Interactive Text (tokens, affordances, semantic recognition)
- K-Block (transactional editing, monadic isolation)
- Portal Token (expandable hyperedges, inline navigation)
- Typed-Hypergraph (ContextNode, observer-dependent edges)
- Witness (decision traces, reasoning capture)

The unifying formula:

    LIVING SPEC = HYPERGRAPH × TOKENS × MONAD × WITNESS

AGENTESE Paths (via @node("self.spec")):
- self.spec.manifest     - View spec with tokens and hyperedges
- self.spec.edit         - Enter editing monad (create K-Block)
- self.spec.commit       - Exit monad with witness trace
- self.spec.navigate     - Follow hyperedge to related specs
- self.spec.expand       - Inline portal expansion

Core Concepts:
- SpecNode: Unified hypergraph node with token affordances
- SpecToken: Seven token types (AGENTESE, Task, Portal, Code, Image, Principle, Requirement)
- SpecMonad: Monadic isolation for fearless editing
- SpecPolynomial: Unified state machine (VIEWING → EDITING → WITNESSING)
- SpecSheaf: Multi-view coherence (Prose ↔ Graph ↔ Code)

Philosophy:
    "Five specs become one. The bramble becomes a garden."

    "The spec is not description—it is generative.
     The text is not passive—it is interface."

See: spec/protocols/SYNTHESIS-living-spec.md

Teaching:
    gotcha: SpecNode is lazy—content and tokens load only on access.
            Always await node.content() and node.tokens() before use.
            (Evidence: test_spec_node.py::test_lazy_loading)

    gotcha: SpecMonad wraps KBlock but IS NOT a KBlock. Use monad.kblock
            property to access underlying KBlock for view operations.
            (Evidence: test_monad.py::test_kblock_access)

    gotcha: SpecPolynomial has 8 states, not 4. HOVERING, EXPANDING,
            NAVIGATING, WITNESSING are new vs DocumentPolynomial.
            (Evidence: test_polynomial.py::test_all_states)

    gotcha: Portal tokens have their own state machine (COLLAPSED → EXPANDED).
            This composes with SpecPolynomial—portal can expand in VIEWING state.
            (Evidence: test_portal_token.py::test_portal_in_viewing)
"""

from .contracts import (
    # Result types
    CommitResult,
    # Delta types
    ContentDelta,
    EditDelta,
    # Core types
    IsolationState,
    # Observer types
    Observer,
    ObserverDensity,
    SemanticDelta,
    SpecKind,
)
from .node import SpecNode
from .polynomial import Effect, SpecPolynomial, SpecState
from .tokens import (
    SPEC_TOKEN_TYPES,
    PortalSpecToken,
    SpecToken,
)

__all__ = [
    # Core types
    "IsolationState",
    "SpecKind",
    "Observer",
    "ObserverDensity",
    "CommitResult",
    "ContentDelta",
    "EditDelta",
    "SemanticDelta",
    # Node
    "SpecNode",
    # Polynomial
    "SpecPolynomial",
    "SpecState",
    "Effect",
    # Tokens
    "SpecToken",
    "PortalSpecToken",
    "SPEC_TOKEN_TYPES",
]
