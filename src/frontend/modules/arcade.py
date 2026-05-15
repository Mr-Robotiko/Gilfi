"""
Gilfi Module - Arcade
Card-based mini-game launcher.

Theming approach
----------------
Almost all styling is driven by object names ("gameCard", "pillTitle",
"tileBtn", "displayBox", …) and dynamic properties ("tone", "hovered").
The actual colors live in the global QSS template (``ui/theme.py``),
which means a theme switch just rebuilds the application stylesheet and
every arcade widget repaints with the right palette — no manual refresh
needed.

The few widgets that genuinely need direct palette access (confetti
particles, flash-label backgrounds, dynamic ``setStyleSheet`` overrides
for short-lived feedback) connect to ``theme_module.signals().theme_changed``
and refresh themselves when the theme changes.

Why this matters: the previous version baked palette colors into inline
stylesheets at widget construction time, so theme switching left half
the arcade with stale colors (dark text on dark background on the hacker
theme, etc.).
"""

import hashlib
import math
import random
import time

from PyQt6.QtCore import (
    Qt, QTimer, QThread, QSettings, QPoint, QPropertyAnimation,
    QEasingCurve, pyqtSignal,
)
from PyQt6.QtGui import (
    QFont, QGuiApplication, QPainter, QColor, QKeySequence, QShortcut,
)
from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel,
    QPushButton, QLineEdit, QTextEdit, QGridLayout, QSlider, QGroupBox,
    QScrollArea, QMessageBox,
)

import api_client
from ui import theme as theme_module


# =============================================================================
# Score persistence
# =============================================================================

def _settings():
    return QSettings()


def load_best(game_key: str, default: int = 0) -> int:
    return int(_settings().value(f"arcade/{game_key}/best", default, type=int))


def save_best(game_key: str, value: int) -> bool:
    current = load_best(game_key)
    if int(value) > current:
        _settings().setValue(f"arcade/{game_key}/best", int(value))
        return True
    return False


def save_last_played(game_key: str) -> None:
    """Stamp when the user last actively engaged with this game."""
    _settings().setValue(f"arcade/{game_key}/last_played", int(time.time()))


def load_last_played(game_key: str) -> int:
    return int(_settings().value(f"arcade/{game_key}/last_played", 0, type=int))


def format_relative_time(ts: int) -> str:
    """Format a Unix timestamp as a short relative time. '' if ts == 0."""
    if ts == 0:
        return ""
    delta = max(0, int(time.time()) - ts)
    if delta < 60:    return "just now"
    if delta < 3600:  return f"{delta // 60}m ago"
    if delta < 86400: return f"{delta // 3600}h ago"
    if delta < 604800:   return f"{delta // 86400}d ago"
    if delta < 2592000:  return f"{delta // 604800}w ago"
    return f"{delta // 2592000}mo ago"


def hearts_for(lives: int, total: int = 3) -> str:
    """Return a heart string like '♥♥♡' for use in a lives label."""
    lives = max(0, min(lives, total))
    return ("♥" * lives) + ("♡" * (total - lives))


# =============================================================================
# Streak / combo tracker
# =============================================================================

class StreakTracker:
    def __init__(self):
        self.streak = 0

    def hit(self):
        self.streak += 1

    def miss(self):
        self.streak = 0

    def reset(self):
        self.streak = 0

    def multiplier(self) -> float:
        if self.streak <= 1: return 1.0
        if self.streak == 2: return 1.5
        if self.streak == 3: return 2.0
        if self.streak == 4: return 2.5
        return 3.0


# =============================================================================
# Cross-platform fonts
# =============================================================================

def mono_font(size=11, bold=False):
    f = QFont()
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setFamily("Consolas")  # falls back via StyleHint on Mac/Linux
    f.setPointSize(size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    return f


def ui_font(size=11, bold=False):
    f = QFont()
    f.setPointSize(size)
    if bold:
        f.setWeight(QFont.Weight.Bold)
    return f


# =============================================================================
# Small style helpers (used only for live feedback overrides; theme-safe
# because they pull from ``current_theme()`` at *call time*, never at
# widget-construction time, and feedback gets cleared on the next round
# anyway)
# =============================================================================

def _palette():
    return theme_module.current_theme()


def _repolish(widget: QWidget):
    """Force Qt to re-evaluate the stylesheet against current properties."""
    if widget is None:
        return
    s = widget.style()
    s.unpolish(widget)
    s.polish(widget)


def set_tone(widget: QWidget, tone: str):
    """Set the 'tone' property and re-polish so QSS picks it up."""
    widget.setProperty("tone", tone)
    _repolish(widget)


# =============================================================================
# Effects: Confetti, Pulse, Shake
# =============================================================================

class ConfettiOverlay(QWidget):
    FRAME_MS = 33
    LIFE_STEP = 0.025
    PARTICLE_COUNT = 36
    GRAVITY = 0.5

    # Picked at construction from the current palette; doesn't matter that
    # they don't update on theme switch — the overlay is alive < 2 seconds.
    PALETTE_KEYS = ("accent", "success", "warning", "error")

    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(parent.rect())

        cx = self.width() / 2
        cy = self.height() / 3.5
        p = _palette()
        colors = [QColor(p[k]) for k in self.PALETTE_KEYS]

        self.particles = []
        for _ in range(self.PARTICLE_COUNT):
            angle = random.uniform(-math.pi / 2 - 0.9, -math.pi / 2 + 0.9)
            speed = random.uniform(5, 12)
            self.particles.append({
                "x": cx + random.uniform(-6, 6),
                "y": cy,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "color": random.choice(colors),
                "size": random.uniform(5, 10),
                "rot": random.uniform(0, 360),
                "rot_vel": random.uniform(-12, 12),
                "life": 1.0,
            })

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step)
        self.timer.start(self.FRAME_MS)
        self.show()
        self.raise_()

    def _step(self):
        any_alive = False
        for prt in self.particles:
            if prt["life"] <= 0:
                continue
            prt["x"] += prt["vx"]
            prt["y"] += prt["vy"]
            prt["vy"] += self.GRAVITY
            prt["rot"] += prt["rot_vel"]
            prt["life"] -= self.LIFE_STEP
            if prt["life"] > 0:
                any_alive = True
        self.update()
        if not any_alive:
            self.timer.stop()
            self.deleteLater()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        for prt in self.particles:
            if prt["life"] <= 0:
                continue
            color = QColor(prt["color"])
            color.setAlphaF(max(0.0, min(1.0, prt["life"])))
            painter.setBrush(color)
            painter.save()
            painter.translate(prt["x"], prt["y"])
            painter.rotate(prt["rot"])
            s = prt["size"]
            painter.drawRect(int(-s / 2), int(-s / 2), int(s), int(s))
            painter.restore()


def flash_label(label: QLabel, tone: str = "success", duration_ms: int = 380):
    """
    Briefly highlight a label's background. Restores stylesheet after the
    duration. Theme-safe: only short-lived, and theme switch during the
    flash window just means the user sees the previous-palette flash and
    everything else updates correctly.
    """
    if label is None:
        return
    p = _palette()
    color_map = {
        "success": p["success"],
        "warning": p["warning"],
        "error": p["error"],
        "accent": p["accent"],
    }
    bg = color_map.get(tone, p["success"])
    fg = p["bg"]
    orig = label.styleSheet()
    label.setStyleSheet(
        orig + f"; background: {bg}; color: {fg}; "
        f"border-radius: 3px; padding: 2px 6px;"
    )
    QTimer.singleShot(duration_ms, lambda lbl=label, s=orig: lbl.setStyleSheet(s))


def shake_widget(widget, distance: int = 6, duration_ms: int = 280):
    if widget is None:
        return
    start = widget.pos()
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration_ms)
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    anim.setKeyValueAt(0.0, start)
    anim.setKeyValueAt(0.2, QPoint(start.x() + distance, start.y()))
    anim.setKeyValueAt(0.4, QPoint(start.x() - distance, start.y()))
    anim.setKeyValueAt(0.6, QPoint(start.x() + distance, start.y()))
    anim.setKeyValueAt(0.8, QPoint(start.x() - distance, start.y()))
    anim.setKeyValueAt(1.0, start)
    anim.start()
    widget._last_shake = anim


# =============================================================================
# Status-bar broadcast & cross-module navigation
# =============================================================================

def announce_best(widget, game_name: str, score):
    mw = widget.window()
    if hasattr(mw, 'statusBar'):
        mw.statusBar().showMessage(
            f"★ New best in {game_name}: {score}", 4000
        )


def _show_status(widget, msg, timeout=2000):
    mw = widget.window()
    if hasattr(mw, 'statusBar'):
        mw.statusBar().showMessage(msg, timeout)


def _send_to_module(widget, module_name, field_values, auto_run=False):
    mw = widget.window()
    if not (hasattr(mw, 'nav_list') and hasattr(mw, 'stack')):
        return False

    target_idx = None
    for i in range(mw.nav_list.count()):
        if mw.nav_list.item(i).text() == module_name:
            target_idx = i
            break
    if target_idx is None:
        return False

    page = mw.stack.widget(target_idx)
    if hasattr(page, 'fields'):
        for label, val in field_values.items():
            if label in page.fields:
                page.fields[label].setText(str(val))

    mw.nav_list.setCurrentRow(target_idx)

    if auto_run and hasattr(page, 'handle_run'):
        page.handle_run()

    return True


def _copy_to_clipboard(text):
    QGuiApplication.clipboard().setText(text)


# =============================================================================
# Help button helper
# =============================================================================

def make_help_button(parent_widget, title: str, body: str) -> QPushButton:
    btn = QPushButton("?")
    # Same object name as ToolPage's help button so the two look identical.
    btn.setObjectName("iconBtn")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setToolTip("How to play")
    btn.setFixedWidth(28)
    btn.clicked.connect(
        lambda: QMessageBox.information(parent_widget, f"{title} — How to play", body)
    )
    return btn


# =============================================================================
# Pill-header
# =============================================================================

class PillHeader(QWidget):
    """
    Compact game header. All labels are object-named so themes apply via
    the global QSS — no inline color literals here.
    """

    def __init__(self, game_name: str, help_text: str, game_key: str, parent=None):
        super().__init__(parent)
        self.game_name = game_name
        self.game_key = game_key
        self._build(help_text)

    def _build(self, help_text: str):
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)

        title = QLabel(self.game_name)
        title.setObjectName("pillTitle")
        row.addWidget(title)
        row.addStretch()

        self.streak_label = QLabel("")
        self.streak_label.setObjectName("pillStreak")
        row.addWidget(self.streak_label)

        self.score_label = QLabel("Score: 0")
        self.score_label.setObjectName("pillScore")
        row.addWidget(self.score_label)

        self.best_label = QLabel(f"Best: {load_best(self.game_key)}")
        self.best_label.setObjectName("pillBest")
        row.addWidget(self.best_label)

        row.addWidget(make_help_button(self.parent() or self, self.game_name, help_text))

    def set_score(self, score: int):
        self.score_label.setText(f"Score: {score}")
        flash_label(self.score_label, "success", 280)

    def set_best(self, score, is_new: bool = False):
        self.best_label.setText(f"Best: {score}" + (" ★ NEW!" if is_new else ""))
        if is_new:
            flash_label(self.best_label, "warning", 500)

    def set_streak(self, streak: int, multiplier: float):
        if streak >= 2:
            # Show a hint about the next-tier multiplier so the user can see
            # what one more hit would unlock. Stops at the max tier.
            tier_hints = {
                2: " — 1 more for ×2.0!",
                3: " — 1 more for ×2.5!",
                4: " — 1 more for ×3.0 (max)!",
            }
            hint = tier_hints.get(streak, "")
            self.streak_label.setText(
                f"🔥 Streak: {streak}  (×{multiplier:.1f}){hint}"
            )
            flash_label(self.streak_label, "warning", 260)
        else:
            self.streak_label.setText("")

    def reset_streak_with_shake(self):
        self.streak_label.setText("")
        shake_widget(self)


