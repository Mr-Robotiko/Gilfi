#!/bin/bash

# Gilfi - Installation and Run Script (Linux/macOS)
# This script installs dependencies and runs the Gilfi application

set -e  # Exit on error

echo "=========================================="
echo "   Gilfi - Installation & Run Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print installation instructions
print_install_instructions() {
    echo ""
    echo -e "${BLUE}=========================================="
    echo "   Installation Instructions"
    echo "==========================================${NC}"
    echo ""
    echo "Please install the following prerequisites:"
    echo ""
    echo -e "${YELLOW}1. Python 3.8 or higher:${NC}"
    echo "   • macOS:   brew install python3"
    echo "   • Linux:   sudo apt install python3 python3-pip python3-venv"
    echo "   • Windows: Download from https://www.python.org/downloads/"
    echo ""
    echo -e "${YELLOW}2. Container Runtime (Docker or Podman):${NC}"
    echo "   Docker (Recommended):"
    echo "   • macOS:   brew install --cask docker"
    echo "   • Linux:   sudo apt install docker.io docker-compose"
    echo "   • Windows: Download from https://www.docker.com/products/docker-desktop"
    echo ""
    echo "   OR Podman:"
    echo "   • macOS:   brew install podman podman-compose"
    echo "   • Linux:   sudo apt install podman podman-compose"
    echo "   • Windows: Download from https://podman.io/getting-started/installation"
    echo ""
    echo -e "${YELLOW}3. System Requirements:${NC}"
    echo "   • RAM: Minimum 4GB (8GB recommended for AI chatbot)"
    echo "   • Disk: ~2GB for Ollama models"
    echo ""
    echo -e "${YELLOW}4. Port Requirements:${NC}"
    echo "   The following ports must be available:"
    echo "   • 8000:  Backend API Server"
    echo "   • 11434: System Ollama (if installed)"
    echo "   • 11435: Local Ollama (Frontend)"
    echo "   • 11436: Docker Ollama (Backend)"
    echo ""
    echo "After installing prerequisites, run this script again."
    echo ""
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed!${NC}"
    print_install_instructions
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check if Docker or Podman is installed
CONTAINER_CMD=""
if command -v docker &> /dev/null; then
    CONTAINER_CMD="docker"
    echo -e "${GREEN}✓${NC} Docker found"
elif command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
    echo -e "${GREEN}✓${NC} Podman found"
else
    echo -e "${YELLOW}⚠${NC} Warning: Neither Docker nor Podman found"
    echo "Backend API will not be available. Only local features will work."
fi

echo ""
echo "=========================================="
echo "   Installing Dependencies"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install frontend requirements
echo "Installing frontend dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Frontend dependencies installed"
else
    echo -e "${RED}Error: requirements.txt not found!${NC}"
    exit 1
fi

# Install backend dependencies (for local development)
echo "Installing backend dependencies..."
if [ -f "src/backend/requirements.txt" ]; then
    pip install -r src/backend/requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Backend dependencies installed"
fi

echo ""
echo "=========================================="
echo "   Starting Backend (Docker)"
echo "=========================================="
echo ""

# Start backend if Docker/Podman is available
if [ -n "$CONTAINER_CMD" ]; then
    echo "Starting backend container..."
    
    # Check if backend-docker.sh exists
    if [ -f "backend-docker.sh" ]; then
        chmod +x backend-docker.sh
        ./backend-docker.sh start
    else
        # Fallback to docker-compose
        if [ -f "docker-compose.backend.yaml" ]; then
            $CONTAINER_CMD compose -f docker-compose.backend.yaml up -d
            echo -e "${GREEN}✓${NC} Backend container started"
        else
            echo -e "${YELLOW}⚠${NC} Backend configuration not found, skipping..."
        fi
    fi
    
    echo ""
    echo "Waiting for backend to be ready..."
    sleep 5
    
    # Check if backend is responding
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend API is ready"
    else
        echo -e "${YELLOW}⚠${NC} Backend API not responding (this is okay for local-only mode)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Skipping backend startup (no container runtime found)"
fi

echo ""
echo "=========================================="
echo "   Starting Gilfi Frontend"
echo "=========================================="
echo ""

# Make sure we're in the virtual environment
source venv/bin/activate

echo "Starting Gilfi application..."
echo ""
echo -e "${GREEN}Gilfi is starting...${NC}"
echo ""
echo "Features available:"
echo "  • Port Scanner"
echo "  • Network Scanner"
echo "  • Hash Generator/Identifier"
if [ -n "$CONTAINER_CMD" ]; then
    echo "  • Hash Cracker (via backend API)"
    echo "  • RSA Encryption (via backend API)"
fi
echo "  • Ask-Gilfi Chat (local AI assistant)"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the application
python3 src/frontend/main.py

# Cleanup on exit
echo ""
echo "=========================================="
echo "   Shutting Down"
echo "=========================================="
echo ""

if [ -n "$CONTAINER_CMD" ] && [ -f "backend-docker.sh" ]; then
    echo "Stopping backend container..."
    ./backend-docker.sh stop
fi

echo -e "${GREEN}✓${NC} Gilfi stopped successfully"
echo ""
