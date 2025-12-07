# Runtime Implementation Plan

## Goal

Add `runtime/` module to `impl/claude-openrouter` that provides LLM-backed execution for kgents agents, enabling zen-agents to use real LLM reasoning for:
- Judge (principled evaluation beyond structural checks)
- Sublate (semantic synthesis of tensions)
- Contradict (semantic contradiction detection)
- H-gents (Hegel, Jung, Lacan - require LLM for dialectic/introspection)
- Creativity Coach, K-gent (require LLM for generation)

## Authentication Strategy

**Primary: Claude Max via OAuth** (no API keys required)

The runtime supports four authentication methods in order of preference:

1. **Claude CLI Backend** (Recommended for Max subscribers)
   - Uses the `claude` CLI binary which is already authenticated via `claude login`
   - Runs `claude --print` for single-turn completions
   - No API keys needed - uses Max subscription credits
   - Requires: `claude login` completed once

2. **OAuth Token** (For programmatic/container use)
   - Use `claude setup-token` to generate a long-lived OAuth token
   - Set `CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...`
   - Works in containers/CI where interactive login isn't possible

3. **OpenRouter via y-router** (Multi-model flexibility)
   - Set `OPENROUTER_API_KEY=sk-or-...`
   - Routes through local y-router (`http://localhost:8787` via Docker)
   - Start y-router: `cd ~/git/y-router && docker-compose up -d`
   - Supports Claude models + other providers (GPT-4, Gemini, Kimi, etc.)
   - Pay-per-use via OpenRouter credits

4. **Direct Anthropic API Key** (Traditional, pay-per-use)
   - Set `ANTHROPIC_API_KEY=sk-ant-...` (from Anthropic Console)
   - Billed separately from Max subscription
   - Fallback for users without Max

## Architecture

```
impl/claude-openrouter/
├── runtime/
│   ├── __init__.py           # Public API
│   ├── client.py             # LLM client abstraction (3 backends)
│   ├── config.py             # Configuration (auth method, models)
│   ├── messages.py           # Message protocol for agent communication
│   ├── llm_agents/           # LLM-backed agent implementations
│   │   ├── __init__.py
│   │   ├── judge.py          # LLMJudge
│   │   ├── sublate.py        # LLMSublate
│   │   ├── contradict.py     # LLMContradict
│   │   └── ground.py         # LLMGround (optional, for dynamic persona)
│   ├── usage.py              # Usage tracking (tokens, not cost for Max)
│   └── cache.py              # Response caching
├── bootstrap/                # Existing (unchanged)
└── agents/                   # Existing (unchanged)
```

## Components

### 1. LLM Client (`runtime/client.py`)

Abstract interface with three backends:

```python
class LLMClient(Protocol):
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system: str | None = None,
    ) -> CompletionResult

class ClaudeCLIClient(LLMClient):
    """
    Uses 'claude' CLI binary for completions.
    Requires prior 'claude login' authentication.
    Best for Max subscribers - no API keys needed.
    """
    async def complete(self, messages, **kwargs):
        # Shells out to: claude --print --model {model} "{prompt}"
        # Uses existing OAuth session from claude login

class OAuthTokenClient(LLMClient):
    """
    Direct API calls using OAuth token from 'claude setup-token'.
    Set CLAUDE_CODE_OAUTH_TOKEN environment variable.
    For containers/CI where interactive login isn't possible.
    """

class OpenRouterClient(LLMClient):
    """
    OpenRouter API via local y-router proxy (Docker).
    Set OPENROUTER_API_KEY environment variable.
    Start y-router: cd ~/git/y-router && docker-compose up -d
    Supports multiple providers (Claude, GPT-4, Gemini, Kimi, etc.)
    """
    DEFAULT_YROUTER_URL = "http://localhost:8787"  # Local Docker

    async def complete(self, messages, model=None, **kwargs):
        # y-router accepts Anthropic format at /v1/messages
        # Model format: "claude-sonnet-4-20250514" or "openai/gpt-4o"

class AnthropicAPIClient(LLMClient):
    """
    Traditional API key authentication.
    Set ANTHROPIC_API_KEY environment variable.
    Fallback for users without Max subscription.
    """
```

