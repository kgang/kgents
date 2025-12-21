"""
Unit tests for VoidHarness (no LLM calls).

These tests verify:
- Prompt building
- Code extraction from various output formats
- Token budget tracking
- Configuration handling

For integration tests with real LLM calls, see:
- test_harness_integration.py (requires --run-llm-tests or RUN_LLM_TESTS=1)
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..harness import (
    GenerationResult,
    SubprocessResult,
    TokenBudget,
    VoidHarness,
    VoidHarnessConfig,
    generate_from_spec,
)

# =============================================================================
# TokenBudget Tests
# =============================================================================


class TestTokenBudget:
    """Test TokenBudget tracking and limits."""

    def test_initial_state(self) -> None:
        """Budget starts with zero usage."""
        budget = TokenBudget(max_tokens=1000)
        assert budget.used_tokens == 0
        assert budget.remaining == 1000
        assert not budget.exhausted

    def test_consume_tokens(self) -> None:
        """Consuming tokens reduces remaining budget."""
        budget = TokenBudget(max_tokens=1000)
        budget.consume(300)
        assert budget.used_tokens == 300
        assert budget.remaining == 700
        assert not budget.exhausted

    def test_consume_multiple_times(self) -> None:
        """Multiple consumptions accumulate."""
        budget = TokenBudget(max_tokens=1000)
        budget.consume(200)
        budget.consume(300)
        budget.consume(100)
        assert budget.used_tokens == 600
        assert budget.remaining == 400

    def test_exhausted_at_limit(self) -> None:
        """Budget is exhausted at max_tokens."""
        budget = TokenBudget(max_tokens=100)
        budget.consume(100)
        assert budget.exhausted
        assert budget.remaining == 0

    def test_consume_raises_on_overflow(self) -> None:
        """Consuming beyond budget raises RuntimeError."""
        budget = TokenBudget(max_tokens=100)
        budget.consume(50)

        with pytest.raises(RuntimeError, match="Token budget exhausted"):
            budget.consume(100)  # Would exceed 100

    def test_warning_threshold(self) -> None:
        """Warning threshold triggers at warn_at_tokens."""
        budget = TokenBudget(max_tokens=1000, warn_at_tokens=500)

        budget.consume(300)
        assert not budget.warning_threshold_reached

        budget.consume(200)
        assert budget.warning_threshold_reached

    def test_default_values(self) -> None:
        """Default budget has sensible defaults."""
        budget = TokenBudget()
        assert budget.max_tokens == 100_000
        assert budget.warn_at_tokens == 50_000


# =============================================================================
# VoidHarnessConfig Tests
# =============================================================================


class TestVoidHarnessConfig:
    """Test VoidHarnessConfig defaults and customization."""

    def test_default_values(self) -> None:
        """Config has sensible defaults."""
        config = VoidHarnessConfig()
        assert config.model == "claude-sonnet-4-20250514"
        assert config.timeout_seconds == 120.0
        assert config.max_concurrent == 3
        assert config.void_prefix == "/tmp/ashc-void"

    def test_custom_values(self) -> None:
        """Config accepts custom values."""
        config = VoidHarnessConfig(
            model="claude-opus-4",
            timeout_seconds=60.0,
            max_concurrent=5,
        )
        assert config.model == "claude-opus-4"
        assert config.timeout_seconds == 60.0
        assert config.max_concurrent == 5


# =============================================================================
# Code Extraction Tests
# =============================================================================


class TestCodeExtraction:
    """Test _extract_code method with various output formats."""

    def get_harness(self) -> VoidHarness:
        """Create harness for extraction testing."""
        return VoidHarness()

    def test_extract_python_fenced(self) -> None:
        """Extract code from ```python block."""
        harness = self.get_harness()
        output = """Here's the implementation:

```python
def add(a: int, b: int) -> int:
    return a + b
```

This function adds two integers."""

        code = harness._extract_code(output)
        assert "def add(a: int, b: int) -> int:" in code
        assert "return a + b" in code
        assert "Here's the implementation" not in code

    def test_extract_unfenced_code(self) -> None:
        """Extract code from unfenced block."""
        harness = self.get_harness()
        output = """```
def multiply(x, y):
    return x * y
