"""
F-gent Phase 5: Crystallize

Morphism: (Intent, Contract, SourceCode) → Artifact

This phase:
1. Assembles validated artifacts into .alo.md format
2. Computes integrity hash for drift detection
3. Assigns semantic version numbers
4. Registers with L-gent (if available)
5. Notifies ecosystem of new artifact

From spec/f-gents/forge.md Phase 5 and spec/f-gents/artifacts.md
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

from agents.f.contract import Contract
from agents.f.intent import Intent
from agents.f.prototype import SourceCode

# L-gent integration (optional import - may not be available)
try:
    from agents.l.catalog import CatalogEntry, EntityType, Registry, Status

    LGENT_AVAILABLE = True
except ImportError:
    LGENT_AVAILABLE = False


class ArtifactStatus(Enum):
    """
    Lifecycle status of an artifact.

    From spec/f-gents/artifacts.md:
    experimental → active → deprecated → retired
    """

    EXPERIMENTAL = "experimental"  # Newly forged, undergoing validation
    ACTIVE = "active"  # Production-ready, stable contract
    DEPRECATED = "deprecated"  # Superseded by newer version
    RETIRED = "retired"  # No longer maintained


class VersionBump(Enum):
    """
    Type of version increment for semantic versioning.

    PATCH: 1.0.0 → 1.0.1 (implementation fix, contract unchanged)
    MINOR: 1.0.0 → 1.1.0 (new capability, backward compatible)
    MAJOR: 1.0.0 → 2.0.0 (breaking change)
    """

    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


@dataclass
class Version:
    """
    Semantic version: MAJOR.MINOR.PATCH

    Attributes:
        major: Breaking changes
        minor: Backward-compatible additions
        patch: Backward-compatible fixes
    """

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        """Format as 'MAJOR.MINOR.PATCH'."""
        return f"{self.major}.{self.minor}.{self.patch}"

    @staticmethod
    def parse(version_string: str) -> "Version":
        """
        Parse version string like '1.0.0' into Version.

        Args:
            version_string: String in format 'MAJOR.MINOR.PATCH'

        Returns:
            Version object

        Raises:
            ValueError: If string is not valid semantic version
        """
        pattern = r"^(\d+)\.(\d+)\.(\d+)$"
        match = re.match(pattern, version_string)
        if not match:
            raise ValueError(
                f"Invalid version string: '{version_string}'. "
                f"Expected format: 'MAJOR.MINOR.PATCH'"
            )
        major, minor, patch = match.groups()
        return Version(int(major), int(minor), int(patch))

    def bump(self, bump_type: VersionBump) -> "Version":
        """
        Create new version with incremented number.

        Args:
            bump_type: PATCH | MINOR | MAJOR

        Returns:
            New Version object with incremented number
        """
        if bump_type == VersionBump.PATCH:
            return Version(self.major, self.minor, self.patch + 1)
        elif bump_type == VersionBump.MINOR:
            return Version(self.major, self.minor + 1, 0)
        elif bump_type == VersionBump.MAJOR:
            return Version(self.major + 1, 0, 0)
        else:
            raise ValueError(f"Unknown bump type: {bump_type}")


@dataclass
class ArtifactMetadata:
    """
    YAML frontmatter metadata for .alo.md artifacts.

    From spec/f-gents/artifacts.md metadata schema.

    Attributes:
        id: Unique identifier (agent_name_version)
        artifact_type: Always 'f_gent_artifact'
        version: Semantic version
        created_at: ISO 8601 timestamp
        created_by: F-gent instance identifier
        parent_version: Previous version (for re-forged artifacts)
        status: Lifecycle status
        hash: SHA-256 of artifact (excluding hash field)
        tags: Searchable keywords for L-gent
        dependencies: External libraries/APIs required
    """

    id: str
    artifact_type: str = "f_gent_artifact"
    version: Version = field(default_factory=lambda: Version(1, 0, 0))
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    created_by: str = "f-gent"
    parent_version: Optional[str] = None
    status: ArtifactStatus = ArtifactStatus.EXPERIMENTAL
    hash: str = ""  # Computed after assembly
    tags: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    def to_yaml(self) -> str:
        """
        Render metadata as YAML frontmatter.

        Returns:
            YAML string with --- delimiters
        """
        lines = ["---"]
        lines.append(f'id: "{self.id}"')
        lines.append(f'type: "{self.artifact_type}"')
        lines.append(f'version: "{self.version}"')
        lines.append(f'created_at: "{self.created_at}"')
        lines.append(f'created_by: "{self.created_by}"')

        if self.parent_version:
            lines.append(f'parent_version: "{self.parent_version}"')
        else:
            lines.append("parent_version: null")

        lines.append(f'status: "{self.status.value}"')
        lines.append(f'hash: "{self.hash}"')

        # Tags
        if self.tags:
            lines.append("tags:")
            for tag in self.tags:
                lines.append(f'  - "{tag}"')
        else:
            lines.append("tags: []")

        # Dependencies
        if self.dependencies:
            lines.append("dependencies:")
            for dep in self.dependencies:
                lines.append(f'  - "{dep}"')
        else:
            lines.append("dependencies: []")

        lines.append("---")
        return "\n".join(lines)


@dataclass
class Artifact:
    """
    Complete F-gent artifact: intent + contract + implementation.

    The .alo.md file structure from spec/f-gents/artifacts.md.

    Attributes:
        metadata: YAML frontmatter
        intent: Section 1 - Natural language intent (human-editable)
        contract: Section 2 - Interface specification (machine-verified)
        source_code: Section 4 - Implementation (auto-generated)
        changelog_entries: Version history
    """

    metadata: ArtifactMetadata
    intent: Intent
    contract: Contract
    source_code: SourceCode
    changelog_entries: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """
        Render artifact as .alo.md markdown file.

        Returns:
            Complete markdown document with all sections
        """
        sections = []

        # YAML frontmatter
        sections.append(self.metadata.to_yaml())
        sections.append("")

        # Section 1: THE INTENT
        sections.append("# 1. THE INTENT (Human-Editable)")
        sections.append("")
        sections.append(
            "> *This section contains the original natural language intent.*"
        )
        sections.append("> *Humans can edit this section to trigger re-forging.*")
        sections.append("")
        sections.append(f"**Purpose**: {self.intent.purpose}")
        sections.append("")

        if self.intent.behavior:
            sections.append("**Behavior**:")
            for behavior in self.intent.behavior:
                sections.append(f"- {behavior}")
            sections.append("")

        if self.intent.constraints:
            sections.append("**Constraints**:")
            for constraint in self.intent.constraints:
                sections.append(f"- {constraint}")
            sections.append("")

        if self.intent.tone:
            sections.append(f"**Tone**: {self.intent.tone}")
            sections.append("")

        sections.append("---")
        sections.append("")

        # Section 2: THE CONTRACT
        sections.append("# 2. THE CONTRACT (Machine-Verified)")
        sections.append("")
        sections.append(
            "> *This section defines the agent's interface and guarantees.*"
        )
        sections.append("> *Generated by F-gent during Forge Loop Phase 2.*")
        sections.append("")

        sections.append("## Type Signature")
        sections.append("")
        sections.append(f"**Agent Name**: `{self.contract.agent_name}`")
        sections.append(f"**Input Type**: `{self.contract.input_type}`")
        sections.append(f"**Output Type**: `{self.contract.output_type}`")
        sections.append("")

        if self.contract.invariants:
            sections.append("## Invariants")
            sections.append("")
            for inv in self.contract.invariants:
                sections.append(f"- **{inv.category}**: {inv.description}")
                if inv.property:
                    sections.append(f"  - Property: `{inv.property}`")
            sections.append("")

        if self.contract.composition_rules:
            sections.append("## Composition Rules")
            sections.append("")
            for rule in self.contract.composition_rules:
                sections.append(f"- **{rule.mode}**: {rule.description}")
                if rule.type_constraint:
                    sections.append(f"  - Type constraint: `{rule.type_constraint}`")
            sections.append("")

        sections.append("---")
        sections.append("")

        # Section 3: THE EXAMPLES
        sections.append("# 3. THE EXAMPLES (Test-Driven Validation)")
        sections.append("")
        sections.append(
            "> *This section contains test cases that validate correct behavior.*"
        )
        sections.append("> *Used during Forge Loop Phase 4 (Validate).*")
        sections.append("")

        if self.intent.examples:
            for idx, example in enumerate(self.intent.examples, 1):
                sections.append(f"## Example {idx}: {example.description}")
                sections.append("")
                sections.append("**Input**:")
                sections.append("```")
                sections.append(str(example.input))
                sections.append("```")
                sections.append("")
                sections.append("**Expected Output**:")
                sections.append("```")
                sections.append(str(example.expected_output))
                sections.append("```")
                sections.append("")
        else:
            sections.append("*No examples provided.*")
            sections.append("")

        sections.append("---")
        sections.append("")

        # Section 4: THE IMPLEMENTATION
        sections.append("# 4. THE IMPLEMENTATION (Auto-Generated)")
        sections.append("")
        sections.append("> **WARNING: AUTO-GENERATED ZONE. DO NOT EDIT DIRECTLY.**")
        sections.append(">")
        sections.append(
            "> This code is synthesized by F-gent from the Intent and Contract."
        )
        sections.append(
            "> To change behavior, edit Section 1 (Intent) and invoke F-gent to re-forge."
        )
        sections.append(">")
        sections.append(f"> **Generated**: {self.metadata.created_at}")
        sections.append(f"> **Generator**: {self.metadata.created_by}")
        sections.append("> **Validation**: ✓ Parsed | ✓ Type-checked | ✓ Tests passed")
        sections.append("")
        sections.append("```python")
        sections.append(self.source_code.code)
        sections.append("```")
        sections.append("")

        sections.append("---")
        sections.append("")

        # CHANGELOG
        sections.append("# CHANGELOG")
        sections.append("")
        if self.changelog_entries:
            for entry in self.changelog_entries:
                sections.append(entry)
                sections.append("")
        else:
            sections.append(f"## v{self.metadata.version} ({self.metadata.created_at})")
            sections.append("- Initial creation")
            sections.append("")

        return "\n".join(sections)

    def compute_hash(self) -> str:
        """
        Compute SHA-256 hash of artifact for integrity verification.

        The hash is computed over the entire markdown content EXCLUDING
        the hash field itself (to avoid circular dependency).

        Returns:
            Hex digest of SHA-256 hash
        """
        # Render markdown with hash field empty
        original_hash = self.metadata.hash
        self.metadata.hash = ""
        content = self.to_markdown()
        self.metadata.hash = original_hash  # Restore

        # Compute hash
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


def extract_tags_from_intent(intent: Intent) -> list[str]:
    """
    Extract searchable tags from intent for L-gent indexing.

    Strategy:
    - Keywords from purpose (nouns, verbs)
    - Domain indicators from constraints
    - Tone descriptors

    Args:
        intent: Intent object

    Returns:
        List of lowercase tags
    """
    tags: set[str] = set()

    # Extract from purpose (simple keyword extraction)
    # In production, use NLP library like spaCy
    purpose_words = intent.purpose.lower().split()
    # Filter out common stop words
    stop_words = {"a", "an", "the", "for", "to", "of", "in", "on", "at", "by", "with"}
    tags.update(
        word for word in purpose_words if word not in stop_words and len(word) > 3
    )

    # Add tone if specified
    if intent.tone:
        tone_words = intent.tone.lower().split(",")
        tags.update(word.strip() for word in tone_words)

    # Limit to reasonable number
    return sorted(list(tags))[:10]


def determine_version_bump(
    old_contract: Optional[Contract], new_contract: Contract
) -> VersionBump:
    """
    Determine semantic version bump type based on contract changes.

    From spec/f-gents/artifacts.md versioning strategy:
    - PATCH: Implementation change, contract unchanged
    - MINOR: Non-breaking contract addition (new optional fields)
    - MAJOR: Breaking contract change (input/output types changed)

    Args:
        old_contract: Previous contract (None if new artifact)
        new_contract: Current contract

    Returns:
        VersionBump type
    """
    if old_contract is None:
        # New artifact, default to 1.0.0
        return VersionBump.MAJOR  # Will create v1.0.0

    # Check for breaking changes
    if (
        old_contract.input_type != new_contract.input_type
        or old_contract.output_type != new_contract.output_type
    ):
        return VersionBump.MAJOR

    # Check for non-breaking additions
    if len(new_contract.invariants) > len(old_contract.invariants) or len(
        new_contract.composition_rules
    ) > len(old_contract.composition_rules):
        return VersionBump.MINOR

    # No contract changes, assume implementation fix
    return VersionBump.PATCH


def assemble_artifact(
    intent: Intent,
    contract: Contract,
    source_code: SourceCode,
    version: Optional[Version] = None,
    parent_version: Optional[str] = None,
    created_by: str = "f-gent",
    status: ArtifactStatus = ArtifactStatus.EXPERIMENTAL,
) -> Artifact:
    """
    Assemble validated components into complete artifact.

    This is the core of Phase 5: taking the validated outputs from
    Phases 1-4 and crystallizing them into a permanent .alo.md artifact.

    Args:
        intent: Natural language intent (Phase 1)
        contract: Type specification (Phase 2)
        source_code: Validated implementation (Phase 3 + 4)
        version: Semantic version (default: 1.0.0)
        parent_version: Previous version if re-forging
        created_by: Creator identifier
        status: Lifecycle status

    Returns:
        Complete Artifact ready for serialization
    """
    # Default version
    if version is None:
        version = Version(1, 0, 0)

    # Generate artifact ID
    artifact_id = f"{contract.agent_name}_v{version}".replace(".", "_")

    # Extract tags from intent
    tags = extract_tags_from_intent(intent)

    # Extract dependencies from intent
    dependencies = [dep.name for dep in intent.dependencies]

    # Create metadata
    metadata = ArtifactMetadata(
        id=artifact_id,
        version=version,
        created_by=created_by,
        parent_version=parent_version,
        status=status,
        tags=tags,
        dependencies=dependencies,
    )

    # Create artifact
    artifact = Artifact(
        metadata=metadata,
        intent=intent,
        contract=contract,
        source_code=source_code,
    )

    # Compute and set hash
    artifact.metadata.hash = artifact.compute_hash()

    return artifact


def save_artifact(artifact: Artifact, output_dir: Path) -> Path:
    """
    Save artifact to .alo.md file.

    Args:
        artifact: Artifact to save
        output_dir: Directory to save artifact in

    Returns:
        Path to saved file

    Raises:
        OSError: If file cannot be written
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename: agent_name_v1_0_0.alo.md
    filename = f"{artifact.metadata.id}.alo.md"
    filepath = output_dir / filename

    # Write file
    content = artifact.to_markdown()
    filepath.write_text(content, encoding="utf-8")

    return filepath


