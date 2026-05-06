"""
Gilfi Module - Hash Generator & Identifier
Uses backend API via api_client instead of direct imports.
"""

from ui.toolpage import ToolPage
import api_client


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
    page.set_status("Computing ...")
    try:
        # Use API client instead of direct import
        result = api_client.hash_generate(text, algo)
        
        page.append_output(f"Input:     {text}")
        page.append_output(f"Algorithm: {algo.upper()}")
        page.append_output("─" * 40)
        page.append_output(f"Hash:      {result}")
        page.set_status("Done")
    except ConnectionError as e:
        page.set_status("Backend not available", error=True)
        page.append_output(str(e))
        page.append_output("\nMake sure the backend container is running:")
        page.append_output("  ./backend-docker.sh start")
    except Exception as e:
        page.set_status("Error", error=True)
        page.append_output(f"Error: {str(e)}")


def _run_identify(page, hash_value):
    page.set_status("Identifying ...")
    try:
        # Use API client instead of direct import
        possible_types = api_client.hash_identify(hash_value)
        
        page.append_output(f"Hash:      {hash_value}")
        page.append_output("─" * 40)
        
        if possible_types:
            page.append_output("Possible hash types:")
            for hash_type in possible_types:
                page.append_output(f"  • {hash_type}")
        else:
            page.append_output("Could not identify hash type")
        
        page.set_status("Done")
    except ConnectionError as e:
        page.set_status("Backend not available", error=True)
        page.append_output(str(e))
        page.append_output("\nMake sure the backend container is running:")
        page.append_output("  ./backend-docker.sh start")
    except Exception as e:
        page.set_status("Error", error=True)
        page.append_output(f"Error: {str(e)}")
