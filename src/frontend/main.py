"""
Gilfi - Security Tool Suite
Frontend application that communicates with dockerized backend via REST API
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont

from ui.mainwindow import MainWindow
from ui.theme import build_stylesheet, set_active_theme, DEFAULT_THEME


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gilfi")
    app.setApplicationDisplayName("Gilfi")
    app.setOrganizationName("Gilfi")

    # System-native sans-serif. No hardcoded family — Qt picks Segoe UI on
    # Windows, San Francisco on macOS, and the distro default on Linux,
    # all through the SansSerif style hint.
    default_font = QFont()
    default_font.setStyleHint(QFont.StyleHint.SansSerif)
    default_font.setPointSize(10)
    app.setFont(default_font)

    # Load theme from persisted settings (or fall back to default).
    settings = QSettings()
    theme_name = settings.value("appearance/theme", DEFAULT_THEME, type=str)
    set_active_theme(theme_name)
    app.setStyleSheet(build_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
