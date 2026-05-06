# Gilfi - System Architecture Documentation

## Document Information
- **Version**: 1.0
- **Date**: 2026-04-28
- **Status**: Active
- **Authors**: Gilfi Development Team

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [System Context](#system-context)
3. [Container Architecture](#container-architecture)
4. [Component Architecture](#component-architecture)
5. [Class Diagrams](#class-diagrams)
6. [Sequence Diagrams](#sequence-diagrams)
7. [Deployment Architecture](#deployment-architecture)
8. [Data Flow](#data-flow)
9. [Technology Stack](#technology-stack)

---

## 1. Architecture Overview

### 1.1 Architecture Style
Gilfi follows a **Client-Server Architecture** with the following characteristics:
- **Separation of Concerns**: Frontend (presentation) and backend (business logic) are independent
- **RESTful Communication**: HTTP/JSON for all client-server interactions
- **Modular Design**: Each security tool is an independent, pluggable module
- **Containerization**: Backend runs in Docker for consistent deployment

### 1.2 Architecture Principles
1. **Modularity**: Each component has a single, well-defined responsibility
2. **Loose Coupling**: Components interact through well-defined interfaces
3. **High Cohesion**: Related functionality is grouped together
4. **Scalability**: Architecture supports horizontal scaling
5. **Testability**: Components can be tested independently
6. **Maintainability**: Clear structure facilitates updates and bug fixes

### 1.3 Quality Attributes
- **Performance**: Response time < 2s for most operations
- **Reliability**: 99%+ uptime for backend services
- **Usability**: Intuitive interface requiring minimal training
- **Security**: Input validation, no sensitive data exposure
- **Portability**: Cross-platform support (Windows, macOS, Linux)

---

## 2. System Context

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        External Context                         │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐                                ┌──────────────┐
    │   End User   │                                │   Network    │
    │  (Student,   │                                │  (Target     │
    │  Pentester,  │                                │   Systems)   │
    │   SysAdmin)  │                                │              │
    └──────┬───────┘                                └──────┬───────┘
           │                                               │
           │ Uses GUI                                      │ Scans
           │                                               │
    ┌──────▼───────────────────────────────────────────────▼──────┐
    │                                                             │
    │                    Gilfi Security Toolkit                   │
    │                                                             │
    │  ┌─────────────────┐              ┌─────────────────┐       │
    │  │    Frontend     │◄────REST────►│     Backend     │       │
    │  │  (PyQt6 GUI)    │   API/JSON   │  (Flask API)    │       │
    │  └─────────────────┘              └─────────────────┘       │
    │                                                             │
    └───────────────────────────┬─────────────────────────────────┘
                                │
                                │ Uses
                                │
                    ┌───────────▼──────────┐
                    │   Ollama Service     │
                    │  (Local LLM for AI)  │
                    └──────────────────────┘
```

### 2.2 External Interfaces

#### User Interface
- **Type**: Graphical User Interface (GUI)
- **Technology**: PyQt6
- **Access**: Local desktop application
- **Users**: Students, penetration testers, system administrators, educators

#### Network Interface
- **Type**: TCP/IP networking
- **Protocols**: ICMP (ping), TCP (port scanning), DNS
- **Access**: Local network and internet
- **Purpose**: Network discovery and port scanning

#### AI Service Interface
- **Type**: HTTP REST API
- **Technology**: Ollama
- **Access**: localhost:11435
- **Purpose**: AI-powered chatbot responses

---

## 3. Container Architecture

### 3.1 Container Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         User's Computer                            │
│                                                                    │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │                    Frontend Container                         │ │
│  │                   (Native Application)                        │ │
│  │                                                               │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐               │ │
│  │  │    Main    │  │    UI      │  │   Modules  │               │ │
│  │  │   Window   │  │ Components │  │  (Tools)   │               │ │
│  │  └─────┬──────┘  └────────────┘  └────────────┘               │ │
│  │        │                                                      │ │
│  │        │         ┌────────────┐                               │ │
│  │        └────────►│API Client  │                               │ │
│  │                  └─────┬──────┘                               │ │
│  └────────────────────────┼──────────────────────────────────────┘ │
│                           │ HTTP/REST                              │
│                           │ localhost:8000                         │
│  ┌────────────────────────▼──────────────────────────────────────┐ │
│  │                    Backend Container                          │ │
│  │                   (Docker Container)                          │ │
│  │                                                               │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐               │ │
│  │  │   Flask    │  │   Hash     │  │  Network   │               │ │
│  │  │ API Server │──┤   Module   │  │   Module   │               │ │
│  │  └─────┬──────┘  └────────────┘  └────────────┘               │ │
│  │        │                                                      │ │
│  │        │         ┌────────────┐  ┌────────────┐               │ │
│  │        └────────►│  Password  │  │    RSA     │               │ │
│  │                  │  Analyzer  │  │   Module   │               │ │
│  │                  └────────────┘  └────────────┘               │ │
│  │                                                               │ │
│  │                  ┌────────────┐                               │ │
│  │                  │ Ask-Gilfi  │                               │ │
│  │                  │   Module   │                               │ │
│  │                  └─────┬──────┘                               │ │
│  └────────────────────────┼──────────────────────────────────────┘ │
│                           │ HTTP                                   │
│                           │ localhost:11436                        │
│  ┌────────────────────────▼──────────────────────────────────────┐ │
│  │                  Ollama Container                             │ │
│  │                 (Optional, for AI)                            │ │
│  │                                                               │ │
│  │  ┌────────────┐  ┌────────────┐                               │ │
│  │  │   Ollama   │  │   Custom   │                               │ │
│  │  │   Server   │──┤   Model    │                               │ │
│  │  └────────────┘  │ (granite4) │                               │ │
│  │                  └────────────┘                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 3.2 Container Responsibilities

#### Frontend Container (Native Application)
- **Technology**: Python 3.8+, PyQt6
- **Responsibilities**:
  - User interface rendering
  - User input validation
  - API request orchestration
  - Result visualization
  - Local state management
- **Communication**: HTTP REST to backend

#### Backend Container (Docker)
- **Technology**: Python 3.11, Flask
- **Responsibilities**:
  - API endpoint handling
  - Business logic execution
  - Module orchestration
  - Data processing
  - Error handling
- **Communication**: HTTP REST from frontend, HTTP to Ollama

#### Ollama Container (Optional)
- **Technology**: Ollama runtime, granite4:350m model
- **Responsibilities**:
  - LLM inference
  - Natural language processing
  - Security knowledge responses
- **Communication**: HTTP REST from backend

---

## 4. Component Architecture

### 4.1 Frontend Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      main.py                               │ │
│  │                 (Application Entry)                        │ │
│  └────────────────────────┬───────────────────────────────────┘ │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────────┐ │
│  │                   MainWindow                               │ │
│  │              (QMainWindow subclass)                        │ │
│  │                                                            │ │
│  │  - Navigation sidebar (QListWidget)                        │ │
│  │  - Content area (QStackedWidget)                           │ │
│  │  - Menu bar                                                │ │
│  │  - Status bar                                              │ │
│  │  - Chatbot dock (QDockWidget)                              │ │
│  └───┬─────────────────┬─────────────────┬────────────────────┘ │
│      │                 │                 │                      │
│  ┌───▼────────┐   ┌────▼─────┐   ┌───────▼─────┐                │
│  │  ToolPage  │   │ChatWidget│   │ api_client  │                │
│  │ (Template) │   │ (AI Chat)│   │(HTTP Client)│                │
│  └───┬────────┘   └──────────┘   └──────┬──────┘                │
│      │                                  │                       │
│  ┌───▼──────────────────────────────────▼────────────────────┐  │
│  │                    Tool Modules                           │  │
│  │                                                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │  │
│  │  │ Network  │  │   Port   │  │   Hash   │  │   RSA    │   │  │
│  │  │ Scanner  │  │ Scanner  │  │  Module  │  │ Encrypt  │   │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │  │
│  │                                                           │  │
│  │  ┌──────────┐  ┌──────────┐                               │  │
│  │  │   Hash   │  │  Arcade  │                               │  │
│  │  │  Crack   │  │  (Games) │                               │  │
│  │  └──────────┘  └──────────┘                               │  │
│  └───────────────────────────────────────────────────────────┘  │ 
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Backend Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Backend Layer                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   api_server.py                            │ │
│  │                  (Flask Application)                       │ │
│  │                                                            │ │
│  │  - Route handlers                                          │ │
│  │  - Request validation                                      │ │
│  │  - Response formatting                                     │ │
│  │  - Error handling                                          │ │
│  │  - CORS configuration                                      │ │
│  └───┬─────────────┬────────────┬─────────────┬───────────────┘ │
│      │             │            │             │                 │
│  ┌───▼────────┐ ┌──▼──────┐ ┌───▼────────┐ ┌──▼──────────┐      │
│  │   Hash     │ │Network  │ │ Password   │ │ Ask-Gilfi   │      │
│  │  Module    │ │ Module  │ │  Analyzer  │ │   Module    │      │
│  └───┬────────┘ └──┬──────┘ └───┬────────┘ └──┬──────────┘      │
│      │             │            │             │                 │
│  ┌───▼────────────────────────────────────────▼──────────────┐  │
│  │                    hash_lib Package                       │  │
│  │                                                           │  │
│  │  ┌──────────┐  ┌───────────┐  ┌──────────┐                │  │
│  │  │  Hasher  │  │Identifier │  │ Cracker  │                │  │
│  │  │ (hash_   │  │ (hash_    │  │ (hash_   │                │  │
│  │  │  core)   │  │identifier)│  │ cracker) │                │  │
│  │  └──────────┘  └───────────┘  └──────────┘                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 password_lib Package                       │ │
│  │                                                            │ │
│  │  ┌───────────────────────────────────────────────────────┐ │ │
│  │  │              PasswordAnalyzer                         │ │ │
│  │  │  - analyze()                                          │ │ │
│  │  │  - generate_report()                                  │ │ │
│  │  │  - Pattern detection (regex)                          │ │ │
│  │  └───────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   RSA Module (C)                           │ │
│  │                                                            │ │
│  │  - Prime generation                                        │ │
│  │  - Key pair generation                                     │ │
│  │  - Encryption/Decryption                                   │ │
│  │  - Modular exponentiation                                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Class Diagrams

### 5.1 Frontend Class Diagram

```mermaid
classDiagram
    class QApplication {
        <<PyQt6>>
    }
    
    class MainWindow {
        -QListWidget nav_list
        -QStackedWidget stack
        -QDockWidget chat_dock
        -ChatWidget chat_widget
        -QPushButton chat_toggle
        +setup_menubar()
        +setup_central()
        +setup_chatbot_dock()
        +register_tools()
        +add_tool(name, page)
        +toggle_chatbot()
    }
    
    class ToolPage {
        -str title
        -str description
        -dict fields
        -QTextEdit output_text
        -QPushButton btn_run
        -callable on_run
        +add_field(label, placeholder)
        +get_input(label) str
        +append_output(text)
        +clear_output()
        +set_status(text, error)
        +handle_run()
    }
    
    class ChatWidget {
        -ChatWorker worker
        -QTextEdit chat_display
        -QLineEdit input_field
        -QPushButton btn_send
        +send_message()
        -on_token(token)
        -on_error(msg)
        -on_finished()
    }
    
    class ChatWorker {
        -str prompt
        +token_received : Signal
        +finished : Signal
        +error_occurred : Signal
        +run()
    }
    
    class GilfiAPIClient {
        -str base_url
        -int timeout
        +health_check() dict
        +hash_generate(text, algo) dict
        +hash_identify(hash) dict
        +hash_crack(hash, wordlist, algo) dict
        +rsa_encrypt(plaintext) dict
        +askgilfi_query(prompt) dict
        -_request(method, endpoint) dict
    }
    
    class NetworkScanner {
        +create_page() ToolPage
        +run(page)
    }
    
    class PortScanner {
        +create_page() ToolPage
        +run(page)
    }
    
    class HashModule {
        +create_page() ToolPage
        +run(page)
    }
    
    class HashCrackModule {
        +create_page() ToolPage
        +run(page)
    }
    
    class RSAEncryption {
        +create_page() ToolPage
        +run(page)
    }
    
    class ArcadeWidget {
        -QTabWidget tabs
        +create_page() QWidget
    }
    
    QApplication --> MainWindow : creates
    MainWindow *-- ToolPage : contains
    MainWindow *-- ChatWidget : contains
    MainWindow --> GilfiAPIClient : uses
    ChatWidget *-- ChatWorker : creates
    ToolPage <|-- NetworkScanner : implements
    ToolPage <|-- PortScanner : implements
    ToolPage <|-- HashModule : implements
    ToolPage <|-- HashCrackModule : implements
    ToolPage <|-- RSAEncryption : implements
    NetworkScanner --> GilfiAPIClient : uses
    PortScanner --> GilfiAPIClient : uses
    HashModule --> GilfiAPIClient : uses
    HashCrackModule --> GilfiAPIClient : uses
    RSAEncryption --> GilfiAPIClient : uses
```

### 5.2 Backend Class Diagram

```mermaid
classDiagram
    class Flask {
        <<Framework>>
        +route(path)
        +run(host, port)
    }
    
    class APIServer {
        +app : Flask
        +health_check() dict
        +hash_generate() dict
        +hash_identify() dict
        +hash_crack() dict
        +rsa_encrypt() dict
        +askgilfi_query() dict
        +list_modules() dict
    }
    
    class Hasher {
        +hash(text, algorithm) str
        +supported_algorithms() list
    }
    
    class HashIdentifier {
        +identify(hash_value) list
        -_check_length(hash) list
        -_check_format(hash) list
    }
    
    class Cracker {
        +crack(hash, wordlist, algo) str
        -_hash_word(word, algo) str
        -_compare_hashes(target, candidate) bool
    }
    
    class PasswordAnalyzer {
        +PATTERNS : dict
        +COMMON_PASSWORDS : set
        +analyze(password) dict
        +generate_report(password) str
        +get_strength_description(strength) str
        -_create_result(...) dict
    }
    
    class PasswordStrength {
        <<enumeration>>
        VERY_WEAK
        WEAK
        MODERATE
        STRONG
        VERY_STRONG
    }
    
    class RSAModule {
        <<C Binary>>
        +generate_keys()
        +encrypt(plaintext, public_key)
        +decrypt(ciphertext, private_key)
    }
    
    class AskGilfiModule {
        +start_gilfi() Process
        +ask_gilfi(prompt) str
        -_stream_response(prompt) Generator
    }
    
    Flask <|-- APIServer : extends
    APIServer --> Hasher : uses
    APIServer --> HashIdentifier : uses
    APIServer --> Cracker : uses
    APIServer --> PasswordAnalyzer : uses
    APIServer --> RSAModule : executes
    APIServer --> AskGilfiModule : uses
    PasswordAnalyzer --> PasswordStrength : uses
    Hasher ..> HashIdentifier : provides data
    HashIdentifier ..> Cracker : identifies for
```

### 5.3 Hash Module Class Diagram (Detailed)

```mermaid
classDiagram
    class Hasher {
        +hash(text: str, algorithm: str) str
        +supported_algorithms() list~str~
        -_validate_algorithm(algo: str) bool
    }
    
    class HashIdentifier {
        +HASH_PATTERNS : dict
        +identify(hash_value: str) list~str~
        -_check_md5(hash: str) bool
        -_check_sha1(hash: str) bool
        -_check_sha256(hash: str) bool
        -_check_sha512(hash: str) bool
        -_is_hex(value: str) bool
    }
    
    class Cracker {
        +crack(hash: str, wordlist: str, algo: str) Optional~str~
        +crack_with_progress(hash, wordlist, algo) Generator
        -_load_wordlist(path: str) Generator
        -_hash_word(word: str, algo: str) str
        -_compare(target: str, candidate: str) bool
    }
    
    class HashType {
        <<enumeration>>
        MD5
        SHA1
        SHA224
        SHA256
        SHA384
        SHA512
        BCRYPT
        ARGON2
    }
    
    Hasher --> HashType : uses
    HashIdentifier --> HashType : returns
    Cracker --> Hasher : uses for hashing
    Cracker --> HashIdentifier : uses for validation
```

---

## 6. Sequence Diagrams

### 6.1 Hash Generation Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend UI
    participant API as API Client
    participant Backend as Flask Server
    participant Hasher as Hash Module
    
    User->>UI: Enter text "password"
    User->>UI: Select algorithm "SHA-256"
    User->>UI: Click "Generate"
    
    UI->>UI: Validate input
    UI->>API: hash_generate("password", "sha256")
    API->>Backend: POST /api/hash/generate
    Note over API,Backend: JSON: {"text": "password", "algorithm": "sha256"}
    
    Backend->>Backend: Validate request
    Backend->>Hasher: hash("password", "sha256")
    Hasher->>Hasher: Calculate SHA-256
    Hasher-->>Backend: "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    
    Backend-->>API: JSON response
    Note over Backend,API: {"success": true, "hash": "5e88..."}
    API-->>UI: Return hash
    UI->>UI: Display hash
    UI->>User: Show result
```

### 6.2 Hash Cracking Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend UI
    participant API as API Client
    participant Backend as Flask Server
    participant Cracker as Hash Cracker
    participant FS as File System
    
    User->>UI: Enter hash
    User->>UI: Select algorithm
    User->>UI: Click "Crack"
    
    UI->>API: hash_crack(hash, wordlist, algo)
    API->>Backend: POST /api/hash/crack
    
    Backend->>Backend: Validate request
    Backend->>Cracker: crack(hash, wordlist, algo)
    
    Cracker->>FS: Open wordlist file
    FS-->>Cracker: File handle
    
    loop For each word in wordlist
        Cracker->>Cracker: hash_word(word, algo)
        Cracker->>Cracker: compare(target, candidate)
        alt Match found
            Cracker-->>Backend: Return plaintext
        end
    end
    
    alt Password found
        Backend-->>API: {"cracked": true, "plaintext": "password"}
        API-->>UI: Return result
        UI->>User: Display "Cracked: password"
    else Not found
        Backend-->>API: {"cracked": false}
        API-->>UI: Return result
        UI->>User: Display "Not found"
    end
```

### 6.3 Port Scanning Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend UI
    participant API as API Client
    participant Backend as Flask Server
    participant Network as Network Module
    participant Target as Target System
    
    User->>UI: Enter target IP
    User->>UI: Enter port range
    User->>UI: Click "Scan"
    
    UI->>API: port_scan(target, ports)
    API->>Backend: POST /api/network/port-scan
    
    Backend->>Network: scan_ports(target, ports)
    
    loop For each port
        Network->>Target: TCP Connect (port)
        alt Port open
            Target-->>Network: Connection accepted
            Network->>Network: Identify service
            Network->>UI: Update progress
        else Port closed
            Target-->>Network: Connection refused
        end
    end
    
    Network-->>Backend: Scan results
    Backend-->>API: JSON response
    API-->>UI: Return results
    UI->>User: Display open ports
```

### 6.4 AI Chatbot Interaction Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Chat Widget
    participant Worker as Chat Worker
    participant API as API Client
    participant Backend as Flask Server
    participant Ollama as Ollama Service
    
    User->>UI: Type question
    User->>UI: Press Enter
    
    UI->>UI: Disable input
    UI->>Worker: Create ChatWorker(prompt)
    UI->>Worker: Start thread
    
    Worker->>API: askgilfi_query(prompt)
    API->>Backend: POST /api/askgilfi/query
    
    Backend->>Backend: Get/start Ollama process
    Backend->>Ollama: POST /api/generate
    
    loop Stream response
        Ollama-->>Backend: Token chunk
        Backend-->>API: Token chunk
        API-->>Worker: Token chunk
        Worker->>UI: Emit token_received signal
        UI->>UI: Append token to display
    end
    
    Ollama-->>Backend: Stream complete
    Backend-->>API: Full response
    API-->>Worker: Response complete
    Worker->>UI: Emit finished signal
    UI->>UI: Enable input
    UI->>User: Show complete response
```

### 6.5 Password Analysis Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Frontend UI
    participant Analyzer as Password Analyzer
    
    User->>UI: Enter password
    User->>UI: Click "Analyze"
    
    UI->>Analyzer: analyze(password)
    
    Analyzer->>Analyzer: Check length
    Analyzer->>Analyzer: Check character variety
    Analyzer->>Analyzer: Check for patterns
    Analyzer->>Analyzer: Check against common passwords
    Analyzer->>Analyzer: Calculate score
    Analyzer->>Analyzer: Determine strength level
    Analyzer->>Analyzer: Generate suggestions
    
    Analyzer-->>UI: Analysis result
    Note over Analyzer,UI: {strength, score, checks, suggestions}
    
    UI->>UI: Display strength meter
    UI->>UI: Display score
    UI->>UI: Display checks (✓/✗)
    UI->>UI: Display suggestions
    UI->>User: Show complete analysis
```

---

## 7. Deployment Architecture

### 7.1 Development Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Machine                        │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Frontend (Native)                                     │ │
│  │  python src/frontend/main.py                           │ │
│  │  Port: N/A (native GUI)                                │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │ HTTP                                │
│                       │ localhost:8000                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │  Backend (Native or Docker)                            │ │
│  │  python src/backend/api_server.py                      │ │
│  │  OR: docker-compose up                                 │ │
│  │  Port: 8000                                            │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │ HTTP                                │
│                       │ localhost:11436                     │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │  Ollama (Optional)                                     │ │
│  │  ollama serve                                          │ │
│  │  Port: 11436                                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Production Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                      User Machine                           │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Frontend (Installed Application)                      │ │
│  │  Gilfi.exe / Gilfi.app / gilfi                         │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │ HTTP                                │
│                       │ localhost:8000                      │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │  Backend (Docker Container)                            │ │
│  │  gilfi-backend:latest                                  │ │
│  │  - Auto-starts on system boot                          │ │
│  │  - Health monitoring                                   │ │
│  │  - Auto-restart on failure                             │ │
│  │  Port: 8000                                            │ │
│  │                                                        │ │
│  │  Includes:                                             │ │
│  │  - Flask API Server                                    │ │
│  │  - All security modules                                │ │
│  │  - Ollama service                                      │ │
│  │  - Wordlist data                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 Deployment Diagram

```mermaid
graph TB
    subgraph "User Machine"
        subgraph "Frontend Process"
            FE[PyQt6 Application]
        end
        
        subgraph "Docker Container"
            BE[Flask API Server]
            HM[Hash Module]
            PM[Password Module]
            NM[Network Module]
            RM[RSA Module]
            AM[Ask-Gilfi Module]
            OL[Ollama Service]
        end
        
        subgraph "File System"
            WL[Wordlist Data]
            CF[Config Files]
        end
    end
    
    FE -->|HTTP:8000| BE
    BE --> HM
    BE --> PM
    BE --> NM
    BE --> RM
    BE --> AM
    AM -->|HTTP:11436| OL
    BE -->|Read| WL
    BE -->|Read| CF
```

---

## 8. Data Flow

### 8.1 Request-Response Flow

```
User Input → Frontend Validation → API Client → HTTP Request →
Backend Validation → Module Processing → Response Generation →
HTTP Response → API Client → Frontend Display → User Output
```

### 8.2 Data Flow Diagram

```mermaid
flowchart LR
    U[User] -->|Input| FE[Frontend]
    FE -->|Validate| FE
    FE -->|HTTP Request| API[API Client]
    API -->|REST Call| BE[Backend]
    BE -->|Validate| BE
    BE -->|Process| MOD[Module]
    MOD -->|Result| BE
    BE -->|Format| BE
    BE -->|HTTP Response| API
    API -->|Parse| FE
    FE -->|Display| U
```

### 8.3 Error Flow

```mermaid
flowchart TD
    START[Operation Start] --> VAL{Input Valid?}
    VAL -->|No| ERR1[Show Validation Error]
    VAL -->|Yes| CONN{Backend Connected?}
    CONN -->|No| ERR2[Show Connection Error]
    CONN -->|Yes| PROC[Process Request]
    PROC --> EXEC{Execution Success?}
    EXEC -->|No| ERR3[Show Processing Error]
    EXEC -->|Yes| RESULT[Return Result]
    ERR1 --> END[End]
    ERR2 --> END
    ERR3 --> END
    RESULT --> END
```

---

## 9. Technology Stack

### 9.1 Frontend Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| GUI Framework | PyQt6 | 6.11.0 | User interface |
| Language | Python | 3.8+ | Application logic |
| HTTP Client | Requests | 2.33.1 | API communication |
| Threading | QThread | Built-in | Async operations |
| Styling | QSS | Built-in | UI theming |

### 9.2 Backend Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Web Framework | Flask | 3.1.0 | REST API |
| Language | Python | 3.11 | Business logic |
| CORS | Flask-CORS | Latest | Cross-origin support |
| Cryptography | hashlib | Built-in | Hash operations |
| Networking | socket | Built-in | Network operations |
| AI Runtime | Ollama | Latest | LLM inference |

### 9.3 Infrastructure Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Container Runtime | Docker/Podman | Backend deployment |
| Base Image | python:3.11-slim | Container base |
| Orchestration | Docker Compose | Multi-container setup |
| Build Tool | GCC | RSA module compilation |

### 9.4 Development Stack

| Tool | Purpose |
|------|---------|
| Git | Version control |
| pytest | Unit testing |
| Black | Code formatting |
| Flake8 | Linting |
| mypy | Type checking |

---

## 10. Architecture Decisions

### 10.1 Key Decisions

#### Decision 1: Client-Server Architecture
**Rationale**: Separates concerns, enables independent scaling, facilitates testing

#### Decision 2: RESTful API
**Rationale**: Standard protocol, language-agnostic, easy to test and document

#### Decision 3: Docker Containerization
**Rationale**: Consistent deployment, dependency isolation, easy distribution

#### Decision 4: Modular Backend
**Rationale**: Independent development, easy testing, flexible deployment

#### Decision 5: PyQt6 for GUI
**Rationale**: Cross-platform, native look, rich widget set, Python integration

### 10.2 Trade-offs

| Decision | Advantages | Disadvantages |
|----------|-----------|---------------|
| Client-Server | Scalability, separation | Network dependency |
| Docker Backend | Consistency, isolation | Overhead, complexity |
| Python | Rapid development, libraries | Performance vs compiled |
| Local AI | Privacy, offline | Resource intensive |

---

**Document Version**: 1.0  
**Last Updated**: 2026-04-28  
**Next Review**: 2026-05-28