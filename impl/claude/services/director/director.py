"""
Document Director: Orchestrator for spec-to-code lifecycle.

> *"Upload spec → Parse → Accumulate evidence → Brilliant executions"*

This is the main orchestrator that implements the full lifecycle from
document-director.md:

1. analyze_deep() - Sovereign analysis + spec claim extraction
2. extract_anticipated() - Parse @anticipated markers from content
3. generate_prompt() - Build ExecutionPrompt for Claude Code
4. capture_execution() - Ingest generated files + create evidence
5. resolve_placeholder() - Handle anticipated placeholder resolution
6. get_status() - Full document status

Teaching:
    gotcha: Deep analysis = basic sovereign analysis + claim extraction.
            The AnalysisCrystal stores everything in overlay/analysis_crystal.json

    gotcha: Evidence marks follow the ladder: L-2 PROMPT, L-1 TRACE, L1 TEST.
            Each level builds on the previous.

See: spec/protocols/document-director.md
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from services.living_spec.analyzer import parse_spec_content
from services.sovereign.analyzer import SovereignAnalyzer
from services.sovereign.ingest import Ingestor
from services.sovereign.store import SovereignStore

from .types import AnalysisCrystal, CaptureResult, DocumentTopics, ExecutionPrompt, TestResults

if TYPE_CHECKING:
    from services.witness.bus import WitnessSynergyBus
    from services.witness.persistence import WitnessPersistence

logger = logging.getLogger(__name__)


@dataclass
class ResolveResult:
    """Result of resolving a placeholder."""

    path: str
    version: int
    placeholder_resolved: bool
    linked_specs: list[str]  # Specs that anticipated this

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "path": self.path,
            "version": self.version,
            "placeholder_resolved": self.placeholder_resolved,
            "linked_specs": self.linked_specs,
            "spec_count": len(self.linked_specs),
        }


# =============================================================================
# Document Director
# =============================================================================


class DocumentDirector:
    """
    Main orchestrator for document lifecycle.

    Composes:
    - SovereignStore: Entity storage and versioning
    - SovereignAnalyzer: Reference discovery and placeholders
    - Ingestor: File ingestion with witness marks
    - WitnessPersistence: Witness mark creation
    - WitnessSynergyBus: Event publishing

    The Director bridges sovereign store with spec analysis and evidence capture.
    """

    def __init__(
        self,
        store: SovereignStore,
        witness: "WitnessPersistence | None" = None,
        bus: "WitnessSynergyBus | None" = None,
    ) -> None:
        """
        Initialize the Document Director.

        Args:
            store: Sovereign store for entity management
            witness: Witness persistence for marks
            bus: Synergy bus for event publishing
        """
        self.store = store
        self.witness = witness
        self.bus = bus

        # Create composed services
        self.analyzer = SovereignAnalyzer(store, witness, bus)
        self.ingestor = Ingestor(store, witness)

    async def analyze_deep(
        self,
        path: str,
        force: bool = False,
        author: str = "system",
    ) -> AnalysisCrystal:
        """
        Deep analysis: Sovereign analysis + spec content parsing.

        Flow:
        1. Run basic sovereign analysis (refs, placeholders)
        2. Parse spec content for claims
        3. Extract anticipated implementations
        4. Store AnalysisCrystal in overlay
        5. Emit DIRECTOR_ANALYSIS_COMPLETE event

        Args:
            path: Entity path to analyze
            force: Force re-analysis
            author: Who is requesting

        Returns:
            AnalysisCrystal with full analysis
        """
        logger.debug(f"Deep analysis starting for {path}")

        # 1. Basic sovereign analysis
        basic_result = await self.analyzer.analyze(path, force=force, author=author)

        if not basic_result.is_successful:
            # Analysis failed - return minimal crystal
            return AnalysisCrystal(
                entity_path=path,
                analyzed_at=datetime.now(UTC).isoformat(),
                status="failed",
                error=basic_result.error,
            )

        # 2. Get entity content for spec parsing
        entity = await self.store.get_current(path)
        if not entity:
            raise ValueError(f"Entity not found: {path}")

        content = entity.content_text

        # 3. Parse spec content for claims
        spec_record = parse_spec_content(path, content)

        # 4. Extract anticipated implementations
        anticipated = await self.extract_anticipated(path, content)

        # 5. Build analysis crystal
        crystal = AnalysisCrystal(
            entity_path=path,
            analyzed_at=datetime.now(UTC).isoformat(),
            title=spec_record.title,
            word_count=spec_record.word_count,
            heading_count=spec_record.heading_count,
            claims=[
                {
                    "type": claim.claim_type.name,
                    "subject": claim.subject,
                    "predicate": claim.predicate,
                    "line": claim.line_number,
                    "raw_text": claim.raw_text,
                }
                for claim in spec_record.claims
            ],
            spec_refs=spec_record.references,
            implementations=spec_record.implementations,
            tests=spec_record.tests,
            discovered_refs=basic_result.discovered_refs,
            placeholder_paths=basic_result.placeholder_paths,
            anticipated=anticipated,
            status="analyzed",
        )

        # 6. Store crystal in overlay
        await self.store.store_overlay(
            path,
            "analysis_crystal",
            crystal.to_dict(),
        )

        # 7. Emit event
        if self.bus:
            await self.bus.publish(
                DocumentTopics.ANALYSIS_COMPLETE,
                {
                    "path": path,
                    "claim_count": len(crystal.claims),
                    "anticipated_count": len(crystal.anticipated),
                    "placeholder_count": len(crystal.placeholder_paths),
                    "analyzed_at": crystal.analyzed_at,
                },
            )

        logger.info(
            f"Deep analysis complete for {path}: {len(crystal.claims)} claims, "
            f"{len(crystal.anticipated)} anticipated"
        )

        return crystal

    async def extract_anticipated(
        self,
        path: str,
        content: str,
    ) -> list[dict[str, Any]]:
        """
        Extract anticipated implementation markers from content.

        Parses markers like:
            <!-- @anticipated impl/path.py -->
            Context about what should be implemented...
            <!-- @end -->

        Args:
            path: The spec path (for logging)
            content: The markdown content

        Returns:
            List of {path, context, spec_line}
        """
        anticipated = []

        # Pattern: <!-- @anticipated path/to/file.py -->
        pattern = re.compile(
            r"<!--\s*@anticipated\s+([^\s]+)\s*-->(.*?)(?:<!--\s*@end\s*-->|$)",
            re.DOTALL | re.MULTILINE,
        )

        for match in pattern.finditer(content):
            target_path = match.group(1).strip()
            context = match.group(2).strip()
            line_number = content[: match.start()].count("\n") + 1

            anticipated.append(
                {
                    "path": target_path,
                    "context": context[:500],  # Truncate long context
                    "spec_line": line_number,
                }
            )

        logger.debug(f"Extracted {len(anticipated)} anticipated implementations from {path}")
        return anticipated

    async def generate_prompt(
        self,
        spec_path: str,
        author: str = "system",
    ) -> ExecutionPrompt:
        """
        Generate execution prompt for Claude Code.

        Flow:
        1. Get entity and analysis crystal
        2. Build ExecutionPrompt with spec + targets + claims
        3. Create witness mark (L-2 PROMPT)
        4. Emit DIRECTOR_PROMPT_GENERATED event

        Args:
            spec_path: Path to spec
            author: Who is generating

        Returns:
            ExecutionPrompt ready for Claude Code
        """
        # 1. Get entity
        entity = await self.store.get_current(spec_path)
        if not entity:
            raise ValueError(f"Spec not found: {spec_path}")

        # 2. Get analysis crystal
        crystal_data = await self.store.get_overlay(spec_path, "analysis_crystal")
        if not crystal_data:
            # No deep analysis yet - run it
            logger.warning(f"No analysis crystal for {spec_path}, running deep analysis")
            crystal = await self.analyze_deep(spec_path, author=author)
        else:
            crystal = AnalysisCrystal.from_dict(crystal_data)

        # 3. Build targets list
        targets = [
            *[a["path"] for a in crystal.anticipated],
            *crystal.placeholder_paths,
        ]

        # 4. Build prompt
        prompt = ExecutionPrompt(
            spec_path=spec_path,
            spec_content=entity.content_text,
            targets=targets,
            context={
                "claims": crystal.claims,
                "existing_refs": crystal.implementations,
                "spec_refs": crystal.spec_refs,
            },
        )

        # 5. Create witness mark (L-2 PROMPT)
        if self.witness:
            mark_result = await self.witness.save_mark(
                action=f"Generated prompt for: {spec_path}",
                reasoning=f"Targeting {len(targets)} implementations from spec analysis",
                tags=[
                    "prompt",
                    "codegen",
                    f"spec:{spec_path}",
                    f"targets:{len(targets)}",
                ],
                author=author,
            )
            prompt.mark_id = mark_result.mark_id

        # 6. Emit event
        if self.bus:
            await self.bus.publish(
                DocumentTopics.PROMPT_GENERATED,
                {
                    "spec_path": spec_path,
                    "target_count": len(targets),
                    "mark_id": prompt.mark_id,
                },
            )

        logger.info(f"Generated prompt for {spec_path}: {len(targets)} targets")
        return prompt

    async def capture_execution(
        self,
        prompt: ExecutionPrompt,
        generated_files: dict[str, str],  # path → content
        test_results: TestResults | None = None,
        author: str = "system",
    ) -> CaptureResult:
        """
        Capture execution results.

        Flow:
        1. For each generated file: ingest via resolve_placeholder()
        2. Create L-1 TRACE evidence marks
        3. If tests passed: create L1 TEST evidence marks
        4. Emit DIRECTOR_EXECUTION_CAPTURED event

        Args:
            prompt: The execution prompt that was used
            generated_files: Map of path → content (str)
            test_results: Test results (if any)
            author: Who is capturing

        Returns:
            CaptureResult with ingestion + evidence details
        """
        if test_results is None:
            test_results = TestResults()

        captured_files = []
        mark_ids = []

        # 1. Ingest all generated files
        for file_path, content in generated_files.items():
            # Resolve placeholder or regular ingest
            result = await self.resolve_placeholder(
                path=file_path,
                content=content.encode("utf-8"),
                source=f"codegen:{prompt.spec_path}",
                author=author,
            )
            captured_files.append(file_path)

            # 2. Create L-1 TRACE evidence mark
            if self.witness:
                trace_mark = await self.witness.save_mark(
                    action=f"Generated: {file_path}",
                    reasoning=f"From spec {prompt.spec_path} via execution prompt",
                    tags=[
                        "evidence:generated",
                        "evidence:trace",
                        f"spec:{prompt.spec_path}",
                        f"file:{file_path}",
                        "codegen",
                    ],
                    author=author,
                    parent_mark_id=prompt.mark_id,
                )
                mark_ids.append(trace_mark.mark_id)

            # 3. Create L1 TEST evidence if tests passed
            if test_results.passed_for(file_path):
                test_count = test_results.count_for(file_path)
                if self.witness:
                    test_mark = await self.witness.save_mark(
                        action=f"Tests passed: {file_path}",
                        reasoning=f"Generated code passes {test_count} tests, validates spec {prompt.spec_path}",
                        tags=[
                            "evidence:test",
                            "evidence:pass",
                            f"spec:{prompt.spec_path}",
                            f"file:{file_path}",
                        ],
                        author=author,
                        parent_mark_id=trace_mark.mark_id if mark_ids else None,
                    )
                    mark_ids.append(test_mark.mark_id)

        # 4. Emit event
        if self.bus:
            await self.bus.publish(
                DocumentTopics.EXECUTION_CAPTURED,
                {
                    "spec_path": prompt.spec_path,
                    "file_count": len(captured_files),
                    "mark_count": len(mark_ids),
                },
            )

        logger.info(
            f"Captured execution for {prompt.spec_path}: "
            f"{len(captured_files)} files, {len(mark_ids)} evidence marks"
        )

        return CaptureResult(
            spec_path=prompt.spec_path,
            captured=captured_files,
            test_results=test_results,
            mark_ids=mark_ids,
        )

    async def resolve_placeholder(
        self,
        path: str,
        content: bytes,
        source: str = "codegen",
        author: str = "system",
    ) -> ResolveResult:
        """
        Resolve a placeholder (or ingest new file).

        Flow:
        1. Check if path was a placeholder
        2. Ingest content
        3. If placeholder: mark resolved + create evidence links to anticipating specs
        4. Emit DIRECTOR_PLACEHOLDER_RESOLVED event

        Args:
            path: File path
            content: File content bytes
            source: Source identifier
            author: Who is resolving

        Returns:
            ResolveResult with resolution details
        """
        # 1. Check if placeholder
        existing = await self.store.get_current(path)
        is_placeholder = False
        linked_specs = []

        if existing:
            metadata = existing.metadata
            is_placeholder = metadata.get("is_placeholder", False)

            if is_placeholder:
                # Find specs that created this placeholder
                created_from = metadata.get("created_from")
                if created_from:
                    linked_specs.append(created_from)

        # 2. Ingest content
        from services.sovereign.types import IngestEvent

        event = IngestEvent.from_content(content, path, source=source)
        ingest_result = await self.ingestor.ingest(event, author=author)

        # 3. If placeholder: create evidence marks
        if is_placeholder and linked_specs:
            for spec_path in linked_specs:
                if self.witness:
                    await self.witness.save_mark(
                        action=f"Resolved anticipated: {path}",
                        reasoning=f"Implementation uploaded, spec {spec_path} now has evidence",
                        tags=[
                            f"spec:{spec_path}",
                            "evidence:impl",
                            f"file:{path}",
                            "placeholder-resolved",
                        ],
                        author=author,
                    )

            # 4. Emit event
            if self.bus:
                await self.bus.publish(
                    DocumentTopics.PLACEHOLDER_RESOLVED,
                    {
                        "path": path,
                        "linked_specs": linked_specs,
                        "version": ingest_result.version,
                    },
                )

            logger.info(f"Resolved placeholder {path} (linked to {len(linked_specs)} specs)")

        return ResolveResult(
            path=path,
            version=ingest_result.version,
            placeholder_resolved=is_placeholder,
            linked_specs=linked_specs,
        )

    async def get_status(self, path: str) -> dict[str, Any]:
        """
        Get full status for a document.

        Returns:
            Dict with:
            - entity: basic entity info
            - analysis: analysis state
            - crystal: analysis crystal (if exists)
            - counts: claims, refs, placeholders, evidence
        """
        # Get entity
        entity = await self.store.get_current(path)
        if not entity:
            return {
                "exists": False,
                "path": path,
            }

        # Get analysis state
        from services.sovereign.analysis import AnalysisState

        analysis_state = await self.store.get_analysis_state(path)

        # Get crystal
        crystal_data = await self.store.get_overlay(path, "analysis_crystal")
        crystal = AnalysisCrystal.from_dict(crystal_data) if crystal_data else None

        # Build counts
        counts = {
            "claims": len(crystal.claims) if crystal else 0,
            "refs": len(crystal.discovered_refs) if crystal else 0,
            "placeholders": len(crystal.placeholder_paths) if crystal else 0,
            "anticipated": len(crystal.anticipated) if crystal else 0,
            "implementations": len(crystal.implementations) if crystal else 0,
            "tests": len(crystal.tests) if crystal else 0,
        }

        return {
            "exists": True,
            "path": path,
            "version": entity.version,
            "content_hash": entity.content_hash,
            "analysis_status": analysis_state.status.value if analysis_state else "unknown",
            "analysis_complete": analysis_state.is_complete if analysis_state else False,
            "has_crystal": crystal is not None,
            "counts": counts,
            "crystal": crystal.to_dict() if crystal else None,
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "DocumentDirector",
    "AnalysisCrystal",
    "ExecutionPrompt",
    "CaptureResult",
    "ResolveResult",
]
