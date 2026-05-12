"""
Gilfi - Settings dialog

Edits user-facing preferences and persists them via QSettings:
    appearance/theme              -> str (theme key)
    appearance/show_splash        -> bool
    backend/url                   -> str
    backend/heartbeat_interval_ms -> int

Emits ``settings_applied`` after the user clicks OK so the MainWindow can
react (re-apply stylesheet, push new URL to the api_client, retune the
heartbeat timer) without restarting the app.
"""

from PyQt6.QtCore import Qt, QSettings, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QPushButton,
    QFrame, QDialogButtonBox, QMessageBox,
)

from ui import theme as theme_module


# Defaults — also used to seed QSettings on first run.
DEFAULTS = {
    "appearance/theme": theme_module.DEFAULT_THEME,
    "appearance/show_splash": True,
    "backend/url": "http://localhost:8000",
    "backend/heartbeat_interval_ms": 10_000,
}


def load_settings() -> dict:
    """Read all known settings, falling back to defaults."""
    s = QSettings()
    return {
        "appearance/theme":
            s.value("appearance/theme", DEFAULTS["appearance/theme"], type=str),
        "appearance/show_splash":
            s.value("appearance/show_splash", DEFAULTS["appearance/show_splash"], type=bool),
        "backend/url":
            s.value("backend/url", DEFAULTS["backend/url"], type=str),
        "backend/heartbeat_interval_ms":
            s.value("backend/heartbeat_interval_ms",
                    DEFAULTS["backend/heartbeat_interval_ms"], type=int),
    }


class SettingsDialog(QDialog):
    """Modal dialog to edit user preferences."""

    settings_applied = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)
        self._settings = QSettings()
        self._build_ui()
        self._load_into_form()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # --- Appearance section ---------------------------------------
        layout.addWidget(self._section_header("Appearance"))

        form_appearance = QFormLayout()
        form_appearance.setSpacing(8)

        self.theme_combo = QComboBox()
        for key in theme_module.theme_names():
            self.theme_combo.addItem(theme_module.display_name(key), userData=key)
        form_appearance.addRow("Theme:", self.theme_combo)

        self.splash_check = QCheckBox("Show splash screen on startup")
        form_appearance.addRow("", self.splash_check)

        layout.addLayout(form_appearance)

        # --- Backend section ------------------------------------------
        layout.addWidget(self._section_header("Backend"))

        form_backend = QFormLayout()
        form_backend.setSpacing(8)

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("http://localhost:8000")
        form_backend.addRow("Base URL:", self.url_edit)

        self.heartbeat_spin = QSpinBox()
        self.heartbeat_spin.setRange(2_000, 120_000)   # 2 s .. 2 min
        self.heartbeat_spin.setSingleStep(1_000)
        self.heartbeat_spin.setSuffix(" ms")
        form_backend.addRow("Heartbeat interval:", self.heartbeat_spin)

        layout.addLayout(form_backend)

        # --- Arcade section ------------------------------------------
        layout.addWidget(self._section_header("Arcade"))

        arcade_row = QHBoxLayout()
        arcade_lbl = QLabel("Wipe all saved best scores:")
        arcade_lbl.setObjectName("toolDesc")
        arcade_row.addWidget(arcade_lbl)
        arcade_row.addStretch()
        self.reset_arcade_btn = QPushButton("Reset best scores …")
        self.reset_arcade_btn.setObjectName("secondaryBtn")
        self.reset_arcade_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_arcade_btn.clicked.connect(self._reset_arcade_scores)
        arcade_row.addWidget(self.reset_arcade_btn)
        layout.addLayout(arcade_row)

        layout.addStretch(1)

        # --- Buttons ---------------------------------------------------
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.RestoreDefaults
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        button_box.button(
            QDialogButtonBox.StandardButton.RestoreDefaults
        ).clicked.connect(self._restore_defaults)
        layout.addWidget(button_box)

    def _section_header(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("font-weight: bold; font-size: 12px;")
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        wrap = QHBoxLayout()
        wrap.setSpacing(8)
        wrap.addWidget(lbl)
        wrap.addWidget(line, stretch=1)
        container = QFrame()
        container.setLayout(wrap)
        return container

    # ------------------------------------------------------------------
    # Load / save
    # ------------------------------------------------------------------
    def _load_into_form(self):
        values = load_settings()

        # Theme dropdown by userData
        theme_key = values["appearance/theme"]
        idx = self.theme_combo.findData(theme_key)
        self.theme_combo.setCurrentIndex(idx if idx >= 0 else 0)

        self.splash_check.setChecked(values["appearance/show_splash"])
        self.url_edit.setText(values["backend/url"])
        self.heartbeat_spin.setValue(values["backend/heartbeat_interval_ms"])

    def _collect_values(self) -> dict:
        return {
            "appearance/theme":
                self.theme_combo.currentData() or theme_module.DEFAULT_THEME,
            "appearance/show_splash":
                self.splash_check.isChecked(),
            "backend/url":
                self.url_edit.text().strip() or DEFAULTS["backend/url"],
            "backend/heartbeat_interval_ms":
                int(self.heartbeat_spin.value()),
        }

    def _restore_defaults(self):
        self.theme_combo.setCurrentIndex(
            self.theme_combo.findData(DEFAULTS["appearance/theme"])
        )
        self.splash_check.setChecked(DEFAULTS["appearance/show_splash"])
        self.url_edit.setText(DEFAULTS["backend/url"])
        self.heartbeat_spin.setValue(DEFAULTS["backend/heartbeat_interval_ms"])

    def _on_accept(self):
        values = self._collect_values()
        for key, val in values.items():
            self._settings.setValue(key, val)
        self.settings_applied.emit(values)
        self.accept()

    def _reset_arcade_scores(self):
        """Wipe every ``arcade/<game>/*`` key from QSettings after confirmation."""
        confirm = QMessageBox.question(
            self, "Reset arcade best scores",
            "This will clear every saved best score and play history in the "
            "Arcade. The change cannot be undone.\n\nProceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        # Iterate over all known keys under the arcade/ group and remove them.
        # QSettings.allKeys with a group prefix returns keys relative to that
        # group; we wipe the whole group.
        self._settings.beginGroup("arcade")
        for key in self._settings.allKeys():
            self._settings.remove(key)
        self._settings.endGroup()
        self._settings.sync()
        QMessageBox.information(
            self, "Reset arcade best scores",
            "All arcade best scores have been cleared. Restart the app or "
            "reopen the Arcade to see the empty board."
        )
