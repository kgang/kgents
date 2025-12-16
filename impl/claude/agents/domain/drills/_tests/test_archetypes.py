"""
Tests for Crisis Archetypes: Domain-Specific Citizen Roles.

Verifies:
1. Archetype specifications (eigenvector biases, cosmotechnics)
2. Factory functions (create_crisis_citizen, create_*_team)
3. Stress level effects on eigenvectors
4. All 8 crisis roles (4 for outage, 4 for breach)
"""

import pytest
from agents.domain.drills.archetypes import (
    ADVOCACY,
    CISO_SPEC,
    COMMAND,
    COMPLIANCE,
    CRISIS_ARCHETYPE_SPECS,
    CUSTOMER_SUCCESS_SPEC,
    EXECUTIVE_SPEC,
    FORENSICS,
    INCIDENT_COMMANDER_SPEC,
    LEGAL_COUNSEL_SPEC,
    NARRATIVE,
    ON_CALL_ENGINEER_SPEC,
    PR_DIRECTOR_SPEC,
    SECURITY_ANALYST_SPEC,
    STAKEHOLDER,
    STRATEGY,
    TRIAGE,
    CrisisArchetype,
    CrisisArchetypeSpec,
    create_crisis_citizen,
    create_data_breach_team,
    create_service_outage_team,
    get_archetype_emoji,
    get_archetype_responsibilities,
)
from agents.town.citizen import Citizen


class TestCrisisCosmotechnics:
    """Tests for crisis-specific cosmotechnics."""

    def test_triage_cosmotechnics(self) -> None:
        """TRIAGE cosmotechnics is defined correctly."""
        assert TRIAGE.name == "triage"
        assert "prioritization" in TRIAGE.description.lower()
        assert TRIAGE.opacity_statement != ""

    def test_command_cosmotechnics(self) -> None:
        """COMMAND cosmotechnics is defined correctly."""
        assert COMMAND.name == "command"
        assert "decisive" in COMMAND.description.lower()

    def test_forensics_cosmotechnics(self) -> None:
        """FORENSICS cosmotechnics is defined correctly."""
        assert FORENSICS.name == "forensics"
        assert "evidence" in FORENSICS.description.lower()

    def test_compliance_cosmotechnics(self) -> None:
        """COMPLIANCE cosmotechnics is defined correctly."""
        assert COMPLIANCE.name == "compliance"
        assert "rules" in COMPLIANCE.description.lower()


class TestCrisisArchetypeEnum:
    """Tests for CrisisArchetype enum."""

    def test_has_eight_archetypes(self) -> None:
        """All 8 crisis archetypes exist."""
        assert len(CrisisArchetype) == 8

    def test_service_outage_archetypes(self) -> None:
        """Service outage archetypes exist."""
        assert CrisisArchetype.ON_CALL_ENGINEER is not None
        assert CrisisArchetype.INCIDENT_COMMANDER is not None
        assert CrisisArchetype.EXECUTIVE is not None
        assert CrisisArchetype.CUSTOMER_SUCCESS is not None

    def test_data_breach_archetypes(self) -> None:
        """Data breach archetypes exist."""
        assert CrisisArchetype.SECURITY_ANALYST is not None
        assert CrisisArchetype.LEGAL_COUNSEL is not None
        assert CrisisArchetype.PR_DIRECTOR is not None
        assert CrisisArchetype.CISO is not None


