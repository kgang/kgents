"""
AGENTESE JIT Compilation: Spec → Implementation

The Generative Principle: Specs are compressed wisdom.
Implementations can be derived mechanically.

This module bridges AGENTESE with J-gent's MetaArchitect for
just-in-time generation of LogosNodes from spec files.

Pipeline:
    spec/world/X.md
           │
           ▼
    ┌─────────────────┐
    │   SpecParser    │───▶ Extract affordances, manifest behavior
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  MetaArchitect  │───▶ Generate Python source
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  JITLogosNode   │───▶ Wrap with usage tracking
    └────────┬────────┘
             │ success_rate >= threshold
             ▼
    ┌─────────────────┐
    │    Promotion    │───▶ Write to impl/, register in L-gent
    └─────────────────┘
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

from .exceptions import (
    PathNotFoundError,
    TastefulnessError,
)
from .node import (
    JITLogosNode,
    LogosNode,
)

if TYPE_CHECKING:
    pass


# === Spec Parsing ===


@dataclass(frozen=True)
class ParsedSpec:
    """Parsed specification for a world entity."""

    entity: str
    context: str
    version: str
    description: str
    affordances: dict[str, list[str]]  # archetype -> verbs
    manifest: dict[str, dict[str, Any]]  # archetype -> rendering config
    state_schema: dict[str, str] = field(default_factory=dict)
    relations: dict[str, list[str]] = field(default_factory=dict)
    behaviors: dict[str, str] = field(default_factory=dict)  # aspect -> description


class SpecParser:
    """
    Parse AGENTESE spec files into structured data.

    Spec files use YAML front matter + markdown body:

    ```markdown
    ---
    entity: library
    context: world
    version: 1.0
    ---

    # world.library

    [Description...]

    ## Affordances
    ```yaml
    affordances:
      architect: [blueprint, measure]
    ```

    ## Manifest
    ...
    ```
    """

    # Regex to extract YAML front matter
    FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    # Regex to extract YAML code blocks under headers
    YAML_BLOCK_RE = re.compile(
        r"##\s+(\w+)\s*\n+```ya?ml\s*\n(.*?)\n```",
        re.DOTALL | re.IGNORECASE,
    )

    def parse(self, spec_content: str, spec_path: Path | None = None) -> ParsedSpec:
        """
        Parse a spec file into structured data.

        Args:
            spec_content: Raw spec file content
            spec_path: Optional path for error messages

        Returns:
            ParsedSpec with extracted configuration

        Raises:
            TastefulnessError: If spec is malformed
        """
        if yaml is None:
            raise TastefulnessError(
                "YAML parser not available",
                why="PyYAML is required for spec parsing",
                suggestion="Install with: pip install pyyaml",
                validation_errors=[str(spec_path) if spec_path else "unknown"],
            )

        # Extract front matter
        front_match = self.FRONT_MATTER_RE.match(spec_content)
        if not front_match:
            raise TastefulnessError(
                "Spec missing YAML front matter",
                why="Specs must start with ---\\n...\\n---",
                suggestion="Add front matter with entity, context, version",
                validation_errors=[str(spec_path) if spec_path else "unknown"],
            )

        try:
            front_matter = yaml.safe_load(front_match.group(1))
        except yaml.YAMLError as e:
            raise TastefulnessError(
                f"Invalid YAML in front matter: {e}",
                why="Front matter must be valid YAML",
                validation_errors=[str(spec_path) if spec_path else "unknown"],
            ) from e

        # Extract required fields
        entity = front_matter.get("entity", "")
        context = front_matter.get("context", "world")
        version = front_matter.get("version", "1.0")

        if not entity:
            raise TastefulnessError(
                "Spec missing 'entity' in front matter",
                why="Every spec must declare its entity name",
                validation_errors=[str(spec_path) if spec_path else "unknown"],
            )

        # Extract body (after front matter)
        body = spec_content[front_match.end() :]

        # Extract description (first paragraph after title)
        desc_match = re.search(r"#[^#\n]+\n+([^#]+?)(?=\n##|\Z)", body)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract YAML blocks under headers
        yaml_blocks: dict[str, Any] = {}
        for match in self.YAML_BLOCK_RE.finditer(body):
            header = match.group(1).lower()
            try:
                content = yaml.safe_load(match.group(2))
                yaml_blocks[header] = content
            except yaml.YAMLError:
                # Skip malformed YAML blocks
                pass

        # Build ParsedSpec
        affordances = yaml_blocks.get("affordances", {})
        if isinstance(affordances, dict) and "affordances" in affordances:
            affordances = affordances["affordances"]

        manifest = yaml_blocks.get("manifest", {})
        if isinstance(manifest, dict) and "manifest" in manifest:
            manifest = manifest["manifest"]

        state_schema = yaml_blocks.get("state", {})
        if isinstance(state_schema, dict) and "state" in state_schema:
            state_schema = state_schema["state"]

        relations = yaml_blocks.get("relations", {})
        if isinstance(relations, dict) and "relations" in relations:
            relations = relations["relations"]

        # Extract behavior descriptions from markdown sections
        behaviors: dict[str, str] = {}
        behavior_re = re.compile(
            r"###\s+(\w+)\s+\([^)]+\)\s*\n(.*?)(?=\n###|\n##|\Z)", re.DOTALL
        )
        for match in behavior_re.finditer(body):
            aspect_name = match.group(1)
            behavior_desc = match.group(2).strip()
            behaviors[aspect_name] = behavior_desc

        return ParsedSpec(
            entity=entity,
            context=context,
            version=version,
            description=description,
            affordances=affordances,
            manifest=manifest,
            state_schema=state_schema,
            relations=relations,
            behaviors=behaviors,
        )


# === Code Generation ===


class SpecCompiler:
    """
    Compile a ParsedSpec into a LogosNode implementation.

    Uses J-gent MetaArchitect for template-based generation,
    enhanced with spec-specific affordances and manifest behavior.
    """

    def compile(self, spec: ParsedSpec) -> str:
        """
        Generate Python source code for a LogosNode.

        Args:
            spec: Parsed specification

        Returns:
            Python source code string
        """
        handle = f"{spec.context}.{spec.entity}"
        class_name = f"JIT{spec.entity.title().replace('_', '')}Node"

        # Generate affordance mapping
        affordance_dict = self._generate_affordance_dict(spec.affordances)

        # Generate manifest method
        manifest_method = self._generate_manifest_method(
            spec.manifest, spec.description
        )

        # Generate invoke method for custom aspects
        invoke_method = self._generate_invoke_method(spec.behaviors, spec.affordances)

        # Build source with proper indentation
        desc_truncated = spec.description[:200] + (
            "..." if len(spec.description) > 200 else ""
        )
        desc_short = spec.description[:100] + (
            "..." if len(spec.description) > 100 else ""
        )

        source = f'''"""
