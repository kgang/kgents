"""
Tests for LLM-powered code generation (Phase 3 LLM integration).

These tests verify:
1. CodeGeneratorAgent prompt construction
2. Response parsing (markdown extraction)
3. Integration with generate_prototype_async
4. Iteration with failure feedback
5. Mock-based testing (no real API calls by default)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from agents.f.contract import Contract, Invariant
from agents.f.intent import Example, Intent
from agents.f.llm_generation import (
    CodeGeneratorAgent,
    GenerationRequest,
    generate_code_with_llm,
)
from agents.f.prototype import PrototypeConfig, generate_prototype_async
from runtime.base import AgentContext, AgentResult, LLMAgent, Runtime

# ============================================================================
# Mock Runtime for Testing
# ============================================================================


@dataclass
class MockRuntime(Runtime):
    """
    Mock runtime that returns pre-defined responses.

    Useful for testing without making real API calls.
    """

    response: str = ""
    call_count: int = 0

    async def execute(
        self, agent: LLMAgent[Any, Any], input_val: Any
    ) -> AgentResult[Any]:
        """Mock execute that returns pre-configured response."""
        self.call_count += 1
        output = agent.parse_response(self.response)
        return AgentResult(
            output=output,
            raw_response=self.response,
            model="mock-model",
            usage={"input_tokens": 100, "output_tokens": 200, "total_tokens": 300},
        )

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """Low-level completion call (not used in these tests)."""
        return (self.response, {"model": "mock-model"})


# ============================================================================
# Test: Prompt Construction
# ============================================================================


def test_code_generator_builds_prompt_with_intent() -> None:
    """Verify prompt includes intent details."""
    intent = Intent(
        purpose="Create a doubler agent",
        behavior=["Multiply input by 2"],
        constraints=["Must be deterministic"],
    )
    contract = Contract(
        agent_name="DoublerAgent",
        input_type="int",
        output_type="int",
        invariants=[
            Invariant(
                description="Deterministic",
                property="f(x) == f(x)",
                category="behavioral",
            )
        ],
    )

    generator = CodeGeneratorAgent()
    request = GenerationRequest(intent=intent, contract=contract)
    context = generator.build_prompt(request)

    # Verify system prompt exists
    assert context.system_prompt
    assert "Python code generation" in context.system_prompt

    # Verify user message contains intent
    assert len(context.messages) == 1
    user_message = context.messages[0]["content"]
    assert "Create a doubler agent" in user_message
    assert "Multiply input by 2" in user_message
    assert "Must be deterministic" in user_message

    # Verify contract details
    assert "DoublerAgent" in user_message
    assert "int" in user_message
    assert "Deterministic" in user_message


def test_code_generator_includes_examples_in_prompt() -> None:
    """Verify examples appear in prompt."""
    intent = Intent(
        purpose="Echo agent",
        behavior=["Return input unchanged"],
        examples=[
            Example(input="hello", expected_output="hello"),
            Example(input="world", expected_output="world"),
        ],
    )
    contract = Contract(
        agent_name="EchoAgent",
        input_type="str",
        output_type="str",
    )

    generator = CodeGeneratorAgent()
    request = GenerationRequest(intent=intent, contract=contract)
    context = generator.build_prompt(request)

    user_message = context.messages[0]["content"]
    assert "Example 1:" in user_message
    assert "hello" in user_message
    assert "Example 2:" in user_message
    assert "world" in user_message


def test_code_generator_includes_previous_failures() -> None:
    """Verify iteration feedback appears in prompt."""
    intent = Intent(purpose="Test agent", behavior=["Test"])
    contract = Contract(agent_name="TestAgent", input_type="str", output_type="str")

    failures = [
        "Attempt 1:",
        "[parse] Syntax error at line 5",
        "",
        "Attempt 2:",
        "[lint] Line 10 exceeds 120 characters",
    ]

    generator = CodeGeneratorAgent()
    request = GenerationRequest(
        intent=intent, contract=contract, previous_failures=failures
    )
    context = generator.build_prompt(request)

    user_message = context.messages[0]["content"]
    assert "Previous Attempt Failures" in user_message
    assert "Syntax error at line 5" in user_message
    assert "Line 10 exceeds 120 characters" in user_message


# ============================================================================
# Test: Response Parsing
# ============================================================================


def test_parse_response_extracts_code_from_markdown() -> None:
    """Parse code from markdown blocks."""
    generator = CodeGeneratorAgent()

    # With python tag
    response = """```python
class TestAgent:
    def invoke(self, x: int) -> int:
        return x * 2
```"""

    code = generator.parse_response(response)
    assert "class TestAgent:" in code
    assert "def invoke" in code
    assert "```" not in code  # Markdown removed


def test_parse_response_handles_generic_code_blocks() -> None:
    """Parse code from ``` blocks without language tag."""
    generator = CodeGeneratorAgent()

    response = """```
