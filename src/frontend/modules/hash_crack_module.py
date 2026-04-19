"""
Gilfi Module - Hash Cracker
Uses backend API via api_client instead of direct imports.
"""

from ui.toolpage import ToolPage
import api_client


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
    page.set_status("Cracking ... (this may take a while)")
    
    # Use backend path for wordlist
    wordlist_path = "/app/data/wordlist/rockyou.txt"
    
    try:
        # Use API client instead of direct import
        result = api_client.hash_crack(hash_value, wordlist_path, algo)
        
        if result is None:
            page.append_output(f"Hash:      {hash_value}")
            page.append_output(f"Algorithm: {algo.upper()}")
            page.append_output("─" * 40)
            page.append_output("No plaintext found in wordlist")
            page.set_status("Not found")
        else:
            page.append_output(f"Hash:      {hash_value}")
            page.append_output(f"Algorithm: {algo.upper()}")
            page.append_output("─" * 40)
            page.append_output(f"Plaintext: {result}")
            page.set_status(f"Done - Cracked!")
            
    except ConnectionError as e:
        page.set_status("Backend not available", error=True)
        page.append_output(str(e))
        page.append_output("\nMake sure the backend container is running:")
        page.append_output("  ./backend-docker.sh start")
    except ValueError:
        page.append_output(f"[ERROR] Unsupported algorithm: '{algo}'")
        page.set_status("Unknown algorithm", error=True)
    except Exception as e:
        page.append_output(f"[ERROR] {e}")
        page.set_status("Error", error=True)

# Made with Bob