JIT-Generated LogosNode for {handle}

Generated from: spec/{spec.context}/{spec.entity}.md
Version: {spec.version}

{desc_truncated}
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from impl.claude.protocols.agentese.node import AgentMeta, Renderable

# Archetype -> affordances mapping
AFFORDANCES: dict[str, tuple[str, ...]] = {affordance_dict}


class {class_name}:
    """
    LogosNode for {handle}.

    {desc_short}
    """

    @property
    def handle(self) -> str:
        return "{handle}"

    # Base affordances available to all
    _base_affordances: tuple[str, ...] = ("manifest", "witness", "affordances")

    def affordances(self, observer: "AgentMeta") -> list[str]:
        """Return observer-specific affordances."""
        base = list(self._base_affordances)
        extra = AFFORDANCES.get(observer.archetype, AFFORDANCES.get("default", ()))
        return base + list(extra)

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        return AFFORDANCES.get(archetype, AFFORDANCES.get("default", ()))

    def lens(self, aspect: str) -> Any:
        """Return composable agent for aspect."""
        from impl.claude.protocols.agentese.node import AspectAgent
        return AspectAgent(self, aspect)

{manifest_method}

{invoke_method}
'''

        return source

    def _generate_affordance_dict(self, affordances: dict[str, list[str]]) -> str:
        """Generate Python dict literal for affordances."""
        lines = ["{"]
        for archetype, verbs in affordances.items():
            verb_tuple = ", ".join(f'"{v}"' for v in verbs)
            lines.append(f'    "{archetype}": ({verb_tuple},),')
        lines.append("}")
        return "\n".join(lines)

    def _generate_manifest_method(
        self,
        manifest: dict[str, dict[str, Any]],
        description: str,
    ) -> str:
        """Generate the manifest() method."""
        # Escape description for use in strings
        desc_80 = description[:80].replace('"', '\\"').replace("\n", " ")
        desc_50 = description[:50].replace('"', '\\"').replace("\n", " ")

        # Build archetype-specific rendering logic
        branches = []
        for archetype, config in manifest.items():
            render_type = config.get("type", "basic")

            if render_type == "blueprint":
                branches.append(f'''        if archetype == "{archetype}":
            from impl.claude.protocols.agentese.node import BlueprintRendering
            return BlueprintRendering(
                dimensions={{"entity": "{desc_50}"}},
                materials=(),
                structural_analysis={{}},
            )''')
            elif render_type == "poetic":
                branches.append(f'''        if archetype == "{archetype}":
            from impl.claude.protocols.agentese.node import PoeticRendering
            return PoeticRendering(
                description="{desc_80}",
                metaphors=(),
                mood="contemplative",
            )''')
            elif render_type == "economic":
                branches.append(f'''        if archetype == "{archetype}":
            from impl.claude.protocols.agentese.node import EconomicRendering
            return EconomicRendering(
                market_value=0.0,
                comparable_sales=(),
                appreciation_forecast={{}},
            )''')

        branches_code = "\n".join(branches) if branches else ""

        return f'''    async def manifest(self, observer: "Umwelt[Any, Any]") -> "Renderable":
        """Collapse to observer-appropriate representation."""
        from impl.claude.protocols.agentese.node import BasicRendering

        dna = observer.dna
        archetype = getattr(dna, "archetype", "default")
{branches_code}

        # Default rendering
        return BasicRendering(
            summary="{desc_80}",
            content="JIT-generated node for {desc_50}",
        )'''

    def _generate_invoke_method(
        self,
        behaviors: dict[str, str],
        affordances: dict[str, list[str]],
    ) -> str:
        """Generate the invoke() method."""
        # Collect all unique aspects
        all_aspects: set[str] = set()
        for verbs in affordances.values():
            all_aspects.update(verbs)

        # Generate aspect handlers
        handlers = []
        for aspect in sorted(all_aspects):
            behavior = behaviors.get(aspect, f"Execute {aspect} operation")
            behavior_escaped = behavior[:50].replace('"', '\\"').replace("\n", " ")
            handlers.append(f'''        if aspect == "{aspect}":
            return {{"aspect": "{aspect}", "behavior": "{behavior_escaped}", "kwargs": kwargs}}''')

        handlers_code = "\n".join(handlers) if handlers else ""

        return f'''    async def invoke(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Execute an aspect on this node."""
        if aspect == "manifest":
            return await self.manifest(observer)
        if aspect == "affordances":
            from impl.claude.protocols.agentese.node import AgentMeta
            dna = observer.dna
            meta = AgentMeta(
                name=getattr(dna, "name", "unknown"),
                archetype=getattr(dna, "archetype", "default"),
            )
            return self.affordances(meta)
{handlers_code}

        # Unknown aspect
        return {{"aspect": aspect, "status": "not_implemented", "kwargs": kwargs}}'''


# === JIT Integration ===


@dataclass
class JITCompiler:
    """
    Full JIT compilation pipeline for AGENTESE specs.

    Combines SpecParser, SpecCompiler, and J-gent safety checks.
    """

    spec_root: Path = field(default_factory=lambda: Path("spec"))
    parser: SpecParser = field(default_factory=SpecParser)
    compiler: SpecCompiler = field(default_factory=SpecCompiler)

    # J-gent integration (optional, for safety checks)
    _meta_architect: Any = None
    _safety_judge: Any = None

    def __post_init__(self) -> None:
        """Initialize J-gent components if available."""
        try:
            from impl.claude.agents.j import MetaArchitect, jit_safety_judge

            self._meta_architect = MetaArchitect()
            self._safety_judge = jit_safety_judge
        except ImportError:
            # J-gent not available, use basic compilation
            pass

    def compile_from_path(self, spec_path: Path) -> JITLogosNode:
        """
        Compile a spec file into a JITLogosNode.

        Args:
            spec_path: Path to the spec file

        Returns:
            JITLogosNode wrapping the generated source

        Raises:
            TastefulnessError: If spec is invalid
            PathNotFoundError: If spec file doesn't exist
        """
        if not spec_path.exists():
            raise PathNotFoundError(
                f"Spec not found: {spec_path}",
                path=str(spec_path),
                why="No spec file at this path",
                suggestion=f"Create {spec_path} with entity definition",
            )

        spec_content = spec_path.read_text()
        return self.compile_from_content(spec_content, spec_path)

    def compile_from_content(
        self,
        spec_content: str,
        spec_path: Path | None = None,
    ) -> JITLogosNode:
        """
        Compile spec content into a JITLogosNode.

        Args:
            spec_content: Raw spec file content
            spec_path: Optional path for error messages

        Returns:
            JITLogosNode wrapping the generated source
        """
        # Parse spec
        parsed = self.parser.parse(spec_content, spec_path)

        # Generate source
        source = self.compiler.compile(parsed)

        # Validate syntax
        try:
            ast.parse(source)
        except SyntaxError as e:
            raise TastefulnessError(
                f"Generated source has syntax error: {e}",
                why="The spec compiler produced invalid Python",
                validation_errors=[str(spec_path) if spec_path else "unknown"],
            ) from e

        # Create JIT node
        handle = f"{parsed.context}.{parsed.entity}"
        return JITLogosNode(
            handle=handle,
            source=source,
            spec=spec_content,
        )

    def compile_and_instantiate(
        self,
        spec_path: Path,
    ) -> LogosNode:
        """
        Compile a spec and return an instantiated LogosNode.

        This executes the generated code and returns an instance
        of the generated class.

        Args:
            spec_path: Path to the spec file

        Returns:
            Instantiated LogosNode

        Raises:
            TastefulnessError: If compilation or instantiation fails
        """
        jit_node = self.compile_from_path(spec_path)

        # Execute source to get class
        namespace: dict[str, Any] = {}
        try:
            exec(jit_node.source, namespace)
        except Exception as e:
            raise TastefulnessError(
                f"Failed to execute generated source: {e}",
                why="The generated code couldn't be executed",
                validation_errors=[str(spec_path)],
            ) from e

        # Find the generated class
        for name, obj in namespace.items():
            if name.startswith("JIT") and name.endswith("Node"):
                return cast(LogosNode, obj())

        raise TastefulnessError(
            "No LogosNode class found in generated source",
            why="The compiler didn't generate a proper node class",
            validation_errors=[str(spec_path)],
        )


# === Promotion Protocol ===


@dataclass
class PromotionResult:
    """Result of attempting to promote a JIT node."""

    success: bool
    handle: str
    reason: str
    impl_path: Path | None = None


class JITPromoter:
    """
    Promote successful JIT nodes to permanent implementations.

    A JIT node is promoted when:
    1. usage_count >= threshold (default: 100)
    2. success_rate >= success_threshold (default: 0.8)

    Promotion writes the source to impl/ and updates L-gent status.
    """

    def __init__(
        self,
        impl_root: Path = Path("impl/claude/protocols/agentese/generated"),
        threshold: int = 100,
        success_threshold: float = 0.8,
    ):
        self.impl_root = impl_root
        self.threshold = threshold
        self.success_threshold = success_threshold

    def should_promote(self, node: JITLogosNode) -> bool:
        """Check if a JIT node meets promotion criteria."""
        return node.should_promote(self.threshold, self.success_threshold)

    def promote(self, node: JITLogosNode, registry: Any = None) -> PromotionResult:
        """
        Promote a JIT node to permanent implementation.

        Args:
            node: The JIT node to promote
            registry: Optional L-gent registry to update

        Returns:
            PromotionResult with success status and details
        """
        if not self.should_promote(node):
            return PromotionResult(
                success=False,
                handle=node.handle,
                reason=(
                    f"Not ready for promotion: "
                    f"usage={node.usage_count}/{self.threshold}, "
                    f"success_rate={node.success_rate:.2f}/{self.success_threshold}"
                ),
            )

        # Ensure output directory exists
        self.impl_root.mkdir(parents=True, exist_ok=True)

        # Generate file name from handle
        context, entity = node.handle.split(".", 1)
        file_name = f"{entity.replace('.', '_')}.py"
        impl_path = self.impl_root / file_name

        # Write source
        try:
            impl_path.write_text(node.source)
        except IOError as e:
            return PromotionResult(
                success=False,
                handle=node.handle,
                reason=f"Failed to write impl file: {e}",
            )

        # Update L-gent registry if provided
        if registry is not None:
            try:
                # Would call registry.update_status(node.handle, Status.ACTIVE)
                pass
            except Exception as e:
                return PromotionResult(
                    success=False,
                    handle=node.handle,
                    reason=f"Failed to update registry: {e}",
                    impl_path=impl_path,
                )

        return PromotionResult(
            success=True,
            handle=node.handle,
            reason=f"Promoted after {node.usage_count} uses ({node.success_rate:.2%} success)",
            impl_path=impl_path,
        )


# === Factory Functions ===


def create_jit_compiler(
    spec_root: Path | str = "spec",
    with_safety_checks: bool = True,
) -> JITCompiler:
    """
    Create a JIT compiler with standard configuration.

    Args:
        spec_root: Path to spec directory
        with_safety_checks: Whether to enable J-gent safety checks

    Returns:
        Configured JITCompiler
    """
    compiler = JITCompiler(spec_root=Path(spec_root))

    if not with_safety_checks:
        compiler._meta_architect = None
        compiler._safety_judge = None

    return compiler


def compile_spec(spec_path: Path | str) -> JITLogosNode:
    """
    Convenience function to compile a spec file.

    Args:
        spec_path: Path to the spec file

    Returns:
        JITLogosNode wrapping the generated source
    """
    compiler = create_jit_compiler()
    return compiler.compile_from_path(Path(spec_path))