```"""

        code = harness._extract_code(output)
        assert "def multiply" in code
        assert "return x * y" in code

    def test_extract_code_like_content(self) -> None:
        """Extract code by detecting def/class/import."""
        harness = self.get_harness()
        output = """Here's what you need:

def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)"""

        code = harness._extract_code(output)
        assert "def factorial" in code
        assert "return n * factorial" in code

    def test_extract_class_definition(self) -> None:
        """Extract class definitions."""
        harness = self.get_harness()
        output = """I'll create a simple class:

class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1"""

        code = harness._extract_code(output)
        assert "class Counter:" in code
        assert "def increment" in code

    def test_extract_import_statements(self) -> None:
        """Extract code starting with imports."""
        harness = self.get_harness()
        output = """from typing import List

def process(items: List[int]) -> int:
    return sum(items)"""

        code = harness._extract_code(output)
        assert "from typing import List" in code
        assert "def process" in code

    def test_extract_async_def(self) -> None:
        """Extract async function definitions."""
        harness = self.get_harness()
        output = """async def fetch_data(url: str) -> dict:
    return {"url": url}"""

        code = harness._extract_code(output)
        assert "async def fetch_data" in code

    def test_extract_decorator(self) -> None:
        """Extract decorated functions."""
        harness = self.get_harness()
        output = """@dataclass
class Point:
    x: int
    y: int"""

        code = harness._extract_code(output)
        assert "@dataclass" in code
        assert "class Point:" in code

    def test_extract_empty_on_require_fence(self) -> None:
        """Return empty when require_code_fence=True and no code patterns."""
        config = VoidHarnessConfig(require_code_fence=True)
        harness = VoidHarness(config)

        # Output with no fences and no code patterns
        output = """Here is some explanation text.
No actual code here, just prose.
Maybe a mention of variables like x and y."""

        code = harness._extract_code(output)
        # No fence, require_code_fence=True, no code patterns, should return empty
        assert code == ""

    def test_extract_fallback_raw(self) -> None:
        """Return raw output when no code patterns found."""
        harness = self.get_harness()
        output = "Just some text without code"

        # With require_code_fence=False (default), returns raw
        code = harness._extract_code(output)
        assert code == "Just some text without code"


# =============================================================================
# Prompt Building Tests
# =============================================================================


class TestPromptBuilding:
    """Test _build_prompt method."""

    def test_prompt_includes_spec(self) -> None:
        """Prompt includes the specification."""
        harness = VoidHarness()
        spec = "def add(a, b): return a + b"

        prompt = harness._build_prompt(spec)

        assert spec in prompt
        assert "SPECIFICATION:" in prompt

    def test_prompt_includes_rules(self) -> None:
        """Prompt includes generation rules."""
        harness = VoidHarness()
        prompt = harness._build_prompt("any spec")

        assert "RULES:" in prompt
        assert "type hints" in prompt.lower()
        assert "docstrings" in prompt.lower()

    def test_prompt_ends_with_code_fence(self) -> None:
        """Prompt ends with code fence to guide output."""
        harness = VoidHarness()
        prompt = harness._build_prompt("any spec")

        assert prompt.strip().endswith("```python")


# =============================================================================
# GenerationResult Tests
# =============================================================================


class TestGenerationResult:
    """Test GenerationResult properties."""

    def test_has_code_true(self) -> None:
        """has_code is True when code is non-empty."""
        result = GenerationResult(
            code="def foo(): pass",
            prompt_used="test",
            duration_ms=100,
            token_estimate=50,
            raw_output="output",
            success=True,
        )
        assert result.has_code

    def test_has_code_false_empty(self) -> None:
        """has_code is False when code is empty."""
        result = GenerationResult(
            code="",
            prompt_used="test",
            duration_ms=100,
            token_estimate=50,
            raw_output="output",
            success=False,
        )
        assert not result.has_code

    def test_has_code_false_whitespace(self) -> None:
        """has_code is False when code is only whitespace."""
        result = GenerationResult(
            code="   \n\t  ",
            prompt_used="test",
            duration_ms=100,
            token_estimate=50,
            raw_output="output",
            success=False,
        )
        assert not result.has_code


# =============================================================================
# VoidHarness Unit Tests (Mocked)
# =============================================================================


