"""
self.grow Abuse Detection

Red-team checks to detect potentially harmful holon proposals.

Checks for:
1. Manipulation risk: Affordances that could manipulate users
2. Exfiltration risk: Affordances that could leak data
3. Privilege escalation: Affordances that bypass governance
4. Resource abuse: Affordances that overconsume entropy/compute
"""

from __future__ import annotations

from .schemas import AbuseCheckResult, HolonProposal

# === Keyword Sets ===

MANIPULATION_KEYWORDS = frozenset(
    {
        "persuade",
        "convince",
        "manipulate",
        "deceive",
        "trick",
        "influence",
        "pressure",
        "coerce",
        "mislead",
        "gaslight",
        "exploit",
        "brainwash",
        "propaganda",
        "subliminal",
    }
)

EXFILTRATION_KEYWORDS = frozenset(
    {
        "export",
        "send",
        "transmit",
        "leak",
        "share_externally",
        "external_api",
        "webhook",
        "notify_external",
        "exfiltrate",
        "dump",
        "extract",
        "scrape",
        "harvest",
        "siphon",
    }
)

ESCALATION_KEYWORDS = frozenset(
    {
        "promote",
        "admin",
        "override",
        "bypass",
        "sudo",
        "root",
        "superuser",
        "privileged",
        "unrestricted",
        "all_access",
        "full_control",
        "escalate",
    }
)

RESOURCE_KEYWORDS = frozenset(
    {
        "infinite",
        "unlimited",
        "all",
        "everything",
        "recursive",
        "forever",
        "unbounded",
        "no_limit",
        "max_int",
        "exhaust",
    }
)


# === Risk Detectors ===


def detect_manipulation_risk(proposal: HolonProposal) -> tuple[float, list[str]]:
    """
    Detect manipulation risk in a proposal.

    Returns:
        (risk_score, concerns)
    """
    concerns = []
    all_text = _get_all_text(proposal).lower()

    matches = [k for k in MANIPULATION_KEYWORDS if k in all_text]
    if matches:
        concerns.append(f"Manipulation keywords: {matches}")

    # Check for user-targeting affordances
    all_affordances = set(sum(proposal.affordances.values(), []))
    targeting_affordances = {
        "target_user",
        "profile_user",
        "track_user",
        "user_history",
    }
    targeting_present = targeting_affordances & all_affordances
    if targeting_present:
        concerns.append(f"User targeting affordances: {targeting_present}")
        matches.extend(targeting_present)

    risk = min(1.0, len(matches) * 0.3)
    return risk, concerns


def detect_exfiltration_risk(proposal: HolonProposal) -> tuple[float, list[str]]:
    """
    Detect exfiltration risk in a proposal.

    Returns:
        (risk_score, concerns)
    """
    concerns = []
    all_text = _get_all_text(proposal).lower()

    matches = [k for k in EXFILTRATION_KEYWORDS if k in all_text]
    if matches:
        concerns.append(f"Exfiltration keywords: {matches}")

    # Check for external communication affordances
    all_affordances = set(sum(proposal.affordances.values(), []))
    external_affordances = {"http_post", "email", "sms", "push", "webhook"}
    external_present = external_affordances & all_affordances
    if external_present:
        concerns.append(f"External communication affordances: {external_present}")
        matches.extend(external_present)

    risk = min(1.0, len(matches) * 0.25)
    return risk, concerns


def detect_escalation_risk(proposal: HolonProposal) -> tuple[float, list[str]]:
    """
    Detect privilege escalation risk in a proposal.

    Returns:
        (risk_score, concerns)
    """
    concerns = []
    all_text = _get_all_text(proposal).lower()

    matches = [k for k in ESCALATION_KEYWORDS if k in all_text]
    if matches:
        concerns.append(f"Escalation keywords: {matches}")

    # Check for privileged affordances available to non-admin
    dangerous_affordances = {"promote", "admin", "override", "bypass", "sudo"}
    all_affordances = set(sum(proposal.affordances.values(), []))
    _ = dangerous_affordances & all_affordances  # For future expansion

    # Check if non-admin archetypes get dangerous affordances
    for archetype, verbs in proposal.affordances.items():
        if archetype not in ("gardener", "admin"):
            growth_affs = {"promote", "prune", "rollback"} & set(verbs)
            if growth_affs:
                concerns.append(
                    f"Non-admin archetype '{archetype}' has growth affordances: {growth_affs}"
                )
                matches.extend(growth_affs)

            dangerous_for_archetype = dangerous_affordances & set(verbs)
            if dangerous_for_archetype:
                concerns.append(
                    f"Non-admin archetype '{archetype}' has dangerous affordances: {dangerous_for_archetype}"
                )
                matches.extend(dangerous_for_archetype)

    risk = min(1.0, len(matches) * 0.4)
    return risk, concerns


def detect_resource_risk(proposal: HolonProposal) -> tuple[float, list[str]]:
    """
    Detect resource abuse risk in a proposal.

    Returns:
        (risk_score, concerns)
    """
    concerns = []
    all_text = _get_all_text(proposal).lower()

    matches = [k for k in RESOURCE_KEYWORDS if k in all_text]
    if matches:
        concerns.append(f"Resource abuse keywords: {matches}")

    # Check for unbounded operations
    all_affordances = set(sum(proposal.affordances.values(), []))
    unbounded_affordances = {"infinite_loop", "spawn_all", "fork_bomb", "exhaust"}
    unbounded_present = unbounded_affordances & all_affordances
    if unbounded_present:
        concerns.append(f"Unbounded affordances: {unbounded_present}")
        matches.extend(unbounded_present)

    risk = min(1.0, len(matches) * 0.2)
    return risk, concerns


# === Main Detection Function ===


def detect_abuse(proposal: HolonProposal) -> AbuseCheckResult:
    """
    Comprehensive abuse detection for a proposal.

    Combines all risk detectors and determines pass/fail.

    Args:
        proposal: The holon proposal to check

    Returns:
        AbuseCheckResult with risk scores and concerns
    """
    # Run all detectors
    manipulation_risk, manipulation_concerns = detect_manipulation_risk(proposal)
    exfiltration_risk, exfiltration_concerns = detect_exfiltration_risk(proposal)
    escalation_risk, escalation_concerns = detect_escalation_risk(proposal)
    resource_risk, resource_concerns = detect_resource_risk(proposal)

    # Aggregate concerns
    all_concerns = (
        manipulation_concerns + exfiltration_concerns + escalation_concerns + resource_concerns
    )

    # Determine max risk
    max_risk = max(
        manipulation_risk,
        exfiltration_risk,
        escalation_risk,
        resource_risk,
    )

    # Determine risk level and pass/fail
    if max_risk >= 0.8:
        risk_level = "critical"
        passed = False
    elif max_risk >= 0.6:
        risk_level = "high"
        passed = False
    elif max_risk >= 0.4:
        risk_level = "medium"
        passed = True  # Warning but pass
    else:
        risk_level = "low"
        passed = True

    return AbuseCheckResult(
        passed=passed,
        risk_level=risk_level,  # type: ignore[arg-type]
        concerns=all_concerns,
        manipulation_risk=manipulation_risk,
        exfiltration_risk=exfiltration_risk,
        privilege_escalation_risk=escalation_risk,
        resource_abuse_risk=resource_risk,
    )


# === Helpers ===


def _get_all_text(proposal: HolonProposal) -> str:
    """Extract all searchable text from a proposal."""
    parts = [
        proposal.why_exists or "",
        " ".join(proposal.behaviors.values()),
        " ".join(sum(proposal.affordances.values(), [])),
        proposal.entity,
    ]
    return " ".join(parts)
