"""
LLMJudge - LLM-backed Judge Agent

Replaces structural checks with principled LLM evaluation.
Uses the 6 kgents principles as evaluation criteria.
"""

import json
import re
from typing import Any

from bootstrap.judge import Judge, JudgeInput, JudgeOutput
from bootstrap.types import Principle, Verdict, VerdictStatus, PRINCIPLE_QUESTIONS

from ..client import LLMClient, get_client
from ..messages import Message
from ..cache import ResponseCache, get_cache
from ..usage import UsageTracker, get_tracker


JUDGE_SYSTEM_PROMPT = """You are the Judge agent for kgents, a principled agent evaluation system.

Your role is to evaluate subjects against the 6 kgents principles:

1. TASTEFUL: Does this have a clear, justified purpose? Is it aesthetically considered?
2. CURATED: Does this add unique value? Is it intentionally selected rather than arbitrary?
3. ETHICAL: Does this respect human agency and privacy? Does it augment rather than replace judgment?
4. JOY-INDUCING: Would I enjoy interacting with this? Does it have personality?
5. COMPOSABLE: Can this work with other agents? Is it a proper morphism in the agent category?
6. HETERARCHICAL: Can this both lead and follow? Does it avoid fixed hierarchy?

For each evaluation, you must respond with a JSON object:
{
    "status": "accept" | "reject" | "revise",
    "reason": "explanation if rejecting",
    "suggestion": "how to improve if revising"
}

Be rigorous but fair. Accept things that genuinely embody the principle.
Reject only when there's a clear violation.
Suggest revision when improvement is possible and worthwhile."""


def _serialize_subject(subject: Any) -> str:
    """Convert a subject to a string representation for the LLM"""
    if hasattr(subject, 'name') and hasattr(subject, 'purpose'):
        # It's an Agent-like object
        return f"""Agent: {subject.name}
Genus: {getattr(subject, 'genus', 'unknown')}
Purpose: {subject.purpose}
Type: {type(subject).__name__}"""

    if hasattr(subject, '__dict__'):
        return f"""Object: {type(subject).__name__}
Attributes: {json.dumps(subject.__dict__, default=str, indent=2)}"""

    return str(subject)


class LLMJudge(Judge):
    """LLM-backed Judge with principled evaluation"""

    def __init__(
        self,
        client: LLMClient | None = None,
        cache: ResponseCache | None = None,
        tracker: UsageTracker | None = None,
    ):
        self._client = client or get_client()
        self._cache = cache or get_cache()
        self._tracker = tracker or get_tracker()

    async def _check_principle(self, principle: Principle, subject: Any) -> Verdict:
        """Check a single principle using LLM reasoning"""
        subject_str = _serialize_subject(subject)
        question = PRINCIPLE_QUESTIONS[principle]

        prompt = f"""Evaluate this subject against the {principle.value.upper()} principle.

Subject:
{subject_str}

Principle Question: {question}

Respond with a JSON object containing your verdict."""

        messages = [Message(role="user", content=prompt)]

        # Check cache first
        cached = self._cache.get(messages, self._client._config.default_model, JUDGE_SYSTEM_PROMPT)
        if cached:
            self._tracker.track(cached.usage, cached=True)
            return self._parse_verdict(cached.content)

        # Call LLM
        result = await self._client.complete(
            messages=messages,
            system=JUDGE_SYSTEM_PROMPT,
            temperature=0.3,  # Lower temperature for consistent judgments
            max_tokens=500,
        )

        # Cache and track
        self._cache.set(messages, result.model, result, JUDGE_SYSTEM_PROMPT)
        self._tracker.track(result.usage, cached=False)

        return self._parse_verdict(result.content)

    def _parse_verdict(self, content: str) -> Verdict:
        """Parse LLM response into a Verdict"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                data = json.loads(content)

            status = data.get("status", "accept").lower()
            reason = data.get("reason")
            suggestion = data.get("suggestion")

            match status:
                case "reject":
                    return Verdict.reject(reason or "Rejected by LLM Judge")
                case "revise":
                    return Verdict.revise(suggestion or "Needs revision")
                case _:
                    return Verdict.accept()

        except (json.JSONDecodeError, KeyError):
            # If parsing fails, default to accept (fail open)
            return Verdict.accept()
