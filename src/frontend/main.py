"""
Gilfi - Security Tool Suite
Einstiegspunkt der Anwendung
"""

import sys
import os

# backend hash-lib zum path hinzufügen damit wir die direkt importieren können
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HASH_LIB_PATH = os.path.join(BASE_DIR, "..", "backend", "hash-module", "src")
sys.path.insert(0, HASH_LIB_PATH)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from ui.mainwindow import MainWindow
from ui.style import STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Gilfi")
    app.setApplicationDisplayName("Gilfi")
    app.setOrganizationName("Gilfi")
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
