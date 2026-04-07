import subprocess
import os
import time
import requests

MODEL_NAME = "granite4:350m"
OLLAMA_URL = "http://localhost:11434/api/pull"

def setup_granite():
    # 1. Pfad zur Binary bestimmen (relativ zum Tool-Ordner)
    binary = "./bin/ollama.exe" if os.name == "nt" else "./bin/ollama"
    
    print("--- Starte Ollama Engine ---")
    # Startet den Server im Hintergrund
    # OLLAMA_MODELS legt fest, wo das Modell gespeichert wird (lokal im Tool)
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = os.path.abspath("./models")
    
    subprocess.Popen([binary, "serve"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(5) # Warten auf Initialisierung

    # 2. Modell herunterladen (entspricht 'ollama pull')
    print(f"--- Lade Modell {MODEL_NAME} (Offline-Vorbereitung) ---")
    try:
        response = requests.post(OLLAMA_URL, json={"name": MODEL_NAME}, stream=True)
        for line in response.iter_lines():
            if line:
                print("Lade...") # Hier könnte man einen Ladebalken für die GUI triggern
        print("Setup abgeschlossen!")
    except Exception as e:
        print(f"Fehler beim Setup: {e}")

if __name__ == "__main__":
    setup_granite()