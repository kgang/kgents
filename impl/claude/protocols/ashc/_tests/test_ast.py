"""Tests for L0 AST types."""

import pytest

from protocols.ashc.ast import (
    DictPattern,
    L0Call,
    L0Compose,
    L0Define,
    L0Emit,
    L0Handle,
    L0Literal,
    L0MatchExpr,
    L0ProgramAST,
    L0Witness,
    ListPattern,
    LiteralPattern,
    WildcardPattern,
)


class TestPatternTypes:
    """Tests for pattern AST types."""

    def test_literal_pattern_frozen(self) -> None:
        """LiteralPattern is immutable."""
        p = LiteralPattern(42)
        assert p.value == 42
        with pytest.raises(AttributeError):
            p.value = 43  # type: ignore

    def test_wildcard_pattern_frozen(self) -> None:
        """WildcardPattern is immutable."""
        p = WildcardPattern("x")
        assert p.name == "x"
        with pytest.raises(AttributeError):
            p.name = "y"  # type: ignore

    def test_dict_pattern_from_dict(self) -> None:
        """DictPattern can be created from dict."""
        p = DictPattern.from_dict({"a": LiteralPattern(1), "b": WildcardPattern("x")})
        assert len(p.keys) == 2
        assert not p.allow_extra

    def test_list_pattern_frozen(self) -> None:
        """ListPattern is immutable."""
        p = ListPattern(elements=(LiteralPattern(1), LiteralPattern(2)))
        assert len(p.elements) == 2


class TestExpressionTypes:
    """Tests for expression AST types."""

    def test_handle_frozen(self) -> None:
        """L0Handle is immutable."""
        h = L0Handle("x")
        assert h.name == "x"
        with pytest.raises(AttributeError):
            h.name = "y"  # type: ignore

    def test_literal_frozen(self) -> None:
        """L0Literal is immutable."""
        lit = L0Literal({"key": "value"})
        assert lit.value == {"key": "value"}

    def test_call_from_dict(self) -> None:
        """L0Call can be created from dict."""
        call = L0Call.from_dict(lambda x: x, {"x": 42})
        assert len(call.args) == 1
        arg_name, arg_expr = call.args[0]
        assert arg_name == "x"
        assert isinstance(arg_expr, L0Literal)

    def test_compose_frozen(self) -> None:
        """L0Compose is immutable."""
        comp = L0Compose(
            first=L0Handle("f"),
            second=L0Handle("g"),
        )
        assert comp.first.name == "f"  # type: ignore
        assert comp.second.name == "g"  # type: ignore

    def test_match_expr_frozen(self) -> None:
        """L0MatchExpr is immutable."""
        expr = L0MatchExpr(
            pattern=LiteralPattern(42),
            value=L0Handle("x"),
        )
        assert isinstance(expr.pattern, LiteralPattern)


class TestStatementTypes:
    """Tests for statement AST types."""

    def test_define_frozen(self) -> None:
        """L0Define is immutable."""
        defn = L0Define(name="x", expr=L0Literal(42))
        assert defn.name == "x"
        assert isinstance(defn.expr, L0Literal)

    def test_emit_frozen(self) -> None:
        """L0Emit is immutable."""
        emit = L0Emit(artifact_type="JSON", content=L0Handle("x"))
        assert emit.artifact_type == "JSON"

    def test_witness_frozen(self) -> None:
        """L0Witness is immutable."""
        wit = L0Witness(
            pass_name="test_pass",
            input_expr=L0Handle("input"),
            output_expr=L0Handle("output"),
        )
        assert wit.pass_name == "test_pass"


class TestProgramAST:
    """Tests for program AST type."""

    def test_program_frozen(self) -> None:
        """L0ProgramAST is immutable."""
        prog = L0ProgramAST(
            name="test",
            statements=(
                L0Define(name="x", expr=L0Literal(42)),
                L0Emit(artifact_type="JSON", content=L0Handle("x")),
            ),
        )
        assert prog.name == "test"
        assert len(prog.statements) == 2

    def test_program_definitions(self) -> None:
        """Program extracts definitions correctly."""
        prog = L0ProgramAST(
            name="test",
            statements=(
                L0Define(name="x", expr=L0Literal(1)),
                L0Emit(artifact_type="JSON", content=L0Handle("x")),
                L0Define(name="y", expr=L0Literal(2)),
            ),
        )
        defs = prog.definitions
        assert len(defs) == 2
        assert defs[0].name == "x"
        assert defs[1].name == "y"

    def test_program_emissions(self) -> None:
        """Program extracts emissions correctly."""
        prog = L0ProgramAST(
            name="test",
            statements=(
                L0Define(name="x", expr=L0Literal(1)),
                L0Emit(artifact_type="JSON", content=L0Handle("x")),
                L0Emit(artifact_type="IR", content=L0Handle("x")),
            ),
        )
        emits = prog.emissions
        assert len(emits) == 2
        assert emits[0].artifact_type == "JSON"
        assert emits[1].artifact_type == "IR"

    def test_program_witnesses(self) -> None:
        """Program extracts witnesses correctly."""
        prog = L0ProgramAST(
            name="test",
            statements=(
                L0Define(name="x", expr=L0Literal(1)),
                L0Witness(
                    pass_name="p1",
                    input_expr=L0Handle("x"),
                    output_expr=L0Handle("x"),
                ),
            ),
        )
        wits = prog.witnesses
        assert len(wits) == 1
        assert wits[0].pass_name == "p1"
