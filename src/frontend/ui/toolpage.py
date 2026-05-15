"""
Gilfi - ToolPage
Reusable widget for each tool module.

Adds beyond the base template:
    * ``run_async()``                 - background work, GUI stays responsive
    * Cancel button                   - while a job is running, the Run
                                        button morphs into a Cancel button
                                        that detaches the worker (the
                                        backend call keeps running on the
                                        server, the worker thread exits
                                        when it naturally returns; the GUI
                                        is freed immediately)
    * Help dialog                     - if ``help_text`` is passed in or
                                        ``set_help_text`` is called, a small
                                        "?" button appears next to the title
    * ``status_changed(str, bool)``   - mirrored in the global status bar
    * ``busy_changed(bool)``          - drives the global progress indicator
    * Coloured output helpers         - append_success / append_error / ...
    * Copy / Clear buttons            - in the Output group header
    * ``set_output_widget(widget)``   - swap the default QTextEdit for a
                                        custom widget (e.g. a result table)
"""

from html import escape

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QGroupBox, QGridLayout, QCheckBox,
    QComboBox, QApplication, QSizePolicy, QMessageBox,
)
from PyQt6.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QTextCharFormat, QTextCursor, QKeySequence, QShortcut

from ui import theme as theme_module


# ---------------------------------------------------------------------------
# Worker for run_async()
# ---------------------------------------------------------------------------

class _AsyncWorker(QObject):
    """Runs a no-arg callable in a worker thread and reports the result.

    The worker is *cooperatively* cancellable. Cancellation works on the
    receiving end, not the worker end: ``cancel_async`` disconnects the
    GUI handlers from ``finished_ok``/``failed``, so when those signals
    eventually fire from the worker, the handlers no longer run. The
    worker still emits as usual so that the thread's ``quit`` slot (which
    stays connected) fires and the thread exits cleanly.

    Why this approach? ``QThread.terminate`` ends the OS thread mid-stack;
    if it was inside a C library holding a lock or in the middle of a
    memory allocation, the process can crash or deadlock. The Qt docs
    explicitly warn against it. ``requests`` → ``urllib3`` → OpenSSL is
    exactly the kind of stack that breaks under terminate, so we never
    call it.

    The ``_cancelled`` flag is a second safety net: if a result is already
    sitting in the GUI event queue when ``cancel_async`` runs, the slot
    invocation may still fire (Qt 6's queued connections can't always be
    cleanly preempted). The slot itself checks this flag and aborts.
    """

    finished_ok = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn):
        super().__init__()
        self._fn = fn
        self._cancelled = False

    def run(self):
        # NOTE: we emit regardless of ``_cancelled`` — emission is what makes
        # ``thread.quit`` fire (it's connected to these signals). The
        # ``_cancelled`` flag is consulted by the *slots*, not here.
        try:
            result = self._fn()
        except ConnectionError as e:
            self.failed.emit(f"__CONN__{e}")
        except Exception as e:
            self.failed.emit(str(e))
        else:
            self.finished_ok.emit(result)


# Semantic colour keys; resolved against the current theme at call time so
# theme switches re-colour subsequent appends without code changes.
_COLOR_KEYS = {
    "normal":  "output_text",
    "success": "success",
    "warning": "warning",
    "error":   "error",
    "dim":     "text_dim",
    "accent":  "accent",
}


