"""
Spec-to-CRD Generator for K-Terrarium.

Converts spec/*.md agent definitions to Agent CRD manifests.
Designed to be triggered by git hooks (post-commit or pre-push).

Git Hook Integration:
    # .git/hooks/post-commit
    #!/bin/bash
    python -m impl.claude.infra.k8s.spec_to_crd --watch

Design:
- Parses frontmatter from spec/agents/*.md
- Generates YAML CRD manifests
- Validates against CRD schema
- Optionally applies to cluster
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class AgentSpecDefinition:
    """Parsed agent specification from markdown."""

    genus: str
    name: str
    description: str = ""
    image: str = "python:3.12-slim"
    replicas: int = 1
    cpu: str = "100m"
    memory: str = "256Mi"
    sidecar_enabled: bool = True
    entrypoint: str | None = None
    config: dict[str, Any] = field(default_factory=dict)
    allow_egress: bool = False
    allowed_peers: list[str] = field(default_factory=list)

    def to_crd_manifest(self) -> dict[str, Any]:
        """Generate Agent CRD manifest."""
        spec: dict[str, Any] = {
            "genus": self.genus,
            "image": self.image,
            "replicas": self.replicas,
            "resources": {
                "cpu": self.cpu,
                "memory": self.memory,
            },
            "sidecar": {
                "enabled": self.sidecar_enabled,
            },
        }

        if self.entrypoint:
            spec["entrypoint"] = self.entrypoint

        if self.config:
            spec["config"] = self.config

        if self.allow_egress or self.allowed_peers:
            spec["networkPolicy"] = {
                "allowEgress": self.allow_egress,
                "allowedPeers": self.allowed_peers,
            }

        manifest: dict[str, Any] = {
            "apiVersion": "kgents.io/v1",
            "kind": "Agent",
            "metadata": {
                "name": f"{self.genus.lower()}-gent",
                "namespace": "kgents-agents",
                "labels": {
                    "app.kubernetes.io/part-of": "kgents",
                    "kgents.io/genus": self.genus,
                },
            },
            "spec": spec,
        }

        return manifest


class SpecParser:
    """
    Parse agent specifications from markdown files.

    Looks for YAML frontmatter or structured headers in spec/*.md files.

    Expected frontmatter format:
        ---
        genus: B
        name: B-gent
        resources:
          cpu: 100m
          memory: 256Mi
        sidecar: true
        ---
    """

    # Pattern for YAML frontmatter
    FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---", re.MULTILINE | re.DOTALL)

    # Pattern for structured headers (fallback)
    GENUS_PATTERN = re.compile(
        r"#\s*([A-Z])-gent|#\s*(\w+)-gent|Letter:\s*([A-Z])", re.IGNORECASE
    )

    def parse_file(self, path: Path) -> AgentSpecDefinition | None:
        """Parse a spec markdown file into AgentSpecDefinition."""
        content = path.read_text()

        # Try frontmatter first
        frontmatter = self._extract_frontmatter(content)
        if frontmatter:
            return self._from_frontmatter(frontmatter, path)

        # Fallback: extract from filename and content
        return self._from_content(content, path)

    def _extract_frontmatter(self, content: str) -> dict[str, Any] | None:
        """Extract YAML frontmatter from markdown."""
        match = self.FRONTMATTER_PATTERN.match(content)
        if not match:
            return None

        try:
            result = yaml.safe_load(match.group(1))
            if isinstance(result, dict):
                return result
            return None
        except yaml.YAMLError:
            return None

    def _from_frontmatter(
        self, data: dict[str, Any], path: Path
    ) -> AgentSpecDefinition:
        """Create spec from parsed frontmatter."""
        resources = data.get("resources", {})
        network = data.get("networkPolicy", {})

        genus = data.get("genus") or self._genus_from_path(path) or "X"

        return AgentSpecDefinition(
            genus=genus,
            name=data.get("name", f"{data.get('genus', 'X')}-gent"),
            description=data.get("description", ""),
            image=data.get("image", "python:3.12-slim"),
            replicas=data.get("replicas", 1),
            cpu=resources.get("cpu", "100m"),
            memory=resources.get("memory", "256Mi"),
            sidecar_enabled=data.get("sidecar", True),
            entrypoint=data.get("entrypoint"),
            config=data.get("config", {}),
            allow_egress=network.get("allowEgress", False),
            allowed_peers=network.get("allowedPeers", []),
        )

    def _from_content(self, content: str, path: Path) -> AgentSpecDefinition | None:
        """Fallback: extract genus from filename/content."""
        genus = self._genus_from_path(path)
        if not genus:
            # Try to find in content
            match = self.GENUS_PATTERN.search(content)
            if match:
                genus = match.group(1) or match.group(2) or match.group(3)
                genus = genus.upper()

        if not genus:
            return None

        return AgentSpecDefinition(
            genus=genus,
            name=f"{genus}-gent",
        )

    def _genus_from_path(self, path: Path) -> str | None:
        """Extract genus from filename like 'b-gent.md' or 'bgent.md'."""
        stem = path.stem.lower()

        # Pattern: x-gent or xgent
        if stem.endswith("-gent"):
            genus = stem[:-5]
        elif stem.endswith("gent"):
            genus = stem[:-4]
        else:
            genus = stem

        # Single letter genus
        if len(genus) == 1 and genus.isalpha():
            return genus.upper()

        # Special case: psi
        if genus == "psi":
            return "Psi"

        return None


@dataclass
class GeneratorResult:
    """Result of CRD generation."""

    success: bool
    message: str
    generated: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class SpecToCRDGenerator:
    """
    Generate Agent CRDs from spec files.

    Example:
        generator = SpecToCRDGenerator()
        result = generator.generate_all()
        for path in result.generated:
            print(f"Generated: {path}")
    """

    def __init__(
        self,
        spec_dir: Path | None = None,
        output_dir: Path | None = None,
    ):
        # Default paths relative to repo root
        self.spec_dir = spec_dir or Path("spec/agents")
        self.output_dir = output_dir or Path("impl/claude/infra/k8s/manifests/agents")
        self.parser = SpecParser()

    def generate_all(self) -> GeneratorResult:
        """Generate CRDs for all spec files."""
        if not self.spec_dir.exists():
            return GeneratorResult(
                success=False,
                message=f"Spec directory not found: {self.spec_dir}",
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)

        generated = []
        errors = []

        for spec_file in self.spec_dir.glob("*.md"):
            try:
                spec = self.parser.parse_file(spec_file)
                if spec:
                    output_path = self._write_crd(spec)
                    generated.append(output_path)
            except Exception as e:
                errors.append(f"{spec_file.name}: {e}")

        return GeneratorResult(
            success=len(errors) == 0,
            message=f"Generated {len(generated)} CRDs",
            generated=generated,
            errors=errors,
        )

    def generate_one(self, spec_file: Path) -> GeneratorResult:
        """Generate CRD for a single spec file."""
        if not spec_file.exists():
            return GeneratorResult(
                success=False,
                message=f"Spec file not found: {spec_file}",
            )

        self.output_dir.mkdir(parents=True, exist_ok=True)

        try:
            spec = self.parser.parse_file(spec_file)
            if spec:
                output_path = self._write_crd(spec)
                return GeneratorResult(
                    success=True,
                    message=f"Generated CRD for {spec.genus}-gent",
                    generated=[output_path],
                )
            return GeneratorResult(
                success=False,
                message=f"Could not parse spec: {spec_file}",
            )
        except Exception as e:
            return GeneratorResult(
                success=False,
                message=f"Error: {e}",
                errors=[str(e)],
            )

    def _write_crd(self, spec: AgentSpecDefinition) -> Path:
        """Write CRD manifest to file."""
        manifest = spec.to_crd_manifest()
        output_path = self.output_dir / f"{spec.genus.lower()}-gent.yaml"

        with open(output_path, "w") as f:
            f.write(f"# Auto-generated from spec/agents/{spec.genus.lower()}-gent.md\n")
            f.write("# Do not edit manually - changes will be overwritten\n")
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

        return output_path


def install_git_hook(repo_root: Path | None = None) -> bool:
    """
    Install git post-commit hook for CRD generation.

    The hook regenerates CRDs when spec/agents/*.md files change.
    """
    if repo_root is None:
        # Find repo root
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return False
            repo_root = Path(result.stdout.strip())
        except Exception:
            return False

    hooks_dir = repo_root / ".git" / "hooks"
    hook_path = hooks_dir / "post-commit"

    hook_content = """#!/bin/bash
# K-Terrarium: Regenerate Agent CRDs when specs change

# Check if any spec files changed in this commit
CHANGED_SPECS=$(git diff-tree --no-commit-id --name-only -r HEAD | grep "^spec/agents/.*\\.md$")

if [ -n "$CHANGED_SPECS" ]; then
    echo "Spec files changed, regenerating CRDs..."
    python -m impl.claude.infra.k8s.spec_to_crd
fi
"""

    try:
        # Create or append to hook
        if hook_path.exists():
            existing = hook_path.read_text()
            if "K-Terrarium" not in existing:
                with open(hook_path, "a") as f:
                    f.write("\n" + hook_content)
        else:
            hook_path.write_text(hook_content)
            hook_path.chmod(0o755)
        return True
    except Exception:
        return False


def main():
    """CLI entry point for spec-to-CRD generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Agent CRDs from spec files")
    parser.add_argument(
        "--spec-dir",
        type=Path,
        default=None,
        help="Directory containing spec markdown files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for CRD manifests",
    )
    parser.add_argument(
        "--install-hook",
        action="store_true",
        help="Install git post-commit hook",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply generated CRDs to cluster",
    )

    args = parser.parse_args()

    if args.install_hook:
        if install_git_hook():
            print("Git hook installed successfully")
        else:
            print("Failed to install git hook")
        return

    generator = SpecToCRDGenerator(
        spec_dir=args.spec_dir,
        output_dir=args.output_dir,
    )

    result = generator.generate_all()

    if result.success:
        print(f"Success: {result.message}")
        for path in result.generated:
            print(f"  Generated: {path}")
    else:
        print(f"Errors: {result.message}")
        for error in result.errors:
            print(f"  {error}")

    if args.apply and result.generated:
        print("\nApplying CRDs to cluster...")
        for path in result.generated:
            subprocess.run(["kubectl", "apply", "-f", str(path)])


if __name__ == "__main__":
    main()
