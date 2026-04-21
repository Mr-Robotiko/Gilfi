"""
Gilfi - Ask Gilfi Chat Widget
Uses the ask-gilfi-chat module to start and communicate with Ollama locally.
"""

import json
import sys
import os
import importlib.util

# Set custom Ollama port BEFORE importing the module to avoid Docker port conflict
os.environ['OLLAMA_HOST'] = '127.0.0.1:11435'

# Add ask-gilfi module to path BEFORE other imports
script_dir = os.path.dirname(os.path.abspath(__file__))
askgilfi_dir = os.path.join(script_dir, "..", "..", "backend", "ask-gilfi-module")
askgilfi_file = os.path.join(askgilfi_dir, "ask-gilfi-chat.py")

# Import from ask-gilfi-chat module using importlib (filename has hyphens)
spec = importlib.util.spec_from_file_location("ask_gilfi_chat", askgilfi_file)
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load ask-gilfi-chat module from {askgilfi_file}")

ask_gilfi_chat = importlib.util.module_from_spec(spec)
sys.modules["ask_gilfi_chat"] = ask_gilfi_chat
spec.loader.exec_module(ask_gilfi_chat)

# Get the functions we need
start_gilfi = ask_gilfi_chat.start_gilfi

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

OLLAMA_URL = "http://localhost:11435/api/generate"  # Use different port to avoid Docker conflict
MODEL_NAME = "ask-gilfi"
OLLAMA_PORT = "11435"

# Global Ollama process
_ollama_process = None


def start_ollama_server():
    """Start the Ollama server using the ask-gilfi module on custom port"""
    global _ollama_process
    
    if _ollama_process is not None:
        return True, "Ollama already running"
    
    try:
        # Use the start_gilfi function from ask-gilfi-chat module
        # (OLLAMA_HOST was set before module import)
        _ollama_process = start_gilfi()
        
        # Check if ask-gilfi model exists, create it if not
        import subprocess
        import time
        
        # Wait a moment for Ollama to be fully ready
        time.sleep(2)
        
        # Get the Ollama binary path
        ollama_bin = ask_gilfi_chat.get_ollama_binary()
        
        # Check if model exists
        try:
            result = subprocess.run(
                [ollama_bin, "list"],
                capture_output=True,
                text=True,
                timeout=5,
                env=os.environ.copy()
            )
            
            if "ask-gilfi" not in result.stdout:
                # Model doesn't exist, create it
                print("ask-gilfi model not found, creating it...")
                
                # Get the Modelfile path
                askgilfi_file = ask_gilfi_chat.__file__
                if askgilfi_file is None:
                    return False, "Could not locate ask-gilfi module"
                askgilfi_dir = os.path.dirname(askgilfi_file)
                modelfile_path = os.path.join(askgilfi_dir, "Modelfile")
                
                # Create the model
                create_result = subprocess.run(
                    [ollama_bin, "create", "ask-gilfi", "-f", modelfile_path],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes for model download
                    env=os.environ.copy()
                )
                
                if create_result.returncode == 0:
                    print("✓ ask-gilfi model created successfully")
                else:
                    print(f"⚠ Failed to create model: {create_result.stderr}")
                    return False, f"Failed to create ask-gilfi model: {create_result.stderr}"
            else:
                print("✓ ask-gilfi model already exists")
                
        except subprocess.TimeoutExpired:
            print("⚠ Model check/creation timed out")
        except Exception as e:
            print(f"⚠ Error checking/creating model: {e}")
        
        return True, f"Ollama started on port {OLLAMA_PORT} (PID: {_ollama_process.pid})"
    except Exception as e:
        return False, f"Failed to start Ollama: {str(e)}"


def stop_ollama_server():
    """Stop the Ollama server"""
    global _ollama_process
    
    if _ollama_process is not None:
        _ollama_process.terminate()
        _ollama_process = None


class OllamaStartupWorker(QThread):
    """Starts Ollama server in background thread"""
    startup_complete = pyqtSignal(bool, str)  # success, message
    
    def run(self):
        try:
            success, message = start_ollama_server()
            self.startup_complete.emit(success, message)
        except Exception as e:
            self.startup_complete.emit(False, f"Startup error: {str(e)}")


