#!/usr/bin/env bash
#
# Battle Test for kg probe command
#
# Tests:
# 1. Health probes (all Crown Jewels)
# 2. Identity law probe
# 3. Associativity law probe
# 4. Coherence probe
# 5. Edge cases (invalid inputs, timeouts)
# 6. JSON output
#
# Exit code: 0 if all tests pass, 1 otherwise

set -e

echo "====================================================="
echo "Battle Testing kg probe command"
echo "====================================================="
echo ""

FAILED=0

# Test 1: Health probe - all components
echo "[1/12] Testing health probe --all..."
if uv run kg probe health --all >/dev/null 2>&1; then
    echo "✓ Health probe --all passed"
else
    echo "✗ Health probe --all failed"
    FAILED=1
fi
echo ""

# Test 2: Health probe - specific jewel (brain)
echo "[2/12] Testing health probe --jewel brain..."
if uv run kg probe health --jewel brain >/dev/null 2>&1; then
    echo "✓ Health probe brain passed"
else
    echo "✗ Health probe brain failed"
    FAILED=1
fi
echo ""

# Test 3: Health probe - specific jewel (witness)
echo "[3/12] Testing health probe --jewel witness..."
if uv run kg probe health --jewel witness >/dev/null 2>&1; then
    echo "✓ Health probe witness passed"
else
    echo "✗ Health probe witness failed"
    FAILED=1
fi
echo ""

# Test 4: Health probe - specific jewel (llm)
echo "[4/12] Testing health probe --jewel llm..."
if uv run kg probe health --jewel llm >/dev/null 2>&1; then
    echo "✓ Health probe llm passed"
else
    echo "✗ Health probe llm failed"
    FAILED=1
fi
echo ""

# Test 5: Health probe with JSON output
echo "[5/12] Testing health probe with --json..."
# Filter out log lines and ANSI codes to get clean JSON
if uv run kg probe health --all --json 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -v "^\[kgents\]" | grep -v "^2025" | grep -v "^Warning" | jq . >/dev/null 2>&1; then
    echo "✓ Health probe JSON output is valid"
else
    echo "✗ Health probe JSON output is invalid"
    FAILED=1
fi
echo ""

# Test 6: Identity law probe
echo "[6/12] Testing identity law probe..."
if uv run kg probe identity >/dev/null 2>&1; then
    echo "✓ Identity law probe passed"
else
    echo "✗ Identity law probe failed"
    FAILED=1
fi
echo ""

# Test 7: Identity law probe with JSON
echo "[7/12] Testing identity probe with --json..."
# Filter out log lines and ANSI codes to get clean JSON
if uv run kg probe identity --json 2>&1 | sed 's/\x1b\[[0-9;]*m//g' | grep -v "^\[kgents\]" | grep -v "^2025" | grep -v "^Warning" | jq . >/dev/null 2>&1; then
    echo "✓ Identity probe JSON output is valid"
else
    echo "✗ Identity probe JSON output is invalid"
    FAILED=1
fi
echo ""

# Test 8: Associativity law probe
echo "[8/12] Testing associativity law probe..."
if uv run kg probe associativity >/dev/null 2>&1; then
    echo "✓ Associativity law probe passed"
else
    echo "✗ Associativity law probe failed"
    FAILED=1
fi
echo ""

# Test 9: Coherence probe
echo "[9/12] Testing coherence probe..."
if uv run kg probe coherence >/dev/null 2>&1; then
    echo "✓ Coherence probe passed"
else
    echo "✗ Coherence probe failed"
    FAILED=1
fi
echo ""

# Test 10: Edge case - invalid jewel name
echo "[10/12] Testing edge case: invalid jewel name..."
if ! uv run kg probe health --jewel nonexistent >/dev/null 2>&1; then
    echo "✓ Invalid jewel name correctly rejected"
else
    echo "✗ Invalid jewel name should have failed"
    FAILED=1
fi
echo ""

# Test 11: Edge case - help output
echo "[11/12] Testing help output..."
if uv run kg probe --help >/dev/null 2>&1; then
    echo "✓ Help output works"
else
    echo "✗ Help output failed"
    FAILED=1
fi
echo ""

# Test 12: Edge case - unknown probe type
echo "[12/12] Testing edge case: unknown probe type..."
if ! uv run kg probe unknown_type >/dev/null 2>&1; then
    echo "✓ Unknown probe type correctly rejected"
else
    echo "✗ Unknown probe type should have failed"
    FAILED=1
fi
echo ""

echo "====================================================="
if [ $FAILED -eq 0 ]; then
    echo "All tests passed! ✓"
    exit 0
else
    echo "Some tests failed. ✗"
    exit 1
fi
