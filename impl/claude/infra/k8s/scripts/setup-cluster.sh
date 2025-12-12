#!/bin/bash
# K8gents Cluster Setup Script
# Creates Kind cluster and deploys all CRDs
#
# Usage: ./setup-cluster.sh
#
# AGENTESE: world.cluster.define

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"
IMPL_DIR="$(dirname "$(dirname "$K8S_DIR")")"

CLUSTER_NAME="kgents-local"
NAMESPACE="kgents-agents"

echo "=== K8gents Cluster Setup ==="
echo "Cluster: $CLUSTER_NAME"
echo "Namespace: $NAMESPACE"
echo ""

# Check prerequisites
echo "[1/5] Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "ERROR: Docker daemon is not running"
    exit 1
fi

if ! command -v kind &> /dev/null; then
    echo "ERROR: Kind is not installed"
    echo "Install: brew install kind (macOS) or https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed"
    exit 1
fi

echo "Prerequisites OK"

# Check if cluster already exists
echo ""
echo "[2/5] Checking for existing cluster..."

if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster '$CLUSTER_NAME' already exists"
    read -p "Delete and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Deleting existing cluster..."
        kind delete cluster --name "$CLUSTER_NAME"
    else
        echo "Using existing cluster"
        kubectl config use-context "kind-${CLUSTER_NAME}"
    fi
fi

# Create cluster if it doesn't exist
if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo ""
    echo "[3/5] Creating Kind cluster..."
    kind create cluster --config "$K8S_DIR/manifests/kind-config.yaml"
fi

# Set context
kubectl config use-context "kind-${CLUSTER_NAME}"

# Create namespace
echo ""
echo "[4/5] Creating namespace and CRDs..."

kubectl apply -f "$K8S_DIR/manifests/namespace.yaml"

# Deploy CRDs
echo "Deploying Agent CRD..."
kubectl apply -f "$K8S_DIR/crds/agent-crd.yaml"

echo "Deploying Pheromone CRD..."
kubectl apply -f "$K8S_DIR/crds/pheromone-crd.yaml"

echo "Deploying Memory CRD..."
kubectl apply -f "$K8S_DIR/crds/memory-crd.yaml"

echo "Deploying Umwelt CRD..."
kubectl apply -f "$K8S_DIR/crds/umwelt-crd.yaml"

echo "Deploying Proposal CRD..."
kubectl apply -f "$K8S_DIR/crds/proposal-crd.yaml"

# Verify
echo ""
echo "[5/5] Verifying setup..."

echo ""
echo "Cluster Info:"
kubectl cluster-info --context "kind-${CLUSTER_NAME}"

echo ""
echo "Namespace:"
kubectl get ns "$NAMESPACE"

echo ""
echo "CRDs:"
kubectl get crds | grep kgents || echo "WARNING: No kgents CRDs found"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Deploy operators: ./deploy-operators.sh"
echo "  2. Verify cluster:   ./verify-cluster.sh"
echo "  3. Deploy L-gent:    ./deploy-lgent.sh"
echo ""
echo "To access the cluster:"
echo "  kubectl config use-context kind-${CLUSTER_NAME}"
