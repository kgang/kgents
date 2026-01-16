"""
Joy Commands: Delight in Interaction.

> *"Surprise and serendipity; discovery should feel rewarding."*
> — JOY_INDUCING Principle

These commands restore the Joy-Inducing principle to the CLI.
They are not gimmicks—they are infrastructure for creative work.

Commands:
    kg oblique      - Draw an Oblique Strategy card
    kg surprise     - Surface serendipity from the void
    kg yes-and      - Improv-style affirmation and extension
    kg challenge    - Daily coding challenge
    kg constrain    - Random creative constraint

AGENTESE Paths:
    void.serendipity    - Routes to surprise
    void.oblique        - Routes to oblique

Philosophy:
    Brian Eno created Oblique Strategies to break creative blocks.
    The void context represents Bataille's "Accursed Share"—entropy
    that, properly channeled, becomes generative rather than destructive.
    Joy commands are how we channel the void.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# Oblique Strategies (Brian Eno & Peter Schmidt, 1975)
# =============================================================================

OBLIQUE_STRATEGIES = [
    # Original strategies (abridged selection of ~50 most useful)
    "Honor thy error as a hidden intention",
    "What would your closest friend do?",
    "Remove specifics and convert to ambiguities",
    "Use an old idea",
    "State the problem in words as clearly as possible",
    "Only one element of each kind",
    "What would you do if you weren't afraid?",
    "Emphasize repetitions",
    "Don't be afraid of things because they're easy to do",
    "Don't be frightened of cliches",
    "What mistakes did you make last time?",
    "Abandon normal instruments",
    "Accept advice",
    "Be dirty",
    "Be extravagant",
    "Bridges -build -burn",
    "Change instrument roles",
    "Cluster analysis",
    "Consider different fading systems",
    "Convert a melodic element into a rhythmic element",
    "Courage!",
    "Cut a vital connection",
    "Decorate, decorate",
    "Define an area as 'safe' and use it as an anchor",
    "Destroy -nothing -the most important thing",
    "Discard an axiom",
    "Disconnect from desire",
    "Discover the recipes you are using and abandon them",
    "Do nothing for as long as possible",
    "Do something boring",
    "Do the washing up",
    "Do the words need changing?",
    "Don't be frightened to display your talents",
    "Don't break the silence",
    "Emphasize differences",
    "Faced with a choice, do both",
    "Find a safe part and use it as an anchor",
    "Give way to your worst impulse",
    "Go slowly all the way round the outside",
    "Go to an extreme, move back to a more comfortable place",
    "How would you explain this to your sister?",
    "Humanize something free of error",
    "Imagine the piece as a set of disconnected events",
    "Into the impossible",
    "Is it finished?",
    "Is there something missing?",
    "It is quite possible (after all)",
    "Just carry on",
    "Left channel, right channel, centre channel",
    "Look at the order in which you do things",
    "Look closely at the most embarrassing details and amplify them",
    "Lowest common denominator check -Loss of interest equals loss of the game",
    "Make a blank valuable by putting it in an exquisite frame",
    "Make an exhaustive list of everything you might do and do the last thing on the list",
    "Mechanize something idiosyncratic",
    "Mute and continue",
    "Only a part, not the whole",
    "Overtly resist change",
    "Put in earplugs",
    "Question the heroic approach",
    "Remember those quiet evenings",
    "Remove ambiguities and convert to specifics",
    "Remove the middle",
    "Repetition is a form of change",
    "Reverse",
    "Short circuit",
    "Shut the door and listen from outside",
    "Simple subtraction",
    "Simply a matter of work",
    "Slow preparation, fast execution",
    "Spectrum analysis",
    "Take a break",
    "Take away the elements in order of apparent non-importance",
    "The inconsistency principle",
    "The tape is now the music",
    "Think of the radio",
    "Tidy up",
    "Trust in the you of now",
    "Turn it upside down",
    "Twist the spine",
    "Use 'unqualified' people",
    "Use fewer notes",
    "Water",
    "What are you really thinking about just now?",
    "What is the reality of the situation?",
    "What wouldn't you do?",
    "Work at a different speed",
    "Would anybody want it?",
    "You are an engineer",
    "You can only make one dot at a time",
    "You don't have to be ashamed of using your own ideas",
    "Your mistake was a hidden intention",
]

# =============================================================================
# Creative Constraints Library
# =============================================================================

CREATIVE_CONSTRAINTS = [
    # Code constraints
    "No conditionals (no if statements)",
    "Under 50 lines total",
    "Single function only",
    "No loops (use recursion or map/reduce)",
    "No imports from external packages",
    "No comments (code must be self-documenting)",
    "Every function must be pure",
    "No mutation of any kind",
    "Maximum 3 parameters per function",
    "No exceptions (use Result types)",
    "Everything must be async",
    "No classes (functional only)",
    "No functions (OOP only)",
    "Single file implementation",
    "No numbers in variable names",
    "Alphabetical variable names only",
    # Design constraints
    "Monochrome only",
    "Single font weight",
    "No borders",
    "Everything must fit on one screen",
    "No hover states",
    "Mobile-first (no desktop optimization)",
    # Process constraints
    "Write tests first (truly)",
    "Pair program with a rubber duck",
    "No backspace key",
    "Document before implementing",
    "Use only tools from 10 years ago",
    # Creative constraints
    "Explain it to a child",
    "Make it a game",
    "Add unnecessary delight",
    "Name everything poetically",
    "Design for your grandmother",
]

# =============================================================================
# Coding Challenges
# =============================================================================

CODING_CHALLENGES = {
    "easy": [
        (
            "FizzBuzz Reimagined",
            "Implement FizzBuzz but make it beautiful. Focus on elegance, not just correctness.",
        ),
        (
            "Palindrome Poetry",
            "Write a function that checks palindromes and outputs them as ASCII art.",
        ),
        (
            "Temperature Converter",
            "Build a converter that handles edge cases gracefully and explains its reasoning.",
        ),
        (
            "Fibonacci with Memory",
            "Implement Fibonacci that shows its work—print the reasoning, not just the result.",
        ),
        ("Vowel Counter", "Count vowels, but in a way that would make a poet proud."),
        ("Reverse String", "Reverse a string using an unusual algorithm. Surprise yourself."),
    ],
    "medium": [
        (
            "State Machine Poetry",
            "Model a haiku as a state machine. Each syllable is a transition.",
        ),
        ("Recursive Art", "Create ASCII art using only recursion. No loops allowed."),
        (
            "Compression Haiku",
            "Compress a haiku to its minimal representation, then decompress it.",
        ),
        ("Async Meditation", "Write an async function that teaches patience through its timing."),
        (
            "Pattern Matching Joy",
            "Implement pattern matching that feels like discovery, not labor.",
        ),
        (
            "Graph of Gratitude",
            "Build a directed graph where nodes are things you're grateful for.",
        ),
    ],
    "hard": [
        (
            "Categorical Composition",
            "Implement function composition that proves it's a category (identity + associativity).",
        ),
        (
            "Monad Tutorial",
            "Write a monad that a beginner would understand, without using the word 'monad'.",
        ),
        (
            "Parser Combinator Art",
            "Build a parser for a language you invent. The language should express joy.",
        ),
        (
            "Concurrent Poetry",
            "Write concurrent code that produces poetry. Race conditions become creative accidents.",
        ),
        (
            "Proof Carrying Code",
            "Implement a function with a proof of correctness embedded in its type.",
        ),
        (
            "Entropy Generator",
            "Create a random number generator that uses environmental entropy creatively.",
        ),
    ],
}

# =============================================================================
# Yes-And Templates
# =============================================================================

YES_AND_TEMPLATES = [
    "Yes! And what if we took that further by {extension}?",
    "Absolutely! And that reminds me—what about {extension}?",
    "Yes, and building on that: {extension}.",
    "I love that. And here's a twist: {extension}.",
    "Yes! And the unexpected consequence might be {extension}.",
    "Brilliant. And if we're being bold, {extension}.",
    "Yes, and—hear me out—{extension}.",
    "That's it! And the natural next step is {extension}.",
]

YES_AND_EXTENSIONS = [
    "making it recursive",
    "adding a surprise element",
    "inverting the assumption",
    "combining it with something unexpected",
    "removing the obvious part",
    "making it playful",
    "adding constraints that liberate",
    "asking 'what would delight?'",
    "considering the opposite",
    "finding the hidden pattern",
    "making it a conversation",
    "adding memory to it",
    "making it composable",
    "turning the bug into a feature",
    "embracing the accident",
]


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class ObliqueCard:
    """A drawn Oblique Strategy card."""

    strategy: str
    drawn_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": self.strategy,
            "drawn_at": self.drawn_at.isoformat(),
        }


@dataclass
class Surprise:
    """A serendipitous discovery from the void."""

    content: str
    source: str  # "fossil", "mark", "crystal", "generated"
    surfaced_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "source": self.source,
            "surfaced_at": self.surfaced_at.isoformat(),
        }


@dataclass
class Challenge:
    """A coding challenge."""

    title: str
    description: str
    difficulty: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
        }


@dataclass
class Constraint:
    """A creative constraint."""

    constraint: str

    def to_dict(self) -> dict[str, Any]:
        return {"constraint": self.constraint}


@dataclass
class YesAnd:
    """An improv-style yes-and response."""

    original: str
    response: str
    extension: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "original": self.original,
            "response": self.response,
            "extension": self.extension,
        }


# =============================================================================
# Helper Functions
# =============================================================================


def _get_invocation_context(cmd: str, args: list[str]) -> Any:
    """Get invocation context from hollow.py."""
    try:
        from protocols.cli.hollow import get_invocation_context

        return get_invocation_context(cmd, args)
    except ImportError:
        return None


def _emit_output(
    human: str,
    semantic: dict[str, Any] | Any,
    ctx: "InvocationContext | None",
) -> None:
    """Emit output to appropriate channels."""
    print(human)

    if ctx is not None and hasattr(ctx, "emit_semantic"):
        data = semantic.to_dict() if hasattr(semantic, "to_dict") else semantic
        ctx.emit_semantic(data)


def _render_panel(content: str, title: str, style: str = "cyan") -> str:
    """Render content in a Rich panel, or fallback to simple box."""
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console(force_terminal=True, width=80)
        with console.capture() as capture:
            console.print(
                Panel(
                    f"[italic]{content}[/italic]",
                    title=f"[bold]{title}[/bold]",
                    border_style=style,
                    padding=(1, 2),
                )
            )
        return capture.get()
    except ImportError:
        # Fallback without Rich
        width = 60
        top = f"+-{title.center(width - 4, '-')}-+"
        bottom = "+" + "-" * (width - 2) + "+"
        wrapped = content[: width - 4]
        return f"\n{top}\n| {wrapped.center(width - 4)} |\n{bottom}\n"


def _get_fossil_wisdom() -> str | None:
    """
    Try to get ancient wisdom from Brain (archived insights, old marks).

    Returns None if Brain not available.
    """
    try:
        import asyncio

        from services.brain.service import BrainService  # type: ignore[import-untyped]

        brain = BrainService()
        # Try to get random old crystal
        crystals = asyncio.run(brain.search_crystals("*", limit=100))
        if crystals:
            ancient = random.choice(crystals)
            return f'"{ancient.content[:200]}..." — archived crystal from {ancient.created_at.strftime("%Y-%m")}'
    except Exception:
        pass

    return None


def _generate_serendipity() -> str:
    """Generate serendipitous wisdom when database unavailable."""
    aphorisms = [
        "The code you delete is the code that can't break.",
        "Every bug is a feature you haven't understood yet.",
        "Simplicity is the ultimate sophistication—but complexity is where the learning lives.",
        "The best documentation is code that doesn't need it.",
        "Types are not constraints; they are conversations with your future self.",
        "A test that never fails is a test that teaches nothing.",
        "The most elegant solution is often the one you didn't write.",
        "Composition is how complexity stays manageable.",
        "Every abstraction is a bet on what will change.",
        "The void is not empty—it's full of possibility.",
        "Joy in interaction is not optional—it's infrastructure.",
        "The accursed share of entropy can be channeled into creativity.",
        "What you resist persists; what you accept transforms.",
        "The shadow contains not just what you reject, but what you haven't yet become.",
        "Memory is not storage—it's continuous reconstruction.",
        "Categories don't constrain; they reveal structure that was always there.",
        "The best time to refactor was yesterday. The second best time is after the tests pass.",
        "Taste is accumulated judgment crystallized into instinct.",
    ]
    return random.choice(aphorisms)


async def _yes_and_with_llm(statement: str) -> str | None:
    """
    Generate yes-and response using LLM if available.

    Returns None if unavailable.
    """
    try:
        from agents.k.persona import DialogueMode
        from agents.k.soul import KgentSoul

        soul = KgentSoul(auto_llm=True)
        if not soul.has_llm:
            return None

        prompt = f"""The user said: "{statement}"

