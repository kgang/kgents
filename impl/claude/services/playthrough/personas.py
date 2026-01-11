"""
Agent Personas: Morphism variations through the PlayAgent functor.

Each persona explores a different region of the gameplay possibility space.
Together, they provide comprehensive coverage for evidence generation.

Categorical Interpretation:
    Each persona defines a different morphism through the same categorical structure.
    Running multiple personas in parallel is a categorical product:

    ParallelFarm = PlayAgent₁ × PlayAgent₂ × ... × PlayAgentₙ
"""

from .agent import AgentPersona

# =============================================================================
# Core Personas
# =============================================================================

AGGRESSIVE = AgentPersona(
    name="aggressive",
    strategic_bias="maximize_dps",
    risk_tolerance=0.8,
    reaction_skill=0.8,
    exploration_rate=0.2,
)
"""
Aggressive player: Maximizes damage output, takes risks.

Tests:
- High DPS upgrade paths
- Combat effectiveness
- Punishment for overcommitment
"""

DEFENSIVE = AgentPersona(
    name="defensive",
    strategic_bias="maximize_survival",
    risk_tolerance=0.2,
    reaction_skill=0.7,
    exploration_rate=0.3,
)
"""
Defensive player: Prioritizes survival, avoids risks.

Tests:
- Survivability upgrade paths
- Late-game scaling
- Fun floor (can defensive play be engaging?)
"""

EXPLORER = AgentPersona(
    name="explorer",
    strategic_bias="try_everything",
    risk_tolerance=0.5,
    reaction_skill=0.6,
    exploration_rate=0.9,
)
"""
Explorer player: Tries all options, low commitment to strategies.

Tests:
- Upgrade diversity
- Discovery of emergent combinations
- Balance across all options
"""

OPTIMIZER = AgentPersona(
    name="optimizer",
    strategic_bias="follow_meta",
    risk_tolerance=0.5,
    reaction_skill=0.95,
    exploration_rate=0.1,
)
"""
Optimizer player: Follows optimal strategies, high execution skill.

Tests:
- Skill ceiling
- Meta viability
- Whether optimal play is also fun
"""

NOVICE = AgentPersona(
    name="novice",
    strategic_bias="random",
    risk_tolerance=0.4,
    reaction_skill=0.3,
    exploration_rate=0.5,
)
"""
Novice player: Limited knowledge, slow reactions, makes mistakes.

Tests:
- Accessibility
- Fun floor for new players
- Whether game is learnable
"""

CHAOTIC = AgentPersona(
    name="chaotic",
    strategic_bias="random",
    risk_tolerance=0.9,
    reaction_skill=0.5,
    exploration_rate=1.0,
)
"""
Chaotic player: Random decisions, stress-tests edge cases.

Tests:
- Edge cases
- Unexpected combinations
- System stability
"""

# =============================================================================
# Specialized Personas
# =============================================================================

SPEEDRUNNER = AgentPersona(
    name="speedrunner",
    strategic_bias="maximize_clear_speed",
    risk_tolerance=0.7,
    reaction_skill=0.95,
    exploration_rate=0.0,  # Knows exactly what to do
)
"""
Speedrunner: Optimizes for fastest clear time.

Tests:
- Speed-running viability
- Optimal pathing
- Time-pressure balance
"""

AFK_FARMER = AgentPersona(
    name="afk_farmer",
    strategic_bias="minimize_interaction",
    risk_tolerance=0.1,
    reaction_skill=0.1,  # Barely paying attention
    exploration_rate=0.0,
)
"""
AFK farmer: Minimal interaction, tests passive play.

Tests:
- Whether passive builds exist
- Balance of active vs passive playstyles
- Whether AFK play is intended
"""

COMPLETIONIST = AgentPersona(
    name="completionist",
    strategic_bias="collect_everything",
    risk_tolerance=0.3,
    reaction_skill=0.6,
    exploration_rate=0.8,
)
"""
Completionist: Tries to experience all content.

Tests:
- Content accessibility
- Achievement balance
- Full game coverage
"""

# =============================================================================
# Persona Collection
# =============================================================================

PERSONAS = {
    # Core personas (always run)
    "aggressive": AGGRESSIVE,
    "defensive": DEFENSIVE,
    "explorer": EXPLORER,
    "optimizer": OPTIMIZER,
    "novice": NOVICE,
    "chaotic": CHAOTIC,
    # Specialized personas (run for specific tests)
    "speedrunner": SPEEDRUNNER,
    "afk_farmer": AFK_FARMER,
    "completionist": COMPLETIONIST,
}

CORE_PERSONAS = ["aggressive", "defensive", "explorer", "optimizer", "novice", "chaotic"]
ALL_PERSONAS = list(PERSONAS.keys())


def get_persona(name: str) -> AgentPersona:
    """Get a persona by name."""
    if name not in PERSONAS:
        raise ValueError(f"Unknown persona: {name}. Available: {list(PERSONAS.keys())}")
    return PERSONAS[name]


def create_custom_persona(
    name: str,
    strategic_bias: str = "balanced",
    risk_tolerance: float = 0.5,
    reaction_skill: float = 0.5,
    exploration_rate: float = 0.5,
) -> AgentPersona:
    """Create a custom persona for specific testing needs."""
    return AgentPersona(
        name=name,
        strategic_bias=strategic_bias,
        risk_tolerance=risk_tolerance,
        reaction_skill=reaction_skill,
        exploration_rate=exploration_rate,
    )
