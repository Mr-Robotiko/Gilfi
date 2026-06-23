@echo off
REM Gilfi - Installation and Run Script (Windows)
REM This script installs dependencies and runs the Gilfi application

setlocal enabledelayedexpansion

echo ==========================================
echo    Gilfi - Installation ^& Run Script
echo ==========================================
echo.

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed!
    echo Please install Python 3.8 or higher and try again.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python 3 found: %PYTHON_VERSION%

REM Check if Docker is installed
set CONTAINER_CMD=
docker --version >nul 2>&1
if not errorlevel 1 (
    set CONTAINER_CMD=docker
    echo [OK] Docker found
) else (
    podman --version >nul 2>&1
    if not errorlevel 1 (
        set CONTAINER_CMD=podman
        echo [OK] Podman found
    ) else (
        echo [WARNING] Neither Docker nor Podman found
        echo Backend API will not be available. Only local features will work.
    )
)

echo.
echo ==========================================
echo    Installing Dependencies
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1

REM Install frontend requirements
echo Installing frontend dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies!
        pause
        exit /b 1
    )
    echo [OK] Frontend dependencies installed
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

REM Install backend dependencies
echo Installing backend dependencies...
if exist "src\backend\requirements.txt" (
    pip install -r src\backend\requirements.txt >nul 2>&1
    echo [OK] Backend dependencies installed
)

echo.
echo ==========================================
echo    Starting Backend (Docker)
echo ==========================================
echo.

REM Start backend if Docker/Podman is available
if defined CONTAINER_CMD (
    echo Starting backend container...
    
    REM Check if backend-docker.sh exists (use docker-compose directly on Windows)
    if exist "docker-compose.backend.yaml" (
        %CONTAINER_CMD% compose -f docker-compose.backend.yaml up -d
        if errorlevel 1 (
            echo [WARNING] Failed to start backend container
        ) else (
            echo [OK] Backend container started
        )
    ) else (
        echo [WARNING] Backend configuration not found, skipping...
    )
    
    echo.
    echo Waiting for backend to be ready...
    timeout /t 5 /nobreak >nul
    
    REM Check if backend is responding
    curl -s http://localhost:8000/health >nul 2>&1
    if not errorlevel 1 (
        echo [OK] Backend API is ready
    ) else (
        echo [WARNING] Backend API not responding (this is okay for local-only mode)
    )
) else (
    echo [WARNING] Skipping backend startup (no container runtime found)
)

echo.
echo ==========================================
echo    Starting Gilfi Frontend
echo ==========================================
echo.

REM Make sure we're in the virtual environment
call venv\Scripts\activate.bat

echo Starting Gilfi application...
echo.
echo Gilfi is starting...
echo.
echo Features available:
echo   * Port Scanner
echo   * Network Scanner
echo   * Hash Generator/Identifier
if defined CONTAINER_CMD (
    echo   * Hash Cracker (via backend API^)
    echo   * RSA Encryption (via backend API^)
)
echo   * Ask-Gilfi Chat (local AI assistant^)
echo.
echo Press Ctrl+C to stop the application
echo.

REM Run the application
python src\frontend\main.py

REM Cleanup on exit
echo.
echo ==========================================
echo    Shutting Down
echo ==========================================
echo.

if defined CONTAINER_CMD (
    if exist "docker-compose.backend.yaml" (
        echo Stopping backend container...
        %CONTAINER_CMD% compose -f docker-compose.backend.yaml down
    )
)

echo [OK] Gilfi stopped successfully
echo.
pause
