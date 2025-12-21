"""
Tests for Projector Laws.

The Alethic Projection Protocol requires all projectors to satisfy
three categorical laws:

1. Determinism: Same input → same output
2. Capability Preservation: Halo capabilities map to target features
3. Empty Halo Identity: No capabilities → minimal agent

These tests verify these laws across all projector implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from hypothesis import given, settings, strategies as st

from agents.a.halo import (
    Capability,
    CapabilityBase,
    ObservableCapability,
    SoulfulCapability,
    StatefulCapability,
    StreamableCapability,
    TurnBasedCapability,
    get_halo,
)
from agents.poly.types import Agent
from system.projector import CLIProjector, K8sProjector, LocalProjector
from system.projector.base import UnsupportedCapabilityError
from system.projector.local import (
    SoulfulAdapter,
    StatefulAdapter,
    TurnBasedAdapter,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Test Agent Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


class PlainAgent(Agent[str, str]):
    """Agent with no capabilities (empty Halo)."""

    @property
    def name(self) -> str:
        return "plain"

    async def invoke(self, input: str) -> str:
        return f"plain:{input}"


@Capability.Stateful(schema=dict)
class StatefulOnlyAgent(Agent[str, str]):
    """Agent with only @Stateful."""

    @property
    def name(self) -> str:
        return "stateful-only"

    async def invoke(self, input: str) -> str:
        return f"stateful:{input}"


@Capability.Soulful(persona="Test")
class SoulfulOnlyAgent(Agent[str, str]):
    """Agent with only @Soulful."""

    @property
    def name(self) -> str:
        return "soulful-only"

    async def invoke(self, input: str) -> str:
        return f"soulful:{input}"


@Capability.Observable(mirror=True, metrics=True)
class ObservableOnlyAgent(Agent[str, str]):
    """Agent with only @Observable."""

    @property
    def name(self) -> str:
        return "observable-only"

    async def invoke(self, input: str) -> str:
        return f"observable:{input}"


@Capability.Streamable(budget=5.0)
class StreamableOnlyAgent(Agent[str, str]):
    """Agent with only @Streamable."""

    @property
    def name(self) -> str:
        return "streamable-only"

    async def invoke(self, input: str) -> str:
        return f"streamable:{input}"


@Capability.TurnBased(entropy_budget=1.0)
class TurnBasedOnlyAgent(Agent[str, str]):
    """Agent with only @TurnBased."""

    @property
    def name(self) -> str:
        return "turnbased-only"

    async def invoke(self, input: str) -> str:
        return f"turnbased:{input}"


@Capability.Stateful(schema=dict)
@Capability.Soulful(persona="AllCaps")
@Capability.Observable(mirror=True, metrics=True)
@Capability.Streamable(budget=10.0)
class FullStackAgent(Agent[str, str]):
    """Agent with all four main capabilities."""

    @property
    def name(self) -> str:
        return "full-stack"

    async def invoke(self, input: str) -> str:
        return f"full-stack:{input}"


@dataclass(frozen=True)
class UnsupportedCapability(CapabilityBase):
    """Custom capability not supported by any projector."""

    custom_field: str = "custom"


@UnsupportedCapability(custom_field="test")
class UnsupportedCapAgent(Agent[str, str]):
    """Agent with unsupported capability."""

    @property
    def name(self) -> str:
        return "unsupported"

    async def invoke(self, input: str) -> str:
        return input


# ═══════════════════════════════════════════════════════════════════════════════
# Law 1: Determinism Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDeterminismLaw:
    """
    Law 1: Determinism - Same input → same output.

    For any projector P and agent class A:
        P.compile(A) == P.compile(A)  (structurally)
    """

    def test_local_projector_determinism_plain(self) -> None:
        """LocalProjector produces same result for plain agent."""
        p = LocalProjector()
        r1 = p.compile(PlainAgent)
        r2 = p.compile(PlainAgent)

        assert type(r1) == type(r2)
        assert r1.name == r2.name

    def test_local_projector_determinism_stateful(self) -> None:
        """LocalProjector produces same result for stateful agent."""
        p = LocalProjector()
        r1 = p.compile(StatefulOnlyAgent)
        r2 = p.compile(StatefulOnlyAgent)

        assert type(r1) == type(r2)
        assert isinstance(r1, StatefulAdapter)
        assert isinstance(r2, StatefulAdapter)

    def test_local_projector_determinism_full_stack(self) -> None:
        """LocalProjector produces same result for full-stack agent."""
        p = LocalProjector()
        r1 = p.compile(FullStackAgent)
        r2 = p.compile(FullStackAgent)

        assert type(r1) == type(r2)
        # Both should be FluxAgent wrapping the same structure
        assert type(r1.inner) == type(r2.inner)

    def test_k8s_projector_determinism_plain(self) -> None:
        """K8sProjector produces same result for plain agent."""
        p = K8sProjector()
        r1 = p.compile(PlainAgent)
        r2 = p.compile(PlainAgent)

        assert len(r1) == len(r2)
        for res1, res2 in zip(r1, r2, strict=True):
            assert res1.kind == res2.kind
            assert res1.metadata["name"] == res2.metadata["name"]

    def test_k8s_projector_determinism_full_stack(self) -> None:
        """K8sProjector produces same manifests for full-stack agent."""
        p = K8sProjector()
        r1 = p.compile(FullStackAgent)
        r2 = p.compile(FullStackAgent)

        kinds1 = sorted(r.kind for r in r1)
        kinds2 = sorted(r.kind for r in r2)
        assert kinds1 == kinds2

    def test_cli_projector_determinism_plain(self) -> None:
        """CLIProjector produces same script for plain agent."""
        p = CLIProjector()
        r1 = p.compile(PlainAgent)
        r2 = p.compile(PlainAgent)

        assert r1 == r2  # Script strings should be identical

    def test_cli_projector_determinism_full_stack(self) -> None:
        """CLIProjector produces same script for full-stack agent."""
        p = CLIProjector()
        r1 = p.compile(FullStackAgent)
        r2 = p.compile(FullStackAgent)

        assert r1 == r2


# ═══════════════════════════════════════════════════════════════════════════════
# Law 2: Capability Preservation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCapabilityPreservationLaw:
    """
    Law 2: Capability Preservation - Halo capabilities map to target features.

    For any projector P, agent A with capability C:
        P.compile(A) has feature corresponding to C
    """

    # ───────────────────────────────────────────────────────────────────────────
    # LocalProjector Capability Preservation
    # ───────────────────────────────────────────────────────────────────────────

    def test_local_stateful_has_state(self) -> None:
        """@Stateful → StatefulAdapter with state property."""
        compiled = LocalProjector().compile(StatefulOnlyAgent)

        assert isinstance(compiled, StatefulAdapter)
        assert hasattr(compiled, "state")
        assert hasattr(compiled, "update_state")

    def test_local_soulful_has_persona(self) -> None:
        """@Soulful → SoulfulAdapter with persona property."""
        compiled = LocalProjector().compile(SoulfulOnlyAgent)

        assert isinstance(compiled, SoulfulAdapter)
        assert hasattr(compiled, "persona")
        assert compiled.persona_name == "Test"

    def test_local_streamable_is_flux(self) -> None:
        """@Streamable → FluxAgent with entropy budget."""
        from agents.flux import FluxAgent

        compiled = LocalProjector().compile(StreamableOnlyAgent)

        assert isinstance(compiled, FluxAgent)
        assert compiled.config.entropy_budget == 5.0

    def test_local_turnbased_has_weave(self) -> None:
        """@TurnBased → TurnBasedAdapter with weave access."""
        compiled = LocalProjector().compile(TurnBasedOnlyAgent)

        assert isinstance(compiled, TurnBasedAdapter)
        assert hasattr(compiled, "weave")
        assert hasattr(compiled, "get_context")
        assert hasattr(compiled, "record_turn")

    # ───────────────────────────────────────────────────────────────────────────
    # K8sProjector Capability Preservation
    # ───────────────────────────────────────────────────────────────────────────

    def test_k8s_stateful_has_statefulset(self) -> None:
        """@Stateful → StatefulSet + PVC."""
        resources = K8sProjector().compile(StatefulOnlyAgent)

        kinds = {r.kind for r in resources}
        assert "StatefulSet" in kinds
        assert "PersistentVolumeClaim" in kinds
        assert "Deployment" not in kinds

    def test_k8s_soulful_has_sidecar(self) -> None:
        """@Soulful → K-gent sidecar container."""
        resources = K8sProjector().compile(SoulfulOnlyAgent)

        deployment = next(r for r in resources if r.kind == "Deployment")
        containers = deployment.spec["template"]["spec"]["containers"]

        assert len(containers) == 2
        sidecar_names = [c["name"] for c in containers]
        assert "kgent-sidecar" in sidecar_names

    def test_k8s_observable_has_servicemonitor(self) -> None:
        """@Observable(metrics=True) → ServiceMonitor."""
        resources = K8sProjector().compile(ObservableOnlyAgent)

        kinds = {r.kind for r in resources}
        assert "ServiceMonitor" in kinds

    def test_k8s_streamable_has_hpa(self) -> None:
        """@Streamable → HorizontalPodAutoscaler."""
        resources = K8sProjector().compile(StreamableOnlyAgent)

        kinds = {r.kind for r in resources}
        assert "HorizontalPodAutoscaler" in kinds

    # ───────────────────────────────────────────────────────────────────────────
    # CLIProjector Capability Preservation
    # ───────────────────────────────────────────────────────────────────────────

    def test_cli_stateful_has_state_handling(self) -> None:
        """@Stateful → state persistence in script."""
        script = CLIProjector().compile(StatefulOnlyAgent)

        assert "load_state" in script
        assert "save_state" in script
        assert "STATE_FILE" in script

    def test_cli_soulful_has_persona_banner(self) -> None:
        """@Soulful → persona in banner."""
        script = CLIProjector().compile(SoulfulOnlyAgent)

        assert "Persona" in script
        assert "Test" in script

    def test_cli_observable_has_metrics(self) -> None:
        """@Observable(metrics=True) → metrics output."""
        script = CLIProjector().compile(ObservableOnlyAgent)

        assert "Metrics" in script or "metrics" in script

    def test_cli_streamable_has_streaming(self) -> None:
        """@Streamable → streaming iteration."""
        script = CLIProjector().compile(StreamableOnlyAgent)

        assert "async for" in script or "start(" in script


# ═══════════════════════════════════════════════════════════════════════════════
# Law 3: Empty Halo Identity Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestEmptyHaloIdentityLaw:
    """
    Law 3: Empty Halo Identity - No capabilities → minimal agent.

    For any projector P and plain agent A (no capabilities):
        P.compile(A) is minimal/unchanged
    """

    def test_local_empty_halo_returns_instance(self) -> None:
        """LocalProjector: empty Halo → original instance."""
        compiled = LocalProjector().compile(PlainAgent)

        assert isinstance(compiled, PlainAgent)
        assert get_halo(PlainAgent) == set()

    def test_k8s_empty_halo_minimal_resources(self) -> None:
        """K8sProjector: empty Halo → minimal resources."""
        resources = K8sProjector().compile(PlainAgent)

        kinds = {r.kind for r in resources}
        # Minimal set: Deployment, Service, ConfigMap (no StatefulSet, HPA, etc.)
        assert kinds == {"Deployment", "Service", "ConfigMap"}

    def test_cli_empty_halo_minimal_script(self) -> None:
        """CLIProjector: empty Halo → minimal script without state/metrics."""
        script = CLIProjector().compile(PlainAgent)

        # Should not have state handling
        assert "load_state" not in script
        assert "save_state" not in script

        # Should not have metrics
        assert "print_metrics" not in script


# ═══════════════════════════════════════════════════════════════════════════════
# Unsupported Capability Error Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestUnsupportedCapabilityHandling:
    """Test that projectors correctly reject unsupported capabilities."""

    def test_local_rejects_unsupported(self) -> None:
        """LocalProjector raises UnsupportedCapabilityError."""
        with pytest.raises(UnsupportedCapabilityError) as exc_info:
            LocalProjector().compile(UnsupportedCapAgent)

        assert exc_info.value.projector == "LocalProjector"
        assert exc_info.value.capability == UnsupportedCapability

    def test_k8s_rejects_unsupported(self) -> None:
        """K8sProjector raises UnsupportedCapabilityError."""
        with pytest.raises(UnsupportedCapabilityError) as exc_info:
            K8sProjector().compile(UnsupportedCapAgent)

        assert exc_info.value.projector == "K8sProjector"

    def test_cli_rejects_unsupported(self) -> None:
        """CLIProjector raises UnsupportedCapabilityError."""
        with pytest.raises(UnsupportedCapabilityError) as exc_info:
            CLIProjector().compile(UnsupportedCapAgent)

        assert exc_info.value.projector == "CLIProjector"


# ═══════════════════════════════════════════════════════════════════════════════
# Property-Based Tests (Hypothesis)
# ═══════════════════════════════════════════════════════════════════════════════


# Strategy for generating capability combinations
def capability_combination_strategy():
    """Generate combinations of capabilities."""
    return st.lists(
        st.sampled_from(
            [
                "stateful",
                "soulful",
                "observable",
                "streamable",
            ]
        ),
        min_size=0,
        max_size=4,
        unique=True,
    )


def create_agent_with_capabilities(capabilities: list[str]) -> type[Agent[str, str]]:
    """Dynamically create an agent class with specified capabilities."""

    class DynamicAgent(Agent[str, str]):
        @property
        def name(self) -> str:
            return "dynamic"

        async def invoke(self, input: str) -> str:
            return f"dynamic:{input}"

    # Apply capabilities
    if "stateful" in capabilities:
        DynamicAgent = Capability.Stateful(schema=dict)(DynamicAgent)
    if "soulful" in capabilities:
        DynamicAgent = Capability.Soulful(persona="DynamicPersona")(DynamicAgent)
    if "observable" in capabilities:
        DynamicAgent = Capability.Observable(mirror=True, metrics=True)(DynamicAgent)
    if "streamable" in capabilities:
        DynamicAgent = Capability.Streamable(budget=5.0)(DynamicAgent)

    return DynamicAgent


class TestPropertyBasedLaws:
    """Property-based tests for projector laws."""

    @given(capabilities=capability_combination_strategy())
    @settings(max_examples=20)
    def test_local_any_halo_compiles(self, capabilities: list[str]) -> None:
        """LocalProjector compiles any valid Halo combination."""
        agent_cls = create_agent_with_capabilities(capabilities)
        result = LocalProjector().compile(agent_cls)

        assert result is not None
        assert hasattr(result, "invoke")

    @given(capabilities=capability_combination_strategy())
    @settings(max_examples=20)
    def test_k8s_any_halo_compiles(self, capabilities: list[str]) -> None:
        """K8sProjector compiles any valid Halo combination."""
        agent_cls = create_agent_with_capabilities(capabilities)
        result = K8sProjector().compile(agent_cls)

        assert result is not None
        assert len(result) >= 3  # At least Deployment/StatefulSet, Service, ConfigMap

    @given(capabilities=capability_combination_strategy())
    @settings(max_examples=20)
    def test_cli_any_halo_compiles(self, capabilities: list[str]) -> None:
        """CLIProjector compiles any valid Halo combination."""
        agent_cls = create_agent_with_capabilities(capabilities)
        result = CLIProjector().compile(agent_cls)

        assert result is not None
        assert "#!/usr/bin/env python" in result
        assert "async def _main" in result

    @given(capabilities=capability_combination_strategy())
    @settings(max_examples=20)
    def test_local_determinism_property(self, capabilities: list[str]) -> None:
        """LocalProjector is deterministic for any Halo."""
        agent_cls = create_agent_with_capabilities(capabilities)
        p = LocalProjector()

        r1 = p.compile(agent_cls)
        r2 = p.compile(agent_cls)

        assert type(r1) == type(r2)

    @given(capabilities=capability_combination_strategy())
    @settings(max_examples=20)
    def test_cli_determinism_property(self, capabilities: list[str]) -> None:
        """CLIProjector is deterministic for any Halo."""
        agent_cls = create_agent_with_capabilities(capabilities)
        p = CLIProjector()

        r1 = p.compile(agent_cls)
        r2 = p.compile(agent_cls)

        assert r1 == r2  # String equality


# ═══════════════════════════════════════════════════════════════════════════════
# Cross-Projector Isomorphism Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlethicIsomorphism:
    """
    Test the Alethic Isomorphism: same Halo produces semantically
    equivalent agents across different projectors.
    """

    def test_streamable_budget_preserved_across_projectors(self) -> None:
        """@Streamable budget maps consistently across projectors."""
        from agents.flux import FluxAgent

        # Local: entropy_budget in FluxConfig
        local = LocalProjector().compile(StreamableOnlyAgent)
        assert isinstance(local, FluxAgent)
        assert local.config.entropy_budget == 5.0

        # K8s: maxReplicas = min(budget * 2, 10)
        k8s = K8sProjector().compile(StreamableOnlyAgent)
        hpa = next(r for r in k8s if r.kind == "HorizontalPodAutoscaler")
        expected_replicas = min(int(5.0 * 2), 10)  # 10
        assert hpa.spec["maxReplicas"] == expected_replicas

    def test_soulful_persona_preserved_across_projectors(self) -> None:
        """@Soulful persona maps consistently across projectors."""
        # Local: persona_name in SoulfulAdapter
        local = LocalProjector().compile(SoulfulOnlyAgent)
        assert isinstance(local, SoulfulAdapter)
        assert local.persona_name == "Test"

        # K8s: KGENT_PERSONA env var in sidecar
        k8s = K8sProjector().compile(SoulfulOnlyAgent)
        deployment = next(r for r in k8s if r.kind == "Deployment")
        sidecar = next(
            c
            for c in deployment.spec["template"]["spec"]["containers"]
            if c["name"] == "kgent-sidecar"
        )
        persona_env = next(e for e in sidecar["env"] if e["name"] == "KGENT_PERSONA")
        assert persona_env["value"] == "Test"

        # CLI: persona in banner
        cli = CLIProjector().compile(SoulfulOnlyAgent)
        assert "Test" in cli

    def test_stateful_produces_persistence_across_projectors(self) -> None:
        """@Stateful produces persistence in all projectors."""
        # Local: StatefulAdapter with state property
        local = LocalProjector().compile(StatefulOnlyAgent)
        assert isinstance(local, StatefulAdapter)
        assert hasattr(local, "state")

        # K8s: StatefulSet + PVC
        k8s = K8sProjector().compile(StatefulOnlyAgent)
        kinds = {r.kind for r in k8s}
        assert "StatefulSet" in kinds
        assert "PersistentVolumeClaim" in kinds

        # CLI: STATE_FILE and load/save_state
        cli = CLIProjector().compile(StatefulOnlyAgent)
        assert "STATE_FILE" in cli
        assert "load_state" in cli
