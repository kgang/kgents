"""
AGENTESE Phase 3: Polymorphic Affordances Tests

Tests for observer-dependent affordance filtering with Umwelt integration.

The key invariants tested:
1. Same path, different observer → different affordances
2. AffordanceError when accessing unavailable aspect
3. Error message lists available affordances
4. manifest() returns archetype-appropriate rendering
"""

import pytest

from ..affordances import (
    CONCEPT_AFFORDANCE_SET,
    # Constants
    STANDARD_ASPECTS,
    VOID_AFFORDANCE_SET,
    # Context sets
    WORLD_AFFORDANCE_SET,
    # DNA
    ArchetypeDNA,
    Aspect,
    # Types
    AspectCategory,
    CapabilityAffordanceMatcher,
    # Matcher
    StandardAffordanceMatcher,
    create_affordance_registry,
    # Adapter
    create_umwelt_adapter,
    get_context_affordance_set,
)
from ..node import AgentMeta
from ..renderings import (
    AdminRendering,
    BasicRendering,
    BlueprintRendering,
    DeveloperRendering,
    EconomicRendering,
    EntropyRendering,
    MemoryRendering,
    PhilosopherRendering,
    PoeticRendering,
    ScientificRendering,
    TemporalRendering,
    create_rendering_factory,
    render_for_archetype,
)
from .conftest import MockUmwelt

# ============================================================
# ASPECT CATEGORY TESTS
# ============================================================


class TestAspectCategory:
    """Tests for AspectCategory enum."""

    def test_all_categories_exist(self) -> None:
        """All six aspect categories exist."""
        categories = [
            AspectCategory.PERCEPTION,
            AspectCategory.MUTATION,
            AspectCategory.COMPOSITION,
            AspectCategory.INTROSPECTION,
            AspectCategory.GENERATION,
            AspectCategory.ENTROPY,
        ]
        assert len(categories) == 6

    def test_categories_are_distinct(self) -> None:
        """Each category is distinct."""
        assert AspectCategory.PERCEPTION != AspectCategory.MUTATION
        assert AspectCategory.MUTATION != AspectCategory.ENTROPY


class TestAspect:
    """Tests for Aspect dataclass."""

    def test_aspect_creation(self) -> None:
        """Can create an aspect."""
        aspect = Aspect(
            name="test",
            category=AspectCategory.PERCEPTION,
            description="A test aspect",
        )
        assert aspect.name == "test"
        assert aspect.category == AspectCategory.PERCEPTION
        assert aspect.description == "A test aspect"
        assert aspect.requires_archetype == ()
        assert aspect.side_effects is False

    def test_aspect_with_archetype_requirement(self) -> None:
        """Aspect can require specific archetypes."""
        aspect = Aspect(
            name="renovate",
            category=AspectCategory.MUTATION,
            requires_archetype=("architect",),
            side_effects=True,
        )
        assert "architect" in aspect.requires_archetype
        assert aspect.side_effects is True

    def test_standard_aspects_exist(self) -> None:
        """Standard aspects are defined."""
        assert "manifest" in STANDARD_ASPECTS
        assert "witness" in STANDARD_ASPECTS
        assert "affordances" in STANDARD_ASPECTS
        assert "refine" in STANDARD_ASPECTS
        assert "sip" in STANDARD_ASPECTS

    def test_manifest_is_perception(self) -> None:
        """manifest is a perception aspect."""
        manifest = STANDARD_ASPECTS["manifest"]
        assert manifest.category == AspectCategory.PERCEPTION

    def test_renovate_requires_architect(self) -> None:
        """renovate requires architect archetype."""
        renovate = STANDARD_ASPECTS["renovate"]
        assert "architect" in renovate.requires_archetype
        assert renovate.side_effects is True


# ============================================================
# AFFORDANCE REGISTRY TESTS
# ============================================================


