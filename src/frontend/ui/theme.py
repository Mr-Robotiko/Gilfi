"""
Gilfi - Theme system

Themes are plain dicts of color tokens. ``build_stylesheet(theme_name)``
renders the same QSS template against the chosen palette. Modules that
need raw colors (e.g. for QTextCharFormat or custom-painted widgets) can
call ``current_theme()`` to read the palette directly.

A module-level Qt signal ``signals().theme_changed`` is emitted whenever
``set_active_theme()`` changes the active palette. Widgets that maintain
inline stylesheets (e.g. custom-painted overlays) should connect to this
signal and refresh themselves; widgets that style purely via object names
in the global QSS pick up the new colors automatically when the
application stylesheet is rebuilt.
"""

from PyQt6.QtCore import QObject, pyqtSignal


# ---------------------------------------------------------------------------
# Theme-change signal emitter (module-level singleton)
# ---------------------------------------------------------------------------

class _ThemeSignals(QObject):
    theme_changed = pyqtSignal(str)


_signals = _ThemeSignals()


def signals() -> _ThemeSignals:
    """Return the module-level signal emitter."""
    return _signals


# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------

THEMES = {
    "dark": {
        "name": "Dark (default)",
        "bg":              "#1a1a2e",
        "bg_alt":          "#16213e",
        "bg_input":        "#0f0f23",
        "border":          "#0f3460",
        "border_focus":    "#53a8d8",
        "text":            "#e0e0e0",
        "text_dim":        "#8a8aa0",
        "text_placeholder":"#555570",
        "accent":          "#53a8d8",
        "accent_strong":   "#0f3460",
        "accent_hover":    "#1a5276",
        "accent_pressed":  "#0a2640",
        "success":         "#4ade80",
        "warning":         "#fbbf24",
        "error":           "#f06b78",
        "error_hover":     "#d85a66",
        "output_text":     "#4ade80",
        "selection_bg":    "#0f3460",
        "selection_text":  "#ffffff",
    },
    "light": {
        "name": "Light",
        "bg":              "#f5f5fa",
        "bg_alt":          "#e8e8f0",
        "bg_input":        "#ffffff",
        "border":          "#c8c8d8",
        "border_focus":    "#3a7ca5",
        "text":            "#1a1a2e",
        "text_dim":        "#5a5a70",
        "text_placeholder":"#a0a0b0",
        "accent":          "#3a7ca5",
        "accent_strong":   "#2a5a7a",
        "accent_hover":    "#4a8cb5",
        "accent_pressed":  "#1a4a6a",
        "success":         "#16a34a",
        "warning":         "#d97706",
        "error":           "#dc2626",
        "error_hover":     "#b91c1c",
        "output_text":     "#1a1a2e",
        "selection_bg":    "#3a7ca5",
        "selection_text":  "#ffffff",
    },
    "hacker": {
        "name": "Hacker (green on black)",
        "bg":              "#000000",
        "bg_alt":           "#0a0a0a",
        "bg_input":        "#050505",
        "border":          "#0d3b0d",
        "border_focus":    "#39ff14",
        "text":            "#39ff14",
        "text_dim":        "#1f8a1f",
        "text_placeholder":"#0d3b0d",
        "accent":          "#39ff14",
        "accent_strong":   "#0d3b0d",
        "accent_hover":    "#1f8a1f",
        "accent_pressed":  "#0a2b0a",
        "success":         "#39ff14",
        "warning":         "#fbbf24",
        "error":           "#ff3939",
        "error_hover":     "#cc2929",
        "output_text":     "#39ff14",
        "selection_bg":    "#0d3b0d",
        "selection_text":  "#39ff14",
    },
}

DEFAULT_THEME = "dark"

# Active theme name. ``main.py`` updates this before the first stylesheet
# build; modules can read it via ``current_theme()``.
_active_theme_name = DEFAULT_THEME


def set_active_theme(name: str) -> None:
    global _active_theme_name
    if name not in THEMES:
        name = DEFAULT_THEME
    _active_theme_name = name
    _signals.theme_changed.emit(name)


def active_theme_name() -> str:
    return _active_theme_name


def current_theme() -> dict:
    """Return the currently active palette dict."""
    return THEMES[_active_theme_name]


def theme_names() -> list:
    """Return theme keys in display order."""
    return list(THEMES.keys())


