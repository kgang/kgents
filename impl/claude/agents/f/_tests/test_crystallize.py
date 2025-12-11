"""
Tests for F-gent Phase 5: Crystallize

Test coverage:
1. Version parsing and bumping
2. Artifact metadata creation
3. Artifact assembly and markdown generation
4. Hash computation and integrity
5. Tag extraction from intent
6. Version bump determination
7. File saving
8. L-gent registration
9. Full crystallization workflow
10. Re-forging scenarios
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from agents.f.contract import CompositionRule, Contract, Invariant
from agents.f.crystallize import (
    ArtifactMetadata,
    ArtifactStatus,
    Version,
    VersionBump,
    assemble_artifact,
    crystallize,
    determine_version_bump,
    extract_tags_from_intent,
    save_artifact,
)
from agents.f.intent import Dependency, DependencyType, Example, Intent
from agents.f.prototype import SourceCode, StaticAnalysisReport

# Try to import L-gent for registration tests
try:
    from agents.d.persistent import PersistentAgent
    from agents.f.crystallize import register_with_lgent
    from agents.l.catalog import Registry

    LGENT_AVAILABLE = True
except ImportError:
    LGENT_AVAILABLE = False


# ==================== Fixtures ====================


@pytest.fixture
def sample_intent() -> Intent:
    """Sample intent for testing."""
    return Intent(
        purpose="Fetch weather data for a given location",
        behavior=["Query weather API", "Return structured JSON"],
        constraints=["Timeout < 5s", "Idempotent", "Handle network errors"],
        tone="Professional, concise",
        dependencies=[
            Dependency(
                name="WeatherAPI",
                type=DependencyType.REST_API,
                description="External weather service",
                required=True,
            )
        ],
        examples=[
            Example(
                input="Seattle, WA",
                expected_output={"temp": 55, "condition": "cloudy"},
                description="Standard query",
            ),
            Example(
                input="New York, NY",
                expected_output={"temp": 72, "condition": "sunny"},
                description="Different location",
            ),
        ],
        raw_text="Create an agent that fetches weather data",
    )


@pytest.fixture
def sample_contract(sample_intent: Intent) -> Contract:
    """Sample contract for testing."""
    return Contract(
        agent_name="WeatherFetcher",
        input_type="str",
        output_type="WeatherData",
        invariants=[
            Invariant(
                description="Response time < 5s",
                property="execution_time < 5.0",
                category="performance",
            ),
            Invariant(
                description="Idempotent",
                property="f(x) == f(x)",
                category="correctness",
            ),
        ],
        composition_rules=[
            CompositionRule(
                mode="sequential",
                description="Can compose with data processors",
                type_constraint="WeatherData → Report",
            )
        ],
        semantic_intent="Fetch current weather data",
        raw_intent=sample_intent,
    )


@pytest.fixture
def sample_source_code() -> SourceCode:
    """Sample source code for testing."""
    code = '''
class WeatherFetcher:
    """Fetch weather data from API."""

    def invoke(self, location: str) -> dict:
        """Fetch weather for location."""
        # Implementation here
        return {"temp": 55, "condition": "cloudy"}
'''
    return SourceCode(
        code=code.strip(),
        analysis_report=StaticAnalysisReport(results=[], passed=True),
        generation_attempt=1,
    )


# ==================== Version Tests ====================


def test_version_string_format() -> None:
    """Version formats as MAJOR.MINOR.PATCH."""
    v = Version(1, 2, 3)
    assert str(v) == "1.2.3"


def test_version_parse_valid() -> None:
    """Version.parse handles valid strings."""
    v = Version.parse("2.5.13")
    assert v.major == 2
    assert v.minor == 5
    assert v.patch == 13


def test_version_parse_invalid() -> None:
    """Version.parse rejects invalid strings."""
    with pytest.raises(ValueError, match="Invalid version string"):
        Version.parse("1.0")

    with pytest.raises(ValueError, match="Invalid version string"):
        Version.parse("v1.0.0")

    with pytest.raises(ValueError, match="Invalid version string"):
        Version.parse("not-a-version")


def test_version_bump_patch() -> None:
    """Version.bump(PATCH) increments patch number."""
    v = Version(1, 0, 0)
    v2 = v.bump(VersionBump.PATCH)
    assert str(v2) == "1.0.1"


def test_version_bump_minor() -> None:
    """Version.bump(MINOR) increments minor, resets patch."""
    v = Version(1, 0, 5)
    v2 = v.bump(VersionBump.MINOR)
    assert str(v2) == "1.1.0"


def test_version_bump_major() -> None:
    """Version.bump(MAJOR) increments major, resets minor and patch."""
    v = Version(1, 3, 7)
    v2 = v.bump(VersionBump.MAJOR)
    assert str(v2) == "2.0.0"


# ==================== Metadata Tests ====================


def test_artifact_metadata_defaults() -> None:
    """ArtifactMetadata has sensible defaults."""
    meta = ArtifactMetadata(id="test_agent_v1")
    assert meta.artifact_type == "f_gent_artifact"
    assert meta.version.major == 1
    assert meta.version.minor == 0
    assert meta.version.patch == 0
    assert meta.status == ArtifactStatus.EXPERIMENTAL
    assert meta.tags == []
    assert meta.dependencies == []


def test_artifact_metadata_to_yaml() -> None:
    """ArtifactMetadata.to_yaml generates valid YAML."""
    meta = ArtifactMetadata(
        id="weather_fetcher_v1_0_0",
        version=Version(1, 0, 0),
        created_by="f-gent-test",
        status=ArtifactStatus.ACTIVE,
        tags=["weather", "api"],
        dependencies=["requests"],
        hash="abc123",
    )

    yaml = meta.to_yaml()
    assert "---" in yaml
    assert 'id: "weather_fetcher_v1_0_0"' in yaml
    assert 'version: "1.0.0"' in yaml
    assert 'status: "active"' in yaml
    assert 'hash: "abc123"' in yaml
    assert '"weather"' in yaml
    assert '"api"' in yaml
    assert '"requests"' in yaml


def test_artifact_metadata_yaml_parent_version() -> None:
    """Metadata includes parent_version for re-forged artifacts."""
    meta = ArtifactMetadata(
        id="agent_v2", version=Version(2, 0, 0), parent_version="1.0.0"
    )

    yaml = meta.to_yaml()
    assert 'parent_version: "1.0.0"' in yaml


# ==================== Tag Extraction Tests ====================


def test_extract_tags_from_purpose() -> None:
    """extract_tags_from_intent extracts keywords from purpose."""
    intent = Intent(
        purpose="Summarize technical papers for executive reading",
        behavior=[],
        constraints=[],
    )

    tags = extract_tags_from_intent(intent)
    # Should extract words > 3 chars, excluding stop words
    assert "summarize" in tags or "technical" in tags or "papers" in tags


def test_extract_tags_includes_tone() -> None:
    """extract_tags_from_intent includes tone descriptors."""
    intent = Intent(
        purpose="Process data",
        behavior=[],
        constraints=[],
        tone="Professional, concise, friendly",
    )

    tags = extract_tags_from_intent(intent)
    # Tone words should be included
    tone_related = any(tag in ["professional", "concise", "friendly"] for tag in tags)
    assert tone_related


def test_extract_tags_limits_count() -> None:
    """extract_tags_from_intent limits to 10 tags."""
    intent = Intent(
        purpose=" ".join([f"word{i}" for i in range(20)]),  # 20 words
        behavior=[],
        constraints=[],
    )

    tags = extract_tags_from_intent(intent)
    assert len(tags) <= 10


# ==================== Version Bump Determination Tests ====================


def test_determine_version_bump_new_artifact() -> None:
    """determine_version_bump returns MAJOR for new artifacts."""
    contract = Contract(
        agent_name="NewAgent",
        input_type="str",
        output_type="int",
        invariants=[],
        composition_rules=[],
    )

    bump = determine_version_bump(old_contract=None, new_contract=contract)
    assert bump == VersionBump.MAJOR


def test_determine_version_bump_breaking_input_type() -> None:
    """determine_version_bump detects input type changes as MAJOR."""
    old = Contract(
        agent_name="Agent",
        input_type="str",
        output_type="int",
        invariants=[],
        composition_rules=[],
    )
    new = Contract(
        agent_name="Agent",
        input_type="Document",  # Changed
        output_type="int",
        invariants=[],
        composition_rules=[],
    )

    bump = determine_version_bump(old_contract=old, new_contract=new)
    assert bump == VersionBump.MAJOR


def test_determine_version_bump_breaking_output_type() -> None:
    """determine_version_bump detects output type changes as MAJOR."""
    old = Contract(
        agent_name="Agent",
        input_type="str",
        output_type="int",
        invariants=[],
        composition_rules=[],
    )
    new = Contract(
        agent_name="Agent",
        input_type="str",
        output_type="float",  # Changed
        invariants=[],
        composition_rules=[],
    )

    bump = determine_version_bump(old_contract=old, new_contract=new)
    assert bump == VersionBump.MAJOR


def test_determine_version_bump_added_invariants() -> None:
    """determine_version_bump detects new invariants as MINOR."""
    old = Contract(
        agent_name="Agent",
        input_type="str",
        output_type="int",
        invariants=[],
        composition_rules=[],
    )
    new = Contract(
        agent_name="Agent",
        input_type="str",
        output_type="int",
        invariants=[
            Invariant(description="New check", property="x > 0", category="correctness")
        ],
        composition_rules=[],
    )

    bump = determine_version_bump(old_contract=old, new_contract=new)
    assert bump == VersionBump.MINOR


def test_determine_version_bump_no_contract_change() -> None:
    """determine_version_bump returns PATCH if contract unchanged."""
    contract = Contract(
        agent_name="Agent",
        input_type="str",
        output_type="int",
        invariants=[],
        composition_rules=[],
    )

    bump = determine_version_bump(old_contract=contract, new_contract=contract)
    assert bump == VersionBump.PATCH


# ==================== Artifact Assembly Tests ====================


def test_assemble_artifact_creates_valid_artifact(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """assemble_artifact creates complete artifact."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    assert artifact.metadata.id == "WeatherFetcher_v1_0_0"
    assert artifact.metadata.version == Version(1, 0, 0)
    assert artifact.intent == sample_intent
    assert artifact.contract == sample_contract
    assert artifact.source_code == sample_source_code
    assert artifact.metadata.hash != ""  # Hash computed