class ChatWorker(QThread):
    """Runs the API request in a background thread"""
    token_received = pyqtSignal(str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        import requests

        payload = {
            "model": MODEL_NAME,
            "prompt": self.prompt,
            "stream": True
        }

        try:
            response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    if token:
                        self.token_received.emit(token)
                    if chunk.get("done"):
                        break

        except requests.exceptions.ConnectionError:
            self.error_occurred.emit(
                "Connection failed! Ollama server may not be running.\n"
                "Try restarting the application."
            )
        except Exception as e:
            self.error_occurred.emit(f"Error: {e}")

        self.finished.emit()


class ChatWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.startup_worker = None
        self.ollama_started = False
        self.setup_ui()
        self.start_ollama()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.status_label = QLabel("Initializing Ollama... (this may take 10-15 seconds)")
        self.status_label.setStyleSheet("color: #555570; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Start a conversation with Gilfi ...")
        layout.addWidget(self.chat_display, stretch=1)

        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message ...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setEnabled(False)
        input_row.addWidget(self.input_field, stretch=1)

        self.btn_send = QPushButton("Send")
        self.btn_send.setObjectName("btnRun")
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.send_message)
        self.btn_send.setEnabled(False)
        input_row.addWidget(self.btn_send)

        layout.addLayout(input_row)

    def start_ollama(self):
        """Start Ollama server on widget initialization (in background thread)"""
        import os
        ollama_port = os.environ.get('OLLAMA_HOST', '127.0.0.1:11435').split(':')[-1]
        
        self.chat_display.append(
            "<span style='color:#555570;'>Starting Ollama server...</span><br>"
            "<span style='color:#555570;'>This may take 10-15 seconds on first start.</span><br>"
            f"<span style='color:#555570;'>Port: {ollama_port}</span>"
        )
        
        # Start Ollama in background thread to avoid blocking UI
        self.startup_worker = OllamaStartupWorker()
        self.startup_worker.startup_complete.connect(self.on_ollama_startup_complete)
        self.startup_worker.start()
    
    def on_ollama_startup_complete(self, success, message):
        """Called when Ollama startup completes"""
        if success:
            self.ollama_started = True
            self.status_label.setText("Offline Chatbot (Ollama) - Ready")
            self.status_label.setStyleSheet("color: #4ade80; font-size: 10px;")
            self.input_field.setEnabled(True)
            self.btn_send.setEnabled(True)
            self.chat_display.append(
                "<span style='color:#4ade80;'>✓ Ollama started successfully!</span><br>"
                "<span style='color:#555570;'>You can now chat with Gilfi.</span>"
            )
        else:
            self.status_label.setText("Offline Chatbot (Ollama) - Error")
            self.status_label.setStyleSheet("color: #f06b78; font-size: 10px;")
            self.chat_display.append(
                f"<span style='color:#f06b78;'>✗ Failed to start Ollama:</span><br>"
                f"<span style='color:#555570;'>{message}</span><br><br>"
                "<span style='color:#555570;'><b>Troubleshooting:</b></span><br>"
                "<span style='color:#555570;'>1. Check if port 11435 is available</span><br>"
                "<span style='color:#555570;'>2. Ensure Ollama binary has execute permissions</span><br>"
                "<span style='color:#555570;'>3. Check system resources (RAM/CPU)</span><br>"
                "<span style='color:#555570;'>4. Try restarting the application</span>"
            )

    def send_message(self):
        if not self.ollama_started:
            self.chat_display.append(
                "<span style='color:#f06b78;'>Ollama is not running. Please restart the application.</span>"
            )
            return
        
        prompt = self.input_field.text().strip()
        if not prompt:
            return
        if self.worker and self.worker.isRunning():
            return

        self.chat_display.append(f"<b style='color:#53a8d8;'>You:</b> {prompt}")
        self.input_field.clear()
        self.chat_display.append("<b style='color:#4ade80;'>Gilfi:</b> ")
        self.btn_send.setEnabled(False)

        self.worker = ChatWorker(prompt)
        self.worker.token_received.connect(self.on_token)
        self.worker.error_occurred.connect(self.on_error)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_token(self, token):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(token)
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def on_error(self, msg):
        self.chat_display.append(f"<span style='color:#f06b78;'>{msg}</span>")

    def on_finished(self):
        self.btn_send.setEnabled(True)
        self.chat_display.append("")

    def closeEvent(self, a0):
        """Clean up when widget is closed"""
        stop_ollama_server()
        super().closeEvent(a0)