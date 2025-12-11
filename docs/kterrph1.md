# K-Terrarium Implementation Guide

**Status**: Phase 1 POC Complete | **Date**: 2025-12-10

This document details the implementation of K-Terrarium Phase 1, providing context for developers who want to understand, extend, or debug the Kubernetes infrastructure.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [File Structure](#2-file-structure)
3. [Core Components](#3-core-components)
4. [CLI Commands](#4-cli-commands)
5. [Docker Images](#5-docker-images)
6. [Kubernetes Manifests](#6-kubernetes-manifests)
7. [How It All Connects](#7-how-it-all-connects)
8. [Common Operations](#8-common-operations)
9. [Debugging Guide](#9-debugging-guide)
10. [Security Model](#10-security-model)
11. [Extending the System](#11-extending-the-system)
12. [Known Limitations](#12-known-limitations)

---

## 1. Architecture Overview

K-Terrarium transforms kgents from Python processes sharing a filesystem into a **Kubernetes-native agent ecosystem**. The key insight is that **isolation becomes physics, not policy**—container boundaries enforce what Python namespaces cannot.

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer's Machine                       │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Docker Desktop                          │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │         Kind Cluster: kgents-local            │  │   │
│  │  │                                               │  │   │
│  │  │  ┌─────────────────────────────────────────┐ │  │   │
│  │  │  │     Namespace: kgents-agents            │ │  │   │
│  │  │  │  ┌──────────────┐  ┌──────────────┐    │ │  │   │
│  │  │  │  │  ping-agent  │  │  (future     │    │ │  │   │
│  │  │  │  │  Pod         │  │   agents)    │    │ │  │   │
│  │  │  │  └──────────────┘  └──────────────┘    │ │  │   │
│  │  │  └─────────────────────────────────────────┘ │  │   │
│  │  │                                               │  │   │
│  │  │  ┌─────────────────────────────────────────┐ │  │   │
│  │  │  │     Namespace: kgents-ephemeral         │ │  │   │
│  │  │  │     (for Q-gent disposable jobs)        │ │  │   │
│  │  │  └─────────────────────────────────────────┘ │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ kgents CLI  │  │   kubectl   │  │    kind     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Why Kind?

| Tool | Pros | Cons | Our Choice |
|------|------|------|------------|
| **Kind** | Docker-only, fast startup (~45s), CI-friendly, ephemeral | No GPU passthrough | ✓ Local dev |
| Minikube | VM-based, more realistic | Heavy, slow startup | Too heavy |
| K3s | Lightweight, production-ready | Requires systemd | Better for edge |
| Docker Compose | Simple | No scheduling, no self-healing | Too limited |

---

## 2. File Structure

```
impl/
├── claude/
│   ├── infra/
│   │   └── k8s/
│   │       ├── __init__.py          # Public API exports
│   │       ├── exceptions.py        # TerrariumError hierarchy
│   │       ├── detection.py         # Environment detection
│   │       ├── cluster.py           # Kind cluster lifecycle
│   │       ├── manifests/
│   │       │   ├── namespace.yaml   # Namespaces + LimitRanges
│   │       │   ├── kind-config.yaml # Kind cluster config
│   │       │   └── ping-agent.yaml  # POC agent deployment
│   │       └── _tests/
│   │           ├── test_detection.py
│   │           └── test_cluster.py
│   │
│   └── protocols/
│       └── cli/
│           └── handlers/
│               └── infra.py         # CLI handler
│
└── images/
    ├── agent-base/
    │   └── Dockerfile               # Base image for agents
    └── ping-agent/
        ├── Dockerfile               # POC agent image
        └── ping_agent.py            # Simple HTTP server
```

---

## 3. Core Components

### 3.1 Exception Hierarchy (`exceptions.py`)

```python
TerrariumError                    # Base exception
├── KindNotFoundError            # Kind CLI not in PATH
├── DockerNotFoundError          # Docker not running
├── ClusterNotFoundError         # Expected cluster missing
├── ClusterOperationError        # Create/destroy failed
└── KubectlNotFoundError         # kubectl not in PATH
```

These exceptions enable **graceful degradation**. When K8s tooling is unavailable, the system falls back to bare-metal mode rather than crashing.

### 3.2 Environment Detection (`detection.py`)

The detection module answers: "What K8s capabilities are available right now?"

```python
from infra.k8s import detect_terrarium_mode

detection = detect_terrarium_mode()
print(detection.capability)      # NONE | KIND_AVAILABLE | CLUSTER_RUNNING
print(detection.docker_available) # True/False
print(detection.kind_path)       # /opt/homebrew/bin/kind or None
print(detection.can_create_cluster)  # True if Kind available
print(detection.has_running_cluster) # True if cluster exists
```

**Detection Order**:
1. Is Docker daemon running? (`docker info`)
2. Is Kind installed? (`which kind`)
3. Does our cluster exist? (`kind get clusters`)

### 3.3 Cluster Lifecycle (`cluster.py`)

The `KindCluster` class manages the full cluster lifecycle:

```python
from infra.k8s import KindCluster, ClusterConfig

# Custom config (optional)
config = ClusterConfig(
    name="kgents-local",           # Cluster name
    image="kindest/node:v1.29.0",  # K8s version
    wait_timeout=120,              # Seconds to wait for ready
    namespaces=["kgents-agents", "kgents-ephemeral"],
)

# With progress callback
def on_progress(msg: str):
    print(f"  {msg}")

cluster = KindCluster(config, on_progress=on_progress)

# Operations (all return ClusterResult)
result = cluster.create()   # Idempotent: succeeds if already exists
result = cluster.destroy()  # Idempotent: succeeds if already gone
result = cluster.pause()    # docker pause (preserves state)
result = cluster.unpause()  # docker unpause

status = cluster.status()   # RUNNING | PAUSED | STOPPED | NOT_FOUND
```

**Key Design Decisions**:

1. **Idempotency**: `create()` succeeds if cluster already exists. `destroy()` succeeds if cluster is already gone. This makes commands safe to retry.

2. **Progress Callbacks**: Long operations report progress via callbacks, enabling both CLI output and programmatic monitoring.

3. **Pause vs Destroy**: `pause()` uses `docker pause` to freeze the container without losing state. This is faster than destroy/recreate for development workflows.

---

## 4. CLI Commands

The CLI is implemented in `protocols/cli/handlers/infra.py` and registered in `hollow.py`.

### Command Reference

```bash
# Initialize cluster (creates if not exists)
kgents infra init
# Output:
# K-Terrarium Init
# ========================================
#   Creating cluster 'kgents-local'...
#   Applying base manifests...
#   Cluster ready in 43.2s

# Check status
kgents infra status
# Output:
# K-Terrarium Status
# ========================================
# Docker: available
# Kind:   /opt/homebrew/bin/kind
# Kubectl: /usr/local/bin/kubectl
#
# Cluster: kgents-local (RUNNING)
#
# Pods in kgents-agents:
# NAME                          READY   STATUS    RESTARTS   AGE
# ping-agent-687c8498c9-v5lqt   1/1     Running   0          5m

# Pause cluster (saves resources)
kgents infra stop

# Resume cluster
kgents infra start

# Destroy cluster (with confirmation)
kgents infra destroy
# Or skip confirmation:
kgents infra destroy --force

# Deploy the POC ping-agent
kgents infra deploy
```

### Handler Architecture

```python
def cmd_infra(args: list[str]) -> int:
    """Main entry point, dispatches to subcommands."""
    subcommand = args[0]
    handlers = {
        "init": _cmd_init,
        "status": _cmd_status,
        "stop": _cmd_stop,
        "start": _cmd_start,
        "destroy": _cmd_destroy,
        "deploy": _cmd_deploy,
    }
    return handlers[subcommand](args[1:])
```

Each subcommand is a separate function that:
1. Imports only what it needs (lazy loading)
2. Returns exit code (0 = success, 1 = failure)
3. Prints human-readable output

---

## 5. Docker Images

### 5.1 Base Image (`agent-base/Dockerfile`)

A minimal Python 3.12 image with common agent dependencies:

```dockerfile
FROM python:3.12-slim

# Non-root user for security
RUN groupadd -r kgents && useradd -r -g kgents kgents

# Common deps
RUN pip install --no-cache-dir aiohttp>=3.9.0 pydantic>=2.5.0

WORKDIR /app
USER kgents

CMD ["python", "-c", "print('override CMD in derived image')"]
```

### 5.2 Ping Agent (`ping-agent/`)

A minimal HTTP server for testing:

```python
# ping_agent.py (simplified)
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._send_response(200, {"status": "healthy"})
        elif self.path == "/ping":
            self._send_response(200, {
                "agent": "ping-agent",
                "hostname": socket.gethostname(),
                "pod_name": os.environ.get("POD_NAME"),
                "namespace": os.environ.get("POD_NAMESPACE"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

server = HTTPServer(("0.0.0.0", 8080), PingHandler)
server.serve_forever()
```

**Dockerfile notes**:

```dockerfile
# UID 1000 matches K8s runAsUser
RUN groupadd -g 1000 kgents && useradd -u 1000 -g kgents kgents

# Explicit ownership for security
COPY --chown=1000:1000 ping_agent.py /app/
RUN chmod 644 /app/ping_agent.py

USER 1000
```

The UID/GID must match the K8s `securityContext.runAsUser` or you'll get permission errors.

---

## 6. Kubernetes Manifests

### 6.1 Namespaces (`namespace.yaml`)

```yaml
# Two namespaces for separation of concerns
---
apiVersion: v1
kind: Namespace
metadata:
  name: kgents-agents
  labels:
    app.kubernetes.io/part-of: kgents
    kgents.io/tier: agents
---
apiVersion: v1
kind: Namespace
metadata:
  name: kgents-ephemeral
  labels:
    kgents.io/tier: ephemeral
```

**Why two namespaces?**
- `kgents-agents`: Long-running agent pods (B-gent, L-gent, etc.)
- `kgents-ephemeral`: Disposable jobs for Q-gent code execution

### 6.2 LimitRanges

```yaml
# Default limits for kgents-agents
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: kgents-agents
spec:
  limits:
    - default:
        cpu: "100m"
        memory: "256Mi"
      defaultRequest:
        cpu: "50m"
        memory: "128Mi"
      type: Container
```

LimitRanges ensure that **every container gets resource limits**, even if the manifest doesn't specify them. This prevents runaway processes from starving others.

### 6.3 Ping Agent Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ping-agent
  namespace: kgents-agents
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: ping-agent
          image: kgents/ping-agent:latest
          imagePullPolicy: Never  # Use local image
          ports:
            - containerPort: 8080
          env:
            # Downward API: inject pod metadata
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          # Health probes
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
```

**Key points**:
- `imagePullPolicy: Never` — Use the image we loaded into Kind
- Downward API injects pod name/namespace as environment variables
- Security context enforces non-root execution

---

## 7. How It All Connects

### Deployment Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    kgents infra deploy                        │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 1: docker build -t kgents/ping-agent:latest            │
│          impl/images/ping-agent/                             │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 2: kind load docker-image kgents/ping-agent:latest     │
│          --name kgents-local                                 │
│                                                              │
│  (Copies image from Docker daemon into Kind's containerd)    │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 3: kubectl apply -f manifests/ping-agent.yaml          │
│                                                              │
│  Kubernetes creates:                                         │
│  - Deployment → ReplicaSet → Pod                            │
│  - Service (ClusterIP)                                       │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Step 4: kubectl wait --for=condition=ready pod              │
│          -l app.kubernetes.io/name=ping-agent                │
│                                                              │
│  Waits for readinessProbe to pass                           │
└──────────────────────────────────────────────────────────────┘
```

### Why `kind load docker-image`?

Kind runs Kubernetes inside Docker containers. The K8s nodes use containerd, not Docker, as their container runtime. To use a locally-built image:

1. Build with Docker (on host)
2. Load into Kind's containerd (`kind load docker-image`)
3. Set `imagePullPolicy: Never` so K8s doesn't try to pull from a registry

---

## 8. Common Operations

### Check cluster status
```bash
kgents infra status
# or directly:
kubectl cluster-info --context kind-kgents-local
```

### View pod logs
```bash
kubectl logs -n kgents-agents deploy/ping-agent
kubectl logs -n kgents-agents deploy/ping-agent --follow
```

### Execute command in pod
```bash
kubectl exec -n kgents-agents deploy/ping-agent -- python -c "print('hello')"
```

### Interactive shell in pod
```bash
kubectl exec -it -n kgents-agents deploy/ping-agent -- /bin/sh
```

### Test the ping endpoint
```bash
kubectl exec -n kgents-agents deploy/ping-agent -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8080/ping').read().decode())"
```

### Port-forward for local access
```bash
kubectl port-forward -n kgents-agents svc/ping-agent 8080:80
# Then: curl http://localhost:8080/ping
```

### View all resources
```bash
kubectl get all -n kgents-agents
kubectl get all -n kgents-ephemeral
```

### Describe pod (debugging)
```bash
kubectl describe pod -n kgents-agents -l app.kubernetes.io/name=ping-agent
```

---

## 9. Debugging Guide

### Problem: Pod in CrashLoopBackOff

```bash
# Check logs
kubectl logs -n kgents-agents deploy/ping-agent

# Common causes:
# 1. Permission denied → UID mismatch (see Security section)
# 2. Module not found → Image build issue
# 3. Port already in use → Check other containers
```

### Problem: Pod stuck in ImagePullBackOff

```bash
# Check if image is loaded
docker images | grep ping-agent
kind load docker-image kgents/ping-agent:latest --name kgents-local

# Verify imagePullPolicy: Never in manifest
kubectl get deploy ping-agent -n kgents-agents -o yaml | grep imagePullPolicy
```

### Problem: Cluster won't start

```bash
# Check Docker
docker info

# Check Kind
kind get clusters

# Delete and recreate
kind delete cluster --name kgents-local
kgents infra init
```

### Problem: kubectl can't connect

```bash
# Check context
kubectl config current-context
# Should be: kind-kgents-local

# Switch context
kubectl config use-context kind-kgents-local

# Or specify explicitly
kubectl --context kind-kgents-local get pods
```

---

## 10. Security Model

### Container Security

```yaml
securityContext:
  runAsNonRoot: true      # Cannot run as root
  runAsUser: 1000         # Specific UID
  # Future additions:
  # readOnlyRootFilesystem: true
  # allowPrivilegeEscalation: false
  # capabilities:
  #   drop: ["ALL"]
```

### Resource Limits

LimitRanges ensure every container has limits:
- CPU: 100m default, prevents CPU starvation
- Memory: 256Mi default, prevents OOM on host

### Network Isolation (Future)

Phase 5 will add NetworkPolicies:
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

---

## 11. Extending the System

### Adding a New Agent

1. **Create Dockerfile** (`impl/images/my-agent/Dockerfile`):
```dockerfile
FROM python:3.12-slim
RUN groupadd -g 1000 kgents && useradd -u 1000 -g kgents kgents
WORKDIR /app
COPY --chown=1000:1000 my_agent.py /app/
USER 1000
CMD ["python", "my_agent.py"]
```

2. **Create manifest** (`infra/k8s/manifests/my-agent.yaml`):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-agent
  namespace: kgents-agents
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: my-agent
  template:
    metadata:
      labels:
        app.kubernetes.io/name: my-agent
    spec:
      containers:
        - name: my-agent
          image: kgents/my-agent:latest
          imagePullPolicy: Never
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
```

3. **Build and deploy**:
```bash
docker build -t kgents/my-agent:latest impl/images/my-agent/
kind load docker-image kgents/my-agent:latest --name kgents-local
kubectl apply -f impl/claude/infra/k8s/manifests/my-agent.yaml
```

### Adding a New CLI Subcommand

Edit `protocols/cli/handlers/infra.py`:

```python
def _cmd_mycommand(args: list[str]) -> int:
    """My new command."""
    print("Doing something...")
    return 0

# Add to handlers dict in cmd_infra()
handlers = {
    ...,
    "mycommand": _cmd_mycommand,
}
```

---

## 12. Known Limitations

### Phase 1 Limitations (POC)

1. **No GPU support**: Kind doesn't support GPU passthrough. F-gent (vision) must run locally.

2. **Single-node cluster**: Production would use multi-node for resilience.

3. **No persistent storage**: Pods use emptyDir. Data is lost on pod restart.

4. **No inter-agent communication**: Agents can't talk to each other yet. Service mesh is Phase 5.

5. **Manual image loading**: Every image change requires `kind load`. Phase 3 will automate this.

### Production Gaps

| Feature | POC | Production |
|---------|-----|------------|
| Cluster | Kind (local) | K3s, EKS, GKE |
| Storage | emptyDir | PVCs with storage class |
| Networking | Default CNI | Cilium with NetworkPolicy |
| Ingress | None | Nginx/Traefik Ingress |
| TLS | None | cert-manager + Let's Encrypt |
| Monitoring | kubectl logs | Prometheus + Grafana |
| Autoscaling | Manual replicas | HPA based on metrics |

---

## Next Steps

**Phase 2: Q-gent (Disposable Execution)**
- Create ephemeral Jobs for untrusted code
- TTL-based cleanup
- Result capture via pod logs

**Phase 3: Agent Operator**
- Custom Resource Definition (CRD) for agents
- Operator watches spec/ and reconciles deployments
- `kgents infra apply b-gent` from spec

**Phase 4: B-gent Economics Integration**
- ResourceQuotas as token budgets
- Kernel-enforced throttling
- Physics-based cost model

---

*"A universe in a bottle. Shake well before observing."*
