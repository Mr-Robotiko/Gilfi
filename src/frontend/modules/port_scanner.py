"""
Gilfi Module - Port Scanner
Checks if specific ports are open on a target host.
TODO: connect to backend
"""

from ui.toolpage import ToolPage
from PyQt6.QtWidgets import (QWidget, QLineEdit)
from PyQt6.QtCore import Qt

import api_client

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

def run(page: ToolPage):
    target = page.get_input("Target IP")
    port = page.get_input("Port")
    port2 = page.get_input("Port2")
    scan_range = [0]

    if not target:
        page.set_status("Please enter a target IP", error=True)
        return

    page.clear_output()
    
    if port:
        scan_range[0] = int(port)
    if port2:
        if int(port2) < scan_range[0]:
            page.set_status("Ending port cant be smaller than starting port", error=True)
            return
        scan_range.append(int(port2))

    call_port_scanner(page, target, scan_range)

def call_port_scanner(page, target, scan_range):
    page.set_status("Scanning...")
    try:
        result = api_client.scan_ports(target, scan_range)
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
    for key in result.keys():
        page.append_output("Port | UDP | TCP | Description")
        page.append_output(str(key))
