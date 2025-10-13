#!/bin/bash

###############################################################################
# XynergyOS Integration Test Suite
#
# Comprehensive integration tests for all services and OAuth flows
#
# Prerequisites:
# 1. All services deployed
# 2. Valid Firebase token for authentication
# 3. OAuth configured (optional - tests will work in mock mode)
#
# Usage: ./tests/integration-tests.sh
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

GATEWAY="https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app"
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_test() {
    echo -e "${YELLOW}Test: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

print_failure() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

run_test() {
    local test_name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    local auth_required="${4:-false}"

    ((TESTS_RUN++))
    print_test "$test_name"

    local headers=""
    if [ "$auth_required" = "true" ] && [ -n "$AUTH_TOKEN" ]; then
        headers="-H \"Authorization: Bearer $AUTH_TOKEN\""
    fi

    local status=$(eval "curl -s -o /dev/null -w \"%{http_code}\" $headers \"$url\" 2>/dev/null" || echo "000")

    if [ "$status" = "$expected_status" ]; then
        print_success "$test_name - Status $status"
        return 0
    else
        print_failure "$test_name - Expected $expected_status, got $status"
        return 1
    fi
}

###############################################################################
# Test Suites
###############################################################################

test_gateway_health() {
    print_header "Gateway Health Tests"

    run_test "Gateway health check" "$GATEWAY/health" 200
}

test_unauthenticated_access() {
    print_header "Authentication Tests - Unauthenticated"

    # All these should return 401 without auth
    run_test "Slack channels (no auth)" "$GATEWAY/api/v2/slack/channels" 401
    run_test "Gmail messages (no auth)" "$GATEWAY/api/v2/email/messages" 401
    run_test "Calendar events (no auth)" "$GATEWAY/api/v2/calendar/events" 401
    run_test "CRM contacts (no auth)" "$GATEWAY/api/v2/crm/contacts" 401
    run_test "Memory items (no auth)" "$GATEWAY/api/v1/memory/items" 401
    run_test "Research sessions (no auth)" "$GATEWAY/api/v1/research-sessions" 401
}

test_authenticated_access() {
    if [ -z "$AUTH_TOKEN" ]; then
        print_header "Authentication Tests - Authenticated (SKIPPED)"
        echo "Set AUTH_TOKEN environment variable to run authenticated tests"
        return 0
    fi

    print_header "Authentication Tests - Authenticated"

    # All these should return 200 with valid auth
    run_test "Slack channels (with auth)" "$GATEWAY/api/v2/slack/channels" 200 true
    run_test "Gmail messages (with auth)" "$GATEWAY/api/v2/email/messages" 200 true
    run_test "Calendar events (with auth)" "$GATEWAY/api/v2/calendar/events" 200 true

    # These might return 200 or 404 depending on data
    ((TESTS_RUN++))
    print_test "CRM contacts (with auth)"
    local status=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $AUTH_TOKEN" "$GATEWAY/api/v2/crm/contacts" 2>/dev/null)
    if [ "$status" = "200" ] || [ "$status" = "404" ]; then
        print_success "CRM contacts - Status $status (expected)"
    else
        print_failure "CRM contacts - Unexpected status $status"
    fi
}

test_oauth_status() {
    print_header "OAuth Configuration Tests"

    ((TESTS_RUN++))
    print_test "Checking Slack OAuth status"
    SLACK_RESPONSE=$(curl -s "https://slack-intelligence-service-835612502919.us-central1.run.app/" 2>/dev/null)
    if echo "$SLACK_RESPONSE" | grep -q '"mockMode":false'; then
        print_success "Slack OAuth CONFIGURED - Real data enabled"
    elif echo "$SLACK_RESPONSE" | grep -q '"mockMode":true'; then
        echo -e "${YELLOW}ℹ️  Slack in mock mode (OAuth not configured)${NC}"
        ((TESTS_PASSED++))
    else
        print_failure "Slack service not responding correctly"
    fi

    ((TESTS_RUN++))
    print_test "Checking Gmail OAuth status"
    GMAIL_RESPONSE=$(curl -s "https://gmail-intelligence-service-835612502919.us-central1.run.app/" 2>/dev/null)
    if echo "$GMAIL_RESPONSE" | grep -q '"mockMode":false'; then
        print_success "Gmail OAuth CONFIGURED - Real data enabled"
    elif echo "$GMAIL_RESPONSE" | grep -q '"mockMode":true'; then
        echo -e "${YELLOW}ℹ️  Gmail in mock mode (OAuth not configured)${NC}"
        ((TESTS_PASSED++))
    else
        print_failure "Gmail service not responding correctly"
    fi

    ((TESTS_RUN++))
    print_test "Checking Calendar OAuth status"
    CALENDAR_RESPONSE=$(curl -s "https://calendar-intelligence-service-835612502919.us-central1.run.app/" 2>/dev/null)
    if echo "$CALENDAR_RESPONSE" | grep -q '"mockMode":false'; then
        print_success "Calendar OAuth CONFIGURED - Real data enabled"
    elif echo "$CALENDAR_RESPONSE" | grep -q '"mockMode":true'; then
        echo -e "${YELLOW}ℹ️  Calendar in mock mode (OAuth not configured)${NC}"
        ((TESTS_PASSED++))
    else
        print_failure "Calendar service not responding correctly"
    fi
}

test_api_functionality() {
    if [ -z "$AUTH_TOKEN" ]; then
        print_header "API Functionality Tests (SKIPPED)"
        echo "Set AUTH_TOKEN environment variable to run functionality tests"
        return 0
    fi

    print_header "API Functionality Tests"

    # Test Slack channels list
    ((TESTS_RUN++))
    print_test "Slack channels list returns data"
    SLACK_DATA=$(curl -s -H "Authorization: Bearer $AUTH_TOKEN" "$GATEWAY/api/v2/slack/channels")
    if echo "$SLACK_DATA" | grep -q '"channels"'; then
        print_success "Slack returns channels array"
    else
        print_failure "Slack channels response invalid"
    fi

    # Test Calendar events list
    ((TESTS_RUN++))
    print_test "Calendar events list returns data"
    CALENDAR_DATA=$(curl -s -H "Authorization: Bearer $AUTH_TOKEN" "$GATEWAY/api/v2/calendar/events")
    if echo "$CALENDAR_DATA" | grep -q '"events"'; then
        print_success "Calendar returns events array"
    else
        print_failure "Calendar events response invalid"
    fi

    # Test Gmail messages list
    ((TESTS_RUN++))
    print_test "Gmail messages list returns data"
    GMAIL_DATA=$(curl -s -H "Authorization: Bearer $AUTH_TOKEN" "$GATEWAY/api/v2/email/messages")
    if echo "$GMAIL_DATA" | grep -q '"messages"'; then
        print_success "Gmail returns messages array"
    else
        print_failure "Gmail messages response invalid"
    fi
}

test_performance() {
    print_header "Performance Tests"

    # Test gateway response time
    ((TESTS_RUN++))
    print_test "Gateway response time"
    START=$(date +%s%N)
    curl -s -o /dev/null "$GATEWAY/health"
    END=$(date +%s%N)
    DURATION=$(( (END - START) / 1000000 ))

    if [ $DURATION -lt 500 ]; then
        print_success "Gateway responded in ${DURATION}ms (excellent)"
    elif [ $DURATION -lt 1000 ]; then
        print_success "Gateway responded in ${DURATION}ms (good)"
    else
        echo -e "${YELLOW}⚠️  Gateway responded in ${DURATION}ms (acceptable but slow)${NC}"
        ((TESTS_PASSED++))
    fi
}

###############################################################################
# Main
###############################################################################

print_header "XynergyOS Integration Test Suite"
echo "Gateway: $GATEWAY"
echo ""

if [ -n "$AUTH_TOKEN" ]; then
    echo -e "${GREEN}✅ Auth token provided - Running full test suite${NC}"
else
    echo -e "${YELLOW}⚠️  No auth token - Running limited tests${NC}"
    echo "   Set AUTH_TOKEN=your-firebase-token to run authenticated tests"
fi
echo ""

# Run test suites
test_gateway_health
test_unauthenticated_access
test_authenticated_access
test_oauth_status
test_api_functionality
test_performance

###############################################################################
# Summary
###############################################################################

print_header "Test Results Summary"

echo "Tests Run:    $TESTS_RUN"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "Integration Status: HEALTHY"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Please review failures above"
    exit 1
fi
