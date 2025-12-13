#!/bin/bash
# Database Triad Setup Script
#
# Deploys the complete Database Triad:
# - PostgreSQL (source of truth)
# - Qdrant (vector search)
# - Redis (cache)
# - Synapse CronJob (CDC processor)
#
# Usage: ./setup-triad.sh
#
# AGENTESE: self.vitals.triad.define

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")"
IMPL_DIR="$(dirname "$(dirname "$K8S_DIR")")"
MANIFESTS_DIR="$K8S_DIR/manifests/triad"

CLUSTER_NAME="kgents-triad"

echo "=== Database Triad Setup ==="
echo "Cluster: $CLUSTER_NAME"
echo "Manifests: $MANIFESTS_DIR"
echo ""

# Check prerequisites
echo "[1/7] Checking prerequisites..."

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
    echo "Install: brew install kind"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "ERROR: kubectl is not installed"
    exit 1
fi

echo "Prerequisites OK"

# Check if cluster exists
echo ""
echo "[2/7] Setting up Kind cluster..."

if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster '$CLUSTER_NAME' already exists"
    kubectl config use-context "kind-${CLUSTER_NAME}"
else
    echo "Creating Kind cluster..."

    # Check for kind config, use defaults if not present
    if [[ -f "$MANIFESTS_DIR/00-kind-config.yaml" ]]; then
        kind create cluster --name "$CLUSTER_NAME" --config "$MANIFESTS_DIR/00-kind-config.yaml"
    else
        kind create cluster --name "$CLUSTER_NAME"
    fi
fi

kubectl config use-context "kind-${CLUSTER_NAME}"

# Deploy namespace
echo ""
echo "[3/7] Creating namespace..."

kubectl apply -f "$MANIFESTS_DIR/00-namespace.yaml"

# Wait for namespace
kubectl wait --for=condition=ready=false ns/kgents-triad 2>/dev/null || true
sleep 2

# Deploy Postgres
echo ""
echo "[4/7] Deploying PostgreSQL (Durability layer)..."

kubectl apply -f "$MANIFESTS_DIR/01-postgres.yaml"
echo "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=triad-postgres -n kgents-triad --timeout=120s 2>/dev/null || \
    echo "PostgreSQL may still be starting..."

# Deploy Qdrant
echo ""
echo "[5/7] Deploying Qdrant (Resonance layer)..."

kubectl apply -f "$MANIFESTS_DIR/02-qdrant.yaml"
echo "Waiting for Qdrant to be ready..."
kubectl wait --for=condition=ready pod -l app=triad-qdrant -n kgents-triad --timeout=120s 2>/dev/null || \
    echo "Qdrant may still be starting..."

# Deploy Redis
echo ""
echo "[6/7] Deploying Redis (Reflex layer)..."

kubectl apply -f "$MANIFESTS_DIR/03-redis.yaml"
echo "Waiting for Redis to be ready..."
kubectl wait --for=condition=ready pod -l app=triad-redis -n kgents-triad --timeout=60s 2>/dev/null || \
    echo "Redis may still be starting..."

# Build and load Synapse image
echo ""
echo "[7/7] Building and deploying Synapse..."

echo "Building Synapse image..."
docker build -t kgents/synapse:latest \
    -f "$K8S_DIR/images/synapse/Dockerfile" \
    "$IMPL_DIR" 2>&1 | tail -5

echo "Loading image into Kind..."
kind load docker-image kgents/synapse:latest --name "$CLUSTER_NAME"

echo "Deploying Synapse CronJob..."
kubectl apply -f "$MANIFESTS_DIR/04-synapse.yaml"

# Verify
echo ""
echo "=== Verification ==="
echo ""
echo "Pods:"
kubectl get pods -n kgents-triad

echo ""
echo "Services:"
kubectl get svc -n kgents-triad

echo ""
echo "CronJobs:"
kubectl get cronjobs -n kgents-triad

echo ""
echo "=== Database Triad Setup Complete ==="
echo ""
echo "Semantic Layers:"
echo "  - Durability (Postgres): triad-postgres:5432"
echo "  - Resonance (Qdrant):    triad-qdrant:6333"
echo "  - Reflex (Redis):        triad-redis:6379"
echo "  - Synapse (CDC):         CronJob every minute"
echo ""
echo "Next steps:"
echo "  1. Verify: ./verify-triad.sh"
echo "  2. Logs:   kubectl logs -n kgents-triad -l app=triad-postgres"
echo "  3. Tear down: ./teardown-triad.sh"
echo ""
