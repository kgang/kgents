"""
Tests for the Prompt Polynomial.

Verifies state transitions and category laws.
"""

import pytest
from protocols.prompt.polynomial import (
    PROMPT_POLYNOMIAL,
    VALID_INPUTS,
    PromptInput,
    PromptOutput,
    PromptState,
)


class TestPromptState:
    """Test PromptState enum."""

    def test_all_states_defined(self) -> None:
        """All four states should be defined."""
        assert PromptState.STABLE is not None
        assert PromptState.EVOLVING is not None
        assert PromptState.VALIDATING is not None
        assert PromptState.COMPILING is not None

    def test_states_are_unique(self) -> None:
        """Each state should have unique value."""
        values = [s.value for s in PromptState]
        assert len(values) == len(set(values))


class TestPromptInput:
    """Test PromptInput dataclass."""

    def test_input_creation(self) -> None:
        """Should create input with kind and optional payload."""
        inp = PromptInput(kind="propose", payload="Add new skill")
        assert inp.kind == "propose"
        assert inp.payload == "Add new skill"

    def test_input_hashable(self) -> None:
        """Inputs should be hashable for use in sets."""
        inp = PromptInput(kind="propose")
        assert hash(inp) is not None

    def test_inputs_frozen(self) -> None:
        """Inputs should be immutable."""
        inp = PromptInput(kind="propose")
        with pytest.raises(AttributeError):
            inp.kind = "compile"  # type: ignore


class TestPromptOutput:
    """Test PromptOutput dataclass."""

    def test_output_creation(self) -> None:
        """Should create output with defaults."""
        out = PromptOutput()
        assert out.content is None
        assert out.message == ""
        assert out.success is True

    def test_output_with_content(self) -> None:
        """Should store content when provided."""
        out = PromptOutput(content="# CLAUDE.md", message="Compiled")
        assert out.content == "# CLAUDE.md"
        assert out.message == "Compiled"


class TestValidInputs:
    """Test valid input mapping."""

    def test_all_states_have_valid_inputs(self) -> None:
        """Every state should have defined valid inputs."""
        for state in PromptState:
            assert state in VALID_INPUTS
            assert len(VALID_INPUTS[state]) > 0

    def test_stable_accepts_propose_and_compile(self) -> None:
        """STABLE should accept propose, compile, and manifest."""
        assert "propose" in VALID_INPUTS[PromptState.STABLE]
        assert "compile" in VALID_INPUTS[PromptState.STABLE]
        assert "manifest" in VALID_INPUTS[PromptState.STABLE]

    def test_evolving_accepts_approval_actions(self) -> None:
        """EVOLVING should accept approve, reject, validate."""
        assert "approve" in VALID_INPUTS[PromptState.EVOLVING]
        assert "reject" in VALID_INPUTS[PromptState.EVOLVING]
        assert "validate" in VALID_INPUTS[PromptState.EVOLVING]


class TestPromptPolynomial:
    """Test the PROMPT_POLYNOMIAL agent."""

    def test_polynomial_name(self) -> None:
        """Should have correct name."""
        assert PROMPT_POLYNOMIAL.name == "PromptPolynomial"

    def test_polynomial_has_all_states(self) -> None:
        """All states should be positions."""
        for state in PromptState:
            assert state in PROMPT_POLYNOMIAL.positions

    def test_stable_to_evolving(self) -> None:
        """STABLE + propose -> EVOLVING."""
        inp = PromptInput(kind="propose", payload="Add skill")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.STABLE, inp)
        assert new_state == PromptState.EVOLVING
        assert "proposed" in output.message.lower()

    def test_stable_to_compiling(self) -> None:
        """STABLE + compile -> COMPILING."""
        inp = PromptInput(kind="compile")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.STABLE, inp)
        assert new_state == PromptState.COMPILING
        assert output.success

    def test_evolving_approve_to_validating(self) -> None:
        """EVOLVING + approve -> VALIDATING."""
        inp = PromptInput(kind="approve")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.EVOLVING, inp)
        assert new_state == PromptState.VALIDATING

    def test_evolving_reject_to_stable(self) -> None:
        """EVOLVING + reject -> STABLE."""
        inp = PromptInput(kind="reject")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.EVOLVING, inp)
        assert new_state == PromptState.STABLE
        assert not output.success

    def test_validating_pass_to_compiling(self) -> None:
        """VALIDATING + validation_pass -> COMPILING."""
        inp = PromptInput(kind="validation_pass")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.VALIDATING, inp)
        assert new_state == PromptState.COMPILING

    def test_validating_fail_to_evolving(self) -> None:
        """VALIDATING + validation_fail -> EVOLVING."""
        inp = PromptInput(kind="validation_fail", payload="Law violation")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.VALIDATING, inp)
        assert new_state == PromptState.EVOLVING
        assert not output.success

    def test_compiling_complete_to_stable(self) -> None:
        """COMPILING + complete -> STABLE."""
        inp = PromptInput(kind="complete", payload="# CLAUDE.md content")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.COMPILING, inp)
        assert new_state == PromptState.STABLE
        assert output.content == "# CLAUDE.md content"

    def test_compiling_abort_to_stable(self) -> None:
        """COMPILING + abort -> STABLE."""
        inp = PromptInput(kind="abort")
        new_state, output = PROMPT_POLYNOMIAL.invoke(PromptState.COMPILING, inp)
        assert new_state == PromptState.STABLE
        assert not output.success


class TestStateTransitionCycle:
    """Test full lifecycle through the polynomial."""

    def test_full_evolution_cycle(self) -> None:
        """Test propose -> approve -> validate -> compile -> complete."""
        state = PromptState.STABLE

        # Propose evolution
        state, _ = PROMPT_POLYNOMIAL.invoke(
            state, PromptInput(kind="propose", payload="Add skill")
        )
        assert state == PromptState.EVOLVING

        # Approve
        state, _ = PROMPT_POLYNOMIAL.invoke(state, PromptInput(kind="approve"))
        assert state == PromptState.VALIDATING

        # Validation passes
        state, _ = PROMPT_POLYNOMIAL.invoke(state, PromptInput(kind="validation_pass"))
        assert state == PromptState.COMPILING

        # Complete compilation
        state, output = PROMPT_POLYNOMIAL.invoke(
            state, PromptInput(kind="complete", payload="New prompt")
        )
        assert state == PromptState.STABLE
        assert output.content == "New prompt"

    def test_rejected_evolution_cycle(self) -> None:
        """Test propose -> reject returns to stable."""
        state = PromptState.STABLE

        # Propose
        state, _ = PROMPT_POLYNOMIAL.invoke(state, PromptInput(kind="propose"))
        assert state == PromptState.EVOLVING

        # Reject
        state, output = PROMPT_POLYNOMIAL.invoke(state, PromptInput(kind="reject"))
        assert state == PromptState.STABLE
        assert not output.success
