#!/bin/bash
#
# Test Docker API Endpoints
#

echo "══════════════════════════════════════════════════════════════════"
echo "🧪 Testing Docker API"
echo "══════════════════════════════════════════════════════════════════"
echo ""

API_URL="http://localhost:5000"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Test 1: Health Check
echo "Test 1: Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
HEALTH=$(curl -s $API_URL/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "$HEALTH" | jq '.'
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "$HEALTH"
fi
echo ""

# Test 2: API Info
echo "Test 2: API Info"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
INFO=$(curl -s $API_URL/)
if echo "$INFO" | grep -q "Housing Price Prediction"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "$INFO" | jq '.service, .version, .endpoints | keys'
else
    echo -e "${RED}❌ FAILED${NC}"
fi
echo ""

# Test 3: Single Prediction
echo "Test 3: Single Prediction"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PREDICTION=$(curl -s -X POST $API_URL/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "median_income": 8.3252,
    "housing_median_age": 41.0,
    "total_rooms": 880,
    "total_bedrooms": 129,
    "population": 322,
    "households": 126,
    "latitude": 37.88,
    "longitude": -122.23,
    "ocean_proximity": "NEAR BAY"
  }')

if echo "$PREDICTION" | grep -q "predicted_price"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "$PREDICTION" | jq '.'
    CACHED=$(echo "$PREDICTION" | jq -r '.cached')
    if [ "$CACHED" = "false" ]; then
        echo -e "${YELLOW}💾 Not cached (first request)${NC}"
    else
        echo -e "${GREEN}⚡ Cached response!${NC}"
    fi
else
    echo -e "${RED}❌ FAILED${NC}"
    echo "$PREDICTION"
fi
echo ""

# Test 4: Cache Test (Same request again)
echo "Test 4: Cache Test (should be faster)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CACHED_PREDICTION=$(curl -s -X POST $API_URL/predict \
  -H 'Content-Type: application/json' \
  -d '{
    "median_income": 8.3252,
    "housing_median_age": 41.0,
    "total_rooms": 880,
    "total_bedrooms": 129,
    "population": 322,
    "households": 126,
    "latitude": 37.88,
    "longitude": -122.23,
    "ocean_proximity": "NEAR BAY"
  }')

CACHED=$(echo "$CACHED_PREDICTION" | jq -r '.cached')
if [ "$CACHED" = "true" ]; then
    echo -e "${GREEN}✅ PASSED - Response cached!${NC}"
    echo "$CACHED_PREDICTION" | jq '.predicted_price_formatted, .cached'
else
    echo -e "${YELLOW}⚠️  Not cached (Redis might not be available)${NC}"
fi
echo ""

# Test 5: Model Info
echo "Test 5: Model Info"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
MODEL_INFO=$(curl -s $API_URL/model/info)
if echo "$MODEL_INFO" | grep -q "model_type"; then
    echo -e "${GREEN}✅ PASSED${NC}"
    echo "$MODEL_INFO" | jq '.model_type, .n_features'
else
    echo -e "${RED}❌ FAILED${NC}"
fi
echo ""

# Test 6: Cache Stats
echo "Test 6: Cache Statistics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CACHE_STATS=$(curl -s $API_URL/cache/stats)
if echo "$CACHE_STATS" | grep -q "connected"; then
    echo -e "${GREEN}✅ PASSED - Redis working!${NC}"
    echo "$CACHE_STATS" | jq '.'
else
    echo -e "${YELLOW}⚠️  Redis not available${NC}"
fi
echo ""

echo "══════════════════════════════════════════════════════════════════"
echo "🎉 Testing Complete!"
echo "══════════════════════════════════════════════════════════════════"