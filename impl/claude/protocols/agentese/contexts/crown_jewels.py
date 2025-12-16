"""
Crown Jewels Path Registry

Registers AGENTESE paths for the Seven Crown Jewel applications:
1. Atelier Experience Platform (Flux) - world.atelier.*
2. Coalition Forge (Operad) - world.coalition.*, concept.task.*
3. Holographic Second Brain (Sheaf) - self.memory.*, self.memory.ghost.*
4. Punchdrunk Park (Polynomial) - world.town.scenario.*, concept.mask.*
5. Domain Simulation Engine (Tenancy) - world.simulation.*, concept.drill.*
6. Gestalt Architecture Visualizer (Reactive) - world.codebase.*
7. The Gardener (N-Phase) - concept.gardener.*

Per plans/core-apps-synthesis.md - the unified categorical foundation.

Crown Symbiont Integration:
Every self.* and time.* path can be wrapped in a CrownSymbiont that fuses
pure handler logic with D-gent infrastructure (TemporalWitness, SemanticManifold,
RelationalLattice). See spec/protocols/crown-symbiont.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from ..logos import Logos

# Crown Symbiont imports (lazy to avoid circular deps)
I = TypeVar("I")
O = TypeVar("O")
S = TypeVar("S")

# =============================================================================
# Path Registry Definitions per Crown Jewel
# =============================================================================

# Crown Jewel 1: Atelier Experience Platform
ATELIER_PATHS: dict[str, dict[str, Any]] = {
    "world.atelier.manifest": {
        "aspect": "manifest",
        "description": "View active Atelier sessions",
        "effects": [],
    },
    "world.atelier.session.manifest": {
        "aspect": "manifest",
        "description": "View current session state (builders, spectators, tokens)",
        "effects": [],
    },
    "world.atelier.session.bid": {
        "aspect": "define",
        "description": "Bid tokens to influence creation direction",
        "effects": ["TOKEN_TRANSFER", "NOTIFY_BUILDERS"],
    },
    "world.atelier.session.tithe": {
        "aspect": "tithe",
        "description": "Gift tokens to creator (pays entropy debt)",
        "effects": ["TOKEN_TRANSFER", "GRATITUDE_EMIT"],
    },
    "world.atelier.gallery.manifest": {
        "aspect": "manifest",
        "description": "Browse saved creations",
        "effects": [],
    },
    "world.atelier.gallery.purchase": {
        "aspect": "define",
        "description": "Purchase a creation from the gallery",
        "effects": ["TOKEN_TRANSFER", "LICENSE_GRANT"],
    },
    "self.tokens.manifest": {
        "aspect": "manifest",
        "description": "View current token balance",
        "effects": [],
    },
    "self.tokens.purchase": {
        "aspect": "define",
        "description": "Purchase tokens (Stripe integration)",
        "effects": ["STRIPE_CHARGE", "TOKEN_CREDIT"],
    },
}

# Crown Jewel 2: Coalition Forge
COALITION_PATHS: dict[str, dict[str, Any]] = {
    "world.coalition.manifest": {
        "aspect": "manifest",
        "description": "List available coalitions",
        "effects": [],
    },
    "world.coalition.create": {
        "aspect": "define",
        "description": "Form a new coalition for a task",
        "effects": ["COALITION_FORMED", "NOTIFY_AGENTS"],
    },
    "world.coalition.execute": {
        "aspect": "define",
        "description": "Execute coalition task",
        "effects": ["CREDIT_CHARGE", "TASK_RUN"],
    },
    "world.coalition.subscribe": {
        "aspect": "witness",
        "description": "Subscribe to real-time coalition formation events (SSE)",
        "effects": [],
    },
    "world.coalition.dialogue.witness": {
        "aspect": "witness",
        "description": "Stream coalition dialogue history",
        "effects": [],
    },
    "world.coalition.formation.manifest": {
        "aspect": "manifest",
        "description": "View coalition formation state (who joined, why, eigenvector compatibility)",
        "effects": [],
    },
    "world.coalition.handoff.witness": {
        "aspect": "witness",
        "description": "Observe handoff events between builders",
        "effects": [],
    },
    "concept.task.manifest": {
        "aspect": "manifest",
        "description": "View task template details",
        "effects": [],
    },
    "concept.task.define": {
        "aspect": "define",
        "description": "Create custom task template",
        "effects": ["TASK_REGISTERED"],
    },
    "self.credits.manifest": {
        "aspect": "manifest",
        "description": "View execution credit balance",
        "effects": [],
    },
    "self.credits.purchase": {
        "aspect": "define",
        "description": "Purchase execution credits",
        "effects": ["STRIPE_CHARGE", "CREDIT_ADDED"],
    },
}

# Crown Jewel 3: Holographic Second Brain
BRAIN_PATHS: dict[str, dict[str, Any]] = {
    "self.memory.manifest": {
        "aspect": "manifest",
        "description": "View memory system health and recent crystals",
        "effects": [],
    },
    "self.memory.capture": {
        "aspect": "define",
        "description": "Capture content into holographic memory",
        "effects": ["CRYSTAL_FORMED", "INDEX_UPDATED"],
    },
    "self.memory.recall": {
        "aspect": "manifest",
        "description": "Query memory via semantic search",
        "effects": [],
    },
    "self.memory.ghost.surface": {
        "aspect": "manifest",
        "description": "Surface ghost suggestions (things you might have forgotten)",
        "effects": [],
    },
    "self.memory.ghost.dismiss": {
        "aspect": "define",
        "description": "Dismiss a ghost suggestion",
        "effects": ["GHOST_ARCHIVED"],
    },
    "self.memory.cartography.manifest": {
        "aspect": "manifest",
        "description": "View knowledge topology map",
        "effects": [],
    },
    "self.memory.cartography.navigate": {
        "aspect": "manifest",
        "description": "Navigate to related concepts",
        "effects": [],
    },
}

# Crown Jewel 4: Punchdrunk Park
PARK_PATHS: dict[str, dict[str, Any]] = {
    # Scenario discovery and filtering
    "world.town.scenario.manifest": {
        "aspect": "manifest",
        "description": "List available scenarios (all or filtered by type/tag/difficulty)",
        "effects": [],
    },
    "world.town.scenario.search": {
        "aspect": "manifest",
        "description": "Search scenarios with filters (type, tags, difficulty)",
        "effects": [],
    },
    # Individual scenario operations
    "world.town.scenario[id].manifest": {
        "aspect": "manifest",
        "description": "View scenario details at specified LOD (0-3)",
        "effects": [],
    },
    "world.town.scenario[id].inhabit": {
        "aspect": "define",
        "description": "Enter a scenario as a character",
        "effects": ["MASK_DONNED", "SESSION_STARTED", "CITIZENS_SPAWNED"],
    },
    "world.town.scenario[id].observe": {
        "aspect": "manifest",
        "description": "Watch scenario unfold as spectator",
        "effects": [],
    },
    "world.town.scenario[id].spawn": {
        "aspect": "define",
        "description": "Spawn citizens from scenario template",
        "effects": ["CITIZENS_CREATED"],
    },
    # Scenario type enumeration
    "world.town.scenario.types.manifest": {
        "aspect": "manifest",
        "description": "List the five scenario types (Mystery, Collaboration, Conflict, Emergence, Practice)",
        "effects": [],
    },
    # Legacy compatibility
    "world.town.scenario.inhabit": {
        "aspect": "define",
        "description": "Enter a scenario as a character (legacy path)",
        "effects": ["MASK_DONNED", "SESSION_STARTED"],
    },
    "world.town.scenario.observe": {
        "aspect": "manifest",
        "description": "Watch scenario unfold as spectator (legacy path)",
        "effects": [],
    },
    # Consent system
    "self.consent.manifest": {
        "aspect": "manifest",
        "description": "View consent ledger (force/apology history)",
        "effects": [],
    },
    "self.consent.force": {
        "aspect": "define",
        "description": "Override agent consent with apology",
        "effects": ["CONSENT_OVERRIDDEN", "APOLOGY_LOGGED"],
    },
    # Mask system
    "concept.mask.manifest": {
        "aspect": "manifest",
        "description": "View available character masks",
        "effects": [],
    },
    "concept.mask.create": {
        "aspect": "define",
        "description": "Create a new character mask",
        "effects": ["MASK_CREATED"],
    },
    # Scenario template management
    "concept.scenario.manifest": {
        "aspect": "manifest",
        "description": "View scenario template schema and available fields",
        "effects": [],
    },
    "concept.scenario.define": {
        "aspect": "define",
        "description": "Create a custom scenario template",
        "effects": ["SCENARIO_REGISTERED"],
    },
    # Temporal
    "time.inhabit.witness": {
        "aspect": "witness",
        "description": "Replay inhabitation session",
        "effects": [],
    },
    "time.scenario.witness": {
        "aspect": "witness",
        "description": "View scenario session history and outcomes",
        "effects": [],
    },
}

# Crown Jewel 5: Domain Simulation Engine
SIMULATION_PATHS: dict[str, dict[str, Any]] = {
    "world.simulation.manifest": {
        "aspect": "manifest",
        "description": "List active simulations",
        "effects": [],
    },
    "world.simulation.create": {
        "aspect": "define",
        "description": "Create a new simulation from drill template",
        "effects": ["CREATE_SIMULATION", "NOTIFY_PARTICIPANTS"],
    },
    "world.simulation.inject": {
        "aspect": "define",
        "description": "Inject runtime event into simulation",
        "effects": ["NOTIFY_PARTICIPANTS", "LOG_AUDIT"],
    },
    "world.simulation.advance": {
        "aspect": "define",
        "description": "Advance simulation polynomial state",
        "effects": ["STATE_TRANSITION", "NOTIFY_PARTICIPANTS", "LOG_AUDIT"],
    },
    "concept.drill.manifest": {
        "aspect": "manifest",
        "description": "List available drill templates (service_outage, data_breach)",
        "effects": [],
    },
    "concept.drill[type].manifest": {
        "aspect": "manifest",
        "description": "View specific drill template by type (e.g., concept.drill[service_outage].manifest)",
        "effects": [],
    },
    "concept.drill.define": {
        "aspect": "define",
        "description": "Create custom drill template",
        "effects": ["DRILL_REGISTERED"],
    },
    # Spike 5B: Canonical Drill Templates
    "world.simulation[id].citizens.manifest": {
        "aspect": "manifest",
        "description": "List citizens participating in drill (roles, eigenvectors, status)",
        "effects": [],
    },
    "world.simulation[id].timers.manifest": {
        "aspect": "manifest",
        "description": "View compliance timers (GDPR 72h, SEC 4-day, etc.)",
        "effects": [],
    },
    "world.simulation[id].injects.manifest": {
        "aspect": "manifest",
        "description": "List active and pending injects",
        "effects": [],
    },
    "world.simulation[id].inject.trigger": {
        "aspect": "define",
        "description": "Manually trigger an inject (media_story, executive_call)",
        "effects": ["INJECT_TRIGGERED", "NOTIFY_PARTICIPANTS", "AUDIT_LOG"],
    },
    "world.simulation[id].inject.resolve": {
        "aspect": "define",
        "description": "Resolve an active inject",
        "effects": ["INJECT_RESOLVED", "AUDIT_LOG"],
    },
    "world.simulation[id].criteria.manifest": {
        "aspect": "manifest",
        "description": "View success criteria evaluation status",
        "effects": [],
    },
    "world.simulation[id].criteria.evaluate": {
        "aspect": "define",
        "description": "Evaluate a success criterion",
        "effects": ["CRITERION_EVALUATED", "AUDIT_LOG"],
    },
    "world.simulation[id].report.manifest": {
        "aspect": "manifest",
        "description": "Generate drill performance report",
        "effects": [],
    },
    "time.simulation.witness": {
        "aspect": "witness",
        "description": "Full audit replay of simulation",
        "effects": [],
    },
    "time.simulation.export": {
        "aspect": "manifest",
        "description": "Export compliance report",
        "effects": [],
    },
    # Crisis Polynomial paths (Spike 5A)
    "world.simulation[id].polynomial.manifest": {
        "aspect": "manifest",
        "description": "View crisis polynomial state for drill",
        "effects": [],
    },
    "world.simulation[id].polynomial.detect": {
        "aspect": "define",
        "description": "Detect incident (NORMAL→INCIDENT)",
        "effects": ["STATE_TRANSITION", "AUDIT_LOG"],
    },
    "world.simulation[id].polynomial.escalate": {
        "aspect": "define",
        "description": "Escalate to higher authority",
        "effects": ["STATE_TRANSITION", "AUDIT_LOG", "NOTIFICATION"],
    },
    "world.simulation[id].polynomial.contain": {
        "aspect": "define",
        "description": "Apply containment action",
        "effects": ["STATE_TRANSITION", "AUDIT_LOG"],
    },
    "world.simulation[id].polynomial.communicate": {
        "aspect": "define",
        "description": "Send status update to stakeholders",
        "effects": ["NOTIFICATION", "AUDIT_LOG"],
    },
    "world.simulation[id].polynomial.investigate": {
        "aspect": "define",
        "description": "Investigate incident details",
        "effects": ["AUDIT_LOG"],
    },
    "world.simulation[id].polynomial.resolve": {
        "aspect": "define",
        "description": "Apply fix or mitigation",
        "effects": ["STATE_TRANSITION", "AUDIT_LOG"],
    },
    "world.simulation[id].polynomial.recover": {
        "aspect": "define",
        "description": "Transition to recovery phase",
        "effects": ["STATE_TRANSITION", "AUDIT_LOG"],
    },
    "world.simulation[id].polynomial.close": {
        "aspect": "define",
        "description": "Complete incident lifecycle (→NORMAL)",
        "effects": ["STATE_TRANSITION", "AUDIT_LOG", "NOTIFICATION"],
    },
    "world.simulation[id].polynomial.audit": {
        "aspect": "witness",
        "description": "Generate compliance audit report",
        "effects": ["AUDIT_REPORT"],
    },
}

# Crown Jewel 6: Gestalt Architecture Visualizer
GESTALT_PATHS: dict[str, dict[str, Any]] = {
    "world.codebase.manifest": {
        "aspect": "manifest",
        "description": "Full architecture graph",
        "effects": [],
    },
    "world.codebase.module.manifest": {
        "aspect": "manifest",
        "description": "Module details",
        "effects": [],
    },
    "world.codebase.layer.manifest": {
        "aspect": "manifest",
        "description": "Layer with members",
        "effects": [],
    },
    "world.codebase.drift.witness": {
        "aspect": "witness",
        "description": "View drift violations",
        "effects": [],
    },
    "world.codebase.drift.refine": {
        "aspect": "refine",
        "description": "Challenge drift rule",
        "effects": ["QUEUE_REVIEW"],
    },
    "world.codebase.health.manifest": {
        "aspect": "manifest",
        "description": "Health metrics for codebase",
        "effects": [],
    },
    "world.codebase.subscribe": {
        "aspect": "witness",
        "description": "Live architecture updates",
        "effects": [],
    },
    "world.codebase.tour": {
        "aspect": "manifest",
        "description": "Guided tour of architecture",
        "effects": [],
    },
    "concept.governance.manifest": {
        "aspect": "manifest",
        "description": "Architecture rules",
        "effects": [],
    },
    "concept.governance.refine": {
        "aspect": "refine",
        "description": "Propose rule change",
        "effects": ["QUEUE_REVIEW"],
    },
}

# Crown Jewel 7: The Gardener
GARDENER_PATHS: dict[str, dict[str, Any]] = {
    "concept.gardener.manifest": {
        "aspect": "manifest",
        "description": "View Gardener status and active sessions",
        "effects": [],
    },
    "concept.gardener.session.create": {
        "aspect": "define",
        "description": "Start new development session",
        "effects": ["SESSION_CREATED", "FOREST_UPDATED"],
    },
    "concept.gardener.session.manifest": {
        "aspect": "manifest",
        "description": "View current session state",
        "effects": [],
    },
    "concept.gardener.session.resume": {
        "aspect": "define",
        "description": "Resume existing session",
        "effects": ["SESSION_RESUMED"],
    },
    "concept.gardener.session.advance": {
        "aspect": "define",
        "description": "Advance to next N-Phase",
        "effects": ["PHASE_ADVANCED", "FOREST_UPDATED"],
    },
    "concept.gardener.propose": {
        "aspect": "manifest",
        "description": "Get proactive suggestions",
        "effects": [],
    },
    "concept.gardener.route": {
        "aspect": "manifest",
        "description": "Route natural language to AGENTESE path",
        "effects": [],
    },
    "self.forest.manifest": {
        "aspect": "manifest",
        "description": "Show forest canopy view",
        "effects": [],
    },
    "self.forest.evolve": {
        "aspect": "define",
        "description": "Propose forest changes",
        "effects": ["FOREST_PROPOSAL"],
    },
    "self.meta.append": {
        "aspect": "define",
        "description": "Add learning to meta.md",
        "effects": ["META_UPDATED"],
    },
}

# =============================================================================
# Unified Registry
# =============================================================================

ALL_CROWN_JEWEL_PATHS: dict[str, dict[str, Any]] = {
    **ATELIER_PATHS,
    **COALITION_PATHS,
    **BRAIN_PATHS,
    **PARK_PATHS,
    **SIMULATION_PATHS,
    **GESTALT_PATHS,
    **GARDENER_PATHS,
}


@dataclass
class CrownJewelRegistry:
    """
    Registry for Crown Jewel AGENTESE paths.

    Provides path discovery and validation for all seven jewels.
    Can be wired into Logos for resolution.
    """

    paths: dict[str, dict[str, Any]] = field(
        default_factory=lambda: ALL_CROWN_JEWEL_PATHS.copy()
    )

    def list_paths(self, jewel: str | None = None) -> list[str]:
        """
        List registered paths, optionally filtered by jewel.

        Args:
            jewel: One of "atelier", "coalition", "brain", "park",
                   "simulation", "gestalt", "gardener", or None for all
        """
        jewel_prefixes = {
            "atelier": ("world.atelier.", "self.tokens."),
            "coalition": (
                "world.coalition.",
                "concept.task.",
                "self.credits.",
                "world.forge.",
            ),
            "brain": ("self.memory.",),
            "park": (
                "world.town.scenario",  # Matches both world.town.scenario. and world.town.scenario[
                "self.consent.",
                "concept.mask.",
                "concept.scenario.",
                "time.inhabit.",
                "time.scenario.",
            ),
            "simulation": ("world.simulation.", "concept.drill.", "time.simulation."),
            "gestalt": ("world.codebase.", "concept.governance."),
            "gardener": ("concept.gardener.", "self.forest.", "self.meta."),
        }

        if jewel is None:
            return list(self.paths.keys())

        prefixes = jewel_prefixes.get(jewel, ())
        return [p for p in self.paths if any(p.startswith(pre) for pre in prefixes)]

    def get_path_info(self, path: str) -> dict[str, Any] | None:
        """Get path metadata if registered."""
        return self.paths.get(path)

    def is_registered(self, path: str) -> bool:
        """Check if path is registered."""
        return path in self.paths

    def get_aspect(self, path: str) -> str | None:
        """Get the aspect for a path."""
        info = self.paths.get(path)
        return info.get("aspect") if info else None

    def get_effects(self, path: str) -> list[str]:
        """Get effects for a path."""
        info = self.paths.get(path)
        return info.get("effects", []) if info else []


# =============================================================================
# Logos Integration
# =============================================================================


def register_crown_jewel_paths(logos: "Logos") -> None:
    """
    Register Crown Jewel paths with a Logos instance.

    This enables discovery and validation of all seven jewel paths.
    Actual resolution still requires handler implementations.

    Args:
        logos: The Logos instance to register with
    """
    # For now, we register paths in the L-gent registry if available
    # Full handler implementations will be added per-jewel
    registry = CrownJewelRegistry()

    # Store registry in logos for query support
    if not hasattr(logos, "_crown_jewel_registry"):
        logos._crown_jewel_registry = registry  # type: ignore[attr-defined]


def get_crown_jewel_registry(logos: "Logos") -> CrownJewelRegistry | None:
    """Get the Crown Jewel registry from a Logos instance."""
    return getattr(logos, "_crown_jewel_registry", None)


# =============================================================================
# Crown Symbiont Integration
# =============================================================================


def list_self_time_paths() -> dict[str, list[str]]:
    """
    List all self.* and time.* Crown paths.

    Returns:
        Dict with "self" and "time" keys containing lists of paths

    Note: Crown Symbiont infrastructure was removed in data-architecture-rewrite.
    """
    self_paths = [p for p in ALL_CROWN_JEWEL_PATHS if p.startswith("self.")]
    time_paths = [p for p in ALL_CROWN_JEWEL_PATHS if p.startswith("time.")]

    return {
        "self": self_paths,
        "time": time_paths,
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Path registries per jewel
    "ATELIER_PATHS",
    "COALITION_PATHS",
    "BRAIN_PATHS",
    "PARK_PATHS",
    "SIMULATION_PATHS",
    "GESTALT_PATHS",
    "GARDENER_PATHS",
    # Unified registry
    "ALL_CROWN_JEWEL_PATHS",
    "CrownJewelRegistry",
    # Logos integration
    "register_crown_jewel_paths",
    "get_crown_jewel_registry",
    "list_self_time_paths",
]
