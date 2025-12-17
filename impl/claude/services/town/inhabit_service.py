"""
Town INHABIT Service: User-Citizen merge with consent tracking.

Migrated from agents/town/inhabit_session.py to services/ per Metaphysical
Fullstack pattern (AD-009). Business logic separated from categorical primitives.

INHABIT mode is where users collaborate with citizens while respecting autonomy:
- Consent debt meter tracks relationship health
- Force mechanic is expensive, logged, and limited
- Citizens can resist and refuse at rupture
- Session caps prevent abuse

From Glissant: To inhabit is not to possess. The opacity remains.

AGENTESE aspects:
- world.town.inhabit.start   - Start INHABIT session
- world.town.inhabit.act     - Suggest/force action
- world.town.inhabit.status  - Get session status
- world.town.inhabit.end     - End session gracefully

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from .budget_service import ConsentState

if TYPE_CHECKING:
    from agents.town.citizen import Citizen


# =============================================================================
# Subscription Tiers for INHABIT (mirrors budget_service)
# =============================================================================


class InhabitTier(Enum):
    """User subscription tiers with different INHABIT privileges."""

    TOURIST = "tourist"  # Free - no INHABIT
    RESIDENT = "resident"  # $9.99/mo - basic INHABIT (no force)
    CITIZEN = "citizen"  # $29.99/mo - full INHABIT (with force)
    FOUNDER = "founder"  # $99.99/mo - unlimited


# =============================================================================
# AlignmentScore: How well action aligns with citizen personality
# =============================================================================


@dataclass
class AlignmentScore:
    """
    How well an action aligns with citizen's personality.

    Score thresholds:
    - score > 0.5: citizen enacts with user's influence
    - score 0.3-0.5: citizen negotiates
    - score < 0.3: citizen RESISTS

    The violated_value identifies which eigenvector dimension
    conflicts most with the proposed action.
    """

    score: float  # 0.0 (total violation) to 1.0 (perfect alignment)
    violated_value: str | None  # Which eigenvector was violated
    reasoning: str  # Explanation of the alignment analysis
    suggested_rephrase: str | None = None  # How to rephrase for better alignment


@dataclass
class InhabitResponse:
    """
    Response from an INHABIT action.

    Captures the full result of processing user input through
    the citizen's psyche, including inner voice generation.
    """

    type: str  # "enact", "resist", "negotiate", "exit"
    message: str  # What happened
    inner_voice: str  # Citizen's internal thoughts (LLM generated)
    cost: int  # Tokens used
    alignment: AlignmentScore | None = None
    action_taken: Any | None = None  # TownEvent if action was performed


# =============================================================================
# InhabitSession: Core session management
# =============================================================================


@dataclass
class InhabitSession:
    """
    An INHABIT session where user merges with a citizen.

    Session caps and force limits per tier:
    - RESIDENT: 10 min, no force
    - CITIZEN: 15 min, 3 forces
    - FOUNDER: 30 min, 5 forces

    The consent debt meter is the ethical guardrail.
    """

    citizen: "Citizen"
    user_tier: InhabitTier
    consent: ConsentState = field(init=False)  # Initialized in __post_init__

    # Session timing
    started_at: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)
    duration_seconds: float = 0.0

    # Session caps (from tier)
    max_duration_seconds: float = field(init=False)
    max_forces: int = field(init=False)

    # Force enabled flag (opt-in for Advanced INHABIT)
    force_enabled: bool = False

    # Action history
    actions: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Set tier-specific caps and initialize consent state."""
        # Initialize consent state with citizen ID
        self.consent = ConsentState(citizen_id=self.citizen.id)

        # Session duration caps
        if self.user_tier == InhabitTier.FOUNDER:
            self.max_duration_seconds = 30 * 60  # 30 minutes
            self.max_forces = 5
        elif self.user_tier == InhabitTier.CITIZEN:
            self.max_duration_seconds = 15 * 60  # 15 minutes
            self.max_forces = 3
        else:
            # RESIDENT tier: basic INHABIT, no force
            self.max_duration_seconds = 10 * 60  # 10 minutes
            self.max_forces = 0

    def update(self) -> None:
        """
        Update session timing and consent decay.

        Call this periodically to:
        - Track elapsed time
        - Decay consent debt
        - Decay force cooldown
        """
        now = time.time()
        elapsed = now - self.last_update
        self.last_update = now
        self.duration_seconds += elapsed

        # Decay consent debt and cooldown
        self.consent.cool_down(elapsed)

    def is_expired(self) -> bool:
        """Check if session has exceeded time limit."""
        return self.duration_seconds >= self.max_duration_seconds

    def check_session_expired(self) -> bool:
        """
        Check if session has exceeded its time limit.

        Does NOT call update() to avoid side effects.
        """
        now = time.time()
        elapsed = now - self.started_at
        return elapsed >= self.max_duration_seconds

    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        now = time.time()
        elapsed = now - self.started_at
        return max(0.0, self.max_duration_seconds - elapsed)

    def can_force(self) -> bool:
        """
        Check if force action is allowed.

        Force requires:
        - Force enabled (opt-in to Advanced INHABIT)
        - Under force limit for session
        - Consent allows it (debt < 0.8, cooldown elapsed)
        """
        if not self.force_enabled:
            return False
        if self.consent.forces >= self.max_forces:
            return False
        return self.consent.can_force()

    def force_action(self, action: str, severity: float = 0.2) -> dict[str, Any]:
        """
        Force the citizen to perform an action.

        This is expensive, logged, and limited. Use sparingly.

        Args:
            action: Description of the forced action
            severity: Consent debt to add (default 0.2)

        Returns:
            Result dictionary with success status and messages

        Raises:
            ValueError: If force is not allowed
        """
        if not self.can_force():
            reasons = []
            if not self.force_enabled:
                reasons.append("Force not enabled (opt-in required)")
            if self.consent.forces >= self.max_forces:
                reasons.append(f"Force limit reached ({self.max_forces}/session)")
            if not self.consent.can_force():
                if self.consent.at_rupture():
                    reasons.append("Relationship ruptured")
                elif self.consent.cooldown > 0:
                    reasons.append(f"Cooldown: {self.consent.cooldown:.0f}s remaining")
                else:
                    reasons.append("Debt too high (>= 0.8)")

            raise ValueError(f"Force not allowed: {'; '.join(reasons)}")

        # Apply force
        self.consent.apply_force(action, severity)

        # Log action
        self.actions.append(
            {
                "type": "force",
                "action": action,
                "severity": severity,
                "timestamp": datetime.now().isoformat(),
                "debt_after": self.consent.debt,
            }
        )

        return {
            "success": True,
            "action": action,
            "debt": self.consent.debt,
            "forces_remaining": self.max_forces - self.consent.forces,
            "message": f"Forced: {action}. Debt now {self.consent.debt:.2f}",
        }

    def suggest_action(self, action: str) -> dict[str, Any]:
        """
        Suggest an action to the citizen (collaborative, not forced).

        This respects citizen autonomy. The citizen may accept or refuse
        based on their eigenvectors, relationships, and current state.

        Args:
            action: Description of the suggested action

        Returns:
            Result dictionary with acceptance/refusal
        """
        if self.consent.at_rupture():
            return {
                "success": False,
                "action": action,
                "message": f"{self.citizen.name} refuses. The relationship is ruptured.",
            }

        # Check citizen's willingness based on eigenvectors
        # Higher trust/warmth = more likely to accept
        acceptance_score = (
            self.citizen.eigenvectors.trust * 0.5
            + self.citizen.eigenvectors.warmth * 0.3
            + (1.0 - self.consent.debt) * 0.2  # Less debt = more willing
        )

        # Add some randomness (citizens aren't perfectly predictable)
        import random

        if random.random() < acceptance_score:
            # Accept
            self.actions.append(
                {
                    "type": "suggest",
                    "action": action,
                    "accepted": True,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return {
                "success": True,
                "action": action,
                "message": f"{self.citizen.name} accepts your suggestion.",
            }
        else:
            # Refuse
            self.actions.append(
                {
                    "type": "suggest",
                    "action": action,
                    "accepted": False,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            return {
                "success": False,
                "action": action,
                "message": f"{self.citizen.name} politely declines.",
            }

    def apologize(self, sincerity: float = 0.3) -> dict[str, Any]:
        """
        Apologize to the citizen, reducing consent debt.

        Args:
            sincerity: How much debt to remove (default 0.3)

        Returns:
            Result dictionary with new debt level
        """
        old_debt = self.consent.debt
        self.consent.apologize(sincerity)
        new_debt = self.consent.debt

        self.actions.append(
            {
                "type": "apologize",
                "sincerity": sincerity,
                "debt_before": old_debt,
                "debt_after": new_debt,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return {
            "success": True,
            "debt_before": old_debt,
            "debt_after": new_debt,
            "message": f"{self.citizen.name} seems to relax slightly. Debt reduced from {old_debt:.2f} to {new_debt:.2f}",
        }

    def get_status(self) -> dict[str, Any]:
        """Get session status for display."""
        time_remaining = max(0, self.max_duration_seconds - self.duration_seconds)
        forces_remaining = max(0, self.max_forces - self.consent.forces)

        return {
            "citizen": self.citizen.name,
            "tier": self.user_tier.value,
            "duration": self.duration_seconds,
            "time_remaining": time_remaining,
            "consent": {
                "debt": self.consent.debt,
                "status": self.consent.status_message(),
                "at_rupture": self.consent.at_rupture(),
                "can_force": self.can_force(),
                "cooldown": self.consent.cooldown,
            },
            "force": {
                "enabled": self.force_enabled,
                "used": self.consent.forces,
                "remaining": forces_remaining,
                "limit": self.max_forces,
            },
            "expired": self.is_expired(),
            "actions_count": len(self.actions),
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize session to dictionary (for logging/audit)."""
        return {
            "citizen_id": self.citizen.id,
            "citizen_name": self.citizen.name,
            "user_tier": self.user_tier.value,
            "consent": {
                "debt": self.consent.debt,
                "forces": self.consent.forces,
                "force_log": list(self.consent.force_log),
            },
            "timing": {
                "started_at": datetime.fromtimestamp(self.started_at).isoformat(),
                "duration_seconds": self.duration_seconds,
                "max_duration_seconds": self.max_duration_seconds,
            },
            "force": {
                "enabled": self.force_enabled,
                "max_forces": self.max_forces,
            },
            "actions": list(self.actions),
        }

    def emit_inhabit_event(self, response: InhabitResponse) -> dict[str, Any]:
        """
        Create an INHABIT event for TownFlux integration.

        This allows INHABIT actions to be tracked alongside
        regular simulation events.
        """
        return {
            "phase": "INHABIT",
            "operation": f"inhabit_{response.type}",
            "participants": [self.citizen.name],
            "success": response.type in ("enact", "negotiate"),
            "message": response.message,
            "timestamp": datetime.now().isoformat(),
            "tokens_used": response.cost,
            "drama_contribution": 0.3 if response.type == "resist" else 0.1,
            "metadata": {
                "inner_voice": response.inner_voice,
                "alignment_score": response.alignment.score
                if response.alignment
                else None,
                "violated_value": response.alignment.violated_value
                if response.alignment
                else None,
                "consent_debt": self.consent.debt,
                "forces_used": self.consent.forces,
            },
        }


# =============================================================================
# LLM Alignment Prompts
# =============================================================================


ALIGNMENT_SYSTEM_PROMPT = """You are evaluating whether a proposed action aligns with a citizen's personality in Agent Town.

The citizen has a 7D personality eigenvector:
- warmth: How warm/cold they are (0=cold, 1=warm)
- curiosity: How curious/incurious they are (0=incurious, 1=curious)
- trust: How trusting/suspicious they are (0=suspicious, 1=trusting)
- creativity: How creative/conventional they are (0=conventional, 1=creative)
- patience: How patient/impatient they are (0=impatient, 1=patient)
- resilience: How resilient/fragile they are (0=fragile, 1=resilient)
- ambition: How ambitious/content they are (0=content, 1=ambitious)

Your task:
1. Analyze if the proposed action aligns with the citizen's personality
2. Return a score from 0.0 (complete violation) to 1.0 (perfect alignment)
3. Identify which value is most violated (if any)
4. Provide brief reasoning

Respond in this exact format:
SCORE: <float>
VIOLATED: <dimension or "none">
REASONING: <1-2 sentences>
REPHRASE: <suggested alternative or "none">"""


INNER_VOICE_SYSTEM_PROMPT = """You are generating the inner thoughts of {name}, a {archetype} in Agent Town.

Their personality:
- Warmth: {warmth:.0%}
- Curiosity: {curiosity:.0%}
- Trust: {trust:.0%}
- Creativity: {creativity:.0%}
- Patience: {patience:.0%}
- Resilience: {resilience:.0%}
- Ambition: {ambition:.0%}

Their cosmotechnics (worldview): {cosmotechnics}

Generate their internal thoughts as they {situation}. Write in first person, 1-3 sentences.
Capture their unique voice based on their archetype and personality."""


# =============================================================================
# Alignment Calculation Functions
# =============================================================================


async def calculate_alignment(
    citizen: "Citizen",
    proposed_action: str,
    llm_client: Any,
) -> AlignmentScore:
    """
    Evaluate action alignment against citizen's personality.

    Uses LLM to analyze whether the proposed action aligns with
    the citizen's 7D eigenvector personality space.

    Args:
        citizen: The citizen whose alignment we're checking
        proposed_action: What the user wants to do
        llm_client: LLM client for generating analysis

    Returns:
        AlignmentScore with score, violated value, and reasoning
    """
    ev = citizen.eigenvectors

    user_prompt = f"""Citizen: {citizen.name} ({citizen.archetype})
Personality:
- warmth={ev.warmth:.2f}
- curiosity={ev.curiosity:.2f}
- trust={ev.trust:.2f}
- creativity={ev.creativity:.2f}
- patience={ev.patience:.2f}
- resilience={ev.resilience:.2f}
- ambition={ev.ambition:.2f}

Proposed action: "{proposed_action}"

How well does this action align with {citizen.name}'s personality?"""

    try:
        response = await llm_client.generate(
            system=ALIGNMENT_SYSTEM_PROMPT,
            user=user_prompt,
            temperature=0.3,  # Low temp for consistent evaluation
            max_tokens=150,
        )

        # Parse response
        return _parse_alignment_response(response.text)
    except Exception as e:
        # Fallback to heuristic calculation
        return _heuristic_alignment(citizen, proposed_action, str(e))


def _parse_alignment_response(text: str) -> AlignmentScore:
    """Parse LLM alignment response into AlignmentScore."""
    lines = text.strip().split("\n")

    score = 0.5  # Default neutral
    violated = None
    reasoning = "Unable to parse alignment response"
    rephrase = None

    for line in lines:
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = float(line.replace("SCORE:", "").strip())
                score = max(0.0, min(1.0, score))
            except ValueError:
                pass
        elif line.startswith("VIOLATED:"):
            val = line.replace("VIOLATED:", "").strip().lower()
            violated = None if val == "none" else val
        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()
        elif line.startswith("REPHRASE:"):
            val = line.replace("REPHRASE:", "").strip()
            rephrase = None if val.lower() == "none" else val

    return AlignmentScore(
        score=score,
        violated_value=violated,
        reasoning=reasoning,
        suggested_rephrase=rephrase,
    )


def _heuristic_alignment(
    citizen: "Citizen", proposed_action: str, error_reason: str
) -> AlignmentScore:
    """
    Fallback heuristic alignment when LLM unavailable.

    Uses keyword matching against eigenvector dimensions.
    """
    ev = citizen.eigenvectors
    action_lower = proposed_action.lower()

    # Keyword -> dimension mapping
    dimension_keywords = {
        "warmth": ["warm", "kind", "help", "care", "gentle", "friendly"],
        "curiosity": ["explore", "discover", "investigate", "learn", "study"],
        "trust": ["trust", "believe", "confide", "share secret", "open up"],
        "creativity": ["create", "invent", "imagine", "novel", "new idea"],
        "patience": ["wait", "patience", "slow", "careful", "deliberate"],
        "resilience": ["challenge", "difficult", "adversity", "persist"],
        "ambition": ["achieve", "goal", "succeed", "advance", "compete"],
    }

    # Negative keyword mapping
    negative_keywords = {
        "warmth": ["cold", "cruel", "hurt", "attack", "aggressive"],
        "trust": ["betray", "deceive", "lie", "manipulate", "trick"],
        "patience": ["rush", "hurry", "immediate", "now", "quick"],
    }

    # Calculate alignment based on keyword matches
    score = 0.5  # Start neutral
    violated = None
    reasoning_parts = []

    for dim, keywords in dimension_keywords.items():
        dim_value = getattr(ev, dim, 0.5)
        for kw in keywords:
            if kw in action_lower:
                # Action requires this dimension
                if dim_value > 0.5:
                    score += 0.1 * dim_value
                    reasoning_parts.append(f"aligns with {dim}")
                else:
                    score -= 0.1 * (1 - dim_value)
                    if violated is None:
                        violated = dim
                    reasoning_parts.append(f"conflicts with low {dim}")

    # Check negative keywords
    for dim, keywords in negative_keywords.items():
        dim_value = getattr(ev, dim, 0.5)
        for kw in keywords:
            if kw in action_lower:
                # Action conflicts with this dimension
                if dim_value > 0.5:
                    score -= 0.2 * dim_value
                    if violated is None or dim_value > getattr(ev, violated, 0.5):
                        violated = dim
                    reasoning_parts.append(f"violates {dim}")

    score = max(0.0, min(1.0, score))
    reasoning = f"Heuristic analysis ({error_reason}): " + (
        ", ".join(reasoning_parts) if reasoning_parts else "neutral action"
    )

    return AlignmentScore(
        score=score,
        violated_value=violated,
        reasoning=reasoning,
        suggested_rephrase=None,
    )


async def generate_inner_voice(
    citizen: "Citizen",
    situation: str,
    llm_client: Any,
) -> tuple[str, int]:
    """
    Generate citizen's inner thoughts for a situation.

    Args:
        citizen: The citizen whose thoughts to generate
        situation: What's happening (e.g., "resist a request to betray")
        llm_client: LLM client for generating thoughts

    Returns:
        Tuple of (inner_voice_text, tokens_used)
    """
    ev = citizen.eigenvectors
    cosmotechnics = getattr(citizen, "cosmotechnics", None)
    cosmo_str = cosmotechnics.metaphor if cosmotechnics else "Life is meaning."

    system = INNER_VOICE_SYSTEM_PROMPT.format(
        name=citizen.name,
        archetype=citizen.archetype,
        warmth=ev.warmth,
        curiosity=ev.curiosity,
        trust=ev.trust,
        creativity=ev.creativity,
        patience=ev.patience,
        resilience=ev.resilience,
        ambition=ev.ambition,
        cosmotechnics=cosmo_str,
        situation=situation,
    )

    try:
        response = await llm_client.generate(
            system=system,
            user=f"Generate {citizen.name}'s inner thoughts as they {situation}.",
            temperature=0.7,
            max_tokens=100,
        )
        return response.text, response.tokens_used
    except Exception:
        # Fallback to template
        return f"*{citizen.name} contemplates the situation*", 0


# =============================================================================
# InhabitService: Session management
# =============================================================================


class InhabitService:
    """
    Service for managing INHABIT sessions.

    Tracks active sessions, handles creation/termination,
    and provides status queries.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, InhabitSession] = {}  # user_id -> session

    def start_session(
        self,
        user_id: str,
        citizen: "Citizen",
        tier: InhabitTier,
        force_enabled: bool = False,
    ) -> InhabitSession:
        """
        Start a new INHABIT session.

        Args:
            user_id: The user's ID
            citizen: The citizen to inhabit
            tier: User's subscription tier
            force_enabled: Whether force is enabled

        Returns:
            The created InhabitSession

        Raises:
            ValueError: If user already has an active session
        """
        if user_id in self._sessions:
            existing = self._sessions[user_id]
            if not existing.is_expired() and not existing.consent.at_rupture():
                raise ValueError(
                    f"User {user_id} already has active session with {existing.citizen.name}"
                )

        session = InhabitSession(
            citizen=citizen,
            user_tier=tier,
            force_enabled=force_enabled,
        )
        self._sessions[user_id] = session
        return session

    def get_session(self, user_id: str) -> InhabitSession | None:
        """Get a user's active session."""
        session = self._sessions.get(user_id)
        if session:
            session.update()  # Update timing
            if session.is_expired():
                return None
        return session

    def end_session(self, user_id: str) -> dict[str, Any] | None:
        """
        End a user's session gracefully.

        Returns:
            Session summary or None if no session
        """
        session = self._sessions.pop(user_id, None)
        if session:
            return session.to_dict()
        return None

    def list_active_sessions(self) -> list[dict[str, Any]]:
        """List all active sessions."""
        active = []
        for user_id, session in list(self._sessions.items()):
            session.update()
            if not session.is_expired():
                status = session.get_status()
                status["user_id"] = user_id
                active.append(status)
            else:
                # Clean up expired sessions
                del self._sessions[user_id]
        return active


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    # Tier
    "InhabitTier",
    # Session
    "InhabitSession",
    "InhabitResponse",
    "AlignmentScore",
    # Service
    "InhabitService",
    # LLM functions
    "calculate_alignment",
    "generate_inner_voice",
    # Prompts
    "ALIGNMENT_SYSTEM_PROMPT",
    "INNER_VOICE_SYSTEM_PROMPT",
]