# =============================================================================
# Common game base
# =============================================================================

class BaseGame(QWidget):

    GAME_KEY = "unset"
    GAME_NAME = "Unnamed"
    HELP_TEXT = ""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.score = 0
        self.streak = StreakTracker()
        self.header = PillHeader(self.GAME_NAME, self.HELP_TEXT, self.GAME_KEY, self)

    def award(self, points: int):
        self.score += int(points)
        self.streak.hit()
        self.header.set_score(self.score)
        self.header.set_streak(self.streak.streak, self.streak.multiplier())
        save_last_played(self.GAME_KEY)

        if save_best(self.GAME_KEY, self.score):
            self.header.set_best(self.score, is_new=True)
            announce_best(self, self.GAME_NAME, self.score)
            ConfettiOverlay(self)

    def penalize(self):
        self.streak.miss()
        self.header.reset_streak_with_shake()
        save_last_played(self.GAME_KEY)

    def reset_score(self):
        self.score = 0
        self.streak.reset()
        self.header.score_label.setText("Score: 0")
        self.header.streak_label.setText("")

    def bind_number_keys(self, handler, count: int):
        """Wire keys ``1``..``count`` to ``handler(idx)``.

        ``handler`` is called with a zero-based index, so pressing ``1``
        invokes ``handler(0)``. Shortcuts are scoped to this game widget
        and its children, so they only fire while the game has focus.
        """
        if not hasattr(self, "_number_shortcuts"):
            self._number_shortcuts = []
        for i in range(count):
            sc = QShortcut(QKeySequence(str(i + 1)), self)
            sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            sc.activated.connect(lambda idx=i: handler(idx))
            self._number_shortcuts.append(sc)


# =============================================================================
# HoverableButton (used by Hash Hunter for hover preview)
# =============================================================================

class HoverableButton(QPushButton):
    hovered = pyqtSignal(bool)

    def enterEvent(self, e):
        self.hovered.emit(True)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.hovered.emit(False)
        super().leaveEvent(e)


# =============================================================================
# Math helpers
# =============================================================================

def caesar_shift(text, shift):
    out = []
    for c in text:
        if c.isupper():
            out.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
        elif c.islower():
            out.append(chr((ord(c) - ord('a') + shift) % 26 + ord('a')))
        else:
            out.append(c)
    return ''.join(out)


def is_prime(n):
    if n < 2: return False
    if n < 4: return True
    if n % 2 == 0: return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0: return False
    return True


def modinv(a, m):
    g, x, _ = _ext_gcd(a, m)
    if g != 1:
        return None
    return x % m


def _ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


# =============================================================================
# Reusable widget builders
# =============================================================================

def make_info_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("gameInfo")
    lbl.setWordWrap(True)
    return lbl


def make_display_label(tone: str = "success") -> QLabel:
    lbl = QLabel("")
    lbl.setObjectName("displayBox")
    lbl.setProperty("tone", tone)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setWordWrap(True)
    lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return lbl


def make_feedback_label() -> QLabel:
    lbl = QLabel("")
    lbl.setObjectName("gameFeedback")
    lbl.setWordWrap(True)
    return lbl


def make_difficulty_row(labels, on_pick) -> tuple:
    """Return (layout, [buttons]) for a "Difficulty: [E] [M] [H]" picker row."""
    row = QHBoxLayout()
    row.setSpacing(6)
    caption = QLabel("Difficulty:")
    caption.setObjectName("gameInfo")
    row.addWidget(caption)
    buttons = []
    for i, name in enumerate(labels):
        btn = QPushButton(name)
        btn.setObjectName("levelBtn")
        btn.setCheckable(True)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda checked=False, idx=i: on_pick(idx))
        row.addWidget(btn)
        buttons.append(btn)
    row.addStretch()
    return row, buttons


def refresh_diff_buttons(buttons, active_idx):
    for i, btn in enumerate(buttons):
        btn.setChecked(i == active_idx)


# =============================================================================
# Game 1: Crack the Code
# =============================================================================

PUZZLE_SENTENCES_EASY = [
    "HELLO GILFI", "I LOVE THIS APP", "GOOD MORNING WORLD",
    "PASSWORDS ARE IMPORTANT", "GILFI IS COOL", "USE STRONG PASSWORDS",
    "BACKUP YOUR DATA", "STAY SECURE ONLINE", "CRYPTO IS FUN",
    "TWO PLUS TWO IS FOUR",
]
PUZZLE_SENTENCES_MEDIUM = [
    "THE SECRETS OF THE CRYPTOGRAPHER ARE WELL GUARDED",
    "JULIUS CAESAR INVENTED THIS KIND OF ENCRYPTION",
    "GILFI IS THE BEST SECURITY SUITE ON CAMPUS",
    "IF YOU CAN READ THIS YOU CRACKED THE CAESAR",
    "NEVER USE PASSWORDS SHORTER THAN EIGHT CHARACTERS",
    "ASYMMETRIC ENCRYPTION IS A BRILLIANT IDEA",
    "THE STUDY OF SECRET COMMUNICATION IS CALLED CRYPTOLOGY",
    "IN COMPUTER SCIENCE NOTHING IS AS CERTAIN AS RANDOMNESS",
    "ALAN TURING WAS A BRITISH MATHEMATICIAN AND CODE BREAKER",
    "PUBLIC KEY AND PRIVATE KEY BELONG TOGETHER",
    "MY PASSWORD IS LONGER THAN EIGHTEEN CHARACTERS",
    "ENCRYPTION PROTECTS INDIVIDUAL PRIVACY",
]
PUZZLE_SENTENCES_HARD = [
    "QUANTUM CRYPTOGRAPHY MAY REPLACE TODAYS STANDARDS WITHIN A DECADE",
    "ZERO KNOWLEDGE PROOFS ALLOW VERIFICATION WITHOUT REVEALING SECRETS",
    "VENI VIDI VICI DIXIT IULIUS CAESAR APUD RUBICONEM FLUVIUM",
    "THE DIFFIE HELLMAN KEY EXCHANGE WAS PUBLISHED IN NINETEEN SEVENTY SIX",
    "ELLIPTIC CURVE CRYPTOGRAPHY OFFERS EQUIVALENT SECURITY WITH SMALLER KEYS",
    "A BRUTE FORCE ATTACK ON A TWO HUNDRED FIFTY SIX BIT KEY IS UNFEASIBLE",
    "SIDE CHANNEL ATTACKS EXPLOIT TIMING POWER CONSUMPTION OR ELECTROMAGNETIC LEAKS",
]


CRACK_HELP = (
    "Goal: figure out which Caesar shift was used and decrypt the text.\n\n"
    "How:\n"
    "  1. The encrypted text is shown at the top.\n"
    "  2. Drag the Shift slider. The 'Your Attempt' field updates live.\n"
    "  3. When the plaintext reads naturally, hit 'Solved!'.\n\n"
    "Scoring: faster solves earn more points. Difficulty and streak both "
    "multiply the score. Wrong guesses reset your streak.\n\n"
    "Real-world tie-in: Caesar is a 2000-year-old cipher, easily broken "
    "by trying all 25 shifts. Modern crypto is unbreakable for exactly "
    "this reason: there are too many keys to try."
)


class CrackTheCodeGame(BaseGame):
    GAME_KEY = "crack_the_code"
    GAME_NAME = "Crack the Code"
    HELP_TEXT = CRACK_HELP

    DIFFICULTIES = [
        ("Easy",   PUZZLE_SENTENCES_EASY,   1.0),
        ("Medium", PUZZLE_SENTENCES_MEDIUM, 1.5),
        ("Hard",   PUZZLE_SENTENCES_HARD,   2.5),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.difficulty_idx = 1
        self.current_shift = 0
        self.original = ""
        self.encrypted = ""
        self.start_time = 0.0
        self._setup_ui()
        self._new_puzzle()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "The text was shifted with a Caesar cipher. Move the slider until "
            "the plaintext makes sense. Uses: plain crypto math (no backend)."
        ))

        diff_row, self.diff_buttons = make_difficulty_row(
            [n for n, _, _ in self.DIFFICULTIES], self._pick_difficulty
        )
        layout.addLayout(diff_row)

        enc_group = QGroupBox("Encrypted")
        enc_l = QVBoxLayout(enc_group)
        self.encrypted_label = make_display_label("error")
        self.encrypted_label.setFont(mono_font(13, bold=True))
        enc_l.addWidget(self.encrypted_label)
        layout.addWidget(enc_group)

        slider_group = QGroupBox("Shift")
        slider_l = QVBoxLayout(slider_group)
        slider_row = QHBoxLayout()
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setObjectName("gameSlider")
        self.slider.setMinimum(0)
        self.slider.setMaximum(25)
        self.slider.valueChanged.connect(self._on_shift_changed)
        slider_row.addWidget(self.slider, stretch=1)
        self.shift_label = QLabel("0")
        self.shift_label.setObjectName("sliderValue")
        self.shift_label.setFont(mono_font(13, bold=True))
        self.shift_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider_row.addWidget(self.shift_label)
        slider_l.addLayout(slider_row)
        layout.addWidget(slider_group)

        dec_group = QGroupBox("Your Attempt")
        dec_l = QVBoxLayout(dec_group)
        self.decrypted_label = make_display_label("success")
        self.decrypted_label.setFont(mono_font(13, bold=True))
        dec_l.addWidget(self.decrypted_label)
        layout.addWidget(dec_group)

        btn_row = QHBoxLayout()
        self.status_label = make_feedback_label()
        btn_row.addWidget(self.status_label)
        btn_row.addStretch()

        self.submit_btn = QPushButton("Solved!")
        self.submit_btn.setObjectName("btnRun")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._check_answer)
        btn_row.addWidget(self.submit_btn)

        self.new_btn = QPushButton("New")
        self.new_btn.setObjectName("btnRun")
        self.new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_btn.clicked.connect(self._new_puzzle)
        btn_row.addWidget(self.new_btn)

        layout.addLayout(btn_row)
        layout.addStretch()
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)

    def _pick_difficulty(self, idx):
        self.difficulty_idx = idx
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)
        self.streak.reset()
        self.header.set_streak(0, 1.0)
        self._new_puzzle()

    def _new_puzzle(self):
        _, pool, _ = self.DIFFICULTIES[self.difficulty_idx]
        self.original = random.choice(pool)
        self.current_shift = random.randint(1, 25)
        self.encrypted = caesar_shift(self.original, self.current_shift)
        self.encrypted_label.setText(self.encrypted)
        self.slider.setValue(0)
        self._on_shift_changed(0)
        self.start_time = time.time()
        self.status_label.setText("New puzzle!")
        set_tone(self.status_label, "")

    def _on_shift_changed(self, value):
        self.shift_label.setText(str(value))
        self.decrypted_label.setText(caesar_shift(self.encrypted, -value))

    def _check_answer(self):
        if self.slider.value() == self.current_shift:
            elapsed = time.time() - self.start_time
            base_points = max(10, int(100 - elapsed * 2))
            _, _, diff_mult = self.DIFFICULTIES[self.difficulty_idx]
            streak_before = self.streak.streak + 1
            mult_after = StreakTracker(); mult_after.streak = streak_before
            streak_mult = mult_after.multiplier()
            points = int(base_points * diff_mult * streak_mult)
            self.award(points)
            self.status_label.setText(
                f"Correct! +{points}  ({elapsed:.1f}s, ×{diff_mult:.1f} diff, ×{streak_mult:.1f} streak)"
            )
            set_tone(self.status_label, "success")
            QTimer.singleShot(1800, self._new_puzzle)
        else:
            self.penalize()
            # Tell the user *how* close they were. Shift values cycle 0..25
            # so the minimal distance wraps.
            raw = abs(self.slider.value() - self.current_shift)
            wrap_dist = min(raw, 26 - raw)
            if wrap_dist == 1:
                msg = f"So close — you were 1 shift off! It was {self.current_shift}. Streak reset."
            elif wrap_dist == 2:
                msg = f"Almost — 2 shifts off. It was {self.current_shift}. Streak reset."
            else:
                msg = f"Nope, correct shift was {self.current_shift}. Streak reset!"
            self.status_label.setText(msg)
            set_tone(self.status_label, "error")


