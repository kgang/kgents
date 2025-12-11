"""Tests for @expose decorator."""

from __future__ import annotations

from protocols.cli.prism import ExposeMetadata, expose, get_expose_meta, is_exposed


class TestExposeDecorator:
    """Tests for the @expose decorator."""

    def test_expose_attaches_metadata(self) -> None:
        """@expose attaches ExposeMetadata to function."""

        @expose(help="Test command")
        def test_cmd() -> None:
            pass

        assert hasattr(test_cmd, "_expose_meta")
        assert isinstance(test_cmd._expose_meta, ExposeMetadata)

    def test_expose_with_help_only(self) -> None:
        """@expose with only help parameter."""

        @expose(help="Reify domain into Tongue")
        def reify(domain: str):
            pass

        meta = get_expose_meta(reify)
        assert meta is not None
        assert meta.help == "Reify domain into Tongue"
        assert meta.examples == []
        assert meta.aliases == []
        assert meta.hidden is False

    def test_expose_with_examples(self) -> None:
        """@expose with examples parameter."""

        @expose(
            help="Reify domain",
            examples=['kgents grammar reify "Calendar"', "kgents grammar reify Math"],
        )
        def reify(domain: str):
            pass

        meta = get_expose_meta(reify)
        assert meta is not None
        assert len(meta.examples) == 2
        assert 'kgents grammar reify "Calendar"' in meta.examples

    def test_expose_with_aliases(self) -> None:
        """@expose with aliases parameter."""

        @expose(help="List items", aliases=["ls", "l"])
        def list_items():
            pass

        meta = get_expose_meta(list_items)
        assert meta is not None
        assert meta.aliases == ["ls", "l"]

    def test_expose_with_hidden(self) -> None:
        """@expose with hidden=True."""

        @expose(help="Debug command", hidden=True)
        def debug():
            pass

        meta = get_expose_meta(debug)
        assert meta is not None
        assert meta.hidden is True

    def test_expose_preserves_function(self) -> None:
        """@expose preserves the original function."""

        @expose(help="Test")
        def my_func(x: int, y: str) -> str:
            """My docstring."""
            return f"{y}: {x}"

        # Function should still work
        assert my_func(42, "answer") == "answer: 42"
        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_expose_on_async_function(self) -> None:
        """@expose works on async functions."""

        @expose(help="Async command")
        async def async_cmd(value: str) -> dict:
            return {"value": value}

        assert is_exposed(async_cmd)
        meta = get_expose_meta(async_cmd)
        assert meta.help == "Async command"

    def test_expose_on_method(self) -> None:
        """@expose works on class methods."""

        class Agent:
            @expose(help="Agent method")
            def method(self, arg: str) -> str:
                return arg.upper()

        agent = Agent()
        assert is_exposed(agent.method)

        # Method should still work
        assert agent.method("hello") == "HELLO"


class TestIsExposed:
    """Tests for is_exposed function."""

    def test_is_exposed_true(self) -> None:
        """is_exposed returns True for decorated functions."""

        @expose(help="Test")
        def exposed():
            pass

        assert is_exposed(exposed) is True

    def test_is_exposed_false(self) -> None:
        """is_exposed returns False for non-decorated functions."""

        def not_exposed():
            pass

        assert is_exposed(not_exposed) is False

    def test_is_exposed_false_for_non_callable(self) -> None:
        """is_exposed returns False for non-callables."""
        assert is_exposed(42) is False
        assert is_exposed("string") is False
        assert is_exposed(None) is False

    def test_is_exposed_false_for_wrong_attribute(self) -> None:
        """is_exposed returns False if _expose_meta is not ExposeMetadata."""

        def fake_exposed():
            pass

        fake_exposed._expose_meta = "not metadata"

        assert is_exposed(fake_exposed) is False


class TestGetExposeMeta:
    """Tests for get_expose_meta function."""

    def test_get_expose_meta_returns_metadata(self) -> None:
        """get_expose_meta returns ExposeMetadata."""

        @expose(help="Test", examples=["ex1"])
        def test_cmd() -> None:
            pass

        meta = get_expose_meta(test_cmd)
        assert isinstance(meta, ExposeMetadata)
        assert meta.help == "Test"
        assert meta.examples == ["ex1"]

    def test_get_expose_meta_returns_none(self) -> None:
        """get_expose_meta returns None for non-decorated functions."""

        def regular_func():
            pass

        assert get_expose_meta(regular_func) is None

    def test_get_expose_meta_returns_none_for_wrong_type(self) -> None:
        """get_expose_meta returns None if attribute is wrong type."""

        def fake():
            pass

        fake._expose_meta = {"help": "not right"}

        assert get_expose_meta(fake) is None


class TestExposeMetadata:
    """Tests for ExposeMetadata dataclass."""

    def test_defaults(self) -> None:
        """ExposeMetadata has correct defaults."""
        meta = ExposeMetadata(help="Test")

        assert meta.help == "Test"
        assert meta.examples == []
        assert meta.aliases == []
        assert meta.hidden is False

    def test_all_fields(self) -> None:
        """ExposeMetadata accepts all fields."""
        meta = ExposeMetadata(
            help="Full command",
            examples=["ex1", "ex2"],
            aliases=["alias1"],
            hidden=True,
        )

        assert meta.help == "Full command"
        assert meta.examples == ["ex1", "ex2"]
        assert meta.aliases == ["alias1"]
        assert meta.hidden is True

    def test_immutability(self) -> None:
        """ExposeMetadata fields are mutable (dataclass default)."""
        meta = ExposeMetadata(help="Test")
        meta.examples.append("new example")

        assert "new example" in meta.examples
