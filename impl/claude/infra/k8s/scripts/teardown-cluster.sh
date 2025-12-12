#!/bin/bash
# K8gents Cluster Teardown Script
# Deletes Kind cluster and all associated resources
#
# Usage: ./teardown-cluster.sh [--force]
#
# AGENTESE: world.cluster.delete

CLUSTER_NAME="kgents-local"

echo "=== K8gents Cluster Teardown ==="
echo ""

# Check if cluster exists
if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster '$CLUSTER_NAME' does not exist"
    exit 0
fi

# Confirm unless --force
if [ "$1" != "--force" ]; then
    echo "WARNING: This will delete cluster '$CLUSTER_NAME' and all data"
    echo ""
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 0
    fi
fi

# Delete cluster
echo ""
echo "Deleting cluster '$CLUSTER_NAME'..."
kind delete cluster --name "$CLUSTER_NAME"

echo ""
echo "=== Teardown Complete ==="
echo ""
echo "To recreate: ./setup-cluster.sh"
