#!/bin/bash

# ============================================================
# Run All Tests Script
# 
# Chạy tất cả tests cho Production AI Agent
# 
# Usage:
#   ./RUN_ALL_TESTS.sh                    # Test local
#   ./RUN_ALL_TESTS.sh https://prod-url   # Test production
# ============================================================

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;96m'
NC='\033[0m' # No Color

# Configuration
BASE_URL=${1:-"http://localhost:8000"}
API_KEY=${2:-"dev-key-change-me-in-production"}

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  RUN ALL TESTS${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "Base URL: ${YELLOW}$BASE_URL${NC}"
echo -e "API Key: ${YELLOW}${API_KEY:0:10}...${NC}"
echo ""

# Check if agent is running
echo -e "${CYAN}[1/5] Checking if agent is running...${NC}"
if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Agent is running"
else
    echo -e "${RED}✗${NC} Agent is not running!"
    echo ""
    echo -e "${YELLOW}Please start the agent first:${NC}"
    echo -e "  docker compose up -d"
    echo ""
    exit 1
fi

# Install dependencies
echo ""
echo -e "${CYAN}[2/5] Installing test dependencies...${NC}"
pip install -q requests redis 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} Could not install dependencies (may already be installed)"
fi

# Run main test suite
echo ""
echo -e "${CYAN}[3/5] Running main test suite...${NC}"
echo ""
python tests/test_agent.py --url "$BASE_URL" --api-key "$API_KEY"
TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓${NC} Main test suite passed!"
else
    echo ""
    echo -e "${RED}✗${NC} Main test suite failed!"
    echo ""
    echo -e "${YELLOW}Check logs:${NC}"
    echo -e "  docker compose logs agent"
    echo ""
    exit 1
fi

# Run production readiness check
echo ""
echo -e "${CYAN}[4/5] Running production readiness check...${NC}"
echo ""
python check_production_ready.py --url "$BASE_URL"
READY_EXIT_CODE=$?

if [ $READY_EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓${NC} Production readiness check passed!"
else
    echo ""
    echo -e "${YELLOW}⚠${NC} Production readiness check has warnings"
fi

# Test API with curl
echo ""
echo -e "${CYAN}[5/5] Testing API with curl...${NC}"
echo ""

# Health check
echo -e "${CYAN}Testing /health...${NC}"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

if [ "$HEALTH_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} Health check: 200 OK"
else
    echo -e "${RED}✗${NC} Health check: $HEALTH_CODE"
fi

# API request
echo ""
echo -e "${CYAN}Testing /ask...${NC}"
ASK_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/ask" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"question": "Test from script"}')
ASK_CODE=$(echo "$ASK_RESPONSE" | tail -n1)
ASK_BODY=$(echo "$ASK_RESPONSE" | head -n-1)

if [ "$ASK_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} API request: 200 OK"
    echo "$ASK_BODY" | jq '.' 2>/dev/null || echo "$ASK_BODY"
else
    echo -e "${RED}✗${NC} API request: $ASK_CODE"
fi

# Summary
echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  TEST SUMMARY${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

if [ $TEST_EXIT_CODE -eq 0 ] && [ "$HEALTH_CODE" = "200" ] && [ "$ASK_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} All tests passed!"
    echo -e "${GREEN}✓${NC} Agent is production ready!"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "  1. Deploy to Railway: railway up"
    echo -e "  2. Deploy to Render: git push origin main"
    echo -e "  3. Test production URL"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠${NC} Some tests failed or have warnings"
    echo ""
    echo -e "${CYAN}Troubleshooting:${NC}"
    echo -e "  1. Check logs: docker compose logs agent"
    echo -e "  2. Restart agent: docker compose restart agent"
    echo -e "  3. Check Redis: docker compose ps redis"
    echo -e "  4. Review test output above"
    echo ""
    exit 1
fi
