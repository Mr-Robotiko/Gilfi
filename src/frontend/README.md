# Gilfi - Frontend

PyQt6-based GUI for the Gilfi Security Tool Suite.

## Setup

### Install dependencies

```bash
pip install PyQt6 requests
```

### Docker / Podman

```bash
pip install --no-cache-dir PyQt6 requests
```

> **Note:** PyQt6 needs a display. In a headless container use `xvfb` or forward X11:
>
> ```bash
> podman run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix ...
> ```

### Run

```bash
cd src/frontend
python main.py
```

## Structure

```
frontend/
├── main.py
├── ui/
│   ├── mainwindow.py
│   ├── toolpage.py
│   ├── chatwidget.py
│   └── style.py
└── modules/
    ├── network_scanner.py    (placeholder)
    ├── port_scanner.py       (placeholder)
    ├── rsa_encryption.py     (calls C binary via subprocess)
    └── hash_module.py        (uses hash_lib from backend)
```

## Ask Gilfi Chatbot

Needs a running Ollama server on `localhost:11434`.

```bash
# start the container (see ask-gilfi_container_installation.sh in root)
podman start ollama
```

Toggle via the **💬 Ask Gilfi** button in the bottom left of the GUI.
