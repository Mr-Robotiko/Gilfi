#!/bin/bash

# Gilfi Backend Docker Management Script
# This script helps manage the Gilfi backend Docker container

set -e

COMPOSE_FILE="docker-compose.backend.yaml"
CONTAINER_NAME="gilfi_backend"

# Detect if using Docker or Podman
if command -v docker &> /dev/null && docker ps &> /dev/null 2>&1; then
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker-compose"
elif command -v podman &> /dev/null; then
    DOCKER_CMD="podman"
    COMPOSE_CMD="podman-compose"
else
    echo "Error: Neither Docker nor Podman found!"
    exit 1
fi

echo "Using: $DOCKER_CMD"

# Function to display usage
usage() {
    cat << EOF
Gilfi Backend Docker Management

Usage: $0 [COMMAND]

Commands:
    build       Build the backend container
    start       Start the backend container
    stop        Stop the backend container
    restart     Restart the backend container
    logs        Show container logs
    shell       Open a shell in the container
    status      Show container status
    
    # Module-specific commands
    hash        Run hash module interactively
    rsa         Run RSA module (usage: $0 rsa <number>)
    askgilfi    Run Ask-Gilfi chat interactively
    
    clean       Stop and remove the container
    rebuild     Clean, rebuild, and start

Examples:
    $0 build
    $0 start
    $0 shell
    $0 rsa 12345
    $0 askgilfi

EOF
    exit 1
}

# Check if container is running
is_running() {
    $DOCKER_CMD ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
}

# Main command handling
case "${1:-}" in
    build)
        echo "Building backend container..."
        $COMPOSE_CMD -f $COMPOSE_FILE build
        echo "Build complete!"
        ;;
    
    start)
        echo "Starting backend container..."
        $COMPOSE_CMD -f $COMPOSE_FILE up -d
        echo "Backend container started!"
        ;;
    
    stop)
        echo "Stopping backend container..."
        $COMPOSE_CMD -f $COMPOSE_FILE down
        echo "Backend container stopped!"
        ;;
    
    restart)
        echo "Restarting backend container..."
        $COMPOSE_CMD -f $COMPOSE_FILE restart
        echo "Backend container restarted!"
        ;;
    
    logs)
        $COMPOSE_CMD -f $COMPOSE_FILE logs -f
        ;;
    
    shell)
        if ! is_running; then
            echo "Error: Container is not running. Start it first with: $0 start"
            exit 1
        fi
        echo "Opening shell in backend container..."
        $DOCKER_CMD exec -it $CONTAINER_NAME bash
        ;;
    
    status)
        echo "Backend container status:"
        $DOCKER_CMD ps -a --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        ;;
    
    hash)
        if ! is_running; then
            echo "Error: Container is not running. Start it first with: $0 start"
            exit 1
        fi
        echo "Running hash module..."
        $DOCKER_CMD exec -it $CONTAINER_NAME python /app/backend/hash-module/main.py
        ;;
    
    rsa)
        if ! is_running; then
            echo "Error: Container is not running. Start it first with: $0 start"
            exit 1
        fi
        if [ -z "${2:-}" ]; then
            echo "Error: Please provide a number to encrypt"
            echo "Usage: $0 rsa <number>"
            exit 1
        fi
        echo "Running RSA module with input: $2"
        $DOCKER_CMD exec -it $CONTAINER_NAME /app/backend/rsa-module/rsa-module "$2"
        ;;
    
    askgilfi)
        if ! is_running; then
            echo "Error: Container is not running. Start it first with: $0 start"
            exit 1
        fi
        echo "Starting Ask-Gilfi chat..."
        echo "Note: First startup may take a moment to initialize Ollama..."
        $DOCKER_CMD exec -it $CONTAINER_NAME python /app/backend/ask-gilfi-module/ask-gilfi-chat.py
        ;;
    
    clean)
        echo "Cleaning up backend container..."
        $COMPOSE_CMD -f $COMPOSE_FILE down -v
        echo "Cleanup complete!"
        ;;
    
    rebuild)
        echo "Rebuilding backend container..."
        $COMPOSE_CMD -f $COMPOSE_FILE down
        $COMPOSE_CMD -f $COMPOSE_FILE build --no-cache
        $COMPOSE_CMD -f $COMPOSE_FILE up -d
        echo "Rebuild complete!"
        ;;
    
    *)
        usage
        ;;
esac