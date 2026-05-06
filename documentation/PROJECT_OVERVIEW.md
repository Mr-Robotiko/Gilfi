# Gilfi - Project Overview

## Executive Summary

Gilfi is a comprehensive security and network analysis toolkit designed to provide cybersecurity professionals, students, and enthusiasts with a unified platform for performing various security assessments and cryptographic operations. The project combines modern software engineering practices with practical security tools, wrapped in an intuitive PyQt6 graphical user interface.

## Project Vision

To create an educational and professional-grade security toolkit that:
- **Democratizes Security Tools**: Makes advanced security analysis accessible to users of all skill levels
- **Promotes Learning**: Provides an interactive environment for understanding cryptography and network security
- **Ensures Quality**: Follows software engineering best practices with comprehensive testing and documentation
- **Maintains Modularity**: Enables easy extension and maintenance through clean architecture

## Project Goals

### Primary Goals
1. **Comprehensive Security Toolkit**: Provide a complete suite of security analysis tools in one application
2. **User-Friendly Interface**: Deliver an intuitive GUI that doesn't compromise on functionality
3. **Educational Value**: Help users understand security concepts through practical application
4. **Professional Quality**: Meet industry standards for code quality, testing, and documentation

### Secondary Goals
1. **Cross-Platform Support**: Run seamlessly on Windows, macOS, and Linux
2. **Containerized Deployment**: Simplify deployment through Docker/Podman containers
3. **AI Integration**: Provide intelligent assistance through an AI-powered chatbot
4. **Extensibility**: Allow easy addition of new security modules

## Key Features

### 1. Network Analysis
- **Network Scanner**: Discover active devices on local networks
- **Port Scanner**: Identify open ports and running services
- **Hostname Resolution**: Resolve IP addresses to hostnames and vice versa

### 2. Cryptographic Operations
- **Hash Generation**: Create hashes using MD5, SHA-1, SHA-256, SHA-512, and more
- **Hash Identification**: Automatically identify hash types based on patterns
- **Hash Cracking**: Advanced dictionary-based attacks with 60+ transformation rules
  - Wordlist shuffler inspired by Hashcat and John the Ripper
  - Case variations, leet speak, number/special character appending
  - Dual-layer caching (in-memory + SQLite) for performance
  - Multiprocessing support for parallel cracking
- **RSA Encryption**: Encrypt and decrypt messages using RSA cryptography

### 3. Password Security
- **Password Analysis**: Evaluate password strength using multiple criteria
  - Scoring system (0-100 points)
  - Character variety analysis
  - Pattern detection (consecutive chars, sequential numbers/letters)
  - Common password checking
  - Entropy calculation
- **Password Generation**: Create cryptographically secure random passwords
  - Customizable length (8-128 characters)
  - Configurable character sets (lowercase, uppercase, digits, special)
  - Ambiguous character exclusion option
  - Automatic strength analysis
- **Security Recommendations**: Provide actionable suggestions for improvement

### 4. AI Assistant
- **Ask Gilfi**: AI-powered chatbot for security-related questions
- **Context-Aware**: Understands security concepts and provides relevant guidance
- **Local Processing**: Runs locally using Ollama for privacy

### 5. Interactive Learning
- **Arcade Mode**: Four mini-games that teach security concepts
  - Crack the Code: Caesar cipher puzzle
  - Hash Hunter: Hash identification game
  - Survive the Cracker: Password strength challenge
  - Factorize: RSA key factorization demonstration

## Technical Architecture

### Architecture Pattern
Gilfi follows a **client-server architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                       │
│              (PyQt6 Desktop Application)                │
│  - User Interface                                       │
│  - Input Validation                                     │
│  - Result Visualization                                 │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
                     │ (localhost:8000)
┌────────────────────▼────────────────────────────────────┐
│                    Backend Layer                        │
│                (Flask REST API Server)                  │
│  - Request Processing                                   │
│  - Business Logic                                       │
│  - Module Orchestration                                 │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┐
        │            │            │            │