Respond in the spirit of improv "yes, and"—affirm their idea enthusiastically and extend it with something unexpected and creative. Be playful but not silly. One paragraph max."""

        response = await soul.dialogue(prompt, mode=DialogueMode.EXPLORE)
        return response.response if response.response else None

    except ImportError:
        return None
    except Exception:
        return None


# =============================================================================
# Command Handlers
# =============================================================================


def _print_oblique_help() -> None:
    """Print help for oblique command."""
    print(__doc__.split("Commands:")[0].strip())
    print()
    print("USAGE:")
    print("  kg oblique              Draw a single Oblique Strategy card")
    print("  kg oblique --all        List all available strategies")
    print("  kg oblique --json       Output as JSON")
    print("  kg oblique --help       Show this help")
    print()
    print("ABOUT:")
    print("  Oblique Strategies were created by Brian Eno and Peter Schmidt")
    print("  in 1975 as a set of cards to break creative blocks.")
    print("  Each card offers a cryptic suggestion that reframes the problem.")
    print()
    print("EXAMPLE:")
    print("  $ kg oblique")
    print("  +------------ Oblique Strategy ------------+")
    print('  | "Honor thy error as a hidden intention"  |')
    print("  +-------------------------------------------+")


@handler(
    "oblique", is_async=False, needs_pty=False, tier=1, description="Draw an Oblique Strategy card"
)
def cmd_oblique(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Draw an Oblique Strategy card.

    Brian Eno's Oblique Strategies are cryptic suggestions
    designed to break creative blocks. Each card reframes
    the problem in an unexpected way.

    AGENTESE Path: void.oblique

    Returns:
        0 on success
    """
    if ctx is None:
        ctx = _get_invocation_context("oblique", args)

    # Help
    if "--help" in args or "-h" in args:
        _print_oblique_help()
        return 0

    json_mode = "--json" in args
    show_all = "--all" in args

    if show_all:
        # List all strategies
        if json_mode:
            import json

            print(json.dumps({"strategies": OBLIQUE_STRATEGIES}, indent=2))
        else:
            print("\n=== All Oblique Strategies ===\n")
            for i, strategy in enumerate(OBLIQUE_STRATEGIES, 1):
                print(f"  {i:2}. {strategy}")
            print(f"\n  Total: {len(OBLIQUE_STRATEGIES)} strategies")
            print()
        return 0

    # Draw a card
    card = ObliqueCard(strategy=random.choice(OBLIQUE_STRATEGIES))

    if json_mode:
        import json

        print(json.dumps(card.to_dict(), indent=2))
    else:
        output = _render_panel(card.strategy, "Oblique Strategy", "magenta")
        print(output)

    # Emit semantic for pipelines
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(card.to_dict())

    return 0


