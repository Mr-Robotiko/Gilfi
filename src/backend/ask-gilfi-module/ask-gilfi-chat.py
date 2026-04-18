import requests
import subprocess
import time
import os
import json
import platform


def get_ollama_binary() -> str:
    """
    Detect OS and set appropriate Ollama binary path from the according Ollama binaries inside bin/
    :return:
    """
    system: str = platform.system().lower()
    script_dir: str = os.path.dirname(os.path.abspath(__file__))

    if system == "linux":
        return os.path.join(script_dir, "bin/linux/ollama")
    elif system == "darwin":  # macOS
        return os.path.join(script_dir, "bin/mac/ollama")
    elif system == "windows":
        return os.path.join(script_dir, "bin/windows/ollama.exe")
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")


# Set paths
script_dir: str = os.path.dirname(os.path.abspath(__file__))
model_dir: str = os.path.join(script_dir, "models")
ollama_bin: str = get_ollama_binary()

# Verify binary exists
if not os.path.exists(ollama_bin):
    raise FileNotFoundError(f"Ollama binary not found at: {ollama_bin}")

# Make sure binary is executable (Unix-like systems)
if platform.system() != "Windows":
    os.chmod(ollama_bin, 0o755)

env = os.environ.copy()
env["OLLAMA_MODELS"] = model_dir

print(f"Using Ollama binary: {ollama_bin}")
print(f"Models directory: {model_dir}")


def start_gilfi():
    ollama_process = subprocess.Popen(
        [ollama_bin, "serve"],
        env = env,
        stdout = subprocess.DEVNULL,
        stderr = subprocess.STDOUT
    )

    time.sleep(10)

    print(f"Server läuft mit PID: {ollama_process.pid}")
    return ollama_process


def ask_gilfi(prompt):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "ask-gilfi",
        "prompt": prompt,
        "stream": True
    }

    print("\n--- Gilfi denkt nach ---")
    print("Antwort: ", end = "", flush = True)

    try:
        response = requests.post(url, json = payload, stream = True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                content = chunk.get("response", "")
                print(content, end = "", flush = True)
                full_response += content

                if chunk.get("done"):
                    break
        print("\n")
        return full_response

    except requests.exceptions.ConnectionError:
        print("\n\n[!] FEHLER: Gilfi ist nicht aktiv! Starte das Tool neu, um diese Funktion nutzen zu können.")
        return None
    except Exception as e:
        print(f"\n\n[!] FEHLER: {e}")
        return None


if __name__ == "__main__":

    ollama_handle = start_gilfi()

    try:
        print("========================================")
        print("   ask-gilfi Terminal Chat (Offline)    ")
        print("  (Tippe 'exit' zum Beenden)            ")
        print("========================================")

        while True:
            user_input = input("\nDu: ")

            if user_input.lower() in ["exit"]:
                print("Bis zum nächsten Mal!")
                break

            if not user_input.strip():
                continue

            ask_gilfi(user_input)

    finally:
        ollama_handle.terminate()
