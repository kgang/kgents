"""Tests for Gestalt widgets: TopologyGraph and GovernanceTable."""

from __future__ import annotations

import pytest

from agents.i.reactive.primitives.gestalt import (
    GovernanceEntry,
    GovernanceTableState,
    GovernanceTableWidget,
    TopologyEdge,
    TopologyGraphState,
    TopologyGraphWidget,
    TopologyNode,
)
from agents.i.reactive.widget import RenderTarget


class TestTopologyGraphState:
    """Tests for TopologyGraphState."""

    def test_default_state(self) -> None:
        """Default state has empty nodes and edges."""
        state = TopologyGraphState()
        assert state.nodes == ()
        assert state.edges == ()
        assert state.title == "System Topology"
        assert state.zoom_level == 1

    def test_state_with_nodes_and_edges(self) -> None:
        """State can be created with nodes and edges."""
        nodes = (
            TopologyNode(id="a", label="Agent A", type="agent", status="active"),
            TopologyNode(id="b", label="Service B", type="service", status="healthy"),
        )
        edges = (TopologyEdge(source="a", target="b", label="connects"),)

        state = TopologyGraphState(nodes=nodes, edges=edges)

        assert len(state.nodes) == 2
        assert len(state.edges) == 1
        assert state.nodes[0].label == "Agent A"
        assert state.edges[0].label == "connects"


class TestTopologyGraphWidget:
    """Tests for TopologyGraphWidget."""

    def test_create_with_default_state(self) -> None:
        """Widget can be created with default state."""
        widget = TopologyGraphWidget()
        assert widget.state.value.nodes == ()

    def test_project_cli_empty(self) -> None:
        """CLI projection shows message for empty topology."""
        widget = TopologyGraphWidget()
        result = widget.project(RenderTarget.CLI)
        assert "empty" in result.lower()

    def test_project_cli_with_nodes(self) -> None:
        """CLI projection includes node labels."""
        widget = TopologyGraphWidget(
            TopologyGraphState(
                nodes=(
                    TopologyNode(id="soul", label="K-gent Soul", type="agent"),
                    TopologyNode(id="memory", label="M-gent Memory", type="agent"),
                ),
            )
        )
        result = widget.project(RenderTarget.CLI)

        assert "K-gent Soul" in result
        assert "M-gent Memory" in result

    def test_project_cli_shows_edges_at_zoom_2(self) -> None:
        """CLI projection shows edges at zoom level 2+."""
        widget = TopologyGraphWidget(
            TopologyGraphState(
                nodes=(
                    TopologyNode(id="a", label="A"),
                    TopologyNode(id="b", label="B"),
                ),
                edges=(TopologyEdge(source="a", target="b", label="links"),),
                zoom_level=2,
            )
        )
        result = widget.project(RenderTarget.CLI)

        assert "links" in result
        assert "Connections" in result

    def test_project_json_structure(self) -> None:
        """JSON projection has expected structure."""
        widget = TopologyGraphWidget(
            TopologyGraphState(
                nodes=(TopologyNode(id="test", label="Test"),),
                edges=(TopologyEdge(source="test", target="test"),),
                title="Test Graph",
            )
        )
        result = widget.project(RenderTarget.JSON)

        assert result["type"] == "topology_graph"
        assert result["title"] == "Test Graph"
        assert len(result["nodes"]) == 1
        assert len(result["edges"]) == 1
        assert result["nodes"][0]["id"] == "test"

    def test_project_marimo_returns_html(self) -> None:
        """MARIMO projection returns HTML with Cytoscape config."""
        widget = TopologyGraphWidget(
            TopologyGraphState(
                nodes=(TopologyNode(id="x", label="X"),),
            )
        )
        result = widget.project(RenderTarget.MARIMO)

        assert "<div" in result
        assert "kgents-topology" in result
        assert "cytoscape" in result.lower()

    def test_ui_hint_is_graph(self) -> None:
        """TopologyGraphWidget ui_hint is 'graph'."""
        widget = TopologyGraphWidget()
        assert widget.ui_hint() == "graph"

    def test_widget_type(self) -> None:
        """widget_type returns 'topology_graph'."""
        widget = TopologyGraphWidget()
        assert widget.widget_type() == "topology_graph"

    def test_to_envelope_works(self) -> None:
        """to_envelope produces valid envelope."""
        from protocols.projection.schema import WidgetStatus

        widget = TopologyGraphWidget(
            TopologyGraphState(nodes=(TopologyNode(id="test", label="Test"),))
        )
        envelope = widget.to_envelope()

        assert envelope.meta.status == WidgetStatus.DONE
        assert envelope.data is not None
        assert envelope.data["type"] == "topology_graph"


class TestGovernanceEntry:
    """Tests for GovernanceEntry."""

    def test_default_entry(self) -> None:
        """Entry has expected defaults."""
        entry = GovernanceEntry(agent_id="test", agent_name="Test Agent")
        assert entry.consent_level == 1.0
        assert entry.status == "active"
        assert entry.permissions == ()

    def test_entry_with_all_fields(self) -> None:
        """Entry can be created with all fields."""
        entry = GovernanceEntry(
            agent_id="soul-1",
            agent_name="Soul Agent",
            consent_level=0.75,
            permissions=("read", "write"),
            status="idle",
            last_action="Permission granted",
        )
        assert entry.consent_level == 0.75
        assert "read" in entry.permissions
        assert entry.status == "idle"


