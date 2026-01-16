"""
AGENTESE Path Composition

Enables: kg "self.brain.search 'auth'" ">>" "concept.analyze"

The >> operator passes the output of the left path as input to the right path.
This is the CLI manifestation of categorical composition.

Phase 3.3 CLI Renaissance: Command Composition via AGENTESE paths.

This module implements the spec promise: "path >> path works uniformly"

Categorical Laws:
    - Associativity: (f >> g) >> h = f >> (g >> h)
    - Identity: Id >> f = f = f >> Id

Teaching:
    gotcha: Composition is right-associative by default, but the result is the same
            due to associativity law. (a >> b) >> c produces identical output to
            a >> (b >> c). This is not an accident but a categorical law.
            (Evidence: test_compose_paths.py::test_associativity_property)

    gotcha: The Logos.compose() method and this module serve different purposes:
            - Logos.compose() is for programmatic composition within Python code
            - compose_paths module is for CLI invocation of compositions
            Both use the same underlying categorical machinery.
            (Evidence: test_compose_paths.py::test_cli_vs_programmatic)

    gotcha: Each path in the composition must be a valid AGENTESE path with aspect.
            If a path fails, the composition short-circuits with that error.
            (Evidence: test_compose_paths.py::test_error_propagation)
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese import Logos, Observer


def parse_composition(command: str) -> list[str]:
    """
    Parse a composition command into paths.

    Handles whitespace variations around the >> operator and preserves
    quoted arguments within paths.

    Examples:
        "self.brain.search 'auth' >> concept.analyze"
            -> ["self.brain.search 'auth'", "concept.analyze"]

        "world.doc.manifest >> concept.summary.refine >> self.memory.engram"
            -> ["world.doc.manifest", "concept.summary.refine", "self.memory.engram"]

        "  path1  >>  path2  "
            -> ["path1", "path2"]

    Args:
        command: The composition command string

    Returns:
        List of individual paths to compose

    Note:
        Empty paths are filtered out to handle edge cases like trailing >>
    """
    # Split by >> (with optional whitespace)
    # This regex handles any amount of whitespace around >>
    paths = re.split(r"\s*>>\s*", command)
    return [p.strip() for p in paths if p.strip()]


async def compose_paths(
    left: str,
    right: str,
    observer: "Observer | Umwelt[Any, Any]",
    logos: "Logos",
    initial_input: Any = None,
) -> Any:
    """
    Compose two AGENTESE paths.

    Implements: left >> right
    Semantics: right(left(initial_input))

    This is the fundamental binary composition operation. For chains of
    more than two paths, use compose_chain() which is more efficient.

    Args:
        left: The first AGENTESE path (executed first)
        right: The second AGENTESE path (receives left's output)
        observer: Observer for both invocations
        logos: Logos instance for path resolution
        initial_input: Optional initial value passed to left path

    Returns:
        Result of right path execution

    Raises:
        PathNotFoundError: If either path cannot be resolved
        AffordanceError: If observer lacks access to either aspect

    Example:
        result = await compose_paths(
            "self.brain.search",
            "concept.analyze",
            observer,
            logos,
            initial_input="authentication"
        )
    """
    # Execute left path
    left_result = await logos.invoke(left, observer, input=initial_input)

    # Pass left_result as input to right
    right_result = await logos.invoke(right, observer, input=left_result)

    return right_result


async def compose_chain(
    paths: list[str],
    observer: "Observer | Umwelt[Any, Any]",
    logos: "Logos",
    initial_input: Any = None,
) -> Any:
    """
    Compose a chain of AGENTESE paths.

    Implements: p1 >> p2 >> p3 >> ... >> pn
    Associativity: (p1 >> p2) >> p3 = p1 >> (p2 >> p3)

    The associativity law means we can process paths left-to-right,
    threading the result through each step. This is more efficient
    than building up nested compositions.

    Args:
        paths: List of AGENTESE paths to compose
        observer: Observer for all invocations
        logos: Logos instance for path resolution
        initial_input: Optional initial value for the first path

    Returns:
        Final result after all paths executed

    Raises:
        ValueError: If paths list is empty
        PathNotFoundError: If any path cannot be resolved
        AffordanceError: If observer lacks access to any aspect

    Example:
        result = await compose_chain(
            [
                "world.doc.manifest",
                "concept.summary.refine",
                "self.memory.engram",
            ],
            observer,
            logos,
        )

    Note:
        If paths has only one element, that single path is invoked.
        If paths is empty, a ValueError is raised.
    """
    if not paths:
        raise ValueError("Cannot compose empty path list")

    result = initial_input

    for path in paths:
        result = await logos.invoke(path, observer, input=result)

    return result


async def compose_from_string(
    composition_string: str,
    observer: "Observer | Umwelt[Any, Any]",
    logos: "Logos",
    initial_input: Any = None,
) -> Any:
    """
    Parse and execute a composition from a string.

    This is the main entry point for CLI composition execution.
    It combines parse_composition() and compose_chain().

    Args:
        composition_string: String like "path1 >> path2 >> path3"
        observer: Observer for all invocations
        logos: Logos instance
        initial_input: Optional initial value

    Returns:
        Final result after all paths executed

    Raises:
        ValueError: If composition string results in no valid paths

    Example:
        # From CLI
        result = await compose_from_string(
            "self.brain.search 'auth' >> concept.analyze",
            observer,
            logos,
        )
    """
    paths = parse_composition(composition_string)

    if not paths:
        raise ValueError(f"No valid paths in composition: {composition_string!r}")

    return await compose_chain(paths, observer, logos, initial_input)


def is_composition(command: str) -> bool:
    """
    Check if a command string contains composition syntax.

    Args:
        command: The command string to check

    Returns:
        True if the command contains >> operator

    Example:
        is_composition("self.brain.search")  # False
        is_composition("self.brain >> concept.analyze")  # True
    """
    return ">>" in command


# =============================================================================
# Verification Helpers (for testing categorical laws)
# =============================================================================


async def verify_associativity(
    p1: str,
    p2: str,
    p3: str,
    observer: "Observer | Umwelt[Any, Any]",
    logos: "Logos",
    initial_input: Any = None,
) -> tuple[Any, Any, bool]:
    """
    Verify the associativity law: (p1 >> p2) >> p3 = p1 >> (p2 >> p3)

    This is a testing utility to verify the categorical law holds for
    specific paths. Note that due to side effects or non-deterministic
    paths, this may not always produce identical results, but for
    well-behaved functional paths, it should.

    Args:
        p1, p2, p3: Three AGENTESE paths
        observer: Observer for all invocations
        logos: Logos instance
        initial_input: Optional initial value

    Returns:
        Tuple of (left_associative_result, right_associative_result, are_equal)

    Example:
        left, right, equal = await verify_associativity(
            "world.doc.manifest",
            "concept.summary.refine",
            "self.memory.engram",
            observer,
            logos,
        )
        assert equal, "Associativity law violated!"
    """
    # (p1 >> p2) >> p3 - left associative
    intermediate = await compose_paths(p1, p2, observer, logos, initial_input)
    left_result = await logos.invoke(p3, observer, input=intermediate)

    # p1 >> (p2 >> p3) - right associative
    # First execute p1
    p1_result = await logos.invoke(p1, observer, input=initial_input)
    # Then compose p2 >> p3 and apply to p1's result
    right_result = await compose_paths(p2, p3, observer, logos, p1_result)

    # Compare results (simple equality)
    are_equal = left_result == right_result

    return (left_result, right_result, are_equal)
