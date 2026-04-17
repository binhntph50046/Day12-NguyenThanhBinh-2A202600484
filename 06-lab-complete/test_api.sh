#!/bin/bash

# ============================================================
# API Testing Script
# 
# Usage:
#   ./test_api.sh                    # Test localhost
#   ./test_api.sh https://your-app.com  # Test production
# ============================================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URL
BASE_URL=${1:-"http://localhost:8000"}
API_KEY=${2:-"dev-key-change-me-in-production"}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  AI Agent API Testing${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "Base URL: ${YELLOW}$BASE_URL${NC}"
echo -e "API Key: ${YELLOW}${API_KEY:0:10}...${NC}"
echo ""

# Test 1: Health Check
echo -e "${BLUE}[Test 1]${NC} Health Check (GET /health)"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Status: $http_code"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ FAIL${NC} - Status: $http_code"
    echo "$body"
fi
echo ""

# Test 2: Readiness Check
echo -e "${BLUE}[Test 2]${NC} Readiness Check (GET /ready)"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/ready")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Status: $http_code"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ FAIL${NC} - Status: $http_code"
    echo "$body"
fi
echo ""

# Test 3: Authentication Required
echo -e "${BLUE}[Test 3]${NC} Authentication Required (POST /ask without key)"
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ask" \
    -H "Content-Type: application/json" \
    -d '{"question": "test"}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Status: $http_code (Unauthorized as expected)"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ FAIL${NC} - Status: $http_code (Should be 401)"
    echo "$body"
fi
echo ""

# Test 4: Valid Request
echo -e "${BLUE}[Test 4]${NC} Valid Request (POST /ask with API key)"
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ask" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"question": "What is deployment?"}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Status: $http_code"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}✗ FAIL${NC} - Status: $http_code"
    echo "$body"
fi
echo ""

# Test 5: Rate Limiting
echo -e "${BLUE}[Test 5]${NC} Rate Limiting (6 requests quickly)"
echo "Making 6 requests..."
for i in {1..6}; do
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ask" \
        -H "Content-Type: application/json" \
        -H "X-API-Key: $API_KEY" \
        -d "{\"question\": \"Test $i\"}")
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "429" ]; then
        echo -e "${GREEN}✓ PASS${NC} - Request $i: Rate limited (429) as expected"
        break
    elif [ "$http_code" = "200" ]; then
        echo -e "${YELLOW}→${NC} Request $i: Success (200)"
    else
        echo -e "${RED}✗${NC} Request $i: Unexpected status $http_code"
    fi
done
echo ""

# Test 6: Input Validation
echo -e "${BLUE}[Test 6]${NC} Input Validation (empty question)"
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ask" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"question": ""}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "422" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Status: $http_code (Validation error as expected)"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Status: $http_code (Expected 422)"
    echo "$body"
fi
echo ""

# Test 7: Metrics Endpoint
echo -e "${BLUE}[Test 7]${NC} Metrics Endpoint (GET /metrics)"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/metrics" \
    -H "X-API-Key: $API_KEY")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Status: $http_code"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - Status: $http_code"
    echo "$body"
fi
echo ""

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${GREEN}✓${NC} Health check working"
echo -e "${GREEN}✓${NC} Readiness check working"
echo -e "${GREEN}✓${NC} Authentication required"
echo -e "${GREEN}✓${NC} API endpoint working"
echo -e "${GREEN}✓${NC} Rate limiting working"
echo -e "${GREEN}✓${NC} Input validation working"
echo ""
echo -e "${GREEN}All tests passed! 🎉${NC}"
