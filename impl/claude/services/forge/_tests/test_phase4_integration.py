"""
Phase 4 Integration Tests.

Tests the full commission pipeline with Herald and Projector artisans.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ..commission import Commission, CommissionService, CommissionStatus


class TestPhase4Pipeline:
    """Integration tests for the Phase 4 commission pipeline."""

    @pytest.fixture
    def temp_output_dir(self) -> Path:
        """Create a temporary output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.asyncio
    async def test_full_commission_through_projector(self) -> None:
        """Test commission from create through projecting stage."""
        service = CommissionService(kgent_soul=None)

        # Create commission
        commission = await service.create(
            intent="Build a simple counter that can increment and decrement",
            name="CounterAgent",
        )
        assert commission.status == CommissionStatus.PENDING
        assert commission.id.startswith("commission-")

        # Start review (K-gent → DESIGNING)
        commission = await service.start_review(commission.id)
        assert commission is not None
        assert commission.status == CommissionStatus.DESIGNING
        assert commission.soul_approved is True  # Auto-approved without K-gent

        # Advance through Architect (DESIGNING → IMPLEMENTING)
        commission = await service.advance(commission.id)
        assert commission is not None
        assert commission.status == CommissionStatus.IMPLEMENTING
        assert "architect" in commission.artisan_outputs

        architect_output = commission.artisan_outputs["architect"]
        assert architect_output.status == "complete"
        assert architect_output.output is not None
        assert "name" in architect_output.output

        # Advance through Smith (IMPLEMENTING → EXPOSING)
        commission = await service.advance(commission.id)
        assert commission is not None
        assert commission.status == CommissionStatus.EXPOSING
        assert "smith" in commission.artisan_outputs

        smith_output = commission.artisan_outputs["smith"]
        assert smith_output.status == "complete"
        assert smith_output.output is not None
        assert "file_count" in smith_output.output

        # Advance through Herald (EXPOSING → PROJECTING)
        commission = await service.advance(commission.id)
        assert commission is not None
        assert commission.status == CommissionStatus.PROJECTING
        assert "herald" in commission.artisan_outputs

        herald_output = commission.artisan_outputs["herald"]
        assert herald_output.status == "complete"
        assert herald_output.output is not None
        assert "registered_path" in herald_output.output
        assert herald_output.output["registered_path"].startswith("world.")

        # Advance through Projector (PROJECTING → SECURING)
        commission = await service.advance(commission.id)
        assert commission is not None
        assert commission.status == CommissionStatus.SECURING
        assert "projector" in commission.artisan_outputs

        projector_output = commission.artisan_outputs["projector"]
        assert projector_output.status == "complete"
        assert projector_output.output is not None
        assert "file_count" in projector_output.output

    @pytest.mark.asyncio
    async def test_herald_generates_node_files(self) -> None:
        """Test that Herald generates the expected node files."""
        service = CommissionService(kgent_soul=None)

        # Run through to Herald
        commission = await service.create(intent="Build a todo list manager")
        commission = await service.start_review(commission.id)
        commission = await service.advance(commission.id)  # Architect
        commission = await service.advance(commission.id)  # Smith
        commission = await service.advance(commission.id)  # Herald

        assert commission is not None
        herald_output = commission.artisan_outputs.get("herald")
        assert herald_output is not None
        assert herald_output.status == "complete"

        # Check Herald output has expected files
        output = herald_output.output
        assert output is not None
        assert "file_count" in output
        assert output["file_count"] == 2
        assert "node.py" in output["files"]
        assert "contracts_ext.py" in output["files"]

    @pytest.mark.asyncio
    async def test_projector_generates_react_files(self) -> None:
        """Test that Projector generates the expected React files."""
        service = CommissionService(kgent_soul=None)

        # Run through to Projector
        commission = await service.create(intent="Build a note-taking app")
        commission = await service.start_review(commission.id)
        commission = await service.advance(commission.id)  # Architect
        commission = await service.advance(commission.id)  # Smith
        commission = await service.advance(commission.id)  # Herald
        commission = await service.advance(commission.id)  # Projector

        assert commission is not None
        projector_output = commission.artisan_outputs.get("projector")
        assert projector_output is not None
        assert projector_output.status == "complete"

        # Check Projector output has expected files
        output = projector_output.output
        assert output is not None
        assert "file_count" in output
        assert output["file_count"] == 3
        assert "index.ts" in output["files"]

    @pytest.mark.asyncio
    async def test_full_pipeline_to_complete(self) -> None:
        """Test commission all the way to COMPLETE status."""
        service = CommissionService(kgent_soul=None)

        # Create and start
        commission = await service.create(intent="Build a calculator")
        commission = await service.start_review(commission.id)

        # Track stages for verification
        stages = [commission.status.value]

        # Advance through all stages until complete or terminal
        for _ in range(10):  # Safety limit
            prev_status = commission.status
            commission = await service.advance(commission.id)

            if commission is None:
                break

            stages.append(commission.status.value)

            # Stop if terminal
            if commission.status in (
                CommissionStatus.COMPLETE,
                CommissionStatus.REJECTED,
                CommissionStatus.FAILED,
            ):
                break

            # Stop if no progress
            if commission.status == prev_status:
                break

        # Should reach COMPLETE
        assert commission is not None
        assert commission.status == CommissionStatus.COMPLETE

        # Verify all 7 artisans were called
        artisan_keys = list(commission.artisan_outputs.keys())
        assert "kgent" in artisan_keys
        assert "architect" in artisan_keys
        assert "smith" in artisan_keys
        assert "herald" in artisan_keys
        assert "projector" in artisan_keys
        assert "sentinel" in artisan_keys  # Placeholder
        assert "witness" in artisan_keys  # Placeholder

    @pytest.mark.asyncio
    async def test_herald_output_contains_agentese_path(self) -> None:
        """Test that Herald output contains the registered AGENTESE path."""
        service = CommissionService(kgent_soul=None)

        commission = await service.create(
            intent="Build a preferences manager",
            name="PreferencesAgent",
        )
        commission = await service.start_review(commission.id)
        commission = await service.advance(commission.id)  # Architect
        commission = await service.advance(commission.id)  # Smith
        commission = await service.advance(commission.id)  # Herald

        assert commission is not None
        herald_output = commission.artisan_outputs["herald"]

        # The path should be derived from the intent/name
        registered_path = herald_output.output["registered_path"]
        assert registered_path.startswith("world.")
        # Should be lowercase
        assert registered_path == registered_path.lower()

    @pytest.mark.asyncio
    async def test_pipeline_preserves_artisan_chain(self) -> None:
        """Test that later artisans can access earlier artisan outputs."""
        service = CommissionService(kgent_soul=None)

        commission = await service.create(intent="Build a chat interface")
        commission = await service.start_review(commission.id)

        # Run through all stages
        for _ in range(7):
            commission = await service.advance(commission.id)
            if commission is None or commission.status in (
                CommissionStatus.COMPLETE,
                CommissionStatus.FAILED,
            ):
                break

        assert commission is not None

        # All artisan outputs should be preserved
        outputs = commission.artisan_outputs

        # K-gent should have reviewed
        assert outputs["kgent"].status in ("complete", "skipped")

        # Architect design should be available
        assert outputs["architect"].output is not None
        assert "name" in outputs["architect"].output

        # Smith should have path
        assert outputs["smith"].output is not None
        assert "path" in outputs["smith"].output

        # Herald should have registered path
        assert outputs["herald"].output is not None
        assert "registered_path" in outputs["herald"].output

        # Projector should have files
        assert outputs["projector"].output is not None
        assert "files" in outputs["projector"].output


