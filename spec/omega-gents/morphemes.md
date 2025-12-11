# Morpheme Catalog

## The Algebra of Bodies

Morphemes are the smallest unit of compositional transformation in the somatic domain. They compose via `>>` following category laws.

---

## Core Morphemes

### Base() - The Identity

```python
@dataclass(frozen=True)
class Base(Morpheme):
    """
    The identity morpheme: minimal viable pod.

    Laws:
    - Base() >> f ≡ f (left identity)
    - f >> Base() ≡ f (right identity)

    This is the starting point for all morphologies.
    """

    image: str = "python:3.12-slim"
    cpu: str = "100m"
    memory: str = "256Mi"

    def to_k8s_patch(self) -> dict:
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "spec": {
                "replicas": 1,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "image": self.image,
                            "resources": {
                                "requests": {"cpu": self.cpu, "memory": self.memory},
                                "limits": {"cpu": self.cpu, "memory": self.memory},
                            },
                        }],
                    },
                },
            },
        }
```

**Token Cost**: 100

---

## Compute Morphemes

### with_cortex(gpu, vram) - GPU Resources

```python
@dataclass(frozen=True)
class WithCortex(Morpheme):
    """
    Add GPU resources to morphology.

    The cortex is the agent's high-compute capability.
    Named for the cerebral cortex: dense, powerful processing.
    """

    gpu: str           # GPU type: "A100", "H100", "T4", etc.
    vram: str = "40GB" # VRAM requirement

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "nodeSelector": {
                            "nvidia.com/gpu.product": self.gpu,
                        },
                        "tolerations": [{
                            "key": "nvidia.com/gpu",
                            "operator": "Exists",
                            "effect": "NoSchedule",
                        }],
                        "containers": [{
                            "name": "agent",
                            "resources": {
                                "limits": {
                                    "nvidia.com/gpu": "1",
                                },
                            },
                        }],
                    },
                },
            },
        }


def with_cortex(gpu: str, vram: str = "40GB") -> WithCortex:
    """Factory function for cortex morpheme."""
    return WithCortex(gpu=gpu, vram=vram)
```

**Token Cost**: 1000
**Use Case**: F-gent artifact generation, Ψ-gent metaphor projection, heavy inference

---

### with_ganglia(replicas) - Horizontal Scaling

```python
@dataclass(frozen=True)
class WithGanglia(Morpheme):
    """
    Set replica count for morphology.

    Ganglia are clusters of nerve cell bodies. Multiple ganglia
    provide redundancy and parallelism.
    """

    replicas: int

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "replicas": self.replicas,
            },
        }


def with_ganglia(replicas: int) -> WithGanglia:
    """Factory function for ganglia morpheme."""
    return WithGanglia(replicas=replicas)
```

**Token Cost**: 200 * replicas
**Use Case**: High availability, parallel processing, load distribution

---

### with_resources(cpu, memory) - Resource Limits

```python
@dataclass(frozen=True)
class WithResources(Morpheme):
    """
    Override default CPU/memory resources.

    Fine-grained control over compute allocation.
    """

    cpu: str     # e.g., "500m", "2"
    memory: str  # e.g., "1Gi", "4Gi"

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "resources": {
                                "requests": {"cpu": self.cpu, "memory": self.memory},
                                "limits": {"cpu": self.cpu, "memory": self.memory},
                            },
                        }],
                    },
                },
            },
        }


def with_resources(cpu: str, memory: str) -> WithResources:
    """Factory function for resources morpheme."""
    return WithResources(cpu=cpu, memory=memory)
```

**Token Cost**: 50
**Use Case**: Tuning resource allocation for specific workloads

---

## Storage Morphemes

### with_vault(persistence, size) - Persistent Storage

