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

from .base import Runtime, LLMAgent, AgentContext, AgentResult

A = TypeVar("A")
B = TypeVar("B")


class ParseError(Exception):
    """Raised when LLM output cannot be parsed."""
    def __init__(self, message: str, raw_response: str):
        super().__init__(message)
        self.raw_response = raw_response


class ClaudeCLIRuntime(Runtime):
    """
    Runtime for executing LLM agents via Claude Code CLI.

    Uses `claude -p` which is already authenticated via OAuth.
    No API key required.

    Usage:
        runtime = ClaudeCLIRuntime()
        result = await runtime.execute(my_agent, input_data)
    """

    def __init__(
        self,
        claude_path: str | None = None,
        timeout: float = 120.0,
        max_retries: int = 3,
    ):
        """
        Initialize Claude CLI runtime.

        Args:
            claude_path: Path to claude CLI. Defaults to finding it in PATH.
            timeout: Timeout in seconds for CLI execution.
            max_retries: Maximum retries on parse failures (Fix pattern).
        """
        self._claude_path = claude_path or shutil.which("claude")
        self._timeout = timeout
        self._max_retries = max_retries

        if not self._claude_path:
            raise RuntimeError(
                "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """Execute raw completion via Claude CLI."""
        # Build the prompt from system + user messages
        prompt_parts = []

        if context.system_prompt:
            prompt_parts.append(context.system_prompt)

        for msg in context.messages:
            if msg["role"] == "user":
                prompt_parts.append(msg["content"])

        full_prompt = "\n\n".join(prompt_parts)

        # Execute claude -p
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

    async def execute(
        self,
        agent: LLMAgent[A, B],
        input: A,
    ) -> AgentResult[B]:
        """
        Execute an LLM agent with Claude CLI.

        Implements Fix pattern: retries on parse failures with feedback.
        """
        context = agent.build_prompt(input)
        last_error = None
        all_responses = []

        for attempt in range(self._max_retries):
            # Add retry context if this is a retry
            if attempt > 0 and last_error:
                retry_context = AgentContext(
                    system_prompt=context.system_prompt,
                    messages=context.messages + [
                        {"role": "assistant", "content": all_responses[-1]},
                        {"role": "user", "content": f"Your response could not be parsed. Error: {last_error}\n\nPlease respond with ONLY valid JSON, no explanatory text before or after."},
                    ],
                    temperature=context.temperature,
                    max_tokens=context.max_tokens,
                )
                response_text, metadata = await self.raw_completion(retry_context)
            else:
                response_text, metadata = await self.raw_completion(context)

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
                if attempt == self._max_retries - 1:
                    raise ParseError(
                        f"Failed to parse response after {self._max_retries} attempts: {last_error}",
                        response_text
                    )

        # Should not reach here
        raise ParseError("Unexpected: no response generated", "")
