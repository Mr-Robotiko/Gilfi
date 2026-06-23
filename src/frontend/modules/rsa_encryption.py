"""
Gilfi Module - RSA Encryption
Uses backend API via api_client. Async work is handled by ToolPage.run_async,
which keeps the GUI responsive and disables the Run button while the call
is in flight.
"""

from ui.toolpage import ToolPage
import api_client


def create_page():
    page = ToolPage(
        title="RSA Encryption",
        description="Generates an RSA key pair and performs encryption/decryption.",
        help_text=(
            "Demo of RSA, the asymmetric algorithm behind much of the "
            "modern web (TLS, signed software, SSH keys).\n\n"
            "Steps the module runs on the backend:\n"
            "  1. Pick two primes p, q and compute n = p*q.\n"
            "  2. Derive public exponent e and private exponent d so that "
            "(m^e)^d ≡ m (mod n).\n"
            "  3. Encrypt the plaintext as c = m^e mod n.\n"
            "  4. Decrypt c back to m to prove it works.\n\n"
            "Field:\n"
            "  • Plaintext (number) — your message, as an integer. RSA "
            "operates on numbers; in real-world TLS the message is the "
            "session key, which is then used for fast symmetric encryption.\n\n"
            "Note: the primes used here are tiny and unsafe — this is a "
            "teaching toy, not a real cryptosystem."
        )
    )
    page.add_field("Plaintext (number)", "e.g. 42, 12345")
    page.set_button_text("Encrypt")
    page.on_run = run
    return page


def run(page):
    plaintext = page.get_input("Plaintext (number)")

    if not plaintext:
        page.set_status("Please enter a number", error=True)
        return

    try:
        plaintext_int = int(plaintext)
    except ValueError:
        page.set_status("Integers only", error=True)
        return

    page.clear_output()

    page.run_async(
        work_fn=lambda: api_client.rsa_encrypt(plaintext_int),
        on_success=lambda result: _show_result(page, plaintext, result),
        running_text="Encrypting via backend API ...",
        done_text="Done",
    )


def _show_result(page, plaintext, result):
    if not result.get('success'):
        page.append_error(f"[ERROR] {result.get('error', 'Unknown error')}")
        page.set_status("Error", error=True)
        return

    page.append_accent("--- RSA Key Generation ---")

    # Extract p, q, n, phi from the raw output block if the backend sends one.
    if 'output' in result:
        for line in result['output'].split('\n'):
            if any(x in line for x in ['p =', 'q =', 'n =', 'phi =']):
                page.append_dim(line)

    page.append_dim("-" * 26)
    page.append_output("")

    if 'public_key' in result:
        page.append_success(f"Public Key (e, n) = {result['public_key']}")
    if 'private_key' in result:
        page.append_warning(f"Private Key (d, n) = {result['private_key']}")

    page.append_output("")
    page.append_dim(f"Original message (M) = {plaintext}")

    if 'ciphertext' in result:
        page.append_accent(f"Ciphertext (C) = {result['ciphertext']}")
    if 'decrypted' in result:
        page.append_success(f"Decrypted message (M*) = {result['decrypted']}")
