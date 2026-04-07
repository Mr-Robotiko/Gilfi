#!/bin/bash

# Make executable: chmod +x ask-gilfi_container_installation.sh
# Execute: ./ask-gilfi_container_installation.sh

# Variables
CONTAINER_NAME="ollama"
OLLAMA_PORT="11434"
MODEL_NAME="granite4:350m"

echo "Starting the installation of the Podman-Container..."

echo "---"
echo "Installing and executing Ollama Container ($CONTAINER_NAME)..."

podman run -d -v ollama:/root/.ollama -p $OLLAMA_PORT:$OLLAMA_PORT --name $CONTAINER_NAME ollama/ollama

if [ $? -eq 0 ]; then
    echo "Ollama-Container is running!"
else
    echo "Error while starting the Ollama-Container. Please verify Podman installation and configuration."
    exit 1
fi

echo "Waiting for Ollama..."
sleep 5

echo "---"
echo "Pulling $MODEL_NAME to Ollama-Container..."

podman exec -it $CONTAINER_NAME ollama run $MODEL_NAME

if [ $? -eq 0 ]; then
    echo "Modell $MODEL_NAME installed and executes successfully."
else
    echo "Error while pulling $MODEL_NAME."
    exit 1
fi

echo "---"
echo "Installation completed!"
echo "Ollama-Port: $OLLAMA_PORT"
echo "To chat with $MODEL_NAME, use:"
echo "podman exec -it $CONTAINER_NAME ollama run $MODEL_NAME"
echo "Or use the API at http://<HOST_IP>:$OLLAMA_PORT."
