"""
Zero Seed Genesis: Core Seeding Logic.

"From nothing, the seed. From the seed, the axioms. From the axioms, the layers."

This module implements the seeding protocol from zero-seed-genesis-grand-strategy.md.
It creates the Zero Seed K-Block (t=0) and populates the initial axioms (t=1, t=2, t=3).

Philosophy:
    "The Zero Seed is not hidden; users watch it spawn."

See: plans/zero-seed-genesis-grand-strategy.md
See: spec/protocols/zero-seed.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from services.k_block.postgres_zero_seed_storage import (
    PostgresZeroSeedStorage,
    get_postgres_zero_seed_storage,
)

# Type alias for compatibility
ZeroSeedStorage = PostgresZeroSeedStorage
from services.zero_seed import EvidenceTier, Proof, ZeroNode
from services.zero_seed.galois.axiomatics import (
    EntityAxiom,
    GaloisGround,
    MorphismAxiom,
    create_axiom_kernel,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

EPOCH = datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
ZERO_SEED_ID = "zero-seed-genesis"

# =============================================================================
# Genesis Data Classes
# =============================================================================


@dataclass(frozen=True)
class SeedAxiom:
    """A seed axiom for the Zero Seed (simple data structure)."""

    id: str
    statement: str
    loss: float
    tier: EvidenceTier
    kind: str  # "axiom" or "ground"


@dataclass(frozen=True)
class DesignLaw:
    """A design law embedded in the Zero Seed."""

    id: str
    name: str
    statement: str
    layer: int  # 1 = axiom-level, 2 = value-level
    immutable: bool


@dataclass(frozen=True)
class ZeroSeed:
    """
    The unwriteable genesis K-Block.

    Not truly immutable — append-only evolution is possible.
    But evolution is DIFFICULT by design.
    Any change to Zero Seed requires:
    1. Dialectical synthesis proposal
    2. Galois loss verification (must not increase system loss)
    3. Witness trail with full justification

    Zero Seed is the FIRST entry in the infinite feed.
    Everything else derives from it.
    """

    id: str
    created_at: datetime
    kind: str
    layer: int
    galois_loss: float

    axioms: tuple[SeedAxiom, ...]
    design_laws: tuple[DesignLaw, ...]

    @property
    def can_evolve(self) -> bool:
        """Evolution is possible but governed."""
        return True

    @property
    def evolution_difficulty(self) -> str:
        """Honest answer: we don't know yet."""
        return "UNKNOWN — designed to be difficult"


# =============================================================================
# Design Laws (Immutable)
# =============================================================================

DESIGN_LAWS: tuple[DesignLaw, ...] = (
    DesignLaw(
        id="feed-is-primitive",
        name="Feed Is Primitive",
        statement=(
            "The feed is not a view of data. The feed IS the primary interface. "
            "Feeds are chronological truth streams, filterable by lens. "
            "A feed without filters is the raw cosmos. A feed with filters is a perspective."
        ),
        layer=1,  # Axiom level
        immutable=True,
    ),
    DesignLaw(
        id="kblock-incidental-essential",
        name="K-Block Incidental Essential",
        statement=(
            "K-Blocks are theoretically decouple-able from kgents. "
            "K-Blocks are pragmatically essential to kgents. "
            "This tension is DESIGNED, not accidental."
        ),
        layer=2,  # Value level
        immutable=True,
    ),
    DesignLaw(
        id="linear-adaptation",
        name="Linear Adaptation",
        statement=(
            "The system adapts to user wants and needs. "
            "The system does NOT change behavior against user will. "
            "Product shapes to user, not user to product."
        ),
        layer=2,  # Value level
        immutable=True,
    ),
    DesignLaw(
        id="contradiction-surfacing",
        name="Contradiction Surfacing",
        statement=(
            "Surfacing, interrogating, and systematically interacting "
            "with personal beliefs, values, and contradictions is "
            "ONE OF THE MOST IMPORTANT PARTS of the system. "
            "Fail-fast epistemology. The system is a mirror."
        ),
        layer=1,  # Axiom level — core to identity
        immutable=True,
    ),
)

# =============================================================================
# Seeding Logic
# =============================================================================


@dataclass
class SeedResult:
    """Result of seeding operation."""

    zero_seed: ZeroSeed
    zero_seed_kblock_id: str
    axiom_kblock_ids: dict[str, str]  # axiom_id -> kblock_id
    design_law_kblock_ids: dict[str, str]  # law_id -> kblock_id
    timestamp: datetime
    success: bool
    message: str


