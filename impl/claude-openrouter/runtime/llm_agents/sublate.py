"""
LLMSublate - LLM-backed Sublate Agent

Semantic synthesis instead of heuristic resolution.
Performs true Hegelian Aufhebung: preserve, negate, elevate.
"""

import json
import re
from typing import Any

from bootstrap.sublate import Sublate, SublateConfig
from bootstrap.types import (
    Tension,
    TensionMode,
    Synthesis,
    HoldTension,
    SynthesisResult,
)

from ..client import LLMClient, get_client
from ..messages import Message
from ..cache import ResponseCache, get_cache
from ..usage import UsageTracker, get_tracker


SUBLATE_SYSTEM_PROMPT = """You are the Sublate agent for kgents, performing Hegelian synthesis (Aufhebung).

When given a tension (thesis vs antithesis), you must either:

1. SYNTHESIZE: Create a higher-order understanding that:
   - PRESERVES what is valuable from both sides
   - NEGATES what is limited or contradictory
   - ELEVATES to a new level of understanding

2. HOLD: Recognize that the tension should not be resolved yet because:
   - The tension is generative and productive as-is
   - More information is needed
   - Premature resolution would lose something important

Respond with a JSON object:

For synthesis:
{
    "action": "synthesize",
    "preserved": ["what we keep from thesis", "what we keep from antithesis"],
    "negated": ["what we reject from thesis", "what we reject from antithesis"],
    "synthesis": {
        "resolution": "the new understanding",
        "elevated_understanding": "what we now see that we didn't before"
    }
}

For holding:
{
    "action": "hold",
    "reason": "why this tension should be held"
}

Be philosophically rigorous. True synthesis isn't compromise—it's transcendence."""


def _tension_to_prompt(tension: Tension) -> str:
    """Convert a Tension to a prompt for the LLM"""
    mode_descriptions = {
        TensionMode.LOGICAL: "logical contradiction (A and not-A)",
        TensionMode.PRAGMATIC: "pragmatic conflict (different recommendations)",
        TensionMode.AXIOLOGICAL: "value tension (opposing values)",
        TensionMode.TEMPORAL: "temporal evolution (position changed over time)",
    }

    return f"""Tension Mode: {tension.mode.value} ({mode_descriptions.get(tension.mode, '')})

Description: {tension.description}

Thesis:
{tension.thesis}

Antithesis:
{tension.antithesis}

Perform Hegelian synthesis (Aufhebung) or explain why this tension should be held."""


class LLMSublate(Sublate):
    """LLM-backed synthesis for dialectic resolution"""

    def __init__(
        self,
        config: SublateConfig | None = None,
        client: LLMClient | None = None,
        cache: ResponseCache | None = None,
        tracker: UsageTracker | None = None,
    ):
        super().__init__(config)
        self._client = client or get_client()
        self._cache = cache or get_cache()
        self._tracker = tracker or get_tracker()

    async def invoke(self, tension: Tension) -> SynthesisResult:
        """Attempt to sublate the tension using LLM reasoning"""
        prompt = _tension_to_prompt(tension)
        messages = [Message(role="user", content=prompt)]

        # Check cache first
        cached = self._cache.get(messages, self._client._config.default_model, SUBLATE_SYSTEM_PROMPT)
        if cached:
            self._tracker.track(cached.usage, cached=True)
            return self._parse_synthesis(cached.content, tension)

        # Call LLM
        result = await self._client.complete(
            messages=messages,
            system=SUBLATE_SYSTEM_PROMPT,
            temperature=0.5,  # Some creativity for synthesis
            max_tokens=1000,
        )

        # Cache and track
        self._cache.set(messages, result.model, result, SUBLATE_SYSTEM_PROMPT)
        self._tracker.track(result.usage, cached=False)

        return self._parse_synthesis(result.content, tension)

    def _parse_synthesis(self, content: str, tension: Tension) -> SynthesisResult:
        """Parse LLM response into a SynthesisResult"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            action = data.get("action", "synthesize").lower()

            if action == "hold":
                return HoldTension(
                    reason=data.get("reason", "Tension should be held"),
                    tension=tension
                )

            # Synthesize
            preserved = data.get("preserved", [])
            negated = data.get("negated", [])
            synthesis_data = data.get("synthesis", {})

            return Synthesis(
                preserved=tuple(preserved),
                negated=tuple(negated),
                synthesis={
                    "resolution": synthesis_data.get("resolution", "Synthesized understanding"),
                    "elevated_understanding": synthesis_data.get("elevated_understanding", ""),
                    "thesis": tension.thesis,
                    "antithesis": tension.antithesis,
                }
            )

        except (json.JSONDecodeError, KeyError):
            # Fallback to basic synthesis on parse failure
            return Synthesis(
                preserved=(str(tension.thesis), str(tension.antithesis)),
                negated=("Parsing failed",),
                synthesis={
                    "resolution": "Fallback synthesis due to parse error",
                    "elevated_understanding": "",
                    "thesis": tension.thesis,
                    "antithesis": tension.antithesis,
                }
            )
