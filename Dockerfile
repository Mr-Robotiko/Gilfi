# Use standard python image as base image
FROM python:3.11-slim

# Install system dependencies for PyQt and X11
RUN apt-get update && apt-get install -y \
    libgl1 \
    libegl1 \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-render0 \
    libxcb-shm0 \
    libxcb-util1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*

# Internal directory
WORKDIR /app

# Copy the entire project into the internal project
COPY . .

# Install hash-module in running environment
RUN pip install -e ./src/backend/hash-module

# Install all python requirements
#RUN pip install -r requirements.txt ...

# Run the frontend entrypoint
#CMD ["python", "src/frontend/main.py"] Frontend main python GUI TBC: