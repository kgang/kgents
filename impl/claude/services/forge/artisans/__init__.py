"""
Forge Artisans: The Seven Craftspeople of the Metaphysical Fullstack.

Each artisan corresponds to one layer of the metaphysical fullstack:
- K-gent: Soul/Governance (Layer 0) - Integrated via CommissionService
- Architect: Categorical Design (Layers 1-3)
- Smith: Service Implementation (Layer 4)
- Herald: AGENTESE Protocol (Layers 5-6)
- Projector: Surface Rendering (Layer 7)
- Sentinel: Security (Cross-cutting)
- Witness: Testing (Cross-cutting)

Phase 4 implements Architect, Smith, Herald, and Projector.
Phase 5 will add Sentinel and Witness.

"The Forge is where Kent builds with Kent."

See: spec/protocols/metaphysical-forge.md
"""

from .architect import AgentDesign, ArchitectArtisan
from .herald import HeraldArtisan, HeraldOutput
from .projector import ProjectorArtisan, ProjectorOutput
from .smith import SmithArtisan, SmithOutput

__all__ = [
    "ArchitectArtisan",
    "AgentDesign",
    "SmithArtisan",
    "SmithOutput",
    "HeraldArtisan",
    "HeraldOutput",
    "ProjectorArtisan",
    "ProjectorOutput",
]
