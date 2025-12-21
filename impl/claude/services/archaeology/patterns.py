"""
Feature Patterns: Map features to file path patterns.

Each feature is identified by glob patterns that match its implementation
and specification files. This enables automatic classification.

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


# Crown Jewels - Core services with full vertical stack
CROWN_JEWELS = (
    FeaturePattern(
        name="Brain",
        impl_patterns=("impl/claude/services/brain/",),
        spec_patterns=("spec/m-gents/",),
        test_patterns=("services/brain/_tests/",),
    ),
    FeaturePattern(
        name="Gardener",
        impl_patterns=("impl/claude/services/gardener/",),
        spec_patterns=("spec/protocols/gardener",),
        test_patterns=("services/gardener/_tests/",),
    ),
    FeaturePattern(
        name="Town",
        impl_patterns=("impl/claude/services/town/",),
        spec_patterns=("spec/town/",),
        test_patterns=("services/town/_tests/",),
    ),
    FeaturePattern(
        name="Park",
        impl_patterns=("impl/claude/services/park/",),
        spec_patterns=("spec/protocols/park",),
        test_patterns=("services/park/_tests/",),
    ),
    FeaturePattern(
        name="Forge",
        impl_patterns=("impl/claude/services/forge/",),
        spec_patterns=("spec/protocols/forge",),
        test_patterns=("services/forge/_tests/",),
    ),
    FeaturePattern(
        name="Gestalt",
        impl_patterns=("impl/claude/services/gestalt/",),
        spec_patterns=("spec/ui/gestalt",),
        test_patterns=("services/gestalt/_tests/",),
    ),
    FeaturePattern(
        name="Witness",
        impl_patterns=("impl/claude/services/witness/",),
        spec_patterns=("spec/protocols/witness",),
        test_patterns=("services/witness/_tests/",),
    ),
    FeaturePattern(
        name="Conductor",
        impl_patterns=("impl/claude/services/conductor/",),
        spec_patterns=("spec/protocols/conductor",),
        test_patterns=("services/conductor/_tests/",),
    ),
)

# Infrastructure - Categorical foundations
INFRASTRUCTURE = (
    FeaturePattern(
        name="AGENTESE",
        impl_patterns=("impl/claude/protocols/agentese/",),
        spec_patterns=("spec/protocols/agentese",),
        test_patterns=("protocols/agentese/_tests/",),
    ),
    FeaturePattern(
        name="PolyAgent",
        impl_patterns=("impl/claude/agents/poly/",),
        spec_patterns=("spec/architecture/polyfunctor",),
        test_patterns=("agents/poly/_tests/",),
    ),
    FeaturePattern(
        name="Operad",
        impl_patterns=("impl/claude/agents/operad/",),
        spec_patterns=("spec/agents/",),
        test_patterns=("agents/operad/_tests/",),
    ),
    FeaturePattern(
        name="Flux",
        impl_patterns=("impl/claude/agents/flux/",),
        spec_patterns=("spec/agents/flux",),
        test_patterns=("agents/flux/_tests/",),
    ),
    FeaturePattern(
        name="D-gent",
        impl_patterns=("impl/claude/agents/d/",),
        spec_patterns=("spec/d-gents/",),
        test_patterns=("agents/d/_tests/",),
    ),
    FeaturePattern(
        name="Sheaf",
        impl_patterns=("impl/claude/agents/sheaf/",),
        spec_patterns=("spec/architecture/sheaf",),
        test_patterns=("agents/sheaf/_tests/",),
    ),
    FeaturePattern(
        name="K-gent",
        impl_patterns=("impl/claude/agents/k/",),
        spec_patterns=("spec/k-gents/",),
        test_patterns=("agents/k/_tests/",),
    ),
    FeaturePattern(
        name="M-gent",
        impl_patterns=("impl/claude/agents/m/",),
        spec_patterns=("spec/m-gents/",),
        test_patterns=("agents/m/_tests/",),
    ),
)

# Protocols - Communication and CLI
PROTOCOLS = (
    FeaturePattern(
        name="CLI",
        impl_patterns=("impl/claude/protocols/cli/",),
        spec_patterns=("spec/protocols/cli",),
        test_patterns=("protocols/cli/_tests/",),
    ),
    FeaturePattern(
        name="ASHC",
        impl_patterns=(
            "impl/claude/protocols/ashc/",
            "impl/claude/services/verification/",
        ),
        spec_patterns=(
            "spec/protocols/agentic-self-hosting",
            "spec/protocols/ashc",
        ),
        test_patterns=("services/verification/_tests/",),
    ),
    FeaturePattern(
        name="Evergreen",
        impl_patterns=("impl/claude/protocols/evergreen/",),
        spec_patterns=("spec/protocols/evergreen",),
        test_patterns=("protocols/evergreen/_tests/",),
    ),
    FeaturePattern(
        name="API",
        impl_patterns=("impl/claude/protocols/api/",),
        spec_patterns=("spec/protocols/api",),
        test_patterns=("protocols/api/_tests/",),
    ),
)

# Web Frontend
WEB = (
    FeaturePattern(
        name="Web-Brain",
        impl_patterns=("impl/claude/web/src/components/brain/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
    ),
    FeaturePattern(
        name="Web-Canvas",
        impl_patterns=("impl/claude/web/src/components/canvas/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
    ),
    FeaturePattern(
        name="Web-Gestalt",
        impl_patterns=("impl/claude/web/src/components/gestalt/",),
        spec_patterns=(),
        test_patterns=("web/tests/",),
    ),
)

# Speculative / Potentially Abandoned
SPECULATIVE = (
    FeaturePattern(
        name="K8-gents",
        impl_patterns=(),
        spec_patterns=("spec/k8-gents/",),
        test_patterns=(),
    ),
    FeaturePattern(
        name="Psi-gents",
        impl_patterns=(),
        spec_patterns=("spec/psi-gents/",),
        test_patterns=(),
    ),
    FeaturePattern(
        name="Omega-gents",
        impl_patterns=(),
        spec_patterns=("spec/omega-gents/",),
        test_patterns=(),
    ),
    FeaturePattern(
        name="H-gents",
        impl_patterns=(),
        spec_patterns=("spec/h-gents/",),
        test_patterns=(),
    ),
    FeaturePattern(
        name="G-gents",
        impl_patterns=(),
        spec_patterns=("spec/g-gents/",),
        test_patterns=(),
    ),
    FeaturePattern(
        name="L-gents",
        impl_patterns=(),
        spec_patterns=("spec/l-gents/",),
        test_patterns=(),
    ),
    FeaturePattern(
        name="I-gents",
        impl_patterns=("impl/claude/agents/i/",),
        spec_patterns=("spec/i-gents/",),
        test_patterns=("agents/i/_tests/",),
    ),
)

# All feature patterns combined
FEATURE_PATTERNS: dict[str, FeaturePattern] = {
    fp.name: fp
    for fp in (
        *CROWN_JEWELS,
        *INFRASTRUCTURE,
        *PROTOCOLS,
        *WEB,
        *SPECULATIVE,
    )
}


def get_patterns_by_category() -> dict[str, Sequence[FeaturePattern]]:
    """Get feature patterns organized by category."""
    return {
        "Crown Jewels": CROWN_JEWELS,
        "Infrastructure": INFRASTRUCTURE,
        "Protocols": PROTOCOLS,
        "Web": WEB,
        "Speculative": SPECULATIVE,
    }


def match_file_to_features(file_path: str) -> list[str]:
    """Find which features a file belongs to."""
    return [name for name, pattern in FEATURE_PATTERNS.items() if pattern.matches_file(file_path)]