# =============================================================================
# Game 2: Hash Hunter
# =============================================================================

HASH_WORDS_EASY = [
    "password", "admin", "hello", "qwerty", "login", "master",
    "dragon", "secret", "welcome", "monkey", "letmein", "shadow",
    "batman", "ninja", "football", "iloveyou", "trustno1", "password1",
    "abc123", "sunshine",
]
HASH_WORDS_MEDIUM = [
    "princess", "superman", "asdf1234", "passw0rd", "starwars", "freedom",
    "whatever", "computer", "butterfly", "dragon123", "thunder", "mercedes",
    "charlie", "daniel", "peanut", "robert", "matrix", "harley",
    "bailey", "access",
]
HASH_WORDS_HARD = [
    "correcthorse", "batterystaple", "gilfi2024", "p@ssw0rd!", "Tr0ub4dor&3",
    "kryptonite", "openSesame", "Zaq1@Wsx", "Hunter2!", "Passphrase",
    "xkcd936", "Jurassic!Park", "abcdef123456", "Qwerty!2024", "moonlight99",
    "coffeeLover42", "BlueSky!77", "IceCream#01", "CodeBreaker9", "NightOwl2023",
]

HUNTER_HELP = (
    "Goal: pick the word that produces the displayed hash.\n\n"
    "How:\n"
    "  1. Read the target hash at the top.\n"
    "  2. The 3×3 grid shows nine candidate words.\n"
    "  3. Hover any tile to preview its hash live — the matching prefix "
    "is highlighted in green.\n"
    "  4. Click the matching word — or press keys 1..9 (reading order, "
    "top-left = 1).\n\n"
    "Difficulty rises with score (MD5 → SHA-1 → SHA-256). Faster answers "
    "score more; you have 3 lives.\n\n"
    "Bonus buttons: Copy hash, Send to Hash Module, Send to Crack Module."
)


class HashHunterGame(BaseGame):
    GAME_KEY = "hash_hunter"
    GAME_NAME = "Hash Hunter"
    HELP_TEXT = HUNTER_HELP
    ROUND_TIME_LIMIT = 12.0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lives = 3
        self.current_word = ""
        self.current_algo = "md5"
        self.round_start = 0.0
        self._accepting_clicks = True
        self._setup_ui()
        self._new_round()
        # Refresh hover preview palette when theme changes.
        theme_module.signals().theme_changed.connect(self._on_theme_changed)
        # Keys 1..9 map to the 3×3 grid in reading order (top-left = 1).
        self.bind_number_keys(self._key_tile, 9)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "Which word produces the hash shown? Hover to preview. "
            "Uses: local hashing (same algos as Hash Module)."
        ))

        hash_group = QGroupBox("Target Hash")
        hash_l = QVBoxLayout(hash_group)
        self.algo_label = QLabel("")
        self.algo_label.setObjectName("gameInfo")
        self.algo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hash_l.addWidget(self.algo_label)
        self.hash_label = make_display_label("success")
        self.hash_label.setFont(mono_font(11))
        hash_l.addWidget(self.hash_label)
        self.preview_label = QLabel("Hover a candidate to preview its hash …")
        self.preview_label.setObjectName("gameInfo")
        self.preview_label.setFont(mono_font(10))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setWordWrap(True)
        hash_l.addWidget(self.preview_label)
        layout.addWidget(hash_group)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setObjectName("secondaryBtn")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self._copy_hash)
        action_row.addWidget(self.copy_btn)
        self.to_hash_btn = QPushButton("Send to Hash Module")
        self.to_hash_btn.setObjectName("secondaryBtn")
        self.to_hash_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.to_hash_btn.clicked.connect(self._send_to_hash_module)
        action_row.addWidget(self.to_hash_btn)
        self.to_crack_btn = QPushButton("Send to Crack Module")
        self.to_crack_btn.setObjectName("secondaryBtn")
        self.to_crack_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.to_crack_btn.clicked.connect(self._send_to_crack_module)
        action_row.addWidget(self.to_crack_btn)
        layout.addLayout(action_row)

        grid_group = QGroupBox("Candidates")
        grid = QGridLayout(grid_group)
        grid.setSpacing(8)
        self.word_buttons = []
        for i in range(9):
            btn = HoverableButton("")
            btn.setObjectName("btnRun")
            btn.setMinimumHeight(38)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_word_clicked(idx))
            btn.hovered.connect(lambda hover, b=btn: self._on_btn_hover(b, hover))
            grid.addWidget(btn, i // 3, i % 3)
            self.word_buttons.append(btn)
        layout.addWidget(grid_group)

        status_row = QHBoxLayout()
        self.lives_label = QLabel(hearts_for(3))
        self.lives_label.setObjectName("pillLives")
        status_row.addWidget(self.lives_label)
        status_row.addStretch()
        self.feedback_label = make_feedback_label()
        status_row.addWidget(self.feedback_label)
        layout.addLayout(status_row)
        layout.addStretch()

    def _hash(self, text, algo):
        h = hashlib.new(algo)
        h.update(text.encode())
        return h.hexdigest()

    def _reset_tile(self, btn):
        btn.setProperty("tone", "")
        _repolish(btn)

    def _new_round(self):
        if self.score < 150:
            pool = HASH_WORDS_EASY
            self.current_algo = "md5"
        elif self.score < 400:
            pool = HASH_WORDS_EASY + HASH_WORDS_MEDIUM
            self.current_algo = "sha1"
        else:
            pool = HASH_WORDS_MEDIUM + HASH_WORDS_HARD
            self.current_algo = "sha256"

        self.current_word = random.choice(pool)
        others = random.sample([w for w in pool if w != self.current_word], 8)
        candidates = others + [self.current_word]
        random.shuffle(candidates)

        self.algo_label.setText(f"Algorithm: {self.current_algo.upper()}")
        self.hash_label.setText(self._hash(self.current_word, self.current_algo))
        set_tone(self.hash_label, "success")
        # First-ever round shows a one-time hint that hovering reveals the
        # candidate's hash; subsequent rounds just show the neutral prompt.
        s = _settings()
        if s.value("arcade/hash_hunter/seen_hover_hint", False, type=bool):
            self.preview_label.setText("Hover a candidate to preview its hash …")
            set_tone(self.preview_label, "")
        else:
            self.preview_label.setText(
                "💡 Tip: hover any tile to preview its hash live — "
                "the matching prefix is highlighted in green."
            )
            set_tone(self.preview_label, "warning")
            s.setValue("arcade/hash_hunter/seen_hover_hint", True)

        for btn, word in zip(self.word_buttons, candidates):
            btn.setText(word)
            btn.setProperty("word", word)
            btn.setEnabled(True)
            self._reset_tile(btn)

        self.round_start = time.time()

    def _on_btn_hover(self, btn, hover):
        if not hover or not btn.isEnabled():
            self.preview_label.setText("Hover a candidate to preview its hash …")
            return
        word = btn.property("word")
        if word is None:
            return
        candidate_hash = self._hash(word, self.current_algo)
        target = self.hash_label.text()
        match_len = 0
        for ca, cb in zip(candidate_hash, target):
            if ca == cb:
                match_len += 1
            else:
                break
        match_part = candidate_hash[:match_len]
        rest_part = candidate_hash[match_len:]
        p = _palette()
        # Inline span colors here are fine — they're refreshed on the next
        # hover, which happens often, and on theme switch we just keep
        # showing the placeholder until the user hovers again.
        self.preview_label.setText(
            f"<span style='color:{p['success']};'>{match_part}</span>"
            f"<span style='color:{p['text_dim']};'>{rest_part}</span>"
            f"<span style='color:{p['text_dim']}; font-size:10px;'>  ← '{word}'</span>"
        )

    def _on_theme_changed(self, _name):
        """Reset the hover preview text — its inline span colors are stale."""
        self.preview_label.setText("Hover a candidate to preview its hash …")

    def _key_tile(self, idx: int):
        """Keyboard handler: only forward to ``_on_word_clicked`` while the
        round is accepting clicks (i.e. buttons enabled and not in
        post-game-over restart state)."""
        if not getattr(self, "_accepting_clicks", True):
            return
        if 0 <= idx < len(self.word_buttons) and self.word_buttons[idx].isEnabled():
            self._on_word_clicked(idx)

    def _on_word_clicked(self, idx):
        btn = self.word_buttons[idx]
        word = btn.property("word")
        for b in self.word_buttons:
            b.setEnabled(False)
        elapsed = time.time() - self.round_start

        if word == self.current_word:
            time_factor = max(0.2, 1.0 - elapsed / self.ROUND_TIME_LIMIT)
            base = 50
            streak_before = self.streak.streak + 1
            mult_after = StreakTracker(); mult_after.streak = streak_before
            streak_mult = mult_after.multiplier()
            points = max(10, int(base * time_factor * streak_mult))
            self.award(points)
            btn.setObjectName("tileBtn")
            set_tone(btn, "success")
            self.feedback_label.setText(f"+{points} ({elapsed:.1f}s, ×{streak_mult:.1f})")
            set_tone(self.feedback_label, "success")
        else:
            self.lives -= 1
            self.penalize()
            self.lives_label.setText(hearts_for(self.lives))
            btn.setObjectName("tileBtn")
            set_tone(btn, "error")
            for b in self.word_buttons:
                if b.property("word") == self.current_word:
                    b.setObjectName("tileBtn")
                    set_tone(b, "success")
            self.feedback_label.setText(f"Was: {self.current_word}")
            set_tone(self.feedback_label, "error")

        if self.lives <= 0:
            QTimer.singleShot(1800, self._game_over)
        else:
            QTimer.singleShot(1500, self._new_round_and_restore_tiles)

    def _new_round_and_restore_tiles(self):
        # Put the tile buttons back to default styling.
        for btn in self.word_buttons:
            btn.setObjectName("btnRun")
            self._reset_tile(btn)
        self._new_round()

    def _copy_hash(self):
        _copy_to_clipboard(self.hash_label.text())
        _show_status(self, "Hash copied to clipboard", 2000)

    def _send_to_hash_module(self):
        ok = _send_to_module(self, "Hash Module", {
            "Input": self.hash_label.text(),
            "Algorithm": self.current_algo,
            "Mode": "identify",
        }, auto_run=True)
        if not ok:
            _show_status(self, "Could not find Hash Module", 2000)

    def _send_to_crack_module(self):
        ok = _send_to_module(self, "Hash Crack Module", {
            "Hash": self.hash_label.text(),
            "Algorithm": self.current_algo,
        }, auto_run=False)
        if not ok:
            _show_status(self, "Could not find Hash Crack Module", 2000)

    def _game_over(self):
        self._accepting_clicks = False
        self.hash_label.setText(f"GAME OVER  -  Final Score: {self.score}")
        set_tone(self.hash_label, "error")
        self.algo_label.setText("Click any tile to restart")
        self.feedback_label.setText("")
        self.copy_btn.setEnabled(False)
        self.to_hash_btn.setEnabled(False)
        self.to_crack_btn.setEnabled(False)
        for btn in self.word_buttons:
            btn.setText("Restart")
            btn.setEnabled(True)
            btn.setObjectName("tileBtn")
            set_tone(btn, "restart")
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(self._restart)

    def _restart(self):
        self._accepting_clicks = True
        self.reset_score()
        self.lives = 3
        self.lives_label.setText(hearts_for(3))
        self.copy_btn.setEnabled(True)
        self.to_hash_btn.setEnabled(True)
        self.to_crack_btn.setEnabled(True)
        for i, btn in enumerate(self.word_buttons):
            btn.setObjectName("btnRun")
            self._reset_tile(btn)
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(lambda checked=False, idx=i: self._on_word_clicked(idx))
        self._new_round()


# =============================================================================
# Game 3: Survive the Cracker
# =============================================================================

class CrackerWorker(QThread):
    done = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, password, algo="sha256"):
        super().__init__()
        self.password = password
        self.algo = algo
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            h = hashlib.new(self.algo)
            h.update(self.password.encode())
            hash_val = h.hexdigest()
            result = api_client.hash_crack(hash_val, self.algo)
            if self._cancelled:
                return
            self.done.emit(result)
        except ConnectionError as e:
            if self._cancelled:
                return
            self.error.emit(str(e))
        except Exception as e:
            if self._cancelled:
                return
            self.error.emit(str(e))


