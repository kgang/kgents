"""
Reference Documentation Generator

Generates comprehensive, public-ready reference documentation
from the codebase using Living Docs infrastructure.

AGENTESE: concept.docs.generate

Usage:
    generator = ReferenceGenerator()

    # Single string output
    docs = generator.generate_all()
    print(docs)

    # Directory output (Phase 3)
    manifest = generator.generate_to_directory(Path("docs/reference"))
    print(f"Generated {manifest.file_count} files")

Teaching:
    gotcha: generate_to_directory() creates directories if they don't exist.
            It will NOT overwrite existing files unless overwrite=True.
            (Evidence: test_generator.py::test_no_overwrite_by_default)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .extractor import DocstringExtractor
from .projector import LivingDocsProjector
from .spec_extractor import SpecExtractor
from .types import DocNode, LivingDocsObserver, Surface, TeachingMoment, Tier


@dataclass
class CategoryConfig:
    """Configuration for a documentation category."""

    name: str
    paths: list[str]
    description: str = ""
    is_spec: bool = False  # True if this category contains spec markdown files


# Documentation categories for kgents
# Note: town, gestalt, park, gardener removed 2025-12-21 (Crown Jewel Cleanup)
CATEGORIES: list[CategoryConfig] = [
    CategoryConfig(
        name="Crown Jewels",
        paths=[
            "services/brain/",
            "services/witness/",
            "services/conductor/",
            "services/living_docs/",
            "services/interactive_text/",
            "services/liminal/",
            "services/verification/",
            "services/morpheus/",
            "services/ashc/",
        ],
        description="The showcase features of kgents.",
    ),
    CategoryConfig(
        name="Categorical Foundation",
        paths=[
            "agents/poly/",
            "agents/operad/",
            "agents/sheaf/",
            "agents/flux/",
            "agents/d/",
            "agents/k/",
            "agents/m/",
        ],
        description="The mathematical substrate: polynomial functors, operads, sheaves.",
    ),
    CategoryConfig(
        name="AGENTESE Protocol",
        paths=[
            "protocols/agentese/",
        ],
        description="The universal API: verb-first ontology for agent-world interaction.",
    ),
    CategoryConfig(
        name="ASHC Compiler",
        paths=[
            "protocols/ashc/",
        ],
        description="Agentic Self-Hosting Compiler: empirical verification via trace accumulation.",
    ),
]

# Spec categories (markdown files)
SPEC_CATEGORIES: list[CategoryConfig] = [
    CategoryConfig(
        name="Core Specifications",
        paths=[
            "spec/principles.md",
            "spec/anatomy.md",
            "spec/bootstrap.md",
            "spec/archetypes.md",
        ],
        description="The foundational specifications: principles, anatomy, bootstrap process.",
        is_spec=True,
    ),
    CategoryConfig(
        name="Agent Specifications",
        paths=[
            "spec/agents/",
        ],
        description="Agent genus specifications: functors, monads, composition patterns.",
        is_spec=True,
    ),
    CategoryConfig(
        name="Protocol Specifications",
        paths=[
            "spec/protocols/",
        ],
        description="Protocol specifications: AGENTESE, projection, data-bus.",
        is_spec=True,
    ),
]


@dataclass
class GeneratedDocs:
    """Generated documentation output."""

    title: str
    content: str
    symbol_count: int
    teaching_count: int
    categories: dict[str, list[DocNode]] = field(default_factory=dict)


@dataclass
class GeneratedFile:
    """Metadata for a generated documentation file."""

    path: Path
    title: str
    symbol_count: int
    teaching_count: int
    category: str


@dataclass
class GenerationManifest:
    """
    Manifest of all generated documentation files.

    Tracks what was generated, when, and provides summary stats.
    """

    files: list[GeneratedFile] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_symbols: int = 0
    total_teaching: int = 0

    @property
    def file_count(self) -> int:
        """Number of files generated."""
        return len(self.files)

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary for serialization."""
        return {
            "files": [
                {
                    "path": str(f.path),
                    "title": f.title,
                    "symbol_count": f.symbol_count,
                    "teaching_count": f.teaching_count,
                    "category": f.category,
                }
                for f in self.files
            ],
            "generated_at": self.generated_at.isoformat(),
            "total_symbols": self.total_symbols,
            "total_teaching": self.total_teaching,
            "file_count": self.file_count,
        }


