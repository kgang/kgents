"""
Systems Section Compiler.

Compiles the built infrastructure section from docs/systems-reference.md.

Wave 2: Now reads dynamically from docs/systems-reference.md with fallback.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING

from ..section_base import NPhase, Section, estimate_tokens, read_file_safe

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


class SystemsSectionCompiler:
    """
    Compile the systems/infrastructure section of CLAUDE.md.

    Wave 2: Reads dynamically from docs/systems-reference.md.
    Falls back to hardcoded content if source file is missing.
    """

    @property
    def name(self) -> str:
        return "systems"

    @property
    def required(self) -> bool:
        return True

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    def compile(self, context: CompilationContext) -> Section:
        """
        Compile systems section.

        Attempts to read from docs/systems-reference.md, falls back to hardcoded.
        """
        source_path = context.docs_path / "systems-reference.md" if context.docs_path else None

        if source_path:
            content = self._compile_dynamic(source_path)
            if content:
                return Section(
                    name=self.name,
                    content=content,
                    token_cost=estimate_tokens(content),
                    required=self.required,
                    phases=self.phases,
                    source_paths=(source_path,),
                )

        # Fallback to hardcoded
        logger.info("Using fallback content for systems section")
        content = self._compile_fallback()
        return Section(
            name=self.name,
            content=content,
            token_cost=estimate_tokens(content),
            required=self.required,
            phases=self.phases,
            source_paths=(),
        )

    def estimate_tokens(self) -> int:
        """Estimate ~300 tokens for systems section."""
        return 300

    def _compile_dynamic(self, source_path) -> str | None:
        """
        Read and extract systems summary from source file.

        Extracts the first section which contains the systems table.
        """
        file_content = read_file_safe(source_path)
        if not file_content:
            return None

        # Extract the categorical foundation section (first major table)
        # Look for the table in the first section
        systems_summary = self._extract_systems_table(file_content)
        if not systems_summary:
            logger.warning(f"Could not extract systems table from {source_path}")
            return None

        return f"""## Built Infrastructure (CHECK FIRST!)

**16 production systems** are fully implemented. Before building anything new, check `docs/systems-reference.md`.

{systems_summary}"""

    def _extract_systems_table(self, content: str) -> str | None:
        """
        Extract the systems summary table from systems-reference.md.

        Strategy: Build a category → components mapping, then format as table.
        Uses the section headers and bold component names from tables.
        """
        lines = content.split("\n")

        # Map category name → list of component names
        categories: dict[str, list[str]] = {}
        current_section: str | None = None

        for line in lines:
            # Match section headers like "## Categorical Foundation (USE FOR ANY DOMAIN)"
            section_match = re.match(r"^##\s+(.+?)(?:\s+\(.+\))?\s*$", line)
            if section_match:
                current_section = section_match.group(1).strip()
                if current_section not in categories:
                    categories[current_section] = []
                continue

            # Look for component rows in tables (bold component names)
            if current_section and "|" in line and "Component" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and parts[0].startswith("**"):
                    # Extract component name (remove ** and backticks)
                    component = parts[0].replace("**", "").replace("`", "").strip()
                    if component and component not in categories[current_section]:
                        categories[current_section].append(component)

        # Filter to only categories with components
        categories = {k: v for k, v in categories.items() if v}

        # If we couldn't parse at least 2 categories, return None to trigger fallback
        # 2 is the minimum to know parsing is working
        if len(categories) < 2:
            logger.warning(f"Only found {len(categories)} categories, using fallback")
            return None

        # Build summary table with all categories
        table_lines = ["| Category | Systems |", "|----------|---------|"]
        for category, components in categories.items():
            systems = ", ".join(components)
            table_lines.append(f"| **{category}** | {systems} |")

        return "\n".join(table_lines)

    def _compile_fallback(self) -> str:
        """Hardcoded fallback content when source file is unavailable."""
        return """## Built Infrastructure (CHECK FIRST!)

**16 production systems** are fully implemented. Before building anything new, check `docs/systems-reference.md`.

| Category | Systems |
|----------|---------|
| **Categorical** | PolyAgent, Operad, Sheaf (use for ANY domain) |
| **Streaming** | Flux (discrete → continuous agents) |
| **Semantics** | AGENTESE (8 phases shipped: parser, JIT, laws, wiring) |
| **Simulation** | Agent Town (citizens, coalitions, dialogue) |
| **Soul** | K-gent (LLM dialogue, hypnagogia, gatekeeper) |
| **Memory** | M-gent (crystals, cartography, stigmergy) |
| **UI** | Reactive (Signal/Computed/Effect → CLI/marimo/JSON) |
| **Lifecycle** | N-Phase compiler (YAML → prompts) |
| **Gateway** | Terrarium (REST bridge, metrics) |
| **SaaS** | API, Billing (Stripe), Licensing (tiers), Tenancy (multi-tenant) |"""


__all__ = ["SystemsSectionCompiler"]
