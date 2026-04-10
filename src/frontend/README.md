# Gilfi - Frontend

PyQt6-basierte GUI für die Gilfi Security Tool Suite.

## Setup

### Dependencies installieren

```bash
pip install PyQt6 requests
```

### In Docker / Podman

```bash
pip install --no-cache-dir PyQt6 requests
```

> **Hinweis:** PyQt6 braucht ein Display. In einem headless Container muss ein virtuelles Display (z.B. `xvfb`) laufen, oder man leitet X11 durch:
>
> ```bash
> # X11 forwarding (Linux Host)
> podman run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ...
> ```

### Starten

```bash
cd src/frontend
python main.py
```

## Struktur

```
frontend/
├── main.py                  # Einstiegspunkt
├── ui/
│   ├── mainwindow.py        # Hauptfenster mit Navigation + Chatbot-Dock
│   ├── toolpage.py          # Wiederverwendbares Widget pro Tool
│   ├── chatwidget.py        # Ask-Gilfi Chat (Ollama API)
│   └── style.py             # Dark Theme Stylesheet
└── modules/
    ├── network_scanner.py   # Platzhalter (TODO)
    ├── port_scanner.py      # Platzhalter (TODO)
    ├── rsa_encryption.py    # Ruft C-Binary auf (subprocess)
    └── hash_module.py       # Nutzt hash_lib aus backend
```

## Ask Gilfi Chatbot

Der Chatbot braucht einen laufenden Ollama-Server auf `localhost:11434`.

```bash
# Container starten (siehe ask-gilfi_container_installation.sh im Root)
podman start ollama

# Oder manuell
podman run -d -p 11434:11434 --name ollama ollama/ollama
```

In der GUI über den **💬 Ask Gilfi** Button unten links erreichbar.