def display_name(theme_key: str) -> str:
    return THEMES.get(theme_key, THEMES[DEFAULT_THEME])["name"]


# ---------------------------------------------------------------------------
# QSS template
# ---------------------------------------------------------------------------

_STYLESHEET_TEMPLATE = """
QMainWindow {{
    background: {bg};
}}
QWidget {{
    color: {text};
    font-size: 13px;
    selection-background-color: {selection_bg};
    selection-color: {selection_text};
}}

/* menu bar */
QMenuBar {{
    background: {bg_alt};
    color: {text};
    font-weight: bold;
    padding: 3px 6px;
    border-bottom: 1px solid {border};
}}
QMenuBar::item {{
    padding: 5px 12px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background: {accent_strong};
}}
QMenu {{
    background: {bg_alt};
    border: 1px solid {border};
    padding: 4px;
}}
QMenu::item {{
    padding: 6px 24px;
    border-radius: 3px;
}}
QMenu::item:selected {{
    background: {accent_strong};
}}

/* navigation */
QListWidget#navList {{
    background: {bg_alt};
    border: none;
    outline: none;
    font-size: 13px;
    padding: 6px;
}}
QListWidget#navList::item {{
    color: {text_dim};
    padding: 10px 14px;
    border-radius: 5px;
    margin: 2px 4px;
}}
QListWidget#navList::item:hover {{
    background: {bg};
    color: {text};
}}
QListWidget#navList::item:selected {{
    background: {accent_strong};
    color: {selection_text};
    font-weight: bold;
}}

/* splitter */
QSplitter::handle {{
    background: {border};
    width: 1px;
}}

/* group boxes */
QGroupBox {{
    background: {bg};
    border: 1px solid {border};
    border-radius: 6px;
    margin-top: 14px;
    padding: 16px 12px 10px 12px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: {accent};
}}

/* input fields */
QLineEdit {{
    background: {bg_input};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 7px 10px;
    color: {text};
}}
QLineEdit:focus {{
    border: 1px solid {border_focus};
}}
QLineEdit::placeholder {{
    color: {text_placeholder};
}}

QComboBox {{
    background: {bg_input};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 7px 10px;
    color: {text};
}}
QComboBox:focus {{
    border: 1px solid {border_focus};
}}
QComboBox QAbstractItemView {{
    background: {bg_input};
    color: {text};
    selection-background-color: {accent_strong};
    selection-color: {selection_text};
}}

QSpinBox {{
    background: {bg_input};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 6px 8px;
    color: {text};
}}
QSpinBox:focus {{
    border: 1px solid {border_focus};
}}

QCheckBox {{
    color: {text_dim};
    spacing: 6px;
}}

/* primary button */
QPushButton#btnRun {{
    background: {accent_strong};
    color: {selection_text};
    font-weight: bold;
    border: none;
    border-radius: 4px;
    padding: 7px 22px;
}}
QPushButton#btnRun:hover {{
    background: {accent_hover};
}}
QPushButton#btnRun:pressed {{
    background: {accent_pressed};
}}
QPushButton#btnRun:disabled {{
    background: {border};
    color: {text_dim};
}}

/* icon-style flat buttons (copy/clear in tool pages) */
QPushButton#iconBtn {{
    background: transparent;
    color: {text_dim};
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
}}
QPushButton#iconBtn:hover {{
    color: {text};
    border: 1px solid {border};
    background: {bg_input};
}}
QPushButton#iconBtn:pressed {{
    background: {accent_strong};
    color: {selection_text};
}}

/* output area */
QTextEdit {{
    background: {bg_input};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 8px;
    color: {output_text};
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
}}

/* result table (port scanner etc.) */
QTableWidget#resultTable {{
    background: {bg_input};
    border: 1px solid {border};
    border-radius: 4px;
    gridline-color: {border};
    color: {text};
    font-family: Consolas, "Courier New", monospace;
    font-size: 12px;
}}
QTableWidget#resultTable::item {{
    padding: 4px 8px;
}}
QTableWidget#resultTable::item:selected {{
    background: {accent_strong};
    color: {selection_text};
}}
QHeaderView::section {{
    background: {bg_alt};
    color: {text_dim};
    padding: 6px 8px;
    border: none;
    border-right: 1px solid {border};
    border-bottom: 1px solid {border};
    font-weight: bold;
}}

/* status bar */
QStatusBar {{
    background: {bg_alt};
    color: {text_dim};
    border-top: 1px solid {border};
    font-size: 11px;
}}
QStatusBar::item {{
    border: none;
}}
QProgressBar#statusProgress {{
    background: transparent;
    border: 1px solid {border};
    border-radius: 3px;
    height: 8px;
    max-width: 120px;
    text-align: center;
    color: transparent;
}}
QProgressBar#statusProgress::chunk {{
    background: {accent};
    border-radius: 3px;
}}

/* scrollbar */
QScrollBar:vertical {{
    background: {bg};
    width: 8px;
}}
QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {accent_strong};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {bg};
    height: 8px;
}}
QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}

/* ask gilfi toggle */
QPushButton#chatToggle {{
    background: {accent_strong};
    color: {accent};
    font-weight: bold;
    border: none;
    border-top: 1px solid {accent_strong};
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
}}
QPushButton#chatToggle:hover {{
    background: {accent_hover};
    color: {selection_text};
}}
QPushButton#chatToggle:checked {{
    background: {accent_hover};
    color: {success};
}}

/* chat dock */
QDockWidget#chatDock {{
    font-weight: bold;
    color: {accent};
}}
QDockWidget#chatDock::title {{
    background: {bg_alt};
    padding: 6px;
    border-bottom: 1px solid {border};
}}

/* labels that should follow the theme */
QLabel#toolTitle {{
    font-size: 18px;
    font-weight: bold;
    color: {text};
}}
QLabel#toolDesc, QLabel#fieldLabel, QLabel#navSubtitle, QLabel#statusBarDim {{
    color: {text_dim};
}}
QLabel#navSubtitle {{
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 4px 10px 12px 10px;
}}
QFrame#navSeparator {{
    color: {border};
    background: {border};
    max-height: 1px;
}}

/* Inline status label inside ToolPage Input boxes */
QLabel#toolStatus {{
    font-size: 11px;
    color: {text_dim};
}}
QLabel#toolStatus[statusTone="success"] {{
    color: {success};
}}
QLabel#toolStatus[statusTone="error"] {{
    color: {error};
}}

/* Backend connectivity indicator on the left side of the status bar */
QLabel#backendStatus {{
    padding: 0 8px;
    color: {text_dim};
}}
QLabel#backendStatus[state="online"] {{
    color: {success};
}}
QLabel#backendStatus[state="offline"] {{
    color: {error};
}}
QLabel#backendStatus[state="checking"] {{
    color: {text_dim};
}}

/* dialog */
QDialog {{
    background: {bg};
}}
QLabel {{
    color: {text};
}}

/* ===========================================================
   ARCADE styles
   All styled by object name so theme switching just works.
   =========================================================== */

/* Game cards on the arcade home screen */
QFrame#gameCard {{
    background: {bg_alt};
    border: 1px solid {border};
    border-radius: 10px;
}}
QFrame#gameCard[hovered="true"] {{
    background: {accent_strong};
    border: 2px solid {accent};
}}
QLabel#cardTitle {{
    color: {accent};
    font-size: 15px;
    font-weight: bold;
    background: transparent;
    border: none;
}}
QLabel#cardTag {{
    color: {warning};
    font-size: 9px;
    font-weight: bold;
    letter-spacing: 1px;
    background: transparent;
    border: none;
}}
QLabel#cardTagline {{
    color: {text_dim};
    font-size: 11px;
    background: transparent;
    border: none;
}}
QLabel#cardBestCaption {{
    color: {text_dim};
    font-size: 10px;
    background: transparent;
    border: none;
}}
QLabel#cardBestValue {{
    color: {text};
    background: transparent;
    border: none;
}}

/* Pill-header in each game */
QLabel#pillTitle {{
    font-size: 16px;
    font-weight: bold;
    color: {accent};
}}
QLabel#pillStreak {{
    color: {warning};
    font-weight: bold;
}}
QLabel#pillScore {{
    color: {accent};
    font-weight: bold;
}}
QLabel#pillBest {{
    color: {text_dim};
}}
QLabel#pillLives {{
    color: {error};
    font-weight: bold;
    font-size: 13px;
}}

/* Difficulty / level picker buttons */
QPushButton#levelBtn {{
    background: {bg_alt};
    color: {text_dim};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 7px 10px;
    font-size: 11px;
    font-weight: bold;
}}
QPushButton#levelBtn:hover {{
    background: {accent_hover};
    color: {selection_text};
}}
QPushButton#levelBtn:checked {{
    background: {accent_strong};
    color: {selection_text};
    border-color: {accent};
}}

/* Small secondary action buttons (Copy / Send to … / Reset / Hint) */
QPushButton#secondaryBtn {{
    background: {bg_alt};
    color: {accent};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 11px;
}}
QPushButton#secondaryBtn:hover {{
    background: {accent_strong};
    color: {selection_text};
}}
QPushButton#secondaryBtn:pressed {{
    background: {accent_hover};
}}
QPushButton#secondaryBtn:disabled {{
    background: {bg_input};
    color: {text_placeholder};
    border-color: {border};
}}

/* Display boxes (encrypted text, hash target, N=p*q, …) — color varies
   by the "tone" property so we can switch states without touching QSS. */
QLabel#displayBox {{
    padding: 12px;
    background: {bg_input};
    border-radius: 4px;
    border: 1px solid {border};
    color: {success};
}}
QLabel#displayBox[tone="success"] {{
    color: {success};
}}
QLabel#displayBox[tone="error"] {{
    color: {error};
}}
QLabel#displayBox[tone="accent"] {{
    color: {accent};
}}
QLabel#displayBox[tone="dim"] {{
    color: {text_dim};
}}
QLabel#displayBox[tone="warning"] {{
    color: {warning};
}}

/* Game-internal status / feedback labels */
QLabel#gameFeedback {{
    color: {text_dim};
}}
QLabel#gameFeedback[tone="success"] {{
    color: {success};
    font-weight: bold;
}}
QLabel#gameFeedback[tone="error"] {{
    color: {error};
    font-weight: bold;
}}
QLabel#gameFeedback[tone="warning"] {{
    color: {warning};
}}

QLabel#gameInfo {{
    color: {text_dim};
    font-size: 11px;
}}

QLabel#gameTimer {{
    color: {accent};
}}
QLabel#gameTimer[tone="error"] {{
    color: {error};
    font-weight: bold;
}}

/* Game-tile buttons (the 3x3 / 2x2 click grids). State is set via the
   "tone" property so theme switching keeps the right semantic color. */
QPushButton#tileBtn[tone="success"] {{
    background: {success};
    color: {bg_input};
    font-weight: bold;
}}
QPushButton#tileBtn[tone="error"] {{
    background: {error};
    color: {selection_text};
    font-weight: bold;
}}
QPushButton#tileBtn[tone="restart"] {{
    background: {accent_strong};
    color: {accent};
}}

/* Slider used by Crack-the-Code */
QSlider#gameSlider::groove:horizontal {{
    height: 6px;
    background: {bg_input};
    border-radius: 3px;
    border: 1px solid {border};
}}
QSlider#gameSlider::handle:horizontal {{
    background: {accent};
    width: 18px;
    margin: -7px 0;
    border-radius: 9px;
}}
QSlider#gameSlider::sub-page:horizontal {{
    background: {accent_strong};
    border-radius: 3px;
}}
QLabel#sliderValue {{
    color: {accent};
    min-width: 34px;
}}

/* Cancel-state run button (overrides #btnRun via property) */
QPushButton#btnRun[mode="cancel"] {{
    background: {error};
    color: {selection_text};
}}
QPushButton#btnRun[mode="cancel"]:hover {{
    background: {error_hover};
}}

/* Arcade home page (host of cards) */
QLabel#arcadeHomeTitle {{
    font-size: 20px;
    font-weight: bold;
    color: {text};
}}
QLabel#arcadeHomeDesc {{
    color: {text_dim};
    font-size: 12px;
}}
QLabel#categoryHeader {{
    color: {accent};
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 2px;
    padding: 8px 0 4px 2px;
}}
QLabel#cardLastPlayed {{
    color: {text_placeholder};
    font-size: 10px;
    background: transparent;
    border: none;
}}
"""


def build_stylesheet(theme_name: str = None) -> str:
    """Return the full QSS for ``theme_name`` (defaults to active theme)."""
    if theme_name is None:
        theme_name = _active_theme_name
    palette = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    return _STYLESHEET_TEMPLATE.format(**palette)
