"""
Gilfi Module - RSA Encryption
Calls the C binary from src/backend/rsa-module via subprocess.
Auto-compiles on first run. Uses QThread to keep the GUI responsive.
"""

import os
import sys
import subprocess

from PyQt6.QtCore import QThread, pyqtSignal
from ui.toolpage import ToolPage

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_RSA_SRC = os.path.join(_MODULE_DIR, "..", "..", "backend", "rsa-module", "rsa-module.c")
_BIN_NAME = "rsa-module.exe" if sys.platform == "win32" else "rsa-module"
_RSA_BIN = os.path.join(_MODULE_DIR, "..", "..", "backend", "rsa-module", _BIN_NAME)


def _ensure_compiled():
    if os.path.isfile(_RSA_BIN):
        return True, ""
    if not os.path.isfile(_RSA_SRC):
        return False, f"C source not found: {_RSA_SRC}"

    try:
        result = subprocess.run(
            ["gcc", _RSA_SRC, "-o", _RSA_BIN],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, f"Compilation failed:\n{result.stderr}"
        return True, ""
    except FileNotFoundError:
        return False, "gcc not found! Please install gcc."


class RSAWorker(QThread):
    """runs the C binary in a background thread"""
    output_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished_ok = pyqtSignal()

    def __init__(self, plaintext):
        super().__init__()
        self.plaintext = plaintext

    def run(self):
        try:
            result = subprocess.run(
                [_RSA_BIN, self.plaintext],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                self.error_occurred.emit(result.stderr.strip())
                return

            self.output_ready.emit(result.stdout.strip())
            self.finished_ok.emit()

        except subprocess.TimeoutExpired:
            self.error_occurred.emit("Timeout")
        except Exception as e:
            self.error_occurred.emit(str(e))


_worker = None


def create_page():
    page = ToolPage(
        title="RSA Encryption",
        description="Generates an RSA key pair and performs encryption/decryption."
    )
    page.add_field("Plaintext (number)", "e.g. 42, 12345")
    page.set_button_text("Encrypt")
    page.on_run = run
    return page


def run(page):
    global _worker

    plaintext = page.get_input("Plaintext (number)")

    if not plaintext:
        page.set_status("Please enter a number", error=True)
        return

    try:
        int(plaintext)
    except ValueError:
        page.set_status("Integers only", error=True)
        return

    if _worker and _worker.isRunning():
        page.set_status("Already running ...", error=True)
        return

    page.clear_output()
    page.set_status("Compiling / Starting ...")

    ok, err = _ensure_compiled()
    if not ok:
        page.append_output(f"[ERROR] {err}")
        page.set_status("Error", error=True)
        return

    page.btn_run.setEnabled(False)

    _worker = RSAWorker(plaintext)

    _worker.output_ready.connect(
        lambda out: [page.append_output(line) for line in out.splitlines()]
    )
    _worker.error_occurred.connect(
        lambda err: (page.append_output(f"[ERROR] {err}"),
                     page.set_status("Error", error=True))
    )
    _worker.finished.connect(lambda: page.btn_run.setEnabled(True))
    _worker.finished_ok.connect(lambda: page.set_status("Done"))

    _worker.start()
