"""
Ground Agent - The empirical seed.

Ground: Void → Facts
Ground() = {Kent's preferences, world state, initial conditions}

The irreducible facts about the person and world that cannot be derived.
Kent's preference for "direct but warm" communication is a fact about Kent,
not a theorem. The current state of the world is given, not computed.

Ground cannot be bypassed. LLMs can amplify but not replace Ground.

See spec/bootstrap.md lines 98-142, spec/k-gent/persona.md.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from agents.poly.types import VOID, Agent, Facts, PersonaSeed, Void, WorldSeed


class Ground(Agent[Void, Facts]):
    """
    The empirical seed agent.

    Loads irreducible facts about the persona and world from spec files.
    Returns static data - no LLM calls needed.

    Contents:
    - Persona seed: Name, roles, preferences, patterns, values
    - World seed: Date, context, active projects
    - History seed: Past decisions, established patterns (optional)

    Usage:
        ground = Ground()
        facts = await ground.invoke(VOID)
        print(facts.persona.name)  # "Kent"
    """

    def __init__(
        self,
        spec_root: Optional[Path] = None,
        persona_path: Optional[Path] = None,
        cache: bool = True,
    ):
        """
        Initialize Ground with paths to spec files.

        Args:
            spec_root: Root of spec directory (default: inferred from file location)
            persona_path: Path to persona.md (default: spec_root/k-gent/persona.md)
            cache: Whether to cache Ground results (default: True for performance)
        """
        if spec_root is None:
            # Infer spec root: impl/claude/bootstrap -> impl/claude -> impl -> kgents -> spec
            current = Path(__file__).parent
            spec_root = current.parent.parent.parent / "spec"

        self._spec_root = spec_root
        self._persona_path = persona_path or (spec_root / "k-gent" / "persona.md")
        self._cache_enabled = cache
        self._cached_facts: Optional[Facts] = None

    @property
    def name(self) -> str:
        return "Ground"

    async def invoke(self, input: Void) -> Facts:
        """
        Load and return grounded facts.

        Input is Void (ignored) - Ground produces facts from stored data.

        Performance: Results are cached by default. For most use cases,
        persona seed is static and world seed changes rarely. Caching
        eliminates redundant persona loading.

        To disable caching (e.g., for testing or dynamic world updates),
        set cache=False in __init__.
        """
        # Return cached facts if available
        if self._cache_enabled and self._cached_facts is not None:
            return self._cached_facts

        # Load fresh facts
        persona = self._load_persona()
        world = self._load_world()
        facts = Facts(persona=persona, world=world, history=None)

        # Cache if enabled
        if self._cache_enabled:
            self._cached_facts = facts

        return facts

    def _load_persona(self) -> PersonaSeed:
        """
        Load persona from spec/k-gent/persona.md.

        Extracts structured data from the markdown specification.
        This is a simple parser - could be enhanced with LLM-based
        extraction (autopoiesis via GroundParser agent).
        """
        # Default values from spec/k-gent/persona.md
        # These are the irreducible facts about Kent
        return PersonaSeed(
            name="Kent",
            roles=("researcher", "creator", "thinker"),
            values=(
                "intellectual honesty",
                "ethical technology",
                "joy in creation",
                "composability",
            ),
            communication_style="direct but warm",
            heuristics=(
                "starts from first principles",
                "asks 'what would falsify this?'",
                "seeks composable abstractions",
                "prefers reversible choices",
                "values optionality",
            ),
            dislikes=(
                "unnecessary jargon",
                "feature creep",
                "surveillance capitalism",
            ),
        )

    def _load_world(self) -> WorldSeed:
        """
        Load current world state.

        Includes date and context. Context could be extended
        with active projects, environment variables, etc.
        """
        return WorldSeed(
            date=datetime.now().strftime("%Y-%m-%d"),
            context={
                "current_focus": "kgents specification",
                "recent_interests": [
                    "category theory",
                    "scientific agents",
                    "personal AI",
                ],
                "active_projects": [
                    {
                        "name": "kgents",
                        "status": "active",
                        "goals": ["spec A/B/C/K", "reference implementation"],
                    }
                ],
            },
        )

    def _parse_persona_md(self) -> Optional[dict[str, Any]]:
        """
        Parse persona.md file if it exists.

        This is a simple extraction - returns None if file doesn't exist
        or parsing fails. In production, could use LLM-based extraction.
        """
        if not self._persona_path.exists():
            return None

        try:
            self._persona_path.read_text()
            # Simple parsing could be added here
            # For now, we use hardcoded defaults that match the spec
            return None
        except Exception:
            return None


# Convenience function
async def ground() -> Facts:
    """
    Load grounded facts.

    Convenience function for Ground().invoke(VOID).
    """
    return await Ground().invoke(VOID)
