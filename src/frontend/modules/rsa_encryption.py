"""
Gilfi Module - RSA Encryption
Uses backend API via api_client instead of calling C binary directly.
Uses QThread to keep the GUI responsive.
"""

from PyQt6.QtCore import QThread, pyqtSignal
from ui.toolpage import ToolPage
import api_client


class RSAWorker(QThread):
    """Calls the backend API in a background thread"""
    output_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    finished_ok = pyqtSignal()

    def __init__(self, plaintext):
        super().__init__()
        self.plaintext = plaintext

    def run(self):
        try:
            # Call backend API with plaintext as a number
            result = api_client.rsa_encrypt(self.plaintext, 'encrypt')
            
            if result.get('success'):
                # Format output similar to C binary
                output_lines = []
                output_lines.append("--- RSA Key Generation ---")
                
                # Extract p, q, n from output if available
                if 'output' in result:
                    for line in result['output'].split('\n'):
                        if any(x in line for x in ['p =', 'q =', 'n =', 'phi =']):
                            output_lines.append(line)
                
                output_lines.append("-" * 26)
                output_lines.append("")
                
                if 'public_key' in result:
                    output_lines.append(f"Public Key (e, n) = {result['public_key']}")
                if 'private_key' in result:
                    output_lines.append(f"Private Key (d, n) = {result['private_key']}")
                
                output_lines.append("")
                output_lines.append(f"Original message (M) = {self.plaintext}")
                
                if 'ciphertext' in result:
                    output_lines.append(f"Ciphertext (C) = {result['ciphertext']}")
                if 'decrypted' in result:
                    output_lines.append(f"Decrypted message (M') = {result['decrypted']}")
                
                self.output_ready.emit('\n'.join(output_lines))
                self.finished_ok.emit()
            else:
                self.error_occurred.emit(result.get('error', 'Unknown error'))
                
        except ConnectionError as e:
            self.error_occurred.emit(f"Backend not available: {str(e)}")
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
    page.set_status("Encrypting via backend API ...")

    page.btn_run.setEnabled(False)

    _worker = RSAWorker(plaintext)

    _worker.output_ready.connect(
        lambda out: [page.append_output(line) for line in out.splitlines()]
    )
    _worker.error_occurred.connect(
        lambda err: (
            page.append_output(f"[ERROR] {err}"),
            page.append_output("\nMake sure the backend container is running:"),
            page.append_output("  ./backend-docker.sh start"),
            page.set_status("Error", error=True)
        )
    )
    _worker.finished.connect(lambda: page.btn_run.setEnabled(True))
    _worker.finished_ok.connect(lambda: page.set_status("Done"))

    _worker.start()
