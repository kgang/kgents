"""
LLM-powered code generation for F-gents Phase 3.

This module provides CodeGeneratorAgent, an LLMAgent that generates Python code
from Intent + Contract specifications using Claude.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from agents.f.contract import Contract
from agents.f.intent import Intent
from runtime.base import AgentContext, LLMAgent

if TYPE_CHECKING:
    from runtime.base import Runtime


@dataclass
class GenerationRequest:
    """Input to CodeGeneratorAgent: what to generate and context."""

    intent: Intent
    contract: Contract
    previous_failures: list[str] | None = None


class CodeGeneratorAgent(LLMAgent[GenerationRequest, str]):
    """
    Agent that generates Python code from Intent + Contract.

    Morphism: GenerationRequest → str (Python source code)

    This agent uses Claude to synthesize implementations that satisfy:
    - The natural language intent
    - The formal contract (types + invariants)
    - Previous iteration feedback (if retrying)

    Example:
        >>> runtime = ClaudeRuntime()
        >>> generator = CodeGeneratorAgent()
        >>> request = GenerationRequest(intent, contract)
        >>> result = await runtime.execute(generator, request)
        >>> code = result.output  # Generated Python code
    """

    @property
    def name(self) -> str:
        return "CodeGeneratorAgent"

    async def invoke(self, request: GenerationRequest) -> str:
        """
        Not directly usable - this agent requires a runtime.
        Use runtime.execute(agent, request) instead.
        """
        raise NotImplementedError(
            "CodeGeneratorAgent requires runtime. Use: await runtime.execute(agent, request)"
        )

    def build_prompt(self, request: GenerationRequest) -> AgentContext:
        """
        Build LLM prompt from generation request.

        Constructs detailed specification including:
        - Intent (purpose, behavior, constraints)
        - Contract (types, invariants, composition)
        - Examples (test cases)
        - Previous failures (iteration feedback)
        """
        prompt = self._build_generation_prompt(
            request.intent,
            request.contract,
            request.previous_failures,
        )

        return AgentContext(
            system_prompt=self._system_prompt(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,  # Deterministic code generation
            max_tokens=4096,
        )

    def parse_response(self, response: str) -> str:
        """
        Parse LLM response to extract Python code.

        Handles common formatting artifacts:
        - Markdown code blocks (```python ... ```)
        - Explanatory text before/after code
        - Extra whitespace

        Returns clean Python source code.
        """
        # Remove markdown code blocks if present
        code = response.strip()

        # Match ```python ... ``` or ``` ... ```
        code_block_pattern = r"```(?:python)?\s*\n(.*?)\n```"
        matches = re.findall(code_block_pattern, code, re.DOTALL)

        if matches:
            # Take the first code block
            code = matches[0]
        else:
            # No markdown blocks - use raw response
            # But remove common prefixes like "Here's the implementation:"
            lines = code.split("\n")
            cleaned_lines = []
            found_code = False

            for line in lines:
                # Skip explanatory lines before code starts
                if not found_code:
                    stripped = line.strip()
                    if stripped.startswith("class ") or stripped.startswith("def "):
                        found_code = True
                        cleaned_lines.append(line)
                    elif stripped.startswith('"""') or stripped.startswith("'''"):
                        # Module docstring might come first
                        found_code = True
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)

            if cleaned_lines:
                code = "\n".join(cleaned_lines)

        return code.strip()

    def _system_prompt(self) -> str:
        """System prompt for code generation."""
        return """You are a Python code generation agent specializing in creating clean, correct implementations from specifications.

Your task is to generate Python code that:
1. Satisfies the given contract (type signatures and invariants)
2. Implements the intended behavior described in natural language
3. Passes all provided test cases
4. Handles errors gracefully
5. Is clean, readable, and maintainable

Guidelines:
- Write ONLY executable Python code, no explanations
- Include clear docstrings
- Use type hints for method signatures
- Handle edge cases appropriately
- Avoid dangerous operations (eval, exec, os.system, subprocess)
- Keep code concise (<120 chars per line)
- Do NOT include TODO or FIXME comments - implement complete solutions

If previous attempts failed, carefully address the reported errors."""

    def _build_generation_prompt(
        self,
        intent: Intent,
        contract: Contract,
        previous_failures: list[str] | None = None,
    ) -> str:
        """
        Build prompt for LLM code generation.

        This constructs a detailed prompt including:
        - Intent (natural language guidance)
        - Contract (type signatures + invariants)
        - Examples (test cases to satisfy)
        - Previous failures (if iteration)

        The prompt guides the LLM to generate Python code satisfying the contract.
        """
        # Base prompt structure
        prompt_parts = [
            "# Task: Generate Python Agent Implementation",
            "",
            "## Intent",
            f"Purpose: {intent.purpose}",
            "",
            "Behavior:",
        ]

        for behavior in intent.behavior:
            prompt_parts.append(f"- {behavior}")

        prompt_parts.append("")
        prompt_parts.append("Constraints:")
        for constraint in intent.constraints:
            prompt_parts.append(f"- {constraint}")

        # Add contract specification
        prompt_parts.extend(
            [
                "",
                "## Contract Specification",
                f"Agent Name: {contract.agent_name}",
                f"Input Type: {contract.input_type}",
                f"Output Type: {contract.output_type}",
                "",
                "Invariants (must be satisfied):",
            ]
        )

        for inv in contract.invariants:
            prompt_parts.append(f"- {inv.description} → {inv.property}")

        if contract.composition_rules:
            prompt_parts.append("")
            prompt_parts.append("Composition Rules:")
            for rule in contract.composition_rules:
                prompt_parts.append(f"- {rule.mode}: {rule.description}")

        # Add examples if provided
        if intent.examples:
            prompt_parts.extend(
                [
                    "",
                    "## Examples (Test Cases)",
                ]
            )
            for i, example in enumerate(intent.examples, 1):
                prompt_parts.append(f"Example {i}:")
                prompt_parts.append(f"  Input: {example.input}")
                prompt_parts.append(f"  Expected Output: {example.expected_output}")

        # Add iteration feedback if this is a retry
        if previous_failures:
            prompt_parts.extend(
                [
                    "",
                    "## Previous Attempt Failures",
                    "The previous implementation failed with these errors:",
                    "",
                ]
            )
            prompt_parts.extend(previous_failures)
            prompt_parts.extend(
                [
                    "",
                    "Please fix these issues in the new implementation.",
                ]
            )

        # Add code generation instructions
        prompt_parts.extend(
            [
                "",
                "## Implementation Requirements",
                "",
                "Generate a Python class that:",
                f"1. Is named '{contract.agent_name}'",
                f"2. Has a method 'invoke(self, input: {contract.input_type}) -> {contract.output_type}'",
                "3. Satisfies all invariants listed above",
                "4. Includes proper error handling",
                "5. Has a clear docstring explaining behavior",
                "",
                "Return ONLY the Python code, no explanations or markdown formatting.",
            ]
        )

        return "\n".join(prompt_parts)


async def generate_code_with_llm(
    intent: Intent,
    contract: Contract,
    runtime: "Runtime",
    previous_failures: list[str] | None = None,
) -> str:
    """
    Generate Python code using LLM.

    This is the async interface to CodeGeneratorAgent.
    Use this from generate_prototype when config.use_llm=True.

    Args:
        intent: Natural language specification
        contract: Formal interface contract
        runtime: LLM runtime (e.g., ClaudeRuntime)
        previous_failures: Errors from previous attempts (for iteration)

    Returns:
        Generated Python source code

    Example:
        >>> from runtime.claude import ClaudeRuntime
        >>> runtime = ClaudeRuntime()
        >>> code = await generate_code_with_llm(intent, contract, runtime)
    """
    request = GenerationRequest(
        intent=intent,
        contract=contract,
        previous_failures=previous_failures,
    )

    generator = CodeGeneratorAgent()
    result = await runtime.execute(generator, request)

    return result.output
