"""
OpenRouter Runtime - Execute agents via OpenRouter API.

OpenRouter provides access to multiple LLM providers through a unified API.
"""

import os
from typing import Any, TypeVar, get_args, get_origin
from dataclasses import dataclass

from .base import Runtime, LLMAgent, AgentContext, AgentResult, with_retry, TransientError, PermanentError

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class APIClient:
    """
    Morphism: AgentContext → (str, dict[str, Any])

    Pure API client that encapsulates HTTP interaction with OpenRouter.
    Composable, testable, and reusable across different runtimes.
    """

    api_key: str
    model: str
    base_url: str = "https://openrouter.ai/api/v1"
    site_url: str | None = None
    site_name: str | None = None
    timeout: float = 120.0
    max_retries: int = 3
    backoff_base: float = 2.0

    _client: Any = None
    
    def _ensure_client(self):
        """Lazy-initialize the HTTP client."""
        if self._client is None:
            try:
                import httpx
                self._client = httpx.AsyncClient(
                    base_url=self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        **({"HTTP-Referer": self.site_url} if self.site_url else {}),
                        **({"X-Title": self.site_name} if self.site_name else {}),
                    },
                    timeout=self.timeout,
                )
            except ImportError:
                raise ImportError(
                    "httpx package required. Install with: pip install httpx"
                )
        return self._client
    
    def _is_transient_error(self, error: Exception) -> bool:
        """Classify HTTP errors as transient or permanent."""
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Already classified
        if isinstance(error, TransientError):
            return True
        if isinstance(error, PermanentError):
            return False

        # HTTP status code errors
        if "429" in error_str or "rate limit" in error_str:
            return True
        if "500" in error_str or "502" in error_str or "503" in error_str or "504" in error_str:
            return True
        if "timeout" in error_str:
            return True
        if "connection" in error_str or "network" in error_str:
            return True

        # Permanent HTTP errors
        if any(code in error_str for code in ["400", "401", "403", "404"]):
            return False

        # Default to transient
        return True

    async def __call__(self, context: AgentContext) -> tuple[str, dict[str, Any]]:
        """
        Execute the morphism: AgentContext → (response_text, metadata).

        This makes APIClient a callable morphism that can be composed.
        Uses Fix pattern retry with exponential backoff.
        """
        async def _attempt() -> tuple[str, dict[str, Any]]:
            """Single API call attempt."""
            client = self._ensure_client()

            messages = [
                {"role": "system", "content": context.system_prompt},
                *context.messages,
            ]

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": context.max_tokens,
                "temperature": context.temperature,
            }

            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})

            metadata = {
                "model": data.get("model", self.model),
                "usage": {
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0),
                },
                "finish_reason": data["choices"][0].get("finish_reason"),
            }

            return text, metadata

        # Use Fix pattern retry
        result, _ = await with_retry(
            _attempt,
            max_attempts=self.max_retries,
            backoff_base=self.backoff_base,
            is_transient=self._is_transient_error,
        )

        return result
    
    async def close(self):
        """Release resources."""
        if self._client:
            await self._client.aclose()
            self._client = None