class ReferenceGenerator:
    """
    Generate comprehensive reference documentation.

    Uses spacious density for maximum detail.
    """

    def __init__(
        self,
        base_path: Path | None = None,
        extractor: DocstringExtractor | None = None,
        projector: LivingDocsProjector | None = None,
        spec_extractor: SpecExtractor | None = None,
        include_specs: bool = True,
    ):
        self._base_path = base_path or Path(__file__).parent.parent.parent
        self._spec_base_path = self._base_path.parent.parent  # Go up to kgents root
        self._extractor = extractor or DocstringExtractor()
        self._spec_extractor = spec_extractor or SpecExtractor()
        self._projector = projector or LivingDocsProjector()
        self._observer = LivingDocsObserver(kind="human", density="spacious")
        self._include_specs = include_specs

    def generate_all(self) -> str:
        """Generate complete reference documentation as markdown."""
        lines: list[str] = []

        # Header
        lines.append("# kgents Reference Documentation")
        lines.append("")
        lines.append(
            '> *Generated by Living Docs — "Docs are not description—they are projection."*'
        )
        lines.append("")
        lines.append("---")
        lines.append("")

        # Stats
        total_symbols = 0
        total_teaching = 0
        all_nodes: list[DocNode] = []

        # Generate each implementation category
        for category in CATEGORIES:
            category_nodes = self._extract_category(category)
            all_nodes.extend(category_nodes)

            if category_nodes:
                lines.append(f"## {category.name}")
                lines.append("")
                if category.description:
                    lines.append(f"*{category.description}*")
                    lines.append("")

                # Group by file
                by_file: dict[str, list[DocNode]] = {}
                for node in category_nodes:
                    key = node.module or "unknown"
                    if key not in by_file:
                        by_file[key] = []
                    by_file[key].append(node)

                for module, nodes in sorted(by_file.items()):
                    # Only show modules with substantial content
                    rich_nodes = [n for n in nodes if n.tier == Tier.RICH and n.summary]
                    if not rich_nodes:
                        continue

                    lines.append(f"### {module}")
                    lines.append("")

                    for node in rich_nodes[:10]:  # Top 10 per module
                        total_symbols += 1
                        total_teaching += len(node.teaching)

                        # Project the node
                        surface = self._projector.project(node, self._observer)
                        lines.append(surface.content)
                        lines.append("")
                        lines.append("---")
                        lines.append("")

                    if len(rich_nodes) > 10:
                        lines.append(f"*...and {len(rich_nodes) - 10} more symbols*")
                        lines.append("")

        # Generate spec categories if enabled
        if self._include_specs:
            for category in SPEC_CATEGORIES:
                category_nodes = self._extract_spec_category(category)
                all_nodes.extend(category_nodes)

                if category_nodes:
                    lines.append(f"## {category.name}")
                    lines.append("")
                    if category.description:
                        lines.append(f"*{category.description}*")
                        lines.append("")

                    # Group by file
                    by_file = {}
                    for node in category_nodes:
                        key = node.module or "unknown"
                        if key not in by_file:
                            by_file[key] = []
                        by_file[key].append(node)

                    for module, nodes in sorted(by_file.items()):
                        # Only show modules with substantial content
                        rich_nodes = [n for n in nodes if n.tier == Tier.RICH and n.summary]
                        if not rich_nodes:
                            continue

                        lines.append(f"### {module}")
                        lines.append("")

                        for node in rich_nodes[:10]:  # Top 10 per module
                            total_symbols += 1
                            total_teaching += len(node.teaching)

                            # Project the node
                            surface = self._projector.project(node, self._observer)
                            lines.append(surface.content)
                            lines.append("")
                            lines.append("---")
                            lines.append("")

                        if len(rich_nodes) > 10:
                            lines.append(f"*...and {len(rich_nodes) - 10} more symbols*")
                            lines.append("")

        # Teaching moments summary
        all_teaching: list[tuple[str, TeachingMoment]] = [
            (n.symbol, m) for n in all_nodes for m in n.teaching
        ]

        if all_teaching:
            lines.append("## Teaching Moments (Gotchas)")
            lines.append("")
            lines.append('> *"Gotchas live in docstrings, not wikis."*')
            lines.append("")

            # Group by severity
            by_severity: dict[str, list[tuple[str, TeachingMoment]]] = {
                "critical": [],
                "warning": [],
                "info": [],
            }
            for symbol, moment in all_teaching:
                by_severity[moment.severity].append((symbol, moment))

            for severity, items in by_severity.items():
                if items:
                    icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}[severity]
                    lines.append(f"### {icon} {severity.title()}")
                    lines.append("")
                    for symbol, moment in items:
                        lines.append(f"- **{symbol}**: {moment.insight}")
                        if moment.evidence:
                            lines.append(f"  - Evidence: `{moment.evidence}`")
                    lines.append("")

        # Summary stats
        lines.append("---")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Symbols**: {total_symbols}")
        lines.append(f"- **Teaching Moments**: {total_teaching}")
        lines.append(f"- **Categories**: {len(CATEGORIES)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by `LivingDocs : (Source × Spec) → Observer → Surface`*")

        return "\n".join(lines)

    def _extract_category(self, category: CategoryConfig) -> list[DocNode]:
        """Extract all nodes from a category."""
        nodes: list[DocNode] = []

        for path_str in category.paths:
            path = self._base_path / path_str
            if not path.exists():
                continue

            for py_file in self._iter_python_files(path):
                try:
                    # Extract module docstring
                    mod_node = self._extractor.extract_module_docstring(py_file)
                    if mod_node:
                        nodes.append(mod_node)

                    # Extract symbols
                    file_nodes = self._extractor.extract_file(py_file)
                    nodes.extend(file_nodes)
                except Exception:
                    continue

        return nodes

    def _iter_python_files(self, path: Path) -> Iterator[Path]:
        """Iterate over Python files, respecting exclusions."""
        for py_file in path.glob("**/*.py"):
            if self._extractor.should_extract(py_file):
                yield py_file

    def _extract_spec_category(self, category: CategoryConfig) -> list[DocNode]:
        """Extract all nodes from a spec category (markdown files)."""
        nodes: list[DocNode] = []

        for path_str in category.paths:
            path = self._spec_base_path / path_str
            if not path.exists():
                continue

            if path.is_file() and path.suffix == ".md":
                # Single file
                try:
                    summary = self._spec_extractor.extract_spec_summary(path)
                    if summary:
                        nodes.append(summary)
                    section_nodes = self._spec_extractor.extract_file(path)
                    nodes.extend(section_nodes)
                except Exception:
                    pass
            else:
                # Directory
                for md_file in self._iter_spec_files(path):
                    try:
                        summary = self._spec_extractor.extract_spec_summary(md_file)
                        if summary:
                            nodes.append(summary)
                        section_nodes = self._spec_extractor.extract_file(md_file)
                        nodes.extend(section_nodes)
                    except Exception:
                        continue

        return nodes

    def _iter_spec_files(self, path: Path) -> Iterator[Path]:
        """Iterate over markdown files, respecting exclusions."""
        for md_file in path.glob("**/*.md"):
            if self._spec_extractor.should_extract(md_file):
                yield md_file

    def generate_gotchas(self) -> str:
        """Generate a dedicated gotchas/teaching moments page."""
        lines: list[str] = []

        lines.append("# Teaching Moments (Gotchas)")
        lines.append("")
        lines.append('> *"Gotchas live in docstrings, not wikis."*')
        lines.append("")

        all_teaching: list[tuple[str, str, TeachingMoment]] = []  # (module, symbol, moment)

        # Extract from implementation categories
        for category in CATEGORIES:
            nodes = self._extract_category(category)
            for node in nodes:
                for moment in node.teaching:
                    all_teaching.append((node.module, node.symbol, moment))

        # Extract from spec categories if enabled
        if self._include_specs:
            for category in SPEC_CATEGORIES:
                nodes = self._extract_spec_category(category)
                for node in nodes:
                    for moment in node.teaching:
                        all_teaching.append((node.module, node.symbol, moment))

        if not all_teaching:
            lines.append(
                "*No teaching moments found. Add `Teaching:` sections with `gotcha:` keywords to your docstrings.*"
            )
            return "\n".join(lines)

        # Group by severity
        by_severity: dict[str, list[tuple[str, str, TeachingMoment]]] = {
            "critical": [],
            "warning": [],
            "info": [],
        }
        for module, symbol, moment in all_teaching:
            by_severity[moment.severity].append((module, symbol, moment))

        for severity in ["critical", "warning", "info"]:
            items = by_severity[severity]
            if items:
                icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}[severity]
                lines.append(f"## {icon} {severity.title()} ({len(items)})")
                lines.append("")

                for module, symbol, moment in items:
                    lines.append(f"### {symbol}")
                    lines.append(f"*Module: {module}*")
                    lines.append("")
                    lines.append(moment.insight)
                    if moment.evidence:
                        lines.append("")
                        lines.append(f"**Evidence**: `{moment.evidence}`")
                    if moment.commit:
                        lines.append(f"**Commit**: `{moment.commit[:7]}`")
                    lines.append("")
                    lines.append("---")
                    lines.append("")

        lines.append(f"*Total: {len(all_teaching)} teaching moments*")

        return "\n".join(lines)

    # =========================================================================
    # Phase 3: Directory-based generation
    # =========================================================================

    def generate_to_directory(
        self,
        output_dir: Path,
        overwrite: bool = False,
    ) -> GenerationManifest:
        """
        Generate complete reference documentation to a directory structure.

        Creates:
            output_dir/
            ├── index.md                    # Overview + navigation
            ├── crown-jewels/
            │   ├── brain.md
            │   ├── witness.md
            │   └── ...
            ├── categorical/
            │   ├── polyagent.md
            │   └── ...
            ├── agentese/
            │   └── protocol.md
            ├── specs/
            │   └── ...
            └── teaching/
                └── gotchas.md

        Args:
            output_dir: Directory to write documentation to
            overwrite: If True, overwrite existing files

        Returns:
            GenerationManifest with all generated file metadata
        """
        manifest = GenerationManifest()

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate implementation category pages
        for category in CATEGORIES:
            nodes = self._extract_category(category)
            if not nodes:
                continue

            # Determine subdirectory
            subdir = self._category_to_dirname(category.name)
            category_dir = output_dir / subdir
            category_dir.mkdir(parents=True, exist_ok=True)

            # Generate category page
            file_info = self._generate_category_page(
                category=category,
                nodes=nodes,
                output_dir=category_dir,
                overwrite=overwrite,
            )
            if file_info:
                manifest.files.append(file_info)
                manifest.total_symbols += file_info.symbol_count
                manifest.total_teaching += file_info.teaching_count

        # Generate spec category pages if enabled
        if self._include_specs:
            specs_dir = output_dir / "specs"
            specs_dir.mkdir(parents=True, exist_ok=True)

            for category in SPEC_CATEGORIES:
                nodes = self._extract_spec_category(category)
                if not nodes:
                    continue

                file_info = self._generate_category_page(
                    category=category,
                    nodes=nodes,
                    output_dir=specs_dir,
                    overwrite=overwrite,
                )
                if file_info:
                    manifest.files.append(file_info)
                    manifest.total_symbols += file_info.symbol_count
                    manifest.total_teaching += file_info.teaching_count

        # Generate teaching moments page
        teaching_dir = output_dir / "teaching"
        teaching_dir.mkdir(parents=True, exist_ok=True)
        gotchas_path = teaching_dir / "gotchas.md"

        if overwrite or not gotchas_path.exists():
            gotchas_content = self.generate_gotchas()
            gotchas_path.write_text(gotchas_content)

            # Count teaching moments from content
            teaching_count = gotchas_content.count("### ")
            manifest.files.append(
                GeneratedFile(
                    path=gotchas_path,
                    title="Teaching Moments (Gotchas)",
                    symbol_count=0,
                    teaching_count=teaching_count,
                    category="teaching",
                )
            )

        # Generate index page
        index_path = output_dir / "index.md"
        if overwrite or not index_path.exists():
            index_content = self._generate_index(manifest, output_dir)
            index_path.write_text(index_content)
            manifest.files.insert(
                0,
                GeneratedFile(
                    path=index_path,
                    title="kgents Reference Documentation",
                    symbol_count=manifest.total_symbols,
                    teaching_count=manifest.total_teaching,
                    category="index",
                ),
            )

        return manifest

    def _category_to_dirname(self, name: str) -> str:
        """Convert category name to directory name."""
        return name.lower().replace(" ", "-")

    def _category_to_filename(self, name: str) -> str:
        """Convert category name to filename."""
        return name.lower().replace(" ", "-") + ".md"

    def _generate_category_page(
        self,
        category: CategoryConfig,
        nodes: list[DocNode],
        output_dir: Path,
        overwrite: bool = False,
    ) -> GeneratedFile | None:
        """
        Generate a single category page.

        Returns metadata about the generated file, or None if skipped.
        """
        filename = self._category_to_filename(category.name)
        filepath = output_dir / filename

        if not overwrite and filepath.exists():
            return None

        lines: list[str] = []
        symbol_count = 0
        teaching_count = 0

        # Header
        lines.append(f"# {category.name}")
        lines.append("")
        if category.description:
            lines.append(f"> *{category.description}*")
            lines.append("")
        lines.append("---")
        lines.append("")

        # Group by module
        by_module: dict[str, list[DocNode]] = {}
        for node in nodes:
            key = node.module or "unknown"
            if key not in by_module:
                by_module[key] = []
            by_module[key].append(node)

        # Generate content for each module
        for module, module_nodes in sorted(by_module.items()):
            # Only show modules with substantial content
            rich_nodes = [n for n in module_nodes if n.tier == Tier.RICH and n.summary]
            if not rich_nodes:
                continue

            lines.append(f"## {module}")
            lines.append("")

            for node in rich_nodes:
                symbol_count += 1
                teaching_count += len(node.teaching)

                # Project the node
                surface = self._projector.project(node, self._observer)
                lines.append(surface.content)
                lines.append("")
                lines.append("---")
                lines.append("")

        # Footer
        lines.append(f"*{symbol_count} symbols, {teaching_count} teaching moments*")
        lines.append("")
        lines.append(
            f"*Generated by Living Docs — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}*"
        )

        # Write file
        filepath.write_text("\n".join(lines))

        return GeneratedFile(
            path=filepath,
            title=category.name,
            symbol_count=symbol_count,
            teaching_count=teaching_count,
            category=self._category_to_dirname(category.name),
        )

    def _generate_index(self, manifest: GenerationManifest, output_dir: Path) -> str:
        """Generate the index.md navigation page."""
        lines: list[str] = []

        # Header
        lines.append("# kgents Reference Documentation")
        lines.append("")
        lines.append('> *"Docs are not description—they are projection."*')
        lines.append("")
        lines.append("Generated by Living Docs — observer-dependent documentation from source.")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Summary stats
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Symbols**: {manifest.total_symbols}")
        lines.append(f"- **Teaching Moments**: {manifest.total_teaching}")
        lines.append(f"- **Generated Files**: {manifest.file_count}")
        lines.append(f"- **Generated At**: {manifest.generated_at.strftime('%Y-%m-%d %H:%M UTC')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Navigation by category
        lines.append("## Navigation")
        lines.append("")

        # Group files by category
        categories: dict[str, list[GeneratedFile]] = {}
        for f in manifest.files:
            if f.category == "index":
                continue
            if f.category not in categories:
                categories[f.category] = []
            categories[f.category].append(f)

        for cat_name, files in sorted(categories.items()):
            lines.append(f"### {cat_name.replace('-', ' ').title()}")
            lines.append("")
            for f in files:
                rel_path = f.path.relative_to(output_dir)
                lines.append(f"- [{f.title}]({rel_path}) ({f.symbol_count} symbols)")
            lines.append("")

        # Quick links
        lines.append("---")
        lines.append("")
        lines.append("## Quick Links")
        lines.append("")
        lines.append(
            "- [Teaching Moments (Gotchas)](teaching/gotchas.md) — All gotchas by severity"
        )
        lines.append("- [Crown Jewels](crown-jewels/crown-jewels.md) — The showcase features")
        lines.append(
            "- [AGENTESE Protocol](agentese-protocol/agentese-protocol.md) — The universal API"
        )
        lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by `LivingDocs : (Source × Spec) → Observer → Surface`*")

        return "\n".join(lines)


def generate_reference() -> str:
    """Convenience function to generate full reference docs."""
    generator = ReferenceGenerator()
    return generator.generate_all()


def generate_gotchas() -> str:
    """Convenience function to generate gotchas page."""
    generator = ReferenceGenerator()
    return generator.generate_gotchas()


def generate_to_directory(output_dir: Path, overwrite: bool = False) -> GenerationManifest:
    """
    Convenience function to generate docs to a directory.

    Usage:
        from services.living_docs import generate_to_directory
        manifest = generate_to_directory(Path("docs/reference"))
        print(f"Generated {manifest.file_count} files")
    """
    generator = ReferenceGenerator()
    return generator.generate_to_directory(output_dir, overwrite=overwrite)
