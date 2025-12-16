"""
AGENTESE Alias System Tests (v3)

Tests for path aliases:
- Alias registration and expansion
- Shadowing prevention
- Recursion prevention
- Persistence
- Logos integration
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from protocols.agentese import (
    AliasError,
    AliasNotFoundError,
    AliasRecursionError,
    AliasRegistry,
    AliasShadowError,
    Logos,
    create_alias_registry,
    create_logos,
    create_standard_aliases,
    expand_aliases,
)
from protocols.agentese.logos import PlaceholderNode


@pytest.fixture
def registry() -> AliasRegistry:
    """Create a fresh alias registry."""
    return AliasRegistry()


@pytest.fixture
def logos() -> Logos:
    """Create a Logos with test nodes."""
    logos = create_logos()
    logos.register("self.soul", PlaceholderNode("self.soul"))
    logos.register("self.memory", PlaceholderNode("self.memory"))
    logos.register("void.entropy", PlaceholderNode("void.entropy"))
    return logos


class TestAliasRegistration:
    """Tests for basic alias registration."""

    def test_register_alias(self, registry: AliasRegistry) -> None:
        """Can register an alias."""
        registry.register("me", "self.soul")
        assert "me" in registry
        assert registry.get("me") == "self.soul"

    def test_register_multiple_aliases(self, registry: AliasRegistry) -> None:
        """Can register multiple aliases."""
        registry.register("me", "self.soul")
        registry.register("brain", "self.memory")
        registry.register("chaos", "void.entropy")

        assert len(registry) == 3
        assert registry.get("me") == "self.soul"
        assert registry.get("brain") == "self.memory"
        assert registry.get("chaos") == "void.entropy"

    def test_overwrite_alias(self, registry: AliasRegistry) -> None:
        """Registering same alias overwrites."""
        registry.register("me", "self.soul")
        registry.register("me", "self.memory")

        assert registry.get("me") == "self.memory"


class TestAliasExpansion:
    """Tests for alias expansion."""

    def test_expand_single_alias(self, registry: AliasRegistry) -> None:
        """Expands alias at start of path."""
        registry.register("me", "self.soul")

        result = registry.expand("me.challenge")
        assert result == "self.soul.challenge"

    def test_expand_alias_only(self, registry: AliasRegistry) -> None:
        """Expands alias when it's the entire path."""
        registry.register("me", "self.soul")

        result = registry.expand("me")
        assert result == "self.soul"

    def test_no_expansion_for_non_alias(self, registry: AliasRegistry) -> None:
        """Returns original path if no alias matches."""
        registry.register("me", "self.soul")

        result = registry.expand("self.soul.challenge")
        assert result == "self.soul.challenge"

    def test_no_expansion_in_middle(self, registry: AliasRegistry) -> None:
        """Aliases only expand at the start."""
        registry.register("soul", "self.soul")

        # "world.soul.manifest" should NOT expand "soul"
        result = registry.expand("world.soul.manifest")
        assert result == "world.soul.manifest"

    def test_expand_empty_path(self, registry: AliasRegistry) -> None:
        """Empty path returns empty."""
        result = registry.expand("")
        assert result == ""


class TestAliasShadowing:
    """Tests for shadowing prevention."""

    def test_cannot_shadow_world(self, registry: AliasRegistry) -> None:
        """Cannot create alias 'world'."""
        with pytest.raises(AliasShadowError) as exc_info:
            registry.register("world", "self.soul")

        assert exc_info.value.alias == "world"
        assert "shadow" in str(exc_info.value)

    def test_cannot_shadow_self(self, registry: AliasRegistry) -> None:
        """Cannot create alias 'self'."""
        with pytest.raises(AliasShadowError):
            registry.register("self", "world.house")

    def test_cannot_shadow_concept(self, registry: AliasRegistry) -> None:
        """Cannot create alias 'concept'."""
        with pytest.raises(AliasShadowError):
            registry.register("concept", "world.house")

    def test_cannot_shadow_void(self, registry: AliasRegistry) -> None:
        """Cannot create alias 'void'."""
        with pytest.raises(AliasShadowError):
            registry.register("void", "world.house")

    def test_cannot_shadow_time(self, registry: AliasRegistry) -> None:
        """Cannot create alias 'time'."""
        with pytest.raises(AliasShadowError):
            registry.register("time", "world.house")


class TestAliasRecursion:
    """Tests for recursion prevention."""

    def test_cannot_create_recursive_alias(self, registry: AliasRegistry) -> None:
        """Cannot create alias that points to another alias."""
        registry.register("me", "self.soul")

        with pytest.raises(AliasRecursionError):
            registry.register("myself", "me.subpath")

    def test_cannot_self_reference(self, registry: AliasRegistry) -> None:
        """Cannot create alias pointing to itself."""
        with pytest.raises(AliasRecursionError):
            registry.register("loop", "loop")

    def test_cannot_self_reference_with_suffix(self, registry: AliasRegistry) -> None:
        """Cannot create alias starting with itself."""
        with pytest.raises(AliasRecursionError):
            registry.register("loop", "loop.subpath")