async def seed_zero_seed(
    storage: ZeroSeedStorage | None = None,
) -> SeedResult:
    """
    Seed the Zero Seed and initial axioms.

    This creates:
    - t=0: Zero Seed (L0, system, loss=0.000)
    - t=1: A1 Entity Axiom (L1, axiom, loss=0.002)
    - t=2: A2 Morphism Axiom (L1, axiom, loss=0.003)
    - t=3: G Galois Ground (L1, ground, loss=0.000)

    Args:
        storage: Optional ZeroSeedStorage instance (uses global if None)

    Returns:
        SeedResult with created K-Block IDs

    Raises:
        ValueError: If seeding fails
    """
    if storage is None:
        storage = await get_postgres_zero_seed_storage()

    logger.info("=== Beginning Zero Seed Genesis ===")

    timestamp = datetime.now(timezone.utc)

    # Create axiom kernel using existing galois logic (returns tuple of axioms)
    kernel_axioms = create_axiom_kernel()

    # Convert kernel axioms to our Axiom type
    axioms_list = []
    for galois_axiom in kernel_axioms:
        if isinstance(galois_axiom, EntityAxiom):
            axioms_list.append(
                SeedAxiom(
                    id="A1",
                    statement="Everything is a node",
                    loss=galois_axiom.loss_profile().total,
                    tier=EvidenceTier.CATEGORICAL,
                    kind="axiom",
                )
            )
        elif isinstance(galois_axiom, MorphismAxiom):
            axioms_list.append(
                SeedAxiom(
                    id="A2",
                    statement="Everything composes",
                    loss=galois_axiom.loss_profile().total,
                    tier=EvidenceTier.CATEGORICAL,
                    kind="axiom",
                )
            )
        elif isinstance(galois_axiom, GaloisGround):
            axioms_list.append(
                SeedAxiom(
                    id="G",
                    statement="Loss measures truth",
                    loss=galois_axiom.loss_profile().total,
                    tier=EvidenceTier.CATEGORICAL,
                    kind="ground",
                )
            )

    axioms = tuple(axioms_list)

    # Create the Zero Seed
    zero_seed = ZeroSeed(
        id=ZERO_SEED_ID,
        created_at=EPOCH,
        kind="SYSTEM",
        layer=0,  # Below L1 — the ground of grounds
        galois_loss=0.000,
        axioms=axioms,
        design_laws=DESIGN_LAWS,
    )

    # Create K-Blocks for Zero Seed
    try:
        # 1. Create Zero Seed K-Block (t=0)
        # Use a fixed ID for Zero Seed so we can find it later
        from services.k_block.core.kblock import KBlockId

        zero_seed_kblock_id_obj = KBlockId(ZERO_SEED_ID)

        zero_seed_content = _format_zero_seed_content(zero_seed)
        zero_seed_kblock, zero_seed_kblock_id = await storage.create_node(
            layer=0,
            title="Zero Seed Genesis",
            content=zero_seed_content,
            lineage=[],
            confidence=1.0,
            tags=["system", "genesis", "zero-seed"],
            created_by="system",
            kblock_id=zero_seed_kblock_id_obj,  # Fixed ID for Zero Seed
        )
        logger.info(f"Created Zero Seed K-Block: {zero_seed_kblock_id}")

        # 2. Create axiom K-Blocks (t=1, t=2, t=3)
        # Note: Axioms have no lineage (they are foundational)
        axiom_kblock_ids = {}
        for axiom in axioms:
            axiom_content = _format_axiom_content(axiom)
            axiom_kblock, axiom_kblock_id = await storage.create_node(
                layer=1,
                title=f"Axiom {axiom.id}: {axiom.statement}",
                content=axiom_content,
                lineage=[],  # Axioms are foundational - no lineage
                confidence=1.0 - axiom.loss,  # High confidence for low loss
                tags=["axiom", axiom.kind, "foundational"],
                created_by="system",
            )
            axiom_kblock_ids[axiom.id] = axiom_kblock_id
            logger.info(f"Created Axiom K-Block {axiom.id}: {axiom_kblock_id}")

        # 3. Create design law K-Blocks
        design_law_kblock_ids = {}
        for law in DESIGN_LAWS:
            law_content = _format_design_law_content(law)
            # L1 design laws cannot have lineage (foundational constraint)
            # L2+ can derive from Zero Seed
            lineage = [] if law.layer == 1 else [zero_seed_kblock_id]
            law_kblock, law_kblock_id = await storage.create_node(
                layer=law.layer,
                title=law.name,
                content=law_content,
                lineage=lineage,
                confidence=1.0,  # Design laws are definitive
                tags=["design-law", "immutable"],
                created_by="system",
            )
            design_law_kblock_ids[law.id] = law_kblock_id
            logger.info(f"Created Design Law K-Block {law.id}: {law_kblock_id}")

        logger.info("=== Zero Seed Genesis Complete ===")

        return SeedResult(
            zero_seed=zero_seed,
            zero_seed_kblock_id=zero_seed_kblock_id,
            axiom_kblock_ids=axiom_kblock_ids,
            design_law_kblock_ids=design_law_kblock_ids,
            timestamp=timestamp,
            success=True,
            message="Zero Seed created successfully",
        )

    except Exception as e:
        logger.error(f"Genesis failed: {e}", exc_info=True)
        return SeedResult(
            zero_seed=zero_seed,
            zero_seed_kblock_id="",
            axiom_kblock_ids={},
            design_law_kblock_ids={},
            timestamp=timestamp,
            success=False,
            message=f"Genesis failed: {str(e)}",
        )


