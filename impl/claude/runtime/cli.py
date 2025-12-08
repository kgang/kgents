"""
Claude CLI Runtime - Execute agents using the Claude Code CLI.

Uses `claude -p` for authenticated execution without needing API keys.
Leverages the CLI's built-in OAuth authentication.

Implements Fix pattern: retries on parse failures until valid output.
"""

import asyncio
import json
import shutil
from typing import Any, TypeVar, Callable
from enum import Enum

from .base import Runtime, LLMAgent, AgentContext, AgentResult

A = TypeVar("A")
B = TypeVar("B")


class ParseErrorType(Enum):
    """Classification of parse errors for retry strategy."""
    TRANSIENT_FORMAT = "transient_format"  # Missing markdown, JSON syntax - retry
    TRANSIENT_EXTRACTION = "transient_extraction"  # Data present but malformed - retry with coercion
    PERMANENT_SCHEMA = "permanent_schema"  # Wrong data structure - fast fail or force coercion
    PERMANENT_MISSING = "permanent_missing"  # Required data absent - fast fail
    TIMEOUT = "timeout"  # CLI timeout - fast fail
    UNKNOWN = "unknown"  # Unclassified - retry


class ParseError(Exception):
    """Raised when LLM output cannot be parsed."""
    def __init__(self, message: str, raw_response: str, error_type: ParseErrorType = ParseErrorType.UNKNOWN):
        super().__init__(message)
        self.raw_response = raw_response
        self.error_type = error_type


def classify_parse_error(error_msg: str, raw_response: str) -> ParseErrorType:
    """
    Classify a parse error to determine retry strategy.
    
    Returns:
        ParseErrorType indicating whether error is transient or permanent
    """
    error_lower = error_msg.lower()
    
    # Timeout errors - permanent
    if "timeout" in error_lower:
        return ParseErrorType.TIMEOUT
    
    # Missing sections - check if data exists but poorly formatted
    if "no code content" in error_lower or "no json" in error_lower:
        # If response is very short, data is likely missing (permanent)
        if len(raw_response.strip()) < 50:
            return ParseErrorType.PERMANENT_MISSING
        # If response is substantial, likely formatting issue (transient)
        return ParseErrorType.TRANSIENT_FORMAT
    
    # JSON errors - check if JSON-like content exists
    if "json" in error_lower or "decode" in error_lower:
        # Look for JSON-like patterns
        if "{" in raw_response and "}" in raw_response:
            return ParseErrorType.TRANSIENT_EXTRACTION
        return ParseErrorType.PERMANENT_MISSING
    
    # Schema/type errors - permanent
    if any(term in error_lower for term in ["schema", "type", "field required", "missing key"]):
        return ParseErrorType.PERMANENT_SCHEMA
    
    # Extraction/parsing errors - transient if data seems present
    if any(term in error_lower for term in ["extract", "parse", "format"]):
        if len(raw_response.strip()) > 100:
            return ParseErrorType.TRANSIENT_EXTRACTION
        return ParseErrorType.PERMANENT_MISSING
    
    return ParseErrorType.UNKNOWN


