# Gilfi

## ✨ Gilfi is a swiss army knife for Crypto and Pentesting

## 📌 Table of Contents

## Installation

Go to the [Releases](https://github.com/Mr-Robotiko/Gilfi/releases) page of Gilfi.

> [!IMPORTANT]
> You need to have [Podman](https://podman.io/docs/installation) installed in order to install Gilfi. From there, it's easy.

## Project Architecture

### High-Level System Flowchart

```mermaid
flowchart TB
    subgraph User["👤 User Interface"]
        UI[PyQt6 Desktop Application<br/>Cross-Platform GUI]
    end
    
    subgraph Frontend["🖥️ Frontend Layer (src/frontend/)"]
        Main[main.py<br/>Application Entry]
        MainWindow[mainwindow.py<br/>Main Window]
        APIClient[api_client.py<br/>HTTP Client]
        
        subgraph Modules["Frontend Modules"]
            HashMod[hash_module.py]
            HashCrack[hash_crack_module.py]
            PortScan[port_scanner.py]
            NetScan[network_scanner.py]
            RSAMod[rsa_encryption.py]
        end
        
        subgraph UIComponents["UI Components"]
            ChatWidget[chatwidget.py<br/>Ask-Gilfi Chat]
            ToolPage[toolpage.py<br/>Tool Pages]
            Style[style.py<br/>Styling]
        end
    end
    
    subgraph Backend["⚙️ Backend Layer (src/backend/)"]
        API[api_server.py<br/>Flask REST API<br/>Port 8000]
        
        subgraph HashModule["Hash Module"]
            Hasher[Hasher<br/>Generate Hashes]
            Identifier[HashIdentifier<br/>Identify Types]
            Cracker[Cracker<br/>Crack Hashes]
        end
        
        subgraph CryptoModule["Crypto Module"]
            RSA[RSA Module<br/>C Binary<br/>Encryption/Decryption]
        end
        
        subgraph AIModule["AI Module"]
            AskGilfi[ask-gilfi-chat.py<br/>AI Assistant]
            Ollama[Ollama Server<br/>granite4:350m]
        end
    end
    
    subgraph Data["💾 Data Layer"]
        Cache[(SQLite Cache<br/>hash_cache.db)]
        Wordlist[(Wordlist<br/>rockyou.txt)]
        Models[(AI Models<br/>Ollama Models)]
    end
    
    subgraph Docker["🐳 Docker Infrastructure"]
        Container[Backend Container<br/>Python 3.11 Slim]
        Compose[Docker Compose<br/>Orchestration]
    end
    
    %% User to Frontend
    User -->|Interacts| UI
    UI --> Main
    Main --> MainWindow
    MainWindow --> UIComponents
    MainWindow --> Modules
    
    %% Frontend to Backend
    Modules -->|HTTP/REST| APIClient
    ChatWidget -->|HTTP/REST| APIClient
    APIClient -->|JSON Requests| API
    
    %% Backend API Routes
    API -->|/api/hash/generate| Hasher
    API -->|/api/hash/identify| Identifier
    API -->|/api/hash/crack| Cracker
    API -->|/api/rsa/encrypt| RSA
    API -->|/api/askgilfi/query| AskGilfi
    
    %% Backend Internal
    Cracker --> Hasher
    Cracker --> Identifier
    AskGilfi --> Ollama
    
    %% Data Access
    Cracker <-->|Read/Write| Cache
    Cracker -->|Read| Wordlist
    Ollama -->|Load| Models
    
    %% Docker
    API -.->|Runs in| Container
    HashModule -.->|Runs in| Container
    RSA -.->|Compiled in| Container
    AskGilfi -.->|Runs in| Container
    Container -.->|Managed by| Compose
    
    %% Styling
    style User fill:#e3f2fd
    style UI fill:#bbdefb
    style Frontend fill:#fff3e0
    style Backend fill:#e8f5e9
    style Data fill:#fff9c4
    style Docker fill:#f3e5f5
    style API fill:#a5d6a7
    style Hasher fill:#c8e6c9
    style Identifier fill:#c8e6c9
    style Cracker fill:#c8e6c9
    style RSA fill:#ce93d8
    style AskGilfi fill:#f48fb1
    style Ollama fill:#f8bbd0
```

### Detailed Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant HashModule
    participant RSAModule
    participant AskGilfi
    participant Database
    
    Note over User,Database: Example: Hash Cracking Flow
    
    User->>Frontend: Enter hash to crack
    Frontend->>API: POST /api/hash/crack<br/>{hash, wordlist, algorithm}
    
    API->>HashModule: Initialize Cracker
    HashModule->>Database: Check cache for hash
    
    alt Hash found in cache
        Database-->>HashModule: Return cached plaintext
        HashModule-->>API: Return result
    else Hash not in cache
        HashModule->>HashModule: Identify hash type
        HashModule->>Database: Read wordlist
        loop For each word
            HashModule->>HashModule: Generate hash
            HashModule->>HashModule: Compare with target
        end
        HashModule->>Database: Save to cache
        HashModule-->>API: Return cracked result
    end
    
    API-->>Frontend: JSON response
    Frontend-->>User: Display result
    
    Note over User,Database: Example: RSA Encryption Flow
    
    User->>Frontend: Enter plaintext number
    Frontend->>API: POST /api/rsa/encrypt<br/>{plaintext}
    API->>RSAModule: Execute C binary
    RSAModule->>RSAModule: Generate prime numbers
    RSAModule->>RSAModule: Calculate keys
    RSAModule->>RSAModule: Encrypt & Decrypt
    RSAModule-->>API: Return keys & ciphertext
    API-->>Frontend: JSON response
    Frontend-->>User: Display encryption result
    
    Note over User,Database: Example: Ask-Gilfi Query Flow
    
    User->>Frontend: Ask security question
    Frontend->>API: POST /api/askgilfi/query<br/>{prompt}
    API->>AskGilfi: Start Ollama server
    AskGilfi->>AskGilfi: Load granite4:350m model
    AskGilfi->>AskGilfi: Process prompt
    AskGilfi-->>API: Stream response
    API-->>Frontend: JSON response
    Frontend-->>User: Display AI answer
```

### Component Interaction Map

```mermaid
graph LR
    subgraph "Client Side"
        A[Desktop Application<br/>PyQt6]
    end
    
    subgraph "Communication Layer"
        B[HTTP/REST API<br/>Port 8000]
    end
    
    subgraph "Backend Services"
        C1[Hash Operations]
        C2[RSA Crypto]
        C3[AI Assistant]
        C4[Network Tools]
    end
    
    subgraph "Data Storage"
        D1[(Hash Cache)]
        D2[(Wordlists)]
        D3[(AI Models)]
    end
    
    A <-->|JSON| B
    B --> C1
    B --> C2
    B --> C3
    B --> C4
    
    C1 <--> D1
    C1 --> D2
    C3 --> D3
    
    style A fill:#4fc3f7
    style B fill:#81c784
    style C1 fill:#aed581
    style C2 fill:#aed581
    style C3 fill:#aed581
    style C4 fill:#aed581
    style D1 fill:#fff59d
    style D2 fill:#fff59d
    style D3 fill:#fff59d
```

### Technology Stack Overview

```mermaid
mindmap
  root((Gilfi))
    Frontend
      PyQt6
        Desktop GUI
        Cross-Platform
      Python 3.11
        API Client
        Module Integration
    Backend
      Flask 3.1.0
        REST API
        CORS Support
      Python Modules
        Hash Operations
        Cryptography
      C Modules
        RSA Implementation
      AI Integration
        Ollama
        granite4:350m
    Infrastructure
      Docker
        Containerization
        Isolation
      Docker Compose
        Orchestration
        Volume Management
    Data
      SQLite
        Hash Caching
      Wordlists
        rockyou.txt
      AI Models
        Custom Training
```

### Deployment Architecture

```mermaid
flowchart TB
    subgraph Host["Host Machine"]
        subgraph FrontendProc["Frontend Process"]
            GUI[PyQt6 Application<br/>Native Window]
        end
        
        subgraph DockerEnv["Docker Environment"]
            subgraph BackendContainer["Backend Container"]
                Flask[Flask API Server<br/>:8000]
                Hash[Hash Module]
                RSA[RSA Binary]
                AI[Ask-Gilfi + Ollama]
            end
            
            subgraph Volumes["Docker Volumes"]
                DataVol[/app/data<br/>Wordlists]
                ModelsVol[/app/backend/ask-gilfi-module/models<br/>AI Models]
            end
        end
    end
    
    GUI -->|HTTP localhost:8000| Flask
    Flask --> Hash
    Flask --> RSA
    Flask --> AI
    Hash --> DataVol
    AI --> ModelsVol
    
    style Host fill:#e1f5fe
    style FrontendProc fill:#b3e5fc
    style DockerEnv fill:#f3e5f5
    style BackendContainer fill:#e1bee7
    style Volumes fill:#fff9c4
```

![structure](documentation/assets/project-structure.png)

### Key Features Flow

1. **Hash Operations**: Generate → Identify → Crack (with caching)
2. **RSA Encryption**: Generate Keys → Encrypt → Decrypt
3. **AI Assistant**: Query → Process → Stream Response
4. **Network Tools**: Scan → Analyze → Report

For detailed class diagrams and technical documentation, see:
- [Backend Architecture](src/backend/README.md)
- [Backend Class Diagrams](documentation/class-diagrams/backend-architecture.md)
- [Frontend Documentation](src/frontend/README.md)

## Features

### AskGilfi 

> [!NOTE]
> The following commands demonstrate how to set up the Podman container for AskGilfi. The installation automation is being developed in the branch `feature/ask-gilfi`.

Install Podman Ollama Container:
```
podman run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```
Pull Granite:
```
podman exec -it ollama ollama run granite4:350m
```
Send request to Granite:
```
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "granite4:350m",
  "prompt": "Erkläre kurz, was ein Large Language Model (LLM) ist.",
  "stream": false
  }'
```

## Architecture Diagram

```
┌─────────────────────────────────────┐
│         Frontend (Local)            │
│                                     │
│  ┌──────────────────────────────┐   │
│  │   PyQt6 GUI Application      │   │
│  │   (src/frontend/main.py)     │   │
│  └──────────────┬───────────────┘   │
│                 │                   │
│  ┌──────────────▼───────────────┐   │
│  │   API Client                 │   │
│  │   (src/frontend/api_client.py)│  │
│  └──────────────┬───────────────┘   │
└─────────────────┼───────────────────┘
                  │ HTTP/REST
                  │ (localhost:8000)
┌─────────────────▼───────────────────┐
│    Backend (Docker Container)       │
│                                     │
│  ┌──────────────────────────────┐   │
│  │   Flask REST API Server      │   │
│  │   (src/backend/api_server.py)│   │
│  └──────────────┬───────────────┘   │
│                 │                   │
│  ┌──────────────▼───────────────┐   │
│  │   Backend Modules:           │   │
│  │   • Hash Module (Python)     │   │
│  │   • RSA Module (C)           │   │
│  │   • Ask-Gilfi (Python+Ollama)│   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```