SURVIVE_HELP = (
    "Goal: invent a password that the cracker can't find in rockyou.txt "
    "(the most famous leaked password list, ~14M entries).\n\n"
    "How:\n"
    "  1. Type a candidate password.\n"
    "  2. Hit 'Start Defense'. The backend hashes it with SHA-256 and "
    "tries every word in rockyou.txt.\n"
    "  3. If the cracker finishes the dictionary without finding yours: "
    "you survived!\n\n"
    "Your best survival time is saved automatically.\n\n"
    "Reality check: surviving rockyou ≠ being secure. Brute force, "
    "credential stuffing and targeted attacks can still crack short or "
    "predictable passwords. Use long passphrases."
)


class SurviveTheCrackerGame(BaseGame):
    GAME_KEY = "survive_cracker_seconds"
    GAME_NAME = "Survive the Cracker"
    HELP_TEXT = SURVIVE_HELP

    def __init__(self, parent=None):
        super().__init__(parent)
        # This game uses time-survived as the score, so hide the score
        # label inherited from the header.
        self.header.score_label.setVisible(False)
        self.header.best_label.setText(
            f"Best survived: {load_best(self.GAME_KEY) / 10:.1f}s"
        )
        self.worker = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.start_time = 0.0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "Type a password; the cracker tries every entry in rockyou.txt. "
            "Survive the dictionary to win. Uses: Hash Crack Module (backend)."
        ))

        input_group = QGroupBox("Your Password")
        il = QVBoxLayout(input_group)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter the password you want to defend ...")
        self.password_input.returnPressed.connect(self._start_defense)
        il.addWidget(self.password_input)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.start_btn = QPushButton("Start Defense")
        self.start_btn.setObjectName("btnRun")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._start_defense)
        btn_row.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("btnRun")
        self.stop_btn.setProperty("mode", "cancel")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_defense)
        btn_row.addWidget(self.stop_btn)
        il.addLayout(btn_row)
        layout.addWidget(input_group)

        result_group = QGroupBox("Attack Log")
        rl = QVBoxLayout(result_group)
        self.timer_label = QLabel("0.0s")
        self.timer_label.setObjectName("gameTimer")
        self.timer_label.setFont(mono_font(14, bold=True))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(self.timer_label)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Attack log will appear here ...")
        self.log.setMinimumHeight(140)
        rl.addWidget(self.log)
        layout.addWidget(result_group, stretch=1)

    def _start_defense(self):
        password = self.password_input.text().strip()
        if not password:
            return
        if self.worker and self.worker.isRunning():
            return

        self.log.clear()
        self.log.append("[0.0s] Hashing password with SHA-256 ...")
        self.log.append("[0.0s] Launching dictionary attack (rockyou.txt) ...")
        self.log.append("")

        self.start_time = time.time()
        self.timer_label.setText("0.0s")
        set_tone(self.timer_label, "")
        self.timer.start(100)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        self.worker = CrackerWorker(password, algo="sha256")
        self.worker.done.connect(self._on_done)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _stop_defense(self):
        """Cancel the running defense — orphans the worker, frees the GUI.

        Same cooperative pattern as ``ToolPage.cancel_async``: the worker
        keeps running on the backend, but its emissions are dropped by the
        flag check, and we disconnect the GUI handlers so it can't touch
        the live state.
        """
        if self.worker is None or not self.worker.isRunning():
            return
        self.worker.cancel()
        try:
            self.worker.done.disconnect(self._on_done)
        except TypeError:
            pass
        try:
            self.worker.error.disconnect(self._on_error)
        except TypeError:
            pass
        self.worker = None
        self.timer.stop()
        self.log.append("")
        self.log.append("[cancelled] You bailed out. Backend job continues in background.")
        self.timer_label.setText("Cancelled")
        set_tone(self.timer_label, "error")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _tick(self):
        elapsed = time.time() - self.start_time
        self.timer_label.setText(f"{elapsed:.1f}s")

    def _on_done(self, result):
        self.timer.stop()
        elapsed = time.time() - self.start_time
        elapsed_tenths = int(elapsed * 10)
        improved = save_best(self.GAME_KEY, elapsed_tenths)
        if improved:
            self.header.best_label.setText(f"Best survived: {elapsed:.1f}s ★ NEW!")
            flash_label(self.header.best_label, "warning", 500)
            announce_best(self, self.GAME_NAME, f"{elapsed:.1f}s")
            ConfettiOverlay(self)

        if result is None:
            self.log.append(f"[{elapsed:.1f}s] Dictionary exhausted.")
            self.log.append("")
            self.log.append("=" * 50)
            self.log.append("YOUR PASSWORD SURVIVED!")
            self.log.append(f"    Time held: {elapsed:.1f}s")
            self.log.append("    Not found in rockyou.txt (14M+ leaked passwords)")
            self.log.append("=" * 50)
            self.log.append("")
            self.log.append("Note: surviving rockyou is not a guarantee of security.")
            self.timer_label.setText(f"SURVIVED  ({elapsed:.1f}s)")
            set_tone(self.timer_label, "")
        else:
            self.log.append(f"[{elapsed:.1f}s] MATCH FOUND!")
            self.log.append("")
            self.log.append("=" * 50)
            self.log.append(f"PASSWORD CRACKED IN {elapsed:.1f}s")
            self.log.append(f"    Plaintext: {result}")
            self.log.append("=" * 50)
            self.log.append("")
            self.log.append("Your password was in rockyou.txt - it was leaked in past breaches.")
            self.timer_label.setText(f"CRACKED  ({elapsed:.1f}s)")
            set_tone(self.timer_label, "error")

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _on_error(self, err):
        self.timer.stop()
        self.log.append(f"[ERROR] {err}")
        self.log.append("")
        self.log.append("Make sure the backend container is running:")
        self.log.append("  ./backend-docker.sh start")
        self.timer_label.setText("Backend offline")
        set_tone(self.timer_label, "error")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


# =============================================================================
# Game 4: Factorize!
# =============================================================================

FACTORIZE_HELP = (
    "Goal: find the two prime numbers p and q whose product is N.\n\n"
    "How:\n"
    "  1. Pick a level (1–4 progressively bigger N; level 5 is BOSS).\n"
    "  2. The number N is shown.\n"
    "  3. Type p and q (in any order) and hit Check.\n"
    "  4. Solve before the timer runs out!\n\n"
    "Streak multiplier kicks in after 2 correct in a row. A miss or "
    "timeout resets it.\n\n"
    "Real-world tie-in: RSA security rests on the assumption that "
    "factoring is hard. The BOSS level has a 20-digit N; real RSA uses "
    "600+. The best known algorithms would take longer than the age of "
    "the universe to factor a real RSA modulus."
)


