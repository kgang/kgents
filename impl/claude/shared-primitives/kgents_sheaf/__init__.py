"""
kgents-sheaf: Local-to-Global Coherence

A sheaf ensures that multiple views of the same data remain coherent.
When you have different perspectives on the same object, a sheaf
guarantees they agree where they overlap.

Quick Start (10 minutes or less):

    from kgents_sheaf import Sheaf, View, SheafVerification

    # Define views
    views = {
        "summary": View("summary", render=lambda content: content[:100]),
        "detail": View("detail", render=lambda content: content),
        "outline": View("outline", render=extract_headings),
    }

    # Create sheaf
    sheaf = Sheaf(
        name="document",
        views=views,
        glue=lambda view_data: canonical_content,
    )

    # Verify coherence
    result = sheaf.verify_coherence(content)
    if result.passed:
        print("All views are coherent!")

What is a Sheaf?

    A sheaf is a mathematical structure that:
    1. Has "sections" (data) over "opens" (regions/views)
    2. Sections that agree on overlaps can be "glued" together
    3. Gluing is unique (there's only one way to combine them)

    In programming terms:
    - Views = Different ways to look at the same data
    - Gluing = Combining partial views into a consistent whole
    - Coherence = All views derive from the same source

Why use a Sheaf?

    1. Multiple views, one truth: Summary, detail, outline all stay in sync
    2. Conflict detection: Find when views disagree
    3. Canonical source: Define which view is the "source of truth"
    4. Change propagation: Update one view, others follow

Real-World Example:

    # Document with multiple views
    class DocumentSheaf(Sheaf):
        def __init__(self, document):
            self.document = document
            super().__init__(
                name="document",
                views={
                    "markdown": MarkdownView(),
                    "outline": OutlineView(),
                    "references": ReferencesView(),
                },
                glue=lambda _: self.document.content,
            )

        def propagate(self, source_view: str, new_content: str):
            # Update canonical content
            self.document.content = new_content
            # Re-render all views
            return {name: view.render(new_content)
                    for name, view in self.views.items()}

License: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

# Type variables
T = TypeVar("T")  # Content type
V = TypeVar("V")  # Rendered view type
# Protocol-specific type variables with proper variance
T_contra = TypeVar("T_contra", contravariant=True)  # Input type for protocols
V_co = TypeVar("V_co", covariant=True)  # Output type for protocols


# -----------------------------------------------------------------------------
# View Protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class ViewProtocol(Protocol[T_contra, V_co]):
    """
    Protocol for sheaf views.

    A view renders content into a specific representation.
    Views must be pure functions of the content.
    """

    @property
    def name(self) -> str:
        """View name for identification."""
        ...

    def render(self, content: T_contra, **kwargs: Any) -> V_co:
        """
        Render content into this view's representation.

        Args:
            content: The canonical content to render
            **kwargs: View-specific options

        Returns:
            The rendered view
        """
        ...


# -----------------------------------------------------------------------------
# View Implementation
# -----------------------------------------------------------------------------


@dataclass
class View(Generic[T, V]):
    """
    A view onto content.

    Views are projections of canonical content into different forms.
    Each view type interprets content differently.

    Example:
        >>> summary_view = View(
        ...     name="summary",
        ...     render_fn=lambda content: content[:100] + "..."
        ... )
        >>> rendered = summary_view.render("A very long document...")
    """

    name: str
    render_fn: Callable[[T], V]
    _last_rendered: V | None = field(default=None, repr=False)
    _last_content: T | None = field(default=None, repr=False)

    def render(self, content: T, **kwargs: Any) -> V:
        """Render content into this view."""
        self._last_content = content
        self._last_rendered = self.render_fn(content)
        return self._last_rendered

    @property
    def cached_render(self) -> V | None:
        """Get the last rendered value."""
        return self._last_rendered


# -----------------------------------------------------------------------------
# Sheaf Verification
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class SheafVerification:
    """
    Result of sheaf coherence verification.

    Example:
        >>> result = sheaf.verify_coherence(content)
        >>> if result:
        ...     print("All views coherent!")
        >>> else:
        ...     for conflict in result.conflicts:
        ...         print(f"Conflict: {conflict}")
    """

    passed: bool
    checked_views: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    coverage: float = 1.0
    message: str = ""

    def __bool__(self) -> bool:
        """Allow using in boolean context."""
        return self.passed

    def __repr__(self) -> str:
        status = "PASSED" if self.passed else "FAILED"
        return (
            f"SheafVerification({status}, "
            f"views={len(self.checked_views)}, "
            f"conflicts={len(self.conflicts)}, "
            f"coverage={self.coverage:.1%})"
        )


# -----------------------------------------------------------------------------
# Sheaf
# -----------------------------------------------------------------------------


@dataclass
class Sheaf(Generic[T]):
    """
    A sheaf over content with multiple views.

    The sheaf manages multiple views of the same content,
    ensuring they remain coherent as edits are made.

    Key operations:
    - activate_view: Get/render a specific view
    - propagate: Propagate changes from one view to all others
    - verify_coherence: Check that all views are consistent
    - glue: Combine views into canonical content

    Example:
        >>> sheaf = Sheaf(
        ...     name="document",
        ...     views={
        ...         "prose": View("prose", lambda c: c),
        ...         "outline": View("outline", extract_headings),
        ...     },
        ...     glue=lambda views: views["prose"],
        ... )
        >>> result = sheaf.verify_coherence(my_content)
    """

    name: str
    views: dict[str, View[T, Any]] = field(default_factory=dict)
    glue_fn: Callable[[dict[str, Any]], T] | None = None
    canonical_view: str = ""  # Which view is the source of truth
    _content: T | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Set default canonical view if not specified."""
        if not self.canonical_view and self.views:
            self.canonical_view = next(iter(self.views.keys()))

    def add_view(self, view: View[T, Any]) -> None:
        """Add a view to the sheaf."""
        self.views[view.name] = view

    def get_view(self, name: str) -> View[T, Any] | None:
        """Get a view by name."""
        return self.views.get(name)

    def activate_view(self, name: str, content: T, **kwargs: Any) -> Any:
        """
        Render a specific view.

        Args:
            name: View name
            content: Content to render
            **kwargs: View-specific options

        Returns:
            Rendered view data

        Raises:
            KeyError: If view not found
        """
        if name not in self.views:
            raise KeyError(
                f"Unknown view: '{name}'. Available views: {list(self.views.keys())}"
            )
        self._content = content
        return self.views[name].render(content, **kwargs)

    def render_all(self, content: T, **kwargs: Any) -> dict[str, Any]:
        """
        Render all views.

        Args:
            content: Content to render
            **kwargs: Passed to each view

        Returns:
            Dict mapping view names to rendered data
        """
        self._content = content
        return {
            name: view.render(content, **kwargs) for name, view in self.views.items()
        }

    def propagate(
        self,
        source_view: str,
        new_content: T,
    ) -> dict[str, Any]:
        """
        Propagate changes from one view to all others.

        When content changes via one view, this updates all other
        views to maintain coherence.

        Args:
            source_view: View where change originated
            new_content: New canonical content

        Returns:
            Dict mapping view names to their updated renders
        """
        self._content = new_content
        return self.render_all(new_content)

    def verify_coherence(self, content: T) -> SheafVerification:
        """
        Verify all views are coherent.

        Coherence means all views derive from the same canonical content.
        This renders all views and checks they can be glued back together.

        Args:
            content: Content to verify against

        Returns:
            SheafVerification with detailed results
        """
        conflicts: list[str] = []
        checked: list[str] = []

        # Render all views
        rendered = self.render_all(content)

        for view_name, view in self.views.items():
            checked.append(view_name)

            # Check that view's cached content matches input
            if view._last_content != content:
                conflicts.append(f"{view_name}: content mismatch (stale cache)")

        # If we have a glue function, verify round-trip
        if self.glue_fn is not None:
            try:
                glued = self.glue_fn(rendered)
                if glued != content:
                    conflicts.append(
                        "Glue round-trip failed: glued content differs from original"
                    )
            except Exception as e:
                conflicts.append(f"Glue function error: {e}")

        return SheafVerification(
            passed=len(conflicts) == 0,
            checked_views=checked,
            conflicts=conflicts,
            coverage=len(checked) / len(self.views) if self.views else 1.0,
            message=(
                "All views coherent"
                if not conflicts
                else f"{len(conflicts)} conflict(s)"
            ),
        )

    def glue(self, rendered_views: dict[str, Any] | None = None) -> T:
        """
        Combine views into canonical content.

        If no glue function is provided, returns the canonical view's content.

        Args:
            rendered_views: Optional pre-rendered views

        Returns:
            Canonical content
        """
        if self.glue_fn is not None:
            views_data = rendered_views or {
                name: view._last_rendered for name, view in self.views.items()
            }
            return self.glue_fn(views_data)

        # Default: return cached content
        if self._content is not None:
            return self._content

        # Fallback: get from canonical view
        if self.canonical_view in self.views:
            view = self.views[self.canonical_view]
            if view._last_content is not None:
                return view._last_content

        raise ValueError("No content available for gluing")

    def __repr__(self) -> str:
        return (
            f"Sheaf({self.name!r}, "
            f"views=[{', '.join(self.views.keys())}], "
            f"canonical={self.canonical_view!r})"
        )