class TestAffordanceRegistry:
    """Tests for AffordanceRegistry."""

    @pytest.fixture
    def registry(self) -> create_affordance_registry:
        return create_affordance_registry()

    def test_core_affordances_for_default(self, registry) -> None:
        """Default archetype gets core affordances."""
        affordances = registry.get_affordances("default")
        assert "manifest" in affordances
        assert "witness" in affordances
        assert "affordances" in affordances

    def test_architect_gets_extra_affordances(self, registry) -> None:
        """Architect archetype gets extra affordances."""
        affordances = registry.get_affordances("architect")
        assert "manifest" in affordances  # Core
        assert "renovate" in affordances  # Architect-specific
        assert "blueprint" in affordances
        assert "demolish" in affordances

    def test_poet_gets_different_affordances(self, registry) -> None:
        """Poet archetype gets different affordances than architect."""
        architect = set(registry.get_affordances("architect"))
        poet = set(registry.get_affordances("poet"))

        # Both have core
        assert "manifest" in architect
        assert "manifest" in poet

        # Architect has architect stuff
        assert "renovate" in architect
        assert "renovate" not in poet

        # Poet has poet stuff
        assert "metaphorize" in poet
        assert "metaphorize" not in architect

    def test_has_affordance(self, registry) -> None:
        """has_affordance checks correctly."""
        assert registry.has_affordance("architect", "manifest")
        assert registry.has_affordance("architect", "renovate")
        assert not registry.has_affordance("poet", "renovate")
        assert registry.has_affordance("poet", "metaphorize")

    def test_register_new_archetype(self, registry) -> None:
        """Can register a new archetype."""
        registry.register(
            "senior_architect", parents=("architect",), additional=("manage",)
        )

        affordances = registry.get_affordances("senior_architect")
        assert "manifest" in affordances  # Core
        assert "renovate" in affordances  # Inherited from architect
        assert "manage" in affordances  # Additional

    def test_extend_archetype(self, registry) -> None:
        """Can extend existing archetype."""
        registry.extend("architect", ("levitate",))

        affordances = registry.get_affordances("architect")
        assert "levitate" in affordances

    def test_list_archetypes(self, registry) -> None:
        """Can list all archetypes."""
        archetypes = registry.list_archetypes()
        assert "architect" in archetypes
        assert "poet" in archetypes
        assert "scientist" in archetypes
        assert "default" in archetypes

    def test_get_aspect_info(self, registry) -> None:
        """Can get aspect information."""
        aspect = registry.get_aspect_info("manifest")
        assert aspect is not None
        assert aspect.name == "manifest"
        assert aspect.category == AspectCategory.PERCEPTION

        # Unknown aspect returns None
        assert registry.get_aspect_info("nonexistent") is None


# ============================================================
# AFFORDANCE MATCHER TESTS
# ============================================================


class TestStandardAffordanceMatcher:
    """Tests for StandardAffordanceMatcher."""

    @pytest.fixture
    def matcher(self) -> StandardAffordanceMatcher:
        return StandardAffordanceMatcher()

    def test_matches_core_affordances(self, matcher) -> None:
        """Core affordances match for any archetype."""
        assert matcher.matches("default", "manifest")
        assert matcher.matches("architect", "manifest")
        assert matcher.matches("poet", "manifest")

    def test_matches_archetype_specific(self, matcher) -> None:
        """Archetype-specific affordances match correctly."""
        assert matcher.matches("architect", "renovate")
        assert not matcher.matches("poet", "renovate")
        assert matcher.matches("poet", "metaphorize")


class TestCapabilityAffordanceMatcher:
    """Tests for CapabilityAffordanceMatcher."""

    @pytest.fixture
    def matcher(self) -> CapabilityAffordanceMatcher:
        return CapabilityAffordanceMatcher(
            capability_grants={
                "admin_access": ("configure", "provision"),
                "creative": ("metaphorize", "inspire"),
            }
        )

    def test_matches_archetype_affordances(self, matcher) -> None:
        """Still matches archetype affordances."""
        assert matcher.matches("architect", "renovate")

    def test_matches_capability_grants(self, matcher) -> None:
        """Matches capability-granted affordances."""
        # Default archetype doesn't have configure
        assert not matcher.matches("default", "configure", capabilities=())

        # But with admin_access capability, they do
        assert matcher.matches("default", "configure", capabilities=("admin_access",))

    def test_capability_overrides_archetype(self, matcher) -> None:
        """Capability can grant affordances regardless of archetype."""
        # Architect normally can't metaphorize
        assert not matcher.matches("architect", "metaphorize", capabilities=())

        # But with creative capability, they can
        assert matcher.matches("architect", "metaphorize", capabilities=("creative",))


# ============================================================
# ARCHETYPE DNA TESTS
# ============================================================


