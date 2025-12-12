# Skill: Deploying an Agent to K8s

How to take an agent from code to running in the K-Terrarium cluster.

## Prerequisites

1. **Kind cluster running**: `kgents infra init && kgents infra status`
2. **CRDs installed**: `kgents infra crd`
3. **Agent has server wrapper** (FastAPI HTTP server)

## Deployment Matrix

| Agent | Status | Server | Dockerfile | Manifest |
|-------|--------|--------|------------|----------|
| U-gent | Ready | `agents/u/server.py` | `infra/k8s/images/ugent/` | `manifests/agents/ugent-*` |
| D-gent | Ready | `agents/d/server.py` | `infra/k8s/images/dgent/` | (sidecar only) |
| L-gent | Ready | `agents/l/server.py` | `agents/l/Dockerfile` | `manifests/l-gent-*` |
| Terrarium | Ready | `protocols/terrarium/server.py` | `protocols/terrarium/Dockerfile` | via CRD |
| Morpheus | Ready | `infra/morpheus/` | `infra/morpheus/Dockerfile` | via CRD |
| K-gent | NOT READY | Missing | Missing | Missing |
| W-gent | Partial | `agents/w/server.py` | Missing | Missing |

## The Three Components

Every deployable agent needs:

### 1. Server Wrapper (FastAPI)

```python
# agents/{letter}/server.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="{Letter}-gent Server")

class InvokeRequest(BaseModel):
    input: dict

class InvokeResponse(BaseModel):
    output: dict

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "{letter}-gent"}

@app.post("/invoke")
async def invoke(request: InvokeRequest) -> InvokeResponse:
    # Call your agent logic
    result = await agent.invoke(request.input)
    return InvokeResponse(output=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 2. Dockerfile

```dockerfile
# infra/k8s/images/{letter}gent/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r agent && useradd -r -g agent agent

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY impl/claude/agents/{letter}/ ./agents/{letter}/
COPY impl/claude/bootstrap/ ./bootstrap/

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
    CMD curl -f http://localhost:8080/health || exit 1

USER agent
EXPOSE 8080

CMD ["python", "-m", "agents.{letter}.server"]
```

### 3. K8s Manifest

```yaml
# infra/k8s/manifests/agents/{letter}gent-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {letter}gent
  namespace: kgents-agents
  labels:
    app.kubernetes.io/name: {letter}gent
    app.kubernetes.io/part-of: kgents
    kgents.io/genus: {LETTER}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {letter}gent
  template:
    metadata:
      labels:
        app: {letter}gent
        kgents.io/genus: {LETTER}
    spec:
      containers:
      - name: {letter}gent
        image: kgents/{letter}gent:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: {letter}gent
  namespace: kgents-agents
spec:
  selector:
    app: {letter}gent
  ports:
  - port: 8080
    targetPort: 8080
```

## Deployment Flow

```bash
# 1. Build image (from repo root)
docker build -t kgents/{letter}gent:latest \
  -f impl/claude/infra/k8s/images/{letter}gent/Dockerfile .

# 2. Load into Kind cluster
kind load docker-image kgents/{letter}gent:latest --name kgents-local

# 3. Apply manifest
kubectl apply -f impl/claude/infra/k8s/manifests/agents/{letter}gent-deployment.yaml

# 4. Verify
kubectl get pods -n kgents-agents -l app={letter}gent
kubectl logs -n kgents-agents deployment/{letter}gent
```

## Adding D-gent Sidecar (for stateful agents)

If your agent needs persistent state, add D-gent as a sidecar:

```yaml
spec:
  template:
    spec:
      containers:
      - name: {letter}gent
        # ... main container ...
        env:
        - name: DGENT_URL
          value: "http://localhost:8081"

      - name: dgent
        image: kgents/dgent:latest
        ports:
        - containerPort: 8081
        volumeMounts:
        - name: state
          mountPath: /data/state

      volumes:
      - name: state
        persistentVolumeClaim:
          claimName: {letter}gent-state
```

## Testing Deployment

```bash
# Port-forward to test locally
kubectl port-forward -n kgents-agents svc/{letter}gent 8080:8080

# Test health
curl http://localhost:8080/health

# Test invoke
curl -X POST http://localhost:8080/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": {"test": true}}'
```

## Observing via Terrarium

Once deployed with label `kgents.io/genus: {LETTER}`:

```bash
# Terrarium auto-discovers via label selector
kgents observe

# Or direct WebSocket
wscat -c ws://localhost:8080/observe/{letter}gent
```

## Common Issues

### Image not found in cluster
```bash
# Must load into Kind, not just build
kind load docker-image kgents/{letter}gent:latest --name kgents-local
```

### Health check failing
- Check container logs: `kubectl logs -n kgents-agents deployment/{letter}gent`
- Verify `/health` endpoint returns 200
- Increase `initialDelaySeconds` if agent needs warm-up

### No data in Terrarium TUI
- Verify agent has label `app.kubernetes.io/part-of: kgents`
- Check Terrarium gateway is running
- Check WebSocket connection to `ws://localhost:8080`

## Reference Implementations

- **U-gent**: Full example with D-gent sidecar, Morpheus integration
  - Server: `agents/u/server.py`
  - Dockerfile: `infra/k8s/images/ugent/Dockerfile`
  - Manifest: `manifests/agents/ugent-deployment.yaml`

- **D-gent**: Minimal stateful agent (used as sidecar)
  - Server: `agents/d/server.py`
  - Dockerfile: `infra/k8s/images/dgent/Dockerfile`

- **L-gent**: Agent with external dependency (PostgreSQL)
  - Server: `agents/l/server.py`
  - Dockerfile: `agents/l/Dockerfile`
  - Manifest: `manifests/l-gent-deployment.yaml`