┌───────▼──────┐ ┌───▼─────┐ ┌────▼────┐ ┌─────▼──────┐
│ Hash Module  │ │ Network │ │Password │ │ Ask-Gilfi  │
│              │ │ Module  │ │Analyzer │ │  Module    │
└──────────────┘ └─────────┘ └─────────┘ └────────────┘
```

### Technology Stack

#### Frontend
- **Framework**: PyQt6 6.11.0
- **Language**: Python 3.8+
- **HTTP Client**: Requests 2.33.1
- **Threading**: QThread for async operations

#### Backend
- **Framework**: Flask 3.1.0
- **Language**: Python 3.11
- **CORS**: Flask-CORS for cross-origin requests
- **Container**: Docker with Python slim base image

#### Modules
- **Hash Module**: Pure Python implementation
- **RSA Module**: C implementation for performance
- **Password Analyzer**: Python with regex patterns
- **Network Module**: Python socket programming
- **Ask-Gilfi**: Ollama integration with custom model

### Design Principles

1. **Separation of Concerns**: Frontend and backend are completely independent
2. **Modularity**: Each security tool is a self-contained module
3. **Scalability**: RESTful API allows for distributed deployment
4. **Testability**: Comprehensive test coverage at all levels
5. **Maintainability**: Clear code structure with extensive documentation

## Project Structure

```
Gilfi/
├── src/
│   ├── backend/                    # Backend API server
│   │   ├── api_server.py          # Main Flask application
│   │   ├── hash-module/           # Hash operations
│   │   ├── password-analyzer-module/  # Password analysis
│   │   ├── networking-module/     # Network tools
│   │   └── ask-gilfi-module/      # AI chatbot
│   └── frontend/                   # PyQt6 GUI application
│       ├── main.py                # Application entry point
│       ├── api_client.py          # Backend communication
│       ├── modules/               # Tool implementations
│       └── ui/                    # UI components
├── tests/                         # Test suites
│   ├── infrastructure/            # Integration tests
│   └── unit/                      # Unit tests
├── documentation/                 # Project documentation
│   ├── architecture/              # Architecture diagrams
│   ├── api/                       # API specifications
│   ├── user-stories/              # User stories
│   └── guides/                    # User and developer guides
├── data/                          # Application data
│   ├── wordlist/                  # Password wordlists
│   └── assets/                    # Images and resources
└── docker-compose.backend.yaml    # Container orchestration
```

## Target Audience

### Primary Users
1. **Cybersecurity Students**: Learning security concepts and tools
2. **Security Professionals**: Performing quick security assessments
3. **Penetration Testers**: Conducting authorized security testing
4. **System Administrators**: Analyzing network and system security

### Secondary Users
1. **Developers**: Understanding cryptographic implementations
2. **Educators**: Teaching security concepts with practical examples
3. **Hobbyists**: Exploring cybersecurity as a personal interest

## Success Criteria

### Functional Requirements
- ✅ All security tools work correctly and reliably
- ✅ Frontend communicates seamlessly with backend
- ✅ AI chatbot provides relevant and accurate responses
- ✅ Cross-platform compatibility (Windows, macOS, Linux)

### Non-Functional Requirements
- ✅ Response time < 2 seconds for most operations
- ✅ Hash cracking performance: 1M+ hashes/second (basic mode)
- ✅ Hash cracking with rules: 60+ transformations per word
- ✅ API timeout: 5 minutes for large wordlist operations
- ✅ Memory usage < 500MB for frontend
- ✅ Backend container size < 1GB

### Quality Requirements
- ✅ Test coverage > 80%
- ✅ Zero critical security vulnerabilities
- ✅ Comprehensive documentation
- ✅ Clean code with consistent style

## Development Methodology

### Agile Approach
- **Iterative Development**: Features developed in sprints
- **User Stories**: Requirements captured as user stories
- **Continuous Integration**: Automated testing on commits
- **Regular Reviews**: Code reviews and retrospectives

### Version Control
- **Git**: Distributed version control
- **Branching Strategy**: Feature branches with main/develop
- **Commit Standards**: Conventional commits format

### Quality Assurance
- **Unit Testing**: pytest for Python modules
- **Integration Testing**: End-to-end API tests
- **Manual Testing**: UI/UX validation
- **Code Review**: Peer review before merging

## Future Roadmap

### Phase 1 (Completed - v1.1.0)
- ✅ Core security tools implementation
- ✅ Basic GUI with all modules
- ✅ Docker containerization
- ✅ AI chatbot integration
- ✅ Advanced hash cracking with 60+ transformation rules
- ✅ Password analyzer with strength scoring
- ✅ Cryptographically secure password generator
- ✅ Dual-layer caching for performance optimization
- ✅ Multiprocessing support for parallel operations

### Phase 2 (Planned)
- 🔄 Advanced network scanning (OS detection, vulnerability scanning)
- 🔄 Additional hash algorithms (bcrypt, Argon2)
- 🔄 Report generation (PDF/HTML exports)
- 🔄 Plugin system for custom modules
- 🔄 Password breach database integration
- 🔄 Custom wordlist management

### Phase 3 (Future)
- 📋 Web-based interface option
- 📋 Multi-user support with authentication
- 📋 Cloud deployment options
- 📋 Mobile companion app

## License and Legal

### License
This project is released under the terms specified in the LICENSE file.

### Ethical Use
Gilfi is designed for:
- ✅ Educational purposes
- ✅ Authorized security testing
- ✅ Personal password management
- ✅ Network administration

**NOT for:**
- ❌ Unauthorized access to systems
- ❌ Malicious activities
- ❌ Privacy violations
- ❌ Illegal purposes

### Disclaimer
Users are responsible for ensuring their use of Gilfi complies with all applicable laws and regulations. The developers assume no liability for misuse of this software.

**Document Version**: 1.1
**Last Updated**: 2026-05-06
**Status**: Active Development

---

## Recent Updates (v1.1.0 - 2026-05-06)

### Hash Cracking Enhancements
- **Wordlist Shuffler**: Implemented 60+ transformation rules inspired by Hashcat and John the Ripper
  - Case variations (capitalize, uppercase, lowercase, alternate case)
  - Leet speak transformations (o→0, e→3, a→4, i→1, s→5, t→7)
  - Number appending (1, 123, 2024, 99, etc.)
  - Special character appending (!, @, #, $, !!, $$, etc.)
  - Word manipulations (reverse, double, wrap with special chars)
  - Advanced combinations (xXwordXx, Word1!, M0nk3y2026, etc.)
- **Performance Optimizations**:
  - Dual-layer caching (in-memory + SQLite)
  - LRU cache for transformation results
  - Batch processing (10,000 words per batch)
  - Early termination on match
  - Multiprocessing support for parallel cracking
- **API Enhancements**:
  - Increased timeout to 5 minutes for large wordlist operations
  - Added `use_rules`, `use_multiprocessing`, and `batch_size` parameters

### Password Security Module
- **Password Analyzer**:
  - Comprehensive strength analysis (0-100 scoring)
  - Five strength levels (VERY_WEAK to VERY_STRONG)
  - Character variety analysis
  - Pattern detection (consecutive, sequential, common patterns)
  - Common password database (20+ weak passwords)
  - Entropy calculation
  - Actionable improvement suggestions
- **Password Generator**:
  - Cryptographically secure random generation using `secrets` module
  - Customizable length (8-128 characters)
  - Configurable character sets (lowercase, uppercase, digits, special)
  - Ambiguous character exclusion (0/O, 1/l/I)
  - Automatic strength analysis of generated passwords
  - Character set diversity enforcement

### GUI Enhancements
- **Password Analyzer & Generator Widget**:
  - Dual functionality (analyze existing or generate new passwords)
  - Visual progress bars for strength indicators
  - Color-coded strength levels
  - Detailed security checks display
  - Actionable suggestions panel
  - Copy-to-clipboard functionality

### Documentation Updates
- Updated API specification with new endpoints
- Enhanced hash module documentation with rule descriptions
- Created comprehensive password analyzer module README
- Updated project overview with latest features
- Added version history and changelog