class FactorizeGame(BaseGame):
    GAME_KEY = "factorize"
    GAME_NAME = "Factorize!"
    HELP_TEXT = FACTORIZE_HELP
    LEVELS = [(2, 20, 30), (10, 100, 45), (100, 1000, 60), (1000, 10000, 90)]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.level = 0
        self.p = 0
        self.q = 0
        self.n = 0
        self.time_left = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._setup_ui()
        self._new_level()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "RSA is based on the difficulty of factoring large numbers into primes. "
            "Find p and q such that p * q = N."
        ))

        picker_group = QGroupBox("Pick Level")
        pg = QHBoxLayout(picker_group)
        pg.setSpacing(6)
        self.level_buttons = []
        for i, lbl in enumerate(["Level 1", "Level 2", "Level 3", "Level 4", "BOSS"]):
            btn = QPushButton(lbl)
            btn.setObjectName("levelBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, idx=i: self._pick_level(idx))
            pg.addWidget(btn)
            self.level_buttons.append(btn)
        layout.addWidget(picker_group)

        n_group = QGroupBox("N = p * q")
        nl = QVBoxLayout(n_group)
        self.n_label = make_display_label("success")
        self.n_label.setFont(mono_font(18, bold=True))
        nl.addWidget(self.n_label)
        layout.addWidget(n_group)

        input_group = QGroupBox("Your Factors")
        ig = QGridLayout(input_group)
        ig.setHorizontalSpacing(10)
        ig.setVerticalSpacing(8)
        p_lbl = QLabel("p =")
        p_lbl.setObjectName("gameInfo")
        ig.addWidget(p_lbl, 0, 0, Qt.AlignmentFlag.AlignRight)
        self.p_input = QLineEdit()
        self.p_input.setPlaceholderText("First prime")
        ig.addWidget(self.p_input, 0, 1)
        q_lbl = QLabel("q =")
        q_lbl.setObjectName("gameInfo")
        ig.addWidget(q_lbl, 1, 0, Qt.AlignmentFlag.AlignRight)
        self.q_input = QLineEdit()
        self.q_input.setPlaceholderText("Second prime")
        self.q_input.returnPressed.connect(self._check_answer)
        ig.addWidget(self.q_input, 1, 1)
        self.submit_btn = QPushButton("Check")
        self.submit_btn.setObjectName("btnRun")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._check_answer)
        ig.addWidget(self.submit_btn, 2, 1)
        layout.addWidget(input_group)

        sr = QHBoxLayout()
        self.level_label = QLabel("Level 1/5")
        self.level_label.setObjectName("pillScore")
        sr.addWidget(self.level_label)
        sr.addStretch()
        self.timer_label = QLabel("")
        self.timer_label.setObjectName("gameTimer")
        self.timer_label.setFont(mono_font(12, bold=True))
        sr.addWidget(self.timer_label)
        layout.addLayout(sr)

        self.status_label = make_feedback_label()
        layout.addWidget(self.status_label)
        layout.addStretch()

    def _new_level(self):
        if self.level >= len(self.LEVELS):
            self._show_boss()
            return
        lo, hi, secs = self.LEVELS[self.level]
        primes = [x for x in range(lo, hi) if is_prime(x)]
        self.p = random.choice(primes)
        self.q = random.choice([x for x in primes if x != self.p])
        if self.p > self.q:
            self.p, self.q = self.q, self.p
        self.n = self.p * self.q
        self.n_label.setText(str(self.n))
        self.n_label.setFont(mono_font(18, bold=True))
        set_tone(self.n_label, "success")
        self.p_input.setText("")
        self.q_input.setText("")
        self.p_input.setEnabled(True)
        self.q_input.setEnabled(True)
        self.submit_btn.setEnabled(True)
        self.submit_btn.setText("Check")
        self.time_left = secs
        self.level_label.setText(f"Level {self.level + 1}/5")
        self.timer_label.setText(f"{self.time_left}s")
        set_tone(self.timer_label, "")
        self.status_label.setText("")
        set_tone(self.status_label, "")
        self._update_level_buttons()
        self.timer.start(1000)

    def _tick(self):
        self.time_left -= 1
        self.timer_label.setText(f"{self.time_left}s")
        if self.time_left <= 5:
            set_tone(self.timer_label, "error")
        if self.time_left <= 0:
            self.timer.stop()
            self.penalize()
            self.status_label.setText(f"Time up! It was {self.p} * {self.q} = {self.n}")
            set_tone(self.status_label, "error")
            self.submit_btn.setEnabled(False)
            QTimer.singleShot(2200, self._new_level)

    def _check_answer(self):
        try:
            p_in = int(self.p_input.text().strip())
            q_in = int(self.q_input.text().strip())
        except ValueError:
            self.status_label.setText("Please enter integers!")
            set_tone(self.status_label, "error")
            return
        if {p_in, q_in} == {self.p, self.q}:
            self.timer.stop()
            base = (self.level + 1) * 100
            streak_before = self.streak.streak + 1
            mult_after = StreakTracker(); mult_after.streak = streak_before
            streak_mult = mult_after.multiplier()
            points = int(base * streak_mult)
            self.award(points)
            self.status_label.setText(
                f"Correct! {self.p} * {self.q} = {self.n}  (+{points}, ×{streak_mult:.1f} streak)"
            )
            set_tone(self.status_label, "success")
            self.submit_btn.setEnabled(False)
            QTimer.singleShot(1800, self._new_level)
        else:
            self.penalize()
            # Half-credit feedback: did the player at least find ONE of the
            # two primes? Don't reveal the other — keep some challenge.
            overlap = {p_in, q_in} & {self.p, self.q}
            if overlap:
                hit = next(iter(overlap))
                self.status_label.setText(
                    f"Close! {hit} is one of the primes, but the other isn't. "
                    f"{p_in} * {q_in} = {p_in * q_in}, not {self.n}. Streak reset."
                )
            else:
                self.status_label.setText(
                    f"{p_in} * {q_in} = {p_in * q_in}, not {self.n}. Streak reset!"
                )
            set_tone(self.status_label, "error")

    def _pick_level(self, idx):
        self.timer.stop()
        self.level = idx
        self.submit_btn.setText("Check")
        self.submit_btn.setEnabled(True)
        self.p_input.setEnabled(True)
        self.q_input.setEnabled(True)
        try:
            self.submit_btn.clicked.disconnect()
        except TypeError:
            pass
        self.submit_btn.clicked.connect(self._check_answer)
        self._new_level()

    def _update_level_buttons(self):
        for i, btn in enumerate(self.level_buttons):
            btn.setChecked(i == self.level)

    def _show_boss(self):
        self.timer.stop()
        self.p = 9999999967
        self.q = 9999999943
        self.n = self.p * self.q
        self.n_label.setText(str(self.n))
        self.level_label.setText("Level 5/5 - BOSS")
        self.timer_label.setText("inf")
        set_tone(self.timer_label, "error")
        self._update_level_buttons()
        self.status_label.setText(
            "This N has 20 digits. Real RSA uses 600+. Good luck trying - "
            "but this is exactly why RSA is secure. Click 'Give Up' for the answer."
        )
        set_tone(self.status_label, "error")
        self.submit_btn.setText("Give Up")
        self.submit_btn.setEnabled(True)
        try:
            self.submit_btn.clicked.disconnect()
        except TypeError:
            pass
        self.submit_btn.clicked.connect(self._show_rsa_lesson)

    def _show_rsa_lesson(self):
        self.n_label.setText(f"{self.p}  *  {self.q}  =  {self.n}")
        self.n_label.setFont(mono_font(11, bold=True))
        self.status_label.setText(
            "RSA-2048 uses primes with ~300 digits each, making N ~600 digits long. "
            "The best known algorithms would take longer than the age of the universe "
            "to factor such an N. That is the one-way function behind RSA."
        )
        set_tone(self.status_label, "")
        self.submit_btn.setText("Restart")
        self.submit_btn.setEnabled(True)
        try:
            self.submit_btn.clicked.disconnect()
        except TypeError:
            pass
        self.submit_btn.clicked.connect(self._restart)

    def _restart(self):
        self.level = 0
        self.reset_score()
        self.submit_btn.setText("Check")
        try:
            self.submit_btn.clicked.disconnect()
        except TypeError:
            pass
        self.submit_btn.clicked.connect(self._check_answer)
        self._new_level()


# =============================================================================
# Game 5: Hash Speed Sort
# =============================================================================

HASH_ALGOS_BY_DIFFICULTY = [
    ("MD5",     "Fast & broken — many collisions known since 2004",   1),
    ("SHA-1",   "Fast — collisions found in 2017, considered weak",   2),
    ("SHA-256", "Standard, secure for general use today",              3),
    ("bcrypt",  "Designed slow + salt — built to resist cracking",     4),
]

SORT_HELP = (
    "Goal: rank the four hash algorithms from EASIEST to HARDEST to crack.\n\n"
    "How:\n"
    "  1. Four algorithms are listed in random order on top.\n"
    "  2. Click them one by one — or press keys 1..4 — so the first "
    "pick is the easiest and the last pick the hardest.\n"
    "  3. When all four are placed, hit Check.\n\n"
    "Reset wipes your placement. Streak rewards correct sorts in a row.\n\n"
    "Real-world tie-in: when storing passwords, the algorithm matters a "
    "lot. Hashing with MD5 or even SHA-256 is unsafe because they're too "
    "fast — attackers can hash millions per second. Algorithms like "
    "bcrypt, scrypt or Argon2 are deliberately slow."
)


class HashSpeedSortGame(BaseGame):
    GAME_KEY = "hash_speed_sort"
    GAME_NAME = "Hash Speed Sort"
    HELP_TEXT = SORT_HELP

    def __init__(self, parent=None):
        super().__init__(parent)
        self.placed = []
        self._setup_ui()
        self._new_round()
        self.bind_number_keys(self._key_pick, 4)

    def _key_pick(self, idx: int):
        if 0 <= idx < len(self.cand_buttons) and self.cand_buttons[idx].isEnabled():
            self._on_candidate_click(idx)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "Sort the algorithms from EASIEST to HARDEST to crack. "
            "Click in order, easiest first."
        ))

        cand_group = QGroupBox("Algorithms")
        cl = QVBoxLayout(cand_group)
        self.cand_buttons = []
        for i in range(4):
            btn = QPushButton("")
            btn.setObjectName("btnRun")
            btn.setMinimumHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_candidate_click(idx))
            cl.addWidget(btn)
            self.cand_buttons.append(btn)
        layout.addWidget(cand_group)

        slot_group = QGroupBox("Your Ranking (Easiest → Hardest)")
        sl = QHBoxLayout(slot_group)
        sl.setSpacing(8)
        self.slot_labels = []
        for i in range(4):
            lbl = make_display_label("accent")
            lbl.setText("—")
            lbl.setFont(mono_font(11, bold=True))
            sl.addWidget(lbl, stretch=1)
            self.slot_labels.append(lbl)
        layout.addWidget(slot_group)

        self.feedback_label = make_feedback_label()
        layout.addWidget(self.feedback_label)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self.reset_btn = QPushButton("Reset Order")
        self.reset_btn.setObjectName("secondaryBtn")
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self._reset_order)
        action_row.addWidget(self.reset_btn)
        self.check_btn = QPushButton("Check")
        self.check_btn.setObjectName("btnRun")
        self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_btn.setEnabled(False)
        self.check_btn.clicked.connect(self._check_answer)
        action_row.addWidget(self.check_btn)
        layout.addLayout(action_row)
        layout.addStretch()

    def _new_round(self):
        shuffled = list(HASH_ALGOS_BY_DIFFICULTY)
        random.shuffle(shuffled)
        for btn, algo in zip(self.cand_buttons, shuffled):
            name, desc, _rank = algo
            btn.setText(f"{name}\n{desc}")
            btn.setProperty("algo", algo)
            btn.setEnabled(True)
        self._reset_order()

    def _reset_order(self):
        self.placed = []
        for lbl in self.slot_labels:
            lbl.setText("—")
            set_tone(lbl, "accent")
        for btn in self.cand_buttons:
            btn.setEnabled(True)
        self.check_btn.setEnabled(False)
        self.feedback_label.setText("")

    def _on_candidate_click(self, idx):
        btn = self.cand_buttons[idx]
        algo = btn.property("algo")
        if algo is None or not btn.isEnabled():
            return
        slot = len(self.placed)
        if slot >= 4:
            return
        self.placed.append(algo)
        self.slot_labels[slot].setText(algo[0])
        btn.setEnabled(False)
        if len(self.placed) == 4:
            self.check_btn.setEnabled(True)

    def _check_answer(self):
        correct_count = sum(
            1 for i, placed in enumerate(self.placed) if placed[2] == i + 1
        )
        all_correct = correct_count == 4

        for i, placed in enumerate(self.placed):
            ok = placed[2] == i + 1
            set_tone(self.slot_labels[i], "success" if ok else "error")

        if all_correct:
            streak_before = self.streak.streak + 1
            mult_after = StreakTracker(); mult_after.streak = streak_before
            streak_mult = mult_after.multiplier()
            points = int(200 * streak_mult)
            self.award(points)
            self.feedback_label.setText(f"Perfect! +{points} (×{streak_mult:.1f})")
            set_tone(self.feedback_label, "success")
        else:
            self.penalize()
            self.feedback_label.setText(
                f"{correct_count}/4 in the right slot. Streak reset!"
            )
            set_tone(self.feedback_label, "error")

        self.check_btn.setEnabled(False)
        QTimer.singleShot(2200, self._new_round)


