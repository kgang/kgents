"""
Feature Patterns: Map features to file path patterns.

Each feature is identified by glob patterns that match its implementation
and specification files. This enables automatic classification.

Updated post-Crown Jewel Cleanup (2025-12-21):
- Town, Park, Gestalt, Forge, Coalition, Muse → EXTINCT
- Brain, Witness, Liminal, Foundry → ACTIVE

See: spec/protocols/repo-archaeology.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class FeaturePattern:
    """
    A feature and its associated file patterns.

    Used to identify which commits belong to which feature.
    """

    name: str
    impl_patterns: tuple[str, ...]  # Patterns for implementation files
    spec_patterns: tuple[str, ...]  # Patterns for specification files
    test_patterns: tuple[str, ...] = field(default_factory=tuple)
    status: str = "active"  # active | extinct | speculative

    @property
    def all_patterns(self) -> tuple[str, ...]:
        """All patterns combined."""
        return self.impl_patterns + self.spec_patterns + self.test_patterns

    def matches_file(self, file_path: str) -> bool:
        """Check if a file path matches any of the feature patterns."""
        for pattern in self.all_patterns:
            if pattern in file_path:
                return True
        return False


# Crown Jewels - Active core services (post-cleanup)
CROWN_JEWELS = (
    FeaturePattern(
        name="Brain",
        impl_patterns=("impl/claude/services/brain/",),
        spec_patterns=("spec/m-gents/", "spec/services/brain"),
        test_patterns=("services/brain/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Witness",
        impl_patterns=("impl/claude/services/witness/",),
        spec_patterns=("spec/services/witness", "spec/protocols/witness"),
        test_patterns=("services/witness/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Liminal",
        impl_patterns=("impl/claude/services/liminal/",),
        spec_patterns=("spec/services/liminal",),
        test_patterns=("services/liminal/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Foundry",
        impl_patterns=("impl/claude/services/foundry/",),
        spec_patterns=("spec/services/foundry",),
        test_patterns=("services/foundry/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Conductor",
        impl_patterns=("impl/claude/services/conductor/",),
        spec_patterns=("spec/protocols/conductor",),
        test_patterns=("services/conductor/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="LivingDocs",
        impl_patterns=("impl/claude/services/living_docs/",),
        spec_patterns=("spec/protocols/living-docs",),
        test_patterns=("services/living_docs/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Fusion",
        impl_patterns=("impl/claude/services/fusion/",),
        spec_patterns=(),
        test_patterns=("services/fusion/_tests/",),
        status="active",
    ),
)

# Extinct Crown Jewels - Removed in Crown Jewel Cleanup (2025-12-21)
# Kept for archaeological purposes - to track their history
EXTINCT = (
    FeaturePattern(
        name="Town",
        impl_patterns=("impl/claude/services/town/",),
        spec_patterns=("spec/town/",),
        test_patterns=("services/town/_tests/",),
        status="extinct",
    ),
    FeaturePattern(
        name="Park",
        impl_patterns=("impl/claude/services/park/",),
        spec_patterns=("spec/protocols/park",),
        test_patterns=("services/park/_tests/",),
        status="extinct",
    ),
    FeaturePattern(
        name="Forge",
        impl_patterns=("impl/claude/services/forge/",),
        spec_patterns=("spec/protocols/forge",),
        test_patterns=("services/forge/_tests/",),
        status="extinct",
    ),
    FeaturePattern(
        name="Gestalt",
        impl_patterns=("impl/claude/services/gestalt/",),
        spec_patterns=("spec/ui/gestalt",),
        test_patterns=("services/gestalt/_tests/",),
        status="extinct",
    ),
    FeaturePattern(
        name="Coalition",
        impl_patterns=("impl/claude/services/coalition/",),
        spec_patterns=(),
        test_patterns=("services/coalition/_tests/",),
        status="extinct",
    ),
    FeaturePattern(
        name="Muse",
        impl_patterns=("impl/claude/services/muse/",),
        spec_patterns=("spec/services/muse",),
        test_patterns=("services/muse/_tests/",),
        status="extinct",
    ),
    FeaturePattern(
        name="Gardener",
        impl_patterns=("impl/claude/services/gardener/",),
        spec_patterns=("spec/protocols/gardener",),
        test_patterns=("services/gardener/_tests/",),
        status="extinct",
    ),
)

# Infrastructure - Categorical foundations
INFRASTRUCTURE = (
    FeaturePattern(
        name="AGENTESE",
        impl_patterns=("impl/claude/protocols/agentese/",),
        spec_patterns=("spec/protocols/agentese",),
        test_patterns=("protocols/agentese/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="PolyAgent",
        impl_patterns=("impl/claude/agents/poly/",),
        spec_patterns=("spec/agents/",),
        test_patterns=("agents/poly/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Operad",
        impl_patterns=("impl/claude/agents/operad/",),
        spec_patterns=("spec/agents/operads",),
        test_patterns=("agents/operad/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Flux",
        impl_patterns=("impl/claude/agents/flux/",),
        spec_patterns=("spec/agents/flux",),
        test_patterns=("agents/flux/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Sheaf",
        impl_patterns=("impl/claude/agents/sheaf/",),
        spec_patterns=("spec/w-gents/",),
        test_patterns=("agents/sheaf/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="K-gent",
        impl_patterns=("impl/claude/agents/k/",),
        spec_patterns=("spec/k-gent/",),
        test_patterns=("agents/k/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="M-gent",
        impl_patterns=("impl/claude/agents/m/",),
        spec_patterns=("spec/m-gents/",),
        test_patterns=("agents/m/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="I-gent",
        impl_patterns=("impl/claude/agents/i/",),
        spec_patterns=("spec/i-gents/",),
        test_patterns=("agents/i/_tests/",),
        status="active",
    ),
)

# Protocols - Communication, CLI, and Systems
PROTOCOLS = (
    FeaturePattern(
        name="CLI",
        impl_patterns=("impl/claude/protocols/cli/",),
        spec_patterns=("spec/protocols/cli", "spec/protocols/os-shell"),
        test_patterns=("protocols/cli/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="ASHC",
        impl_patterns=(
            "impl/claude/protocols/ashc/",
            "impl/claude/services/verification/",
        ),
        spec_patterns=(
            "spec/protocols/ASHC",
            "spec/protocols/agentic-self-hosting",
        ),
        test_patterns=("protocols/ashc/_tests/", "services/verification/_tests/"),
        status="active",
    ),
    FeaturePattern(
        name="API",
        impl_patterns=("impl/claude/protocols/api/",),
        spec_patterns=("spec/protocols/api",),
        test_patterns=("protocols/api/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Trail",
        impl_patterns=("impl/claude/protocols/trail/",),
        spec_patterns=("spec/protocols/trail-protocol",),
        test_patterns=("protocols/trail/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Portal",
        impl_patterns=("impl/claude/protocols/portal",),
        spec_patterns=("spec/protocols/portal",),
        test_patterns=("protocols/portal/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Derivation",
        impl_patterns=("impl/claude/protocols/derivation/",),
        spec_patterns=("spec/protocols/derivation-framework",),
        test_patterns=("protocols/derivation/_tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Exploration",
        impl_patterns=("impl/claude/protocols/exploration/",),
        spec_patterns=("spec/protocols/exploration-harness",),
        test_patterns=("protocols/exploration/_tests/",),
        status="active",
    ),
    # Extinct protocols
    FeaturePattern(
        name="Evergreen",
        impl_patterns=("impl/claude/protocols/evergreen/",),
        spec_patterns=("spec/protocols/evergreen",),
        test_patterns=("protocols/evergreen/_tests/",),
        status="extinct",
    ),
)

# Web Frontend
WEB = (
    FeaturePattern(
        name="Web-Brain",
        impl_patterns=("impl/claude/web/src/components/brain/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Web-Witness",
        impl_patterns=("impl/claude/web/src/components/witness/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Web-Trail",
        impl_patterns=("impl/claude/web/src/components/trail/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Web-Portal",
        impl_patterns=("impl/claude/web/src/components/portal/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
        status="active",
    ),
    FeaturePattern(
        name="Web-Shell",
        impl_patterns=("impl/claude/web/src/shell/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
        status="active",
    ),
    # Extinct web components
    FeaturePattern(
        name="Web-Canvas",
        impl_patterns=("impl/claude/web/src/components/canvas/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
        status="extinct",
    ),
    FeaturePattern(
        name="Web-Gestalt",
        impl_patterns=("impl/claude/web/src/components/gestalt/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
        status="extinct",
    ),
)

# Speculative - Spec exists but minimal/no implementation
SPECULATIVE = (
    FeaturePattern(
        name="Psi-gents",
        impl_patterns=(),
        spec_patterns=("spec/psi-gents/",),
        test_patterns=(),
        status="speculative",
    ),
    FeaturePattern(
        name="Omega-gents",
        impl_patterns=(),
        spec_patterns=("spec/omega-gents/",),
        test_patterns=(),
        status="speculative",
    ),
    FeaturePattern(
        name="G-gents",
        impl_patterns=(),
        spec_patterns=("spec/g-gents/",),
        test_patterns=(),
        status="speculative",
    ),
    FeaturePattern(
        name="L-gents",
        impl_patterns=(),
        spec_patterns=("spec/l-gents/",),
        test_patterns=(),
        status="speculative",
    ),
    FeaturePattern(
        name="W-gents",
        impl_patterns=(),
        spec_patterns=("spec/w-gents/",),
        test_patterns=(),
        status="speculative",
    ),
)

# All feature patterns combined
FEATURE_PATTERNS: dict[str, FeaturePattern] = {
    fp.name: fp
    for fp in (
        *CROWN_JEWELS,
        *EXTINCT,
        *INFRASTRUCTURE,
        *PROTOCOLS,
        *WEB,
        *SPECULATIVE,
    )
}

# Convenience: just active features
ACTIVE_FEATURES: dict[str, FeaturePattern] = {
    name: fp for name, fp in FEATURE_PATTERNS.items() if fp.status == "active"
}


def get_patterns_by_category() -> dict[str, Sequence[FeaturePattern]]:
    """Get feature patterns organized by category."""
    return {
        "Crown Jewels": CROWN_JEWELS,
        "Extinct": EXTINCT,
        "Infrastructure": INFRASTRUCTURE,
        "Protocols": PROTOCOLS,
        "Web": WEB,
        "Speculative": SPECULATIVE,
    }


def get_patterns_by_status() -> dict[str, list[FeaturePattern]]:
    """Get feature patterns organized by status."""
    result: dict[str, list[FeaturePattern]] = {
        "active": [],
        "extinct": [],
        "speculative": [],
    }
    for fp in FEATURE_PATTERNS.values():
        result[fp.status].append(fp)
    return result


def match_file_to_features(file_path: str) -> list[str]:
    """Find which features a file belongs to."""
    return [name for name, pattern in FEATURE_PATTERNS.items() if pattern.matches_file(file_path)]
