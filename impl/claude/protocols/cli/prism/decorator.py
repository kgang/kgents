"""
@expose Decorator - Mark methods for CLI exposure.

Instead of writing argument parsers manually, methods are annotated
with @expose to declare their CLI surface. The Prism then uses
introspection to generate argparse configurations.

See: spec/protocols/prism.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    pass

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class ExposeMetadata:
    """
    Metadata attached to @expose decorated methods.

    Attributes:
        help: Short description shown in CLI help (required).
        examples: Usage examples for extended help.
        aliases: Alternative command names.
        hidden: If True, exclude from help listings but still callable.
    """

    help: str
    examples: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    hidden: bool = False


def expose(
    help: str,
    examples: list[str] | None = None,
    aliases: list[str] | None = None,
    hidden: bool = False,
) -> Callable[[F], F]:
    """
    Mark a method as exposed to the CLI.

    The decorated method's type hints are used to generate argparse
    arguments. The docstring provides extended help text.

    Args:
        help: Short description for CLI help (required).
        examples: Usage examples shown in extended help.
        aliases: Alternative command names (e.g., ["ls"] for "list").
        hidden: If True, command works but doesn't appear in help.

    Returns:
        Decorator function that attaches ExposeMetadata.

    Example:
        @expose(
            help="Reify domain into Tongue artifact",
            examples=['kgents grammar reify "Calendar"'],
        )
        async def reify(self, domain: str, level: str = "command") -> dict:
            '''
            Transform a domain description into a formal Tongue.

            The domain string describes the conceptual space.
            '''
            ...
    """

    def decorator(fn: F) -> F:
        fn._expose_meta = ExposeMetadata(  # type: ignore[attr-defined]
            help=help,
            examples=examples or [],
            aliases=aliases or [],
            hidden=hidden,
        )
        return fn

    return decorator


def is_exposed(fn: Any) -> bool:
    """
    Check if a function has the @expose decorator.

    Args:
        fn: Any callable to check.

    Returns:
        True if fn has _expose_meta attribute (was decorated with @expose).
    """
    return hasattr(fn, "_expose_meta") and isinstance(fn._expose_meta, ExposeMetadata)


def get_expose_meta(fn: Any) -> ExposeMetadata | None:
    """
    Retrieve ExposeMetadata from a decorated function.

    Args:
        fn: A function that may have been decorated with @expose.

    Returns:
        ExposeMetadata if present, None otherwise.
    """
    meta = getattr(fn, "_expose_meta", None)
    if isinstance(meta, ExposeMetadata):
        return meta
    return None
