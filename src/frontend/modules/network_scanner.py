"""
Gilfi Modul - Network Scanner
Sucht nach aktiven Geräten in einem Subnetz.
TODO: C-Modul anbinden
"""

from ui.toolpage import ToolPage


def create_page():
    page = ToolPage(
        title="Network Scanner",
        description="Scannt ein Subnetz nach aktiven Geräten (ARP/ICMP)."
    )
    page.add_field("Subnetz", "z.B. 192.168.1.0/24")
    page.add_field("Timeout (s)", "z.B. 3")
    page.set_button_text("Scan starten")
    page.on_run = run
    return page


def run(page):
    subnet = page.get_input("Subnetz")

    if not subnet:
        page.set_status("Bitte Subnetz eingeben", error=True)
        return

    page.clear_output()
    page.set_status("Scanne ...")

    # TODO: Hier wird später das C-Modul aufgerufen
    page.append_output(f"Subnetz: {subnet}")
    page.append_output("─" * 40)
    page.append_output("192.168.1.1     Gateway       (up)")
    page.append_output("192.168.1.12    Desktop-PC    (up)")
    page.append_output("192.168.1.34    Smartphone    (up)")
    page.append_output("192.168.1.100   NAS           (up)")
    page.append_output("─" * 40)
    page.append_output("4 Hosts gefunden")

    page.set_status("Fertig - 4 Hosts gefunden")
