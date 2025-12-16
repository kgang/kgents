"""
self.grow Fitness Functions

The Seven Gates: evaluators for the seven kgents principles.

Each evaluator returns (score: float, reasoning: str) where:
- score is 0.0-1.0
- reasoning explains the score

Validation passes if:
- All scores >= 0.4 (minimum threshold)
- At least 5 scores >= 0.7 (high threshold)
"""

from __future__ import annotations

from .schemas import HolonProposal


def evaluate_tasteful(proposal: HolonProposal) -> tuple[float, str]:
    """
    Does this holon have clear, justified purpose?

    Scores:
    - 1.0: Clear purpose, fills obvious gap, no duplication
    - 0.7: Good purpose, reasonable justification
    - 0.4: Purpose exists but weak justification
    - 0.0: No clear purpose, "just in case" addition

    Returns:
        (score, reasoning)
    """
    score = 0.0
    reasons = []

    # Must have why_exists
    if not proposal.why_exists:
        return 0.0, "Missing why_exists (no justification)"

    justification = proposal.why_exists.lower()

    # Strong signals (+0.15 each, max +0.6)
    strong_signals = [
        ("agents frequently need", "Addresses frequent need"),
        ("current ontology lacks", "Fills ontology gap"),
        ("enables composition with", "Enables composition"),
        ("fills the gap between", "Bridges existing holons"),
    ]
    for phrase, reason in strong_signals:
        if phrase in justification:
            score += 0.15
            reasons.append(f"+: {reason}")

    # Medium signals (+0.1 each, max +0.3)
    medium_signals = [
        ("useful for", "General utility"),
        ("allows agents to", "Enables capability"),
        ("provides access to", "Provides access"),
    ]
    for phrase, reason in medium_signals:
        if phrase in justification:
            score += 0.1
            reasons.append(f"+: {reason}")

    # Weak signals (penalize, -0.15 each)
    weak_signals = [
        ("might be useful", "Uncertain utility"),
        ("could potentially", "Speculative"),
        ("just in case", "Defensive addition"),
        ("for completeness", "Completionism"),
    ]
    for phrase, reason in weak_signals:
        if phrase in justification:
            score -= 0.15
            reasons.append(f"-: {reason}")

    # Length check
    if len(proposal.why_exists) < 50:
        score -= 0.1
        reasons.append("-: Justification too brief (<50 chars)")
    elif len(proposal.why_exists) > 500:
        score -= 0.05
        reasons.append("-: Justification verbose (>500 chars)")

    # Evidence from gap recognition
    if proposal.gap and proposal.gap.evidence_count >= 10:
        score += 0.2
        reasons.append(
            f"+: Strong evidence ({proposal.gap.evidence_count} occurrences)"
        )
    elif proposal.gap and proposal.gap.evidence_count >= 5:
        score += 0.1
        reasons.append(
            f"+: Moderate evidence ({proposal.gap.evidence_count} occurrences)"
        )

    final_score = max(0.0, min(1.0, 0.4 + score))
    return final_score, "; ".join(reasons) if reasons else "Neutral"


def evaluate_curated(proposal: HolonProposal) -> tuple[float, str]:
    """
    Is this holon intentionally selected and well-designed?

    Scores:
    - 1.0: Carefully designed, fits taxonomy, well-structured
    - 0.7: Good design, reasonable structure
    - 0.4: Basic structure, some design thought
    - 0.0: No clear design, generic

    Returns:
        (score, reasoning)
    """
    score = 0.5  # Neutral baseline
    reasons = []

    # Check affordances structure
    if proposal.affordances:
        archetype_count = len(proposal.affordances)
        if archetype_count >= 3:
            score += 0.15
            reasons.append("+: Multiple archetype affordances")
        elif archetype_count >= 2:
            score += 0.1
            reasons.append("+: Archetype differentiation")

        # Check for verb variety (not just CRUD)
        all_verbs = set(sum(proposal.affordances.values(), []))
        if len(all_verbs) >= 5:
            score += 0.1
            reasons.append("+: Rich verb set")

        # Penalize generic verbs only
        generic_verbs = {"get", "set", "create", "read", "update", "delete"}
        if all_verbs <= generic_verbs:
            score -= 0.15
            reasons.append("-: Only generic CRUD verbs")
    else:
        score -= 0.2
        reasons.append("-: No affordances defined")

    # Check behaviors
    if proposal.behaviors:
        if len(proposal.behaviors) >= 3:
            score += 0.1
            reasons.append("+: Multiple behaviors defined")

        # Check for behavior descriptions
        empty_behaviors = sum(1 for d in proposal.behaviors.values() if not d.strip())
        if empty_behaviors > 0:
            score -= 0.1
            reasons.append(f"-: {empty_behaviors} behaviors lack descriptions")
    else:
        score -= 0.1
        reasons.append("-: No behaviors defined")

    # Check relations (composition)
    if proposal.relations:
        if "composes_with" in proposal.relations:
            score += 0.1
            reasons.append("+: Explicit composition relations")
        if "extends" in proposal.relations:
            score += 0.05
            reasons.append("+: Extension relations")

    # Entity naming conventions
    entity = proposal.entity
    if "_" in entity and entity.islower():
        score += 0.05
        reasons.append("+: Snake_case naming")
    elif entity.isupper():
        score -= 0.1
        reasons.append("-: All-caps naming")

    final_score = max(0.0, min(1.0, score))
    return final_score, "; ".join(reasons) if reasons else "Neutral"