class TestGovernanceTableState:
    """Tests for GovernanceTableState."""

    def test_sorted_entries_by_name(self) -> None:
        """sorted_entries sorts by name by default."""
        state = GovernanceTableState(
            entries=(
                GovernanceEntry(agent_id="z", agent_name="Zeta"),
                GovernanceEntry(agent_id="a", agent_name="Alpha"),
            ),
            sort_by="name",
            sort_direction="asc",
        )

        sorted_names = [e.agent_name for e in state.sorted_entries]
        assert sorted_names == ["Alpha", "Zeta"]

    def test_sorted_entries_by_consent(self) -> None:
        """sorted_entries can sort by consent level."""
        state = GovernanceTableState(
            entries=(
                GovernanceEntry(agent_id="low", agent_name="Low", consent_level=0.2),
                GovernanceEntry(agent_id="high", agent_name="High", consent_level=0.9),
            ),
            sort_by="consent",
            sort_direction="desc",
        )

        sorted_names = [e.agent_name for e in state.sorted_entries]
        assert sorted_names == ["High", "Low"]

    def test_show_inactive_filters(self) -> None:
        """show_inactive=False filters out revoked/suspended."""
        state = GovernanceTableState(
            entries=(
                GovernanceEntry(agent_id="active", agent_name="Active", status="active"),
                GovernanceEntry(agent_id="revoked", agent_name="Revoked", status="revoked"),
            ),
            show_inactive=False,
        )

        assert len(state.sorted_entries) == 1
        assert state.sorted_entries[0].agent_name == "Active"


class TestGovernanceTableWidget:
    """Tests for GovernanceTableWidget."""

    def test_create_with_default_state(self) -> None:
        """Widget can be created with default state."""
        widget = GovernanceTableWidget()
        assert widget.state.value.entries == ()

    def test_project_cli_empty(self) -> None:
        """CLI projection shows message for empty table."""
        widget = GovernanceTableWidget()
        result = widget.project(RenderTarget.CLI)
        assert "no governance" in result.lower()

    def test_project_cli_with_entries(self) -> None:
        """CLI projection includes entry information."""
        widget = GovernanceTableWidget(
            GovernanceTableState(
                entries=(
                    GovernanceEntry(
                        agent_id="soul",
                        agent_name="K-gent Soul",
                        consent_level=0.85,
                        permissions=("read", "write"),
                        status="active",
                    ),
                ),
            )
        )
        result = widget.project(RenderTarget.CLI)

        assert "K-gent Soul" in result
        assert "active" in result
        assert "85%" in result

    def test_project_cli_shows_consent_bar(self) -> None:
        """CLI projection includes consent bar."""
        widget = GovernanceTableWidget(
            GovernanceTableState(
                entries=(GovernanceEntry(agent_id="x", agent_name="X", consent_level=0.5),),
            )
        )
        result = widget.project(RenderTarget.CLI)

        # Should have filled and empty blocks
        assert "█" in result
        assert "░" in result

    def test_project_json_structure(self) -> None:
        """JSON projection has expected structure."""
        widget = GovernanceTableWidget(
            GovernanceTableState(
                entries=(
                    GovernanceEntry(
                        agent_id="test",
                        agent_name="Test",
                        consent_level=0.7,
                        permissions=("read",),
                    ),
                ),
                title="Test Governance",
            )
        )
        result = widget.project(RenderTarget.JSON)

        assert result["type"] == "governance_table"
        assert result["title"] == "Test Governance"
        assert len(result["entries"]) == 1
        assert result["entries"][0]["agentId"] == "test"
        assert result["entries"][0]["consentLevel"] == 0.7
        assert "summary" in result
        assert result["summary"]["avgConsent"] == 0.7

    def test_project_marimo_returns_html(self) -> None:
        """MARIMO projection returns HTML table."""
        widget = GovernanceTableWidget(
            GovernanceTableState(
                entries=(GovernanceEntry(agent_id="x", agent_name="X"),),
            )
        )
        result = widget.project(RenderTarget.MARIMO)

        assert "<table" in result
        assert "kgents-governance" in result
        assert "consent-bar" in result

    def test_ui_hint_is_table(self) -> None:
        """GovernanceTableWidget ui_hint is 'table'."""
        widget = GovernanceTableWidget()
        assert widget.ui_hint() == "table"

    def test_widget_type(self) -> None:
        """widget_type returns 'governance_table'."""
        widget = GovernanceTableWidget()
        assert widget.widget_type() == "governance_table"

    def test_to_envelope_works(self) -> None:
        """to_envelope produces valid envelope."""
        from protocols.projection.schema import WidgetStatus

        widget = GovernanceTableWidget(
            GovernanceTableState(entries=(GovernanceEntry(agent_id="test", agent_name="Test"),))
        )
        envelope = widget.to_envelope()

        assert envelope.meta.status == WidgetStatus.DONE
        assert envelope.data is not None
        assert envelope.data["type"] == "governance_table"


class TestGestaltDeterminism:
    """Tests for Gestalt widget determinism."""

    def test_topology_same_state_same_output(self) -> None:
        """Same TopologyGraphState produces same output."""
        state = TopologyGraphState(
            nodes=(
                TopologyNode(id="a", label="A", status="active"),
                TopologyNode(id="b", label="B", status="idle"),
            ),
            edges=(TopologyEdge(source="a", target="b"),),
        )

        w1 = TopologyGraphWidget(state)
        w2 = TopologyGraphWidget(state)

        assert w1.to_json() == w2.to_json()
        assert w1.to_cli() == w2.to_cli()

    def test_governance_same_state_same_output(self) -> None:
        """Same GovernanceTableState produces same output."""
        state = GovernanceTableState(
            entries=(
                GovernanceEntry(agent_id="x", agent_name="X", consent_level=0.5),
                GovernanceEntry(agent_id="y", agent_name="Y", consent_level=0.8),
            ),
        )

        w1 = GovernanceTableWidget(state)
        w2 = GovernanceTableWidget(state)

        assert w1.to_json() == w2.to_json()
        assert w1.to_cli() == w2.to_cli()
