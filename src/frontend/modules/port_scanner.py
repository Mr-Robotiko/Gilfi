"""
Gilfi Module - Port Scanner
Checks if specific ports are open on a target host.
TODO: connect C module
"""

from ui.toolpage import ToolPage


def create_page():
    page = ToolPage(
        title="Port Scanner",
        description="Scans ports on a target host and shows their status."
    )
    page.add_field("Target IP", "e.g. 192.168.1.1")
    page.add_field("Ports", "e.g. 22,80,443 or 1-1024")
    page.add_dropdown(2, 1, ["BOTH", "TCP", "UDP"], "Protocol")
    page.set_button_text("Start Scan")
    page.on_run = run
    return page


def run(page):
    target = page.get_input("Target IP")
    ports = page.get_input("Ports")

    if not target:
        page.set_status("Please enter a target IP", error=True)
        return

    page.clear_output()
    page.set_status("Scanning ...")

    # TODO: call C module here
    page.append_output(f"Target: {target}")
    page.append_output(f"Ports:  {ports or '1-1024 (default)'}")
    page.append_output("─" * 40)
    page.append_output("Port 22    SSH       closed")
    page.append_output("Port 80    HTTP      open")
    page.append_output("Port 443   HTTPS     open")
    page.append_output("Port 3306  MySQL     closed")
    page.append_output("─" * 40)
    page.append_output("2/4 ports open")

    page.set_status("Done - 4 ports scanned")