# =============================================================================
# Game 6: Port Knocker
# =============================================================================

PORT_SERVICES_EASY = [
    ("HTTP",   80), ("HTTPS", 443), ("SSH",  22), ("FTP",  21), ("DNS",  53),
]
PORT_SERVICES_HARD = [
    ("HTTP", 80), ("HTTPS", 443), ("SSH", 22), ("FTP", 21), ("DNS", 53),
    ("SMTP", 25), ("IMAP", 143), ("POP3", 110), ("Telnet", 23),
    ("MySQL", 3306), ("PostgreSQL", 5432), ("RDP", 3389),
    ("VNC", 5900), ("MongoDB", 27017), ("Redis", 6379),
]

KNOCKER_HELP = (
    "Goal: pick the standard port that the named service listens on.\n\n"
    "How:\n"
    "  1. A service name is shown (e.g. HTTPS).\n"
    "  2. Four port numbers appear as buttons. Click the right one — or "
    "press keys 1..4 (reading order, top-left = 1).\n"
    "  3. Faster answers score more; you have 3 lives.\n\n"
    "Difficulty:\n"
    "  • Easy — five most common services (HTTP, HTTPS, SSH, FTP, DNS).\n"
    "  • Hard — fifteen services including DB, mail and remote-access.\n\n"
    "Real-world tie-in: knowing the standard ports is half the job of "
    "scanning a host. The Gilfi Port Scanner sweeps ports and reports "
    "what's open — turning open port numbers back into service names "
    "is the first thing any pentester does."
)


class PortKnockerGame(BaseGame):
    GAME_KEY = "port_knocker"
    GAME_NAME = "Port Knocker"
    HELP_TEXT = KNOCKER_HELP
    ROUND_TIME_LIMIT = 8.0

    DIFFICULTIES = [
        ("Easy",  PORT_SERVICES_EASY, 1.0),
        ("Hard",  PORT_SERVICES_HARD, 1.6),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lives = 3
        self.difficulty_idx = 0
        self.current_service = None
        self.round_start = 0.0
        self._accepting_clicks = True
        self._setup_ui()
        self._new_round()
        # Keys 1..4 map to the 2×2 grid in reading order.
        self.bind_number_keys(self._key_port, 4)

    def _key_port(self, idx: int):
        if not self._accepting_clicks:
            return
        if 0 <= idx < len(self.port_buttons) and self.port_buttons[idx].isEnabled():
            self._on_port_click(idx)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "Pick the standard port for the named service. "
            "Uses: knowledge of port-to-service mappings (Port Scanner)."
        ))

        diff_row, self.diff_buttons = make_difficulty_row(
            [n for n, _, _ in self.DIFFICULTIES], self._pick_difficulty
        )
        layout.addLayout(diff_row)

        svc_group = QGroupBox("Service")
        sl = QVBoxLayout(svc_group)
        self.service_label = make_display_label("accent")
        self.service_label.setFont(ui_font(22, bold=True))
        sl.addWidget(self.service_label)
        layout.addWidget(svc_group)

        ports_group = QGroupBox("Ports")
        grid = QGridLayout(ports_group)
        grid.setSpacing(8)
        self.port_buttons = []
        for i in range(4):
            btn = QPushButton("")
            btn.setObjectName("btnRun")
            btn.setMinimumHeight(50)
            btn.setFont(mono_font(13, bold=True))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_port_click(idx))
            grid.addWidget(btn, i // 2, i % 2)
            self.port_buttons.append(btn)
        layout.addWidget(ports_group)

        status_row = QHBoxLayout()
        self.lives_label = QLabel(hearts_for(3))
        self.lives_label.setObjectName("pillLives")
        status_row.addWidget(self.lives_label)
        status_row.addStretch()
        self.feedback_label = make_feedback_label()
        status_row.addWidget(self.feedback_label)
        layout.addLayout(status_row)
        layout.addStretch()
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)

    def _pick_difficulty(self, idx):
        self.difficulty_idx = idx
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)
        self.streak.reset()
        self.header.set_streak(0, 1.0)
        self._new_round()

    def _new_round(self):
        _, pool, _ = self.DIFFICULTIES[self.difficulty_idx]
        self.current_service = random.choice(pool)
        name, correct_port = self.current_service

        distractors = [p for n, p in pool if p != correct_port]
        random.shuffle(distractors)
        options = distractors[:3] + [correct_port]
        random.shuffle(options)

        self.service_label.setText(name)
        set_tone(self.service_label, "accent")
        for btn, port in zip(self.port_buttons, options):
            btn.setText(str(port))
            btn.setProperty("port", port)
            btn.setEnabled(True)
            btn.setObjectName("btnRun")
            btn.setProperty("tone", "")
            _repolish(btn)

        self.round_start = time.time()

    def _on_port_click(self, idx):
        btn = self.port_buttons[idx]
        port = btn.property("port")
        for b in self.port_buttons:
            b.setEnabled(False)

        elapsed = time.time() - self.round_start
        _, correct_port = self.current_service
        _, _, diff_mult = self.DIFFICULTIES[self.difficulty_idx]

        if port == correct_port:
            time_factor = max(0.2, 1.0 - elapsed / self.ROUND_TIME_LIMIT)
            base = 60
            streak_before = self.streak.streak + 1
            mult_after = StreakTracker(); mult_after.streak = streak_before
            streak_mult = mult_after.multiplier()
            points = max(15, int(base * time_factor * streak_mult * diff_mult))
            self.award(points)
            btn.setObjectName("tileBtn")
            set_tone(btn, "success")
            self.feedback_label.setText(f"+{points} ({elapsed:.1f}s, ×{streak_mult:.1f})")
            set_tone(self.feedback_label, "success")
        else:
            self.lives -= 1
            self.penalize()
            self.lives_label.setText(hearts_for(self.lives))
            btn.setObjectName("tileBtn")
            set_tone(btn, "error")
            for b in self.port_buttons:
                if b.property("port") == correct_port:
                    b.setObjectName("tileBtn")
                    set_tone(b, "success")
            self.feedback_label.setText(f"Correct port: {correct_port}")
            set_tone(self.feedback_label, "error")

        if self.lives <= 0:
            QTimer.singleShot(1800, self._game_over)
        else:
            QTimer.singleShot(1500, self._new_round)

    def _game_over(self):
        self._accepting_clicks = False
        self.service_label.setText(f"GAME OVER  -  Final: {self.score}")
        set_tone(self.service_label, "error")
        self.feedback_label.setText("Click any tile to restart")
        set_tone(self.feedback_label, "")
        for btn in self.port_buttons:
            btn.setText("Restart")
            btn.setEnabled(True)
            btn.setObjectName("tileBtn")
            set_tone(btn, "restart")
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(self._restart)

    def _restart(self):
        self._accepting_clicks = True
        self.reset_score()
        self.lives = 3
        self.lives_label.setText(hearts_for(3))
        self.feedback_label.setText("")
        for i, btn in enumerate(self.port_buttons):
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(lambda checked=False, idx=i: self._on_port_click(idx))
        self._new_round()


# =============================================================================
# Game 7: Password Anatomy
# =============================================================================

PASSWORD_PUZZLES_EASY = [
    ("password",   0, ["Common dictionary word", "Has special chars", "Too long", "Random letters"]),
    ("12345678",   0, ["Sequential digits", "Mixed case missing", "Too random", "Uses symbols"]),
    ("qwerty",     0, ["Keyboard pattern", "Too random", "Numbers only", "Long enough"]),
    ("abc",        0, ["Too short", "Has uppercase", "Sequential digits", "Has special chars"]),
    ("iloveyou",   0, ["Common phrase", "Random letters", "Has digits", "Has special chars"]),
    ("admin",      0, ["Default credential", "Too long", "Truly random", "All digits"]),
    ("aaaaaaaa",   0, ["Repeated character", "Mixed case", "Has digits", "Random characters"]),
    ("monkey",     0, ["Common dictionary word", "Has uppercase", "All digits", "16+ characters"]),
]

PASSWORD_PUZZLES_HARD = PASSWORD_PUZZLES_EASY + [
    ("P@ssw0rd",   0, ["Predictable substitutions", "Truly random", "Too long", "All numeric"]),
    ("dragon123",  0, ["Word + trailing digits", "Truly random", "Too short", "No letters"]),
    ("LetMeIn1",   0, ["Common phrase + digit", "All random", "Has 12+ chars", "Lowercase only"]),
    ("1qaz2wsx",   0, ["Keyboard pattern", "Truly random", "All uppercase", "Has special chars"]),
    ("Summer2024", 0, ["Word + year", "Truly random", "Has special chars", "Too short"]),
    ("Q1w2e3r4",   0, ["Walking keyboard rows", "Random mix", "No digits", "All lowercase"]),
]


ANATOMY_HELP = (
    "Goal: identify the main weakness of the displayed password.\n\n"
    "How:\n"
    "  1. A password appears at the top.\n"
    "  2. Four possible weaknesses are listed.\n"
    "  3. Pick the most accurate description of why it's weak — click, "
    "or press keys 1..4 (reading order, top-left = 1).\n\n"
    "Difficulty:\n"
    "  • Easy — obviously weak passwords ('password', '12345', 'qwerty').\n"
    "  • Hard — subtler tricks: leet-speak, walking keys, word+year.\n\n"
    "Real-world tie-in: this is exactly what the Gilfi Password Analyzer "
    "does. Different weaknesses are detectable by different rules — "
    "common-list lookups, regex for keyboard walks, leet-speak "
    "substitution mapping, entropy calculation."
)