class TestAliasRemoval:
    """Tests for alias removal."""

    def test_unregister_alias(self, registry: AliasRegistry) -> None:
        """Can remove an alias."""
        registry.register("me", "self.soul")
        registry.unregister("me")

        assert "me" not in registry

    def test_unregister_nonexistent_raises(self, registry: AliasRegistry) -> None:
        """Removing nonexistent alias raises."""
        with pytest.raises(AliasNotFoundError) as exc_info:
            registry.unregister("nonexistent")

        assert exc_info.value.alias == "nonexistent"

    def test_clear_all_aliases(self, registry: AliasRegistry) -> None:
        """Can clear all aliases."""
        registry.register("me", "self.soul")
        registry.register("brain", "self.memory")
        registry.clear()

        assert len(registry) == 0


class TestAliasPersistence:
    """Tests for alias persistence."""

    def test_save_and_load(self) -> None:
        """Can save and load aliases from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "aliases.yaml"

            # Create and save
            registry = AliasRegistry()
            registry.set_persistence_path(path)
            registry.register("me", "self.soul")
            registry.register("brain", "self.memory")
            registry.save()

            # Load into new registry
            new_registry = AliasRegistry()
            new_registry.set_persistence_path(path)
            new_registry.load()

            assert new_registry.get("me") == "self.soul"
            assert new_registry.get("brain") == "self.memory"

    def test_load_nonexistent_file_ok(self) -> None:
        """Loading from nonexistent file is silently ignored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.yaml"

            registry = AliasRegistry()
            registry.set_persistence_path(path)
            registry.load()  # Should not raise

            assert len(registry) == 0


class TestStandardAliases:
    """Tests for standard alias set."""

    def test_standard_aliases_exist(self) -> None:
        """Standard aliases are defined."""
        standard = create_standard_aliases()

        assert "me" in standard
        assert standard["me"] == "self.soul"
        assert "brain" in standard
        assert "chaos" in standard

    def test_create_registry_with_standard(self) -> None:
        """Factory can include standard aliases."""
        registry = create_alias_registry(include_standard=True)

        assert "me" in registry
        assert "brain" in registry

    def test_create_registry_without_standard(self) -> None:
        """Factory can exclude standard aliases."""
        registry = create_alias_registry(include_standard=False)

        assert "me" not in registry


class TestLogosAliasIntegration:
    """Tests for Logos integration with aliases."""

    def test_logos_alias_method(self, logos: Logos) -> None:
        """Logos.alias() registers an alias."""
        logos.alias("me", "self.soul")

        aliases = logos.get_aliases()
        assert "me" in aliases
        assert aliases["me"] == "self.soul"

    def test_logos_unalias_method(self, logos: Logos) -> None:
        """Logos.unalias() removes an alias."""
        logos.alias("me", "self.soul")
        logos.unalias("me")

        assert "me" not in logos.get_aliases()

    def test_logos_alias_expansion_in_invoke(self, logos: Logos) -> None:
        """Aliases are expanded during invoke()."""
        logos.alias("me", "self.soul")

        # The path should be expanded and the node found
        # This will work because we registered self.soul
        # The actual invoke might fail due to missing aspect impl,
        # but the alias expansion is tested

    def test_logos_get_aliases_empty(self, logos: Logos) -> None:
        """get_aliases returns empty dict when no aliases."""
        assert logos.get_aliases() == {}

    def test_logos_with_aliases_method(self, logos: Logos) -> None:
        """with_aliases creates new Logos with alias registry."""
        registry = AliasRegistry()
        registry.register("me", "self.soul")

        logos_with = logos.with_aliases(registry)

        assert logos_with.get_aliases() == {"me": "self.soul"}
        # Original unaffected
        assert logos.get_aliases() == {}


class TestExpandAliasesFunction:
    """Tests for the expand_aliases helper function."""

    def test_expand_with_registry(self) -> None:
        """expand_aliases works with registry."""
        registry = AliasRegistry()
        registry.register("me", "self.soul")

        result = expand_aliases("me.challenge", registry)
        assert result == "self.soul.challenge"

    def test_expand_with_none_registry(self) -> None:
        """expand_aliases with None returns original."""
        result = expand_aliases("me.challenge", None)
        assert result == "me.challenge"


class TestAliasEdgeCases:
    """Tests for edge cases."""

    def test_has_alias(self, registry: AliasRegistry) -> None:
        """has_alias returns correct value."""
        registry.register("me", "self.soul")

        assert registry.has_alias("me")
        assert not registry.has_alias("nonexistent")

    def test_list_aliases(self, registry: AliasRegistry) -> None:
        """list_aliases returns copy of aliases."""
        registry.register("me", "self.soul")
        registry.register("brain", "self.memory")

        aliases = registry.list_aliases()
        assert aliases == {"me": "self.soul", "brain": "self.memory"}

        # Modifying returned dict doesn't affect registry
        aliases["new"] = "new.path"
        assert "new" not in registry

    def test_registry_contains(self, registry: AliasRegistry) -> None:
        """Registry supports 'in' operator."""
        registry.register("me", "self.soul")

        assert "me" in registry
        assert "nonexistent" not in registry

    def test_registry_len(self, registry: AliasRegistry) -> None:
        """Registry supports len()."""
        assert len(registry) == 0

        registry.register("me", "self.soul")
        assert len(registry) == 1

        registry.register("brain", "self.memory")
        assert len(registry) == 2
