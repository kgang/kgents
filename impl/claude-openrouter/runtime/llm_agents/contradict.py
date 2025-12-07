"""
LLMContradict - LLM-backed Contradict Agent

Semantic contradiction detection instead of structural comparison.
Detects subtle tensions that heuristics would miss.
"""

import json
import re
from typing import Any

from bootstrap.contradict import Contradict, ContradictInput
from bootstrap.types import Tension, TensionMode

from ..client import LLMClient, get_client
from ..messages import Message
from ..cache import ResponseCache, get_cache
from ..usage import UsageTracker, get_tracker


CONTRADICT_SYSTEM_PROMPT = """You are the Contradict agent for kgents, detecting tensions and contradictions.

Given two items (thesis and antithesis), determine if they are in tension.

Tension modes:
- LOGICAL: Direct contradiction (A and not-A)
- PRAGMATIC: Conflicting recommendations or actions
- AXIOLOGICAL: Opposing values or goals
- TEMPORAL: Position changed over time (past vs present)

Respond with a JSON object:

If tension exists:
{
    "tension_found": true,
    "mode": "logical" | "pragmatic" | "axiological" | "temporal",
    "description": "brief explanation of the tension"
}

If no tension:
{
    "tension_found": false,
    "reason": "why these are compatible"
}

Be precise. Not every difference is a tension.
True tension means they cannot both be held without resolution."""


def _serialize_item(item: Any) -> str:
    """Convert an item to string representation"""
    if isinstance(item, str):
        return item

    if hasattr(item, '__dict__'):
        return f"{type(item).__name__}: {json.dumps(item.__dict__, default=str)}"

    return str(item)


class LLMContradict(Contradict):
    """LLM-backed contradiction detection"""

    def __init__(
        self,
        client: LLMClient | None = None,
        cache: ResponseCache | None = None,
        tracker: UsageTracker | None = None,
    ):
        self._client = client or get_client()
        self._cache = cache or get_cache()
        self._tracker = tracker or get_tracker()

    async def invoke(self, input: ContradictInput) -> Tension | None:
        """Detect contradiction using LLM reasoning"""
        thesis_str = _serialize_item(input.thesis)
        antithesis_str = _serialize_item(input.antithesis)

        # Quick check: identical items can't contradict
        if thesis_str == antithesis_str:
            return None

        mode_hint = ""
        if input.mode:
            mode_hint = f"\nHint: Check specifically for {input.mode.value} tension."

        prompt = f"""Analyze these two items for tension or contradiction.

Thesis:
{thesis_str}

Antithesis:
{antithesis_str}
{mode_hint}

Determine if there is a genuine tension between them."""

        messages = [Message(role="user", content=prompt)]

        # Check cache first
        cached = self._cache.get(messages, self._client._config.default_model, CONTRADICT_SYSTEM_PROMPT)
        if cached:
            self._tracker.track(cached.usage, cached=True)
            return self._parse_tension(cached.content, input)

        # Call LLM
        result = await self._client.complete(
            messages=messages,
            system=CONTRADICT_SYSTEM_PROMPT,
            temperature=0.2,  # Low temperature for consistent detection
            max_tokens=500,
        )

        # Cache and track
        self._cache.set(messages, result.model, result, CONTRADICT_SYSTEM_PROMPT)
        self._tracker.track(result.usage, cached=False)

        return self._parse_tension(result.content, input)

    def _parse_tension(self, content: str, input: ContradictInput) -> Tension | None:
        """Parse LLM response into a Tension or None"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            if not data.get("tension_found", False):
                return None

            # Parse mode
            mode_str = data.get("mode", "logical").lower()
            mode_map = {
                "logical": TensionMode.LOGICAL,
                "pragmatic": TensionMode.PRAGMATIC,
                "axiological": TensionMode.AXIOLOGICAL,
                "temporal": TensionMode.TEMPORAL,
            }
            mode = mode_map.get(mode_str, TensionMode.LOGICAL)

            return Tension(
                mode=mode,
                thesis=input.thesis,
                antithesis=input.antithesis,
                description=data.get("description", "Tension detected by LLM")
            )

        except (json.JSONDecodeError, KeyError):
            # If parsing fails, fall back to heuristic
            return None