class PasswordAnatomyGame(BaseGame):
    GAME_KEY = "password_anatomy"
    GAME_NAME = "Password Anatomy"
    HELP_TEXT = ANATOMY_HELP
    ROUND_TIME_LIMIT = 12.0

    DIFFICULTIES = [
        ("Easy", PASSWORD_PUZZLES_EASY, 1.0),
        ("Hard", PASSWORD_PUZZLES_HARD, 1.5),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.lives = 3
        self.difficulty_idx = 0
        self.current_puzzle = None
        self._shuffled_correct = 0
        self.round_start = 0.0
        self._accepting_clicks = True
        self._setup_ui()
        self._new_round()
        self.bind_number_keys(self._key_option, 4)

    def _key_option(self, idx: int):
        if not self._accepting_clicks:
            return
        if 0 <= idx < len(self.option_buttons) and self.option_buttons[idx].isEnabled():
            self._on_option_click(idx)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "Why is this password weak? Pick the most fitting reason. "
            "Uses: same checks as the Password Analyzer."
        ))

        diff_row, self.diff_buttons = make_difficulty_row(
            [n for n, _, _ in self.DIFFICULTIES], self._pick_difficulty
        )
        layout.addLayout(diff_row)

        pw_group = QGroupBox("Password")
        pl = QVBoxLayout(pw_group)
        self.pw_label = make_display_label("error")
        self.pw_label.setFont(mono_font(22, bold=True))
        pl.addWidget(self.pw_label)
        layout.addWidget(pw_group)

        opt_group = QGroupBox("What's the main issue?")
        og = QGridLayout(opt_group)
        og.setSpacing(8)
        self.option_buttons = []
        for i in range(4):
            btn = QPushButton("")
            btn.setObjectName("btnRun")
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_option_click(idx))
            og.addWidget(btn, i // 2, i % 2)
            self.option_buttons.append(btn)
        layout.addWidget(opt_group)

        status_row = QHBoxLayout()
        self.lives_label = QLabel(hearts_for(3))
        self.lives_label.setObjectName("pillLives")
        status_row.addWidget(self.lives_label)
        status_row.addStretch()
        self.feedback_label = make_feedback_label()
        status_row.addWidget(self.feedback_label)
        layout.addLayout(status_row)

        action_row = QHBoxLayout()
        action_row.addStretch()
        self.to_analyzer_btn = QPushButton("Send to Password Analyzer")
        self.to_analyzer_btn.setObjectName("secondaryBtn")
        self.to_analyzer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.to_analyzer_btn.clicked.connect(self._send_to_analyzer)
        action_row.addWidget(self.to_analyzer_btn)
        layout.addLayout(action_row)
        layout.addStretch()
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)

    def _pick_difficulty(self, idx):
        self.difficulty_idx = idx
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)
        self.streak.reset()
        self.header.set_streak(0, 1.0)
        self._new_round()

    def _new_round(self):
        _, pool, _mult = self.DIFFICULTIES[self.difficulty_idx]
        self.current_puzzle = random.choice(pool)
        password, correct_idx, options = self.current_puzzle
        indexed = list(enumerate(options))
        random.shuffle(indexed)
        self._shuffled_correct = next(
            i for i, (orig_idx, _) in enumerate(indexed) if orig_idx == correct_idx
        )
        self.pw_label.setText(password)
        set_tone(self.pw_label, "error")
        for btn, (_, text) in zip(self.option_buttons, indexed):
            btn.setText(text)
            btn.setEnabled(True)
            btn.setObjectName("btnRun")
            btn.setProperty("tone", "")
            _repolish(btn)
        self.round_start = time.time()

    def _on_option_click(self, idx):
        for b in self.option_buttons:
            b.setEnabled(False)
        elapsed = time.time() - self.round_start
        _, _, diff_mult = self.DIFFICULTIES[self.difficulty_idx]

        if idx == self._shuffled_correct:
            time_factor = max(0.2, 1.0 - elapsed / self.ROUND_TIME_LIMIT)
            base = 50
            streak_before = self.streak.streak + 1
            mult_after = StreakTracker(); mult_after.streak = streak_before
            streak_mult = mult_after.multiplier()
            points = max(10, int(base * time_factor * streak_mult * diff_mult))
            self.award(points)
            self.option_buttons[idx].setObjectName("tileBtn")
            set_tone(self.option_buttons[idx], "success")
            self.feedback_label.setText(f"+{points} ({elapsed:.1f}s, ×{streak_mult:.1f})")
            set_tone(self.feedback_label, "success")
        else:
            self.lives -= 1
            self.penalize()
            self.lives_label.setText(hearts_for(self.lives))
            self.option_buttons[idx].setObjectName("tileBtn")
            set_tone(self.option_buttons[idx], "error")
            self.option_buttons[self._shuffled_correct].setObjectName("tileBtn")
            set_tone(self.option_buttons[self._shuffled_correct], "success")
            self.feedback_label.setText("Correct one highlighted")
            set_tone(self.feedback_label, "error")

        if self.lives <= 0:
            QTimer.singleShot(1800, self._game_over)
        else:
            QTimer.singleShot(1600, self._new_round)

    def _send_to_analyzer(self):
        if self.current_puzzle is None:
            return
        password, _, _ = self.current_puzzle
        ok = _send_to_module(self, "Password Analyzer", {
            "Password": password,
        }, auto_run=True)
        if not ok:
            _show_status(self, "Could not find Password Analyzer", 2000)

    def _game_over(self):
        self._accepting_clicks = False
        self.pw_label.setText(f"GAME OVER — {self.score}")
        set_tone(self.pw_label, "error")
        for btn in self.option_buttons:
            btn.setText("Restart")
            btn.setEnabled(True)
            btn.setObjectName("tileBtn")
            set_tone(btn, "restart")
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(self._restart)

    def _restart(self):
        self._accepting_clicks = True
        self.reset_score()
        self.lives = 3
        self.lives_label.setText(hearts_for(3))
        self.feedback_label.setText("")
        for i, btn in enumerate(self.option_buttons):
            try:
                btn.clicked.disconnect()
            except TypeError:
                pass
            btn.clicked.connect(lambda checked=False, idx=i: self._on_option_click(idx))
        self._new_round()


# =============================================================================
# Game 8: RSA Speedrun
# =============================================================================

def _gen_rsa_puzzle(prime_pool):
    p = random.choice(prime_pool)
    q = random.choice([x for x in prime_pool if x != p])
    phi = (p - 1) * (q - 1)
    candidates = [e for e in (3, 5, 7, 11, 13) if e < phi and _ext_gcd(e, phi)[0] == 1]
    e = random.choice(candidates)
    n = p * q
    d = modinv(e, phi)
    m = random.randint(2, n - 1)
    c = pow(m, e, n)
    return {"p": p, "q": q, "n": n, "phi": phi, "e": e, "d": d, "m": m, "c": c}


RSA_HELP = (
    "Goal: walk through an RSA encryption by hand, one step at a time.\n\n"
    "How (four steps per puzzle):\n"
    "  1. Compute n = p · q\n"
    "  2. Compute φ(n) = (p − 1)(q − 1)\n"
    "  3. Find d so that e · d ≡ 1 (mod φ). The hint button gives the answer.\n"
    "  4. Encrypt the message m: compute c = mᵉ mod n.\n\n"
    "Difficulty:\n"
    "  • Easy — tiny primes (3..13). Solvable in your head.\n"
    "  • Hard — primes up to 29. Calculator helps.\n\n"
    "The Hint button reveals the current step's answer but reduces "
    "scoring for it.\n\n"
    "Real-world tie-in: this *is* RSA. The only difference between this "
    "and what TLS does on every HTTPS connection is the size of the "
    "primes (here 1–2 digits, in TLS 300+ digits)."
)


class RSASpeedrunGame(BaseGame):
    GAME_KEY = "rsa_speedrun"
    GAME_NAME = "RSA Speedrun"
    HELP_TEXT = RSA_HELP

    STEPS = [
        ("n",   "Compute n = p · q",
            "n is just the product of p and q. Multiply them."),
        ("phi", "Compute φ(n) = (p − 1)(q − 1)",
            "Subtract 1 from each prime, then multiply the results."),
        ("d",   "Find d such that e · d ≡ 1 (mod φ)",
            "d is the modular inverse of e mod φ. Try d = 1, 2, 3 ... "
            "until e · d mod φ = 1."),
        ("c",   "Encrypt: compute c = mᵉ mod n",
            "Raise m to the power of e, then take the result mod n."),
    ]

    DIFFICULTIES = [
        ("Easy", [3, 5, 7, 11, 13], 1.0),
        ("Hard", [3, 5, 7, 11, 13, 17, 19, 23, 29], 1.6),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.difficulty_idx = 0
        self.puzzle = None
        self.step_idx = 0
        self.used_hint = False
        self._setup_ui()
        self._new_puzzle()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        layout.addWidget(self.header)
        layout.addWidget(make_info_label(
            "Walk through an RSA encryption by hand: n, φ, d, then c. "
            "Uses: same math as the RSA Encryption module."
        ))

        diff_row, self.diff_buttons = make_difficulty_row(
            [n for n, _, _ in self.DIFFICULTIES], self._pick_difficulty
        )
        layout.addLayout(diff_row)

        givens_group = QGroupBox("Givens")
        gv = QVBoxLayout(givens_group)
        self.givens_label = make_display_label("dim")
        self.givens_label.setFont(mono_font(13))
        gv.addWidget(self.givens_label)
        layout.addWidget(givens_group)

        step_group = QGroupBox("Step")
        sg = QVBoxLayout(step_group)
        self.step_label = QLabel("")
        self.step_label.setObjectName("pillScore")
        self.step_label.setFont(ui_font(13, bold=True))
        self.step_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sg.addWidget(self.step_label)

        ans_row = QHBoxLayout()
        ans_row.addStretch()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Your answer")
        self.input.setMaximumWidth(180)
        self.input.returnPressed.connect(self._submit)
        ans_row.addWidget(self.input)
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setObjectName("btnRun")
        self.submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_btn.clicked.connect(self._submit)
        ans_row.addWidget(self.submit_btn)
        self.hint_btn = QPushButton("Hint")
        self.hint_btn.setObjectName("secondaryBtn")
        self.hint_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hint_btn.clicked.connect(self._hint)
        ans_row.addWidget(self.hint_btn)
        ans_row.addStretch()
        sg.addLayout(ans_row)
        layout.addWidget(step_group)

        self.feedback_label = make_feedback_label()
        layout.addWidget(self.feedback_label)

        sr = QHBoxLayout()
        self.progress_label = QLabel("Step 1/4")
        self.progress_label.setObjectName("pillScore")
        sr.addWidget(self.progress_label)
        sr.addStretch()
        layout.addLayout(sr)
        layout.addStretch()
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)

    def _pick_difficulty(self, idx):
        self.difficulty_idx = idx
        refresh_diff_buttons(self.diff_buttons, self.difficulty_idx)
        self.streak.reset()
        self.header.set_streak(0, 1.0)
        self._new_puzzle()

    def _new_puzzle(self):
        _, prime_pool, _ = self.DIFFICULTIES[self.difficulty_idx]
        self.puzzle = _gen_rsa_puzzle(prime_pool)
        self.step_idx = 0
        self._show_step()

    def _show_step(self):
        self.used_hint = False
        self.input.setEnabled(True)
        self.submit_btn.setEnabled(True)
        self.hint_btn.setEnabled(True)
        self.input.setText("")
        self.input.setFocus()
        _, title, _ = self.STEPS[self.step_idx]
        self.progress_label.setText(f"Step {self.step_idx + 1}/4")
        self.step_label.setText(title)
        z = self.puzzle
        if self.step_idx == 0:
            self.givens_label.setText(f"p = {z['p']}    q = {z['q']}")
        elif self.step_idx == 1:
            self.givens_label.setText(f"p = {z['p']}    q = {z['q']}    n = {z['n']}")
        elif self.step_idx == 2:
            self.givens_label.setText(f"n = {z['n']}    φ(n) = {z['phi']}    e = {z['e']}")
        else:
            self.givens_label.setText(f"n = {z['n']}    e = {z['e']}    m = {z['m']}")
        self.feedback_label.setText("")
        set_tone(self.feedback_label, "")

    def _expected(self):
        key = self.STEPS[self.step_idx][0]
        return int(self.puzzle[key])

    def _submit(self):
        try:
            answer = int(self.input.text().strip())
        except ValueError:
            self.feedback_label.setText("Please enter an integer!")
            set_tone(self.feedback_label, "error")
            return
        expected = self._expected()
        _, _, diff_mult = self.DIFFICULTIES[self.difficulty_idx]
        if answer == expected:
            base = 25 if self.used_hint else 75
            streak_before = self.streak.streak + 1
            mult_after = StreakTracker(); mult_after.streak = streak_before
            streak_mult = mult_after.multiplier()
            points = int(base * streak_mult * diff_mult)
            self.award(points)
            self.feedback_label.setText(
                f"Correct! +{points}" + (" (hint used)" if self.used_hint else "")
            )
            set_tone(self.feedback_label, "success")
            self.step_idx += 1
            if self.step_idx >= len(self.STEPS):
                QTimer.singleShot(2200, self._puzzle_complete)
            else:
                QTimer.singleShot(1400, self._show_step)
        else:
            self.penalize()
            self.feedback_label.setText(f"Not quite — expected {expected}. Streak reset.")
            set_tone(self.feedback_label, "error")

    def _hint(self):
        self.used_hint = True
        expected = self._expected()
        _, _, explanation = self.STEPS[self.step_idx]
        self.feedback_label.setText(
            f"Hint: {explanation}\nAnswer: {expected}  (scoring reduced for this step)"
        )
        set_tone(self.feedback_label, "warning")

    def _puzzle_complete(self):
        self.feedback_label.setText("Puzzle complete! New puzzle starting ...")
        set_tone(self.feedback_label, "success")
        QTimer.singleShot(1500, self._new_puzzle)


