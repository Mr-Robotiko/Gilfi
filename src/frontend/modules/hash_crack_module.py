"""
Gilfi Module - Hash Cracker
Uses hash_lib from src/backend/hash-crack-module.
"""

from ui.toolpage import ToolPage
from hash_lib.hash_cracker.cracker import Cracker

_cracker = Cracker()


def create_page():
    page = ToolPage(
        title="Hash Crack Module",
        description="Cracks MD5, SHA-1, SHA-256 and more based on rockyou.txt"
    )
    page.add_field("Hash", "Hash to crack")
    page.add_field("Algorithm", "e.g. md5, sha1, sha256 (default: sha256)")
    page.set_button_text("Run")
    page.on_run = run
    return page


def run(page):
    hash_value = page.get_input("Hash")
    algo = page.get_input("Algorithm") or "sha256"

    if not hash_value:
        page.set_status("Please enter hash value", error=True)
        return
    page.clear_output()

    _run_crack(page, hash_value, algo)


def _run_crack(page, hash_value, algo):
    page.set_status("Computing ...")
    path = "/Users/raphaeltack/Gilfi/data/wordlist/rockyou.txt" #"/app/data/wordlist/rockyou.txt"
    try:
        result = _cracker.crack(hash_value, path, algo)
        if result is None:
            page.append_output(f"No Plaintext found:     {hash_value}")
        else:
            page.append_output(f"Hash:     {hash_value}")
            page.append_output(f"Algorithm: {algo.upper()}")
            page.append_output("─" * 40)
            page.append_output(f"Plaintext: {result}")
            page.set_status(f"Done - {algo.upper()}")
    except ValueError:
        page.append_output(f"[ERROR] Unsupported algorithm: '{algo}'")
        page.set_status("Unknown algorithm", error=True)
    except Exception as e:
        page.append_output(f"[ERROR] {e}")
        page.set_status("Error", error=True)