```python
@dataclass(frozen=True)
class WithVault(Morpheme):
    """
    Add persistent storage to morphology.

    The vault protects state across pod restarts.
    """

    persistence: str   # Storage class: "nvme", "ssd", "hdd"
    size: str          # Size: "10Gi", "100Gi"
    mount_path: str = "/data"

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "volumeMounts": [{
                                "name": "vault",
                                "mountPath": self.mount_path,
                            }],
                        }],
                        "volumes": [{
                            "name": "vault",
                            "persistentVolumeClaim": {
                                "claimName": "{{AGENT_NAME}}-vault",
                            },
                        }],
                    },
                },
            },
            "_pvc": {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": "{{AGENT_NAME}}-vault",
                },
                "spec": {
                    "accessModes": ["ReadWriteOnce"],
                    "storageClassName": self._storage_class(),
                    "resources": {
                        "requests": {"storage": self.size},
                    },
                },
            },
        }

    def _storage_class(self) -> str:
        return {
            "nvme": "fast-nvme",
            "ssd": "standard-ssd",
            "hdd": "slow-hdd",
        }.get(self.persistence, "standard")


def with_vault(persistence: str, size: str, mount_path: str = "/data") -> WithVault:
    """Factory function for vault morpheme."""
    return WithVault(persistence=persistence, size=size, mount_path=mount_path)
```

**Token Cost**: 100
**Use Case**: D-gent state persistence, M-gent memory storage

---

### with_secret(name, mount_path) - Secret Access

```python
@dataclass(frozen=True)
class WithSecret(Morpheme):
    """
    Mount a Kubernetes secret into the pod.

    Secrets provide secure access to credentials.
    """

    name: str          # Secret name
    mount_path: str    # Where to mount

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "volumeMounts": [{
                                "name": f"secret-{self.name}",
                                "mountPath": self.mount_path,
                                "readOnly": True,
                            }],
                        }],
                        "volumes": [{
                            "name": f"secret-{self.name}",
                            "secret": {
                                "secretName": self.name,
                            },
                        }],
                    },
                },
            },
        }


def with_secret(name: str, mount_path: str) -> WithSecret:
    """Factory function for secret morpheme."""
    return WithSecret(name=name, mount_path=mount_path)
```

**Token Cost**: 50
**Use Case**: API keys, database credentials, TLS certificates

---

## Network Morphemes

### with_membrane(allow_peers) - Network Isolation

```python
@dataclass(frozen=True)
class WithMembrane(Morpheme):
    """
    Configure network isolation via NetworkPolicy.

    The membrane controls what can enter and exit.
    Named for the cell membrane: selective permeability.
    """

    allow_peers: list[str]  # Agent genera that can communicate

    def to_k8s_patch(self) -> dict:
        return {
            "_network_policy": {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": "{{AGENT_NAME}}-membrane",
                },
                "spec": {
                    "podSelector": {
                        "matchLabels": {
                            "kgents.io/agent": "{{AGENT_NAME}}",
                        },
                    },
                    "policyTypes": ["Ingress", "Egress"],
                    "ingress": [{
                        "from": [
                            {"podSelector": {"matchLabels": {"kgents.io/genus": peer}}}
                            for peer in self.allow_peers
                        ],
                    }],
                    "egress": [{
                        "to": [
                            {"podSelector": {"matchLabels": {"kgents.io/genus": peer}}}
                            for peer in self.allow_peers
                        ],
                    }],
                },
            },
        }


def with_membrane(allow_peers: list[str]) -> WithMembrane:
    """Factory function for membrane morpheme."""
    return WithMembrane(allow_peers=allow_peers)
```

**Token Cost**: 50
**Use Case**: Security isolation, multi-tenant deployments

---

## Sidecar Morphemes

### with_sidecar(agent) - D-gent State Sidecar