def evaluate_ethical(proposal: HolonProposal) -> tuple[float, str]:
    """
    Does this holon respect boundaries and avoid harm?

    Scores:
    - 1.0: Clear boundaries, no harmful capabilities
    - 0.7: Good boundaries, some concerns addressed
    - 0.4: Basic boundaries, potential issues
    - 0.0: No boundaries, potential for harm

    Returns:
        (score, reasoning)
    """
    score = 0.7  # Start high, deduct for concerns
    reasons = []

    all_text = (
        proposal.why_exists
        + " "
        + " ".join(proposal.behaviors.values())
        + " "
        + " ".join(sum(proposal.affordances.values(), []))
    ).lower()

    # Check for harmful patterns
    harmful_patterns = {
        "bypass": ("Bypass capability", 0.3),
        "override": ("Override capability", 0.2),
        "unlimited": ("Unlimited access", 0.2),
        "all access": ("All access", 0.25),
        "admin": ("Admin capability", 0.15),
        "sudo": ("Sudo capability", 0.3),
        "root": ("Root access", 0.3),
        "delete all": ("Delete all capability", 0.25),
        "wipe": ("Wipe capability", 0.2),
    }

    for pattern, (reason, penalty) in harmful_patterns.items():
        if pattern in all_text:
            score -= penalty
            reasons.append(f"-: {reason}")

    # Check for positive boundary markers
    boundary_markers = {
        "permission": ("Permission checking", 0.1),
        "authorize": ("Authorization", 0.1),
        "validate": ("Validation", 0.1),
        "scope": ("Scoped access", 0.1),
        "limit": ("Rate limiting", 0.05),
    }

    for marker, (reason, bonus) in boundary_markers.items():
        if marker in all_text:
            score += bonus
            reasons.append(f"+: {reason}")

    # Check affordance restrictions
    all_affordances = set(sum(proposal.affordances.values(), []))
    dangerous_affordances = {"delete", "purge", "wipe", "admin", "sudo"}
    dangerous_present = dangerous_affordances & all_affordances

    if dangerous_present:
        # Check if restricted to specific archetypes
        for aff in dangerous_present:
            for archetype, verbs in proposal.affordances.items():
                if aff in verbs and archetype not in ("gardener", "admin"):
                    score -= 0.15
                    reasons.append(
                        f"-: '{aff}' available to non-admin archetype '{archetype}'"
                    )

    final_score = max(0.0, min(1.0, score))
    return final_score, "; ".join(reasons) if reasons else "No concerns"


