"""
Tests for Phase 2: Zero Seed Genesis Grand Strategy - Uploads.

Tests the upload staging, file explorer, integration, and splitting services.
"""

import pytest
from pathlib import Path
from datetime import datetime


def test_uploaded_file_creation():
    """Test UploadedFile dataclass creation."""
    from services.sovereign.uploads import UploadedFile, UploadStatus

    upload = UploadedFile(
        path="test.md",
        content_hash="abc123",
        size_bytes=1024,
        uploaded_at=datetime.now(),
        status=UploadStatus.STAGED,
        metadata={"mime_type": "text/markdown"},
    )

    assert upload.path == "test.md"
    assert upload.status == UploadStatus.STAGED
    assert upload.to_dict()["mime_type"] == "text/markdown"


def test_file_explorer_entry_creation():
    """Test FileExplorerEntry dataclass creation."""
    from services.sovereign.uploads import FileExplorerEntry

    entry = FileExplorerEntry(
        path="spec/protocols",
        name="protocols",
        is_directory=True,
        metadata={"layer": 3},
    )

    assert entry.is_directory
    assert entry.metadata["layer"] == 3
    assert entry.to_dict()["name"] == "protocols"


def test_integration_result_creation():
    """Test IntegrationResult dataclass creation."""
    from services.sovereign.integration import (
        IntegrationResult,
        DiscoveredEdge,
        PortalToken,
    )

    edge = DiscoveredEdge(
        source_path="test.md",
        target_path="other.md",
        edge_type="references",
        confidence=0.8,
    )

    token = PortalToken(token="concept.entity", token_type="concept")

    result = IntegrationResult(
        source_path="uploads/test.md",
        destination_path="spec/test.md",
        kblock_id="kblock-123",
        layer=3,
        edges=[edge],
        portal_tokens=[token],
    )

    assert result.success
    assert len(result.edges) == 1
    assert len(result.portal_tokens) == 1
    assert result.to_dict()["layer"] == 3


def test_split_recommendation_creation():
    """Test SplitRecommendation dataclass creation."""
    from services.sovereign.splitting import (
        SplitRecommendation,
        SplitReason,
        SplitReasonType,
        SplitPlan,
        SplitSection,
    )

    section = SplitSection(
        title="Introduction",
        content="# Introduction\nSome content",
        start_line=0,
        end_line=10,
        estimated_layer=3,
        estimated_tokens=50,
    )

    plan = SplitPlan(
        sections=[section],
        recommended_paths=["spec/intro.md"],
        total_loss_before=0.8,
        estimated_loss_after=0.5,
        improvement=0.3,
    )

    reason = SplitReason(
        type=SplitReasonType.MULTIPLE_CONCEPTS,
        description="Too many sections",
        confidence=0.7,
    )

    recommendation = SplitRecommendation(
        should_split=True, reasons=[reason], plan=plan, requires_user_approval=True
    )

    assert recommendation.should_split
    assert len(recommendation.reasons) == 1
    assert recommendation.plan.num_sections == 1


def test_upload_service_factory():
    """Test UploadService factory pattern."""
    from services.sovereign.uploads import (
        get_upload_service,
        reset_upload_service,
    )

    # Reset first
    reset_upload_service()

    # Get service
    service1 = get_upload_service()
    assert service1 is not None

    # Verify singleton
    service2 = get_upload_service()
    assert service1 is service2

    # Cleanup
    reset_upload_service()


def test_integration_service_factory():
    """Test IntegrationService factory pattern."""
    from services.sovereign.integration import (
        get_integration_service,
        reset_integration_service,
    )

    # Reset first
    reset_integration_service()

    # Get service
    service1 = get_integration_service()
    assert service1 is not None

    # Verify singleton
    service2 = get_integration_service()
    assert service1 is service2

    # Cleanup
    reset_integration_service()


def test_splitting_service_factory():
    """Test SplittingService factory pattern."""
    from services.sovereign.splitting import (
        get_splitting_service,
        reset_splitting_service,
    )

    # Reset first
    reset_splitting_service()

    # Get service
    service1 = get_splitting_service()
    assert service1 is not None

    # Verify singleton
    service2 = get_splitting_service()
    assert service1 is service2

    # Cleanup
    reset_splitting_service()


@pytest.mark.asyncio
async def test_splitting_service_extract_sections():
    """Test section extraction from markdown."""
    from services.sovereign.splitting import get_splitting_service, reset_splitting_service

    reset_splitting_service()
    service = get_splitting_service()

    text = """# Document Title

Some intro text.

## Section 1

Content for section 1.

## Section 2

Content for section 2.

### Subsection 2.1

Nested content.
"""

    sections = service._extract_sections(text)

    # Should extract sections with ## or ### headings
    assert len(sections) >= 2
    assert "Section 1" in sections[0].title or "Section 2" in sections[0].title

    # Cleanup
    reset_splitting_service()


@pytest.mark.asyncio
async def test_integration_layer_assignment():
    """Test layer assignment heuristics."""
    from services.sovereign.integration import get_integration_service, reset_integration_service

    reset_integration_service()
    service = get_integration_service()

    # Test axiom content
    axiom_content = b"This is an AXIOM about principles"
    layer, loss = await service._assign_layer(axiom_content)
    assert layer == 1  # L1: Axioms

    # Test spec content
    spec_content = b"This is a SPEC for the protocol"
    layer, loss = await service._assign_layer(spec_content)
    assert layer == 4  # L4: Specifications

    # Cleanup
    reset_integration_service()


@pytest.mark.asyncio
async def test_splitting_contradiction_detection():
    """Test internal contradiction detection."""
    from services.sovereign.splitting import (
        get_splitting_service,
        reset_splitting_service,
        SplitSection,
    )

    reset_splitting_service()
    service = get_splitting_service()

    # Create sections with contradictory keywords
    sections = [
        SplitSection(
            title="Rules",
            content="This is ALWAYS required and NEVER optional",
            start_line=0,
            end_line=5,
        ),
        SplitSection(
            title="Exceptions",
            content="However, this is sometimes TRUE and sometimes FALSE",
            start_line=6,
            end_line=10,
        ),
    ]

    loss = await service._compute_internal_contradiction(sections)

    # Should detect contradiction
    assert loss > 0.0

    # Cleanup
    reset_splitting_service()
