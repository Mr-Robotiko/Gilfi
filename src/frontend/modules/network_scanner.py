"""
Gilfi Module - Network Scanner
Scans a subnet for active devices.
TODO: connect C module
"""

from ui.toolpage import ToolPage


def create_page():
    page = ToolPage(
        title="Network Scanner",
        description="Scans a subnet for active devices (ARP/ICMP)."
    )
    page.add_field("Subnet", "e.g. 192.168.1.0/24")
    page.add_field("Timeout (s)", "e.g. 3")
    page.set_button_text("Start Scan")
    page.on_run = run
    return page


def run(page):
    subnet = page.get_input("Subnet")

    if not subnet:
        page.set_status("Please enter a subnet", error=True)
        return

    page.clear_output()
    page.set_status("Scanning ...")

    # TODO: call C module here
    page.append_output(f"Subnet: {subnet}")
    page.append_output("─" * 40)
    page.append_output("192.168.1.1     Gateway       (up)")
    page.append_output("192.168.1.12    Desktop-PC    (up)")
    page.append_output("192.168.1.34    Smartphone    (up)")
    page.append_output("192.168.1.100   NAS           (up)")
    page.append_output("─" * 40)
    page.append_output("4 hosts found")

    page.set_status("Done - 4 hosts found")