class TestArchetypeDNA:
    """Tests for ArchetypeDNA."""

    def test_default_dna(self) -> None:
        """Default DNA has default archetype."""
        dna = ArchetypeDNA()
        assert dna.name == "agent"
        assert dna.archetype == "default"
        assert dna.capabilities == ()

    def test_custom_dna(self) -> None:
        """Can create DNA with custom archetype."""
        dna = ArchetypeDNA(
            name="claude",
            archetype="developer",
            capabilities=("test", "deploy"),
        )
        assert dna.name == "claude"
        assert dna.archetype == "developer"
        assert "test" in dna.capabilities

    def test_germinate(self) -> None:
        """Can germinate DNA."""
        dna = ArchetypeDNA.germinate(
            name="claude",
            archetype="scientist",
        )
        assert dna.archetype == "scientist"

    def test_exploration_budget(self) -> None:
        """DNA has exploration budget (Accursed Share)."""
        dna = ArchetypeDNA()
        assert dna.exploration_budget == 0.1

        dna_explorer = ArchetypeDNA(exploration_budget=0.3)
        assert dna_explorer.exploration_budget == 0.3


# ============================================================
# UMWELT ADAPTER TESTS
# ============================================================


class TestUmweltAdapter:
    """Tests for UmweltAdapter."""

    @pytest.fixture
    def adapter(self) -> create_umwelt_adapter:
        return create_umwelt_adapter()

    @pytest.fixture
    def architect_umwelt(self) -> MockUmwelt:
        return MockUmwelt(archetype="architect")

    @pytest.fixture
    def poet_umwelt(self) -> MockUmwelt:
        return MockUmwelt(archetype="poet")

    def test_extract_meta(self, adapter, architect_umwelt) -> None:
        """Can extract AgentMeta from Umwelt."""
        meta = adapter.extract_meta(architect_umwelt)
        assert isinstance(meta, AgentMeta)
        assert meta.archetype == "architect"

    def test_get_affordances(self, adapter, architect_umwelt, poet_umwelt) -> None:
        """Gets correct affordances for different umwelts."""
        architect_affs = adapter.get_affordances(architect_umwelt)
        poet_affs = adapter.get_affordances(poet_umwelt)

        assert "renovate" in architect_affs
        assert "renovate" not in poet_affs
        assert "metaphorize" in poet_affs
        assert "metaphorize" not in architect_affs

    def test_can_invoke(self, adapter, architect_umwelt, poet_umwelt) -> None:
        """can_invoke checks correctly."""
        assert adapter.can_invoke(architect_umwelt, "renovate")
        assert not adapter.can_invoke(poet_umwelt, "renovate")
        assert adapter.can_invoke(poet_umwelt, "metaphorize")
        assert not adapter.can_invoke(architect_umwelt, "metaphorize")

        # Core affordances available to all
        assert adapter.can_invoke(architect_umwelt, "manifest")
        assert adapter.can_invoke(poet_umwelt, "manifest")

    def test_filter_affordances(self, adapter, architect_umwelt) -> None:
        """Can filter affordances to those available."""
        available = ["manifest", "renovate", "metaphorize", "sip"]
        filtered = adapter.filter_affordances(architect_umwelt, available)

        assert "manifest" in filtered
        assert "renovate" in filtered
        assert "metaphorize" not in filtered  # Poet only


# ============================================================
# CONTEXT AFFORDANCE SET TESTS
# ============================================================


class TestContextAffordanceSet:
    """Tests for ContextAffordanceSet."""

    def test_world_affordance_set(self) -> None:
        """World affordance set has correct base."""
        affs = WORLD_AFFORDANCE_SET.get_for_archetype("default")
        assert "manifest" in affs
        assert "witness" in affs
        assert "define" in affs

    def test_void_affordance_set_universal(self) -> None:
        """Void affordances are the same for all archetypes."""
        architect = VOID_AFFORDANCE_SET.get_for_archetype("architect")
        poet = VOID_AFFORDANCE_SET.get_for_archetype("poet")
        default = VOID_AFFORDANCE_SET.get_for_archetype("default")

        # All should have sip, pour, tithe, thank
        for affs in [architect, poet, default]:
            assert "sip" in affs
            assert "pour" in affs
            assert "tithe" in affs
            assert "thank" in affs

    def test_concept_philosopher_affordances(self) -> None:
        """Philosopher gets dialectical affordances for concepts."""
        affs = CONCEPT_AFFORDANCE_SET.get_for_archetype("philosopher")
        assert "refine" in affs
        assert "dialectic" in affs
        assert "synthesize" in affs
        assert "critique" in affs

    def test_get_context_affordance_set(self) -> None:
        """Can get affordance set by context name."""
        world_set = get_context_affordance_set("world")
        assert world_set is WORLD_AFFORDANCE_SET

        void_set = get_context_affordance_set("void")
        assert void_set is VOID_AFFORDANCE_SET


