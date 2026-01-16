"""
LLM-Powered Document Analyzer: Extract structure and connections using Claude.

> *"LLM analysis reveals the 80/20 connections humans would find obvious."*

This module provides LLM-powered document analysis that complements the
structural analyzer. It extracts:

    Content Analysis:
        - Title and summary
        - Key claims/assertions
        - Document type classification

    Connection Discovery:
        - Explicit references (spec/*, impl/*, AGENTESE paths)
        - Semantic connections (mentions of known concepts)
        - Suggested connections (80/20 obvious links)
        - Placeholder candidates (missing refs to create)

The analyzer uses ClaudeCLIRuntime for execution, leveraging the
existing retry logic (Fix pattern) and response coercion.

Teaching:
    gotcha: This is for 80/20 OBVIOUS connections, not complete knowledge graphs.
            Trust the LLM to find what's explicit and semantically clear.
            Don't try to build perfect ontologies.

    gotcha: AnalysisCrystal is immutable by default. Use with_mark_id() to
            add mark linkage after witnessing.

See: plans/claude-document-analysis.md
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any

from runtime.base import AgentContext, LLMAgent
from runtime.cli import ClaudeCLIRuntime

logger = logging.getLogger(__name__)


# =============================================================================
# Data Types
# =============================================================================


@dataclass(frozen=True)
class SuggestedConnection:
    """
    A suggested connection between documents.

    Fields:
        target: Path to connect to (e.g., "spec/protocols/k-block.md")
        reason: Why this connection makes sense
        confidence: 0.0-1.0 confidence score

    Example:
        >>> conn = SuggestedConnection(
        ...     target="spec/protocols/witness.md",
        ...     reason="Document mentions witness marks and witnessing pattern",
        ...     confidence=0.85,
        ... )
    """

    target: str
    reason: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "target": self.target,
            "reason": self.reason,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SuggestedConnection:
        """Create from dictionary."""
        return cls(
            target=data.get("target", ""),
            reason=data.get("reason", ""),
            confidence=float(data.get("confidence", 0.5)),
        )


@dataclass
class AnalysisCrystal:
    """
    Crystallized analysis of a document.

    Contains extracted structure and discovered connections.
    This is the primary output of LLM-powered document analysis.

    Fields:
        title: Document title (extracted or inferred)
        summary: 1-2 sentence summary of the document
        document_type: Classification (spec, guide, reference, api, impl, etc.)
        claims: Key claims or assertions made in the document
        references: Discovered explicit references (file paths, AGENTESE paths)
        suggested_connections: 80/20 bootstrap connections with confidence
        placeholders: Missing references that should become placeholders
        analyzed_by: "claude" for LLM analysis, "structural" for fallback
        analysis_mark_id: Optional witness mark ID (set after witnessing)

    Example:
        >>> crystal = AnalysisCrystal(
        ...     title="K-Block Protocol",
        ...     summary="Defines the K-Block verification protocol for sovereign data.",
        ...     document_type="spec",
        ...     claims=["All exports must be witnessed", "K-Blocks are immutable"],
        ...     references=["spec/protocols/witness.md", "impl/claude/services/sovereign/"],
        ...     suggested_connections=[
        ...         SuggestedConnection("spec/protocols/sovereign.md", "Related sovereignty concept", 0.9),
        ...     ],
        ...     placeholders=["spec/protocols/export.md"],
        ...     analyzed_by="claude",
        ... )
    """

    title: str
    summary: str
    document_type: str
    claims: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    suggested_connections: list[SuggestedConnection] = field(default_factory=list)
    placeholders: list[str] = field(default_factory=list)
    analyzed_by: str = "claude"
    analysis_mark_id: str | None = None

    def with_mark_id(self, mark_id: str) -> AnalysisCrystal:
        """Return a copy with the analysis mark ID set."""
        return AnalysisCrystal(
            title=self.title,
            summary=self.summary,
            document_type=self.document_type,
            claims=list(self.claims),
            references=list(self.references),
            suggested_connections=list(self.suggested_connections),
            placeholders=list(self.placeholders),
            analyzed_by=self.analyzed_by,
            analysis_mark_id=mark_id,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "summary": self.summary,
            "document_type": self.document_type,
            "claims": self.claims,
            "references": self.references,
            "suggested_connections": [c.to_dict() for c in self.suggested_connections],
            "placeholders": self.placeholders,
            "analyzed_by": self.analyzed_by,
            "analysis_mark_id": self.analysis_mark_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnalysisCrystal:
        """Create from dictionary."""
        suggested_connections = [
            SuggestedConnection.from_dict(c) for c in data.get("suggested_connections", [])
        ]

        return cls(
            title=data.get("title", "Untitled"),
            summary=data.get("summary", ""),
            document_type=data.get("document_type", "unknown"),
            claims=data.get("claims", []),
            references=data.get("references", []),
            suggested_connections=suggested_connections,
            placeholders=data.get("placeholders", []),
            analyzed_by=data.get("analyzed_by", "structural"),
            analysis_mark_id=data.get("analysis_mark_id"),
        )

    @classmethod
    def empty(cls, analyzed_by: str = "structural") -> AnalysisCrystal:
        """Create an empty crystal (used for fallback)."""
        return cls(
            title="Untitled",
            summary="",
            document_type="unknown",
            analyzed_by=analyzed_by,
        )


# =============================================================================
# Document Analysis Agent
# =============================================================================


# The expected JSON schema for the LLM response
ANALYSIS_SCHEMA = """{
    "title": "string - document title (extracted from content or inferred)",
    "summary": "string - 1-2 sentence summary of the document",
    "document_type": "string - one of: spec, guide, reference, api, impl, config, doc, unknown",
    "claims": ["string - key claims or assertions made in the document"],
    "references": ["string - discovered file paths (spec/*, impl/*, etc.) or AGENTESE paths"],
    "suggested_connections": [
        {
            "target": "string - path to related document",
            "reason": "string - why this connection makes sense",
            "confidence": "number 0.0-1.0"
        }
    ],
    "placeholders": ["string - paths mentioned but likely don't exist yet"]
}"""


class DocumentAnalysisAgent(LLMAgent[str, AnalysisCrystal]):
    """
    LLM-powered document analysis using ClaudeCLIRuntime.

    This agent:
    1. Takes document content as input
    2. Builds a prompt requesting structured JSON analysis
    3. Parses the LLM response into an AnalysisCrystal

    The agent focuses on 80/20 obvious connections:
    - Explicit references: paths mentioned in the text
    - Semantic similarity: concepts that clearly relate to known specs
    - Implementation hints: code references, module mentions

    Example:
        >>> agent = DocumentAnalysisAgent()
        >>> runtime = ClaudeCLIRuntime()
        >>> result = await runtime.execute(agent, document_content)
        >>> crystal = result.output
    """

    def __init__(self) -> None:
        """Initialize the document analysis agent."""
        # Store expected format for coercion (used by ClaudeCLIRuntime)
        self._expected_format = ANALYSIS_SCHEMA

    @property
    def name(self) -> str:
        """Agent name for logging."""
        return "DocumentAnalysisAgent"

    async def invoke(self, input: str) -> AnalysisCrystal:
        """
        Not implemented - use execute_async with runtime instead.

        The LLMAgent pattern requires a runtime for execution.
        """
        raise NotImplementedError(
            "DocumentAnalysisAgent requires runtime. Use execute_async or runtime.execute()."
        )

    def build_prompt(self, content: str) -> AgentContext:
        """
        Build the analysis prompt for Claude.

        The prompt requests structured JSON output with the AnalysisCrystal schema.
        It focuses on 80/20 obvious connections rather than exhaustive analysis.

        Args:
            content: Document content to analyze

        Returns:
            AgentContext with system prompt and user message
        """
        system_prompt = (
            """You are a document analyzer for a knowledge management system.

