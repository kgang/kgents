"""
Manifest command for A-gent.

Generates projection artifacts via target-specific Projectors.

Targets:
- k8s: Kubernetes manifests (YAML)
- cli: Executable Python script
- docker: Dockerfile
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from . import _emit_output
from .inspect import resolve_agent_class

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# Valid projection targets
VALID_TARGETS = {"k8s", "cli", "docker", "wasm", "marimo"}


def execute_manifest(
    agent_name: str,
    namespace: str,
    json_mode: bool,
    validate_mode: bool,
    target: str,
    ctx: "InvocationContext | None",
) -> int:
    """
    Handle 'a manifest <agent>' command.

    Routes to appropriate projector based on --target flag:
    - k8s: K8sProjector → YAML manifests
    - cli: CLIProjector → Executable Python script
    - docker: DockerProjector → Dockerfile
    """
    # Validate target
    if target not in VALID_TARGETS:
        _emit_output(
            f"[A] Invalid target: {target}. Valid: {', '.join(sorted(VALID_TARGETS))}",
            {"error": f"Invalid target: {target}"},
            ctx,
        )
        return 1

    try:
        agent_cls = resolve_agent_class(agent_name)
        if agent_cls is None:
            _emit_output(
                f"[A] Agent not found: {agent_name}",
                {"error": f"Agent not found: {agent_name}"},
                ctx,
            )
            return 1

        # Route to appropriate projector
        match target:
            case "k8s":
                return _execute_k8s_manifest(
                    agent_cls, agent_name, namespace, json_mode, validate_mode, ctx
                )
            case "cli":
                return _execute_cli_manifest(agent_cls, agent_name, json_mode, ctx)
            case "docker":
                return _execute_docker_manifest(agent_cls, agent_name, json_mode, ctx)
            case "wasm":
                return _execute_wasm_manifest(agent_cls, agent_name, json_mode, ctx)
            case "marimo":
                return _execute_marimo_manifest(agent_cls, agent_name, json_mode, ctx)
            case _:
                # Should not reach here due to validation above
                _emit_output(
                    f"[A] Unsupported target: {target}",
                    {"error": f"Unsupported target: {target}"},
                    ctx,
                )
                return 1

    except Exception as e:
        _emit_output(f"[A] Error generating manifests: {e}", {"error": str(e)}, ctx)
        return 1


def _execute_k8s_manifest(
    agent_cls: type,
    agent_name: str,
    namespace: str,
    json_mode: bool,
    validate_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Generate K8s manifests via K8sProjector."""
    from system.projector import K8sProjector, manifests_to_yaml

    # Compile to K8s manifests
    projector = K8sProjector(namespace=namespace)
    resources = projector.compile(agent_cls)

    # Validate if requested
    if validate_mode:
        validation_result = _validate_manifests(resources)
        if not validation_result["valid"]:
            _emit_output(
                f"[A] Validation failed: {validation_result['errors']}",
                {"valid": False, "errors": validation_result["errors"]},
                ctx,
            )
            return 1

    if json_mode:
        import json

        manifests = [r.to_dict() for r in resources]
        result: dict[str, Any] = {"manifests": manifests, "count": len(resources)}
        if validate_mode:
            result["valid"] = True
            result["message"] = f"Generated {len(resources)} valid K8s resources"
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        yaml_output = manifests_to_yaml(resources)
        if validate_mode:
            _emit_output(
                f"[A] Generated {len(resources)} valid K8s resources\n---\n{yaml_output}",
                {"manifest_count": len(resources), "valid": True},
                ctx,
            )
        else:
            _emit_output(yaml_output, {"manifest_count": len(resources)}, ctx)

    return 0


def _execute_cli_manifest(
    agent_cls: type,
    agent_name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Generate CLI script via CLIProjector."""
    from system.projector import CLIProjector

    projector = CLIProjector()
    script = projector.compile(agent_cls)

    if json_mode:
        import json

        result = {
            "target": "cli",
            "agent": agent_name,
            "script": script,
            "lines": len(script.splitlines()),
        }
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        _emit_output(script, {"target": "cli", "agent": agent_name}, ctx)

    return 0


def _execute_docker_manifest(
    agent_cls: type,
    agent_name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Generate Dockerfile via DockerProjector."""
    try:
        from system.projector import DockerProjector
    except ImportError:
        _emit_output(
            "[A] DockerProjector not yet implemented",
            {"error": "DockerProjector not implemented"},
            ctx,
        )
        return 1

    projector = DockerProjector()
    dockerfile = projector.compile(agent_cls)

    if json_mode:
        import json

        result = {
            "target": "docker",
            "agent": agent_name,
            "dockerfile": dockerfile,
            "lines": len(dockerfile.splitlines()),
        }
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        _emit_output(dockerfile, {"target": "docker", "agent": agent_name}, ctx)

    return 0


def _execute_wasm_manifest(
    agent_cls: type,
    agent_name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Generate WASM HTML bundle via WASMProjector."""
    from system.projector import WASMProjector

    projector = WASMProjector()
    html = projector.compile(agent_cls)

    if json_mode:
        import json

        result = {
            "target": "wasm",
            "agent": agent_name,
            "html": html,
            "lines": len(html.splitlines()),
            "sandbox": True,
        }
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        _emit_output(html, {"target": "wasm", "agent": agent_name, "sandbox": True}, ctx)

    return 0


def _execute_marimo_manifest(
    agent_cls: type,
    agent_name: str,
    json_mode: bool,
    ctx: "InvocationContext | None",
) -> int:
    """Generate marimo cell via MarimoProjector."""
    from system.projector import MarimoProjector

    projector = MarimoProjector()
    cell = projector.compile(agent_cls)

    if json_mode:
        import json

        result = {
            "target": "marimo",
            "agent": agent_name,
            "cell": cell,
            "lines": len(cell.splitlines()),
            "interactive": True,
        }
        _emit_output(json.dumps(result, indent=2), result, ctx)
    else:
        _emit_output(cell, {"target": "marimo", "agent": agent_name, "interactive": True}, ctx)

    return 0


def _validate_manifests(resources: list[Any]) -> dict[str, Any]:
    """
    Validate K8s manifests for correctness.

    Checks:
    - Required fields present (apiVersion, kind, metadata.name)
    - Names are RFC 1123 compliant
    - Namespace is set on all resources
    - No duplicate resource names within same kind

    Returns:
        dict with 'valid' bool and 'errors' list
    """
    rfc1123 = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
    errors: list[str] = []
    seen: dict[str, set[str]] = {}  # kind -> set of names

    for r in resources:
        d = r.to_dict()

        # Check required fields
        if "apiVersion" not in d:
            errors.append(f"Missing apiVersion in {r.kind}")
        if "kind" not in d:
            errors.append("Missing kind")
        if "metadata" not in d or "name" not in d.get("metadata", {}):
            errors.append(f"Missing metadata.name in {r.kind}")
            continue

        name = d["metadata"]["name"]
        kind = d["kind"]

        # RFC 1123 validation
        if not rfc1123.match(name):
            errors.append(f"Invalid name '{name}' in {kind}: not RFC 1123 compliant")

        # Length check
        if len(name) > 63:
            errors.append(f"Name '{name}' in {kind} exceeds 63 chars")

        # Namespace check
        if "namespace" not in d.get("metadata", {}):
            errors.append(f"Missing namespace in {kind}/{name}")

        # Duplicate check
        if kind not in seen:
            seen[kind] = set()
        if name in seen[kind]:
            errors.append(f"Duplicate {kind} name: {name}")
        seen[kind].add(name)

    return {"valid": len(errors) == 0, "errors": errors}
