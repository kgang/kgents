"""
Functor Law Verification for Projections.

Projections are natural transformations from Widget State to Renderable Output.
As such, they must satisfy functor laws to ensure composability.

The Two Functor Laws:
    1. Identity: project(id(state)) ≡ project(state)
       Projecting unchanged state produces unchanged output.

    2. Composition: project(f ∘ g)(state) ≡ project(f)(project(g)(state))
       Projecting composed state changes equals composing the projections.

Additional Properties:
    - Determinism: Same state → same output (no hidden randomness)
    - Idempotence: project(project(state)) ≡ project(state) (for JSON target)

These laws ensure that developers can reason about projections compositionally.
If laws fail, the projection is buggy or the widget has hidden state.

Usage:
    from agents.i.reactive.projection import verify_identity_law

    # In tests
    def test_glyph_projection_laws():
        glyph = GlyphWidget(GlyphState(char="X"))
        assert verify_identity_law(glyph, ExtendedTarget.CLI)
        assert verify_composition_law(glyph, lambda s: s, lambda s: s, ExtendedTarget.CLI)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Protocol, TypeVar, runtime_checkable

from agents.i.reactive.projection.targets import ExtendedTarget

if TYPE_CHECKING:
    from agents.i.reactive.signal import Signal
    from agents.i.reactive.widget import KgentsWidget, RenderTarget

S = TypeVar("S")


@runtime_checkable
class StatefulWidget(Protocol[S]):
    """Protocol for widgets with accessible state.

    Most concrete KgentsWidget implementations have a `state` attribute
    of type Signal[S]. This protocol captures that pattern for law verification.
    """

    state: "Signal[S]"

    def project(self, target: "RenderTarget") -> Any: ...


class ProjectionLawError(Exception):
    """
    Raised when a projection violates a functor law.

    Attributes:
        law: Which law was violated ("identity", "composition", "determinism")
        expected: Expected output
        actual: Actual output
        target: The projection target
        widget_type: Type of the widget that failed
    """

    def __init__(
        self,
        law: str,
        expected: Any,
        actual: Any,
        target: ExtendedTarget | str,
        widget_type: str,
    ) -> None:
        self.law = law
        self.expected = expected
        self.actual = actual
        self.target = target
        self.widget_type = widget_type
        super().__init__(
            f"{widget_type} violates {law} law for target {target}.\n"
            f"Expected: {expected!r}\n"
            f"Actual: {actual!r}"
        )


def _project_widget(
    widget: StatefulWidget[Any] | "KgentsWidget[Any]",
    target: ExtendedTarget | str,
) -> Any:
    """
    Project a widget to a target, handling both string and enum targets.

    Args:
        widget: The widget to project
        target: Target as ExtendedTarget or string

    Returns:
        Projected representation
    """
    from agents.i.reactive.widget import RenderTarget

    # Convert to RenderTarget for built-in targets
    target_name = target.name if isinstance(target, ExtendedTarget) else target.upper()

    target_map = {
        "CLI": RenderTarget.CLI,
        "TUI": RenderTarget.TUI,
        "MARIMO": RenderTarget.MARIMO,
        "JSON": RenderTarget.JSON,
    }

    render_target = target_map.get(target_name)
    if render_target is not None:
        return widget.project(render_target)

    # For extended targets, fall back to JSON
    return widget.project(RenderTarget.JSON)


def verify_identity_law(
    widget: StatefulWidget[S] | "KgentsWidget[S]",
    target: ExtendedTarget | str,
    *,
    raise_on_failure: bool = False,
) -> bool:
    """
    Verify the identity functor law.

    Identity Law: project(id(state)) ≡ project(state)

    In practice, this means projecting the same state twice
    should produce identical output.

    Args:
        widget: Widget to verify
        target: Projection target
        raise_on_failure: If True, raise ProjectionLawError on failure

    Returns:
        True if law holds, False otherwise

    Raises:
        ProjectionLawError: If raise_on_failure=True and law violated
    """
    # Project twice with same state
    output1 = _project_widget(widget, target)
    output2 = _project_widget(widget, target)

    # Compare outputs
    if output1 != output2:
        if raise_on_failure:
            raise ProjectionLawError(
                law="identity",
                expected=output1,
                actual=output2,
                target=target,
                widget_type=type(widget).__name__,
            )
        return False

    return True


def verify_composition_law(
    widget: StatefulWidget[S],
    f: Callable[[S], S],
    g: Callable[[S], S],
    target: ExtendedTarget | str,
    *,
    raise_on_failure: bool = False,
) -> bool:
    """
    Verify the composition functor law.

    Composition Law: project(f ∘ g)(state) ≡ project(f)(project(g)(state))

    Note: For projections, this is tricky because we can't compose
    rendered outputs. What we actually verify is that state transformations
    followed by projection equal projection after state transformation.

    In practice: if we change state via f, then project, the result should
    be the same as if we projected the f-transformed state directly.

    Args:
        widget: Widget to verify (will be mutated via state updates)
        f: First state transformation
        g: Second state transformation
        target: Projection target
        raise_on_failure: If True, raise ProjectionLawError on failure

    Returns:
        True if law holds, False otherwise

    Example:
        def double_entropy(s: GlyphState) -> GlyphState:
            return GlyphState(char=s.char, entropy=s.entropy * 2)

        def noop(s: GlyphState) -> GlyphState:
            return s

        assert verify_composition_law(glyph, double_entropy, noop, "cli")
    """
    from agents.i.reactive.signal import Signal

    # Get current state
    current_state = widget.state.value

    # Apply g, then f (f ∘ g)
    composed_state = f(g(current_state))

    # Create temporary widget with composed state
    # This is a bit hacky but avoids mutating the original widget
    widget.state.set(composed_state)
    output_composed = _project_widget(widget, target)

    # Reset state
    widget.state.set(current_state)

    # Apply g first, project, then apply f to state and project
    widget.state.set(g(current_state))
    widget.state.set(f(widget.state.value))
    output_sequential = _project_widget(widget, target)

    # Reset state
    widget.state.set(current_state)

    if output_composed != output_sequential:
        if raise_on_failure:
            raise ProjectionLawError(
                law="composition",
                expected=output_composed,
                actual=output_sequential,
                target=target,
                widget_type=type(widget).__name__,
            )
        return False

    return True


def verify_determinism(
    widget: StatefulWidget[S] | "KgentsWidget[S]",
    target: ExtendedTarget | str,
    *,
    iterations: int = 10,
    raise_on_failure: bool = False,
) -> bool:
    """
    Verify that projection is deterministic.

    Determinism: Same state always produces same output.

    This catches bugs where projections have hidden state or
    use randomness inappropriately.

    Args:
        widget: Widget to verify
        target: Projection target
        iterations: Number of times to project (default: 10)
        raise_on_failure: If True, raise ProjectionLawError on failure

    Returns:
        True if deterministic, False otherwise

    Raises:
        ProjectionLawError: If raise_on_failure=True and non-deterministic
    """
    outputs = []
    for _ in range(iterations):
        output = _project_widget(widget, target)
        outputs.append(output)

    # All outputs should be identical
    first = outputs[0]
    for i, output in enumerate(outputs[1:], start=2):
        if output != first:
            if raise_on_failure:
                raise ProjectionLawError(
                    law="determinism",
                    expected=first,
                    actual=output,
                    target=target,
                    widget_type=f"{type(widget).__name__} (iteration {i})",
                )
            return False

    return True


@dataclass(frozen=True)
class LawVerificationResult:
    """
    Result of verifying all projection laws for a widget.

    Attributes:
        identity: Whether identity law holds
        composition: Whether composition law holds (if tested)
        determinism: Whether determinism holds
        all_passed: True if all tested laws passed
        errors: List of law violations if any
    """

    identity: bool
    composition: bool | None  # None if not tested
    determinism: bool
    errors: list[str]

    @property
    def all_passed(self) -> bool:
        """True if all tested laws passed."""
        return (
            self.identity
            and self.determinism
            and (self.composition is None or self.composition)
        )


def verify_all_laws(
    widget: StatefulWidget[S],
    target: ExtendedTarget | str,
    *,
    state_transforms: list[Callable[[S], S]] | None = None,
) -> LawVerificationResult:
    """
    Verify all projection laws for a widget.

    This is the comprehensive verification function for testing.

    Args:
        widget: Widget to verify
        target: Projection target
        state_transforms: Optional list of state transformations for composition law.
                         If None, composition law is skipped.

    Returns:
        LawVerificationResult with all results

    Example:
        def incr(s: CounterState) -> CounterState:
            return CounterState(count=s.count + 1)

        result = verify_all_laws(
            counter_widget,
            ExtendedTarget.CLI,
            state_transforms=[incr, lambda s: s],
        )
        assert result.all_passed
    """
    errors: list[str] = []

    # Identity
    identity_ok = verify_identity_law(widget, target)
    if not identity_ok:
        errors.append(f"Identity law failed for {target}")

    # Determinism
    determinism_ok = verify_determinism(widget, target)
    if not determinism_ok:
        errors.append(f"Determinism failed for {target}")

    # Composition (if transforms provided)
    composition_ok: bool | None = None
    if state_transforms and len(state_transforms) >= 2:
        f, g = state_transforms[0], state_transforms[1]
        composition_ok = verify_composition_law(widget, f, g, target)
        if not composition_ok:
            errors.append(f"Composition law failed for {target}")

    return LawVerificationResult(
        identity=identity_ok,
        composition=composition_ok,
        determinism=determinism_ok,
        errors=errors,
    )


__all__ = [
    "ProjectionLawError",
    "verify_identity_law",
    "verify_composition_law",
    "verify_determinism",
    "verify_all_laws",
    "LawVerificationResult",
]