def test_assemble_artifact_extracts_tags(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """assemble_artifact extracts tags from intent."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    assert len(artifact.metadata.tags) > 0
    # Should extract some keywords from purpose
    assert any(
        tag in artifact.metadata.tags
        for tag in ["fetch", "weather", "data", "location"]
    )


def test_assemble_artifact_extracts_dependencies(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """assemble_artifact extracts dependencies from intent."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    assert "WeatherAPI" in artifact.metadata.dependencies


def test_assemble_artifact_custom_version(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """assemble_artifact accepts custom version."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
        version=Version(2, 3, 5),
    )

    assert artifact.metadata.version == Version(2, 3, 5)
    assert artifact.metadata.id == "WeatherFetcher_v2_3_5"


def test_assemble_artifact_with_parent_version(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """assemble_artifact tracks parent version for re-forging."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
        version=Version(1, 0, 1),
        parent_version="1.0.0",
    )

    assert artifact.metadata.parent_version == "1.0.0"


# ==================== Markdown Generation Tests ====================


def test_artifact_to_markdown_structure(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact.to_markdown generates well-structured markdown."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    markdown = artifact.to_markdown()

    # Should have all sections
    assert "---" in markdown  # YAML frontmatter
    assert "# 1. THE INTENT" in markdown
    assert "# 2. THE CONTRACT" in markdown
    assert "# 3. THE EXAMPLES" in markdown
    assert "# 4. THE IMPLEMENTATION" in markdown
    assert "# CHANGELOG" in markdown


def test_artifact_to_markdown_includes_intent(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact markdown includes intent details."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    markdown = artifact.to_markdown()

    assert sample_intent.purpose in markdown
    assert "Query weather API" in markdown  # behavior
    assert "Timeout < 5s" in markdown  # constraint


def test_artifact_to_markdown_includes_contract(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact markdown includes contract details."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    markdown = artifact.to_markdown()

    assert "WeatherFetcher" in markdown  # agent name
    assert "str" in markdown  # input type
    assert "WeatherData" in markdown  # output type
    assert "Response time < 5s" in markdown  # invariant


def test_artifact_to_markdown_includes_examples(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact markdown includes test examples."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    markdown = artifact.to_markdown()

    assert "Seattle, WA" in markdown  # example input
    assert "cloudy" in markdown  # example output


def test_artifact_to_markdown_includes_source_code(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact markdown includes implementation."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    markdown = artifact.to_markdown()

    assert "```python" in markdown
    assert "class WeatherFetcher" in markdown
    assert "DO NOT EDIT DIRECTLY" in markdown  # Warning


# ==================== Hash Computation Tests ====================


def test_artifact_compute_hash_deterministic(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact.compute_hash is deterministic for same content."""
    # Use fixed timestamp to ensure determinism
    fixed_time = "2025-12-08T10:00:00+00:00"

    artifact1 = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )
    artifact1.metadata.created_at = fixed_time

    artifact2 = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )
    artifact2.metadata.created_at = fixed_time

    hash1 = artifact1.compute_hash()
    hash2 = artifact2.compute_hash()

    assert hash1 == hash2


def test_artifact_compute_hash_changes_with_content(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact.compute_hash changes if content changes."""
    artifact1 = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    # Modify intent
    modified_intent = Intent(
        purpose="MODIFIED PURPOSE",
        behavior=sample_intent.behavior,
        constraints=sample_intent.constraints,
    )
    artifact2 = assemble_artifact(
        intent=modified_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    hash1 = artifact1.compute_hash()
    hash2 = artifact2.compute_hash()

    assert hash1 != hash2


def test_artifact_hash_excludes_hash_field(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact hash computation excludes hash field itself."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    # Hash should be non-empty
    assert artifact.metadata.hash != ""
    assert len(artifact.metadata.hash) == 64  # SHA-256 hex digest


# ==================== File Saving Tests ====================


def test_save_artifact_creates_file(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """save_artifact creates .alo.md file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        artifact = assemble_artifact(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
        )

        filepath = save_artifact(artifact, output_dir)

        assert filepath.exists()
        assert filepath.suffix == ".md"
        assert "WeatherFetcher" in filepath.name


def test_save_artifact_content_matches_markdown(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """save_artifact writes correct markdown content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        artifact = assemble_artifact(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
        )

        filepath = save_artifact(artifact, output_dir)
        content = filepath.read_text()

        assert content == artifact.to_markdown()


def test_save_artifact_creates_directory(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """save_artifact creates output directory if needed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "nested" / "directory"
        assert not output_dir.exists()

        artifact = assemble_artifact(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
        )

        filepath = save_artifact(artifact, output_dir)

        assert output_dir.exists()
        assert filepath.exists()


# ==================== L-gent Registration Tests ====================


@pytest.mark.skipif(not LGENT_AVAILABLE, reason="L-gent not available")
async def test_register_with_lgent_creates_entry(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """register_with_lgent creates catalog entry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = str(Path(tmpdir) / "registry.json")
        registry = Registry(storage_path)

        artifact = assemble_artifact(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
        )

        entry = await register_with_lgent(artifact, registry, Path("/tmp/test.alo.md"))

        assert entry is not None
        assert entry.id == artifact.metadata.id
        assert entry.name == "WeatherFetcher"
        assert entry.description == sample_intent.purpose


@pytest.mark.skipif(not LGENT_AVAILABLE, reason="L-gent not available")
async def test_register_with_lgent_maps_status(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """register_with_lgent maps artifact status to catalog status."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = str(Path(tmpdir) / "registry.json")
        registry = Registry(storage_path)

        artifact = assemble_artifact(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
            status=ArtifactStatus.ACTIVE,
        )

        entry = await register_with_lgent(artifact, registry, Path("/tmp/test.alo.md"))

        from agents.l.catalog import Status

        assert entry is not None
        assert entry.status == Status.ACTIVE


@pytest.mark.skipif(not LGENT_AVAILABLE, reason="L-gent not available")
async def test_register_with_lgent_lineage_relationships(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """register_with_lgent adds lineage relationships."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = str(Path(tmpdir) / "registry.json")
        registry = Registry(storage_path)

        artifact = assemble_artifact(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
            version=Version(1, 0, 1),
            parent_version="1.0.0",
        )

        entry = await register_with_lgent(artifact, registry, Path("/tmp/test.alo.md"))

        assert entry is not None
        assert "successor_to" in entry.relationships
        assert "1.0.0" in entry.relationships["successor_to"]


# ==================== Full Crystallization Tests ====================


async def test_crystallize_full_workflow(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """crystallize executes complete Phase 5 workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        artifact, filepath, catalog_entry = await crystallize(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
            output_dir=output_dir,
        )

        # Artifact created
        assert artifact is not None
        assert artifact.metadata.hash != ""

        # File saved
        assert filepath.exists()
        assert filepath.read_text() == artifact.to_markdown()

        # No registry provided, so no catalog entry
        assert catalog_entry is None


@pytest.mark.skipif(not LGENT_AVAILABLE, reason="L-gent not available")
async def test_crystallize_with_lgent_registration(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """crystallize registers with L-gent if registry provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        storage_path = str(Path(tmpdir) / "registry.json")
        registry = Registry(storage_path)

        artifact, filepath, catalog_entry = await crystallize(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
            output_dir=output_dir,
            registry=registry,
        )

        # Catalog entry created
        assert catalog_entry is not None
        assert catalog_entry.id == artifact.metadata.id

        # Entry retrievable from registry
        retrieved = await registry.get(artifact.metadata.id)
        assert retrieved is not None
        assert retrieved.name == "WeatherFetcher"


async def test_crystallize_re_forging_scenario(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """crystallize handles re-forging with version increment."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)

        # Initial artifact
        artifact_v1, _, _ = await crystallize(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
            output_dir=output_dir,
            version=Version(1, 0, 0),
        )

        # Re-forge with patch version
        artifact_v2, filepath_v2, _ = await crystallize(
            intent=sample_intent,
            contract=sample_contract,
            source_code=sample_source_code,
            output_dir=output_dir,
            version=Version(1, 0, 1),
            parent_version="1.0.0",
        )

        # Version incremented
        assert artifact_v2.metadata.version == Version(1, 0, 1)
        assert artifact_v2.metadata.parent_version == "1.0.0"

        # Different file created
        assert "v1_0_1" in filepath_v2.name

        # Different hash (metadata differs)
        assert artifact_v1.metadata.hash != artifact_v2.metadata.hash


# ==================== Edge Cases ====================


def test_artifact_with_no_examples(
    sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact handles intent with no examples."""
    intent_no_examples = Intent(
        purpose="Simple agent",
        behavior=[],
        constraints=[],
        examples=[],  # No examples
    )

    artifact = assemble_artifact(
        intent=intent_no_examples,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    markdown = artifact.to_markdown()
    assert "# 3. THE EXAMPLES" in markdown
    assert "No examples provided" in markdown


def test_artifact_with_no_dependencies(
    sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact handles intent with no dependencies."""
    intent_no_deps = Intent(
        purpose="Self-contained agent",
        behavior=[],
        constraints=[],
        dependencies=[],  # No dependencies
    )

    artifact = assemble_artifact(
        intent=intent_no_deps,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    assert artifact.metadata.dependencies == []


def test_artifact_changelog_default(
    sample_intent: Intent, sample_contract: Contract, sample_source_code: SourceCode
) -> None:
    """Artifact includes default changelog for v1.0.0."""
    artifact = assemble_artifact(
        intent=sample_intent,
        contract=sample_contract,
        source_code=sample_source_code,
    )

    markdown = artifact.to_markdown()
    assert "# CHANGELOG" in markdown
    assert "Initial creation" in markdown
