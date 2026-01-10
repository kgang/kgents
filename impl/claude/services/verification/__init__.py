"""
Verification Crown Jewel: Formal Verification Metatheory System.

The Verification service transforms kgents into a self-improving autopilot OS
through practical category-theoretic verification. It provides:

- Graph-based specification analysis (derivation paths from principles to implementation)
- Categorical law verification with LLM-assisted analysis
- Behavioral correctness through enhanced trace witnesses
- Semantic consistency verification across documents
- Self-improvement through automated proposal generation
- HoTT-based unification for isomorphic specifications

AGENTESE Paths (via @node("self.verification")):
- self.verification.manifest     - Verification system status
- self.verification.analyze      - Analyze specification for consistency
- self.verification.suggest      - Generate improvement suggestions
- self.verification.verify_laws  - Verify categorical laws
- self.verification.trace        - Enhanced trace witness collection

The Metaphysical Fullstack Pattern (AD-009):
- VerificationNode wraps VerificationService as AGENTESE node
- Universal gateway auto-exposes all aspects
- Frontend components co-located in web/ directory

See: .kiro/specs/formal-verification-metatheory/
"""

from .categorical_checker import CategoricalChecker
from .contracts import (
    AgentMorphism,
    BehavioralPattern,
    CounterExample,
    HoTTTypeResult,
    ImprovementProposalResult,
    ProposalStatus,
    SemanticConsistencyResult,
    TraceWitnessResult,
    VerificationGraphResult,
    VerificationResult,
    VerificationStatus,
    ViolationType,
)
from .graph_engine import GraphEngine
from .lean_import import (
    LeanProofChecker,
    LeanVerificationEvidence,
    ProofStatus,
    VerificationReport,
    get_constitutional_evidence,
    verify_categorical_laws,
    verify_categorical_laws_sync,
)
from .persistence import VerificationPersistence
from .service import VerificationService

__all__ = [
    # Service (domain logic)
    "VerificationService",
    # Persistence (data access)
    "VerificationPersistence",
    # Graph Engine (derivation analysis)
    "GraphEngine",
    # Categorical Checker (law verification)
    "CategoricalChecker",
    # Contracts (domain types)
    "VerificationStatus",
    "ViolationType",
    "ProposalStatus",
    "VerificationGraphResult",
    "TraceWitnessResult",
    "VerificationResult",
    "ImprovementProposalResult",
    "SemanticConsistencyResult",
    "HoTTTypeResult",
    "AgentMorphism",
    "CounterExample",
    "BehavioralPattern",
    # Lean 4 Formal Verification
    "LeanProofChecker",
    "LeanVerificationEvidence",
    "ProofStatus",
    "VerificationReport",
    "get_constitutional_evidence",
    "verify_categorical_laws",
    "verify_categorical_laws_sync",
]
