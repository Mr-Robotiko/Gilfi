#!/bin/bash

# Backend Container Entrypoint Script
# This script runs when the container starts and handles setup tasks

set -e

echo "========================================="
echo "  Gilfi Backend Container Starting"
echo "========================================="

# Function to print colored output
print_info() {
    echo "[INFO] $1"
}

print_success() {
    echo "[SUCCESS] $1"
}

print_error() {
    echo "[ERROR] $1"
}

# Compile RSA module if not already compiled
print_info "Checking RSA module..."

RSA_SOURCE="/app/backend/rsa-module/rsa-module.c"
RSA_BINARY="/app/backend/rsa-module/rsa-module"

if [ ! -f "$RSA_BINARY" ] || [ "$RSA_SOURCE" -nt "$RSA_BINARY" ]; then
    print_info "Compiling RSA module..."
    if gcc "$RSA_SOURCE" -o "$RSA_BINARY"; then
        chmod +x "$RSA_BINARY"
        print_success "RSA module compiled successfully"
    else
        print_error "Failed to compile RSA module"
        exit 1
    fi
else
    print_success "RSA module already compiled"
fi

# Verify Ollama binary permissions
print_info "Checking Ollama binary permissions..."

OLLAMA_BINARY="/app/backend/ask-gilfi-module/bin/linux/ollama"

if [ -f "$OLLAMA_BINARY" ]; then
    if [ ! -x "$OLLAMA_BINARY" ]; then
        print_info "Setting Ollama binary permissions..."
        chmod +x "$OLLAMA_BINARY"
        print_success "Ollama binary is now executable"
    else
        print_success "Ollama binary is executable"
    fi
else
    print_error "Ollama binary not found at $OLLAMA_BINARY"
fi

# Verify Python packages
print_info "Verifying Python packages..."

if python -c "import hash_lib" 2>/dev/null; then
    print_success "Hash module package installed"
else
    print_error "Hash module package not found"
fi

if python -c "import networking-lib" 2>/dev/null; then
    print_success "Networking module package installed"
else
    print_error "Networking module package not found"
fi

if python -c "import requests" 2>/dev/null; then
    print_success "Requests package installed"
else
    print_error "Requests package not found"
fi

# Display environment info
print_info "Environment information:"
echo "  - Python version: $(python --version)"
echo "  - Working directory: $(pwd)"
echo "  - OS: $(uname -s)"
echo "  - Architecture: $(uname -m)"

# Display available modules
print_info "Available backend modules:"
echo "  - Hash module: /app/backend/hash-module"
echo "  - Networking module: /app/backend/networking-module"
echo "  - RSA module: /app/backend/rsa-module/rsa-module"
echo "  - Ask-Gilfi: /app/backend/ask-gilfi-module/ask-gilfi-chat.py"

echo "========================================="
echo "  Backend Ready!"
echo "========================================="

exec "$@"
