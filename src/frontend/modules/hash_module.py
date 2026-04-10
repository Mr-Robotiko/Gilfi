"""
Gilfi Modul - Hash Generator & Identifier
Nutzt die hash_lib aus src/backend/hash-module.
Kann hashes berechnen und hash-typen identifizieren.
"""

from ui.toolpage import ToolPage

# hash_lib wird über sys.path in main.py verfügbar gemacht
from hash_lib.hash_core.hasher import Hasher
from hash_lib.hash_identifier.identifier import HashIdentifier

_hasher = Hasher()
_identifier = HashIdentifier()


def create_page():
    page = ToolPage(
        title="Hash Module",
        description="Berechnet MD5, SHA-1, SHA-256 und weitere Hashes. "
                    "Kann auch Hash-Typen identifizieren."
    )
    page.add_field("Eingabetext", "Text zum Hashen oder Hash zum Identifizieren")
    page.add_field("Algorithmus", "z.B. md5, sha1, sha256 (leer = sha256)")
    page.add_field("Modus", "'hash' oder 'identify' (Standard: hash)")
    page.set_button_text("Ausführen")
    page.on_run = run
    return page


def run(page):
    text = page.get_input("Eingabetext")
    algo = page.get_input("Algorithmus") or "sha256"
    modus = page.get_input("Modus").lower() or "hash"

    if not text:
        page.set_status("Bitte Text eingeben", error=True)
        return

    page.clear_output()

    if modus == "identify":
        _run_identify(page, text)
    else:
        _run_hash(page, text, algo)


def _run_hash(page, text, algo):
    """hash berechnen mit dem angegebenen algo"""
    page.set_status("Berechne ...")

    try:
        result = _hasher.hash(text, algo)
        page.append_output(f"Input:       {text}")
        page.append_output(f"Algorithmus: {algo.upper()}")
        page.append_output("─" * 40)
        page.append_output(f"Hash: {result}")
        page.set_status(f"Fertig - {algo.upper()}")

    except ValueError:
        page.append_output(f"[FEHLER] Algorithmus '{algo}' wird nicht unterstützt.")
        page.set_status("Unbekannter Algorithmus", error=True)
    except Exception as e:
        page.append_output(f"[FEHLER] {e}")
        page.set_status("Fehler", error=True)


def _run_identify(page, hash_value):
    """hash-typ anhand der länge erkennen"""
    page.set_status("Identifiziere ...")

    results = _identifier.identify(hash_value)
    page.append_output(f"Hash:   {hash_value}")
    page.append_output(f"Länge:  {len(hash_value.strip())} Zeichen")
    page.append_output("─" * 40)

    if results:
        page.append_output("Mögliche Algorithmen:")
        for r in results:
            page.append_output(f"  - {r}")
    else:
        page.append_output("Kein passender Algorithmus gefunden.")

    page.set_status("Fertig")