Your task is to analyze documents and extract structured information.

FOCUS ON 80/20 OBVIOUS CONNECTIONS:
- Extract explicit references (file paths like spec/*, impl/*, AGENTESE paths like world.*, self.*, etc.)
- Identify semantic connections that are CLEAR and OBVIOUS (not speculative)
- Note paths mentioned that might not exist yet (placeholders)

DO NOT:
- Speculate about distant or uncertain connections
- Try to build complete ontologies
- Over-interpret vague mentions

DOCUMENT TYPES:
- spec: Specification documents (requirements, protocols, designs)
- guide: How-to guides and tutorials
- reference: API references, function documentation
- api: REST API, GraphQL, or protocol definitions
- impl: Implementation code or implementation notes
- config: Configuration files or schemas
- doc: General documentation
- unknown: Cannot determine

OUTPUT FORMAT:
Return ONLY valid JSON matching this schema (no markdown, no explanation):
"""
            + ANALYSIS_SCHEMA
        )

        user_message = f"""Analyze this document and return structured JSON:

---
{content[:15000]}
---

Return ONLY the JSON object, no markdown code blocks, no explanation."""

        return AgentContext(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=0.3,  # Low temperature for structured extraction
            max_tokens=4096,
        )

    def parse_response(self, response: str) -> AnalysisCrystal:
        """
        Parse the LLM response into an AnalysisCrystal.

        Handles common LLM output quirks:
        - Response might be in markdown code blocks
        - Fields might be missing (uses defaults)
        - Arrays might be empty vs null

        Args:
            response: Raw LLM response text

        Returns:
            AnalysisCrystal with parsed data

        Raises:
            ValueError: If JSON cannot be extracted or parsed
        """
        # Try to extract JSON from various formats
        json_text = self._extract_json(response)

        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {e}. Raw: {json_text[:200]}")

        # Validate and normalize data
        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON object, got {type(data).__name__}")

        # Normalize fields
        data = self._normalize_data(data)

        return AnalysisCrystal.from_dict(data)

    def _extract_json(self, response: str) -> str:
        """
        Extract JSON from various response formats.

        Handles:
        - Raw JSON
        - JSON in markdown code blocks (```json ... ```)
        - JSON with surrounding text
        """
        response = response.strip()

        # Try raw JSON first
        if response.startswith("{") and response.endswith("}"):
            return response

        # Try markdown code block
        code_block_patterns = [
            r"```json\s*\n?(.*?)\n?```",
            r"```\s*\n?(.*?)\n?```",
        ]

        for pattern in code_block_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                extracted = match.group(1).strip()
                if extracted.startswith("{"):
                    return extracted

        # Try to find JSON object in the response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            return json_match.group(0)

        # Last resort: return as-is (will fail in parse)
        return response

    def _normalize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Normalize parsed data to ensure all required fields exist.

        Handles:
        - Missing fields (use defaults)
        - null vs empty arrays
        - Type coercion
        """
        normalized: dict[str, Any] = {
            "title": str(data.get("title", "Untitled")),
            "summary": str(data.get("summary", "")),
            "document_type": str(data.get("document_type", "unknown")).lower(),
            "claims": self._ensure_string_list(data.get("claims")),
            "references": self._ensure_string_list(data.get("references")),
            "suggested_connections": self._normalize_connections(data.get("suggested_connections")),
            "placeholders": self._ensure_string_list(data.get("placeholders")),
            "analyzed_by": "claude",
        }

        # Validate document_type
        valid_types = {"spec", "guide", "reference", "api", "impl", "config", "doc", "unknown"}
        if normalized["document_type"] not in valid_types:
            normalized["document_type"] = "unknown"

        return normalized

    def _ensure_string_list(self, value: Any) -> list[str]:
        """Ensure value is a list of strings."""
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if item]
        return []

    def _normalize_connections(self, connections: Any) -> list[dict[str, Any]]:
        """Normalize suggested_connections to list of dicts."""
        if connections is None:
            return []
        if not isinstance(connections, list):
            return []

        normalized = []
        for conn in connections:
            if isinstance(conn, dict):
                normalized.append(
                    {
                        "target": str(conn.get("target", "")),
                        "reason": str(conn.get("reason", "")),
                        "confidence": float(conn.get("confidence", 0.5)),
                    }
                )
        return normalized


# =============================================================================
# Convenience Function
# =============================================================================


async def analyze_with_claude(
    content: str,
    verbose: bool = False,
    timeout: float = 120.0,
    max_retries: int = 3,
) -> AnalysisCrystal:
    """
    Analyze a document using Claude LLM.

    This is the main entry point for LLM-powered document analysis.
    Creates the runtime and agent, executes, and returns the crystal.

    On failure, returns a minimal crystal with analyzed_by="structural"
    to indicate fallback analysis should be used.

    Args:
        content: Document content to analyze
        verbose: Print progress messages during execution
        timeout: Timeout in seconds for CLI execution
        max_retries: Maximum retries on parse failures

    Returns:
        AnalysisCrystal with analysis results

    Example:
        >>> content = open("spec/protocols/k-block.md").read()
        >>> crystal = await analyze_with_claude(content)
        >>> print(f"Title: {crystal.title}")
        >>> print(f"Found {len(crystal.references)} references")
    """
    try:
        runtime = ClaudeCLIRuntime(
            timeout=timeout,
            max_retries=max_retries,
            verbose=verbose,
            enable_coercion=True,
            coercion_confidence=0.8,
        )
        agent = DocumentAnalysisAgent()

        result = await runtime.execute(agent, content)
        return result.output

    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        # Return empty crystal with structural flag for fallback
        return AnalysisCrystal.empty(analyzed_by="structural")


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SuggestedConnection",
    "AnalysisCrystal",
    "DocumentAnalysisAgent",
    "analyze_with_claude",
]
