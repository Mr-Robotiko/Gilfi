"""
Gilfi Modul - Port Scanner
Prüft ob bestimmte Ports auf einem Host offen sind.
TODO: C-Modul anbinden
"""

from ui.toolpage import ToolPage


def create_page():
    page = ToolPage(
        title="Port Scanner",
        description="Scannt Ports auf einem Zielhost und zeigt deren Status."
    )
    page.add_field("Ziel-IP", "z.B. 192.168.1.1")
    page.add_field("Ports", "z.B. 22,80,443 oder 1-1024")
    page.add_field("Timeout (s)", "z.B. 2")
    page.set_button_text("Scan starten")
    page.on_run = run
    return page


def run(page):
    target = page.get_input("Ziel-IP")
    ports = page.get_input("Ports")

    if not target:
        page.set_status("Bitte Ziel-IP eingeben", error=True)
        return

    page.clear_output()
    page.set_status("Scanne ...")

    # TODO: Hier wird später das C-Modul aufgerufen
    page.append_output(f"Ziel:   {target}")
    page.append_output(f"Ports:  {ports or '1-1024 (Standard)'}")
    page.append_output("─" * 40)
    page.append_output("Port 22    SSH       closed")
    page.append_output("Port 80    HTTP      open")
    page.append_output("Port 443   HTTPS     open")
    page.append_output("Port 3306  MySQL     closed")
    page.append_output("─" * 40)
    page.append_output("2/4 Ports offen")

    page.set_status("Fertig - 4 Ports gescannt")
