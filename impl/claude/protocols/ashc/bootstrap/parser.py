"""
ASHC Bootstrap Spec Parser

Parses spec/bootstrap.md into structured BootstrapAgentSpec objects.

Each spec captures:
- Agent name (Id, Compose, Judge, etc.)
- Type signature (A → A, (Agent, Agent) → Agent)
- Laws/invariants the agent must satisfy
- Full section content for generation prompts

> "The spec is the compressed Ground. Human judgment captured once."
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

# =============================================================================
# Constants
# =============================================================================

AGENT_NAMES = ["Id", "Compose", "Judge", "Ground", "Contradict", "Sublate", "Fix"]

# Default spec path relative to project root
DEFAULT_SPEC_PATH = Path("spec/bootstrap.md")


# =============================================================================
# Types
# =============================================================================


@dataclass(frozen=True)
class BootstrapAgentSpec:
    """
    Parsed specification for a single bootstrap agent.

    Extracted from spec/bootstrap.md, this captures everything
    needed to regenerate the agent via LLM.
    """

    name: str
    signature: str
    description: str
    laws: tuple[str, ...]
    section_content: str
    section_number: int = 0

    @property
    def spec_hash(self) -> str:
        """Content-addressed identifier for the spec."""
        return hashlib.sha256(self.section_content.encode()).hexdigest()[:12]

    @property
    def has_laws(self) -> bool:
        """Does this spec define laws?"""
        return len(self.laws) > 0

    def __repr__(self) -> str:
        return f"BootstrapAgentSpec(name={self.name!r}, signature={self.signature!r}, laws={len(self.laws)})"


@dataclass
class ParseResult:
    """Result of parsing the bootstrap spec."""

    specs: tuple[BootstrapAgentSpec, ...]
    parse_errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def success(self) -> bool:
        """All 7 agents parsed successfully."""
        return len(self.specs) == 7 and len(self.parse_errors) == 0

    @property
    def agent_names(self) -> set[str]:
        """Names of successfully parsed agents."""
        return {s.name for s in self.specs}


# =============================================================================
# Parsing Logic
# =============================================================================


def parse_bootstrap_spec(
    spec_path: Path | None = None,
) -> tuple[BootstrapAgentSpec, ...]:
    """
    Parse spec/bootstrap.md into individual agent specs.

    Args:
        spec_path: Path to bootstrap.md. Defaults to spec/bootstrap.md.

    Returns:
        Tuple of 7 BootstrapAgentSpecs (Id, Compose, Judge, Ground, Contradict, Sublate, Fix)

    Raises:
        FileNotFoundError: If spec file doesn't exist
        ValueError: If parsing fails
    """
    if spec_path is None:
        # Find project root by looking for spec/ directory
        current = Path.cwd()
        while current != current.parent:
            if (current / "spec" / "bootstrap.md").exists():
                spec_path = current / "spec" / "bootstrap.md"
                break
            current = current.parent
        else:
            # Try relative to this file
            module_path = Path(__file__).parent.parent.parent.parent.parent
            spec_path = module_path / "spec" / "bootstrap.md"

    if not spec_path.exists():
        raise FileNotFoundError(f"Bootstrap spec not found: {spec_path}")

    content = spec_path.read_text()
    return _parse_content(content)


def parse_bootstrap_spec_detailed(
    spec_path: Path | None = None,
) -> ParseResult:
    """
    Parse with detailed error reporting.

    Returns ParseResult with any parse errors captured.
    """
    try:
        specs = parse_bootstrap_spec(spec_path)
        return ParseResult(specs=specs)
    except Exception as e:
        return ParseResult(specs=(), parse_errors=(str(e),))


def _parse_content(content: str) -> tuple[BootstrapAgentSpec, ...]:
    """Parse the markdown content into agent specs."""
    specs = []

    # Find each agent section
    for i, name in enumerate(AGENT_NAMES, start=1):
        spec = _extract_agent_spec(content, name, i)
        if spec is not None:
            specs.append(spec)

    if len(specs) != 7:
        missing = set(AGENT_NAMES) - {s.name for s in specs}
        raise ValueError(f"Failed to parse all agents. Missing: {missing}")

    return tuple(specs)


def _extract_agent_spec(content: str, name: str, section_number: int) -> BootstrapAgentSpec | None:
    """Extract a single agent's specification from the markdown."""
    # Find the section for this agent
    # Pattern: ### N. Name (OptionalParens)
    pattern = rf"###\s*{section_number}\.\s*{name}\s*\([^)]*\)"

    match = re.search(pattern, content, re.IGNORECASE)
    if not match:
        # Try simpler pattern without parenthetical
        pattern = rf"###\s*{section_number}\.\s*{name}"
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            return None

    # Find the end of this section (next ### or ## or end of file)
    start = match.start()
    next_section = re.search(r"\n##[#]?\s+", content[match.end() :])
    end = match.end() + next_section.start() if next_section else len(content)

    section_content = content[start:end].strip()

    # Extract signature from code block
    signature = _extract_signature(section_content, name)

    # Extract description (first paragraph after code block)
    description = _extract_description(section_content)

    # Extract laws
    laws = _extract_laws(section_content, name)

    return BootstrapAgentSpec(
        name=name,
        signature=signature,
        description=description,
        laws=tuple(laws),
        section_content=section_content,
        section_number=section_number,
    )


