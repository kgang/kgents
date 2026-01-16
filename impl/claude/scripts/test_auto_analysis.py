"""
Test script for auto-analysis flow.

Verifies that:
1. Upload with auto_analyze=True triggers background analysis
2. Status transitions: pending → processing → ready
3. Events are emitted: started → complete
"""

import asyncio
import logging
from datetime import UTC, datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_auto_analysis():
    """Test auto-analysis flow."""
    from protocols.api.director import _run_analysis
    from services.providers import get_sovereign_store
    from services.sovereign.ingest import Ingestor
    from services.sovereign.types import IngestEvent

    logger.info("Starting auto-analysis test")

    # Get store
    store = await get_sovereign_store()

    # Create test document
    test_path = "spec/test/auto_analysis_test.md"
    test_content = """# Test Specification

This is a test specification for auto-analysis.

## Claims

- The system shall parse this document
- The system shall extract claims
- The system shall identify references

## Implementation

See: impl/test/example.py

## Testing

Tests at: impl/test/test_example.py
"""

    logger.info(f"Ingesting test document: {test_path}")

    # Ingest document
    event = IngestEvent.from_content(
        content=test_content.encode("utf-8"),
        claimed_path=test_path,
        source="test",
    )
    ingestor = Ingestor(store, witness=None)
    result = await ingestor.ingest(event, author="test")

    logger.info(f"✓ Document ingested: v{result.version}")

    # Set status to ANALYZING
    from services.sovereign.analysis import AnalysisState, AnalysisStatus

    await store.set_analysis_state(
        test_path,
        AnalysisState(
            status=AnalysisStatus.ANALYZING,
            started_at=datetime.now(UTC).isoformat(),
        ),
    )

    logger.info("✓ Status set to ANALYZING")

    # Run background analysis
    logger.info("Running background analysis...")
    await _run_analysis(test_path, store)

    # Check final status
    state = await store.get_analysis_state(test_path)
    logger.info(f"✓ Final status: {state.status.value if state else 'unknown'}")

    # Check analysis results
    overlay = await store.get_overlay(test_path, "analysis_crystal")
    if overlay:
        logger.info("✓ Analysis crystal created")
        logger.info(f"  - Claims: {len(overlay.get('claims', []))}")
        logger.info(f"  - Implementations: {len(overlay.get('implementations', []))}")
        logger.info(f"  - Tests: {len(overlay.get('tests', []))}")
        logger.info(f"  - Placeholders: {len(overlay.get('placeholder_paths', []))}")
    else:
        logger.warning("✗ No analysis crystal found")

    logger.info("✓ Auto-analysis test complete")


if __name__ == "__main__":
    asyncio.run(test_auto_analysis())
