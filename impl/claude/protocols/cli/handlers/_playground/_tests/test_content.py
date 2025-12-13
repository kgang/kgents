"""Tests for tutorial content files."""

from __future__ import annotations

import pytest


class TestHelloWorldTutorial:
    """Tests for the Hello World tutorial content."""

    def test_tutorial_structure(self) -> None:
        """Hello World tutorial has correct structure."""
        from ..content.hello_world import HELLO_WORLD_TUTORIAL

        assert HELLO_WORLD_TUTORIAL.name == "Hello World"
        assert len(HELLO_WORLD_TUTORIAL.steps) >= 2
        assert HELLO_WORLD_TUTORIAL.description

    def test_tutorial_steps_have_code(self) -> None:
        """Each step has code content."""
        from ..content.hello_world import HELLO_WORLD_TUTORIAL

        for step in HELLO_WORLD_TUTORIAL.steps:
            assert step.code
            assert step.title
            assert step.explanation

    @pytest.mark.asyncio
    async def test_greet_executor(self) -> None:
        """The greet executor produces expected output."""
        from ..content.hello_world import _run_greet

        result = await _run_greet()
        assert "Hello" in result
        assert "World" in result


class TestCompositionTutorial:
    """Tests for the Composition tutorial content."""

    def test_tutorial_structure(self) -> None:
        """Composition tutorial has correct structure."""
        from ..content.composition import COMPOSITION_TUTORIAL

        assert COMPOSITION_TUTORIAL.name == "Composition"
        assert len(COMPOSITION_TUTORIAL.steps) >= 2

    def test_mentions_composition_operator(self) -> None:
        """Tutorial mentions the >> operator."""
        from ..content.composition import COMPOSITION_TUTORIAL

        all_code = " ".join(step.code for step in COMPOSITION_TUTORIAL.steps)
        assert ">>" in all_code

    @pytest.mark.asyncio
    async def test_pipeline_executor(self) -> None:
        """The pipeline executor demonstrates composition."""
        from ..content.composition import _run_pipeline

        result = await _run_pipeline()
        assert "42" in result or "Result" in result

    @pytest.mark.asyncio
    async def test_associativity_executor(self) -> None:
        """The associativity executor shows equal results."""
        from ..content.composition import _run_associativity

        result = await _run_associativity()
        assert "Equal" in result or "True" in result


class TestFunctorTutorial:
    """Tests for the Functor tutorial content."""

    def test_tutorial_structure(self) -> None:
        """Functor tutorial has correct structure."""
        from ..content.functor import FUNCTOR_TUTORIAL

        assert FUNCTOR_TUTORIAL.name == "Lift to Maybe"
        assert len(FUNCTOR_TUTORIAL.steps) >= 2

    def test_mentions_maybe(self) -> None:
        """Tutorial mentions Maybe type."""
        from ..content.functor import FUNCTOR_TUTORIAL

        all_code = " ".join(step.code for step in FUNCTOR_TUTORIAL.steps)
        assert "Maybe" in all_code
        assert "Just" in all_code
        assert "Nothing" in all_code


class TestSoulTutorial:
    """Tests for the Soul tutorial content."""

    def test_tutorial_structure(self) -> None:
        """Soul tutorial has correct structure."""
        from ..content.soul import SOUL_TUTORIAL

        assert SOUL_TUTORIAL.name == "K-gent Dialogue"
        assert len(SOUL_TUTORIAL.steps) >= 2

    def test_mentions_dialogue_modes(self) -> None:
        """Tutorial mentions the four dialogue modes."""
        from ..content.soul import SOUL_TUTORIAL

        all_text = " ".join(
            f"{step.code} {step.explanation}" for step in SOUL_TUTORIAL.steps
        )
        assert "REFLECT" in all_text
        assert "ADVISE" in all_text
        assert "CHALLENGE" in all_text
        assert "EXPLORE" in all_text


class TestTutorialRegistry:
    """Tests for the tutorial registry."""

    def test_all_tutorials_loadable(self) -> None:
        """All expected tutorials can be loaded."""
        from .. import TUTORIALS, _load_tutorials

        _load_tutorials()

        expected = ["hello", "compose", "functor", "soul"]
        for name in expected:
            assert name in TUTORIALS, f"Tutorial '{name}' not found"

    def test_tutorials_are_tutorial_instances(self) -> None:
        """All registered tutorials are Tutorial instances."""
        from .. import TUTORIALS, _load_tutorials
        from ..tutorial import Tutorial

        _load_tutorials()

        for name, tutorial in TUTORIALS.items():
            assert isinstance(tutorial, Tutorial), f"'{name}' is not a Tutorial"
