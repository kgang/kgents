#!/usr/bin/env bash
# =============================================================================
# wait-for-health.sh - Health Check with Exponential Backoff
# =============================================================================
#
# Waits for a health endpoint to return 200 OK before proceeding.
# Uses exponential backoff (1s, 2s, 4s, 8s, 16s) to avoid hammering.
#
# Usage:
#   ./wait-for-health.sh [URL] [MAX_ATTEMPTS]
#
# Examples:
#   ./wait-for-health.sh                                    # Default: localhost:8000/health, 5 attempts
#   ./wait-for-health.sh http://localhost:8000/health 5     # Explicit
#   ./wait-for-health.sh http://localhost:3000/api/health 3 # Frontend health
#
# Exit codes:
#   0 - Health check passed
#   1 - Health check failed after all attempts
#
# =============================================================================

set -e

URL="${1:-http://localhost:8000/health}"
MAX_ATTEMPTS="${2:-5}"

echo "Waiting for $URL to become healthy (max $MAX_ATTEMPTS attempts)..."

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  # Calculate exponential backoff wait time: 2^(i-1) = 1, 2, 4, 8, 16...
  WAIT=$((2 ** (i - 1)))

  # Try the health check
  if curl -sf "$URL" > /dev/null 2>&1; then
    echo "Health check passed after $i attempt(s)"
    exit 0
  fi

  # Not ready yet
  if [ "$i" -lt "$MAX_ATTEMPTS" ]; then
    echo "Attempt $i/$MAX_ATTEMPTS: not ready, waiting ${WAIT}s..."
    sleep "$WAIT"
  fi
done

# Failed after all attempts
echo "Health check failed after $MAX_ATTEMPTS attempts"
echo ""
echo "Debug output from final attempt:"
curl -v "$URL" 2>&1 || true
exit 1
