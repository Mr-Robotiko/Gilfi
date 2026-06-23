#!/bin/bash

# Infrastructure Tests Runner
# Runs all infrastructure tests for Gilfi backend

set -e

echo "=========================================="
echo "   Gilfi Infrastructure Tests"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend is running"
    BACKEND_RUNNING=true
else
    echo -e "${YELLOW}⚠${NC} Backend is not running"
    echo "Starting backend container..."
    
    cd ../..
    if [ -f "backend-docker.sh" ]; then
        ./backend-docker.sh start
    else
        docker compose -f docker-compose.backend.yaml up -d
    fi
    
    echo "Waiting for backend to be ready..."
    sleep 10
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend started successfully"
        BACKEND_RUNNING=true
        BACKEND_STARTED_BY_SCRIPT=true
    else
        echo -e "${RED}✗${NC} Failed to start backend"
        BACKEND_RUNNING=false
    fi
    
    cd tests/infrastructure
fi

echo ""
echo "=========================================="
echo "   Running Tests"
echo "=========================================="
echo ""

# Detect Python interpreter
# Priority: conda environment > venv > system python3
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    # Already in a conda environment, use python from it
    PYTHON_CMD="python"
    echo "Using conda environment: $CONDA_DEFAULT_ENV"
elif [ -d "../../venv" ]; then
    # Activate virtual environment if it exists
    source ../../venv/bin/activate
    PYTHON_CMD="python"
    echo "Using virtual environment"
else
    # Fall back to system python3
    PYTHON_CMD="python3"
    echo "Using system Python"
fi

# Run tests
TEST_FAILED=false

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project root for tests (they expect to run from there)
cd "$PROJECT_ROOT"

echo "1. Testing Docker Backend..."
if $PYTHON_CMD -m pytest tests/infrastructure/test_docker_backend.py -v; then
    echo -e "${GREEN}✓${NC} Docker backend tests passed"
else
    echo -e "${RED}✗${NC} Docker backend tests failed"
    TEST_FAILED=true
fi

echo ""
echo "2. Testing API Endpoints..."
if [ "$BACKEND_RUNNING" = true ]; then
    if $PYTHON_CMD -m pytest tests/infrastructure/test_api_endpoints.py -v; then
        echo -e "${GREEN}✓${NC} API endpoint tests passed"
    else
        echo -e "${RED}✗${NC} API endpoint tests failed"
        TEST_FAILED=true
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping API tests (backend not running)"
fi

echo ""
echo "3. Testing Frontend Client..."
if $PYTHON_CMD -m pytest tests/infrastructure/test_frontend_client.py -v; then
    echo -e "${GREEN}✓${NC} Frontend client tests passed"
else
    echo -e "${RED}✗${NC} Frontend client tests failed"
    TEST_FAILED=true
fi

echo ""
echo "=========================================="
echo "   Test Summary"
echo "=========================================="
echo ""

if [ "$TEST_FAILED" = true ]; then
    echo -e "${RED}✗ Some tests failed${NC}"
    EXIT_CODE=1
else
    echo -e "${GREEN}✓ All tests passed${NC}"
    EXIT_CODE=0
fi

# Cleanup if we started the backend
if [ "$BACKEND_STARTED_BY_SCRIPT" = true ]; then
    echo ""
    echo "Stopping backend container..."
    cd ../..
    if [ -f "backend-docker.sh" ]; then
        ./backend-docker.sh stop
    else
        docker compose -f docker-compose.backend.yaml down
    fi
fi

echo ""
exit $EXIT_CODE

# Made with Bob