class ToolPage(QWidget):

    status_changed = pyqtSignal(str, bool)  # (message, is_error)
    busy_changed = pyqtSignal(bool)         # True while a run_async job is in flight

    def __init__(self, title, description="", help_text="", parent=None):
        super().__init__(parent)
        self.title = title
        self.description = description
        self.help_text = help_text
        self.fields = {}
        self.isSplit = {}
        self.field_row = 0
        self.on_run = None
        self._default_button_text = "Start"

        # Async machinery
        self._thread = None
        self._worker = None

        # Output widget swap support
        self._output_text = None
        self._custom_output_widget = None
        self._custom_clear_cb = None
        self._custom_copy_cb = None

        self.setup_ui()

        self.initialCollumnCount = self.input_grid.columnCount() + 1

        # Escape cancels a running async job. The shortcut is unconditional
        # — cancel_async itself is a no-op when there's nothing to cancel.
        self._cancel_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self._cancel_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self._cancel_shortcut.activated.connect(self.cancel_async)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Title row with optional help button
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title_label = QLabel(self.title)
        title_label.setObjectName("toolTitle")
        title_row.addWidget(title_label)

        title_row.addStretch()

        self.btn_help = QPushButton("?")
        self.btn_help.setObjectName("iconBtn")
        self.btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_help.setToolTip("How does this work?")
        self.btn_help.setFixedWidth(28)
        self.btn_help.clicked.connect(self._show_help)
        self.btn_help.setVisible(bool(self.help_text))
        title_row.addWidget(self.btn_help)

        layout.addLayout(title_row)

        if self.description:
            desc_label = QLabel(self.description)
            desc_label.setObjectName("toolDesc")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addSpacing(4)

        # --- Input area ------------------------------------------------
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
        self.status_label.setObjectName("toolStatus")
        btn_row.addWidget(self.status_label)
        btn_row.addStretch()

        self.btn_run = QPushButton(self._default_button_text)
        self.btn_run.setObjectName("btnRun")
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.clicked.connect(self.handle_run)
        btn_row.addWidget(self.btn_run)

        input_layout.addLayout(btn_row)
        layout.addWidget(self.input_group)

        # --- Output area ----------------------------------------------
        self.output_group = QGroupBox("Output")
        self._output_outer_layout = QVBoxLayout(self.output_group)
        self._output_outer_layout.setContentsMargins(12, 18, 12, 10)
        self._output_outer_layout.setSpacing(6)

        header_row = QHBoxLayout()
        header_row.setSpacing(6)
        header_row.addStretch()

        self.btn_copy = QPushButton("Copy")
        self.btn_copy.setObjectName("iconBtn")
        self.btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy.setToolTip("Copy output to clipboard")
        self.btn_copy.clicked.connect(self.copy_output)
        header_row.addWidget(self.btn_copy)

        self.btn_clear = QPushButton("Clear")
        self.btn_clear.setObjectName("iconBtn")
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.setToolTip("Clear output")
        self.btn_clear.clicked.connect(self.clear_output)
        header_row.addWidget(self.btn_clear)

        self._output_outer_layout.addLayout(header_row)

        self._output_text = QTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setPlaceholderText("Results will appear here ...")
        self._output_text.setMinimumHeight(100)
        self._output_outer_layout.addWidget(self._output_text)

        self.output_text = self._output_text

        layout.addWidget(self.output_group, stretch=1)

    # ------------------------------------------------------------------
    # Help
    # ------------------------------------------------------------------
    def set_help_text(self, text: str):
        self.help_text = text or ""
        self.btn_help.setVisible(bool(self.help_text))

    def _show_help(self):
        if not self.help_text:
            return
        QMessageBox.information(self, f"{self.title} — How it works", self.help_text)

    # ------------------------------------------------------------------
    # Field helpers
    # ------------------------------------------------------------------
    def add_field(self, label, placeholder="", span=1):
        lbl = QLabel(label)
        lbl.setObjectName("fieldLabel")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        self.fields[label] = line_edit
        self.input_grid.addWidget(lbl, self.field_row, 0, Qt.AlignmentFlag.AlignRight)
        self.input_grid.addWidget(line_edit, self.field_row, 1, 1, span)
        self.field_row += 1

    def add_field_with_checkbox(self, label, placeholder="", checkbox_placeholder="",
                                checkbox_connect_to=None):
        lbl = QLabel(label)
        lbl.setObjectName("fieldLabel")
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        checkbox = QCheckBox()
        checkbox.setText(checkbox_placeholder)
        if checkbox_connect_to is not None:
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

        for col in range(column + 1, self.initialCollumnCount):
            item = self.input_grid.itemAtPosition(row, col)
            self.input_grid.addWidget(new_line_edit, row, col)
            if item is not None:
                self.input_grid.addWidget(item.widget(), row, col + 1)

    def undo_split_input_field(self, line_edit_name):
        original_line_edit = self.fields[line_edit_name]
        idx = self.input_grid.indexOf(original_line_edit)
        row, column, _, _ = self.input_grid.getItemPosition(idx)

        for col in range(column + 1, self.initialCollumnCount):
            item_before = self.input_grid.itemAtPosition(row, col)
            item = self.input_grid.itemAtPosition(row, col + 1)
            if item_before is not None:
                self.input_grid.removeWidget(item_before.widget())
            self.fields.pop((line_edit_name + "2"), None)
            if item is not None:
                self.input_grid.addWidget(item.widget(), row, col)

    def handle_split(self, line_edit_name):
        if self.isSplit[line_edit_name]:
            self.undo_split_input_field(line_edit_name)
            self.isSplit[line_edit_name] = False
        else:
            self.split_input_field(line_edit_name)
            self.isSplit[line_edit_name] = True

    # ------------------------------------------------------------------
    # I/O helpers
    # ------------------------------------------------------------------
    def get_input(self, label):
        widget = self.fields.get(label)
        if widget is None:
            return ""
        if isinstance(widget, QComboBox):
            return widget.currentText().strip()
        return widget.text().strip()

    def append_output(self, text):
        self._append_styled(str(text), "normal")

    def append_success(self, text):
        self._append_styled(str(text), "success")

    def append_warning(self, text):
        self._append_styled(str(text), "warning")

    def append_error(self, text):
        self._append_styled(str(text), "error")

    def append_dim(self, text):
        self._append_styled(str(text), "dim")

    def append_accent(self, text):
        self._append_styled(str(text), "accent")

    def _append_styled(self, text, color_key):
        if self._output_text is None:
            return

        palette = theme_module.current_theme()
        color_hex = palette.get(_COLOR_KEYS.get(color_key, "output_text"),
                                palette["output_text"])

        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))

        cursor = self._output_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if not self._output_text.document().isEmpty():
            cursor.insertBlock()
        cursor.insertText(text, fmt)
        self._output_text.setTextCursor(cursor)
        self._output_text.ensureCursorVisible()

    def clear_output(self):
        if self._custom_clear_cb is not None:
            self._custom_clear_cb()
        elif self._output_text is not None:
            self._output_text.clear()

    def copy_output(self):
        text = ""
        if self._custom_copy_cb is not None:
            try:
                text = str(self._custom_copy_cb() or "")
            except Exception:
                text = ""
        elif self._output_text is not None:
            text = self._output_text.toPlainText()
        if not text:
            self.set_status("Nothing to copy")
            return
        QApplication.clipboard().setText(text)
        self.set_status("Copied to clipboard")

    def set_status(self, text, error=False):
        # Property-driven QSS so the colour follows theme changes
        # automatically (see ``QLabel#toolStatus[statusTone="..."]`` in the
        # global stylesheet).
        self.status_label.setText(text)
        self.status_label.setProperty("statusTone", "error" if error else "success")
        self._repolish(self.status_label)
        self.status_changed.emit(text, error)

    def set_button_text(self, text):
        self.btn_run.setText(text)
        self._default_button_text = text

    # ------------------------------------------------------------------
    # Custom output widget
    # ------------------------------------------------------------------
    def set_output_widget(self, widget, clear_cb=None, copy_cb=None):
        if self._output_text is not None:
            self._output_outer_layout.removeWidget(self._output_text)
            self._output_text.deleteLater()
            self._output_text = None
            self.output_text = None

        widget.setSizePolicy(QSizePolicy.Policy.Expanding,
                             QSizePolicy.Policy.Expanding)
        self._output_outer_layout.addWidget(widget, stretch=1)
        self._custom_output_widget = widget
        self._custom_clear_cb = clear_cb
        self._custom_copy_cb = copy_cb
        self.btn_clear.setEnabled(clear_cb is not None)
        self.btn_copy.setEnabled(copy_cb is not None)

    # ------------------------------------------------------------------
    # Run handling
    # ------------------------------------------------------------------
    def handle_run(self):
        if callable(self.on_run):
            self.on_run(self)
        else:
            self.clear_output()
            self.append_error(f"[{self.title}] Module not connected.")
            self.set_status("No module connected", error=True)

    # ------------------------------------------------------------------
    # Async backend calls
    # ------------------------------------------------------------------
    def run_async(self, work_fn, on_success=None, on_error=None,
                  running_text="Running ...", done_text="Done"):
        """Run ``work_fn`` in a background thread, with cancel support."""
        if self._thread is not None and self._thread.isRunning():
            self.set_status("Already running ...", error=True)
            return False

        # Swap Run -> Cancel while the job is in flight.
        self.btn_run.setText("Cancel")
        self.btn_run.setProperty("mode", "cancel")
        self._repolish(self.btn_run)
        self.btn_run.setEnabled(True)
        try:
            self.btn_run.clicked.disconnect()
        except TypeError:
            pass
        self.btn_run.clicked.connect(self.cancel_async)

        self.set_status(running_text)
        self.busy_changed.emit(True)

        thread = QThread(self)
        worker = _AsyncWorker(work_fn)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        # The handlers consult worker._cancelled as a safety net in case
        # the slot was already queued in the GUI thread when cancel_async
        # ran. If cancelled, the handler does nothing — the visible state
        # was already reset by cancel_async.
        def _handle_success(result):
            if worker._cancelled:
                return
            self.set_status(done_text)
            if on_success is not None:
                try:
                    on_success(result)
                except Exception as e:
                    self.set_status("Error", error=True)
                    self.append_error(f"Error in result handler: {e}")

        def _handle_error(message):
            if worker._cancelled:
                return
            is_connection_error = message.startswith("__CONN__")
            clean = message[len("__CONN__"):] if is_connection_error else message
            if on_error is not None:
                try:
                    on_error(clean)
                except Exception as e:
                    self.append_error(f"Error in error handler: {e}")
            else:
                self.append_error(f"Error: {clean}")
            if is_connection_error:
                self.set_status("Backend not available", error=True)
                self.append_dim("Make sure the backend container is running:")
                self.append_dim("  ./backend-docker.sh start")
            else:
                self.set_status("Error", error=True)

        worker.finished_ok.connect(_handle_success)
        worker.failed.connect(_handle_error)

        # Make the thread quit when the worker is done — this MUST stay
        # connected even after cancel, otherwise the thread's event loop
        # runs forever.
        worker.finished_ok.connect(thread.quit)
        worker.failed.connect(thread.quit)

        # Cleanup: thread.finished fires on quit. We connect both our
        # GUI-state reset (for non-cancelled runs) and the C++ deletion.
        thread.finished.connect(self._on_async_thread_finished)
        thread.finished.connect(thread.deleteLater)
        worker.finished_ok.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)

        self._thread = thread
        self._worker = worker
        thread.start()
        return True

    def cancel_async(self):
        """Cancel a running async job — cooperatively, not by termination.

        We do NOT touch the worker thread. The HTTP call keeps running
        until it returns naturally; when it does, the worker emits as
        usual and the thread quits and deletes itself. We just stop
        caring about the result:

          1. Mark ``worker._cancelled = True`` (safety net for already-
             queued slot invocations).
          2. Disconnect the GUI handlers (``_handle_success``,
             ``_handle_error``) and ``_on_async_thread_finished`` so they
             never fire on the live ToolPage state.
          3. Drop our own references — a new task can start immediately.

        ``QThread.terminate`` is never called because it ends the OS
        thread mid-stack. If the thread was blocked inside OpenSSL,
        urllib3, malloc, or any other C library holding a lock, the
        process can crash or deadlock. The Qt docs explicitly warn
        against it.
        """
        if self._thread is None or not self._thread.isRunning():
            return

        worker = self._worker
        thread = self._thread

        # 1. Mark cancelled.
        if worker is not None:
            worker._cancelled = True

        # 2. Disconnect everything that touches GUI state. Leave the
        #    worker→thread.quit and thread.finished→deleteLater
        #    connections intact so the orphan cleans itself up.
        if worker is not None:
            try:
                worker.finished_ok.disconnect()  # disconnects ALL slots
            except TypeError:
                pass
            try:
                worker.failed.disconnect()
            except TypeError:
                pass
            # Re-attach only the bits we need for clean shutdown.
            worker.finished_ok.connect(thread.quit)
            worker.failed.connect(thread.quit)
            worker.finished_ok.connect(worker.deleteLater)
            worker.failed.connect(worker.deleteLater)
        try:
            thread.finished.disconnect(self._on_async_thread_finished)
        except TypeError:
            pass
        # Make sure the thread still self-deletes on finish.
        try:
            thread.finished.disconnect()  # clear any lingering connections
        except TypeError:
            pass
        thread.finished.connect(thread.deleteLater)

        # 3. Detach. A new run can start.
        self._thread = None
        self._worker = None

        # Visible reset.
        self._restore_run_button()
        self.set_status("Cancelled (backend job continues in background)",
                        error=True)
        self.busy_changed.emit(False)

    def _restore_run_button(self):
        """Put the Run button back into its idle state."""
        self.btn_run.setText(self._default_button_text)
        self.btn_run.setProperty("mode", "")
        self._repolish(self.btn_run)
        try:
            self.btn_run.clicked.disconnect()
        except TypeError:
            pass
        self.btn_run.clicked.connect(self.handle_run)
        self.btn_run.setEnabled(True)

    @staticmethod
    def _repolish(widget):
        """Force a stylesheet re-evaluation after a property change."""
        s = widget.style()
        s.unpolish(widget)
        s.polish(widget)

    def _on_async_thread_finished(self):
        """Cleanup for non-cancelled runs (fires via thread.finished)."""
        self._restore_run_button()
        self._worker = None
        self._thread = None
        self.busy_changed.emit(False)