```python
@dataclass(frozen=True)
class WithSidecar(Morpheme):
    """
    Add a sidecar container for state management.

    The D-gent sidecar provides persistent state with
    automatic synchronization.
    """

    agent: str  # Sidecar agent type: "d-gent", "o-gent"
    image: str = "kgents/d-gent-sidecar:latest"

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": "agent",
                                # Main container unchanged
                            },
                            {
                                "name": f"{self.agent}-sidecar",
                                "image": self.image,
                                "resources": {
                                    "requests": {"cpu": "50m", "memory": "64Mi"},
                                    "limits": {"cpu": "100m", "memory": "128Mi"},
                                },
                                "volumeMounts": [{
                                    "name": "shared-state",
                                    "mountPath": "/state",
                                }],
                            },
                        ],
                        "volumes": [{
                            "name": "shared-state",
                            "emptyDir": {},
                        }],
                    },
                },
            },
        }


def with_sidecar(agent: str, image: str | None = None) -> WithSidecar:
    """Factory function for sidecar morpheme."""
    return WithSidecar(
        agent=agent,
        image=image or f"kgents/{agent}-sidecar:latest"
    )
```

**Token Cost**: 150
**Use Case**: D-gent state persistence, O-gent metrics collection

---

## Health Morphemes

### with_probe(liveness, readiness) - Health Checks

```python
@dataclass(frozen=True)
class WithProbe(Morpheme):
    """
    Configure liveness and readiness probes.

    Probes let Kubernetes know if the agent is healthy.
    """

    liveness_path: str = "/health/live"
    readiness_path: str = "/health/ready"
    port: int = 8080
    initial_delay: int = 10
    period: int = 10

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "livenessProbe": {
                                "httpGet": {
                                    "path": self.liveness_path,
                                    "port": self.port,
                                },
                                "initialDelaySeconds": self.initial_delay,
                                "periodSeconds": self.period,
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": self.readiness_path,
                                    "port": self.port,
                                },
                                "initialDelaySeconds": self.initial_delay,
                                "periodSeconds": self.period,
                            },
                        }],
                    },
                },
            },
        }


def with_probe(
    liveness_path: str = "/health/live",
    readiness_path: str = "/health/ready",
    port: int = 8080,
) -> WithProbe:
    """Factory function for probe morpheme."""
    return WithProbe(
        liveness_path=liveness_path,
        readiness_path=readiness_path,
        port=port,
    )
```

**Token Cost**: 25
**Use Case**: Production deployments, auto-healing

---

## Scheduling Morphemes

### with_affinity(rules) - Scheduling Constraints

```python
@dataclass(frozen=True)
class WithAffinity(Morpheme):
    """
    Configure pod affinity/anti-affinity rules.

    Controls where pods can be scheduled.
    """

    prefer_same_node_as: list[str] | None = None
    avoid_same_node_as: list[str] | None = None
    require_node_label: dict[str, str] | None = None

    def to_k8s_patch(self) -> dict:
        affinity = {}

        if self.prefer_same_node_as:
            affinity["podAffinity"] = {
                "preferredDuringSchedulingIgnoredDuringExecution": [{
                    "weight": 100,
                    "podAffinityTerm": {
                        "labelSelector": {
                            "matchExpressions": [{
                                "key": "kgents.io/genus",
                                "operator": "In",
                                "values": self.prefer_same_node_as,
                            }],
                        },
                        "topologyKey": "kubernetes.io/hostname",
                    },
                }],
            }

        if self.avoid_same_node_as:
            affinity["podAntiAffinity"] = {
                "requiredDuringSchedulingIgnoredDuringExecution": [{
                    "labelSelector": {
                        "matchExpressions": [{
                            "key": "kgents.io/genus",
                            "operator": "In",
                            "values": self.avoid_same_node_as,
                        }],
                    },
                    "topologyKey": "kubernetes.io/hostname",
                }],
            }

        if self.require_node_label:
            affinity["nodeAffinity"] = {
                "requiredDuringSchedulingIgnoredDuringExecution": {
                    "nodeSelectorTerms": [{
                        "matchExpressions": [
                            {"key": k, "operator": "In", "values": [v]}
                            for k, v in self.require_node_label.items()
                        ],
                    }],
                },
            }

        return {
            "spec": {
                "template": {
                    "spec": {
                        "affinity": affinity,
                    },
                },
            },
        }


def with_affinity(
    prefer_same_node_as: list[str] | None = None,
    avoid_same_node_as: list[str] | None = None,
    require_node_label: dict[str, str] | None = None,
) -> WithAffinity:
    """Factory function for affinity morpheme."""
    return WithAffinity(
        prefer_same_node_as=prefer_same_node_as,
        avoid_same_node_as=avoid_same_node_as,
        require_node_label=require_node_label,
    )
```