# =============================================================================
# Game Card
#
# Cross-platform-safe styling:
#   - the card itself is a QFrame#gameCard, styled entirely from the global
#     QSS template (so theme switch just works)
#   - hover is implemented via a dynamic property ``hovered`` ("true"/"false")
#     and ``_repolish`` instead of the ``:hover`` selector, which is
#     unreliable on macOS QFrame
#   - child labels have explicit transparent backgrounds (via QSS for the
#     specific object names) so the card's background colour shows through
# =============================================================================

class GameCard(QFrame):
    clicked = pyqtSignal()

    CARD_WIDTH = 230
    CARD_HEIGHT = 175

    def __init__(self, name: str, tagline: str, tag: str, game_key: str,
                 parent=None):
        super().__init__(parent)
        self.name = name
        self.tagline = tagline
        self.tag = tag
        self.game_key = game_key
        self.setObjectName("gameCard")
        self.setProperty("hovered", "false")
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._build()

    def _build(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(4)

        title = QLabel(self.name)
        title.setObjectName("cardTitle")
        title.setWordWrap(True)
        v.addWidget(title)

        tag_lbl = QLabel(self.tag)
        tag_lbl.setObjectName("cardTag")
        v.addWidget(tag_lbl)

        v.addSpacing(2)

        tagline_lbl = QLabel(self.tagline)
        tagline_lbl.setObjectName("cardTagline")
        tagline_lbl.setWordWrap(True)
        v.addWidget(tagline_lbl, stretch=1)

        best_row = QHBoxLayout()
        best_label_caption = QLabel("Best")
        best_label_caption.setObjectName("cardBestCaption")
        best_row.addWidget(best_label_caption)
        self.best_value_lbl = QLabel(str(load_best(self.game_key)))
        self.best_value_lbl.setObjectName("cardBestValue")
        self.best_value_lbl.setFont(mono_font(12, bold=True))
        best_row.addWidget(self.best_value_lbl)
        best_row.addStretch()
        # Last-played timestamp on the right — empty when never played.
        self.last_played_lbl = QLabel(format_relative_time(load_last_played(self.game_key)))
        self.last_played_lbl.setObjectName("cardLastPlayed")
        best_row.addWidget(self.last_played_lbl)
        v.addLayout(best_row)

    def refresh_best(self):
        """Refresh the visible best score and last-played from QSettings."""
        self.best_value_lbl.setText(str(load_best(self.game_key)))
        self.last_played_lbl.setText(format_relative_time(load_last_played(self.game_key)))

    def enterEvent(self, e):
        self.setProperty("hovered", "true")
        _repolish(self)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setProperty("hovered", "false")
        _repolish(self)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(e)


# =============================================================================
# Arcade root
# =============================================================================

GAMES_CATALOG = [
    # (class, display_name, tagline, module_tag, category)
    (CrackTheCodeGame,        "Crack the Code",
        "Caesar cipher slider puzzle. Three difficulty tiers.",
        "CRYPTO", "Cryptography"),
    (FactorizeGame,           "Factorize!",
        "Find p and q from N. Level 5 is the boss.",
        "RSA TEASER", "Cryptography"),
    (RSASpeedrunGame,         "RSA Speedrun",
        "Walk through RSA by hand: n, φ, d, c.",
        "RSA ENCRYPTION", "Cryptography"),
    (HashHunterGame,          "Hash Hunter",
        "Match the hash to a word. Live hover preview.",
        "HASH MODULE", "Hashing"),
    (HashSpeedSortGame,       "Hash Speed Sort",
        "Rank algorithms easiest-to-hardest to crack.",
        "HASH / HASH CRACK", "Hashing"),
    (SurviveTheCrackerGame,   "Survive the Cracker",
        "Defend a password against rockyou.txt.",
        "HASH CRACK MODULE", "Hashing"),
    (PortKnockerGame,         "Port Knocker",
        "Pick the standard port for a service. Easy/Hard.",
        "PORT SCANNER", "Defense"),
    (PasswordAnatomyGame,     "Password Anatomy",
        "Spot the weakness in weak passwords. Easy/Hard.",
        "PASSWORD ANALYZER", "Defense"),
]

# Order in which categories appear on the home screen.
CATEGORY_ORDER = ["Cryptography", "Hashing", "Defense"]


class ArcadeWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._game_pages = {}
        self._setup_ui()
        # Refresh card best / last-played labels whenever we come back to
        # home; also rebuild on theme change.
        theme_module.signals().theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 12)
        outer.setSpacing(8)

        self.stack = QStackedWidget()
        self.stack.currentChanged.connect(self._on_stack_changed)
        outer.addWidget(self.stack)

        self.home_page = self._build_home()
        self.stack.addWidget(self.home_page)

    def _build_home(self):
        home = QWidget()
        v = QVBoxLayout(home)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        title = QLabel("Gilfi Arcade")
        title.setObjectName("arcadeHomeTitle")
        v.addWidget(title)

        desc = QLabel(
            "Mini-games tied to the Gilfi modules. Pick a card to play. "
            "Best scores are saved automatically and broadcast to the status bar."
        )
        desc.setObjectName("arcadeHomeDesc")
        desc.setWordWrap(True)
        v.addWidget(desc)
        v.addSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        cards_host = QWidget()
        sections_layout = QVBoxLayout(cards_host)
        sections_layout.setContentsMargins(0, 0, 0, 0)
        sections_layout.setSpacing(6)

        # ``self.cards`` is the flat list, used by refresh helpers.
        # ``self._section_grids`` is a list of (category, [cards], QGridLayout)
        # used by ``_reflow_cards`` to lay each section out independently.
        self.cards = []
        self._section_grids = []

        # Bucket games by category preserving the catalog order.
        by_category = {cat: [] for cat in CATEGORY_ORDER}
        for entry in GAMES_CATALOG:
            cat = entry[4]
            by_category.setdefault(cat, []).append(entry)

        for category in CATEGORY_ORDER:
            entries = by_category.get(category) or []
            if not entries:
                continue

            header = QLabel(category.upper())
            header.setObjectName("categoryHeader")
            sections_layout.addWidget(header)

            grid_host = QWidget()
            grid = QGridLayout(grid_host)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(14)
            grid.setVerticalSpacing(14)

            section_cards = []
            for cls, name, tagline, tag, _cat in entries:
                card = GameCard(name, tagline, tag, cls.GAME_KEY)
                card.clicked.connect(
                    lambda c=cls, n=name: self._open_game(c, n)
                )
                self.cards.append(card)
                section_cards.append(card)

            self._section_grids.append((category, section_cards, grid))
            sections_layout.addWidget(grid_host)

        sections_layout.addStretch(1)
        self._reflow_cards(4)

        scroll.setWidget(cards_host)
        v.addWidget(scroll, stretch=1)

        return home

    def _reflow_cards(self, cols: int):
        """Lay each category's cards out in ``cols`` columns independently."""
        for _category, section_cards, grid in self._section_grids:
            for card in section_cards:
                grid.removeWidget(card)
            for i, card in enumerate(section_cards):
                r, c = divmod(i, cols)
                grid.addWidget(
                    card, r, c,
                    Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                )
            # Trailing column-stretch so the row doesn't justify-fill.
            grid.setColumnStretch(cols, 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        if w < 600:
            cols = 1
        elif w < 900:
            cols = 2
        elif w < 1200:
            cols = 3
        else:
            cols = 4
        if hasattr(self, "_section_grids") and cols != getattr(self, "_last_cols", None):
            self._last_cols = cols
            self._reflow_cards(cols)

    def _open_game(self, game_class, name: str):
        if name not in self._game_pages:
            page = QWidget()
            v = QVBoxLayout(page)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(8)

            back_row = QHBoxLayout()
            back_btn = QPushButton("← Back to Arcade")
            back_btn.setObjectName("secondaryBtn")
            back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
            back_row.addWidget(back_btn)
            back_row.addStretch()
            v.addLayout(back_row)

            v.addWidget(game_class())

            self._game_pages[name] = self.stack.addWidget(page)
        self.stack.setCurrentIndex(self._game_pages[name])

    def _on_stack_changed(self, idx):
        # When we come back to home, refresh card labels in case a game
        # just set a new best or updated its last-played timestamp.
        if idx == 0:
            for card in getattr(self, "cards", []):
                card.refresh_best()

    def _on_theme_changed(self, _name):
        # Re-polish all cards so the property-based hover styling picks up
        # the new palette immediately.
        for card in getattr(self, "cards", []):
            _repolish(card)
            card.refresh_best()


def create_page():
    """Entry point — called by mainwindow.register_tools()."""
    return ArcadeWidget()
