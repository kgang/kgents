#!/bin/bash
# K8gents Operator Deployment Script
# Builds operator image and deploys to Kind cluster
#
# Usage: ./deploy-operators.sh
#
# AGENTESE: world.cluster.operators.define

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"
IMPL_DIR="$(dirname "$(dirname "$K8S_DIR")")"
ROOT_DIR="$(dirname "$(dirname "$IMPL_DIR")")"

CLUSTER_NAME="kgents-local"
NAMESPACE="kgents-agents"
IMAGE_NAME="kgents/operator"
IMAGE_TAG="latest"

echo "=== K8gents Operator Deployment ==="
echo ""

# Check prerequisites
echo "[1/5] Checking prerequisites..."

if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "ERROR: Cluster '$CLUSTER_NAME' not found"
    echo "Run: ./setup-cluster.sh"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    exit 1
fi

echo "Prerequisites OK"

# Build operator image
echo ""
echo "[2/5] Building operator image..."
cd "$ROOT_DIR"

docker build \
    -t "${IMAGE_NAME}:${IMAGE_TAG}" \
    -f impl/claude/infra/k8s/operators/Dockerfile \
    .

echo "Image built: ${IMAGE_NAME}:${IMAGE_TAG}"

# Load image into Kind
echo ""
echo "[3/5] Loading image into Kind cluster..."
kind load docker-image "${IMAGE_NAME}:${IMAGE_TAG}" --name "$CLUSTER_NAME"
echo "Image loaded into Kind"

# Deploy operators
echo ""
echo "[4/5] Deploying operators..."
kubectl config use-context "kind-${CLUSTER_NAME}"
kubectl apply -f "$K8S_DIR/manifests/operators-deployment.yaml"

# Wait for deployment
echo ""
echo "[5/5] Waiting for operator pod..."
kubectl rollout status deployment/kgents-operator -n "$NAMESPACE" --timeout=120s

echo ""
echo "=== Operator Deployment Complete ==="
echo ""
echo "Operator status:"
kubectl get pods -n "$NAMESPACE" -l app=kgents-operator
echo ""
echo "Operator logs:"
kubectl logs -l app=kgents-operator -n "$NAMESPACE" --tail=20
echo ""
echo "To test:"
echo "  # Create test agent"
echo "  kubectl apply -f - <<EOF"
echo "  apiVersion: kgents.io/v1"
echo "  kind: Agent"
echo "  metadata:"
echo "    name: test-agent"
echo "    namespace: kgents-agents"
echo "  spec:"
echo "    genus: T"
echo "    deployMode: PLACEHOLDER"
echo "  EOF"
echo ""
echo "  # Check reconciliation"
echo "  kubectl get agents -n kgents-agents"
echo "  kubectl get deployments -n kgents-agents"