def _format_zero_seed_content(zero_seed: ZeroSeed) -> str:
    """Format Zero Seed as markdown content."""
    return f"""# Zero Seed Genesis

**ID**: {zero_seed.id}
**Created**: {zero_seed.created_at.isoformat()}
**Kind**: {zero_seed.kind}
**Layer**: L{zero_seed.layer} (Ground of Grounds)
**Galois Loss**: {zero_seed.galois_loss:.3f}

## Philosophy

> "From nothing, the seed. From the seed, the axioms. From the axioms, the layers.
> From the layers, the contradictions. From the contradictions, the self."

The Zero Seed is the unwriteable genesis — the first entry in the infinite feed.
Everything else derives from it.

## Axioms

{chr(10).join(f"- **{axiom.id}** ({axiom.kind}): {axiom.statement} (L={axiom.loss:.3f})" for axiom in zero_seed.axioms)}

## Design Laws

{chr(10).join(f"- **{law.name}**: {law.statement}" for law in zero_seed.design_laws)}

## Evolution

Can evolve: {zero_seed.can_evolve}
Evolution difficulty: {zero_seed.evolution_difficulty}

Any change to Zero Seed requires:
1. Dialectical synthesis proposal
2. Galois loss verification (must not increase system loss)
3. Witness trail with full justification
"""


def _format_axiom_content(axiom: SeedAxiom) -> str:
    """Format axiom as markdown content."""
    return f"""# Axiom {axiom.id}: {axiom.statement}

**ID**: {axiom.id}
**Kind**: {axiom.kind}
**Galois Loss**: {axiom.loss:.3f}
**Evidence Tier**: {axiom.tier.name}

## Statement

{axiom.statement}

## Justification

This axiom was discovered as a zero-loss fixed point through Galois modularization.
It represents a fundamental truth that cannot be further decomposed without loss.

Loss < 0.01 indicates this is a fixed point — a stable foundation for the system.

## Properties

- **Immutable**: This axiom cannot be modified without consensus
- **Foundational**: All higher layers derive from this axiom
- **Universal**: This axiom applies to all contexts within kgents
"""


def _format_design_law_content(law: DesignLaw) -> str:
    """Format design law as markdown content."""
    return f"""# Design Law: {law.name}

**ID**: {law.id}
**Layer**: L{law.layer}
**Immutable**: {law.immutable}

## Statement

{law.statement}

## Justification

This design law emerged from the philosophy of kgents and the Grand Strategy.
It represents a fundamental constraint on system behavior.

## Enforcement

This law is:
- Embedded in the Zero Seed
- Checked during system operations
- Surfaced when violations are detected

Violating this law is possible but requires explicit justification.
"""


# =============================================================================
# Status Check
# =============================================================================


@dataclass
class GenesisStatus:
    """Status of genesis seeding."""

    is_seeded: bool
    zero_seed_exists: bool
    axiom_count: int
    design_law_count: int
    seed_timestamp: datetime | None


async def check_genesis_status(
    storage: ZeroSeedStorage | None = None,
) -> GenesisStatus:
    """
    Check if the system has been seeded.

    Args:
        storage: Optional ZeroSeedStorage instance (uses global if None)

    Returns:
        GenesisStatus with current state
    """
    if storage is None:
        storage = await get_postgres_zero_seed_storage()

    # Check if Zero Seed K-Block exists
    zero_seed_kblock = await storage.get_node(ZERO_SEED_ID)
    zero_seed_exists = zero_seed_kblock is not None

    # Count axioms (L1 nodes derived from Zero Seed)
    layer_1_nodes = await storage.get_layer_nodes(1)
    axiom_count = len(layer_1_nodes)

    # Count design laws (would need metadata query in production)
    design_law_count = len(DESIGN_LAWS)

    is_seeded = zero_seed_exists and axiom_count >= 3

    return GenesisStatus(
        is_seeded=is_seeded,
        zero_seed_exists=zero_seed_exists,
        axiom_count=axiom_count,
        design_law_count=design_law_count,
        seed_timestamp=EPOCH if is_seeded else None,
    )


__all__ = [
    "ZeroSeed",
    "DesignLaw",
    "SeedResult",
    "GenesisStatus",
    "DESIGN_LAWS",
    "seed_zero_seed",
    "check_genesis_status",
]
