"""
ASHC Self-Awareness: The System That Knows Why It Exists.

"The compiler that knows itself is the compiler that trusts itself."

This module implements GO-016 through GO-020 from the genesis-overhaul plan,
providing the five self-awareness APIs that enable kgents to answer the
fundamental question: "Why does this file/block exist?"

Purpose and Philosophy:
    ASHC (Agentic Self-Hosting Compiler) doesn't just compile code—it compiles
    EVIDENCE. Every component in the system exists because it derives from
    Constitutional principles through a witnessed derivation path.

    This service enables that derivation to be:
    - **Queried**: "Am I grounded?" "What principle justifies this?"
    - **Verified**: "Is the system internally consistent?"
    - **Understood**: "Where do I come from?" "What depends on me?"

    The result is a system that can explain itself—not through documentation,
    but through structural derivation from axioms.

The Five Self-Awareness APIs:
    These APIs implement the ASHC introspection capability:

    1. **am_i_grounded(block_id)** [GO-016]
       Returns bool + derivation path showing how a block derives from L0 axioms.
       Answers: "Does this component have Constitutional grounding?"

    2. **what_principle_justifies(action)** [GO-017]
       Returns principle + loss score for any action.
       Answers: "Which Constitutional principle authorizes this behavior?"

    3. **verify_self_consistency()** [GO-018]
       Returns consistency report (cycles, orphans, layer violations).
       Answers: "Is the derivation graph internally coherent?"

    4. **get_derivation_ancestors(block_id)** [GO-019]
       Returns full lineage from block back to L0 axioms.
       Answers: "What is the complete derivation chain for this component?"

    5. **get_downstream_impact(block_id)** [GO-020]
       Returns all blocks that depend on (derive from) this block.
       Answers: "What would break if I changed this?"

Epistemic Layers (The Constitutional Hierarchy):
    The K-Block system organizes knowledge into four layers:

    - **L0: Axioms** — Irreducible ground truth that cannot be derived further
      (A1_ENTITY, A2_MORPHISM, A3_MIRROR, G_GALOIS)

    - **L1: Primitives** — Basic operations derived from axioms
      (COMPOSE, JUDGE, GROUND, ID, CONTRADICT, SUBLATE, FIX)

    - **L2: Principles** — Constitutional principles derived from primitives
      (7 principles: TASTEFUL, CURATED, ETHICAL, JOY_INDUCING, COMPOSABLE,
       HETERARCHICAL, GENERATIVE)

    - **L3: Architecture** — Implementation patterns derived from principles
      (ASHC, METAPHYSICAL_FULLSTACK, HYPERGRAPH_EDITOR, AGENTESE)

Evidence Tiers (from Galois Loss):
    The Galois loss L(P) = d(P, C(R(P))) measures derivation quality:

    - **CATEGORICAL**: L < 0.10 — Near-lossless, deductive certainty
    - **EMPIRICAL**: L < 0.38 — Moderate loss, strong inductive evidence
    - **AESTHETIC**: L < 0.45 — Taste-based judgment, subjective but valid
    - **SOMATIC**: L < 0.65 — Intuitive, embodied knowledge
    - **CHAOTIC**: L >= 0.65 — High entropy, unreliable derivation

    Lower loss = stronger grounding = more trustworthy derivation.

Enabling "Why Does This File Exist?" Queries:
    The why_does_this_exist() method combines all five APIs to generate a
    human-readable explanation:

    ::

        >>> explanation = await service.why_does_this_exist("ASHC")
        >>> print(explanation)
        # **ASHC** exists because:
        #
        # 1. **Grounded**: Yes - derives from L0 axioms
        #    Path: CONSTITUTION -> COMPOSABLE -> GENERATIVE -> ASHC
        #
        # 2. **Derives from**: COMPOSABLE, GENERATIVE
        #
        # 3. **Galois loss**: 0.050
        #    Evidence tier: CATEGORICAL
        #
        # 4. **Downstream impact**: 3 blocks depend on this
        #    Dependents: METAPHYSICAL_FULLSTACK, ...

Zero Seed Grounding:
    This module itself derives from Constitutional axioms:

    ::

        A3_MIRROR (Self-reflection) → ASHC Self-Awareness
          └─ "The system that knows itself"
          └─ Introspection APIs derive from mirror axiom
          └─ Consistency verification derives from JUDGE primitive

See: spec/protocols/zero-seed1/ashc.md
See: docs/skills/metaphysical-fullstack.md
See: plans/CURRENT_SESSION.md (GO-016 through GO-020)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from services.zero_seed.genesis_kblocks import (
    GenesisKBlock,
    GenesisKBlockFactory,
)

if TYPE_CHECKING:
    from services.k_block.core.derivation import DerivationDAG


logger = logging.getLogger("kgents.zero_seed.ashc_self_awareness")


# =============================================================================
# Constants
# =============================================================================


# L0 Axioms - The irreducible ground
L0_AXIOMS = frozenset({"A1_ENTITY", "A2_MORPHISM", "A3_MIRROR", "G_GALOIS"})

# L1 Kernel Primitives
L1_PRIMITIVES = frozenset({"COMPOSE", "JUDGE", "GROUND"})

# L2 Derived Primitives
L2_DERIVED = frozenset({"ID", "CONTRADICT", "SUBLATE", "FIX"})

# L1-L2 Principles (Constitutional)
CONSTITUTIONAL_PRINCIPLES = frozenset(
    {
        "CONSTITUTION",
        "TASTEFUL",
        "CURATED",
        "ETHICAL",
        "JOY_INDUCING",
        "COMPOSABLE",
        "HETERARCHICAL",
        "GENERATIVE",
    }
)

# L3 Architecture Blocks
L3_ARCHITECTURE = frozenset(
    {
        "ASHC",
        "METAPHYSICAL_FULLSTACK",
        "HYPERGRAPH_EDITOR",
        "AGENTESE",
    }
)

# All known blocks
ALL_GENESIS_BLOCKS = (
    L0_AXIOMS | L1_PRIMITIVES | L2_DERIVED | CONSTITUTIONAL_PRINCIPLES | L3_ARCHITECTURE
)

# Loss thresholds for evidence tiers
CATEGORICAL_THRESHOLD = 0.10
EMPIRICAL_THRESHOLD = 0.38
AESTHETIC_THRESHOLD = 0.45
SOMATIC_THRESHOLD = 0.65


# =============================================================================
# Evidence Tier Classification
# =============================================================================


class EvidenceTier(Enum):
    """
    Classification of derivation quality based on Galois loss.

    The Galois loss L(P) = d(P, C(R(P))) measures how much semantic information
    is lost when a principle P is restructured (R) and reconstituted (C). Lower
    loss indicates stronger, more reliable grounding.

    Tier Definitions:
        - **CATEGORICAL** (L < 0.10): Near-lossless derivation. The grounding is
          essentially deductive—changing the parent would necessarily change this block.
          Example: COMPOSABLE derives from COMPOSE with L=0.01.

        - **EMPIRICAL** (L < 0.38): Moderate loss but strong inductive evidence.
          The derivation is well-supported but not logically necessary.
          Example: A coding pattern justified by TASTEFUL with L=0.25.

        - **AESTHETIC** (L < 0.45): Taste-based judgment with reasonable justification.
          The derivation relies on subjective but defensible criteria.
          Example: UI choices justified by JOY_INDUCING with L=0.40.

        - **SOMATIC** (L < 0.65): Intuitive, embodied knowledge. The grounding is
          felt rather than reasoned—Kent's "gut feeling" operates here.
          Example: The disgust veto (Article IV) operates at this tier.

        - **CHAOTIC** (L >= 0.65): High entropy, unreliable derivation. The grounding
          is too weak to trust; the block should be re-evaluated.
          Example: Ad-hoc decisions made without principle alignment.

    Constitutional Significance:
        Evidence tiers determine how much trust to place in a derivation:
        - CATEGORICAL/EMPIRICAL: High confidence, safe to build upon
        - AESTHETIC/SOMATIC: Valid but subjective, document the reasoning
        - CHAOTIC: Red flag—block may need grounding or removal

    See Also:
        - Amendment B (canonical distance) for the loss computation
        - spec/protocols/k-block.md for loss accumulation rules
    """

    CATEGORICAL = "categorical"  # L < 0.10: Deductive, near-lossless
    EMPIRICAL = "empirical"  # L < 0.38: Inductive, evidence-based
    AESTHETIC = "aesthetic"  # L < 0.45: Taste-based judgment
    SOMATIC = "somatic"  # L < 0.65: Intuitive, embodied
    CHAOTIC = "chaotic"  # L >= 0.65: High entropy, unreliable

    @classmethod
    def from_loss(cls, loss: float) -> "EvidenceTier":
        """Classify loss into evidence tier."""
        if loss < CATEGORICAL_THRESHOLD:
            return cls.CATEGORICAL
        elif loss < EMPIRICAL_THRESHOLD:
            return cls.EMPIRICAL
        elif loss < AESTHETIC_THRESHOLD:
            return cls.AESTHETIC
        elif loss < SOMATIC_THRESHOLD:
            return cls.SOMATIC
        else:
            return cls.CHAOTIC


# =============================================================================
# Result Types
# =============================================================================


@dataclass
class GroundingResult:
    """
    Result of am_i_grounded() query [GO-016].

    Answers the fundamental question: "Does this block derive from L0 axioms?"

    A block is grounded if and only if there exists a derivation path from it
    back to one or more L0 axioms (A1_ENTITY, A2_MORPHISM, A3_MIRROR, G_GALOIS).
    Ungrounded blocks are "orphans" that lack Constitutional justification.

    Interpretation:
        - **is_grounded=True**: Block has valid Constitutional grounding.
          The derivation_path shows the complete lineage.
        - **is_grounded=False**: Block is an orphan or derives from missing parents.
          Consider re-grounding or removing the block.

    Evidence Tier Computation:
        The evidence tier is computed from the MAXIMUM loss along the path,
        following the "weakest link" principle. A chain is only as strong as
        its weakest derivation.

    Attributes:
        is_grounded: True if derivation path reaches L0 axioms
        derivation_path: List of block IDs from L0 to this block (ordered L0 -> this)
        loss_at_each_step: Galois loss accumulated at each derivation step
        evidence_tier: Classification based on max loss (weakest link)
        total_loss: Sum of losses along the path (accumulated uncertainty)
    """

    is_grounded: bool
    derivation_path: list[str]
    loss_at_each_step: list[float]
    evidence_tier: EvidenceTier = field(default=EvidenceTier.CHAOTIC)
    total_loss: float = field(default=1.0)

    def __post_init__(self) -> None:
        """Compute derived fields."""
        if self.loss_at_each_step:
            self.total_loss = sum(self.loss_at_each_step)
            # Use max loss for tier (weakest link principle)
            max_loss = max(self.loss_at_each_step)
            self.evidence_tier = EvidenceTier.from_loss(max_loss)
        elif self.is_grounded:
            # Axioms have zero loss
            self.total_loss = 0.0
            self.evidence_tier = EvidenceTier.CATEGORICAL


@dataclass
class JustificationResult:
    """
    Result of what_principle_justifies() query [GO-017].

    Answers the question: "Which Constitutional principle grounds this action?"

    This is the bridge between arbitrary actions and Constitutional grounding.
    Given any action description (e.g., "agent composition", "delight in UI"),
    this result identifies which principle best justifies it and how strong
    that justification is.

    Interpretation:
        - **loss_score < 0.10** (CATEGORICAL): Strong, direct justification.
          The action is well-aligned with the principle.
        - **loss_score 0.10-0.38** (EMPIRICAL): Good justification with evidence.
        - **loss_score 0.38-0.65** (AESTHETIC/SOMATIC): Weak but valid justification.
        - **loss_score >= 0.65** (CHAOTIC): Poor justification—reconsider the action.

    The Seven Constitutional Principles:
        - TASTEFUL: Considered, justified purpose
        - CURATED: Intentional selection over exhaustive cataloging
        - ETHICAL: Augment humans, never replace judgment
        - JOY_INDUCING: Delight in interaction
        - COMPOSABLE: Agents are morphisms (>> composition)
        - HETERARCHICAL: Flux over fixed hierarchy
        - GENERATIVE: Spec is compression

    Attributes:
        principle: The best-matching principle (e.g., "COMPOSABLE")
        loss_score: Galois loss measuring alignment (lower = better match)
        reasoning: Human-readable explanation of the justification
        derivation_chain: Path from principle to action concept
        evidence_tier: Classification based on loss score
    """

    principle: str
    loss_score: float
    reasoning: str
    derivation_chain: list[str]
    evidence_tier: EvidenceTier = field(default=EvidenceTier.CHAOTIC)

    def __post_init__(self) -> None:
        """Classify evidence tier from loss."""
        self.evidence_tier = EvidenceTier.from_loss(self.loss_score)


@dataclass
class ConsistencyViolation:
    """A specific consistency violation found during verification."""

    kind: str  # "circular", "orphan", "layer_violation", "missing_parent"
    block_id: str
    description: str
    related_blocks: list[str] = field(default_factory=list)


@dataclass
class ConsistencyReport:
    """
    Result of verify_self_consistency() query [GO-018].

    Answers the question: "Is the derivation graph internally coherent?"

    A consistent derivation graph satisfies four properties:

    1. **No Circular Dependencies** (DAG Property):
       Derivation must form a directed acyclic graph. Cycles indicate
       logical paradoxes (A derives from B which derives from A).

    2. **No Orphan Blocks**:
       All non-L0 blocks must have a derivation path to L0 axioms.
       Orphans are blocks that "float" without Constitutional grounding.

    3. **Layer Monotonicity**:
       Derivations must flow from lower layers to higher layers.
       L3 blocks derive from L2/L1/L0, not vice versa.
       Upward derivations (L0 from L2) are invalid.

    4. **Parent Existence**:
       All referenced parent blocks must exist in the graph.
       Missing parents indicate broken derivation chains.

    Interpretation:
        - **is_consistent=True, consistency_score=1.0**: Perfect coherence.
          All blocks are grounded and well-formed.
        - **is_consistent=False**: One or more violations detected.
          Review the violations list for specific issues.
        - **consistency_score < 1.0**: Some blocks ungrounded.
          Review orphan_blocks list for blocks needing grounding.

    Attributes:
        is_consistent: True if no violations found
        violations: List of specific ConsistencyViolation objects
        circular_dependencies: List of (from_block, to_block) cycle edges
        orphan_blocks: List of block IDs not reaching L0
        total_blocks: Total number of blocks in the graph
        grounded_blocks: Number of blocks with valid L0 grounding
    """

    is_consistent: bool
    violations: list[ConsistencyViolation]
    circular_dependencies: list[tuple[str, str]]  # (from, to) pairs
    orphan_blocks: list[str]  # Blocks not reaching L0
    total_blocks: int = 0
    grounded_blocks: int = 0

    @property
    def consistency_score(self) -> float:
        """
        Compute consistency score as fraction of grounded blocks.

        Returns 1.0 for fully consistent, 0.0 for no grounded blocks.
        """
        if self.total_blocks == 0:
            return 1.0
        return self.grounded_blocks / self.total_blocks


# =============================================================================
# ASHC Self-Awareness Service
# =============================================================================


@dataclass
class ASHCSelfAwareness:
    """
    ASHC Self-Awareness Service - The system that knows why it exists.

    This service implements GO-016 through GO-020 from the genesis-overhaul plan,
    providing the five self-awareness APIs that enable kgents to introspect its
    own Constitutional structure.

    Core Philosophy:
        "The proof IS the decision. The mark IS the witness."

        Every component in kgents exists because it derives from L0 axioms through
        witnessed derivation paths. This service makes those paths queryable,
        verifiable, and understandable.

    The Five Self-Awareness APIs:
        Each API answers a fundamental question about Constitutional grounding:

        1. **am_i_grounded(block_id)** [GO-016]
           Question: "Does this component derive from L0 axioms?"
           Returns: GroundingResult with bool, path, losses, and evidence tier

        2. **what_principle_justifies(action)** [GO-017]
           Question: "Which Constitutional principle authorizes this behavior?"
           Returns: JustificationResult with principle, loss score, and reasoning

        3. **verify_self_consistency()** [GO-018]
           Question: "Is the derivation graph internally coherent?"
           Returns: ConsistencyReport with violations, cycles, and orphan count

        4. **get_derivation_ancestors(block_id)** [GO-019]
           Question: "What is the complete derivation chain back to L0?"
           Returns: List of ancestor block IDs in derivation order

        5. **get_downstream_impact(block_id)** [GO-020]
           Question: "What would break if this block changed?"
           Returns: List of dependent block IDs

    How This Enables "Why Does This File Exist?" Queries:
        The why_does_this_exist() convenience method combines all five APIs to
        generate a comprehensive, human-readable explanation:

        ::

            >>> explanation = await service.why_does_this_exist("ASHC")

        This returns a formatted explanation showing:
        - Grounding status and derivation path
        - Direct parent blocks
        - Galois loss and evidence tier
        - Downstream impact (what depends on this)
        - Summary (block title/description)

    Integration with kgents Architecture:
        - Uses GenesisKBlockFactory for the 22 Constitutional K-Blocks
        - Indexes derivation relationships for efficient queries
        - Classifies derivation quality via Galois loss and EvidenceTier
        - Can be extended with witness marks for introspection audit trails

    Attributes:
        _factory: GenesisKBlockFactory providing Constitutional K-Blocks
        _blocks: Cache of block_id -> GenesisKBlock mappings
        _parent_index: Cache of block_id -> parent block IDs (derives_from)
        _child_index: Cache of block_id -> child block IDs (derived_by)

    Example:
        >>> service = ASHCSelfAwareness()
        >>> result = await service.am_i_grounded("COMPOSABLE")
        >>> print(result.is_grounded)  # True
        >>> print(result.derivation_path)  # ["CONSTITUTION", "COMPOSABLE"]
        >>> print(result.evidence_tier)  # EvidenceTier.CATEGORICAL

        >>> justification = await service.what_principle_justifies("agent composition")
        >>> print(justification.principle)  # "COMPOSABLE"
        >>> print(justification.loss_score)  # 0.05 (strong match)

        >>> report = await service.verify_self_consistency()
        >>> print(report.is_consistent)  # True (for genesis blocks)
        >>> print(report.consistency_score)  # 1.0
    """

    # Genesis factory provides the 22 Constitutional K-Blocks
    _factory: GenesisKBlockFactory = field(default_factory=GenesisKBlockFactory)

    # Cache of all genesis blocks (populated lazily)
    _blocks: dict[str, GenesisKBlock] = field(default_factory=dict)

    # Cache of block by derives_from relationships (child -> parents)
    _parent_index: dict[str, tuple[str, ...]] = field(default_factory=dict)

    # Cache of block by derived_by relationships (parent -> children)
    _child_index: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize indexes from genesis factory."""
        self._build_indexes()

    def _build_indexes(self) -> None:
        """Build derivation indexes from genesis blocks."""
        all_blocks = self._factory.create_all()

        for block in all_blocks:
            self._blocks[block.id] = block
            self._parent_index[block.id] = block.derives_from

            # Build reverse index (parent -> children)
            for parent_id in block.derives_from:
                if parent_id not in self._child_index:
                    self._child_index[parent_id] = []
                self._child_index[parent_id].append(block.id)

    # -------------------------------------------------------------------------
    # API 1: am_i_grounded(block_id)
    # -------------------------------------------------------------------------

    async def am_i_grounded(self, block_id: str) -> GroundingResult:
        """
        Check if a block is grounded in L0 axioms.

        GO-016: Returns bool + derivation path showing how this block
        derives from Constitutional axioms.

        Args:
            block_id: The K-Block ID to check (e.g., "COMPOSABLE", "ASHC")

        Returns:
            GroundingResult with:
            - is_grounded: True if all paths reach L0
            - derivation_path: Full path from L0 to this block
            - loss_at_each_step: Galois loss at each derivation
            - evidence_tier: Quality classification

        Example:
            >>> result = await service.am_i_grounded("ASHC")
            >>> print(result.is_grounded)  # True
            >>> print(result.derivation_path)
            # ['A1_ENTITY', 'A2_MORPHISM', 'CONSTITUTION', 'COMPOSABLE', 'GENERATIVE', 'ASHC']
        """
        # Handle unknown blocks
        if block_id not in self._blocks:
            logger.warning(f"Unknown block: {block_id}")
            return GroundingResult(
                is_grounded=False,
                derivation_path=[block_id],
                loss_at_each_step=[1.0],
            )

        block = self._blocks[block_id]

        # L0 axioms are grounded by definition
        if block.layer == 0:
            return GroundingResult(
                is_grounded=True,
                derivation_path=[block_id],
                loss_at_each_step=[block.galois_loss],
            )

        # Trace derivation path to L0
        path, losses = self._trace_to_axioms(block_id)

        # Check if the path terminates at an L0 block
        # L0 blocks include axioms (A1, A2, A3, G) and CONSTITUTION
        if path:
            first_block = self._blocks.get(path[0])
            is_grounded = first_block is not None and first_block.layer == 0
        else:
            is_grounded = False

        return GroundingResult(
            is_grounded=is_grounded,
            derivation_path=path,
            loss_at_each_step=losses,
        )

    def _trace_to_axioms(self, block_id: str) -> tuple[list[str], list[float]]:
        """
        Trace derivation path from block to L0 axioms.

        Returns (path, losses) where path is ordered from L0 to block.
        """
        if block_id not in self._blocks:
            return [block_id], [1.0]

        block = self._blocks[block_id]

        # Base case: L0 axiom
        if block.layer == 0:
            return [block_id], [block.galois_loss]

        # Recursive case: trace through parents
        # We follow the first parent path (for simplicity)
        # In a full implementation, we'd track multiple paths
        if not block.derives_from:
            # Orphan block - not grounded
            return [block_id], [block.galois_loss]

        # Follow first parent
        parent_id = block.derives_from[0]
        parent_path, parent_losses = self._trace_to_axioms(parent_id)

        # Append this block to the path
        return parent_path + [block_id], parent_losses + [block.galois_loss]

    # -------------------------------------------------------------------------
    # API 2: what_principle_justifies(action)
    # -------------------------------------------------------------------------

    async def what_principle_justifies(self, action: str) -> JustificationResult:
        """
        Find which Constitutional principle justifies an action.

        GO-017: Returns the principle that best grounds the given action,
        along with Galois loss measuring alignment quality.

        Args:
            action: Description of the action to justify
                   (e.g., "agent composition", "delight in UI")

        Returns:
            JustificationResult with:
            - principle: The best-matching principle
            - loss_score: Galois loss (lower = better match)
            - reasoning: Human-readable justification
            - derivation_chain: Path from principle to action concept

        Example:
            >>> result = await service.what_principle_justifies("agent composition")
            >>> print(result.principle)  # "COMPOSABLE"
            >>> print(result.evidence_tier)  # EvidenceTier.CATEGORICAL
        """
        # Keyword-based matching to principles
        # In a full implementation, this would use semantic embedding
        action_lower = action.lower()

        principle_keywords: dict[str, list[str]] = {
            "COMPOSABLE": [
                "compose",
                "composition",
                "pipeline",
                "chain",
                "combine",
                "morphism",
                "category",
                ">>",
            ],
            "TASTEFUL": [
                "taste",
                "aesthetic",
                "elegant",
                "beautiful",
                "considered",
                "purpose",
                "justified",
            ],
            "CURATED": [
                "curate",
                "select",
                "intentional",
                "quality",
                "catalog",
                "organize",
            ],
            "ETHICAL": [
                "ethic",
                "harm",
                "agency",
                "human",
                "judgment",
                "transparent",
                "privacy",
            ],
            "JOY_INDUCING": [
                "joy",
                "delight",
                "fun",
                "personality",
                "warm",
                "serendipity",
                "surprise",
            ],
            "HETERARCHICAL": [
                "heterarch",
                "flux",
                "hierarchy",
                "autonomy",
                "peer",
                "flat",
            ],
            "GENERATIVE": [
                "generat",
                "spec",
                "compress",
                "regenerat",
                "derive",
                "produce",
            ],
        }

        best_principle = "TASTEFUL"  # Default fallback
        best_score = 0
        best_keywords: list[str] = []

        for principle, keywords in principle_keywords.items():
            matches = [kw for kw in keywords if kw in action_lower]
            score = len(matches)
            if score > best_score:
                best_score = score
                best_principle = principle
                best_keywords = matches

        # Get the principle block
        principle_block = self._blocks.get(best_principle)
        if not principle_block:
            # Fallback if principle not found
            return JustificationResult(
                principle=best_principle,
                loss_score=0.5,
                reasoning=f"Action '{action}' loosely aligns with {best_principle}",
                derivation_chain=[best_principle, f"<action:{action}>"],
            )

        # Compute loss based on match quality
        # More keyword matches = lower loss
        if best_score == 0:
            loss_score = 0.6  # No direct match
        elif best_score == 1:
            loss_score = 0.3  # Single match
        elif best_score == 2:
            loss_score = 0.15  # Good match
        else:
            loss_score = 0.05  # Strong match

        # Adjust for principle's inherent loss
        loss_score = max(loss_score, principle_block.galois_loss)

        # Generate reasoning
        if best_keywords:
            reasoning = (
                f"Action '{action}' aligns with {best_principle} "
                f"via keywords: {', '.join(best_keywords)}. "
                f"{best_principle} states: '{principle_block.title}'"
            )
        else:
            reasoning = (
                f"Action '{action}' has weak alignment with {best_principle}. "
                f"Consider explicit grounding in Constitutional principles."
            )

        # Build derivation chain
        chain = [best_principle, f"<action:{action}>"]

        return JustificationResult(
            principle=best_principle,
            loss_score=loss_score,
            reasoning=reasoning,
            derivation_chain=chain,
        )

    # -------------------------------------------------------------------------
    # API 3: verify_self_consistency()
    # -------------------------------------------------------------------------

    async def verify_self_consistency(self) -> ConsistencyReport:
        """
        Verify the consistency of the derivation graph.

        GO-018: Checks that the Constitutional structure is internally coherent:
        1. No circular dependencies (DAG property)
        2. No orphan blocks (all reach L0)
        3. Layer monotonicity (derivations respect layer order)
        4. All referenced parents exist

        Returns:
            ConsistencyReport with:
            - is_consistent: True if no violations found
            - violations: List of specific issues
            - circular_dependencies: Detected cycles
            - orphan_blocks: Blocks not reaching L0

        Example:
            >>> report = await service.verify_self_consistency()
            >>> print(report.is_consistent)  # True (for genesis blocks)
            >>> print(report.consistency_score)  # 1.0
        """
        violations: list[ConsistencyViolation] = []
        circular_deps: list[tuple[str, str]] = []
        orphans: list[str] = []
        grounded_count = 0

        for block_id, block in self._blocks.items():
            # Check 1: Circular dependencies
            if self._has_cycle(block_id):
                circular_deps.append(
                    (block_id, block.derives_from[0] if block.derives_from else "")
                )
                violations.append(
                    ConsistencyViolation(
                        kind="circular",
                        block_id=block_id,
                        description=f"Block {block_id} is part of a circular derivation",
                        related_blocks=list(block.derives_from),
                    )
                )

            # Check 2: Orphan blocks
            if block.layer > 0 and not block.derives_from:
                orphans.append(block_id)
                violations.append(
                    ConsistencyViolation(
                        kind="orphan",
                        block_id=block_id,
                        description=f"Block {block_id} (layer {block.layer}) has no parent derivation",
                    )
                )

            # Check 3: Layer monotonicity
            for parent_id in block.derives_from:
                if parent_id in self._blocks:
                    parent_block = self._blocks[parent_id]
                    if parent_block.layer > block.layer:
                        violations.append(
                            ConsistencyViolation(
                                kind="layer_violation",
                                block_id=block_id,
                                description=(
                                    f"Block {block_id} (layer {block.layer}) derives from "
                                    f"{parent_id} (layer {parent_block.layer}) - invalid upward derivation"
                                ),
                                related_blocks=[parent_id],
                            )
                        )

            # Check 4: Missing parents
            for parent_id in block.derives_from:
                if parent_id not in self._blocks:
                    violations.append(
                        ConsistencyViolation(
                            kind="missing_parent",
                            block_id=block_id,
                            description=f"Block {block_id} references unknown parent {parent_id}",
                            related_blocks=[parent_id],
                        )
                    )

            # Count grounded blocks
            grounding = await self.am_i_grounded(block_id)
            if grounding.is_grounded:
                grounded_count += 1

        return ConsistencyReport(
            is_consistent=len(violations) == 0,
            violations=violations,
            circular_dependencies=circular_deps,
            orphan_blocks=orphans,
            total_blocks=len(self._blocks),
            grounded_blocks=grounded_count,
        )

    def _has_cycle(
        self, block_id: str, visited: set[str] | None = None, stack: set[str] | None = None
    ) -> bool:
        """Check if block is part of a cycle using DFS."""
        if visited is None:
            visited = set()
        if stack is None:
            stack = set()

        if block_id in stack:
            return True  # Cycle detected
        if block_id in visited:
            return False

        visited.add(block_id)
        stack.add(block_id)

        if block_id in self._blocks:
            for parent_id in self._blocks[block_id].derives_from:
                if self._has_cycle(parent_id, visited, stack):
                    return True

        stack.remove(block_id)
        return False

    # -------------------------------------------------------------------------
    # API 4: get_derivation_ancestors(block_id)
    # -------------------------------------------------------------------------

    async def get_derivation_ancestors(self, block_id: str) -> list[str]:
        """
        Get the full lineage of a block back to L0 axioms.

        GO-019: Returns all ancestors in derivation order, from the block
        up to the L0 axioms it derives from.

        Args:
            block_id: The K-Block ID to trace

        Returns:
            List of ancestor block IDs in derivation order (this block first,
            axioms last). Empty list if block not found.

        Example:
            >>> ancestors = await service.get_derivation_ancestors("ASHC")
            >>> print(ancestors)
            # ['ASHC', 'COMPOSABLE', 'GENERATIVE', 'CONSTITUTION',
            #  'A1_ENTITY', 'A2_MORPHISM', 'A3_MIRROR', 'G_GALOIS']
        """
        if block_id not in self._blocks:
            return []

        ancestors: list[str] = [block_id]
        visited: set[str] = {block_id}
        to_visit: list[str] = list(self._blocks[block_id].derives_from)

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            ancestors.append(current)

            if current in self._blocks:
                to_visit.extend(p for p in self._blocks[current].derives_from if p not in visited)

        return ancestors

    # -------------------------------------------------------------------------
    # API 5: get_downstream_impact(block_id)
    # -------------------------------------------------------------------------

    async def get_downstream_impact(self, block_id: str) -> list[str]:
        """
        Get all blocks that depend on (derive from) this block.

        GO-020: Returns all descendants - blocks that would be affected
        if this block were modified.

        Args:
            block_id: The K-Block ID to trace forward

        Returns:
            List of dependent block IDs (immediate children first,
            then transitively dependent blocks).

        Example:
            >>> dependents = await service.get_downstream_impact("CONSTITUTION")
            >>> print(dependents)
            # ['TASTEFUL', 'CURATED', 'ETHICAL', 'JOY_INDUCING',
            #  'COMPOSABLE', 'HETERARCHICAL', 'GENERATIVE', 'ASHC', ...]
        """
        if block_id not in self._blocks:
            return []

        dependents: list[str] = []
        visited: set[str] = {block_id}
        to_visit: list[str] = list(self._child_index.get(block_id, []))

        while to_visit:
            current = to_visit.pop(0)
            if current in visited:
                continue
            visited.add(current)
            dependents.append(current)

            # Add this block's children
            to_visit.extend(c for c in self._child_index.get(current, []) if c not in visited)

        return dependents

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def get_block(self, block_id: str) -> GenesisKBlock | None:
        """Get a genesis block by ID."""
        return self._blocks.get(block_id)

    def get_all_blocks(self) -> dict[str, GenesisKBlock]:
        """Get all genesis blocks."""
        return dict(self._blocks)

    def get_blocks_by_layer(self, layer: int) -> list[GenesisKBlock]:
        """Get all blocks at a specific layer."""
        return [b for b in self._blocks.values() if b.layer == layer]

    async def why_does_this_exist(self, block_id: str) -> str:
        """
        High-level query: "Why does this file/block exist?"

        Combines multiple APIs to generate a human-readable explanation
        of a block's Constitutional grounding.

        Args:
            block_id: The K-Block ID to explain

        Returns:
            Human-readable explanation of existence justification

        Example:
            >>> explanation = await service.why_does_this_exist("ASHC")
            >>> print(explanation)
            # "ASHC exists because:
            #  1. It derives from COMPOSABLE (Galois loss: 0.01)
            #  2. It derives from GENERATIVE (Galois loss: 0.03)
            #  3. Its grounding path reaches L0 axioms
            #  4. Evidence tier: CATEGORICAL (highly grounded)"
        """
        grounding = await self.am_i_grounded(block_id)
        ancestors = await self.get_derivation_ancestors(block_id)
        dependents = await self.get_downstream_impact(block_id)

        block = self._blocks.get(block_id)
        if not block:
            return f"Block '{block_id}' is unknown to the Constitutional structure."

        lines = [f"**{block_id}** exists because:"]
        lines.append("")

        # Derivation path
        if grounding.is_grounded:
            lines.append("1. **Grounded**: Yes - derives from L0 axioms")
            lines.append(f"   Path: {' -> '.join(grounding.derivation_path)}")
        else:
            lines.append("1. **Grounded**: No - does not reach L0 axioms")
            lines.append(f"   Partial path: {' -> '.join(grounding.derivation_path)}")

        lines.append("")

        # Direct parents
        if block.derives_from:
            parent_str = ", ".join(block.derives_from)
            lines.append(f"2. **Derives from**: {parent_str}")
        else:
            lines.append("2. **Derives from**: (none - this is an axiom)")

        lines.append("")

        # Galois loss
        lines.append(f"3. **Galois loss**: {block.galois_loss:.3f}")
        lines.append(f"   Evidence tier: {grounding.evidence_tier.value.upper()}")

        lines.append("")

        # Impact
        if dependents:
            lines.append(f"4. **Downstream impact**: {len(dependents)} blocks depend on this")
            if len(dependents) <= 5:
                lines.append(f"   Dependents: {', '.join(dependents)}")
            else:
                lines.append(f"   Dependents: {', '.join(dependents[:5])}...")
        else:
            lines.append("4. **Downstream impact**: No blocks depend on this")

        lines.append("")

        # Summary
        lines.append(f"**Summary**: {block.title}")

        return "\n".join(lines)


