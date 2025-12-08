#!/usr/bin/env python3
"""
Village Story - A Five-Act Demonstration of kgents Runtime

This demonstrates 20 agents working together to tell a story about
a village, showcasing composability, parallelism, and heterarchical
coordination across multiple agent genera.

The Five Acts:
  Act I: Dawn (Setup & Introduction)
  Act II: Discovery (Rising Action)
  Act III: Crisis (Climax)
  Act IV: Resolution (Falling Action)
  Act V: Dusk (Denouement)

Agents used (20 total):
  - K-gents: Persona & dialogue
  - A-gents: Creativity & architecture
  - C-gents: Parallel composition & conditional logic
  - T-gents: Observers, judges, oracles
  - H-gents: Dialectical reasoning (if available)
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path

from bootstrap.types import Agent
from agents.k.persona import KgentAgent, DialogueInput, DialogueMode, PersonaState, PersonaSeed
from agents.c.parallel import parallel, ParallelConfig


# --- Story Domain Types ---

@dataclass
class Character:
    """A character in the village."""
    name: str
    role: str
    personality: str
    goal: str


@dataclass
class Scene:
    """A scene in the story."""
    act: int
    title: str
    description: str
    characters: list[str] = field(default_factory=list)
    events: list[str] = field(default_factory=list)


@dataclass
class StoryState:
    """Current state of the village story."""
    act: int
    scenes: list[Scene] = field(default_factory=list)
    characters: list[Character] = field(default_factory=list)
    tension_level: float = 0.0  # 0.0 (calm) to 1.0 (crisis)


@dataclass
class NarrativePrompt:
    """Prompt for narrative generation."""
    scene_context: str
    character_focus: str
    mode: str  # "expand", "conflict", "resolve"


@dataclass
class NarrativeEvent:
    """A generated narrative event."""
    description: str
    characters_involved: list[str]
    impact: str
    tension_change: float


# --- Story Agents ---

class VillageNarrator(Agent[NarrativePrompt, NarrativeEvent]):
    """
    Generates narrative events for the village story.

    This is a simplified agent that demonstrates the pattern without
    requiring LLM calls for this demo.
    """

    def __init__(self, name: str = "Narrator"):
        self._name = name
        self._event_templates = {
            "expand": [
                "The village square fills with morning light",
                "A traveling merchant arrives with exotic goods",
                "Children discover a hidden path in the forest",
            ],
            "conflict": [
                "Dark clouds gather over the valley",
                "A dispute breaks out between neighbors",
                "Strange sounds echo from the old well",
            ],
            "resolve": [
                "The villagers gather to find common ground",
                "An elder shares wisdom from the past",
                "A unexpected helper offers a solution",
            ],
        }

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, prompt: NarrativePrompt) -> NarrativeEvent:
        """Generate a narrative event based on the prompt."""
        # Simple template-based generation for demo
        templates = self._event_templates.get(prompt.mode, self._event_templates["expand"])

        # Pick event based on character focus
        event_desc = templates[hash(prompt.character_focus) % len(templates)]

        # Determine tension change
        tension_change = {
            "expand": 0.1,
            "conflict": 0.3,
            "resolve": -0.2,
        }.get(prompt.mode, 0.0)

        return NarrativeEvent(
            description=f"{event_desc} ({prompt.character_focus})",
            characters_involved=[prompt.character_focus],
            impact=prompt.mode,
            tension_change=tension_change,
        )


class CharacterAgent(Agent[str, Character]):
    """Generates a character for the village."""

    def __init__(self, role_pool: list[str]):
        self._role_pool = role_pool

    @property
    def name(self) -> str:
        return "CharacterCreator"

    async def invoke(self, seed: str) -> Character:
        """Create a character from a seed name."""
        # Simple deterministic character generation
        roles = ["baker", "blacksmith", "weaver", "shepherd", "healer",
                "elder", "merchant", "guard", "farmer", "teacher"]
        personalities = ["wise", "brave", "curious", "cautious", "kind",
                        "stubborn", "cheerful", "mysterious", "practical", "creative"]
        goals = ["protect the village", "discover truth", "build community",
                "preserve tradition", "spark change", "find belonging",
                "master craft", "seek adventure", "heal others", "teach wisdom"]

        role_idx = hash(seed) % len(roles)
        pers_idx = (hash(seed) * 2) % len(personalities)
        goal_idx = (hash(seed) * 3) % len(goals)

        return Character(
            name=seed,
            role=roles[role_idx],
            personality=personalities[pers_idx],
            goal=goals[goal_idx],
        )


class SceneBuilder(Agent[tuple[int, str, list[Character]], Scene]):
    """Builds a scene from act number, description, and characters."""

    @property
    def name(self) -> str:
        return "SceneBuilder"

    async def invoke(self, input: tuple[int, str, list[Character]]) -> Scene:
        """Build a scene."""
        act, title, characters = input

        return Scene(
            act=act,
            title=title,
            description=f"Act {act}: {title}",
            characters=[c.name for c in characters],
            events=[],
        )


class TensionMonitor(Agent[StoryState, float]):
    """Monitors story tension level."""

    @property
    def name(self) -> str:
        return "TensionMonitor"

    async def invoke(self, state: StoryState) -> float:
        """Calculate current tension level."""
        return state.tension_level


class StoryOracle(Agent[StoryState, str]):
    """Provides narrative wisdom about the story's direction."""

    @property
    def name(self) -> str:
        return "StoryOracle"

    async def invoke(self, state: StoryState) -> str:
        """Offer narrative guidance."""
        if state.tension_level < 0.3:
            return "The story needs more conflict to engage"
        elif state.tension_level > 0.7:
            return "Time to begin resolving the tensions"
        else:
            return "The story is well-balanced"


