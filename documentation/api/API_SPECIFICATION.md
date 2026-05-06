# Gilfi Backend API Specification

## Document Information
- **Version**: 1.0.0
- **Base URL**: `http://localhost:8000`
- **Protocol**: HTTP/REST
- **Data Format**: JSON
- **Date**: 2026-04-28

## Table of Contents
1. [Overview](#1-overview)
2. [Common Responses](#2-common-responses)
3. [Health & Status Endpoints](#3-health--status-endpoints)
4. [Hash Module Endpoints](#4-hash-module-endpoints)
5. [RSA Module Endpoints](#5-rsa-module-endpoints)
6. [Ask-Gilfi Chatbot Endpoints](#6-ask-gilfi-chatbot-endpoints)
7. [Error Handling](#7-error-handling)
8. [Examples](#8-examples)

---

## 1. Overview

The Gilfi Backend API provides RESTful endpoints for security analysis tools. All endpoints accept and return JSON data unless otherwise specified.

### Base URL
```
http://localhost:8000
```

### API Versioning
Current version: `v1` (implicit in all endpoints)

### Content Type
All requests and responses use:
```
Content-Type: application/json
```

---

## 2. Common Responses

### Success Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response Format
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": { ... }
}
```

### HTTP Status Codes
| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input parameters |
| 404 | Not Found | Endpoint or resource not found |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## 3. Health & Status Endpoints

### 3.1 Health Check

**Endpoint**: `GET /health`

**Description**: Check if the API server is running and healthy.

**Request**: No parameters required

**Response**:
```json
{
  "status": "healthy",
  "service": "Gilfi Backend API",
  "version": "1.0.0",
  "timestamp": "2026-04-28T11:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy

**Example**:
```bash
curl http://localhost:8000/health
```

---

### 3.2 List Available Modules

**Endpoint**: `GET /api/modules`

**Description**: List all available backend modules and their status.

**Request**: No parameters required

**Response**:
```json
{
  "success": true,
  "modules": {
    "hash": {
      "name": "Hash Module",
      "endpoints": [
        "/api/hash/generate",
        "/api/hash/identify",
        "/api/hash/crack"
      ],
      "status": "available"
    },
    "rsa": {
      "name": "RSA Module",
      "endpoints": ["/api/rsa/encrypt"],
      "status": "available"
    },
    "password": {
      "name": "Password Analyzer",
      "endpoints": ["/api/password/analyze"],
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

**Status Codes**:
- `200 OK`: Successfully retrieved module list

**Example**:
```bash
curl http://localhost:8000/api/modules
```

---

## 4. Hash Module Endpoints

### 4.1 Generate Hash

**Endpoint**: `POST /api/hash/generate`

**Description**: Generate a cryptographic hash from input text.

**Request Body**:
```json
{
  "text": "string (required)",
  "algorithm": "string (optional, default: sha256)"
}
```

**Supported Algorithms**:
- `md5`
- `sha1`
- `sha224`
- `sha256` (default)
- `sha384`
- `sha512`

**Response**:
```json
{
  "success": true,
  "input": "password123",
  "algorithm": "sha256",
  "hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"
}
```

**Error Responses**:
```json
{
  "error": "Text is required"
}
```

```json
{
  "error": "Unsupported algorithm: md4"
}
```

**Status Codes**:
- `200 OK`: Hash generated successfully
- `400 Bad Request`: Missing or invalid parameters
- `500 Internal Server Error`: Hash generation failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "password123", "algorithm": "sha256"}'
```

---

### 4.2 Identify Hash Type

**Endpoint**: `POST /api/hash/identify`

**Description**: Identify the type of a hash based on its format and length.

**Request Body**:
```json
{
  "hash": "string (required)"
}
```

**Response**:
```json
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "possible_types": ["MD5", "MD4", "MD2"],
  "most_likely": "MD5",
  "confidence": "high"
}
```

**Hash Type Detection**:
| Length | Possible Types |
|--------|---------------|
| 32 | MD5, MD4, MD2 |
| 40 | SHA-1 |
| 56 | SHA-224 |
| 64 | SHA-256 |
| 96 | SHA-384 |
| 128 | SHA-512 |

**Error Responses**:
```json
{
  "error": "Hash is required"
}
```

```json
{
  "error": "Invalid hash format"
}
```

**Status Codes**:
- `200 OK`: Hash identified successfully
- `400 Bad Request`: Missing or invalid hash
- `500 Internal Server Error`: Identification failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/hash/identify \
  -H "Content-Type: application/json" \
  -d '{"hash": "5f4dcc3b5aa765d61d8327deb882cf99"}'
```

---

### 4.3 Crack Hash

**Endpoint**: `POST /api/hash/crack`

**Description**: Attempt to crack a password hash using a wordlist attack.

**Request Body**:
```json
{
  "hash": "string (required)",
  "wordlist": "string (optional, default: /app/data/wordlist/rockyou.txt)",
  "algorithm": "string (optional, default: sha256)"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algorithm": "md5",
  "cracked": true,
  "plaintext": "password",
  "attempts": 1234,
  "time_elapsed": "0.5s"
}
```

**Response (Not Found)**:
```json
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algorithm": "md5",
  "cracked": false,
  "message": "Password not found in wordlist",
  "attempts": 14344391,
  "time_elapsed": "45.2s"
}
```

**Error Responses**:
```json
{
  "error": "Hash is required"
}
```

```json
{
  "error": "Wordlist not found: /path/to/wordlist.txt"
}
```

**Status Codes**:
- `200 OK`: Cracking attempt completed
- `400 Bad Request`: Missing or invalid parameters
- `404 Not Found`: Wordlist file not found
- `500 Internal Server Error`: Cracking process failed

**Performance Notes**:
- Average speed: 1M+ hashes/second
- Large wordlists may take several minutes
- Operation can be cancelled by client

**Example**:
```bash
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
    "algorithm": "md5",
    "wordlist": "/app/data/wordlist/rockyou.txt"
  }'
```

---

## 5. RSA Module Endpoints

### 5.1 RSA Encryption

**Endpoint**: `POST /api/rsa/encrypt`

**Description**: Perform RSA encryption on a numeric plaintext.

**Request Body**:
```json
{
  "plaintext": "number (required)"
}
```

**Response**:
```json
{
  "success": true,
  "plaintext": 42,
  "public_key": {
    "e": 65537,
    "n": 3233
  },
  "private_key": {
    "d": 2753,
    "n": 3233
  },
  "ciphertext": 2557,
  "decrypted": 42,
  "verification": "success",
  "output": "Full RSA operation output..."
}
```

**Response Fields**:
- `plaintext`: Original input number
- `public_key`: Public key (e, n)
- `private_key`: Private key (d, n)
- `ciphertext`: Encrypted value
- `decrypted`: Decrypted value (should match plaintext)
- `verification`: "success" if decryption matches plaintext
- `output`: Complete output from RSA module

**Error Responses**:
```json
{
  "error": "Plaintext is required"
}
```

```json
{
  "error": "Plaintext must be a number"
}
```

```json
{
  "error": "RSA module failed",
  "details": "Binary not found or execution error"
}
```

**Status Codes**:
- `200 OK`: RSA operation completed successfully
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: RSA module execution failed

**Limitations**:
- Educational implementation (small primes)
- Not suitable for production encryption
- Plaintext must be smaller than modulus n

**Example**:
```bash
curl -X POST http://localhost:8000/api/rsa/encrypt \
  -H "Content-Type: application/json" \
  -d '{"plaintext": 42}'
```

---

## 6. Ask-Gilfi Chatbot Endpoints

### 6.1 Query Chatbot

**Endpoint**: `POST /api/askgilfi/query`

**Description**: Send a question to the AI chatbot and receive a response.

**Request Body**:
```json
{
  "prompt": "string (required)",
  "stream": "boolean (optional, default: false)"
}
```

**Response (Non-Streaming)**:
```json
{
  "success": true,
  "prompt": "What is a hash function?",
  "response": "A hash function is a mathematical algorithm that takes an input (or 'message') and returns a fixed-size string of bytes. The output is typically a 'digest' that is unique to each unique input. Hash functions are commonly used in cryptography for data integrity verification, password storage, and digital signatures.",
  "model": "ask-gilfi-4:350m",
  "tokens": 67,
  "response_time": "2.3s"
}
```

**Response (Streaming)**:
When `stream: true`, the response is sent as Server-Sent Events (SSE):
```
data: {"token": "A"}
data: {"token": " hash"}
data: {"token": " function"}
...
data: {"done": true}
```

**Error Responses**:
```json
{
  "error": "Prompt is required"
}
```

```json
{
  "success": false,
  "error": "Ollama server not responding"
}
```

**Status Codes**:
- `200 OK`: Response generated successfully
- `400 Bad Request`: Missing prompt
- `500 Internal Server Error`: Ollama service unavailable
- `503 Service Unavailable`: AI model not loaded

**Example**:
```bash
curl -X POST http://localhost:8000/api/askgilfi/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is a hash function?"}'
```

---

## 7. Error Handling

### 7.1 Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional context",
    "timestamp": "2026-04-28T11:00:00Z"
  }
}
```

### 7.2 Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Invalid or missing input parameters |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `MODULE_UNAVAILABLE` | 503 | Backend module not available |
| `PROCESSING_ERROR` | 500 | Error during request processing |
| `TIMEOUT` | 504 | Operation timed out |

### 7.3 Error Examples

**Missing Required Field**:
```json
{
  "error": "Text is required",
  "code": "INVALID_INPUT",
  "details": {
    "field": "text",
    "received": null
  }
}
```

**File Not Found**:
```json
{
  "error": "Wordlist not found: /app/data/wordlist/custom.txt",
  "code": "RESOURCE_NOT_FOUND",
  "details": {
    "path": "/app/data/wordlist/custom.txt"
  }
}
```

**Service Unavailable**:
```json
{
  "error": "Ollama server not responding",
  "code": "MODULE_UNAVAILABLE",
  "details": {
    "service": "ollama",
    "expected_port": 11436
  }
}
```

## 8. Examples

### 8.1 Complete Hash Workflow

```bash
# 1. Generate a hash
curl -X POST http://localhost:8000/api/hash/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "password", "algorithm": "md5"}'

# Response: {"hash": "5f4dcc3b5aa765d61d8327deb882cf99"}

# 2. Identify the hash type
curl -X POST http://localhost:8000/api/hash/identify \
  -H "Content-Type: application/json" \
  -d '{"hash": "5f4dcc3b5aa765d61d8327deb882cf99"}'

# Response: {"possible_types": ["MD5", "MD4", "MD2"]}

# 3. Crack the hash
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
    "algorithm": "md5"
  }'

# Response: {"cracked": true, "plaintext": "password"}
```
---

---

## 9. Client Libraries

### Python Client

```python
from api_client import GilfiAPIClient

client = GilfiAPIClient("http://localhost:8000")

# Generate hash
result = client.hash_generate("password", "sha256")
print(result['hash'])

# Crack hash
result = client.hash_crack(
    "5f4dcc3b5aa765d61d8327deb882cf99",
    algorithm="md5"
)
if result['cracked']:
    print(f"Password: {result['plaintext']}")
```

### JavaScript Client

```javascript
const API_BASE = 'http://localhost:8000';

async function generateHash(text, algorithm = 'sha256') {
  const response = await fetch(`${API_BASE}/api/hash/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, algorithm })
  });
  return await response.json();
}

// Usage
const result = await generateHash('password', 'sha256');
console.log(result.hash);
```

---

## 10. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-28 | Initial API specification |

---

**Document Status**: Active  
**Last Updated**: 2026-04-28  
**Maintained By**: Gilfi Development Team