class TestPhase4ErrorHandling:
    """Tests for error handling in Phase 4 pipeline."""

    @pytest.mark.asyncio
    async def test_herald_fails_without_architect_output(self) -> None:
        """Test that Herald fails if architect output is missing."""
        service = CommissionService(kgent_soul=None)

        # Create and manually advance to EXPOSING without architect output
        commission = await service.create(intent="Test failure")
        commission = await service.start_review(commission.id)

        # Clear architect output to simulate missing data
        commission.status = CommissionStatus.EXPOSING
        commission.artisan_outputs.clear()

        # Advance should fail
        commission = await service.advance(commission.id)

        assert commission is not None
        assert commission.status == CommissionStatus.FAILED
        assert "herald" in commission.artisan_outputs
        assert commission.artisan_outputs["herald"].status == "failed"

    @pytest.mark.asyncio
    async def test_projector_fails_without_herald_output(self) -> None:
        """Test that Projector fails if herald output is missing."""
        service = CommissionService(kgent_soul=None)

        # Run through Herald
        commission = await service.create(intent="Test failure")
        commission = await service.start_review(commission.id)
        commission = await service.advance(commission.id)  # Architect
        commission = await service.advance(commission.id)  # Smith
        commission = await service.advance(commission.id)  # Herald

        # Clear herald output to simulate missing data
        commission.status = CommissionStatus.PROJECTING
        del commission.artisan_outputs["herald"]

        # Advance should fail
        commission = await service.advance(commission.id)

        assert commission is not None
        assert commission.status == CommissionStatus.FAILED
        assert "projector" in commission.artisan_outputs
        assert commission.artisan_outputs["projector"].status == "failed"
