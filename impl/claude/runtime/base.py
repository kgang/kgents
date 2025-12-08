"""
Base Runtime - Core abstractions for LLM-backed agent execution.

An LLMAgent wraps the bootstrap Agent with an LLM execution strategy.
The runtime handles the actual API calls and response parsing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Optional, Callable, Awaitable
import json
import asyncio

from bootstrap import Agent

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


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
    metadata: Optional[dict[str, Any]] = None  # Arbitrary metadata for agent execution


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
    retry_count: int = 0
    success: bool = True  # Whether execution succeeded
    error: Optional[str] = None  # Error message if failed

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

    async def execute_async(self, input: A, runtime: 'Runtime') -> B:
        """
        Async execution of this agent.
        
        Default implementation calls runtime.execute and extracts output.
        Override for custom async behavior.
        """
        result = await runtime.execute(self, input)
        return result.output

    def then_async(self, g: 'LLMAgent[B, C]') -> 'AsyncComposedAgent[A, C]':
        """
        Async composition: self >> g.
        
        Returns an agent that executes self, then g on the result.
        Both executions are awaited sequentially.
        """
        return AsyncComposedAgent(self, g)


class AsyncComposedAgent(LLMAgent[A, C], Generic[A, B, C]):
    """
    Composition of two async agents: f >> g.
    
    Executes f, then g on f's output.
    Preserves the morphism structure with clear A → B → C types.
    """
    
    def __init__(self, f: LLMAgent[A, B], g: LLMAgent[B, C]):
        self.f = f
        self.g = g
    
    def build_prompt(self, input: A) -> AgentContext:
        """Not used - async execution bypasses this."""
        raise NotImplementedError("AsyncComposedAgent uses execute_async")
    
    def parse_response(self, response: str) -> C:
        """Not used - async execution bypasses this."""
        raise NotImplementedError("AsyncComposedAgent uses execute_async")
    
    async def execute_async(self, input: A, runtime: 'Runtime') -> C:
        """Execute f, then g sequentially."""
        b = await self.f.execute_async(input, runtime)
        c = await self.g.execute_async(b, runtime)
        return c


async def acompose(*agents: LLMAgent) -> LLMAgent:
    """
    Async composition of multiple agents: f >> g >> h.
    
    Example:
        pipeline = acompose(extract_facts, summarize, format_output)
        result = await pipeline.execute_async(input, runtime)
    """
    if len(agents) == 0:
        raise ValueError("acompose requires at least one agent")
    if len(agents) == 1:
        return agents[0]
    
    result = agents[0]
    for agent in agents[1:]:
        result = result.then_async(agent)
    return result


async def parallel_execute(
    agents: list[LLMAgent[A, B]],
    inputs: list[A],
    runtime: 'Runtime'
) -> list[B]:
    """
    Execute multiple agents concurrently on their respective inputs.
    
    This enables true parallelism for I/O-bound LLM calls.
    
    Args:
        agents: List of agents to execute
        inputs: Corresponding inputs for each agent
        runtime: Runtime to use for execution
    
    Returns:
        List of outputs in the same order as inputs
    
    Example:
        # Process multiple documents concurrently
        results = await parallel_execute(
            [summarize_agent] * len(documents),
            documents,
            runtime
        )
    """
    if len(agents) != len(inputs):
        raise ValueError("agents and inputs must have same length")
    
    tasks = [
        agent.execute_async(input_val, runtime)
        for agent, input_val in zip(agents, inputs)
    ]
    
    return await asyncio.gather(*tasks)


class TransientError(Exception):
    """Transient error that may succeed on retry (rate limits, timeouts, etc)."""
    pass


class PermanentError(Exception):
    """Permanent error that won't succeed on retry (auth, invalid input, etc)."""
    pass


async def with_retry(
    fn: Callable[[], Awaitable[B]],
    max_attempts: int = 3,
    backoff_base: float = 2.0,
    is_transient: Optional[Callable[[Exception], bool]] = None
) -> tuple[B, int]:
    """
    Fix pattern for retry logic.
    
    Executes fn with exponential backoff on transient errors.
    This is the Fix pattern: we repeatedly apply fn until success or max attempts.
    
    Args:
        fn: Async function to retry
        max_attempts: Maximum number of attempts (default 3)
        backoff_base: Base for exponential backoff in seconds (default 2.0)
        is_transient: Predicate to determine if error is transient (default: check TransientError type)
    
    Returns:
        Tuple of (result, attempt_count)
    
    Raises:
        Last exception if all attempts fail
    
    Example:
        result, attempts = await with_retry(
            lambda: runtime.raw_completion(context),
            max_attempts=5
        )
    """
    if is_transient is None:
        is_transient = lambda e: isinstance(e, TransientError)
    
    last_error = None
    
    for attempt in range(max_attempts):
        try:
            result = await fn()
            return (result, attempt)
        except Exception as e:
            last_error = e
            
            # Don't retry on permanent errors
            if not is_transient(e):
                raise
            
            # Don't sleep after last attempt
            if attempt < max_attempts - 1:
                delay = backoff_base ** attempt
                await asyncio.sleep(delay)
    
    # All attempts exhausted
    raise last_error


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


def parse_structured_sections(
    response: str,
    section_names: list[str]
) -> dict[str, list[str]]:
    """
    Parse structured sections from LLM response.

    Looks for section headers (e.g., "RESPONSES:", "FOLLOW-UPS:") and extracts
    content as lists. Handles both numbered lists (1. item) and bullet lists (- item).

    Args:
        response: The LLM response text
        section_names: List of section names to look for (case-insensitive)

    Returns:
        Dict mapping section names to lists of extracted items

    Example:
        >>> response = '''
        ... RESPONSES:
        ... 1. First response
        ... 2. Second response
        ...
        ... FOLLOW-UPS:
        ... - First question?
        ... - Second question?
        ... '''
        >>> parse_structured_sections(response, ["responses", "follow-ups"])
        {'responses': ['First response', 'Second response'],
         'follow-ups': ['First question?', 'Second question?']}
    """
    import re

    result: dict[str, list[str]] = {}
    lines = response.split('\n')

    # Build regex patterns for section headers (case-insensitive)
    # Match "SECTION_NAME:" or "SECTION-NAME:" or "SECTION NAME:"
    section_patterns = {}
    for name in section_names:
        # Normalize name for pattern matching (replace underscores/hyphens with flexible pattern)
        pattern_name = name.replace('_', r'[\s_-]').replace('-', r'[\s_-]')
        pattern = re.compile(rf'^{pattern_name}\s*:\s*$', re.IGNORECASE)
        section_patterns[name] = pattern

    current_section = None
    current_items = []

    for line in lines:
        stripped = line.strip()

        # Check if this line is a section header
        found_section = False
        for section_name, pattern in section_patterns.items():
            if pattern.match(stripped):
                # Save previous section if any
                if current_section and current_items:
                    result[current_section] = current_items

                # Start new section
                current_section = section_name
                current_items = []
                found_section = True
                break

        if found_section:
            continue

        # If we're in a section, try to extract list items
        if current_section:
            # Match numbered lists: "1. item" or "1) item"
            numbered_match = re.match(r'^\d+[\.\)]\s+(.+)$', stripped)
            if numbered_match:
                current_items.append(numbered_match.group(1))
                continue

            # Match bullet lists: "- item" or "* item"
            bullet_match = re.match(r'^[-\*]\s+(.+)$', stripped)
            if bullet_match:
                current_items.append(bullet_match.group(1))
                continue

    # Save last section
    if current_section and current_items:
        result[current_section] = current_items

    return result
