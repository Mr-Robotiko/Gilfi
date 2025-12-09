# Gilfi

## ✨ Gilfi is a swiss army knife for Crypto and Pentesting

## 📌 Table of Contents

## Installation

Go to the [Releases](https://github.com/Mr-Robotiko/Gilfi/releases) page of Gilfi.

> [!IMPORTANT]
> You need to have [Podman](https://podman.io/docs/installation) installed in order to install Gilfi. From there, it's easy.

## Project idea

![structure](documentation/assets/project-structure.png)

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
