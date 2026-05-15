"""
Gilfi - Main Window

The status bar serves four purposes:
    * a permanent backend-connectivity indicator on the left,
    * an indeterminate progress bar that appears while any tool page is
      running a background job,
    * the name of the currently selected tool on the right,
    * transient messages emitted by tool pages in between.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QListWidget,
    QStackedWidget, QLabel, QSplitter, QStatusBar,
    QFrame, QPushButton, QDockWidget, QProgressBar,
    QMessageBox, QApplication,
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, QObject, pyqtSignal, pyqtSlot, QSettings,
)
from PyQt6.QtGui import QKeySequence, QShortcut

from modules import (
    port_scanner, rsa_encryption,
    hash_module, hash_crack_module, password_analyzer, arcade,
)
from ui.animated_logo import AnimatedLogo
from ui.chatwidget import ChatWidget
from ui.splash_overlay import SplashOverlay
from ui.toolpage import ToolPage
from ui.settings_dialog import SettingsDialog, load_settings
from ui.nav_delegate import NavItemDelegate
from ui import theme as theme_module
import api_client


# ---------------------------------------------------------------------------
# Heartbeat worker (runs api_client.health_check() off the GUI thread)
# ---------------------------------------------------------------------------

class _HeartbeatWorker(QObject):
    """Pings the backend ``/health`` endpoint in a background thread.

    Emits ``result(healthy, info)`` where ``info`` is the parsed JSON from
    the endpoint (version, service name, etc.) on success, or an empty
    dict on failure. The Splash and the status bar both consume this.
    """

    result = pyqtSignal(bool, dict)

    @pyqtSlot()
    def check(self):
        try:
            client = api_client.get_client()
            data = client.health_check() or {}
            info = {
                "version": str(data.get("version", "")),
                "service": str(data.get("service", "")),
                "status":  str(data.get("status", "")),
            }
            self.result.emit(True, info)
        except Exception:
            self.result.emit(False, {})


class MainWindow(QMainWindow):

    # Used to request a heartbeat check on the worker thread. Connecting
    # this to the worker via QueuedConnection guarantees the check runs on
    # the worker's event loop, not on the GUI thread.
    _request_heartbeat = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gilfi")
        self.setMinimumSize(900, 560)
        self.resize(1000, 650)

        self._splash = None
        self._splash_started = False

        # Load persisted settings.
        prefs = load_settings()
        self._show_splash = prefs["appearance/show_splash"]
        api_client.get_client(prefs["backend/url"])

        # Number of currently-busy tool pages (drives the progress bar).
        self._busy_count = 0

        # Heartbeat machinery
        self._heartbeat_thread = QThread(self)
        self._heartbeat_worker = _HeartbeatWorker()
        self._heartbeat_worker.moveToThread(self._heartbeat_thread)
        self._heartbeat_worker.result.connect(self._on_heartbeat_result)
        self._request_heartbeat.connect(
            self._heartbeat_worker.check,
            Qt.ConnectionType.QueuedConnection,
        )
        self._heartbeat_thread.start()

        self._heartbeat_timer = QTimer(self)
        self._heartbeat_timer.setInterval(prefs["backend/heartbeat_interval_ms"])
        self._heartbeat_timer.timeout.connect(self._request_heartbeat.emit)

        self.setup_menubar()
        self.setup_central()
        self.setup_chatbot_dock()
        self.setup_statusbar()
        self._install_shortcuts()

        self.nav_list.setCurrentRow(0)
        self._update_current_tool_label()

        # Kick off the first heartbeat (on the worker thread) and start
        # the periodic timer.
        self._request_heartbeat.emit()
        self._heartbeat_timer.start()

    # ------------------------------------------------------------------
    # Menu / central widget / dock
    # ------------------------------------------------------------------
    def setup_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        file_menu.addAction("Exit").triggered.connect(self.close)

        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Settings ...").triggered.connect(self.open_settings)

        view_menu = menubar.addMenu("View")
        view_menu.addAction("Toggle Fullscreen").triggered.connect(
            self._toggle_fullscreen
        )

        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About Gilfi").triggered.connect(self._show_about)

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

        nav_layout.addSpacing(14)

        self.logo = AnimatedLogo()
        _sp = self.logo.sizePolicy()
        _sp.setRetainSizeWhenHidden(True)
        self.logo.setSizePolicy(_sp)
        # Hidden until the splash hands over (or shown immediately if the
        # splash is disabled).
        self.logo.hide()
        nav_layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignHCenter)

        subtitle = QLabel("Security Tool Suite")
        subtitle.setObjectName("navSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(subtitle)

        line = QFrame()
        line.setObjectName("navSeparator")
        line.setFrameShape(QFrame.Shape.HLine)
        nav_layout.addWidget(line)

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("navList")
        self._nav_delegate = NavItemDelegate(self.nav_list)
        self.nav_list.setItemDelegate(self._nav_delegate)
        nav_layout.addWidget(self.nav_list, stretch=1)

        # chatbot toggle at the bottom
        self.chat_toggle = QPushButton("Ask Gilfi")
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
        self.nav_list.currentRowChanged.connect(self._update_current_tool_label)
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

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def setup_statusbar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Left-hand permanent: backend connectivity indicator. Style is
        # property-driven via the global QSS so it follows theme changes
        # without code (see ``QLabel#backendStatus[state="..."]``).
        self.backend_status_label = QLabel("Backend: checking ...")
        self.backend_status_label.setObjectName("backendStatus")
        self.backend_status_label.setProperty("state", "checking")
        self.status_bar.addWidget(self.backend_status_label)

        # Indeterminate progress bar that appears while any tool page is busy.
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("statusProgress")
        self.progress_bar.setRange(0, 0)        # indeterminate / busy spinner
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setFixedWidth(120)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Right-hand permanent: currently selected tool name.
        self.current_tool_label = QLabel("")
        self.current_tool_label.setObjectName("statusBarDim")
        self.status_bar.addPermanentWidget(self.current_tool_label)

        # Transient messages from tool pages land here. The "Ready" gets
        # a short timeout so it doesn't permanently obscure the backend
        # indicator on the left (QStatusBar draws temporary messages over
        # widgets added with addWidget).
        self.status_bar.showMessage("Ready", 2000)

    def _update_current_tool_label(self, _row=None):
        item = self.nav_list.currentItem()
        if item is not None:
            self.current_tool_label.setText(item.text())
        else:
            self.current_tool_label.setText("")

    def _on_heartbeat_result(self, healthy: bool, info: dict):
        if healthy:
            self.backend_status_label.setText("● Backend: online")
            self.backend_status_label.setProperty("state", "online")
        else:
            self.backend_status_label.setText("● Backend: offline")
            self.backend_status_label.setProperty("state", "offline")
        # Property-change requires a repolish to pick up the new QSS rule.
        s = self.backend_status_label.style()
        s.unpolish(self.backend_status_label)
        s.polish(self.backend_status_label)

        # If the startup splash is still visible, mirror the result there.
        if self._splash is not None:
            self._splash.on_version_info(healthy, info)

    def _on_tool_status_changed(self, message: str, is_error: bool):
        """Mirror a ToolPage status message in the global status bar."""
        if is_error:
            self.status_bar.showMessage(message, 6000)
        else:
            self.status_bar.showMessage(message, 4000)

    def _on_tool_busy_changed(self, busy: bool):
        """Show / hide the indeterminate progress bar based on active jobs."""
        if busy:
            self._busy_count += 1
        else:
            self._busy_count = max(0, self._busy_count - 1)
        self.progress_bar.setVisible(self._busy_count > 0)

    # ------------------------------------------------------------------
    # Tool registration
    # ------------------------------------------------------------------
    def register_tools(self):
        """add new tools here"""
        tools = [
            ("Port Scanner",      port_scanner.create_page()),
            ("RSA Encryption",    rsa_encryption.create_page()),
            ("Hash Module",       hash_module.create_page()),
            ("Hash Crack Module", hash_crack_module.create_page()),
            ("Password Analyzer", password_analyzer.create_page()),
            ("Arcade",            arcade.create_page()),
        ]

        for name, page in tools:
            self.add_tool(name, page)

    def add_tool(self, name, page):
        self.nav_list.addItem(name)
        self.stack.addWidget(page)
        row = self.nav_list.count() - 1
        if isinstance(page, ToolPage):
            page.status_changed.connect(self._on_tool_status_changed)
            # Two consumers of busy_changed:
            #   * the global progress bar (counts active jobs)
            #   * the nav delegate (animates the pulsing dot on this row)
            page.busy_changed.connect(self._on_tool_busy_changed)
            page.busy_changed.connect(
                lambda busy, r=row: self._nav_delegate.set_busy(r, busy)
            )

    # ------------------------------------------------------------------
    # Shortcuts
    # ------------------------------------------------------------------
    def _install_shortcuts(self):
        """Ctrl+1..9 (Cmd+1..9 on macOS) jump directly to the matching tool.

        ``Qt.Modifier.CTRL`` is the platform-conditional modifier: on macOS
        it maps to the Command key, on Windows/Linux to Ctrl. Combining it
        with the digit keys via the enum (rather than a string like
        ``"Ctrl+1"``) gives the right binding on every OS.
        """
        digit_keys = [
            Qt.Key.Key_1, Qt.Key.Key_2, Qt.Key.Key_3,
            Qt.Key.Key_4, Qt.Key.Key_5, Qt.Key.Key_6,
            Qt.Key.Key_7, Qt.Key.Key_8, Qt.Key.Key_9,
        ]
        for i, key in enumerate(digit_keys, start=1):
            sc = QShortcut(QKeySequence(Qt.Modifier.CTRL | key), self)
            sc.activated.connect(lambda i=i: self._jump_to_tool(i - 1))

    def _jump_to_tool(self, index: int):
        if 0 <= index < self.nav_list.count():
            self.nav_list.setCurrentRow(index)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _show_about(self):
        tool_count = self.nav_list.count()
        # Build a native-format example like "⌘+1" on Mac or "Ctrl+1" on
        # Win/Linux so the help text matches what the user actually presses.
        example_seq = QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_1)
        native_first = example_seq.toString(QKeySequence.SequenceFormat.NativeText)
        # ``native_first`` is e.g. "Ctrl+1" or "⌘+1" — strip the digit so we
        # can render the range cleanly.
        if native_first.endswith("+1"):
            modifier = native_first[:-1]   # keeps trailing "+"
            shortcut_hint = f"{modifier}1..{modifier}{tool_count}"
        else:
            shortcut_hint = f"Ctrl+1..Ctrl+{tool_count}"
        QMessageBox.about(
            self, "About Gilfi",
            "<b>Gilfi</b> — Security Tool Suite<br>"
            "PyQt6 desktop frontend talking to a dockerized backend.<br><br>"
            f"Use {shortcut_hint} to jump between tools.<br>"
            "Press Escape to cancel a running task."
        )

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.settings_applied.connect(self._apply_settings)
        dlg.exec()

    def _apply_settings(self, values: dict):
        # Theme — rebuild stylesheet on the application.
        new_theme = values.get("appearance/theme", theme_module.DEFAULT_THEME)
        theme_changed = new_theme != theme_module.active_theme_name()
        if theme_changed:
            theme_module.set_active_theme(new_theme)
            app = QApplication.instance()
            if app is not None:
                app.setStyleSheet(theme_module.build_stylesheet())

        # Backend URL
        new_url = values.get("backend/url", "")
        if new_url:
            api_client.get_client(new_url)

        # Heartbeat interval
        new_interval = int(values.get("backend/heartbeat_interval_ms",
                                      self._heartbeat_timer.interval()))
        if new_interval != self._heartbeat_timer.interval():
            self._heartbeat_timer.setInterval(new_interval)

        # Splash preference takes effect on the next launch; we just
        # persist it. (Already saved by SettingsDialog.)
        self._show_splash = bool(values.get("appearance/show_splash", True))

        # Trigger an immediate heartbeat so (a) the user sees feedback right
        # away, and (b) the backend status label picks up the new theme
        # colours (the label colour is set in _on_heartbeat_result).
        self._request_heartbeat.emit()
        self.status_bar.showMessage("Settings applied", 3000)

    # ------------------------------------------------------------------
    # Startup splash overlay
    # ------------------------------------------------------------------
    def showEvent(self, event):
        super().showEvent(event)
        if not self._splash_started:
            self._splash_started = True
            if self._show_splash:
                self._splash = SplashOverlay(self, self.logo)
                self._splash.destroyed.connect(self._on_splash_destroyed)
                self._splash.start()
            else:
                # No splash: show the logo straight away.
                self.logo.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._splash is not None:
            self._splash.setGeometry(self.rect())

    def _on_splash_destroyed(self, *_):
        self._splash = None
        # Defensive: if the splash never reached _finish (e.g. the window was
        # closed mid-splash), make sure the static logo is visible afterwards.
        if not self.logo.isVisible():
            self.logo.show()

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._heartbeat_timer.stop()
        self._heartbeat_thread.quit()
        self._heartbeat_thread.wait(2000)
        super().closeEvent(event)
