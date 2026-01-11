"""
KGames: Game Generation from Axioms.

The KGames service enables game generation and verification using the
four constitutional axioms discovered through wasm-survivors:

Axioms:
- A1: AGENCY (L=0.02) - Player choices determine outcomes
- A2: ATTRIBUTION (L=0.05) - Outcomes trace to identifiable causes
- A3: MASTERY (L=0.08) - Skill development is externally observable
- A4: COMPOSITION (L=0.03) - Moments compose algebraically into arcs

Components:
- GameKernel: The four axiom classes with validation
- GameOperad: Composition grammar for game mechanics
- KGamesNode: AGENTESE interface for AI agent access

The Witness Integration (Mark -> Trace -> Crystal):
- Marks capture decision points for A1 (agency) and A2 (attribution)
- Traces accumulate skill metrics for A3 (mastery)
- Crystals compose moments into arcs for A4 (composition)

Example usage:
    >>> from services.kgames import GameKernel, create_kernel
    >>>
    >>> kernel = create_kernel()
    >>> print(kernel.to_text())
    >>>
    >>> # Validate an implementation
    >>> result = kernel.validate_implementation(my_game)
    >>> if result.is_valid:
    ...     print("All axioms satisfied!")

Philosophy:
    "Games are theorems in the KGAMES kernel.
     Generation is proof search. Verification is proof checking."

See: pilots/wasm-survivors-game/systems/axiom-guards.ts
See: spec/agents/kgames-kernel.md
"""

from .kernel import (
    # Axioms
    AgencyAxiom,
    AttributionAxiom,
    AxiomResult,
    # Enums
    AxiomSeverity,
    # Types
    AxiomViolation,
    CompositionAxiom,
    GameImplementation,
    # Kernel
    GameKernel,
    MasteryAxiom,
    ValidationResult,
    create_kernel,
)
from .node import (
    GameSpecRendering,
    KernelRendering,
    KGamesNode,
    MockGameImplementation,
    OperadRendering,
    ValidationRendering,
)
from .operad import (
    # Predefined mechanics
    ATTACK,
    BLOCK,
    DASH,
    DODGE,
    # Laws
    GAME_LAWS,
    GAME_OPERAD,
    # Operations
    GAME_OPERATIONS,
    LEVEL_UP,
    MOVE,
    PREDEFINED_MECHANICS,
    SPAWN_ENEMY,
    SPAWN_WAVE,
    UPGRADE,
    GameLaw,
    # Game Law Types
    GameLawStatus,
    GameLawVerification,
    # Operad
    GameOperad,
    GameOperation,
    # Mechanic Types
    Mechanic,
    MechanicConditional,
    MechanicFeedback,
    MechanicParallel,
    MechanicSequence,
    # Workflow composition
    compose_mechanic_workflow,
    create_game_operad,
    get_mechanic,
    list_mechanics,
)

__all__ = [
    # Kernel - Enums
    "AxiomSeverity",
    # Kernel - Types
    "AxiomViolation",
    "AxiomResult",
    "ValidationResult",
    "GameImplementation",
    # Kernel - Axioms
    "AgencyAxiom",
    "AttributionAxiom",
    "MasteryAxiom",
    "CompositionAxiom",
    # Kernel - Main
    "GameKernel",
    "create_kernel",
    # Operad - Game Law Types
    "GameLawStatus",
    "GameLawVerification",
    "GameLaw",
    "GameOperation",
    # Operad - Mechanic Types
    "Mechanic",
    "MechanicSequence",
    "MechanicParallel",
    "MechanicConditional",
    "MechanicFeedback",
    # Operad - Operations & Laws
    "GAME_OPERATIONS",
    "GAME_LAWS",
    "GameOperad",
    "GAME_OPERAD",
    "create_game_operad",
    # Operad - Predefined mechanics
    "ATTACK",
    "DODGE",
    "BLOCK",
    "MOVE",
    "DASH",
    "UPGRADE",
    "LEVEL_UP",
    "SPAWN_ENEMY",
    "SPAWN_WAVE",
    "PREDEFINED_MECHANICS",
    "get_mechanic",
    "list_mechanics",
    "compose_mechanic_workflow",
    # Node
    "KGamesNode",
    "KernelRendering",
    "OperadRendering",
    "ValidationRendering",
    "GameSpecRendering",
    "MockGameImplementation",
]
