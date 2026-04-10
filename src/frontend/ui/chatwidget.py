"""
Gilfi - Ask Gilfi Chat Widget
Talks to the Ollama API on localhost:11434.
"""

import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "ask-gilfi"


class ChatWorker(QThread):
    """runs the api request in a background thread"""
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
            response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=60)
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
                "Connection failed! Is the Ollama container running? "
                "(podman start ollama)"
            )
        except Exception as e:
            self.error_occurred.emit(f"Error: {e}")

        self.finished.emit()


class ChatWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        hint = QLabel("Offline Chatbot (Ollama)")
        hint.setStyleSheet("color: #555570; font-size: 10px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Start a conversation with Gilfi ...")
        layout.addWidget(self.chat_display, stretch=1)

        input_row = QHBoxLayout()
        input_row.setSpacing(6)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message ...")
        self.input_field.returnPressed.connect(self.send_message)
        input_row.addWidget(self.input_field, stretch=1)

        self.btn_send = QPushButton("Send")
        self.btn_send.setObjectName("btnRun")
        self.btn_send.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_send.clicked.connect(self.send_message)
        input_row.addWidget(self.btn_send)

        layout.addLayout(input_row)

    def send_message(self):
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
