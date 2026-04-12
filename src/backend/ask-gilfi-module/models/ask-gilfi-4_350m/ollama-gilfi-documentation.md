export OLLAMA_MODELS="./models"

./ollama serve

./ollama create ask-gilfi -f modelfile.dockerfile

./src/backend/ask-gilfi-module/models/manifests/registry.ollama.ai/library

Ollama source:
curl -fsSL https://ollama.com/install.sh | sh
