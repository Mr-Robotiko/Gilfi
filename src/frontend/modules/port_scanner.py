"""
Gilfi Module - Port Scanner
Checks if specific ports are open on a target host.
"""

from ui.toolpage import ToolPage
import api_client


def _parse_port(s: str):
    """Return port as int if valid (1..65535), else None."""
    if not s:
        return None
    try:
        n = int(s)
    except ValueError:
        return None
    return n if 1 <= n <= 65535 else None

def create_page():
    page = ToolPage(
        title="Port Scanner",
        description="Scans ports on a target host and shows their status."
    )

    page.add_field("Target IP", "e.g. 192.168.1.1")
    page.add_field_with_checkbox("Port", "e.g. 22,80,443", "Range", lambda: page.handle_split("Port"))
    page.add_dropdown(2, 1, ["TCP", "UDP", "BOTH"], "Protocol")
    page.set_button_text("Start Scan")
    page.on_run = run
    return page

def run(page: ToolPage):
    target = page.get_input("Target IP")
    if not target:
        page.set_status("Please enter a target IP", error=True)
        return

    port = page.get_input("Port")
    port2 = page.get_input("Port2")

    if not port:
        scan_range = [0]  # full scan – sentinel preserved for backend
    else:
        start = _parse_port(port)
        if start is None:
            page.set_status("Port must be a number between 1 and 65535", error=True)
            return

        if port2:
            end = _parse_port(port2)
            if end is None:
                page.set_status("End port must be a number between 1 and 65535", error=True)
                return
            if end < start:
                page.set_status("End port must be >= start port", error=True)
                return
            scan_range = [start, end]
        else:
            scan_range = [start]

    page.clear_output()
    call_port_scanner(page, target, scan_range)

def call_port_scanner(page, target, scan_range):
    page.set_status("Scanning...")
    try:
        # NB: connection_type must be passed by keyword. The third positional
        # parameter on api_client.scan_ports is ip_type, not connection_type.
        result = api_client.scan_ports(
            target, scan_range,
            connection_type=page.fields["Protocol"].currentText(),
        )
        print_result(page, result)
    except ConnectionError as e:
        page.set_status("Backend not available", error=True)
        page.append_output(str(e))
        page.append_output("\nMake sure the backend container is running:")
        page.append_output("  ./backend-docker.sh start")
    except Exception as e:
        page.set_status("Error", error=True)
        page.append_output(f"Error: {str(e)}")

def print_result(page, result):
    port = "Port".ljust(5)
    desc = "Description".rjust(2)
    prot = page.fields["Protocol"].currentText()
    prot_list = [prot]

    if prot == "BOTH":
        prot = "UDP      TCP"
        prot_list = ["UDP", "TCP"]

    prot = prot.center(2)
    header = port + "   " + prot + "     " + desc  

    page.append_output(header)

    for key in result.keys():
        port = str(key).ljust(5)
        prot_state = "Closed "
        desc = result.get(key).get("Description")

        if len(prot_list) == 1:
            if result.get(key).get(prot) == 0:
                prot_state = "Open   "
        else:
            if result.get(key).get("UDP") == 0:
                prot_state = "Open "
            if result.get(key).get("TCP") == 0:
                prot_state += "  Open "
            else:
                prot_state += "  Closed "

        if desc:
            desc = desc[0]

        page.append_output(f"{port}   {prot_state}   {desc}")

