"""
AGENTESE REPL Fuzzy Matching Engine.

Wave 3 Intelligence: Typo-tolerant path resolution for the AGENTESE REPL.

Design Principles:
    - Graceful Degradation: Works without rapidfuzz (falls back to simpler matching)
    - Configurable: Threshold can be adjusted per use case
    - Composable: Works with Logos registry and CLI commands

Usage:
    matcher = FuzzyMatcher(threshold=80)
    suggestions = matcher.match("sle", ["self", "world", "concept"])
    # -> [("self", 86)]

    best = matcher.suggest("sle", ["self", "world", "concept"])
    # -> "self"
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

# Graceful import - rapidfuzz is optional
try:
    from rapidfuzz import fuzz, process  # type: ignore[import-not-found]

    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    fuzz = None
    process = None

if TYPE_CHECKING:
    pass


@dataclass
class FuzzyMatcher:
    """
    Typo-tolerant path matching with configurable threshold.

    Uses rapidfuzz for fast fuzzy matching with Levenshtein distance.
    Falls back to simple substring matching if rapidfuzz unavailable.

    Threshold guide:
        100: Exact match only
        90+: Very similar (1-char typos)
        80+: Similar (2-char typos, transpositions)
        70+: Loosely similar (multiple edits)
        <70: May produce false positives
    """

    threshold: int = 80
    limit: int = 5

    def match(self, query: str, candidates: list[str]) -> list[tuple[str, int]]:
        """
        Return matches above threshold with confidence scores.

        Args:
            query: The user's input (possibly misspelled)
            candidates: Valid options to match against

        Returns:
            List of (candidate, score) tuples, sorted by score descending
        """
        if not query or not candidates:
            return []

        if RAPIDFUZZ_AVAILABLE and process is not None:
            # Use rapidfuzz for fast fuzzy matching
            matches = process.extract(
                query,
                candidates,
                scorer=fuzz.ratio,
                score_cutoff=self.threshold,
                limit=self.limit,
            )
            # process.extract returns list of (match, score, index)
            return [(m[0], int(m[1])) for m in matches]
        else:
            # Fallback: simple substring/prefix matching
            return self._fallback_match(query, candidates)

    def suggest(self, query: str, candidates: list[str]) -> str | None:
        """
        Return the best suggestion, or None if no good match.

        Args:
            query: The user's input
            candidates: Valid options to match against

        Returns:
            Best matching candidate, or None if no match above threshold
        """
        matches = self.match(query, candidates)
        if matches:
            return matches[0][0]
        return None

    def did_you_mean(
        self, query: str, candidates: list[str], max_suggestions: int = 3
    ) -> str | None:
        """
        Generate a "Did you mean: ..." suggestion string.

        Args:
            query: The user's input
            candidates: Valid options
            max_suggestions: Maximum suggestions to show

        Returns:
            Formatted suggestion string, or None if no matches
        """
        matches = self.match(query, candidates)
        if not matches:
            return None

        suggestions = [m[0] for m in matches[:max_suggestions]]

        if len(suggestions) == 1:
            return f"Did you mean: {suggestions[0]}?"
        else:
            return f"Did you mean: {', '.join(suggestions)}?"

    def _fallback_match(
        self, query: str, candidates: list[str]
    ) -> list[tuple[str, int]]:
        """
        Simple fallback matching when rapidfuzz unavailable.

        Uses prefix matching and substring matching with simple scoring.
        """
        query_lower = query.lower()
        results: list[tuple[str, int]] = []

        for candidate in candidates:
            cand_lower = candidate.lower()
            score = 0

            # Exact match
            if query_lower == cand_lower:
                score = 100
            # Prefix match
            elif cand_lower.startswith(query_lower):
                score = 90 - (len(candidate) - len(query))
            # Substring match
            elif query_lower in cand_lower:
                score = 70
            # Simple character overlap
            else:
                common = sum(1 for c in query_lower if c in cand_lower)
                if common > 0:
                    score = int(60 * common / len(query_lower))

            if score >= self.threshold:
                results.append((candidate, score))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[: self.limit]


@dataclass
class LLMSuggester:
    """
    Semantic suggestion engine using lightweight LLM.

    Only called when:
    - Exact match fails
    - Fuzzy match fails
    - Entropy budget allows (costs entropy per suggestion)

    Uses Haiku for speed/cost optimization.
    """

    entropy_cost: float = 0.01
    _client: object | None = None

    async def suggest(
        self,
        query: str,
        context: str,
        valid_options: list[str],
        entropy_budget: float,
    ) -> str | None:
        """
        Generate semantic suggestion via LLM.

        Args:
            query: The user's input (misspelled or unclear)
            context: Current AGENTESE context (e.g., "self", "world")
            valid_options: List of valid commands/paths
            entropy_budget: Remaining entropy budget

        Returns:
            Suggested command, or None if budget insufficient or no suggestion
        """
        if entropy_budget < self.entropy_cost:
            return None

        if not valid_options:
            return None

        # Build a concise prompt
        options_str = ", ".join(valid_options[:20])  # Limit to 20 options
        prompt = (
            f"User typed '{query}' in AGENTESE REPL context '{context}'. "
            f"Valid options: {options_str}. "
            f"What did they most likely mean? Reply with ONE word only, "
            f"the exact option from the list, or 'none' if no match."
        )

        try:
            response = await self._call_llm(prompt)
            suggestion = response.strip().lower()

            # Validate response is in our options
            for opt in valid_options:
                if opt.lower() == suggestion:
                    return opt

            return None
        except Exception:
            return None

    async def _call_llm(self, prompt: str) -> str:
        """
        Call the LLM (Haiku) for a suggestion.

        Override this method to inject a different LLM client.
        """
        try:
            from anthropic import AsyncAnthropic

            if self._client is None:
                self._client = AsyncAnthropic()

            client = self._client
            response = await client.messages.create(  # type: ignore[attr-defined]
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            text: str = response.content[0].text
            return text
        except ImportError:
            return ""
        except Exception:
            return ""


# === Factory Functions ===


def create_fuzzy_matcher(threshold: int = 80, limit: int = 5) -> FuzzyMatcher:
    """Create a FuzzyMatcher with specified settings."""
    return FuzzyMatcher(threshold=threshold, limit=limit)


def create_llm_suggester(entropy_cost: float = 0.01) -> LLMSuggester:
    """Create an LLMSuggester with specified entropy cost."""
    return LLMSuggester(entropy_cost=entropy_cost)


# === Utility Functions ===


def is_fuzzy_available() -> bool:
    """Check if rapidfuzz is available for high-quality fuzzy matching."""
    return RAPIDFUZZ_AVAILABLE
