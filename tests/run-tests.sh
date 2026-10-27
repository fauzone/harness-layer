#!/usr/bin/env bash
# Harness Layer Conformance Check Test Suite
# Runs check tool against minimal-workspace (expect PASS) and broken-workspace (expect FAIL)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
CHECK_TOOL="$REPO_ROOT/tools/harness-layer-check.py"
MINIMAL_WS="$REPO_ROOT/examples/minimal-workspace"
BROKEN_WS="$REPO_ROOT/examples/broken-workspace"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

run_check() {
    local workspace="$1"
    local expected_exit="$2"
    local description="$3"
    
    echo "=== Testing: $description ==="
    echo "Workspace: $workspace"
    echo "Expected exit: $expected_exit"
    echo ""
    
    python3 "$CHECK_TOOL" "$workspace"
    local actual_exit=$?
    
    echo ""
    echo "Actual exit code: $actual_exit"
    
    if [[ $actual_exit -eq $expected_exit ]]; then
        echo -e "${GREEN}✓ Exit code matches expected${NC}"
        return 0
    else
        echo -e "${RED}✗ Exit code mismatch: expected $expected_exit, got $actual_exit${NC}"
        return 1
    fi
}

check_fail_contains() {
    local workspace="$1"
    local pattern="$2"
    local description="$3"
    
    echo "=== Checking output for: $description ==="
    
    # Capture output
    output=$(python3 "$CHECK_TOOL" "$workspace" 2>&1)
    exit_code=$?
    
    echo "$output"
    echo ""
    
    if echo "$output" | grep -q "$pattern"; then
        echo -e "${GREEN}✓ Output contains expected pattern: $pattern${NC}"
        return 0
    else
        echo -e "${RED}✗ Output missing expected pattern: $pattern${NC}"
        return 1
    fi
}

main() {
    echo "Harness Layer Check Tool - Test Suite"
    echo "======================================"
    echo ""
    
    local all_passed=1
    
    # Test 1: minimal-workspace should pass (exit 0)
    if ! run_check "$MINIMAL_WS" 0 "minimal-workspace (conformant)"; then
        all_passed=0
    fi
    echo ""
    
    # Test 2: broken-workspace should fail (exit 1)
    if ! run_check "$BROKEN_WS" 1 "broken-workspace (non-conformant)"; then
        all_passed=0
    fi
    echo ""
    
    # Test 3: broken-workspace output should contain FAIL for IDENTITY
    if ! check_fail_contains "$BROKEN_WS" "FAIL.*L0-FILES.*IDENTITY" "FAIL for missing IDENTITY.md"; then
        all_passed=0
    fi
    echo ""
    
    # Test 4: broken-workspace output should contain FAIL for STATE lines > 15
    if ! check_fail_contains "$BROKEN_WS" "FAIL.*L3-STATE.*26 lines" "FAIL for STATE.md > 15 lines"; then
        all_passed=0
    fi
    echo ""
    
    # Test 5: broken-workspace output should contain FAIL for missing memory/ folder
    if ! check_fail_contains "$BROKEN_WS" "FAIL.*L2-FILES.*memory.*missing" "FAIL for missing memory/ folder"; then
        all_passed=0
    fi
    echo ""
    
    # Summary
    echo "======================================"
    if [[ $all_passed -eq 1 ]]; then
        echo -e "${GREEN}TESTS PASSED${NC}"
        exit 0
    else
        echo -e "${RED}TESTS FAILED${NC}"
        exit 1
    fi
}

main "$@"