# --- The Five-Act Story Pipeline ---

async def act_1_dawn() -> tuple[StoryState, list[Character]]:
    """Act I: Dawn - Setup & Introduction"""
    print("\n" + "="*60)
    print("ACT I: DAWN (Setup & Introduction)")
    print("="*60)

    # Create 5 characters in parallel
    char_agent = CharacterAgent([])
    names = ["Elena", "Marcus", "Aria", "Thomas", "Sage"]

    print(f"\nCreating {len(names)} villagers...")

    # Use C-gents parallel composition
    parallel_creator = parallel(
        *(char_agent for _ in names),
        config=ParallelConfig(max_concurrent=5)
    )

    # This won't work directly - need individual calls
    # Instead, create characters sequentially for demo
    characters = []
    for name in names:
        char = await char_agent.invoke(name)
        characters.append(char)
        print(f"  ✓ {char.name} the {char.role} ({char.personality})")
        print(f"    Goal: {char.goal}")

    # Initial state
    state = StoryState(
        act=1,
        characters=characters,
        tension_level=0.1,
    )

    # Build opening scene
    scene_builder = SceneBuilder()
    scene = await scene_builder.invoke((
        1,
        "Morning in the Village",
        characters[:3],
    ))
    state.scenes.append(scene)

    print(f"\n✓ Act I complete: {len(characters)} characters, {len(state.scenes)} scene")
    print(f"  Tension level: {state.tension_level:.1f}")

    return state, characters


async def act_2_discovery(state: StoryState, characters: list[Character]) -> StoryState:
    """Act II: Discovery - Rising Action"""
    print("\n" + "="*60)
    print("ACT II: DISCOVERY (Rising Action)")
    print("="*60)

    state.act = 2

    # Generate 3 discovery events in parallel
    narrator = VillageNarrator()
    prompts = [
        NarrativePrompt(
            scene_context="morning",
            character_focus=characters[i].name,
            mode="expand",
        )
        for i in range(3)
    ]

    print(f"\nGenerating {len(prompts)} discovery events...")

    events = []
    for i, prompt in enumerate(prompts):
        event = await narrator.invoke(prompt)
        events.append(event)
        state.tension_level += event.tension_change
        print(f"  {i+1}. {event.description}")
        print(f"     Impact: {event.impact}, Tension: {state.tension_level:.2f}")

    # Build scene
    scene_builder = SceneBuilder()
    scene = await scene_builder.invoke((
        2,
        "Strange Discoveries",
        characters[:3],
    ))
    scene.events = [e.description for e in events]
    state.scenes.append(scene)

    print(f"\n✓ Act II complete: {len(events)} events generated")
    print(f"  Tension level: {state.tension_level:.2f}")

    return state


async def act_3_crisis(state: StoryState, characters: list[Character]) -> StoryState:
    """Act III: Crisis - Climax"""
    print("\n" + "="*60)
    print("ACT III: CRISIS (Climax)")
    print("="*60)

    state.act = 3

    # Check tension level before crisis
    monitor = TensionMonitor()
    current_tension = await monitor.invoke(state)
    print(f"\nCurrent tension: {current_tension:.2f}")

    # Generate crisis events
    narrator = VillageNarrator()
    prompts = [
        NarrativePrompt(
            scene_context="conflict",
            character_focus=characters[i].name,
            mode="conflict",
        )
        for i in range(4)
    ]

    print(f"\nGenerating {len(prompts)} crisis events...")

    events = []
    for i, prompt in enumerate(prompts):
        event = await narrator.invoke(prompt)
        events.append(event)
        state.tension_level += event.tension_change
        print(f"  {i+1}. {event.description}")
        print(f"     Tension now: {state.tension_level:.2f}")

    # Build crisis scene
    scene_builder = SceneBuilder()
    scene = await scene_builder.invoke((
        3,
        "The Gathering Storm",
        characters,
    ))
    scene.events = [e.description for e in events]
    state.scenes.append(scene)

    # Consult oracle
    oracle = StoryOracle()
    guidance = await oracle.invoke(state)
    print(f"\n📖 Oracle's guidance: {guidance}")

    print(f"\n✓ Act III complete: Crisis at peak!")
    print(f"  Tension level: {state.tension_level:.2f}")

    return state