class TestAgent:
    def invoke(self, x: int) -> int:
        return x * 2
```"""

    code = generator.parse_response(response)
    assert "class TestAgent:" in code
    assert "```" not in code


def test_parse_response_removes_explanation_text() -> None:
    """Remove explanatory text before code."""
    generator = CodeGeneratorAgent()

    response = """Here's the implementation:

class TestAgent:
    def invoke(self, x: int) -> int:
        return x * 2"""

    code = generator.parse_response(response)
    assert "class TestAgent:" in code
    assert "Here's the implementation" not in code


def test_parse_response_preserves_docstrings() -> None:
    """Keep module and class docstrings."""
    generator = CodeGeneratorAgent()

    response = '''"""Test module."""

class TestAgent:
    """Test agent."""

    def invoke(self, x: int) -> int:
        return x * 2'''

    code = generator.parse_response(response)
    assert '"""Test module."""' in code
    assert '"""Test agent."""' in code


# ============================================================================
# Test: Integration with generate_prototype_async
# ============================================================================


@pytest.mark.asyncio
async def test_generate_prototype_async_with_llm() -> None:
    """Integration test: generate_prototype_async with mock LLM."""
    intent = Intent(
        purpose="Double numbers",
        behavior=["Multiply by 2"],
    )
    contract = Contract(
        agent_name="DoublerAgent",
        input_type="int",
        output_type="int",
    )

    # Mock LLM response (valid Python code)
    mock_response = """class DoublerAgent:
    def invoke(self, x: int) -> int:
        return x * 2"""

    runtime = MockRuntime(response=mock_response)
    config = PrototypeConfig(use_llm=True, runtime=runtime)

    source = await generate_prototype_async(intent, contract, config)

    # Verify LLM was called
    assert runtime.call_count == 1

    # Verify code was generated and validated
    assert source.is_valid
    assert "class DoublerAgent:" in source.code
    assert "def invoke" in source.code
    assert source.generation_attempt == 1


@pytest.mark.asyncio
async def test_generate_prototype_async_iterates_on_failure() -> None:
    """Verify iteration when LLM generates invalid code."""
    intent = Intent(purpose="Test", behavior=["Test"])
    contract = Contract(agent_name="TestAgent", input_type="str", output_type="str")

    # Mock runtime that returns different code on each call
    class IteratingMockRuntime(Runtime):
        def __init__(self) -> None:
            self.call_count = 0
            self.responses = [
                # Attempt 1: Syntax error
                "class TestAgent\n    def invoke(self, x): return x",
                # Attempt 2: Valid code
                "class TestAgent:\n    def invoke(self, x: str) -> str:\n        return x",
            ]

        async def execute(
            self, agent: LLMAgent[Any, Any], input_val: Any
        ) -> AgentResult[Any]:
            response = self.responses[self.call_count]
            self.call_count += 1
            output = agent.parse_response(response)
            return AgentResult(
                output=output,
                raw_response=response,
                model="mock",
                usage={},
            )

        async def raw_completion(
            self,
            context: AgentContext,
        ) -> tuple[str, dict[str, Any]]:
            """Low-level completion call (not used in these tests)."""
            response = (
                self.responses[self.call_count]
                if self.call_count < len(self.responses)
                else self.responses[-1]
            )
            return (response, {"model": "mock"})

    runtime = IteratingMockRuntime()
    config = PrototypeConfig(use_llm=True, runtime=runtime, max_attempts=3)

    source = await generate_prototype_async(intent, contract, config)

    # Verify LLM was called twice (failed once, then succeeded)
    assert runtime.call_count == 2

    # Verify final code is valid
    assert source.is_valid
    assert source.generation_attempt == 2


@pytest.mark.asyncio
async def test_generate_prototype_async_respects_max_attempts() -> None:
    """Verify max_attempts bound is honored."""
    intent = Intent(purpose="Test", behavior=["Test"])
    contract = Contract(agent_name="TestAgent", input_type="str", output_type="str")

    # Mock that always returns invalid code
    mock_response = "class TestAgent\n    # Invalid syntax"
    runtime = MockRuntime(response=mock_response)
    config = PrototypeConfig(use_llm=True, runtime=runtime, max_attempts=3)

    source = await generate_prototype_async(intent, contract, config)

    # Verify exactly 3 attempts
    assert runtime.call_count == 3

    # Verify final result is invalid (escalation needed)
    assert not source.is_valid
    assert source.generation_attempt == 3