class CLIAgent:
    """
    Pure morphism: AgentContext → (str, dict).
    
    This is the core CLI execution primitive - a simple function
    from prompt context to raw LLM response.
    
    Type signature: AgentContext → (response_text, metadata)
    
    Benefits:
    - Composable: Can be wrapped, chained, or tested independently
    - Clear contract: Input and output types are explicit
    - Single responsibility: Just execute, don't retry/parse
    """
    
    def __init__(
        self,
        claude_path: str | None = None,
        timeout: float = 120.0,
        verbose: bool = False,
        progress_callback: Callable[[str], None] | None = None,
    ):
        """
        Initialize CLI agent.
        
        Args:
            claude_path: Path to claude CLI. Defaults to finding it in PATH.
            timeout: Timeout in seconds for CLI execution.
            verbose: Print progress messages during execution.
            progress_callback: Optional callback for progress updates.
        """
        self._claude_path = claude_path or shutil.which("claude")
        self._timeout = timeout
        self._verbose = verbose
        self._progress_callback = progress_callback
        
        if not self._claude_path:
            raise RuntimeError(
                "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )
    
    def _log(self, msg: str) -> None:
        """Log progress if verbose or callback is set."""
        if self._progress_callback:
            self._progress_callback(msg)
        if self._verbose:
            print(f"      [CLI] {msg}", flush=True)
    
    async def __call__(self, context: AgentContext) -> tuple[str, dict[str, Any]]:
        """
        Execute: AgentContext → (response_text, metadata).
        
        This is the morphism application - pure execution without retry logic.
        """
        # Build the prompt from system + user messages
        prompt_parts = []
        
        if context.system_prompt:
            prompt_parts.append(context.system_prompt)
        
        for msg in context.messages:
            if msg["role"] == "user":
                prompt_parts.append(msg["content"])
        
        full_prompt = "\n\n".join(prompt_parts)
        prompt_len = len(full_prompt)
        self._log(f"Sending {prompt_len:,} chars to Claude CLI...")
        
        # Execute claude -p
        assert self._claude_path is not None  # Already validated in __init__
        proc = await asyncio.create_subprocess_exec(
            self._claude_path,
            "-p", full_prompt,
            "--output-format", "text",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=self._timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise TimeoutError(f"Claude CLI timed out after {self._timeout}s")
        
        if proc.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise RuntimeError(f"Claude CLI failed: {error_msg}")
        
        response_text = stdout.decode().strip()
        self._log(f"Received {len(response_text):,} chars response")
        
        # CLI doesn't provide token counts, so we estimate
        metadata = {
            "model": "claude-cli",
            "usage": {
                "input_tokens": len(full_prompt) // 4,  # Rough estimate
                "output_tokens": len(response_text) // 4,
                "total_tokens": (len(full_prompt) + len(response_text)) // 4,
            },
        }
        
        return response_text, metadata


class ClaudeCLIRuntime(Runtime):
    """
    Runtime for executing LLM agents via Claude Code CLI.

    Uses CLIAgent morphism internally for execution.
    Adds retry logic (Fix pattern) and response coercion.

    Usage:
        runtime = ClaudeCLIRuntime()
        result = await runtime.execute(my_agent, input_data)
    """

    def __init__(
        self,
        claude_path: str | None = None,
        timeout: float = 120.0,
        max_retries: int = 3,
        verbose: bool = False,
        progress_callback: Callable[[str], None] | None = None,
        enable_coercion: bool = True,
        coercion_confidence: float = 0.9,
    ):
        """
        Initialize Claude CLI runtime.

        Args:
            claude_path: Path to claude CLI. Defaults to finding it in PATH.
            timeout: Timeout in seconds for CLI execution.
            max_retries: Maximum retries on parse failures (Fix pattern).
            verbose: Print progress messages during execution.
            progress_callback: Optional callback for progress updates.
            enable_coercion: Use AI to coerce malformed responses as last resort.
            coercion_confidence: Minimum confidence (0-1) to accept coerced response.
        """
        # Compose with CLIAgent morphism
        self._cli_agent = CLIAgent(
            claude_path=claude_path,
            timeout=timeout,
            verbose=verbose,
            progress_callback=progress_callback,
        )
        self._max_retries = max_retries
        self._enable_coercion = enable_coercion
        self._coercion_confidence = coercion_confidence

    def _log(self, msg: str) -> None:
        """Log progress (delegate to CLI agent)."""
        self._cli_agent._log(msg)

    def _build_retry_message(self, error: str, previous_response: str, error_type: ParseErrorType) -> str:
        """
        Build a targeted retry message based on error type.

        This implements the "delta retry" pattern - ask only for what we don't have.
        """
        error_lower = error.lower()

        # Detect specific missing components
        if "no code content" in error_lower or "new_content" in error_lower:
            return (
                "Your response was missing the CODE section. "
                "Please provide ONLY the complete code in a markdown block:\n\n"
                "## CODE\n```python\n# Your complete file here\n```"
            )
        elif "no json" in error_lower or "json" in error_lower:
            return (
                "Your response was missing or had invalid METADATA. "
                "Please provide ONLY the metadata JSON:\n\n"
                "## METADATA\n"
                '{"description": "...", "rationale": "...", "improvement_type": "...", "confidence": 0.8}'
            )
        elif "description" in error_lower:
            return 'Please provide just the "description" field as a simple string.'
        elif "rationale" in error_lower:
            return 'Please provide just the "rationale" field as a simple string.'
        else:
            # Generic fallback
            return (
                f"Parse error: {error}\n\n"
                "Please provide your response in the expected format. "
                "Keep it simple - one field at a time if needed."
            )

    async def _coerce_response(
        self,
        malformed_response: str,
        expected_format: str,
        error_message: str,
    ) -> tuple[str, float]:
        """
        Use AI to coerce a malformed response into the expected format.

        Returns (coerced_response, confidence).
        """
        coercion_prompt = f"""You are a response parser. Extract data from a malformed LLM response and reformat it correctly.

MALFORMED RESPONSE:
{malformed_response[:8000]}  # Truncate to avoid massive prompts

EXPECTED FORMAT:
{expected_format}

PARSE ERROR:
{error_message}

INSTRUCTIONS:
1. Extract all relevant data from the malformed response
2. Reformat it into the expected structure
3. If data is missing, use reasonable defaults or "unknown"
4. Return the reformatted response followed by your confidence (0.0-1.0)

OUTPUT FORMAT:
## REFORMATTED
[Your reformatted response here]

## CONFIDENCE
[A number between 0.0 and 1.0]"""

        self._log("Attempting AI coercion of malformed response...")

        context = AgentContext(
            system_prompt="You are a precise data extraction and reformatting assistant.",
            messages=[{"role": "user", "content": coercion_prompt}],
            temperature=0.1,  # Low temperature for precise extraction
            max_tokens=4096,
        )

        response_text, _ = await self._cli_agent(context)

        # Parse the coercion response
        import re

        # Extract reformatted content
        reformatted_match = re.search(
            r'##\s*REFORMATTED\s*\n(.*?)(?=##\s*CONFIDENCE|$)',
            response_text,
            re.DOTALL | re.IGNORECASE
        )

        # Extract confidence
        confidence_match = re.search(
            r'##\s*CONFIDENCE\s*\n\s*([\d.]+)',
            response_text,
            re.IGNORECASE
        )

        if reformatted_match:
            coerced = reformatted_match.group(1).strip()
        else:
            # Fallback: use the whole response
            coerced = response_text

        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
            except ValueError:
                confidence = 0.5
        else:
            confidence = 0.5

        self._log(f"Coercion confidence: {confidence:.2f}")
        return coerced, confidence

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """Execute raw completion via CLI agent morphism."""
        return await self._cli_agent(context)

    async def execute(
        self,
        agent: LLMAgent[A, B],
        input: A,
    ) -> AgentResult[B]:
        """
        Execute an LLM agent with Claude CLI.

        Implements Fix pattern: retries on parse failures with feedback.
        Uses error classification to apply smart retry strategies.
        """
        context = agent.build_prompt(input)
        last_error = None
        last_error_type = ParseErrorType.UNKNOWN
        all_responses = []

        for attempt in range(self._max_retries):
            # Add retry context if this is a retry
            if attempt > 0 and last_error:
                # Construct a helpful retry message based on what's missing
                retry_message = self._build_retry_message(last_error, all_responses[-1], last_error_type)
                retry_context = AgentContext(
                    system_prompt=context.system_prompt,
                    messages=context.messages + [
                        {"role": "assistant", "content": all_responses[-1]},
                        {"role": "user", "content": retry_message},
                    ],
                    temperature=context.temperature,
                    max_tokens=context.max_tokens,
                )
                response_text, metadata = await self._cli_agent(retry_context)
            else:
                response_text, metadata = await self._cli_agent(context)

            all_responses.append(response_text)

            try:
                output = agent.parse_response(response_text)
                return AgentResult(
                    output=output,
                    raw_response=response_text,
                    model=metadata["model"],
                    usage=metadata["usage"],
                )
            except Exception as e:
                last_error = str(e)
                last_error_type = classify_parse_error(last_error, response_text)
                self._log(f"Parse attempt {attempt + 1} failed: {last_error_type.value} - {last_error[:100]}")

                # Fast-fail on permanent errors if we're not on last retry
                if attempt < self._max_retries - 1:
                    if last_error_type in (ParseErrorType.PERMANENT_SCHEMA, ParseErrorType.PERMANENT_MISSING, ParseErrorType.TIMEOUT):
                        self._log(f"Permanent error detected ({last_error_type.value}), skipping to coercion")
                        # Jump to coercion logic if enabled
                        if self._enable_coercion:
                            attempt = self._max_retries - 1  # Force to last attempt
                        else:
                            raise ParseError(
                                f"Permanent parse error on attempt {attempt + 1}: {last_error}",
                                response_text,
                                last_error_type
                            )

                # Last retry failed - try AI coercion if enabled
                if attempt == self._max_retries - 1:
                    if self._enable_coercion:
                        # Try to coerce the response using another AI call
                        try:
                            # Get expected format from the agent's docstring or system prompt
                            expected_format = getattr(agent, '_expected_format', None)
                            if not expected_format:
                                expected_format = context.system_prompt[:1000] if context.system_prompt else "JSON object"

                            coerced, confidence = await self._coerce_response(
                                malformed_response=response_text,
                                expected_format=expected_format,
                                error_message=last_error,
                            )

                            if confidence >= self._coercion_confidence:
                                self._log(f"Coercion succeeded with confidence {confidence:.2f}")
                                try:
                                    output = agent.parse_response(coerced)
                                    return AgentResult(
                                        output=output,
                                        raw_response=coerced,
                                        model=metadata["model"] + "+coerced",
                                        usage=metadata["usage"],
                                    )
                                except Exception as coerce_error:
                                    self._log(f"Coerced response still failed to parse: {coerce_error}")
                            else:
                                self._log(f"Coercion confidence {confidence:.2f} below threshold {self._coercion_confidence}")
                        except Exception as coercion_err:
                            self._log(f"Coercion failed: {coercion_err}")

                    raise ParseError(
                        f"Failed to parse response after {self._max_retries} attempts: {last_error}",
                        response_text,
                        last_error_type
                    )

        # Should not reach here
        raise ParseError("Unexpected: no response generated", "", ParseErrorType.UNKNOWN)
