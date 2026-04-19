"""
Gilfi - Security Tool Suite
Frontend application that communicates with dockerized backend via REST API
"""

import sys
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