def _print_surprise_help() -> None:
    """Print help for surprise command."""
    print("SURPRISE: Surface serendipity from the void")
    print()
    print("USAGE:")
    print("  kg surprise             Surface random serendipity")
    print("  kg surprise --fossil    Ancient wisdom only (from Brain archives)")
    print("  kg surprise --json      Output as JSON")
    print("  kg surprise --help      Show this help")
    print()
    print("ABOUT:")
    print("  The void context represents Bataille's 'Accursed Share'—")
    print("  entropy that, when channeled, becomes generative.")
    print("  This command surfaces unexpected wisdom from:")
    print("    - Archived crystals from Brain")
    print("    - Old marks from Witness")
    print("    - Generated aphorisms")
    print()
    print("AGENTESE PATH: void.serendipity")


@handler(
    "surprise",
    is_async=False,
    needs_pty=False,
    tier=1,
    description="Surface serendipity from the void",
)
def cmd_surprise(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Surface serendipity from the void.

    Pulls random wisdom from archived insights, old marks,
    or generates serendipitous aphorisms.

    AGENTESE Path: void.serendipity

    Returns:
        0 on success
    """
    if ctx is None:
        ctx = _get_invocation_context("surprise", args)

    # Help
    if "--help" in args or "-h" in args:
        _print_surprise_help()
        return 0

    json_mode = "--json" in args
    fossil_only = "--fossil" in args

    # Try to get fossil wisdom first
    content = None
    source = "generated"

    if fossil_only:
        content = _get_fossil_wisdom()
        if content:
            source = "fossil"
        else:
            # Fossil requested but unavailable
            if json_mode:
                import json

                print(
                    json.dumps({"error": "No fossils found (Brain unavailable or empty)"}, indent=2)
                )
            else:
                print("\n[No fossils found—Brain unavailable or empty]")
                print("Try 'kg brain capture' to start building your archive.\n")
            return 1
    else:
        # Try fossil first, fall back to generated
        content = _get_fossil_wisdom()
        if content:
            source = "fossil"
        else:
            content = _generate_serendipity()
            source = "generated"

    surprise = Surprise(content=content, source=source)

    if json_mode:
        import json

        print(json.dumps(surprise.to_dict(), indent=2))
    else:
        title = "Ancient Wisdom" if source == "fossil" else "Serendipity"
        style = "yellow" if source == "fossil" else "cyan"
        output = _render_panel(content, title, style)
        print(output)

    # Emit semantic
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(surprise.to_dict())

    return 0


def _print_yes_and_help() -> None:
    """Print help for yes-and command."""
    print("YES-AND: Improv-style affirmation and extension")
    print()
    print("USAGE:")
    print('  kg yes-and "Your idea here"    Affirm and extend the idea')
    print('  kg yes-and --llm "..."         Use LLM for creative extension')
    print("  kg yes-and --json              Output as JSON")
    print("  kg yes-and --help              Show this help")
    print()
    print("ABOUT:")
    print("  'Yes, and...' is the foundational rule of improv comedy.")
    print("  Instead of blocking ideas, you accept and build on them.")
    print("  Use this command to overcome creative blocks and brainstorm.")
    print()
    print("EXAMPLES:")
    print('  $ kg yes-and "We should add caching"')
    print("  Yes! And what if we took that further by making it composable?")
    print()
    print('  $ kg yes-and --llm "What if types were colors?"')
    print("  [LLM generates creative extension]")


@handler("yes-and", is_async=False, needs_pty=False, tier=1, description="Improv-style affirmation")
def cmd_yes_and(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Improv-style affirmation and extension.

    Takes user input, affirms it enthusiastically, and extends
    with something unexpected. Useful for brainstorming and
    overcoming creative blocks.

    Returns:
        0 on success, 1 on error
    """
    import asyncio

    if ctx is None:
        ctx = _get_invocation_context("yes-and", args)

    # Help
    if "--help" in args or "-h" in args:
        _print_yes_and_help()
        return 0

    json_mode = "--json" in args
    use_llm = "--llm" in args

    # Extract statement
    statement_parts = []
    for arg in args:
        if arg.startswith("-"):
            continue
        statement_parts.append(arg)

    statement = " ".join(statement_parts)

    if not statement:
        print("[YES-AND] What idea would you like to build on?")
        print('  Example: kg yes-and "We should add caching"')
        return 1

    # Generate response
    response = None
    extension = None

    if use_llm:
        response = asyncio.run(_yes_and_with_llm(statement))
        if response:
            extension = "LLM-generated"
        else:
            print("[YES-AND] LLM unavailable, using templates")

    if not response:
        # Template-based response
        extension = random.choice(YES_AND_EXTENSIONS)
        template = random.choice(YES_AND_TEMPLATES)
        response = template.format(extension=extension)

    yes_and = YesAnd(original=statement, response=response, extension=extension or "")

    if json_mode:
        import json

        print(json.dumps(yes_and.to_dict(), indent=2))
    else:
        print()
        print(f"  \033[90mYou said:\033[0m {statement}")
        print()
        print(f"  \033[1;32m{response}\033[0m")
        print()

    # Emit semantic
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(yes_and.to_dict())

    return 0


def _print_challenge_help() -> None:
    """Print help for challenge command."""
    print("CHALLENGE: Daily coding challenge")
    print()
    print("USAGE:")
    print("  kg challenge                    Get a random challenge")
    print("  kg challenge --difficulty easy  Specify difficulty (easy|medium|hard)")
    print("  kg challenge --json             Output as JSON")
    print("  kg challenge --help             Show this help")
    print()
    print("DIFFICULTY LEVELS:")
    print("  easy   - Fundamentals with a twist (5-15 min)")
    print("  medium - Creative problem-solving (15-45 min)")
    print("  hard   - Deep categorical thinking (45+ min)")
    print()
    print("ABOUT:")
    print("  These challenges are designed to build joy, not just skill.")
    print("  Focus on elegance and creativity, not just correctness.")


@handler("challenge", is_async=False, needs_pty=False, tier=1, description="Daily coding challenge")
def cmd_challenge(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Present a coding challenge.

    Challenges are designed to build joy through creative
    constraints. Focus on elegance, not just correctness.

    Returns:
        0 on success
    """
    if ctx is None:
        ctx = _get_invocation_context("challenge", args)

    # Help
    if "--help" in args or "-h" in args:
        _print_challenge_help()
        return 0

    json_mode = "--json" in args

    # Parse difficulty
    difficulty = "medium"  # default
    for i, arg in enumerate(args):
        if arg == "--difficulty" and i + 1 < len(args):
            d = args[i + 1].lower()
            if d in CODING_CHALLENGES:
                difficulty = d
            else:
                print(f"[CHALLENGE] Unknown difficulty: {d}")
                print("  Valid: easy, medium, hard")
                return 1

    # Select challenge
    challenges = CODING_CHALLENGES[difficulty]
    title, description = random.choice(challenges)

    challenge = Challenge(title=title, description=description, difficulty=difficulty)

    if json_mode:
        import json

        print(json.dumps(challenge.to_dict(), indent=2))
    else:
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text

            console = Console()

            difficulty_colors = {
                "easy": "green",
                "medium": "yellow",
                "hard": "red",
            }

            content = Text()
            content.append(description, style="italic")
            content.append("\n\n")
            content.append("Difficulty: ", style="dim")
            content.append(difficulty.upper(), style=f"bold {difficulty_colors[difficulty]}")

            console.print()
            console.print(
                Panel(
                    content,
                    title=f"[bold]Challenge: {title}[/bold]",
                    border_style="blue",
                    padding=(1, 2),
                )
            )
            console.print()

        except ImportError:
            # Fallback
            print()
            print(f"=== Challenge: {title} ===")
            print()
            print(f"  {description}")
            print()
            print(f"  Difficulty: {difficulty.upper()}")
            print()

    # Emit semantic
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(challenge.to_dict())

    return 0


def _print_constrain_help() -> None:
    """Print help for constrain command."""
    print("CONSTRAIN: Random creative constraint")
    print()
    print("USAGE:")
    print("  kg constrain            Get a random constraint")
    print("  kg constrain --all      List all constraints")
    print("  kg constrain --json     Output as JSON")
    print("  kg constrain --help     Show this help")
    print()
    print("ABOUT:")
    print("  Creative constraints liberate by limiting options.")
    print("  When everything is possible, nothing gets done.")
    print("  A constraint focuses energy and reveals solutions.")
    print()
    print("EXAMPLES:")
    print("  $ kg constrain")
    print("  +-------- Creative Constraint --------+")
    print('  | "No conditionals (no if statements)" |')
    print("  +--------------------------------------+")


@handler(
    "constrain", is_async=False, needs_pty=False, tier=1, description="Random creative constraint"
)
def cmd_constrain(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Apply a random creative constraint.

    Constraints liberate by limiting. Use this to add
    creative challenge to any task.

    Returns:
        0 on success
    """
    if ctx is None:
        ctx = _get_invocation_context("constrain", args)

    # Help
    if "--help" in args or "-h" in args:
        _print_constrain_help()
        return 0

    json_mode = "--json" in args
    show_all = "--all" in args

    if show_all:
        if json_mode:
            import json

            print(json.dumps({"constraints": CREATIVE_CONSTRAINTS}, indent=2))
        else:
            print("\n=== All Creative Constraints ===\n")
            for i, c in enumerate(CREATIVE_CONSTRAINTS, 1):
                print(f"  {i:2}. {c}")
            print(f"\n  Total: {len(CREATIVE_CONSTRAINTS)} constraints")
            print()
        return 0

    # Draw a constraint
    selected = random.choice(CREATIVE_CONSTRAINTS)
    constraint = Constraint(constraint=selected)

    if json_mode:
        import json

        print(json.dumps(constraint.to_dict(), indent=2))
    else:
        output = _render_panel(selected, "Creative Constraint", "green")
        print(output)

    # Emit semantic
    if ctx is not None and hasattr(ctx, "emit_semantic"):
        ctx.emit_semantic(constraint.to_dict())

    return 0


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "cmd_oblique",
    "cmd_surprise",
    "cmd_yes_and",
    "cmd_challenge",
    "cmd_constrain",
    "OBLIQUE_STRATEGIES",
    "CREATIVE_CONSTRAINTS",
    "CODING_CHALLENGES",
]
