"""
Gilfi Modul - RSA Encryption
Ruft das C-Binary aus src/backend/rsa-module per subprocess auf.
Kompiliert automatisch beim ersten mal.
Läuft in einem QThread damit die GUI nicht einfriert.
"""

import os
import sys
import subprocess

from PyQt6.QtCore import QThread, pyqtSignal
from ui.toolpage import ToolPage

# pfade zum c-source und binary
# auf windows braucht das binary die .exe endung
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_RSA_SRC = os.path.join(_MODULE_DIR, "..", "..", "backend", "rsa-module", "rsa-module.c")
_BIN_NAME = "rsa-module.exe" if sys.platform == "win32" else "rsa-module"
_RSA_BIN = os.path.join(_MODULE_DIR, "..", "..", "backend", "rsa-module", _BIN_NAME)


def _ensure_compiled():
    """kompiliert das binary falls es noch nicht existiert"""
    if os.path.isfile(_RSA_BIN):
        return True, ""

    if not os.path.isfile(_RSA_SRC):
        return False, f"C-Source nicht gefunden: {_RSA_SRC}"

    try:
        result = subprocess.run(
            ["gcc", _RSA_SRC, "-o", _RSA_BIN],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return False, f"Kompilierung fehlgeschlagen:\n{result.stderr}"
        return True, ""
    except FileNotFoundError:
        return False, "gcc nicht gefunden! Bitte gcc installieren."


class RSAWorker(QThread):
    """führt das c-binary im hintergrund aus"""
    output_ready = pyqtSignal(str)   # gesamte stdout ausgabe
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
            self.error_occurred.emit("Timeout - hat zu lange gedauert")
        except Exception as e:
            self.error_occurred.emit(str(e))


# referenz auf den worker damit er nicht vom garbage collector gekillt wird
_worker = None


def create_page():
    page = ToolPage(
        title="RSA Encryption",
        description="Erzeugt ein RSA-Schlüsselpaar und führt Ver-/Entschlüsselung durch."
    )
    page.add_field("Klartext (Zahl)", "z.B. 42, 12345")
    page.set_button_text("Verschlüsseln")
    page.on_run = run
    return page


def run(page):
    global _worker

    plaintext = page.get_input("Klartext (Zahl)")

    if not plaintext:
        page.set_status("Bitte eine Zahl eingeben", error=True)
        return

    # nur ganze zahlen
    try:
        int(plaintext)
    except ValueError:
        page.set_status("Nur ganze Zahlen erlaubt", error=True)
        return

    # nicht doppelt starten
    if _worker and _worker.isRunning():
        page.set_status("Läuft bereits ...", error=True)
        return

    page.clear_output()
    page.set_status("Kompiliere / Starte ...")

    # kompilieren falls nötig
    ok, err = _ensure_compiled()
    if not ok:
        page.append_output(f"[FEHLER] {err}")
        page.set_status("Fehler", error=True)
        return

    # worker starten
    page.btn_run.setEnabled(False)

    _worker = RSAWorker(plaintext)

    _worker.output_ready.connect(
        lambda out: [page.append_output(line) for line in out.splitlines()]
    )
    _worker.error_occurred.connect(
        lambda err: (page.append_output(f"[FEHLER] {err}"),
                     page.set_status("Fehler", error=True))
    )
    _worker.finished.connect(lambda: page.btn_run.setEnabled(True))
    _worker.finished_ok.connect(lambda: page.set_status("Fertig"))

    _worker.start()