class OpenRouterRuntime(Runtime):
    """
    Runtime for executing LLM agents via OpenRouter.

    Usage:
        runtime = OpenRouterRuntime(model="anthropic/claude-3.5-sonnet")
        result = await runtime.execute(my_agent, input_data)
    """

    DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        site_url: str | None = None,
        site_name: str | None = None,
        validate_types: bool = True,
        max_retries: int = 3,
        backoff_base: float = 2.0,
    ):
        """
        Initialize OpenRouter runtime.

        Args:
            api_key: OpenRouter API key. Defaults to OPENROUTER_API_KEY env var.
            model: Model to use. Defaults to anthropic/claude-3.5-sonnet.
            site_url: Your site URL for rankings (optional).
            site_name: Your site name for rankings (optional).
            validate_types: If True, validate parse_response output types at runtime.
            max_retries: Maximum retry attempts on transient errors (default: 3).
            backoff_base: Base for exponential backoff in seconds (default: 2.0).
        """
        self._validate_types = validate_types

        # Initialize composable API client morphism
        self._client = APIClient(
            api_key=api_key or os.environ.get("OPENROUTER_API_KEY"),
            model=model or self.DEFAULT_MODEL,
            site_url=site_url,
            site_name=site_name,
            max_retries=max_retries,
            backoff_base=backoff_base,
        )

    def _validate_output_type(self, output: Any, agent: LLMAgent[A, B]) -> None:
        """
        Validate that parse_response returned the expected output type.
        
        Performs basic runtime type checking to catch mismatches early.
        Only validates simple types (str, int, float, dict, list, bool, None).
        For complex types or generics, validation is best-effort.
        
        Args:
            output: The parsed output from parse_response
            agent: The agent that produced the output
            
        Raises:
            TypeError: If output type doesn't match agent's type annotation
        """
        if not self._validate_types:
            return
            
        # Try to get the output type from the agent's class annotations
        agent_class = type(agent)
        
        # Look for __orig_bases__ which contains Generic[A, B] info
        if not hasattr(agent_class, "__orig_bases__"):
            return  # Can't validate without type info
            
        for base in agent_class.__orig_bases__:
            origin = get_origin(base)
            if origin is None:
                continue
                
            # Check if this is LLMAgent[A, B] or Agent[A, B]
            base_name = getattr(origin, "__name__", "")
            if base_name in ("LLMAgent", "Agent"):
                args = get_args(base)
                if len(args) >= 2:
                    expected_type = args[1]  # B is the second type parameter
                    
                    # Validate against expected type
                    if not self._check_type_match(output, expected_type):
                        raise TypeError(
                            f"Agent {agent.name} parse_response returned {type(output).__name__}, "
                            f"but expected {expected_type}"
                        )
                    return

    def _check_type_match(self, value: Any, expected_type: Any) -> bool:
        """
        Check if value matches expected type.
        
        Handles basic types, type unions (|), and simple generic types.
        Returns True for TypeVars or complex types we can't validate.
        """
        # Handle TypeVar - we can't validate these at runtime
        if isinstance(expected_type, TypeVar):
            return True
            
        # Handle None type
        if expected_type is type(None):
            return value is None
            
        # Handle Union types (int | str)
        origin = get_origin(expected_type)
        if origin is not None:
            # For Union types, check if value matches any of the types
            if hasattr(origin, "__name__") and origin.__name__ == "UnionType":
                return any(self._check_type_match(value, t) for t in get_args(expected_type))
            
            # For generic types like list[str], dict[str, int]
            # Just check the outer type (list, dict) for now
            if origin in (list, dict, set, tuple):
                return isinstance(value, origin)
                
            # For other generic types, be permissive
            return True
            
        # Handle basic types
        if expected_type in (str, int, float, bool, dict, list, tuple, set):
            return isinstance(value, expected_type)
            
        # For other types, assume valid (be permissive for complex types)
        return True

    async def raw_completion(
        self,
        context: AgentContext,
    ) -> tuple[str, dict[str, Any]]:
        """Execute raw completion via OpenRouter API."""
        return await self._client(context)

    async def execute(
        self,
        agent: LLMAgent[A, B],
        input: A,
    ) -> AgentResult[B]:
        """Execute an LLM agent with OpenRouter."""
        context = agent.build_prompt(input)
        response_text, metadata = await self.raw_completion(context)

        output = agent.parse_response(response_text)
        
        # Validate output type matches agent's declared type B
        self._validate_output_type(output, agent)

        return AgentResult(
            output=output,
            raw_response=response_text,
            model=metadata["model"],
            usage=metadata["usage"],
        )

    async def close(self):
        """Close the HTTP client."""
        await self._client.close()
