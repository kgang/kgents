"""
LLM backing for Tiny Atelier using ClaudeCLIRuntime.

Uses `claude -p` for authenticated execution without needing API keys.
Leverages the CLI's built-in OAuth authentication.

This module provides:
- ArtisanLLMAgent: LLMAgent implementation for artisan work
- get_runtime(): Singleton runtime for artisan execution
- artisan_completion(): Simple interface for artisan LLM calls
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from typing import Any

from runtime.base import AgentContext, AgentResult, LLMAgent
from runtime.cli import ClaudeCLIRuntime

# =============================================================================
# Artisan LLM Agent
# =============================================================================


@dataclass
class ArtisanRequest:
    """Input for artisan LLM call."""

    prompt: str
    artisan_name: str
    artisan_personality: str


@dataclass
class ArtisanResponse:
    """Parsed output from artisan LLM call."""

    interpretation: str
    considerations: list[str]
    content: str
    form: str


class ArtisanLLMAgent(LLMAgent[ArtisanRequest, ArtisanResponse]):
    """
    LLM agent for artisan work.

    Uses ClaudeCLIRuntime for execution, leveraging CLI OAuth auth.
    """

    name = "ArtisanAgent"

    # Expected format hint for coercion
    _expected_format = """
{
  "interpretation": "how you understood this request",
  "considerations": ["what you thought about"],
  "content": "the piece itself",
  "form": "what form it took (e.g., haiku, letter, map)"
}
"""

    def build_prompt(self, input: ArtisanRequest) -> AgentContext:
        """Build prompt context for artisan work."""
        system_prompt = f"""{input.artisan_personality}

You are {input.artisan_name}. Create something beautiful in response to the request.

IMPORTANT: Respond with valid JSON only, no markdown code blocks:
{{
  "interpretation": "how you understood this request",
  "considerations": ["what you thought about"],
  "content": "the piece itself",
  "form": "what form it took (e.g., haiku, letter, map)"
}}
"""

        return AgentContext(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": input.prompt}],
            temperature=0.8,  # Creative temperature
            max_tokens=2048,
        )

    def parse_response(self, response: str) -> ArtisanResponse:
        """Parse LLM response to ArtisanResponse."""
        # Try to extract JSON from the response
        text = response.strip()

        # Handle markdown code blocks
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                text = text[start:end].strip()

        # Try to find JSON object
        if "{" in text:
            start = text.find("{")
            # Find matching closing brace
            depth = 0
            end = start
            for i, char in enumerate(text[start:], start):
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            text = text[start:end]

        try:
            data = json.loads(text)
            return ArtisanResponse(
                interpretation=data.get("interpretation", ""),
                considerations=data.get("considerations", []),
                content=data.get("content", text),
                form=data.get("form", "reflection"),
            )
        except json.JSONDecodeError:
            # Fallback: treat entire response as content
            return ArtisanResponse(
                interpretation="Created from request",
                considerations=[],
                content=response,
                form="reflection",
            )

    async def invoke(self, input: ArtisanRequest) -> ArtisanResponse:
        """Execute using the global runtime."""
        runtime = get_runtime()
        result = await runtime.execute(self, input)
        return result.output


# =============================================================================
# Runtime Singleton
# =============================================================================

_runtime: ClaudeCLIRuntime | None = None


def get_runtime() -> ClaudeCLIRuntime:
    """
    Get the singleton ClaudeCLIRuntime.

    Lazily initializes the runtime on first call.
    """
    global _runtime

    if _runtime is None:
        # Check if claude CLI is available
        if not shutil.which("claude"):
            raise RuntimeError(
                "Claude CLI not found. Install with: npm install -g @anthropic-ai/claude-code"
            )

        _runtime = ClaudeCLIRuntime(
            timeout=120.0,
            max_retries=2,
            verbose=False,
            enable_coercion=True,
        )

    return _runtime


def reset_runtime() -> None:
    """Reset the singleton runtime (for testing)."""
    global _runtime
    _runtime = None


# =============================================================================
# Simple Interface
# =============================================================================


async def artisan_completion(
    prompt: str,
    artisan_name: str,
    artisan_personality: str,
) -> ArtisanResponse:
    """
    Simple interface for artisan LLM completion.

    Uses ClaudeCLIRuntime under the hood.

    Args:
        prompt: The user's request
        artisan_name: Name of the artisan
        artisan_personality: Personality description

    Returns:
        ArtisanResponse with interpretation, considerations, content, and form
    """
    agent = ArtisanLLMAgent()
    request = ArtisanRequest(
        prompt=prompt,
        artisan_name=artisan_name,
        artisan_personality=artisan_personality,
    )

    return await agent.invoke(request)


# =============================================================================
# Raw Completion (for custom prompts)
# =============================================================================


async def raw_completion(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> tuple[str, dict[str, Any]]:
    """
    Raw LLM completion via ClaudeCLIRuntime.

    Returns (response_text, metadata).
    """
    runtime = get_runtime()
    context = AgentContext(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return await runtime.raw_completion(context)


__all__ = [
    "ArtisanLLMAgent",
    "ArtisanRequest",
    "ArtisanResponse",
    "get_runtime",
    "reset_runtime",
    "artisan_completion",
    "raw_completion",
]
