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

# Set up Ollama model (download granite4 and create ask-gilfi)
print_info "Checking Ollama model setup..."

MODEL_MANIFEST="/app/backend/ask-gilfi-module/models/manifests/registry.ollama.ai/library/ask-gilfi/latest"

if [ ! -f "$MODEL_MANIFEST" ]; then
    print_info "ask-gilfi model not found - attempting setup..."
    
    # Test if Ollama binary works (architecture check)
    if $OLLAMA_BINARY --version > /dev/null 2>&1; then
        print_info "Setting up ask-gilfi model (first-time setup)..."
        print_info "This may take a few minutes to download granite4:350m..."
        
        # Start Ollama server in background
        $OLLAMA_BINARY serve > /tmp/ollama.log 2>&1 &
        OLLAMA_PID=$!
        
        # Wait for Ollama to be ready
        print_info "Waiting for Ollama server to start..."
        sleep 5
        
        # Check if Ollama is responding
        OLLAMA_READY=false
        for i in {1..30}; do
            if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                print_success "Ollama server is ready"
                OLLAMA_READY=true
                break
            fi
            sleep 1
        done
        
        if [ "$OLLAMA_READY" = true ]; then
            # Pull granite4:350m model
            print_info "Downloading granite4:350m model..."
            if $OLLAMA_BINARY pull granite4:350m; then
                print_success "granite4:350m downloaded"
            else
                print_error "Failed to download granite4:350m"
            fi
            
            # Create ask-gilfi model from Modelfile
            print_info "Creating ask-gilfi model..."
            if $OLLAMA_BINARY create ask-gilfi -f /app/backend/ask-gilfi-module/Modelfile; then
                print_success "ask-gilfi model created"
            else
                print_error "Failed to create ask-gilfi model"
            fi
            
            # Verify model
            print_info "Verifying model installation..."
            $OLLAMA_BINARY list
        fi
        
        # Stop Ollama server
        print_info "Stopping temporary Ollama server..."
        kill $OLLAMA_PID 2>/dev/null || true
        wait $OLLAMA_PID 2>/dev/null || true
        
        print_success "Ollama model setup complete!"
    else
        print_error "Ollama binary not compatible with container architecture"
        print_info "Note: ask-gilfi chatbot requires manual setup on host system"
        print_info "See documentation for local setup instructions"
    fi
else
    print_success "ask-gilfi model already configured"
fi

# Create cache directory for persistent hash storage
print_info "Setting up cache directory..."
CACHE_DIR="/app/data/cache"
mkdir -p "$CACHE_DIR"
if [ -d "$CACHE_DIR" ]; then
    print_success "Cache directory ready at $CACHE_DIR"
else
    print_error "Failed to create cache directory"
fi

# Extract rockyou.7z if not already extracted
print_info "Checking rockyou wordlist..."

ROCKYOU_ARCHIVE="/app/data/wordlist/rockyou.7z"
ROCKYOU_TXT="/app/data/wordlist/rockyou.txt"

if [ -f "$ROCKYOU_ARCHIVE" ]; then
    if [ ! -f "$ROCKYOU_TXT" ]; then
        print_info "Extracting rockyou.7z wordlist..."
        
        # Try different 7z commands (compatibility for different distros)
        # Note: -o flag must be directly followed by path (no space)
        if command -v 7z &> /dev/null; then
            print_info "Using 7z command..."
            if 7z x "$ROCKYOU_ARCHIVE" -o"/app/data/wordlist/" -y; then
                print_success "rockyou.txt extracted successfully"
                # Verify extraction
                if [ -f "$ROCKYOU_TXT" ]; then
                    print_success "Verified: rockyou.txt exists at $ROCKYOU_TXT"
                    ls -lh "$ROCKYOU_TXT"
                else
                    print_error "Extraction completed but file not found at expected location"
                    print_info "Listing wordlist directory contents:"
                    ls -la /app/data/wordlist/
                fi
            else
                print_error "Failed to extract rockyou.7z with 7z (exit code: $?)"
            fi
        elif command -v 7za &> /dev/null; then
            print_info "Using 7za command..."
            if 7za x "$ROCKYOU_ARCHIVE" -o"/app/data/wordlist/" -y; then
                print_success "rockyou.txt extracted successfully"
                # Verify extraction
                if [ -f "$ROCKYOU_TXT" ]; then
                    print_success "Verified: rockyou.txt exists at $ROCKYOU_TXT"
                    ls -lh "$ROCKYOU_TXT"
                else
                    print_error "Extraction completed but file not found at expected location"
                    print_info "Listing wordlist directory contents:"
                    ls -la /app/data/wordlist/
                fi
            else
                print_error "Failed to extract rockyou.7z with 7za (exit code: $?)"
            fi
        else
            print_error "No 7z extraction tool found (tried: 7z, 7za)"
            print_error "Please install p7zip or p7zip-full package"
        fi
    else
        print_success "rockyou.txt already extracted at $ROCKYOU_TXT"
    fi
else
    print_error "rockyou.7z not found at $ROCKYOU_ARCHIVE"
    print_info "Please ensure rockyou.7z is in the data/wordlist directory"
fi

# Verify Python packages
print_info "Verifying Python packages..."

if python -c "import hash_lib" 2>/dev/null; then
    print_success "Hash module package installed"
else
    print_error "Hash module package not found"
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
echo "  - RSA module: /app/backend/rsa-module/rsa-module"
echo "  - Ask-Gilfi: /app/backend/ask-gilfi-module/ask-gilfi-chat.py"

echo "========================================="
echo "  Backend Ready!"
echo "========================================="

exec "$@"
