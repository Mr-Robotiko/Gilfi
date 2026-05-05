"""
Gilfi Module - Network Scanner
Scans a subnet for active devices.

NOTE: This module currently returns hardcoded sample data. Real ARP/ICMP
scanning is not yet implemented. The output is therefore not a real scan
result.

TODO: connect C module
"""

from ui.toolpage import ToolPage


def create_page():
    page = ToolPage(
        title="Network Scanner  [MOCK – not yet implemented]",
        description=("WARNING: this module currently returns hardcoded sample "
                     "data. Real ARP/ICMP scanning is not implemented yet.")
    )
    page.add_field("Subnet", "e.g. 192.168.1.0/24")
    page.add_field("Timeout (s)", "e.g. 3")
    page.set_button_text("Start Scan (mock)")
    page.on_run = run
    return page


def run(page):
    subnet = page.get_input("Subnet")

    if not subnet:
        page.set_status("Please enter a subnet", error=True)
        return

    page.clear_output()
    page.set_status("Returning mock data ...")

    page.append_output("WARNING: MOCK MODULE")
    page.append_output("The following list is hardcoded and is NOT the result of")
    page.append_output("an actual network scan.")
    page.append_output("─" * 60)
    page.append_output(f"Subnet: {subnet}")
    page.append_output("─" * 60)
    page.append_output("192.168.1.1     Gateway       (up)")
    page.append_output("192.168.1.12    Desktop-PC    (up)")
    page.append_output("192.168.1.34    Smartphone    (up)")
    page.append_output("192.168.1.100   NAS           (up)")
    page.append_output("─" * 60)
    page.append_output("4 hosts (mock)")

    page.set_status("Done (mock data – no real scan was performed)", error=True)