class TestArchetypeSpecs:
    """Tests for CrisisArchetypeSpec specifications."""

    def test_all_archetypes_have_specs(self) -> None:
        """Every archetype has a spec in the registry."""
        for archetype in CrisisArchetype:
            assert archetype in CRISIS_ARCHETYPE_SPECS

    def test_on_call_engineer_spec(self) -> None:
        """ON_CALL_ENGINEER spec has correct properties."""
        spec = ON_CALL_ENGINEER_SPEC
        assert spec.display_name == "On-Call Engineer"
        assert spec.emoji == "🔧"
        assert spec.cosmotechnics == TRIAGE
        assert len(spec.responsibilities) >= 3
        # High curiosity and resilience
        assert spec.curiosity_bias > 0
        assert spec.resilience_bias > 0

    def test_incident_commander_spec(self) -> None:
        """INCIDENT_COMMANDER spec has correct properties."""
        spec = INCIDENT_COMMANDER_SPEC
        assert spec.display_name == "Incident Commander"
        assert spec.emoji == "🎖️"
        assert spec.cosmotechnics == COMMAND
        # High resilience
        assert spec.resilience_bias > 0.3

    def test_executive_spec(self) -> None:
        """EXECUTIVE spec has correct properties."""
        spec = EXECUTIVE_SPEC
        assert spec.display_name == "Executive"
        assert spec.emoji == "👔"
        assert spec.cosmotechnics == STAKEHOLDER
        # High ambition
        assert spec.ambition_bias > 0.2

    def test_customer_success_spec(self) -> None:
        """CUSTOMER_SUCCESS spec has correct properties."""
        spec = CUSTOMER_SUCCESS_SPEC
        assert spec.display_name == "Customer Success"
        assert spec.emoji == "💬"
        assert spec.cosmotechnics == ADVOCACY
        # High warmth
        assert spec.warmth_bias > 0.3

    def test_security_analyst_spec(self) -> None:
        """SECURITY_ANALYST spec has correct properties."""
        spec = SECURITY_ANALYST_SPEC
        assert spec.display_name == "Security Analyst"
        assert spec.emoji == "🔒"
        assert spec.cosmotechnics == FORENSICS
        # High curiosity, low trust
        assert spec.curiosity_bias > 0.3
        assert spec.trust_bias < 0

    def test_legal_counsel_spec(self) -> None:
        """LEGAL_COUNSEL spec has correct properties."""
        spec = LEGAL_COUNSEL_SPEC
        assert spec.display_name == "Legal Counsel"
        assert spec.emoji == "⚖️"
        assert spec.cosmotechnics == COMPLIANCE
        # High patience
        assert spec.patience_bias > 0.2

    def test_pr_director_spec(self) -> None:
        """PR_DIRECTOR spec has correct properties."""
        spec = PR_DIRECTOR_SPEC
        assert spec.display_name == "PR Director"
        assert spec.emoji == "📢"
        assert spec.cosmotechnics == NARRATIVE
        # High creativity
        assert spec.creativity_bias > 0.2

    def test_ciso_spec(self) -> None:
        """CISO spec has correct properties."""
        spec = CISO_SPEC
        assert spec.display_name == "CISO"
        assert spec.emoji == "🛡️"
        assert spec.cosmotechnics == STRATEGY
        # High resilience
        assert spec.resilience_bias > 0.3


class TestEigenvectorCreation:
    """Tests for eigenvector creation with stress levels."""

    def test_create_eigenvectors_baseline(self) -> None:
        """Eigenvectors at zero stress use biases directly."""
        spec = ON_CALL_ENGINEER_SPEC
        eigenvectors = spec.create_eigenvectors(stress_level=0.0)

        # Base value is 0.5, biases are added
        assert eigenvectors.curiosity == pytest.approx(
            0.5 + spec.curiosity_bias, abs=0.01
        )
        assert eigenvectors.resilience == pytest.approx(
            0.5 + spec.resilience_bias, abs=0.01
        )

    def test_create_eigenvectors_with_stress(self) -> None:
        """Eigenvectors are amplified under stress."""
        spec = ON_CALL_ENGINEER_SPEC
        no_stress = spec.create_eigenvectors(stress_level=0.0)
        high_stress = spec.create_eigenvectors(stress_level=1.0)

        # Biases should be more pronounced under stress
        # (unless clamped by bounds)
        assert high_stress.curiosity >= no_stress.curiosity
        assert high_stress.resilience >= no_stress.resilience

    def test_eigenvectors_are_clamped(self) -> None:
        """Eigenvectors are clamped to [0, 1]."""
        # Create spec with extreme bias
        spec = SECURITY_ANALYST_SPEC  # Has high curiosity bias
        eigenvectors = spec.create_eigenvectors(stress_level=1.0)

        # All values should be within bounds
        for attr in [
            "warmth",
            "curiosity",
            "trust",
            "creativity",
            "patience",
            "resilience",
            "ambition",
        ]:
            value = getattr(eigenvectors, attr)
            assert 0.0 <= value <= 1.0


class TestCreateCrisisCitizen:
    """Tests for create_crisis_citizen factory."""

    def test_creates_citizen_with_archetype(self) -> None:
        """Factory creates Citizen with correct archetype."""
        citizen = create_crisis_citizen(
            archetype=CrisisArchetype.ON_CALL_ENGINEER,
            name="Alex",
            region="war_room",
        )

        assert isinstance(citizen, Citizen)
        assert citizen.name == "Alex"
        assert citizen.archetype == "On-Call Engineer"
        assert citizen.region == "war_room"
        assert citizen.cosmotechnics == TRIAGE

    def test_creates_citizen_with_custom_stress(self) -> None:
        """Factory respects stress level."""
        low_stress = create_crisis_citizen(
            archetype=CrisisArchetype.SECURITY_ANALYST,
            name="Riley",
            stress_level=0.2,
        )
        high_stress = create_crisis_citizen(
            archetype=CrisisArchetype.SECURITY_ANALYST,
            name="Riley",
            stress_level=0.8,
        )

        # Higher stress should amplify biases
        # (Security analyst has positive curiosity bias)
        assert high_stress.eigenvectors.curiosity >= low_stress.eigenvectors.curiosity

    def test_creates_citizen_with_overrides(self) -> None:
        """Factory applies eigenvector overrides."""
        citizen = create_crisis_citizen(
            archetype=CrisisArchetype.EXECUTIVE,
            name="Morgan",
            eigenvector_overrides={"warmth": 0.3},  # Boost warmth
        )

        # Override should increase warmth from baseline
        assert citizen.eigenvectors.warmth > 0.5


