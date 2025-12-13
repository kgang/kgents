"""
Language Games: Wittgensteinian Memory Access.

Memory access as playing a game. From Wittgenstein: meaning is use.
A concept's "memory" is the set of valid moves one can make with it
in context. This implements the Four Pillars insight: memory is
reconstruction through grammatical participation, not retrieval.

Key Concepts:
- LanguageGame: A game with positions (states) and directions (moves)
- Move: A transition from one position to another
- Grammar: Rules for valid moves
- Polynomial structure: P(y) = Σₛ y^{D(s)}

The polynomial functor insight: each position offers a set of directions,
and the game is the sum over all positions of the directions available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Generic, Protocol, TypeVar

S = TypeVar("S")  # State/Position type
D = TypeVar("D")  # Direction type


class Direction(Enum):
    """Standard directions in memory games."""

    ELABORATE = auto()  # Expand with detail
    COMPRESS = auto()  # Summarize
    ASSOCIATE = auto()  # Link to related concepts
    FORGET = auto()  # Graceful forgetting
    WITNESS = auto()  # Show history
    REFINE = auto()  # Dialectical challenge
    MANIFEST = auto()  # Collapse to observer's view
    NAVIGATE = auto()  # Move to related concept


@dataclass(frozen=True)
class Move(Generic[S]):
    """A move in a language game.

    Records the transition from one position to another,
    including whether it was grammatical (valid).
    """

    from_position: S
    direction: str
    to_position: S
    is_grammatical: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class LanguageGame(Generic[S]):
    """
    Memory access as playing a game.

    Polynomial functor structure: P(y) = Σₛ y^{D(s)}
    - S: positions (states)
    - D(s): directions (valid moves from state s)

    A concept's memory is what you can DO with it, not what it IS.
    This is the Wittgensteinian insight made operational.

    Example:
        game = LanguageGame(
            name="recall",
            directions=lambda s: {"elaborate", "compress", "associate"},
            rules=lambda s, d: True,  # All moves allowed
            transitions=lambda s, d: f"{s}:{d}",  # State transformation
        )

        move = game.play("user preferences", "elaborate")
        if move.is_grammatical:
            print(f"Moved to: {move.to_position}")
    """

    def __init__(
        self,
        name: str,
        directions: Callable[[S], set[str]] | None = None,
        rules: Callable[[S, str], bool] | None = None,
        transitions: Callable[[S, str], S] | None = None,
    ) -> None:
        """Initialize language game.

        Args:
            name: Game identifier
            directions: Function returning valid directions from a position
            rules: Function checking if a move is grammatical
            transitions: Function computing the new position
        """
        self.name = name
        self._positions: set[S] = set()

        # Default implementations
        self._directions = directions or (lambda s: set())
        self._rules = rules or (lambda s, d: d in self.directions(s))
        self._transitions = transitions or (lambda s, d: s)

    @property
    def positions(self) -> set[S]:
        """Known positions in the game."""
        return self._positions.copy()

    def add_position(self, position: S) -> None:
        """Register a position in the game."""
        self._positions.add(position)

    def directions(self, position: S) -> set[str]:
        """Get valid directions from a position.

        Args:
            position: Current position/state

        Returns:
            Set of valid direction names
        """
        return self._directions(position)

    def is_grammatical(self, position: S, direction: str) -> bool:
        """Check if a move is grammatical (valid).

        A move is grammatical if:
        1. The direction is valid from this position
        2. The rules allow it

        Args:
            position: Current position
            direction: Proposed direction

        Returns:
            True if the move is valid
        """
        if direction not in self.directions(position):
            return False
        return self._rules(position, direction)

    def apply(self, position: S, direction: str) -> S:
        """Make a move, returning the new position.

        Args:
            position: Current position
            direction: Direction to move

        Returns:
            New position

        Raises:
            ValueError: If the move is ungrammatical
        """
        if not self.is_grammatical(position, direction):
            raise ValueError(f"Ungrammatical move: {direction} from {position}")
        return self._transitions(position, direction)

    def play(self, position: S, direction: str) -> Move[S]:
        """Attempt a move and return the result.

        Unlike apply(), this never raises - it returns a Move
        with is_grammatical=False for invalid moves.

        Args:
            position: Current position
            direction: Attempted direction

        Returns:
            Move record with result
        """
        grammatical = self.is_grammatical(position, direction)

        if grammatical:
            new_position = self._transitions(position, direction)
        else:
            new_position = position

        return Move(
            from_position=position,
            direction=direction,
            to_position=new_position,
            is_grammatical=grammatical,
        )

    def trace(self, start: S, directions: list[str]) -> list[Move[S]]:
        """Execute a sequence of moves and return the trace.

        Args:
            start: Starting position
            directions: Sequence of directions to follow

        Returns:
            List of Move records
        """
        moves: list[Move[S]] = []
        current = start

        for direction in directions:
            move = self.play(current, direction)
            moves.append(move)
            if move.is_grammatical:
                current = move.to_position

        return moves


# ========== Pre-defined Game Types ==========


def create_recall_game() -> LanguageGame[str]:
    """The recall game: cue → associated memories.

    Directions:
    - elaborate: Add detail to memory
    - compress: Summarize memory
    - associate: Link to related concepts
    - forget: Begin graceful forgetting
    """

    def directions(state: str) -> set[str]:
        return {"elaborate", "compress", "associate", "forget", "witness"}

    def transitions(state: str, direction: str) -> str:
        if direction == "elaborate":
            return f"{state}:detailed"
        elif direction == "compress":
            return f"{state}:summary"
        elif direction == "associate":
            return f"{state}:linked"
        elif direction == "forget":
            return f"{state}:fading"
        elif direction == "witness":
            return f"{state}:history"
        return state

    return LanguageGame(
        name="recall",
        directions=directions,
        transitions=transitions,
    )


def create_navigation_game() -> LanguageGame[tuple[str, str]]:
    """The navigation game: position → nearby landmarks.

    State is a tuple of (concept, context).

    Directions:
    - north/south/east/west: Spatial navigation (metaphorical)
    - zoom_in: Focus on detail
    - zoom_out: Broader context
    """

    def directions(state: tuple[str, str]) -> set[str]:
        return {"north", "south", "east", "west", "zoom_in", "zoom_out"}

    def transitions(state: tuple[str, str], direction: str) -> tuple[str, str]:
        concept, context = state
        if direction == "zoom_in":
            return (f"{concept}:detail", context)
        elif direction == "zoom_out":
            return (f"{concept}:context", context)
        else:
            # Cardinal directions change context
            return (concept, f"{context}:{direction}")

    return LanguageGame(
        name="navigation",
        directions=directions,
        transitions=transitions,
    )


def create_dialectical_game() -> LanguageGame[str]:
    """The dialectical game: thesis → antithesis → synthesis.

    Directions:
    - challenge: Propose antithesis
    - defend: Strengthen current position
    - synthesize: Attempt sublation
    - abandon: Give up position
    """

    def directions(state: str) -> set[str]:
        base = {"challenge", "defend", "synthesize", "abandon"}
        # Can only synthesize if there's a tension marker
        if ":challenged" not in state:
            base.discard("synthesize")
        return base

    def rules(state: str, direction: str) -> bool:
        # Can't abandon if already synthesized
        if ":synthesized" in state and direction == "abandon":
            return False
        return direction in directions(state)

    def transitions(state: str, direction: str) -> str:
        if direction == "challenge":
            return f"{state}:challenged"
        elif direction == "defend":
            return f"{state}:defended"
        elif direction == "synthesize":
            # Remove tension markers, add synthesis marker
            base = state.replace(":challenged", "").replace(":defended", "")
            return f"{base}:synthesized"
        elif direction == "abandon":
            return ":abandoned"
        return state

    return LanguageGame(
        name="dialectical",
        directions=directions,
        rules=rules,
        transitions=transitions,
    )


def create_associative_game() -> LanguageGame[str]:
    """The associative game: concept → related concepts.

    Models spreading activation in semantic memory.

    Directions:
    - activate: Spread activation to neighbors
    - inhibit: Reduce activation
    - prime: Prepare for retrieval
    - decay: Natural forgetting
    """

    def directions(state: str) -> set[str]:
        return {"activate", "inhibit", "prime", "decay"}

    def transitions(state: str, direction: str) -> str:
        if direction == "activate":
            return f"{state}:active"
        elif direction == "inhibit":
            return f"{state}:inhibited"
        elif direction == "prime":
            return f"{state}:primed"
        elif direction == "decay":
            return f"{state}:decayed"
        return state

    return LanguageGame(
        name="associative",
        directions=directions,
        transitions=transitions,
    )


def create_episodic_game() -> LanguageGame[tuple[str, str, str]]:
    """The episodic game: (what, where, when) → memory reconstruction.

    State is a tuple of (event, location, time).

    Directions:
    - contextualize: Add contextual detail
    - temporalize: Navigate in time
    - spatialize: Navigate in space
    - personalize: Add emotional/personal color
    """

    def directions(state: tuple[str, str, str]) -> set[str]:
        return {"contextualize", "temporalize", "spatialize", "personalize"}

    def transitions(
        state: tuple[str, str, str], direction: str
    ) -> tuple[str, str, str]:
        event, location, time = state
        if direction == "contextualize":
            return (f"{event}:contextual", location, time)
        elif direction == "temporalize":
            return (event, location, f"{time}:navigated")
        elif direction == "spatialize":
            return (event, f"{location}:navigated", time)
        elif direction == "personalize":
            return (f"{event}:personal", location, time)
        return state

    return LanguageGame(
        name="episodic",
        directions=directions,
        transitions=transitions,
    )


# ========== Game Composition ==========


class ComposedGame(Generic[S]):
    """Composition of multiple language games.

    Allows playing multiple games simultaneously, with moves
    that affect state across games.
    """

    def __init__(self, games: list[LanguageGame[S]]) -> None:
        """Initialize with list of games.

        Args:
            games: Games to compose
        """
        self._games = {g.name: g for g in games}

    def directions(self, position: S) -> dict[str, set[str]]:
        """Get directions for each game.

        Returns:
            Dict mapping game name to available directions
        """
        return {name: game.directions(position) for name, game in self._games.items()}

    def play_in(self, game_name: str, position: S, direction: str) -> Move[S] | None:
        """Play a move in a specific game.

        Args:
            game_name: Which game to play in
            position: Current position
            direction: Direction to move

        Returns:
            Move result, or None if game not found
        """
        game = self._games.get(game_name)
        if game is None:
            return None
        return game.play(position, direction)


# ========== Polynomial Functor Interface ==========


@dataclass
class PolynomialPosition(Generic[S]):
    """Position in polynomial functor interpretation.

    P(y) = Σₛ y^{D(s)}

    Each position contributes its directions to the functor.
    """

    position: S
    directions: set[str]

    def as_polynomial_term(self) -> tuple[S, int]:
        """Return (state, exponent) for polynomial interpretation."""
        return (self.position, len(self.directions))


def game_to_polynomial(
    game: LanguageGame[S], positions: list[S]
) -> list[PolynomialPosition[S]]:
    """Convert a game's structure to polynomial representation.

    Args:
        game: The language game
        positions: Positions to analyze

    Returns:
        List of PolynomialPosition representing the polynomial
    """
    return [
        PolynomialPosition(
            position=pos,
            directions=game.directions(pos),
        )
        for pos in positions
    ]


def polynomial_signature(game: LanguageGame[S], positions: list[S]) -> dict[int, int]:
    """Compute the polynomial signature: exponent → count.

    This shows the distribution of direction counts across positions.

    Args:
        game: The language game
        positions: Positions to analyze

    Returns:
        Dict mapping exponent (direction count) to frequency
    """
    poly = game_to_polynomial(game, positions)
    signature: dict[int, int] = {}

    for pp in poly:
        exp = len(pp.directions)
        signature[exp] = signature.get(exp, 0) + 1

    return signature