# ============================================================================
# Test: generate_code_with_llm Function
# ============================================================================


@pytest.mark.asyncio
async def test_generate_code_with_llm() -> None:
    """Test standalone code generation function."""
    intent = Intent(purpose="Echo", behavior=["Return input"])
    contract = Contract(agent_name="EchoAgent", input_type="str", output_type="str")

    mock_response = """class EchoAgent:
    def invoke(self, x: str) -> str:
        return x"""

    runtime = MockRuntime(response=mock_response)

    code = await generate_code_with_llm(intent, contract, runtime)

    assert "class EchoAgent:" in code
    assert "def invoke" in code


@pytest.mark.asyncio
async def test_generate_code_with_llm_with_failures() -> None:
    """Test code generation with previous failures."""
    intent = Intent(purpose="Test", behavior=["Test"])
    contract = Contract(agent_name="TestAgent", input_type="str", output_type="str")

    mock_response = (
        "class TestAgent:\n    def invoke(self, x: str) -> str:\n        return x"
    )
    runtime = MockRuntime(response=mock_response)

    failures = ["Attempt 1:", "[parse] Syntax error"]

    code = await generate_code_with_llm(
        intent, contract, runtime, previous_failures=failures
    )

    # Verify code was generated
    assert "class TestAgent:" in code

    # Note: In real usage, the prompt would include failures.
    # Here we just verify the function accepts the parameter.


# ============================================================================
# Test: Configuration Validation
# ============================================================================


@pytest.mark.asyncio
async def test_generate_prototype_async_requires_runtime_when_use_llm() -> None:
    """Verify error when use_llm=True but runtime not provided."""
    intent = Intent(purpose="Test", behavior=["Test"])
    contract = Contract(agent_name="TestAgent", input_type="str", output_type="str")

    config = PrototypeConfig(use_llm=True, runtime=None)

    with pytest.raises(ValueError, match="runtime is required when use_llm=True"):
        await generate_prototype_async(intent, contract, config)


# ============================================================================
# Test: Temperature and Token Settings
# ============================================================================


def test_code_generator_uses_zero_temperature() -> None:
    """Verify deterministic generation (temperature=0)."""
    intent = Intent(purpose="Test", behavior=["Test"])
    contract = Contract(agent_name="TestAgent", input_type="str", output_type="str")

    generator = CodeGeneratorAgent()
    request = GenerationRequest(intent=intent, contract=contract)
    context = generator.build_prompt(request)

    # Code generation should be deterministic
    assert context.temperature == 0.0


def test_code_generator_sets_max_tokens() -> None:
    """Verify max_tokens is configured."""
    intent = Intent(purpose="Test", behavior=["Test"])
    contract = Contract(agent_name="TestAgent", input_type="str", output_type="str")

    generator = CodeGeneratorAgent()
    request = GenerationRequest(intent=intent, contract=contract)
    context = generator.build_prompt(request)

    # Should have reasonable token limit
    assert context.max_tokens == 4096


# ============================================================================
# Test: Real-World Example (requires API key - skipped by default)
# ============================================================================


@pytest.mark.skip(reason="Requires API key and makes real API call")
@pytest.mark.asyncio
async def test_generate_with_real_claude() -> None:
    """
    Integration test with real Claude API.

    To run this test:
    1. Set ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN
    2. Run: pytest -k test_generate_with_real_claude -v -s
    """
    from runtime.claude import ClaudeRuntime

    intent = Intent(
        purpose="Create a simple calculator that adds two numbers",
        behavior=["Take two numbers as input", "Return their sum"],
        constraints=["Handle integer overflow gracefully"],
        examples=[
            Example(input=(2, 3), expected_output=5),
            Example(input=(100, 200), expected_output=300),
        ],
    )

    contract = Contract(
        agent_name="CalculatorAgent",
        input_type="tuple[int, int]",
        output_type="int",
        invariants=[
            Invariant(
                description="Commutative",
                property="f(a,b) == f(b,a)",
                category="behavioral",
            ),
        ],
    )

    runtime = ClaudeRuntime()
    config = PrototypeConfig(use_llm=True, runtime=runtime)

    source = await generate_prototype_async(intent, contract, config)

    # Verify generation succeeded
    print(f"\nGenerated code:\n{source.code}")
    print(f"\nGeneration attempt: {source.generation_attempt}")
    print(f"Valid: {source.is_valid}")

    assert source.is_valid
    assert "class CalculatorAgent:" in source.code
    assert "def invoke" in source.code