def _extract_signature(section: str, name: str) -> str:
    """
    Extract type signature from section.

    Looks for patterns like:
    - Id: A → A
    - Compose: (Agent, Agent) → Agent
    """
    # Look in code blocks first
    code_block = re.search(r"```\s*(.*?)```", section, re.DOTALL)
    if code_block:
        block_content = code_block.group(1)
        # Find signature line
        sig_match = re.search(rf"{name}\s*:\s*([^\n]+)", block_content)
        if sig_match:
            return sig_match.group(1).strip()

    # Look for standalone signature line
    sig_match = re.search(rf"{name}\s*:\s*([A-Za-z\[\](),→ ]+)", section)
    if sig_match:
        return sig_match.group(1).strip()

    return "unknown"


def _extract_description(section: str) -> str:
    """
    Extract the description paragraph.

    Takes the first substantial paragraph after the code block.
    """
    # Skip past code block
    code_end = section.find("```", section.find("```") + 3)
    if code_end == -1:
        code_end = 0

    rest = section[code_end + 3 :].strip()

    # Get first paragraph
    paragraphs = rest.split("\n\n")
    for para in paragraphs:
        cleaned = para.strip()
        # Skip headers and lists
        if cleaned and not cleaned.startswith(("#", "-", "*", "```", "|")):
            return cleaned

    return ""


def _extract_laws(section: str, name: str) -> list[str]:
    """
    Extract laws/invariants from section.

    Looks for:
    - Bullet points under "Laws" or "Laws/invariants"
    - Mathematical expressions in code blocks
    - Key invariant statements
    """
    laws = []

    # Look for explicit laws section
    laws_match = re.search(
        r"(?:Laws|Invariants?).*?:(.*?)(?=\n\n|\n##|$)", section, re.IGNORECASE | re.DOTALL
    )
    if laws_match:
        laws_content = laws_match.group(1)
        # Extract bullet points
        for line in laws_content.split("\n"):
            line = line.strip()
            if line.startswith(("-", "*")):
                law = line.lstrip("-* ").strip()
                if law:
                    laws.append(law)

    # Look for key patterns in code blocks
    code_match = re.search(r"```\s*(.*?)```", section, re.DOTALL)
    if code_match:
        code = code_match.group(1)
        for line in code.split("\n"):
            line = line.strip()
            # Skip signature lines
            if ":" in line and not line.startswith(name):
                continue
            # Mathematical laws often have = or ≡
            if "=" in line or "≡" in line:
                if line and line not in laws:
                    laws.append(line)

    # Agent-specific law extraction
    if name == "Id":
        # Always include identity laws
        if not any("Id(x) = x" in law for law in laws):
            laws.insert(0, "Id(x) = x")
    elif name == "Compose":
        # Associativity
        if not any("associativ" in law.lower() for law in laws):
            laws.append("Associativity: (f >> g) >> h ≡ f >> (g >> h)")

    return laws


# =============================================================================
# Utility Functions
# =============================================================================


def get_spec_for_agent(name: str, spec_path: Path | None = None) -> BootstrapAgentSpec | None:
    """Get spec for a single agent by name."""
    specs = parse_bootstrap_spec(spec_path)
    return next((s for s in specs if s.name == name), None)


def format_spec_summary(specs: tuple[BootstrapAgentSpec, ...]) -> str:
    """Format specs for display."""
    lines = ["Bootstrap Agent Specs:", "=" * 40]
    for spec in specs:
        lines.append(f"\n{spec.name}")
        lines.append(f"  Signature: {spec.signature}")
        lines.append(f"  Laws: {len(spec.laws)}")
        if spec.laws:
            for law in spec.laws[:3]:  # Show first 3
                lines.append(f"    - {law[:60]}...")
    return "\n".join(lines)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AGENT_NAMES",
    "BootstrapAgentSpec",
    "ParseResult",
    "parse_bootstrap_spec",
    "parse_bootstrap_spec_detailed",
    "get_spec_for_agent",
    "format_spec_summary",
]
