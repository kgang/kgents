"""
Reflection Parser (Strategy 3.1 - Enhanced)

The Principle: Instead of generic retry loops, use LLM to reflect on and fix
its own errors. Feed validation errors back to the LLM for targeted repairs.

Benefits:
- Learns from mistakes (reflection, not blind retry)
- Cheaper than full regeneration (fixes specific issues)
- Precise error messages guide LLM to correct fix
- Confidence degrades with retry count

Use Cases:
- Code generation: Fix import errors, type mismatches
- B-gent hypothesis validation: Add missing falsifiability criteria
- F-gent contract synthesis: Repair constraint violations
"""

from dataclasses import dataclass
from typing import Any, Callable, Generic, Iterator, Optional, TypeVar

from agents.p.core import Parser, ParserConfig, ParseResult

A = TypeVar("A")


@dataclass
class ReflectionContext:
    """
    Context for reflection loop iterations.

    Tracks:
    - Original input
    - Current attempt
    - Previous errors
    - LLM responses
    """

    original_input: str
    attempt: int
    previous_errors: list[str]
    previous_responses: list[str]


class ReflectionParser(Generic[A]):
    """
    Parser with LLM-based reflection loop for self-repair.

    Unlike blind retry, reflection:
    1. Tries to parse
    2. On failure, extracts error message
    3. Asks LLM to fix the specific error
    4. Retries with fixed output
    5. Limits attempts (config.max_reflection_retries)

    Confidence degrades with retry count:
    - 0 retries (first try): 0.9
    - 1 retry: 0.7
    - 2 retries: 0.5
    - 3+ retries: 0.4
    """

    def __init__(
        self,
        base_parser: Parser[A],
        llm_fix_fn: Callable[[str, str, ReflectionContext], str],
        config: Optional[ParserConfig] = None,
    ):
        """
        Initialize reflection parser.

        Args:
            base_parser: Underlying parser to use for actual parsing
            llm_fix_fn: Function that takes (text, error, context) and returns fixed text
                       Signature: (text: str, error: str, context: ReflectionContext) -> str
            config: Parser configuration (uses max_reflection_retries)
        """
        self.base_parser = base_parser
        self.llm_fix_fn = llm_fix_fn
        self.config = config or ParserConfig()

    def parse(self, text: str) -> ParseResult[A]:
        """
        Parse with reflection loop.

        Args:
            text: Text to parse

        Returns:
            ParseResult[A] with reflection metadata

        Note:
            Confidence degrades with retry count.
            All reflection attempts tracked in metadata.
        """
        context = ReflectionContext(
            original_input=text,
            attempt=0,
            previous_errors=[],
            previous_responses=[],
        )

        current_text = text

        for attempt in range(self.config.max_reflection_retries + 1):
            context.attempt = attempt

            # Try to parse
            result = self.base_parser.parse(current_text)

            if result.success:
                # Success! Calculate confidence based on attempts
                confidence = self._calculate_confidence(attempt, result.confidence)

                # Track reflection in metadata
                result.confidence = confidence
                result.strategy = f"reflection[{attempt}]:{result.strategy}"
                result.metadata["reflection_attempts"] = attempt
                result.metadata["reflection_errors"] = context.previous_errors
                result.metadata["reflection_fixed"] = attempt > 0

                # Add repair note if we reflected
                if attempt > 0:
                    result.repairs.append(f"Fixed via {attempt} reflection iteration(s)")

                return result
            else:
                # Failure - reflect and retry
                error = result.error or "Unknown parsing error"
                context.previous_errors.append(error)

                # Check if we've exhausted retries
                if attempt >= self.config.max_reflection_retries:
                    # Out of retries, return failure
                    return ParseResult(
                        success=False,
                        error=f"Reflection failed after {attempt + 1} attempts. Last error: {error}",
                        strategy="reflection-exhausted",
                        metadata={
                            "reflection_attempts": attempt + 1,
                            "reflection_errors": context.previous_errors,
                        },
                    )

                # Ask LLM to fix the error
                try:
                    fixed_text = self.llm_fix_fn(current_text, error, context)
                    context.previous_responses.append(fixed_text)
                    current_text = fixed_text
                except Exception as e:
                    return ParseResult(
                        success=False,
                        error=f"LLM reflection failed: {e}",
                        strategy="reflection-llm-error",
                        metadata={
                            "reflection_attempts": attempt + 1,
                            "reflection_errors": context.previous_errors + [str(e)],
                        },
                    )

        # Should never reach here (loop always returns)
        return ParseResult(
            success=False,
            error="Reflection loop unexpected termination",
            strategy="reflection-error",
        )

    def _calculate_confidence(self, attempts: int, base_confidence: float) -> float:
        """
        Calculate confidence based on reflection attempts.

        Args:
            attempts: Number of reflection iterations (0 = first try)
            base_confidence: Confidence from base parser

        Returns:
            Adjusted confidence (penalized by retry count)
        """
        if attempts == 0:
            # First try success - minimal penalty
            return base_confidence * 0.95
        elif attempts == 1:
            # One reflection - moderate penalty
            return base_confidence * 0.7
        elif attempts == 2:
            # Two reflections - significant penalty
            return base_confidence * 0.5
        else:
            # Three+ reflections - heavy penalty
            return base_confidence * 0.4

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[A]]:
        """
        Stream parsing with reflection (buffer and parse complete).

        Note:
            Reflection requires complete input to retry, so we buffer.
        """
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config: Any) -> "ReflectionParser[A]":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**vars(self.config), **config})
        new_config.validate()

        return ReflectionParser(
            base_parser=self.base_parser,
            llm_fix_fn=self.llm_fix_fn,
            config=new_config,
        )


