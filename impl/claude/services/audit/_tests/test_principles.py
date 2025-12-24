"""
Tests for principle scoring.

Validates that the 7 constitutional principles can be scored
from spec files with reasonable accuracy.
"""

import tempfile
from pathlib import Path

import pytest

from services.audit.principles import score_principles
from services.audit.types import PrincipleScores


def test_principle_scores_validation():
    """Test that PrincipleScores validates score ranges."""
    # Valid scores
    scores = PrincipleScores(
        tasteful=0.8,
        curated=0.7,
        ethical=0.9,
        joy_inducing=0.6,
        composable=0.75,
        heterarchical=0.5,
        generative=0.85,
    )
    assert 0.0 <= scores.tasteful <= 1.0

    # Invalid score (out of range)
    with pytest.raises(ValueError):
        PrincipleScores(
            tasteful=1.5,  # Invalid
            curated=0.7,
            ethical=0.9,
            joy_inducing=0.6,
            composable=0.75,
            heterarchical=0.5,
            generative=0.85,
        )


def test_principle_scores_gates():
    """Test validation gate logic."""
    # Passing: all >= 0.4, 5+ >= 0.7
    passing = PrincipleScores(
        tasteful=0.8,
        curated=0.75,
        ethical=0.9,
        joy_inducing=0.7,
        composable=0.85,
        heterarchical=0.5,  # Below 0.7 but >= 0.4
        generative=0.6,  # Below 0.7 but >= 0.4
    )
    assert passing.passes_gates()
    assert passing.passing_count() == 5

    # Failing: one below 0.4
    failing = PrincipleScores(
        tasteful=0.3,  # Below 0.4
        curated=0.75,
        ethical=0.9,
        joy_inducing=0.7,
        composable=0.85,
        heterarchical=0.5,
        generative=0.8,
    )
    assert not failing.passes_gates()

    # Failing: all >= 0.4 but only 4 >= 0.7
    failing2 = PrincipleScores(
        tasteful=0.8,
        curated=0.75,
        ethical=0.9,
        joy_inducing=0.7,
        composable=0.6,  # Below 0.7
        heterarchical=0.5,  # Below 0.7
        generative=0.55,  # Below 0.7
    )
    assert not failing2.passes_gates()
    assert failing2.passing_count() == 4


def test_score_tasteful_spec():
    """Test scoring a tasteful spec."""
    spec_content = """
# Example Agent

## Purpose

This agent demonstrates clear, focused design with a single responsibility.

## Why This Exists

Justification for the agent's existence.

## Examples

Example 1: Simple use case
Example 2: Another use case

The design is tasteful and elegant.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(spec_content)
        spec_path = Path(f.name)

    try:
        scores = score_principles(spec_path)

        # Should score well on tasteful (has purpose, why, limited examples)
        assert scores.tasteful >= 0.7

        # Should have reasonable overall scores
        assert 0.0 <= scores.mean() <= 1.0

    finally:
        spec_path.unlink()


def test_score_composable_spec():
    """Test scoring a composable spec."""
    spec_content = """
# Composable Agent

Agent[A, B]: A -> B

## Interface

Type signature: `(Input, Context) → Output`

## Category Laws

Identity: `Id >> Agent ≡ Agent ≡ Agent >> Id`
Associativity: `(A >> B) >> C ≡ A >> (B >> C)`

Always returns single output (not arrays).

## Composition

Can be composed with other agents using `>>` operator.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(spec_content)
        spec_path = Path(f.name)

    try:
        scores = score_principles(spec_path)

        # Should score very well on composable
        assert scores.composable >= 0.8

    finally:
        spec_path.unlink()


def test_score_ethical_spec():
    """Test scoring an ethical spec."""
    spec_content = """
# Ethical Agent

## Privacy

This agent respects user privacy and does not collect data without consent.

## Transparency

All decisions are explained. Limitations are clearly stated.

## Human Agency

The human always has final say. This agent augments, never replaces judgment.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(spec_content)
        spec_path = Path(f.name)

    try:
        scores = score_principles(spec_path)

        # Should score well on ethical
        assert scores.ethical >= 0.7

    finally:
        spec_path.unlink()


def test_score_joy_inducing_spec():
    """Test scoring a joy-inducing spec."""
    spec_content = """
# Delightful Agent 🎯

This agent is designed to bring joy to your workflow!

## Examples

Imagine you're working on a project and you need a little boost.
Let's explore how this agent can help you...

Example: The agent surprises you with creative suggestions.

You'll love the playful interactions! ✨
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(spec_content)
        spec_path = Path(f.name)

    try:
        scores = score_principles(spec_path)

        # Should score well on joy-inducing (emoji, engaging language)
        assert scores.joy_inducing >= 0.7

    finally:
        spec_path.unlink()


def test_score_minimal_spec():
    """Test scoring a minimal spec (should score low)."""
    spec_content = """
# Agent

Does something.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(spec_content)
        spec_path = Path(f.name)

    try:
        scores = score_principles(spec_path)

        # Should score low across all principles (minimal content)
        assert scores.mean() < 0.6

        # Should fail validation gates
        assert not scores.passes_gates()

    finally:
        spec_path.unlink()


def test_score_nonexistent_spec():
    """Test scoring a spec that doesn't exist."""
    spec_path = Path("/nonexistent/spec.md")

    with pytest.raises(FileNotFoundError):
        score_principles(spec_path)
