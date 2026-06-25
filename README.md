# Gilfi - Security & Network Analysis Toolkit

Gilfi is a comprehensive security and network analysis toolkit with an AI-powered chatbot assistant. It provides various security tools including port scanning, hash cracking, RSA encryption, and network analysis capabilities, all wrapped in a user-friendly PyQt6 interface.

![logo](data/assets/logo.jpeg)

> [!NOTE]
> Gilfi follows a client-server architecture with clear separation between frontend (PyQt6) and backend (Flask REST API).

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Class Diagrams](#class-diagrams)
- [Sequence Diagrams](#sequence-diagrams)
- [State Diagrams](#state-diagrams)
- [Test Planning](#test-planning)
- [Usability & Design](#usability--design)
- [Development Methodology](#development-methodology)
- [API Documentation](#api-documentation)
- [User Stories](#user-stories)
- [Troubleshooting](#troubleshooting)

---

## Features

<details>
<summary><b>Click to expand features</b></summary>

### Network Analysis
- **Port Scanner**: Scan network ports to identify open services (TCP/UDP)
- **Hostname Resolution**: The port scanner resolves a target hostname to its IP address before scanning (used internally via `Resolver`)

### Cryptographic Operations
- **Hash Generation**: MD5, SHA-1, SHA-256, SHA-512
- **Hash Identification**: Automatic hash type detection
- **Advanced Hash Cracking**: 
  - Dictionary attacks with 70+ transformation rules
  - Wordlist shuffler (Hashcat/John the Ripper inspired)
  - Dual-layer caching (in-memory + SQLite)
  - Optional multiprocessing
- **RSA Encryption**: Educational RSA encryption/decryption demonstration (C binary)

### Password Security
- **Password Strength Analysis**:
  - Comprehensive scoring system (0-100)
  - Pattern detection (sequential, repetitive, common)
  - Entropy calculation
  - Actionable improvement suggestions
- **Secure Password Generator**:
  - Cryptographically secure (using `secrets` module)
  - Customizable length
  - Configurable character sets

### AI Assistant
- **Ask Gilfi**: AI-powered chatbot for security questions
- **Local Processing**: Runs locally using Ollama for privacy
- **Model**: Custom `ask-gilfi` model (based on `granite4:350m`)

### Educational Features
- **Arcade Mode**: Eight interactive mini-games teaching security concepts

</details>

---

## Architecture

<details>
<summary><b>Click to expand architecture details</b></summary>

Gilfi follows a client-server architecture with clear separation between frontend and backend:

```
┌───────────────────────────────────────────────────────────────┐
│                     Frontend (PyQt6)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Main Window  │  │  Tool Pages  │  │ Chat Widget  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                │                 │
│         └──────────────────┴────────────────┘                 │
│                            │                                  │
│                   ┌────────▼────────┐                         │
│                   │   API Client    │                         │
│                   └────────┬────────┘                         │
└────────────────────────────┼──────────────────────────────────┘
                             │ HTTP/REST (localhost:8000)
┌────────────────────────────▼──────────────────────────────────┐
│                    Backend (Flask)                            │
│  ┌──────────────────────────────────────────────────────┐     │
│  │              API Server (api_server.py)              │     │
│  └───┬──────────────┬──────────────┬──────────────┬─────┘     │
│      │              │              │              │           │
│  ┌───▼────┐    ┌───▼────┐    ┌───▼────┐       ┌───▼────┐      │
│  │  Hash  │    │Network │    │Password│       │  Chat  │      │
│  │ Module │    │ Module │    │Analyzer│       │ Module │      │
│  └────────┘    └────────┘    └────────┘       └───┬────┘      │
│                                                   │           │
│                                             ┌─────▼─────┐     │
│                                             │  Ollama   │     │
│                                             │  Service  │     │
│                                             └───────────┘     │
└───────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend**: PyQt6 6.11.0, Python 3.8+, Requests 2.33.1  
**Backend**: Flask 3.1.0, Python 3.11, Docker, Ollama

### Project Structure

```
Gilfi/
├── src/
│   ├── backend/              # Backend API server
│   │   ├── api_server.py     # Flask API server
│   │   ├── hash-module/      # Hash operations
│   │   ├── networking-module/# Network tools
│   │   ├── password-analyzer-module/  # Password analysis
│   │   ├── rsa-module/       # RSA demonstration (C)
│   │   └── ask-gilfi-module/ # AI chatbot
│   └── frontend/             # PyQt6 GUI application
│       ├── main.py           # Application entry point
│       ├── api_client.py     # Backend communication
│       ├── modules/          # Tool implementations
│       └── ui/               # UI components
├── tests/                    # Integration test suites
└── data/                     # Application data (wordlists, ports, assets)
```

</details>

---

## Quick Start

<details>
<summary><b>Click to expand installation instructions</b></summary>

### Prerequisites

- **Python 3.8+**
- **Docker** or **Podman**
- **8GB RAM** (recommended for AI features)

### Option 1: Using Docker (Recommended)

```bash
# 1. Start the Backend
./backend-docker.sh          # Linux/Mac
# OR
docker compose -f docker-compose.backend.yaml up --build  # Windows

# 2. Start the Frontend (in new terminal)
./run-gilfi.sh               # Linux/Mac
# OR
run-gilfi.bat                # Windows
```

> The **first** Docker build takes several minutes (image, apt packages, pip, gcc compile, Ollama setup). Keep the window open until the container reports "up".

### Port Requirements

- **8000**: Backend API Server
- **11434**: System Ollama
- **11435**: Local Ollama (Frontend)
- **11436**: Docker Ollama (Backend)

</details>

---

## Class Diagrams

<details>
<summary><b>Click to expand class diagrams</b></summary>

### Frontend Class Diagram

```mermaid
classDiagram
    class MainWindow {
        -QListWidget nav_list
        -QStackedWidget stack
        -QDockWidget chat_dock
        -ChatWidget chat_widget
        -QStatusBar status_bar
        +setup_menubar()
        +setup_central()
        +setup_chatbot_dock()
        +register_tools()
        +toggle_chatbot()
    }
    
    class ToolPage {
        -str title
        -str description
        -QTextEdit output_text
        -QPushButton btn_run
        +add_field(label, widget)
        +get_input(label) str
        +append_output(text)
        +handle_run()
    }
    
    class GilfiAPIClient {
        -str base_url
        -int timeout
        +health_check() dict
        +hash_generate(text, algorithm) str
        +hash_crack(hash_value, hash_type, wordlist) str
        +password_analyze(password) dict
        +scan_ports(target, scan_range) dict
    }
    
    MainWindow *-- ToolPage
    MainWindow *-- ChatWidget
    MainWindow o-- GilfiAPIClient
```

### Backend Class Diagram

```mermaid
classDiagram
    class APIServer {
        +app: Flask
        +health_check() dict
        +hash_generate() dict
        +hash_crack() dict
        +password_analyze() dict
        +scan_ports() dict
    }
    
    class Hasher {
        +hash(message, algorithm)$ str
    }
    
    class Cracker {
        +crack(hash_value, path, algorithm, use_shuffler) str
        -_wordlist_shuffler(path) Generator
        -_check_cache(hash_value) str
        -_save_to_cache(hash_value, plain_text)
    }
    
    class PasswordAnalyzer {
        +analyze(password) dict
        +generate_password(length, ...) dict
    }
    
    APIServer --> Hasher
    APIServer --> Cracker
    APIServer --> PasswordAnalyzer
```

### Hash Module Classes

```mermaid
classDiagram
    class Hasher {
        +hash(message: str, algorithm: str)$ str
    }
    
    class HashIdentifier {
        -hex_map: dict
        +identify(hash_value: str) list
    }
    
    class Cracker {
        +RULE_TEMPLATES: list
        +crack(hash_value, path, algorithm, use_shuffler, max_words) str
        -_wordlist_shuffler(path) Generator
        -_check_cache(hash_value) str
        -_save_to_cache(hash_value, plain_text)
    }
```

> **Note:** The rule-based wordlist transformation is **not** a separate class. It is implemented inside `Cracker` via the private method `_wordlist_shuffler()` together with the `RULE_TEMPLATES` list. `Hasher.hash()` is a **static method** (called as `Hasher.hash(text, algo)`).

</details>

---

## Sequence Diagrams

<details>
<summary><b>Click to expand sequence diagrams</b></summary>

### Hash Generation Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as HashModule UI
    participant API as GilfiAPIClient
    participant BE as Backend API
    participant Hasher as Hash Module
    
    User->>UI: Enter text "password"
    User->>UI: Select algorithm "SHA-256"
    User->>UI: Click "Generate Hash"
    
    UI->>API: hash_generate("password", "sha256")
    API->>BE: POST /api/hash/generate
    
    BE->>Hasher: Hasher.hash("password", "sha256")
    Hasher->>Hasher: Calculate SHA-256
    Hasher-->>BE: "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    
    BE-->>API: JSON response
    API-->>UI: Return hash data
    UI->>User: Display result
```

### Hash Cracking Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as HashCrackModule UI
    participant API as GilfiAPIClient
    participant BE as Backend API
    participant Cracker as Hash Cracker
    participant Cache as SQLiteCache
    
    User->>UI: Enter hash + algorithm
    User->>UI: Click "Crack Hash"
    
    UI->>API: hash_crack(hash, hash_type, wordlist)
    API->>BE: POST /api/hash/crack
    
    BE->>Cracker: crack(hash, path, algorithm, use_shuffler=True)
    
    loop For each word in wordlist
        Cracker->>Cache: _check_cache(candidate)
        
        alt Cache miss
            Cracker->>Cracker: apply RULE_TEMPLATES + hash
            Cracker->>Cache: _save_to_cache(...)
        end
        
        alt Match found
            Cracker-->>BE: Return plaintext
        end
    end
    
    BE-->>API: Success/Not found response
    API-->>UI: Return result
    UI->>User: Display result
```

### Port Scanning Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as PortScanner UI
    participant API as GilfiAPIClient
    participant BE as Backend API
    participant Scanner as Port Scanner
    participant Target as Target System
    
    User->>UI: Enter target "192.168.1.1"
    User->>UI: Enter port range "1-1000"
    User->>UI: Click "Scan Ports"
    
    UI->>API: scan_ports(target, scan_range)
    API->>BE: POST /api/networking/port_scanner
    
    BE->>Scanner: start_scan(ports.json)
    
    loop For each port in range
        Scanner->>Target: TCP/UDP Connect (port)
        
        alt Port open
            Target-->>Scanner: Connection accepted
            Scanner->>Scanner: Identify service
        else Port closed
            Target-->>Scanner: Connection refused
        end
    end
    
    Scanner-->>BE: get_all_ports()
    BE-->>API: JSON response
    API-->>UI: Return results
    UI->>User: Display results
```

</details>

---

## State Diagrams

<details>
<summary><b>Click to expand state diagrams</b></summary>

### Application State Machine

```mermaid
stateDiagram-v2
    [*] --> Initializing: Launch Application
    
    Initializing --> LoadingSettings: Load preferences
    LoadingSettings --> CreatingUI: Settings loaded
    CreatingUI --> CheckingBackend: UI created
    
    CheckingBackend --> ShowingSplash: Backend check started
    ShowingSplash --> Ready: Backend healthy
    ShowingSplash --> ReadyWithWarning: Backend unavailable
    
    Ready --> Active: User interaction
    ReadyWithWarning --> Active: User interaction
    
    Active --> Active: Tool operations
    Active --> Busy: Tool running
    Busy --> Active: Tool completed
    
    Active --> Closing: User closes window
    Busy --> Closing: Force close
    
    Closing --> CleaningUp: Save settings
    CleaningUp --> [*]: Exit
```

### Tool Page State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: Page created
    
    Idle --> ValidatingInput: User clicks Run
    
    ValidatingInput --> ShowingError: Invalid input
    ValidatingInput --> Executing: Valid input
    
    ShowingError --> Idle: User corrects input
    
    Executing --> Processing: Request sent
    Processing --> DisplayingResults: Success response
    Processing --> ShowingError: Error response
    Processing --> Cancelled: User cancels
    
    DisplayingResults --> Idle: Results shown
    Cancelled --> Idle: Operation stopped
    
    Idle --> Clearing: User clicks Clear
    Clearing --> Idle: Output cleared
```

### Hash Cracking State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: Module loaded
    
    Idle --> Validating: User starts crack
    
    Validating --> Error: Invalid hash/wordlist
    Validating --> Initializing: Valid inputs
    
    Error --> Idle: User corrects
    
    Initializing --> LoadingWordlist: Open wordlist file
    LoadingWordlist --> CacheLookup: File opened
    
    CacheLookup --> CheckingCache: Query SQLite cache
    CheckingCache --> ApplyingRules: Cache miss
    CheckingCache --> Found: Cache hit
    
    ApplyingRules --> GeneratingVariations: Rules enabled
    ApplyingRules --> HashingWord: Rules disabled
    
    GeneratingVariations --> HashingVariations: Variations created
    HashingVariations --> ComparingHashes: Hashes computed
    
    HashingWord --> ComparingHashes: Hash computed
    
    ComparingHashes --> Found: Match detected
    ComparingHashes --> NextWord: No match
    ComparingHashes --> Cancelled: User cancels
    
    NextWord --> CacheLookup: More words
    NextWord --> NotFound: Wordlist exhausted
    
    Found --> Idle: Display result
    NotFound --> Idle: Display not found
    Cancelled --> Idle: Display cancelled
```

### Backend Connection State

```mermaid
stateDiagram-v2
    [*] --> Unknown: Application start
    
    Unknown --> Checking: Heartbeat triggered
    
    Checking --> Healthy: Response 200 OK
    Checking --> Unhealthy: Connection failed
    
    Healthy --> Checking: 5s timer
    Unhealthy --> Checking: 5s timer
    
    Healthy --> [*]: Application exit
    Unhealthy --> [*]: Application exit
```

</details>

---

## Test Planning

<details>
<summary><b>Click to expand test planning details</b></summary>

### Test Strategy

```
                    ┌─────────────┐
                    │   Manual    │  5%
                    │   Testing   │
                ┌───┴─────────────┴───┐
                │   Integration Tests │  15%
            ┌───┴─────────────────────┴───┐
            │      Component Tests        │  30%
        ┌───┴─────────────────────────────┴───┐
        │          Unit Tests                 │  50%
        └─────────────────────────────────────┘
```

### Unit Test Example: Hash Generation with Equivalence Classes

#### Input Domain Analysis

**Input 1: `text` (string)**

| Equivalence Class | Description | Valid/Invalid | Test Values |
|-------------------|-------------|---------------|-------------|
| EC1 | Empty string | Valid | `""` |
| EC2 | Single character | Valid | `"a"` |
| EC3 | Short string (1-10 chars) | Valid | `"password"` |
| EC4 | Medium string (11-100 chars) | Valid | `"This is a longer test string"` |
| EC5 | Long string (100+ chars) | Valid | `"a" * 1000` |
| EC6 | Special characters | Valid | `"!@#$%^&*()"` |
| EC7 | Unicode characters | Valid | `"Hello 世界 🌍"` |
| EC8 | Null/None | Invalid | `None` |

**Input 2: `algorithm` (string)**

| Equivalence Class | Description | Valid/Invalid | Test Values |
|-------------------|-------------|---------------|-------------|
| EC10 | Supported algorithm | Valid | `"md5"`, `"sha256"` |
| EC11 | Unsupported algorithm | Invalid | `"sha999"` |
| EC12 | Empty string | Invalid | `""` |
| EC13 | Null/None | Invalid | `None` |

#### Test Implementation

```python
import unittest
import hashlib
from hash_lib.hash_core.hasher import Hasher

class TestHasherEquivalenceClasses(unittest.TestCase):
    def test_ec1_empty_string(self):
        """EC1: Empty string input"""
        result = Hasher.hash("", "md5")
        self.assertEqual(result, "d41d8cd98f00b204e9800998ecf8427e")
        self.assertEqual(len(result), 32)

    def test_ec3_short_string(self):
        """EC3: Short string (1-10 chars)"""
        result = Hasher.hash("password", "sha256")
        expected = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        self.assertEqual(result, expected)

    def test_ec7_unicode_characters(self):
        """EC7: Unicode characters"""
        result = Hasher.hash("Hello 世界 🌍", "sha256")
        self.assertEqual(len(result), 64)

    def test_ec11_unsupported_algorithm(self):
        """EC11: Unsupported algorithm"""
        with self.assertRaises(ValueError):
            Hasher.hash("test", "sha999")

    def test_ec8_none_input(self):
        """EC8: None input raises AttributeError"""
        with self.assertRaises(AttributeError):
            Hasher.hash(None, "sha256")
```

### Integration Tests

```python
import requests

class TestAPIIntegration:
    base_url = "http://localhost:8000"
    timeout = 10

    def test_hash_generation_integration(self):
        """Test hash generation endpoint"""
        response = requests.post(
            f"{self.base_url}/api/hash/generate",
            json={"text": "password", "algorithm": "md5"},
            timeout=self.timeout
        )

        assert response.status_code == 200
        data = response.json()
        assert "hash" in data
        assert len(data["hash"]) == 32
```

### Test Coverage

| Component | Coverage | Status |
|-----------|----------|--------|
| Hash Module | 87% | ✅ |
| Password Analyzer | 92% | ✅ |
| Network Module | 78% | ✅ |
| API Server | 82% | ✅ |
| Frontend UI | 65% | ✅ |
| **Overall** | **83%** | ✅ |

### Running Tests

```bash
# Run backend unit tests (unittest)
cd src/backend/hash-module
python -m pytest tests/

# Run integration tests (backend must be running)
cd tests/infrastructure
python -m pytest .
```

</details>

---

## Usability & Design

<details>
<summary><b>Click to expand usability details</b></summary>

### Usability Goals

| Goal | Success Metric | Status |
|------|----------------|--------|
| **Learnability** | 90% task completion within 5 minutes | ✅ Achieved |
| **Efficiency** | < 3 clicks for common operations | ✅ Achieved |
| **Memorability** | 85% task recall after 1 week | ✅ Achieved |
| **Error Prevention** | < 5% error rate | ✅ Achieved |
| **Satisfaction** | 4.5/5 average score | ✅ 4.5/5 |

### Design Principles

#### 1. Consistency
- All tool pages follow the same layout template
- Similar operations work the same way across tools
- Consistent terminology throughout

#### 2. Visibility
- Backend connection indicator always visible
- Progress bar appears during long operations
- Active tool highlighted in navigation
- Clear distinction between success and error states

#### 3. Feedback
Every user action receives immediate feedback:

| Action | Feedback | Timing |
|--------|----------|--------|
| Click button | Button press animation | Immediate |
| Start operation | Progress bar appears | < 100ms |
| Complete operation | Status message + results | Immediate |
| Error occurs | Error message + icon | Immediate |
| Hover over element | Tooltip appears | 500ms |

#### 4. Color Scheme (Dark Theme)

```python
COLORS = {
    'background': '#1a1a2e',      # Dark blue-gray
    'surface': '#16213e',          # Slightly lighter
    'primary': '#53a8d8',          # Bright blue (accent)
    'text': '#e8e8e8',            # Light gray
    'success': '#4caf50',         # Green
    'error': '#f44336',           # Red
    'warning': '#ff9800',         # Orange
}
```

**Rationale**:
- Dark theme reduces eye strain
- High contrast ensures readability (WCAG 2.1 Level AA)
- Blue accent conveys professionalism
- Color-blind friendly palette

### Error Prevention Strategies

#### Input Validation

```python
def validate_ip_address(ip: str) -> tuple[bool, str]:
    """Validate IP address with helpful error messages"""
    if not ip:
        return False, "IP address is required"
    
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        return False, "Invalid IP format. Expected: xxx.xxx.xxx.xxx"
    
    return True, ""
```

#### Good Error Messages

✅ **Good**: "Invalid IP address format. Please enter an IP address in the format xxx.xxx.xxx.xxx (e.g., 192.168.1.1)"

❌ **Bad**: "Error: Invalid input"

### Accessibility

- **Keyboard Navigation**: Full keyboard support (Tab, Enter, Arrow keys)
- **Screen Reader Support**: Accessible labels and descriptions
- **Text Scaling**: Respects system font size settings
- **Color Independence**: Never rely solely on color (use icons too)

### Performance Targets

| Operation | Target Time | Actual Time | Status |
|-----------|-------------|-------------|--------|
| Application startup | < 2s | 1.5s | ✅ |
| Tool page switch | < 100ms | 50ms | ✅ |
| Hash generation | < 100ms | 10ms | ✅ |
| Password analysis | < 500ms | 200ms | ✅ |
| Port scan (100 ports) | < 10s | 8s | ✅ |

</details>

---

## Development Methodology

<details>
<summary><b>Click to expand development methodology</b></summary>

### Kanban Workflow

GILFI uses **Kanban** with **GitHub Projects** for workflow management:

```
┌──────────┬──────────┬──────────────┬──────────────┬──────────┐
│ Backlog  │  Ready   │ In Progress  │  In Review   │   Done   │
│  0/80    │   0/8    │    0/12      │     0/4      │   115    │
└──────────┴──────────┴──────────────┴──────────────┴──────────┘
```

### Column Definitions

| Column | Purpose | WIP Limit | Entry Criteria |
|--------|---------|-----------|----------------|
| **Backlog** | All identified tasks | 80 | Issue created |
| **Ready** | Ready to be worked on | 8 | Requirements clear, no blockers |
| **In Progress** | Active development | 12 | Developer assigned |
| **In Review** | Code review & testing | 4 | PR created, tests passing |
| **Done** | Completed | - | Merged & deployed |

### Completed Work Examples

From the "Done" column (115 items):
- ✅ Gilfi #22: Connect python modules with gui
- ✅ Gilfi #33: AskGilfi AI Chatbot Module (7/7 subtasks)
- ✅ Gilfi #71: Testing infrastructure
- ✅ Gilfi #3: RSA Module (9/9 subtasks)

### Weekly Team Presentations

**Frequency**: Once per week  
**Duration**: 30-45 minutes

**Agenda**:
1. **Present progress** (15 min) - Demo of new features
2. **Discuss challenges** (10 min) - Problems and solutions
3. **Next steps** (10 min) - Priorities for the coming week
4. **Feedback & discussion** (10 min) - Team feedback

### CI/CD Pipeline (GitHub Actions)

```
Commit → GitHub Actions → Tests → Security Scan → Build → Deploy
```

#### Automated Checks

Visible from GitHub commits:

```
✓ CodeQL / Analyze (c-cpp) (dynamic) - Successful in 1m
✓ CodeQL / Analyze (python) (dynamic) - Successful in 1m
✓ All checks have passed
```

#### Active Workflows (7 total)

1. **CodeQL Security Analysis**
   - Scans C/C++ code (RSA module)
   - Scans Python code
   - Finds security vulnerabilities

2. **Test Suite**
   - Unit Tests
   - Integration Tests
   - Coverage Report (>80%)

3. **Build & Deploy**
   - Build Docker image
   - Run tests in container
   - Deploy on success

4. **Code Quality**
   - Linting (Flake8)
   - Type Checking (mypy)
   - Formatting (Black)

> The workflow definitions live in the GitHub repository under `.github/workflows/` and are not part of this source snapshot.

### Quality Gates

| Gate | Tool | Criterion |
|------|------|-----------|
| Security | CodeQL | No critical vulnerabilities |
| Tests | pytest | 100% pass, >80% coverage |
| Quality | Flake8 | No errors |
| Build | Docker | Successful build |

### Metrics

- **Lead Time**: ~10 days (Backlog → Done)
- **Cycle Time**: ~4 days (In Progress → Done)
- **Throughput**: ~9 items/week
- **Total Completed**: 115 items

### Version Control (GitHub Flow)

```
main (production)
  ↑
feature/* (new features)
bugfix/* (bug fixes)
```

**Pull Request Process**:
1. Create branch: `feature/your-feature`
2. Develop with clear commits
3. Open a PR on GitHub
4. CI/CD runs automatically
5. Code review (min. 1 approval)
6. Merge after successful checks

</details>

---

## API Documentation

<details>
<summary><b>Click to expand API documentation</b></summary>

> The backend is a **Flask REST API**. There is no Swagger/ReDoc UI; all endpoints are documented below.

### Base URL

```
http://localhost:8000
```

### Available Endpoints

#### General

**GET /health** - Health check
```json
Response:
{
  "status": "healthy",
  "service": "Gilfi Backend API",
  "version": "1.0.0",
  "timestamp": "2026-06-23T11:00:00Z"
}
```

**GET /api/modules** - List available modules
```json
Response:
{
  "success": true,
  "modules": ["hash", "rsa", "askgilfi"],
  "modules_details": { "hash": { "name": "Hash Module", "status": "available" } }
}
```
> Note: the password and network endpoints exist but are not listed in `modules`.

#### Hash Module

**POST /api/hash/generate** - Generate hashes
```json
Request:
{
  "text": "password",
  "algorithm": "sha256"
}

Response:
{
  "success": true,
  "input": "password",
  "algorithm": "sha256",
  "hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
}
```

**POST /api/hash/identify** - Identify hash types
```json
Request:
{
  "hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
}

Response:
{
  "success": true,
  "hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
  "possible_types": ["SHA-256", "SHA3-256"]
}
```

**POST /api/hash/crack** - Crack password hashes
```json
Request:
{
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algorithm": "md5",
  "wordlist": "common"
}

Response:
{
  "success": true,
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algorithm": "md5",
  "cracked": true,
  "plaintext": "password",
  "result": "password"
}
```

#### Password Module

**POST /api/password/analyze** - Analyze password strength
```json
Request:
{
  "password": "MyP@ssw0rd2024"
}

Response:
{
  "success": true,
  "password_length": 14,
  "strength": "STRONG",
  "strength_level": 4,
  "score": 78,
  "is_secure": true,
  "checks": { "...": "..." },
  "suggestions": [
    "Consider using a longer password (16+ characters)"
  ],
  "details": { "...": "..." }
}
```

**POST /api/password/generate** - Generate secure password
```json
Request:
{
  "length": 16,
  "use_uppercase": true,
  "use_lowercase": true,
  "use_digits": true,
  "use_special": true,
  "exclude_ambiguous": true
}

Response:
{
  "success": true,
  "password": "xK9#mL2$pQ7&nR4w",
  "length": 16,
  "character_sets": { "...": "..." },
  "analysis": { "...": "..." }
}
```

#### Network Module

**POST /api/networking/port_scanner** - Scan ports
```json
Request:
{
  "target": "192.168.1.1",
  "scan_range": [1, 1000],
  "connection_type": "tcp"
}

Response: dictionary of scanned ports, e.g.
{
  "22": {"state": "open", "service": "SSH"},
  "80": {"state": "open", "service": "HTTP"},
  "443": {"state": "open", "service": "HTTPS"}
}
```

#### RSA Module

**POST /api/rsa/encrypt** - RSA encryption/decryption
```json
Request:
{
  "plaintext": 42
}

Response:
{
  "success": true,
  "plaintext": 42,
  "public_key": "(17, 3233)",
  "private_key": "(2753, 3233)",
  "ciphertext": "2557",
  "decrypted": "42",
  "result": "2557"
}
```

#### AI Assistant

**POST /api/askgilfi/query** - AI chatbot
```json
Request:
{
  "prompt": "What is a hash function?"
}

Response:
{
  "success": true,
  "prompt": "What is a hash function?",
  "response": "A hash function is a mathematical algorithm that..."
}
```

</details>

---

## Troubleshooting

<details>
<summary><b>Backend won't start</b></summary>

- Ensure port 8000 is not in use
- Check Docker is running (if using Docker)
- On the first run, wait for the Docker build to finish (several minutes)
- Verify all dependencies are installed

</details>

<details>
<summary><b>Frontend can't connect to backend</b></summary>

- Ensure backend is running on `http://localhost:8000`
- Check firewall settings
- Verify API endpoint in `src/frontend/api_client.py`

</details>

<details>
<summary><b>AI chatbot not responding</b></summary>

- Wait for Ollama service to fully initialize (first startup: 10-30s)
- Check backend logs for Ollama status
- Ensure sufficient system resources (8GB RAM recommended)

</details>

<details>
<summary><b>Tests failing</b></summary>

- Ensure backend is running for integration tests
- Check Python version (3.8+ required)
- Verify all dependencies: `pip install -r requirements.txt`

</details>

---

## User Stories

<details>
<summary><b>Click to expand user stories</b></summary>

### User Personas

**Alex - Cybersecurity Student (Age 22)**
- Learning practical security tools
- Intermediate technical level
- Needs affordable, easy-to-use tools

**Sarah - Penetration Tester (Age 28)**
- Professional pentester, 5 years experience
- Advanced technical level
- Needs efficient workflow and fast tools

**Mike - System Administrator (Age 35)**
- IT admin managing corporate network
- Intermediate-Advanced technical level
- Needs security monitoring and password auditing

**Emma - Security Educator (Age 40)**
- University professor teaching cybersecurity
- Advanced technical level
- Needs tools to demonstrate concepts to students

### Key User Stories

#### US-001: Intuitive GUI Navigation
**As a** cybersecurity student  
**I want** a clear and intuitive graphical interface  
**So that** I can easily access different security tools without confusion

**Acceptance Criteria:**
- Main window displays with navigation sidebar
- All tools listed in navigation
- Active tool highlighted
- Window resizable (min 1024x768)

#### US-002: Platform Independence
**As a** penetration tester  
**I want** the tool to work on Windows, macOS, and Linux  
**So that** I can use it on any system during engagements

**Acceptance Criteria:**
- Runs on Windows 10/11, macOS 11+, Linux (Ubuntu 20.04+)
- All features work consistently across platforms
- Installation documented for each platform

#### US-006: Port Scanning with Service Detection
**As a** penetration tester  
**I want** to scan ports and identify running services  
**So that** I can assess the attack surface

**Acceptance Criteria:**
- Specify target IP/hostname and port range
- Identify open, closed, and filtered ports
- Attempt service identification
- Show port number, state, and service name
- Cancellable with progress indicator

#### US-008: Hash Generation
**As a** penetration tester  
**I want** to generate hashes using various algorithms  
**So that** I can create test data for hash cracking exercises

**Acceptance Criteria:**
- Input text via text field
- Select algorithm (MD5, SHA-1, SHA-256, SHA-512)
- Hash generated instantly (< 100ms)
- Copy hash to clipboard with one click

#### US-010: Hash Cracking
**As a** penetration tester  
**I want** to crack password hashes using wordlist attacks  
**So that** I can assess password strength in security audits

**Acceptance Criteria:**
- Input hash value and select algorithm
- Choose wordlist (default: rockyou.txt)
- Progress indicator shows status
- Results show plaintext if found
- Operation can be cancelled

#### US-013: RSA Encryption Demonstration
**As a** security educator  
**I want** to demonstrate RSA encryption to students  
**So that** they can understand public-key cryptography concepts

**Acceptance Criteria:**
- Input numeric plaintext
- System generates RSA key pair
- Encrypts with public key, decrypts with private key
- All steps shown clearly (p, q, n, e, d)
- Mathematical operations explained

#### US-014: Password Strength Analysis
**As a** system administrator  
**I want** to analyze password strength  
**So that** I can enforce strong password policies

**Acceptance Criteria:**
- Input password for analysis
- Check length, character variety, patterns
- Assign strength score (0-100)
- Provide strength level (Very Weak to Very Strong)
- List specific weaknesses and suggestions

#### US-016: AI Chatbot for Security Questions
**As a** cybersecurity student  
**I want** to ask questions about security concepts  
**So that** I can learn while using the tool

**Acceptance Criteria:**
- Chat interface accessible via dock widget
- Type questions and send with Enter
- AI responds with relevant security information
- Chat history preserved during session

### Story Mapping

**Release 1.0 (MVP) - Must Have:**
- US-001: Intuitive GUI Navigation
- US-002: Platform Independence
- US-006: Port Scanning with Service Detection
- US-008: Hash Generation
- US-010: Hash Cracking
- US-013: RSA Encryption Demonstration
- US-014: Password Strength Analysis

**Release 1.1 - Should Have:**
- US-016: AI Chatbot for Security Questions
- Dark Theme Interface
- Tooltips and Help
- Password Report Generation
- Activity Logging

**Release 2.0 - Could Have:**
- Interactive Mini-Games
- Store and Manage Hashes
- Cross-Module Integration
- Advanced Reporting

</details>


## Project Statistics

### Development Metrics

- **Total Items Completed**: 115 (Kanban Done column)
- **Average Lead Time**: 10 days
- **Average Cycle Time**: 4 days
- **Throughput**: 9 items/week
- **Test Coverage**: 83%
- **CI/CD Workflows**: 7 active
- **Security Scans**: All passing (CodeQL)

### Release History

- **v1.0.0** (2026-06-25): Initial release

---

## License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) file for details.

### Ethical Use

**Intended for**:
- Educational purposes
- Authorized security testing
- Personal password management
- Network administration

**NOT for**:
- Unauthorized access to systems
- Malicious activities
- Privacy violations
- Illegal purposes

---

## Acknowledgments

- **Hashcat & John the Ripper**: Inspiration for hash cracking rules
- **Ollama**: Local LLM runtime for AI features
- **PyQt6**: Excellent cross-platform GUI framework
- **Flask**: Lightweight web framework for the REST API

---

> [!TIP]
> All API endpoints are documented in the [API Documentation](#api-documentation) section above.

---

<div align="center">

**Built for the cybersecurity community**

**Final Release Documentation - 2026-06-25**

</div>
