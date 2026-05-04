"""
Gilfi - ToolPage
Reusable widget for each tool module.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QGroupBox, QGridLayout, QCheckBox,
    QLayoutItem, QWidgetItem, QComboBox
)
from PyQt6.QtCore import Qt


class ToolPage(QWidget):

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.fields = {}
        self.isSplit = {}
        self.field_row = 0
        self.on_run = None

        self.setup_ui()

        self.initialCollumnCount = self.input_grid.columnCount() + 1

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

    def add_field(self, label, placeholder="", span=1):
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #8a8aa0; font-size: 12px;")

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)

        self.fields[label] = line_edit
        self.input_grid.addWidget(lbl, self.field_row, 0, Qt.AlignmentFlag.AlignRight)
        self.input_grid.addWidget(line_edit, self.field_row, 1, 1, span)
        self.field_row += 1

    def add_field_with_checkbox(self, label, placeholder="", checkbox_placeholder="", checkbox_connect_to=None):
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #8a8aa0; font-size: 12px;")

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)

        checkbox = QCheckBox()
        checkbox.setText(checkbox_placeholder)
        checkbox.setStyleSheet("color: #8a8aa0; font-size: 12px;")
        checkbox.stateChanged.connect(checkbox_connect_to)

        self.fields[label] = line_edit
        self.isSplit[label] = False
        self.input_grid.addWidget(lbl, self.field_row, 0, Qt.AlignmentFlag.AlignRight)
        self.input_grid.addWidget(line_edit, self.field_row, 1)
        self.input_grid.addWidget(checkbox, self.field_row, 2)
        self.field_row += 1

    def add_dropdown(self, row, col, options, label):
        combo_box = QComboBox()
        combo_box.addItems(options)
        self.input_grid.addWidget(combo_box, row, col)
        self.fields[label] = combo_box

    def split_input_field(self, line_edit_name):
        original_line_edit = self.fields[line_edit_name]
        idx = self.input_grid.indexOf(original_line_edit)
        row, column, _, _ = self.input_grid.getItemPosition(idx)

        new_line_edit = QLineEdit()
        new_line_edit.setPlaceholderText(original_line_edit.placeholderText())

        self.fields[line_edit_name + "2"] = new_line_edit

        # Shift everything after first line_edit to the right
        for col in range(column+1, self.initialCollumnCount):
            item = self.input_grid.itemAtPosition(row, col)
            self.input_grid.addWidget(new_line_edit, row, col)
            self.input_grid.addWidget(item.widget(), row, col+1)

        # Adjust the row span of the objects
        for row in range(self.input_grid.rowCount()):
            for col in range(self.initialCollumnCount):
                item = self.input_grid.itemAtPosition(row, col)

    def undo_split_input_field(self, line_edit_name):
        original_line_edit = self.fields[line_edit_name]
        idx = self.input_grid.indexOf(original_line_edit)
        row, column, _, _ = self.input_grid.getItemPosition(idx)

        for col in range(column+1, self.initialCollumnCount):
            item_before = self.input_grid.itemAtPosition(row, col)
            item = self.input_grid.itemAtPosition(row, col+1)
            
            self.input_grid.removeWidget(item_before.widget())
            self.fields.pop((line_edit_name + "2"), None)

            self.input_grid.addWidget(item.widget(), row, col)

    def handle_split(self, line_edit_name):
        if self.isSplit[line_edit_name]:
            self.undo_split_input_field(line_edit_name)
            self.isSplit[line_edit_name] = False
        else:
            self.split_input_field(line_edit_name)
            self.isSplit[line_edit_name] = True

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
