# Gilfi Backend API Specification

## Document Information
- **Version**: 1.1.0
- **Base URL**: `http://localhost:8000`
- **Protocol**: HTTP/REST
- **Data Format**: JSON
- **Date**: 2026-05-06

## Table of Contents
1. [Overview](#1-overview)
2. [Common Responses](#2-common-responses)
3. [Health & Status Endpoints](#3-health--status-endpoints)
4. [Hash Module Endpoints](#4-hash-module-endpoints)
5. [Password Analyzer Endpoints](#5-password-analyzer-endpoints)
6. [RSA Module Endpoints](#6-rsa-module-endpoints)
7. [Ask-Gilfi Chatbot Endpoints](#7-ask-gilfi-chatbot-endpoints)
8. [Error Handling](#8-error-handling)
9. [Examples](#9-examples)

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
      "endpoints": [
        "/api/password/analyze",
        "/api/password/generate"
      ],
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

**Description**: Attempt to crack a password hash using a wordlist attack with optional rule-based transformations.

**Request Body**:
```json
{
  "hash": "string (required)",
  "wordlist": "string (optional, default: /app/data/wordlist/rockyou.txt)",
  "algorithm": "string (optional, default: sha256)",
  "use_rules": "boolean (optional, default: false)",
  "use_multiprocessing": "boolean (optional, default: false)",
  "batch_size": "number (optional, default: 10000)"
}
```

**Parameters**:
- `hash`: The hash to crack (required)
- `wordlist`: Path to wordlist file (optional, defaults to rockyou.txt)
- `algorithm`: Hash algorithm to use (optional, defaults to sha256)
- `use_rules`: Enable 60+ transformation rules for password variations (optional, default: false)
- `use_multiprocessing`: Use parallel processing across CPU cores (optional, default: false)
- `batch_size`: Number of words to process per batch (optional, default: 10000)

**Rule-Based Transformations**:
When `use_rules: true`, the cracker applies 60+ transformation patterns including:
- Case variations (capitalize, uppercase, lowercase, alternate case)
- Leet speak (o→0, e→3, a→4, i→1, s→5, t→7)
- Number appending (1, 123, 2024, 99, etc.)
- Special character appending (!, @, #, $, !!, $$, etc.)
- Word manipulations (reverse, double, wrap with special chars)
- Combinations (capitalize + numbers, leet + special chars)

Examples of transformations:
- `monkey` → `Monkey`, `MONKEY`, `m0nk3y`, `Monkey1!`, `monkey123`, `!monkey!`, `xXmonkeyXx`

**Response (Success - Basic)**:
```json
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algorithm": "md5",
  "cracked": true,
  "plaintext": "password",
  "attempts": 1234,
  "time_elapsed": "0.5s",
  "used_rules": false
}
```

**Response (Success - With Rules)**:
```json
{
  "success": true,
  "hash": "e10adc3949ba59abbe56e057f20f883e",
  "algorithm": "md5",
  "cracked": true,
  "plaintext": "Monkey1!",
  "original_word": "monkey",
  "transformation": "cap_append_1!",
  "attempts": 45678,
  "time_elapsed": "2.3s",
  "used_rules": true
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
- Average speed: 1M+ hashes/second (basic mode)
- With rules: 60+ transformations per word
- Dual-layer caching (in-memory + SQLite) for faster repeated lookups
- LRU cache for transformation results
- Multiprocessing support for parallel cracking
- Large wordlists may take several minutes
- API timeout: 5 minutes (300 seconds)
- Operation can be cancelled by client

**Examples**:

Basic cracking:
```bash
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
    "algorithm": "md5"
  }'
```

With rule-based transformations:
```bash
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "e10adc3949ba59abbe56e057f20f883e",
    "algorithm": "md5",
    "use_rules": true
  }'
```

With multiprocessing:
```bash
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
    "algorithm": "sha256",
    "use_rules": true,
    "use_multiprocessing": true,
    "batch_size": 50000
  }'
```

---

## 5. Password Analyzer Endpoints

### 5.1 Analyze Password

**Endpoint**: `POST /api/password/analyze`

**Description**: Analyze password strength and security characteristics.

**Request Body**:
```json
{
  "password": "string (required)"
}
```

**Response**:
```json
{
  "success": true,
  "password": "MyP@ssw0rd2024",
  "analysis": {
    "strength": "STRONG",
    "score": 75,
    "is_secure": true,
    "length": 14,
    "has_lowercase": true,
    "has_uppercase": true,
    "has_digits": true,
    "has_special": true,
    "unique_chars": 13,
    "entropy": 3.7,
    "has_consecutive_chars": false,
    "has_sequential_numbers": false,
    "has_sequential_letters": false,
    "has_common_patterns": false,
    "is_common_password": false,
    "suggestions": []
  }
}
```

**Strength Levels**:
| Level | Score Range | Description |
|-------|-------------|-------------|
| VERY_WEAK | 0-19 | Easily crackable, not recommended |
| WEAK | 20-39 | Vulnerable to attacks, should be improved |
| MODERATE | 40-59 | Acceptable but could be stronger |
| STRONG | 60-79 | Good password, resistant to most attacks |
| VERY_STRONG | 80-100 | Excellent password, highly secure |

**Analysis Fields**:
- `strength`: Overall strength level (VERY_WEAK to VERY_STRONG)
- `score`: Numeric score from 0-100
- `is_secure`: Boolean indicating if password meets security standards (score ≥ 60)
- `length`: Number of characters
- `has_lowercase`: Contains lowercase letters (a-z)
- `has_uppercase`: Contains uppercase letters (A-Z)
- `has_digits`: Contains digits (0-9)
- `has_special`: Contains special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)
- `unique_chars`: Number of unique characters
- `entropy`: Randomness measure (higher is better)
- `has_consecutive_chars`: Contains repeated characters (aaa, 111)
- `has_sequential_numbers`: Contains sequential numbers (123, 456)
- `has_sequential_letters`: Contains sequential letters (abc, xyz)
- `has_common_patterns`: Contains common patterns (password, admin)
- `is_common_password`: Matches known weak passwords
- `suggestions`: Array of improvement recommendations

**Error Responses**:
```json
{
  "error": "Password is required"
}
```

**Status Codes**:
- `200 OK`: Analysis completed successfully
- `400 Bad Request`: Missing password parameter
- `500 Internal Server Error`: Analysis failed

**Example**:
```bash
curl -X POST http://localhost:8000/api/password/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "MyP@ssw0rd2024"}'
```

---

### 5.2 Generate Password

**Endpoint**: `POST /api/password/generate`

**Description**: Generate a cryptographically secure random password with customizable options.

**Request Body**:
```json
{
  "length": "number (optional, default: 16, range: 8-128)",
  "use_lowercase": "boolean (optional, default: true)",
  "use_uppercase": "boolean (optional, default: true)",
  "use_digits": "boolean (optional, default: true)",
  "use_special": "boolean (optional, default: true)",
  "exclude_ambiguous": "boolean (optional, default: true)"
}
```

**Parameters**:
- `length`: Password length (8-128 characters, default: 16)
- `use_lowercase`: Include lowercase letters a-z (default: true)
- `use_uppercase`: Include uppercase letters A-Z (default: true)
- `use_digits`: Include digits 0-9 (default: true)
- `use_special`: Include special characters !@#$%^&*()_+-=[]{}|;:,.<>? (default: true)
- `exclude_ambiguous`: Exclude ambiguous characters (0/O, 1/l/I) for clarity (default: true)

**Response**:
```json
{
  "success": true,
  "password": "Xk9#mP2@qL5$wR3!",
  "length": 16,
  "analysis": {
    "strength": "VERY_STRONG",
    "score": 98,
    "is_secure": true,
    "length": 16,
    "has_lowercase": true,
    "has_uppercase": true,
    "has_digits": true,
    "has_special": true,
    "unique_chars": 16,
    "entropy": 4.0,
    "suggestions": []
  }
}
```

**Security Features**:
- Uses Python's `secrets` module for cryptographic randomness
- Ensures at least one character from each selected character set
- Shuffles characters using cryptographically secure random
- NOT suitable for cryptographic keys (use dedicated key generation tools)

**Ambiguous Characters**:
When `exclude_ambiguous: true`, the following characters are excluded:
- `0` (zero) - can be confused with `O` (letter O)
- `1` (one) - can be confused with `l` (lowercase L) or `I` (uppercase i)
- `O` (uppercase O) - can be confused with `0` (zero)
- `I` (uppercase I) - can be confused with `1` (one) or `l` (lowercase L)
- `l` (lowercase L) - can be confused with `1` (one) or `I` (uppercase i)

**Error Responses**:
```json
{
  "error": "Length must be between 8 and 128"
}
```

```json
{
  "error": "At least one character type must be selected"
}
```

**Status Codes**:
- `200 OK`: Password generated successfully
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Generation failed

**Examples**:

Generate default password (16 characters, all types):
```bash
curl -X POST http://localhost:8000/api/password/generate \
  -H "Content-Type: application/json" \
  -d '{}'
```

Generate custom password (20 characters, no special chars):
```bash
curl -X POST http://localhost:8000/api/password/generate \
  -H "Content-Type: application/json" \
  -d '{
    "length": 20,
    "use_lowercase": true,
    "use_uppercase": true,
    "use_digits": true,
    "use_special": false,
    "exclude_ambiguous": true
  }'
```

Generate PIN-like password (8 digits only):
```bash
curl -X POST http://localhost:8000/api/password/generate \
  -H "Content-Type: application/json" \
  -d '{
    "length": 8,
    "use_lowercase": false,
    "use_uppercase": false,
    "use_digits": true,
    "use_special": false
  }'
```

---

## 6. RSA Module Endpoints

### 6.1 RSA Encryption

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

## 7. Ask-Gilfi Chatbot Endpoints

### 7.1 Query Chatbot

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

## 8. Error Handling

### 8.1 Error Response Format

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

### 8.2 Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_INPUT` | 400 | Invalid or missing input parameters |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource not found |
| `MODULE_UNAVAILABLE` | 503 | Backend module not available |
| `PROCESSING_ERROR` | 500 | Error during request processing |
| `TIMEOUT` | 504 | Operation timed out |

### 8.3 Error Examples

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

## 9. Examples

### 9.1 Complete Hash Workflow

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

### 9.2 Complete Password Security Workflow

```bash
# 1. Generate a secure password
curl -X POST http://localhost:8000/api/password/generate \
  -H "Content-Type: application/json" \
  -d '{"length": 16}'

# Response: {"password": "Xk9#mP2@qL5$wR3!", "analysis": {...}}

# 2. Analyze an existing password
curl -X POST http://localhost:8000/api/password/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "password123"}'

# Response: {"strength": "WEAK", "score": 25, "suggestions": [...]}

# 3. Generate a strong password with specific requirements
curl -X POST http://localhost:8000/api/password/generate \
  -H "Content-Type: application/json" \
  -d '{
    "length": 20,
    "use_lowercase": true,
    "use_uppercase": true,
    "use_digits": true,
    "use_special": true,
    "exclude_ambiguous": true
  }'

# Response: {"password": "Yk8@nQ4#pM7$xW2!", "analysis": {...}}
```

### 9.3 Advanced Hash Cracking with Rules

```bash
# 1. Crack a simple password
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
    "algorithm": "md5"
  }'

# Response: {"cracked": true, "plaintext": "password"}

# 2. Crack a password with transformations (e.g., "Monkey1!")
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "e10adc3949ba59abbe56e057f20f883e",
    "algorithm": "md5",
    "use_rules": true
  }'

# Response: {
#   "cracked": true,
#   "plaintext": "Monkey1!",
#   "original_word": "monkey",
#   "transformation": "cap_append_1!"
# }

# 3. Crack with multiprocessing for large wordlists
curl -X POST http://localhost:8000/api/hash/crack \
  -H "Content-Type: application/json" \
  -d '{
    "hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
    "algorithm": "sha256",
    "use_rules": true,
    "use_multiprocessing": true,
    "batch_size": 50000
  }'

# Response: {"cracked": true, "plaintext": "password"}
```

---

## Version History

### Version 1.1.0 (2026-05-06)
- ✨ Added password analyzer endpoints (`/api/password/analyze`)
- ✨ Added password generator endpoints (`/api/password/generate`)
- ✨ Enhanced hash cracking with 60+ rule-based transformations
- ✨ Added multiprocessing support for hash cracking
- ✨ Dual-layer caching (in-memory + SQLite) for improved performance
- ✨ Increased API timeout to 5 minutes for large wordlist operations
- 📚 Comprehensive documentation of all new features

### Version 1.0.0 (2026-04-28)
- Initial API release
- Hash generation, identification, and cracking
- RSA encryption
- Ask-Gilfi chatbot integration

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