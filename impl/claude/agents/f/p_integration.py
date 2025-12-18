"""
F-gent Artifact Parser Integration with P-gents Protocol

This module provides parsers that extract F-gent artifacts from .alo.md files
or LLM responses, conforming to the P-gents Parser[A] protocol.

Architecture:
- Parses .alo.md markdown format into Artifact objects
- Implements Parser[Artifact] for composability
- Supports parsing both complete artifacts and partial/in-progress artifacts
"""

from __future__ import annotations

import re
from typing import Any, Iterator, Optional

from agents.p.core import (
    Parser,
    ParserConfig as PParserConfig,
    ParseResult as PParseResult,
)

from .contract import Contract
from .crystallize import Artifact, ArtifactMetadata, ArtifactStatus, Version
from .intent import Intent
from .prototype import SourceCode, StaticAnalysisReport


class FgentArtifactParser:
    """
    F-gent artifact parser conforming to P-gents Parser[Artifact].

    Parses .alo.md markdown format with sections:
    - YAML frontmatter (metadata)
    - Section 1: THE INTENT (human-editable)
    - Section 2: THE CONTRACT (machine-verified)
    - Section 4: THE IMPLEMENTATION (auto-generated)

    Example:
        >>> from agents.f.p_integration import artifact_parser
        >>> parser = artifact_parser()
        >>> with open("my_agent.alo.md") as f:
        ...     result = parser.parse(f.read())
        >>> if result.success:
        ...     print(f"Artifact: {result.value.contract.agent_name}")
        ...     print(f"Version: {result.value.metadata.version}")
    """

    def __init__(self, config: Optional[PParserConfig] = None):
        self.config = config or PParserConfig()

    def parse(self, text: str) -> PParseResult[Artifact]:
        """
        Parse .alo.md markdown into Artifact.

        Args:
            text: .alo.md markdown text

        Returns:
            PParseResult[Artifact] with parsed artifact
        """
        try:
            # Parse sections
            metadata = self._parse_metadata(text)
            intent = self._parse_intent(text)
            contract = self._parse_contract(text)
            source_code = self._parse_source_code(text)

            # Build artifact
            artifact = Artifact(
                metadata=metadata,
                intent=intent,
                contract=contract,
                source_code=source_code,
            )

            # Assess confidence
            confidence = self._assess_confidence(text, artifact)

            return PParseResult(
                success=True,
                value=artifact,
                strategy="f-gent:artifact",
                confidence=confidence,
                metadata={
                    "artifact_id": metadata.id,
                    "version": str(metadata.version),
                    "status": metadata.status.value,
                },
            )

        except Exception as e:
            return PParseResult(
                success=False,
                error=f"Failed to parse F-gent artifact: {str(e)}",
                strategy="f-gent:artifact",
                confidence=0.0,
            )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[PParseResult[Artifact]]:
        """
        Stream parsing for artifacts (accumulate and parse at section boundaries).
        """
        accumulated = []
        section_markers = [
            "# 1. THE INTENT",
            "# 2. THE CONTRACT",
            "# 4. THE IMPLEMENTATION",
        ]

        for token in tokens:
            accumulated.append(token)
            text = "".join(accumulated)

            # Try parsing at section boundaries
            if any(marker in token for marker in section_markers):
                result = self.parse(text)
                if result.success:
                    yield PParseResult(
                        success=True,
                        value=result.value,
                        strategy=result.strategy,
                        confidence=result.confidence * 0.85,  # Reduce for partial
                        partial=True,
                        metadata=result.metadata,
                    )

        # Final parse
        final_text = "".join(accumulated)
        yield self.parse(final_text)

    def configure(self, **config: Any) -> "FgentArtifactParser":
        """Return new parser with updated P-gents config."""
        new_config = PParserConfig(**{**vars(self.config), **config})
        new_config.validate()
        return FgentArtifactParser(config=new_config)

    def _parse_metadata(self, text: str) -> ArtifactMetadata:
        """Parse YAML frontmatter metadata."""
        # Extract YAML frontmatter
        yaml_match = re.search(r"^---\s*\n(.*?)\n---", text, re.DOTALL | re.MULTILINE)
        if not yaml_match:
            raise ValueError("No YAML frontmatter found")

        yaml_text = yaml_match.group(1)

        # Parse fields
        id_match = re.search(r'id:\s*["\']?([^"\'\n]+)["\']?', yaml_text)
        version_match = re.search(r'version:\s*["\']?([^"\'\n]+)["\']?', yaml_text)
        created_at_match = re.search(r'created_at:\s*["\']?([^"\'\n]+)["\']?', yaml_text)
        created_by_match = re.search(r'created_by:\s*["\']?([^"\'\n]+)["\']?', yaml_text)
        status_match = re.search(r'status:\s*["\']?([^"\'\n]+)["\']?', yaml_text)
        hash_match = re.search(r'hash:\s*["\']?([^"\'\n]+)["\']?', yaml_text)

        # Parse tags
        tags = []
        tags_section = re.search(r"tags:\s*\n((?:\s*-\s*[^\n]+\n?)*)", yaml_text)
        if tags_section:
            tag_lines = re.findall(r'-\s*["\']?([^"\'\n]+)["\']?', tags_section.group(1))
            tags = tag_lines

        # Parse dependencies
        dependencies = []
        deps_section = re.search(r"dependencies:\s*\n((?:\s*-\s*[^\n]+\n?)*)", yaml_text)
        if deps_section:
            dep_lines = re.findall(r'-\s*["\']?([^"\'\n]+)["\']?', deps_section.group(1))
            dependencies = dep_lines

        return ArtifactMetadata(
            id=id_match.group(1) if id_match else "unknown",
            version=Version.parse(version_match.group(1)) if version_match else Version(1, 0, 0),
            created_at=created_at_match.group(1) if created_at_match else "",
            created_by=created_by_match.group(1) if created_by_match else "f-gent",
            status=ArtifactStatus(status_match.group(1))
            if status_match
            else ArtifactStatus.EXPERIMENTAL,
            hash=hash_match.group(1) if hash_match else "",
            tags=tags,
            dependencies=dependencies,
        )

    def _parse_intent(self, text: str) -> Intent:
        """Parse THE INTENT section."""
        intent_section = re.search(r"# 1\. THE INTENT.*?\n(.*?)(?=\n#|\Z)", text, re.DOTALL)
        if not intent_section:
            raise ValueError("No INTENT section found")

        intent_text = intent_section.group(1)

        # Parse purpose
        purpose_match = re.search(
            r"\*\*Purpose\*\*:\s*(.+?)(?=\n\n|\n\*\*|\Z)", intent_text, re.DOTALL
        )
        purpose = purpose_match.group(1).strip() if purpose_match else ""

        # Parse behavior
        behavior = []
        behavior_section = re.search(r"\*\*Behavior\*\*:\s*\n((?:\s*-\s*[^\n]+\n?)*)", intent_text)
        if behavior_section:
            behavior = re.findall(r"-\s*(.+)", behavior_section.group(1))

        # Parse constraints
        constraints = []
        constraints_section = re.search(
            r"\*\*Constraints\*\*:\s*\n((?:\s*-\s*[^\n]+\n?)*)", intent_text
        )
        if constraints_section:
            constraints = re.findall(r"-\s*(.+)", constraints_section.group(1))

        # Parse tone
        tone_match = re.search(r"\*\*Tone\*\*:\s*(.+)", intent_text)
        tone = tone_match.group(1).strip() if tone_match else None

        return Intent(
            purpose=purpose,
            behavior=behavior,
            constraints=constraints,
            tone=tone,
        )

    def _parse_contract(self, text: str) -> Contract:
        """Parse THE CONTRACT section."""
        contract_section = re.search(
            r"# 2\. THE CONTRACT.*?\n(.*?)(?=\n# [0-9]|\Z)", text, re.DOTALL
        )
        if not contract_section:
            raise ValueError("No CONTRACT section found")

        contract_text = contract_section.group(1)

        # Parse agent name (try multiple formats)
        name_match = re.search(r"\*\*Agent Name\*\*:\s*`([^`]+)`", contract_text, re.MULTILINE)
        if not name_match:
            name_match = re.search(r"Agent Name:\s*`([^`]+)`", contract_text, re.MULTILINE)
        agent_name = name_match.group(1) if name_match else "UnknownAgent"

        # Parse input/output types
        input_match = re.search(r"\*\*Input Type\*\*:\s*`([^`]+)`", contract_text, re.MULTILINE)
        if not input_match:
            input_match = re.search(r"Input Type:\s*`([^`]+)`", contract_text, re.MULTILINE)

        output_match = re.search(r"\*\*Output Type\*\*:\s*`([^`]+)`", contract_text, re.MULTILINE)
        if not output_match:
            output_match = re.search(r"Output Type:\s*`([^`]+)`", contract_text, re.MULTILINE)

        input_type = input_match.group(1) if input_match else "Any"
        output_type = output_match.group(1) if output_match else "Any"

        # Parse invariants (simplified - would need full parser for complex cases)
        from agents.f.contract import Invariant

        invariants: list[Invariant] = []

        return Contract(
            agent_name=agent_name,
            input_type=input_type,
            output_type=output_type,
            invariants=invariants,
            composition_rules=[],
        )

    def _parse_source_code(self, text: str) -> SourceCode:
        """Parse THE IMPLEMENTATION section."""
        impl_section = re.search(
            r"# 4\. THE IMPLEMENTATION.*?\n.*?```python\s*\n(.*?)```", text, re.DOTALL
        )
        if not impl_section:
            # Return minimal source code if not found
            return SourceCode(
                code="# No implementation found",
                analysis_report=StaticAnalysisReport(passed=False),
            )

        code = impl_section.group(1).strip()
        # Create a basic analysis report (parsers don't validate, just extract)
        return SourceCode(
            code=code,
            analysis_report=StaticAnalysisReport(passed=True),
        )

    def _assess_confidence(self, text: str, artifact: Artifact) -> float:
        """
        Assess confidence in parsed artifact.

        Factors:
        - All required sections present
        - Valid YAML frontmatter
        - Non-empty intent/contract/code
        - Valid version number
        """
        confidence = 0.5  # Base confidence

        # YAML frontmatter valid
        if artifact.metadata.id and artifact.metadata.id != "unknown":
            confidence += 0.1

        # Intent has purpose
        if artifact.intent.purpose:
            confidence += 0.15

        # Contract has agent name and types
        if artifact.contract.agent_name and artifact.contract.agent_name != "UnknownAgent":
            confidence += 0.1

        # Source code present
        if artifact.source_code.code and "No implementation found" not in artifact.source_code.code:
            confidence += 0.15

        return min(1.0, max(0.0, confidence))


def artifact_parser(config: Optional[PParserConfig] = None) -> Parser[Artifact]:
    """
    Create F-gent artifact parser conforming to P-gents protocol.

    This is the standard parser for F-gent .alo.md artifacts.

    Usage:
        >>> from agents.f.p_integration import artifact_parser
        >>> parser = artifact_parser()
        >>> with open("my_agent.alo.md") as f:
        ...     result = parser.parse(f.read())
        >>> if result.success:
        ...     artifact = result.value
        ...     print(f"Parsed: {artifact.contract.agent_name} v{artifact.metadata.version}")
    """
    return FgentArtifactParser(config=config)