# ============================================================
# RENDERING TESTS
# ============================================================


class TestRenderings:
    """Tests for polymorphic renderings."""

    def test_basic_rendering(self) -> None:
        """BasicRendering works."""
        r = BasicRendering(summary="Test", content="Content")
        assert r.summary == "Test"
        assert "Test" in r.to_text()
        assert r.to_dict()["summary"] == "Test"

    def test_blueprint_rendering(self) -> None:
        """BlueprintRendering for architects."""
        r = BlueprintRendering(
            dimensions={"width": 10, "height": 8},
            materials=("wood", "stone"),
        )
        assert "BLUEPRINT" in r.to_text()
        assert r.to_dict()["type"] == "blueprint"

    def test_poetic_rendering(self) -> None:
        """PoeticRendering for poets."""
        r = PoeticRendering(
            description="A shelter against the storm",
            metaphors=("home is a harbor",),
            mood="wistful",
        )
        assert r.mood == "wistful"
        assert "wistful" in r.to_text().lower()

    def test_economic_rendering(self) -> None:
        """EconomicRendering for economists."""
        r = EconomicRendering(
            market_value=500000.0,
            appreciation_forecast={"1y": 0.05},
        )
        assert "$500,000" in r.to_text()
        assert r.to_dict()["market_value"] == 500000.0

    def test_scientific_rendering(self) -> None:
        """ScientificRendering for scientists."""
        r = ScientificRendering(
            entity="house",
            measurements={"area_sqm": 150},
            observations=("located in valley", "south-facing"),
            confidence=0.85,
        )
        assert "SCIENTIFIC ANALYSIS" in r.to_text()
        assert "85" in r.to_text()  # Could be "85.00%" or "85%"

    def test_developer_rendering(self) -> None:
        """DeveloperRendering for developers."""
        r = DeveloperRendering(
            entity="app",
            language="python",
            build_status="passing",
            test_coverage=0.87,
        )
        assert "TECHNICAL" in r.to_text()
        assert "python" in r.to_text().lower()

    def test_admin_rendering(self) -> None:
        """AdminRendering for admins."""
        r = AdminRendering(
            entity="server",
            status="healthy",
            health=0.95,
            alerts=("high memory usage",),
        )
        assert "SYSTEM" in r.to_text()
        assert "healthy" in r.to_text()

    def test_philosopher_rendering(self) -> None:
        """PhilosopherRendering for philosophers."""
        r = PhilosopherRendering(
            concept="justice",
            definition="The quality of being fair",
            thesis="Justice is fairness",
            antithesis="Justice is mere convention",
            synthesis="Justice is both natural and constructed",
            related_concepts=("fairness", "equality"),
        )
        assert "CONCEPT" in r.to_text()
        assert "justice" in r.to_text().lower()
        assert "thesis" in r.to_text().lower()

    def test_memory_rendering(self) -> None:
        """MemoryRendering for self.memory."""
        r = MemoryRendering(
            memory_count=100,
            consolidated=80,
            temporary=20,
            capacity_used=0.1,
        )
        assert "MEMORY STATE" in r.to_text()
        assert "100" in r.to_text()

    def test_entropy_rendering(self) -> None:
        """EntropyRendering for void.entropy."""
        r = EntropyRendering(
            remaining=75.0,
            total=100.0,
            history_length=10,
        )
        assert "ACCURSED SHARE" in r.to_text()
        assert "75" in r.to_text()

    def test_temporal_rendering(self) -> None:
        """TemporalRendering for time.trace."""
        r = TemporalRendering(
            trace_count=50,
            scheduled_count=3,
        )
        assert "TEMPORAL" in r.to_text()
        assert "50" in r.to_text()


