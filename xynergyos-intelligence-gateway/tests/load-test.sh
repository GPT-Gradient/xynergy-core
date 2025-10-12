#!/bin/bash
# Load Testing Script for Intelligence Gateway
# Requires: apache2-utils (ab), curl

GATEWAY_URL="${GATEWAY_URL:-https://xynergyos-intelligence-gateway-835612502919.us-central1.run.app}"

echo "====================================="
echo "Intelligence Gateway Load Testing"
echo "====================================="
echo "Gateway URL: $GATEWAY_URL"
echo ""

# Test 1: Health Endpoint (Lightweight)
echo "Test 1: Health Endpoint"
echo "------------------------"
echo "1000 requests, 10 concurrent"
ab -n 1000 -c 10 -q "$GATEWAY_URL/health"
echo ""

# Test 2: Deep Health Check (Moderate)
echo "Test 2: Deep Health Check"
echo "-------------------------"
echo "500 requests, 5 concurrent"
ab -n 500 -c 5 -q "$GATEWAY_URL/health/deep"
echo ""

# Test 3: Rate Limiting Test
echo "Test 3: Rate Limiting"
echo "---------------------"
echo "Rapid-fire 150 requests (should hit limit at 100)"
for i in {1..150}; do
  curl -s -o /dev/null -w "%{http_code} " "$GATEWAY_URL/health"
  if [ $((i % 10)) -eq 0 ]; then
    echo ""
  fi
done
echo ""
echo ""

# Test 4: Concurrent Connections
echo "Test 4: Concurrent Connections"
echo "-------------------------------"
echo "200 requests, 20 concurrent (max scaling test)"
ab -n 200 -c 20 -q "$GATEWAY_URL/health"
echo ""

# Test 5: Sustained Load
echo "Test 5: Sustained Load"
echo "----------------------"
echo "2000 requests, 15 concurrent, over ~30 seconds"
ab -n 2000 -c 15 -q "$GATEWAY_URL/health"
echo ""

echo "====================================="
echo "Load Testing Complete"
echo "====================================="
echo ""
echo "Check metrics at: $GATEWAY_URL/api/v1/metrics"
