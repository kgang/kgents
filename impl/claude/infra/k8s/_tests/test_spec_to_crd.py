"""Tests for spec-to-CRD generator."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from ..spec_to_crd import (
    AgentSpecDefinition,
    GeneratorResult,
    SpecParser,
    SpecToCRDGenerator,
)


class TestAgentSpecDefinition:
    """Tests for AgentSpecDefinition."""

    def test_defaults(self):
        """Default values are set."""
        spec = AgentSpecDefinition(genus="B", name="B-gent")

        assert spec.genus == "B"
        assert spec.name == "B-gent"
        assert spec.image == "python:3.12-slim"
        assert spec.replicas == 1
        assert spec.cpu == "100m"
        assert spec.memory == "256Mi"
        assert spec.sidecar_enabled is True
        assert spec.entrypoint is None
        assert spec.config == {}

    def test_to_crd_manifest_minimal(self):
        """Generate minimal CRD manifest."""
        spec = AgentSpecDefinition(genus="B", name="B-gent")

        manifest = spec.to_crd_manifest()

        assert manifest["apiVersion"] == "kgents.io/v1"
        assert manifest["kind"] == "Agent"
        assert manifest["metadata"]["name"] == "b-gent"
        assert manifest["metadata"]["namespace"] == "kgents-agents"
        assert manifest["spec"]["genus"] == "B"
        assert manifest["spec"]["replicas"] == 1

    def test_to_crd_manifest_full(self):
        """Generate full CRD manifest with all options."""
        spec = AgentSpecDefinition(
            genus="B",
            name="B-gent",
            image="custom/b-gent:v1",
            replicas=3,
            cpu="500m",
            memory="1Gi",
            sidecar_enabled=True,
            entrypoint="agents.b.main",
            config={"token_budget": 10000},
            allow_egress=True,
            allowed_peers=["L", "F"],
        )

        manifest = spec.to_crd_manifest()

        assert manifest["spec"]["image"] == "custom/b-gent:v1"
        assert manifest["spec"]["replicas"] == 3
        assert manifest["spec"]["resources"]["cpu"] == "500m"
        assert manifest["spec"]["resources"]["memory"] == "1Gi"
        assert manifest["spec"]["entrypoint"] == "agents.b.main"
        assert manifest["spec"]["config"]["token_budget"] == 10000
        assert manifest["spec"]["networkPolicy"]["allowEgress"] is True
        assert manifest["spec"]["networkPolicy"]["allowedPeers"] == ["L", "F"]

    def test_manifest_labels(self):
        """Labels are set correctly."""
        spec = AgentSpecDefinition(genus="B", name="B-gent")

        manifest = spec.to_crd_manifest()

        labels = manifest["metadata"]["labels"]
        assert labels["app.kubernetes.io/part-of"] == "kgents"
        assert labels["kgents.io/genus"] == "B"


class TestSpecParser:
    """Tests for SpecParser."""

    def test_parse_frontmatter(self, tmp_path: Path):
        """Parse YAML frontmatter from markdown."""
        spec_file = tmp_path / "b-gent.md"
        spec_file.write_text(
            dedent(
                """
            ---
            genus: B
            name: B-gent
            resources:
              cpu: 200m
              memory: 512Mi
            ---

            # B-gent

            The Banker agent.
            """
            ).strip()
        )

        parser = SpecParser()
        spec = parser.parse_file(spec_file)

        assert spec is not None
        assert spec.genus == "B"
        assert spec.name == "B-gent"
        assert spec.cpu == "200m"
        assert spec.memory == "512Mi"

    def test_parse_frontmatter_full(self, tmp_path: Path):
        """Parse frontmatter with all options."""
        spec_file = tmp_path / "l-gent.md"
        spec_file.write_text(
            dedent(
                """
            ---
            genus: L
            name: L-gent
            image: custom/l-gent:v1
            replicas: 2
            resources:
              cpu: 500m
              memory: 1Gi
            sidecar: true
            entrypoint: agents.l.main
            config:
              max_results: 100
            networkPolicy:
              allowEgress: false
              allowedPeers:
                - B
                - F
            ---

            # L-gent

            The Librarian agent.
            """
            ).strip()
        )

        parser = SpecParser()
        spec = parser.parse_file(spec_file)

        assert spec is not None
        assert spec.genus == "L"
        assert spec.image == "custom/l-gent:v1"
        assert spec.replicas == 2
        assert spec.cpu == "500m"
        assert spec.memory == "1Gi"
        assert spec.entrypoint == "agents.l.main"
        assert spec.config["max_results"] == 100
        assert spec.allowed_peers == ["B", "F"]

    def test_parse_no_frontmatter_fallback(self, tmp_path: Path):
        """Fall back to parsing from filename."""
        spec_file = tmp_path / "f-gent.md"
        spec_file.write_text(
            dedent(
                """
            # F-gent

            The Frontier agent for LLM invocation.
            """
            ).strip()
        )

        parser = SpecParser()
        spec = parser.parse_file(spec_file)

        assert spec is not None
        assert spec.genus == "F"
        assert spec.name == "F-gent"

    def test_parse_psi_gent(self, tmp_path: Path):
        """Parse Psi-gent (special case)."""
        spec_file = tmp_path / "psi-gent.md"
        spec_file.write_text(
            dedent(
                """
            ---
            genus: Psi
            name: Psi-gent
            ---

            # Psi-gent

            The Psychopomp.
            """
            ).strip()
        )

        parser = SpecParser()
        spec = parser.parse_file(spec_file)

        assert spec is not None
        assert spec.genus == "Psi"

    def test_genus_from_path_single_letter(self, tmp_path: Path):
        """Extract single-letter genus from path."""
        parser = SpecParser()

        assert parser._genus_from_path(Path("b-gent.md")) == "B"
        assert parser._genus_from_path(Path("bgent.md")) == "B"
        assert parser._genus_from_path(Path("l-gent.md")) == "L"

    def test_genus_from_path_psi(self, tmp_path: Path):
        """Extract Psi genus from path."""
        parser = SpecParser()

        assert parser._genus_from_path(Path("psi-gent.md")) == "Psi"
        assert parser._genus_from_path(Path("psigent.md")) == "Psi"


class TestSpecToCRDGenerator:
    """Tests for SpecToCRDGenerator."""

    def test_generate_one(self, tmp_path: Path):
        """Generate CRD for single spec file."""
        spec_dir = tmp_path / "spec" / "agents"
        spec_dir.mkdir(parents=True)

        output_dir = tmp_path / "output"

        spec_file = spec_dir / "b-gent.md"
        spec_file.write_text(
            dedent(
                """
            ---
            genus: B
            name: B-gent
            ---

            # B-gent
            """
            ).strip()
        )

        generator = SpecToCRDGenerator(
            spec_dir=spec_dir,
            output_dir=output_dir,
        )

        result = generator.generate_one(spec_file)

        assert result.success is True
        assert len(result.generated) == 1
        assert result.generated[0].name == "b-gent.yaml"
        assert result.generated[0].exists()

    def test_generate_all(self, tmp_path: Path):
        """Generate CRDs for all spec files."""
        spec_dir = tmp_path / "spec" / "agents"
        spec_dir.mkdir(parents=True)

        output_dir = tmp_path / "output"

        # Create multiple spec files
        for letter in ["B", "L", "F"]:
            spec_file = spec_dir / f"{letter.lower()}-gent.md"
            spec_file.write_text(
                dedent(
                    f"""
                ---
                genus: {letter}
                name: {letter}-gent
                ---

                # {letter}-gent
                """
                ).strip()
            )

        generator = SpecToCRDGenerator(
            spec_dir=spec_dir,
            output_dir=output_dir,
        )

        result = generator.generate_all()

        assert result.success is True
        assert len(result.generated) == 3
        assert result.errors == []

    def test_generate_nonexistent_spec(self, tmp_path: Path):
        """Handle nonexistent spec file."""
        generator = SpecToCRDGenerator(
            spec_dir=tmp_path / "nonexistent",
            output_dir=tmp_path / "output",
        )

        result = generator.generate_one(tmp_path / "nonexistent.md")

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_generate_nonexistent_dir(self, tmp_path: Path):
        """Handle nonexistent spec directory."""
        generator = SpecToCRDGenerator(
            spec_dir=tmp_path / "nonexistent",
            output_dir=tmp_path / "output",
        )

        result = generator.generate_all()

        assert result.success is False
        assert "not found" in result.message.lower()

    def test_generated_crd_content(self, tmp_path: Path):
        """Verify generated CRD file content."""
        spec_dir = tmp_path / "spec" / "agents"
        spec_dir.mkdir(parents=True)

        output_dir = tmp_path / "output"

        spec_file = spec_dir / "b-gent.md"
        spec_file.write_text(
            dedent(
                """
            ---
            genus: B
            name: B-gent
            resources:
              cpu: 200m
              memory: 512Mi
            ---

            # B-gent
            """
            ).strip()
        )

        generator = SpecToCRDGenerator(
            spec_dir=spec_dir,
            output_dir=output_dir,
        )

        result = generator.generate_one(spec_file)

        # Read and verify content
        content = result.generated[0].read_text()
        assert "apiVersion: kgents.io/v1" in content
        assert "kind: Agent" in content
        assert "genus: B" in content
        assert "cpu: 200m" in content
        assert "Auto-generated" in content