async def register_with_lgent(
    artifact: Artifact, registry: "Registry", artifact_path: Path
) -> Optional["CatalogEntry"]:
    """
    Register artifact with L-gent catalog for discovery.

    From spec/f-gents/forge.md Phase 5 "Registration":
    - Create CatalogEntry from artifact metadata
    - Register with L-gent registry
    - Enable ecosystem-wide discovery

    Args:
        artifact: Artifact to register
        registry: L-gent Registry instance
        artifact_path: Path to .alo.md file

    Returns:
        CatalogEntry if registration successful, None if L-gent unavailable

    Raises:
        ValueError: If L-gent is not available (import failed)
    """
    if not LGENT_AVAILABLE:
        raise ValueError(
            "L-gent is not available. Cannot register artifact. "
            "Install L-gent dependencies or skip registration."
        )

    # Map artifact status to catalog status
    status_mapping = {
        ArtifactStatus.EXPERIMENTAL: Status.DRAFT,
        ArtifactStatus.ACTIVE: Status.ACTIVE,
        ArtifactStatus.DEPRECATED: Status.DEPRECATED,
        ArtifactStatus.RETIRED: Status.RETIRED,
    }

    # Create catalog entry
    entry = CatalogEntry(
        id=artifact.metadata.id,
        entity_type=EntityType.AGENT,
        name=artifact.contract.agent_name,
        version=str(artifact.metadata.version),
        description=artifact.intent.purpose,
        keywords=artifact.metadata.tags,
        author=artifact.metadata.created_by,
        created_at=datetime.fromisoformat(artifact.metadata.created_at),
        forged_by=artifact.metadata.created_by,
        forged_from=artifact.intent.purpose,  # Intent as source
        input_type=artifact.contract.input_type,
        output_type=artifact.contract.output_type,
        contracts_implemented=[],  # Contract itself defines interface
        status=status_mapping[artifact.metadata.status],
    )

    # Add lineage relationships if re-forging
    if artifact.metadata.parent_version:
        entry.relationships["successor_to"] = [artifact.metadata.parent_version]

    # Add dependency relationships
    if artifact.metadata.dependencies:
        entry.relationships["depends_on"] = artifact.metadata.dependencies

    # Register with L-gent (async operation)
    await registry.register(entry)

    return entry


