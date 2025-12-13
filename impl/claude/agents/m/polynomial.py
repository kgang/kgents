"""
Memory as Polynomial Agent.

The polynomial functor P(y) = Σₛ y^{D(s)} captures state-dependent behavior.
Memory games ARE polynomial functors—each position offers a set of directions.

This module provides:
- MemoryState: State representation for memory agents
- MemoryPolynomial: PolyAgent implementation backed by Four Pillars
- Game-derived polynomials: Automatically construct polynomials from language games

Mathematical Foundation:
    For a language game G:
    - Positions = all possible positions in the game
    - Directions(s) = game.directions(s)
    - Transition(s, d) = (game.play(s, d).to_position, game.play(s, d))

This unifies memory operations with the polynomial agent framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, FrozenSet, Generic, TypeVar

if TYPE_CHECKING:
    from .crystal import MemoryCrystal
    from .games import LanguageGame, Move
    from .inference import ActiveInferenceAgent

S = TypeVar("S")
T = TypeVar("T")


class MemoryMode(Enum):
    """Operating modes for memory polynomial agents."""

    IDLE = auto()  # Waiting for focus
    FOCUSED = auto()  # Focused on a concept
    EXPLORING = auto()  # Following associative trails
    CONSOLIDATING = auto()  # Running inference-guided consolidation
    PLAYING = auto()  # Engaged in a language game


@dataclass
class MemoryState:
    """
    State of memory polynomial agent.

    Captures:
    - mode: Current operating mode
    - focus: Current concept focus (if any)
    - game: Active language game
    - position: Current position in the game
    - resolution: Current resolution level
    - history: Recent transitions for trace
    """

    mode: MemoryMode = MemoryMode.IDLE
    focus: str | None = None
    game: str = "recall"
    position: str = ""
    resolution: float = 1.0
    history: list[str] = field(default_factory=list)

    def __hash__(self) -> int:
        """Enable use in frozen sets."""
        return hash((self.mode, self.focus, self.game, self.position))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemoryState):
            return False
        return (
            self.mode == other.mode
            and self.focus == other.focus
            and self.game == other.game
            and self.position == other.position
        )


@dataclass
class MemoryDirection:
    """
    A direction (input) for memory transitions.

    Directions can be:
    - Language game moves (elaborate, compress, associate, etc.)
    - Meta-operations (focus, unfocus, switch_game)
    - Consolidation triggers (evaluate, consolidate)
    """

    action: str
    target: str | None = None  # Optional target for actions

    def __hash__(self) -> int:
        return hash((self.action, self.target))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemoryDirection):
            return False
        return self.action == other.action and self.target == other.target

    def __repr__(self) -> str:
        if self.target:
            return f"Direction({self.action}→{self.target})"
        return f"Direction({self.action})"


@dataclass
class MemoryOutput:
    """
    Output from a memory transition.

    Contains:
    - content: Retrieved/modified content (if any)
    - resolution: Resolution at output
    - grammatical: Whether the move was grammatical
    - metadata: Additional context
    """

    content: str | None = None
    resolution: float = 1.0
    grammatical: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryPolynomial(Generic[T]):
    """
    Memory as polynomial agent.

    State: MemoryState (mode, focus, game, position, resolution)
    Input: MemoryDirection (action + target)
    Output: MemoryOutput (content + metadata)

    The polynomial functor structure P(y) = Σₛ y^{D(s)} means:
    - Each memory state s offers directions D(s)
    - The total agent is the sum over all states
    - Composition works because games compose

    Example:
        crystal = MemoryCrystal(dimension=64)
        games = {"recall": create_recall_game()}
        poly = MemoryPolynomial(crystal, games)

        state = MemoryState(mode=MemoryMode.IDLE)
        directions = poly.directions(state)  # Available actions

        # Execute a transition
        new_state, output = poly.transition(state, MemoryDirection("focus", "python"))
    """

    def __init__(
        self,
        crystal: "MemoryCrystal[T]",
        games: dict[str, "LanguageGame[Any]"],
        inference: "ActiveInferenceAgent[T] | None" = None,
    ) -> None:
        """
        Initialize memory polynomial.

        Args:
            crystal: The memory substrate
            games: Dict of language games for navigation
            inference: Optional inference agent for evaluation
        """
        self.crystal = crystal
        self.games = games
        self.inference = inference
        self._initial_state = MemoryState()

    @property
    def name(self) -> str:
        """Agent name."""
        return "MemoryPolynomial"

    @property
    def positions(self) -> FrozenSet[MemoryState]:
        """
        Valid positions (states).

        Note: This is theoretically infinite (all possible focus states),
        so we return the reachable states from initial.
        """
        # Return representative states for each mode
        states: set[MemoryState] = set()

        # Add idle state
        states.add(MemoryState(mode=MemoryMode.IDLE))

        # Add focused states for each concept
        for concept_id in self.crystal.concepts:
            states.add(
                MemoryState(
                    mode=MemoryMode.FOCUSED,
                    focus=concept_id,
                    game="recall",
                    position=concept_id,
                )
            )

        # Add game states
        for game_name in self.games:
            states.add(
                MemoryState(
                    mode=MemoryMode.PLAYING,
                    game=game_name,
                )
            )

        return frozenset(states)

    def directions(self, state: MemoryState) -> FrozenSet[MemoryDirection]:
        """
        Valid directions from a state.

        The directions depend on the current mode:
        - IDLE: Can focus or start exploring
        - FOCUSED: Can play game moves or unfocus
        - PLAYING: Game-specific directions
        - CONSOLIDATING: Consolidation actions
        """
        dirs: set[MemoryDirection] = set()

        match state.mode:
            case MemoryMode.IDLE:
                # Can focus on any concept
                for concept_id in self.crystal.concepts:
                    dirs.add(MemoryDirection("focus", concept_id))
                # Can start exploring
                dirs.add(MemoryDirection("explore"))
                # Can switch games
                for game_name in self.games:
                    dirs.add(MemoryDirection("switch_game", game_name))
                # Can trigger consolidation
                if self.inference:
                    dirs.add(MemoryDirection("consolidate"))

            case MemoryMode.FOCUSED:
                # Can play game moves
                if state.focus and state.game in self.games:
                    game = self.games[state.game]
                    for d in game.directions(state.position or state.focus):
                        dirs.add(MemoryDirection(d))

                # Can unfocus
                dirs.add(MemoryDirection("unfocus"))

                # Can switch games
                for game_name in self.games:
                    if game_name != state.game:
                        dirs.add(MemoryDirection("switch_game", game_name))

                # Can evaluate
                if self.inference:
                    dirs.add(MemoryDirection("evaluate"))

            case MemoryMode.EXPLORING:
                # Follow gradients
                for concept_id in self.crystal.concepts:
                    dirs.add(MemoryDirection("visit", concept_id))
                dirs.add(MemoryDirection("stop"))

            case MemoryMode.PLAYING:
                # Pure game mode
                if state.game in self.games and state.position:
                    game = self.games[state.game]
                    for d in game.directions(state.position):
                        dirs.add(MemoryDirection(d))
                dirs.add(MemoryDirection("stop"))

            case MemoryMode.CONSOLIDATING:
                # Consolidation in progress
                dirs.add(MemoryDirection("continue"))
                dirs.add(MemoryDirection("stop"))

        return frozenset(dirs)

    def transition(
        self, state: MemoryState, direction: MemoryDirection
    ) -> tuple[MemoryState, MemoryOutput]:
        """
        Execute a state transition.

        Args:
            state: Current state
            direction: Direction to move

        Returns:
            Tuple of (new_state, output)
        """
        action = direction.action
        target = direction.target

        # Track history
        history = state.history.copy()
        history.append(f"{action}:{target or ''}")
        if len(history) > 20:
            history = history[-20:]

        match action:
            case "focus":
                if target and target in self.crystal.concepts:
                    pattern = self.crystal.get_pattern(target)
                    content = self.crystal.retrieve_content(target)
                    return (
                        MemoryState(
                            mode=MemoryMode.FOCUSED,
                            focus=target,
                            game=state.game,
                            position=target,
                            resolution=pattern.resolution if pattern else 1.0,
                            history=history,
                        ),
                        MemoryOutput(
                            content=str(content) if content else None,
                            resolution=pattern.resolution if pattern else 1.0,
                            grammatical=True,
                            metadata={"action": "focused", "concept": target},
                        ),
                    )
                return (state, MemoryOutput(grammatical=False))

            case "unfocus":
                return (
                    MemoryState(
                        mode=MemoryMode.IDLE,
                        focus=None,
                        game=state.game,
                        history=history,
                    ),
                    MemoryOutput(grammatical=True, metadata={"action": "unfocused"}),
                )

            case "switch_game":
                if target and target in self.games:
                    return (
                        MemoryState(
                            mode=state.mode,
                            focus=state.focus,
                            game=target,
                            position=state.focus or "",
                            resolution=state.resolution,
                            history=history,
                        ),
                        MemoryOutput(
                            grammatical=True,
                            metadata={"action": "switched_game", "game": target},
                        ),
                    )
                return (state, MemoryOutput(grammatical=False))

            case "explore":
                return (
                    MemoryState(
                        mode=MemoryMode.EXPLORING,
                        game=state.game,
                        history=history,
                    ),
                    MemoryOutput(
                        grammatical=True,
                        metadata={"action": "exploring"},
                    ),
                )

            case "visit":
                if target and target in self.crystal.concepts:
                    pattern = self.crystal.get_pattern(target)
                    content = self.crystal.retrieve_content(target)
                    return (
                        MemoryState(
                            mode=MemoryMode.EXPLORING,
                            focus=target,
                            game=state.game,
                            position=target,
                            resolution=pattern.resolution if pattern else 1.0,
                            history=history,
                        ),
                        MemoryOutput(
                            content=str(content) if content else None,
                            resolution=pattern.resolution if pattern else 1.0,
                            grammatical=True,
                            metadata={"action": "visited", "concept": target},
                        ),
                    )
                return (state, MemoryOutput(grammatical=False))

            case "stop":
                return (
                    MemoryState(
                        mode=MemoryMode.IDLE,
                        focus=state.focus,
                        game=state.game,
                        history=history,
                    ),
                    MemoryOutput(grammatical=True, metadata={"action": "stopped"}),
                )

            case "evaluate":
                if self.inference and state.focus:
                    # This would be async in real use
                    return (
                        state,
                        MemoryOutput(
                            grammatical=True,
                            metadata={
                                "action": "evaluate_requested",
                                "concept": state.focus,
                            },
                        ),
                    )
                return (state, MemoryOutput(grammatical=False))

            case "consolidate":
                return (
                    MemoryState(
                        mode=MemoryMode.CONSOLIDATING,
                        game=state.game,
                        history=history,
                    ),
                    MemoryOutput(
                        grammatical=True,
                        metadata={"action": "consolidating"},
                    ),
                )

            case "continue":
                # Continue consolidation
                return (
                    state,
                    MemoryOutput(
                        grammatical=True,
                        metadata={"action": "continuing"},
                    ),
                )

            case _:
                # Try as game move
                if state.game in self.games and state.position:
                    game = self.games[state.game]
                    if action in game.directions(state.position):
                        move = game.play(state.position, action)
                        return (
                            MemoryState(
                                mode=state.mode,
                                focus=state.focus,
                                game=state.game,
                                position=move.to_position,
                                resolution=state.resolution,
                                history=history,
                            ),
                            MemoryOutput(
                                content=move.to_position,
                                grammatical=move.is_grammatical,
                                metadata={
                                    "action": "game_move",
                                    "from": move.from_position,
                                    "direction": action,
                                    "to": move.to_position,
                                },
                            ),
                        )

                return (state, MemoryOutput(grammatical=False))

    def invoke(
        self, state: MemoryState, direction: MemoryDirection
    ) -> tuple[MemoryState, MemoryOutput]:
        """
        Execute one step with validation.

        Args:
            state: Current state
            direction: Direction to move

        Returns:
            Tuple of (new_state, output)

        Raises:
            ValueError: If direction is not valid for state
        """
        valid = self.directions(state)
        if direction not in valid:
            raise ValueError(f"Invalid direction {direction} for state {state.mode}")
        return self.transition(state, direction)

    def run(
        self, initial: MemoryState, directions: list[MemoryDirection]
    ) -> tuple[MemoryState, list[MemoryOutput]]:
        """
        Run through a sequence of directions.

        Args:
            initial: Starting state
            directions: Sequence of directions

        Returns:
            Tuple of (final_state, outputs)
        """
        state = initial
        outputs: list[MemoryOutput] = []
        for d in directions:
            state, out = self.transition(state, d)
            outputs.append(out)
        return state, outputs

    def initial_state(self) -> MemoryState:
        """Get the initial state."""
        return self._initial_state


# ========== Factory Functions ==========


def create_memory_polynomial(
    crystal: "MemoryCrystal[T]",
    include_default_games: bool = True,
    inference: "ActiveInferenceAgent[T] | None" = None,
) -> MemoryPolynomial[T]:
    """
    Create a memory polynomial with default configuration.

    Args:
        crystal: The memory crystal
        include_default_games: If True, include standard games
        inference: Optional inference agent

    Returns:
        Configured MemoryPolynomial
    """
    games: dict[str, "LanguageGame[Any]"] = {}

    if include_default_games:
        try:
            from .games import (
                create_associative_game,
                create_dialectical_game,
                create_navigation_game,
                create_recall_game,
            )

            games = {
                "recall": create_recall_game(),
                "dialectical": create_dialectical_game(),
                "navigation": create_navigation_game(),
                "associative": create_associative_game(),
            }
        except ImportError:
            pass

    return MemoryPolynomial(crystal=crystal, games=games, inference=inference)


def game_to_polynomial(
    game: "LanguageGame[Any]",
    initial_positions: list[Any],
    max_positions: int = 100,
) -> dict[str, Any]:
    """
    Extract polynomial signature from a language game.

    The polynomial P(y) = Σₛ y^{D(s)} is represented as:
    {position: direction_count, ...}

    Args:
        game: The language game
        initial_positions: Starting positions to explore
        max_positions: Maximum positions to explore (prevents infinite loops)

    Returns:
        Dict mapping positions to direction counts
    """
    signature: dict[Any, int] = {}
    visited: set[Any] = set()
    to_visit = list(initial_positions)

    while to_visit and len(visited) < max_positions:
        pos = to_visit.pop(0)
        if pos in visited:
            continue
        visited.add(pos)

        dirs = game.directions(pos)
        signature[pos] = len(dirs)

        # Explore reachable positions (limited)
        for d in dirs:
            move = game.play(pos, d)
            if (
                move.is_grammatical
                and move.to_position not in visited
                and len(to_visit) < max_positions
            ):
                to_visit.append(move.to_position)

    return {
        "positions": list(signature.keys()),
        "signature": signature,
        "total_directions": sum(signature.values()),
        "explored": len(visited),
        "truncated": len(to_visit) > 0,
    }
