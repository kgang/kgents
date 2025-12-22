"""
Exploration Harness: Safety and evidence for hypergraph navigation.

This module provides bounded, evidence-gathering exploration of the
typed-hypergraph context model.

Core Components:
- ExplorationHarness: Main integration point (harness.py)
- NavigationBudget: Resource limits (budget.py)
- LoopDetector: Prevent trivially bad loops (loops.py)
- EvidenceCollector: Gather evidence during exploration (evidence.py)
- ASHCCommitment: Commit claims based on evidence (commitment.py)

Types (types.py):
- Trail, TrailStep: Navigation history
- ContextNode, ContextGraph: Typed-hypergraph navigation
- Evidence, Claim: Evidence from exploration
- Observer: Phenomenological context

Usage:
    from protocols.exploration import (
        ExplorationHarness,
        ContextNode,
        Observer,
        create_harness,
    )

    # Create starting point
    node = ContextNode(path="world.auth_middleware", holon="auth_middleware")
    observer = Observer(id="dev-1", archetype="developer")

    # Create harness
    harness = create_harness(node, observer)

    # Navigate with safety
    result = await harness.navigate("tests")
    if result.success:
        # Record observation
        harness.record_observation("Found comprehensive test coverage")

    # Commit a claim
    claim = Claim(statement="Auth middleware is well-tested")
    commitment = await harness.commit_claim(claim)

Spec References:
- spec/protocols/exploration-harness.md
- spec/protocols/typed-hypergraph.md
- spec/protocols/portal-token.md
"""

# Types
# Budget
from .budget import (
    BudgetExhausted,
    ExhaustionReason,
    NavigationBudget,
    # Presets
    quick_budget,
    standard_budget,
    thorough_budget,
    unlimited_budget,
)

# Commitment
from .commitment import (
    ASHCCommitment,
    CommitmentCheckResult,
    CommitmentRequirements,
)

# Evidence
from .evidence import (
    EvidenceCollector,
    EvidenceScope,
    EvidenceSummary,
    TrailAsEvidence,
)

# Harness
from .harness import (
    ExplorationHarness,
    ExplorationState,
    # Factories
    create_harness,
    quick_harness,
    thorough_harness,
)

# Loops
from .loops import (
    EmbeddingFunction,
    LoopDetector,
    LoopEvent,
    LoopResponse,
    cosine_similarity,
    # Factories
    create_loop_detector,
    relaxed_loop_detector,
    strict_loop_detector,
)
from .types import (
    # Evidence
    Claim,
    CommitmentLevel,
    CommitmentResult,
    ContextGraph,
    # Context
    ContextNode,
    Counterevidence,
    Evidence,
    EvidenceStrength,
    # Enums
    LoopStatus,
    # Results
    NavigationResult,
    # Observer
    Observer,
    # Trail
    Trail,
    TrailStep,
)

__all__ = [
    # === Types ===
    # Enums
    "LoopStatus",
    "CommitmentLevel",
    "CommitmentResult",
    "EvidenceStrength",
    # Observer
    "Observer",
    # Trail
    "Trail",
    "TrailStep",
    # Context
    "ContextNode",
    "ContextGraph",
    # Evidence
    "Claim",
    "Evidence",
    "Counterevidence",
    # Results
    "NavigationResult",
    # === Budget ===
    "NavigationBudget",
    "BudgetExhausted",
    "ExhaustionReason",
    "quick_budget",
    "standard_budget",
    "thorough_budget",
    "unlimited_budget",
    # === Loops ===
    "LoopDetector",
    "LoopResponse",
    "LoopEvent",
    "EmbeddingFunction",
    "cosine_similarity",
    "create_loop_detector",
    "strict_loop_detector",
    "relaxed_loop_detector",
    # === Evidence ===
    "TrailAsEvidence",
    "EvidenceCollector",
    "EvidenceScope",
    "EvidenceSummary",
    # === Commitment ===
    "ASHCCommitment",
    "CommitmentRequirements",
    "CommitmentCheckResult",
    # === Harness ===
    "ExplorationHarness",
    "ExplorationState",
    "create_harness",
    "quick_harness",
    "thorough_harness",
]
