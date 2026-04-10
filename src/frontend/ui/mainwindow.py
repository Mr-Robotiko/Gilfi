"""
Gilfi - Main Window
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QListWidget,
    QStackedWidget, QLabel, QSplitter, QStatusBar,
    QFrame, QPushButton, QDockWidget
)
from PyQt6.QtCore import Qt

from modules import network_scanner, port_scanner, rsa_encryption, hash_module, hash_crack_module
from ui.chatwidget import ChatWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gilfi")
        self.setMinimumSize(900, 560)
        self.resize(1000, 650)

        self.setup_menubar()
        self.setup_central()
        self.setup_chatbot_dock()
        self.setup_statusbar()

        self.nav_list.setCurrentRow(0)

    def setup_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("  File  ")
        file_menu.addAction("Modul laden ...")
        file_menu.addSeparator()
        file_menu.addAction("Beenden").triggered.connect(self.close)

        edit_menu = menubar.addMenu("  Edit  ")
        edit_menu.addAction("Einstellungen ...")

        view_menu = menubar.addMenu("  View  ")
        view_menu.addAction("Vollbild umschalten")

        help_menu = menubar.addMenu("  Help  ")
        help_menu.addAction("Über Gilfi")

    def setup_central(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # left side - navigation
        nav_widget = QWidget()
        nav_widget.setMinimumWidth(190)
        nav_widget.setMaximumWidth(260)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(0)

        title = QLabel("  GILFI")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #53a8d8;"
            "padding: 14px 10px 2px 10px; letter-spacing: 2px;"
        )
        nav_layout.addWidget(title)

        subtitle = QLabel("  Security Tool Suite")
        subtitle.setStyleSheet(
            "color: #555570; font-size: 10px;"
            "padding: 0px 10px 10px 10px;"
        )
        nav_layout.addWidget(subtitle)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #0f3460;")
        nav_layout.addWidget(line)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        nav_layout.addWidget(self.nav_list, stretch=1)

        # chatbot toggle at the bottom
        self.chat_toggle = QPushButton("💬  Ask Gilfi")
        self.chat_toggle.setObjectName("chatToggle")
        self.chat_toggle.setCheckable(True)
        self.chat_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chat_toggle.clicked.connect(self.toggle_chatbot)
        nav_layout.addWidget(self.chat_toggle)

        splitter.addWidget(nav_widget)

        # right side - tool pages
        self.stack = QStackedWidget()
        splitter.addWidget(self.stack)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([210, 750])

        self.setCentralWidget(splitter)
        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.register_tools()

    def setup_chatbot_dock(self):
        self.chat_widget = ChatWidget()

        self.chat_dock = QDockWidget("Ask Gilfi", self)
        self.chat_dock.setObjectName("chatDock")
        self.chat_dock.setWidget(self.chat_widget)
        self.chat_dock.setMinimumWidth(320)

        self.chat_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.chat_dock)
        self.chat_dock.hide()
        self.chat_dock.visibilityChanged.connect(self.on_dock_visibility_changed)

    def toggle_chatbot(self):
        if self.chat_dock.isVisible():
            self.chat_dock.hide()
        else:
            self.chat_dock.show()

    def on_dock_visibility_changed(self, visible):
        self.chat_toggle.setChecked(visible)

    def setup_statusbar(self):
        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Bereit")

    def register_tools(self):
        """add new tools here"""
        tools = [
            ("Network Scanner",  network_scanner.create_page()),
            ("Port Scanner",     port_scanner.create_page()),
            ("RSA Encryption",   rsa_encryption.create_page()),
            ("Hash Module",      hash_module.create_page()),
            ("Hash Crack Module", hash_crack_module.create_page()),
        ]

        for name, page in tools:
            self.nav_list.addItem(name)
            self.stack.addWidget(page)

    def add_tool(self, name, page):
        self.nav_list.addItem(name)
        self.stack.addWidget(page)
