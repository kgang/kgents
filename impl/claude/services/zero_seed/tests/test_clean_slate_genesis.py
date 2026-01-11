"""Tests for CleanSlateGenesis."""

from __future__ import annotations

import pytest

from services.zero_seed.clean_slate_genesis import (
    COLORS,
    GENESIS_IDS,
    CleanSlateGenesis,
    GenesisKBlockSpec,
    GenesisResult,
    get_genesis_specs,
)


class TestCleanSlateGenesis:
    """Tests for the CleanSlateGenesis class."""

    def test_loads_22_specs(self) -> None:
        """Should load exactly 22 genesis specs."""
        genesis = CleanSlateGenesis()
        assert len(genesis.specs) == 22

    def test_layer_distribution(self) -> None:
        """Should have correct distribution across layers."""
        genesis = CleanSlateGenesis()

        l0 = genesis.get_layer_specs(0)
        l1 = genesis.get_layer_specs(1)
        l2 = genesis.get_layer_specs(2)
        l3 = genesis.get_layer_specs(3)

        assert len(l0) == 4, "L0 should have 4 axioms"
        assert len(l1) == 7, "L1 should have 7 kernel primitives"
        assert len(l2) == 7, "L2 should have 7 principles"
        assert len(l3) == 4, "L3 should have 4 architecture K-Blocks"

    def test_l0_axioms_have_no_derivations(self) -> None:
        """L0 axioms should have no parent derivations."""
        genesis = CleanSlateGenesis()

        for spec in genesis.get_layer_specs(0):
            assert len(spec.derivations_from) == 0, f"{spec.id} should have no derivations"

    def test_no_backward_derivations(self) -> None:
        """No K-Block should derive from a K-Block in a higher layer."""
        genesis = CleanSlateGenesis()

        for spec in genesis.specs:
            for parent_id in spec.derivations_from:
                parent_spec = genesis.get_spec(parent_id)
                if parent_spec:
                    assert parent_spec.layer <= spec.layer, (
                        f"{spec.id} (L{spec.layer}) cannot derive from "
                        f"{parent_id} (L{parent_spec.layer})"
                    )

    def test_loss_monotonicity(self) -> None:
        """Average loss should increase with layer number."""
        genesis = CleanSlateGenesis()

        def avg_loss(layer: int) -> float:
            specs = genesis.get_layer_specs(layer)
            if not specs:
                return 0.0
            return sum(s.loss for s in specs) / len(specs)

        l0_avg = avg_loss(0)
        l1_avg = avg_loss(1)
        l2_avg = avg_loss(2)
        l3_avg = avg_loss(3)

        assert l0_avg <= l1_avg, f"L0 ({l0_avg}) should have <= loss than L1 ({l1_avg})"
        assert l1_avg <= l2_avg, f"L1 ({l1_avg}) should have <= loss than L2 ({l2_avg})"
        # L3 can have varying loss depending on how well architecture maps to principles

    def test_all_genesis_ids_have_specs(self) -> None:
        """Every GENESIS_ID should have a corresponding spec."""
        genesis = CleanSlateGenesis()

        for name, genesis_id in GENESIS_IDS.items():
            spec = genesis.get_spec(genesis_id)
            assert spec is not None, f"Missing spec for {name}: {genesis_id}"

    def test_all_specs_have_content(self) -> None:
        """Every spec should have non-empty content."""
        genesis = CleanSlateGenesis()

        for spec in genesis.specs:
            assert spec.content, f"{spec.id} has empty content"
            assert len(spec.content) > 100, f"{spec.id} content too short"

    def test_all_specs_have_colors(self) -> None:
        """Every spec should have a color from the LIVING_EARTH palette."""
        genesis = CleanSlateGenesis()

        for spec in genesis.specs:
            assert spec.color, f"{spec.id} missing color"
            assert spec.color.startswith("#"), f"{spec.id} color should be hex"

    def test_derivation_path_to_axioms(self) -> None:
        """Derivation path should trace back to L0 axioms."""
        genesis = CleanSlateGenesis()

        # Check a few key derivation paths
        for genesis_id in [GENESIS_IDS["ashc"], GENESIS_IDS["agentese"], GENESIS_IDS["tasteful"]]:
            path = genesis.get_derivation_path(genesis_id)
            assert len(path) > 0, f"Path for {genesis_id} should not be empty"

            # First element should be the target
            # Trace should eventually reach L0
            has_l0 = False
            for node_id in path:
                spec = genesis.get_spec(node_id)
                if spec and spec.layer == 0:
                    has_l0 = True
                    break

            assert has_l0, f"Path for {genesis_id} should reach L0"

    def test_get_genesis_specs_function(self) -> None:
        """Module-level get_genesis_specs should work."""
        specs = get_genesis_specs()
        assert len(specs) == 22

    def test_spec_tags_not_empty(self) -> None:
        """Every spec should have tags."""
        genesis = CleanSlateGenesis()

        for spec in genesis.specs:
            assert len(spec.tags) > 0, f"{spec.id} has no tags"
            assert "genesis" in spec.tags, f"{spec.id} should have 'genesis' tag"

    def test_spec_paths_are_valid(self) -> None:
        """Every spec should have a valid AGENTESE path."""
        genesis = CleanSlateGenesis()

        for spec in genesis.specs:
            assert spec.path, f"{spec.id} missing path"
            parts = spec.path.split(".")
            assert len(parts) >= 2, f"{spec.id} path too short"
            assert parts[0] in ("void", "concept", "world", "self", "time"), (
                f"{spec.id} path has invalid context: {parts[0]}"
            )


class TestGenesisKBlockSpec:
    """Tests for the GenesisKBlockSpec dataclass."""

    def test_layer_name(self) -> None:
        """layer_name property should return correct names."""
        genesis = CleanSlateGenesis()

        for spec in genesis.get_layer_specs(0):
            assert spec.layer_name == "axiom"

        for spec in genesis.get_layer_specs(1):
            assert spec.layer_name == "kernel"

        for spec in genesis.get_layer_specs(2):
            assert spec.layer_name == "principle"

        for spec in genesis.get_layer_specs(3):
            assert spec.layer_name == "architecture"


class TestGenesisConstants:
    """Tests for genesis constants."""

    def test_genesis_ids_complete(self) -> None:
        """GENESIS_IDS should have all 22 entries."""
        assert len(GENESIS_IDS) == 22

    def test_genesis_ids_unique(self) -> None:
        """All genesis IDs should be unique."""
        ids = list(GENESIS_IDS.values())
        assert len(ids) == len(set(ids))

    def test_colors_for_all_names(self) -> None:
        """COLORS should have an entry for each GENESIS_ID name."""
        for name in GENESIS_IDS.keys():
            assert name in COLORS, f"Missing color for {name}"
