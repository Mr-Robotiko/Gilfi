# Gilfi Backend

The Gilfi backend is a REST API server that provides cryptographic and security analysis tools through HTTP endpoints. It's designed to run in a Docker container and serves as the computational engine for the Gilfi frontend application.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Modules](#modules)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Development](#development)
- [Docker Deployment](#docker-deployment)
- [Testing](#testing)

## Overview

The backend provides the following capabilities:
- **Hash Operations**: Generate, identify, and crack cryptographic hashes
- **RSA Encryption**: Perform RSA encryption/decryption operations
- **AI Assistant**: Query the Ask-Gilfi chatbot for security-related questions

### Technology Stack

- **Framework**: Flask 3.1.0 with Flask-CORS
- **Language**: Python 3.11
- **Container**: Docker with Python slim base image
- **Dependencies**: See [requirements.txt](requirements.txt)

## Architecture

```
src/backend/
├── api_server.py          # Main Flask REST API server
├── entrypoint.sh          # Docker container initialization script
├── Dockerfile             # Container build configuration
├── requirements.txt       # Python dependencies
├── hash-module/           # Hash generation, identification, and cracking
├── rsa-module/            # RSA encryption (C implementation)
└── ask-gilfi-module/      # AI chatbot with Ollama integration
```

### Component Interaction

```
Frontend (PyQt6) → HTTP/REST → Backend API Server → Modules
                                      ├── Hash Module (Python)
                                      ├── RSA Module (C binary)
                                      └── Ask-Gilfi (Ollama + Python)
```

## Modules

### 1. Hash Module

**Location**: `hash-module/`

A Python package providing comprehensive hash operations:

- **Hasher**: Generate hashes using various algorithms (MD5, SHA-1, SHA-256, SHA-512, etc.)
- **Identifier**: Identify hash types based on length and format patterns
- **Cracker**: Crack hashes using wordlist-based dictionary attacks

**Installation**:
```bash
pip install -e hash-module/
```

**Key Classes**:
- `hash_lib.hash_core.hasher.Hasher`
- `hash_lib.hash_identifier.identifier.HashIdentifier`
- `hash_lib.hash_cracker.cracker.Cracker`

### 2. RSA Module

**Location**: `rsa-module/`

A C implementation of RSA encryption providing:
- Prime number generation
- Public/private key pair generation
- Encryption and decryption operations
- Modular exponentiation

**Compilation**:
```bash
gcc rsa-module/rsa-module.c -o rsa-module/rsa-module
```

**Usage**:
```bash
./rsa-module/rsa-module <plaintext_number>
```

### 3. Ask-Gilfi Module

**Location**: `ask-gilfi-module/`

An AI-powered chatbot using Ollama with a custom security-focused model:

- **Model**: granite4:350m (customized for security topics)
- **Platform Support**: Linux, macOS, Windows
- **Features**: Context-aware responses about security tools and concepts

**Components**:
- `ask-gilfi-chat.py`: Python interface to Ollama
- `bin/`: Platform-specific Ollama binaries
- `models/`: Pre-configured AI model and blobs

## API Endpoints

### Health Check

```http
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "Gilfi Backend API",
  "version": "1.0.0"
}
```

### List Modules

```http
GET /api/modules
```

**Response**:
```json
{
  "success": true,
  "modules": {
    "hash": {
      "name": "Hash Module",
      "endpoints": ["/api/hash/generate", "/api/hash/identify", "/api/hash/crack"],
      "status": "available"
    },
    "rsa": {
      "name": "RSA Module",
      "endpoints": ["/api/rsa/encrypt"],
      "status": "available"
    },
    "askgilfi": {
      "name": "Ask-Gilfi Chatbot",
      "endpoints": ["/api/askgilfi/query"],
      "status": "available"
    }
  }
}
```

### Hash Operations

#### Generate Hash

```http
POST /api/hash/generate
Content-Type: application/json

{
  "text": "password123",
  "algorithm": "sha256"
}
```

**Response**:
```json
{
  "success": true,
  "input": "password123",
  "algorithm": "sha256",
  "hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
}
```

**Supported Algorithms**: md5, sha1, sha224, sha256, sha384, sha512

#### Identify Hash

```http
POST /api/hash/identify
Content-Type: application/json

{
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99"
}
```

**Response**:
```json
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "possible_types": ["MD5", "MD4", "MD2"]
}
```

#### Crack Hash

```http
POST /api/hash/crack
Content-Type: application/json

{
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "wordlist": "/app/data/wordlist/rockyou.txt",
  "algorithm": "md5"
}
```

**Response** (Success):
```json
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algorithm": "md5",
  "cracked": true,
  "plaintext": "password"
}
```

**Response** (Not Found):
```json
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algorithm": "md5",
  "cracked": false,
  "message": "Password not found in wordlist"
}
```

### RSA Encryption

```http
POST /api/rsa/encrypt
Content-Type: application/json

{
  "plaintext": 42
}
```

**Response**:
```json
{
  "success": true,
  "plaintext": 42,
  "public_key": "(e, n)",
  "private_key": "(d, n)",
  "ciphertext": "encrypted_value",
  "decrypted": "42",
  "output": "Full RSA operation output..."
}
```

### Ask-Gilfi Chatbot

```http
POST /api/askgilfi/query
Content-Type: application/json

{
  "prompt": "What is a hash function?"
}
```

**Response**:
```json
{
  "success": true,
  "prompt": "What is a hash function?",
  "response": "A hash function is a mathematical algorithm that..."
}
```

## Installation

### Prerequisites

- Python 3.11+
- GCC compiler (for RSA module)
- Docker (for containerized deployment)

### Local Development Setup

1. **Install Python dependencies**:
```bash
cd src/backend
pip install -r requirements.txt
```

2. **Install hash module**:
```bash
pip install -e hash-module/
```

3. **Compile RSA module**:
```bash
gcc rsa-module/rsa-module.c -o rsa-module/rsa-module
chmod +x rsa-module/rsa-module
```

4. **Set up Ollama binary permissions**:
```bash
# Linux
chmod +x ask-gilfi-module/bin/linux/ollama

# macOS
chmod +x ask-gilfi-module/bin/mac/ollama
```

5. **Run the API server**:
```bash
python api_server.py
```

The server will start on `http://localhost:8000`

## Development

### Running the Server

```bash
python api_server.py
```

**Output**:
```
==================================================
  Gilfi Backend API Server
==================================================
Starting server on http://0.0.0.0:8000

Available endpoints:
  GET  /health
  GET  /api/modules
  POST /api/hash/generate
  POST /api/hash/identify
  POST /api/hash/crack
  POST /api/rsa/encrypt
  POST /api/askgilfi/query
==================================================
```

### Testing Endpoints

Using `curl`:

```bash
# Health check
curl http://localhost:8000/health

# Generate hash
curl -X POST http://localhost:8000/api/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "algorithm": "sha256"}'

# Identify hash
curl -X POST http://localhost:8000/api/hash/identify \
  -H "Content-Type: application/json" \
  -d '{"hash": "5f4dcc3b5aa765d61d8327deb882cf99"}'
```

### Environment Variables

- `OLLAMA_MODELS`: Path to Ollama models directory (default: `/app/backend/ask-gilfi-module/models`)

## Docker Deployment

### Building the Container

```bash
docker build -t gilfi-backend -f src/backend/Dockerfile src/backend/
```

### Running the Container

```bash
docker run -d \
  --name gilfi_backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  gilfi-backend
```

### Docker Compose

The backend is designed to work with Docker Compose. See the root `docker-compose.backend.yaml` for the complete setup.

```bash
docker-compose -f docker-compose.backend.yaml up -d
```

### Container Entrypoint

The `entrypoint.sh` script automatically:
1. Compiles the RSA module if needed
2. Sets Ollama binary permissions
3. Verifies Python package installations
4. Displays environment information
5. Lists available modules

### Accessing the Container

```bash
# Execute commands in the running container
docker exec -it gilfi_backend bash

# View logs
docker logs gilfi_backend

# Recompile RSA module if needed
docker exec gilfi_backend gcc /app/backend/rsa-module/rsa-module.c -o /app/backend/rsa-module/rsa-module
```

## Testing

### Manual Testing

Test the API endpoints using the provided test scripts in the `tests/infrastructure/` directory:

```bash
# Run all infrastructure tests
cd tests/infrastructure
./run_tests.sh
```

### Module-Specific Tests

**Hash Module**:
```bash
cd hash-module/tests
python -m pytest test_cases_hasher.py
python -m pytest test_cases_identifier.py
python -m pytest test_cases_cracker.py
```

**RSA Module**:
```bash
cd rsa-module/tests
./test_rsa.sh
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "error": "Error message description"
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (missing or invalid parameters)
- `404`: Not Found (endpoint or resource not found)
- `500`: Internal Server Error

## Troubleshooting

### RSA Module Not Found

```bash
# Recompile the module
gcc rsa-module/rsa-module.c -o rsa-module/rsa-module
chmod +x rsa-module/rsa-module
```

### Ollama Binary Permission Denied

```bash
# Set executable permissions
chmod +x ask-gilfi-module/bin/linux/ollama  # or mac/ollama or windows/ollama.exe
```

### Hash Module Import Error

```bash
# Reinstall the package
pip install -e hash-module/
```

### Port Already in Use

```bash
# Change the port in api_server.py or kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```