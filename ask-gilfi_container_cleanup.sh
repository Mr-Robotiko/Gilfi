#!/bin/bash

# Make executable: chmod +x ask-gilfi_container_installation.sh
# Execute: ./ask-gilfi_container_installation.sh

# Variables
CONTAINER_NAME="ollama"
VOLUME_NAME="ollama"
IMAGE_NAME="ollama/ollama"

echo "Starting cleanup of the Ollama container and volume..."

# Stop and Remove the Container

echo "Stopping the container: $CONTAINER_NAME..."

podman stop $CONTAINER_NAME

if [ $? -eq 0 ]; then
    echo "Container $CONTAINER_NAME stopped successfully."
elif podman ps -a --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "Container $CONTAINER_NAME exists but could not be stopped. Proceeding with force removal."
else
    echo "Container $CONTAINER_NAME does not appear to be running or does not exist. Skipping stop."
fi

echo "Removing the container: $CONTAINER_NAME..."

podman rm -f $CONTAINER_NAME

if [ $? -eq 0 ]; then
    echo "Container $CONTAINER_NAME removed successfully."
else
    echo "Could not remove container $CONTAINER_NAME. It might have already been removed."
fi

# Remove the Persistent Volume

echo "Removing the persistent volume: $VOLUME_NAME..."
echo "WARNING: This will delete ALL downloaded models (like Granite) and associated data."

podman volume rm -f $VOLUME_NAME

if [ $? -eq 0 ]; then
    echo "Volume $VOLUME_NAME removed successfully."
else
    echo "Could not remove volume $VOLUME_NAME. It might not exist or another error occurred."
fi

# Remove the Image

echo "Removing the image: $IMAGE_NAME..."

podman rmi $IMAGE_NAME

if [ $? -eq 0 ]; then
    echo "Image $IMAGE_NAME removed successfully."
else
    echo "Could not remove image $IMAGE_NAME. It might not exist or be referenced by another entity."
fi

echo "Cleanup complete!"
echo "The Ollama container and its persistent data volume have been removed."