# =============================================================================
# Factory Functions
# =============================================================================


def create_ashc_self_awareness() -> ASHCSelfAwareness:
    """
    Create an ASHCSelfAwareness service instance.

    Returns:
        Configured ASHCSelfAwareness service
    """
    return ASHCSelfAwareness()


# Module-level singleton
_service: ASHCSelfAwareness | None = None


def get_ashc_self_awareness() -> ASHCSelfAwareness:
    """
    Get the global ASHCSelfAwareness instance.

    Creates instance on first call (lazy initialization).
    """
    global _service
    if _service is None:
        _service = create_ashc_self_awareness()
    return _service


def reset_ashc_self_awareness() -> None:
    """Reset the global service instance."""
    global _service
    _service = None


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Constants
    "L0_AXIOMS",
    "L1_PRIMITIVES",
    "L2_DERIVED",
    "CONSTITUTIONAL_PRINCIPLES",
    "L3_ARCHITECTURE",
    "ALL_GENESIS_BLOCKS",
    # Evidence Tier
    "EvidenceTier",
    # Result Types
    "GroundingResult",
    "JustificationResult",
    "ConsistencyViolation",
    "ConsistencyReport",
    # Service
    "ASHCSelfAwareness",
    # Factory
    "create_ashc_self_awareness",
    "get_ashc_self_awareness",
    "reset_ashc_self_awareness",
]
