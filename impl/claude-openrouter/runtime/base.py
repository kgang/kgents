"""
Base Runtime - Core abstractions for LLM-backed agent execution.

An LLMAgent wraps the bootstrap Agent with an LLM execution strategy.
The runtime handles the actual API calls and response parsing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Optional
import json

from bootstrap import Agent

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class AgentContext:
    """
    Context passed to LLM during agent execution.

    Contains the agent's system prompt, conversation history,
    and any grounded facts needed for execution.
    """
    system_prompt: str
    messages: list[dict[str, str]] = field(default_factory=list)
    facts: Optional[dict[str, Any]] = None
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class AgentResult(Generic[B]):
    """
    Result of LLM agent execution.

    Includes the output, raw response, and any metadata.
    """
    output: B
    raw_response: str
    model: str
    usage: dict[str, int] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.usage.get("total_tokens", 0)


class LLMAgent(Agent[A, B], ABC):
    """
    Base class for LLM-backed agents.

    Extends the bootstrap Agent interface with LLM-specific methods:
    - build_prompt: Convert input to LLM prompt
    - parse_response: Extract output from LLM response

    Usage:
        class MyAgent(LLMAgent[str, dict]):
            def build_prompt(self, input: str) -> AgentContext:
                return AgentContext(
                    system_prompt="You are a helpful assistant.",
                    messages=[{"role": "user", "content": input}],
                )

            def parse_response(self, response: str) -> dict:
                return json.loads(response)
    """

    @abstractmethod
    def build_prompt(self, input: A) -> AgentContext:
        """Convert input to LLM context."""
        pass

    @abstractmethod
    def parse_response(self, response: str) -> B:
        """Parse LLM response to output type."""
        pass


class Runtime(ABC):
    """
    Base runtime for executing LLM agents.

    Subclasses implement the actual API calls for different providers.
    """

    @abstractmethod
    async def execute(
        self,
        agent: LLMAgent[A, B],
        input: A
    ) -> AgentResult[B]:
        """Execute an LLM agent with input and return result."""
        pass

    @abstractmethod
    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """
        Low-level completion call.

        Returns (response_text, metadata).
        """
        pass


def robust_json_parse(response: str, allow_partial: bool = True) -> dict[str, Any]:
    """
    Robust JSON parser that handles common LLM output issues.

    Handles:
    - Markdown code blocks (```json ... ```)
    - Truncated JSON (closes brackets)
    - Trailing commas
    - Extra text before/after JSON
    - Unterminated strings

    Args:
        response: Raw LLM response text
        allow_partial: If True, try to repair truncated JSON

    Returns:
        Parsed JSON dict

    Raises:
        ValueError: If JSON cannot be parsed even after repair attempts
    """
    text = response.strip()

    # Step 1: Extract JSON from markdown code blocks
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
        else:
            # Unterminated code block - take everything after ```json
            text = text[start:].strip()
    elif "```" in text:
        # Generic code block
        start = text.find("```") + 3
        # Skip language identifier if on same line
        newline = text.find("\n", start)
        if newline > 0:
            start = newline + 1
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
        else:
            text = text[start:].strip()

    # Step 2: Find JSON boundaries if there's extra text
    first_brace = text.find("{")
    first_bracket = text.find("[")
    if first_brace < 0 and first_bracket < 0:
        raise ValueError("No JSON object or array found in response")

    if first_brace >= 0 and (first_bracket < 0 or first_brace < first_bracket):
        text = text[first_brace:]
        closer = "}"
        opener = "{"
    else:
        text = text[first_bracket:]
        closer = "]"
        opener = "["

    # Step 3: Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 4: Try to repair common issues
    if allow_partial:
        repaired = _repair_json(text, opener, closer)
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass

    # Step 5: Last resort - try to extract any valid JSON object
    import re
    # Look for outermost balanced braces/brackets
    depth = 0
    start = -1
    for i, char in enumerate(text):
        if char == opener:
            if depth == 0:
                start = i
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0 and start >= 0:
                candidate = text[start:i+1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass

    raise ValueError(f"Could not parse JSON from response: {text[:200]}...")


def _repair_json(text: str, opener: str, closer: str) -> str:
    """
    Attempt to repair truncated or malformed JSON.

    Strategies:
    - Remove trailing commas
    - Close unterminated strings
    - Balance brackets/braces
    - Handle embedded code with unescaped characters
    """
    import re

    # Remove trailing commas before closers
    text = re.sub(r',\s*([}\]])', r'\1', text)

    # Try to find and fix unterminated strings containing code
    # This is tricky - we need to find the last properly escaped string
    repaired = text

    # Count unescaped quotes (not preceded by backslash)
    # This is a simplified heuristic
    in_string = False
    escaped = False
    quote_positions = []

    for i, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == '\\':
            escaped = True
            continue
        if char == '"':
            quote_positions.append(i)
            in_string = not in_string

    # If odd number of quotes, string is unterminated
    if len(quote_positions) % 2 == 1:
        # Add closing quote
        repaired = repaired.rstrip()
        if not repaired.endswith('"'):
            repaired += '"'

    # Count brackets to see if we need to close
    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")

    # Close brackets and braces
    repaired += "]" * open_brackets
    repaired += "}" * open_braces

    return repaired


def _extract_field_values(text: str, fields: list[str]) -> dict[str, Any]:
    """
    Extract specific field values from malformed JSON using regex.

    Fallback for when JSON repair fails but we need specific fields.
    """
    import re
    result = {}

    for field in fields:
        # Match "field": "value" or "field": value patterns
        pattern = rf'"{field}"\s*:\s*("([^"\\]|\\.)*"|[^,\}}\]]+)'
        match = re.search(pattern, text)
        if match:
            value = match.group(1).strip()
            # Try to parse the value
            if value.startswith('"') and value.endswith('"'):
                result[field] = value[1:-1]  # Remove quotes
            elif value.lower() in ('true', 'false'):
                result[field] = value.lower() == 'true'
            elif value.lower() == 'null':
                result[field] = None
            else:
                try:
                    result[field] = float(value) if '.' in value else int(value)
                except ValueError:
                    result[field] = value

    return result


def json_response_parser(response: str) -> dict[str, Any]:
    """Standard JSON response parser with markdown code block handling."""
    return robust_json_parse(response, allow_partial=True)