### 2. Configuration (`runtime/config.py`)

```python
class AuthMethod(Enum):
    CLI = "cli"             # Use claude CLI (requires claude login)
    OAUTH = "oauth"         # Use CLAUDE_CODE_OAUTH_TOKEN
    OPENROUTER = "openrouter"  # Use OPENROUTER_API_KEY via y-router
    API_KEY = "api_key"     # Use ANTHROPIC_API_KEY

@dataclass
class RuntimeConfig:
    # Authentication (auto-detected in order: CLI > OAuth > OpenRouter > API_KEY)
    auth_method: AuthMethod | None = None  # None = auto-detect

    # Model defaults
    default_model: str = "claude-sonnet-4-20250514"
    # For OpenRouter, prefix with provider: "anthropic/claude-sonnet-4"

    # y-router configuration (for OpenRouter via local Docker)
    yrouter_base_url: str = "http://localhost:8787"

    # Token limits (for rate limiting)
    max_tokens_per_request: int = 4096
    max_tokens_per_minute: int | None = None  # Rate limit

    # Caching
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600

def load_config() -> RuntimeConfig:
    """Load from environment and/or config file"""

def detect_auth_method() -> AuthMethod:
    """
    Auto-detect available authentication:
    1. Check if 'claude' CLI is logged in (preferred for Max)
    2. Check for CLAUDE_CODE_OAUTH_TOKEN
    3. Check for OPENROUTER_API_KEY (uses y-router)
    4. Check for ANTHROPIC_API_KEY
    5. Raise if none available
    """
```

### 3. Message Protocol (`runtime/messages.py`)

Structured messages for agent-to-LLM communication:

```python
@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str

@dataclass
class CompletionResult:
    content: str
    model: str
    usage: TokenUsage
    cached: bool = False

@dataclass
class TokenUsage:
    input_tokens: int
    output_tokens: int
    cost_usd: float  # Computed from model pricing
```

### 4. LLM-Backed Agents (`runtime/llm_agents/`)

#### LLMJudge

Replaces structural checks with principled LLM evaluation:

```python
class LLMJudge(Judge):
    """LLM-backed Judge with principled evaluation"""

    async def _check_principle(self, principle: Principle, subject: Any) -> Verdict:
        prompt = self._build_principle_prompt(principle, subject)
        result = await self._client.complete([
            Message("system", JUDGE_SYSTEM_PROMPT),
            Message("user", prompt),
        ])
        return self._parse_verdict(result.content)
```

System prompt embodies the 6 principles as evaluation criteria.

#### LLMSublate

Semantic synthesis instead of heuristic resolution:

```python
class LLMSublate(Sublate):
    """LLM-backed synthesis for dialectic resolution"""

    async def invoke(self, tension: Tension) -> SynthesisResult:
        prompt = self._build_synthesis_prompt(tension)
        result = await self._client.complete([
            Message("system", SUBLATE_SYSTEM_PROMPT),
            Message("user", prompt),
        ])
        return self._parse_synthesis(result.content)
```

#### LLMContradict

Semantic contradiction detection:

```python
class LLMContradict(Contradict):
    """LLM-backed contradiction detection"""

    async def invoke(self, input: ContradictInput) -> Tension | None:
        prompt = self._build_contradiction_prompt(input.thesis, input.antithesis)
        result = await self._client.complete([
            Message("system", CONTRADICT_SYSTEM_PROMPT),
            Message("user", prompt),
        ])
        return self._parse_tension(result.content)
```

### 5. Usage Tracking (`runtime/usage.py`)

```python
@dataclass
class UsageStats:
    input_tokens: int = 0
    output_tokens: int = 0
    requests: int = 0
    cache_hits: int = 0

class UsageTracker:
    """Track token usage (informational, not billing for Max subscribers)"""
    def track(self, usage: TokenUsage) -> None
    def get_session_stats(self) -> UsageStats
    def reset(self) -> None
```

### 6. Caching (`runtime/cache.py`)

Simple disk-based cache with TTL:

```python
class ResponseCache:
    def get(self, key: str) -> CompletionResult | None
    def set(self, key: str, result: CompletionResult) -> None
    def _make_key(self, messages: list[Message], model: str) -> str
```