**Token Cost**: 50
**Use Case**: Co-locating related agents, spreading for fault tolerance

---

## Environment Morphemes

### with_env(vars) - Environment Variables

```python
@dataclass(frozen=True)
class WithEnv(Morpheme):
    """
    Set environment variables in the container.
    """

    vars: dict[str, str]

    def to_k8s_patch(self) -> dict:
        return {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "agent",
                            "env": [
                                {"name": k, "value": v}
                                for k, v in self.vars.items()
                            ],
                        }],
                    },
                },
            },
        }


def with_env(vars: dict[str, str]) -> WithEnv:
    """Factory function for env morpheme."""
    return WithEnv(vars=vars)
```

**Token Cost**: 10
**Use Case**: Configuration, feature flags

---

## Composition Examples

### Minimal Agent

```python
morphology = Base()
# → Single pod, 100m CPU, 256Mi memory
# Cost: 100 tokens
```

### GPU-Enabled Agent

```python
morphology = Base() >> with_cortex("A100", vram="80GB")
# → Single pod with A100 GPU
# Cost: 1100 tokens
```

### High-Availability Agent

```python
morphology = (
    Base()
    >> with_ganglia(3)
    >> with_vault("ssd", "10Gi")
    >> with_probe()
)
# → 3 replicas, persistent storage, health checks
# Cost: 100 + 600 + 100 + 25 = 825 tokens
```

### Production Agent

```python
morphology = (
    Base()
    >> with_resources("1", "2Gi")
    >> with_ganglia(5)
    >> with_vault("nvme", "50Gi")
    >> with_membrane(["L", "F", "O"])
    >> with_sidecar("d-gent")
    >> with_probe()
    >> with_affinity(avoid_same_node_as=["B"])
)
# → Full production setup
# Cost: 100 + 50 + 1000 + 100 + 50 + 150 + 25 + 50 = 1525 tokens
```

---

## Creating Custom Morphemes

```python
@dataclass(frozen=True)
class WithCustomAnnotation(Morpheme):
    """
    Example custom morpheme.

    Follow the pattern:
    1. Inherit from Morpheme
    2. Define parameters as dataclass fields
    3. Implement to_k8s_patch()
    4. Provide factory function
    """

    key: str
    value: str

    def to_k8s_patch(self) -> dict:
        return {
            "metadata": {
                "annotations": {
                    self.key: self.value,
                },
            },
        }


def with_custom_annotation(key: str, value: str) -> WithCustomAnnotation:
    return WithCustomAnnotation(key=key, value=value)
```

---

## Token Cost Summary

| Morpheme | Cost | Justification |
|----------|------|---------------|
| `Base()` | 100 | Minimal pod creation |
| `with_cortex()` | 1000 | GPU is expensive |
| `with_ganglia(n)` | 200*n | Each replica costs |
| `with_resources()` | 50 | Config change only |
| `with_vault()` | 100 | Storage allocation |
| `with_secret()` | 50 | Config change only |
| `with_membrane()` | 50 | NetworkPolicy creation |
| `with_sidecar()` | 150 | Additional container |
| `with_probe()` | 25 | Config change only |
| `with_affinity()` | 50 | Config change only |
| `with_env()` | 10 | Config change only |

---

*"The body is composed of traits; traits compose into forms."*
