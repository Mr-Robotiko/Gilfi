"""
Gilfi - ToolPage
Reusable widget for each tool module.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt


class ToolPage(QWidget):

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.fields = {}
        self.field_row = 0
        self.on_run = None

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        title_label = QLabel(self.title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title_label)

        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setStyleSheet("color: #8a8aa0; font-size: 12px;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addSpacing(4)

        # input area
        self.input_group = QGroupBox("Input")
        input_layout = QVBoxLayout(self.input_group)
        input_layout.setContentsMargins(12, 18, 12, 10)
        input_layout.setSpacing(8)

        self.input_grid = QGridLayout()
        self.input_grid.setHorizontalSpacing(10)
        self.input_grid.setVerticalSpacing(8)
        self.input_grid.setColumnStretch(1, 1)
        input_layout.addLayout(self.input_grid)

        btn_row = QHBoxLayout()
        self.status_label = QLabel("")
        btn_row.addWidget(self.status_label)
        btn_row.addStretch()

        self.btn_run = QPushButton("Start")
        self.btn_run.setObjectName("btnRun")
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.clicked.connect(self.handle_run)
        btn_row.addWidget(self.btn_run)

        input_layout.addLayout(btn_row)
        layout.addWidget(self.input_group)

        # output area
        self.output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(self.output_group)
        output_layout.setContentsMargins(12, 18, 12, 10)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Results will appear here ...")
        self.output_text.setMinimumHeight(100)
        output_layout.addWidget(self.output_text)

        layout.addWidget(self.output_group, stretch=1)

    def add_field(self, label, placeholder=""):
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #8a8aa0; font-size: 12px;")

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)

        self.fields[label] = line_edit
        self.input_grid.addWidget(lbl, self.field_row, 0, Qt.AlignmentFlag.AlignRight)
        self.input_grid.addWidget(line_edit, self.field_row, 1)
        self.field_row += 1

    def get_input(self, label):
        widget = self.fields.get(label)
        if widget:
            return widget.text().strip()
        return ""

    def append_output(self, text):
        self.output_text.append(text)

    def clear_output(self):
        self.output_text.clear()

    def set_status(self, text, error=False):
        color = "#f06b78" if error else "#4ade80"
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 11px;")

    def set_button_text(self, text):
        self.btn_run.setText(text)

    def handle_run(self):
        if callable(self.on_run):
            self.on_run(self)
        else:
            self.clear_output()
            self.append_output(f"[{self.title}] Module not connected.")
            self.set_status("No module connected", error=True)
