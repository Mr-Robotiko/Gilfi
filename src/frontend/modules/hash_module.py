"""
Gilfi Module - Hash Generator & Identifier
Uses hash_lib from src/backend/hash-module.
"""

from ui.toolpage import ToolPage
from hash_lib.hash_core.hasher import Hasher
from hash_lib.hash_identifier.identifier import HashIdentifier

_hasher = Hasher()
_identifier = HashIdentifier()


def create_page():
    page = ToolPage(
        title="Hash Module",
        description="Computes MD5, SHA-1, SHA-256 and more. Can also identify hash types."
    )
    page.add_field("Input", "Text to hash or hash to identify")
    page.add_field("Algorithm", "e.g. md5, sha1, sha256 (default: sha256)")
    page.add_field("Mode", "'hash' or 'identify' (default: hash)")
    page.set_button_text("Run")
    page.on_run = run
    return page


def run(page):
    text = page.get_input("Input")
    algo = page.get_input("Algorithm") or "sha256"
    mode = page.get_input("Mode").lower() or "hash"

    if not text:
        page.set_status("Please enter text", error=True)
        return

    page.clear_output()

    if mode == "identify":
        _run_identify(page, text)
    else:
        _run_hash(page, text, algo)


def _run_hash(page, text, algo):
    page.set_status("Computing ...")
    try:
        result = _hasher.hash(text, algo)
        page.append_output(f"Input:     {text}")
        page.append_output(f"Algorithm: {algo.upper()}")
        page.append_output("─" * 40)
        page.append_output(f"Hash: {result}")
        page.set_status(f"Done - {algo.upper()}")
    except ValueError:
        page.append_output(f"[ERROR] Unsupported algorithm: '{algo}'")
        page.set_status("Unknown algorithm", error=True)
    except Exception as e:
        page.append_output(f"[ERROR] {e}")
        page.set_status("Error", error=True)


def _run_identify(page, hash_value):
    page.set_status("Identifying ...")
    results = _identifier.identify(hash_value)

    page.append_output(f"Hash:   {hash_value}")
    page.append_output(f"Length: {len(hash_value.strip())} chars")
    page.append_output("─" * 40)

    if results:
        page.append_output("Possible algorithms:")
        for r in results:
            page.append_output(f"  - {r}")
    else:
        page.append_output("No matching algorithm found.")

    page.set_status("Done")
