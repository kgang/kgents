"""
ASHC Crown Jewel: Agentic Self-Hosting Compiler with Proof Generation.

The ASHC service extends evidence compilation to produce formal proofs
that LLMs attempt to discharge. This transforms kgents from statistically
likely correct to provably correct over time.

Heritage: Kleppmann (§12), Polynomial Functors (§10), Stigmergic Cognition (§13)

The Core Insight:
    "LLM hallucinations don't matter for proofs because proof checkers
    reject invalid proofs." — Martin Kleppmann

    The LLM can hallucinate all it wants. The proof checker is the gatekeeper.

The Pipeline:
    Test Failure → ProofObligation → LLM Proof Search → Checker → VerifiedLemma
                                                                      ↓
                                                            Causal Graph (Lemma DB)
                                                                      ↓
                                                            NEXT Generation (uses lemmas)

This creates a ratchet: each failure can add to the corpus of verified facts.

AGENTESE Paths:
    concept.ashc.obligation    → Generate proof obligation from failure
    concept.ashc.prove         → Attempt to discharge obligation
    concept.ashc.lemma         → Query verified lemmas
    concept.ashc.graph         → Visualize lemma dependency graph

Laws:
    1. Soundness: verified(lemma) → property_holds(lemma.property)
    2. Monotonicity: lemmas(t+1) ⊇ lemmas(t)
    3. Compositionality: compose(lemma_a, lemma_b) → valid_proof

See: spec/protocols/proof-generation.md
"""

from .checker import (
    # Exceptions
    CheckerError,
    CheckerUnavailable,
    # Protocol
    ProofChecker,
    # Implementations
    DafnyChecker,
    MockChecker,
    # Registry
    CheckerRegistry,
    available_checkers,
    get_checker,
)
from .contracts import (
    # Checker bridge
    CheckerResult,
    # Type aliases
    LemmaId,
    ObligationId,
    # Enums
    ObligationSource,
    # Core contracts
    ProofAttempt,
    ProofAttemptId,
    ProofObligation,
    # Configuration
    ProofSearchConfig,
    ProofSearchResult,
    ProofStatus,
    VerifiedLemma,
)
from .obligation import (
    # Constants
    MAX_CONTEXT_LINES,
    MAX_CONTEXT_LINE_LENGTH,
    # Extractor
    ObligationExtractor,
    # Convenience function
    extract_from_pytest_report,
)
from .search import (
    # Protocol
    LemmaDatabase,
    # Stub implementation
    InMemoryLemmaDatabase,
    # Searcher
    ProofSearcher,
)
from .persistence import (
    # Postgres implementation (Phase 4)
    PostgresLemmaDatabase,
    LemmaStats,
)

__all__ = [
    # Type aliases
    "ObligationId",
    "LemmaId",
    "ProofAttemptId",
    # Enums
    "ProofStatus",
    "ObligationSource",
    # Core contracts
    "ProofObligation",
    "ProofAttempt",
    "VerifiedLemma",
    "ProofSearchResult",
    # Configuration
    "ProofSearchConfig",
    # Checker bridge
    "CheckerResult",
    # Checker exceptions
    "CheckerUnavailable",
    "CheckerError",
    # Checker protocol
    "ProofChecker",
    # Checker implementations
    "DafnyChecker",
    "MockChecker",
    # Checker registry
    "CheckerRegistry",
    "get_checker",
    "available_checkers",
    # Obligation extraction (Phase 2)
    "ObligationExtractor",
    "extract_from_pytest_report",
    "MAX_CONTEXT_LINES",
    "MAX_CONTEXT_LINE_LENGTH",
    # Proof search (Phase 3)
    "LemmaDatabase",
    "InMemoryLemmaDatabase",
    "ProofSearcher",
    # Postgres persistence (Phase 4)
    "PostgresLemmaDatabase",
    "LemmaStats",
]
