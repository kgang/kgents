"""
Ground (⊥) - The empirical seed.

Type: Void → Facts
Returns: {Kent's preferences, world state, initial conditions}

The irreducible facts about the person and world that cannot be derived.

Why irreducible: Kent's preference for "direct but warm" is a fact about Kent,
                 not a theorem. The current state of the world is given.
What it grounds: K-gent's persona. The starting point for personalization.

Contents:
- Persona seed: Name, roles, preferences, patterns, values
- World seed: Date, context, active projects
- History seed: Past decisions, established patterns

THE BOOTSTRAP PARADOX:
> Ground cannot be bypassed. LLMs can amplify but not replace Ground.

What LLMs CAN do:
- Amplify Ground (generate variations, explore implications)
- Apply Ground (translate preferences into code)
- Extend Ground (infer related preferences from stated ones)

What LLMs CANNOT do:
- Create Ground from nothing
- Replace human judgment about what matters
- Substitute for real-world usage feedback
"""

import asyncio
from datetime import date
from typing import Optional, TypeVar, Callable, Any

from .types import Agent, Facts, PersonaSeed, WorldSeed


A = TypeVar('A')
B = TypeVar('B')


class Fix(Agent[tuple[Callable[[A], B], A], B]):
    """
    Fix-pattern retry: repeatedly applies function until success or max attempts.
    
    Type: ((A → B), A, max_attempts, backoff) → B
    
    Implements exponential backoff for transient failures.
    """
    
    def __init__(self, max_attempts: int = 3, initial_backoff: float = 0.1):
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff
    
    @property
    def name(self) -> str:
        return "Fix"
    
    async def invoke(self, input: tuple[Callable[[A], B], A]) -> B:
        """Apply function with exponential backoff retry."""
        fn, arg = input
        
        last_error: Optional[Exception] = None
        backoff = self.initial_backoff
        
        for attempt in range(self.max_attempts):
            try:
                if asyncio.iscoroutinefunction(fn):
                    return await fn(arg)
                else:
                    return fn(arg)
            except Exception as e:
                last_error = e
                if attempt < self.max_attempts - 1:
                    await asyncio.sleep(backoff)
                    backoff *= 2  # exponential backoff
        
        # All attempts failed
        raise RuntimeError(
            f"Fix failed after {self.max_attempts} attempts"
        ) from last_error


class Ground(Agent[None, Facts]):
    """
    The empirical seed: loads irreducible facts about person and world.

    Usage:
        ground = Ground()
        facts = await ground.invoke(None)

        # Access persona
        facts.persona.name  # "Kent"
        facts.persona.preferences["communication"]["style"]  # "direct but warm"

        # Access world
        facts.world.date  # current date
        facts.world.active_projects  # ongoing work

    The Ground agent can be initialized with custom facts (for testing)
    or will use the default Kent persona from spec.
    """

    def __init__(self, facts: Optional[Facts] = None, use_retry: bool = True):
        """
        Initialize Ground with optional custom facts.

        If no facts provided, loads the default Kent persona from spec.
        
        Args:
            facts: Optional pre-loaded facts (for testing)
            use_retry: Whether to use Fix-pattern retry for loading (default True)
        """
        self._use_retry = use_retry
        self._facts = facts or None  # Lazy load on first invoke

    @property
    def name(self) -> str:
        return "Ground"

    async def invoke(self, _: None) -> Facts:
        """Return the grounded facts. Input is ignored (Void → Facts)."""
        if self._facts is None:
            if self._use_retry:
                fix = Fix(max_attempts=3, initial_backoff=0.1)
                self._facts = await fix.invoke((self._load_default_facts_sync, None))
            else:
                self._facts = self._load_default_facts_sync(None)
        
        return self._facts

    def _load_default_facts_sync(self, _: None) -> Facts:
        """
        Load the default Kent persona from spec/k-gent/persona.md.

        This is the irreducible seed - human judgment captured as data.
        
        Wrapped by Fix pattern to handle transient filesystem/network issues.
        """
        # In production, this might read from external file/API
        # For now, returns hardcoded seed with potential for external load
        return Facts(
            persona=PersonaSeed(
                name="Kent",
                roles=["researcher", "creator", "thinker"],
                preferences={
                    "communication": {
                        "style": "direct but warm",
                        "length": "concise preferred",
                        "formality": "casual with substance",
                    },
                    "aesthetics": {
                        "design": "minimal, functional",
                        "prose": "clear over clever",
                    },
                },
                patterns={
                    "thinking": [
                        "starts from first principles",
                        "asks 'what would falsify this?'",
                        "seeks composable abstractions",
                    ],
                    "decision_making": [
                        "prefers reversible choices",
                        "values optionality",
                    ],
                    "communication": [
                        "uses analogies frequently",
                        "appreciates precision in technical contexts",
                    ],
                },
                values=[
                    "intellectual honesty",
                    "ethical technology",
                    "joy in creation",
                    "composability",
                ],
                dislikes=[
                    "unnecessary jargon",
                    "feature creep",
                    "surveillance capitalism",
                ],
            ),
            world=WorldSeed(
                date=date.today().isoformat(),
                context={
                    "current_focus": "kgents specification",
                    "recent_interests": [
                        "category theory",
                        "scientific agents",
                        "personal AI",
                    ],
                },
                active_projects=[
                    {
                        "name": "kgents",
                        "status": "active",
                        "goals": ["spec A/B/C/K", "reference implementation"],
                    }
                ],
            ),
            history={},
        )


# The LLM/Human boundary:
#
# Spec + Ground = Human territory (irreducible, already provided)
# Impl = LLM territory (mechanical translation from spec)
# Polish = Hybrid territory (accumulated wisdom from real usage)