class TestStandardRenderingFactory:
    """Tests for StandardRenderingFactory."""

    @pytest.fixture
    def factory(self) -> create_rendering_factory:
        return create_rendering_factory()

    def test_creates_blueprint_for_architect(self, factory) -> None:
        """Creates BlueprintRendering for architect."""
        r = factory.create("architect", "house", {"dimensions": {"w": 10}})
        assert isinstance(r, BlueprintRendering)

    def test_creates_poetic_for_poet(self, factory) -> None:
        """Creates PoeticRendering for poet."""
        r = factory.create("poet", "house", {})
        assert isinstance(r, PoeticRendering)

    def test_creates_economic_for_economist(self, factory) -> None:
        """Creates EconomicRendering for economist."""
        r = factory.create("economist", "house", {"value": 500000})
        assert isinstance(r, EconomicRendering)

    def test_creates_scientific_for_scientist(self, factory) -> None:
        """Creates ScientificRendering for scientist."""
        r = factory.create("scientist", "house", {})
        assert isinstance(r, ScientificRendering)

    def test_creates_developer_for_developer(self, factory) -> None:
        """Creates DeveloperRendering for developer."""
        r = factory.create("developer", "app", {})
        assert isinstance(r, DeveloperRendering)

    def test_creates_admin_for_admin(self, factory) -> None:
        """Creates AdminRendering for admin."""
        r = factory.create("admin", "server", {})
        assert isinstance(r, AdminRendering)

    def test_creates_philosopher_for_philosopher(self, factory) -> None:
        """Creates PhilosopherRendering for philosopher."""
        r = factory.create("philosopher", "justice", {})
        assert isinstance(r, PhilosopherRendering)

    def test_creates_basic_for_unknown(self, factory) -> None:
        """Creates BasicRendering for unknown archetype."""
        r = factory.create("unknown_archetype", "entity", {})
        assert isinstance(r, BasicRendering)

    def test_render_for_archetype_helper(self) -> None:
        """render_for_archetype helper works."""
        r = render_for_archetype("poet", "sunset", {})
        assert isinstance(r, PoeticRendering)


# ============================================================
# INTEGRATION: POLYMORPHIC MANIFEST TESTS
# ============================================================


class TestPolymorphicManifest:
    """Integration tests for polymorphic manifest()."""

    @pytest.mark.asyncio
    async def test_world_node_architect_manifest(self) -> None:
        """WorldNode.manifest returns BlueprintRendering for architect."""
        from ..contexts.world import create_world_node

        node = create_world_node(
            name="house",
            state={"dimensions": {"width": 10}},
        )
        observer = MockUmwelt(archetype="architect")

        result = await node.manifest(observer)
        assert isinstance(result, BlueprintRendering)

    @pytest.mark.asyncio
    async def test_world_node_poet_manifest(self) -> None:
        """WorldNode.manifest returns PoeticRendering for poet."""
        from ..contexts.world import create_world_node

        node = create_world_node(name="house")
        observer = MockUmwelt(archetype="poet")

        result = await node.manifest(observer)
        assert isinstance(result, PoeticRendering)

    @pytest.mark.asyncio
    async def test_world_node_economist_manifest(self) -> None:
        """WorldNode.manifest returns EconomicRendering for economist."""
        from ..contexts.world import create_world_node

        node = create_world_node(
            name="house",
            state={"value": 500000},
        )
        observer = MockUmwelt(archetype="economist")

        result = await node.manifest(observer)
        assert isinstance(result, EconomicRendering)

    @pytest.mark.asyncio
    async def test_world_node_scientist_manifest(self) -> None:
        """WorldNode.manifest returns ScientificRendering for scientist."""
        from ..contexts.world import create_world_node

        node = create_world_node(name="house")
        observer = MockUmwelt(archetype="scientist")

        result = await node.manifest(observer)
        assert isinstance(result, ScientificRendering)

    @pytest.mark.asyncio
    async def test_world_node_developer_manifest(self) -> None:
        """WorldNode.manifest returns DeveloperRendering for developer."""
        from ..contexts.world import create_world_node

        node = create_world_node(name="app")
        observer = MockUmwelt(archetype="developer")

        result = await node.manifest(observer)
        assert isinstance(result, DeveloperRendering)

    @pytest.mark.asyncio
    async def test_world_node_admin_manifest(self) -> None:
        """WorldNode.manifest returns AdminRendering for admin."""
        from ..contexts.world import create_world_node

        node = create_world_node(name="server")
        observer = MockUmwelt(archetype="admin")

        result = await node.manifest(observer)
        assert isinstance(result, AdminRendering)

    @pytest.mark.asyncio
    async def test_world_node_default_manifest(self) -> None:
        """WorldNode.manifest returns BasicRendering for default."""
        from ..contexts.world import create_world_node

        node = create_world_node(name="house")
        observer = MockUmwelt(archetype="default")

        result = await node.manifest(observer)
        assert isinstance(result, BasicRendering)

    @pytest.mark.asyncio
    async def test_concept_node_philosopher_manifest(self) -> None:
        """ConceptNode.manifest returns PhilosopherRendering for philosopher."""
        from ..contexts.concept import create_concept_node

        node = create_concept_node(
            name="justice",
            definition="The quality of being fair",
        )
        observer = MockUmwelt(archetype="philosopher")

        result = await node.manifest(observer)
        assert isinstance(result, PhilosopherRendering)
        assert "justice" in result.concept

    @pytest.mark.asyncio
    async def test_concept_node_scientist_manifest(self) -> None:
        """ConceptNode.manifest returns ScientificRendering for scientist."""
        from ..contexts.concept import create_concept_node

        node = create_concept_node(name="entropy")
        observer = MockUmwelt(archetype="scientist")

        result = await node.manifest(observer)
        assert isinstance(result, ScientificRendering)


