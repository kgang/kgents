#!/bin/bash
# K8gents L-gent Deployment Script
# Builds L-gent image and deploys to Kind cluster
#
# Usage: ./deploy-lgent.sh [--skip-build]
#
# Options:
#   --skip-build    Skip Docker build, use existing image
#
# AGENTESE: world.library.deploy

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"
IMPL_DIR="$(dirname "$(dirname "$K8S_DIR")")"
ROOT_DIR="$(dirname "$(dirname "$IMPL_DIR")")"

CLUSTER_NAME="kgents-local"
NAMESPACE="kgents-agents"
IMAGE_NAME="kgents/l-gent"
IMAGE_TAG="latest"
SKIP_BUILD=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=== K8gents L-gent Deployment ==="
echo ""

# Check prerequisites
echo "[1/6] Checking prerequisites..."

if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "ERROR: Cluster '$CLUSTER_NAME' not found"
    echo "Run: ./setup-cluster.sh"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    exit 1
fi

# Check PostgreSQL is running
if ! kubectl get pod l-gent-postgres-0 -n "$NAMESPACE" --no-headers 2>/dev/null | grep -q "Running"; then
    echo "WARNING: PostgreSQL pod not running"
    echo "L-gent will start in standalone mode without database"
fi

echo "Prerequisites OK"

# Build L-gent image
if [ "$SKIP_BUILD" = false ]; then
    echo ""
    echo "[2/6] Building L-gent image..."
    cd "$ROOT_DIR"

    docker build \
        -t "${IMAGE_NAME}:${IMAGE_TAG}" \
        -f impl/claude/agents/l/Dockerfile \
        .

    echo "Image built: ${IMAGE_NAME}:${IMAGE_TAG}"
else
    echo ""
    echo "[2/6] Skipping build (--skip-build)"
fi

# Load image into Kind
echo ""
echo "[3/6] Loading image into Kind cluster..."
kind load docker-image "${IMAGE_NAME}:${IMAGE_TAG}" --name "$CLUSTER_NAME"
echo "Image loaded into Kind"

# Update deployment to use real image
echo ""
echo "[4/6] Updating L-gent deployment..."
kubectl config use-context "kind-${CLUSTER_NAME}"

# Patch deployment to use real image and command
kubectl patch deployment l-gent -n "$NAMESPACE" --type='json' -p='[
  {"op": "replace", "path": "/spec/template/spec/containers/0/image", "value": "'"${IMAGE_NAME}:${IMAGE_TAG}"'"},
  {"op": "replace", "path": "/spec/template/spec/containers/0/command", "value": ["python", "-m", "agents.l.server"]}
]' 2>/dev/null || {
    echo "Deployment patch failed, applying full manifest..."
    kubectl apply -f "$K8S_DIR/manifests/l-gent-deployment.yaml"
}

# Force pod restart to pick up new image
echo ""
echo "[5/6] Restarting L-gent pod..."
kubectl delete pod -l app=l-gent -n "$NAMESPACE" --wait=false 2>/dev/null || true

# Wait for deployment
echo ""
echo "[6/6] Waiting for L-gent pod..."
kubectl rollout status deployment/l-gent -n "$NAMESPACE" --timeout=120s

echo ""
echo "=== L-gent Deployment Complete ==="
echo ""
echo "L-gent status:"
kubectl get pods -n "$NAMESPACE" -l app=l-gent
echo ""
echo "L-gent logs:"
kubectl logs -l app=l-gent -n "$NAMESPACE" --tail=20 2>/dev/null || echo "(waiting for logs...)"
echo ""
echo "To test:"
echo "  # Port forward"
echo "  kubectl port-forward svc/l-gent -n kgents-agents 8080:8080"
echo ""
echo "  # Health check"
echo "  curl http://localhost:8080/health"
echo ""
echo "  # Readiness check"
echo "  curl http://localhost:8080/ready"
echo ""
echo "  # List catalog"
echo "  curl http://localhost:8080/catalog"
echo ""
echo "  # Search"
echo "  curl -X POST http://localhost:8080/search -d '{\"query\": \"test\"}'"
