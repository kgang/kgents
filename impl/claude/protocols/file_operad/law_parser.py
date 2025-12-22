"""
Law Parser: Parse .law Markdown Files into Structured LawDefinition.

"The proof IS the decision. The mark IS the witness."

.law files are human-readable markdown documents with structured sections:
- Statement: The mathematical equation
- Verification: Embedded Python test code
- Last Verified: Audit trail
- Wires To: Cross-operad links

This parser extracts these into a frozen LawDefinition dataclass for
programmatic verification and ASHC integration.

See: spec/protocols/file-operad.md (Session 6)

Teaching:
    gotcha: Status parsing uses emoji detection (✅, ❌, ⏸) because
            .law files are human-first documents. The parser is forgiving
            of formatting variations.

    gotcha: Verification code is extracted raw (including ```python fences)
            for inspection. The caller strips fences before execution.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any

# =============================================================================
# Types
# =============================================================================


class LawStatus(Enum):
    """
    Verification status of a law.

    Follows spec: each law has a living status based on last verification.
    """

    VERIFIED = auto()  # ✅ All tests pass
    UNVERIFIED = auto()  # ⏸ Not yet verified
    FAILED = auto()  # ❌ Verification failed


# =============================================================================
# LawDefinition Dataclass
# =============================================================================


@dataclass(frozen=True)
class LawDefinition:
    """
    Parsed law from .law markdown file.

    Frozen for immutability—law definitions are facts, not mutable state.
    Use dataclasses.replace() to create modified versions.

    Laws:
        1. Immutability: Once parsed, a LawDefinition never changes
        2. Completeness: All fields required for verification are present
        3. Traceability: source_path links back to original file

    Example:
        >>> law = parse_law_file(Path("~/.kgents/operads/AGENT_OPERAD/_laws/seq_associativity.law"))
        >>> law.name
        'seq_associativity'
        >>> law.status
        <LawStatus.VERIFIED: 1>
    """

    # Core identification
    name: str  # "create_read_identity"
    equation: str  # "read(create(p, c)) ≡ c"

    # Metadata
    operations: tuple[str, ...]  # ("read", "create")
    category: str  # "Identity" | "Composition" | "Preservation"
    status: LawStatus  # Current verification status

    # Verification
    verification_code: str  # Embedded Python test code
    description: str = ""  # Human-readable description

    # Cross-references
    wires_to: tuple[str, ...] = ()  # Links to operations/other laws

    # Audit trail
    last_verified: datetime | None = None
    verified_by: str | None = None
    source_path: str | None = None  # Original file path

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for persistence/API."""
        return {
            "name": self.name,
            "equation": self.equation,
            "operations": list(self.operations),
            "category": self.category,
            "status": self.status.name,
            "verification_code": self.verification_code,
            "description": self.description,
            "wires_to": list(self.wires_to),
            "last_verified": self.last_verified.isoformat() if self.last_verified else None,
            "verified_by": self.verified_by,
            "source_path": self.source_path,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LawDefinition":
        """Deserialize from dictionary."""
        last_verified = data.get("last_verified")
        if isinstance(last_verified, str):
            last_verified = datetime.fromisoformat(last_verified)

        return cls(
            name=data["name"],
            equation=data["equation"],
            operations=tuple(data.get("operations", [])),
            category=data.get("category", ""),
            status=LawStatus[data.get("status", "UNVERIFIED")],
            verification_code=data.get("verification_code", ""),
            description=data.get("description", ""),
            wires_to=tuple(data.get("wires_to", [])),
            last_verified=last_verified,
            verified_by=data.get("verified_by"),
            source_path=data.get("source_path"),
        )

    @property
    def is_verified(self) -> bool:
        """Check if law is currently verified."""
        return self.status == LawStatus.VERIFIED

    @property
    def status_emoji(self) -> str:
        """Get emoji for current status (for display)."""
        return {
            LawStatus.VERIFIED: "✅",
            LawStatus.UNVERIFIED: "⏸",
            LawStatus.FAILED: "❌",
        }[self.status]


# =============================================================================
# Parsing Helpers
# =============================================================================


def _parse_name(content: str) -> str:
    """
    Extract law name from "# Law: name" header.

    Returns empty string if not found.
    """
    match = re.search(r"^#\s*Law:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def _parse_status(content: str) -> LawStatus:
    """
    Parse status from "**Status**: ✅ VERIFIED" line.

    Looks for emoji or text indicators.
    """
    # Check for emoji first
    if "✅" in content:
        return LawStatus.VERIFIED
    if "❌" in content:
        return LawStatus.FAILED
    if "⏸" in content:
        return LawStatus.UNVERIFIED

    # Check for text
    status_match = re.search(r"\*\*Status\*\*:\s*(.+)$", content, re.MULTILINE)
    if status_match:
        status_text = status_match.group(1).strip().upper()
        if "VERIFIED" in status_text or "PASSED" in status_text:
            return LawStatus.VERIFIED
        if "FAILED" in status_text or "ERROR" in status_text:
            return LawStatus.FAILED

    return LawStatus.UNVERIFIED


def _parse_operations(content: str) -> tuple[str, ...]:
    """
    Parse operations from "**Operations**: `op1`, `op2`" line.

    Returns tuple of operation names.
    """
    match = re.search(r"\*\*Operations\*\*:\s*(.+)$", content, re.MULTILINE)
    if match:
        ops_text = match.group(1)
        # Extract backtick-wrapped names
        ops = re.findall(r"`([^`]+)`", ops_text)
        return tuple(ops)
    return ()


def _parse_category(content: str) -> str:
    """
    Parse category from "**Category**: Identity" line.
    """
    match = re.search(r"\*\*Category\*\*:\s*(.+)$", content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def _parse_section(content: str, section_name: str) -> str:
    """
    Extract content between "## Section" and next "## " or "---".

    Returns empty string if section not found.
    """
    # Pattern: ## Section\n ... (until next ## or ---)
    pattern = rf"##\s*{re.escape(section_name)}\s*\n(.*?)(?=\n##|\n---|\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def _parse_statement(content: str) -> str:
    """
    Parse the equation from the Statement section.

    Extracts content from code fence if present, otherwise takes first non-empty line.
    """
    statement_section = _parse_section(content, "Statement")
    if not statement_section:
        return ""

    # Look for code fence
    code_match = re.search(r"```\w*\n(.+?)\n```", statement_section, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # Take first non-empty line that looks like an equation
    for line in statement_section.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith(">"):
            # Skip pure prose sentences
            if "≡" in line or "==" in line or "->" in line or "→" in line:
                return line
            # If no operators, might be on next line
    return ""


def _parse_verification_code(content: str) -> str:
    """
    Parse verification code from the Verification section.

    Returns the full code block including fences for inspection.
    Caller strips fences before execution.
    """
    verification_section = _parse_section(content, "Verification")
    if not verification_section:
        return ""

    # Extract code block (including fence markers for inspection)
    code_match = re.search(r"(```python\n.+?\n```)", verification_section, re.DOTALL)
    if code_match:
        return code_match.group(1)

    # Alternative: any code fence
    code_match = re.search(r"(```\w*\n.+?\n```)", verification_section, re.DOTALL)
    if code_match:
        return code_match.group(1)

    return ""


def _parse_description(content: str) -> str:
    """
    Parse description from blockquote after title.

    Looks for: > *"Some description."*
    """
    match = re.search(r">\s*\*[\"'](.+?)[\"']\*", content)
    if match:
        return match.group(1).strip()
    return ""


def _parse_last_verified(content: str) -> tuple[datetime | None, str | None]:
    """
    Parse last verification info from "## Last Verified" section.

    Returns (datetime, verified_by) tuple.
    """
    section = _parse_section(content, "Last Verified")
    if not section:
        return None, None

    # Parse date
    date_match = re.search(r"\*\*Date\*\*:\s*(.+)$", section, re.MULTILINE)
    verified_date = None
    if date_match:
        date_str = date_match.group(1).strip()
        try:
            verified_date = datetime.fromisoformat(date_str)
        except ValueError:
            # Try parsing common formats
            try:
                verified_date = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                pass

    # Parse by
    by_match = re.search(r"\*\*By\*\*:\s*(.+)$", section, re.MULTILINE)
    verified_by = by_match.group(1).strip() if by_match else None

    return verified_date, verified_by


def _parse_wires_to(content: str) -> tuple[str, ...]:
    """
    Parse wires from "## Wires To" section.

    Format: - [edge_type] `path`
    """
    section = _parse_section(content, "Wires To")
    if not section:
        return ()

    # Extract paths from backticks
    paths = re.findall(r"`([^`]+)`", section)
    return tuple(paths)


# =============================================================================
# Main Parser Functions
# =============================================================================


def parse_law_markdown(content: str, source_path: str | None = None) -> LawDefinition:
    """
    Parse a .law markdown file into a LawDefinition.

    Args:
        content: The markdown content of the .law file
        source_path: Optional path to the source file (for traceability)

    Returns:
        LawDefinition with all parsed fields

    Raises:
        ValueError: If required fields (name, equation) are missing

    Example:
        >>> content = '''
        ... # Law: create_read_identity
        ...
        ... > *"Created content is immediately readable."*
        ...
        ... **Status**: ✅ VERIFIED
        ... **Operations**: `create`, `read`
        ... **Category**: Identity
        ...
        ... ## Statement
        ...
        ... read(create(p, c)) ≡ c
        ... '''
        >>> law = parse_law_markdown(content)
        >>> law.name
        'create_read_identity'
    """
    name = _parse_name(content)
    if not name:
        raise ValueError("Law file must have '# Law: <name>' header")

    equation = _parse_statement(content)
    if not equation:
        # Try to extract from Statement section more broadly
        statement_section = _parse_section(content, "Statement")
        if statement_section:
            # Take first code fence or meaningful line
            for line in statement_section.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith(">"):
                    if not line.startswith("For ") and not line.startswith("This "):
                        equation = line
                        break

    status = _parse_status(content)
    operations = _parse_operations(content)
    category = _parse_category(content)
    verification_code = _parse_verification_code(content)
    description = _parse_description(content)
    wires_to = _parse_wires_to(content)
    last_verified, verified_by = _parse_last_verified(content)

    return LawDefinition(
        name=name,
        equation=equation,
        operations=operations,
        category=category,
        status=status,
        verification_code=verification_code,
        description=description,
        wires_to=wires_to,
        last_verified=last_verified,
        verified_by=verified_by,
        source_path=source_path,
    )


def parse_law_file(path: Path | str) -> LawDefinition:
    """
    Parse a .law file from filesystem.

    Args:
        path: Path to the .law file

    Returns:
        LawDefinition with source_path set

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is malformed
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Law file not found: {path}")

    content = path.read_text()
    return parse_law_markdown(content, source_path=str(path))


def list_laws_in_operad(operad_path: Path | str) -> list[LawDefinition]:
    """
    List all laws in an operad's _laws/ directory.

    Args:
        operad_path: Path to operad directory (e.g., ~/.kgents/operads/FILE_OPERAD)

    Returns:
        List of parsed LawDefinitions
    """
    operad_path = Path(operad_path)
    laws_dir = operad_path / "_laws"

    if not laws_dir.exists():
        return []

    laws = []
    for law_file in sorted(laws_dir.glob("*.law")):
        try:
            law = parse_law_file(law_file)
            laws.append(law)
        except (ValueError, FileNotFoundError) as e:
            # Log but don't fail on individual file errors
            import logging

            logging.getLogger("kgents.file_operad.law_parser").warning(
                f"Failed to parse {law_file}: {e}"
            )

    return laws


def extract_verification_code(law: LawDefinition) -> str:
    """
    Extract executable Python code from a law's verification_code.

    Strips ```python fences and returns pure code.
    """
    code = law.verification_code
    if not code:
        return ""

    # Strip code fence
    code = re.sub(r"^```\w*\n", "", code)
    code = re.sub(r"\n```$", "", code)

    return code.strip()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "LawStatus",
    "LawDefinition",
    # Parser functions
    "parse_law_markdown",
    "parse_law_file",
    "list_laws_in_operad",
    "extract_verification_code",
]