# ============================================================
# INTEGRATION: AFFORDANCE ERROR TESTS
# ============================================================


class TestAffordanceErrors:
    """Tests for affordance error handling."""

    @pytest.mark.asyncio
    async def test_logos_rejects_unavailable_affordance(self) -> None:
        """Logos.invoke raises AffordanceError for unavailable aspects."""
        from ..exceptions import AffordanceError
        from ..logos import create_logos

        logos = create_logos()
        poet_umwelt = MockUmwelt(archetype="poet")

        # Poet cannot renovate
        with pytest.raises(AffordanceError) as exc_info:
            await logos.invoke("world.house.renovate", poet_umwelt)

        # Error message should list available affordances
        error = exc_info.value
        assert "renovate" in str(error)
        assert "poet" in str(error).lower() or "Your affordances" in str(error)

    @pytest.mark.asyncio
    async def test_affordance_error_suggests_alternatives(self) -> None:
        """AffordanceError suggests what the observer can do."""
        from ..exceptions import AffordanceError

        error = AffordanceError(
            "Aspect 'renovate' not available to poet",
            aspect="renovate",
            observer_archetype="poet",
            available=["manifest", "witness", "describe", "metaphorize"],
        )

        error_str = str(error)
        assert "renovate" in error_str
        # Should mention available affordances
        assert any(aff in error_str for aff in ["manifest", "describe", "metaphorize"])


# ============================================================
# INTEGRATION: LOGOS WITH AFFORDANCES TESTS
# ============================================================


class TestLogosWithAffordances:
    """Integration tests for Logos with affordance filtering."""

    @pytest.fixture
    def logos(self) -> "Logos":
        from ..logos import create_logos

        return create_logos()

    @pytest.mark.asyncio
    async def test_same_path_different_observer_different_result(self, logos) -> None:
        """Same path yields different results for different observers."""
        architect = MockUmwelt(archetype="architect")
        poet = MockUmwelt(archetype="poet")

        arch_result = await logos.invoke("world.house.manifest", architect)
        poet_result = await logos.invoke("world.house.manifest", poet)

        assert type(arch_result) != type(poet_result)
        assert isinstance(arch_result, BlueprintRendering)
        assert isinstance(poet_result, PoeticRendering)

    @pytest.mark.asyncio
    async def test_architect_can_renovate(self, logos) -> None:
        """Architect can invoke renovate aspect."""
        architect = MockUmwelt(archetype="architect")

        # Should not raise
        result = await logos.invoke(
            "world.house.transform", architect, changes={"roof": "new"}
        )
        assert "transformed" in result

    @pytest.mark.asyncio
    async def test_void_available_to_all(self, logos) -> None:
        """Void aspects are available to all archetypes."""
        archetypes = ["default", "architect", "poet", "scientist"]

        for archetype in archetypes:
            observer = MockUmwelt(archetype=archetype)
            # All should be able to sip entropy
            result = await logos.invoke("void.entropy.sip", observer, amount=1.0)
            assert "seed" in result