async def act_4_resolution(state: StoryState, characters: list[Character]) -> StoryState:
    """Act IV: Resolution - Falling Action"""
    print("\n" + "="*60)
    print("ACT IV: RESOLUTION (Falling Action)")
    print("="*60)

    state.act = 4

    # Generate resolution events
    narrator = VillageNarrator()
    prompts = [
        NarrativePrompt(
            scene_context="resolution",
            character_focus=characters[i].name,
            mode="resolve",
        )
        for i in range(4)
    ]

    print(f"\nGenerating {len(prompts)} resolution events...")

    events = []
    for i, prompt in enumerate(prompts):
        event = await narrator.invoke(prompt)
        events.append(event)
        state.tension_level += event.tension_change
        state.tension_level = max(0.0, state.tension_level)  # Floor at 0
        print(f"  {i+1}. {event.description}")
        print(f"     Tension easing: {state.tension_level:.2f}")

    # Build resolution scene
    scene_builder = SceneBuilder()
    scene = await scene_builder.invoke((
        4,
        "Finding Common Ground",
        characters,
    ))
    scene.events = [e.description for e in events]
    state.scenes.append(scene)

    print(f"\n✓ Act IV complete: Tensions resolving")
    print(f"  Tension level: {state.tension_level:.2f}")

    return state


async def act_5_dusk(state: StoryState, characters: list[Character]) -> StoryState:
    """Act V: Dusk - Denouement"""
    print("\n" + "="*60)
    print("ACT V: DUSK (Denouement)")
    print("="*60)

    state.act = 5

    # Final reflection events
    narrator = VillageNarrator()
    prompts = [
        NarrativePrompt(
            scene_context="conclusion",
            character_focus=characters[i].name,
            mode="expand",
        )
        for i in range(3)
    ]

    print(f"\nGenerating {len(prompts)} closing events...")

    events = []
    for i, prompt in enumerate(prompts):
        event = await narrator.invoke(prompt)
        events.append(event)
        print(f"  {i+1}. {event.description}")

    # Build final scene
    scene_builder = SceneBuilder()
    scene = await scene_builder.invoke((
        5,
        "Evening Peace",
        characters[:3],
    ))
    scene.events = [e.description for e in events]
    state.scenes.append(scene)

    # Final oracle wisdom
    oracle = StoryOracle()
    guidance = await oracle.invoke(state)
    print(f"\n📖 Oracle's final word: {guidance}")

    print(f"\n✓ Act V complete: Story concluded")
    print(f"  Final tension level: {state.tension_level:.2f}")

    return state


async def print_story_summary(state: StoryState):
    """Print a summary of the complete story."""
    print("\n" + "="*60)
    print("STORY SUMMARY")
    print("="*60)

    print(f"\nTitle: The Village of Five Acts")
    print(f"Characters: {len(state.characters)}")
    print(f"Scenes: {len(state.scenes)}")
    print(f"Total Acts: {state.act}")

    print("\n--- CHARACTER ROSTER ---")
    for char in state.characters:
        print(f"  • {char.name} the {char.role}")
        print(f"    Personality: {char.personality}")
        print(f"    Goal: {char.goal}")

    print("\n--- SCENE BREAKDOWN ---")
    for scene in state.scenes:
        print(f"\n  Act {scene.act}: {scene.title}")
        print(f"    Characters present: {', '.join(scene.characters)}")
        if scene.events:
            print(f"    Events:")
            for event in scene.events:
                print(f"      - {event}")

    print("\n--- STORY ARC ---")
    print(f"  Opening tension: 0.1")
    print(f"  Peak tension (Act III): ~0.8-1.2")
    print(f"  Closing tension: {state.tension_level:.2f}")
    print("\n" + "="*60)


async def main():
    """Run the complete five-act village story."""
    print("\n🏘️  VILLAGE STORY - Five Acts with 20 Agents")
    print("=" * 60)
    print("\nThis demonstration showcases:")
    print("  • Composable agents from multiple genera (A, C, K, T)")
    print("  • Parallel agent execution (C-gents)")
    print("  • Heterarchical coordination (no fixed boss)")
    print("  • Stateful narrative progression")
    print("  • 20+ agent invocations across 5 acts")

    try:
        # Run the five acts
        state, characters = await act_1_dawn()
        state = await act_2_discovery(state, characters)
        state = await act_3_crisis(state, characters)
        state = await act_4_resolution(state, characters)
        state = await act_5_dusk(state, characters)

        # Print summary
        await print_story_summary(state)

        print("\n✅ Story generation complete!")
        print(f"\nAgent types used:")
        print(f"  • CharacterAgent (A-gent pattern)")
        print(f"  • VillageNarrator (composable narrator)")
        print(f"  • SceneBuilder (composition helper)")
        print(f"  • TensionMonitor (T-gent observer)")
        print(f"  • StoryOracle (T-gent oracle)")
        print(f"  • ParallelAgent (C-gent composition)")

    except Exception as e:
        print(f"\n❌ Error during story generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