class TestVoidHarnessMocked:
    """Test VoidHarness with mocked subprocess."""

    @pytest.mark.asyncio
    async def test_generate_success(self) -> None:
        """Successful generation returns code."""
        harness = VoidHarness()

        mock_result = SubprocessResult(
            stdout="```python\ndef add(a, b): return a + b\n```",
            stderr="",
            returncode=0,
            duration_ms=100,
        )

        with patch.object(harness, "_run_claude_cli", return_value=mock_result):
            result = await harness.generate_detailed("def add(a, b): ...")

        assert result.success
        assert "def add" in result.code
        assert result.error is None

    @pytest.mark.asyncio
    async def test_generate_failure_returncode(self) -> None:
        """Non-zero returncode marks as failure."""
        harness = VoidHarness()

        mock_result = SubprocessResult(
            stdout="",
            stderr="Error: API rate limit exceeded",
            returncode=1,
            duration_ms=100,
        )

        with patch.object(harness, "_run_claude_cli", return_value=mock_result):
            result = await harness.generate_detailed("any spec")

        assert not result.success
        assert "returncode" in result.error or "CLI returned" in result.error

    @pytest.mark.asyncio
    async def test_generate_failure_no_code(self) -> None:
        """Empty code extraction marks as failure."""
        harness = VoidHarness(VoidHarnessConfig(require_code_fence=True))

        mock_result = SubprocessResult(
            stdout="I'm sorry, I cannot help with that.",
            stderr="",
            returncode=0,
            duration_ms=100,
        )

        with patch.object(harness, "_run_claude_cli", return_value=mock_result):
            result = await harness.generate_detailed("any spec")

        assert not result.success
        assert "No code" in result.error or result.code == ""

    @pytest.mark.asyncio
    async def test_generate_increments_count(self) -> None:
        """Generation increments generation_count."""
        harness = VoidHarness()

        mock_result = SubprocessResult(
            stdout="```python\npass\n```",
            stderr="",
            returncode=0,
            duration_ms=100,
        )

        assert harness.generation_count == 0

        with patch.object(harness, "_run_claude_cli", return_value=mock_result):
            await harness.generate_detailed("spec 1")
            await harness.generate_detailed("spec 2")

        assert harness.generation_count == 2

    @pytest.mark.asyncio
    async def test_generate_tracks_tokens(self) -> None:
        """Generation tracks token usage."""
        harness = VoidHarness()

        mock_result = SubprocessResult(
            stdout="```python\n" + "x" * 400 + "\n```",  # ~100 tokens
            stderr="",
            returncode=0,
            duration_ms=100,
        )

        assert harness.tokens_used == 0

        with patch.object(harness, "_run_claude_cli", return_value=mock_result):
            await harness.generate_detailed("a" * 400)  # ~100 tokens in prompt

        assert harness.tokens_used > 0

    @pytest.mark.asyncio
    async def test_generate_respects_budget(self) -> None:
        """Generation fails when budget exhausted."""
        budget = TokenBudget(max_tokens=100)
        budget.consume(100)  # Exhaust budget

        harness = VoidHarness(budget=budget)

        result = await harness.generate_detailed("any spec")

        assert not result.success
        assert "budget exhausted" in result.error.lower()

    @pytest.mark.asyncio
    async def test_generate_raises_on_budget_exceed(self) -> None:
        """generate() raises when budget exceeded."""
        budget = TokenBudget(max_tokens=100)
        budget.consume(100)

        harness = VoidHarness(budget=budget)

        with pytest.raises(RuntimeError, match="budget"):
            await harness.generate("any spec")

    @pytest.mark.asyncio
    async def test_generate_n_concurrent(self) -> None:
        """generate_n runs concurrently with semaphore."""
        harness = VoidHarness(VoidHarnessConfig(max_concurrent=2))

        call_count = 0

        async def mock_execute(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return GenerationResult(
                code=f"result {call_count}",
                prompt_used="",
                duration_ms=10,
                token_estimate=10,
                raw_output="",
                success=True,
            )

        with patch.object(harness, "_execute_in_void", side_effect=mock_execute):
            results = await harness.generate_n("spec", n=5)

        assert len(results) == 5
        # All should be GenerationResults (not exceptions)
        assert all(isinstance(r, GenerationResult) for r in results)


# =============================================================================
# is_available Tests
# =============================================================================


class TestIsAvailable:
    """Test is_available class method."""

    def test_is_available_with_claude(self) -> None:
        """is_available returns True when claude is in PATH."""
        with patch("shutil.which", return_value="/usr/local/bin/claude"):
            assert VoidHarness.is_available()

    def test_is_available_without_claude(self) -> None:
        """is_available returns False when claude is not in PATH."""
        with patch("shutil.which", return_value=None):
            assert not VoidHarness.is_available()


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @pytest.mark.asyncio
    async def test_generate_from_spec(self) -> None:
        """generate_from_spec creates harness and generates."""
        # Mock at the instance level by patching _execute_in_void
        mock_result = GenerationResult(
            code="def foo(): pass",
            prompt_used="test",
            duration_ms=100,
            token_estimate=50,
            raw_output="```python\ndef foo(): pass\n```",
            success=True,
        )

        with patch.object(VoidHarness, "_execute_in_void", new_callable=AsyncMock) as mock:
            mock.return_value = mock_result

            result = await generate_from_spec("any spec")

            assert result == "def foo(): pass"
            mock.assert_called_once()
