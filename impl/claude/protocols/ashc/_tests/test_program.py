"""Tests for L0 program builder and runtime."""

import pytest

from protocols.ashc import L0Error, L0Program, L0Result


class TestL0ProgramBuilder:
    """Tests for L0Program builder DSL."""

    def test_create_program(self) -> None:
        """Create empty program."""
        prog = L0Program("test")
        assert prog.name == "test"
        assert len(prog) == 0

    def test_define_literal(self) -> None:
        """Define with literal value."""
        prog = L0Program("test")
        x = prog.define("x", prog.literal(42))
        assert x.name == "x"
        assert len(prog) == 1

    def test_define_with_call(self) -> None:
        """Define with function call."""
        prog = L0Program("test")

        def add_one(n: int) -> int:
            return n + 1

        x = prog.define("x", prog.call(add_one, n=5))
        assert x.name == "x"

    def test_emit_artifact(self) -> None:
        """Add emit statement."""
        prog = L0Program("test")
        x = prog.define("x", prog.literal(42))
        prog.emit("JSON", x)
        assert len(prog) == 2

    def test_witness_statement(self) -> None:
        """Add witness statement."""
        prog = L0Program("test")
        x = prog.define("x", prog.literal(42))
        y = prog.define("y", prog.literal(43))
        prog.witness("test_pass", x, y)
        assert len(prog) == 3

    def test_compose_expressions(self) -> None:
        """Compose expressions."""
        prog = L0Program("test")
        x = prog.define("x", prog.literal(42))
        f = prog.define("f", prog.call(lambda n: n + 1, n=x))
        comp = prog.compose(x, f)
        assert comp is not None

    def test_build_ast(self) -> None:
        """Build program AST."""
        prog = L0Program("test")
        prog.define("x", prog.literal(42))
        prog.emit("JSON", prog.handle("x"))

        ast = prog.build()
        assert ast.name == "test"
        assert len(ast.statements) == 2


class TestL0ProgramExecution:
    """Tests for L0Program execution."""

    @pytest.mark.asyncio
    async def test_run_minimal_program(self) -> None:
        """Run minimal program with literal."""
        prog = L0Program("minimal")
        x = prog.define("x", prog.literal(42))
        prog.emit("JSON", x)

        result = await prog.run()
        assert isinstance(result, L0Result)
        assert result.program_name == "minimal"
        assert result.bindings["x"] == 42
        assert len(result.artifacts) == 1
        assert result.artifacts[0].content == 42

    @pytest.mark.asyncio
    async def test_run_with_function_call(self) -> None:
        """Run program with function call."""
        prog = L0Program("with_call")

        def double(n: int) -> int:
            return n * 2

        x = prog.define("x", prog.call(double, n=21))
        prog.emit("result", x)

        result = await prog.run()
        assert result.bindings["x"] == 42
        assert result.artifacts[0].content == 42

    @pytest.mark.asyncio
    async def test_run_with_async_call(self) -> None:
        """Run program with async function call."""
        prog = L0Program("async_call")

        async def async_double(n: int) -> int:
            return n * 2

        x = prog.define("x", prog.call(async_double, n=21))
        prog.emit("result", x)

        result = await prog.run()
        assert result.bindings["x"] == 42

    @pytest.mark.asyncio
    async def test_run_with_witness(self) -> None:
        """Run program emits witness."""
        prog = L0Program("with_witness")
        inp = prog.define("input", prog.literal({"data": 1}))
        out = prog.define("output", prog.literal({"result": 2}))
        prog.witness("transform", inp, out)

        result = await prog.run()
        assert len(result.witnesses) == 1
        assert result.witnesses[0].pass_name == "transform"

    @pytest.mark.asyncio
    async def test_run_chain_definitions(self) -> None:
        """Run program with chained definitions."""
        prog = L0Program("chain")

        x = prog.define("x", prog.literal(10))
        y = prog.define("y", prog.call(lambda n: n + 5, n=x))
        z = prog.define("z", prog.call(lambda n: n * 2, n=y))
        prog.emit("result", z)

        result = await prog.run()
        assert result.bindings["x"] == 10
        assert result.bindings["y"] == 15
        assert result.bindings["z"] == 30

    @pytest.mark.asyncio
    async def test_run_multiple_artifacts(self) -> None:
        """Run program with multiple artifacts."""
        prog = L0Program("multi_emit")
        x = prog.define("x", prog.literal(42))
        prog.emit("JSON", x)
        prog.emit("IR", x)
        prog.emit("CODE", x)

        result = await prog.run()
        assert len(result.artifacts) == 3
        types = [a.artifact_type for a in result.artifacts]
        assert "JSON" in types
        assert "IR" in types
        assert "CODE" in types


class TestL0ProgramFailFast:
    """Tests for fail-fast behavior."""

    @pytest.mark.asyncio
    async def test_undefined_handle_fails(self) -> None:
        """Referencing undefined handle fails immediately."""
        prog = L0Program("undefined")
        prog.emit("JSON", prog.handle("nonexistent"))

        with pytest.raises(L0Error) as exc_info:
            await prog.run()
        assert "nonexistent" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_function_exception_fails(self) -> None:
        """Function exception fails immediately."""
        prog = L0Program("exception")

        def bad_function(n: int) -> int:
            raise ValueError("intentional error")

        prog.define("x", prog.call(bad_function, n=1))

        with pytest.raises(L0Error) as exc_info:
            await prog.run()
        assert "define x" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_no_partial_results(self) -> None:
        """No partial results on failure."""
        prog = L0Program("partial")

        # First definition succeeds
        prog.define("x", prog.literal(42))
        prog.emit("first", prog.handle("x"))

        # Second definition fails
        def bad() -> None:
            raise RuntimeError("boom")

        prog.define("y", prog.call(bad))

        # Should fail completely, no partial result
        with pytest.raises(L0Error):
            await prog.run()


class TestL0ProgramPatterns:
    """Tests for pattern matching in programs."""

    @pytest.mark.asyncio
    async def test_pattern_match_success(self) -> None:
        """Successful pattern match."""
        prog = L0Program("pattern_match")

        data = prog.define("data", prog.literal({"type": "spec", "content": "hello"}))
        pattern = prog.pattern_dict(
            {
                "type": prog.pattern_literal("spec"),
                "content": prog.pattern_wildcard("c"),
            }
        )
        bindings = prog.define("bindings", prog.match_expr(pattern, data))
        prog.emit("result", bindings)

        result = await prog.run()
        assert result.bindings["bindings"] == {"c": "hello"}

    @pytest.mark.asyncio
    async def test_pattern_match_failure(self) -> None:
        """Failed pattern match returns None."""
        prog = L0Program("pattern_fail")

        data = prog.define("data", prog.literal({"type": "other"}))
        pattern = prog.pattern_dict(
            {
                "type": prog.pattern_literal("spec"),
            }
        )
        bindings = prog.define("bindings", prog.match_expr(pattern, data))
        prog.emit("result", bindings)

        result = await prog.run()
        assert result.bindings["bindings"] is None


class TestL0ProgramRepr:
    """Tests for program representation."""

    def test_repr(self) -> None:
        """Program has readable repr."""
        prog = L0Program("test_repr")
        prog.define("x", prog.literal(1))
        prog.define("y", prog.literal(2))

        r = repr(prog)
        assert "test_repr" in r
        assert "2" in r  # statement count
