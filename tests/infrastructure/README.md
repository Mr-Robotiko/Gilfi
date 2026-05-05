# Infrastructure Tests

Comprehensive test suite for Gilfi's Docker backend infrastructure, REST API endpoints, and frontend API client.

## Test Files

### 1. `test_docker_backend.py`
Tests Docker container setup and configuration:
- ✅ Docker/Podman availability
- ✅ Configuration files existence
- ✅ Ollama binaries for all platforms
- ✅ Container startup and health
- ✅ RSA module compilation
- ✅ Environment variables
- ✅ Container logs

**14 test cases**

### 2. `test_api_endpoints.py`
Tests backend REST API functionality:
- ✅ Health check endpoint
- ✅ Modules listing
- ✅ Hash generation (MD5, SHA256)
- ✅ Hash identification
- ✅ Hash cracking
- ✅ RSA encryption/decryption
- ✅ Error handling
- ✅ CORS headers
- ✅ Response times

**15 test cases**

### 3. `test_frontend_client.py`
Tests frontend API client:
- ✅ Client initialization
- ✅ All API methods
- ✅ Convenience functions
- ✅ Error handling
- ✅ Connection error handling
- ✅ Timeout configuration
- ✅ Custom base URL

**15 test cases**

## Running Tests

### Quick Start

**With Conda Environment (Recommended):**
```bash
# Activate the conda environment first
conda activate gilfi

# Run from project root
./tests/infrastructure/run_tests.sh
```

**Or using conda run:**
```bash
conda run -n gilfi ./tests/infrastructure/run_tests.sh
```

**Linux/macOS (without conda):**
```bash
cd tests/infrastructure
./run_tests.sh
```

**Windows:**
```cmd
cd tests\infrastructure
run_tests.bat
```

The test runner will:
1. Detect and use the active conda environment (or venv/system Python)
2. Check if backend is running
3. Start backend if needed
4. Run all test suites from project root
5. Display results
6. Clean up (stop backend if started by script)

### Manual Testing

**With conda environment:**
```bash
conda activate gilfi
cd /path/to/Gilfi
python -m pytest tests/infrastructure/ -v
```

**Run specific test file:**
```bash
python -m pytest tests/infrastructure/test_docker_backend.py -v
python -m pytest tests/infrastructure/test_api_endpoints.py -v
python -m pytest tests/infrastructure/test_frontend_client.py -v
```

**Run specific test:**
```bash
python -m pytest tests/infrastructure/test_docker_backend.py::TestDockerBackend::test_01_docker_available -v
```

**Run with coverage:**
```bash
python -m pytest tests/infrastructure/ --cov=src/backend --cov-report=html
```

## Prerequisites

### Required
- Python 3.8+
- Conda environment with pytest installed, OR
- pytest (`pip install pytest` or `conda install pytest`)
- requests (`pip install requests` or `conda install requests`)

### Conda Environment Setup
```bash
# Create conda environment
conda create -n gilfi python=3.13

# Activate environment
conda activate gilfi

# Install dependencies
pip install pytest requests
pip install -r requirements.txt
```

### Optional (for full test coverage)
- Docker or Podman
- Backend container running

## Test Categories

### Unit Tests
- Client initialization
- Configuration validation
- Error handling

### Integration Tests
- API endpoint communication
- Docker container interaction
- End-to-end workflows

### Infrastructure Tests
- Container startup/shutdown
- Port availability
- File system checks
- Binary permissions

## Expected Results

### With Backend Running
All 44 tests should pass:
- ✅ 14 Docker backend tests
- ✅ 15 API endpoint tests
- ✅ 15 Frontend client tests

### Without Backend
Some tests will be skipped:
- ✅ Docker configuration tests pass
- ⚠️ API tests skipped (backend not available)
- ⚠️ Some client tests skipped

## Troubleshooting

### Backend Not Starting

**Check Docker:**
```bash
docker ps
docker logs gilfi_backend
```

**Check ports:**
```bash
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows
```

**Manual start:**
```bash
cd ../..
./backend-docker.sh start  # Linux/macOS
docker compose -f docker-compose.backend.yaml up -d  # Windows
```

### Tests Failing

**Conda Environment Issues:**
If you see "No module named pytest":
```bash
# Make sure you're in the conda environment
conda activate gilfi

# Install pytest in the conda environment
conda install pytest
# or
pip install pytest
```

**Update dependencies:**
```bash
# With conda environment active
pip install -r requirements.txt
pip install -r src/backend/requirements.txt
pip install pytest requests
```

**Check Python version:**
```bash
python --version  # Should be 3.8+
```

**Verify backend health:**
```bash
curl http://localhost:8000/health
```

**Test Script Not Using Conda Environment:**
The test script automatically detects conda environments. If it's not working:
1. Make sure `CONDA_DEFAULT_ENV` is set (check with `echo $CONDA_DEFAULT_ENV`)
2. Activate the environment before running: `conda activate gilfi`
3. Or use: `conda run -n gilfi ./tests/infrastructure/run_tests.sh`

### Permission Errors

**Linux/macOS:**
```bash
chmod +x run_tests.sh
chmod +x ../../backend-docker.sh
```

### Import Errors

Make sure you're running from the correct directory:
```bash
cd tests/infrastructure
python -m pytest
```

## Test Coverage

Current coverage areas:
- ✅ Docker container lifecycle
- ✅ REST API endpoints
- ✅ Frontend API client
- ✅ Error handling
- ✅ Configuration validation
- ✅ Binary availability
- ✅ Environment setup