# -----------------------------------------------------------------------------
# Common View Factories
# -----------------------------------------------------------------------------


def identity_view(name: str = "identity") -> View[T, T]:
    """Create a view that passes content through unchanged."""
    return View(name=name, render_fn=lambda x: x)


def slice_view(name: str, start: int, end: int | None = None) -> View[str, str]:
    """Create a view that slices string content."""
    return View(name=name, render_fn=lambda x: x[start:end])


def transform_view(
    name: str,
    transform: Callable[[T], V],
) -> View[T, V]:
    """Create a view with a custom transform function."""
    return View(name=name, render_fn=transform)


# -----------------------------------------------------------------------------
# Convenience: Coherent Type
# -----------------------------------------------------------------------------


@dataclass
class Coherent(Generic[T]):
    """
    A coherent bundle of views over content.

    This is a simplified sheaf for common use cases where you just
    need to keep multiple derived values in sync.

    Example:
        >>> coherent = Coherent(
        ...     canonical="Hello, World!",
        ...     derived={
        ...         "upper": lambda s: s.upper(),
        ...         "lower": lambda s: s.lower(),
        ...         "length": lambda s: len(s),
        ...     }
        ... )
        >>> print(coherent.get("upper"))  # "HELLO, WORLD!"
        >>> coherent.update("Goodbye!")
        >>> print(coherent.get("upper"))  # "GOODBYE!"
    """

    canonical: T
    derived: dict[str, Callable[[T], Any]] = field(default_factory=dict)
    _cache: dict[str, Any] = field(default_factory=dict, repr=False)

    def get(self, name: str) -> Any:
        """Get a derived value (cached)."""
        if name not in self._cache:
            if name not in self.derived:
                raise KeyError(f"Unknown derived value: {name}")
            self._cache[name] = self.derived[name](self.canonical)
        return self._cache[name]

    def update(self, new_canonical: T) -> None:
        """Update canonical content and invalidate cache."""
        self.canonical = new_canonical
        self._cache.clear()

    def all_derived(self) -> dict[str, Any]:
        """Compute and return all derived values."""
        return {name: self.get(name) for name in self.derived}


__all__ = [
    # Protocol
    "ViewProtocol",
    # Core types
    "View",
    "Sheaf",
    "SheafVerification",
    # Convenience
    "Coherent",
    # View factories
    "identity_view",
    "slice_view",
    "transform_view",
]
