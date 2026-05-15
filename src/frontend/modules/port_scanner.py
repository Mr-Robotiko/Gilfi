"""
Gilfi Module - Port Scanner
Checks if specific ports are open on a target host. Results are rendered
in a sortable table with colour-coded state pills.
"""

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from ui.toolpage import ToolPage
from ui import theme as theme_module
import api_client


# ---------------------------------------------------------------------------
# Custom result table
# ---------------------------------------------------------------------------

class PortScanTable(QTableWidget):
    """A sortable result table with colour-coded open/closed states."""

    COLUMNS = ["Port", "TCP", "UDP", "Description"]

    def __init__(self, parent=None):
        super().__init__(0, len(self.COLUMNS), parent)
        self.setObjectName("resultTable")
        self.setHorizontalHeaderLabels(self.COLUMNS)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(False)
        self.setSortingEnabled(True)
        self.verticalHeader().setVisible(False)

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        # Cached state so we can re-colour existing rows when the theme
        # changes — QTableWidgetItem foreground colours are baked in at
        # ``populate`` time and don't follow the QSS cascade.
        self._last_result: dict = {}
        self._last_protocols: list = []
        theme_module.signals().theme_changed.connect(self._on_theme_changed)

    # ----- populate -----
    def populate(self, result: dict, protocols: list):
        """``protocols`` is a subset of [\"TCP\", \"UDP\"]."""
        self._last_result = result or {}
        self._last_protocols = list(protocols)
        self._render(self._last_result, self._last_protocols)

    def _on_theme_changed(self, _name):
        # Repaint whatever's currently in the table with the new palette.
        if self._last_result:
            self._render(self._last_result, self._last_protocols)

    def _render(self, result: dict, protocols: list):
        # Sorting must be off while we insert rows, otherwise auto-sort
        # races with item creation.
        self.setSortingEnabled(False)
        self.setRowCount(0)

        if not result:
            self.setSortingEnabled(True)
            return

        palette = theme_module.current_theme()

        # Sort by numeric port for a stable initial display.
        try:
            keys = sorted(result.keys(), key=lambda k: int(k))
        except (TypeError, ValueError):
            keys = list(result.keys())

        for port in keys:
            entry = result.get(port) or {}
            row = self.rowCount()
            self.insertRow(row)

            # Port (numeric sort) ----------------------------------------------
            port_item = QTableWidgetItem()
            port_item.setData(Qt.ItemDataRole.DisplayRole, int(port))
            port_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 0, port_item)

            # TCP / UDP cells --------------------------------------------------
            for col, proto in [(1, "TCP"), (2, "UDP")]:
                if proto in protocols:
                    state_open = entry.get(proto) == 0
                    item = self._make_state_item(state_open, palette)
                else:
                    item = QTableWidgetItem("—")
                    item.setForeground(QColor(palette["text_placeholder"]))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row, col, item)

            # Description ------------------------------------------------------
            desc = entry.get("Description")
            if isinstance(desc, (list, tuple)) and desc:
                desc = desc[0]
            desc_item = QTableWidgetItem(str(desc) if desc else "")
            desc_item.setForeground(QColor(palette["text"]))
            self.setItem(row, 3, desc_item)

        self.setSortingEnabled(True)

    @staticmethod
    def _make_state_item(is_open: bool, palette: dict) -> QTableWidgetItem:
        item = QTableWidgetItem("● Open" if is_open else "○ Closed")
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setForeground(QColor(palette["success" if is_open else "text_dim"]))
        # Sort key so "Open" sorts before "Closed".
        item.setData(Qt.ItemDataRole.UserRole, 0 if is_open else 1)
        return item

    # ----- callbacks for ToolPage Copy / Clear buttons -----
    def clear_rows(self):
        self._last_result = {}
        self.setSortingEnabled(False)
        self.setRowCount(0)
        self.setSortingEnabled(True)

    def to_text(self) -> str:
        if self.rowCount() == 0:
            return ""
        lines = ["\t".join(self.COLUMNS)]
        for row in range(self.rowCount()):
            cells = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                cells.append(item.text() if item is not None else "")
            lines.append("\t".join(cells))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_port(s: str):
    """Return port as int if valid (1..65535), else None."""
    if not s:
        return None
    try:
        n = int(s)
    except ValueError:
        return None
    return n if 1 <= n <= 65535 else None


# ---------------------------------------------------------------------------
# Page wiring
# ---------------------------------------------------------------------------

def create_page():
    page = ToolPage(
        title="Port Scanner",
        description="Scans ports on a target host and shows their status.",
        help_text=(
            "Probes one or more TCP/UDP ports on a target host to see which "
            "are open.\n\n"
            "Inputs:\n"
            "  • Target IP — the host to scan (e.g. 192.168.1.1 or scanme.nmap.org)\n"
            "  • Port — a single port number, or with 'Range' enabled, the "
            "start of a range. Leave empty to do a default scan.\n"
            "  • Protocol — TCP, UDP, or BOTH.\n\n"
            "Open ports often reveal what services a host is running. Use "
            "responsibly: scanning hosts you don't own can be against the law."
        )
    )

    page.add_field("Target IP", "e.g. 192.168.1.1")
    page.add_field_with_checkbox("Port", "e.g. 22,80,443", "Range",
                                 lambda: page.handle_split("Port"))
    page.add_dropdown(2, 1, ["TCP", "UDP", "BOTH"], "Protocol")
    page.set_button_text("Start Scan")
    page.on_run = run

    # Swap the default text output for a result table.
    table = PortScanTable()
    page.set_output_widget(
        table,
        clear_cb=table.clear_rows,
        copy_cb=table.to_text,
    )
    page.table = table  # keep a handy reference for ``run``
    return page


def run(page: ToolPage):
    target = page.get_input("Target IP")
    if not target:
        page.set_status("Please enter a target IP", error=True)
        return

    port = page.get_input("Port")
    port2 = page.get_input("Port2")

    # Build the scan range. [0] = full-scan sentinel for the backend.
    if not port:
        scan_range = [0]
    else:
        start = _parse_port(port)
        if start is None:
            page.set_status("Port must be a number between 1 and 65535",
                            error=True)
            return
        if port2:
            end = _parse_port(port2)
            if end is None:
                page.set_status("End port must be a number between 1 and 65535",
                                error=True)
                return
            if end < start:
                page.set_status("End port must be >= start port", error=True)
                return
            scan_range = [start, end]
        else:
            scan_range = [start]

    protocol = page.get_input("Protocol") or "BOTH"
    if protocol == "BOTH":
        protocols = ["TCP", "UDP"]
    else:
        protocols = [protocol]

    page.clear_output()

    # NB: connection_type must be passed by keyword. The third positional
    # parameter on api_client.scan_ports is ip_type, not connection_type.
    page.run_async(
        work_fn=lambda: api_client.scan_ports(
            target, scan_range, connection_type=protocol,
        ),
        on_success=lambda result: page.table.populate(result or {}, protocols),
        running_text="Scanning ...",
        done_text="Scan complete",
    )