# Convenience constructors and helpers


def simple_reflection_prompt(text: str, error: str, context: ReflectionContext) -> str:
    """
    Simple reflection prompt for LLMs.

    Can be used as default llm_fix_fn template.
    User should wrap this with their actual LLM call.

    Args:
        text: Current text that failed to parse
        error: Error message from parser
        context: Reflection context

    Returns:
        Prompt string to send to LLM
    """
    return f"""
The following text failed to parse with error:

ERROR: {error}

TEXT:
{text}

Please fix the text to resolve this error. Output ONLY the corrected text, no explanations.

Previous attempts ({context.attempt}):
{chr(10).join(f"- {e}" for e in context.previous_errors)}

Corrected text:
""".strip()


def create_reflection_parser_with_llm(
    base_parser: Parser[Any],
    llm_callable: Callable[[str], str],
    config: Optional[ParserConfig] = None,
) -> "ReflectionParser[Any]":
    """
    Create reflection parser with LLM callable.

    Args:
        base_parser: Base parser to wrap
        llm_callable: Function that takes prompt and returns LLM response
                     Signature: (prompt: str) -> str
        config: Parser configuration

    Returns:
        ReflectionParser configured with LLM

    Example:
        >>> import anthropic
        >>> client = anthropic.Anthropic()
        >>>
        >>> def llm_fix(prompt: str) -> str:
        ...     response = client.messages.create(
        ...         model="claude-3-5-sonnet-20241022",
        ...         messages=[{"role": "user", "content": prompt}],
        ...         max_tokens=1000,
        ...     )
        ...     return response.content[0].text
        >>>
        >>> parser = create_reflection_parser_with_llm(
        ...     base_parser=json_parser,
        ...     llm_callable=llm_fix,
        ... )
    """

    def llm_fix_fn(text: str, error: str, context: ReflectionContext) -> str:
        """Wrapper that creates prompt and calls LLM."""
        prompt = simple_reflection_prompt(text, error, context)
        return llm_callable(prompt)

    return ReflectionParser(
        base_parser=base_parser,
        llm_fix_fn=llm_fix_fn,
        config=config,
    )


# Mock LLM for testing (no actual LLM calls)


def mock_llm_fix_json(text: str, error: str, context: ReflectionContext) -> str:
    """
    Mock LLM that fixes common JSON errors for testing.

    This is NOT a real LLM - it's a deterministic rule-based fixer
    for testing ReflectionParser without API calls.
    """
    import re

    # Fix unclosed structures (any of these errors indicate unclosed brackets/braces)
    unclosed_indicators = [
        "unclosed",
        "unexpected end",
        "unterminated string",
        "expecting ',' delimiter",
        "expecting property name",
        "end of input",
        "eof",
    ]

    if any(indicator in error.lower() for indicator in unclosed_indicators):
        # Try to close structures
        if text.count("{") > text.count("}"):
            return text + "}"
        if text.count("[") > text.count("]"):
            return text + "]"
        # If we have unclosed string, try to close it
        if text.count('"') % 2 != 0:
            return text + '"'

    # Fix trailing comma
    if "trailing comma" in error.lower():
        return text.replace(",]", "]").replace(",}", "}")

    # Fix missing quotes
    if "quote" in error.lower() and "property name" in error.lower():
        # Simple heuristic: if we see key: value without quotes, add them
        return re.sub(r":\s*([a-zA-Z]+)", r': "\1"', text)

    # Default: return as-is (reflection will fail)
    return text