async def crystallize(
    intent: Intent,
    contract: Contract,
    source_code: SourceCode,
    output_dir: Path,
    version: Optional[Version] = None,
    parent_version: Optional[str] = None,
    created_by: str = "f-gent",
    status: ArtifactStatus = ArtifactStatus.EXPERIMENTAL,
    registry: Optional["Registry"] = None,
) -> tuple[Artifact, Path, Optional["CatalogEntry"]]:
    """
    Complete Phase 5: Crystallize validated components into artifact.

    This function:
    1. Assembles artifact from intent, contract, source code
    2. Computes integrity hash
    3. Saves to .alo.md file
    4. Optionally registers with L-gent (if registry provided)
    5. Returns artifact, file path, and catalog entry

    Args:
        intent: Natural language intent
        contract: Type specification
        source_code: Validated implementation
        output_dir: Where to save .alo.md file
        version: Semantic version (default: 1.0.0)
        parent_version: Previous version if re-forging
        created_by: Creator identifier
        status: Lifecycle status
        registry: Optional L-gent Registry for registration

    Returns:
        Tuple of (Artifact, Path to saved file, Optional CatalogEntry)
    """
    # Assemble artifact
    artifact = assemble_artifact(
        intent=intent,
        contract=contract,
        source_code=source_code,
        version=version,
        parent_version=parent_version,
        created_by=created_by,
        status=status,
    )

    # Save to file
    filepath = save_artifact(artifact, output_dir)

    # Register with L-gent if available
    catalog_entry = None
    if registry is not None and LGENT_AVAILABLE:
        catalog_entry = await register_with_lgent(artifact, registry, filepath)

    return artifact, filepath, catalog_entry