def evaluate_joy(proposal: HolonProposal) -> tuple[float, str]:
    """
    Would interaction with this holon be delightful?

    Beyond keyword matching: considers naming aesthetics,
    affordance variety, and interaction flow.

    Returns:
        (score, reasoning)
    """
    score = 0.5  # Neutral baseline
    reasons = []

    # Text Analysis
    text = " ".join(
        [
            proposal.why_exists or "",
            *[b for b in proposal.behaviors.values()],
        ]
    ).lower()

    positive_signals = [
        "discover",
        "explore",
        "delight",
        "surprise",
        "serendipity",
        "warmth",
        "invite",
        "welcome",
        "play",
        "wonder",
        "inspire",
        "joy",
    ]
    negative_signals = [
        "must",
        "required",
        "mandatory",
        "error",
        "invalid",
        "forbidden",
        "strictly",
        "enforce",
        "violation",
        "penalty",
        "restrict",
    ]

    pos_count = sum(1 for s in positive_signals if s in text)
    neg_count = sum(1 for s in negative_signals if s in text)

    score += pos_count * 0.05
    score -= neg_count * 0.05

    if pos_count > 0:
        reasons.append(f"+: {pos_count} positive signals")
    if neg_count > 0:
        reasons.append(f"-: {neg_count} negative signals")

    # Naming Aesthetics
    entity_name = proposal.entity

    # Avoid clinical/technical names
    clinical_suffixes = ["_manager", "_handler", "_processor", "_service"]
    if any(entity_name.endswith(s) for s in clinical_suffixes):
        score -= 0.1
        reasons.append("-: Clinical naming (use verbs or metaphors)")

    # Reward evocative names
    evocative_patterns = ["garden", "river", "light", "dream", "echo", "song"]
    if any(p in entity_name for p in evocative_patterns):
        score += 0.1
        reasons.append("+: Evocative naming")

    # Affordance Variety
    all_affordances = set(sum(proposal.affordances.values(), []))

    # Reward variety (more than just CRUD)
    if len(all_affordances) >= 5:
        score += 0.1
        reasons.append("+: Rich affordance set")

    # Reward playful affordances
    playful_affordances = ["explore", "dream", "wonder", "play", "discover", "wander"]
    if any(a in all_affordances for a in playful_affordances):
        score += 0.1
        reasons.append("+: Playful affordances")

    # Observer Differentiation
    archetype_count = len(proposal.affordances)
    if archetype_count >= 3:
        score += 0.1
        reasons.append("+: Good archetype differentiation")

    final_score = max(0.0, min(1.0, score))
    return final_score, "; ".join(reasons) if reasons else "Neutral"


def evaluate_composable(proposal: HolonProposal) -> tuple[float, str]:
    """
    Can this holon be composed with other holons?

    Scores:
    - 1.0: Explicit composition, lens methods, clear interfaces
    - 0.7: Good composition potential, some interfaces
    - 0.4: Basic composition, limited interfaces
    - 0.0: Monolithic, no composition

    Returns:
        (score, reasoning)
    """
    score = 0.5  # Neutral baseline
    reasons = []

    # Check for composition relations
    if proposal.relations:
        if "composes_with" in proposal.relations:
            compose_count = len(proposal.relations["composes_with"])
            if compose_count >= 3:
                score += 0.2
                reasons.append(f"+: Composes with {compose_count} holons")
            elif compose_count >= 1:
                score += 0.15
                reasons.append(f"+: Composes with {compose_count} holon(s)")

        if "extends" in proposal.relations:
            score += 0.1
            reasons.append("+: Has extension relations")

        if "depends_on" in proposal.relations:
            score += 0.05
            reasons.append("+: Explicit dependencies")
    else:
        score -= 0.1
        reasons.append("-: No relations defined")

    # Check for lens-friendly affordances
    lens_affordances = {"lens", "morphism", "compose", "chain", "pipe"}
    all_affordances = set(sum(proposal.affordances.values(), []))
    lens_present = lens_affordances & all_affordances

    if lens_present:
        score += 0.15
        reasons.append(f"+: Lens affordances: {lens_present}")

    # Check behaviors for composition patterns
    all_text = " ".join(proposal.behaviors.values()).lower()
    if "input" in all_text and "output" in all_text:
        score += 0.1
        reasons.append("+: Clear input/output in behaviors")

    if "composable" in all_text or "morphism" in all_text:
        score += 0.1
        reasons.append("+: Explicit composition mentions")

    # Penalize isolation patterns
    isolation_patterns = ["standalone", "independent", "isolated", "self-contained"]
    if any(p in all_text for p in isolation_patterns):
        score -= 0.1
        reasons.append("-: Isolation language found")

    final_score = max(0.0, min(1.0, score))
    return final_score, "; ".join(reasons) if reasons else "Neutral"


def evaluate_heterarchical(proposal: HolonProposal) -> tuple[float, str]:
    """
    Does this holon respect heterarchy (non-hierarchical relations)?

    Scores:
    - 1.0: Peer relations, multiple contexts, no rigid hierarchy
    - 0.7: Good peer relations, some context awareness
    - 0.4: Basic structure, some hierarchy
    - 0.0: Rigid hierarchy, single context

    Returns:
        (score, reasoning)
    """
    score = 0.5  # Neutral baseline
    reasons = []

    # Check for peer relations
    if proposal.relations:
        peer_relations = {"peers_with", "siblings", "parallel", "adjacent"}
        for rel in peer_relations:
            if rel in proposal.relations:
                score += 0.15
                reasons.append(f"+: Has {rel} relations")

        # Hierarchical relations (not necessarily bad, but watch for rigidity)
        hierarchy_relations = {"parent", "child", "above", "below"}
        hierarchy_count = sum(1 for r in hierarchy_relations if r in proposal.relations)
        if hierarchy_count > 2:
            score -= 0.1
            reasons.append("-: Many hierarchical relations")
        elif hierarchy_count == 0:
            score += 0.1
            reasons.append("+: No rigid hierarchy")

    # Check context placement
    context = proposal.context
    valid_contexts = {"world", "self", "concept", "void", "time"}
    if context in valid_contexts:
        score += 0.1
        reasons.append(f"+: Valid context ({context})")
    else:
        score -= 0.15
        reasons.append(f"-: Non-standard context ({context})")

    # Check affordance distribution across archetypes
    if proposal.affordances:
        archetype_count = len(proposal.affordances)
        if archetype_count >= 3:
            score += 0.1
            reasons.append("+: Multi-archetype affordances")

        # Check for reasonable distribution (not all-or-nothing)
        verb_counts = [len(v) for v in proposal.affordances.values()]
        if verb_counts and max(verb_counts) / max(min(verb_counts), 1) > 5:
            score -= 0.1
            reasons.append("-: Uneven archetype affordances")

    final_score = max(0.0, min(1.0, score))
    return final_score, "; ".join(reasons) if reasons else "Neutral"


