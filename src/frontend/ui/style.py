"""
Gilfi - Dark Theme Stylesheet
"""

STYLESHEET = """

/* ── Allgemein ───────────────────────────────────────── */
QMainWindow {
    background: #1a1a2e;
}
QWidget {
    color: #e0e0e0;
    font-size: 13px;
}

/* ── Menüleiste ──────────────────────────────────────── */
QMenuBar {
    background: #16213e;
    color: #e0e0e0;
    font-weight: bold;
    padding: 3px 6px;
    border-bottom: 1px solid #0f3460;
}
QMenuBar::item {
    padding: 5px 12px;
    border-radius: 4px;
}
QMenuBar::item:selected {
    background: #0f3460;
}
QMenu {
    background: #16213e;
    border: 1px solid #0f3460;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 3px;
}
QMenu::item:selected {
    background: #0f3460;
}

/* ── Navigation ──────────────────────────────────────── */
QListWidget#navList {
    background: #16213e;
    border: none;
    outline: none;
    font-size: 13px;
    padding: 6px;
}
QListWidget#navList::item {
    color: #8a8aa0;
    padding: 10px 14px;
    border-radius: 5px;
    margin: 2px 4px;
}
QListWidget#navList::item:hover {
    background: #1a1a40;
    color: #e0e0e0;
}
QListWidget#navList::item:selected {
    background: #0f3460;
    color: #ffffff;
    font-weight: bold;
}

/* ── Splitter ────────────────────────────────────────── */
QSplitter::handle {
    background: #0f3460;
    width: 1px;
}

/* ── GroupBox ────────────────────────────────────────── */
QGroupBox {
    background: #1a1a2e;
    border: 1px solid #0f3460;
    border-radius: 6px;
    margin-top: 14px;
    padding: 16px 12px 10px 12px;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #53a8d8;
}

/* ── Eingabefelder ───────────────────────────────────── */
QLineEdit {
    background: #0f0f23;
    border: 1px solid #0f3460;
    border-radius: 4px;
    padding: 7px 10px;
    color: #e0e0e0;
}
QLineEdit:focus {
    border: 1px solid #53a8d8;
}
QLineEdit::placeholder {
    color: #555570;
}

/* ── Buttons ─────────────────────────────────────────── */
QPushButton#btnRun {
    background: #0f3460;
    color: #ffffff;
    font-weight: bold;
    border: none;
    border-radius: 4px;
    padding: 7px 22px;
}
QPushButton#btnRun:hover {
    background: #1a5276;
}
QPushButton#btnRun:pressed {
    background: #0a2640;
}

/* ── Output ──────────────────────────────────────────── */
QTextEdit {
    background: #0f0f23;
    border: 1px solid #0f3460;
    border-radius: 4px;
    padding: 8px;
    color: #4ade80;
    font-family: Consolas, monospace;
    font-size: 12px;
}

/* ── StatusBar ───────────────────────────────────────── */
QStatusBar {
    background: #16213e;
    color: #8a8aa0;
    border-top: 1px solid #0f3460;
    font-size: 11px;
}

/* ── Scrollbar ───────────────────────────────────────── */
QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #0f3460;
    border-radius: 4px;
    min-height: 24px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ── Ask Gilfi Toggle-Button ─────────────────────────────── */
QPushButton#chatToggle {
    background: #0f3460;
    color: #53a8d8;
    font-weight: bold;
    border: none;
    border-top: 1px solid #0f3460;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
}
QPushButton#chatToggle:hover {
    background: #1a5276;
    color: #ffffff;
}
QPushButton#chatToggle:checked {
    background: #1a5276;
    color: #4ade80;
}

/* ── Chat Dock ───────────────────────────────────────────── */
QDockWidget#chatDock {
    font-weight: bold;
    color: #53a8d8;
}
QDockWidget#chatDock::title {
    background: #16213e;
    padding: 6px;
    border-bottom: 1px solid #0f3460;
}
"""
