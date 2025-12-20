"""
Principle Healer: Therapeia prescriptions for principle violations.

The Therapeia stance - healing and restoration.
Given a violation, prescribes the path to restoration.

See: spec/principles/node.md for the heal aspect specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .types import (
    PRINCIPLE_AD_MAPPING,
    PRINCIPLE_NAMES,
    PRINCIPLE_NUMBERS,
    THE_SEVEN_PRINCIPLES,
    HealingPrescription,
    Stance,
)

if TYPE_CHECKING:
    from .loader import PrincipleLoader


@dataclass
class PrincipleHealer:
    """
    Prescribes healing paths for principle violations.

    The healer:
    1. Identifies the violated principle
    2. Loads relevant anti-patterns
    3. Matches context to specific anti-pattern
    4. Finds helpful puppets (isomorphic structures)
    5. Returns step-by-step healing path

    Example:
        healer = PrincipleHealer(loader)
        prescription = await healer.heal(
            violation="composable",
            context="Agent can't be combined with other agents"
        )
        print(prescription.path)  # Step-by-step healing
    """

    loader: "PrincipleLoader"

    def _resolve_principle(self, violation: int | str) -> int:
        """
        Resolve principle from number or name.

        Args:
            violation: Principle number (1-7) or name

        Returns:
            Principle number (1-7)

        Raises:
            ValueError: If principle not found
        """
        if isinstance(violation, int):
            if 1 <= violation <= 7:
                return violation
            raise ValueError(f"Invalid principle number: {violation}")

        # Try to match by name
        name_lower = violation.lower().strip()
        if name_lower in PRINCIPLE_NAMES:
            return PRINCIPLE_NAMES[name_lower]

        # Try partial match
        for name, num in PRINCIPLE_NAMES.items():
            if name_lower in name or name in name_lower:
                return num

        raise ValueError(f"Unknown principle: {violation}")

    async def heal(
        self,
        violation: int | str,
        context: str | None = None,
    ) -> HealingPrescription:
        """
        Diagnose violation and prescribe restoration.

        Args:
            violation: Principle number (1-7) or name
            context: Optional context about what went wrong

        Returns:
            HealingPrescription with path to restoration
        """
        # Resolve principle
        principle_num = self._resolve_principle(violation)
        principle_name = PRINCIPLE_NUMBERS[principle_num]

        # Load anti-patterns for this principle
        anti_patterns = await self.loader.load_anti_patterns(principle_num)

        # Match context to specific anti-pattern
        matched_pattern = None
        if context:
            matched_pattern = self._match_anti_pattern(context, anti_patterns)

        # Load puppets (isomorphic structures for reframing)
        puppets = await self.loader.load_puppets_for_principle(principle_num)

        # Get related ADs
        related_ads = await self.loader.load_related_ads(principle_num)

        # Build healing path
        path = self._build_healing_path(
            principle_num=principle_num,
            principle_name=principle_name,
            matched_pattern=matched_pattern,
            puppets=puppets,
            related_ads=related_ads,
        )

        return HealingPrescription(
            principle=principle_num,
            principle_name=principle_name,
            anti_patterns=anti_patterns,
            matched_pattern=matched_pattern,
            puppets=puppets,
            related_ads=related_ads,
            path=path,
            stance=Stance.THERAPEIA,
        )

    def _match_anti_pattern(
        self,
        context: str,
        anti_patterns: tuple[str, ...],
    ) -> str | None:
        """
        Match context to a specific anti-pattern.

        Args:
            context: Description of what went wrong
            anti_patterns: Available anti-patterns

        Returns:
            Matched anti-pattern or None
        """
        context_lower = context.lower()

        # Score each anti-pattern
        best_match: str | None = None
        best_score = 0

        for pattern in anti_patterns:
            pattern_words = set(pattern.lower().split())
            context_words = set(context_lower.split())

            # Count overlapping words
            overlap = len(pattern_words & context_words)
            if overlap > best_score:
                best_score = overlap
                best_match = pattern

        return best_match if best_score > 0 else None

    def _build_healing_path(
        self,
        principle_num: int,
        principle_name: str,
        matched_pattern: str | None,
        puppets: tuple[str, ...],
        related_ads: tuple[int, ...],
    ) -> tuple[str, ...]:
        """
        Build step-by-step healing path.

        Args:
            principle_num: The violated principle
            principle_name: Name of the principle
            matched_pattern: The matched anti-pattern
            puppets: Available puppet structures
            related_ads: Related AD numbers

        Returns:
            Tuple of healing steps
        """
        steps: list[str] = []

        # Step 1: Identify the anti-pattern
        if matched_pattern:
            steps.append(f"Recognize the anti-pattern: '{matched_pattern}'")
        else:
            steps.append(f"Review the anti-patterns for {principle_name} principle")

        # Step 2: Find a puppet if available
        if puppets:
            steps.append(f"Consider the puppet: {puppets[0]}")
            steps.append("Ask: How would this structure solve the problem?")
        else:
            steps.append(f"Consider: What makes something truly {principle_name.lower()}?")

        # Step 3: Reference ADs
        if related_ads:
            ad_refs = ", ".join(f"AD-{ad:03d}" for ad in related_ads[:2])
            steps.append(f"Study the pattern in {ad_refs}")

        # Step 4: Rebuild
        steps.append("Rebuild in Poiesis stance with the corrected approach")

        # Step 5: Verify
        steps.append("Verify with concept.principles.check")

        return tuple(steps)

    async def diagnose(
        self,
        context: str,
    ) -> tuple[int, str] | None:
        """
        Attempt to diagnose which principle was violated from context.

        Args:
            context: Description of the problem

        Returns:
            Tuple of (principle_number, matched_anti_pattern) or None
        """
        context_lower = context.lower()

        for principle in THE_SEVEN_PRINCIPLES:
            for anti_pattern in principle.anti_patterns:
                pattern_lower = anti_pattern.lower()
                # Check for significant word overlap
                pattern_words = set(pattern_lower.split())
                context_words = set(context_lower.split())

                if len(pattern_words & context_words) >= 2:
                    return (principle.number, anti_pattern)

        return None

    def get_principle_question(self, principle: int | str) -> str:
        """
        Get the question to ask for a principle.

        Args:
            principle: Principle number or name

        Returns:
            The question
        """
        num = self._resolve_principle(principle)
        return THE_SEVEN_PRINCIPLES[num - 1].question


# === Factory Function ===


def create_principle_healer(loader: "PrincipleLoader") -> PrincipleHealer:
    """
    Create a PrincipleHealer instance.

    Args:
        loader: PrincipleLoader for file access

    Returns:
        Configured PrincipleHealer
    """
    return PrincipleHealer(loader=loader)


# === Exports ===

__all__ = [
    "PrincipleHealer",
    "create_principle_healer",
]