## Integration with zen-agents

zen-agents already imports from `bootstrap`. The runtime adds **optional** LLM backing:

```python
# zen-agents can use either:

# 1. Heuristic (default, no API key needed)
from bootstrap import judge_agent
verdict = await judge_agent.invoke(...)

# 2. LLM-backed (when runtime configured)
from bootstrap.runtime import get_llm_judge
llm_judge = get_llm_judge()  # Returns LLMJudge if configured, else judge_agent
verdict = await llm_judge.invoke(...)
```

The runtime provides a `get_*` factory pattern that returns LLM-backed agents when configured, falling back to heuristic versions.

## Implementation Order

1. **`runtime/config.py`** - Configuration and environment loading
2. **`runtime/messages.py`** - Message types and token usage
3. **`runtime/client.py`** - AnthropicClient (start simple, add OpenRouter later)
4. **`runtime/cost.py`** - Cost tracking
5. **`runtime/cache.py`** - Response caching
6. **`runtime/llm_agents/judge.py`** - LLMJudge (most impactful)
7. **`runtime/llm_agents/sublate.py`** - LLMSublate
8. **`runtime/llm_agents/contradict.py`** - LLMContradict
9. **`runtime/__init__.py`** - Public API with factory functions
10. **Tests** - Unit tests for each component
11. **Update `pyproject.toml`** - Add `anthropic` dependency

## Dependencies

```toml
dependencies = [
    "httpx>=0.27.0",  # For OAuth token client
]

[project.optional-dependencies]
anthropic = ["anthropic>=0.40.0"]  # Only needed for API key auth
```

## Authentication Setup

### For Claude Max Subscribers (Recommended)

```bash
# One-time setup - authenticate via browser
claude login

# Verify authentication
claude --version  # Should show logged-in status

# That's it! The runtime auto-detects CLI auth
```

### For Container/CI Use

```bash
# Generate long-lived OAuth token (one-time, on host machine)
claude setup-token

# Set in container environment
export CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
```

### For OpenRouter Users (Multi-Model)

```bash
# 1. Start local y-router (Docker)
cd ~/git/y-router && docker-compose up -d

# 2. Get API key from openrouter.ai
export OPENROUTER_API_KEY=sk-or-...

# Routes through local y-router at http://localhost:8787
# Supports: claude-*, openai/gpt-*, google/gemini-*, moonshotai/kimi-*, etc.
```

### For Direct API Key Users (Fallback)

```bash
# From Anthropic Console (separate billing)
export ANTHROPIC_API_KEY=sk-ant-...
```

## Environment Variables

```bash
# Authentication (auto-detected in priority order):
# 1. CLI auth (claude login)
# 2. CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...
# 3. OPENROUTER_API_KEY=sk-or-...
# 4. ANTHROPIC_API_KEY=sk-ant-...

# Optional configuration:
KGENTS_MODEL=claude-sonnet-4-20250514     # Default model
KGENTS_AUTH_METHOD=cli|oauth|openrouter|api_key  # Force auth method
KGENTS_CACHE_DIR=~/.cache/kgents          # Cache location
KGENTS_YROUTER_URL=http://localhost:8787  # y-router URL (default: local Docker)
```

## Future: Human UI Integration

The runtime enables future UI features:
- **Agent chat** - Stream LLM responses to UI
- **Usage dashboard** - Show token usage stats
- **Principle scores** - Visualize Judge evaluations
- **Dialectic view** - Show thesis/antithesis/synthesis flow

The message protocol is designed to support real-time streaming:

```python
async def complete_stream(
    self,
    messages: list[Message],
    **kwargs
) -> AsyncIterator[str]:
    """Yield tokens as they arrive"""
```

## Success Criteria

1. `LLMJudge` evaluates agents against principles using LLM reasoning
2. `LLMSublate` produces meaningful synthesis from tensions
3. `LLMContradict` detects semantic contradictions
4. Claude CLI auth works seamlessly for Max subscribers (no API keys)
5. OAuth token auth works for containers/CI
6. OpenRouter via y-router provides multi-model flexibility
7. Caching reduces redundant LLM calls
8. zen-agents can opt-in to LLM backing without code changes
9. Fallback to direct API key auth for non-Max users