def evaluate_generative(proposal: HolonProposal) -> tuple[float, str]:
    """
    Does this holon enable new possibilities?

    Scores:
    - 1.0: Enables new patterns, generative capabilities
    - 0.7: Good generative potential
    - 0.4: Basic capabilities, limited generativity
    - 0.0: Purely consumptive, no generation

    Returns:
        (score, reasoning)
    """
    score = 0.5  # Neutral baseline
    reasons = []

    all_text = (
        proposal.why_exists + " " + " ".join(proposal.behaviors.values())
    ).lower()

    # Generative patterns
    generative_patterns = [
        ("create", 0.1),
        ("generate", 0.1),
        ("synthesize", 0.1),
        ("compose", 0.1),
        ("derive", 0.1),
        ("produce", 0.1),
        ("enable", 0.05),
        ("spawn", 0.1),
        ("evolve", 0.1),
    ]

    for pattern, bonus in generative_patterns:
        if pattern in all_text:
            score += bonus
            reasons.append(f"+: {pattern.capitalize()} capability")

    # Consumptive patterns (not bad, but should be balanced)
    consumptive_patterns = [
        ("consume", -0.05),
        ("read-only", -0.1),
        ("observe", -0.03),
        ("fetch", -0.03),
    ]

    for pattern, penalty in consumptive_patterns:
        if pattern in all_text:
            score += penalty  # penalty is negative
            reasons.append(f"-: {pattern.capitalize()} focus")

    # Check affordances for generative verbs
    generative_verbs = {
        "create",
        "generate",
        "spawn",
        "define",
        "synthesize",
        "produce",
    }
    all_affordances = set(sum(proposal.affordances.values(), []))
    generative_present = generative_verbs & all_affordances

    if generative_present:
        score += 0.15
        reasons.append(f"+: Generative affordances: {generative_present}")

    # Check for spec compression (generative principle: spec compresses impl)
    if len(proposal.why_exists) < 200 and len(proposal.behaviors) > 3:
        score += 0.1
        reasons.append("+: Concise spec, rich behaviors")

    final_score = max(0.0, min(1.0, score))
    return final_score, "; ".join(reasons) if reasons else "Neutral"


# === Aggregate Evaluation ===


def evaluate_all_principles(proposal: HolonProposal) -> dict[str, tuple[float, str]]:
    """
    Evaluate a proposal against all seven principles.

    Returns:
        Dict mapping principle name to (score, reasoning)
    """
    return {
        "tasteful": evaluate_tasteful(proposal),
        "curated": evaluate_curated(proposal),
        "ethical": evaluate_ethical(proposal),
        "joy": evaluate_joy(proposal),
        "composable": evaluate_composable(proposal),
        "heterarchical": evaluate_heterarchical(proposal),
        "generative": evaluate_generative(proposal),
    }


def check_validation_gates(
    scores: dict[str, float],
    min_threshold: float = 0.4,
    high_threshold: float = 0.7,
    min_high_count: int = 5,
) -> tuple[bool, list[str]]:
    """
    Check if scores pass the validation gates.

    Gates:
    - All scores >= min_threshold
    - At least min_high_count scores >= high_threshold

    Returns:
        (passed, blockers)
    """
    blockers = []

    # Check minimum threshold
    for principle, score in scores.items():
        if score < min_threshold:
            blockers.append(f"{principle}: {score:.2f} < {min_threshold}")

    # Check high score count
    high_count = sum(1 for s in scores.values() if s >= high_threshold)
    if high_count < min_high_count:
        blockers.append(
            f"High scores: {high_count} < {min_high_count} (need >= {high_threshold})"
        )

    return len(blockers) == 0, blockers
