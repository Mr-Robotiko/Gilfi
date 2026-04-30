# Backend Dockerfile for Gilfi
# Supports Linux containers with appropriate Ollama binary

FROM python:3.11-slim

# Install system dependencies for compilation, runtime, and 7zip extraction
# Note: p7zip-full provides both 7z and 7za commands for maximum compatibility
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    p7zip-full \
    p7zip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Environment setup
WORKDIR /app/backend
COPY entrypoint.sh /app/backend/entrypoint.sh
RUN chmod +x /app/backend/entrypoint.sh
COPY . /app/backend/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e /app/backend/hash-module
RUN pip install -e /app/backend/networking-module

# Compile RSA module
RUN gcc /app/backend/rsa-module/rsa-module.c -o /app/backend/rsa-module/rsa-module

# Set up Ollama for ask-gilfi module
RUN chmod +x /app/backend/ask-gilfi-module/bin/linux/ollama

# Set environment variable for Ollama models directory
ENV OLLAMA_MODELS=/app/backend/ask-gilfi-module/models

# Note: Ollama model setup is done at runtime in entrypoint.sh
# This avoids architecture issues during build and makes the container Git LFS independent

# If using volume mounts in development, the RSA binary may need recompilation
# Run: docker exec gilfi_backend gcc /app/backend/rsa-module/rsa-module.c -o /app/backend/rsa-module/rsa-module

# Expose port for API Backend Server
EXPOSE 8000

# Set entrypoint to handle setup tasks
ENTRYPOINT ["/bin/bash", "/app/backend/entrypoint.sh"]

CMD ["tail", "-f", "/dev/null"]