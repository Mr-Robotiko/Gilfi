"""
Gilfi Module - Hash Generator & Identifier
Hashing and hash-type identification, performed by the backend API.
"""

from ui.toolpage import ToolPage
import api_client


def create_page():
    page = ToolPage(
        title="Hash Module",
        description="Computes MD5, SHA-1, SHA-256 and more. Can also identify hash types.",
        help_text=(
            "Two modes:\n\n"
            "  • hash: turn arbitrary text into a fixed-length fingerprint. "
            "Same input always produces the same hash, but the hash can't be "
            "reversed back to the input.\n"
            "  • identify: take a hash and guess which algorithm produced it "
            "(based on length and character set).\n\n"
            "Fields:\n"
            "  • Input — the text to hash, or the hash to identify.\n"
            "  • Algorithm — md5, sha1, sha256, sha512, … (default sha256).\n"
            "  • Mode — 'hash' or 'identify' (default hash).\n\n"
            "Hashes are everywhere: password storage, file integrity, "
            "blockchains."
        )
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
    mode = (page.get_input("Mode") or "hash").lower()

    if not text:
        page.set_status("Please enter text", error=True)
        return

    page.clear_output()

    if mode == "identify":
        _run_identify(page, text)
    else:
        _run_hash(page, text, algo)


def _run_hash(page, text, algo):
    page.run_async(
        work_fn=lambda: api_client.hash_generate(text, algo),
        on_success=lambda result: _show_hash_result(page, text, algo, result),
        running_text="Computing ...",
        done_text="Done",
    )


def _show_hash_result(page, text, algo, result):
    page.append_dim(f"Input:     {text}")
    page.append_dim(f"Algorithm: {algo.upper()}")
    page.append_dim("─" * 40)
    page.append_success(f"Hash:      {result}")


def _run_identify(page, hash_value):
    page.run_async(
        work_fn=lambda: api_client.hash_identify(hash_value),
        on_success=lambda result: _show_identify_result(page, hash_value, result),
        running_text="Identifying ...",
        done_text="Done",
    )


def _show_identify_result(page, hash_value, possible_types):
    page.append_dim(f"Hash:      {hash_value}")
    page.append_dim("─" * 40)
    if possible_types:
        page.append_output("Possible hash types:")
        for hash_type in possible_types:
            page.append_accent(f"  • {hash_type}")
    else:
        page.append_warning("Could not identify hash type")