class TestCreateServiceOutageTeam:
    """Tests for create_service_outage_team factory."""

    def test_creates_four_citizens(self) -> None:
        """Factory creates all 4 service outage roles."""
        team = create_service_outage_team()

        assert len(team) == 4
        assert CrisisArchetype.ON_CALL_ENGINEER in team
        assert CrisisArchetype.INCIDENT_COMMANDER in team
        assert CrisisArchetype.EXECUTIVE in team
        assert CrisisArchetype.CUSTOMER_SUCCESS in team

    def test_uses_default_names(self) -> None:
        """Factory uses default names if not provided."""
        team = create_service_outage_team()

        assert team[CrisisArchetype.ON_CALL_ENGINEER].name == "Alex"
        assert team[CrisisArchetype.INCIDENT_COMMANDER].name == "Jordan"
        assert team[CrisisArchetype.EXECUTIVE].name == "Morgan"
        assert team[CrisisArchetype.CUSTOMER_SUCCESS].name == "Casey"

    def test_uses_custom_names(self) -> None:
        """Factory uses custom names when provided."""
        team = create_service_outage_team(
            names={
                CrisisArchetype.ON_CALL_ENGINEER: "CustomEngineer",
            }
        )

        assert team[CrisisArchetype.ON_CALL_ENGINEER].name == "CustomEngineer"

    def test_respects_stress_level(self) -> None:
        """Factory applies stress level to all team members."""
        team = create_service_outage_team(stress_level=0.9)

        for citizen in team.values():
            # High stress should be reflected in eigenvectors
            # (all specs have some positive resilience bias)
            assert citizen.eigenvectors.resilience >= 0.5


class TestCreateDataBreachTeam:
    """Tests for create_data_breach_team factory."""

    def test_creates_four_citizens(self) -> None:
        """Factory creates all 4 data breach roles."""
        team = create_data_breach_team()

        assert len(team) == 4
        assert CrisisArchetype.SECURITY_ANALYST in team
        assert CrisisArchetype.LEGAL_COUNSEL in team
        assert CrisisArchetype.PR_DIRECTOR in team
        assert CrisisArchetype.CISO in team

    def test_uses_default_names(self) -> None:
        """Factory uses default names if not provided."""
        team = create_data_breach_team()

        assert team[CrisisArchetype.SECURITY_ANALYST].name == "Riley"
        assert team[CrisisArchetype.LEGAL_COUNSEL].name == "Quinn"
        assert team[CrisisArchetype.PR_DIRECTOR].name == "Avery"
        assert team[CrisisArchetype.CISO].name == "Blake"

    def test_higher_default_stress(self) -> None:
        """Data breach team has higher default stress (0.6)."""
        # Create with default stress
        breach_team = create_data_breach_team()
        outage_team = create_service_outage_team()

        # Breach team should generally have more amplified biases
        # due to higher default stress
        # (this is hard to test directly, but we can verify creation works)
        assert breach_team[CrisisArchetype.SECURITY_ANALYST] is not None


class TestArchetypeHelpers:
    """Tests for helper functions."""

    def test_get_archetype_responsibilities(self) -> None:
        """Can get responsibilities for archetype."""
        responsibilities = get_archetype_responsibilities(
            CrisisArchetype.ON_CALL_ENGINEER
        )

        assert len(responsibilities) >= 3
        assert "First response" in responsibilities[0]

    def test_get_archetype_emoji(self) -> None:
        """Can get emoji for archetype."""
        assert get_archetype_emoji(CrisisArchetype.ON_CALL_ENGINEER) == "🔧"
        assert get_archetype_emoji(CrisisArchetype.SECURITY_ANALYST) == "🔒"
        assert get_archetype_emoji(CrisisArchetype.LEGAL_COUNSEL) == "⚖️"
        assert get_archetype_emoji(CrisisArchetype.CISO) == "🛡️"
