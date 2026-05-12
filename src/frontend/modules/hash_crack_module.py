"""
Gilfi Module - Hash Cracker
Dictionary-based hash cracking, performed by the backend API.
"""

from ui.toolpage import ToolPage
import api_client


def create_page():
    page = ToolPage(
        title="Hash Crack Module",
        description="Cracks MD5, SHA-1, SHA-256 and more based on rockyou.txt",
        help_text=(
            "Tries to reverse a hash by hashing every word in a wordlist "
            "(rockyou.txt, ~14M leaked passwords) and comparing.\n\n"
            "Fields:\n"
            "  • Hash — the hex string to crack.\n"
            "  • Algorithm — which algorithm produced the hash "
            "(md5, sha1, sha256, …).\n\n"
            "If the original plaintext is in the wordlist, it pops out. "
            "If not, you get 'not found' — but that doesn't mean the hash "
            "is safe, just that this particular attack didn't work.\n\n"
            "Cracking can take a while. Hit Cancel if you don't want to "
            "wait — the backend job will finish in the background but the "
            "GUI is free again."
        )
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

    def _on_success(result):
        page.append_dim(f"Hash:      {hash_value}")
        page.append_dim(f"Algorithm: {algo.upper()}")
        page.append_dim("─" * 40)
        if result is None:
            page.append_warning("No plaintext found in wordlist")
            page.set_status("Not found")
        else:
            page.append_success(f"Plaintext: {result}")
            page.set_status("Done - Cracked!")

    def _on_error(err_msg):
        if "algorithm" in err_msg.lower() or "unsupported" in err_msg.lower():
            page.append_error(f"[ERROR] Unsupported algorithm: '{algo}'")
            page.set_status("Unknown algorithm", error=True)
        else:
            page.append_error(f"[ERROR] {err_msg}")

    page.run_async(
        work_fn=lambda: api_client.hash_crack(hash_value, algo, 'common'),
        on_success=_on_success,
        on_error=_on_error,
        running_text="Cracking ... (this may take a while)",
        done_text="Done",
    )
